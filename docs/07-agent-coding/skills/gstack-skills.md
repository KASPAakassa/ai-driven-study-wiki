# gstack:YC CEO 的角色化虚拟工程团队——23+ 个 Skill 把 Claude Code 变成一支团队

> **一句话摘要**:Y Combinator CEO Garry Tan 开源的角色化技能集——每个 Skill 对应一个专业角色(CEO、工程经理、设计师、QA、安全官、发布工程师),把 Claude Code 从单一 AI 助手变成一支虚拟工程团队。作者用它 60 天发布 60 万行生产代码,核心贡献是 **Browse Daemon(给 AI 装上眼睛)** 与**角色分解设计模式**。
>
> **来源**:GitHub 仓库 garrytan/gstack,https://github.com/garrytan/gstack;中文解读整理自 Yu 的赛博工位(https://yudesk.dev/docs/notes)

## 概念

**gstack** 由 Y Combinator CEO **Garry Tan** 创建(2026 年 3 月开源,MIT 许可,3 周内 60,500+ stars)。它包含 **23+ 个 Slash Commands**,每个 skill 对应一个专业角色——CEO、工程经理、设计师、QA Lead、安全官、发布工程师——赋予 AI 不同的思维模式和专业视角。

Garry Tan 背景:14 岁写代码、斯坦福计算机工程、**Palantir 第 10 号员工**、联合创办 Posterous(被 Twitter 收购)、2023 年起任 YC President & CEO。他自称**从不手写代码**,用 gstack 60 天发布 60 万行生产代码(35% 是测试),其中一个项目 garylist.org 21 天上线 15 万行代码——质量超过他之前花 500 万美元、两年、10 个工程师做的创业项目。

**它要解决的问题**不是"怎么让 AI 写更多代码",而是"怎么让 AI 编程从随机应变变成可靠交付"。答案:**把开发流程拆给一支虚拟工程团队,由人来指挥角色切换**。

### 工具生态中的位置

| 维度 | Ralph Wiggum | GSD | SpecKit | Superpowers | gstack |
| --- | --- | --- | --- | --- | --- |
| 核心定位 | 无限循环迭代 | 上下文工程 + 规格驱动 | 需求→规格→任务 | 流程纪律 + TDD | 角色化虚拟团队 |
| 核心模式 | Bash 循环 + 新进程 | Phase-based Roadmap | Spec → Plan → Tasks | 严格开发流水线 | Sprint 七步流程 |
| 人类参与 | Hands-off (AFK) | 每阶段验证 | 规格审批 | 每步确认 | 每阶段角色审查 |
| 独特能力 | 无限迭代 | Context Rot 管理 | 需求追溯 | 强制 TDD | 浏览器自动化 + 多角色审查 |

关键规律:**这些工具不互相竞争,而是从不同维度解决 AI 编程问题**。Superpowers 用流程纪律保证质量(从 1 到 N 工程落地),GSD 用上下文工程管理复杂项目,gstack 用**角色分解提升决策质量**(从 0 到 1 产品构建)——CEO 视角审产品、工程经理审架构、QA 跑真实浏览器。

## 原理:核心工作流与三大哲学

### The Sprint 七步走

gstack 把开发组织为 **Think → Plan → Build → Review → Test → Ship → Reflect** 循环,叫"The Sprint"——不是敏捷 Sprint,而是"**角色依次登场**"的开发节奏:

**1. Think — 产品门诊** `/office-hours`:灵感来自 YC Office Hours。AI 问你 6 个逼迫性问题——谁具体需要这个?他们今天没有它怎么办?为什么现在很紧迫?你怎么知道它能用?如果什么都不做会怎样?你能发布的最小版本是什么?目的不是写代码,而是**写代码前重新审视问题本身**。

**2. Plan — 多角色审查** `/plan-ceo-review`(CEO 视角,找 10 星级产品)、`/plan-eng-review`(工程经理,锁定架构边界)、`/plan-design-review`(设计师,0-10 评分)、`/autoplan`(自动依次跑三个审查)。CEO Review 本质是"Founder Mode"——退后一步问"这个产品真正的目的是什么?",支持扩大/选择性扩展/保持/缩小范围四种模式。

**3. Build — 编码实现**:按审查通过的计划,用标准 Claude Code 能力编码。

**4. Review — 平行专家审查** `/review`:一次性派出 **7 个并行子代理**,分别从测试、可维护性、安全、性能、数据迁移、API 合约、红队攻击 7 个角度审查,明显问题自动修复。

**5. Test — 真实浏览器 QA** `/qa`:启动真实 headless Chromium,打开应用、点击按钮、填表单、截图——像真人测试员。发现 bug 自动修复、生成回归测试、重新验证。

