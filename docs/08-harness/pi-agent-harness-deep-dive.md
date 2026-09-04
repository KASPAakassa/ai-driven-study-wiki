# Pi Agent Harness 深度解析:极简内核、四层架构与"五个 No"的设计哲学

> **一句话摘要**:Pi(earendil-works/pi)不是"又一款 Claude Code 平替",而是一套把 Agent 主链路拆成可复用积木的工程样板——**"一个小内核 + 最大可塑性"**。它用五个"故意不做"(MCP/子代理/权限弹窗/Plan mode/内置 To-dos)立住立场,用**四层 monorepo**(pi-ai / pi-agent-core / pi-coding-agent / pi-tui)实现"极简提示词 + 极简工具集 + 可观测性至上",在 Terminal-Bench 以 4 个工具拿下 #2。本文综合作者博客《Why I built Pi》与社区源码解析,拆解其设计哲学、架构、核心机制、Harness v3 演进与生态影响力。
>
> **来源**:
> - 深度资料:剪贴板整理版《Pi Agent Harness:设计思路解析与学习资料合集》(存档 `docs/inbox/pi-agent-harness-source.md`)
> - 作者博客:Mario Zechner《What I learned building an opinionated and minimal coding agent》(https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)
> - 仓库:https://github.com/earendil-works/pi;官网:https://pi.dev

## 概念

### 项目速览

| 维度 | 内容 |
| --- | --- |
| 仓库 | github.com/earendil-works/pi(MIT,纯 TypeScript monorepo,Node ≥ 22) |
| 作者 | Mario Zechner(badlogic,libGDX 作者)+ Armin Ronacher(Flask/Jinja 作者) |
| 规模 | Star 6万→8万;npm 周下载 130 万+;9 个 npm 包 |
| 运行形态 | 交互式 TUI / print / JSON / RPC / SDK 四种模式 |
| 模型 | 40+ Provider(Anthropic/OpenAI/Google/DeepSeek/Kimi/Ollama/OpenRouter…) |
| 一句话 | Cursor/Claude Code = 完整成品;Pi = 乐高积木——可拼出终端编码助手,也可拆出底层 SDK 嵌入自研系统 |

### 设计动机(作者第一手)

Mario 用过 Cursor、Claude Code,最终不满:**Claude Code 变成了"80% 功能我用不上的太空飞船"**——系统提示词和工具每次发布都变,破坏工作流、改变模型行为;而且现有 harness **无法精确控制进入上下文的内容**,会"在背后注入你没看见的东西"。他想要:**context engineering 的主导权 + 检查与模型交互的每一个细节 + 干净的会话格式可自动后处理 + 能在 agent core 之上搭替代 UI**。结论是"自己写一个",于是有了 Pi。

### 五个"No"(官方立场,最有观点的地方)

| 不做 | 官方理由 | 替代方案 |
| --- | --- | --- |
| **不做 MCP** | MCP server 常占上下文 7-9%,多数工具用不上 | 构建带 README 的 CLI 工具,模型按需读 README + bash 调用(渐进式披露);或写 extension 加 MCP |
| **不做 Sub-agents** | 子代理是"黑盒中的黑盒",可观测性为零、上下文传递差 | tmux 起多个 Pi 实例;或 extension 实现(官方有完整示例) |
| **不做权限弹窗** | 权限弹窗是"安全剧场"——能写代码能跑命令时防线已失守 | 默认 YOLO 模式(以启动用户权限运行);要隔离用 Gondolin 微 VM / Docker / OpenShell |
| **不做 Plan mode** | 计划应落盘为文件:可版本化、可跨会话共享、完全可观测 | 维护 `PLAN.md`;或 extension / 社区 package |
| **不做内置 To-dos** | 待办列表增加模型状态跟踪负担、干扰 LLM | 维护 `TODO.md`,由 Agent 自己读写 |

### 三条底层信念

1. **极简提示词 + 极简工具集**:系统提示词(含工具定义)< 1000 tokens;默认只有 `read / write / edit / bash` 四工具(+ grep/find/ls 等只读)——前沿模型已被 RL 训练得足够好,不需要上万 token 脚手架;
2. **可观测性至上**:文件即状态(TODO.md / PLAN.md / AGENTS.md),一切可见、可审计;
3. **少即是多(基准验证)**:Terminal-Bench 82 任务中,Pi 以 4 工具 + 极简 prompt 拿下 **#2**(Claude Opus),击败大量带 MCP/子代理/后台 bash 的重型 Agent;Terminal-Bench 团队的 Terminus 2(只给模型一个 tmux 会话)同样印证极简有效。

