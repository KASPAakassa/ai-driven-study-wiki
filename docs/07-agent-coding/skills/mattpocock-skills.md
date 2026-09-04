# Matt Pocock 的 "Skills For Real Engineers":一个值得借鉴的 Agent Skill 集合

> **一句话摘要**:TypeScript 社区知名作者 Matt Pocock 开源的个人 Agent skills 集合——针对真实工程(而非 vibe coding)的常见失败模式,设计成"小、易改编、可组合、模型无关"的 skill 包。本文总结其设计哲学、四个核心解法与完整 skill 清单。
>
> **来源**:GitHub 仓库 mattpocock/skills,https://github.com/mattpocock/skills

## 概念

**仓库定位**:Matt Pocock(Total TypeScript 课程作者)日常真实工程中使用的 Agent skills 集合,副标题 "Skills For Real Engineers"。它不是又一个"接管整个开发流程"的框架,而是一组**小而精的可复用纪律**。

**设计哲学**(作者原话):

- **小、易改编、可组合**:不像 GSD、BMAD、Spec-Kit 那样"拥有流程"(流程出 bug 时很难排查),这些 skill 是可以 hack 的零件;
- **模型无关**:与 Claude Code、Codex 等任何 coding agent 配合;
- **基于几十年工程经验**:大量引用《The Pragmatic Programmer》、DDD、Kent Beck、John Ousterhout 的《A Philosophy of Software Design》。

**安装方式**(三选一):

```bash
# 方式一:Claude Code 官方插件(只读、自动更新,订阅而非 fork)
claude plugins install mattpocock-skills
# 或会话内 /plugin install mattpocock-skills

# 方式二:复制为可编辑文件(Codex 及其他 agent,也可用于 Claude Code)
npx skills@latest add mattpocock/skills
# 拉取我的最新改动: npx skills update

# 方式三:装完每个仓库运行一次初始化
# /setup-matt-pocock-skills   —— 选 issue tracker(GitHub/Linear/本地文件)、triage 标签、文档存放位置
```

## 原理:四个失败模式与对应解法

作者构建这些 skill 的动机,是修复 coding agent 的**四个常见失败模式**——这也是整个仓库的思想骨架:

### 失败模式 1:Agent 没做我想做的(沟通错位)

> "没有人确切知道自己想要什么。" —— 《The Pragmatic Programmer》

最常见失败模式是**错位(misalignment)**:你以为说清楚了,agent 却理解偏了。修复方法是 **grilling session(拷问会话)**——反过来让 agent 持续向你提问,直到需求树的每个分支都被敲定。

- [`/grill-me`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me) —— 非代码场景;
- [`/grill-with-docs`](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs) —— 拷问的同时构建项目领域模型。**这是仓库里最受欢迎、作者认为最强大的技巧**。

### 失败模式 2:Agent 太啰嗦(缺少共享语言)

> "有了统一语言,开发者之间的对话和代码的表达都源自同一个领域模型。" —— Eric Evans, DDD

Agent 被丢进项目后要现场猜行话,于是"20 个词能说清的事用 200 个词"。修复:**建立共享语言文档**——`CONTEXT.md`(项目语境/术语表)+ **ADR**(架构决策记录)。

!!! tip "共享语言的连锁收益"
    - 变量、函数、文件名用共享语言**命名一致**,代码库对 agent 更可导航;
    - agent 思考时**省 token**(语言更精炼);
    - 例:把 "There's a problem when a lesson inside a section of a course is made real" 精炼为 "There's a problem with the **materialization cascade**"。

### 失败模式 3:代码不 work(反馈循环缺失)

> "永远小步走。反馈的速度就是你的速度上限。" —— 《The Pragmatic Programmer》

对齐了仍然产出垃圾 → 缺反馈循环。修复:静态类型 + 浏览器访问 + **自动化测试**,尤其是 **red-green-refactor(TDD)**。