**6. Ship — 一键发布** `/ship`:同步主分支 → 跑测试 → 审查 diff → 更新版本号和 CHANGELOG → 提交 → 推送 → 创建 PR。无测试框架时自动搭建。

**7. Reflect — 回顾与学习** `/retro`:工程经理风格周报——提交历史、测试比例、代码质量趋势,跟踪"连续发布天数"。

### 技术原理:Browse Daemon 与角色分解

**Browse Daemon:给 AI 装上眼睛** —— gstack 最独特的技术贡献。一个长驻的 headless Chromium 实例,通过 localhost HTTP 通信:首次调用启动浏览器(约 3 秒),之后每次命令只需 **100-200ms**。AI 真正"看到"应用而不是猜 DOM 结构。配套 **Ref System(元素引用 @e1, @e2)**,通过 accessibility tree 定位元素,不需要写 CSS 选择器——这是被社区(包括批评者)公认的"真正有技术含量的贡献"。

**角色分解:不是一个 agent,而是一支团队** —— 把角色拆成独立 prompt 文件,在不同阶段切换"大脑模式":founder thinking、engineering rigor、paranoid review、fast execution。核心洞察:**规划不等于审查,审查不等于发布,创始人品味和工程严谨是完全不同的思维模式**。

### 三大哲学(ETHOS.md)

1. **Boil the Lake(煮沸整个湖)**:当 AI 让完整性的边际成本趋近零时,永远选择完整实现——100% 测试覆盖、所有边界情况、所有错误路径。"发布捷径"是旧时代思维;
2. **Search Before Building(先搜索再构建)**:三层知识——久经考验的模式、新且流行的方案、第一性原理。先理解所有人在做什么,质疑他们的假设,再发现为什么常规方案是错的;
3. **User Sovereignty(用户主权)**:AI 推荐,人类决定。即使两个 AI 模型达成共识,用户判断仍然优先——因为用户有领域知识、战略视角和品味。

## 代码 / 实现:安装与命令体系

### 安装(30 秒,全局推荐)

前置:Claude Code、Git、**Bun v1.0+**(gstack 基于 Bun;Windows 还需 Node.js)。

```bash
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup
```

`./setup` 做三件事:把 skill 信息加入 `CLAUDE.md`、把 skill 文件放入 skills 目录、安装 Playwright + Chromium(用于 /browse 和 /qa)。

**多 Agent 支持**:`./setup --host codex|opencode|cursor|factory|slate|kiro|hermes|gbrain|openclaw`——已支持 10 个 AI 编程 Agent,各 host 的 skill 装在独立路径互不干扰。

**Team Mode(团队共享 + 自动更新,推荐)**:开发者全局安装,仓库只记录"我们用 gstack",更新自动发生:

```bash
(cd ~/.claude/skills/gstack && ./setup --team) && \
~/.claude/skills/gstack/bin/gstack-team-init required && \
git add .claude/ CLAUDE.md && git commit -m "require gstack for AI-assisted work"
```

更新:`cd ~/.claude/skills/gstack && git pull && ./setup`,或 `/gstack-upgrade`。

### 命令参考(按功能分类)

**Sprint 流程**:`/office-hours`(6 个逼迫性问题)、`/plan-ceo-review`、`/plan-eng-review`、`/plan-design-review`、`/plan-devex-review`(DX 负责人,20-45 个问题)、`/autoplan`(自动 CEO→设计→工程→DX 审查,仅上抛"品味决策")。

**设计**:`/design-consultation`(完整设计系统,产出 DESIGN.md)、`/design-shotgun`(多方案浏览器对比)、`/design-html`(生产级 HTML/CSS,自动检测 React/Svelte/Vue)。

**审查与安全**:`/review`(Staff 工程师,找"能过 CI 但会在生产爆炸"的 bug)、`/investigate`(根因调试,铁律:不找到根因不修 bug)、`/design-review`(视觉审计+自动修复)、`/devex-review`(真实跑 onboarding、计时 TTHW)、`/cso`(安全官,OWASP Top 10 + STRIDE,8/10 置信度门槛)。

**测试与 QA**:`/qa`(真实浏览器测试+修复+回归)、`/qa-only`(仅报告)、`/benchmark`(Core Web Vitals 基线)、`/browse`(~100ms 浏览器命令)、`/open-gstack-browser`(可见的 AI 控制 Chromium)、`/setup-browser-cookies`(导入真实浏览器 cookie)、`/pair-agent`(跨 Agent 共享浏览器,ngrok 隧道)。

**发布与运维**:`/ship`、`/land-and-deploy`(合并 PR→CI→部署→验证)、`/canary`(金丝雀监控)、`/setup-deploy`(自动检测平台 Fly.io/Render/Vercel/Netlify/Heroku/GHA)、`/setup-gbrain`。

