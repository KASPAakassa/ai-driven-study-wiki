# GSD (Get Shit Done):轻量级上下文工程 + 规格驱动开发系统

> **一句话摘要**:TÂCHES(glittercowboy)开源的元提示系统——把"让 Claude Code 可靠地交付整个项目"这件事系统化:讨论 → 计划 → 执行 → 验证的循环、子代理编排与文件系统状态管理,让独立开发者用几个命令就能完成复杂项目(作者 4 小时零手写代码做出 macOS 原生 App)。
>
> **来源**:GitHub 仓库 TACHES/GSD,https://github.com/glittercowboy/gsd;中文解读整理自 Yu 的赛博工位(https://yudesk.dev/docs/notes)

## 概念

**GSD (Get Shit Done)** 是一个轻量级的元提示、上下文工程和规格驱动开发系统,支持 **Claude Code、OpenCode 和 Gemini CLI**。它解决的核心问题是 **context rot(上下文腐烂)**——随着对话变长,上下文窗口被失败代码、过时讨论和无关信息填满,输出质量不断下降。

**创建者动机**(TÂCHES 原话):

> "我不是 50 人的软件公司。我不想玩企业戏剧。我只是一个想做出好东西的创意人。"

他的自我定位不是程序员,而是**高层项目经理**——描述愿景、做关键决策、验证结果。在他的直播中,他用 GSD 在 4 小时内从零构建了完整的 macOS 原生音乐生成应用(Sample Digger),全程零手写代码。

**设计哲学:把复杂性藏在系统里**。用户只需要几个简单命令,系统在背后处理所有的上下文管理、任务编排和质量验证。区别于 BMAD、SpecKit 等"企业级"工具——它们倾向于引入 sprint ceremonies、story points、stakeholder syncs 等企业工作流,对独立开发者反而是负担。

> "It's not enterprise theater. We understand that you're just one person, you just want some sort of scaffolding around Claude Code to make sure it executes the tasks it says it's going to execute in an effective way." —— Chase AI

### 工具生态中的位置

| 维度 | Ralph Wiggum | SpecKit | BMAD | GSD |
| --- | --- | --- | --- | --- |
| 核心定位 | 执行技术(bash loop) | 规格生成工具包 | 企业级框架 | 上下文工程 + 规格驱动 |
| 规划能力 | 无(需自备 spec) | 强(spec→plan→tasks) | 强(完整敏捷流程) | 强(研究→讨论→规划) |
| 执行自主性 | 最高(AFK 模式) | 需手动触发每步 | 需手动触发每步 | 需手动触发每步 |
| 人类参与模式 | Human on the Loop | Human in the Loop | Human in the Loop | Human in the Loop |
| Context Rot 处理 | 新 session 重启 | 无内置方案 | 无内置方案 | 子代理新鲜上下文 |
| 质量验证 | 依赖外部测试 | 构建检查 | 内置 QA 流程 | 自动验证 + UAT |
| 用户复杂度 | 最低 | 中等 | 较高 | 低 |
| 系统复杂度 | 最低 | 中等 | 较高 | 高 |

关键取舍:**Ralph 用最低系统复杂度换最高执行自主性;GSD 用高系统复杂度换规划质量和人类校验**。GSD 继承了 Ralph 的"新鲜上下文、文件作为真相来源"原则,但补上了 Ralph 缺的项目理解、阶段规划与质量验证。

> Ralph 循环假设你带着完整蓝图来——GSD 帮你构建这个蓝图。—— Chase AI

## 原理:核心工作流与四个技术支撑

### 工作流:讨论 → 计划 → 执行 → 验证的循环

**1. 初始化项目** `/gsd:new-project` — 持续提问直到理解你的想法(目标、约束、技术偏好、边界情况)→ 派出并行代理研究相关领域 → 提取需求(区分 v1 / v2 / 超出范围)→ 创建阶段路线图。已有代码库?先跑 `/gsd:map-codebase`。
产出:`PROJECT.md`、`REQUIREMENTS.md`、`ROADMAP.md`、`STATE.md`。

