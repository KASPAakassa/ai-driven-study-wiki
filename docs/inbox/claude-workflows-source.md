# 原始资料:Claude Code /workflow 深度解析:多智能体编排的底层实现

> 来源:微信公众号「AI觉醒观测者」;原文链接:https://mp.weixin.qq.com/s/Luw5nGwHx_oXipIlFIW2ew
> 抓取日期:2026-08-09;状态:已整理为 docs/07-agent-coding/claude-code-deep-dive/claude-workflows.md
> 性质:Dynamic Workflows(ultracode 关键词)技术深度解析:触发方式、JS 运行时架构、核心 API(agent/pipeline/parallel/workflow)、确定性执行与断点续跑、对抗性验证等编排模式

---

一个 JavaScript 脚本，让 Claude 同时调度几十乃至上百个 Subagent 并行工作——这就是 Claude Code 在 2026 年 5 月随 Opus 4.8 一同推出的 Dynamic Workflows 功能。本文从使用场景出发，深入拆解其技术架构、核心 API 设计、确定性执行机制以及对抗性验证等工程细节。

一、为什么需要 Workflow？
在 Claude Code 的日常使用中，你大概经历过这样的困境：
你想让 Claude 全面扫描一个有几百个文件的大型代码库，找出所有潜在的 auth 漏洞——但单次对话的上下文窗口装不下整个代码库；你让 Claude 逐步扫描，但"计划"本身就躺在 Claude 的记忆里，做完第一个文件，Claude 对第二个文件的上下文已经被挤占了大半；你试着用 Agent 工具分出几个并行任务，但 Claude 只能凭感觉决定"下一步做什么"，没有可以重跑的确定性执行计划。
这就是 Workflow 要解决的核心问题：把"计划"从 Claude 的上下文窗口里挪出去，放进一段可运行、可重跑的 JavaScript 代码里。
与此同时，这段代码也承担了另一件重要的事：把质量保障模式固化成可复现的流程——比如让多个独立 Agent 互相对抗性审查对方的发现，而不是靠单次 Pass 的 Claude 自己判断自己对不对。
二、Workflow 是什么？与其他方案怎么选？
Claude Code 提供了四种多步骤任务执行方式，它们的本质区别在于："谁来持有计划"。
方案
计划持有者
中间结果存在哪
可重复性
规模
SubagentsClaude，逐轮决策
Claude 上下文窗口
每次重跑策略不同
每轮几个
SkillsClaude，跟随 Prompt
Claude 上下文窗口
同 Subagents
同 Subagents
Agent Teams主导 Agent，逐轮分配
共享任务列表
团队定义可复用
少量长期 peers
WorkflowsJavaScript 脚本
脚本变量
脚本本身可重跑
几十到上百个 agentWorkflow 把"哪个 Agent 做什么、做完了做什么"这条链条编进了代码的循环和分支里。Claude 的上下文里只剩最终结果，不再承载所有中间状态。这让超大规模的并行执行成为可能——同时也让执行过程变得确定性可追踪。
三、如何触发 Workflow？
3.1 关键词触发（最常用）
在提示词里加入 ultracode 关键词，Claude Code 会识别它，让 Claude 为当前任务编写一个 Workflow 脚本并执行：
ultracode: 扫描 src/routes/ 下所有 API 路由，找出缺少 auth 检查的接口
Claude Code 会在输入框里高亮显示这个关键词（紫色高亮）。如果你不想触发，按 Option+W（macOS）或 Alt+W（Windows/Linux）取消。也可以用自然语言，比如"用 workflow 来做"、"请用 workflow 执行这个任务"。
版本注意：Dynamic Workflows 于 2026-05-28 随 v2.1.154 发布，彼时触发关键词是 workflow。2026-06-02 的 v2.1.160 版本将其改为 ultracode（同时原词 workflow 不再触发），自然语言方式在两个版本中均有效。如果你用的是 v2.1.154–v2.1.159，请用 workflow 关键词。

