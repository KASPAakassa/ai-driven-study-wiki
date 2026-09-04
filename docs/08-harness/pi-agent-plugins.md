# Pi Agent:极简 Harness 的源码级架构、插件生态与 DeepSearch 实践

> **一句话摘要**:Pi 是一个"极简 Agent 框架(minimal agent harness)"——不内置子智能体、计划模式、权限弹窗,把一切留给用户组装。本文三层展开:**源码级架构拆解**(双层 Agent Loop、四原子工具、五步管道、拒 MCP 理由、Session Tree)、**11 个实用插件清单**、以及**用 Extension 给 Pi 补一个 DeepSearch 研究能力**的完整实践。
>
> **来源**:微信公众号《我的 Pi Agent 插件清单》(糖醋鱼哈),https://mp.weixin.qq.com/s/6E_cAjfnLFGlveCOdBHvXw;官网 https://pi.dev;架构概览与 DeepSearch 整理自 Yu 的赛博工位(https://yudesk.dev/docs/notes);源码级拆解整理自《Pi Agent 是什么:一个生产级 Agent 运行时的架构拆解》(迈索斯,https://mp.weixin.qq.com/s/cy-xG9FgryWmtvfgY5j8ag),原始资料存档于 `docs/inbox/pi-agent-architecture-source.md`

## 概念:Pi 是什么

**Pi** 是官网定义下的 **极简 Agent 框架(minimal agent harness)**。它的核心理念是一句反问:

> **你去适配 Pi,还是 Pi 适配你?** Pi 选择了后者。

它**不内置**子智能体、不搞计划模式、没有权限弹窗、没有内置待办事项——这些统统留给用户自己组装。需要某个功能,要么让 Pi 自己写一个,要么装个现成的插件包。

Pi 真正有意思的地方,不是它多做了什么,而是它**少做了什么**:它把 AI 编程工具最核心的那层保留下来——模型、上下文、工具、会话、扩展——然后尽量不把用户的工作流提前写死。所以更准确的理解是:**Pi 不是一个"更全"的 AI 编程产品,而是一个更薄、更透明的 coding agent harness**。

| 特性 | 说明 |
| --- | --- |
| 运行模式 | 交互式 TUI / 打印·JSON 模式 / RPC 进程集成 / SDK 嵌入 |
| 模型 | 15+ 模型供应商、数百个模型 |
| 会话 | 树结构存储,任意节点可回溯分支 |
| 插件机制 | Extensions 是 TypeScript 模块,可访问 Pi 全部工具、命令、快捷键、事件、TUI 组件;可打包成 Pi Package 经 npm 或 git 分发 |

```bash
pi install npm:@xxx/pi-xxx       # npm 分发
pi install git:github.com/user/repo   # git 分发
```

!!! note "与本站其他 Harness 的关系"
    Pi 走的是"**极简内核 + 插件生态**"路线,和 [mattpocock/skills](../07-agent-coding/skills/mattpocock-skills.md)"小、易改编、可组合"的哲学同源;它的插件形态可对照 [08-harness 章节](index.md) 的编码 Agent 与框架索引。

## 原理:Pi Runtime 是怎么工作的

### 整体结构:harness 内部拆成了哪些模块

一个 AI 编程工具可粗略分三层:模型、harness、工程环境。Pi 真正值得看的,是中间这层 harness 里面又拆成了哪些模块:

```
用户任务(目标、约束、@文件引用、steering message)
        ↓ 进入当前 cwd,创建或恢复 session
Pi Coding Agent Runtime
├── AgentSessionRuntime   维护当前 cwd、session,负责切换、fork、teardown
├── AgentSession          会话生命周期:模型、thinking、compaction、bash、事件订阅
│       ↓ 加载资源并构建 prompt
├── ResourceLoader        读取 AGENTS.md / CLAUDE.md、skills、extensions、prompt templates、themes
├── SystemPrompt Builder  把工具说明、项目规则、skills 摘要、日期和 cwd 放进系统提示词
│       ↓ 交给 harness 执行
├── AgentHarness          保存 messages、resources、tools、activeToolNames、hooks、follow-up 队列
├── AgentLoop             模型响应 → tool call → tool result → 继续下一轮,直到没有更多工具调用
│       ↓ 扩展和状态在循环旁边介入
├── ExtensionRunner       注册工具、命令、快捷键、UI、生命周期 hook
├── Tool Registry         read、edit、write、bash、grep、find、ls 和自定义工具
└── SessionManager        保存历史、分支、compact 记录、token 和成本信息
        ↓ 向外部系统请求模型,或在真实项目里执行工具
外部系统:Model Provider(Claude/OpenAI/Gemini/OpenRouter/本地端点)
        项目环境(文件系统、Shell、Git、测试命令、依赖、数据库)
        用户自定义资源(packages、skills、extensions、个人全局 AGENTS.md)
```

三个重点:

1. **Pi 不是只有一个"聊天 UI"**:CLI、交互 TUI、print/JSON、RPC、SDK 都只是入口,真正承接任务的是 `AgentSessionRuntime` 和 `AgentSession`;
2. **请求模型之前先做资源加载**:`ResourceLoader` 把 AGENTS.md、CLAUDE.md、skills、extensions、prompt templates 整理出来,交给 `SystemPrompt Builder` 组装成模型真正看到的上下文;
3. **模型不直接控制文件系统**:`AgentHarness` 和 `AgentLoop` 负责校验工具、执行工具、接住结果、继续下一轮;Extensions、Tool Registry、SessionManager 在旁边扩展能力和保存状态。

### 一次请求的时序

1. **输入任务**:创建/恢复 AgentSession,合并 cwd 与历史消息;
2. **引用文件或规则**:ResourceLoader 读取 AGENTS.md、skills、extensions,模型收到 system prompt + messages + tools;
3. **等待 agent 行动**:AgentLoop 调用 `streamAssistantResponse`,模型返回文本或 `tool_call`;
4. **观察工具调用**:Harness **校验工具名和参数**,触发 extension hooks,read/edit/write/bash 开始执行;
5. **继续或插话**:`tool_result` 追加进 messages,follow-up / steering message 可插入,模型带结果继续下一轮;
6. **得到结论**:没有更多 `tool_call` 后结束 turn,SessionManager 保存记录。

最关键的是第 4-5 步之间的来回:**模型只提出 `tool_call`,Pi 接住调用、校验、触发 hooks、执行真实操作,再把 `tool_result` 放回上下文**。这就是 coding agent 和普通聊天机器人的区别——聊天机器人在文本里完成任务,coding agent 要进入工程系统,必须有 harness 管理工具、上下文和状态。

Pi 的默认工具很少:`read`(读文件)、`edit`(改已有文件)、`write`(创建/覆盖)、`bash`(执行 shell 命令),以及可启用/限制的 `grep`、`find`、`ls` 只读工具。这个工具集已形成编程闭环:读代码、改代码、跑测试、根据错误继续修。

### 为什么它不急着内置很多功能

很多产品把计划模式、todo、子代理、MCP、权限弹窗、浏览器工具都做进产品里——上手快,但代价是**你很难知道模型实际收到了什么上下文,也很难把产品工作流改成自己的工作流**。Pi 的路线相反:核心只管 agent loop,具体工作流交给用户和团队自己组合:

| 你想改变什么 | Pi 交给哪里 |
| --- | --- |
| 项目规则 | AGENTS.md / CLAUDE.md |
| 专门任务方法 | Skills |
| 自定义工具和 UI | Extensions |
| 一组可分享能力 | Pi Packages |
| 模型选择 | Provider / Model 配置 |

**四层扩展入口**(不是只有"插件"一种方式):

