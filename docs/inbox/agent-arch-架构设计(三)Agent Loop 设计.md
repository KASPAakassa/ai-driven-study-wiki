# 原始资料:万字长文拆解Agent架构设计(三):Agent Loop 设计

> 来源:微信公众号(Agent 架构设计系列),原文链接:https://mp.weixin.qq.com/s/EkhdD5h0OgAge1rPo2smZA
> 抓取日期:2026-08-09;状态:已拆解入库(见归档记录)

---

本系列目标：拆解 Claude Code 源码，理解 Agent 底层架构的设计思路。核心方法：读源码 → 理解设计决策 → 用 TypeScript 手写核心逻辑。
每一篇聚焦一个子系统，讲清楚"为什么这么设计"比"代码怎么写"更重要。

引言
前两篇分别讲了记忆系统和工具系统。这一篇讲 Agent Loop——把记忆和工具串起来的主循环。
Agent Loop 的基本结构很简单：一个 while 循环，模型说话 → 调用工具 → 拿到结果 → 再说话，直到不再调用工具为止。但要让它稳定运行，还需要解决三个问题：
一、上下文组装
模型每一轮看到的内容，分成四层：

为什么要分层？核心原因是缓存。
模型 API 通常支持 prompt caching：两次请求的前缀如果相同，就能复用之前的计算结果。system prompt 几乎每轮都一样，放在最前面就能稳定命中缓存。如果把它和每轮都变的历史消息混在一起，历史一变，整个前缀的缓存全部失效。
代码上，组装过程就是依次收集这四层：