3.2 全局 ultracode 模式
/effort ultracode
开启后，当前 session 里每个实质性任务都会自动规划成 Workflow。一个需求可能触发多个串联 Workflow：先理解代码、再改动、再验证。代价是消耗 token 会大幅增加，所以用完这次任务建议用 /effort high 退回。
3.3 内置 /deep-research 命令
这是 Claude Code 自带的第一个 Workflow 命令，也是最直观的上手方式：
/deep-research Node.js v20 到 v22 权限模型发生了哪些变化？
执行后，它会在后台对问题展开多角度搜索，对各来源交叉核验，最后返回一份带引用的综合报告。你的主对话窗口在这期间一直保持响应。
3.4 保存和复用
如果某次 Workflow 的效果不错，可以把它保存成命令：运行 /workflows，选中该 run，按 s 保存。
保存到 .claude/workflows/：随项目代码库共享给所有人

保存到 ~/.claude/workflows/：只对自己可用，适用于所有项目

保存后，它和 /deep-research 一样出现在 / 自动补全里。
四、底层实现：JavaScript 运行时架构

Dynamic Workflow 的核心设计决策是：把编排逻辑从"Claude 的输出"迁移到"独立 JavaScript 运行时"。
Claude 收到任务后会编写一段 JS 脚本，然后由运行时在后台独立进程中执行。这个进程与你的对话上下文完全隔离——中间结果存储在脚本变量里，不进入 Claude 的上下文窗口。
每次运行的脚本都会持久化到 ~/.claude/projects/ 下的对应 session 目录，你可以直接打开查看 Claude 写的编排逻辑，也可以手动编辑后让 Claude 重新执行。
运行时有几个关键约束：
约束
原因
最多 16 个 Agent 并发（受 CPU 核心数限制）
控制本地资源消耗
每次运行最多 1000 个 Agent
防止无限循环失控
脚本中禁止使用 Date.now() / Math.random() / new Date()（无参数）
保证确定性，支持断点续跑
Subagent 始终在 acceptEdits 模式下运行
文件编辑自动批准，减少中断
脚本是纯 JavaScript（不支持 TypeScript 转译）
简化运行时，类型注解会报错
五、核心 API 深度解析
一个 Workflow 脚本的最小结构如下：
export const meta = {
  name: 'auth-audit',
  description: '扫描所有 API 路由的 auth 缺失问题',
  phases: [
    { title: '扫描' },
    { title: '验证' },
  ],
}

// 脚本主体在异步上下文中执行，可直接 await
phase('扫描')
const findings = await agent('扫描 src/routes/ 找出 auth 漏洞', {
  schema: FINDINGS_SCHEMA,
  label: 'auth-scanner'
})
meta 必须是纯字面量——不能有变量、函数调用、模板字符串或 spread。phases 里的标题与脚本中 phase() 调用的标题精确匹配时，Agent 会被归入对应的进度分组。

5.1 agent()：基础单元
const result = await agent(prompt, {
  schema,      // JSON Schema → 启用结构化输出 + 自动重试
  label,       // /workflows 面板中的显示名称
  phase,       // 手动指定进度分组（在 pipeline/parallel 内防止状态竞争）
  model,       // 覆盖 session 模型（如用 haiku 做轻量任务）
  agentType,   // 使用自定义 subagent 类型
  isolation,   // 'worktree' → 在独立 git worktree 中运行（并行写文件时防冲突）
})
agent() 的返回值：
无 schema：返回 Agent 最终文本

有 schema：运行时强制 Agent 调用 StructuredOutput 工具，校验通过后返回 JS 对象；校验失败则自动重试，无需手动 parse JSON

Agent 出错或被用户跳过则返回 null，记得 .filter(Boolean) 过滤

5.2 pipeline() vs parallel()：最重要的设计选择
这是 Workflow 脚本里最容易踩坑的地方，官方文档明确建议：默认用 pipeline()，只有在下游真的需要全量结果时才用 parallel()。

pipeline(items, ...stages)：
无屏障，各 item 独立推进

Item A 完成第 1 阶段就立即进入第 2 阶段，不等 Item B/C

壁钟时间 = 最慢那条流水线，而非"各阶段最慢之和"

每个 stage 接收 (prevResult, originalItem, index)——用 originalItem 在后期阶段保留原始上下文

parallel(thunks[])：
有同步屏障，等所有 thunk 完成才返回

