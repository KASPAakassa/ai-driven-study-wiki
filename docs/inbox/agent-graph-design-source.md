# 原始资料:Claude Graph Engineering:从线性 Agent 到图工作流架构师的 14 步路线

> 来源:微信公众号「山行AI」(整理自 0xCodez 原文);原文:https://x.com/0xCodez/status/2079165300625330317
> 原文链接:https://mp.weixin.qq.com/s/6xqI5LlOPM8_SQ6Emexz4w
> 抓取日期:2026-08-09;状态:已整理为正式文章 docs/03-agents/agent-graph-design.md(设计角度,与 07 使用经验篇互补)

---

前言

很多人第一次做多步 Agent，写出来的其实是一条直线：第一步、第二步、第三步，每一步都等上一件事结束。问题是，很多步骤根本不需要等。

它们不路由，不分支，不并行，只是在同一个上下文窗口里排队。等窗口越来越长，Agent 也开始忘记自己最初要做什么。

这篇内容讨论的是一个更硬的转变：不要把 Agent 设计成一串提示词，而是把工作设计成一张图。节点负责具体任务，边负责传递结果，代码负责调度。这样，一个单文件线性流程就可以变成能扇出、能验证、能合并的多 Agent 工作图。

可以把它理解为：提示词是一句话，循环是一种节奏，harness 是 Agent 站立的地板；真正决定 Agent 能跑多远的，是任务本身的拓扑结构。

这套方法解决什么问题

Claude Code 的 dynamic workflows 让 Claude 可以写一段普通 JavaScript 编排脚本，再启动一组 subagent 协同执行。调度本身由代码完成，不需要反复塞进模型对话里，所以不会持续占用主会话上下文。

文章的核心观点很直接：工作流的形状本身就是图。哪些步骤能同时跑，哪些步骤必须等待，哪些结果需要汇总，哪些发现要复核，这些都不是“提示词写得好不好”的问题，而是图结构问题。

如果能画出节点和边，就能看见三个机会：

•哪些步骤其实没有依赖，可以并行。
•哪些步骤只是数据清洗，应该用代码完成。
•哪些结果必须经过验证节点，才能进入最终答案。

01. 节点是任务，边是流动的数据

图只有两个基础对象：节点和边。

节点是一段有边界的工作：一个 Agent、一个明确任务、一个输入和一个输出。边是依赖关系，表示这个节点的输出会进入另一个节点的输入。

最常见的误区，是把“然后”当成边。比如“总结这个文件，然后告诉我天气”，两件事没有真实依赖，天气查询不读取文件总结结果。它们是两个独立节点，只是被线性脚本硬绑在一起。

判断一条边是否真实，问一句就够了：下一步是否读取上一步的输出？如果不读取，就没有边，也没有等待的理由。

class="language-text">把工作画成盒子和箭头。
盒子是一次 agent() 调用。
箭头是一个节点返回的变量，被传入另一个节点的 prompt。
如果画不出这条变量箭头，两个盒子就是独立的。

02. 线性脚本是一种退化图

“先做 A，再做 B，再做 C，再做 D”当然也是一张图，只是它退化成了一条链。每个节点只有一条输入边和一条输出边。

这类链条通常能跑，但慢，也脆。只要 C 卡住，D 永远不会发生，A 和 B 的结果也被困在上游。

图工程的第一项能力，是重画这条链。拿着每一条箭头问：这里真的有数据依赖吗？很多链条里，有两三条箭头只是你敲代码时自然写下的顺序，并不是任务本身的依赖。

剪掉这些假边，线性链条就会变宽：几个独立节点可以同时跑，最后再汇入一个真正需要全量结果的节点。

03. 给每个节点一个契约

如果一个节点的输入输出说不清，就很难并行。解决办法是给节点写契约：输入有边界，输出有结构，任务只做一件事。

输入应该显式传入，不能假设它能读到某个共享上下文。输出最好用 schema 验证，方便下游节点直接消费。

在 Claude workflow 里，可以在 agent() 调用中提供 JSON schema。子 Agent 必须返回符合结构的数据；如果不匹配，验证层会让它重试，而不是把一段自由文本丢给你再手动解析。

