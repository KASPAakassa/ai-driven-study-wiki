# Agent 面试题知识提炼:2026 大模型 Agent 面试全攻略

> **一句话摘要**:把知乎热帖《2026大模型Agent面试全攻略》的 16 道面试题按 6 大板块提炼成 Agent 知识要点——概念架构、多智能体、设计模式、状态管理、评估、Agentic RAG,每题给出核心知识点并链接站内对应文章。
>
> **来源**:知乎 pin(作者:光速敲代码的青丝),https://www.zhihu.com/pin/2065466101639681414;原始资料存档于 `docs/inbox/agent-interview-source.md`

## 说明

原帖 16 道题覆盖 Agent 知识图谱的六个板块。以下每题提炼**核心知识点**(Q1-Q3 依据原帖文字要点,Q4-Q16 依据题目结合本知识库整理),可作为复习索引使用。

---

## 一、核心概念与架构

### Q1:Agent 的基本架构组成?与传统 LLM Chain 的区别?

**知识点**:

- **Agent 基本公式**:`Agent = LLM(推理) + Planning(规划) + Memory(记忆) + Tool Use(工具使用)`——详见 [AI Agent 入门](agent-intro.md);
- **Chain 是预定义、线性的硬编码工作流**:步骤写死、按序执行,不根据中间结果改变路径;
- **Agent 具备"自主性"**:根据目标自发决定执行路径,通过**推理循环(Reasoning Loop)**不断调整策略——同一个"循环执行"vs"一次性生成"的区别,是 Agent 与普通 LLM 应用的分水岭。

### Q2:ReAct 模式的工作原理?

**知识点**:

- **ReAct = Reasoning + Acting**,是 Agent 的基石模式(论文 ReAct, Yao et al. 2022);
- 核心循环:**Thought(推理)→ Action(行动)→ Observation(观察)→ 下一轮 Thought**;
- LLM 先生成一段推理说明下一步要做什么,然后调用工具、观察结果,再根据结果进入下一轮推理——把"思考"和"行动"交织在一起,见 [Agent 入门](agent-intro.md) 的 think-act-observe 循环。

### Q3:如何实现 Agent 的长期记忆(Long-term Memory)?

**知识点**:

- **短期记忆**:利用 Context Window,存储当前会话历史(Chat History);
- **长期记忆**:通过 **RAG(检索增强)**——把历史经验、知识编码为 Embedding 存入向量数据库,Agent 执行任务前检索相关经验(Experience Retrieval);
- **2026 新趋势**:长文本模型(Long-context LLMs)直接处理超长历史;或通过"**摘要层级结构**"对记忆递归压缩——记忆分层的思路可参考 [TencentDB Agent Memory](../08-harness/agent-memory-plugin.md) 的 L0-L3 四层记忆。

---

## 二、多智能体协同(Multi-Agent Systems, MAS)

### Q4:单 Agent 遇到瓶颈时,为什么需要 Multi-Agent?常见协作模式?

**知识点**:

- **单 Agent 瓶颈**:上下文窗口有限、单模型能力边界、长任务容易丢失方向、串行执行效率低;
- **常见协作模式**:**编排(Orchestrator-Workers)**、**辩论(Debate)**、**流水线(Pipeline)**、**黑盒团队**——详见 [多 Agent 协作](multi-agent.md);
- 价值:角色分工、并行提速、相互校验(降低单一模型自我说服风险)。

### Q5:多智能体系统中如何解决"无限循环"或"通信冗余"?

**知识点**:

- **无限循环**:设置最大轮次/步数上限、收敛检测(论点重复即停止)、超时熔断、人工介入开关——见 [Agent 开发实践](agent-practice.md) 的可靠性策略;
- **通信冗余**:结构化消息协议(只传必要字段)、去重记忆(不重复论点)、消息路由过滤、控制 Agent 数量与拓扑(星型 vs 全连接)。

---

## 三、Agent 核心设计模式(Design Patterns)

### Q6:对比"工作流(Workflows)"与"自主智能体(Autonomous Agents)"的优劣

**知识点**:

| 维度 | 工作流 Workflows | 自主智能体 Autonomous Agents |
| --- | --- | --- |
| 控制 | 预定义步骤、确定性强 | 模型自主决策、灵活 |
| 可预测性 | 高,易调试、易测试 | 低,行为不可完全预期 |
| 适用 | 稳定、可枚举步骤的任务 | 开放式、需动态调整的任务 |
| 风险 | 低 | 高(需护栏:权限/步数/审计) |

工程上常用**混合**:高确定性部分用工作流,高自由部分用 Agent——与 [mattpocock/skills](../07-agent-coding/skills/mattpocock-skills.md) 的"按风险分级自动化"思路一致。

### Q7:"编排者-执行者(Orchestrator-Workers)"模式

**知识点**:

- **Orchestrator(编排者)**:负责任务分解、调度、汇总——"大脑";
- **Workers(执行者)**:多个专职子 Agent,各自负责一个子任务,可并行;
- 典型应用:Orchestrator 把"写报告"拆成"调研/分析/写作"分给不同 Worker;编排者需要**状态管理**与**结果校验**,防止子任务失控。

### Q8:"反思/自我纠正(Reflection/Self-Correction)"模式

**知识点**:

- Agent 生成结果后**自我审视**:检查是否满足要求、发现错误并重试(如 Reflexion:用语言反馈迭代改进);
- 实现方式:评审子 Agent(双角色——写作者 vs 评审者)、代码运行错误回填、测试驱动(红-绿-重构见 [tdd](../07-agent-coding/skills/mattpocock-skills.md));
- 代价:多一轮 LLM 调用 = 更多 Token 与延迟,需按任务价值取舍。

