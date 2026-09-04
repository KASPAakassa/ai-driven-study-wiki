# Agent 持久化运行的工程范式:三大模式解决"7 小时问题"

> **一句话摘要**:agentic AI 革命的"脏秘密":Agent 跑得越久越容易失败——生产数据显示运行 35 分钟后成功率开始下降,任务时长翻倍则失败率翻四倍;1% 的步骤失败率在 100 步后复合成 63% 的总失败率。这就是 **"7 小时问题"**。2025-2026 年出现三大生产级工程范式:**Temporal Durable Execution(事件回放,Activity 级)、LangGraph Checkpointing(图状态快照,节点级)、Harness-Level Checkpointing(文件系统即状态,子任务级)**——共同硬前提是**工具幂等性**。
>
> **来源**:AgentMarketCap 博客《The 7-Hour Problem: How Production AI Agents Survive Crashes, Context Limits, and Tool Failures》,https://agentmarketcap.ai/blog/2026/04/05/agent-state-persistence-long-running-task-recovery;原始资料存档于 `docs/inbox/agent-persistence-source.md`

## 概念:7 小时问题与三种失败模式

**7 小时问题**:企业开始让 Agent 跑全天任务(重构 20 万行代码库、多步骤尽调工作流、季度合规审计自动化),可靠性数学变得残酷:

- **1% 的步骤失败率,在 100 步后复合成 63% 的总失败率**;
- 运行 35 分钟后成功率可测下降;任务时长翻倍则失败率翻四倍;
- 2025.10-2026.1,Claude Code 交互会话的 99 分位 turn 时长从不到 25 分钟翻倍到 45+ 分钟——长时程已是主流,基础设施问题从理论变紧迫。

### 长时程 Agent 会话的三种失败模式(需要不同解法)

| 失败模式 | 表现 | 关键点 |
| --- | --- | --- |
| **上下文窗口耗尽** | 40-50 步顺序决策后 20 万 token 窗口开始填满;压缩策略(定时清理旧工具结果/对话摘要/会话记忆提取/全历史摘要/最旧消息截断)会**丢失信息**,溢出后 Agent 忘记自己在做什么 | Claude Code 用五种上下文管理策略 |
| **进程级崩溃** | LLM API 超时、网络失败、容器编排器 OOM kill、开发机睡眠——7 小时自主运行中至少发生一次的概率接近必然 | 没有外部状态,整个会话丢失 |
| **工具失败与非幂等副作用** | 写数据库/发邮件/部署代码中途失败产生不一致状态;朴素重试**重放已完成步骤**,造成重复写入、重复发邮件、部分应用的迁移 | **最危险**:Agent 恢复了,但世界已经坏了 |

## 原理:三大工程范式

### 范式一:Temporal Durable Execution——事件历史作为 ground truth

**架构**:不 checkpoint 状态,而是 **checkpoint 事件**——Agent 的每个动作(LLM 调用、工具调用、外部 API 请求)在执行前写入 append-only Event History。进程崩溃时,工作流引擎**从开始回放 Event History**,跳过已完成 Activities(用记录的返回值替代)。

**关键分离**:Workflows(确定性编排逻辑)vs Activities(非确定性工作,如 LLM 调用和工具使用)。LLM 调用是 Activity,会被记录——进程在 LLM 响应后、Agent 行动前死掉,Temporal 回放工作流、跳过 LLM 调用(返回缓存结果)、从下一步继续。**不浪费 token、不丢状态**。

- **成熟度**:2026 年 3 月 Temporal × OpenAI Agents SDK 集成 GA;模式可推广到任何框架——把 agent loop 包进 Temporal Workflow,把每个 LLM 调用/工具调用提升为 Activity,Agent 就"构造上防崩溃";
- **约束**:Workflows 必须确定性——随机数、时间戳读取、非确定性分支都要走 Temporal 的确定性安全等价物;
- **适合**:隔夜研究、自主代码迁移、多日合规工作流等长时程后台任务(崩溃容忍是首要约束,且团队熟悉 Temporal 编程模型)。

### 范式二:LangGraph Checkpointing——图状态作为一等公民

**架构**:Agent 是有向图,每个节点(LLM 决策、工具调用、条件分支)在把控制权交给下一节点前,把输出状态写入配置的 checkpointer。进程崩溃时**从最后一个成功写入的 checkpoint 恢复继续向前**——不同于 Temporal 的回放模型,LangGraph 不重执行之前的步骤,而是加载序列化状态快照继续。

**存储后端**:

| 后端 | 适用 |
| --- | --- |
| MemorySaver | 进程内,仅开发 |
| SqliteSaver / PostgresSaver | 单机持久化,小团队 |
| **DynamoDBSaver**(AWS 维护) | 生产规模;**大 checkpoint 自动卸载到 S3**(状态 >350KB),DynamoDB 存指针引用(多轮 Agent 累积工具结果/长文档/中间输出易超 400KB 项限制) |

**生产配置**:TTL 过期(如 `ttl_seconds=86400*7` 保留 7 天)+ checkpoint 压缩(数百个 checkpoint 的会话可省 60-70% 存储成本)。

**附带收益:天然支持 human-in-the-loop**——Agent 可在任意节点 checkpoint、暂停等人审、数天后恢复(受监管工作流需中间人工签核的场景)。