**2. 讨论阶段** `/gsd:discuss-phase 1` — 识别当前阶段的"灰色地带"(有多种合理实现方式的决策点:视觉功能 / API/CLI / 内容系统),捕获实现偏好。跳过也可用默认值,但深入讨论显著减少返工。
产出:`{phase}-CONTEXT.md`。

**3. 计划阶段** `/gsd:plan-phase 1` — 研究实现方式 → 创建 2-3 个原子任务计划(XML 结构化)→ 验证计划是否满足需求,循环修正直到通过。核心设计理念是 **Goal-Backward Planning(目标回溯规划)**:不是问"我们应该构建什么",而是问"为了实现目标,什么条件必须成立",再反向推导计划。每个计划足够小,能在全新上下文窗口中执行。
产出:`{phase}-RESEARCH.md`、`{phase}-{N}-PLAN.md`。

**4. 执行阶段** `/gsd:execute-phase 1` — 波次执行(独立任务并行,有依赖的按顺序)→ 每个计划在**全新的 200k tokens 上下文**中执行(零累积垃圾)→ 每个任务独立 git commit → 自动验证代码库是否实现了阶段承诺。TÂCHES 直播中完成 3 个完整阶段,主上下文窗口始终保持在 24%;Executor 子代理只需加载不到 1,000 行上下文就能完成一个阶段。
产出:`{phase}-{N}-SUMMARY.md`、`{phase}-VERIFICATION.md`。

**5. 验证阶段** `/gsd:verify-work 1` — 提取可测试的交付物 → 逐一引导你确认("能用邮箱登录吗?" 是/否)→ 失败则自动诊断根因、创建修复计划。这是 GSD 与 Ralph 最大的理念差异:**每个阶段结束都有人类验证环节(Human in the Loop)**,避免错误在无人监督下层层叠加。
产出:`{phase}-UAT.md`。

循环重复:`discuss-phase 2 → plan-phase 2 → execute-phase 2 → verify-work 2 → ... → /gsd:complete-milestone → /gsd:new-milestone`。

### 技术支撑一:Context Engineering(文件即状态)

| 文件 | 作用 |
| --- | --- |
| `PROJECT.md` | 项目愿景,始终加载 |
| `research/` | 生态知识(技术栈、功能、架构、陷阱) |
| `REQUIREMENTS.md` | 分版本的需求,带阶段追溯 |
| `ROADMAP.md` | 方向和进度 |
| `STATE.md` | 决策、阻碍、位置——跨 session 的记忆 |
| `PLAN.md` | 原子任务 + XML 结构 + 验证步骤 |
| `SUMMARY.md` | 执行记录,提交到历史 |

每个文件都有基于 Claude 质量退化阈值的大小限制。主上下文窗口保持在 30-40%,实际工作在子代理的全新 200k 上下文中完成。

> 无论上下文窗口多大,前半段的 token 都比后半段更有效。这不是 bug,这是 LLM 的固有特性。—— Chase AI 对 context rot 的解释

TÂCHES 在 $200/月 Max 计划上每月消耗约 $30,000 的 Opus tokens,但因为每个任务在新鲜上下文执行、返工极少,实际效率远高于在退化上下文中反复修补。

### 技术支撑二:XML Prompt Formatting

每个计划都是为 Claude 优化的结构化 XML——精确指令,无需猜测,验证内置:

```xml
<task type="auto">
  <name>Create login endpoint</name>
  <files>src/app/api/auth/login/route.ts</files>
  <action>
    Use jose for JWT (not jsonwebtoken - CommonJS issues).
    Validate credentials against users table.
    Return httpOnly cookie on success.
  </action>
  <verify>curl -X POST localhost:3000/api/auth/login returns 200 + Set-Cookie</verify>
  <done>Valid credentials return cookie, invalid return 401</done>
</task>
```

### 技术支撑三:Multi-Agent Orchestration

每个阶段使用相同模式:**薄编排器派出专门化代理,收集结果,路由到下一步**。编排器从不做重活:

| 阶段 | 编排器做什么 | 代理做什么 |
| --- | --- | --- |
| 研究 | 协调、展示发现 | 4 个并行研究员调查技术栈、功能、架构、陷阱 |
| 规划 | 验证、管理迭代 | 规划者创建计划,检查者验证,循环直到通过 |
| 执行 | 分组波次、跟踪进度 | 执行者并行实现,各自拥有全新 200k 上下文 |
| 验证 | 展示结果、路由下一步 | 验证者检查代码库,调试者诊断失败 |

### 技术支撑四:Atomic Git Commits

每个任务完成后立即独立提交,`git bisect` 能定位到具体失败任务、每个任务可独立回滚、清晰历史帮助 Claude 在 future session 理解代码演变。

## 代码 / 实现:安装与命令体系

### 安装

```bash
npx get-shit-done-cc@latest
```

安装器提示选择:**运行时**(Claude Code、OpenCode、Gemini CLI 或全部)+ **位置**(全局或当前项目)。安装后输入 `/gsd:help` 验证。

推荐用以下方式运行 Claude Code(无摩擦自动化):

```bash
claude --dangerously-skip-permissions
```

不想用该标志,可在 `.claude/settings.json` 配置细粒度权限。GSD 更新频繁(TÂCHES 几乎每天推送 15-20 次),定期运行 `/gsd:update`。

### 完整命令参考

**核心工作流(主循环,按序使用)**

| 命令 | 说明 |
| --- | --- |
| `/gsd:new-project` | 初始化项目:提问 → 研究 → 提取需求 → 创建路线图 |
| `/gsd:discuss-phase [N]` | 讨论第 N 阶段灰色地带,捕获实现偏好 |
| `/gsd:plan-phase [N]` | 创建原子任务计划(研究 + 规划 + 验证) |
| `/gsd:execute-phase <N>` | 子代理并行实现,每个任务独立提交 |
| `/gsd:verify-work [N]` | 引导逐一确认交付物,自动诊断问题 |

`[N]` 可选(省略时自动检测当前阶段),`<N>` 必填。

**里程碑管理**:`/gsd:audit-milestone`(审计进度)、`/gsd:complete-milestone`(归档并标记版本)、`/gsd:new-milestone [name]`(开启下一周期)。

**阶段管理**:`/gsd:add-phase`、`/gsd:insert-phase [N]`(插入后自动重编号)、`/gsd:remove-phase [N]`(级联删除产出文件)、`/gsd:list-phase-assumptions [N]`。

**Quick Mode 与工具**:`/gsd:quick [--full]`(跳过研究/计划检查/验证,适合小任务)、`/gsd:debug [desc]`(隔离调试子代理)、`/gsd:add-todo [desc]`、`/gsd:check-todos`、`/gsd:map-codebase`。

**Session 与配置**:`/gsd:pause-work`(状态存 STATE.md)、`/gsd:resume-work`、`/gsd:progress`、`/gsd:help`、`/gsd:settings`、`/gsd:set-profile`(切模型配置)、`/gsd:update`。

### 模型配置(三种 profile)

| 配置 | 规划 | 执行 | 验证 | 适用场景 |
| --- | --- | --- | --- | --- |
| quality | Opus | Opus | Sonnet | 复杂项目、关键功能、首次使用 |
| balanced(默认) | Opus | Sonnet | Sonnet | 日常开发、多数场景 |
| budget | Sonnet | Sonnet | Haiku | 简单功能、预算敏感 |

### 核心设置与工作流开关

`/gsd:settings` 可改:`mode`(模型配置)、`depth`(研究深度 quick/standard/deep)、`git.branching_strategy`(feature/phase/none)。可独立开关的代理:`research`(规划前自动研究)、`plan_check`(计划自动验证)、`verifier`(执行后自动验证)、`auto_advance`(阶段后自动推进,默认关)。关闭 research 和 plan_check 可显著提速,但可能降低规划质量。

## 实践 / 应用:从零交付一个功能

### 实战演示(博客系统加评论功能)