**回顾与学习**:`/retro`(团队感知周报)、`/document-release`(文档匹配已发布代码)、`/learn`(跨会话学习记忆)、`/context-save` `/context-restore`(checkpoint 模式)。

**安全防护**:`/careful`(危险操作警告)、`/freeze` `/unfreeze`(锁定编辑范围)、`/guard`(组合最高安全)、`/checkpoint`(状态快照)。

**工具集成**:`/codex`(Codex 独立审查,跨模型重叠分析)、`/health`(0-10 综合评分)、`/skillify`(工作流固化为 skill)、`/scrape`、`/landing-report`、`/make-pdf`。

### 前端 Skill 六层流水线

设计基建(`/design-consultation`、`/teach-impeccable`、`/brand-guidelines`)→ 设计探索(`/design-shotgun`、`/frontend-design`、`/canvas-design`)→ 设计实现(`/design-html`、`/mobile-responsiveness`、`/adapt`、`/typeset`、`/arrange`)→ 设计增强(`/animate`、`/delight`、`/bolder`、`/colorize`、`/overdrive`、`/onboard`)→ 设计优化(`/polish`、`/quieter`、`/distill`、`/normalize`、`/clarify`)→ 设计审查(`/plan-design-review`、`/design-review`、`/critique`、`/audit`、`/benchmark`)。

实战链路示例(倒计时纪念日页面):`/design-consultation` → `/design-shotgun`(3-5 方案) → `/frontend-design` → `/animate` → `/polish` → `/ship`。熟练后常用链路只有 `/frontend-design → /animate → /polish → /ship` 四步。

## 原理进阶:gstack 的工程体系(为什么它"好用")

gstack 不只是 prompt 文件集合,背后有一套完整工程体系——这些设计对任何 skill 项目都有借鉴价值:

**1. SKILL.md 模板生成系统**:每个 SKILL.md 由人写的 `.tmpl` + 构建脚本生成,占位符从源码提取(`{{PREAMBLE}}`、`{{COMMAND_REFERENCE}}`)。好处:文档与代码永不同步、23 个 skill 共享同一份约 220 行 preamble、CI 可 `--dry-run` 检查过期。**教训:跨 skill 共享内容应提取到模板,手动同步迟早出问题。**

**2. 三层升级机制**:`bin/gstack-update-check` 独立 bash 脚本(读 VERSION、缓存检查:UP_TO_DATE 缓存 60 分钟 / UPGRADE_AVAILABLE 缓存 720 分钟)→ **每次调用任何 skill 时 preamble 第一行自动检测更新**(存在感为零但覆盖率 100%)→ **贪睡机制渐进退避**(第 1 次提醒 24h 后再提、第 2 次 48h、之后 7 天,新版本重置计数),可开 `auto_upgrade`。升级区分 5 种安装类型,失败从 `.bak` 恢复。

**3. 学习系统(跨会话记忆)**:`~/.gstack/projects/$SLUG/learnings.jsonl` 追加写入(JSONL);每个 skill 完成前自动反思记录"意外失败/项目怪癖";新会话加载前 3 条高置信度学习条目;**observed/inferred 来源的条目每 30 天衰减 1 分**(过时知识自然消退);`/learn` 提供 search/prune/export。

**4. Preamble 注入(中间件层)**:每 skill 共享 220 行 preamble,类似 Web 框架中间件——更新检测、会话追踪、配置读取、学习历史加载、上下文恢复、路由规则、首次引导。bash 输出键值对(BRANCH: main、PROACTIVE: true),模板用自然语言条件让 Claude 据此调整行为——**把 bash 输出当 Claude 的"环境变量"**。

**5. Sentinel 文件渐进引导**:`~/.gstack/.welcome-seen` 等 touch 文件确保每个引导步骤只出现一次——比 config 里维护 `onboarding_step: 3` 更简单可靠。

**6. SKILL.md 三层架构**:YAML Frontmatter(`allowed-tools` 工具白名单、`benefits-from` 前置依赖、`hooks` PreToolUse 拦截)+ 共享 Preamble + skill 特有逻辑。

