# Claude Code Dynamic Workflows(/workflow,ultracode):把编排从上下文窗口搬进 JS 运行时

> **一句话摘要**:Dynamic Workflows 是 Claude Code 在 2026 年 5 月随 Opus 4.8 推出的多智能体编排能力——让 Claude **编写一段 JavaScript 脚本**,由独立运行时后台执行,同时调度几十到上百个 Subagent 并行工作。核心设计决策:**把"计划"从 Claude 的上下文窗口里挪出去,放进一段可运行、可重跑的确定性 JS 代码**——换来规模、可重复性与可固化的质量模式。
>
> **来源**:微信公众号「AI觉醒观测者」《Claude Code /workflow 深度解析:多智能体编排的底层实现》,https://mp.weixin.qq.com/s/Luw5nGwHx_oXipIlFIW2ew;原始资料存档于 `docs/inbox/claude-workflows-source.md`

## 概念:为什么需要 Workflow

日常使用 Claude Code 时的大规模任务困境:全面扫描几百个文件的代码库找 auth 漏洞——单次对话上下文装不下;逐步扫描则"计划"躺在 Claude 记忆里,做完第一个文件第二个文件的上下文已被挤占;用 Agent 工具并行又只能"凭感觉决定下一步",没有可重跑的确定性计划。

**Workflow 解决的核心问题**:把"计划"从 Claude 上下文窗口里挪出去,放进一段可运行、可重跑的 JavaScript 代码。同时把**质量保障模式固化成可复现流程**——比如多个独立 Agent 互相对抗性审查对方的发现,而非靠单次 Pass 的 Claude 自己判断自己对不对。

### 四种多步骤执行方式的本质区别:"谁来持有计划"

| 方案 | 计划持有者 | 中间结果存在哪 | 可重复性 | 规模 |
| --- | --- | --- | --- | --- |
| Subagents | Claude,逐轮决策 | Claude 上下文窗口 | 每次重跑策略不同 | 每轮几个 |
| Skills | Claude,跟随 Prompt | Claude 上下文窗口 | 同 Subagents | 同 Subagents |
| Agent Teams | 主导 Agent,逐轮分配 | 共享任务列表 | 团队定义可复用 | 少量长期 peers |
| **Workflows** | **JavaScript 脚本** | **脚本变量** | **脚本本身可重跑** | **几十到上百个 agent** |

Workflow 把"哪个 Agent 做什么、做完了做什么"编进代码的循环和分支里。Claude 的上下文里只剩最终结果,不再承载所有中间状态——超大规模并行成为可能,执行过程也确定性可追踪。

## 代码 / 实现:如何触发 Workflow

**1. 关键词触发(最常用)**:提示词里加 `ultracode` 关键词,Claude 会为任务编写 Workflow 脚本并执行:

```
ultracode: 扫描 src/routes/ 下所有 API 路由,找出缺少 auth 检查的接口
```

输入框紫色高亮该关键词;按 `Option+W`(macOS)或 `Alt+W` 取消。也可用自然语言("用 workflow 来做")。

!!! note "版本注意"
    Dynamic Workflows 于 2026-05-28 随 v2.1.154 发布,触发关键词是 `workflow`;2026-06-02 的 v2.1.160 改为 `ultracode`(原词不再触发)。v2.1.154–v2.1.159 请用 `workflow`;自然语言方式两个版本均有效。

**2. 全局 ultracode 模式**:`/effort ultracode` 开启后,当前 session 每个实质性任务自动规划成 Workflow(一个需求可能触发多个串联 Workflow:先理解代码、再改动、再验证)。**代价是 token 消耗大幅增加**,用完建议 `/effort high` 退回。

**3. 内置 `/deep-research`**:Claude Code 自带的第一个 Workflow 命令——后台多角度搜索、交叉核验,返回带引用综合报告,主对话窗口保持响应。

**4. 保存复用**:运行 `/workflows` 选中 run 按 `s` 保存——存 `.claude/workflows/`(随项目共享)或 `~/.claude/workflows/`(个人所有项目),保存后出现在 `/` 自动补全。

## 原理:JavaScript 运行时架构与核心约束

**核心设计决策**:把编排逻辑从"Claude 的输出"迁移到"独立 JavaScript 运行时"。Claude 编写 JS 脚本,由运行时在**后台独立进程**执行——与对话上下文完全隔离,中间结果存脚本变量,不进 Claude 上下文窗口。每次运行脚本持久化到 `~/.claude/projects/` 对应 session 目录,可直接查看/编辑后重跑。

