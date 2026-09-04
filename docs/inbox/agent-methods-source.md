# 原始资料:四种 Agent 开发方法对比:BMAD、Spec Kit、GSD 和 Skills 怎么选

> 来源:微信公众号「山行AI」;原文链接:https://mp.weixin.qq.com/s/uIRPK1Hy96lsW7gLnuvSFw
> 抓取日期:2026-08-09;状态:已提炼为 docs/03-agents/agent-development-methods.md(控制层级对比 + 选型框架)
> 性质:BMAD METHOD / Spec Kit / GSD Core / Matt Pocock Skills 四种 Agent 开发方法的控制层级对比(流程/规范/上下文/工程习惯)与选型决策

---

AGENT METHOD

2026.07
只靠提示词
Agent 开发方法
到底怎么选

BMAD · Spec Kit · GSD Core · Skills

流程、规范、上下文、工程习惯

— 四种 Agent 开发方法的控制层级对比

过去半年，AI 编程工具的讨论正在从模型能不能写代码，转向另一个更现实的问题：当 Agent 真的参与开发，团队到底该把多少流程交给它？

BMAD METHOD、Spec Kit、GSD Core 和 Matt Pocock Skills 都在解决 Agent 编程失控的问题，但切入层级完全不同。

「BMAD 管团队流程，Spec Kit 管规范入口，GSD 管上下文质量，Skills 管工程习惯。」

数据说明：本文的 Star、Fork、Issue、语言和默认分支数据抓取于 2026-07-30，GitHub 数据会随时间变化。

01
PART

先放在同一张坐标系里
METHOD · MAP

这四个项目不是简单替代关系，真正差别在于 Agent 接管到哪一层。BMAD 和 Spec Kit 更像把开发组织方式固定下来，GSD 更像让 Agent 长任务不烂尾，Matt Pocock Skills 更像保留控制权的小工具箱。

•BMAD METHOD：51,265 Star，多角色敏捷框架，强调 34+ workflows 和模块生态。

•Spec Kit：124,531 Star，spec-driven development 工具包，强调 constitution、spec、plan、tasks、implement。

•GSD Core：7,415 Star，上下文工程框架，强调 Discuss、Plan、Execute、Verify、Ship 五阶段循环。

•Matt Pocock Skills：195,022 Star，工程技能集合，强调可编辑、可组合、按失败模式调用。

02
PART

BMAD：多角色敏捷框架
ROLE · WORKFLOW

— BMAD METHOD 项目横幅

BMAD METHOD 不是一个单点提示词，而是一套 AI-driven agile development 框架。它把需求澄清、产品设计、架构、UX、开发、测试和研究拆成多个专家 Agent 与工作流。

•核心能力：34+ workflows、多 Agent 角色协作、Party Mode、模块生态和 Web Bundles。

•架构模式：业务目标进入多角色 Agent，再由结构化 workflow 编排，最终沉淀 PRD、架构、UX、任务和研究产物。

•优势：体系完整、角色边界清晰，适合复杂产品和多人协作。

•限制：流程较重，团队需要接受它的工作方式；个人快速修 bug 时可能显得过于正式。

text
业务目标

  -> 多角色 Agent 拆解

  -> 结构化 workflow 编排

  -> IDE 或 Agent 环境执行

03
PART

Spec Kit：规格说明变成入口
SPEC · GOVERNANCE

— Spec Kit 标识

— Spec Kit 视频头图

Spec Kit 强调 Spec-Driven Development：先定义要构建什么，再让 AI coding agent 去实现。它的关键观念是，规格说明不再只是写完就丢的脚手架，而是会继续参与实现过程的可执行资产。

•核心流程：specify init、constitution、specify、plan、tasks、implement。

•扩展机制：Extension 增加新能力，Preset 改造既有 workflow，Bundle 组合角色化安装包。

•优势：组织治理能力强，能把需求、计划、任务和审查沉淀为资产。

•限制：spec 写得差，后面的 plan 和 tasks 也会跟着偏；流程资产越多，维护成本越高。

text
specify init

  -> /speckit.constitution

  -> /speckit.specify

  -> /speckit.plan

  -> /speckit.tasks

  -> /speckit.implement

04
PART

GSD：对抗长任务上下文失真
CONTEXT · LOOP

GSD Core 的核心不是更多角色，而是 context engineering。它认为 AI 编程在规模化时最常见的问题，是上下文不断膨胀后输出质量下降，也就是 context rot。

•五阶段循环：Discuss、Plan、Execute、Verify、Ship。

•关键机制：重研究、规划和执行放进 fresh-context subagents，主会话保持精简。

•状态资产：STATE.md 和 CONTEXT.md 保存跨 session 的结构化记忆。

•优势：适合长任务、多会话和跨 Agent 协作。

•限制：更偏执行质量与上下文纪律，产品和组织治理层需要自己补足。

text
主会话保持轻量

  -> 阶段循环驱动任务

  -> fresh-context subagents 执行重任务

  -> STATE.md / CONTEXT.md 保存状态

  -> Verify 后再 Ship

05
PART

Skills：不接管流程，只补工程纪律
SKILL · COMPOSABLE

— Matt Pocock Skills 横幅

Matt Pocock Skills 的立场和前三者明显不同。它不建一个大框架，而是把真实工程里的失败模式拆成小技能。

•需求没对齐：用 grill-me 或 grill-with-docs 先问清楚。

•术语混乱：用 shared language、CONTEXT.md 和 ADR 建立项目共享语言。

•代码跑不起来：用 tdd 和 diagnosing-bugs 建立反馈循环。

•代码库变泥球：用 to-spec 和 improve-codebase-architecture 做持续修复。

•优势：轻量、可改、可组合，迁移成本低。

•限制：不会替你设计整条开发流程，团队工程纪律弱时只装 skills 不会自动变强。

06
PART

怎么选：看接管哪一层
DECISION · GUIDE

— 四种方法选择决策图

可以先问四个问题：你要统一团队开发流程吗？你最怕什么失败模式？你能接受多少流程资产？你希望框架替你决策，还是只提醒你？

•团队从 0 到 1 做复杂产品：先看 BMAD。

•组织想把需求、计划、任务治理起来：先看 Spec Kit。

•长任务经常因为上下文膨胀而失真：先看 GSD Core。

•个人或小团队想保持控制权，只补工程纪律：先看 Matt Pocock Skills。

「真正要避免的，是在一个团队里同时引入多套最高指挥部，最后人和 Agent 都不知道听谁的。」

///
LAST

结语：从 prompt 走向操作系统
SUMMARY

这四个项目共同说明了一件事：Agent 开发已经不再只是写几个提示词，而是在重建软件工程的操作层。

BMAD 把它做成多角色协作系统，Spec Kit 把它做成规范资产，GSD 把它做成上下文工程循环，Matt Pocock Skills 把它做成可组合工程纪律。

如果你正在给团队选型，别先问哪个最火。更应该先问：我们到底缺的是流程、规范、上下文，还是工程习惯？

「答案不同，工具就不同。」

声明
本文由山行整理自：GSD Core、BMAD METHOD、Spec Kit、Matt Pocock Skills，如果对您有帮助，请帮忙点赞、关注、收藏，谢谢～
来源：https://github.com/open-gsd/gsd-core ｜ https://github.com/bmad-code-org/BMAD-METHOD ｜ https://github.com/github/spec-kit ｜ https://github.com/mattpocock/skills