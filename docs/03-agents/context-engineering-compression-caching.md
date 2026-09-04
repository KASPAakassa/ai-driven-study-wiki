# 上下文压缩与提示缓存:省钱省心的高级技术

> **一句话摘要**:Compaction(压缩)与 Prompt Caching(提示缓存)是上下文工程的两大高级技术——前者对抗 context rot 与 token 成本,后者省 41-90% 的推理费用。本文整合 7 篇补充文献(Zylos Research ×2、usewire、luminhkhuong、cuiliang、掘金、Codex 实践):**压缩三层策略与信息损失代价、选择性淘汰、缓存"不可变前缀"纪律与健康度指标、token tax 与预算纪律**。
>
> **来源**:Zylos《Agent Context Compaction》《Prompt Caching for AI Agents》、usewire《How prompt caching cuts AI agent costs by 90%》、luminhkhuong.dev、cuiliang.ai、掘金《Context Engineering 不是写更长 Prompt》、danielvaughan《Codex CLI Context Window Budget》,文献清单见 `docs/inbox/context-engineering-references-source.md`

## 概念:为什么需要压缩与缓存

**Token Tax(token 税)**:agentic 循环的每一步都把全部累计历史重新发给模型,成本**复合增长**。示例:step 1 发 2,000 token($0.003)→ step 20 发 120,000 token($0.180)——**同样任务,成本是第 1 步的 60 倍**。加上 O(N²) 的计费模式(20 步循环实际消耗 21 万输入 token 而非 2 万),压缩与缓存成为必需。

**两大目标**:

- **压缩(Compaction)**:对抗 context rot 与 token 成本——主动丢弃/摘要最旧历史;
- **缓存(Caching)**:省推理费用——复用已计算的 KV 张量。

## 原理:压缩(Compaction)

### 三层递进策略(cuiliang,综合 Manus/Claude Code/Codex)

| 层级 | 策略 | 说明 |
| --- | --- | --- |
| Layer 1: Raw | 完整保留 | 最新工具调用结果不压缩(模型下一步决策高度依赖最近 observation) |
| Layer 2: Compact | 精简引用 | 较早工具结果用"引用"替换完整内容(如 `[Tool Result - Compact] 内容已保存至 /sandbox/page.html`);信息未丢失,从 context 移到文件系统 |
| Layer 3: Summarize | 语义摘要 | 整个对话轨迹做语义摘要——**必须用完整工具结果生成**(先恢复文件再摘要);**用 schema 定义摘要字段而非自由格式** |

**实现方式**:滚动摘要(阈值触发)、分层摘要(递归再摘要)、map-reduce(分块并行摘要再合并,Google Gemini 生产方案)。

**核心原则**:先最大化 recall(捕获所有关键信息),再迭代优化 precision(去冗余);最安全的"轻触"压缩是**清除很早之前的工具调用与结果**。

### 压缩的信息损失代价(必须知道)

!!! danger "自由摘要会静默丢失精确技术细节"
    - **Factory.ai 对 36,611 条生产消息评测**:三家摘要方法在"工件追踪(哪些文件被改)"上仅得 **2.19-2.45/5.0**;
    - **ACON 论文**(arXiv:2510.00615):AppWorld 多步任务上朴素摘要比无压缩上限损失 10-15 个百分点,结构化优化后恢复到 1-2% 内,但精确工件召回所有方法都失败;
    - **实例对比**(178 条消息调试会话):Anthropic 压缩只记得 "401 error on authentication endpoint",结构化压缩记得 "/api/auth/login endpoint… stale Redis connection";
    - 压缩链误差累积目前甚至没有基准测量。

**缓解**:压缩前用 PreCompact hook 保存关键状态;优先避免触发压缩(把任务拆小);结构化摘要优于自由叙述。

### 选择性淘汰(Selective Eviction)

- **LRU**:丢最旧的工具结果;
- **重要性打分**(KV cache 压缩研究路线):累计注意力权重("heavy hitter")、键向量 L2 范数、注意力熵,只保留 Top-K(Ada-KV、NACL);
- **去重去噪**:同一文件重复读取只留最新;已解决错误消息直接清除;工具输出格式化。
- 零模型开销但留下位置空洞;注意力打分存在循环论证。

### lost-in-the-middle 效应

Liu et al.(TACL):模型在相关信息位于上下文**首/尾**时性能最佳;答案文档落在 20 文档上下文中段时,多文档 QA 准确率**陡降超 30 个百分点**。根因是 RoPE 位置编码对中段注意力的衰减,长上下文模型中依然存在且随会话增长恶化——**这解释了为何压缩必须刻意保留两端**。

