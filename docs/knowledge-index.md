# 🗺 知识库索引(渐进式加载入口)

> **这是知识库的"第一层入口"**:每次新的 session / 人进入知识库,先读本文件(轻量),再按需进入章节 `index.md`(第二层),最后深读具体文章(第三层)。本文件带每章定位与代表文章摘要,确保对知识库模块"理解到位"再动手。
>
> **维护约定**:新增/移动文章时,同步更新本文件的模块地图、主题索引与对应章节 `index.md`。

## 📌 渐进式加载协议(三层)

```
第 1 层(必读,≈ 30 秒):本 INDEX.md
    → 章节地图(下面)定位目标主题在哪个章节
第 2 层(按需):进入目标章节的 index.md
    → 看该章全部文章的一句话摘要,确定读哪篇
第 3 层(深读):打开具体文章.md
    → 完整阅读(概念 → 原理 → 代码 → 实践 → 总结 → 延伸阅读)
```

**常见任务 → 入口映射**(快速定位):

| 我想… | 去这里 |
| --- | --- |
| 学 AI/ML/DL 基础 | [01-ai-basics](01-ai-basics/index.md) |
| 学 LLM 原理(Transformer/预训练/RAG) | [02-llm](02-llm/index.md) |
| 学 Agent 概念/开发/设计 | [03-agents](03-agents/index.md) |
| 对比选型 Agent 框架 | [03 框架专题](03-agents/index.md) + [08-harness 编排框架清单](08-harness/orchestration-frameworks.md) |
| 动手做项目/复现 | [04-practice](04-practice/index.md) |
| 查论文/书/工具/博客资源 | [05-reference](05-reference/index.md) |
| 企业落地/Ontology/FDE | [06-enterprise](06-enterprise/index.md) |
| 个人 Agent Coding 经验/Skill | [07-agent-coding](07-agent-coding/index.md) |
| 找开源 Harness/编码 Agent | [08-harness](08-harness/index.md) |
| 读 Agent 前沿论文 | [09-agent-research](09-agent-research/index.md) |
| 鸿蒙开发 | [10-harmonyos](10-harmonyos/index.md) |
| 丢新资料待整理 | [📥 收件箱](inbox/README.md) |

## 🗺 模块地图(十章)

### 1. 🤖 AI · ML · DL 基础 — `01-ai-basics/`(14 篇)
> 知识库地基:AI/ML/DL 概念、经典 ML 算法、深度神经网络,由浅入深。

- **代表文章**:[人工智能入门](01-ai-basics/ai-intro.md)、[线性回归与逻辑回归](01-ai-basics/ml-linear-models.md)(手写梯度下降)、[神经网络基础](01-ai-basics/dl-neural-network-basics.md)、[CNN](01-ai-basics/dl-cnn.md)、[RNN](01-ai-basics/dl-rnn.md)(与 Transformer 对比)
- **学习线**:AI 基础 → 经典 ML(线性/树/SVM/聚类)→ DL(MLP/CNN/RNN)

### 2. 💬 大语言模型 — `02-llm/`(10 篇)
> LLM 全链路:Transformer、Tokenizer、预训练、微调、RLHF、量化推理、RAG、后训练。

- **代表文章**:[Transformer 架构](02-llm/transformer-architecture.md)、[预训练与规模定律](02-llm/pretraining.md)、[对齐(RLHF 与 DPO)](02-llm/rlhf-alignment.md)、[检索增强生成 RAG](02-llm/rag.md)、[推理的预训练-后训练接口](02-llm/reasoning-pretraining-posttraining.md)(arXiv:2607.16097,缩放律)
- **学习线**:Transformer → Tokenizer → 预训练 → 微调/RLHF → 推理部署 → RAG

### 3. 🛠 Agent — `03-agents/`(62 篇,最大章节)
> Agent 概念、上下文工程、核心组件、框架专题(13 篇)、记忆、设计工程、评测、面试。

