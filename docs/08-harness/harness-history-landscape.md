# AI Agent Harness 发展历程与竞争格局(2022-2026)

> **一句话摘要**:从 2022 年 ReAct 论文与 LangChain 诞生,到 2026 年协议标准化时代,梳理 AI Agent Harness 的四阶段发展史、五强竞争图谱与路径依赖洞察——并附"知识索引",把文中提到的每个概念/框架/论文映射到本站对应文章。
>
> **来源**:微信公众号《AI Agent Harness框架分析报告》(目光落点,约 2.5 万字),https://mp.weixin.qq.com/s/JU4d8rtGSkKxN1T3qD5v4g

## 概念:什么是 Agent Harness

> **AI Agent Harness 是让大语言模型能够自主规划、调用工具、执行多步任务的编排框架**——它把"一问一答"的 ChatBot 变成了能完成复杂工作的自主 Agent。

Harness 解决的一直是同一个工程问题:**如何让 Agent 在真实世界可靠运行**(权限、可观测、错误恢复、成本、信任),而不是模型能力本身。

## 纵向:四阶段发展史

### 萌芽期(2022.10 - 2023.2):范式确立

- **2022.10 ReAct 论文**(Princeton 姚顺雨团队):"想一步、做一步、看结果、再想下一步"——现代 Agent 的基础范式,详见 [AI Agent 入门](../03-agents/agent-intro.md) 的 think-act-observe 循环;
- **2022.10 LangChain v0.1**(Harrison Chase):把 LLM 调用、prompt 模板、工具调用串成 chain;
- **2022.11 ChatGPT 发布**:引爆 LLM 潜力,但暴露"只能对话、不能做事"的根本限制——需要执行层,即 Harness;
- 技术前史(2015-2022):RL 社区的 OpenAI Gym、RLlib、BDI 架构(见 [学习范式与核心概念](../01-ai-basics/ml-learning-paradigms.md) 的强化学习)。

### 爆发期(2023):从链条到编排

- **2023.3 GPT-4 + ChatGPT Plugins**:LLM 调用外部工具成为可用产品功能;微软推出 **Semantic Kernel**(第一个大厂 Agent 框架);
- **2023.3-4 BabyAGI / AutoGPT 爆火**:"自主 Agent"全民化,但易陷入无限循环、狂烧 Token;证明市场需要"能完成任务的 AI";
- **2023.5 Berkeley Gorilla + Function-Calling Leaderboard**:工具越多 LLM 性能越差(**7-85% 下降**)——工具管理与上下文压缩成为框架核心问题;
- **2023.6 OpenAI Function Calling**:成为行业标配,工具调用复杂度下沉到模型层;
- **2023.8-10 AutoGen**(微软研究院):多 Agent 对话协作;LangChain 发布 LCEL、Hub、LangServe;
- **2023 学术里程碑**:Reflexion(NeurIPS 2023,自我反思,HumanEval 91% pass@1)、斯坦福 DSPy(prompt 工程模块化)。

### 成熟期(2024-2025):生产化与商业化

- **2024.3 Andrew Ng 定义 Agentic Workflow 四大模式**:reflection、tool use、planning、multi-agent collaboration(见 [面试题知识提炼](../03-agents/agent-interview-knowledge.md) 设计模式篇);
- **2024.4 LangGraph**:架构转型——从线性 chain 到**图状态机**,关键创新是 **checkpointing(检查点持久化)**,失败断点恢复;
- **2024 商业化分水岭**:LangChain 获 Series A/B(独角兽)、推出 LangSmith(可观测);CrewAI Series A;LlamaIndex 转型 RAG 平台(LlamaCloud/LlamaParse);Anthropic 2024.10 推出 **Computer Use**(Agent 直接操作桌面);
- **2025**:LangGraph 1.0 + Platform GA(Klarna/Replit/Uber/LinkedIn 采用);2025.10 微软合并 AutoGen+Semantic Kernel 为 **MAF**;AutoGen 进入维护模式、社区 fork 出 **AG2**;2025.12 **AAIF**(Anthropic/OpenAI/Block,Linux Foundation)成立并接收 **MCP** 捐赠。

### 标准化期(2026 至今):协议时代

