# Vibe Coding 最佳实践:从"让 AI 写代码"到可验证的软件工程闭环

> **一句话摘要**:代码生成速度飞快,交付效率却不同步——Vibe Coding 的真正问题不是"模型能不能写代码",而是"怎样稳定完成一个工程任务"。本文总结一条工程方法论总纲:Specification → Prompt → Context → Harness → Loop → Verifiable Software 六层工程栈 + 12 条最佳实践,并把每条映射到站内对应深度文章,作为 agent coding 思路的汇总枢纽。
>
> **来源**:Coggle数据科学《Vibe Coding 最佳实践:从"让 AI 写代码"到构建可验证的软件工程闭环》(https://mp.weixin.qq.com/s/nREHkoo50j6oPKQ4w6jOzg)

## 概念

### 核心矛盾:生成速度 ↑,交付效率不涨

Vibe Coding 最大的震撼来自**代码生成速度**:几句话描述,Agent 就能搜索项目、改代码、跑命令、给出可运行版本。但用久了会发现一个**反直觉**现象:

> 代码生成速度提升得非常快,真正的软件交付效率却没有同比例增长。

Skill 越来越多、Workflow 越来越复杂、Agent 一次改的代码越来越多,但**需求理解错误、上下文丢失、架构偏离、测试不足、修改范围失控、长任务漂移**依然存在。早期问题是"模型能不能写代码",现在变成"模型怎样**稳定地完成一个工程任务**"——差几个字,工程含义完全不同。

### 六层工程栈(总纲)

```
Specification           需求与验收边界(什么算完成)
   ↓
Prompt Engineering      把人的意图转化为清晰任务
   ↓
Context Engineering     让 Agent 在恰当时机看到正确的信息
   ↓
Harness Engineering     工具、权限、沙箱、状态、验证、观测环境
   ↓
Loop Engineering        在执行结果的反馈中判断、修正、重试、停止
   ↓
Verifiable Software     可验证交付
```

本质转变:不再把大模型当"特别聪明的代码生成器",而是**软件系统中的一个概率性执行组件**——既然概率性,就不能假设每一步正确;既然不能保证正确,就需要上下文、工具、验证、权限、反馈和恢复机制。

### 演进路线

```
Prompt("告诉 Agent 做什么")
  → Context("让 Agent 看见正确的信息")
  → Workflow("让 Agent 按合理步骤执行")
  → Harness("让 Agent 在可靠环境中工作")
  → Loop("让 Agent 根据反馈自主修正")
  → Software Engineering System("让整个开发过程持续可验证")
```

## 原理(12 条最佳实践)

### 1. 完成条件显式化:Agent 最大的问题不是不会写,而是不知道什么才算完成

很多 Vibe Coding 失败看似模型能力不足,实际发生在**任务定义阶段**。刚进项目上下文的 Agent 没有边界条件,只能靠训练数据猜"优化"意味着什么——可能优化代码结构,而你关心 Redis 故障降级;可能重写组件,而你只想修视觉细节。

关键思想转变:**不要只告诉 Agent 做什么,还要告诉它什么情况下可以认为已经做完。** 人工开发时程序员靠经验判断完成,所以验收标准不必写全;执行者变成 Agent 后,没有显式完成条件,它只能自己推测何时停止。

### 2. 设计前置:Agent 越能写,实施前越值得投入时间

代码生产成本剧降后,一份模糊需求可能在短时间内扩展成几十个文件、数千行修改;方向一错,生成越快,错误规模越大。所以一个反直觉结论:**Agent 编码能力越强,实施前的需求澄清和设计阶段反而应该越厚。**

成熟流程不是 `Requirement → Code`,而是 `Requirement → Research → Design → Plan → Implement → Verify → Review`。错误架构决策在 Design 阶段否掉成本几分钟;代码生成后再发现,修复成本剧增。真正高效的 Vibe Coding 不是减少人出现的次数,而是**让人只出现在最值得决策的位置**(需求是否正确、架构是否合理、边界是否可接受)。

### 3. 仓库即上下文:从每次重新解释项目,到让仓库本身教 Agent 开发它

每次开新会话都重新告诉 Agent 技术栈/目录/测试命令/风格约束,等于把本该属于项目基础设施的信息放回人工 Prompt——团队每天几十上百次 Session 的重复劳动。

`AGENTS.md` / `CLAUDE.md` 不是简单的"Prompt 文件",而是**项目内部面向 Agent 的长期工程说明**。成熟思路:**不要不断告诉 Agent 如何开发项目,要让项目本身能够教 Agent 如何开发它**(Agent Friendly Repository):模块职责、环境启动、测试/Lint/Type Check 命令、架构规则、可改目录、需人工确认的操作、兼容性要求。

### 4. 长上下文不是答案,信息选择才是

上下文窗口再大,问题不是"装不下"而是**信息密度下降**:几十个文件、几千行日志、测试失败、聊天记录、设计文档、工具输出混在一个窗口,即使没到 Token 上限,也会显著增加找到重要信息的难度——上下文越大,不代表模型对所有信息有同等稳定的注意力。

对 Coding Agent 尤其关键:代码仓库天然是巨大的潜在上下文源。正确流水线:

```
Repository → Search / Explore → Relevant Files → Research Summary
  → Design → Implementation Plan → Current Task Context
```

### 5. 抽象是 Agent 隔离的有效方法:按认知任务和上下文边界拆,不按开发角色拆

Subagent 的价值常被误解成"并行加速"。真实 Coding Workflow 里,Subagent 更重要的价值是**隔离不同类型任务产生的大量中间上下文**:

```
            Main Agent
      ┌───────────┼───────────┐
      ↓           ↓           ↓
  Research     Verify      Review
  (代码探索)   (测试分析)   (独立审查)
      └─────── Summary ───────┘
                   ↓
              Main Context
```

**按认知任务和上下文边界拆 Agent,而不是机械按开发角色拆**:读大量代码但输出结论短 → Subagent;需要独立观点避免实现者自我确认 → Subagent(Review);并行且依赖弱的探索 → Subagent。紧密顺序依赖的小功能,没必要为 Multi-Agent 而 Multi-Agent。

### 6. Skill 的价值:把偶然成功变成可重复流程

积累一堆"好用的 Prompt"(写测试/做 Review/分析日志/生成文档)短期有价值,但更高效的是把**稳定、重复出现的操作流程沉淀成 Skill**。Skill 与普通 Prompt 的区别:不仅描述"模型应该怎么回答",还能组织任务步骤、参考资料、脚本、工具甚至验证方式(例:"修复 Python Bug" Skill = 复现 → 定位调用链 → 新增失败测试 → 最小修改 → 跑 Ruff/BasedPyright/pytest → 输出摘要与验证结果)。

**重复出现的自然语言经验,最终应该尽可能转化为结构化工程资产。** 成熟项目的 Agent 能力不会是单个巨大的 CLAUDE.md,而是**项目规则(长期约束)+ Skills(可复用流程)+ MCP/工具(行动能力)+ Subagents(上下文隔离)+ Hooks(确定性程序行为)+ 验证体系**的组合。

### 7. 可靠性最终是环境问题,不只是模型问题

Agent 拿到 Shell/文件系统/Git/浏览器/数据库/云服务/部署权限后,风险快速上升。要思考的不只是"写代码准不准",而是:**在什么环境执行、能访问什么资源、哪些操作要审批、失败怎么恢复、长任务如何保存状态、如何知道 Agent 做过什么、什么时候必须强制停止**。

**Agent 权限越大,Harness 越重要**——不是 Agent 一定会做坏事,而是能高速执行错误计划的系统,本身就需要更强的防护和回滚能力。

### 8. Workflow 告诉 Agent 下一步做什么,Loop 决定它能不能自己收敛

固定 Workflow 是"计划→写码→跑测试→结束"的流水线,比自由 Agent 稳定,但没解决:**测试失败怎么办?实现与设计不一致怎么办?方案不可行怎么办?连续三次没改善何时停止?**

Loop Engineering 关注系统在**真实反馈**下如何动态决定下一步(观察、评估、重试、终止、人类介入)。对 Coding Agent,"测试"不再是流程中的一个阶段,而是**理解自己是否正确的重要观察信号**:

```
Plan → Execute → Observe → Verify
  ┌── Success? ──┐
 Yes             No → Diagnose → Revise
  │                             │
  └─────────── Done ←───────────┘
```

一句话:**权限解决"Agent 能不能做",反馈和验收解决"Agent 做得对不对"。**

### 9. TDD 特别适合 Coding Agent

模型无法像人一样直接感知软件运行状态,修改后必须依赖外部信号判断对错,而测试提供**结构化、可重复、低歧义的反馈**。测试失败 → Agent 读错误、分析原因、再修改——开发从"模型凭感觉判断写对没有"变成"模型不断根据客观信号逼近目标"。

### 10. 当 Agent 写得比人看得快,Review 模式必然变化

一天改几十行时逐行审查没问题;多个 Agent 并行每天产生数千上万行 Diff,人就成了吞吐瓶颈。此时**架构设计、详细设计、开发计划和验收方式反而更重要**;人的注意力从"这一行写了什么"转向"边界是否正确、验证证据是否可信、失败后能否恢复"。

### 11. Agent 很容易优化正确性,却可能同时积累复杂性

模型围绕明确指标优化:如果 Harness 只告诉它"pytest 必须通过",它最终学会的是"想办法让 pytest 通过"。短期没问题,但对持续维护数年的大型系统,**"当前测试通过"不代表工程质量**——Agent 完全可能用五个模块间的特殊判断获得正确结果,半年后团队才发现小改动要理解十五处隐藏逻辑。

### 12. 不是工具竞赛:从自己的失败模式反推工程机制

不必为"没装某 Skill/MCP、没有 Multi-Agent"焦虑。工具列表太长增加选择难度与上下文消耗,复杂方案引入规则冲突与维护成本。**不存在一套所有项目都该复制的 Workflow**(个人原型 vs 金融核心系统要求完全不同)。最好做法:从失败模式反推——经常误解需求 → 增加 Requirement Interview(动手前主动提出未知项);经常在大仓库迷失 → 优化代码搜索/Research/Context Compression。

## 代码 / 实现

本文的可直接落地形态(均已内嵌上文):

- **上下文流水线**:`Repository → Search → Relevant Files → Research Summary → Design → Implementation Plan → Current Task Context`;
- **Subagent 拓扑**:Main Agent + Research/Verify/Review 三个隔离 Subagent,汇总 Summary 回主上下文;
- **Loop 状态图**:`Plan → Execute → Observe → Verify → (Success? Yes: Done / No: Diagnose → Revise)`。

配套工程资产组合(对应第 6 条):项目规则(AGENTS.md/CLAUDE.md)+ Skills + MCP/工具 + Subagents + Hooks + CI/Test 验证。工具建议:**规则负责长期约束,Skill 负责可复用流程,MCP 负责扩展行动,Hook 把必须执行的要求从自然语言建议变成确定性程序行为。**

## 实践 / 应用(与站内资料汇总)

> 本文是总纲,每条最佳实践站内都有对应深度文章——按需下沉,避免重复造轮子:

| # | 最佳实践 | 站内深度文章(汇总入口) |
| --- | --- | --- |
| 1 | 完成条件显式化 | [WorkBuddy Bench:Agent 的"完成"由什么证明](../../03-agents/workbuddy-bench.md)、[评估驱动开发 EDD](../../03-agents/agent-eval-driven-dev.md) |
| 2 | 设计前置(Spec-First) | [Spec-First 决策栈](spec-first-decision-stack.md)、[SDD+OpenSpec+Superpowers](../skills/sdd-openspec-superpowers.md)、[Spec Kit](../skills/spec-kit-github.md)、[得物 Spec-Driven 案例](../../04-practice/ai-native-order-system-spec-driven.md) |
| 3 | 仓库即上下文 | [给 Coding Agent 立规矩(AGENTS.md)](agent-rules-agents-md.md)、[上下文工程官方一手资料](../../03-agents/context-engineering-official-sources.md) |
| 4 | 信息选择 | [Context Engineering 系列](../../03-agents/context-engineering.md)(playbook/压缩缓存/文档漂移) |
| 5 | Subagent 上下文隔离 | [Subagent:上下文隔离与职责分工](../../03-agents/subagent-isolation.md)、[Agent Session 通信设计](../../03-agents/agent-collaboration-messaging.md) |
| 6 | Skill 沉淀 | [📦 Skill 收藏](../skills/index.md)(16 篇:治理/版本/测评/收藏) |
| 7 | 可靠性 = 环境 | [AI Coding Harness 设计经验](ai-coding-harness-design.md)、[生产级 9 层架构(权限/沙箱)](../../03-agents/ai-infra-layering.md)、[Agent 生产架构](../../03-agents/agent-production-architecture.md) |
| 8 | Workflow vs Loop | [Loop Engineering](loop-engineering.md)、[Ralph Wiggum 循环](ralph-wiggum-loop.md)、[Agent 规划与工作流模式](../../03-agents/agent-planning-patterns.md) |
| 9 | TDD for Agent | [AI 时代的 TDD 四层落地](ai-tdd-practice.md) |
| 10 | Review 模式变化 | [Agentic Code Review](agentic-code-review.md) |
| 11 | 正确性 vs 复杂性 | [用 Agent 持续交付(认知复杂度)](agent-cognitive-complexity-gates.md)、[Agent 架构反熵增](../../03-agents/agent-architecture-antientropy.md) |
| 12 | 从失败模式反推 | [Agent 容错设计](../../03-agents/agent-fault-tolerance-design.md)、[Agent 性能剖析](../../03-agents/agent-performance-analysis.md) |

### 指标:不该看生成了多少代码

代码便宜之后,"一天写多少代码"、Tool Call 次数、改文件数都只是过程指标。真正决定效率的:**需求从提出到形成可验证交付的 Lead Time,以及失败后恢复的时间**。评价应接近软件工程本身指标:任务 Lead Time、首次验证通过率、回归率、平均失败恢复时间、人工干预次数、每任务 Token 与算力成本、下一次修改同一模块的理解成本。

### 人的位置在不断向上移动

```
人负责写代码 → 人告诉模型写什么 → 人负责需求/设计/验收
  → 人负责环境/权限/反馈回路/停止条件 → 人负责 Specification/Evaluation/风险边界/异常决策
```

**Agent 负责大量探索、实现、测试和局部修正;人负责决定方向、设计边界、定义反馈和处理例外。** 这种分工建立后,效率提升才不再是"打字更快",而是整个 SDLC 的效率提升。

## 扩展:外部同类思路印证(2025 年一手资料)

> 检索补充:以下外部一手资料与本总纲思路高度一致或提供关键深化,均经核实可溯源,可直接作延伸阅读。

### 1. Anthropic《Effective context engineering for AI agents》(2025-09-29)——印证 #3 / #4 / #6 / #8

- **context rot**:上下文 token 越多,信息回忆精度越低;context 是"有限资源",目标是**最小的高信号 token 集**——与第 4 条"长上下文不是答案,信息选择才是"直接同构;
- **CLAUDE.md 混合策略**:CLAUDE.md(AGENTS.md 类文件)前置注入 + glob/grep 即时检索(just-in-time retrieval / progressive disclosure),而非全量塞入——深化第 3 条"仓库即上下文";
- **长任务三件套**:compaction(压缩会话)+ 结构化笔记 / agentic memory(CLAUDE.md、NOTES.md、todo list)+ sub-agent 架构(子 agent 隔离上下文,**只回传 1000–2000 token 摘要**);
- **工具即 contract**:最小可行工具集、token 高效、避免工具膨胀导致歧义;例子要精选 canonical 样例而非堆砌 edge cases。

### 2. Anthropic《Building agents with the Claude Agent SDK》(2025-09-29)——印证 #7 / #8 / #5

- **Agent 反馈环的官方定义**:`gather context → take action → verify work → repeat`——与"Loop 收敛 + Verifiable Software"直接同构;
- **Harness 设计原则"给 agent 一台电脑"**:终端、bash、文件编辑、lint、run、debug,迭代直到代码成功——本身就是可验证闭环;
- **信息检索优先级**:agentic search(把文件系统当 context engineering)优于 semantic search(更慢、维护成本高、不透明);
- Subagents 默认支持,两大用途:**并行化 + 隔离上下文窗口**(只回传相关摘录)。

### 3. Simon Willison context-engineering 合辑(一手转述,含 Drew Breunig / Liz Fong-Jones / Matt Webb)——印证 #3 / #4 / #5 + 补充边界

- **Karpathy / Lutke 定义**:context engineering 是"向上下文窗口**填充恰好正确信息**的艺术与科学"(比 prompt engineering 更准确);
- **Drew Breunig《How to Fix Your Context》——context rot 四种模式**:Poisoning(污染)/ Distraction(分心)/ Confusion(混淆)/ Clash(冲突);对策:Tool Loadout(>20 个工具会迷惑模型)、**Context Quarantine(= sub-agent 隔离,Claude Code 与 Anthropic multi-agent 论文同款模式)**、Pruning、Summarization、Offloading(plan.md 等);
- **Liz Fong-Jones 便签类比**:把模型想成"读过所有教科书、但没有你代码库经验的实习生"——AGENTS.md / style guide / checklist 是贴给它的便签,但 **"100 张便签"会混淆它,必须定期清理替换**——深化第 3 条的边界:仓库即上下文 ≠ 上下文越多越好;
- **Matt Webb:context plumbing**——把 agent 的架构问题重构为"把上下文从源头输送到需要它的地方"。

### 对应关系小结

| 外部来源 | 核心思路 | 印证 / 深化本站条目 |
| --- | --- | --- |
| Anthropic Effective context engineering | context rot;CLAUDE.md 混合策略;长任务三件套;工具即 contract | #3 仓库即上下文、#4 信息选择、#6 Skill、#8 Loop 长程机制 |
| Anthropic Claude Agent SDK | gather→act→verify→repeat;给 agent 一台电脑;agentic search | #7 Harness、#8 Loop、#5 Subagent |
| Drew Breunig | context rot 四模式;Context Quarantine;Tool Loadout | #4 信息选择、#5 Subagent 隔离 |
| Liz Fong-Jones | 便签类比:AGENTS.md 需定期清理 | #3 边界(不是越多越好) |
| Karpathy / Lutke | context engineering 定义 | #4(概念层) |

**小结**:外部一手资料没有推翻总纲,而是为"信息选择、仓库即上下文、Subagent 隔离、Loop 收敛"四条提供了最直接的权威背书,并补上一条关键边界——**AGENTS.md 不是写一次就完事,要像维护代码一样定期清理替换**;context rot 四模式(污染/分心/混淆/冲突)则是诊断"上下文为什么失效"的现成分类学。

## 总结

1. **总纲是六层工程栈**:Specification → Prompt → Context → Harness → Loop → Verifiable Software;本质是把 LLM 当概率性执行组件,用系统机制补上"不保证每一步正确"。
2. **完成条件是第一优先级**:告诉 Agent 什么情况算做完,否则它只能猜;Agent 越能写,实施前的需求澄清与设计越要厚。
3. **上下文靠选择不靠长度**:仓库即上下文(AGENTS.md)、信息密度、Subagent 按认知任务隔离中间上下文。
4. **经验要沉淀成资产**:自然语言经验 → Skill/规则/Hooks/验证体系;Workflow 给路径,Loop 给收敛,权限管"能不能做",反馈验收管"做得对不对"。
5. **指标回到软件工程**:Lead Time、首次验证通过率、恢复时间、理解成本;人的位置向上移动到需求/边界/验收/风险决策。

**下一步学什么**:按上表映射逐条下沉——先从 [Loop Engineering](loop-engineering.md) 和 [AI Coding Harness 设计经验](ai-coding-harness-design.md) 开始;或读 [Spec-First 决策栈](spec-first-decision-stack.md) 补齐设计前置。

## 延伸阅读

- 站内:[AI Coding Harness 设计经验](ai-coding-harness-design.md)、[Loop Engineering](loop-engineering.md)、[Spec-First 决策栈](spec-first-decision-stack.md)、[AI 时代的 TDD](ai-tdd-practice.md)、[给 Coding Agent 立规矩](agent-rules-agents-md.md)、[Subagent 隔离](../../03-agents/subagent-isolation.md)、[Context Engineering](../../03-agents/context-engineering.md)、[Skill 收藏](../skills/index.md)、[Agentic Code Review](agentic-code-review.md)
- 外部:原文《Vibe Coding 最佳实践》(https://mp.weixin.qq.com/s/nREHkoo50j6oPKQ4w6jOzg);Anthropic *Effective context engineering for AI agents*(https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents);Anthropic *Building agents with the Claude Agent SDK*(https://claude.com/blog/building-agents-with-the-claude-agent-sdk);Simon Willison *context-engineering* 合辑(https://simonwillison.net/tags/context-engineering/,含 Drew Breunig《How to Fix Your Context》与 Liz Fong-Jones 线程)