class="language-javascript">"color:#6a9955">#6a9955">// 一个有契约的节点：输入有边界，输出被验证，只做一个任务。
const ITEM = {
  type: 'object',
  additionalProperties: false,
  properties: {
    title: { type: 'string' },
    url: { type: 'string' },
    impact: { type: 'string', enum: ['high', 'medium', 'low'] },
  },
  required: ['title', 'url', 'impact'],
};

const result = await agent(source.prompt, {
  label: "color:#ce9178">`research:${source.key}`,
  schema: ITEM,
  agentType: 'general-purpose',
});

这就是“能被图接线的节点”和“只能让人读一遍输出”的节点之间的区别。

04. 把边当作数据契约

边不是“B 在 A 后面”。边的含义是：A 产出一种结构，B 消费这种结构。

当你用数据来命名边，而不是用执行顺序命名边，两件事会更清楚：

•这条边是否真实存在，是否真的有数据移动。
•只要数据结构不变，边两端的节点是否可以替换。

在实际 workflow 里，很多边只是普通 JavaScript：展开数组、去重、过滤、排序。这些不需要 Agent，也不需要模型判断。

class="language-text">如果“合并结果”只是 flatMap 和 Set，就别启动一个 Agent。
Agent 应该用来做判断，不该用来搬管道。
边如果全是 Agent，整张图就在为自己的接线付 token。

05. 用 parallel() 扇出

这是图工程里最能立刻带来收益的一步。面对 N 个独立节点，比如 N 个资料源、N 个文件、N 条路由，不要串行跑。

用 parallel() 扇出。Claude 会接收一组 thunk，并为每个 thunk 启动一个 subagent 并发执行，最后返回结果数组。

这里有两个细节很重要：

•parallel() 是一个 barrier，它会等所有 thunk 结束后再返回。
•某个 thunk 抛错会变成 null，不会让整个批次失败。

所以结果回来后，通常要做一次 .filter(Boolean)。并发数量会被限制在机器可承受范围内，多出来的任务排队执行。

class="language-javascript">phase('Research');

const raw = await parallel(
  SOURCES.map((s) => () =>
    agent(s.prompt, {
      label: "color:#ce9178">`research:${s.key}`,
      phase: 'Research',
      schema: ITEM_SCHEMA,
      agentType: 'general-purpose',
    }),
  ),
);

const collected = raw.filter(Boolean);

扇出的好处不只是速度。主 Claude 会话不必同时塞下九个来源，每个 subagent 自己携带局部上下文，最后只把结构化结果返回给编排层。

06. 在 barrier 处扇入

扇出之后，必须有地方把结果收回来。扇入节点就是多条边汇合的地方，它会看到所有上游结果，然后做真正需要全量视角的事情：跨来源去重、按影响排序，或者发现总结果为空就提前退出。

规则很简单：只有某个阶段真的需要所有上游结果时，才设置 barrier。

跨来源去重需要 barrier；单纯展开数组不需要。能用普通代码做的中间变换，就让边自己完成。

class="language-javascript">const flat = collected.flatMap((c) => c.items);
log("color:#ce9178">`Collected ${flat.length} items`);

phase('Curate');
const curated = await agent(
  `Dedupe and rank these by impact:
${JSON.stringify(flat)}`,
  { phase: 'Curate', schema: CURATED_SCHEMA },
);

如果你写出了 parallel -> transform -> parallel，而中间的 transform 没有跨项目依赖，那通常应该改成 pipeline，不该让所有 item 在中间集体等一次。

07. 钻石结构：拆分、工作、合并

把 fan-out 和 fan-in 放在一起，就是严肃 Agent 图里最常见的拓扑：钻石结构。

一个节点拆任务，多个节点并行工作，一个节点合并结果。市场扫描、依赖审计、代码审查、研究报告，都可以套这副骨架，只需要换来源和 prompt。

它的标准形态是：fan out -> reduce -> synthesize。

