# Agent 框架七方对比:Agno / OpenAI Agents SDK / Pydantic AI / AgentScope / MAF / Mastra / VoltAgent

> **一句话摘要**:2026 年 Agent 框架格局的七方横评——从**维护方、代码规模、整洁度、功能完善度、依赖文档、工程化**六个维度对比 Agno、OpenAI Agents SDK、Pydantic AI、AgentScope、Microsoft Agent Framework、Mastra、VoltAgent,并给出选型建议与综合成熟度排序。七框架各自独立成文(见延伸阅读)。
>
> **来源**:微信公众号《Agent 框架七方对比》(作者:improvedNPC),https://mp.weixin.qq.com/s/4WqTup7EwoBko-jfrozlgw;七框架核心知识由官方文档调研补充;原始资料存档于 `docs/inbox/agent-frameworks-seven-source.md`

## 概念:一句话定位

| 框架 | 一句话定位 |
| --- | --- |
| **Agno** | "Agent 平台 SDK",生态覆盖面最广(46 模型 / 100+ 工具 / 18 向量库 / 16 存储),自带 AgentOS 生产运行时,cookbook 海量 |
| **OpenAI Agents SDK** | OpenAI 官方,Realtime / Voice 独家,轻量核心,扩展生态大 |
| **Pydantic AI** | Pydantic 官方,工程严谨度天花板,单 Agent + 工作流 + evals/graph 闭环 |
| **AgentScope** | 阿里通义,平台级开箱即用(多租户 / 沙箱 / 权限 / 长期记忆),docstring 最全 |
| **Microsoft Agent Framework (MAF)** | 微软官方,多语言(Python + .NET)双栈,核心极轻量(4 依赖),企业级可观测/持久化/治理,深度绑定 Azure |
| **Mastra** | TypeScript 框架,体量最大、包最多(140+),全栈覆盖(Storage/Voice/Auth/Deployer/Playground),JS 生态最完整 |
| **VoltAgent** | TypeScript 框架,框架 + VoltOps Console 平台双形态,全 provider 内建、文档/示例生态强、起步晚但迭代快 |

**语言栈分布**:Python 系(Agno / OpenAI SDK / Pydantic AI / AgentScope)+ 双语言(MAF:Python+.NET)+ TypeScript 系(Mastra / VoltAgent)。

## 原理:六维对比

### 1. 基本面与社区迭代

| | Agno | OpenAI SDK | Pydantic AI | AgentScope | MAF | Mastra | VoltAgent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 维护方 | Agno(原 Phidata) | OpenAI 官方 | Pydantic 团队 | 阿里通义 | 微软官方 | Mastra(独立) | VoltAgent(独立) |
| 语言 | Python | Python | Python | Python | Python+.NET | TypeScript | TypeScript |
| 起步 | 2023-11 | 2025-03 | 2024-06 | 较早+v2 重构 | 2025 | 2024-08 | 2025-04 |
| 贡献者 | 507 | 301 | 516 | 68 | 156 | 526 | 74 |
| 提交数 | 5,763 | 1,645 | 2,242 | v2 以来 81 | 2,438 | 16,284 | 1,731 |

**要点**:Mastra 提交最频繁(16k+);Pydantic AI / Mastra 贡献者最多;VoltAgent 起步最晚但 14 个月 1.7k 提交/700 tag,迭代很快,不过贡献者仅 74 人且含 bot,集中度高;MAF 双语言但贡献者偏少;OpenAI SDK 仍 0.x;AgentScope 社区最小。**注意 Mastra/VoltAgent 第一大提交者是 AI bot,提交量含自动化成分。**

### 2. 代码规模与可维护性

| | Agno | OpenAI SDK | Pydantic AI | AgentScope | MAF | Mastra | VoltAgent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 核心源码 | ~32.9 万行 | ~9.4 万 | ~9.3 万 | ~6.3 万 | Py 13.7 万+.NET 12.2 万 | ~118 万 | ~30 万 |
| 测试/源码比 | 0.84× | 1.57× | **2.2×** | 0.8× | Py 1.4×/.NET 1.5× | ~0.66× | **0.19×** |