- **2026.2-4 MAF 1.0 GA**:Azure Foundry 托管,CodeAct 优化(52.4% 更快、63.9% 省 Token);
- **协议栈成形**:**MCP**(agent-to-system)+ **A2A**(agent-to-agent,Google,150+ 组织)+ ACP/UCP/AP2;
- **2026.7 IETF 126 维也纳会议**:`draft-hw-protocol-agent-00` 投票——Agent 通信协议有望成为像 HTTP/SMTP 一样的互联网基础协议;
- 市场数据:2026 年 AI Agent 市场规模 $10.9-11.8 亿(+44-47%);Gartner 预测 Agent 软件支出 $2,065 亿(+139%);65% 企业已使用;但 **51% 生产使用、<10% 规模化**——障碍是工程问题而非模型能力。

## 横向:2026 竞争图谱(五强对比)

| 维度 | LangGraph | CrewAI | MAF | AG2 | LlamaIndex |
| --- | --- | --- | --- | --- | --- |
| Stars | 38.3k | 56.2k | 12.4k | 4.8k | 51.1k |
| 架构 | 图状态机+检查点 | 角色-任务团队 | 混合编排(AutoGen+SK) | 对话共识 | RAG 工作流 |
| 学习曲线 | 陡峭(2-4h) | 平缓(30-60min) | 中等 | 中等 | 中等 |
| 生产可靠性 | 最高 | 问题多(超时/内存泄漏/总线瓶颈) | 待验证 | 无状态管理 | 垂直场景高 |
| 企业采用 | 68%(Gartner) | 63% Fortune 500(官网) | Azure 生态 | 低 | 垂直场景 |
| 云服务 | LangSmith($39/月起) | 企业版(询价) | Azure Foundry | 无 | LlamaCloud |
| 生态位 | 生产环境默认 | 快速原型首选 | Azure/.NET 企业 | 研究/对话实验 | 文档密集型 |

**核心分工**:可靠性 vs 速度(LangGraph vs CrewAI)、通用 vs 垂直(LlamaIndex)、社区 vs 企业(AG2 vs MAF)、生态绑定 vs 中立。行业共识是**混合策略**:CrewAI 快速验证想法 → LangGraph 实现产品;微软生态直接上 MAF。

## 横纵交汇洞察(要点)