- **聚簇① 上下文管理(7 篇)**:[Context Engineering](03-agents/context-engineering.md) → [管理方案全景](03-agents/context-engineering-playbook.md) → [官方一手资料](03-agents/context-engineering-official-sources.md) → [文档漂移治理](03-agents/context-engineering-doc-drift.md) → [代码注释纪律](03-agents/context-engineering-comment-discipline.md) → [压缩与提示缓存](03-agents/context-engineering-compression-caching.md) → [多轮对话上下文管理(nanobot 源码)](03-agents/agent-context-management.md)
- **聚簇② 框架专题(13 篇)**:LangChain / LlamaIndex / AutoGen / nanobot / Qwen-Agent / Deep Agents / Agno / OpenAI SDK / Pydantic AI / AgentScope / MAF / Mastra / VoltAgent + [七方对比](03-agents/agent-frameworks-seven-comparison.md) + [选型地图](03-agents/agent-framework-selection.md)
- **聚簇③ 记忆(3 篇)**:[记忆体系](03-agents/agent-memory-systems.md)(概念)、[共享记忆](03-agents/agent-shared-memory.md)(多 Agent)、[Hermes 记忆工程设计](03-agents/agent-memory-harness-design.md)(源码)
- **多 Agent(4 篇)**:[多 Agent 协作](03-agents/multi-agent.md)(概念)、[Anthropic 多智能体研究系统](03-agents/agent-multi-agent-research-system.md)(orchestrator-worker 一手工程实践)、[Subagent 隔离](03-agents/subagent-isolation.md)、[Session 通信设计](03-agents/agent-collaboration-messaging.md)
- **其他代表**:[生产级 9 层架构](03-agents/ai-infra-layering.md)、[工具调用](03-agents/tool-calling.md)、[持久化运行范式](03-agents/agent-persistence-patterns.md)、[Agent 评测](03-agents/agent-evaluation.md)、[推理时验证设计范式](03-agents/agent-test-time-verification.md)、[10 个 AI Agent 工作流模板](03-agents/agent-workflow-templates.md)、[Building effective agents 五种模式](03-agents/agent-building-effective-agents.md)、[长时任务 Harness 三件套](03-agents/agent-harness-long-running.md)、[OpenAI 长时 agent 三件套](03-agents/agent-long-running-openai.md)、[工具设计五原则](03-agents/agent-tool-design-practice.md)、[基于插件的 Agent 开发范式](03-agents/agent-plugin-development-paradigm.md)、[Outlines Index 文档检索](03-agents/outlines-index-doc-retrieval.md)

### 4. 🚀 实战 — `04-practice/`(12 篇)
> 从理论到落地:项目复现、LLM API 应用、Agent 应用案例、排查清单。

- **代表文章**:[端到端 ML 项目](04-practice/practice-end-to-end-ml.md)、[numpy 从零实现神经网络](04-practice/practice-numpy-nn.md)、[调用 LLM API 构建应用](04-practice/practice-llm-api.md)、[DeepTutor AI 辅导工作空间](04-practice/deeptutor-agent-workspace.md)、[阿里云 AgentTeams](04-practice/aliyun-agentteams-enterprise.md)、[Agent 效果优化实战(AgentLoop 7 步闭环)](04-practice/agent-effect-optimization-practice.md)、[SKILL.md 结果驱动自进化](04-practice/skill-evolution-results-driven.md)

### 5. 📚 参考 — `05-reference/`(4 篇)
> 资源清单:经典论文、书、课程、工具、博客,按主题归档。

- [必读论文清单](05-reference/reference-papers.md)(27 篇)、[书籍与课程](05-reference/reference-books-courses.md)(23 项)、[工具与库](05-reference/reference-tools.md)(37 项)、[博客与社区](05-reference/reference-blogs.md)