**7. Prompt 工程技巧**:
- **反谄媚规则**:禁止 "That's an interesting approach"、"You might want to consider..."——要求 take a position、说 "This is wrong because..."、说清是否 WILL work;
- **禁用词表**:delve、crucial、robust、comprehensive、nuanced、pivotal、landscape 及"here's the kicker"、"plot twist"、em dash 等"AI 味"表达;
- **认知模式注入**:CEO Review 18 条(Bezos 单向/双向门、Munger 逆向思维、Jobs 减法)、Eng Review 15 条(blast radius 直觉、Conway 定律)、Design Review 12 条;
- **具体化标准**:Not "you should test this" but `bun test test/billing.test.ts`;Not "this might be slow" but "this queries N+1, ~200ms per page load with 50 items";
- **置信度校准**:review 发现附带置信度,9-10 正常展示、3-4 隐藏、1-2 仅 P0 展示;
- **交互门控**:ship 精确定义何时停(测试失败无修复/冲突需人判/变更不明)何时不停(常规 git 操作、CHANGELOG 更新、PR 创建)。

**8. 状态管理(文件系统即数据库)**:`~/.gstack/` 下 config.yaml、sessions/、projects/$SLUG/learnings.jsonl、timeline.jsonl、checkpoints/、analytics/。时间序列数据全用 JSONL 追加写入——并发安全、无需数据库、grep/jq 可查、损坏最多丢最后一行。

**9. 跨 Skill 集成**:skill 间通过文件系统传产物(office-hours → design doc → plan-ceo-review → ceo-plans/ → autoplan;review → reviews.jsonl → ship 展示 Review Readiness Dashboard);前置依赖建议(无 design doc 时建议先跑 office-hours);使用序列预测(重复 review → ship → review 则建议 /ship)。

**10. 其他**:Hook 系统(careful/freeze/guard 用 PreToolUse 拦截危险操作)、多平台适配(同模板 `--host` 生成不同平台格式)、完成状态协议(DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT)、**三次失败升级规则**(3 次失败强制停下,防无限重试)、Diff-based 测试选择(E2E 测试约 $4/次,按 git diff 只跑受影响测试)。

## 实践 / 应用:边界与争议

### 社区两极分化

**看好**:创始人和非技术构建者普遍认可 `/office-hours`、`/plan-ceo-review` 这类"产品思维" skill,帮助在写码前重新审视产品方向;`/review` 的多角度并行审查能发现隐蔽安全漏洞。

**质疑**:
- **LOC 指标意义不大**:60 天 60 万行,代码行数从来不是质量指标;
- **本质是 prompt 模板**:每个 skill 就是一个 SKILL.md,技术门槛不高,真正价值在 prompt 设计质量;
- **AI 自审代码的局限**:`/review` 让 AI 审 AI 写的代码,相当于自己批改自己作业,多角色并行只能缓解;
- **名人效应加成**:创建者若不是 YC CEO,关注度大概率没那么高。

### 借鉴建议

抛开争议,真正有价值的是两个不依赖 Garry Tan 是谁的部分:**Browse Daemon 的浏览器自动化技术**和**角色分解的设计模式**。角色化的核心意义不在技术层面,而在行为层面——**帮助你更有意识地组织 AI 工作流,而不是一股脑把所有事丢给一个通用 agent**。

gstack 适合 **fork 和定制**:取你需要的 skill、改你想改的 prompt,而不是全盘照搬。它代表的方向不是让 AI 更自主(Ralph 的路线),也不是让流程更严格(Superpowers 的路线),而是**让 AI 扮演不同角色来提升决策质量**。

## 总结

- **定位**:YC CEO Garry Tan 的角色化技能集,23+ 个 Slash Command 把 Claude Code 变成虚拟工程团队;The Sprint 七步循环(Think → Plan → Build → Review → Test → Ship → Reflect);
- **核心技术**:Browse Daemon(headless Chromium,~100-200ms 命令,Ref System 免 CSS 选择器)+ 角色分解(CEO/EM/设计/QA/安全/发布);
- **工程体系**:模板生成、三层升级(调用时检测+贪睡退避)、JSONL 学习记忆(30 天置信度衰减)、Preamble 中间件、sentinel 引导、hook 安全;
- **三大哲学**:Boil the Lake、Search Before Building、User Sovereignty;
- **借鉴价值**:即使不用它,其"角色切换提升决策质量"的设计模式与 Browse Daemon 技术也值得吸收;与 GSD(上下文工程)、Ralph(自主循环)、Superpowers(流程纪律)互补而非竞争。

## 延伸阅读

- GitHub 仓库:https://github.com/garrytan/gstack(README、ETHOS.md 即最好的文档)
- 视频:Better Stack 综合介绍、YC CEO 50 天连发 100 个 PR
- 站内:[GSD 工作流系统](gsd-workflow-skill.md)(上下文工程对照)、[Ralph Wiggum 循环](../experience/ralph-wiggum-loop.md)(自主循环对照)、[Superpowers 与 Matt Pocock Skills](mattpocock-skills.md)(流程纪律对照)、[Skill 收藏](index.md)、[Agent Skill 版本管理](skill-version-management.md)(学习记忆与升级机制呼应)