### 上下文工程是成败关键

控制权还给开发者:AGENTS.md(项目级指令,逐级加载,`AGENTS.override.md` 可整体覆盖)、SYSTEM.md(按项目替换/追加系统提示)、Compaction(近上限自动摘要,策略可自定义)、Skills(按需加载,渐进式披露不爆破 prompt cache)、Prompt templates(`/name` 展开)、动态上下文(扩展可在每轮前注入消息/过滤历史/实现 RAG 或长期记忆)。

## 原理(四层架构与核心机制)

### 四层 Monorepo + 9 包依赖 DAG

```
Layer 3  pi-coding-agent  产品层:CLI/TUI 入口·会话树(JSONL)·扩展系统·Skills·Compaction·认证·包管理
Layer 2  pi-agent-core    运行时内核:双层 agent-loop·工具执行(并行/串行/钩子)·steering/follow-up·事件流
Layer 1  pi-ai            统一 LLM 抽象:stream()/complete()·40+ Provider·TypeBox schema·partial-json·模型发现
Layer 0  基础层            pi-tui(差分渲染)·pi-protocol(CBOR+帧)·pi-telemetry(厂商中立遥测)
```

构建顺序(即依赖方向):`tui → telemetry → ai → agent → sqlite-node → protocol → client → server → coding-agent`。**单向依赖、无循环**;coding-agent 是入度最大汇聚点(~199 个 .ts),agent 运行时核心仅 **49 个文件**。

### pi-ai:统一多厂商 LLM 抽象

- **只有四种 API**:OpenAI Completions / OpenAI Responses / Anthropic Messages / Google Generative AI——90% 的提供商都在这四个协议里,但每个对 Completions 的理解都不同(Cerebras/xAI/Mistral 不喜欢 `store` 字段、reasoning 字段在 `reasoning_content` vs `reasoning`…),pi-ai 用 Provider 适配器 + 工厂收敛;
- **TypeBox 工具 schema** + **partial-json 增量解析**:每个 ToolCall 挂 `partialJson` scratch 缓冲,边收 token 边还原参数,用完即删;`stopReason == "length"` 时整批判失败——**宁让模型重发,也不执行参数残缺的 bash**(截断兜底);
- **Context handoff(跨厂商上下文交接)**:会话中途从 Anthropic 切到 OpenAI,thinking traces 转成 `<thinking></thinking>` 标签的内容块;序列化/反序列化 `Context` 后可用任意模型继续——"多模型世界"的一等公民;
- **模型注册表**:解析 OpenRouter + models.dev 生成 `models.generated.ts`(含成本/能力/上下文窗口),新增自定义模型(如 Ollama 本地)只需一个类型安全的 `Model` 对象;
- **三套认证归一**:环境变量 API Key / `auth.json` / 订阅登录(Claude Pro、ChatGPT Plus、Copilot);
- 诚实局限:token/cache 统计是 Wild West(有的开头报、有的结尾报),pi-ai 做 best-effort——**够个人用,不够精确计费**。

### pi-agent-core:双层工具调用循环(agent-loop.ts 仅 792 行)

`runLoop()` 是**双层 while 循环**:内层处理工具调用与 steering 消息,外层承接 follow-up 消息。

```
① 注入 steering 消息(本回合进行中用户插话,立即生效)
→ ② 调用 LLM(流式 streamAssistantResponse)
→ ③ 解析 tool call(partial-json)
→ ④ 截断防御(length → 回灌错误结果要求重发)
→ ⑤ 执行工具(默认并行 Promise.all,结果按原始顺序回灌;单工具可声明 sequential)
→ ⑥ 回灌 tool_result → 检查 terminate → 检查 follow-up 队列
```

