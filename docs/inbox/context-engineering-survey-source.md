# Agent Coding 上下文工程管理方案 — 全网资料调研报告

> 调研日期：2026-08-10
> 覆盖范围：Anthropic / OpenAI / Google 官方资料、Claude Code / Cursor / Codex / Windsurf / Cline / Aider 等工具实践、记忆系统生态（Mem0 / Zep / Letta）、中英文社区深度文章
> 用途：为 Agent Coding（AI 编程智能体）的上下文工程（Context Engineering）建设提供完整资料地图

---

## 一、为什么「上下文工程」成为 Agent Coding 的核心

2023 年开发者学的是 **Prompt Engineering（提示词工程）**——如何把指令写好；2025-2026 年行业已转向 **Context Engineering（上下文工程）**——管理「模型在每一轮推理时看到什么」。

**Anthropic 的官方定义**（《Effective context engineering for AI agents》）：

> Context engineering 指为 LLM 推理期间**策划并维护最优 token 集合**的策略集，涵盖 System Prompt、工具定义、MCP、外部数据、消息历史等所有可能进入上下文的要素。与一次性写好提示词不同，上下文工程是**迭代式**的——每次决定"把什么传给模型"都是一次策划。

核心原因（为什么 Agent 时代必须做上下文工程）：

| 原因 | 说明 |
|------|------|
| **有限注意力预算** | Transformer 是 n² 的 pairwise attention，token 越多，每个 token 分到的注意力越少；上下文越长，信息召回精度越低（needle-in-a-haystack 测试证实） |
| **Context Rot（上下文腐化）** | 上下文填充到 70%-80% 时推理质量就开始下降（不是等窗口满才崩）；模型开始遗忘早期指令、重复劳动、重新引入已修复的 bug |
| **Lost in the Middle** | Liu et al.（TACL）证实：相关信息位于上下文**中段**时模型召回率大幅下降（多文档 QA 中可掉 30+ 个百分点），位置两端（头部/尾部）表现最好 |
| **成本失控** | Agent 是输入密集型负载：Manus 报告输入/输出 token 比约 100:1；每轮推理都重发全部历史，未优化的长任务会话成本可呈数量级增长 |
| **失败模式复合** | 上下文污染（poisoning）→ 分心（distraction）→ 混淆（confusion）→ 冲突（clash），四种失败模式会互相强化 |

**结论：上下文必须被当作「边际收益递减的有限资源」管理。大窗口 ≠ 可以乱塞。** 窗口是工作集（working set），不是数据库。

> 中文社区比喻：「Prompt Engineering 是教厨师做菜的口诀，Context Engineering 是配备齐全的厨房——食材、刀具、菜谱、计时器，一切就位，厨师只需要发挥手艺。」（CSDN《上下文工程实战指南 2026》）
> 另一比喻：「模型不是缺资料，而是缺一张干净的工作台。Context Engineering 做的就是帮模型把工作台整理干净。」（掘金）

---

## 二、理论基石：关键概念速查

### 2.1 Context Rot（上下文腐化）

- 定义：随上下文窗口填充，模型推理质量渐进式下降的现象，是 Transformer 注意力机制的固有特性
- 触发阈值：约 **70%-80% 窗口容量**（业界经验与测试一致指向该区间）
- 症状：矛盾前期决策、重复生成已存在的代码、遗忘开局约束、重新引入已修复的 bug
- 对策：主动压缩（compaction）+ 结构化状态外置

### 2.2 Context Drift（上下文漂移）

- 定义：agent 的「人设/目标/约束」因累积对话历史逐渐偏离原始意图
- 例子：以「性能优先的后端工程师」开局，30 轮调试日志后变成「只顾眼前错误的调试助手」
- 对策：定期重置/强化 system prompt；用 /compact 或新开会话

### 2.3 四大失败模式（Sources: Anthropic / LangChain / Chroma）

| 模式 | 现象 | 触发场景 |
|------|------|----------|
| Context poisoning | 一次幻觉/错误进入上下文后被当成事实扩散 | 未验证的工具输出回流历史 |
| Context distraction | 模型被大量历史分心而非基于当下推理 | 超长对话日志 |
| Context confusion | 无关内容干扰响应 | 整篇文档/过多工具直接倾倒 |
| Context clash | 矛盾信息导致推理不一致 | 过期记忆混入新状态 |

### 2.4 Token 预算管理（Token Budget）

社区给出的 128K 窗口预算参考框架（toolhalla.ai 2026）：

