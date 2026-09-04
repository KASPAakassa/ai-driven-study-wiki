# Agent 开发方法选型:BMAD / Spec Kit / GSD / Skills 的控制层级对比

> **一句话摘要**:当 Agent 真的参与开发,团队该把多少流程交给它?四种 Agent 开发方法——BMAD METHOD、Spec Kit、GSD Core、Matt Pocock Skills——都在解决 Agent 编程失控问题,但切入层级完全不同:**BMAD 管团队流程,Spec Kit 管规范入口,GSD 管上下文质量,Skills 管工程习惯**。本文提炼这套"控制层级"坐标系与选型框架,作为 Agent 开发方法设计(而非框架/架构)的决策参考。
>
> **来源**:微信公众号「山行AI」《四种 Agent 开发方法对比:BMAD、Spec Kit、GSD 和 Skills 怎么选》,https://mp.weixin.qq.com/s/uIRPK1Hy96lsW7gLnuvSFw;Star 数据抓取于 2026-07-30;原始资料存档于 `docs/inbox/agent-methods-source.md`

## 概念:不是"哪个最火",而是"接管到哪一层"

过去半年,AI 编程讨论从"模型能不能写代码"转向"**当 Agent 真的参与开发,团队到底该把多少流程交给它**"。四个项目不是简单替代关系,真正差别在于 **Agent 接管到哪一层**:

> **BMAD 管团队流程,Spec Kit 管规范入口,GSD 管上下文质量,Skills 管工程习惯。**

| 方法 | Star | 定位 | 接管层级 |
| --- | --- | --- | --- |
| **BMAD METHOD** | 51,265 | 多角色敏捷框架,34+ workflows 和模块生态 | 团队流程 |
| **Spec Kit** | 124,531 | spec-driven development 工具包(constitution/spec/plan/tasks/implement) | 规范入口 |
| **GSD Core** | 7,415 | 上下文工程框架(Discuss/Plan/Execute/Verify/Ship 五阶段) | 上下文质量 |
| **Matt Pocock Skills** | 195,022 | 工程技能集合(可编辑、可组合、按失败模式调用) | 工程习惯 |

## 原理:四种方法的机制与边界

### 1. BMAD METHOD:多角色敏捷框架(管流程)

不是单点提示词,而是一套 **AI-driven agile development 框架**——把需求澄清、产品设计、架构、UX、开发、测试和研究拆成多个专家 Agent 与工作流。

- **核心能力**:34+ workflows、多 Agent 角色协作、Party Mode、模块生态、Web Bundles;
- **架构模式**:业务目标 → 多角色 Agent 拆解 → 结构化 workflow 编排 → IDE/Agent 环境执行 → 沉淀 PRD、架构、UX、任务和研究产物;
- **优势**:体系完整、角色边界清晰,适合复杂产品和多人协作;
- **限制**:流程较重,团队需要接受它的工作方式;个人快速修 bug 时可能显得过于正式。

### 2. Spec Kit:规格说明变成入口(管规范)

强调 **Spec-Driven Development**——先定义要构建什么,再让 AI coding agent 去实现。关键观念:**规格说明不再只是写完就丢的脚手架,而是会继续参与实现过程的可执行资产**。

- **核心流程**:`specify init` → `/speckit.constitution` → `/speckit.specify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`;
- **扩展机制**:Extension 增加新能力,Preset 改造既有 workflow,Bundle 组合角色化安装包;
- **优势**:组织治理能力强,能把需求、计划、任务和审查沉淀为资产;
- **限制**:spec 写得差,后面的 plan 和 tasks 也会跟着偏;流程资产越多,维护成本越高。

### 3. GSD Core:对抗长任务上下文失真(管上下文)

核心不是更多角色,而是 **context engineering**——AI 编程规模化时最常见的问题,是上下文不断膨胀后输出质量下降(context rot)。

- **五阶段循环**:Discuss、Plan、Execute、Verify、Ship;
- **关键机制**:重研究、规划和执行放进 **fresh-context subagents**,主会话保持精简;
- **状态资产**:STATE.md 和 CONTEXT.md 保存跨 session 的结构化记忆;
- **优势**:适合长任务、多会话和跨 Agent 协作;
- **限制**:更偏执行质量与上下文纪律,产品和组织治理层需要自己补足。