先扇出拿广度，再用代码压缩结果，最后用一个 Agent 写答案。理解了钻石结构，就不会只问“怎样让 Agent 做更多步骤”，而是开始问“哪里应该拆，哪里应该合”。

08. 用条件判断在运行时路由

图不一定是固定的。很多时候，下游路径取决于上游节点发现了什么。

一个 router 节点可以先分类，再由代码决定走哪条边：工单属于哪一类，就交给对应处理器；diff 风险高，就进入完整审计；风险低，就走快速审查。

在 workflow 里，这就是 JavaScript 的 if 或 switch。Claude 可以负责分类，但路由本身由代码执行。这样同样的分类会走同样的路径，不会出现模型临场跳过审计的意外。

class="language-javascript">const { severity } = await agent(
  `Classify this diff's risk:
${diff}`,
  {
    schema: {
      type: 'object',
      properties: { severity: { enum: ['low', 'high'] } },
      required: ['severity'],
    },
  },
);

let review;
if (severity === 'high') {
  review = await parallel(FILES.map((f) => () => agent("color:#ce9178">`Audit ${f}`)));
} else {
  review = await agent("color:#ce9178">`Quick review of ${diff}`);
}

09. 在边上放验证器

图的真正杠杆不是“更多 Agent”，而是能在 Agent 周围包上可靠结构。

验证节点放在结果进入下游之前，任务只有一个：试着推翻这个发现。能活下来，就放行；活不下来，就不进入最终答案。

作者给了三种验证模式：

•对抗式验证：每个发现交给 N 个独立怀疑者去反驳，多数通过才保留。
•多视角验证：每个 verifier 带不同视角，比如正确性、安全性、是否可复现。
•评委组：从多个角度生成 N 个候选结果，再让评委并行打分，综合出最终版本。

这种结构已经出现在真实工程里：例如把 Bun runtime 移植到另一个环境时，把对抗式代码审查嵌进循环，能提前挡掉单 Agent 容易漏掉的问题。

10. 隔离节点，避免一个失败污染整张图

在线性链条里，一个节点失败会向后级联。C 死了，D 就不会运行。

图应该把失败限制在节点内部。parallel() 已经做了一部分：某个 thunk 失败会返回 null，其他节点照常返回。你的 fan-in 需要能容忍缺失输入，而不是假设每个上游节点都成功。

还有一种更隐蔽的问题：并行 Agent 会互相踩文件。多个 Agent 同时写代码时，可能互相覆盖。

解决办法是隔离工作区。每个 Agent 在自己的 git worktree 里执行，完成后再干净合并。它不是所有任务的默认成本，而是“并行写文件”这种拓扑的安全带。

11. 加循环，但必须收敛

有些任务一开始不知道规模：未知 bug 搜索、发现一个问题又牵出三个问题的扫描。它需要循环，也就是一条回到早先节点的受控边。

风险也很明显：不收敛的循环会无限启动 Agent，直到预算耗尽。

可收敛的模式叫 loop-until-dry：持续启动发现节点，直到连续 K 轮没有新发现再停止。

这里最容易犯错的是去重对象。要对所有“见过”的项目去重，而不是只对已确认项目去重。否则被否掉的发现会每轮重新出现，循环永远不会干。

class="language-text">const seen = new Set();
const confirmed = [];
let dry = 0;

while (dry < 2) {
  const found = (await parallel(
    FINDERS.map((f) => () => agent(f.prompt, { schema: BUGS }))
  )).filter(Boolean).flatMap((r) => r.bugs);

  const fresh = found.filter((b) => !seen.has(key(b)));
  if (!fresh.length) { dry++; continue; }
  dry = 0;
  fresh.forEach((b) => seen.add(key(b)));

  "color:#6a9955">#6a9955">// 对 fresh 发现做多视角验证，通过后才进入 confirmed。
}

12. 按节点给模型分层

不是每个节点都需要最强模型。图结构会把这件事暴露得很清楚：有些节点很重复，比如抽字段、分类工单；有些节点才真的需要判断，比如合成报告、裁决发现。

