# 原始资料:用 Claude 做 Graph Engineering:从 0 到 graph 架构师的 14 步路线图(完整课程)

> 来源:微信公众号(转载自 X,作者:0xCodez);原文:https://x.com/0xCodez/status/2079165300625330317
> 原文链接:https://mp.weixin.qq.com/s/MhcPo5RMdg-alL0bZplinQ
> 抓取日期:2026-08-09;状态:已整理为正式文章 docs/07-agent-coding/experience/graph-engineering-14-steps.md(Agent 使用经验:Graph Engineering 14 步)

---

老习惯了，先打个预防针，英文好的建议自己看原文：https://x.com/0xCodez/status/2079165300625330317

大多数人试着搭建多步 agent 时，最后都做成了一条直线：步骤一、步骤二、步骤三——每一步都礼貌地等上一步做完才开始。
十个人里有九个会发现：这些步骤里有一半根本不需要等待。
它们不路由（route），不分支（branch），不并行（parallelize）。它们只是排队——一个大脑（head）、一个上下文（context）、一次只做一件事——直到上下文窗口被填满，智能体也忘了自己原本在做什么。
这套 14 步路线图，就是把那条单文件直线，变成一张图（graph）：一张能在整支智能体集群（fleet）中扇出（fan out）、自我验证发现、并收敛到一个单个智能体永远无法承载的结果的graph。

这里有一个没人明说的思维转变：提示词（Prompt）是一句话。循环（Loop）是一个环。执行框架（Harness）是智能体立足的地板。
但工作本身的形状——什么先运行、什么可以同时运行、什么必须等待其他一切——那个形状是一张图。节点（Node）负责思考，边（Edge）负责传递结果。
Claude Code 已经推出了直接构建这些图的工具：动态工作流（Dynamic Workflows）。
Claude 会写一段纯 JavaScript 编排脚本，然后生成一支协同的子智能体（subagent）集群去执行它——而这种协调本身不消耗任何模型 token，因为它是代码，不是对话。
  01 Node 是任务，Edge 是流动的东西
一张 graph 只有两样东西，把它们分清，大半困惑就消失了。Node 是一个工作单元——一个 agent、一份有边界的 job、一份 input 进、一份 output 出。
Edge 是依赖关系：它说的是「这个 node 的 output 喂给那个 node 的 input」。仅此而已。

常见的错误是把"然后"（and then）当作edge。"Summarize the file and then tell me the weather（总结这个文件，然后告诉我天气）"这两者之间没有edge——天气并不消费那份摘要。
那只是两个互不连接的 node，被线性脚本硬串在一起。只有当数据真正跨过去时，edge 才存在。
学会对 agent 里每一个「然后」发问：下一步会不会读上一步的 output？如果不会，就没有 edge，等待就是浪费。

Draw it as boxes and arrows. A box is an agent() call.An arrow is a variable passed from one call’s return into another’sprompt. If you can’t draw the arrow - if no variable crosses - the twoboxes are independent, and independence is the thing you’ll exploitfor the rest of this course.
// 把它画成方框和箭头。一个方框就是一次 agent() 调用。// 一个箭头就是从一次调用的返回值传入另一次调用提示词的变量。// 如果你画不出箭头——如果没有变量跨越——那这两个方框就是独立的，// 而"独立性"正是本课程后续内容中你要利用的核心。
  02 你的线性脚本，是一张退化的 graph
当你把 agent 写成「先做 A，再做 B，再做 C，再做 D」，你其实已经画了一张 graph——一条没有分支的单链。每个 node 恰好只有一条 edge 进、一条 edge 出。
它能正确跑。但它也跑得慢、且脆弱：因为链没有冗余——C 卡住，D 永远不会发生，A 的工作也被困在上游无处可去。

Graph engineering 的第一项真正技能，是重画这条链。拿你的线性 agent，对每一条箭头问 Step 1 那个问题。
多数链里会有两三条箭头根本不携带数据——只是你碰巧按那个顺序打字而已。
剪掉那些箭头，链就会塌成更宽的结构：几个可以同时跑的独立 node，共同喂给一个需要它们全部结果的 node。
  03 给每个 node 一份 contract
一个你无法推理的node，就是一个你无法并行化的node（节点） 。解决办法是"契约（contract）"：有边界的输入、有边界的输出、只做一件事。
Input 是 node 会读的一切——必须显式传入，绝不假设来自某个共享的上下文窗口。输出是一种确定的结构，最好经过校验，这样下一个节点就能直接消费，而不用去猜。

