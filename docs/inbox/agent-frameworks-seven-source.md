# 原始资料:Agent 框架七方对比:Agno / OpenAI Agents SDK / Pydantic AI / AgentScope / Microsoft Agent Framework / Mastra / VoltAgent

> 来源:微信公众号(作者:improvedNPC);原文链接:https://mp.weixin.qq.com/s/4WqTup7EwoBko-jfrozlgw
> 抓取日期:2026-08-09;状态:已整理为综述文章 + 七个框架独立文章
> 性质:七框架横向对比综述(维护方/代码规模/整洁度/功能/依赖/工程化/选型建议)

---

一句话定位
Agno — “Agent 平台 SDK”，生态覆盖面最广（46 模型 / 100+ 工具 / 18 向量库 / 16 存储），自带 AgentOS 生产运行时，cookbook 海量。

OpenAI Agents SDK — OpenAI 官方，Realtime / Voice 独家，轻量核心，扩展生态大。

Pydantic AI — Pydantic 官方，工程严谨度天花板，单 Agent + 工作流 + evals/graph 闭环。

AgentScope — 阿里通义，平台级开箱即用（多租户 / 沙箱 / 权限 / 长期记忆），docstring 最全。

Microsoft Agent Framework（MAF） — 微软官方，多语言（Python + .NET）双栈，核心极轻量（4 依赖），企业级可观测/持久化/治理，深度绑定 Azure 生态。

Mastra — TypeScript 框架，体量最大、包最多（140+），全栈覆盖（Storage/Voice/Auth/Deployer/Playground），JS 生态最完整的 Agent 平台。

VoltAgent — TypeScript 框架，框架 + VoltOps Console 平台双形态，全 provider 内建、文档/示例生态强、起步晚但迭代快（2025-04 起）。

1. 基本面

Agno
OpenAI SDK
Pydantic AI
AgentScope
MAF
Mastra
VoltAgent
维护方
Agno（原 Phidata）
OpenAI 官方
Pydantic 团队
阿里通义
微软官方
Mastra（独立）
VoltAgent（独立）
语言
Python
Python
Python
Python
Python + .NETTypeScriptTypeScript版本
2.6.20
0.17.7
2.1.1
2.0.4dev
Py 1.10.0/.NET 1.11.1
多包 changesets
多包 changesets
状态
稳定,1–3 天/版
0.x 演进中
Stable
Beta
核心稳定,扩展多 preview
稳定,高频发版
稳定,高频发版
贡献者
507
301
51668
156
52674
提交数
5,763
1,645
2,242
v2.0 以来 81
2,438
16,2841,731
Tags
207
105
272
41
166
5,600700
起步
2023-11
2025-03
2024-06
较早+v2 重构
2025
2024-08
2025-04

社区与迭代：Mastra 提交最频繁（16k+）；Pydantic AI / Mastra 贡献者最多（~520）；VoltAgent 起步最晚（2025-04）但 14 个月已 1.7k 提交/700 tag,迭代很快,不过贡献者仅 74 人且含 bot,集中度高。MAF 双语言但贡献者偏少且集中；OpenAI SDK 仍 0.x；AgentScope 社区最小。注意 Mastra/VoltAgent 第一大提交者是 AI bot,提交量含自动化成分。
2. 代码规模

Agno
OpenAI SDK
Pydantic AI
AgentScope
MAF
Mastra
VoltAgent
核心源码
~32.9 万(885)
~9.4 万(284)
~9.3 万(278)
~6.3 万(289)
Py ~13.7 万+.NET ~12.2 万
~118 万(6,227)
~30 万(1,665)
测试代码
~27.6 万(930)
~14.7 万(281)
~20.5 万(199)
~5.1 万(90)
Py ~19.4 万+.NET ~18 万
~78 万(2,135)
~5.7 万(203)
测试/源码比
0.84×
1.57×
2.2×0.8×
Py ~1.4×/.NET ~1.5×
~0.66×
~0.19×(偏低)
示例
2,101 cookbook
214
41
5+web_ui
Py 486+.NET 467
25+ 模板
87 示例

Mastra 体量最大（源码 118 万行）；MAF 双语言合计 ~76 万行；Agno 33 万行；VoltAgent 30 万行居中。Pydantic AI 测试投入比例最健康（2.2×）；VoltAgent 测试/源码比最低（0.19×）,测试治理最薄弱。
可维护性风险点：Agno 超大文件（workflow.py 10,794 行）、Mastra “上帝包”（packages/core 23.4 万行）、VoltAgent 核心包 11.4 万行占 38% 偏重。
3. 代码整洁度