默认情况下，Claude 启动的每个 subagent 会继承当前会话模型。如果你在高配模型会话里跑一大批重复节点，成本会很快上来。

可以在单个 agent() 调用里指定模型。把重复、边界清楚的扇出节点切到便宜模型，把最终合并和判断节点留给强模型。这不改变图的形状，却能显著改变成本。

13. 拓扑决定成本和延迟

图的形状不是装饰，它直接决定延迟。

最容易踩坑的选择是 parallel() 和 pipeline()。parallel() 的 barrier 会让所有节点等最慢那个结束，下一阶段才能开始。pipeline() 则让每个 item 独立流过所有阶段。A 已经到第三阶段时，B 可能还在第一阶段，快 item 不必陪慢 item 等。

默认应该先考虑 pipeline。只有某个阶段确实需要前一阶段的全量结果，才使用 barrier，比如跨集合去重、根据总量提前退出、需要比较“其他发现”的 prompt。

“代码更整齐”不是 barrier 的理由。分阶段不等于同步等待。

14. 让 Claude 自己画图

最后一步，是不要总是手动画图。对于无法预先规划的任务，可以直接让 Claude 写动态 workflow。

你描述目标，Claude 写编排脚本，拆任务、选择扇出、启动 subagent fleet，再合成结果。得到的不是一张固定模板，而是为当前任务临时生成的图。

入口有三种：

•在 prompt 中直接说 “workflow”，让 Claude 为这次任务写一个工作流。
•运行保存过或内置的 workflow，例如 /deep-research，它本身就是“scope -> parallel search -> fetch -> adversarial verify -> synthesize”的生产级图。
•打开 ultracode，让 Claude 为会话里的重大任务规划 workflow。

如果某次 workflow 跑得好，可以按 s 保存到 .claude/workflows/。这样它会进入版本控制，可以按名字复跑，团队其他人 clone 仓库后也能使用。

class="language-text">Run a workflow to audit every route under src/routes/ for missing auth.
Spawn one agent per route file, then verify each finding before reporting.

Claude wrote an orchestration script, launching in background...
/workflows - auth-audit - running
Scope 1/1
Fan-out 18/18, one agent per route file
Verify 11/18, three-vote skeptics per finding
Synthesize waiting on verify

本周可以试的六张图

第一张图：安全扫描。让 Claude 为每个路由文件启动一个 subagent，寻找缺失的鉴权检查，再用 verifier 确认每个发现。它能覆盖单个上下文装不下的范围。

第二张图：带引用的深度研究。用 /deep-research 把问题拆成多个角度，并行搜索，去重资料，再用对抗式验证复核每个结论。

第三张图：逐文件移植模块。把一个模块按文件扇出迁移，每个文件跑测试作为 gate，失败再回环修复。这里的重点是“文件级并行 + 测试门禁 + 对抗审查”。

第四张图：diff 的对抗式审查。先按 diff 大小或风险路由，小改动走快速审查，大改动触发多视角并行审计，比如正确性、安全性、性能，再由评委组合成结果。

第五张图：定时生态扫描。把多个来源并行抓取，在 barrier 处按影响排序，最后生成摘要。保存成 .claude/workflows/ 后可以长期复跑。

第六张图：未知规模发现。并行启动 finder，对所有已见项目去重，验证幸存发现，再循环到连续两轮没有新发现为止。

结语

普通 prompter 会问一个问题，架构师会画一张图。

线性 Agent 从来不是上限，它只是最容易写出来的第一种形状：一条线，一个头，一次只做一件事。

一旦能看见节点和边，你就不会只要求 Agent “多做几步”，而会开始让工作图变宽：独立任务扇出，需要信心的地方加验证，判断不强的节点换便宜模型，真正需要全量视角时再合并。

很多人还会继续把步骤排成队。能画出图的人，会跑出一支 Agent fleet，也会更少被上下文窗口和串行延迟困住。

声明

本文由山行整理自：原文链接[1]，如果对您有帮助，请帮忙点赞、关注、收藏，谢谢～

参考链接

[1] 原文链接: https://x.com/0xCodez/article/2079165300625330317