- **steering vs follow-up 两阶段**:Enter 发 steering(当前工具执行完后立即注入,中断其余工具);Alt+Enter 发 follow-up(等 Agent 跑完再处理);
- **事件流驱动**:`runLoop` emit `agent_start / turn_start / message_update / tool_execution_* / agent_end`——UI、日志、遥测、远程 RPC 订阅同一份事件流,**运行时与展示完全解耦**;
- **钩子机制**:`beforeToolCall`(可拦截,返回 `{block: true, reason}`)/ `afterToolCall`(可改写结果)——权限系统、输出护栏都挂钩子上,不污染核心循环;
- **为什么只有 792 行(责任分层)**:循环只做循环;错误处理推给下层(pi-ai 把网络错误封装成流内事件),状态维护与重试推给上层(AgentSession)。

### pi-coding-agent:扩展系统是灵魂

- **四个内置工具**:`read` / `write` / `edit`(精确替换 + 模糊匹配归一化:NFKC、弯引号→直引号、连字符→半角减号、特殊空格→普通空格)/ `bash`;
- **扩展 API**:`defineTool` 十几行注册新工具(TypeBox 定义参数);扩展还能注册命令、挂事件总线、拦截工具调用、自定义渲染器、注入系统提示——**理论上几乎整个 Agent 的可见行为都可被扩展改写**;
- **自扩展(self-extensible)**:扩展是 TS 文件,经 jiti 加载(无需构建);Pi 可在运行中修改自己的扩展文件并**热重载**——"让 Pi 给你写一个缺失的工具,它在同一轮里写完、加载、开用";
- **60+ 示例扩展**:sub-agent、plan-mode、permission-gate、protected-paths、SSH 执行、sandbox、git checkpoint、自定义 compaction,甚至 Space Invaders / Doom 小游戏;
- **会话管理**:JSONL append-only、断点续传;会话按项目存 `~/.pi/agent/`;**会话树**支持 branch/fork/clone(`/tree` 回到任意历史点);`/export` 导出 HTML、`/share` 上传 gist;持久化后端可插拔(node:sqlite 默认、memory 测试、search.ts 全文检索);
- **权限与安全**:默认以启动用户权限运行(YOLO);工程层防护靠扩展(project-trust/output-guard/protected-paths);部署层隔离三模式(见下)。

### pi-tui:差分渲染终端 UI

保留模式(Retained Mode)渲染,只重写变化行,整个更新包在"同步输出"(CSI 2026)中防撕裂;视口追踪(滚动区行号与硬件光标行号分开维护,`computeLineDiff` 只算最小光标位移);全量重绘刻意收紧(仅终端宽度变化时);支持 Kitty 图像协议渲染图片。

### 协议层:CBOR + 帧封装

消息 CBOR 编码,外层 4 字节大端长度前缀帧(单帧上限 16MB);`FrameDecoder` 增量式(任意字节块 push 出完整帧);所有 schema 由 TypeBox 定义——**编译时类型 + 运行时校验 + 传输格式三位一体**;RPC 模式用 JSON over stdin/stdout 供非 Node 集成。

### 沙箱三模式(部署层隔离)

| 模式 | 隔离范围 | 适用 |
| --- | --- | --- |
| Gondolin 扩展 | 内置工具与 `!` 命令进本地 Linux 微 VM | 主机保留认证、工具进 VM,改动经 `/workspace` 写回 |
| Plain Docker | 整个 pi 进程进容器 | 最简单本地隔离(API Key 会进容器) |
| OpenShell | 整个进程进策略沙箱 | 文件/进程/网络/凭据全维度策略控制,支持本地或远端 K8s 网关 |

## 代码 / 实现

**跨厂商上下文交接(作者原文示例)**:

```ts
import { getModel, complete, Context } from '@mariozechner/pi-ai';

const claude = getModel('anthropic', 'claude-sonnet-4-5');
const context: Context = { messages: [] };
context.messages.push({ role: 'user', content: 'What is 25 * 18?' });
const claudeResponse = await complete(claude, context, { thinkingEnabled: true });
context.messages.push(claudeResponse);

// 中途切到 GPT:它会看到 Claude 的 thinking 作为 <thinking> 标签文本
const gpt = getModel('openai', 'gpt-5.1-codex');
context.messages.push({ role: 'user', content: 'Is that correct?' });
const gptResponse = await complete(gpt, context);
context.messages.push(gptResponse);

// 序列化/反序列化后可用任意模型继续
const restored: Context = JSON.parse(JSON.stringify(context));
restored.messages.push({ role: 'user', content: 'Summarize our conversation' });
await complete(claude, restored);
```

**自定义模型(如 Ollama 本地)**:

```ts
const ollamaModel: Model<'openai-completions'> = {
  id: 'llama-3.1-8b', name: 'Llama 3.1 8B (Ollama)',
  api: 'openai-completions', provider: 'ollama',
  baseUrl: 'http://localhost:11434/v1', reasoning: false,
  input: ['text'], cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
  contextWindow: 128000, maxTokens: 32000
};
await stream(ollamaModel, context, { apiKey: 'dummy' });
```

**快速开始**:

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
cd /path/to/project && pi          # 交互 TUI
pi -p "query"                      # 非交互
pi --mode json                     # JSON 事件流
pi install npm:@foo/pi-tools       # 装 Pi Package
# 会话:/tree /fork /clone /model /export /share
```

## 实践 / 应用

### 六大设计模式("抄作业"清单)

| # | 模式 | 落地 | 价值 |
| --- | --- | --- | --- |
| 1 | Provider 适配器 + 工厂 | pi-ai | 40+ 厂商收敛为统一流式接口,按 `model.api` 自动分派 |
| 2 | partial-json 增量解析 | pi-ai | 流式 tool call 边收边解析,scratch 用完即删;截断宁重发不执行残缺参数 |
| 3 | 事件流驱动双层循环 | agent-loop.ts | UI/遥测/RPC 订阅同一事件流,运行时与展示解耦 |
| 4 | 钩子式工具执行 | before/afterToolCall | 权限、护栏、改写挂钩子,不污染核心循环 |
| 5 | 差分渲染 TUI | pi-tui | 只重写变化行 + 同步输出防撕裂 |
| 6 | 扩展系统一等公民 | extensions | defineTool 十几行注入能力,Agent 可自扩展、热重载 |
| 7 | TypeBox schema 三位一体 | 全仓 | 编译时类型 + 运行时校验 + 传输格式同源 |
| 8 | 会话树 + JSONL | session | append-only、branch/fork/clone、可分享、断点续传 |
| 9 | 责任分层(瘦循环) | agent-loop 792 行 | 错误推下层、状态推上层,循环只做循环 |

### Harness v3:走向持久化运行(2026-08 最新演进)

v3 规范已写完(2026-08-11),进入最终审计(尚未发布)。行业趋势背景下(OpenAI 研究 Codex 长时间持续工作、Anthropic 称 Claude Code 越来越多用于长任务),v3 方向:

- **durable execution**:模型请求和工具调用**前先保存执行状态,完成后写回结果**;
- **崩溃恢复**:进程崩溃、甚至 Harness 自身升级,都能从中断处继续;
- **副作用感知**:重启后识别哪些任务已完成、哪些可重跑、哪些因副作用不能再执行一次;
- **状态分离存储**:对话、运行状态、Token 成本分开保存,支持**跨版本状态迁移**。

> 现有能力是 durable session(会话持久化);v3 将补上 durable execution——与站内 [Agent 持久化运行范式](../03-agents/agent-persistence-patterns.md) 和 [Anthropic 长时 harness](../03-agents/agent-harness-long-running.md) 同属"长任务"趋势。

### 生态与影响力

- **OpenClaw**(38.4 万 Star)深度复用 Pi 的 Runtime 与 TUI,官方 README 致谢——Pi SDK 嵌入模式的最佳真实集成;
- **Oh My Pi**(2 万 Star):Fork Pi 内核,新增浏览器/子 Agent/海量内置工具;
- **MiniMax Code**:明确基于 OpenCode + Pi 搭建 Harness;
- **pi-chat**:聊天频道(Discord/Telegram)映射为独立 session/workspace/memory/Skills/worker + Gondolin 微 VM——channel 从消息地址变成 Agent 的持久责任边界;
- **pi-share-hf**:发布会话到 Hugging Face,推动 Agent 编码过程可审计、可学习;
- 社区前端:VS Code、Emacs、桌面、移动端多端。

### 与站内文章的对应

- [Pi Agent:源码级架构、插件生态与 DeepSearch 实践](pi-agent-plugins.md):插件视角(11 插件清单 + DeepSearch 扩展),与本文(架构/哲学/v3/生态)互补;
- [08-harness 通用编排框架](orchestration-frameworks.md):Pi 条目;
- [Subagent 上下文隔离](../03-agents/subagent-isolation.md) / [MCP 工具调用](../03-agents/tool-calling.md):Pi 用 tmux 多实例替代子代理、用 CLI+README 替代 MCP 的对照;
- [Building effective agents 五种模式](../03-agents/agent-building-effective-agents.md):Pi 的极简 agent loop 是"agents"模式的参考实现。

## 总结

1. **定位**:Pi 不是"又一个终端编码助手",而是把 Agent 主链路拆成**可独立复用、可嵌入、可扩展**积木的工程样板——模型抽象(pi-ai)、运行时循环(pi-agent-core)、终端渲染(pi-tui)、产品形态(pi-coding-agent)各司其职,中间全用**事件与钩子**解耦。
2. **五个"No"立立场**:不做 MCP(上下文 7-9% 代价)/子代理(黑盒)/权限弹窗(安全剧场)/Plan mode/内置 To-dos——都有可观测的替代方案。
3. **极简被基准验证**:4 工具 + <1000 token prompt 拿下 Terminal-Bench #2;少即是多。
4. **可观测性至上 + 文件即状态**:AGENTS.md/TODO.md/PLAN.md、JSONL 会话树、事件流,一切可见可审计可后处理。
5. **Harness v3 走向 durable execution**:崩溃恢复/副作用感知/状态分离迁移——长任务趋势下的基础设施动作。

**下一步学什么**:先用 [pi-agent-plugins.md](pi-agent-plugins.md) 上手插件与 DeepSearch;再按文末学习路径(读 agent-loop.ts 792 行 → pi-ai Provider → pi-tui 差分渲染 → protocol CBOR);或对照 [Anthropic 长时 harness](../03-agents/agent-harness-long-running.md) 理解 v3 方向。

## 延伸阅读

- 站内:[Pi Agent:源码级架构、插件生态与 DeepSearch 实践](pi-agent-plugins.md)、[08-harness 通用编排框架](orchestration-frameworks.md)、[Building effective agents](../03-agents/agent-building-effective-agents.md)、[Anthropic 长时 harness](../03-agents/agent-harness-long-running.md)、[Agent 持久化运行范式](../03-agents/agent-persistence-patterns.md)
- 官方一手:官网 https://pi.dev;文档 https://pi.dev/docs/latest;仓库 https://github.com/earendil-works/pi;示例扩展 https://github.com/earendil-works/pi/tree/main/packages/coding-agent/examples/extensions;Pi Packages https://pi.dev/packages
- 作者博客(第一手设计思想):
  - 《Why I built Pi》(本文章节核心来源):https://mariozechner.at/posts/2025-11-30-pi-coding-agent/
  - 《Claude Code 历史》(系统提示词与工具演变):https://mariozechner.at/posts/2025-08-03-cchistory/
  - 《What if you don't need MCP》:https://mariozechner.at/posts/2025-11-02-what-if-you-dont-need-mcp/
  - Armin Ronacher《Agents are hard》:https://lucumr.pocoo.org/2025/11/21/agents-are-hard/
- 源码级解析(中文):
  - 《Pi Agent Harness 源码深度技术解析》(9 包依赖 DAG + 核心链路代码级):https://www.iceyao.com.cn/post/2026-08-11-pi-agent-harness源码深度技术解析
  - 《Agent 的本质是一个 while 循环:拆解 pi 的 792 行核心源码》:http://www.jxxy.net/ai/articles/yanhua1010-agent-while-loop-source
  - 《零到一实现一个 Coding Agent》(读 Pi 源码课程,多数课用内置 faux provider,无需 API key 不花钱):https://juejin.cn/post/7663456780569313306
  - 《跟着 OpenCode 学习 Pi Coding Agent》系列:https://blog.csdn.net/qq_26879323/article/details/162466512
- 架构与理念:Pi 完整教学(四层/扩展/事件流):https://tpow-001.netlify.app/post/2026-06-07-pi-tutorial;Pi:一个故意不替你做决定的 Coding Agent:http://ailinklab.com/zh/opensource/pi-agent-harness
- 英文评测:Pi Coding Agent Review(极简主义/四模式/Session 树/诚实局限):https://andrew.ooo/posts/pi-coding-agent-minimal-terminal-harness-review
- v3 动态:Pi 重构 Agent 执行层(durable execution 方向):https://www.theblockbeats.info/flash/360970
- 生态:OpenClaw https://github.com/OpenClaw/OpenClaw;pi-chat https://github.com/earendil-works/pi-chat