### 6. 🏢 企业落地与 FDE — `06-enterprise/`(34 篇,4 子主题)
> 企业真实场景:Ontology 语义层、AI Friendly 架构、组织转型、FDE 方法论。

- [🧬 Ontology 与 Agent 企业落地](06-enterprise/ontology-agent-adoption/index.md)(19 篇):Ontology as Code / 四大技术 / Palantir 系列(6 篇)/ 企业 Agent 工程化(4 篇)/ 落地方法论
- [🏗️ AI Friendly 架构](06-enterprise/ai-friendly-architecture/index.md)(3 篇):后端架构 AI Friendly 标准、[Context System 四层架构](06-enterprise/ai-friendly-architecture/context-system-architecture.md)(事实/上下文/执行/反馈,与 Ontology/Context Engineering 横向汇总)、文档 SSOT
- [🏛️ AI 组织转型与超级个体](06-enterprise/ai-org-transformation/index.md)(3 篇):超级个体→超级组织、企业 AI 战略、个人 AI 思维
- [🧑💻 FDE 理论与方法论](06-enterprise/fde-methodology/index.md)(9 篇):《前线部署工程师》全书拆解(导读+8 章)
- 另含 [生产级 Agent 全景总纲](06-enterprise/production-agent-panorama.md)

### 7. 🛠️ 个人 Agent Coding 经验 — `07-agent-coding/`(42 篇,4 子主题)
> 个人实践视角:使用经验、现成 Skill、项目 Agent 配置、Claude Code 深度解析。

- [💡 使用经验](07-agent-coding/experience/index.md)(20 篇):[Vibe Coding 最佳实践(工程闭环总纲)](07-agent-coding/experience/vibe-coding-engineering-practice.md)、[OpenAI Harness Engineering(0 行手写战报)](07-agent-coding/experience/openai-harness-engineering.md)、Ralph Wiggum 循环、AI TDD、Loop Engineering、Gate 模式、Handoff、Graph Engineering、Agent Hook 等
- [📦 Skill 收藏](07-agent-coding/skills/index.md)(18 篇):GSD / gstack / Spec Kit / SDD / prd-writer / Matt Pocock / [Agent Plugins 1.0 统一插头规范](07-agent-coding/skills/agent-plugins-spec.md) / [Agent Skills 设计理念](07-agent-coding/skills/agent-skills-design.md) / 治理与测评等
- [🔧 项目 Agent 配置](07-agent-coding/agent-config/index.md)(1 篇):Claude Code 个人项目配置拆解
- [🧠 Claude Code 深度解析](07-agent-coding/claude-code-deep-dive/index.md)(10 篇):[官方最佳实践](07-agent-coding/claude-code-deep-dive/claude-code-best-practices.md)(验证闭环/四阶段工作流/规模化)、[Sandboxing](07-agent-coding/claude-code-deep-dive/claude-code-sandboxing.md)(双边界+凭证外置)、架构工具系统 / Worktree / Cross-session / Workflows / Skills-Plugin-Subagent / 源码 20 章 / Tmux

### 8. 🧰 Harness 框架与开源方案 — `08-harness/`(21 篇)
> 开源 Harness 收录索引:编码 Agent、编排框架、配套方案(协议/沙箱/评测)。

- **三类清单**:[编码 Agent 工具](08-harness/coding-agents.md)、[通用编排框架](08-harness/orchestration-frameworks.md)(含 LongHorizon-Harness、DeerFlow 等)、[配套开源方案](08-harness/harness-tools.md)
- **专题收录**:PenguinHarness / [Pi Agent(插件篇)](08-harness/pi-agent-plugins.md) + [Pi 深度解析(哲学/四层/v3)](08-harness/pi-agent-harness-deep-dive.md) / [DeepSeek Harness(一切皆插件)](08-harness/deepseek-harness.md) + [Cordis 插件框架](08-harness/cordis-plugin-framework.md) / Headroom / Avernet / AutoAgent / OpenWorker / 云端软件工厂 等
- 定位:开源**索引**(与 03-agents 框架原理互补)

