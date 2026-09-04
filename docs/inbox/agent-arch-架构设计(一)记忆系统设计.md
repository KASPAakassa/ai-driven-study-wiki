# 原始资料:万字长文拆解Agent架构设计(一):记忆系统设计

> 来源:微信公众号(Agent 架构设计系列),原文链接:https://mp.weixin.qq.com/s/rCNtpDFyZtgtZLT4MH9X1A
> 抓取日期:2026-08-09;状态:已拆解入库(见归档记录)

---

本系列目标：拆解 Claude Code 源码，理解 Agent 底层架构的设计思路。
核心方法：读源码 → 理解设计决策 → 用 TypeScript 手写核心逻辑。
每一篇聚焦一个子系统，讲清楚"为什么这么设计"比"代码怎么写"更重要。

引言
没有记忆的 Agent 就像每次对话都失忆的人——你说过的每一句话，它都要重新理解。
Claude Code 的记忆系统设计非常精巧，它不用向量数据库，不做语义搜索，却实现了高效的上下文管理。核心思路是：用文件系统路径编码相关性，用 Token 预算驱动行为调节，用分层提示构建实现缓存优化。
这篇文章聚焦三个部分：拆解 Claude Code 的真实实现 → 理解背后的设计决策 → 用 TypeScript 手写核心逻辑。

Part 1：拆解 Claude Code 源码
Claude Code 的源码（TypeScript）已经被社区逆向分析得很清楚了。核心记忆逻辑集中在三个地方：系统提示构建、CLAUDE.md 加载、Token 预算管理。
1.1 系统提示构建：buildSystemPrompt()
这是 Claude Code 记忆系统的入口，每次调用模型前都会执行。

// 简化自 Claude Code 源码（去掉无关细节）interface SystemPromptConfig { gitStatus?: GitStatus; claudeMdContent?: string; skillsList?: SkillSummary[]; tokenBudget?: TokenBudget;} function buildSystemPrompt(config: SystemPromptConfig): string { const parts: string[] = [];  // === 固定层（走 Prefix Cache，付一次就永久缓存）=== parts.push(AGENT_IDENTITY); // Agent 身份定义 parts.push(CODING_PHILOSOPHY); // 最小化修改、只做被要求的事 parts.push(TOOL_USAGE_RULES); // 工具调用规范  // === 条件层（按需注入，节省 Token）===  // 1. 项目规则：有 CLAUDE.md 才注入 if (config.claudeMdContent) { parts.push(`<project_rules>\n${config.claudeMdContent}\n</project_rules>`); }  // 2. Git 上下文：在 Git 仓库内才注入 if (config.gitStatus) { parts.push(formatGitStatus(config.gitStatus)); }  // 3. Skills 索引：只注入名称+描述，不注入完整内容 if (config.skillsList?.length) { parts.push(formatSkillsIndex(config.skillsList)); }  // 4. Token 预算：用户设置了目标时才注入 if (config.tokenBudget) { parts.push(formatTokenBudget(config.tokenBudget)); }  return parts.join('\n\n');}
关键设计决策：固定层和条件层分离。固定层不变，Anthropic API 的 Prompt Caching 会自动缓存前缀——你为这部分 token 只付一次输入费用，之后命中缓存只要付 10% 的费用。
1.2 CLAUDE.md 分层加载：loadClaudeMd()
这是"路径即相关性"设计的实现核心。Claude Code 不用向量搜索——相关性完全由文件系统路径编码。