在工作流（workflow）里，这份contract是通过 schema强制执行的。当你给 Claude 的 agent() 调用配上一个 JSON schema 时，Claude 生成的子智能体就被强制返回经过校验的结构化数据——校验发生在工具调用（tool-call）层，所以一旦不匹配，Claude 会重试，而不是把一段自由文本甩给你，让你自己去解析、去祈祷。
这就是「Claude 能接进 graph 的 node」和「只有人类读 output 才管用的 node」之间的差别。

// 一个有真正contract的节点：输入有界、输出经校验、只做一件事。const ITEM = {type: 'object', additionalProperties: false,properties: {title: { type: 'string' },url: { type: 'string' },impact: { type: 'string', enum: ['high', 'medium', 'low'] },},required: ['title', 'url', 'impact'],};const result = await agent(source.prompt, {label: research:${source.key},schema: ITEM, // forces validated structured outputagentType: 'general-purpose',});// result 现在是下一个节点可以信任的结构 —— 而不是自由文本。
  04 把 edge 当作 data contract
Edge 不只是「B 在 A 之后」。它是关于什么会跨过去的承诺：A 产出这个 shape，B 被设计成消费这个 shape。当你用数据而不是顺序来命名 edge 时，两件事会立刻变容易。

你能一眼看出 edge 是否真实（数据是否真的在流动？）；只要 shape 成立，你就能替换任一端的 node 而不弄坏整张 graph。
在实践中，edge 活在普通 JavaScript 里。扇出（fan-out）与综合（synthesis）之间的归并步骤——拍平（flatten）、去重（dedupe）、过滤（filter）——只是对 node 返回的 shape 做运算的代码。
这是图式思维的一个隐性红利：人们烧掉大量模型 token 干的事，其实很多只是 edge——而 edge 是免费的。

The temptation is to spawn an agent to “combine the results.” Resistit. If combining means flatten-and-dedupe, that’s results.flatMap(...)and a Set — deterministic, instant, zero tokens. Save agents forjudgment, not for plumbing. A graph where every edge is an agent is agraph paying rent on its own wiring.
// 诱惑在于派生一个智能体来"合并结果"。请抵制这种诱惑。// 如果合并只是扁平化加去重，那就是 results.flatMap(...) 加一个 Set// —— 确定性的、瞬时的、零 token。把智能体留给需要判断力的事，// 而不是管道工程。一张每条边都是智能体的图，// 是在为自己的接线付租金。。
  05 用 parallel() 做 Fan out
这是能让一切物有所值的关键动作。当你有 N 个独立节点——N 个需要检查的信息源、N 个需要审查的文件、N 条需要审计的路由——你不应该把它们串成链。
你应该告诉 Claude 把它们Fan out并同时运行。在工作流中，这就是 parallel()：Claude 接收一个 thunk 数组，为每个 thunk 生成一个子智能体，全部并发执行，然后把结果数组返还给你。

两个细节让它足够稳健。第一，parallel() 是一个屏障（barrier）——它会等待所有 thunk 完成才返回，这样下一阶段看到的才是完整的结果集合。第二，抛出异常的 thunk 会被解析为 null，而不是让整个批次都失败，所以一个不稳定的智能体不会拖垮整次运行。
务必对结果执行 .filter(Boolean)。并发度大致以你的核心数为上限，超出的部分会排队执行，所以即使你传入上百个 thunk，它们最终都会完成——只是每次只跑一小批。

phase('Research');// 九个信息源，九个智能体，同时运行.const raw = await parallel(SOURCES.map((s) => () =>agent(s.prompt, {label: research:${s.key},phase: 'Research',schema: ITEM_SCHEMA, // 每个节点返回经校验的 JSONagentType: 'general-purpose',}),),);const collected = raw.filter(Boolean);  // 丢弃失败智能体产生的 null 
Fan-out 存在于 Claude 编写的代码中，而不是模型对话里。Claude 自己的上下文从不需要同时容纳九个信息源——每个子智能体携带自己的上下文，只有最终答案会返回。
这正是让 Claude 能把工作流扩展到数十甚至数百个子智能体而不淹没会话的原因。编排层消耗零 token，因为它不是 Claude 的又一轮思考。
  06 在 barrier 处 Fan in