### 9. 🏫 Agent 前沿学术 — `09-agent-research/`(9 篇)
> 论文解析、研究方法论、开源数据集与基准,偏学术视角。

- **代表文章**:[LongHorizon-Harness 长程任务状态管理](09-agent-research/longhorizon-harness-paper.md)(MEA 状态机)、[DeepVerifier 推理时验证](09-agent-research/inference-time-verification.md)、[自我改进综述](09-agent-research/self-improving-agents-survey.md)、[Self-Harness](09-agent-research/self-harness-paper.md)、[Harness Handbook](09-agent-research/harness-handbook.md)、[LLM 记忆综述](09-agent-research/llm-memory-survey.md)

### 10. 📱 鸿蒙开发 — `10-harmonyos/`(5 篇)
> 独立平台专题(只收鸿蒙):平台全景、ArkUI、质量发布、AI 辅助开发、离线知识库。

- [平台全景与开发基线](10-harmonyos/harmonyos-platform-overview.md)(API 24 生产基线)、[ArkUI 开发](10-harmonyos/harmonyos-arkui-development.md)、[AI 辅助鸿蒙开发](10-harmonyos/harmonyos-ai-development.md)、[鸿蒙离线知识库](10-harmonyos/harmonyos-offline-reference.md)

## 🔗 主题交叉索引(横向检索)

> 同一主题散落在多个章节时,从这里一次找全。

| 主题 | 入口文章(按阅读顺序) |
| --- | --- |
| **上下文管理** | 03:[Context Engineering](03-agents/context-engineering.md) → [多轮对话上下文管理](03-agents/agent-context-management.md) → [压缩与缓存](03-agents/context-engineering-compression-caching.md) → [Subagent 隔离](03-agents/subagent-isolation.md);07:[Ralph Wiggum 循环](07-agent-coding/experience/ralph-wiggum-loop.md)、[Handoff 交接](07-agent-coding/experience/handoff-handover-methodology.md) |
| **记忆** | 03:[记忆体系](03-agents/agent-memory-systems.md)(概念)→ [共享记忆](03-agents/agent-shared-memory.md)(多 Agent)→ [Hermes 工程设计](03-agents/agent-memory-harness-design.md)(源码);09:[LLM 记忆综述](09-agent-research/llm-memory-survey.md)(学术);08:[TencentDB Agent Memory](08-harness/agent-memory-plugin.md)(开源) |
| **工具调用 / MCP** | 03:[工具调用](03-agents/tool-calling.md)、[核心组件](03-agents/agent-core-components.md);08:[配套开源方案](08-harness/harness-tools.md);07:[Claude Code 工具系统](07-agent-coding/claude-code-deep-dive/claude-architecture-tools.md) |
| **Agent 框架选型** | 03:[框架专题(13 篇)](03-agents/index.md)、[七方对比](03-agents/agent-frameworks-seven-comparison.md)、[选型地图](03-agents/agent-framework-selection.md);08:[编排框架清单](08-harness/orchestration-frameworks.md)(开源索引) |
| **Harness / 运行时** | 08:整章(18 篇);09:[Harness Handbook](09-agent-research/harness-handbook.md)、[LongHorizon-Harness](09-agent-research/longhorizon-harness-paper.md)、[Self-Harness](09-agent-research/self-harness-paper.md);07:[AI Coding Harness 设计经验](07-agent-coding/experience/ai-coding-harness-design.md) |
| **长程任务 / 持久化** | 09:[LongHorizon-Harness](09-agent-research/longhorizon-harness-paper.md)(MEA 状态机);03:[持久化运行范式](03-agents/agent-persistence-patterns.md)、[推理时验证](03-agents/agent-test-time-verification.md);08:[DeerFlow](08-harness/orchestration-frameworks.md) 等 |
| **评测 / 验证** | 03:[Agent 评测](03-agents/agent-evaluation.md)、[WorkBuddy Bench](03-agents/workbuddy-bench.md)、[评估驱动开发](03-agents/agent-eval-driven-dev.md)、[性能剖析](03-agents/agent-performance-analysis.md);09:[DeepVerifier](09-agent-research/inference-time-verification.md);07:[Skill 测评](07-agent-coding/skills/skill-evaluation.md)、[SkillHub TRACE](07-agent-coding/skills/skillhub-trace-evaluation.md) |
| **企业落地** | 06:整章(34 篇);03:[业务理解](03-agents/agent-business-understanding.md)、[大规模系统设计](03-agents/agent-system-scaling.md)、[生产级架构](03-agents/agent-production-architecture.md) |
| **Skill 体系** | 07/skills:整子主题(16 篇);03:[开发方法选型(BMAD/Spec Kit/GSD/Skills)](03-agents/agent-development-methods.md);06:[AI Friendly SKILL](06-enterprise/ai-friendly-architecture/ai-friendly-backend.md) |
| **规格驱动开发(SDD/Spec)** | 07:[Spec Kit](07-agent-coding/skills/spec-kit-github.md)、[SDD+OpenSpec+Superpowers](07-agent-coding/skills/sdd-openspec-superpowers.md)、[Spec-First Skill](07-agent-coding/skills/spec-first-skill.md)、[Spec-First 决策栈](07-agent-coding/experience/spec-first-decision-stack.md);04:[得物 Spec-Driven 案例](04-practice/ai-native-order-system-spec-driven.md) |
| **Claude Code** | 07/claude-code-deep-dive:整子主题(10 篇);07/experience:Agent Hook 实战、Git Worktree 等 |