**要点**:Mastra 体量最大(118 万行);Pydantic AI 测试投入比例最健康(2.2×);VoltAgent 测试治理最薄弱(0.19×)。可维护性风险点:Agno 超大文件(workflow.py 10,794 行)、Mastra "上帝包"(packages/core 23.4 万行)、VoltAgent 核心包 11.4 万行占 38%。

### 3. 代码整洁度

| | Agno | OpenAI SDK | Pydantic AI | AgentScope | MAF | Mastra | VoltAgent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 类型检查 | ruff+mypy | ruff+mypy | pyright strict | basic(弱) | **pyright strict+mypy strict+bandit** | TS strict 全量 | TS strict(4 包未启用) |
| Docstring | 67.7% | 32%(低) | 53–81% | **95%+** | 中 | 中 | 12/33 包无 README |
| Coverage 门控 | 无 | 85%(有水分) | **fail_under=100** | 无 | Py 85%/.NET 80% | 无 | 仅 2 包 |

**要点**:类型严格度 MAF 最严(双语言全覆盖);类型注解密度 OpenAI SDK / AgentScope 最高;docstring AgentScope 最全;测试门控仅 Pydantic AI 有 100% 硬门控;MAF 独有强制版权头 + bandit 安全扫描 + .NET TreatWarningsAsErrors;VoltAgent 亮点是 Biome + commitlint 强制 Conventional Commits + syncpack 依赖一致性。

### 4. 功能完善度

| 能力 | Agno | OpenAI SDK | Pydantic AI | AgentScope | MAF | Mastra | VoltAgent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 模型 provider | **46 家** | OpenAI+100+ | 30+ | 十余家 | OpenAI/Azure/Anthropic/Gemini/Ollama/Bedrock 等 | 40+ | 全 provider 内建 |
| 多 Agent 编排 | team+workflow | handoffs | graph 引擎 | 事件总线 | 顺序/并发/handoff/group+time-travel | 图工作流 | sub-agents+workflow |
| 生产运行时 | **AgentOS** | ❌ | ❌ | FastAPI 多租户 | Foundry Hosted+Durable Task | server+deployer+playground | server+VoltOps Console |
| 沙箱 | ❌ | ✅ 多家 | ❌ | ✅ 本地/Docker/E2B | ✅(Hyperlight 等) | ✅(browser agent) | ✅(e2b/blaxel) |
| 权限/RBAC | ✅ JWT | ❌ | ❌ | ✅ | ✅(Purview) | ✅(12 auth 适配器) | ✅(Guardrails) |
| 长期记忆 | ✅ | ✅ | 仅 embeddings | ✅ Qdrant+Mem0 | ✅ sessions+持久化 | ✅ memory+RAG+观察记忆 | ✅ memory+RAG |
| Realtime/Voice | ❌ | ✅ **独家** | ❌ | ❌ | ❌ | ❌ | ❌ |
| 声明式 Agent | ❌ | ❌ | ❌ | ❌ | ✅ **YAML 独家** | ❌ | ❌ |
| 多语言运行时 | ❌ | ❌ | ❌ | ❌ | ✅ **Python+.NET 独家** | ❌ | ❌ |
| MCP / HITL / Tracing | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**功能特色**:Agno 独家最广集成矩阵 + 多聊天接口(Slack/TG/WA);OpenAI SDK 独家 Realtime/Voice/Guardrails;Pydantic AI 独家 evals+graph+durable-exec 闭环最完整;AgentScope 独家沙箱+权限+长期记忆+多租户一体化最完整;MAF 独家双语言+声明式 YAML+Durable Task 持久化/time-travel+Azure 治理;Mastra 独家 JS 生态最完整全栈+Playground 可视化+模板脚手架;VoltAgent 独家框架+平台双形态+Guardrails/evals/scorers 一体+resumable-streams 可恢复流。

### 5. 依赖与文档

