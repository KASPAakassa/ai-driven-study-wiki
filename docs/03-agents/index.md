# 🛠 Agent 使用与开发

> AI Agent:概念与分类、主流框架(如 LangChain、AutoGen、CrewAI 等)、工具调用、记忆与规划、多 Agent 协作、开发实践。

## 本章节文章

- [AI Agent 入门](agent-intro.md) — 定义、与 LLM 应用的区别、四大能力
- [Context Engineering:Agent 上下文管理](context-engineering.md) — Write/Select/Compress/Isolate 四杠杆,管好上下文又准又省钱
- [上下文工程管理方案:从概念到落地](context-engineering-playbook.md) — 全网调研整合:理论基石、六大工具机制、指令文件标准、四大动态技术、外部记忆、落地路线图
- [上下文工程官方一手资料](context-engineering-official-sources.md) — Anthropic 定义与注意力预算、Claude Code 最佳实践、五层记忆体系、AGENTS.md 开放标准
- [文档漂移治理:从单一来源到 CI 文档门禁](context-engineering-doc-drift.md) — Single-Source Governance 四要素、Docs-as-Code 与自动发布、文档门禁 CI pass/fail
- [代码注释纪律:WHY 而非 WHAT](context-engineering-comment-discipline.md) — 三个社区 Skill 共识:标记约定、反模式清单、AI 过度注释修正
- [上下文压缩与提示缓存](context-engineering-compression-caching.md) — Compaction 三层与信息损失代价、缓存不可变前缀纪律、token tax 与预算
- [Agent 多轮对话上下文管理:Session、消息链与五层压缩](agent-context-management.md) — nanobot 源码拆解:LLM 无状态本质、session_key 隔离加锁、四类消息与 tool_call_id 配对、ContextBuilder 拼装、五层压缩防线、崩溃恢复与原子写入、记忆四层次(含面试答题框架)
- [Outlines Index:用渐进式披露替代 RAG 的文档检索方法](outlines-index-doc-retrieval.md) — 为每个文档建"名片"(Metadata+Outline 不存原文),search→outline→read 三层 MCP 工具让 AI 自主决定看多少(≈800 tokens vs RAG 4000-6000);brief/budget/单向量/BM25+向量双路/渐进可用(替代 RAG 的检索范式,与渐进式披露系列同源)
- [生产级 AI Agent 系统:9 层架构全景](ai-infra-layering.md) — L0-L8 九层 + 安全/CI-CD/FinOps/DevEx 四横切(整理自 Knock)
- [核心组件](agent-core-components.md) — LLM/工具/记忆/规划
- [工具调用](tool-calling.md) — function calling 原理与协议
- [Agent 框架](agent-frameworks.md) — LangChain/AutoGen/CrewAI 对比与选型

### 🧩 框架专题(13 篇,每框架独立一篇 + 综述)