```bash
/gsd:new-project     # "为 Next.js 博客添加评论功能。支持匿名和登录评论、
                     #  Markdown 渲染、管理后台。技术栈用 Prisma + PostgreSQL。"
/gsd:discuss-phase 1 # 回答灰色地带:嵌套层级?验证码?批量操作?
/gsd:plan-phase 1    # 生成原子任务:数据模型 / API 路由 / 前端组件
/gsd:execute-phase 1 # Wave 1(schema、Prisma 模型)→ Wave 2(API、CRUD)→ Wave 3(前端组件)
/gsd:verify-work 1   # 逐一确认:数据库表?状态码?评论输入框?实时更新?
```

### 实战建议

1. **放慢才能加快**:研究和讨论阶段多花时间,执行阶段返工更少;
2. **阶段之间清上下文**:每个阶段间运行 `clear` 或 `/compact`,保持主上下文在 30-40%;
3. **Token 权衡**:子代理方式确实更耗 token,但"plan twice, prompt once"(计划两次,提示一次)比"提示一次然后修修补补"长期更省——在新鲜上下文做对一次,优于在退化上下文反复修复;
4. **不如意就回滚**:`git reset --hard HEAD~3` + `/gsd:remove-phase 2` 级联删除,干脆利落;
5. **To-Do 系统**:`/gsd:add-todo` 记录想法,里程碑讨论时拉出来作为下一周期输入。

### 常见问题

- **支持哪些运行时?** Claude Code、OpenCode、Gemini CLI。
- **Quick Mode 与完整模式?** Quick 保留原子提交和状态跟踪,跳过研究/计划检查/验证,适合 bug 修复、小功能、配置变更。
- **执行中可暂停?** 可以,`/gsd:pause-work` 保存状态,`/gsd:resume-work` 继续。
- **控制 token?** 切 budget profile、关 research/plan_check、用 quick。
- **能和 Ralph 一起用?** 可以——GSD 负责规划,用 Ralph 循环执行不需要人类介入的阶段。

### 边界

GSD 是**人类引导的工作流,不是自主代理**——不能持久化运行,每个阶段边界都需要手动输入命令。你不能说"帮我做个 app"然后去睡觉,每个关键节点都要你在场:审批路线图、回答讨论、触发规划、启动执行、确认验证。这是有意识的设计取舍,不是缺陷。

## 总结

- **定位**:轻量级元提示 + 上下文工程 + 规格驱动开发系统,为 Claude Code / OpenCode / Gemini CLI 设计,解决 context rot;
- **核心循环**:讨论 → 计划 → 执行 → 验证,每个阶段有人类验证(Human in the Loop),产出全部落盘到 `.planning/`;
- **四个技术支撑**:Context Engineering(文件即状态,主窗口 30-40%)、XML Prompt Formatting(精确指令 + 内置验证)、Multi-Agent Orchestration(薄编排器派专门化代理)、Atomic Git Commits;
- **与 Ralph 的关系**:GSD 继承 Ralph 的"新鲜上下文"原则,补上项目理解、阶段规划与质量验证——Ralph 假设你带蓝图来,GSD 帮你构建蓝图;
- **下一步**:对比本站 [Ralph Wiggum 循环](../experience/ralph-wiggum-loop.md) 与 [Loop Engineering](../experience/loop-engineering.md),理解"规划型 vs 自主型"两种 Agent 工作流的取舍。

## 延伸阅读

- GitHub 仓库:https://github.com/glittercowboy/gsd(README 即最好的文档)
- 视频:I Created GSD For Claude Code(TÂCHES 4 小时直播)、The New Claude Code Meta(Chase AI)、Stop Using Ralph Loops (Use This Instead)
- 站内:[Ralph Wiggum 循环](../experience/ralph-wiggum-loop.md)(自主循环对照)、[Loop Engineering](../experience/loop-engineering.md)、[Spec-First Skill](spec-first-skill.md)、[Spec Kit:GitHub 官方规格驱动工具](spec-kit-github.md)、[Skill 收藏](index.md)
