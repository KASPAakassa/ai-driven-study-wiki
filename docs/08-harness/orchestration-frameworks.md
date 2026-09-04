# 🧩 通用编排框架(Harness 框架)

> 面向"把多个 LLM 调用、工具、子 Agent 编排成复杂系统"的开源 Harness 框架:从轻量 agent 库到多 Agent 协作、工作流/图编排。

## 概念

通用编排框架不局限于写代码,而是提供 Agent 运行时的抽象:**模型封装、工具注册、记忆、规划、多 Agent 通信、工作流/图执行**。选择维度:控制粒度(手写循环 vs 图编排 vs 对话式多 Agent)、语言生态(Python/TS)、与外部工具/数据源集成。

## 清单

| 名称 | 仓库 | 一句话定位 | 亮点 / 特点 |
| --- | --- | --- | --- |
| **LangGraph** | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | LangChain 团队的状态化图编排框架 | 用图/状态机描述 Agent 流程,支持持久化、人机回环(human-in-the-loop)、流式;生产级控制力强 |
| **DeerFlow** | [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | 字节开源的长程 SuperAgent Harness(79.6K★) | 基于 LangGraph 的完整运行时:中间件/技能/子 Agent/MCP,可复刻 Claude Code 级行为;系列解读见 [架构设计体系](../03-agents/agent-architecture-series.md) |
| **LongHorizon-Harness** | [AMAP-ML/LongHorizon-Harness](https://github.com/AMAP-ML/LongHorizon-Harness) | 长程任务状态管理 Harness(arXiv:2608.01964,MIT) | MEA(Manage-Execute-Audit)状态机:Manager 持状态不触环境 / Executor 新鲜有界上下文执行 / Auditor 只读独立核验;AgentAdapter 接入 Claude Code/Codex;WeaveBench 51.8%→80.7%;论文解析见 [09-agent-research](../09-agent-research/longhorizon-harness-paper.md) |
| **OpenAI Agents SDK** | [openai/openai-agents-python](https://github.com/openai/openai-agents-python) | OpenAI 官方轻量 Agent SDK | 简单链式 + Handoff(交接),上手最平缓;OpenAI 生态首选,适合快速原型 |
| **Microsoft Agent Framework(MAF)** | [microsoft/agent-framework](https://github.com/microsoft/agent-framework) | 微软统一 Agent 框架(2026 GA) | AutoGen(对话)+ Semantic Kernel(插件)合并;Python/C# 双语言,CodeAct 优化;深度绑定 Azure Foundry |
| **AG2** | [ag2ai/ag2](https://github.com/ag2ai/ag2) | AutoGen 社区 fork | 对话共识架构、Apache-2.0、纯社区驱动;研究/多 Agent 讨论场景,主流影响力已边缘化 |
| **AutoGen** | [microsoft/autogen](https://github.com/microsoft/autogen) | 微软的多 Agent 对话框架 | 多个 Agent 通过对话协作完成任务;支持代码执行、群聊模式 |
| **CrewAI** | [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | 角色分工的 Agent 团队框架 | "Crew(团队)"概念:角色 + 任务 + 工具,上手快,适合流程化任务 |
| **LlamaIndex** | [run-llama/llama_index](https://github.com/run-llama/llama_index) | 文档密集型 Agent 框架(2024 起转型) | RAG pipeline 深度优化:LlamaParse 文档解析、LlamaCloud;常作为 LangGraph 的工具节点,垂直场景守门人 |
| **smolagents** | [huggingface/smolagents](https://github.com/huggingface/smolagents) | Hugging Face 的极简 Agent 库 | 代码即行动(code-first):agent 直接写 Python 调用工具;依赖少、易读 |
| **MetaGPT** | [geekan/MetaGPT](https://github.com/geekan/MetaGPT) | 模拟软件公司的多 Agent 框架 | 角色扮演(产品/架构/开发/测试)+ SOP 流程,产出文档与代码 |
| **AutoGPT** | [Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) | 早期的自治 Agent 项目 | 2023 年引爆"自主 Agent"概念;如今转向构建平台,历史意义大于当前实用性 |
| **Semantic Kernel**(历史) | [microsoft/semantic-kernel](https://github.com/microsoft/semantic-kernel) | 微软首个 Agent 框架(2023.3) | 插件式架构、面向 .NET;2025.10 并入 MAF,现仅维护历史意义 |
| **DSPy** | [stanfordnlp/dspy](https://github.com/stanfordnlp/dspy) | Prompt 编程框架(斯坦福) | 把 prompt 工程变成可编程/可优化的模块化系统,面向研究者与 pipeline 优化 |
| **PenguinHarness** | [Prism-Shadow/penguin-harness](https://github.com/Prism-Shadow/penguin-harness) | 让 Agent 自主构建 Agent 的平台 | LlamaFactory 作者新作;"一句话构建 + 自进化迭代 + 精简工具集",详见 [专题收录](penguin-harness.md) |
| **Pi** | [pi.dev](https://pi.dev) | 极简 Agent Harness(minimal agent harness) | 不内置能力、插件化组装;11 个实用插件清单见 [专题收录](pi-agent-plugins.md) |
| **Dify** | [langgenius/dify](https://github.com/langgenius/dify) | LLM 应用开发平台(含 Agent 编排) | 可视化编排 Agent/工作流,自带 RAG、工具、发布;偏平台而非纯框架 |
| **Multica** | [multica-ai/multica](https://github.com/multica-ai/multica) | 编码 Agent 的统一调度/托管中台 | 纳管 17+ 编码 AI CLI,看板派单、AI 小队、技能沉淀、私有化部署,详见 [专题收录](multica.md) |
| **OpenWorker** | [andrewyng/openworker](https://github.com/andrewyng/openworker) | 吴恩达团队的开源本地优先桌面 Agent | MIT 参考实现:风险分类/权限/Inbox/Artifacts/审计,详见 [专题收录](openworker-architecture.md) |
| **Avernet** | [alipay/avernet](https://github.com/alipay/avernet) | 蚂蚁开源的 Agent 协作层"操作系统"(V0.1,Apache 2.0) | Rust 实现 BCS(Bot Coordination Service)管"谁在说/谁在听/谁在做";Plugin(WebSocket 主动连入)/ Gateway(被动调度已有平台)双路径;Agent 发现市场/群组共享上下文,详见 [专题收录](avernet-collaboration-network.md) |

!!! note "与 03-agents 章节的关系"
    原理级对比(框架核心抽象、选型权衡)见 [03-agents/Agent 框架](../03-agents/agent-frameworks.md);这里作为**开源索引**持续补充新框架。

## 实践 / 应用:如何选型

1. **要生产级可控**:LangGraph(状态、持久化、回环)优先;要快速原型:smolagents、CrewAI。
2. **要多 Agent 协作**:AutoGen(对话)、MetaGPT(角色+流程)二选一;轻量场景 smolagents 也支持多 Agent。
3. **要可视化平台**(不写太多代码):Dify。
4. **评估标准**:可观测性(能否看每步状态)、持久化(会话恢复)、人机回环、成本控制、社区维护活跃度。

## 延伸阅读

- 站内:[Harness 章节首页](index.md)、[Agent 框架(原理篇)](../03-agents/agent-frameworks.md)、[多 Agent 协作](../03-agents/multi-agent.md)
- 外部:各仓库 README;smolagents 官方文档(极好的 Agent 入门教程)
