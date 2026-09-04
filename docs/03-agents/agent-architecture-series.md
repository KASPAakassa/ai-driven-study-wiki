# Agent 架构设计体系:五子系统 + 三层开发方式(系列导读)

> **一句话摘要**:Agent 架构可以拆成五个相互依赖的子系统——记忆、工具、循环、协作、技能;开发方式分三层——Framework、Runtime、Harness。本文沉淀整套设计思路(基于拆解 Claude Code 源码的万字系列),给出每子系统的核心设计原则与源码级洞察,并映射到本站对应文章。
>
> **来源**:「万字长文拆解 Agent 架构设计」系列(拆解 Claude Code 源码,TypeScript 手写核心逻辑)+ 入门/演进/开发方式三篇,原文链接见 [系列存档](#系列存档)

## 概念:Agent 架构的五系统视图

!!! note "核心方法论"
    本系列的方法:读源码 → 理解设计决策 → 手写核心逻辑。**"为什么这么设计"比"代码怎么写"更重要。**

五个子系统及其依赖关系:

```
        协作(子 Agent = 新循环的复用)
              ↑
        技能(目录注入上下文,正文按需进场,工具落地)
              ↑
  记忆 ──┐        ┌── 工具
  (最底层)├──→ 循环 ←──┤(最底层)
  (相互独立)      (组装成每轮推理)
```

!!! tip "理解依赖关系比理解细节更重要"
    记忆和工具在最底层、相互独立;循环架在两者之上;协作是循环的复用;技能是循环的"给养"。**它决定了你改一处时,哪些地方受影响、哪些不会。**

## 五子系统:核心设计原则

### ① 记忆系统(拆解 Claude Code)

| 设计原则 | 实现 | 为什么 |
| --- | --- | --- |
| **固定层在前** | 系统提示分"固定层 + 条件层",固定层(身份/哲学/工具规则)永远排最前 | 走 Prompt Cache,前缀稳定 → 输入成本降 90%(命中只付 10%) |
| **路径即相关性** | `CLAUDE.md` 三层加载(global → project → directory,到 git root 为止) | 零基础设施,不用向量数据库;标注来源让模型判断优先级 |
| **约束 → 指令** | `formatForInjection()` 把 Token 预算状态翻译成自然语言指令 | 对 LLM 而言自然语言是最好的 API;模型读到"避免读大文件"会真的调整行为 |
| **预算感知** | TokenBudgetManager 三级阈值(70%/85%/90%) | Agent 主动调整计划,避免上下文溢出;消息裁剪**从最新往前保留** |

!!! tip "最深的洞察"
    "自然语言就是最好的 API":把工程状态(限流/内存/错误率)翻译成模型能执行的指令,而不是硬截断。**扩展思路**:用 LLM 做记忆压缩(小模型如 haiku)、记忆重要性评分、向量检索补语义记忆。

### ② 工具系统(拆解 Claude Code)

| 设计原则 | 实现 | 为什么 |
| --- | --- | --- |
| **权限内聚** | `defaultPermission` 在工具接口里(三档:allow/ask/deny) | 工具自描述,不依赖外部配置 |
| **命令级签名** | `buildSignature()` 返回 `bash:cmd` | 防止"始终允许"变成全量授权 |
| **运行时评估** | `assessRisk()` 按**具体输入**调权限 | 同一工具不同调用风险不同 |
| **结构性约束** | 分类器输入字段在程序级控制 | 不受 Prompt Injection 影响 |

!!! tip "扩展方向"
    子 Agent **工具子集**(权限不递归放大——子 Agent 工具集是父的子集);两阶段安全分类器(Haiku 单 token 快速过滤,99% 正常调用 <100ms,可疑 1% 才人工确认);工具插件化(文件系统发现)。

### ③ Agent Loop 设计(拆解 Claude Code)

- **分层组装 + 主动压缩 + 显式预算** 是核心;循环 = 模型调用 → 工具执行 → 结果回填 → 再调用;
- **主动压缩**:旧消息 LLM 摘要化,阈值按任务类型动态调整;
- **显式预算**:外部预算(跑了多久、花了多少)不关心模型怎么想,触发时带已有结果返回;
- **流式解析工具调用**:参数未完整时就识别工具名,并行做权限预检查;
- **失败处理**:工具失败作为结果反馈给模型(重试/换方式/放弃),不抛异常;并行调用用 `Promise.allSettled` 隔离部分失败。

### ④ 多 Agent 协作(拆解 Claude Code)

- **子 Agent = 一个新循环**:没有任何特殊执行路径——多 Agent 层几乎不产生新逻辑,只是把已有部件组合起来;
- **Task 工具是薄封装**:把 `spawnSubagent` 注册成普通工具;description 里列出所有候选子 Agent 类型 → **prompt 就是 API 契约**;
- **三条规则**:预算只减不增(allocateSubagentBudget)、全新上下文(taskPrompt 是唯一传入)、返回值 = 最后一条消息;
- **并行零代码**:模型在一轮里发多个 task 调用,循环天然并发——**模型就是调度器**。

### ⑤ 技能系统设计(拆解 Claude Code)

- **渐进式披露(progressive disclosure)**:技能目录(名称+描述)常驻系统提示,正文经 `skill` 工具**按需一次取回**——"目录上墙,正文取阅";
- 技能正文里可以写**判断点**(如"网络类失败重试一次"),重试决策由模型临场判断,不是代码写死;
- 附件(scripts/references)不进上下文,要用时模型自己用文件工具读;
- 与 [mattpocock/skills](../07-agent-coding/skills/mattpocock-skills.md) 的"小、易改编"哲学同源,但这里给出了**源码级实现**(loadSkills + buildSkillMenu + createSkillTool)。

## 三层开发方式:Framework → Runtime → Harness

| 层级 | 代表工具 | 定位 | 适合谁 | 投入 |
| --- | --- | --- | --- | --- |
| **Framework** | LangChain、CrewAI、AutoGen | 组件库(LLM 封装/工具/模板) | 快速原型、学习 | 低 |
| **Runtime** | LangGraph | 状态机 + 执行引擎(图编排) | 需要流程控制的工程 | 中 |
| **Harness** | DeerFlow 2.0 | 完整 Agent 运行时(中间件/技能/子 Agent) | 企业级平台 | 高(几个人月+) |

!!! tip "核心判断"
    你处于哪个 Tier,不取决于你选了哪个工具,而取决于**你投入了多少研发**。生产级的差距不在工具,在 Harness 工程的深度。

## LangChain 三年演进:做减法到核心

```
v0.0  Chain(线性链 + 基于 JSON 解析的 ReAct Agent)
  → v0.1  AgentExecutor(黑盒:无法控制循环内部)
  → v0.2  LangGraph(图状态机,checkpointing,可控制)
  → v1.0  create_agent(最小 Harness:模型循环 + 工具 + 提示词 + 中间件挂钩)
```

- **减法路径**:Chain 被 LangGraph 取代、AgentExecutor 被 create_agent 取代、Memory 模块被 checkpointer + 中间件取代;
- **中间件哲学**:**取所需,弃其余**——每个中间件处理一个关注点(ModelRetry/ToolRetry/HumanInTheLoop/Summarization/SubagentLimit/LoopDetection/Clarification),在正确时机钩入循环;
- **结论**:Agent 的核心从来不是"框架替你做了多少事",而是"**框架给你多少控制权**"——最小但完整的控制面,就是 Harness 的精髓(呼应本站 [生产级 Agent 9 层架构](ai-infra-layering.md))。

## 用 DeerFlow 复刻 Claude Code(实战视角)

- **底座**:DeerFlow 的 Lead Agent 基于 LangGraph;用中间件栈组合出"Claude Code 式"行为:历史压缩(循环)→ 跨会话记忆注入(记忆)→ 并行子 Agent 封顶(协作)→ 死循环检测(Loop)→ 澄清询问;
- **加能力 = 加配置不碰代码**:加技能(一个文件夹 + SKILL.md)、加自定义 Agent(配置进 task 可选名单)、接外部系统(挂 MCP,支持 OAuth 与懒加载);
- **安全扫描**:技能是别人写的文本,注入上下文前先过安检——低门槛生态必须配的保险;
- 入门路径:让 LLM 调用工具(LangChain)→ 用图编排(LangGraph)→ 包装成服务(DeerFlow);DeerFlow 定位"Agent 运行时(工程师向)",区别于 Dify/Coze"搭建平台(产品向)"。

## 知识索引:系列 → 本站

| 系列主题 | 本站对应 |
| --- | --- |
| 记忆系统(Claude Code 源码) | ✅ [Agent 记忆体系](agent-memory-systems.md)、[Context Engineering](context-engineering.md)(预算/压缩)、[Agent 规则文件](../07-agent-coding/experience/agent-rules-agents-md.md)(CLAUDE.md) |
| 工具系统(权限/签名/评估) | ✅ [工具调用](tool-calling.md)、[Subagent 隔离](subagent-isolation.md)(工具子集)、[OpenWorker 拆解](../08-harness/openworker-architecture.md)(风险分类) |
| Agent Loop(压缩/预算/失败) | ✅ [Agent 规划模式](agent-planning-patterns.md)、[评估驱动开发](agent-eval-driven-dev.md) |
| 多 Agent(子 Agent=新循环/Task 契约) | ✅ [多 Agent 协作](multi-agent.md)、[Subagent 隔离](subagent-isolation.md) |
| 技能系统(渐进式披露) | ✅ [Skill 收藏](../07-agent-coding/skills/index.md)、[mattpocock/skills](../07-agent-coding/skills/mattpocock-skills.md) |
| 三层开发方式 / LangChain 演进 | ✅ [生产级 Agent 9 层架构](ai-infra-layering.md)、[Harness 发展史](../08-harness/harness-history-landscape.md) |
| DeerFlow | ✨ [08-harness 编排框架清单新增 DeerFlow 条目](../08-harness/orchestration-frameworks.md) |

## 系列存档

| 篇 | 标题 | 原文链接 |
| --- | --- | --- |
| 一 | 记忆系统设计 | https://mp.weixin.qq.com/s/rCNtpDFyZtgtZLT4MH9X1A |
| 二 | 工具系统设计 | https://mp.weixin.qq.com/s/iD73TPYxZj6s-Jpmpt0ulw |
| 三 | Agent Loop 设计 | https://mp.weixin.qq.com/s/EkhdD5h0OgAge1rPo2smZA |
| 四 | 多 Agent 协作 | https://mp.weixin.qq.com/s/CFTp_TVA8DQLFuvirkrFvQ |
| 五 | 技能系统设计 | https://mp.weixin.qq.com/s/2nlnrJeAlhZHGMMn_6udTg |
| 七 | 用 Deerflow 复刻 Claude Code | https://mp.weixin.qq.com/s/APBfdOzDTFXVGtMj8MSvZw |
| 附 | 从零开始入门指南 | https://mp.weixin.qq.com/s/cR0kF-AsxwtACPJ_1WGWJw |
| 附 | LangChain 版本演进视角 | https://mp.weixin.qq.com/s/CRccAYUeeAelf6dK7OzO7A |
| 附 | 三种 Agent 开发方式 | https://mp.weixin.qq.com/s/JYSHpmIBhTbOwrFuJZkoig |

9 篇原文全部存档于 `docs/inbox/agent-arch-*.md`。

## 总结

- **五子系统**:记忆(缓存优化/路径相关性/约束即指令)、工具(权限内聚/命令级签名/运行时评估)、循环(分层组装/主动压缩/显式预算)、协作(子 Agent=新循环/Task 契约)、技能(渐进式披露);
- **三层开发方式**:Framework(组件库)→ Runtime(状态机)→ Harness(完整运行时),层级由研发投入决定;
- **LangChain 演进 = 做减法**:最后剩下"模型循环 + 工具 + 提示词 + 中间件挂钩"的最小 Harness;
- 整套设计证明:**Agent 架构的核心是"给你多少控制权",不是"替你做了多少事"**。

## 延伸阅读

- 站内:[Agent 记忆体系](agent-memory-systems.md)、[工具调用](tool-calling.md)、[Agent 规划模式](agent-planning-patterns.md)、[多 Agent 协作](multi-agent.md)、[生产级 Agent 9 层架构](ai-infra-layering.md)
- 外部:系列原文(见上表);DeerFlow 官方仓库;LangChain v1.0 文档