壁钟时间 = 最慢那个 thunk

快速 thunk 完成后只能等待

parallel() 正确使用的场景只有两种：
下游需要对全量结果去重 / 跨 item 比较

需要在整体结果为空时 early-exit（跳过后续全部阶段）

一个实际案例——多维度代码审查：
// ✅ 正确：用 pipeline，各维度独立推进
// bugs 维度完成 Review 就立即开始 Verify，不等 security/perf 维度
const DIMS = [
  { key: 'bugs', prompt: '找出所有逻辑 bug' },
  { key: 'security', prompt: '找出所有安全漏洞' },
  { key: 'perf', prompt: '找出性能瓶颈' }
]
const results = await pipeline(
  DIMS,
  d => agent(d.prompt, { label: `review:${d.key}`, phase: 'Review', schema: FINDINGS }),
  findings => parallel(findings.map(f => () =>
    agent(`对抗性验证：${f.title}`, { label: `verify:${f.file}`, phase: 'Verify', schema: VERDICT })
  ))
)
5.3 workflow()：嵌套调用
const report = await workflow('deep-research', { question: '...' })
// 或调用脚本文件
const result = await workflow({ scriptPath: '/path/to/script.js' }, args)
workflow() 让你在一个 Workflow 内调用另一个已保存的 Workflow，共享父级的并发上限、Agent 计数和 token 预算。只支持一层嵌套——子 Workflow 内再调用 workflow() 会报错。
六、三个关键机制深析
6.1 确定性执行与断点续跑
运行时会把每个 agent() 调用的结果记录到 Journal（执行日志）。如果 Workflow 中途暂停或失败，可以在同一 session 内续跑：
已完成的 agent() 调用直接从 Journal 返回缓存结果（毫秒级）

未完成的调用重新执行

相同脚本 + 相同 args → 100% 缓存命中

为了让 Journal 的缓存 key 保持一致，脚本必须是确定性的：同样的输入每次产生同样的调用序列。这就是为什么 Date.now()、Math.random()、无参数的 new Date() 在脚本中会直接抛出——它们会导致 key 不匹配，破坏 Journal 的缓存。带固定参数的 new Date('2026-01-01') 不受限制。
需要时间戳？通过 args 从外部传入：
// 调用时传入时间戳
// Workflow({ args: { timestamp: Date.now() } })
const ts = args.timestamp
注意：断点续跑只在当前 session 内有效。退出 Claude Code 后 Journal 丢失，下次启动会重跑整个 Workflow。
6.2 结构化输出与 Schema 验证
当你给 agent() 传入 schema 选项时，运行时会强制 Subagent 调用内置的 StructuredOutput 工具，在工具调用层面做 JSON Schema 校验，校验失败自动重试——这比让 Agent 返回自由文本再手动 parse 可靠得多。
const BUGS_SCHEMA = {
  type: 'object',
  properties: {
    bugs: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' },
          line: { type: 'number' },
          description: { type: 'string' },
          severity: { type: 'string', enum: ['low', 'medium', 'high'] }
        },
        required: ['file', 'line', 'description', 'severity']
      }
    }
  },
  required: ['bugs']
}

