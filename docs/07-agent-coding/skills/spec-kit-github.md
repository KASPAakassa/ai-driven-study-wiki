# Spec Kit:GitHub 官方的规格驱动开发工具包(speckit 命令链)

> **一句话摘要**:GitHub 2025 年 10 月开源的规格驱动开发工具——`specify-cli` 初始化 + `/speckit.specify → clarify → plan → tasks → implement` 命令链,把"先写规格再写代码"变成可执行的工作流:每个阶段有明确输入输出、产出落盘、全程可追溯。本文聚焦**工具本身**(理念部分见站内 [Spec-First Skill](spec-first-skill.md))。
>
> **来源**:GitHub 仓库 github/spec-kit,https://github.com/github/spec-kit;中文解读整理自 Yu 的赛博工位(https://yudesk.dev/docs/notes)

## 概念

**Spec Kit** 是 GitHub 开源的规格驱动开发(Spec-Driven Development)工具包,支持 Claude Code / GitHub Copilot / Gemini CLI。核心思路:与其直接说"帮我添加用户登录功能"(隐藏了成百上千个未说明的决策,AI 不得不猜),不如**先定义"做什么",再考虑"怎么做"**——需求 → 规格 → 计划 → 任务 → 代码。

**为什么有效**:规格驱动开发解决 AI 编程的核心矛盾——**信息不对称**。当你写下用户故事、功能需求、成功标准时,那些"显而易见"的细节浮出水面;渐进式细化让错误更早暴露(Specify 阶段改需求成本几乎为零,代码写完后才改要推倒重来)。

**与 Vibe Coding 的边界**(Karpathy 2025 年提出的概念):

| 场景 | Vibe Coding | 规格驱动开发 |
| --- | --- | --- |
| 原型 / 演示 | ✓ 适合 | 过度 |
| 一次性脚本 | ✓ 适合 | 过度 |
| 生产功能 | 风险高 | ✓ 推荐 |
| 安全相关 | 危险 | ✓ 必须 |
| 团队协作 | 难维护 | ✓ 推荐 |

**但规格不是银弹**:规格减少了猜测,没有消除审查需求。即使有完整规格,AI 仍可能错过边界情况、生成性能不达标代码、引入安全漏洞——验收检查仍然必要。

> 规格驱动开发的价值在于让错误更容易被发现,而不是消除错误本身。

## 原理:六阶段工作流

```
Constitution → Specify → Clarify → Plan → Tasks → Implement
  项目宪法      功能规格    澄清模糊   技术计划   任务分解   执行实现
```

| 阶段 | 命令 | 产出物 | 作用 |
| --- | --- | --- | --- |
| Constitution | `/speckit.constitution` | `constitution.md` | 定义项目原则(测试优先/简单至上/API 优先) |
| Specify | `/speckit.specify` | `spec.md` + git 分支 | 功能规格(用户故事/需求/成功标准) |
| Clarify | `/speckit.clarify` | 更新后的 `spec.md` | 消除模糊点(最多 5 个关键问题) |
| Plan | `/speckit.plan` | `plan.md`、`research.md`、`data-model.md`、`contracts/` | 技术方案设计 |
| Tasks | `/speckit.tasks` | `tasks.md` | 可执行任务清单(按用户故事分组、标并行) |
| Implement | `/speckit.implement` | 实际代码 | 逐个执行任务,可追溯 |

关键设计:规格文档**只关注"做什么",不涉及"怎么做"**——不提技术栈、不写代码结构。每个阶段输入输出明确,形成一条可追溯的链条。

## 代码 / 实现:安装与命令详解

### 安装

新项目:

```bash
# 使用 uv 安装 specify-cli
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# 初始化新项目,指定使用 Claude 作为 AI 助手
specify init my-project --ai claude
```

已有项目(不会覆盖现有文件):

```bash
cd your-existing-project
specify init . --ai claude  # 注意是 . 表示当前目录
```

生成结构:

```
your-project/
├── .specify/
│   ├── templates/       # 规格、计划等模板
│   ├── scripts/         # 辅助脚本
│   └── memory/          # constitution.md
├── .claude/
│   └── commands/        # Claude Code 命令配置(speckit.specify.md 等)
└── specs/               # 功能规格存放目录
```

!!! warning "speckit 命令不是 Claude Code 内置的"
    必须先完成 `specify init`,否则直接运行 `/speckit.specify` 会提示命令不存在。

### 核心命令

**`/speckit.specify`** — 从自然语言创建功能规格:

```bash
/speckit.specify 我想添加一个用户登录功能,支持邮箱密码登录,需要有记住登录状态的选项
```

产出:`specs/001-user-auth/spec.md` + 新 git 分支(`001-user-auth`)。规格核心结构:

```markdown
# Feature Specification: 用户登录功能

## User Scenarios & Testing
### User Story 1 - 用户登录 (Priority: P1)
**Acceptance Scenarios**:
1. Given 用户输入正确的邮箱和密码, When 点击登录, Then 成功进入系统

## Requirements
### Functional Requirements
- FR-001: 系统必须支持邮箱密码登录

## Success Criteria
- SC-001: 用户能在 30 秒内完成登录流程
```

不明确处标记 `[NEEDS CLARIFICATION]`。

**`/speckit.clarify`** — 识别模糊点,按优先级(范围 > 安全 > 用户体验 > 技术细节)排序,每次只问一个问题,支持选项字母 / "yes" / 自定义回答,回答后更新规格并追加澄清记录:

```markdown
## Clarifications
### Session 2025-12-20
- Q: 登录失败如何处理? → A: 连续 5 次失败后锁定账户 15 分钟
```

**`/speckit.plan 我使用 Next.js + Prisma + PostgreSQL`** — 可附加技术栈偏好,产出技术计划(Technical Context / Project Structure / Data Model / API 设计)与研究报告。

**`/speckit.tasks`** — 按用户故事分组生成任务清单:

```markdown
## Phase 1: Setup
- [ ] T001 创建项目结构
- [ ] T002 [P] 配置 Prisma schema   # [P] = 可并行

## Phase 2: User Story 1 - 用户登录 (P1)
- [ ] T004 [US1] 创建 User 模型 in prisma/schema.prisma
```

每个任务有:任务 ID(T001...)、`[P]` 并行标记、`[US]` 用户故事标签、明确文件路径。

**`/speckit.implement`** — 按阶段顺序执行、每完成一个任务标记 `[X]`、遵循依赖、并行任务同时进行。

### 辅助命令

| 命令 | 作用 |
| --- | --- |
| `/speckit.analyze` | 跨文档一致性分析(spec/plan/tasks 是否覆盖,只报告不修改) |
| `/speckit.constitution` | 创建项目宪法,统一团队开发标准 |
| `/speckit.checklist` | 按规格生成定制化质量检查清单 |
| `/speckit.taskstoissues` | 把 tasks.md 转成 GitHub Issues(通过 gh CLI) |

### 工具生态对比

| 工具 | 特点 | 适用场景 |
| --- | --- | --- |
| GitHub Spec Kit | MIT 开源,Claude Code / Copilot / Gemini CLI | 命令行偏好、跨工具协作 |
| AWS Kiro | VS Code fork,可视化工作流,EARS 表示法 | GUI 偏好、AWS 生态 |
| JetBrains Junie | IntelliJ 生态集成,Think More 推理模式 | JetBrains IDE 用户 |
| Cursor Plan Mode | 内置规划阶段,自动生成执行计划 | 已使用 Cursor 的开发者 |

核心理念相通——工具只是载体,重要的是先规格后代码的思维方式。

## 实践 / 应用:完整案例(文章收藏功能)

```bash
/speckit.specify 我想为博客添加文章收藏功能,用户可以收藏喜欢的文章,并在个人中心查看收藏列表
# → specs/002-article-bookmark/spec.md(US1 收藏文章 P1、US2 查看收藏列表 P2、FR-001~003、SC-001 500ms)

/speckit.clarify
# → 提问「收藏数量是否有上限?」→ 回答「最多 100 篇」→ 规格追加 FR-004

/speckit.plan 使用 Next.js + Prisma
# → Bookmark 模型(userId, articleId, createdAt)、API 设计(POST/DELETE /api/bookmarks)、组件设计

/speckit.tasks
# → T001 添加 Bookmark 模型;T002 创建收藏 API;T003 BookmarkButton 组件;T005 收藏列表页...

/speckit.implement
# → 按序执行并标记 [X]
```

**实现后必做人工审查**(不要直接合并代码):

1. 运行测试套件(`npm test`),确认没破坏现有功能;
2. 对照 spec.md 检查是否符合规格意图、代码风格、安全问题;
3. 边界测试:空值、极端输入、并发场景、错误路径;
4. 性能检查:数据库操作/API 调用是否有 N+1 查询。

> 即使规格写得很详细,AI 仍可能在实现细节上出现偏差。审查不是不信任规格驱动开发,而是工程纪律的一部分。

**适用判断**:新功能开发(涉及 3+ 个文件)、需求不完全明确(用 clarify)、多人协作(规格作为共识)适合;简单 bug 修复、探索性编程、时间极紧迫不适合。**一个小时能完成的事,不需要花一小时写规格;一个星期的功能开发,花两小时写规格绝对值得。**

## 总结

- **定位**:GitHub 官方的规格驱动开发工具包,`specify init` 初始化 + `/speckit.*` 命令链;
- **六阶段**:Constitution → Specify → Clarify → Plan → Tasks → Implement,每步输入输出明确、产出落盘、可追溯;
- **核心命令**:specify(建规格+分支)、clarify(每次一问澄清)、plan(技术方案+研究)、tasks(按用户故事分组、[P] 并行、[US] 标签)、implement(逐任务执行);
- **边界**:规格减少猜测但不消除审查——实现后必须人工 review + 边界测试;
- **与站内关系**:理念见 [Spec-First Skill](spec-first-skill.md) 与 [Spec-First 决策栈](../experience/spec-first-decision-stack.md),本文补充 GitHub 官方工具的操作细节。

## 延伸阅读

- GitHub 仓库:https://github.com/github/spec-kit
- 理念参考:ThoughtWorks《Spec-driven development unpacking》、Sean Grove 在 OpenAI AI Engineer Conference 2025 的演讲
- 站内:[Spec-First Skill:把 AI Coding 装进工程闭环](spec-first-skill.md)、[Spec-First 决策栈](../experience/spec-first-decision-stack.md)、[得物 AI Native 交易系统(Spec-Driven 五道关口)](../../04-practice/ai-native-order-system-spec-driven.md)、[GSD 工作流系统](gsd-workflow-skill.md)(同为规格驱动生态)