| 组件 | 预算占比 |
|------|----------|
| System prompt + 规则 | 3% |
| 工具定义（5-8 个） | 2% |
| Few-shot 示例 | 3% |
| RAG 检索上下文 | 15% |
| 对话历史（已压缩） | 25% |
| 工作记忆（working memory） | 28% |
| 安全缓冲 | 22% |

本地小模型（32K）建议：System 5% + Tools 3% + 检索 16% + 历史 25% + 工作记忆 31% + 缓冲 20%；**Compaction 在 32K 下是刚需**（10-15 次复杂工具交互即触顶）。

---

## 三、主流工具上下文管理机制全景对比

### 3.1 Claude Code（Anthropic）—— 体系最完整的参考系

Claude Code 的上下文管理由多个层级构成，是业界公认的最佳实践模板：

**① 记忆文件体系（Memory）**
- `CLAUDE.md`（用户/团队写的持久指令）——按作用域分五层，加载顺序（后加载覆盖先加载）：
  1. 企业托管策略：macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`
  2. 用户级：`~/.claude/CLAUDE.md`
  3. 项目级：`./CLAUDE.md` 或 `./.claude/CLAUDE.md`（团队共享，进 Git）
  4. 本地级：`./CLAUDE.local.md`（个人，gitignore）
  5. 路径级规则：`.claude/rules/*.md`（带 glob 作用域，按需加载）
- `@import` 语法支持拆分子文件（递归最深 5 层）
- **Auto Memory（自动记忆）**：Claude 自己在 `~/.claude/projects/<项目>/memory/MEMORY.md` 记录观察到的模式（命令、调试洞见、隐含约定），每次会话自动加载前 200 行/25KB
- 最佳实践：CLAUDE.md 目标 **<200 行**（宽松建议 <300）；只放「团队约定 + 构建命令 + 红线」，领域知识用引用而非内联；`/init` 自动生成初始文件（生成后建议删掉大半，因为它会包含模型本就能从代码推断的废话）

**② Skills（技能，按需加载的杀手锏）**
- 渐进式披露（Progressive Disclosure）三阶段：
  - 阶段 1：仅加载 YAML frontmatter 的 name + description（约 100 token/技能）
  - 阶段 2：判定相关时加载完整 SKILL.md（<5K token）
  - 阶段 3：用到时加载配套脚本/资源
- 10 个技能不激活时只付 ~1,000 token，而非全量 50,000+ —— 社区称 **98% 的 token 节省**
- 技能描述（description）写得好不好直接决定能否被触发

**③ Hooks（钩子，零 token 的自动化）**
- PreToolUse / PostToolUse / UserPromptSubmit / Stop / PreCompact 等生命周期事件触发 shell 命令
- 典型用法：Write 后自动 prettier、Bash 前拦截危险命令（rm -rf）、Stop 时发通知
- **关键价值：Hooks 是「强制执行的规则」，不占 context、零 token，比让模型"记住"可靠得多**
- **PreCompact hook**：在自动压缩前保存关键指令，官方称可降低压缩导致的关键信息丢失约 30%

**④ Subagents（子代理，上下文隔离）**
- 独立 200K 上下文窗口，主 Agent 委派耗 token 的子任务，子代理只回传结论（约 1-2K token 高密度摘要）
- 主上下文只多了一句结论，而不是整个思考过程 —— 长对话救星

**⑤ 会话级工具**
- `/compact`：手动压缩上下文，恢复约 70% 空间
- `/clear`：清空历史 100% 恢复
- `/cost`、`/status`、`/context`：监控 token 用量与上下文构成
- Plan mode（Shift+Tab）：只分析不改动，用轻量模型推理，token 减半（实测架构分析省 51%、代码审查省 53%）
- 自动压缩阈值可配置（默认约 98%，建议降到 85% 提前触发，可减少 2.3 秒/次的平均响应延迟）

**⑥ 官方降本技巧（Anthropic 工程博客）**
- 自定义 statusline 持续显示上下文用量
- `.claudeignore` 排除不需要的文件
- 精简工具列表、缩短工具描述
- 给 Claude 可运行的验证手段（测试/构建/lint），闭环自检减少无效来回

### 3.2 Cursor —— Rules / Skills / Hooks 三件套

**Rules（规则，静态上下文）**：`.cursor/rules/*.md`，四种应用方式：
- Always（每次对话都包含）
- Auto（agent 判断何时相关）
- Glob 文件级（如 `src/components/**/*.tsx`）
- Manual（@提及才用）
- 旧式 `.cursorrules` 仍兼容；规则建议 **<500 行**，拆小文件、扁平目录
- 最佳实践：规则里引用文件（@filename）而非复制内容；只有 agent 反复犯错时才加规则

**Skills（技能，动态能力）**：`SKILL.md` 封装领域知识/工作流，按相关性动态加载，与 Rules「永远在场」互补——**Rules 保持窗口精简，Skills 按需注入专门能力**

**Hooks**：`.cursor/hooks.json`，支持 stop hook 实现「持续迭代直到测试全绿」的循环模式（grind.ts 示例）

**其他最佳实践**（Cursor 官方 agent-best-practices）：
- 新对话引用 @Past Chats 而不是复制粘贴整个旧对话
- 对话变臃肿时果断新开
- 规则提交 Git 团队共享；看到 agent 犯错就更新规则，可在 GitHub issue @cursor 让 agent 自己改规则

### 3.3 OpenAI Codex —— 缓存敏感型实践的典型

**AGENTS.md 支持**：项目指令默认合并上限 **32 KiB**（`project_doc_max_bytes` 可调）；全局在 `~/.codex/AGENTS.md`，临时覆盖 `AGENTS.override.md`；`CODEX_HOME` 可切换干净环境

**压缩配置**（社区实测，防止长上下文高价计费）：
```toml
model_context_window = 272000
model_auto_compact_token_limit = 240000
model_reasoning_summary = "concise"
```
- 在 272K 高价区间前强制压缩；上下文到 60% 就手动 `/compact`；任务切换就开新会话

**Codex 的 compaction 机制**（danielvaughan 分析）：
- 单层 handoff 摘要：提取最近用户消息（~20K token 上限）→ LLM 生成结构化摘要（进度/决策/约束/剩余任务/关键数据）→ 用摘要替换所有 assistant + tool 轮次，用户消息原样保留
- 支持服务端压缩（OpenAI 模型，compact_threshold 参数）与客户端压缩（本地模型）
- 注意：Codex 是**一刀切压缩**（all-or-nothing），不如 Claude Code 的三层渐进（工具结果裁剪 → 缓存优化 → 结构化摘要）；因此 **「避免触发压缩」比依赖压缩更好**

**Codex 省 token 的实战原则**（社区共识）：
1. **任务 = 会话**：一个任务一个线程（one thread per task），修完 A bug 做 B 功能请新开；`/fork` 探索分支不污染主线
2. **@文件名 精准引用** 而非全局扫描（surgical @-mentions）
3. **同会话不切模型**（切换模型 = 缓存作废全价重算）
4. **Prompt cache 保鲜**：缓存约 5 分钟 TTL，用占位符保持前缀活跃，命中后成本约 1/10
5. Quick Chat 不耗 token，先确认再进正式任务
6. 工具结果占 token 大头（实测调试会话中约 81%），控制 agent 读哪些文件、何时读是最大杠杆

### 3.4 其他工具速览

| 工具 | 上下文机制要点 |
|------|----------------|
| **Windsurf** | 支持 AGENTS.md / `.windsurfrules`；Cascade 记忆（MCP 记忆 + 项目记忆）；官方建议规则精简、引用不复制 |
| **Cline** | `.clinerules/` + 自动兼容 `.cursorrules` / `.windsurfrules` / AGENTS.md；**conditional rules**（frontmatter 写 glob paths，匹配才激活）；Auto Compact 利用 prompt cache 成本≈一次普通工具调用 |
| **Aider** | **Repo Map（仓库地图）**：用树状结构 + 重要性评分把仓库关键文件概览注入上下文，显著降低工具结果 token 开销；支持 AGENTS.md |
| **GitHub Copilot** | `.github/copilot-instructions.md`；支持 AGENTS.md；官方建议覆盖 commands/testing/structure/style/git-workflow/boundaries 六类 |
| **Gemini CLI / Google Jules / Amp / Factory / CodeRabbit** | 均原生支持 AGENTS.md（跨工具标准的力量） |

---

## 四、指令文件体系标准（静态上下文层）

### 4.1 AGENTS.md —— 开放标准（当前最重要）

- **治理**：由 Linux Foundation 下的 **Agentic AI Foundation** 托管（原由 OpenAI Codex、Amp、Google Jules、Cursor、Factory 协作制定）
- **采纳度**：GitHub 60,000+ 仓库；OpenAI 内部 monorepo 用了 **88 个** AGENTS.md
- **支持方**：Claude Code、OpenAI Codex、Google Jules、Gemini CLI、GitHub Copilot、Cursor、Windsurf、Cline、Aider、Amp、Factory、CodeRabbit……
- **核心定位**：项目级「README for AI agents」——回答"这个项目怎么做"而不是"这个项目是什么"
- **加载规则**：仓库根目录一份；monorepo 用嵌套（子项目各一份）；agent 读目录树中最近的，最近者优先；用户聊天提示覆盖一切
- **内容建议**（~100 行指针式，不内联大文档）：
  - 项目是什么（2-3 句）+ 构建/测试命令
  - 非显然约束（"用 bun 不用 npm"）
  - 代码风格、Git 约定、红线边界（Always / Ask first / Never 三段式）
  - 领域文档用引用（"改支付代码前先读 docs/payment-architecture.md"）
- **与工具私有格式的关系**：AGENTS.md 是跨工具通用层；CLAUDE.md（hooks 等 Claude 特有）、.cursorrules（Cursor 特有）作补充

### 4.2 各类指令文件对比

| 特性 | AGENTS.md | CLAUDE.md | .cursorrules | copilot-instructions.md |
|------|-----------|-----------|--------------|--------------------------|
| 跨工具 | ✅ 所有主流 | ❌ Claude 系 | ❌ Cursor | ❌ Copilot |
| 格式 | Markdown | Markdown | Markdown | Markdown |
| Monorepo | 嵌套（最近优先） | 嵌套 | 单根文件 | 单文件 |
| 治理方 | Linux Foundation | Anthropic | Cursor | GitHub |

### 4.3 编写纪律（多来源共识）

- **小**：能放一屏（~100 行）最佳；CLAUDE.md <200 行；每条规则必须是"可执行的指令"，避免"要写好代码"这类废话
- **引用优于内联**：用 `@file` 指向样例/规范，防止文件过时
- **犯错驱动增长**：只在 agent 反复犯同样错误时加规则（"从简单开始，不要过度优化"）
- **元数据化**：给上下文文件加 frontmatter（last_updated / owner / scope），当成代码管理，定期 review + prune
- **进 Git**：团队共享，版本控制，让所有人（人和 agent）看到同一套规则

---

## 五、动态上下文管理技术（核心方法论）

### 5.1 Compaction（压缩）—— 三层递进策略

综合 Manus（Lance Martin webinar）、Claude Code、OpenAI Codex 实践的**三层压缩策略**（cuiliang.ai 总结）：

| 层级 | 策略 | 说明 |
|------|------|------|
| **Layer 1: Raw** | 完整保留 | 最新工具调用结果不压缩——模型下一步决策高度依赖最近 observation |
| **Layer 2: Compact** | 精简结构 | 较早的历史工具输出做结构化摘录（保留路径、ID、错误码、关键数字、决策点） |
| **Layer 3: Summarize** | 语义摘要 | 更早的对话轮次压成高密度叙事摘要（目标、子目标、关键决策及理由、当前状态、待办） |

**实现方式对比**：
- 滚动摘要（rolling summary）：阈值触发，摘要替换原始历史
- 分层摘要（hierarchical）：递归摘要（先 1-50 轮，再 1-100 轮含摘要）
- Map-Reduce 摘要：并行分块摘要再合并（Google Gemini 生产流水线方案）
- **触发阈值建议**：60-75% 容量即压缩，而非等 98% 触顶（上下文腐烂从 70% 就开始）

**压缩的代价（必须知道）**：
- Factory.ai 对 36,611 条生产消息的基准测试：Anthropic / OpenAI / Factory 三家摘要方法在「工件追踪（哪些文件被改）」上仅得 2.19-2.45/5.0 —— 自由摘要会静默丢失精确技术细节
- ACON 论文（arxiv:2510.00615）：naive 摘要（FIFO/通用提示）在多步任务上精度严重退化
- 缓解：压缩前用 PreCompact hook 保存关键状态；优先避免触发压缩（把任务拆小）

### 5.2 Selective Eviction（选择性淘汰）

- **LRU**：丢最旧的工具结果
- **重要度打分**：按累计注意力权重（heavy hitter）、KV 向量 L2 范数、注意力熵排序，只保留 Top-K（KV cache 压缩研究路线：NACL / Ada-KV）
- **去重去噪**：同一文件重复读取只留最新；已解决的错误消息直接清除（Claude Code 的 Pi 插件）；工具输出格式化成精简摘要
- 零合成成本、无损保留，但需要启发式规则支撑

### 5.3 Prompt Caching（提示缓存 / KV Cache）—— 省钱第一杠杆

**原理**：LLM 处理输入时计算 KV 张量，是推理最贵部分。若新请求与前序请求**前缀逐字节相同**，直接复用缓存，只算新增部分。

**各家实现与折扣**：
| 厂商 | 模式 | 优惠 |
|------|------|------|
| Anthropic | 显式 cache_control 断点；TTL 5min-1h | 缓存读 0.1x（省 90%）；写 1.25-2x |
| OpenAI | 自动缓存（≥1,024 token 前缀） | 缓存输入约 $0.175/M vs $1.75/M |
| Google | 命名缓存对象（需手动管理 TTL） | 可配 |

**「不可变前缀」架构纪律**（三个毁缓存的坑）：
1. 会话中途增删/改工具定义（工具 schema 在前缀里，一变全失效）
2. 中途切换模型（模型特定指令在前缀）
3. 前缀里放动态内容（时间戳、request ID、配置 —— 每次请求都缓存全毁）

**正确布局**：静态前缀（system prompt → 工具定义 → 历史）+ 动态后缀（当前用户消息、工具结果）。静态在前、多变在后；user 特定内容放共享内容之后。

**收益实测**：system-prompt-only 缓存策略跨厂商实现 41-80% 成本下降、TTFT 提升 13-31%；Thomson Reuters 管道降 60%；某 SaaS 月费 $15,000→$4,500；最高 90%。Manus 称 KV cache 命中率是「生产级 agent 最重要的单一指标」。

**语义缓存（Semantic Caching）**：按 embedding 相似度（cosine >0.95）命中，缓存"意图"而非字面，适合高频重复问答（客服 FAQ），命中率上限更高但实现复杂、牺牲新鲜度。

**自托管**：vLLM `--enable-prefix-caching` / SGLang RadixAttention / LMCache；KVFlow 论文提出面向多 agent 调度的工作流感知淘汰，可提速 2.19x。

### 5.4 Just-in-Time 按需加载

- **渐进式披露（Progressive Disclosure）**：先看文件名/目录结构/时间戳建立信息布局，层层探索，不一次性全加载（Claude Code 的 Skills 就是这个思想）
- 维护轻量引用句柄（文件路径、查询关键词、链接），需要时才动态拉全文
- 工具懒加载（Tool Retrieval）：向量检索选出当前任务最相关的 Top-5 工具挂载，而不是把所有工具描述塞进 system prompt
- 混合策略：代码库分析类（动态探索多）以 JIT 为主；法律文书类（上下文稳定）以预检索为主

### 5.5 工具结果过滤（Observation 清洗）

- 工具默认返回**摘要**：完整结果写入文件，上下文只留关键错误、路径、ID、计数、下一步建议
- 日志只给错误片段、表格只给相关行、网页只给正文摘要+链接、数据库只给必要字段
- 设计工具时就让输出结构化、精简（"返回 200 个最相关词+来源 URL 比返回 5,000 词抓取文本好"）
- **Prompt Injection 防御**：外部内容（网页/文件/DB）进入上下文前做沙箱清洗，防止夹带伪造指令

### 5.6 四大策略总纲（Write / Select / Compress / Isolate）

生产级 agent 收敛于四招组合拳（lushbinary / luminhkhuong 等）：

| 策略 | 做什么 | 何时用 |
|------|--------|--------|
| **Write（外置）** | 把计划/决策/中间结果写入外部存储（scratchpad、任务清单、NOTES.md、DB），窗口只留指针/摘要 | 每个主要步骤之后 |
| **Select（按需检索）** | 只动态加载当前步骤相关文件/事实/工具（向量检索、AST 节点、API schema） | 大型代码库（>50 文件）长任务；省 80-95% token |
| **Compress（压缩）** | 主动在 60-70% 容量时压缩最旧部分历史 | 每个长任务 |
| **Isolate（隔离）** | 子代理独立上下文处理子任务 | 子任务不需要父代理全部历史时 |

---

## 六、外部记忆系统（跨会话上下文）

Agent 上下文工程的另一半：**把上下文从"对话内"扩展到"对话外"**。

### 6.1 三类主流架构

| 平台 | 架构 | 核心卖点 | 适合场景 |
|------|------|----------|----------|
| **Mem0** | 向量优先（Vector-first）：从对话抽取原子事实存向量库，每轮前语义检索 | 上手最快（30 秒接入）、框架中立（21 框架 / 20 向量后端）、四层记忆（对话/会话/用户/组织） | 个性化助手、聊天机器人；AWS Agent SDK 独家记忆供应商 |
| **Zep / Graphiti** | 时间知识图谱（Temporal KG）：实体+关系+**事实失效时间** | 能回答"1 月谁负责项目？"与"现在谁负责？"；事实过期自动失效不覆盖 | CRM 副驾、合规 agent、实体关系频繁变化的业务 |
| **Letta（原 MemGPT）** | OS 式分层：core memory（窗口内）+ recall memory（可检索历史）+ archival memory（长期存储） | Agent 自己用工具决定 promote/archive，显式控制什么留在上下文 | 长生命周期自治 agent（数天/数周运行） |
| **LangMem** | LangGraph 原生记忆原语 | 与 LangGraph 深度集成 | 已用 LangGraph 的团队 |
| **Cloudflare Agents** | 会话历史 + context memory + 压缩 + 搜索 | Cloudflare 原生 | Cloudflare Workers 生态 |

### 6.2 分层记忆架构（工程落地标准模型）

| 层级 | 内容 | 生命周期 | 载体 |
|------|------|----------|------|
| In-context 记忆 | 当前任务状态、最近工具输出 | 当前窗口 | 对话本身 |
| 短期记忆（Session） | 最近 5 轮 + 关键实体 ID | 会话结束 | Redis 缓冲 |
| 中期记忆（Task） | 跨会话进行中任务（ID、状态机、最后操作时间） | 任务完成 | Redis/DB 结构化对象 |
| 长期记忆（User/Org） | 用户偏好、组织知识 | 持久 | 向量库 + 加密 DB |
| 工作区记忆 | 文件、代码、笔记等中间产物 | 随项目 | 文件系统 |

**实践规则**（agdex.ai 2026）：
- 记忆写入**异步化**（不阻塞响应）；记忆提取 + 存储放后台任务
- 记忆 TTL：情景记忆设过期（如 1 年），语义记忆永存
- 写入前一致性校验，保留 `{old_value, new_value, timestamp}` 可回滚（避免"把预算从 5 万改成 8 万"直接覆盖无法追溯）
- 评测基准：**LoCoMo、LongMemEval、BEAM**

### 6.3 选型速查

| 场景 | 推荐 |
|------|------|
| 个人助手 / 聊天机器人 | Mem0（托管云最快） |
| 企业 CRM / 客服（实体关系+时间） | Zep（自托管） |
| 长期自治 agent | Letta |
| 强合规（GDPR/HIPAA） | 自建 + pgvector |
| 多 agent 系统 | Mem0 共享记忆层 |
| 延迟/拓扑强控制 | Redis 自建 |

---

## 七、架构模式：上下文组装与隔离

### 7.1 RAM vs Disk 心智模型

把上下文窗口当 **RAM**（快、有限、会话间清空），外部存储（DB、文件系统、向量库）当 **Disk**（便宜、大、需显式检索）。好的上下文工程在每一步决定：现在哪些该进 RAM，哪些留 Disk 等需要时取。静态层（system/工具定义/规则）放前缀并缓存；动态层（用户输入/工具输出/检索结果）放后缀保持最小。

### 7.2 分层组装流水线（Two-Pass Assembly）

1. **第一遍**：加载静态上下文（system prompt、缓存指令、长期摘要）→ 可前缀缓存
2. **第二遍**：注入动态上下文（当前任务状态、新鲜检索结果、最近历史）→ 最小化
- 附带收益：调试定位容易——行为异常要么是静态配置问题（prompt 工程层），要么是动态状态问题（检索/历史管理层）

### 7.3 Subagent / 多智能体上下文隔离

- **Subagent 模式**：主 agent 只负责计划与综合；子 agent 消耗大量 token 做深度检索/局部分析/实验验证，只回传 **1,000-2,000 token 高密度结论**，避免主上下文被细节淹没
- **多智能体上下文传递**（CSDN 总结）：
  - 共享 Scratchpad：所有 agent 读写同一状态文件（紧耦合协作）
  - 消息总线：agent 异步传递结构化消息（松耦合流水线）
  - Handoff 协议：序列化完整状态 vs 只传摘要——直接影响下游理解质量
  - 角色隔离：子 agent 只看与自己任务相关的上下文切片，orchestrator 保留全局视图（省 token + 防信息泄漏 + 防角色混淆）

### 7.4 长任务持久化三件套

1. **Compaction**：LLM 总结历史，保留关键决策和未解决问题
2. **Structured Note-taking（结构化笔记）**：维护 `TODO.md` / `progress.md` / `known_issues.md` / `decisions.md`，每轮结束更新状态文件，而不是把状态留在对话里
3. **Sub-agent 分层**：子任务独立上下文 + 摘要回传

### 7.5 监控与评测（没有指标就是玄学调参）

**context review 指标**：单次任务 prompt tokens、工具结果 tokens、重复内容比例、压缩次数、读取文件数、无效检索次数
**缓存健康度**：`cache_read_input_tokens / 总输入` 命中率（生产 >80%）；缓存写入成本 <5%
**上下文健康度仪表盘**（CSDN 案例）：
- Context Bloat Rate（会话新增 token / 有效信息密度）
- Memory Recall Accuracy（检索信息被实际引用的比例）
- Isolation Breach Count（跨隔离域访问次数）
- Compression Fidelity Score（压缩前后关键事实保留率）
- 任一指标连续 3 天偏离基线 ±15% 触发自动调优
**回放评测**（掘金）：拿真实任务记录回放，检查：关键约束是否丢失？RAG 引用是否支撑结论？记忆是否错记？token 成本是否下降？任务成功率是否提升？

---

## 八、中文社区实践精华

### 8.1 掘金《Context Engineering 不是写更长 Prompt，而是管理 Agent 的注意力预算》

最小可落地六件事：
1. **定义上下文预算**（如 20K 分配：system 2K + 任务 1K + 近期历史 3K + RAG 8K + 工具结果 4K + 余量 2K）
2. 硬约束做成**结构化 State**，不依赖摘要
3. **RAG 和 Memory 分开**：外部文档进 RAG，用户偏好/连续性进 Memory，当前执行进 State
4. **工具结果先过滤再进上下文**
5. 长任务用 **compaction + 结构化笔记**
6. **回放评测**

### 8.2 CSDN《上下文工程实战指南 2026》

- 六板块：System Prompt（Markdown 强制分区 + Goldilocks zone）、User Prompt、Memory、RAG & Tools、Structured Output、Token 优化
- 五方案：动态信息按需挂载（工具懒加载+Observation 摘要）、Token 预算降级策略（三级优先级：早期历史→RAG 背景→System 核心永不丢）、Just-in-Time 加载、长任务持久化（compaction/笔记/sub-agent）、静态规则结构化编排
- 核心原则：上下文是**系统输出**不是静态配置；高信噪比优于高信息量；上下文需要**代谢机制**；从最简方案开始

### 8.3 2048ai《Context Engineering 解读》

研发团队上下文治理清单：每类上下文设预算 → 工具默认返回摘要 → 让 Agent 学会记笔记（TODO/progress/known_issues/decisions）→ 建立 context review 指标 → 不同任务不同策略。并提醒：上下文工程不是"少给信息"，目标是**高信号**而非短；判断标准是任务成功率/可复现性/错误类型，不是 token 数字。

### 8.4 头条/社区《Codex 省 token 神操作合集》

- `~/.codex/config.toml`：272K 前强制压缩（`model_context_window=272000`, `model_auto_compact_token_limit=240000`）
- 会话到 60% 就 /compact；任务切换开新会话；@文件名精准提问；同会话不切模型；删闲置 Skill/MCP；缓存 5 分钟保鲜期用占位符保持活跃；Quick Chat 不耗 token

---

## 九、从零搭建上下文管理体系 —— 落地路线图

按性价比排序（levelop.dev 建议的实施顺序）：

**第一阶段：打地基（最高杠杆，当天见效）**
1. 写一份 **AGENTS.md**（<100 行：项目简介、构建/测试命令、代码风格、红线边界）
2. 调好 **system prompt 的 altitude**（具体到能引导行为，抽象到不脆弱）
3. 精简**工具加载**（5-8 个、职责不重叠）

**第二阶段：控窗口（长任务开始触顶时）**
4. 配置 **auto-compact 阈值 85%** + PreCompact hook 备份关键状态
5. 开启**结构化笔记**纪律（progress.md / decisions.md）
6. 任务切分：**一个任务一个会话**

**第三阶段：省成本**
7. 设计**缓存友好前缀**：静态在前、动态在后、会话内不动工具列表/不切模型
8. 工具输出**默认摘要化**

**第四阶段：扩规模**
9. **Subagent 隔离**耗 token 子任务
10. 引入**外部记忆**（Mem0 起步 → 按需升级 Zep/Letta）

**始终记住的核心原则**：
- 上下文是有限资源，目标是「**下一步所需的最小高信号 token 集**」
- 从最简单的能工作的方案开始，根据失败模式逐步加机制（Anthropic 明确建议）
- 有监控有评测，否则一切都是玄学调参

---

## 十、参考资料汇总（全部链接）

### 官方一手资料
- Anthropic：《Effective context engineering for AI agents》https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic：《Claude Code best practices》https://anthropic.com/engineering/claude-code-best-practices
- Claude Code 官方文档《How Claude remembers your project》https://code.claude.com/docs/en/memory
- Cursor 官方《Agent best practices》https://cursor.ac.cn/blog/agent-best-practices
- Cursor 官方《Rules》文档 https://prod.cursor.com/help/customization/rules
- AGENTS.md 规范（Linux Foundation）https://agents.md

### 概念与综述
- MachineLearningMastery：《Effective Context Engineering for AI Agents: A Developer's Guide》https://machinelearningmastery.com/effective-context-engineering-for-ai-agents-a-developers-guide
- toolhalla.ai：《Context Engineering for AI Agents: The Complete Guide (2026)》https://toolhalla.ai/blog/context-engineering-ai-agents-2026
- Lushbinary：《Context Engineering for AI Agents: 2026 Production Guide》https://lushbinary.com/blog/context-engineering-ai-agents-production-guide
- luminhkhuong：《Context Engineering, Compaction & Advanced Vibe Coding》https://luminhkhuong.dev/technical-knowledge/ai-agents/context-engineering
- cuiliang.ai（中文）：《Context Engineering: Agent 架构师的核心手艺》https://cuiliang.ai/posts/prompt-caching-context-engineering

### 压缩与上下文腐化
- Zylos Research：《Agent Context Compaction for Long-Running Sessions》https://zylos.ai/en/research/2026-04-21-agent-context-compaction-long-running-sessions/
- MindStudio：《What Is Context Rot and How Does Auto-Compact Fix It?》https://www.mindstudio.ai/blog/context-rot-ai-agents-auto-compact-fix
- SFEIR Institute：《Context Management - Optimization Guide》https://institute.sfeir.com/en/claude-code/claude-code-context-management/optimization

### Prompt Caching
- usewire.io：《How prompt caching cuts AI agent costs by 90%》https://usewire.io/blog/how-prompt-caching-cuts-ai-agent-costs
- Zylos：《Prompt Caching for AI Agents: Architecture Patterns》https://zylos.ai/research/2026-02-24-prompt-caching-ai-agents-architecture
- AgentPatterns：《Prompt Caching: Architectural Discipline》https://www.agentpatterns.ai/context-engineering/prompt-cache-economics
- wangjun.dev（中文）：《4 techniques reduce token costs by 90%》https://wangjun.dev/2026/05/agentic-ai-how-to-save-on-tokens

### 记忆系统
- datapace.ai：《Mem0 vs Zep vs Letta vs LangMem》https://datapace.ai/blog/ai-agent-memory-tools-2026
- FrontierNews：《The Memory Wars》https://www.frontiernews.ai/news/article/the-memory-wars-how-ai-agents-are-learning-to-reme-43fa0582
- agdex.ai：《AI Agent Memory Systems in 2026》https://agdex.ai/blog/ai-agent-memory-systems-2026
- Supermemory：《Context Management Tools for LLM Chat》https://supermemory.ai/blog/best-context-management-tools-llm-chat/

### 工具实践细节
- vibecoding.app：《AGENTS.md Review: The Open Standard》https://vibecoding.app/blog/agents-md-review
- agentpatterns.ai：《AGENTS.md: Project-Level README》https://agentpatterns.ai/standards/agents-md
- danielvaughan：《Codex CLI Context Window Budget》https://codex.danielvaughan.com/2026/04/20/codex-cli-context-window-budget-token-management-large-codebases
- fanyamin.com（中文）：《用 Codex 怎么省 Token》https://www.fanyamin.com/codex-save-token.html
- codewithseb：《Claude Code Skills: The 98% Token Savings Architecture》https://www.codewithseb.com/blog/claude-code-skills-reusable-ai-workflows-guide
- softaverse（繁体中文）：《Claude Code 系列文 8 – 七大元件》https://www.softaverse.com/claude-code-components
- orchestrator.dev：《Claude Code & Agent Memory: Best Practices for 2026》https://orchestrator.dev/blog/2026-04-06--claude-code-agent-memory-2026/

### 中文社区
- 掘金：《Context Engineering 不是写更长 Prompt，而是管理注意力预算》https://juejin.cn/post/7640643117474201641
- CSDN：《Agent 上下文工程完全指南》https://blog.csdn.net/m0_63648885/article/details/161386204
- CSDN：《上下文工程实战指南 2026》https://mukebb.blog.csdn.net/article/details/160345588
- CSDN：《Agent 记忆系统设计与实现》https://blog.csdn.net/xx_nm98/article/details/162587493
- 2048ai：《Context Engineering 解读：Agent 可靠性靠上下文治理》https://2048ai.net/6a573f5e10ee7a33f28dc85d.html
- 掘金：《在 Codex 里开新会话，哪些内容会自动进上下文？》https://juejin.cn/post/7660385253705711635

---

*本报告基于 2026-08-10 全网公开资料整理，链接均为搜索结果原文地址。*