---

## 四、深度技术实现与状态管理

### Q9:多轮对话 Agent 中,如何处理"状态爆炸"和"上下文溢出"?

**知识点**:

- **上下文溢出**:超长历史导致 Token 爆炸——方案:滑动窗口、摘要压缩、**外部记忆卸载**(见 [TencentDB Agent Memory](../08-harness/agent-memory-plugin.md) 的 Offload:长内容外置、上下文只留摘要与索引);
- **状态爆炸**:多轮状态量多且混乱——方案:状态结构化(只存必要字段)、状态分层(会话级/任务级/全局级)、检查点持久化(见 [Loop Engineering](../07-agent-coding/experience/loop-engineering.md) 的检查点设计)。

### Q10:如何保证 Agent 调用工具(Function Calling)的可靠性?

**知识点**:

- **工具契约清晰**:schema 定义严格(参数类型、必填、枚举)、描述让模型无歧义——见 [工具调用](tool-calling.md);
- **结果校验**:解析失败重试、工具返回结构化错误码、超时处理;
- **权限与安全**:工具白名单、敏感操作分级授权、审计日志(见 [AI Friendly 后端架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md) 的权限分级与 Harness 工具层);
- **降级策略**:工具不可用时优雅降级(缓存、兜底路径)。

### Q11:LangGraph 的"节点(Node)和边(Edge)"与传统工作流有何不同?

**知识点**:

- 传统工作流:线性/固定 DAG,分支写死;
- **LangGraph**:状态化图(StateGraph)——节点是处理单元,边可以带**条件路由(Conditional Edges)**,节点间共享 State,支持循环、持久化、人机回环(interrupt);
- 本质区别:**图是动态的、状态驱动的**——模型可以决定下一步走哪条边,工作流则不能;详见 [通用编排框架](../08-harness/orchestration-frameworks.md) 的 LangGraph 条目。

---

## 五、2026 必考的 Evals(评估)

### Q12:你如何量化一个 Agent 的性能?

**知识点**:

- **四层评测**:结果层(任务完成度)、过程层(规划合理性/步骤稳定)、效率层(耗时/Token/工具调用次数)、风险层(越权/安全)——见 [Agent 评测](agent-evaluation.md);
- **评测方法**:客观评测(规则/断言)+ 主观评测(Rubric 二元化、人机一致率)+ 基准(SWE-bench、τ-bench 等,见 [配套开源方案](../08-harness/harness-tools.md));
- **数据飞轮**:Bad/Good Case 喂养评测集,评测结果反哺迭代——"观测 + 评测 = 持续迭代"。

---

## 六、Agentic RAG 专项问答

### Q13:RAG 检索出的片段互相冲突,Agent 该听谁的?

**知识点**:

- **冲突处理策略**:时间戳/版本优先(更新者胜)、来源可信度加权、语义一致性投票、Agent 向用户呈现冲突并请求裁决;
- **根本解法**:元数据治理(每个 chunk 带来源、时间、权限),检索时按场景过滤——见 [RAG](../02-llm/rag.md)。

### Q14:企业知识库的"权限隔离"问题(Agent 会不会把高管工资查出来给普通员工?)

**知识点**:

- **检索期权限过滤**:把文档级/行级权限元数据写入索引,检索时按用户身份过滤——**权限必须在检索前生效,不能只靠提示词约束**;
- **生成期校验**:Agent 输出前检查引用来源是否在用户权限内;
- 呼应 [AI Friendly 后端架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md) 的 L0-L5 权限分级与数据脱敏原则——"权限失控的 AI 比写错代码更危险"。

### Q15:知识库内容更新很快(每日新闻/实时股价),RAG 如何应对?

**知识点**:

- **更新链路**:增量索引(新文档写入即索引)、失效淘汰(TTL/版本淘汰旧 chunk)、混合检索(新鲜度加权,如 BM25+向量+时间权重);
- **缓存与轮询**:高频数据定期拉取;回答时标注信息时间,防止用旧知识答新问题;
- 评估"时效性"指标:检索到的最新信息占比。

### Q16:如何提升问答准确度?

**知识点**:

- **检索质量**:chunk 大小与切分策略、混合检索(稀疏+稠密)、查询改写(Query Rewriting)、重排序(Rerank);
- **生成质量**:Few-shot 示例、引用溯源(答案带来源)、拒绝回答阈值(不确定时不硬答);
- **闭环**:Bad Case 回流改进检索与提示词——数据飞轮,见 [RAG](../02-llm/rag.md) 与 [Agent 评测](agent-evaluation.md)。

---

## 总结

- 原帖 16 题覆盖 Agent 知识六大板块:**概念架构 / 多智能体 / 设计模式 / 状态管理 / 评估 / Agentic RAG**;
- 核心主线:Agent 公式(LLM+规划+记忆+工具)、ReAct 循环、长期记忆(RAG/长文本)、多 Agent 协作、工作流 vs 自主、编排者-执行者、反思模式、状态与上下文管理、可靠性、评测、权限与时效性;
- 面试准备建议:先吃透 [Agent 入门](agent-intro.md) 与 [核心组件](agent-core-components.md),再逐题结合本文知识点 + 站内专题深入。

## 延伸阅读

- 站内:[AI Agent 入门](agent-intro.md)、[核心组件](agent-core-components.md)、[工具调用](tool-calling.md)、[多 Agent 协作](multi-agent.md)、[Agent 评测](agent-evaluation.md)、[RAG](../02-llm/rag.md)
- 外部:知乎原帖 https://www.zhihu.com/pin/2065466101639681414