Fan-out 只有在有东西把结果收拢时才有用。Fan-in 就是那些 edge 汇合的 node——一个 agent（或一段代码）一次性看到所有上游结果，并做需要「完整集合」才能做的事：跨 source dedupe、按 impact 排序、总数为空就 early-exit。这是 barrier 唯一值得付出 wall-clock 成本的地方。

让 graph 保持高效的规则：只有当某阶段真的需要把先前所有结果凑在一起时，才用 barrier。要跨所有 source 做 dedupe？用 barrier——才是正解。

// 这条edge：纯 JS，无智能体，零 token。const flat = collected.flatMap((c) => c.items);log(Collected ${flat.length} items);phase('Curate');// 屏障节点：需要"完整集合"来去重 + 排序。const curated = await agent(Dedupe and rank these by impact:\n${JSON.stringify(flat)},{ phase: 'Curate', schema: CURATED_SCHEMA },);
只是 flatten 一个 list？那是 edge，直接内联处理就好。判断的准则很简单也很残酷：如果你写出了 parallel → transform → parallel，而中间那个 transform 并不存在跨条目依赖，那你本该用流水线（pipeline），完全跳过这道屏障（barrier）。
  07 菱形拓扑：拆分 → 处理 → 归并
把 fan-out 和 fan-in 合在一起，就得到每一张严肃智能体图的主力拓扑：菱形（Diamond）
一个节点拆分任务，多个节点并行处理，一个节点归并结果。这正是市场扫描、依赖审计、代码审查、研究报告背后的形状——换掉信息源和提示词，同一套骨架依然适用。

这个规范形式有一个值得牢记的名字：扇出（fan-out ） → 归约（reduce） → 综合（synthesize）。扇出（fan-out ）以获取广度，用纯代码归约来压缩，用最后一个agent综合来撰写答案。
一旦你看懂了这个菱形，你就不会再问"如何让我的智能体做更多步骤"，而是开始问"哪里拆分、哪里合并"——这才是真正能扩展规模的问题。
  08 用条件语句在运行时路由edge
不是所有graph都是固定的。有时该走哪条dege，取决于某个节点发现了什么。路由（router）节点检查一个结果，并决定哪条下游路径被触发——先对工单分类，再分支到对应的处理器；先检查 diff 的大小，再决定是做一次快速审查，还是启动一次完整审计。
在工作流中，这只是对某个节点已校验输出的一次 JavaScript if 或 switch 判断，因为控制流本身就存在于在代码里。

这正是确定性（determinism）成为优势而非局限的地方。路由器的判断可以由 Claude 驱动（一个子智能体做分类），但路由本身是 Claude 写下的代码——因此对同一个分类结果，它每次都以相同方式运行。
你在节点上获得 Claude 的判断力，在edge上获得脚本的可靠性。不会出现"Claude 突然决定跳过审计"这种意外的涌现行为——因为要跳过，必须先被写进graph里，而它没有被写进去。

// 路由器节点：智能体做分类，代码选edge。const { severity } = await agent(Classify this diff's risk:\n${diff},{ schema: { type: 'object',properties: { severity: { enum: ['low', 'high'] } },required: ['severity'] } },);let review;if (severity === 'high') { // 重路径：全面并行审计  review = await parallel(FILES.map((f) => () => agent(Audit ${f})));} else {// 轻路径：一次快速评审  review = await agent(Quick review of ${diff});}
  09 在edge放置一个验证器（verifier）
一张graph真正的杠杆，不在于更多的智能体——而在于你能围绕它们构建出的、用来产生信心（confidence）的结构。
验证器节点（verifier node）坐在结果被允许流向下游之前的那条边上，它唯一的工作就是尝试推翻这个发现。如果发现挺过去了，就通过；如果没有，它永远到达不了最终答案。

有三种模式值得你随手掌握。
对抗式验证（Adversarial verify）：对每一个发现，生成 N 个相互独立的"怀疑者"，专门被提示去反驳它；只有当多数怀疑者仍未能推翻它时才保留。

多视角验证（Perspective-diverse verify）：给每个验证者一个不同的视角——正确性、安全性、能否复现——因为多样性能捕捉到 N 个相同检查永远抓不住的失败模式。

评审团（Judge panel）：从不同角度生成 N 次尝试，用并行的评委给它们打分，从获胜者中综合结果，同时嫁接其他优秀方案里最好的部分。