### 4. Matt Pocock Skills:不接管流程,只补工程纪律(管习惯)

立场与前三者明显不同——不建大框架,而是把真实工程里的**失败模式**拆成小技能:

| 失败模式 | 对应 Skill |
| --- | --- |
| 需求没对齐 | `grill-me` / `grill-with-docs`(先问清楚) |
| 术语混乱 | shared language、CONTEXT.md、ADR(建立共享语言) |
| 代码跑不起来 | `tdd`、`diagnosing-bugs`(建立反馈循环) |
| 代码库变泥球 | `to-spec`、`improve-codebase-architecture`(持续修复) |

- **优势**:轻量、可改、可组合,迁移成本低;
- **限制**:不会替你设计整条开发流程;团队工程纪律弱时只装 skills 不会自动变强。

## 实践 / 应用:怎么选——看接管哪一层

**选型决策四问**:

1. 你要**统一团队开发流程**吗?(→ BMAD)
2. 你**最怕什么失败模式**?(→ 对应 Skills 或 GSD)
3. 你能**接受多少流程资产**?(Spec Kit 资产多、Skills 资产少)
4. 你希望框架**替你决策**,还是**只提醒你**?(→ BMAD/Spec Kit 替你决策,GSD/Skills 偏提醒)

**场景推荐**:

| 场景 | 先看 |
| --- | --- |
| 团队从 0 到 1 做复杂产品 | **BMAD**(流程完整、角色清晰) |
| 组织想把需求、计划、任务治理起来 | **Spec Kit**(规范资产化) |
| 长任务经常因上下文膨胀而失真 | **GSD Core**(上下文工程循环) |
| 个人/小团队想保持控制权,只补工程纪律 | **Matt Pocock Skills**(可组合纪律) |

!!! warning "避免多套最高指挥部"
    **真正要避免的,是在一个团队里同时引入多套最高指挥部,最后人和 Agent 都不知道听谁的。** 选型时先问"我们到底缺的是流程、规范、上下文,还是工程习惯?"——答案不同,工具就不同。

## 总结

- **核心视角**:四种方法不是替代关系,差别在 **Agent 接管到哪一层**——流程(BMAD)/ 规范(Spec Kit)/ 上下文(GSD)/ 工程习惯(Skills);
- **BMAD**:多角色敏捷框架(34+ workflows),适合复杂产品多人协作,流程较重;
- **Spec Kit**:spec 是可执行资产(constitution→spec→plan→tasks→implement),组织治理强、spec 质量是命门;
- **GSD**:五阶段循环 + fresh-context subagents + STATE.md/CONTEXT.md,对抗 context rot;
- **Skills**:按失败模式调用的可组合小技能,轻量但需团队已有纪律基础;
- **选型铁律**:四问(流程统一?失败模式?流程资产?谁决策?)+ 避免多套最高指挥部;
- **下一步**:深入各方法见站内专文——[BMAD 补充](agent-frameworks.md)、[Spec Kit](../07-agent-coding/skills/spec-kit-github.md)、[GSD](../07-agent-coding/skills/gsd-workflow-skill.md)、[Matt Pocock Skills](../07-agent-coding/skills/mattpocock-skills.md)。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/uIRPK1Hy96lsW7gLnuvSFw
- 仓库:BMAD https://github.com/bmad-code-org/BMAD-METHOD · Spec Kit https://github.com/github/spec-kit · GSD Core https://github.com/open-gsd/gsd-core · Matt Pocock https://github.com/mattpocock/skills
- 站内:[Agent 框架选型地图](agent-framework-selection.md)(运行时框架的三层控制权模型,与此文"开发方法控制层级"互补)、[Agent 架构全景](agent-architecture-panorama.md)(架构档位)、[Spec Kit](../07-agent-coding/skills/spec-kit-github.md)、[GSD 工作流系统](../07-agent-coding/skills/gsd-workflow-skill.md)、[Matt Pocock Skills](../07-agent-coding/skills/mattpocock-skills.md)