| 运行时约束 | 原因 |
| --- | --- |
| 最多 **16 个 Agent 并发**(受 CPU 核心数限制) | 控制本地资源消耗 |
| 每次运行最多 **1000 个 Agent** | 防止无限循环失控 |
| 禁止 `Date.now()` / `Math.random()` / `new Date()`(无参数) | 保证确定性,支持断点续跑 |
| Subagent 始终在 `acceptEdits` 模式运行 | 文件编辑自动批准,减少中断 |
| 纯 JavaScript(不支持 TypeScript 转译) | 简化运行时,类型注解会报错 |

### 核心 API:最小脚本结构

```javascript
export const meta = {
  name: 'auth-audit',
  description: '扫描所有 API 路由的 auth 缺失问题',
  phases: [
    { title: '扫描' },
    { title: '验证' },
  ],
}

// 脚本主体在异步上下文中执行,可直接 await
phase('扫描')
const findings = await agent('扫描 src/routes/ 找出 auth 漏洞', {
  schema: FINDINGS_SCHEMA,
  label: 'auth-scanner'
})
```

`meta` 必须是**纯字面量**(不能有变量/函数调用/模板字符串/spread);`phases` 标题与脚本中 `phase()` 调用标题精确匹配时,Agent 归入对应进度分组。

### agent():基础单元

```javascript
const result = await agent(prompt, {
  schema,      // JSON Schema → 结构化输出 + 自动重试
  label,       // /workflows 面板显示名称
  phase,       // 手动指定进度分组(在 pipeline/parallel 内防状态竞争)
  model,       // 覆盖 session 模型(如 haiku 做轻量任务)
  agentType,   // 使用自定义 subagent 类型
  isolation,   // 'worktree' → 独立 git worktree 运行(并行写文件防冲突)
})
```

- **返回值**:无 schema 返回最终文本;有 schema 运行时强制 Agent 调 `StructuredOutput` 工具,校验通过返回 JS 对象,失败自动重试(无需手动 parse JSON);出错或被跳过返回 `null`,记得 `.filter(Boolean)` 过滤。

### pipeline() vs parallel():最重要的设计选择

官方明确建议:**默认用 `pipeline()`,只有下游真的需要全量结果时才用 `parallel()`**。

- **`pipeline(items, ...stages)`**:无屏障,各 item 独立推进——Item A 完成第 1 阶段立即进第 2 阶段,不等 B/C;壁钟时间 = 最慢那条流水线(而非"各阶段最慢之和");每个 stage 接收 `(prevResult, originalItem, index)`;
- **`parallel(thunks[])`**:有同步屏障,等所有 thunk 完成才返回;壁钟时间 = 最慢那个 thunk,快的只能等待。**正确使用场景只有两种**:下游需要对全量结果去重/跨 item 比较;整体结果为空时 early-exit。

**多维度代码审查案例**:

```javascript
const DIMS = [
  { key: 'bugs', prompt: '找出所有逻辑 bug' },
  { key: 'security', prompt: '找出所有安全漏洞' },
  { key: 'perf', prompt: '找出性能瓶颈' }
]
const results = await pipeline(
  DIMS,
  d => agent(d.prompt, { label: `review:${d.key}`, phase: 'Review', schema: FINDINGS }),
  findings => parallel(findings.map(f => () =>
    agent(`对抗性验证:${f.title}`, { label: `verify:${f.file}`, phase: 'Verify', schema: VERDICT })
  ))
)
```

### workflow():嵌套调用

```javascript
const report = await workflow('deep-research', { question: '...' })
// 或调用脚本文件
const result = await workflow({ scriptPath: '/path/to/script.js' }, args)
```

在一个 Workflow 内调用另一个已保存的 Workflow,共享父级并发上限、Agent 计数和 token 预算;**只支持一层嵌套**,子 Workflow 内再调 `workflow()` 会报错。

## 实践 / 应用:三个关键机制与编排模式

### 机制一:确定性执行与断点续跑(Journal)

运行时把每个 `agent()` 调用结果记录到 **Journal(执行日志)**。Workflow 中途暂停/失败可同 session 续跑:**已完成调用直接从 Journal 返回缓存结果(毫秒级),未完成的重新执行;相同脚本 + 相同 args → 100% 缓存命中**。

为让缓存 key 一致,脚本必须确定性——这就是禁 `Date.now()`/`Math.random()` 的原因(带固定参数的 `new Date('2026-01-01')` 不受限)。需要时间戳?通过 `args` 外部传入(`Workflow({ args: { timestamp: Date.now() } })`)。**注意:断点续跑只在当前 session 内有效,退出后 Journal 丢失**。

### 机制二:结构化输出与 Schema 验证

给 `agent()` 传 `schema` 时,运行时强制 Subagent 调内置 `StructuredOutput` 工具,在**工具调用层面**做 JSON Schema 校验,失败自动重试——比返回自由文本再手动 parse 可靠得多。返回值直接是 JS 对象,无需 `JSON.parse`。

### 机制三:Git Worktree 隔离