### 压缩与缓存的根本冲突

压缩是**硬语义断裂**,使全部缓存前缀失效。需系统提示后置 cache_control 断点、压缩块上也打标记(2026 年 Claude Code v2.1.62 曾因缺缓存失效触发输出过期前缀)。另注意 Devin 曾现"上下文焦虑"(临上限草率总结),**阈值建议设 70-75% 而非 98%**。

## 原理:提示缓存(Prompt Caching)

### 原理与各家折扣

按**前缀逐字节匹配**复用已计算的 KV 张量,只算新增部分:

| 厂商 | 模式 | 折扣 |
| --- | --- | --- |
| Anthropic | 显式 cache_control 断点,TTL 5min-1h | 缓存读 0.1x(省 90%),写 1.25-2x |
| OpenAI | 自动缓存(≥1024 token 前缀) | 缓存输入约 $0.175/M vs $1.75/M |
| Google | 命名缓存对象(手动管理 TTL) | 可配 |

### 静态前缀 + 动态后缀布局(不可变前缀纪律)

上下文按"稳定性"分层组装:**静态前缀在前**(system prompt → 工具定义 → 历史消息),**动态后缀在后**(当前用户消息、最新工具结果、检索结果)。静态层字节不变即稳定命中;多变内容放后,即使变化也不破坏已缓存前缀。

**缓存破坏三规则**(三个毁缓存的坑):

1. **会话中途增删/改工具定义**——工具 schema 在前缀,一变其后全部缓存失效(MCP 动态工具发现尤易触发);
2. **中途切换模型**——模型特定指令在前缀,切换后前缀字节不同;
3. **前缀中混入动态内容**——时间戳、request ID、会话配置每次请求都变,放进前缀则每次全量重算。

