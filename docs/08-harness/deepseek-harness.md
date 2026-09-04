# DeepSeek Harness(`dsh`):一切皆插件的 Agent Harness

> **一句话摘要**:DeepSeek 官方 2026-08-13 发布的开发者预览版 agent harness——**"一切皆插件(Everything is a Plugin)"**。它由 **Cordis** 插件系统驱动:模型、工具、技能、会话、沙箱、存储、循环、调度、UI 等**所有 Agent 能力都由插件提供**,内核只负责插件的加载/卸载/依赖,开发者不改源码即可在**配置层**选择、替换、重组任一能力;同时**运行有迹可循**——模型看到的一切写入 append-only 会话日志,Trajectory 视图按来源可查。定位:**Agent = Model + Harness**。
>
> **来源**:
> - GitHub:https://github.com/deepseek-ai/deepseek-harness(75.8k★,MIT,TypeScript,2026-08-13 更新)
> - 官方页:https://deepseek.com/harness
> - 架构文档:https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md

## 概念

### 定位:Agent = Model + Harness

> 模型是 Agent 的灵魂;Harness 给予 Agent **理解环境、使用工具,并在真实场景中持续工作**的能力。

DeepSeek Harness(`dsh`)是 DeepSeek AI 开源的第一方 agent harness,开发者预览阶段(快速迭代,**未来有 breaking changes**)。它不强调"又一个编码助手",而是把 Harness 本身做成**可自由替换、灵活重组**的插件组合物。

### 核心架构:三层逻辑

```
Cordis 内核       只负责插件加载/卸载/依赖关系,不承载 Agent 具体能力
插件提供能力      模型/工具/技能/会话/沙箱/存储/循环/调度/UI 全由插件提供,
                 通过 Cordis 服务与事件彼此协作
配置层自由组合    不改源码,在配置层选择/替换/扩展任一能力
```

## 原理(设计逻辑拆解)

### 1. Cordis:无特权核心的插件框架