| 你要沉淀的东西 | 用什么 | 适合什么场景 |
| --- | --- | --- |
| 项目习惯和约束 | AGENTS.md / CLAUDE.md | 告诉 agent 怎么改代码、跑什么检查、哪些目录不能碰 |
| 一套可复用方法 | Skill | 代码审查、写文章、发版、生成文档这类"步骤和经验" |
| 一个真实能力 | Extension | 注册工具、拦截工具调用、加 slash command、加 UI、接外部 API |
| 一组可分发能力 | Pi Package | 把 extensions、skills、prompt templates、themes 打包复用 |

> **Skill 是工作手册,Extension 是可执行插件,Package 是分发容器。**

### 源码级拆解:双层 Agent Loop 与三层运行时(pi-agent-core 0.81.x)

> 本节整理自《Pi Agent 是什么:一个生产级 Agent 运行时的架构拆解》(迈索斯),基于 badlogic/pi-mono 公开仓库(原文作者访问日期 2026-08-07)。

**pi-mono monorepo 的 7 个包**(分层纪律严格:pi-ai 不知道 pi-agent-core 存在,pi-agent-core 不依赖 pi-coding-agent,每层可独立测试/替换):

| 包 | 定位 | 职责 |
| --- | --- | --- |
| pi-ai | LLM 抽象层 | 统一 20+ 提供商 API、上下文序列化、跨提供商切换 |
| **pi-agent-core** | Agent 运行时 | 通用 Agent 循环、状态机、工具系统、事件系统、会话管理(整个体系的"发动机") |
| pi-coding-agent | 编码 Agent CLI | 面向编码场景的交互式 Agent,会话管理、扩展系统 |
| pi-tui | 终端 UI 库 | 保留模式渲染、差异更新、图片显示、自动补全 |
| pi-web-ui | Web UI 组件 | 聊天面板、沙箱 iframe、Artifact 渲染 |
| pi-mom | Slack 机器人 | 将 Agent 接入 Slack 工作空间 |
| pi-pods | GPU Pod 管理 | 远程 vLLM 部署和管理 |

**Agent Loop 的两层设计**:

1. **底层:`agentLoop` 纯函数**——`agentLoop(context, config) → Observable<AgentEvent>`,无状态、不持有可变状态、不管理队列、不负责持久化;可嵌入 React 组件/Express 服务器/CLI 工具而不引入 Pi 其他部分。内部是**双层嵌套循环**:
   - **外层(follow-up loop)**:处理 Agent 停止后追加的消息("继续"、"再检查一下");
   - **内层(turn loop)**:标准一轮执行——调用 LLM → 检查工具调用 → 执行工具 → 反馈结果 → 检查是否停止;
2. **上层:`Agent` 有状态类**——封装消息历史(transcript)、工具注册表、配置快照(model/systemPrompt/thinkingLevel 可运行时动态修改)、两个消息队列(**steering 队列**用于中途干预/"停止"按钮,**followUp 队列**用于停止后追加指令)、AbortController(单次运行锁 + 中断控制);
3. **再往上:`AgentHarness` 编排层**——会话持久化(JSONL Session)、资源管理(Skills/Prompts)、执行环境抽象(跨 Node/Termux/Browser 的 FS/Shell 接口)、操作锁。**"生产级"和"demo 级"的分界线:demo 只需要 Agent,生产需要 Harness。**(与上文运行时模块图中的 AgentHarness 同指一层——前者按职责列示,此处按源码分层描述。)

**工具系统:四个原子工具 + 五步管道**

Pi 的核心工具是 4 个原子操作——`read`(读取)、`write`(创建/覆盖)、`edit`(基于字符串匹配的精准修改)、`bash`(执行 Shell 命令);另有 `grep`、`find`、`ls` 等只读工具可按需启用。Agent 像程序员一样组合它们:改代码 = read + edit;创建项目 = bash(mkdir)+ write;调试 = bash(跑测试)+ read(看错误日志)。**工具越少,Agent 越不会选错工具;工具越原子,行为越可预测。**

工具从定义到执行结果回收经过**五步管道**,每步都有明确扩展点:

```
定义(defineTool + TypeBox schema) → 注册(registerTool) → 拦截(beforeToolCall hook)
→ 执行(并行/串行) → 回收(afterToolCall hook)
```

`beforeToolCall` 和 `afterToolCall` 是 hook——注入权限检查、日志记录、结果缓存等逻辑,无需修改工具本身。

**为什么不用 MCP?(有争议的设计决策)**

MCP 的问题是**启动成本**:一个典型 MCP Server 连接时把所有工具定义一次性发给 Agent——50 个工具的 Server 可能意味着 13,000+ token 的系统 prompt 开销,而大部分工具本次对话用不到。Pi 的替代:**CLI 工具 + README 渐进式加载**——工具可执行文件放磁盘,README 描述用途和参数,Agent 需要时通过 `read` 工具按需加载。结果:Pi 核心系统 Prompt 仅约 **800 token**(同类框架通常 1000-2000)。这是典型的"Pi 式权衡":放弃生态互操作性(MCP 现成 Server 很多),换取更低 token 开销和更精确的上下文控制。**注意:这是核心层的设计选择——社区插件(如 `pi-mcp-adapter`)仍可按需接入 MCP 生态。**

**消息系统:内外分离 + 事件驱动**

- **内部 `AgentMessage`**:联合类型含 7 种消息——除标准 user/assistant/tool 外,还有系统通知、配置变更、分支标记等"元消息";TypeScript 声明合并允许应用层扩展消息类型而无需改框架;
- **外部 `convertToLlm()`**:把 AgentMessage[] 转为 LLM 能理解的 3 种标准 Message(user/assistant/tool)——UI 专用消息、未完成流式消息、元数据消息只存在于内部,不浪费对外 token;
- **`transformContext()`**:上下文压缩/裁剪——旧消息替换为摘要、删除不再需要的工具结果;
- **流水线**:`AgentMessage[] → transformContext() → AgentMessage[] → convertToLlm() → Message[] → LLM`;
- **事件驱动可观测性**:`agent.subscribe()` 注册的监听器按注册顺序依次调用(await)——agent_start/turn_start/message_update(流式增量)/tool_execution_start/tool_execution_end/turn_end(统计 token)/agent_end,把日志、监控、权限拦截、UI 更新以插件形式挂载到 Agent 上,不改核心循环。**事件系统 + 工具 hook = Pi 的"神经系统"。**

**会话管理:Session Tree(树结构而非线性日志)**

每个会话是一个 JSONL 文件(追加写,一行一个条目),条目含 `id`、`parentId`、`timestamp`,通过 parentId 链接可分叉:

```
        [根消息]
        /        \
   [分支A]    [分支B]
    /    \         \
[A.1]  [A.2]     [B.1]
```

三种核心操作:**`branch()`**(从当前节点开新分支,试错不影响主线)、**`checkout()`**(切换分支)、**`rewind(n)`**(回退 N 条消息重来)。会话具备类似 Git 的探索能力——每条路径完整保留,出错随时回分叉点。除消息外还支持多种条目:compaction(压缩标记)、model_change(模型切换)、branch_summary(分支摘要);`buildSessionContext()` 从当前叶子沿 parentId 链走回根,收集所有有效消息。

**设计哲学三条**:

1. **显式优于隐式**:上下文完全可控、完全可序列化(完整 JSON 序列化支持存储恢复);不替你管理 prompt、不替你压缩历史——代价是你需要自己做更多工作;
2. **原子优于庞杂**:4 个工具打天下,组合而非枚举;行为更可预测、system prompt 更短——但需要调用第三方 API 时得自己写工具;
3. **库优于框架**:可以只用 `agentLoop` 函数嵌入现有系统,不引入 Agent 类和 Harness;框架不强加架构——代价是开箱即用体验不如 Claude Code 产品。

**当前边界**:无内置权限系统(设计文档建议容器化/沙箱处理)、中文文档和社区薄弱、版本迭代快(0.81.x)、API 稳定性承诺尚不明确。