Agno
OpenAI SDK
Pydantic AI
AgentScope
MAF
Mastra
VoltAgent
Lint/Type
ruff+mypy
ruff+mypy strict+pyright basic(弱)
ruff+pyright strict+mypyblack+flake8+mypy+pylint(旧,无 ruff)
ruff+pyright strict+mypy strict+banditeslint+prettier+stylelint+TS strict
biome+prettier+TS strict
类型注解
返回88%/参数78%
近100%
82–96%
100%高(pyright strict 强制)
TS strict 全量
TS strict(4 包未启用)
Docstring
67.7%
32%(低)
53–81%
95%+Google 风格,CPY 强制
中(TS 注解为主)
包 README 缺(12/33 无)
Coverage 门控
无
85%(omit 7.4% 有水分)
fail_under=100无
Py 85%/.NET 80%(按包强制)
无 threshold
仅 2 包 100%,核心包无门控
pre-commit
❌
❌
✅
✅
✅
husky+lint-staged(仅 format)
husky+lint-staged+commitlint
py.typed/声明
✅
✅
✅
✅
✅
TS 声明
TS 声明

整洁度结论：
类型严格度：MAF 最严（pyright strict + mypy strict + bandit 双语言全覆盖），Pydantic AI 次之，Mastra/VoltAgent TS strict 全量（VoltAgent 4 包未启用是缺口）。

类型注解密度：OpenAI SDK / AgentScope 最高（近 100%），Agno 偏低。

Docstring/包文档：AgentScope 最全（95%+）；VoltAgent 12/33 包无 README 是明显短板；OpenAI SDK 函数 docstring 32% 最薄。

测试门控：仅 Pydantic AI 有 100% 硬门控；MAF 按包强制 85%/80%；Agno/AgentScope/Mastra/VoltAgent 都无全局门控（VoltAgent 仅 2 包）。

MAF 独有亮点：强制版权头、bandit 安全扫描、.NET TreatWarningsAsErrors + nullable。

VoltAgent 亮点：Biome 现代化、commitlint 强制 Conventional Commits、syncpack 管理依赖一致性。

4. 功能完善度
能力
Agno
OpenAI SDK
Pydantic AI
AgentScope
MAF
Mastra
VoltAgent
模型 provider
46 家OpenAI+100+
30+
十余家
OpenAI/Azure/Anthropic/Gemini/Ollama/Bedrock 等
40+
全 provider 内建(core 44 依赖)
多 Agent 编排
team+workflow
handoffs
graph 引擎
事件总线
顺序/并发/handoff/group+checkpoint+time-travel
图工作流(.then/.branch/.parallel)
sub-agents+workflow
生产运行时
AgentOS❌
❌
FastAPI 多租户
Foundry Hosted+Durable Task
server+deployer+playground
server-hono/elysia+VoltOps Console
沙箱
❌(infra docker)
✅ 多家
❌
✅ 本地/Docker/E2B
✅(Hyperlight 等)
✅(browser agent)
✅(e2b/blaxel)
权限/RBAC
✅ JWT
❌
❌
✅
✅(Purview 治理)
✅(auth 12 适配器)
✅(Guardrails)
长期记忆
✅
✅
仅 embeddings
✅ Qdrant+Mem0
✅ sessions+持久化
✅ memory+RAG+观察记忆
✅ memory+RAG
Vector/Storage DB
18/16 种❌
❌
Qdrant
Cosmos/Redis/Azure AI Search
27 storelibsql/postgres/supabase/cf-d1
Realtime/Voice
❌
✅ 独家❌
❌(仅 TTS)
❌
✅(17 voice)
✅(voice)
Guardrails
❌
✅
❌
❌
❌
❌
✅
评估框架
✅ eval
❌
✅ pydantic-evals❌
❌
✅ evals
✅ evals+scorers
图/工作流
✅ workflow
❌
✅ pydantic-graph
❌
✅(强项,checkpoint/time-travel)
✅(图原生)
✅ workflow
持久化执行
❌
✅ temporal
✅ DBOS/Temporal/Prefect
❌
✅ Durable Task 强项✅(durable agents)
✅(resumable-streams)
多接口(Slack/TG/WA)
✅ 独家❌
❌
❌
A2A/AG-UI
✅(client-sdks 多框架)
A2A/MCP server
声明式 Agent
❌
❌
❌
❌
✅ YAML 独家❌
❌
MCP / HITL / Tracing
✅
✅
✅
✅
✅
✅
✅
多语言运行时
❌
❌
❌
❌
✅ Python+.NET 独家❌(仅 TS)
❌(仅 TS)
部署生态
❌
❌
❌
❌
Azure Functions/Foundry
vercel/cloudflare/netlifyserverless-hono/多 server 框架