- [LangChain 1.x:LCEL 管道与 @tool](langchain-framework.md) — 组件化(Runnable)+ LCEL 管道编排、@tool 工具注册、RunnableWithMessageHistory 记忆
- [LlamaIndex:数据驱动的 RAG 专家](llamaindex-framework.md) — Index-First 哲学、一站式文档处理、索引持久化、FunctionTool+ReActAgent、保险 RAG 案例
- [AutoGen:多智能体协作框架](autogen-framework.md) — GroupChat 群聊 + 四种发言者策略(round_robin/random/auto/自定义);⚠️ 已维护模式,迁移 Agent Framework
- [nanobot:超轻量自托管个人 Agent](nanobot-framework.md) — HKUDS 46.8k stars:工具调用+shell 代码执行+MCP+模型路由+WebUI,快速 POC 首选
- [Qwen-Agent:阿里通义官方框架](qwen-agent-framework.md) — @register_tool 强约束工具注册、内置 Gradio WebUI、code_interpreter、GroupChat 多 Agent
- [Deep Agents:LangChain 官方 Agent Harness](deepagents-framework.md) — 开箱即用:可插拔沙箱、多模文件解析(PDF/PPT/音视频)、MCP 一等公民
- [Agent 框架七方对比](agent-frameworks-seven-comparison.md) — Agno/OpenAI SDK/Pydantic AI/AgentScope/MAF/Mastra/VoltAgent 六维横评 + 综合成熟度排序(各框架独立文章见延伸阅读)
- [Agno:Agent 平台 SDK](agno-framework.md) — 最广集成矩阵(46 模型/100+ 工具)+ AgentOS 生产运行时 + 多聊天接口
- [OpenAI Agents SDK](openai-agents-sdk.md) — 官方轻量框架:Agent/Handoff/Guardrail/Session 原语少,Realtime/Voice 独家
- [Pydantic AI:工程严谨度天花板](pydantic-ai-framework.md) — pyright strict + 100% coverage、依赖注入、evals/graph/durable-exec 闭环
- [AgentScope:阿里通义平台级框架](agentscope-framework.md) — 多租户/沙箱/权限/长期记忆一体化,docstring 最全
- [Microsoft Agent Framework](microsoft-agent-framework.md) — Semantic Kernel+AutoGen 继任者:Python+.NET 双语言、Durable Task、声明式 YAML
- [Mastra:JS 全栈 Agent 平台](mastra-framework.md) — 140+ 包全栈覆盖、四层记忆、Playground 可视化、模板脚手架
- [VoltAgent:框架+平台双形态](voltagent-framework.md) — 全 provider 内建、Guardrails/evals/scorers 一体、resumable-streams 可恢复流

### 🛠️ 多 Agent · 工程 · 设计(其余文章)