正是这种模式，让一支真实团队成功把 Bun 运行时移植了过去，并在循环中内建了对抗式代码审查。
  10 隔离节点，避免一次失败污染整张graph
在一条链里，失败会级联传播——C 挂了，D 永远不会运行，整个流程停摆。而在一张graph里，失败应该被限制在其所在的节点内。
这一点在某种程度上已经实现了：parallel() 内部抛出异常的 thunk 会被解析为 null，所以八个正常的智能体依然会返回结果，一个坏的会掉线。你的 .filter(Boolean) 就是那道containment（隔离防线）。设计每一个fan-in节点时，都要能容忍缺失的输入，而不是假设集合总是完整的。

更隐蔽的失败是节点之间互相踩脚。当多个智能体并行写文件时，它们可能会发生冲突。解决办法是隔离："worktree"——每个智能体在自己的 git worktree 中运行，在一个沙盒里完成工作，然后干净地合并回去。只有当节点确实需要并行写入时才使用它——它是那一种确实需要它的拓扑的安全带，而不是每次运行都要默认缴纳的税。
  11 添加一个循环——但要确保它能收敛
有时候，任务有多大，只有做起来才知道：未知规模的发现型任务、一场 bug 排查，找到一个 bug 却牵出另外三个。这就需要一个循环（cycle）——一条回到早期节点的受控edge。
危险显而易见：不收敛的循环就是一个无限循环，它会不断派生智能体，直到烧光你的Token预算。

能够收敛的模式叫做"循环直到枯竭（loop-until-dry）"：持续生成"探测者"节点，直到连续 K 轮什么新东西都没发现，然后停止。真正决定成败的一个细节——也是几乎所有人第一次都会犯的错误——是你拿什么去重。
要针对所有见过的（seen）去重，而不是只针对已确认的（confirmed）结果去重。否则被否决的发现会在每一轮重新出现，循环永远跑不干，你就造出了一台不断付费重新发现同样死胡同的机器。