## 插件清单

| 插件 | 作用 | 典型场景 | 安装 |
| --- | --- | --- | --- |
| **pi-cache-optimizer** | 稳定 Prompt 结构、提升 KV 缓存命中率;跨模型切换自动适配供应商缓存策略;对话末尾展示缓存统计 | 几十轮长对话后二次打开项目响应变快,省 API 费用 | `pi install npm:pi-cache-optimizer` |
| **pi-slopchop** | 终端内审查代码 diff、加注释、生成修改建议,结果直接喂给 Pi 改代码 | 提 PR 前先让 Pi 以 reviewer 视角过一遍改动 | `pi install npm:pi-slopchop` |
| **pi-rtk-optimizer** | 拦截 bash 调用,把低效 shell 命令重写为更优等价命令;压缩工具输出(去 ANSI、截断、聚合测试输出、过滤构建日志) | 调试时 5-6 轮定位问题缩减到 3-4 轮(需 `cargo install rtk` 或 `brew install rtk`) | `pi install npm:pi-rtk-optimizer` |
| **pi-subagents** | 动态创建子智能体:链式执行(前一步输出自动成为下一步输入)与并行执行 | 大重构前两个子 agent 并行跑代码质量审查 + 安全审计;开发走"分析→设计→写码"流水线 | `pi install npm:pi-subagents` |
| **pi-agent-browser-native** | 浏览器自动化:打开网页、截图、点击、填表单、跑 QA 检查 | 查最新 API 文档、部署后自动开线上页查控制台报错 | `pi install npm:pi-agent-browser-native` |
| **pi-mcp-adapter** | 按 MCP 标准连接任意 MCP 服务器,自动发现注册其工具,支持 OAuth | 连本地 MySQL,对话里直接查库,不用开客户端 | `pi install npm:pi-mcp-adapter` |
| **dcg-guard** | bash 执行前先经 dcg 评估,拦截破坏性命令(如 `rm -rf`);Fail-Open 策略(dcg 挂了不影响执行) | 批量重构不怕误操作(需 `brew install dcg`;本地扩展放 `~/.pi/agent/extensions/`) | 手动放文件 + `pi reload` |
| **pi-hashline-edit-pro** | 为每行代码生成唯一 3 字符哈希锚点,编辑基于哈希而非行号 | 改上千行 K8s YAML/Terraform 时行号偏移不误改 | `pi install npm:pi-hashline-edit-pro` |
| **pi-add-dir** | 加载外部目录的 AGENTS.md / CLAUDE.md / 技能文件 | 微服务多仓库场景,一次对话理解完整调用链,不"断片" | `pi install npm:pi-add-dir` |
| **pi-workspace-history** | 会话内跟踪文件修改,一键撤销(类似 Claude Code 的 `/rewind`) | TS 重构批量改 30+ 文件后类型冲突,一句话回滚 | `pi install npm:pi-workspace-history` |
| **pi-autoresearch** | 自主实验循环(受 Karpathy 的 autoresearch 启发):提出假设→跑实验→测量→保留/丢弃→迭代 | 优化数据处理管道自动跑 20+ 轮实验找最优参数 | `pi install npm:pi-autoresearch` |
| **主题 @victor-software-house/pi-curated-themes** | 从 iTerm2-Color-Schemes 精选的暗色终端主题 | 夜间编程舒适度 | `pi install npm:@victor-software-house/pi-curated-themes` |

!!! tip "两个特别值得借鉴的插件思路"
    - **pi-rtk-optimizer**:给工具输出"减脂"——压缩/过滤工具输出能直接减少 token 与无效轮次,是成本优化的通用杠杆;
    - **pi-hashline-edit-pro**:用哈希锚点替代行号编辑,解决长文件行号漂移问题,对大文件场景很实用。

## 代码 / 实现:用 Extension 给 Pi 补一个 DeepSearch