- [多 Agent 协作](multi-agent.md) — 协作模式、消息通信、成本
- [Anthropic 多智能体研究系统:orchestrator-worker 架构与工程实践](agent-multi-agent-research-system.md) — 一手工程方法论:LeadResearcher+并行 Subagent+CitationAgent;内部评测比单智能体高 90.2%、token 经济学(agent 4×/多智能体 15×)、委派 prompt 八原则、LLM-as-judge 评估、生产可靠性(checkpoint/tracing/rainbow 部署)
- [Effective harnesses for long-running agents:跨上下文窗口的多窗口工作流](agent-harness-long-running.md) — 长时任务落地三件套(init.sh + claude-progress.txt + feature_list.json)+ initializer/coding 双 agent 分工;JSON 只改 passes、禁止删测试;Puppeteer MCP 端到端自测(与持久化范式互补)
- [OpenAI 长时 agent 三件套:Skills + hosted Shell + Compaction](agent-long-running-openai.md) — OpenAI 官方:Skill description 路由逻辑(缺负例 Glean 触发率掉 ~20%)、模板放 skill 内、双层 allowlist+domain_secrets、/mnt/data 交接、server-side compaction(与 Anthropic 长时 harness 对比)
- [Writing effective tools for agents:工具设计五原则 + Advanced tool use](agent-tool-design-practice.md) — 工具=契约;五原则(少而精/命名空间化/高信号上下文/Token 效率/描述 prompt 工程)+ eval 驱动 agent 重构;Advanced tool use 三 beta(Tool Search/Programmatic/Examples)效果数据
- [Agent 开发实践](agent-practice.md) — 开发流程、常见坑、可靠性、评测
- [Agent 开发方法选型:BMAD / Spec Kit / GSD / Skills](agent-development-methods.md) — 控制层级坐标系(流程/规范/上下文/工程习惯)+ 选型四问 + 避免多套最高指挥部
- [基于插件的 Agent 开发范式:从"向上封装"到"原子化透明"](agent-plugin-development-paradigm.md) — 插件化范式 vs LangChain 封装范式(目标分野)、双层不透明与日志即真相源、dsh 分层 Bundle→Profile→Patch→Overlay、效果成本调优;扩充思考:范式光谱/分阶段选型、透明≠可解释、与站内可观测性/评估驱动呼应、过度工程风险(与 DeepSeek Harness/Pi 互链)
- [Agent 评测](agent-evaluation.md) — 评测方法论、Rubric 二元化、长程 Agent 评测(整理自美团图灵团队)
- [Agent 面试题知识提炼](agent-interview-knowledge.md) — 2026 面试全攻略 16 题,六大板块知识要点(整理自知乎)
- [WorkBuddy Bench:Agent 的"完成"该由什么证明](workbuddy-bench.md) — 四层完成度、四赛道验收协议、五份合同(整理自腾讯论文解读)
- [《深入理解 AI Agent》导读与知识索引](ai-agent-book-guide.md) — 李博杰开源书 10 章精华 + 章→本站映射
- [Agent 的持续进化](agent-continuous-evolution.md) — 三层验证、四种更新方式、在线/离线分离闭环(整理自书第 8 章)
- [多模态与实时交互](agent-multimodal-realtime.md) — 语音三范式、Computer Use、机器人对照实验(整理自书第 9 章)
- [大规模 Agent 系统设计](agent-system-scaling.md) — 从个人助手到十亿用户:四阶段演进、LLM Gateway、成本测算与基础设施四件套
- [Agent 如何理解业务](agent-business-understanding.md) — 业务理解六要素、状态三元、编译式业务决策记录、理解/决策/执行三层架构、五份小合同
- [Agent 意图识别:分层路由系统](agent-intent-recognition.md) — 规则守边界/小模型提效率/大模型兜底的分层漏斗,各层适用场景与多维评估(面试题拆解)
- [生产级 Agent 架构](agent-production-architecture.md) — 权限六层洋葱、多 Agent 协作(上下文隔离/并行/工具限制)、分层容错恢复、部署三模式
- [Agent 性能剖析:找到系统的真正瓶颈](agent-performance-analysis.md) — 从端到端 trace 开始:统计口径(P95/P99/调用次数/失败重试)、延迟归因、trace 规范与设计练习
- [AI 协作规则设计](agent-collaboration-rules.md) — 六维度框架(开发基础/工作方式/边界/规范/验证/安全)、规则挖掘三步、边界写"怎么办"
- [Agent 图工作流设计](agent-graph-design.md) — 节点契约/数据边/扇出扇入/钻石拓扑/验证器三模式/收敛循环/模型分层,含 dynamic workflows 真实 JS 代码
- [Agent 系统设计的 5 个决策](agent-system-5-decisions.md) — 模型路由/循环(可验证+熔断)/工具(权限+沙箱)/闭环(凭证隔离)/安全,含四处实践修正
- [Agent 框架选型地图](agent-framework-selection.md) — 三层控制权模型(循环/运行时/协作)+ 五框架 2026 对比(OpenAI SDK/LangGraph/CrewAI/Eino/ADK)+ 四条防迁移边界
- [Agent 容错设计:不止于重试的完整思路](agent-fault-tolerance-design.md) — 错误三分类(调用前/中/后)+ 分层应对(Schema/韧性三件套/降级兜底)+ 完整架构与 LLM 非确定性难点
- [Agent 持久化运行的工程范式](agent-persistence-patterns.md) — 7 小时问题:三大模式(Temporal 事件回放 / LangGraph 图状态快照 / Harness 文件系统即状态)+ 幂等性约束 + 选型对照
- [Agent 架构全景:七种架构对比与选择档位](agent-architecture-panorama.md) — 单Agent→ReAct→P&E→多Agent→Router+Skill→Blackboard→Graph 七档,选型档位+每档指向站内深入文章
- [什么是真正的 Agent?Agentic 与 Agentive 的分界](agent-model-critique.md) — 邢波《Critique of Agent Model》:自动化在哪结束、agency 在哪开始;五维度(目标/身份/决策/自我调节/学习)内化 vs 外化脚手架(学术深度见 09)
- [Agentic Abstention:该学会"停下来"](agentic-abstention.md) — 停止判断力:三类弃权场景、CONVOLVE 上下文工程(26.7%→57.4%)、模型越大越执着、AbsRec 指标
- [经典多智能体系统](multi-agent-systems-classical.md) — 涌现智能、Agent 分类(反应式/慎思式)、NetLogo Flocking 三规则、通信协议 KIF/KQML(微软 AI 课程 23 章)
- [Agent 架构反熵增:长期治理](agent-architecture-antientropy.md) — 复杂度治理(变更三问)/技术债(台账+还债预算)/架构演进(可替换性+ADR+双写)
- [Agent 治理设计:用 Hook 堵住偷懒越权失忆](agent-governance-hooks.md) — 读写两侧 offload+HITL 守卫+state-Attachment 闭环,原则"prompt 定意图,框架 Hook 定边界"
- [多智能体协作设计:Agent Team / Room / Task / Member](agent-team-room-collaboration.md) — 临时团队+mkdir 原子文件锁、Room 收件箱+草稿板、AX 原则(整合 Raft)、Task/Member 统一建模
- [Agent Session 通信设计:异步协作范式](agent-collaboration-messaging.md) — 从 Claude Cross-session messaging 提炼:独立 Session + 显式消息通信(寻址/异步投递/进入决策/权限隔离),与文件锁收件箱范式对照
- [Agent 规划与工作流模式](agent-planning-patterns.md) — 推理四模式(ReAct/P&E/Reflexion/ToT)+ 工作流四模式(线性/ReAct/管道/人机)+ 三条选型铁律
- [10 个 AI Agent 工作流模板:把重复工作设计成可复用系统](agent-workflow-templates.md) — 业务工作流实例:收件箱/研究简报/表单/会议行动项/客服分类/内容再利用/竞品监控/发票核对/CRM/QA;五部分框架(trigger/context/tools/decision rule/human checkpoint)+ 风险分级人工闸门 + 审计轨迹(与 planning-patterns 理论互补)
- [Anthropic《Building effective agents》:workflow 与 agent 的五种模式](agent-building-effective-agents.md) — 原文整理:简单可组合 vs 过度设计框架;workflows(prompt chaining/routing/parallelization/orchestrator-workers/evaluator-optimizer)vs agents 自主模式;三原则(简单/透明/ACI)+ 工具工程 poka-yoke(与 workflow-templates 的"五部分"解读澄清区别)
- [Agent 记忆体系](agent-memory-systems.md) — 短期/长期记忆、写入闸门、记忆整合与衰减
- [Agent 共享记忆:多 Agent 协作的"同一个大脑"](agent-shared-memory.md) — 共享记忆池:向量/图/事件日志三阵营、场景锁与 CRDT、记忆分层与语义路由、群体智能涌现、遗忘访问续期
- [Agent 记忆模块的 3 个工程设计:Hermes 源码拆解](agent-memory-harness-design.md) — 显式注入(推非拉)/ 启动时冻结快照(保 prefix cache)/ 威胁降级显示不静默删除;框架只做基础设施、决定权留给最知情一方
- [Subagent:上下文隔离与职责分工](subagent-isolation.md) — 委派任务契约、结构化结果、与 Tool/Permission/Hook 的边界
- [评估驱动开发(EDD)](agent-eval-driven-dev.md) — traces 金矿、验证器防作弊、评估=训练目标+回归测试集
- [Agent 架构设计体系导读](agent-architecture-series.md) — 记忆/工具/循环/协作/技能五系统 + Framework/Runtime/Harness 三层开发方式
- [推理时验证设计范式](agent-test-time-verification.md) — 验证不对称性、失败分类学、Decomposition-Judge,拒绝盲目重试(与 09 学术篇互补)
- [Prompt 工程](prompt-engineering.md) — few-shot、CoT、结构化输出

## 待整理 / 规划

<!-- 从 inbox 收件箱转入本主题的素材,梳理前先登记在这里 -->

## 学习指引

- 前置:了解 [LLM 基础](../02-llm/index.md),尤其是推理、上下文窗口、工具调用。
- 入门顺序:Agent 是什么 → 核心组件(LLM/工具/记忆/规划)→ 框架上手 → 多 Agent → 生产实践。
