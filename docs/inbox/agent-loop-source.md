# 原始资料:Loop engineering:loop 中文入门指南

> 来源:微信公众号「晓码的创造栈」,翻译整理自 Anthropic 官方博客《Getting started with loops》(作者:Delba de Oliveira、Michael Segner)
> 原文链接:https://mp.weixin.qq.com/s/FyBQNXNeNAqq16fbMliB8Q;英文原文:https://claude.com/blog/getting-started-with-loops
> 抓取日期:2026-08-09;状态:双角度沉淀——四类 loop 概念融入 docs/03-agents/agent-intro.md(Agentic Loop 小节),设计纪律融入 docs/03-agents/ai-infra-layering.md(Loop Engineering 小节)

---

本文翻译整理自 Anthropic 官方博客《Getting started with loops》。原作者：Delba de Oliveira、Michael Segner。专业术语保留英文，文末附原文链接。

  如今，越来越多的人讨论loop engineering：不再只给 coding agent 写一次 prompt，而是开始“设计 loop”。如果你在 X 上试图弄清 loop 究竟是什么，会看到很多不同的答案。

  在 Claude Code 团队，我们把loop 定义为：agent 重复执行工作 cycle，直到满足 stop condition。不同类型的 loop，主要由四件事区分：

    如何触发
如何停止
使用哪一种 Claude Code primitive
最适合哪一类任务

  下面将介绍主要的 loop 类型、每种类型的适用时机，以及如何在管理 token usage 的同时保持代码质量。并不是所有任务都需要复杂的 loop；应当从最简单的方案开始，再有选择地使用这些模式。

  Turn-based loop

  图片来源：Anthropic 官方博客

    触发方式：用户输入一个 prompt。
停止条件：Claude 判断任务已经完成，或者需要补充 context。
最适合：不属于固定流程或固定 schedule 的短任务。
控制 usage：编写更具体的 prompt，并通过 skill 改进验证，减少 turn 数。

  你发出的每一条 prompt 都会启动一个 manual loop，由你逐个 turn 进行指挥。Claude 收集 context、采取行动、检查自己的工作、在必要时重复，然后作出回应。我们把它称为agentic loop。

  例如，让 Claude 创建一个点赞按钮。它会读取代码、完成修改、运行测试，再交回一个它认为能够正常工作的结果。随后你手动检查，再写下一条 prompt。

  你可以把手动验证步骤编码进SKILL.md，从而改进 verification step，让 Claude 能够端到端地检查更多自己的工作。其中应当包含能让 Claude 看到、衡量或与结果交互的工具或 connector。检查越量化，Claude 就越容易完成 self-verification。

  例如，你可以在 SKILL.md 中写入：

  ---
name: verify-frontend-change
description: 在宣布 UI 变更完成之前，对其进行端到端验证。
---

# 验证前端变更
不要仅因为代码修改成功，就报告 UI 变更已经完成。请像 human reviewer 一样验证：

1. 启动 dev server，并在 browser 中打开修改后的页面。
2. 直接与新的 control 交互，确认预期 state change，并截取操作前后的 screenshot。
3. 检查 browser console：不得出现新的 error 或 warning。
4. 使用 Chrome DevTools MCP 运行 performance trace，并审查 Core Web Vitals。

如果任一步骤失败，修复问题并从第 1 步重新执行。

  Goal-based loop（/goal）

  图片来源：Anthropic 官方博客

    触发方式：实时输入一个 manual prompt。
停止条件：goal 达成，或者达到最大 turn 数。
最适合：具有可验证 exit criteria 的任务。
控制 usage：设置明确的完成标准和显式 turn 上限。

  有时一个 turn 并不够，尤其是在更复杂的任务中。agent 能够迭代时，通常会表现得更好。通过/goal定义“完成”是什么样子，你可以让 Claude 持续迭代更长时间。

  一旦成功标准明确，Claude 就不必自己判断什么算“足够好”，也不会过早结束 loop。每当 Claude 尝试停止时，一个evaluator model会检查你设定的条件；如果尚未满足，就让 Claude 返回继续工作，直到 goal 达成，或者达到你定义的 turn 数。

  这就是 deterministic criteria 特别有效的原因，例如已通过的测试数量，或者是否越过某个分数阈值。

  /goal 将首页的 Lighthouse score 提升到 90 或以上，最多尝试 5 次。

  Time-based loop（/loop 与 /schedule）

    触发方式：指定的时间间隔。
