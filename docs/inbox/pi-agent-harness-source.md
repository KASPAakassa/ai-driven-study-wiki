# Pi Agent Harness：设计思路解析与学习资料合集

> 整理日期：2026-08-14
> 主题：开源 Harness 框架 Pi（earendil-works/pi）的设计思路拆解 + 分层次学习资料清单
> 一句话定位：**Pi 不是一个"又一款 Claude Code 平替"，而是一套把 Agent 主链路拆成可复用积木的工程样板**——"There are many agent harnesses, but this one is yours."

---

## 一、项目速览

| 维度 | 内容 |
|---|---|
| 全称 | Pi Agent Harness |
| 仓库 | [github.com/earendil-works/pi](https://github.com/earendil-works/pi) |
| 官网 / 文档 | [pi.dev](https://pi.dev/) / [pi.dev/docs/latest](https://pi.dev/docs/latest) |
| 作者 | Mario Zechner（badlogic，libGDX 作者）、Armin Ronacher（Flask / Jinja 作者） |
| 所属组织 | Earendil（2026 年被收购，Mario 继续负责开发） |
| 开源协议 | MIT |
| 技术栈 | 纯 TypeScript，monorepo（npm workspaces），Node ≥ 22，standalone 二进制由 Bun 编译 |
| 规模 | GitHub Star 6 万 → 8 万（快速上升中）；npm 周下载 130 万+；提交 5600+ |
| 核心包 | `pi-ai`、`pi-agent-core`、`pi-tui`、`pi-coding-agent`（另有 telemetry / protocol / client / server / sqlite 后端共 9 个包） |
| 运行形态 | 四种模式：交互式 TUI / print / JSON / RPC / SDK |
| 模型支持 | 15+（官方口径）~ 40+（源码口径）家 Provider：Anthropic、OpenAI、Google、DeepSeek、Kimi、MiniMax、Ollama、OpenRouter 等 |
| 一句话对比 | Cursor / Claude Code = 完整成品 IDE；Pi = 乐高积木，可拼出终端编码助手，也可拆出底层 SDK 嵌入自研系统 |
| 行业佐证 | OpenClaw（38.4 万 Star）深度复用 Pi 的 Runtime 与 TUI；MiniMax Code 明确基于 OpenCode + Pi 搭建 Harness；Oh My Pi（2 万 Star）Fork 自 Pi |

---

## 二、设计哲学：核心为什么这样做

Pi 的设计思想可以用 **"一个小内核 + 最大可塑性"** 概括。官方 README 直白列出了它"故意不做"的东西，这些否定项恰恰是它最有观点的地方。

### 2.1 五个 "No"（官方立场）

| 不做 | 官方理由 | 替代方案 |
|---|---|---|
| **不做 MCP** | MCP server（Playwright 等）常占上下文 7-9%，多数工具用不上 | 构建带 README 的 CLI 工具，模型按需读 README（渐进式披露）+ 用 bash 调用；或写 extension 加 MCP |
| **不做 Sub-agents** | 子代理是"黑盒中的黑盒"，可观测性为零，上下文传递差 | tmux 起多个 Pi 实例；或 extension 实现（官方提供完整示例） |
| **不做权限弹窗** | 权限弹窗是"安全剧场"——能写代码能跑命令时防线已失守 | 默认 YOLO 模式（以启动用户权限运行）；要隔离用 Gondolin 微 VM / Docker / OpenShell |
| **不做 Plan mode** | 计划应落盘为文件，可版本化、可跨会话共享、完全可观测 | 维护 `PLAN.md`；或 extension / 社区 package |
| **不做内置 To-dos** | 待办列表增加模型状态跟踪负担，还容易干扰 LLM | 维护 `TODO.md` 文件，由 Agent 自己读写 |

### 2.2 三条底层信念

1. **极简提示词 + 极简工具集**：系统提示词（含工具定义）< 1000 tokens，只有几行；默认只有 `read / write / edit / bash` 四个工具（外加 grep/find/ls 等只读工具）。作者认为前沿模型已被 RL 训练得足够好，不需要上万 token 的脚手架指令。
2. **可观测性至上**：作者（Mario）最核心的诉求是"精确控制进入上下文的内容 + 检查与模型交互的每一个细节"。文件即状态（TODO.md / PLAN.md / AGENTS.md），一切可见、可审计。
3. **少即是多（在基准上被验证）**：Terminal-Bench 82 个任务中，Pi 以 4 个工具 + 极简 prompt 拿下 **#2**（Claude Opus），击败了大量带 MCP / 子代理 / 后台 bash 的重型 Agent。Terminal-Bench 团队的 Terminus 2（只给模型一个 tmux 会话）也印证了极简方法的有效性。

### 2.3 "上下文工程"是成败关键

Pi 把控制权还给开发者，靠的是：
- **AGENTS.md**：项目级指令，启动时从 `~/.pi/agent/`、父目录、当前目录逐级加载；`AGENTS.override.md` 可整体覆盖。
- **SYSTEM.md**：按项目替换 / 追加默认系统提示词。
- **Compaction（上下文压缩）**：接近上下文上限时自动摘要旧消息，策略完全可自定义（扩展可换成基于主题、代码感知的摘要，或用不同的摘要模型）。
- **Skills**：按需加载的能力包（指令 + 工具），渐进式披露，不爆破 prompt cache。
- **Prompt templates**：Markdown 模板，`/name` 展开。
- **动态上下文**：扩展可在每轮前注入消息、过滤历史、实现 RAG 或长期记忆。

---

## 三、架构设计：四层 Monorepo

### 3.1 分层总览

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: pi-coding-agent  产品层（CLI/TUI 入口）              │
│   交互式 CLI · 会话管理(JSONL 树) · 扩展系统 · Skills ·        │
│   Compaction · 认证(Auth/Trust) · 包管理(pi install)          │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: pi-agent-core    运行时内核（Agent 循环）            │
│   agent-loop(双层循环) · 工具执行(并行/串行/钩子) ·             │
│   steering/follow-up 队列 · 事件流 · 状态管理                  │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: pi-ai            统一 LLM 抽象层                     │
│   stream()/complete() · 40+ Provider 适配器 · TypeBox 工具    │
│   schema · partial-json 增量解析 · 模型发现 · OAuth/API Key    │
├─────────────────────────────────────────────────────────────┤
│  Layer 0: 基础层                                             │
│   pi-tui（差分渲染 TUI） · pi-protocol（CBOR+帧协议）          │
│   pi-telemetry（厂商中立遥测）                                 │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 9 个 npm 包与依赖 DAG

构建顺序（即依赖方向）：`tui → telemetry → ai → agent → sqlite-node → protocol → client → server → coding-agent`

| 包 | npm 名 | 依赖 | 核心职责 |
|---|---|---|---|
| telemetry | `@earendil-works/pi-telemetry` | 无 | 厂商中立遥测契约、类型化 span schema（兼容 OTel 风格） |
| tui | `@earendil-works/pi-tui` | 无 | 差分渲染终端 UI 库（约 600 行核心，含 Darwin/Win32 原生模块） |
| protocol | `@earendil-works/pi-protocol` | 无 | CBOR 编解码 + 4 字节长度前缀帧 + TypeBox schema |
| ai | `@earendil-works/pi-ai` | telemetry | 统一多厂商 LLM API、模型发现、OAuth、Provider 适配器 |
| agent | `@earendil-works/pi-agent-core` | ai, telemetry | Agent 运行时、工具调用循环、状态管理、transport 抽象 |
| client | `@earendil-works/pi-client` | protocol | 远端会话的传输中立客户端 |
| server | `@earendil-works/pi-server` | ai, protocol | 远端会话服务端（experimental） |
| sqlite-node | `@earendil-works/pi-session-backend-sqlite-node` | ai, agent-core | `node:sqlite` 会话持久化后端 |
| coding-agent | `@earendil-works/pi-coding-agent` | agent-core, ai, client, protocol, tui | CLI/TUI 入口、内置工具、会话管理、扩展系统 |

**架构特点**：单向依赖、无循环依赖；`coding-agent` 是入度最大的汇聚点（约 199 个 .ts 文件），`agent` 运行时核心仅 49 个文件；想单独研究模型层跑 `npm --prefix packages/ai test` 即可。

### 3.3 供应链工程化（值得抄作业）

- 直接外部依赖全部锁定精确版本（`.npmrc` 开启 `save-exact` + `min-release-age=2`）；
- `package-lock.json` 为唯一事实来源，pre-commit 阻止意外提交 lockfile；
- 发布包自带 `npm-shrinkwrap.json` 锁死传递依赖；
- CI 用 `npm ci --ignore-scripts`，定时跑 `npm audit`；
- 安装推荐 `--ignore-scripts` 禁用依赖生命周期脚本。

---

## 四、核心机制拆解（源码级）

### 4.1 pi-ai：统一多厂商 LLM 抽象

- **类型体系**：`Api`（协议集合：openai-completions / mistral-conversations / openai-responses / pi-messages…）、`ProviderId`（40+ 已知厂商）、`Model`（id/name/api/provider/baseUrl/cost/contextWindow/compat…）；统一消息模型 `UserMessage / AssistantMessage / ToolResultMessage`；统一 `StopReason`（stop | length | toolUse | error | aborted | deferred）。
- **Provider 适配器 + 工厂**：一个 Provider 可横跨多种协议（`api` 传 map 按 `model.api` 自动分派）；`currentModels()` 把 `fetchModels()` 拉到的远端模型按 id 覆盖/追加到静态目录——订阅类 Provider（Copilot、Claude Pro）模型列表随账号状态动态变化。
- **partial-json 增量解析**：每个 `ToolCall` 挂一个 `partialJson` scratch 缓冲，边收 token 边增量还原参数，用完即删；配合"截断兜底"——`stopReason == "length"` 时整批判失败，宁让模型重发，也不执行参数残缺的 bash。
- **三套认证通道归一**：环境变量 API Key / `auth.json` / 订阅登录（Claude Pro、ChatGPT Plus、Copilot）。

### 4.2 pi-agent-core：双层工具调用循环（agent-loop.ts 仅 792 行）

`runLoop()` 是**双层 while 循环**：内层处理工具调用与 steering 消息，外层承接 follow-up 消息。

```
① 注入 steering 消息（本回合进行中用户插话，立即生效）
→ ② 调用 LLM（streamAssistantResponse，流式）
→ ③ 解析 tool call（partial-json）
→ ④ 截断防御（length → 回灌错误结果要求重发）
→ ⑤ 执行工具（默认并行 Promise.all，结果按原始顺序回灌；单工具可声明 sequential）
→ ⑥ 回灌 tool_result
→ 检查是否该停（result.terminate）
→ 检查 follow-up 队列（agent 本该结束但还有新任务）
```

- **steering 与 follow-up 是两个阶段**：Enter 发 steering（当前工具执行完后立即注入，中断其余工具）；Alt+Enter 发 follow-up（等 Agent 跑完再处理）。
- **事件流驱动**：`runLoop` 不直接返回结果，而是 emit `agent_start / turn_start / message_start / message_update / tool_execution_start / tool_execution_end / agent_end`——UI、日志、遥测、远程 RPC 订阅同一份事件流，运行时与展示完全解耦。
- **钩子机制**：`beforeToolCall`（可拦截，返回 `{block: true, reason}`）/ `afterToolCall`（可改写结果）。权限系统、输出护栏（output-guard）都挂在钩子上，不污染核心循环。
- **为什么能只有 792 行**：责任划分——循环只做循环，错误处理推给下层（pi-ai 把网络错误封装成流内事件），状态维护与重试推给上层（coding-agent 的 AgentSession）。

### 4.3 pi-coding-agent：扩展系统是灵魂

- **四个内置工具**：`read`、`write`、`edit`（精确替换 + 模糊匹配归一化：NFKC、弯引号→直引号、连字符→半角减号、特殊空格→普通空格）、`bash`。
- **扩展 API**：`defineTool` 十几行即可注册新工具（TypeBox 定义参数 schema）；扩展还能：注册命令、挂事件总线、拦截工具调用（permission-gate / tool-override）、自定义渲染器、注入系统提示。**理论上几乎整个 Agent 的可见行为都可被扩展改写**。
- **自扩展（self-extensible）**：扩展是 TS 文件，通过 jiti 加载（无需构建步骤）；Pi 可以在运行中修改自己的扩展文件并**热重载**——"让 Pi 给你写一个缺失的工具，它在同一轮里写完、加载、开用"。
- **60+ 示例扩展**：`examples/extensions/` 下躺着 sub-agent、plan-mode、permission-gate、protected-paths、SSH 执行、sandbox、git checkpoint、自定义 compaction、甚至 Space Invaders / Doom 小游戏。
- **会话管理**：JSONL 传输格式（append-only、断点续传）；会话按项目存于 `~/.pi/agent/`；**会话树**支持 branch / fork / clone（`/tree` 回到任意历史点继续）；`/export` 导出 HTML、`/share` 上传 gist 生成可分享 URL；持久化后端可插拔（默认 node:sqlite，memory 用于测试，search.ts 提供会话内全文检索）。
- **权限与安全边界**：默认以启动用户权限运行（YOLO）；工程层防护靠扩展（project-trust / output-guard / protected-paths）；部署层隔离可选三种沙箱（见下）。

### 4.4 pi-tui：差分渲染终端 UI

- 保留模式（Retained Mode）渲染：只重写变化行，整个更新包在"同步输出"（CSI 2026）中，防撕裂；
- 视口追踪：滚动区行号与硬件光标行号分开维护，`computeLineDiff` 只算最小光标位移；
- 全量重绘条件刻意收紧：仅终端宽度变化时全量重绘（Termux 软键盘场景跳过）；
- 支持 Kitty 图像协议在终端渲染图片。

### 4.5 协议层：CBOR + 帧封装

消息编码为 CBOR，外层套 4 字节大端长度前缀帧（单帧上限 16MB）；`FrameDecoder` 是增量式的（任意字节块 push 出完整帧）；所有 schema 由 TypeBox 定义，编解码 / 校验 / 传输格式三位一体。RPC 模式用 JSON over stdin/stdout 供非 Node 集成。

### 4.6 沙箱三模式（部署层隔离）

| 模式 | 隔离范围 | 适用场景 |
|---|---|---|
| Gondolin 扩展 | 内置工具与 `!` 命令进本地 Linux 微 VM | 主机保留认证、工具进 VM，改动经 `/workspace` 写回宿主机 |
| Plain Docker | 整个 pi 进程进容器 | 最简单本地隔离（API Key 会进容器） |
| OpenShell | 整个进程进策略沙箱 | 文件/进程/网络/凭据全维度策略控制，支持本地或远端 K8s 网关 |

---

## 五、关键设计模式总结（"抄作业"清单）

| # | 模式 | 落地位置 | 一句话价值 |
|---|---|---|---|
| 1 | Provider 适配器 + 工厂 | pi-ai `models.ts` | 40+ 厂商 API 收敛为统一流式接口，模型按 `model.api` 自动分派 |
| 2 | partial-json 增量解析 | pi-ai 各 provider | 流式 tool call 参数边收边解析，scratch 缓冲用完即删 |
| 3 | 事件流驱动的双层循环 | agent-core `agent-loop.ts` | UI / 遥测 / RPC 订阅同一份事件流，运行时与展示解耦 |
| 4 | 钩子式工具执行 | agent-loop.ts | before/afterToolCall 上挂权限、护栏、改写，不污染核心循环 |
| 5 | 差分渲染 TUI | pi-tui `tui-main-screen.ts` | 只重写变化行 + 同步输出防撕裂，全量重绘被刻意收紧 |
| 6 | 扩展系统一等公民 | pi-coding-agent extensions | defineTool 十几行注入能力，Agent 可自扩展、热重载 |
| 7 | TypeBox schema 三位一体 | 全仓 | 编译时类型 + 运行时校验 + 传输格式同源 |
| 8 | 会话树 + JSONL | coding-agent session | append-only、branch/fork/clone、可分享、断点续传 |
| 9 | 责任分层（瘦循环） | agent-loop 792 行 | 错误推下层、状态推上层，循环只做循环 |

---

## 六、Harness v3：走向持久化运行（最新演进，2026-08）

Pi 正在重做 Agent Harness，**v3 规范已于 2026-08-11 写完，进入最终审计**。这是行业里"长任务 Agent"趋势下最关键的基础设施动作（OpenAI 在研究 Codex 长时间持续工作，Anthropic 称 Claude Code 越来越多用于长任务）：

- **durable execution**：模型请求和工具调用**前先保存执行状态，完成后写回结果**；
- **崩溃恢复**：进程崩溃、甚至 Harness 自身升级，都能从中断处继续；
- **副作用感知**：重启后能识别哪些任务已完成、哪些可重跑、哪些因副作用不能再执行一次；
- **状态分离存储**：对话、运行状态、Token 成本分开保存，并支持**跨版本状态迁移**。

> 注意：截至整理时 v3 处于"规范已写完 + 最终审计"阶段，尚未发布；现有能力属于 durable session（会话持久化），v3 将补上 durable execution。

---

## 七、生态与影响力

- **OpenClaw**（38.4 万 Star 顶流开源 Agent）：早期深度复用 Pi 的 Agent Runtime 与 TUI 终端组件，官方 README 专门致谢 Pi 作者——是 Pi SDK 能力（嵌入模式）的最佳真实集成案例。
- **Oh My Pi**（2 万 Star）：直接 Fork Pi 内核，新增浏览器、子 Agent、海量内置工具。
- **MiniMax Code**：明确基于 OpenCode + Pi 搭建 Harness。
- **pi-chat**（独立仓库 earendil-works/pi-chat）：把聊天频道（Discord / Telegram）映射为独立 session、workspace、memory、Skills、worker 与 Gondolin 微 VM——channel 从消息地址变成 Agent 的持久责任边界。
- **社区前端**：VS Code、Emacs、桌面、移动端多端前端。
- **开源会话共享**：badlogic/pi-share-hf 发布会话到 Hugging Face，推动 Agent 编码过程可审计、可学习。

---

## 八、推荐学习路径

### 路线 A：快速上手（0.5-1 天）
1. 看官网 [pi.dev](https://pi.dev/) 首页 + 读 Mario 官方博客《[Why I built Pi](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)》（第一手设计动机）；
2. 安装：`npm install -g --ignore-scripts @earendil-works/pi-coding-agent`，在项目里跑 `pi`；
3. 读 README 的 "What we didn't build"，理解五个 No；
4. 装 2-3 个官方示例扩展，感受扩展系统。

### 路线 B：系统理解架构（2-3 天）
1. 读 [Pi AI Agent Toolkit — 完整教學](https://tpow-001.netlify.app/post/2026-06-07-pi-tutorial)（四层架构 + Extension System + Agent Loop 事件流的系统讲解）；
2. 读《[Pi Agent Harness 源码深度技术解析](https://www.iceyao.com.cn/post/2026-08-11-pi-agent-harness源码深度技术解析)》（9 包依赖 DAG + 每条核心链路的代码级拆解）；
3. 读《[Agent 的本质是一个 while 循环：拆解 pi 的 792 行核心源码](http://www.jxxy.net/ai/articles/yanhua1010-agent-while-loop-source)》；
4. 对照 [Agent Harness 架构解析](http://ailinklab.com/zh/opensource/pi-agent-harness) 理解"为什么是 harness 而不是产品"。

### 路线 C：动手实战（1-2 周）
1. 掘金《[零到一实现一个 Coding Agent](https://juejin.cn/post/7663456780569313306)》配套两门课程——**课程 A：读 Pi 源码**（docs/course/，18 节基础 + 7 节进阶，多数课用内置 faux provider mock LLM，**不需要 API key 不花钱**）：阶段 A 环境与类型系统 → 阶段 B Agent Loop 核心 → 阶段 C Session 树与 compaction → 阶段 D 扩展与 SDK；进阶篇对照 Kimi Code；
2. CSDN《[跟着 OpenCode 学习 Pi Coding Agent](https://blog.csdn.net/qq_26879323/article/details/162466512)》系列（从 types.ts 到流式输出逐步手写等比例缩小版）；
3. 挑 3-5 个 `examples/extensions/` 示例（sub-agent、permission-gate、plan-mode、custom-compaction）读懂并改造。

### 路线 D：源码深度（1 个月+）
1. 通读 `packages/agent/src/agent-loop.ts`（792 行核心循环）+ `agent.ts`；
2. 读 `packages/ai` 的 Provider 体系与 partial-json 解析；
3. 读 `packages/tui/src/tui-main-screen.ts` 差分渲染；
4. 读 `packages/protocol` 的 CBOR 帧协议与 `packages/session-backends/sqlite-node`；
5. 跟随 Mario 博客的历史系列：Claude Code 演进史（cchistory）、为什么不需要 MCP。

---

## 九、学习资料清单（全）

### 9.1 官方一手资料
| 资料 | 链接 | 说明 |
|---|---|---|
| 官网 | https://pi.dev/ | 定位、安装、Why Pi |
| 官方文档 | https://pi.dev/docs/latest | 完整文档 |
| GitHub 仓库 | https://github.com/earendil-works/pi | README / CONTRIBUTING / RFCs / AGENTS.md |
| coding-agent 文档目录 | https://github.com/earendil-works/pi/tree/main/packages/coding-agent/docs | models.md / custom-provider.md / containerization.md / rpc.md 等 |
| 示例扩展库 | https://github.com/earendil-works/pi/tree/main/packages/coding-agent/examples/extensions | 60+ 示例 |
| Pi Packages 市场 | https://pi.dev/packages | 可安装的包 |

### 9.2 作者博客（第一手设计思想）
| 资料 | 链接 | 说明 |
|---|---|---|
| Why I built Pi（核心） | https://mariozechner.at/posts/2025-11-30-pi-coding-agent/ | 设计动机、极简主义、YOLO 模式、拒绝 MCP/子代理的理由 |
| Claude Code 历史 | https://mariozechner.at/posts/2025-08-03-cchistory/ | 记录 Claude Code 系统提示词与工具演变 |
| What if you don't need MCP | https://mariozechner.at/posts/2025-11-02-what-if-you-dont-need-mcp/ | 对 MCP 的完整批评与替代方案 |
| Armin Ronacher：Agents are hard | https://lucumr.pocoo.org/2025/11/21/agents-are-hard/ | 合作作者关于 Agent 构建难点的思考 |

### 9.3 源码级解析（中文）
| 资料 | 链接 | 深度 |
|---|---|---|
| Pi Agent Harness 源码深度技术解析 | https://www.iceyao.com.cn/post/2026-08-11-pi-agent-harness源码深度技术解析 | ★★★★★ 9 包架构 + 全部核心链路代码级拆解 + 6 大设计模式 |
| Agent 的本质是一个 while 循环（792 行核心源码） | http://www.jxxy.net/ai/articles/yanhua1010-agent-while-loop-source | ★★★★★ agent-loop.ts 逐层拆解（对比 codex / grok-build） |
| 零到一实现一个 Coding Agent（含课程） | https://juejin.cn/post/7663456780569313306 | ★★★★☆ 两门实战课程：读 Pi 源码（docs/course/）+ 进阶对照 Kimi Code |
| 跟着 OpenCode 学习 Pi Coding Agent 系列 | https://blog.csdn.net/qq_26879323/article/details/162466512 | ★★★☆☆ 手写等比例缩小版（types → 流式 → 工具） |

### 9.4 架构与理念解析（中文）
| 资料 | 链接 | 说明 |
|---|---|---|
| Pi:一个故意不替你做决定的 Coding Agent | http://ailinklab.com/zh/opensource/pi-agent-harness | 设计哲学 + 与 Claude Code 对比 |
| Pi 项目介绍：可改造的终端 Harness | https://silenceper.com/article/2026-05-27-pi-coding-agent-harness | 基础信息卡片 + 定位分析 |
| Pi AI Agent Toolkit — 完整教學 | https://tpow-001.netlify.app/post/2026-06-07-pi-tutorial | 完整教学：四层架构 / 扩展 / 事件流 / 对比表 |

### 9.5 英文资料
| 资料 | 链接 | 说明 |
|---|---|---|
| Pi Coding Agent Review: The Minimal Terminal Harness | https://andrew.ooo/posts/pi-coding-agent-minimal-terminal-harness-review （镜像 https://dev.to/andrew-ooo/pi-coding-agent-review-the-minimal-terminal-harness-5b46） | 深度评测：极简主义、四种模式、Session 树、诚实局限 |
| Pi (Coding Agent Harness) 词条 | https://www.superteams.ai/glossary/pi-harness | 结构化词条：四个工具、四层 monorepo、自扩展机制、Terminal-Bench #2 |

### 9.6 动态与行业（v3 / 生态）
| 资料 | 链接 | 说明 |
|---|---|---|
| Pi 重构 Agent 执行层（v3 动态） | https://www.theblockbeats.info/flash/360970 | v3 durable execution 方向报道 |
| 同源报道 | https://news.marsbit.co/flash/20260811181625022860.html 、https://www.kucoin.com/news/flash/pi-overhauls-agent-execution-layer-for-persistent-long-task-support | 补充确认 |
| OpenClaw | https://github.com/OpenClaw/OpenClaw | Pi SDK 真实集成案例 |
| pi-chat | https://github.com/earendil-works/pi-chat | 聊天网关形态 |

---

## 十、快速开始（备忘）

```bash
# 安装（推荐禁用脚本，供应链加固）
npm install -g --ignore-scripts @earendil-works/pi-coding-agent

# 在项目目录启动
cd /path/to/project && pi

# 认证：订阅类用 /login；API Key 用环境变量或 ~/.pi/agent/auth.json
# 例：export ANTHROPIC_API_KEY=sk-ant-...

# 常用命令
pi --version            # 版本
pi --list-models        # 可用模型
pi -p "query"           # 非交互模式
pi --mode json          # JSON 事件流
pi install npm:@foo/pi-tools   # 安装 Pi Package
pi update --self        # 更新本体

# 会话操作：/tree（会话树导航） /fork /clone /model（切模型） /export /share
```

---

## 附：给想借鉴的人一句话总结

> Pi 的价值不在于"又一个终端编码助手"，而在于它示范了如何把 Agent 主链路拆成**可独立复用、可嵌入、可扩展**的积木：模型抽象（pi-ai）、运行时循环（pi-agent-core）、终端渲染（pi-tui）、产品形态（pi-coding-agent）各司其职，中间全部用**事件与钩子**解耦。对想自研编码 Agent、或深度定制 AI 工作流的开发者，它的源码就是一份高质量参考实现——这就是"Harness"（套具/底座）一词的含义。