功能特色：
Agno 独家：最广的模型/工具/向量库/存储集成矩阵；多聊天接口（Slack/TG/WA）。

OpenAI SDK 独家：Realtime/Voice、Guardrails。

Pydantic AI 独家：evals + graph + durable-exec 工程闭环最完整。

AgentScope 独家：沙箱 + 权限 + 长期记忆 + 多租户一体化最完整。

MAF 独家：Python + .NET 双语言、声明式 YAML Agent、Durable Task 持久化/time-travel、Azure 治理（Purview）。

Mastra 独家：JS 生态最完整全栈（27 store/17 voice/12 auth/8 server-adapter/4 deployer）、Playground 可视化、模板化项目脚手架。

VoltAgent 特色：框架 + VoltOps Console 平台双形态、全 provider 内建开箱即用、Guardrails + evals + scorers 一体、resumable-streams 可恢复流。

5. 依赖与文档

Agno
OpenAI SDK
Pydantic AI
AgentScope
MAF
Mastra
VoltAgent
核心依赖
最轻(13)
轻(7)
最轻(slim)
重(24)
最轻(4)中(ai-sdk/mcp/ws…)
重(core 44 prod deps)Extras/包
127 extras
20
~30
9
35 Py+39 .NET
140+ 包33 包
仓库内文档
docs 私有392 文件/4.3 万行,四语
166 md/3.5 万行
仅 4 文件
49 md/2 万行+MS Learn
905 md/22.3 万行342 md/7.2 万行+Docusaurus
示例
2,101 cookbook
214
41
5
Py 486+.NET 467
25+ 模板
87 示例

MAF 核心最轻（仅 4 运行时依赖）；Mastra 文档/包最多；VoltAgent 核心包依赖最重（44 prod deps,因全 provider 内建）；Agno docs 私有不透明是短板；OpenAI SDK 文档+示例公开度最好（四语）；AgentScope 仓库内文档最薄。VoltAgent 文档/示例生态强（342 篇 + 87 示例 + 多语言 README）,但 12/33 包无 README。
6. 工程化

Agno
OpenAI SDK
Pydantic AI
AgentScope
MAF
Mastra
VoltAgent
CI 矩阵
Py3.10/3.12+30 模型 job
Py3.10–3.14+Win
Py3.10–3.14×4+最低版本
3 OS×Py3.11
Py3.10–3.14+Win/.NET 多目标
33 workflow,分片+矩阵
Node 20/22/24,11 包入矩阵
集成测试
真实模型 API 逐家
mock 为主
VCR 录制回放
AsyncMock
pytest.mark.integration+.NET
Vitest unit/e2e+store 矩阵
Vitest+PostgreSQL+E2E(条件)
供应链安全
无 Dependabot
trusted publishing
Dependabot+zizmor+SHA+隔离 build/publish基础 CI
CODEQL+dependabot
Renovate+OIDC+blockExoticSubdeps无 Dependabot/Renovate
AI code review
✅ claude.yml
❌
❌
❌
❌
CodeRabbit
❌
发布自动化
PyPI/TestPyPI
release-pr→tag→PyPI
隔离 build/publish
PyPI 自动
双语言独立发版
changesets alpha/stable/snapshotchangesets+publint+syncpack

