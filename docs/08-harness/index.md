# 🧰 Harness 框架与开源方案

> 收录让 AI Agent"真正跑起来"的 Harness(执行轨道)类开源项目:编码 Agent 工具、通用编排框架、以及配套的协议/沙箱/评测方案。持续更新,欢迎补充。

## 概念:什么是 Harness

**Harness(直译"线束/马具")** 在 AI/Agent 语境下,指**让模型作为 Agent 运行的系统**:处理输入、编排工具调用、执行命令、管理权限与上下文、验证结果并返回(参考 Anthropic 的定义:评测的是"框架 + 模型"协同,而非模型本身)。

- 对**编码场景**,Harness 是 CLI/IDE 里的 Coding Agent(Claude Code、Codex CLI 等);
- 对**通用场景**,Harness 是编排框架(LangGraph、AutoGen 等);
- 配套的还有**协议**(MCP)、**沙箱**(E2B)、**评测基准**(SWE-bench)等开源方案。

!!! note "与本站其他章节的分工"
    - 本章节是**开源 Harness 的收录索引**(持续更新);
    - 框架的**原理与对比**见 [03-agents/Agent 框架](../03-agents/agent-frameworks.md);
    - Harness 的**工程方法论**(上下文装载/工具/计划/执行/验证/审计/回滚七层)见 [AI Friendly 后端架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md);
    - 个人**使用经验**见 [07-agent-coding](../07-agent-coding/index.md)。

## 收录清单

- [⌨️ 编码 Agent 工具](coding-agents.md) — CLI / IDE 型 Coding Agent Harness
- [🧩 通用编排框架](orchestration-frameworks.md) — 多 Agent / 工作流编排 Harness 框架
- [🧪 配套开源方案](harness-tools.md) — 协议、沙箱、评测基准等支撑设施
- [🐧 PenguinHarness(专题收录)](penguin-harness.md) — 让 Agent 自主构建 Agent 的自进化平台
- [🐧 Pi Agent:极简 Harness 的源码级架构、插件生态与 DeepSearch 实践](pi-agent-plugins.md) — 双层 Agent Loop/四原子工具/拒 MCP 理由/Session Tree(源码级拆解)+ 运行时模块 + 11 个插件清单 + Extension 实现 DeepSearch 完整实践
- [🔬 Pi Agent Harness 深度解析:极简内核、四层架构与"五个 No"](pi-agent-harness-deep-dive.md) — 设计哲学(五 No + 三条信念)+ 四层 monorepo 九包依赖 DAG + 核心机制(pi-ai 统一抽象/agent-loop 792 行/扩展系统/tui 差分渲染/CBOR 协议/沙箱三模式)+ 九大设计模式 + Harness v3(durable execution)+ 生态(OpenClaw/Oh My Pi/pi-chat)+ 分层次学习路径
- [🐋 DeepSeek Harness(`dsh`):一切皆插件的 Agent Harness](deepseek-harness.md) — DeepSeek 官方 2026-08-13 发布:Agent=Model+Harness;Cordis 内核只管加载/依赖,模型/工具/技能/会话/沙箱/存储/循环/调度/UI 全由插件提供;配置层 patch 组合(profile+bundle);运行有迹可循(append-only 会话日志+Trajectory);四种模式(标准/PTC/极简/创造)
- [🧩 Cordis 插件框架深度解析:教程、原理、可靠性与适用性](cordis-plugin-framework.md) — dsh 底层运行时/元框架:插件=挂到共享 Context 的函数;五核心概念 + 时空可组合性论文;7 章教程主线;可靠性(可逆卸载/HMR/配置校验/依赖卫生)与弱点;适用性对比(VS Code/Obsidian)与门槛(API 未稳定)
- [🧠 TencentDB Agent Memory(专题收录)](agent-memory-plugin.md) — 外部记忆与上下文卸载,长任务省 Token
- [🤝 Multica(专题收录)](multica.md) — 编码 Agent 的统一调度中台,让 AI 成为正式团队成员
- [📜 Agent Harness 发展历程与竞争格局](harness-history-landscape.md) — 2022-2026 四阶段发展史 + 五强对比 + 知识索引(整理自《AI Agent Harness框架分析报告》)
- [🖥️ OpenWorker 桌面 Agent 架构拆解](openworker-architecture.md) — 四层架构、风险分类、Inbox/Artifacts/审计,Harness 落地样本(整理自架构师 JiaGouX)
- [🐳 AgentScope 2.0(专题收录)](agentscope-managed-agents.md) — 专为 Managed Agents 而生的 Harness 底座:Brain/Hands 拆分、控制面/数据面/Worker 三层、三种 Worker 模式
- [🏭 云端软件工厂(深度拆解)](cloud-software-factory.md) — 从 Vibe Coding 到 AI 原生生产线:Loop/Harness/Factory 拓扑、Graph 状态机控制面、7-Agent 权限隔离、主权智能与元工程师
- [🗜️ Headroom(专题收录)](headroom-context-compression.md) — AI Agent 的上下文压缩层:JSON 省 60-95% token、tree-sitter 代码压缩、CCR 可逆、库/代理/wrap 18 工具/MCP 四种形态
- [🤖 TuyaOpen(专题收录)](tuyaopen-ai-hardware.md) — AI 智能体硬件的开源 Harness:五层架构(TKL/TAL/Libraries/Services/Applications)、语音+LLM+多模态+云、TuyaOpenClaw 硬件 Agent
- [🧑‍🎓 Reasonix 使用教程(小白版)](reasonix-tutorial.md) — 可留它一直跑的编码 Agent 引擎:从零安装(CLI/桌面/VS Code)→ 第一次跑通 → 配置讲解 → 三个核心场景 → 安全与权限 → FAQ
- [🧑‍🎓 OpenCode 使用教程(小白版)](opencode-tutorial.md) — Anthropic 团队开源的 AI 编码 Agent:一键安装、双 Agent(build 干活 / plan 只读)Tab 切换、三场景、常用命令、FAQ
- [🎨 Crush(专题收录)](crush-coding-agent.md) — Charm 出品的终端编程搭档:多模型会话中切换、多会话 SQLite、LSP 增强、MCP 扩展、hooks 引擎、crushrc 配置、全平台
- [🤝 Avernet(专题收录)](avernet-collaboration-network.md) — 蚂蚁开源 Agent 协作层"操作系统":BCS(Bot Coordination Service)管身份/连接/路由,Plugin/Gateway 双路径、Agent 发现市场、群组共享上下文
- [⚡ AutoAgent(专题收录)](autoagent-zero-code-framework.md) — HKUDS 全自动零代码 Agent 框架(前身 MetaChain):自然语言生成工具/Agent/工作流,Agent OS 四组件(System Utilities/Actionable Engine/Self-Managing File System/Self-Play)、user mode + agent editor + workflow editor 三模式

## 待整理 / 规划

<!-- 从 inbox 收件箱转入本主题的素材,梳理前先登记在这里 -->

## 收录原则

- 只收**开源**项目,注明官方仓库链接;每条含:名称、仓库、一句话定位、适用场景。
- 仓库链接均已核验(2026-08-09);链接失效或改名会在更新时修正。
- 不在清单里、但你觉得值得收录的项目,丢进 `docs/inbox/` 即可。