const seen = new Set(); const confirmed = []; let dry = 0;while (dry < 2) { // 连续 2 轮空手而归即停止 const found = (await parallel( FINDERS.map((f) => () => agent(f.prompt, { schema: BUGS })) )).filter(Boolean).flatMap((r) => r.bugs); const fresh = found.filter((b) => !seen.has(key(b))); if (!fresh.length) { dry++; continue; } // 无新发现 → 趋向枯竭 dry = 0; fresh.forEach((b) => seen.add(key(b))); // 对 SEEN 去重，而非 confirmed // 每个新发现在计入前，先经多视角验证 const judged = await parallel(fresh.map((b) => () => parallel(['correctness', 'security', 'repro'].map((lens) => () => agent(`Judge ”${b.desc}” via ${lens} — real?`, { schema: VERDICT }))) .then((v) => ({ b, real: v.filter(Boolean).filter((x) => x.real).length >= 2 })))); confirmed.push(...judged.filter((v) => v.real).map((v) => v.b));}
  12 在各节点之间分层调配模型
不是每个节点都需要你最好的模型。graph让这一点变得一目了然，而单个智能体永远做不到：有些节点有界且重复（提取这个字段、给这个工单分类），有些则承载真正的判断（综合报告、裁定发现）。
把那些无聊的节点跑在更便宜的模型上，把昂贵的 token 花在真正需要判断力的地方。

在工作流中，Claude 派生的每个子智能体默认继承你的会话模型，除非脚本覆盖它——所以一次大型运行默认全按你的会话模型档位计费。单次 agent() 调用上的 model 选项，可以告诉 Claude 把那一个节点路由到别的模型。
大型运行前先检查 /model，然后让 Claude 把 fan-out 里重复性 node 降到更便宜的 model，合并节点保持高档。这是那根杠杆：不改 graph 形状，就能把吃 token 的 graph 从昂贵变成划算。
  13 拓扑结构决定你的成本与延迟
Graph 的形状不是装饰——它是影响实际运行时间的最大杠杆。绊倒所有人的选择题是：parallel() 还是 pipeline()。parallel() 的屏障会让所有任务等待最慢的节点完成，下一阶段才能开始
而 pipeline() 让每个条目独立地流经所有阶段，没有屏障——条目 A 可以在第 3 阶段时，条目 B 还在第 1 阶段。快的条目提前完成，而不是在慢条目后面空等。

默认使用 pipeline()。只有当一个阶段确实需要一次性拿到所有先前结果时才用屏障——例如跨集合去重、根据总数提前退出、或者一个需要与"其他发现"逐一比对的提示词。"代码更干净"和"各阶段感觉是分开的"都不是理由；屏障造成的延迟是真实的、可测量的、被浪费掉的时间。分开（separate）不等于同步（synchronized）。
  14. 让 Claude 自己画 graph——self-routing
最后一招：对那些你无法提前规划的活，别再手动画 graph。
借助动态工作流（dynamic workflows），你只需描述目标，Claude 会自己写出编排脚本——拆解任务、选择fan-out方式、生成一支协同的子智能体集群、并综合出最终结果。你得到的是一张为这次运行量身定制的图，而不是一张你只能寄望"刚好适用"的固定图。

有三种入口。在提示词里说出"workflow"这个词，Claude 就会为该任务写一个工作流。运行已保存或内置的工作流—— /deep-research 就是一张已在生产环境中交付的真实的图：确定范围 → 并行搜索 → 抓取 → 对抗式验证 → 综合，正是本课程讲的那副骨架。
或者开启 ultracode，让 Claude 为会话中每一项重大任务都规划一个工作流。当某次运行效果不错时，按下 s 键即可把这段脚本保存进 .claude/workflows/ 目录——纳入版本控制、可按名字重新运行，成为任何克隆了这个仓库的人都能启动的一张graph。

› Run a workflow to audit every route under src/routes/ for missing auth. Spawn one agent per route file, then verify each finding before reporting. ● Claude wrote an orchestration script · launching in background… /workflows — auth-audit · running ✓ Scope 1/1 2.1k tok · 4s ✓ Fan-out 18/18 one agent per route file ◯ Verify 11/18 3-vote skeptics per finding… ○ Synthesize 0/1 waiting on verify session stays responsive — keep working while the fleet runs --- › 运行一个工作流，审计 src/routes/ 下所有路由的鉴权缺失问题。每个路由文件派生一个智能体，每个发现上报前先经过验证。● Claude 已编写编排脚本 · 后台启动中…/workflows — auth-audit · running✓ Scope 1/1 2.1k tok · 4s✓ Fan-out 18/18 每个路由文件一个智能体◯ Verify 11/18 每个发现由 3 票怀疑者裁决…○ Synthesize 0/1 等待验证完成会话保持响应 —— 舰队运行时你可以继续工作
本周就可以和 Claude 一起构建的六张图

全路由安全扫描。Claude 为每个路由文件派生一个子agent，各自排查缺失的鉴权检查，再由验证器通道确认每个发现后才进入报告。这是任何单一上下文都无法承载的广度。
用 /deep-research 生成带引用的报告。一张已随 Claude Code 交付的graph。Claude 把你的问题分解为不同角度，运行并行搜索，去重信息源，然后用三票怀疑者对每条论断做对抗式验证，最后才动笔。
逐文件移植模块。Bun 的天花板，缩放到你的仓库。Claude 把翻译工作fan-out到各个文件，用测试套件作为每个文件的关卡（gate），把失败的循环回炉——对抗式评审能拦下单次遍历会带bug上线的东西。
对 diff 的对抗式评审。Claude 按 diff 大小路由：小改动一次快速评审，大改动触发全面并行审计，评审者各持不同视角——正确性、安全性、性能——最后由评审团综合。
定时生态扫描。保存一次，永远复用。Claude 并行检查多个信息源——发布、博客、讨论区——在屏障处按影响力排序，写出摘要。版本控制在 .claude/workflows/ 中，按名称即可启动。
未知规模的探索。你不知道有多少个 Bug。Claude 并行运行发现者，把每个新发现与所有已见过的去重，验证存活者，持续循环直到连续两轮一无所获——然后停止。

  结语:
Prompter 问问题。Architect 画 graph。
线性agent从来不是天花板——它只是第一种形状，是每个人最先想到的那种，因为它符合我们打字的方式。一行、一个大脑、一次只做一件事。
一旦你能看清node 和 edge，你就会停止要求智能体"做更多步骤"，转而开始要求这张graph"变得更宽"：在工作彼此独立的地方fan-out，在需要信任度的地方在边上设卡验证，在不需要判断力的地方分层调配模型。
多数人会继续把步骤排成一条线。学会画 graph 的人，会开一支集群——并且再也感觉不到其余人头顶那道天花板。