interface AssembledContext { systemPrompt: string; toolDefinitions: ToolDef[]; memorySnapshot: string; messages: Message[];} class ContextAssembler { // 依赖：静态提示词、工具注册表、记忆系统、压缩器 async assemble(rawHistory: Message[], sessionId: string): Promise { // 记忆按需检索：拿最近一条用户消息去查询，不是全量注入 const lastUserMsg = [...rawHistory].reverse().find(m => m.role === 'user');  return { systemPrompt: STATIC_PROMPT, toolDefinitions: getToolDefs(), memorySnapshot: lastUserMsg ? await memoryStore.retrieveRelevant(lastUserMsg.content, sessionId) : '', messages: await compactor.compact(rawHistory), // 见下一节 }; }}
注意依赖方向：ContextAssembler 依赖 HistoryCompactor，反过来不是。组装是压缩的消费者，压缩不关心自己被谁调用。这样压缩策略可以单独测试。
二、历史压缩
最常见的做法是上下文超限时截断最早的消息。这有两个问题：
截断没有优先级——砍掉的不一定不重要，只是最老

截断是突然的——上下文长度"缓升→断崖"，关键信息可能在断崖处丢失

更好的做法是主动分级压缩：每一轮都在做，按消息的"年龄"分成几档，越老的压得越狠。
一个典型的分级方案：
实现上就是遍历历史，按年龄匹配策略：

for (const msg of history) { const age = totalTurns - turnIndexOf(msg);  if (age <= 5) result.push(msg); else if (age <= 15) result.push(stripToolOutput(msg)); // 丢输出，留工具名 else if (age <= 30) result.push(await summarize(msg)); // 小模型摘要 // age > 30: 直接跳过}
这样上下文长度曲线是平滑的：先增长，然后趋于饱和。信息损失被摊薄到很多轮里，而不是集中在一个点上。
还有一个隐含的假设：重要的事实性信息在压缩之前就应该已经写入记忆系统（见第一篇）。这样即使历史消息被丢弃，关键约束也不会丢。这也是为什么记忆提取要在对话过程中持续进行，而不是最后才做。
万字长文拆解Agent 架构设计（一）：记忆系统设计
三、循环本体与终止条件
Agent Loop 的自然终止条件是"模型不再调用工具"。但这不够可靠——工具调用失败后重试、子 Agent 递归调用，都可能导致模型陷入无限循环。
万字长文拆解Agent 架构设计（二）：工具系统设计
所以需要外部预算来兜底。三个维度：

interface LoopBudget { maxTurns: number; // 最多多少轮工具调用 maxTokens: number; // token 总量上限 maxWallClockMs: number; // 墙钟时间上限}
把预算追踪抽成独立类，方便测试和复用：

class BudgetTracker { private turnsUsed = 0; private tokensUsed = 0; private startTime = Date.now();  constructor(private limits: LoopBudget) {}  recordTurn(tokens: number) { this.turnsUsed++; this.tokensUsed += tokens; }  isExhausted(): { exhausted: boolean; reason?: string } { if (this.turnsUsed >= this.limits.maxTurns) return { exhausted: true, reason: 'max_turns_exceeded' }; if (this.tokensUsed >= this.limits.maxTokens) return { exhausted: true, reason: 'token_budget_exceeded' }; if (Date.now() - this.startTime >= this.limits.maxWallClockMs) return { exhausted: true, reason: 'timeout' }; return { exhausted: false }; }}
循环主体：

async run(userMessage: string): Promise { let history: Message[] = [{ role: 'user', content: userMessage }]; const tracker = new BudgetTracker(budget);  while (true) { // ① 预算检查放在循环顶部——加新条件只需在这里加一行 const { exhausted, reason } = tracker.isExhausted(); if (exhausted) return `[循环结束：${reason}]`;  // ② 组装上下文，调用模型 const context = await assembler.assemble(history, sessionId); const response = await llm.chat({ system: [context.systemPrompt, context.memorySnapshot].filter(Boolean).join('\n\n'), messages: context.messages, }); tracker.recordTurn(response.usage.totalTokens);  // ③ 模型不再调用工具 → 自然结束 if (!response.toolCalls?.length) return response.content;  // ④ 执行工具调用（经过权限检查），结果追加到历史 const results = await Promise.all( response.toolCalls.map(call => executeToolCall(call)), ); history.push( { role: 'assistant', content: response.content, toolCalls: response.toolCalls }, ...results.map(r => ({ role: 'tool', content: r.output, toolCallId: r.callId })), ); }}
几个设计选择：
终止条件统一放在循环顶部。不在循环中间散着检查。这样加新条件（比如"预估费用上限"）只改一个地方。
预算耗尽返回文字，不抛异常。上层拿到的是一个可用的部分结果，不是一个错误。这比硬中断好——用户至少能看到已经做了什么。
工具调用经过权限检查。executeToolCall 里先查权限再执行（权限管道见第二篇）。被拦截的调用返回"被拦截"的文字作为工具结果，模型会看到这个信息并调整行为。
四、为什么这样设计
4.1 上下文分层，不拼成一个大字符串
拼成一个大字符串更简单，但会丢掉分层缓存的能力。
模型 API 的 prompt caching 是按前缀匹配的。system prompt 不变 → 命中缓存；历史消息每轮都变 → 每次重新算。分开传，不变的部分享受缓存，变化的部分正常计算。拼在一起，历史一变，整个前缀缓存全部失效。
4.2主动分级压缩，不是被动截断
被动截断按"谁最老"来砍，不按"谁不重要"。5 轮前的 ls 输出没什么价值，但可能因为它比用户的某句寒暄更老而被砍掉；用户 30 轮前说过的重要约束，可能因为它最老而被砍掉。
分级压缩把"年龄"和"信息类型"结合起来：工具输出最先压（衰减最快），整轮对话随后摘要，更早的直接丢弃。重要事实在压缩前已经进了记忆系统，压缩历史不会丢。
4.3显式预算终止，不依赖模型自我判断
让模型自己判断"该停了"是不可靠的。工具调用失败→重试→又失败→又重试，模型可能陷入循环，永远不触发"不调用工具就返回文本"这个自然终止条件。
外部预算不关心模型怎么想，只关心"跑了多久、花了多少"。触发时带着已有结果返回，调用方拿到的始终是一个可用的结果。
五、扩展方向
5.1 流式解析工具调用
模型的响应是流式返回的，工具调用的 JSON 参数逐 token 到达。可以在参数还没完整时就识别出工具名称，提前做权限检查：

class StreamingToolCallParser { private buffer = ''; private toolName: string | null = null;  feed(chunk: string): { toolNameKnown: boolean; complete: boolean } { this.buffer += chunk; if (!this.toolName) { const match = this.buffer.match(/”name”\s*:\s*”([^”]+)”/); if (match) this.toolName = match[1]; } return { toolNameKnown: this.toolName !== null, complete: this.tryParse() !== null }; }}
好处是：识别出工具名之后，就可以在和模型生成参数并行的时间里做权限预检查，节省等待时间。
5.2 工具调用失败重试
工具执行失败时，不应该让循环抛异常。把错误信息作为工具结果反馈给模型，让模型决定下一步——重试、换方式、或者放弃：

async function executeWithRetry(tool: AgentTool, input: unknown, ctx: ToolContext) { for (let i = 0; i <= 2; i++) { try { return await tool.execute(input, ctx); } catch (e) { if (i === 2) return `执行失败（重试 2 次）：${(e as Error).message}`; } }}
5.3 并行工具调用的部分失败
模型一次可能调用多个工具。Promise.all 一个失败全部失败，Promise.allSettled 可以隔离失败：

const settled = await Promise.allSettled( response.toolCalls.map(call => executeToolCall(call)),);const results = settled.map((r, i) => r.status === 'fulfilled' ? r.value : { callId: response.toolCalls[i].id, output: `失败: ${r.reason}` });
总结
和 Claude Code 的区别：实际实现中流式解析、并行调度、记忆检索的相关性排序都更复杂，压缩策略也会根据任务类型动态调整阈值。但"分层组装 + 主动压缩 + 显式预算"是核心，足够支撑一个稳定的 Agent Loop。