1. **ReAct 范式成为唯一共识**:简单、直观、有效——但也带来路径依赖,无人质疑其是否最优;
2. **LangChain 先发优势的三层护城河**:开发者心智 → 生态整合 → 企业客户反馈(生产痛点直接驱动 LangGraph 检查点设计);CrewAI Stars 更高但企业采用被碾压——**Stars 是试用热度,采用率是生产信任**;
3. **Function Calling 标准化**:工具调用逻辑趋同,框架差异转向"如何编排多步工作流";工具选择本质是搜索问题(7-85% 性能下降)至今无根治,方向是分层工具管理;
4. **AutoGen 分裂的必然性**:研究项目基因(快速迭代、自由探索)vs 企业平台基因(稳定、兼容)不可调和;AG2 的教训——纯社区驱动在基础设施层很难竞争;
5. **CrewAI 没走 LangGraph 的路**:保持简单是核心竞争力,修复生产问题(超时 #4135、内存泄漏、消息总线瓶颈)会破坏简单性——守住原型生态位是理性选择;
6. **起源决定终点**:LangChain 个人项目→务实重构、CrewAI 创业公司→差异化抽象、微软双线→战略整合、AG2 社区反抗→边缘化、LlamaIndex 垂直需求→做深护城河。

## 知识索引:文中提到的所有 Agent 内容 → 本站

!!! note "索引说明"
    下表把报告正文提到的每个概念/框架/论文/协议,映射到本站对应文章。✅=已收录;**=本次新补充的清单条目。

### 概念与范式

| 文中实体 | 类型 | 本站对应 |
| --- | --- | --- |
| ReAct 范式 | 论文/模式 | ✅ [AI Agent 入门](../03-agents/agent-intro.md)(think-act-observe) |
| Agentic Workflow 四大模式 | 设计模式 | ✅ [面试题知识提炼](../03-agents/agent-interview-knowledge.md)(三、设计模式) |
| Reflexion(自我反思) | 论文/模式 | ✅ [面试题知识提炼](../03-agents/agent-interview-knowledge.md)(Q8) |
| Function Calling | 能力 | ✅ [工具调用](../03-agents/tool-calling.md) |
| Computer Use(桌面操作) | 能力 | ** [配套开源方案](harness-tools.md)(工具类新增) |
| 强化学习/RL 前史(Gym/RLlib/BDI) | 背景 | ✅ [学习范式与核心概念](../01-ai-basics/ml-learning-paradigms.md) |
| Context Engineering / 上下文压缩 | 工程 | ✅ [Context Engineering](../03-agents/context-engineering.md) |

### 框架与项目(2026 五强 + 历史)

| 文中实体 | 类型 | 本站对应 |
| --- | --- | --- |
| LangGraph | 框架(生产标准) | ✅ [通用编排框架](orchestration-frameworks.md)(LangGraph 条目) |
| CrewAI | 框架(原型首选) | ✅ [通用编排框架](orchestration-frameworks.md)(CrewAI 条目) |
| Microsoft Agent Framework | 框架(Azure 生态) | ** [通用编排框架](orchestration-frameworks.md)(MAF 条目) |
| AG2 | 框架(社区分叉) | ** [通用编排框架](orchestration-frameworks.md)(AG2 条目) |
| LlamaIndex | 框架(RAG 垂直) | ** [通用编排框架](orchestration-frameworks.md)(LlamaIndex 条目) |
| OpenAI Agents SDK | 框架 | ** [通用编排框架](orchestration-frameworks.md)(OpenAI Agents SDK 条目) |
| Semantic Kernel | 框架(已被 MAF 取代) | ** [通用编排框架](orchestration-frameworks.md)(历史条目) |
| LangChain(chain 时代) | 框架(历史) | ✅ [通用编排框架](orchestration-frameworks.md)(LangGraph 条目内提及) |
| AutoGPT / BabyAGI | 项目(自主 Agent 先驱) | ✅ [编码 Agent 工具](coding-agents.md)(AutoGPT 条目) |
| DSPy | 项目(prompt 编程) | ** [通用编排框架](orchestration-frameworks.md)(DSPy 条目) |
| Gorilla / Berkeley FCL | 论文/评测 | ✅ [Agent 评测](../03-agents/agent-evaluation.md)(工具调用性能问题) |

### 协议与标准

| 文中实体 | 类型 | 本站对应 |
| --- | --- | --- |
| MCP | 协议 | ✅ [配套开源方案](harness-tools.md)(MCP 条目) |
| A2A(Agent-to-Agent) | 协议 | ** [配套开源方案](harness-tools.md)(A2A 条目) |
| AAIF / IETF 标准化 | 组织/进程 | ** [配套开源方案](harness-tools.md)(协议条目内说明) |

### 评测与可观测

| 文中实体 | 类型 | 本站对应 |
| --- | --- | --- |
| LangSmith | 可观测平台 | ✅ [配套开源方案](harness-tools.md)(评测条目提及) |
| Berkeley FCL | 评测基准 | ✅ [配套开源方案](harness-tools.md)(评测基准) |
| 生产规模化障碍(权限/可观测/恢复) | 工程 | ✅ [生产级 Agent 9 层架构](../03-agents/ai-infra-layering.md) |

## 总结

- Agent Harness 从 2022 年的"简单链条"演进到 2026 年的"状态机 + 检查点 + 可观测 + 协议栈",四阶段:萌芽(ReAct/LangChain)→ 爆发(自主 Agent/Function Calling)→ 成熟(生产化/商业化)→ 标准化(MCP/A2A/IETF);
- 2026 竞争格局:**LangGraph(生产)、CrewAI(原型)、MAF(Azure)、LlamaIndex(文档)、AG2(边缘化)**,混合策略成为共识;
- 每个框架的优劣势都能追溯到历史决策——**路径依赖**是理解这个市场的最佳透镜;
- 规模化障碍不是模型能力,而是**工程问题**(权限、可观测、错误恢复、成本、信任)——这正是 Harness 的价值所在。

## 延伸阅读

- 站内:[Harness 章节首页](index.md)、[通用编排框架](orchestration-frameworks.md)、[编码 Agent 工具](coding-agents.md)、[配套开源方案](harness-tools.md)、[生产级 Agent 9 层架构](../03-agents/ai-infra-layering.md)
- 外部:原文(目光落点);ReAct / Reflexion / AutoGen 论文(见文末信息来源);原始资料存档于 `docs/inbox/harness-report-source.md`