dsh 建立在 [Cordis](https://github.com/cordiverse/cordis) 之上(设计见论文《A Programming Paradigm for Spatiotemporal Composability》)。**产品的每一部分都是插件**——包括模型适配器、工具注册表、会话日志、甚至 agent loop 本身——所以每个部分都可以从配置替换。

- **没有特权核心可打补丁**:扩展 = 在旁边挂一个插件;注册是 **effects**,插件卸载时自动回卷;
- 插件贡献:**services(服务)、typed events(类型化事件)、reversible effects(可回卷效应)** 到共享 context。

### 2. Profiles 与 Bundles:配置层组合机制

运行中的 `dsh` 是**启动时按有序层组合出来的插件树**:

- **Profile(配置档)**:命名组合,存于 Harness home,列出它堆叠的 bundles、安装的树外插件、用户的 `cordis.patch.yml`;`web` 与 `headless` 是内置模板;
- **Bundle(包)**:Cordis 配置行 + 代码的分发格式——插进去的东西仍可被上层 patch;
- **分层应用顺序**:profile 的 bundles → profile 的 `cordis.patch.yml` → home 级 → `--patch` overlay;**patch 按行 id 定位并整体替换该行配置,或插入新行**;
- **查看你的插件树**:`dsh --profile web --dump-config`——打印的每一行都能用你自己的 patch 替换;
- `dsh-base` 是每个 profile 的第一层:模型适配器、工具、持久化、沙箱与审批策略、设置、凭证、遥测;`dsh-web-app` 加浏览器应用,`dsh-headless` 加无服务器一次性运行器。

### 3. 核心包(插件树中的关键节点)

| 包 | 职责 | `ctx` key |
| --- | --- | --- |
| `core/session` | append-only `SessionEvent` 日志 + 内存存储 | `ctx.sessions` |
| `core/system-prompt` | Prompt-section 与 tool-schema 组装 | `ctx.systemPrompt` |
| `core/tools` | 作用域工具注册表 + 受守卫的执行管线 | `ctx.tools` |
| `core/agent` | `Agent` 接口、live registry、`agent/*` 事件 | `ctx.agents` |
| `core/agent-loop` | 默认驱动(实现 Agent 接口) | `ctx.agentLoop` |
| `core/scope` | 每 agent 的作用域注册原语 | 库,无 key |
| `llm/llm` | 消息与流词汇 + 适配器接缝 | `ctx.llm` |

### 4. 事件是扩展点:三个域

- **Session events**:追加进日志的**持久事实**,经 `session/event` 广播——事实需要跨 reload 存活时用;
- **Agent events**(`agent/*`):携带 live `Agent`(inbox/step/status/request/validation/continuation)——观察或拦截进行中的工作;
- **Capability events**(`fs/*`、`tools/*`、`telemetry/*`):把策略与适配器挂到接缝上,不 import 循环。

其中 `agent/pre-step`、`agent/request`、`llm/stream` 和三个 `tools/*` 事件是 **waterfalls**(监听者必须 `next()` 委派);`agent/turn-stopping` 是串行、无 `next()`。

### 5. Turn 流程:step 与 turn

- **step** = 一次模型请求 + 它调用的工具;**turn** = 零或多个 step(打开于首个输入被认领前,关闭于"不再欠任何东西");
- 流程:`turn/start → claim input → 组装 prompt sections + tool schemas → agent/pre-step(可拒绝/改写)→ step/start → 追加消息 → derive model history → agent/request → llm/stream → tool/call → tools/pre-execute → execute → post-execute → tool/result → step/end →(还欠工具请求或有新输入则下一 step)→ agent/turn-stopping → turn/end`;
- 输入经一个 inbox 到达驱动;注入的上下文在 inbox 等待直到有消息唤醒;
- 被拒绝或空的首次 claim 也会关闭一个**未消费 step 的持久 turn**——日志记录这次尝试。

### 6. 会话日志即上下文源:运行有迹可循

> **Model-visible means logged(模型可见即已记录)**——运行时不变量。

- `deriveMessages()` 从会话日志**投影**模型历史;原始 `assistant/chunk` 事件保留回放与 UI 保真;
- **Fork、resume、transcripts、telemetry、persistence 全部派生自同一份事件流**;
- 任何新的模型可见输入必须新增 session event(扩展 `SessionEventMap` 并从日志渲染);
- 官方 Trajectory 视图按来源查看:系统提示词、思维链、工具调用与结果、子 Agent 调度、每一次上下文注入。

### 7. Capability seams:可换能力的三角色

一个 **seam** 是三个角色:**Service Definition**(声明接口)/ **Service Provider**(实现)/ **Consumer**(使用,通常是模型面工具)。一个包可组合多角色,但单一角色不成 seam。

- **一个 provider 换掉,整个产品改变**:文件系统与子进程 provider 共享同一执行世界——把它们指向远程沙箱,Bash、PTY、LSP 一起移动,无需 provider fork;
- **Subagent providers**:从全新子 agent 到另一产品中的委托回合,都藏在同一个接口后面。

### 8. 新行为去哪(扩展点速查)

| 目标 | 机制 |
| --- | --- |
| 加模型 provider | 在 `ctx.llm` 注册适配器 |
| 加模型面能力 | 在 `ctx.tools` 注册;schema 加入 prompt 组装 |
| 给某会话不同能力集 | 组合 agent preset(service 行需 `isolate` realm) |
| 加 shell 执行 | 注册 `ctx.shell` 后端(本地经 `ctx.subprocess` 派生) |
| 加持久终端执行 | 注册 `ctx.terminals` 后端 + `dsh-tool-terminal` |
| 加人类命令 | 注册 `ctx.commands`(不经模型回合直接分发) |
| 加后台工作 | 注册 `ctx.jobs`;`job_*` 工具收集/停止 |
| 加文件系统/策略 | 注册 `ctx.fs` provider 或监听 `fs/*` 事件 |
| 限制派生进程 | 用 `ctx.sandbox` 后端,消费者包装 argv 后再 spawn |
| 拦截请求/工具/回合 | 用 `agent/*` 或 `tools/*` 事件;`agent/turn-stopping` 停回合 |
| 加模型面上下文 | `agent.inject()`(进入下一个被受理的请求) |
| 持久会话状态 | 扩展 `SessionEventMap`,从日志渲染/回放 |
| fork 活会话 | `ctx.sessions.fork(source, boundary?, childSessionId?)` |
| 注册限定到某 agent | 用该 agent 的 `agent.ctx` |

## 深度解析(子系统与运行时机制)

> 本节下沉到仓库子系统文档(源码级,基于 master 分支 docs/subsystems/ 与 packages 文档)。

### 1. 六包 spine 与可替换的 loop

```
session(append-only 日志) → system-prompt(prompt/schema 组装) → tools(注册表+守卫管线)
  → agent(接口+registry) → agent-loop(唯一具体驱动) → scope(垫底,避免循环依赖)
```

- `agent-loop` 是 public `Agent` 契约的**唯一实现**,但扩展插件只依赖 `agent` 接口包、不依赖 `agent-loop`——**loop 可被替换**;
- `scope` 是纯库原语(createScope/scopeOf/scopeTarget),置于模块图底层。

### 2. 事件词汇:三域 + 四种分派模式

Cordis 事件有 **4 种分派模式**(公开契约一部分,`@mode` 标注):`emit`(观察,无返回值)/ `waterfall`(环绕中间件,可短路,有返回值)/ `parallel`(并行)/ `serial`(顺序,有返回值)。

| 域 | 事件(节选) | 用途 |
| --- | --- | --- |
| **Session(持久事实)** | `turn/start|end`、`step/start|end`、`user/message`、`assistant/chunk`(原始流块,token 级保真)、`assistant/message`、`tool/call`(原始 arguments JSON,`callId` 配对)、`tool/result`、`todo/write`(whole-list 快照)、`request/header`(EpochHeader 快照) | append-only 日志;Fork/resume/replay 都从它推导 |
| **Agent(live 控制)** | `agent/created|disposed|status`、`agent/pre-step`(waterfall,拒绝/替换进入 step 的消息)、`agent/request`(waterfall,替换冻结的调用配置)、`agent/request-error`(waterfall,retry 或委托)、`agent/inbox/inserted|claimed|discarded`、`agent/turn-stopping`(serial,数据决定结局) | 观察/拦截进行中的工作 |
| **Capability(接缝)** | `fs/*`、`tools/*`、`telemetry/*`、`llm/stream` | 把策略/适配器挂到接缝 |

**设计原则:可重放事实走 `session/event`,live 控制/状态走 `agent/*`**——SDK 用户要 transcript 用 session/event。

### 3. 会话日志:请求是日志的纯函数(reconstructability)

- `Session` 是 typed `SessionEvent` 的 append-only 日志,是 agent 交互历史的**唯一真源**;LLM 消息历史从日志**推导**(`deriveMessages()`),从不单独存储——**replay 即重新推导**;
- **EpochHeader**(config + adapterDefaults + rendered system + tool schemas)是 logged state,`foldRequestHeader(events)` 重建最新快照——**每次模型请求是日志的纯函数**;`invariant companion` 用 `ctx.invariants` 独立重建并运行时自检这一不变量;
- 持久化**故意不在 core**:插件订阅 `session/event` 写穿、`session/flush`(parallel)做 checkpoint(JSONL/SQLite 由 persistence 插件提供);
- SessionStore 四原语:`create / prepare+enter+announce(复合 effect 顺序化)/ flush / fork(boundary)`。

### 4. 工具执行管线:三层策略分离

- `ToolDefinition` = `ToolSchema` + **强制 `output`**(canonical JSON Schema + render + presentationMeta)+ `execute` + 可选 `finalizeContent` / `timeoutMs` / `isConcurrencySafe` / `presentCall` / `presentResult`;
- **模型可见面白名单化**:`schemas()` 只投影 name/description/parameters——`output`/`execute`/`timeoutMs` 绝不泄漏到模型请求;
- **管线**(tool/call 先落日志 → presentCall → pre-execute → guard → execute → body → post-execute → finalizeContent → tools/result → tool/result 落日志 → presentResult):
  1. `tools/pre-execute`:**可重排 waterfall**(allow/deny/ask;`ask` 经 `ctx.approval`);
  2. **单调 guard**(owner policy):只能否决、无法强制放行——防重排的 owner 策略;
  3. `tools/execute`:**around-dispatch**(timeout/retry/metrics),只换 `exec.signal`;
  4. `tools/post-execute`:接受/替换/阻塞;
  5. `finalizeContent`:同步 last-mile,全 outcome 必经(含绕过 post-execute 的失败);
  6. `tools/result`:冻结的权威结果,emit 观察;
- **取消语义**:入口后、结果物化前到达的取消 → 未启动 body 跳为 `ABORTED_BEFORE_DISPATCH`、已成功替换为 `ABORTED`;不可见工具报 `UNKNOWN_TOOL`;
- **并发**:`isConcurrencySafe` + barrier + bounded rolling pool(dispatch/body 才重叠,策略与结果保持模型序;`maxParallelToolCalls` 默认 10,1=串行)。

### 5. 子代理 providers:一接口多 provider + 续谈机制

- `ctx.subagents` 是**多 provider 并存**、按名注册(`subagent-spawn-in-process/-fork/-acp/-codex/-claude-code/-dsh-sdk`),registry 模式同 LLM adapter;
- **启动时能力静态检查**(`SubagentCapabilities`:outputSchema/depthLimit/toolFilter/persona),缺能力 `SubagentError('UNSUPPORTED_CAPABILITY')` 响亮拒绝;续谈能力以方法存在性 + TS narrowing 表达;
- **续谈子代理 = 一个持久 child Session + 至多一个 process-local Activation**(resident 期间的 Agent):不另造任务/队列状态机,状态从 Agent quiescence + owned-child 集推导;
- **Agent inbox 是唯一队列**;`followup()` 路由仅取决于 Activation 状态:running→同 Activation 入队;waiting→唤醒;无 Activation→从持久 Session 冷恢复;followup 权威来自精确 live parent(`SessionHeader.parentSession`);
- `interrupt()` 保留未认领 inbox 与已发布后代;`listChildren/listDescendants` 纯投影(live 优先)不加载 Agent。

### 6. scope 原语:per-agent 注册

- `ScopeKey = object`(不透明、按身份比较;loop 用 live Agent 对象作 key);`Scoped<T>` 是 compile-time brand 载体,事件声明用作 `this` 类型;
- 注册用一个 context 同时表达**可见性**(per-agent 遮蔽/继承)+ **effect 所有权**;`ScopedLayers` = eager 全局层 + 懒建 exact-scope 层,整个 ScopeLayer 空时才回收;
- in-process 子代理用 `tools.restrict()` 应用 toolFilter、用 scoped `deployment:persona` section 遮蔽部署 persona。

### 7. 事务化创建与取消

- `ctx.agents.create()/resume()` 返回 `AgentHandle { agent, dispose() }`——disposer 是"能力",只有持有者能拆掉 agent;创建是事务:构造私有 session/agent/scoped ctx → await setup → enter 双 registry → announce `session/created`+`agent/created` → `agent/session-start` → 启动 driver;**setup 期任何拒绝/抛错/所有者 dispose 都回滚事务**;
- `Agent` 句柄:`send(message, target, wakeup)` 统一原语(`followup`/`steer`/`inject` 是固定预设别名)、`cancel(cause, {keepInbox})`、`whenIdle()`、`runMaintenance(task)`;状态只有 `idle`/`running`;
- **取消收敛竞态**:醒来输入在 abort 后、收敛前到达会被 latch(`wakeRequested`)在 driver 收敛边界回放;`turn/end` 记 `aborted`/`disposed`;未分派的模型工具调用获得合成 `tool/call` + `ABORTED_BEFORE_DISPATCH` 结果对。

### 8. Cordis 集成:事件模式 + 可逆 effect + scope 层

- **事件模式即契约**:gen-cordis-catalog.ts 从源码抽事件 catalog 并做声明/分派点一致性校验;`ctx.waterfall` 是 around-middleware(不调 `next()` 即短路);
- **注册皆可逆 effect**:`ctx.effect()`/`ctx.on()` 安装 prompt section、tool schema、adapter、listener,reload/teardown 时按序撤销;每个注册必须有 disposer(支撑 HMR);
- `internal/*` 字符串(dispatch/plugin/service/status)供 CLI/动态 Cordis/服务发现。

### 9. 最值得深读的源码/文档

1. `packages/core/agent-loop/README.md` + `packages/core/agent/src/runtime-types.ts`——loop 语义与 `agent/*` 事件词汇权威来源;
2. `packages/core/tools/src/index.ts`——`ToolDefinition` 全字段、`ToolRestriction` 继承过滤、execute 完整管线(取消/并发实现);
3. `packages/core/session/src/index.ts`——SessionStore prepare/enter/announce/flush 与 rollback 语义,配合 `docs/agent-lifecycle.md` 时序图。

## 代码 / 实现

**快速体验(Web UI,默认 http://127.0.0.1:3080)**:

```bash
npx @deepseek-ai/dsh web
# 或从源码:git clone → pnpm install → pnpm run build → pnpm dsh web
```

**查看/替换配置树**:

```bash
dsh --profile web --dump-config   # 打印插件树;任何行都能被你的 patch 替换
```

**四种运行模式(agent preset)**:

| 模式 | 内容 |
| --- | --- |
| **标准模式** | 功能完整编码 Agent:文件编辑、Shell、文件与网页检索、Skills、计划、目标、子代理、工作流 |
| **PTC 模式** | 标准全部能力 + **Code Mode SDK**:模型用一个 TypeScript 程序组合多步工具调用 |
| **极简模式** | 仅 `持久 bash` + `str_replace_editor` 双工具——最小化环境下的**模型基准测试** |
| **创造模式** | 检查当前运行时、在内存中试验 Cordis 插件,创作自定义 agent preset |

**Python SDK**:安装后运行 `jsonrpc-agent` 最小变体;基准测试用独立 workspace + session ID 跑独立任务(见仓库 BENCHMARK.md)。

## 实践 / 应用

### 与站内其他 Harness 的对比

| 维度 | DeepSeek Harness(dsh) | [Pi Agent Harness](pi-agent-harness-deep-dive.md) | Claude Code / Anthropic 系 |
| --- | --- | --- | --- |
| 核心哲学 | **一切皆插件**(连 agent loop 都是插件),Cordis 内核只管加载/依赖 | 极简内核 + 插件生态(扩展是 TS 文件,热重载) | 完整产品 + 官方最佳实践 |
| 扩展方式 | 插件 + **配置层 patch**(不写代码改能力) | defineTool 十几行注册,自扩展 | Skills/Plugins/Subagents/Hooks |
| 可观测性 | **Trajectory 视图**:模型所见全部落 append-only 日志 | 文件即状态 + 事件流 | context window 管理 + 验证闭环 |
| 特色 | 四种模式(标准/PTC/极简/创造)、会话日志即上下文源 | Terminal-Bench #2(极简验证)、durable execution v3 | 验证闭环/四阶段工作流/沙箱双边界 |
| 成熟度 | 开发者预览(有 breaking changes) | 生产可用(8 万★) | 生产级 |

- **可观测性思路呼应**:与 [LongHorizon-Harness](../09-agent-research/longhorizon-harness-paper.md) 的"任务状态脱离上下文、审计可复放"同理念(这里用 append-only 会话日志 + Trajectory);
- **插件化路线对照**:dsh 比 Pi 更彻底——Pi 的内核仍是"极简 loop + 扩展",dsh 连 loop/调度/UI 本身都是插件、可配置替换;
- **极简模式**呼应 [Building effective agents](../03-agents/agent-building-effective-agents.md)"简单可组合"与 Pi 的 4 工具基准思路;
- **PTC 模式(代码组合工具)**呼应 OpenAI [Programmatic Tool Calling](../03-agents/agent-tool-design-practice.md) 的"用程序编排多步调用"。

### 生态与注意

- 社区插件:`dsh-plugin` topic 可被发现;Discord / 企微群;
- 定位:面向 **Harness 开发者**(而非终端用户)——"在开源、开放、可复用、可组合的基础设施之上探索智能上限";
- ⚠️ **开发者预览**:核心插件与基础 API 持续迭代,生产使用需关注 breaking changes 与 [安全使用政策](https://deepseek.com/harness/privacy/);
- 模型无关(插件化模型适配器),但天然契合 DeepSeek 自家模型;官方文档:https://deepseek-harness.github.io/deepseek-harness/guide/quickstart

## 总结

1. **定位**:Agent = Model + Harness;dsh 是第一方开源 harness,把"让 Agent 持续工作的能力"拆成**可替换重组的插件组合物**。
2. **一切皆插件**:Cordis 内核只管加载/卸载/依赖;模型/工具/技能/会话/沙箱/存储/循环/调度/UI 全是插件,连 agent loop 都可配置替换;没有特权核心。
3. **配置层组合**:profile + bundle + patch(按行替换/插入),`dsh --profile web --dump-config` 看到的一切都能改——不写代码扩展能力。
4. **运行有迹可循**:模型所见全部落 append-only 会话日志(不变量 "Model-visible means logged"),Fork/resume/检索/回放/Trajectory 共享同一事件流。
5. **四种模式**:标准(全功能)/ PTC(代码组合工具)/ 极简(双工具基准)/ 创造(定制 preset);开发者预览,API 会变。

**下一步学什么**:对比 [Pi Agent Harness 深度解析](pi-agent-harness-deep-dive.md)(同为插件化,理解两种插件哲学的差异);读 [Building effective agents](../03-agents/agent-building-effective-agents.md)(模式层)与 [LongHorizon-Harness](../09-agent-research/longhorizon-harness-paper.md)(可审计状态);想上手先 `npx @deepseek-ai/dsh web` 体验 Web UI,再看 `docs/architecture.md` 的 event map。

## 延伸阅读

- 站内:[Pi Agent Harness 深度解析](pi-agent-harness-deep-dive.md)、[Pi Agent 插件生态](pi-agent-plugins.md)、[Building effective agents](../03-agents/agent-building-effective-agents.md)、[LongHorizon-Harness](../09-agent-research/longhorizon-harness-paper.md)、[工具设计五原则](../03-agents/agent-tool-design-practice.md)、[08-harness 章节](index.md)
- 官方一手:GitHub https://github.com/deepseek-ai/deepseek-harness;官方页 https://deepseek.com/harness;开发者文档 https://deepseek-harness.github.io/deepseek-harness/guide/quickstart;中文 README https://github.com/deepseek-ai/deepseek-harness/blob/master/README.zh.md
- 架构深度:docs/architecture.md 与 docs/architecture.zh.md(架构文档);docs/development.md(开发指南);AGENTS.md(面向 agent 的仓库说明);**docs/subsystems/**(38 页子系统索引:session/system-prompt/tools/core/subagent/scope/llm-streaming/compaction/persistence/goal/schedule/jobs/terminal/commands/plan 等);docs/event-producer-consumer.md(事件生产/消费矩阵);docs/capability-seams.md(能力接缝图);docs/agent-lifecycle.md + docs/tool-execution-pipeline.md(时序/管线图);docs/cordis-primer.md(Cordis 入门)
- 底层框架:Cordis https://github.com/cordiverse/cordis;论文《A Programming Paradigm for Spatiotemporal Composability》https://github.com/cordiverse/paper
- 生态:https://github.com/topics/dsh-plugin;安全使用政策 https://deepseek.com/harness/privacy/