## 📊 结构说明与合并归类建议

**✅ 已执行的轻量归类**:
- `03-agents/index.md` 将 13 篇框架文章划入「🧩 框架专题」小节,与其余设计/工程文章分组,便于按图索骥。

**🟡 有意保持"双视角"、不建议合并**(每对都是"工具机制"与"方法论"互补):
- `handoff-skill.md`(Skill 收藏)vs `handoff-handover-methodology.md`(使用经验)
- `spec-first-skill.md`(Skill 收藏)vs `spec-first-decision-stack.md`(使用经验)
- `agent-hooks-usage.md`(指南)vs `agent-hooks-codex-claude-practice.md`(实战配置)
- `gate-pattern.md`(独立详解)vs `agent-cognitive-complexity-gates.md`(主文)
- 03-agents「框架专题」vs 08-harness「编排框架清单」:前者讲原理与用法,后者是开源索引,分工明确。

**🟢 可选优化(需确认后执行,均为非破坏性)**:
1. `05-reference/reference-papers.md` 增加指向 09-agent-research 各论文解析的交叉链接;
2. 03-agents 上下文聚簇(7 篇)已在 index 连续排列,可考虑在 `agent-context-management.md` 顶部加"本聚簇导航";
3. 若觉得 03-agents(62 篇)过大,可将「框架专题 13 篇」整体迁往 08-harness——**不建议**:03 是"学习框架",08 是"开源索引",语义不同。

**🚫 不建议的合并**:不同章节的论文解析/工程实现(如 09 的 longhorizon-harness 与 08 的清单条目)、跨领域文章(鸿蒙与 AI 章节完全独立,勿动)。

## 📥 收件箱

- 所有新资料先进 [docs/inbox/README.md](inbox/README.md),任务登记在 [docs/inbox/tasks.md](inbox/tasks.md)(该文件不进站点)。
- 待整理队列、已归档记录与原始素材(`*-source.md`)都在 inbox 目录,归档后原始素材保留不删。

---
*本索引随知识库演进持续维护;发现文章增删或章节调整,请先更新本文件再提交。*