const result = await agent('找出这个函数中的所有 bug', { schema: BUGS_SCHEMA })
// result 直接是 JS 对象，result.bugs 是数组，无需 JSON.parse
6.3 Git Worktree 隔离
当多个 Agent 需要并行写文件时，直接在同一工作目录操作会产生冲突。isolation: 'worktree' 选项为每个 Agent 创建一个独立的 git worktree：
const results = await parallel(files.map(f => () =>
  agent(`重构 ${f}`, {
    isolation: 'worktree',  // 每个 agent 在独立 worktree 中运行
    label: `refactor:${f}`
  })
))
Worktree 有额外开销（约 200-500ms setup + 磁盘占用），因此只应在并行写文件会冲突时使用，只读操作不需要。如果 Agent 没有做任何改动，worktree 会被自动清理。
七、实用编排模式
7.1 对抗性验证：让 Agent 互相怼
这是 Workflow 相比单次 Pass 最核心的质量优势——让独立 Skeptic Agent 尝试反驳每个发现，多数票通过才算确认：
// 3 个 Skeptic Agent 尝试反驳，≥2 票"站不住脚"则丢弃
const votes = await parallel(
  Array.from({ length: 3 }, () => () =>
    agent(`尝试反驳这个 bug 报告：${finding.description}。默认倾向 refuted=true。`, {
      schema: VERDICT_SCHEMA
    })
  )
)
const survives = votes.filter(Boolean).filter(v => !v.refuted).length >= 2
7.2 Loop-Until-Dry：发现数量未知时的循环策略
当你不知道有多少 bug / issue 要找时，用计数循环（while count < N）会漏掉尾部；更稳健的模式是"连续 K 轮没有新发现才停止"：
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
注意：去重要对 seen（全部已见过的），而不仅是 confirmed（已验证通过的）——否则被 Skeptic 否决的发现会每轮重复出现，导致循环不收敛。
7.3 Token 预算控制
如果用户在提示里指定了 Token 上限（如 +500k），budget 全局变量可以让你动态调整循环深度：
while (budget.total && budget.remaining() > 50_000) {
  const result = await agent('发现更多问题', { schema: BUGS_SCHEMA })
  confirmed.push(...result.bugs)
  log(`已发现 ${confirmed.length} 个，剩余 ${Math.round(budget.remaining() / 1000)}k token`)
}
无 Token 上限时 budget.total 为 null，budget.remaining() 返回 Infinity——注意用 budget.total && 守卫，否则循环会一路跑到 1000 Agent 上限。
八、/workflows 监控界面
Workflow 在后台运行，不占用你的主对话窗口。随时用 /workflows 查看所有运行中和已完成的 Workflow：
进度界面按 phase 分组展示每个 Agent 的状态、token 消耗和耗时。主要快捷键：
键
功能
↑ / ↓
选择 phase 或 agent
Enter / →
展开查看 agent 的 prompt、工具调用和结果
p暂停 / 继续运行
x停止选中的 agent 或整个 workflow
r重启选中的运行中 agent
s将该 run 的脚本保存为命令
底部的任务面板也会显示一行进度摘要，按方向键下可以聚焦并展开，按 p 暂停整个 run。
九、何时用 Workflow，何时不用
适合用 Workflow 的场景：
全代码库 bug 扫描 / 安全审计，需要独立验证

大规模迁移（几百个文件，需要并行处理）

需要多角度交叉核验的研究任务

需要对抗性验证保证质量的关键工作

你希望把这个流程固化成可重复执行的脚本

不适合用 Workflow 的场景：
简单的一次性任务（改个 bug、解释一段代码）

需要中途和你频繁交互讨论的任务（Workflow 运行中无法接收用户输入）

你只是想并行跑几个 Subagent 而不需要确定性编排

成本提示：一次大型 Workflow 的 token 消耗可能是普通对话的数倍乃至数十倍。官方建议先在小范围（一个目录、一个具体问题）试跑，确认效果后再扩大到全量。
十、总结
Dynamic Workflows 代表了 Anthropic 对"如何让 Claude 处理超大规模任务"这个问题的系统性回答。
核心设计决策：把编排计划从模型的上下文窗口里移出去，放进一段确定性的 JavaScript 脚本，由独立运行时执行。这个决策带来了三件事：
规模：上下文窗口不再是并发瓶颈，几百个 Agent 并行成为可能

可重复性：脚本是代码，可以 diff、可以版本控制、可以重跑

质量模式：对抗性验证、多角度草稿、Loop-Until-Dry 等质量模式可以被固化进脚本，每次执行都走同一套保障流程

从架构角度看，pipeline() vs parallel() 的区别（无屏障流水线 vs 同步屏障）是日常写脚本最重要的判断点；schema 带来的结构化输出是让编排逻辑与 Agent 输出解耦的关键；Journal 机制让长时间运行的任务可以断点续跑而不从头来过。
随着 AI 工具越来越多地被用于大型代码库和复杂研究任务，这类"把协调逻辑从模型上下文迁移到确定性运行时"的设计思路，很可能会成为 AI 工程工具链的通用范式。

欢迎关注 AI观测者，持续追踪 LLM 工程实践与 Agent 系统设计前沿。