工程严谨度：Pydantic AI 供应链安全最严；Mastra 发布流水线最先进；MAF 双语言 CI 矩阵最复杂；VoltAgent 工程基础扎实（Biome/commitlint/syncpack/publint）但 CI 仅 11 包入测试矩阵、无依赖自动更新；Agno/AgentScope 最基础。
安全响应亮点：Agno 对 PyPI 受污染的 litellm/mistralai 显式禁用；Mastra 大量 overrides+patchedDependencies 处理漏洞；VoltAgent 有完善 SECURITY.md（72 小时响应）。
7. 优劣速览
Agno
优：生态最广（46 模型/100+ 工具/18 向量库/16 存储）、AgentOS 生产运行时完整、cookbook 海量、发版最频繁、核心依赖最轻、安全响应及时。劣：docs 私有不透明、无 coverage 门控、超大文件（10k+ 行）可维护性差、docstring 67% 偏低、无 pre-commit/Dependabot、集成测试依赖真实 API 易 flaky、requires-python>=3.7 与实际语法脱节。
OpenAI Agents SDK
优：OpenAI 官方、Realtime/Voice 独家、沙箱生态广、类型注解近 100%、四语文档+214 示例。劣：0.x API 不稳定、pyright basic 名实不符、docstring 32% 薄、coverage 85% 有水分、无 pre-commit。
Pydantic AI
优：工程严谨度顶尖（pyright strict + 100% coverage）、社区最大、slim 核心轻、evals/graph/durable-exec 闭环、供应链安全最严。劣：代码库庞大复杂、docstring 中等、v1→v2 breaking 多、无内置服务运行时。
AgentScope
优：服务化开箱即用（多租户/沙箱/权限/长期记忆）、docstring 最全（95%+）、多智能体事件系统、双语社区。劣：Beta + v2.0 一个月、仓库内文档薄、核心依赖重、Lint 工具链旧无 ruff、测试无门控。
Microsoft Agent Framework（MAF）
优：微软官方、Python + .NET 双语言独一档、核心极轻（4 依赖）、类型检查最严（pyright strict + mypy strict + bandit 双栈）、Durable Task 持久化/time-travel 强、声明式 YAML Agent、Azure 生态治理深。劣：大量扩展包仍 preview/alpha（35 包仅 5 个 released）、历史短（2025 起）、.NET 依赖偏重且多预览版、CODEOWNERS 覆盖不足、深度绑定 Azure 上手门槛高。
Mastra
优：TS 生态最完整全栈（140+ 包/27 store/17 voice/12 auth）、文档最多（905 篇）、发版最频繁（16k 提交）、changesets+OIDC+Renovate 发布流水线先进、Playground 可视化、模板脚手架完善。劣：体量巨大（118 万行源码）认知/构建成本高、packages/core 23.4 万行“上帝包”、无 coverage 门控、依赖网络复杂（多版本 alias + 大量 overrides/patches）、AI bot 提交占比高、pre-commit 仅 format。
VoltAgent
优：框架 + VoltOps Console 平台双形态、全 provider 内建开箱即用、Guardrails+evals+scorers 一体、文档/示例生态强（342 篇+87 示例+多语言 README）、工程基础扎实（Biome/commitlint/syncpack/publint/husky）、起步晚但迭代快（14 个月 1.7k 提交）、SECURITY 完善。劣：测试治理最薄弱（测试/源码比 0.19×、核心包无 coverage 门控、CI 仅 11 包入矩阵）、核心包依赖最重（44 prod deps）、12/33 包无 README、4 包未启用 strict TS、未用 workspace protocol、无依赖自动更新、保留 3 个空壳废弃包、AI bot 提交占比高。
8. 选型建议（七方）
要最广的模型/工具/存储集成矩阵 + 生产运行时 + 多聊天接口（Slack/TG/WA） → Agno（生态最全，接受 docs 不透明和超大文件风险）。

语音/Realtime 实时对话/Guardrails → OpenAI Agents SDK（独家，接受 0.x 不稳定）。

最强工程规范/类型安全/可测试性 + evals/graph 闭环 → Pydantic AI（最稳，工程标杆）。

企业级多智能体服务（沙箱+权限+长期记忆一体化） → AgentScope（省基础设施，接受 Beta 风险）。

微软/.NET 栈 + Azure 生态 + 声明式 Agent + 持久化可重启工作流 → Microsoft Agent Framework（双语言独一档，接受扩展包 preview 风险）。

TypeScript/JS 全栈 + 丰富 store/voice/auth 部署生态 + 可视化 Playground → Mastra（JS 生态最完整，接受体量与复杂度）。

TypeScript + 全 provider 开箱即用 + 框架/平台双形态 + Guardrails/evals 一体 → VoltAgent（上手快、文档好，接受测试治理薄弱和核心依赖重）。

综合成熟度排序（工程严谨度 + 社区 + 稳定性 + 文档透明度）：
Pydantic AI ≈ MAF > Agno ≈ Mastra > OpenAI SDK ≈ VoltAgent > AgentScope
说明：
Pydantic AI 与 MAF 工程严谨度并列最高——前者胜在 100% 覆盖率门控 + 稳定 API + 社区最大；后者胜在双语言 + 最严类型检查 + 企业治理，但扩展包 preview 拖累。

Agno / Mastra 功能广度与生产运行时最强，但前者 docs 私有 + 超大文件，后者体量过大 + 无覆盖率门控。

OpenAI SDK / VoltAgent 各有独家能力但工程成熟度有缺口——前者 0.x 不稳定，后者起步晚 + 测试治理薄弱（0.19× 测试比、核心包无门控）。

AgentScope 平台一体化设计优秀，但 Beta + v2.0 刚起步 + 工程化最弱。

七者语言栈（Python / .NET / TypeScript）和部署生态差异大，应按需求（语言/部署生态/独家能力）而非纯排名选。