| | Agno | OpenAI SDK | Pydantic AI | AgentScope | MAF | Mastra | VoltAgent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 核心依赖 | 最轻(13) | 轻(7) | 最轻(slim) | 重(24) | **最轻(4)** | 中 | 重(core 44 prod deps) |
| 仓库内文档 | docs 私有(短板) | 392 文件四语 | 166 md | 仅 4 文件 | 49 md+MS Learn | **905 md** | 342 md+Docusaurus |
| 示例 | 2,101 cookbook | 214 | 41 | 5 | Py 486+.NET 467 | 25+ 模板 | 87 示例 |

**要点**:MAF 核心最轻(4 依赖);Mastra 文档最多;VoltAgent 核心依赖最重(全 provider 内建);Agno docs 私有不透明是短板;OpenAI SDK 文档+示例公开度最好(四语);AgentScope 仓库内文档最薄。

### 6. 工程化与供应链安全

| | Agno | OpenAI SDK | Pydantic AI | AgentScope | MAF | Mastra | VoltAgent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CI 矩阵 | Py3.10/3.12+30 模型 job | Py3.10–3.14+Win | Py3.10–3.14×4 | 3 OS×Py3.11 | Py3.10–3.14+Win/.NET | 33 workflow 分片矩阵 | Node 20/22/24,11 包 |
| 供应链安全 | 无 Dependabot | trusted publishing | **Dependabot+zizmor+SHA 最严** | 基础 CI | CODEQL+dependabot | Renovate+OIDC | 无 Dependabot/Renovate |
| AI code review | ✅ claude.yml | ❌ | ❌ | ❌ | ❌ | CodeRabbit | ❌ |
| 发布自动化 | PyPI/TestPyPI | release-pr→PyPI | 隔离 build/publish | PyPI 自动 | 双语言独立发版 | **changesets alpha/stable/snapshot** | changesets+publint+syncpack |

**要点**:Pydantic AI 供应链安全最严;Mastra 发布流水线最先进;MAF 双语言 CI 矩阵最复杂;VoltAgent 工程基础扎实但 CI 仅 11 包入矩阵。安全响应亮点:Agno 显式禁用被污染的 litellm/mistralai;Mastra 大量 overrides/patches 处理漏洞;VoltAgent 有完善 SECURITY.md(72 小时响应)。

## 实践 / 应用:优劣速览与选型

### 各框架优劣势速览

| 框架 | 优 | 劣 |
| --- | --- | --- |
| **Agno** | 生态最广、AgentOS 生产运行时完整、cookbook 海量、发版最频繁、核心依赖最轻、安全响应及时 | docs 私有不透明、无 coverage 门控、超大文件可维护性差、docstring 67% 偏低、集成测试依赖真实 API 易 flaky |
| **OpenAI SDK** | 官方、Realtime/Voice 独家、沙箱生态广、类型注解近 100%、四语文档 | 0.x API 不稳定、pyright basic 名实不符、docstring 32% 薄、coverage 85% 有水分 |
| **Pydantic AI** | 工程严谨度顶尖、社区最大、slim 核心轻、evals/graph/durable-exec 闭环、供应链安全最严 | 代码库庞大复杂、v1→v2 breaking 多、无内置服务运行时 |
| **AgentScope** | 服务化开箱即用、docstring 最全、多智能体事件系统、双语社区 | Beta+v2.0 刚起步、仓库内文档薄、核心依赖重、Lint 工具链旧、测试无门控 |
| **MAF** | 双语言独一档、核心极轻(4 依赖)、类型检查最严、Durable Task 持久化/time-travel 强、声明式 YAML、Azure 治理深 | 扩展包大量 preview(35 包仅 5 个 released)、历史短、.NET 依赖偏重、深度绑定 Azure 门槛高 |
| **Mastra** | TS 生态最完整全栈、文档最多、发版最频繁、发布流水线先进、Playground 可视化 | 体量巨大认知成本高、上帝包、无 coverage 门控、依赖网络复杂、AI bot 提交占比高 |
| **VoltAgent** | 框架+平台双形态、全 provider 内建开箱即用、Guardrails/evals/scorers 一体、文档示例强、工程基础扎实 | 测试治理最薄弱(0.19×)、核心依赖最重、12/33 包无 README、无依赖自动更新、AI bot 提交占比高 |