DeepSearch 不是简单的联网搜索,而是一套研究型工作流:问题拆解 → 多轮检索 → 来源筛选 → 证据整理 → 综合回答。它涉及网络请求、第三方搜索 API、来源过滤、结果截断、引用格式和安全边界——**这些属于工作流能力,不该写进 Pi 本体,也不该只靠 prompt 硬凑,最适合做成一个 Pi Extension**。

设计原则:把"检索"和"综合"拆开——Extension 负责确定性的搜索、去重、截断(只提供高质量证据),Pi 当前模型负责判断证据重要性与最终答案写作(需要推理和上下文理解)。Extension 不需要自己调用模型,也不需要变成嵌套 agent。

### 目录结构

```
.pi/extensions/deepsearch/
  package.json
  index.ts
```

```json
{
  "name": "pi-deepsearch-extension",
  "private": true,
  "dependencies": {
    "typebox": "*",
    "@earendil-works/pi-ai": "*",
    "@earendil-works/pi-coding-agent": "*"
  },
  "pi": {
    "extensions": ["./index.ts"]
  }
}
```

```bash
mkdir -p .pi/extensions/deepsearch
cd .pi/extensions/deepsearch && npm install
export TAVILY_API_KEY=tvly-...   # 搜索服务可选 Tavily/Exa/Brave/SerpAPI,第一版先抽象成 searchWeb()
```

### 注册 deep_search 工具(核心)

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { StringEnum } from "@earendil-works/pi-ai";
import { Type } from "typebox";

type SearchResult = {
  title: string;
  url: string;
  snippet: string;
  score?: number;
};

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "deep_search",
    label: "DeepSearch",
    description: "Search the web for source-backed evidence about a question.",
    promptSnippet: "Research a question with web search and return source-backed evidence.",
    promptGuidelines: [
      "Use deep_search when the user asks for current facts, external sources, comparison, investigation, or source-backed research.",
      "After deep_search returns results, synthesize an answer with citations and clearly separate facts, inference, and uncertainty.",
      "Do not treat deep_search results as final truth; inspect source quality and mention gaps."
    ],
    parameters: Type.Object({
      query: Type.String({ description: "The research question or search query." }),
      depth: Type.Optional(StringEnum(["quick", "normal", "deep"] as const)),
      maxResults: Type.Optional(Type.Number({ minimum: 3, maximum: 10, default: 6 }))
    }),
    async execute(_toolCallId, params, signal) {
      const depth = params.depth ?? "normal";
      const maxResults = params.maxResults ?? 6;
      const results = await searchWeb(params.query, depth, maxResults, signal);
      return {
        content: [{ type: "text", text: formatResultsForModel(params.query, results) }],
        details: { query: params.query, depth, results }
      };
    }
  });
}

async function searchWeb(query: string, depth: "quick" | "normal" | "deep",
  maxResults: number, signal: AbortSignal): Promise<SearchResult[]> {
  const apiKey = process.env.TAVILY_API_KEY;
  if (!apiKey) throw new Error("Missing TAVILY_API_KEY. Set it before starting pi.");

  const response = await fetch("https://api.tavily.com/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      api_key: apiKey, query,
      search_depth: depth === "quick" ? "basic" : "advanced",
      max_results: maxResults,
      include_answer: false,
      include_raw_content: depth === "deep"
    }),
    signal
  });
  if (!response.ok) throw new Error(`Search failed: ${response.status} ${response.statusText}`);

  const data = await response.json() as { results?: Array<{ title?: string; url?: string; content?: string; score?: number }> };
  return dedupeByUrl((data.results ?? []).map((item) => ({
    title: item.title ?? "Untitled", url: item.url ?? "",
    snippet: item.content ?? "", score: item.score
  }))).filter((item) => item.url);
}