停止条件：你取消它，或者工作已经完成。
最适合：重复性工作，或者与外部 environment / system 交互。
控制 usage：设置更长的间隔，或者根据 event 而不是时间作出响应。

  有些 agentic 工作会重复发生：任务本身不变，只有输入变化。例如，每天早晨汇总 Slack 消息。另一些工作依赖外部 system；一种简单的连接方式，是定期检查并对变化作出反应。例如，一个可能收到 code review，或者 CI 失败的 PR。

  对于这类情况，可以使用/loop让 Claude 按时间间隔重新运行一个 prompt。例如：

  /loop 5m 检查我的 PR，处理 review 意见，并修复失败的 CI

  /loop在你的电脑上运行，因此电脑关机后它就会停止。你可以使用/schedule创建 routine，把 loop 移到 Cloud 中运行。

  Proactive loop

  图片来源：Anthropic 官方博客

    触发方式：由 event 或 schedule 触发，不需要人实时参与。
停止条件：每个 task 在自身 goal 达成时退出；routine 持续运行直到关闭。
最适合：持续流入且定义清晰的工作。
控制 usage：把 routine 路由给更小、更快的 model。

  前面介绍的 primitives，再加上 Claude Code 的其他能力，例如auto mode与dynamic workflows（research preview），可以组合成处理 long-running work 的 loop。

  例如，为了处理持续收到的 feedback，你可以：

    01使用/schedule运行一个 routine，定期检查新的 report。
02使用/goal定义“完成”的标准，并通过 skills 记录验证方法。
03使用dynamic workflows编排多个 agents，分别完成 report triage、修复和 review。
04使用auto mode，让 routine 不必停下来询问权限。

  /schedule 每小时：检查 #project-feedback 中的 bug report。
/goal：在本次运行发现的每一份 report 都完成 triage、处理并得到回复之前，不要停止。
修复 bug 时，使用 workflow 在并行 worktrees 中探索三种方案，
并让一个 judge agent 对这些方案进行 adversarial review。

  保持代码质量

  loop 输出的质量，取决于它周围的 system。设计这个 system 时：

    保持 codebase 本身整洁
Claude 会遵循已经存在的模式和惯例。
让 Claude 能够验证自己的工作
通过 skills 编码你和团队对“高质量”的定义。
让 docs 容易获取
framework 与 library 的 docs 包含最新 best practices。
使用第二个 agent 做 code review
拥有全新 context 的 reviewer 偏见更少。

  当某一次结果没有达到标准时，不要只修复这一个问题。应当尝试把经验编码进 system，从而改善未来的所有 iteration。

  管理 token usage

  为了管理 token usage，loop 应当拥有清晰的边界：

    选择正确的 primitive 和 model
小任务不需要多个 agents 或复杂 loop。
定义成功标准和停止条件
明确说明“完成”是什么样子。
大规模运行前先试点
先在较小的工作切片上评估 usage。
对 deterministic work 使用 script
运行 script 比每次重新推理步骤更便宜。
不要以超过需要的频率运行 routine
让运行间隔匹配被监控对象的实际变化频率。
检查 usage
使用 /usage、/goal 与 /workflows 查看消耗。

  你对model与effort level的选择，是影响一个 loop 成本最大的杠杆之一。

  开始实践

    Turn-based
交出检查，适合探索或决策，使用 verification skills。

Goal-based
交出停止条件，适合目标清晰的任务，使用 /goal。

Time-based
交出触发器，适合按 schedule 发生的工作，使用 /loop 与 /schedule。

Proactive
交出 prompt，适合重复且定义清晰的工作，并结合 dynamic workflows。

  要开始使用 loop，可以先观察你已经在做的工作。挑出一个“你自己是 bottleneck”的任务，然后问：其中哪一部分可以交出去？你能否写出 verification check？goal 是否足够清晰？工作是否按 schedule 到来？

  有了想法后，就运行这个 loop，观察结果，例如它在哪里卡住、在哪里做得过头，然后持续 iteration，不必害怕重新调整。

  延伸阅读

  parallel agents
https://code.claude.com/docs/en/agents
loop 与 goal
https://code.claude.com/docs/en/goal
schedule 与 routines
https://code.claude.com/docs/en/routines
dynamic workflows
https://code.claude.com/docs/en/workflows

    原作者：Delba de Oliveira、Michael Segner

    原文：https://claude.com/blog/getting-started-with-loops