多个 Agent 并行写文件时,`isolation: 'worktree'` 为每个 Agent 创建独立 git worktree,防冲突。**有额外开销(200-500ms setup + 磁盘占用),只在并行写文件会冲突时使用;只读操作不需要;无改动时 worktree 自动清理**。

### 实用编排模式

**1. 对抗性验证(质量核心)**:独立 Skeptic Agent 尝试反驳每个发现,多数票通过才确认——相比单次 Pass 最核心的质量优势:

```javascript
const votes = await parallel(
  Array.from({ length: 3 }, () => () =>
    agent(`尝试反驳这个 bug 报告:${finding.description}。默认倾向 refuted=true。`, {
      schema: VERDICT_SCHEMA
    })
  )
)
const survives = votes.filter(Boolean).filter(v => !v.refuted).length >= 2
```

**2. Loop-Until-Dry**:发现数量未知时,"连续 K 轮没有新发现才停止"比计数循环更稳(计数会漏掉尾部):

```javascript
const seen = new Set()
const confirmed = []
let dryRounds = 0

while (dryRounds < 2) {
  const found = await agent('继续搜索未发现的 bug', { schema: BUGS_SCHEMA })
  const fresh = found.bugs.filter(b => !seen.has(`${b.file}:${b.line}`))
  if (!fresh.length) { dryRounds++; continue }
  dryRounds = 0
  fresh.forEach(b => seen.add(`${b.file}:${b.line}`))
  confirmed.push(...fresh)
}
```

!!! warning "去重要对 `seen`(全部已见过的),而非仅 `confirmed`"
    否则被 Skeptic 否决的发现会每轮重复出现,导致循环不收敛。

**3. Token 预算控制**:用户指定 Token 上限(如 `+500k`)时,`budget` 全局变量可动态调整循环深度。**注意 `budget.total` 无上限时为 `null`,要用 `budget.total &&` 守卫,否则循环一路跑到 1000 Agent 上限**。

### /workflows 监控界面

Workflow 后台运行不占主对话窗口。`/workflows` 查看运行中/已完成 Workflow,进度界面按 phase 分组展示每个 Agent 的状态/token 消耗/耗时。快捷键:`↑/↓` 选择、`Enter/→` 展开查看 prompt/工具调用/结果、`p` 暂停/继续、`x` 停止、`r` 重启、`s` 保存为命令。

## 实践 / 应用:何时用 Workflow

**适合**:

- 全代码库 bug 扫描 / 安全审计,需要独立验证;
- 大规模迁移(几百个文件并行处理);
- 需要多角度交叉核验的研究任务;
- 需要对抗性验证保证质量的关键工作;
- 希望把流程固化成可重复执行的脚本。

**不适合**:

- 简单一次性任务(改个 bug、解释一段代码);
- 需要中途频繁交互讨论的任务(Workflow 运行中无法接收用户输入);
- 只是想并行跑几个 Subagent 而不需要确定性编排。

**成本提示**:一次大型 Workflow 的 token 消耗可能是普通对话的数倍至数十倍——**先在小范围试跑确认效果,再扩大到全量**。

## 总结

- **核心设计决策**:把编排计划从模型上下文窗口移进确定性 JS 脚本,由独立运行时执行——上下文窗口不再是并发瓶颈,几百个 Agent 并行成为可能;
- **三大收益**:规模(几十到上百 agent 并行)、可重复性(脚本可 diff/版本控制/重跑)、质量模式(对抗性验证/Loop-Until-Dry 等可固化);
- **关键 API**:`agent()`(基础单元,schema 结构化输出)、`pipeline()` vs `parallel()`(无屏障流水线 vs 同步屏障,日常最重要的判断点)、`workflow()`(一层嵌套);
- **机制**:Journal 断点续跑(同 session)、StructuredOutput 工具层校验、git worktree 隔离并行写;
- **触发**:`ultracode` 关键词(v2.1.154-159 为 `workflow`)、`/effort ultracode` 全局模式、`/deep-research` 内置示例、`/workflows` 保存复用;
- **下一步**:对比站内 [Worktree 与 Agent Teams](claude-worktree-teams.md)(worktree 隔离机制同源)、[源码解析](claude-code-harness-analysis.md)(任务系统章节),理解"把协调逻辑从模型上下文迁移到确定性运行时"的通用范式。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/Luw5nGwHx_oXipIlFIW2ew
- 站内:[Claude Code 深度解析子主题](index.md)、[Claude Code Worktree 与 Agent Teams](claude-worktree-teams.md)、[Claude Code 源码解析](claude-code-harness-analysis.md)(任务/团队章节)、[Git Worktree 多 Agent 并行](../experience/git-worktree-parallel-agents.md)(worktree 隔离基础)、[Agent 架构全景](../../03-agents/agent-architecture-panorama.md)(多 Agent 编排模式对照)