function dedupeByUrl(results: SearchResult[]): SearchResult[] {
  const seen = new Set<string>();
  return results.filter((r) => {
    const key = normalizeUrl(r.url);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function normalizeUrl(url: string): string {
  try {
    const parsed = new URL(url);
    parsed.hash = "";
    ["utm_source", "utm_medium", "utm_campaign"].forEach((p) => parsed.searchParams.delete(p));
    return parsed.toString();
  } catch { return url; }
}

function formatResultsForModel(query: string, results: SearchResult[]): string {
  if (results.length === 0) return `DeepSearch found no results for: ${query}`;
  const lines = results.map((result, index) => [
    `## Source ${index + 1}`, `Title: ${result.title}`, `URL: ${result.url}`,
    result.score === undefined ? undefined : `Score: ${result.score}`,
    `Snippet: ${result.snippet}`
  ].filter(Boolean).join("\n"));
  return [
    `DeepSearch query: ${query}`, "",
    "Use these sources as evidence. Cite URLs when making factual claims.",
    "Separate confirmed facts from inference and uncertainty.", "",
    ...lines
  ].join("\n\n");
}
```

**关键点**:`pi.registerTool()` 把工具暴露给模型;`parameters` 告诉模型需要哪些参数;`promptGuidelines` 告诉模型**什么时候用、用完后怎么处理**;`dedupeByUrl` 去掉重复 URL;`formatResultsForModel` 把结果整理成模型容易引用的证据块。

### 加一个 /deepsearch 命令(用户直接入口)

工具是给模型调用的,用户还需要直接入口。命令不直接搜索,而是给 Pi 发一条更完整的任务说明——**保留 agent 的判断空间,搜索工具只是证据入口,不是最终答案生成器**:

```typescript
pi.registerCommand("deepsearch", {
  description: "Run a source-backed DeepSearch task",
  handler: async (args, ctx) => {
    const query = String(args ?? "").trim();
    if (!query) { ctx.ui.notify("Usage: /deepsearch <question>", "warning"); return; }
    pi.sendUserMessage(
      [
        "请对下面的问题做 DeepSearch。", "",
        `问题:${query}`, "",
        "要求:",
        "1. 先判断是否需要调用 deep_search。",
        "2. 如果问题较复杂,先拆成 2-4 个子问题分别检索。",
        "3. 最终答案必须包含来源链接。",
        "4. 区分事实、推断和仍不确定的部分。",
        "5. 不要把搜索结果原样堆出来,要给出综合判断。"
      ].join("\n"),
      { deliverAs: "followUp" }
    );
  }
});
```

### 启动与验证

```bash
TAVILY_API_KEY=tvly-... pi                    # 项目本地 extension 自动加载
TAVILY_API_KEY=tvly-... pi -e ./.pi/extensions/deepsearch/index.ts   # 临时测试
```

验收标准:能看到 `deep_search` 被调用、每个关键事实后有 URL、不重复引用同一页面、有归纳判断、对版本变化和第三方 API 保持不确定性边界。如果结果只是"搜索结果列表",说明 `promptGuidelines` 不够强——改成 "Use deep_search to gather evidence, not to produce the final answer" 并强调引用官方文档与一手来源。

### 让 DeepSearch 更像研究工具(三阶段进阶)

1. **子问题拆解**:把大问题(如"Pi Agent 能不能替代 Claude Code?")拆成 2-4 个子问题分别检索——第一版让模型自己拆,第二版让 `/deepsearch` 命令强制模型先列子问题再逐个检索;
2. **来源质量分层**:在 `formatResultsForModel()` 里用 `classifySource(url)` 标注来源类型——P0 官方文档/源码/release note、P1 作者博客/维护者说明/issue、P2 高质量教程、P3 社区讨论,避免模型把社区传言和官方文档放在同一证据等级;
3. **上下文截断**:工具输出少而精——标题、URL、200-500 字摘要放进输出;页面全文、原始 HTML、搜索 API 原始 JSON 放进 `details` 而非正文。

## 实践 / 应用:插件管理命令与借鉴

```bash
# 查看已安装的 npm 包
ls ~/.pi/agent/npm/node_modules/ | grep ^pi-

# 查看启用的扩展
ls ~/.pi/agent/extensions/

# 安装新插件
pi install npm:<package-name>

# 更新所有插件
pi update --extensions
```

1. **极简内核 + 按需组装**:Pi 不给"全家桶",而是提供钩子让用户/agent 组装能力——适合喜欢掌控细节、讨厌默认行为的用户;
2. **插件是分层能力**:缓存(省钱)、输出压缩(省 token)、安全拦截(防误删)、子 agent(提并行)、浏览器/MCP(扩边界)——几乎覆盖了 [AI Friendly 架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md) 中 Harness 七层里的工具层与安全层;
3. **Extension 是真正的插件层**:注册工具(deep_search、query_logs、open_issue)、注册命令(/review、/publish)、拦截事件(bash 执行 rm -rf/sudo 前确认)、改 UI、保存状态、接外部系统;全局放 `~/.pi/agent/extensions/`,项目放 `.pi/extensions/`,临时测试用 `pi -e ./my-extension.ts`;
4. **选型提示**:Pi 生态相对新,插件质量参差;接入前先看维护活跃度,重要功能优先选官方或高星插件。

## 总结

- Pi = **极简 Agent Harness**:不内置能力,用插件生态让用户自己组装;核心只管 agent loop,工作流交给 AGENTS.md / Skills / Extensions / Packages 四层;
- **运行时架构**:AgentSessionRuntime / AgentSession(会话)→ ResourceLoader / SystemPrompt Builder(上下文)→ AgentHarness / AgentLoop(工具循环)→ ExtensionRunner / Tool Registry / SessionManager(扩展与状态);模型只提 `tool_call`,Pi 校验、执行、把结果放回上下文;
- **源码级设计**:双层 Agent Loop(agentLoop 纯函数可嵌入 + Agent 有状态类 + AgentHarness 生产分界)、四原子工具(read/write/edit/bash)+ 五步管道 hook、拒 MCP 换 800 token 系统 Prompt、消息内外分离(AgentMessage 7 种 vs 3 种标准)、Session Tree(branch/checkout/rewind,JSONL 追加写)、事件驱动可观测性;
- **设计哲学**:显式优于隐式、原子优于庞杂、库优于框架——理解"Agent SDK 应该怎么设计"的最佳参考之一;
- **11 个实用插件**覆盖:缓存优化、代码审查、命令重写、子智能体、浏览器自动化、MCP、命令安全、哈希锚点编辑、多目录上下文、撤销/重做、自主实验循环;
- **DeepSearch 实践**:把研究型工作流做成 Extension——检索与综合分离、promptGuidelines 控制行为、子问题拆解 + 来源分层 + 上下文截断三阶段进阶;
- **借鉴价值**:极简内核哲学、输出压缩/哈希锚点等插件思路、"检索与推理分离"的扩展设计模式。

## 延伸阅读

- 站内:[Harness 章节首页](index.md)、[通用编排框架](orchestration-frameworks.md)、[Pi Agent Harness 深度解析(设计哲学/四层架构/v3)](pi-agent-harness-deep-dive.md)、[mattpocock/skills](../07-agent-coding/skills/mattpocock-skills.md)、[Loop Engineering](../07-agent-coding/experience/loop-engineering.md)
- 外部:原文《我的 Pi Agent 插件清单》;Pi 官网 https://pi.dev;源码级拆解《Pi Agent 是什么》(迈索斯,https://mp.weixin.qq.com/s/cy-xG9FgryWmtvfgY5j8ag);GitHub https://github.com/badlogic/pi-mono;DeepWiki https://deepwiki.com/badlogic/pi-mono;学习笔记 learning-pi-agent / how-pi-agent-works / dg-ai-notes;pi-session-traces 数据集 https://huggingface.co/datasets/grfwings/pi-session-traces;Python 移植版 nu-duo;原始资料存档于 `docs/inbox/pi-agent-plugins-source.md`、`docs/inbox/pi-agent-architecture-source.md` 与 `docs/inbox/yudesk-claude-code/pi-agent_*.txt`