- [`/tdd`](https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd) —— 先写失败测试再修复,给 agent 一致且即时的反馈;
- [`/diagnosing-bugs`](https://github.com/mattpocock/skills/tree/main/skills/engineering/diagnosing-bugs) —— 把调试最佳实践封装成有阶段门禁的纪律循环。

### 失败模式 4:建成了大泥球(Ball of Mud)

> "每天都要投资系统的设计。" —— Kent Beck
> "最好的模块是深模块:用简单接口暴露大量功能。" —— John Ousterhout

Agent 加速写码的同时也**加速了软件熵**。修复:在意代码设计。

- [`/to-spec`](https://github.com/mattpocock/skills/tree/main/skills/engineering/to-spec) —— 动手前先拷问你要动哪些模块、产出 spec;
- [`/improve-codebase-architecture`](https://github.com/mattpocock/skills/tree/main/skills/engineering/improve-codebase-architecture) —— 扫描代码库找"深化(deepening)"机会,输出可视化 HTML 报告;建议**每隔几天跑一次**。它是"调查"而非"救援"。

## Skill 清单

Skill 沿一个轴区分:**User-invoked(用户触发)**——只有手动输入 `/xxx` 才生效,负责编排;**Model-invoked(模型触发)**——任务匹配时 agent 可自动调用,承载可复用纪律。user-invoked 可以调用 model-invoked,但从不调用另一个 user-invoked。

### Engineering(工程,19 个)

**User-invoked(9 个)**

| Skill | 作用 |
| --- | --- |
| `ask-matt` | 路由器:问它"当前情况该用哪个 skill/流程" |
| `grill-with-docs` | 拷问会话,同时构建领域模型,内联更新 `CONTEXT.md` 与 ADR |
| `triage` | 用 triage 角色状态机流转 issue |
| `improve-codebase-architecture` | 扫描代码库找深化机会,HTML 报告 + 拷问 |
| `setup-matt-pocock-skills` | 每仓库初始化一次(issue tracker、triage 标签、文档布局) |
| `to-spec` | 把当前对话合成 spec 并发布到 issue tracker,无需采访 |
| `to-tickets` | 把计划/spec/对话拆成一组 tracer-bullet 票据,声明阻塞边 |
| `implement` | 按 spec/票据实现,在约定接缝处驱动 `/tdd`,提交前用 `/code-review` 收尾 |
| `wayfinder` | 规划超过一个 agent 会话容量的巨型工作:在 issue tracker 上建"决策票据地图",逐个解决直到路径清晰 |

**Model-invoked(10 个)**

| Skill | 作用 |
| --- | --- |
| `prototype` | 做一次性原型回答设计问题(状态/逻辑用单个 HTML 文件,UI 用多个可切换变体) |
| `diagnosing-bugs` | 有纪律的调试循环:让 bug 变红 → 最小化 → 假设 → 插桩 → 修复 → 回归 |
| `research` | 基于高可信一手来源调研,结论写成带引用的 Markdown 存进仓库 |
| `tdd` | red-green-refactor,一次一个垂直切片地开发/修 bug |
| `domain-modeling` | 主动构建并打磨领域模型,挑战术语、压力测试边界场景 |
| `codebase-design` | 深模块设计的共享纪律与词汇:小接口承载多行为,放在干净接缝处 |
| `code-review` | 双轴评审:Standards(仓库规范 + Fowler 坏味道基线)× Spec(是否忠实实现来源 issue/spec),并行子代理互不污染 |
| `resolving-merge-conflicts` | 逐 hunk 按"意图溯源到双方一手来源"解决冲突,绝不用 `--abort` |
| `wizard` | 生成交互式 bash 向导,带人类完成只有人能做的步骤(配 infra、设密钥、走陌生后台、一次性迁移) |

### Productivity(效率,7 个)

**User-invoked(5 个)**

| Skill | 作用 |
| --- | --- |
| `grill-me` | 被持续采访,直到设计树的每个分支都被敲定(非代码场景) |
| `handoff` | 把当前对话压缩成交接文档,让另一个 agent 接着干 |
| `teach` | 多会话教用户新技能,把当前目录当作有状态的教工作区 |
| `to-questionnaire` | 把一个人无法拍板的决策转成 Markdown 问卷,交给唯一能回答的人 |
| `wait-what` | 消息没看懂时立刻触发:用 `CONTEXT.md` 词汇重讲一遍 |

**Model-invoked(2 个)**

| Skill | 作用 |
| --- | --- |
| `grilling` | 底层采访原语,被 grill-me / grill-with-docs / triage / wayfinder / improve-codebase-architecture 复用 |
| `writing-for-agents` | 写"给 agent 看"的文档:skill、AGENTS.md/CLAUDE.md、任何 agent 会按指针读取的文档 |

### Misc(杂项,4 个,不主动推广)

`git-guardrails-claude-code`(用 Claude Code hooks 拦截危险 git 命令)、`migrate-to-shoehorn`(测试断言迁移)、`scaffold-exercises`(习题目录脚手架)、`setup-pre-commit`(Husky + lint-staged 配置)。

### In-progress(开发中,6 个)

`claude-handoff`、`loop-me`、`setup-ts-deep-modules`、`writing-beats`、`writing-fragments`、`writing-shape`(写作向,探索中)。

## 核心 Skill 深度拆解

> 清单只回答"有什么",这一节回答"怎么用、为什么这么设计"——从原始 SKILL.md 与作者演讲提炼的关键细节,按使用场景组织。

### /zoom-out:上升抽象层,画领域地图

**用途**:你不熟悉某块代码,或已经钻进某个文件但忘了它为什么存在——打断"隧道视野",让 agent 暂停实现,先回答:这块代码属于哪个领域概念?谁调用它?它调用谁?背后有哪些不变量?和 CONTEXT.md 的术语怎么对应?是否受某个 ADR 约束?

**与 /improve-codebase-architecture 的区别**:后者找可深化的架构机会(候选重构、deletion test),前者只是"请给我讲讲这块"——**不急着提重构方案,更不直接改代码,目标是降低认知负担**。

**关键:必须用领域词汇解释**。如果用文件名解释,AI 容易输出"OrderService 调用 OrderRepository,然后调用 db client"这种"看似解释其实没解释"的话。更有用的地图:

> Checkout flow 里,Order Draft 是用户尚未支付前的临时订单。Order Finalization 会把 Draft 转成不可变 Order,并触发 Inventory Reservation。`OrderService.finalize()` 是这个转换的 seam,调用者主要来自 Payment Callback 和 Admin Retry。

第二种解释把代码放回了业务语言——你不只知道"谁调用谁",还知道"它为什么存在"。

### /diagnose 与 /triage:一个负责事实,一个负责流程

- **/diagnose 关心**:这个 bug 到底是什么、怎么复现、怎么证明修好了;
- **/triage 关心**:这个 issue 现在该等信息、给 agent、给人,还是不做。

真实项目里两者常连在一起:先 triage 一个 bug issue → 信息不够就 needs-info → 够了用 diagnose 建反馈回路 → 复现清楚再决定 ready-for-agent 还是 ready-for-human。

**/diagnose 的核心:反馈回路就是全部**——先建立一个 agent 能运行的 pass/fail 信号,再谈假设。六阶段:

| 阶段 | 目标 |
| --- | --- |
| Build a feedback loop | 搭一个快速、确定、可反复运行的失败信号 |
| Reproduce | 让这个信号复现用户描述的同一个 bug |
| Hypothesise | 列 3-5 个可证伪假设 |
| Instrument | 用最少探针验证假设 |
| Fix + regression test | 在正确测试面写回归测试,再修 |
| Cleanup + post-mortem | 清理临时探针,记录真实根因 |

反馈回路优先级(从最好到最兜底):失败测试 → curl/HTTP script → CLI+fixture → Headless browser → Replay captured trace → Throwaway harness → Property/fuzz loop → Bisection/differential loop → HITL script。**硬判断:没有回路,不要进入假设阶段——没有信号,所有分析都只是"看起来像"。**

### /tdd:把"成功标准"变成 agent 能听懂的反馈

Matt 演讲的第三个失败模式:"AI 做对了东西,但跑不起来"。修法是给 AI 装反馈基础设施:**TypeScript、让 LLM 能访问浏览器自己看页面、自动化测试**。

**核心原则**:测试通过公共接口验证行为,不测实现细节;好测试是 integration-style 的,读起来像规格("重命名一个内部函数,测试就跪了——那这个测试在测实现而不是行为")。

**工作流(带 checklist)**:

1. **Planning**:写码前对齐——确认接口改动、确认要测哪些行为(按优先级)、找 deep module 机会、设计可测接口;**关键:不是所有行为都值得测,把火力集中到核心路径和复杂逻辑**("You can't test everything");
2. **Tracer Bullet(曳光弹)**:写一个端到端测试验证一件事——RED(失败)→ GREEN(最小实现通过);不是先 schema 再 API 再 UI,而是**切一条最薄但贯穿全栈的路径**;
3. **Incremental Loop**:每个行为重复 RED→GREEN——一次一个测试、只写够通过当前测试的代码、**不要预判未来的测试**(AI 会忍不住"反正以后也要支持 X,顺便加上吧"——这就开始横向切片化了);
4. **Refactor**:测试都过之后再看重构机会——**Never refactor while RED**(红着重构 = 同时改测试和代码 = 你不知道是测试错还是代码错)。

**Per-Cycle Checklist**(每个红绿循环自检):测试描述行为而非实现 / 只用公共接口 / 能扛住内部重构 / 代码对此测试最小 / 没有投机性功能。

**关于 Mock 的强烈观点**:mock 内部协作者 = 测试和实现 1:1 耦合 = 重构时测试集体跪。偏好 integration-style——尽量用真实数据库(in-memory 或 testcontainers)、真实 HTTP(MSW)、真实文件系统(tmp dir),只在真正昂贵或不稳定的边界(如 OpenAI API)才 mock。**"好代码库 = 容易测试的代码库"**——如果必须 mock 一堆才能测,说明代码结构有问题,先改架构。

**TDD 在 AI 时代的新意义**(引用 Karpathy):

> LLM 极擅长循环直到达成具体目标。不要告诉它做什么,给它成功标准然后看它跑。

"成功标准"最好的形式就是测试——机器可验证、二值化、不会被狡辩。/tdd 不只是质量保证手段,它**是 agent loop 的输入接口**:每个红绿循环都是一次完整的"输入 → 行动 → 反馈",AI 在循环里学到真实情况,下次更准。

### /to-prd 与 /to-issues:把对话决策切成可领取的工作包

解决 AI 编程的常见断点:和 AI 讨论清楚需求后直接"全部实现"会输出太大、难 review、难测试、难交给 AFK agent。正确做法:**先固化成 PRD,再切成小到可以独立领取的 issue**。

**工作流位置**:`/grill-me` 或 `/grill-with-docs`(谈清楚)→ `/to-prd`(凝固成 PRD)→ `/to-issues`(切成 vertical slice)→ `/tdd`(一个 slice 一个 slice 跑红绿)。

**/to-prd 的关键约束**:SKILL.md 开头一句很重要的话——"This skill takes the current conversation context and codebase understanding and produces a PRD. **Do NOT interview the user** — just synthesize what you already know."不再问问题(那是 grill 阶段的事),只做合成,所以**不要清 context 再跑 to-prd**。

PRD 模板要点:Problem Statement / Solution(从用户视角)/ **User Stories 要 LONG, numbered list**(逼你穷举完整功能点,避免"我以为说清楚了"的盲点)/ Implementation Decisions(**不写文件路径或代码片段**——"they may end up being outdated very quickly",但模块边界、接口契约生命周期更长)/ Testing Decisions / **Out of Scope(必须有**——后续切 issue 时的边界保险)/ Further Notes。

**/to-issues 的核心概念:Vertical Slice(纵向切片)**——"Each issue is a thin vertical slice cutting through ALL integration layers end-to-end, NOT a horizontal slice of one layer."做"评论功能"时,错误方式是横向切(schema / API / UI / 测试四个 issue),正确方式是纵向切:**Issue 1: "访客可以提交一条匿名评论"(schema + API + UI + test 全在内,但范围小到只能匿名)**。切得够细,AFK agent 才能独立领取并完成。

### /caveman:极限压缩沟通(少 token 模式)

要求 agent 去掉寒暄、填充词、过度解释和模糊缓冲,只保留技术信息。适合:高频迭代不想读长回复、debug 时只要事实/原因/下一步、长上下文快满需要压缩输出。**注意它会持续生效直到你说退出**——建议当临时档位而非长期默认,高风险操作和复杂多步骤指令太短容易误读。

### /setup-matt-pocock-skills:把隐含约定外显化

为什么装完必须跑一次 setup:to-prd、to-issues、triage、diagnose、tdd、improve-codebase-architecture、zoom-out 都需要**同一批项目上下文**,如果每个 skill 临时问一遍流程会很碎。它回答三个工程问题:

1. **Issue tracker 在哪**(GitHub/GitLab/本地 markdown/其他)→ 决定 to-prd、to-issues、triage 怎么建 issue;
2. **Triage 标签怎么映射**(needs-triage、needs-info、ready-for-agent 对应仓库里哪些真实标签)→ 避免 skill 自创新标签把 tracker 弄脏;
3. **领域文档在哪里**(单一 CONTEXT.md 还是 CONTEXT-MAP.md + 分区 ADR)→ grill-with-docs、diagnose、tdd、zoom-out 都靠它。

这套 skills 的核心思路是"小而可组合",代价是它们不接管整个项目流程,所以必须知道项目真实约定——**setup 的价值不是自动化,而是把隐含约定外显化**。

## 代码 / 实现:SKILL 长什么样

每个 skill 是仓库里一个目录,核心是 `SKILL.md`(frontmatter + markdown 指令),可选配 `agents/openai.yaml` 等模型适配、脚本与配套文档:

```markdown
---
name: wayfinder
description: Plan a huge chunk of work — more than one agent session can hold —
  as a shared map of decision tickets on your issue tracker, and resolve them
  one at a time until the way to the destination is clear.
disable-model-invocation: true
---

# 正文:给 agent 的完整操作指令(何时用、怎么用、输出什么)

## The Map
...
```

**格式要点**:

- `name` + `description` 是必须的 frontmatter(供 agent 决定何时调用);
- `disable-model-invocation: true` 表示只能用户手动触发(user-invoked);
- 正文是**面向 agent 的操作手册**,不是给人读的散文:定义目标、步骤、边界、输出格式;
- 复杂 skill 带配套文档(如 `domain-modeling` 的 ADR-FORMAT、`codebase-design` 的 DESIGN-IT-TWICE.md)与脚本(如 `wizard` 的 template.sh)。

这也呼应了本 Wiki [Skill 收藏](index.md) 的收录原则:**原样保存文件 + 写清"怎么用、什么时候用"**。

## 实践 / 应用:如何借鉴这套体系

### 开箱即用

1. 按上文三选一安装;
2. 每仓库运行一次 `/setup-matt-pocock-skills`(选 issue tracker、triage 标签、文档位置);
3. 开始使用。

### 值得复制的核心工作流

```
/grill-with-docs   ① 拷问 + 建领域模型(先对齐,再动手)
/to-spec           ② 把共识沉淀成 spec 发布到 tracker
/to-tickets        ③ 拆成带阻塞边的票据
/implement         ④ 按票实现(TDD 驱动,代码评审收尾)
/wayfinder         ⑤ 巨型工作:决策票据地图逐个击破
```

### 值得吸收的设计理念(即使不用它的 skill)

1. **先拷问再动手**:用"让 agent 采访你"代替"你给 agent 下指令",是消除错位的最强杠杆;
2. **共享语言进仓库**:`CONTEXT.md` + ADR 让 agent 少猜、少啰嗦、命名一致;
3. **把工程纪律做成可调用 skill**:TDD、调试、评审、冲突解决这些"资深工程师经验",从人脑变成 agent 可调用的资产——与本站 [AI Friendly 架构](../../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md) 中 SKILL 化的思路完全一致;
4. **双轨设计**:user-invoked 编排 / model-invoked 复用,避免 skill 互相调用失控。

## 姊妹项目:Superpowers——247k Star 的工程化流程 Skills 集合

!!! tip "同一个思路,另一种规模"
    Matt Pocock 的集合主打"小而精的纪律";**Superpowers**(https://github.com/obra/superpowers,247k Star)则走"全流程框架"路线——给 Coding Agent 装一整套工程化开发流程:**先澄清需求 → 写计划 → TDD 实现 → 代码审查 + 质量验证**。两者互补:纪律型适合想保留控制权的个人,流程型适合想"整包交付"的团队。

**v6 重构:质量、成本与可控性的再平衡**——作者用 Claude Fable 5 重写了 Subagent Driven Development 审查链路,在 Anthropic eval benchmarks 上**质量不变、构建提速 50%、Token 消耗降 60%**。四个关键改动,对任何 skill 集合都有借鉴价值:

1. **双审查合并**:原来"spec compliance review(需求符合性)+ code quality review(代码质量)"两个 reviewer 各读一遍 diff;v6 合并为一个 `task-reviewer-prompt`,**一名 reviewer 一次读取、两类判断**,一个修复轮次同时处理两类问题——省掉重复的上下文读取;
2. **文件化而非粘贴**:过去把大段 diff 粘贴进上下文、reviewer 反复跑 git 重建材料;v6 用 `task-brief` 和 `review-package` 两个脚本,**把任务文本、审查 diff 和元数据提前写成文件**交给 subagent 读取——diff 不再长期占据昂贵上下文,工具调用也大幅减少;
3. **计划预检(pre-flight read)**:第一个任务开始前,controller 先检查计划是否存在内部冲突、或包含会被 reviewer 判为缺陷的要求——**像真实团队的方案评审**,与其等代码写到一半才发现需求打架,不如执行前一次性暴露(长任务尤其重要);
4. **跨 harness 适配**:把"使用 Task tool""写进 CLAUDE.md"这类 Claude Code 口吻,改成通用动作("派发一个 subagent""写入你的 instructions file"),**再用映射文件适配** Claude Code / Codex / Copilot / Pi / Antigravity / Kimi Code 等环境。

!!! warning "给 skill 作者的启示"
    Superpowers v6 的四个改动本质上是一条经验:**skill 的 Token 效率来自"减少重复消费"**——合并重复审查、用文件代替上下文常驻、事前预检避免返工、写通用动作 + 映射适配。这与本文 Matt Pocock 的"纪律 SKILL 化"是同一思路的两面:前者管质量,后者管成本。

**安装**(三选一):

```bash
# Claude Code:官方插件市场
/plugin install superpowers@claude-plugins-official

# Kimi Code:插件管理器 Marketplace 或直接安装
/plugins install https://github.com/obra/superpowers

# 其他 harness:见 https://github.com/obra/superpowers#installation
```

## 总结

- 定位:**真实工程可用的 Agent skill 集合**,小而可组合、模型无关,基于经典工程经验(Pragmatic Programmer / DDD / Ousterhout)。
- 四个失败模式与解法:沟通错位(grilling)、太啰嗦(共享语言)、代码不 work(TDD/调试循环)、大泥球(深度设计)。
- 共 36 个 skill:Engineering 19 + Productivity 7 + Misc 4 + In-progress 6,沿 user-invoked / model-invoked 双轴组织。
- 核心工作流:grill-me/grill-with-docs(对齐)→ to-prd(固化 PRD)→ to-issues(切 vertical slice)→ tdd(逐 slice 红绿)→ improve-codebase-architecture(深化);装完先跑一次 setup 把项目约定外显化。
- 深度拆解要点:zoom-out(领域语言画地图)、diagnose(反馈回路优先,triage 管流程)、tdd(曳光弹 + 不 mock 内部协作者 + "成功标准"即 agent loop 输入)、to-prd/to-issues(纵向切片而非横向切片)。
- 借鉴价值:即使不直接使用,其"grilling 对齐、共享语言、纪律 SKILL 化"的设计也值得复刻到自己的 Agent 工作流。

## 延伸阅读

- 仓库原文:https://github.com/mattpocock/skills(README 即最好的文档;各 skill 目录下的 SKILL.md 是深度拆解的一手来源)
- 姊妹项目:Superpowers,https://github.com/obra/superpowers;v6 公告 https://primeradiant.com/blog/2026/superpowers-6.html;RELEASE-NOTES https://github.com/obra/superpowers/blob/main/RELEASE-NOTES.md
- 理论源头:《The Pragmatic Programmer》、《Domain-Driven Design》(Eric Evans)、《A Philosophy of Software Design》(John Ousterhout)、《The Design of Design》(Frederick P. Brooks)
- 站内:[Skill 收藏](index.md)、[个人 Agent Coding 经验](../index.md)、[AI Friendly 后端架构](../../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md)(SKILL/Harness 章节)、[Agent 开发实践](../../03-agents/agent-practice.md)、[AI 时代 TDD 实践](../experience/ai-tdd-practice.md)(Codex 侧 TDD 落地)、[Spec Kit:GitHub 官方规格驱动工具](spec-kit-github.md)(规格驱动生态对照)