### 选型建议(七条路线)

1. **要最广的模型/工具/存储集成矩阵 + 生产运行时 + 多聊天接口(Slack/TG/WA)** → **Agno**(接受 docs 不透明和超大文件风险);
2. **语音/Realtime 实时对话/Guardrails** → **OpenAI Agents SDK**(独家,接受 0.x 不稳定);
3. **最强工程规范/类型安全/可测试性 + evals/graph 闭环** → **Pydantic AI**(最稳,工程标杆);
4. **企业级多智能体服务(沙箱+权限+长期记忆一体化)** → **AgentScope**(省基础设施,接受 Beta 风险);
5. **微软/.NET 栈 + Azure 生态 + 声明式 Agent + 持久化可重启工作流** → **Microsoft Agent Framework**(双语言独一档,接受扩展包 preview 风险);
6. **TypeScript/JS 全栈 + 丰富 store/voice/auth 部署生态 + 可视化 Playground** → **Mastra**(JS 生态最完整,接受体量与复杂度);
7. **TypeScript + 全 provider 开箱即用 + 框架/平台双形态 + Guardrails/evals 一体** → **VoltAgent**(上手快文档好,接受测试治理薄弱和核心依赖重)。

### 综合成熟度排序

> **Pydantic AI ≈ MAF > Agno ≈ Mastra > OpenAI SDK ≈ VoltAgent > AgentScope**

- Pydantic AI 与 MAF 工程严谨度并列最高——前者胜在 100% 覆盖率门控+稳定 API+社区最大;后者胜在双语言+最严类型检查+企业治理,但扩展包 preview 拖累;
- Agno / Mastra 功能广度与生产运行时最强,但前者 docs 私有+超大文件,后者体量过大+无覆盖率门控;
- OpenAI SDK / VoltAgent 各有独家能力但工程成熟度有缺口——前者 0.x 不稳定,后者起步晚+测试治理薄弱;
- AgentScope 平台一体化设计优秀,但 Beta+v2.0 刚起步+工程化最弱。

**七者语言栈(Python / .NET / TypeScript)和部署生态差异大,应按需求(语言/部署生态/独家能力)而非纯排名选。**

## 总结

- **七框架三个语言阵营**:Python 四家(Agno/OpenAI SDK/Pydantic AI/AgentScope)、双语言一家(MAF)、TypeScript 两家(Mastra/VoltAgent);
- **工程严谨度标杆**:Pydantic AI(100% 覆盖率门控)与 MAF(双语言最严类型检查);**测试治理短板**:VoltAgent(0.19×);
- **独家能力**:OpenAI SDK(Realtime/Voice)、MAF(声明式 YAML+双语言+Durable Task)、Agno(最广集成矩阵)、AgentScope(沙箱+权限+记忆一体化)、Mastra(JS 全栈)、VoltAgent(Guardrails/evals/scorers 一体);
- **选型铁律**:先定语言栈与部署生态,再看独家能力,最后参考综合排序——纯排名选型会忽略语言与生态差异;
- **下一步**:每个框架的深入知识与最小示例见独立文章(延伸阅读)。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/4WqTup7EwoBko-jfrozlgw
- **框架独立文章**:
  - [Agno:Agent 平台 SDK](agno-framework.md)
  - [OpenAI Agents SDK](openai-agents-sdk.md)
  - [Pydantic AI:工程严谨度天花板](pydantic-ai-framework.md)
  - [AgentScope:阿里通义平台级框架](agentscope-framework.md)
  - [Microsoft Agent Framework:双语言企业级](microsoft-agent-framework.md)
  - [Mastra:JS 全栈 Agent 平台](mastra-framework.md)
  - [VoltAgent:框架+平台双形态](voltagent-framework.md)
- 站内:[Agent 框架选型地图](agent-framework-selection.md)(三层控制权模型+另一组五框架对比)、[Agent 框架](agent-frameworks.md)(基础概念)、[AgentScope 2.0 专文](../08-harness/agentscope-managed-agents.md)(08-harness 视角)、[通用编排框架](../08-harness/orchestration-frameworks.md)