- **适合**:交互式/半自主 Agent(需 HITL)、多租户部署(并发会话隔离)、已在用 LangGraph 想最小改动。

### 范式三:Harness-Level Checkpointing——Claude Code 的做法

**架构**:来自对生产编码 Agent 长会话的观察,不依赖外部编排框架。核心是**分离 session state 与 task state**:

- **Session state**(对话历史、工具调用结果、模型响应)= 易失;
- **Task state**(文件系统、git 仓库、已完成子任务集合)= 持久。

Claude Code **把文件系统当作 checkpoint store**——任何恢复点都可读 git 历史、检查修改过的文件、查看仓库标记来重建任务进度。

**通用模式**(多个团队独立实现):

1. 把任务分解为**带显式完成标记的可验证子任务**(git commit、状态文件、数据库记录);
2. 进入下一子任务前**把完成状态写外部**;
3. 恢复时**扫描外部状态**确定哪些子任务完成,从第一个未完成的继续。

**本质**:手工实现的 event log——比 Temporal 简单、比 LangGraph 结构弱,但**零额外基础设施**。

- **同类实践**:Devin(每个 PR 是一个 checkpoint 单位,可在 PR 间被中断并干净恢复;Cognition 2025 年报:67% 的 PR 已合并,较 2024 的 34% 大幅提升,归因于更好的任务分解与 checkpoint 子任务管理)、Replit Agent 4(Repl 本身是 checkpoint,每次有意义的状态变化持久化到云端,崩溃后重启 Repl 恢复工作环境/依赖/文件状态,只回放规划步不重做工作);
- **适合**:编码 Agent/开发者工具(工作产物代码/文件/git 历史本身就是状态)——开销低、无框架依赖,但需要仔细的任务分解与标记设计。

## 原理:幂等性约束——三个范式共享的硬前提

!!! danger "每个写外部状态的工具必须幂等"
    如果 Agent 调用支付 API、发 webhook、写数据库记录后,在 checkpoint 提交前崩溃,恢复机制会重试该动作。**没有幂等性(通常用绑定 workflow/checkpoint ID 的幂等键实现),重试造成重复副作用。**

**生产中最严重的 Agent 故障不是崩溃本身,而是非幂等重试留下的不一致状态**:重复客户邮件、重复应用的数据库迁移、冗余 API 计费。**采用任一范式前,必须先审计每个外部工具调用的幂等性,再信任恢复路径。**

## 实践 / 应用:企业部署对照与选择

### 三大范式对比

| 范式 | 最适合 | 所需基础设施 | 恢复粒度 |
| --- | --- | --- | --- |
| Temporal Durable Execution | 隔夜/后台任务 | Temporal cluster 或云 | Activity 级(逐步) |
| LangGraph + DynamoDB/S3 | 交互式 + HITL 工作流 | AWS 基础设施或 Postgres | 节点级(图步骤) |
| Harness Checkpointing | 编码 Agent、基于文件的工作 | 外部存储(git/DB/S3) | 子任务级(手工) |

### 关键洞察

- **可靠性差距主要是基础设施差距,不是模型能力差距**——SWE-bench 只测 Agent 能否解决问题,不测能否在数小时、多失败、规模化下可靠解决;
- Gartner 预测 2026 年底 40% 的企业应用将包含任务特定 AI Agent(2025 年不到 5%)——**现在构建持久状态管理的团队,将在下一波浪潮中拥有结构性优势**;
- "7 小时问题"不是靠更好的模型解决,而是靠**把 Agent 状态当作基础设施**——像对待数据库事务、消息队列、分布式锁一样。

## 总结

- **问题**:7 小时问题——长时程 Agent 成功率随运行时间急剧下降(1% 步失败率 100 步后 63% 总失败);三种失败模式(上下文耗尽/进程崩溃/非幂等副作用);
- **范式一 Temporal**:事件回放(append-only Event History),Activity 级恢复,确定性约束,零 token 浪费;
- **范式二 LangGraph**:图节点 checkpoint,节点级恢复,DynamoDB+S3 分层存储,天然 HITL;
- **范式三 Harness**:session/task state 分离,文件系统即 checkpoint,子任务级手工实现,Devin/Replit 同款思路;
- **硬前提**:工具幂等性(幂等键)——否则恢复重试造成重复副作用;
- **选择**:后台任务→Temporal;交互+HITL→LangGraph;编码 Agent→Harness Checkpointing;
- **下一步**:对照站内 [Agent 容错设计](agent-fault-tolerance-design.md)(重试/韧性/降级)与 [生产级 Agent 架构](agent-production-architecture.md)(权限/容错/部署),理解"持久化运行"在生产 Agent 中的完整位置。

## 延伸阅读

- 原文:https://agentmarketcap.ai/blog/2026/04/05/agent-state-persistence-long-running-task-recovery
- 站内:[Agent 容错设计:不止于重试](agent-fault-tolerance-design.md)(错误分类/韧性三件套)、[生产级 Agent 架构](agent-production-architecture.md)(权限/协作/容错/部署)、[Agent 系统设计的 5 个决策](agent-system-5-decisions.md)(工程决策)、[Microsoft Agent Framework](microsoft-agent-framework.md)(Durable Task 持久化)、[上下文压缩与提示缓存](context-engineering-compression-caching.md)(上下文管理)