import * as path from 'path';import * as fs from 'fs/promises'; interface ClaudeMdLayer { scope: 'global' | 'project' | 'directory'; filePath: string; content: string;} async function loadClaudeMd(cwd: string): Promise<string> { const layers: ClaudeMdLayer[] = [];  // 1. 全局层：~/.claude/CLAUDE.md（所有项目都加载） const globalPath = path.join(process.env.HOME!, '.claude', 'CLAUDE.md'); const globalContent = await readIfExists(globalPath); if (globalContent) { layers.push({ scope: 'global', filePath: globalPath, content: globalContent }); }  // 2. 项目层：向上遍历查找 CLAUDE.md（到 git root 为止） const projectRoot = await findGitRoot(cwd) ?? cwd; const projectPath = path.join(projectRoot, 'CLAUDE.md'); const projectContent = await readIfExists(projectPath); if (projectContent) { layers.push({ scope: 'project', filePath: projectPath, content: projectContent }); }  // 3. 目录层：当前工作目录的 CLAUDE.md（如果和项目根不同） if (cwd !== projectRoot) { const dirPath = path.join(cwd, 'CLAUDE.md'); const dirContent = await readIfExists(dirPath); if (dirContent) { layers.push({ scope: 'directory', filePath: dirPath, content: dirContent }); } }  // 拼接时注明来源，让模型知道规则的作用域 return layers .map(l => `<!-- ${l.scope}: ${l.filePath} -->\n${l.content}`) .join('\n\n');} async function findGitRoot(startDir: string): Promise<string | null> { let dir = startDir; while (dir !== path.dirname(dir)) { try { await fs.access(path.join(dir, '.git')); return dir; } catch { dir = path.dirname(dir); } } return null;} async function readIfExists(filePath: string): Promise<string | null> { try { return await fs.readFile(filePath, 'utf-8'); } catch { return null; }}
三层加载的设计让规则自动按作用域生效：全局规则（比如"我是全栈工程师"）所有项目共享，项目规则（比如"我们用 TypeScript strict mode"）跟着仓库走，目录规则（比如"这个模块的 API 用 REST"）跟着子目录走。
1.3 Token 预算感知：TokenBudgetManager
这是 Claude Code 最值得借鉴的设计——让 Agent 自己感知剩余预算，从而主动调整行为。

interface TokenBudget { used: number; total: number; percentage: number; warningLevel: 'none' | 'approaching' | 'critical' | 'compacting';} class TokenBudgetManager { private readonly THRESHOLDS = { approaching: 0.70, // 70%：第一次提示 critical: 0.85, // 85%：第二次提示 compacting: 0.90, // 90%：执行压缩 };  assess(used: number, total: number): TokenBudget { const pct = used / total; let warningLevel: TokenBudget['warningLevel'] = 'none';  if (pct >= this.THRESHOLDS.compacting) warningLevel = 'compacting'; else if (pct >= this.THRESHOLDS.critical) warningLevel = 'critical'; else if (pct >= this.THRESHOLDS.approaching) warningLevel = 'approaching';  return { used, total, percentage: pct, warningLevel }; }  // 核心：把预算状态转换成注入 Agent 的文本 // Agent 读到这段话，会真的调整自己的行为 formatForInjection(budget: TokenBudget): string | null { if (budget.warningLevel === 'none') return null;  const remaining = budget.total - budget.used; const messages: Record<TokenBudget['warningLevel'], string> = { none: '', approaching: `<token_budget>You have used ${Math.round(budget.percentage * 100)}% of your context window (~${remaining.toLocaleString()} tokens remaining).Consider finishing current tasks before starting new ones.</token_budget>`, critical: `<token_budget>CONTEXT LIMIT APPROACHING: ${Math.round(budget.percentage * 100)}% used (~${remaining.toLocaleString()} tokens left).Prioritize completing critical steps. Avoid reading large files.</token_budget>`, compacting: `<token_budget>CONTEXT COMPACTION IMMINENT. Complete any in-progress writes now.</token_budget>`, };  return messages[budget.warningLevel]; }}
注意这里的关键设计：不直接截断上下文，而是用自然语言告知 Agent。Agent 读到 "Avoid reading large files" 后会在规划时真的避免打开大文件。这是上下文工程里很微妙的一个技巧——把工程约束翻译成模型能理解的指令。
Part 2：为什么这样设计——从代码看决策
看完代码，三个设计决策值得重点理解。
决策一：parts.push() 的顺序有意义
固定层在最前面，是因为 Prompt Cache 缓存的是"前缀"——前缀越稳定，缓存命中率越高。条件层在后面变动，不影响固定层的缓存。
如果你把 Git Status（每次都变）放在最前面，整个系统提示都无法缓存。顺序即成本。

缓存命中区 ──────────────────────────────┐┌──────────────────────────────────────┐ ││ AGENT_IDENTITY │ │ 固定层│ CODING_PHILOSOPHY │ │ （永远缓存）│ TOOL_USAGE_RULES │ │└──────────────────────────────────────┘ │ │┌──────────────────────────────────────┐ ││ <project_rules>... │ ││ <git_status>... │ │ 条件层│ <skills_index>... │ │ （按需变化）│ <token_budget>... │ │└──────────────────────────────────────┘ │ │ 缓存分界线 ←─────────────────┘
决策二：findGitRoot() 决定了 CLAUDE.md 的作用域边界
没有向量搜索，没有相似度计算。相关性完全由文件系统路径编码。

// 路径 → 相关性// ~/.claude/CLAUDE.md → 所有项目// /project/CLAUDE.md → 这个项目// /project/src/api/CLAUDE.md → 这个模块
代价是它只能做"这个目录用什么规则"，不能做"这个任务需要什么历史经验"——这正是 Claude Code 没有情景记忆（episodic memory）的根本原因。但它的语义记忆（semantic memory，即事实性知识）通过 CLAUDE.md 管理得非常高效。
决策三：formatForInjection() 把系统状态变成自然语言
这是一个很深的洞察：对于 LLM，自然语言就是最好的 API。

工程状态（Token 用量 85%） ↓ formatForInjection()自然语言指令（”Avoid reading large files”） ↓ 模型读取行为调整（真的不去读大文件了）
这种"把约束翻译成指令"的模式可以推广到很多场景：
把 API 限流状态翻译成"请减少工具调用频率"

把内存用量翻译成"请避免处理大文件"

把错误率翻译成"请更仔细地验证输出"

Part 3：手写核心逻辑（TypeScript）
把 Part 1 拆解的三个组件串起来，手写一个最小可用的记忆系统。不追求完整工程，聚焦每个模块最关键的设计逻辑。
3.0 项目结构

memory-system/├── src/│ ├── types.ts # 核心类型定义│ ├── token-counter.ts # Token 估算器│ ├── budget-manager.ts # Token 预算管理器│ ├── claude-md-loader.ts # CLAUDE.md 分层加载器│ ├── prompt-builder.ts # 系统提示构建器│ ├── memory-store.ts # 情景记忆存储（对话压缩）│ ├── memory-system.ts # 统一入口：组装所有组件│ └── index.ts # 使用示例├── package.json└── tsconfig.json
3.1 Token 估算：不需要精确，只需要方向
记忆系统需要一个 Token 计数器来感知预算。精确计数依赖 tiktoken 或模型的 tokenizer API，但在设计阶段，一个简单的字符估算就够用了。
核心思路：英文约 4 字符/token，中文约 1.5 字符/token。区分CJK字符是因为中文的信息密度远高于英文。

class TokenCounter { private readonly CJK_REGEX = /[一-鿿㐀-䶿豈-﫿]/g;  count(text: string): number { const cjkChars = (text.match(this.CJK_REGEX) ?? []).length; const nonCjkChars = text.length - cjkChars; return Math.ceil(nonCjkChars / 4 + cjkChars / 1.5); }}
就这么简单。生产环境可以换成精确的 tokenizer，但接口不变——记忆系统只依赖 count(text: string): number 这个契约。
3.2 预算管理器：把数字变成指令
预算管理器只做一件事：监控 Token 使用率，在接近上限时生成自然语言警告。
设计关键在 formatForInjection()——它不是返回一个数字，而是返回一段模型能读懂的指令。三级阈值对应三种语气：

70% → ”Consider finishing current tasks before starting new ones.”85% → ”Avoid reading large files.”90% → ”Complete any in-progress writes NOW.”

class BudgetManager { // 三级阈值 private readonly THRESHOLDS = { approaching: 0.70, // 温和提示 critical: 0.85, // 明确限制 compacting: 0.90, // 紧急压缩 };  assess(used: number, total: number): TokenBudget { const pct = used / total; const level = pct >= 0.90 ? 'compacting' : pct >= 0.85 ? 'critical' : pct >= 0.70 ? 'approaching' : 'none'; return { used, total, percentage: pct, warningLevel: level }; }  // 核心：把数字状态翻译成模型能理解的指令 formatForInjection(budget: TokenBudget): string | null { if (budget.warningLevel === 'none') return null; const pct = Math.round(budget.percentage * 100); const remaining = budget.total - budget.used;  // 语气随严重程度递增 return `<context_budget status=”${budget.warningLevel}”>You have used ${pct}% (~${remaining.toLocaleString()} tokens remaining).${this.getAdvice(budget.warningLevel)}</context_budget>`; }  private getAdvice(level: string): string { switch (level) { case 'approaching': return 'Consider finishing current tasks first.'; case 'critical': return 'Avoid reading large files. Prioritize critical steps.'; case 'compacting': return 'Complete in-progress writes NOW. Do NOT start new operations.'; default: return ''; } }  // 计算消息历史的可用预算 = 总窗口 - 系统提示 - 输出预留 allocateForMessages(total: number, systemTokens: number, outputReserve: number): number { return Math.max(0, total - systemTokens - outputReserve); }}
为什么要翻译成自然语言而不是直接截断？ 这是 Claude Code 最深的设计洞察。直接截断会让模型"不知道自己丢了什么"，而自然语言指令让模型主动调整行为——它读到"Avoid reading large files"就真的会避开大文件。约束变成指令，模型变成执行者。
3.3 CLAUDE.md 加载器：路径即相关性
这部分在 Part 1 已经完整展示过。这里只强调一个设计要点：三层加载的拼接顺序。

// 加载顺序：global → project → directory// 拼接时标注来源，让模型知道每条规则的作用域layers.map(l => `<!-- CLAUDE.md [${l.scope}: ${l.filePath}] -->\n${l.content}`)
为什么标注来源？因为不同层的规则可能冲突。当全局规则说"用 tabs"而项目规则说"用 spaces"时，模型需要知道哪个优先级更高——越靠近项目目录的规则优先级越高。标注来源就是让模型能做出正确的优先级判断。
3.4 提示构建器：顺序即成本
PromptBuilder 的核心逻辑就是一个 build() 方法。它的关键不在于代码复杂度，而在于 parts.push() 的顺序：

build(config: SystemPromptConfig): string { const parts: string[] = [];  // ===== 固定层（永远不变 → 走 Prompt Cache）===== if (config.agentIdentity) parts.push(wrap('identity', config.agentIdentity)); if (config.codingPhilosophy) parts.push(wrap('philosophy', config.codingPhilosophy)); if (config.toolUsageRules) parts.push(wrap('tool_rules', config.toolUsageRules));  // ===== 条件层（按需变化 → 不影响固定层缓存）===== if (config.claudeMdContent) parts.push(wrap('project_rules', config.claudeMdContent)); if (config.gitStatus) parts.push(formatGitStatus(config.gitStatus)); if (config.skillsIndex) parts.push(formatSkillsIndex(config.skillsIndex)); if (config.tokenBudget) parts.push(budgetManager.formatForInjection(config.tokenBudget)); if (config.episodicMemory) parts.push(wrap('history', config.episodicMemory));  return parts.join('\n\n');}
三个细节值得注意：
XML 标签 wrap()：<identity>、<project_rules> 这些标签不是装饰——它们帮助模型识别不同段落的边界和语义角色，比纯文本分隔线有效得多。

Skills 只注入索引：不注入 skill 的完整定义，只给名字和描述。模型看到索引后需要时才通过工具加载。这和浏览器的"懒加载"是同一个思路。

预算注入在最后：Token 预算是每次都变的值，放在最后面，永远不会破坏前面的缓存。

3.5 情景记忆：Claude Code 不做的事
Claude Code 没有情景记忆——每次对话都是全新的。但我们可以扩展，加入对话压缩机制。
设计思路很简单：定期把旧消息压缩成摘要，摘要代替原文留在上下文中。

对话轮次 1-10 → [LLM 压缩] → ”用户重构了 LRU 缓存，使用双重链表方案”对话轮次 11-20 → 保持原文（最新消息）
核心的压缩触发逻辑：

class MemoryStore { private entries: MemoryEntry[] = []; // 已压缩的记忆 private pendingMessages: Message[] = []; // 待压缩的消息 private compactionThreshold = 4000; // token 阈值  shouldCompact(): boolean { const pendingTokens = this.tokenCounter.countMessages(this.pendingMessages); return pendingTokens >= this.compactionThreshold; }  storeCompaction(summary: string): void { this.entries.push({ id: `mem_${Date.now()}`, summary, tokenCount: this.tokenCounter.count(summary), createdAt: Date.now(), importance: 0.5, }); this.pendingMessages = []; // 清空待压缩队列  // 超过上限时，淘汰重要性最低的 if (this.entries.length > 20) { this.entries.sort((a, b) => b.importance - a.importance); this.entries = this.entries.slice(0, 20); } }  // 注入系统提示时，按时间顺序拼接所有摘要 getSummaryForInjection(): string { return this.entries .map(e => `[${new Date(e.createdAt).toISOString()}] ${e.summary}`) .join('\n'); }}
这里的关键决策：摘要应该由 LLM 生成，不是简单截取。用 claude-haiku-4-5 这种小模型做压缩，成本低效果好。prompt 可以是："Summarize the following conversation concisely, preserving key decisions and file changes."
3.6 组装：buildContext() 的完整流程
所有组件串起来后，对外只暴露一个 buildContext() 方法。它的执行流程就是一个清晰的 pipeline：

buildContext(cwd, gitStatus) │ ├─ 1. claudeMdLoader.load(cwd) // 加载项目规则 │ ├─ 2. memoryStore.getSummaryForInjection() // 获取历史摘要 │ ├─ 3. promptBuilder.build(config) // 构建系统提示（不含预算） │ ↓ │ tokenCounter.count(basePrompt) // 计算系统提示 token 数 │ ├─ 4. budgetManager.allocateForMessages() // 算出消息可用预算 │ ↓ │ fitMessagesToBudget(messages, budget) // 从最新往前，裁剪到预算内 │ ├─ 5. budgetManager.assess(totalUsed) // 评估最终预算状态 │ ↓ │ 如果 warningLevel != 'none' │ → 重新 build() 含预算警告的系统提示 │ └─ 6. 返回 { systemPrompt, messages, budgetStatus }
最关键的细节在第 4 步：消息裁剪策略是从最新的消息开始保留，往旧的丢弃。这比 FIFO 丢弃更符合直觉——Agent 最需要的是最近的上下文，而不是最早的。
3.7 使用示例

const memory = new MemorySystem({ contextWindow: 200_000, agentIdentity: 'You are a helpful coding assistant.', codingPhilosophy: 'Prefer editing existing files. Follow project code style.', toolUsageRules: 'Use Read before Edit. Run type check after changes.', skills: [ { name: 'code-review', description: 'Review code changes', trigger: 'When reviewing a diff' }, ],}); // 添加对话memory.addMessage({ role: 'user', content: '帮我重构 LRU 缓存', timestamp: Date.now() });memory.addMessage({ role: 'assistant', content: '好的，我先看当前实现...', timestamp: Date.now() }); // 检查是否需要压缩if (memory.shouldCompact()) { const summary = await llm.summarize(memory.getPendingMessages()); memory.storeCompaction(summary);} // 构建完整上下文 → 直接喂给 LLMconst context = await memory.buildContext(process.cwd(), gitStatus);// context.systemPrompt → 系统提示（含缓存优化 + 预算警告 + 历史摘要）// context.messages → 裁剪后的消息历史
Part 4：扩展方向
上面的最小实现覆盖了 Claude Code 的核心设计。如果你想进一步魔改，几个清晰的方向：
扩展一：用 LLM 做记忆压缩
上面的 storeCompaction() 接受一个 summary 参数，实际项目中应该让小模型生成：

async function compactWithLLM(messages: Message[], llm: LLMClient): Promise<string> { const response = await llm.chat({ model: 'claude-haiku-4-5', // 用便宜的小模型 messages: [ { role: 'system', content: 'Summarize concisely, preserving key decisions and file changes.' }, { role: 'user', content: messages.map(m => `[${m.role}]: ${m.content}`).join('\n') }, ], }); return response.content;}
扩展二：给记忆加重要性评分
不是所有消息都值得记住。可以在 addMessage() 时评估：

function assessImportance(message: Message): number { let score = 0.5; if (message.content.includes('remember') || message.content.includes('记住')) score += 0.3; if (/\b[\w-]+\.\w{1,4}\b/.test(message.content)) score += 0.1; // 包含文件路径 if (message.content.includes('```')) score += 0.1; // 包含代码块 return Math.min(1, score);}
扩展三：接入向量存储做语义检索
Claude Code 的路径相关性做不到的事——"这个任务需要什么历史经验"——可以用向量检索补上：

class SemanticMemoryStore extends MemoryStore { async searchRelevantMemories(query: string, topK = 5): Promise<MemoryEntry[]> { const embedding = await this.embedder.embed(query); const results = await this.vectorStore.search(embedding, topK); return results.map(r => r.metadata as MemoryEntry); }}
总结
这篇文章拆解了 Claude Code 记忆系统的三个核心组件，并用 TypeScript 实现了核心逻辑。
核心设计原则回顾：
原则
实现
为什么
固定层在前
parts.push() 顺序
走 Prompt Cache，降低 90% 的输入成本
路径即相关性
findGitRoot() 三层加载
零基础设施成本，无需向量数据库
约束 → 指令
formatForInjection()用自然语言驱动模型行为调整
预算感知
BudgetManager 三级阈值
Agent 主动调整计划，避免上下文溢出
和 Claude Code 的区别：我们的实现额外加入了情景记忆（MemoryStore），这是 Claude Code 刻意不做的事情。Claude Code 认为对话历史不需要跨会话保留——每次对话都是全新的。但如果你需要跨会话记忆，上面的扩展方向已经给出了清晰的路线。