**收益实测**(arXiv《Don't Break the Cache》,500+ 代理会话):

- **system-prompt-only 缓存策略**(仅缓存系统指令+工具定义)跨厂商降本 **41-80%**、TTFT 提升 13-31%——无论代理做什么,稳定前缀都完好;
- 全上下文缓存(含工具结果)结果参差:工具输出每轮变动导致未命中,反而延迟上升;
- 佐证:Thomson Reuters 降本 60%;某 SaaS 月支出 $15,000→$4,500;某 RAG 客服系统降本 85%;
- Manus 称 **KV cache 命中率是"生产级 agent 最重要的单一指标"**。

### 缓存健康度指标

- **缓存命中率** = `cache_read_input_tokens / 总输入`,生产环境应 **>80%**;
- **缓存写入成本 <5%**(写入费为原价 1.25-2 倍);
- 纳入上下文健康度仪表盘,与 Context Bloat Rate、Isolation Breach Count 等共同触发自动调优。

### 多租户缓存隔离

多租户 SaaS 共享推理网关时,缓存 key 必须**纳入租户标识(namespace)**,防止租户 A 前缀误命中租户 B 缓存(错误降本 + 数据泄漏);各租户 system prompt/工具集本就不同,天然形成不同前缀;按租户隔离缓存配额与驱逐策略。

## 代码 / 实现:Codex 实践与预算纪律

### Codex 压缩机制(danielvaughan)

- **触发**:上下文接近上限自动触发,默认阈值约 20 万 token;
- **单层 handoff 摘要**:提取近期用户消息(上限约 2 万 token)→ LLM 生成结构化总结(当前进度与决策、约束与偏好、剩余任务、续作关键数据)→ 用摘要替换全部助手回复与工具结果,**用户消息原样保留**;
- **特点**:"全有或全无"的一次性压缩,不如 Claude Code 三层渐进式;作者结论:**避免压缩优于依赖压缩**——主动 `/compact` 优于触发自动压缩。

### Token 去向分析(工具结果占大头)

多文件重构的典型分配:系统提示+AGENTS.md **8%**、用户消息+@file **15%**、**工具调用结果 45%**、助手推理轨迹 22%、先前历史 10%。据分析,**工具结果(文件读取、grep)占代表性调试会话总 token 约 81%**——**最大的节省杠杆是控制 agent 读哪些文件、何时读**(精准 @文件而非目录级引用,monorepo 中一次 `@src/` 可注入数万 token)。

### 单线程单任务纪律

- **一个连贯工作单元对应一个线程**;"修登录 bug"的线程漂移成"顺便重构 auth 模块"比三个聚焦线程烧上下文快得多;
- `/new` 开启独立任务;`/fork` 探索替代方案不污染主线程;
- 决策树:新任务不属于同一逻辑单元→`/new`;上下文 >60% 且需先前上下文→`/compact` 后继续否则 `/new`;需读多文件→委派子代理(独立上下文窗口)。

### 上下文预算分配示例(掘金)

每轮上限 20k token 时大致分配:系统提示 2k、当前任务 1k、近期历史 3k、RAG 证据 8k、工具结果 4k、余量 2k。比例不必完美但必须有意识。压缩按类型分策略:历史可摘要、**硬约束结构化**(如 `"avoid": [...]` 而非自然语言)、工具结果过滤(1 万行日志只留 Top5 错误+时间范围+路径+复现命令)、RAG 证据带 `[source: ...]` 来源。

### RAG / Memory / State 三者分离(掘金)

三者常被混用但解决不同问题:

- **RAG**(外部知识):回答"资料里怎么说"——像开卷考试;风险:Chunk 断裂、召回不准;
- **Memory**(个体经历):回答"这个用户/任务之前发生过什么"——带来源/时间/置信度;风险:错记、旧记忆污染;
- **State**(结构化状态):当前执行进度含硬约束——**硬约束不能用自然语言摘要**,否则"必须包含"会被压成"最好有"。

## 实践 / 应用:研发团队上下文治理清单(2048ai)

1. **每类上下文设预算**:系统提示、工具定义、项目文档、历史消息、工具结果、长期记忆都设上限;
2. **工具默认返回摘要**:完整结果写文件,上下文只留关键错误、路径、ID、计数、下一步建议;
3. **让 Agent 学会记笔记**:长任务维护 TODO/progress/known_issues/decisions 结构化文件;
4. **建立 context review 指标**:单次任务 prompt tokens、工具结果 tokens、重复比例、压缩次数、读取文件数、无效检索次数;
5. **不同任务不同策略**:短任务少量 upfront;代码库任务项目说明+按需 grep;研究任务子 Agent 并行探索(只回传 1-2K 结论);长迁移任务 compaction+结构化笔记。

> **"高信号而非短"**:上下文治理不是"少给信息",目标是**高信号**而非短——某些任务需要长背景或多个示例,盲目压缩反而降低准确率。判断标准是**任务成功率、可复现性和错误类型**,不是 token 数字。同时警惕过度设计:先做能工作的最简单方案,再按失败模式加机制。

## 总结

- **Token Tax**:agentic 循环每步重发全部历史,成本复合增长(20 步可达第 1 步 60 倍);
- **压缩三层**:Raw(最新不压)/ Compact(引用替换)/ Summarize(schema 结构化摘要);先最大化 recall 再优化 precision;**信息损失代价真实**(Factory 2.19-2.45/5.0);
- **lost-in-the-middle**:两端好中段差(RoPE 衰减),压缩须保留两端;压缩与缓存根本冲突,阈值建议 70-75%;
- **缓存纪律**:静态前缀+动态后缀、三破坏规则(改工具/切模型/前缀动态内容)、system-prompt-only 降本 41-80%、命中率 >80% 是核心指标;
- **预算纪律**:Codex 工具结果占 81%,最大杠杆是控制读取;一个任务一个线程;RAG/Memory/State 分离、硬约束结构化;
- **下一步**:把这些技术纳入 [上下文工程管理方案](context-engineering-playbook.md) 的"动态上下文管理技术"章节,或对比站内 [Headroom 上下文压缩](../08-harness/headroom-context-compression.md) 的实现。

## 延伸阅读

- Zylos 压缩报告:https://zylos.ai/en/research/2026-04-21-agent-context-compaction-long-running-sessions/
- Zylos 缓存报告:https://zylos.ai/research/2026-02-24-prompt-caching-ai-agents-architecture
- usewire 缓存文章:https://usewire.io/blog/how-prompt-caching-cuts-ai-agent-costs
- luminhkhuong:https://luminhkhuong.dev/technical-knowledge/ai-agents/context-engineering
- cuiliang:https://cuiliang.ai/posts/prompt-caching-context-engineering
- 掘金:https://juejin.cn/post/7640643117474201641
- Codex 预算:https://codex.danielvaughan.com/2026/04/20/codex-cli-context-window-budget-token-management-large-codebases
- 站内:[上下文工程管理方案](context-engineering-playbook.md)(四技术总纲)、[Headroom 上下文压缩](../08-harness/headroom-context-compression.md)、[Agent 记忆体系](agent-memory-systems.md)(RAG/Memory/State 分离深化)、[TencentDB Agent Memory](../08-harness/agent-memory-plugin.md)
