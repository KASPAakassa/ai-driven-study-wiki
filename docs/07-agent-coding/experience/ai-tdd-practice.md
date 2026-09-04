# AI 时代的 TDD:把"相信模型"换成"相信反馈"

> **一句话摘要**:AI 编程时代,TDD 不再是程序员的个人自律,而是一套**刹车系统**——模型最擅长也最危险的事是"快速写出一大段看起来完整的代码"。TDD 把"相信模型"换成"相信反馈":RED(证明缺口)→ GREEN(最小实现)→ REFACTOR(只改结构),并用 AGENTS.md 纪律 + Codex Skill + Subagents 隔离 + Hooks 盯防四层落地到 Codex。
>
> **来源**:中文解读整理自 Yu 的赛博工位(https://yudesk.dev/docs/notes);TDD 经典方法论参考 Kent Beck

## 概念:TDD 不是"先写测试"

过去说 TDD,常常是在说程序员的自律:先写测试,再写实现,小步重构。到了 AI 编程里,它更像一套刹车系统——**AI 十几秒就能给你一个实现文件 + 一组测试 + 一句"已完成",但"看起来完整"不是工程意义上的完成**。

工程意义上的完成,至少要回答:

1. 这个行为有没有被一个明确的失败测试定义过?
2. 这个失败有没有因为实现而变绿?
3. 变绿以后,有没有在不改行为的前提下整理代码?

**关键洞察:TDD 的重点不是"测试文件出现得早",而是"失败反馈出现得足够早"。**

### TDD 的第一步叫 RED,不叫 TEST

RED 的意思是:先写一个测试,让系统明确失败。这个失败必须满足三件事:

- **它确实失败**;
- **它因为目标行为不存在而失败**;
- **它失败的方式和你的预期一致**。

没有先看到红,后面的绿就没有意义。比如实现 `slugify("Hello World") -> "hello-world"`,一个有价值的 RED 不是"我写了个测试文件",而是:

```bash
Test: tests/test_slugify.py
Command: pytest tests/test_slugify.py -q
Failure: NameError: name 'slugify' is not defined
Reason: 目标函数还不存在,符合预期
```

这时测试才变成了**规格**——它告诉你:下一步实现只需要让这一条行为成立。

### 先绿再补测试,通常是在补故事

AI 很容易走"先写实现,再补测试"的路——体验很顺,但有致命问题:**测试很可能只是对当前实现的追认**。它不是在问"需求应该是什么",而是在问"当前代码怎么写才容易通过"。

AI 写测试的常见"味道":断言太贴合当前实现、mock 太多(真实边界没测到)、只测 happy path、为了让现有代码通过把断言写得很宽——**没有一个测试能证明旧代码原本是错的**。TDD 要反过来:先让需求变成失败,再让代码追上需求。

## 原理:为什么 AI 时代更需要 TDD

**AI 编程的核心矛盾不是"代码写得慢",而是"反馈来得晚"。** 没有 TDD 时的工作方式:描述需求 → AI 写一堆代码 → 人肉看 diff → 跑一下 → 发现问题 → 回头修。问题堆到最后,你发现错时可能已混着三类东西:需求理解错了、实现路径错了、重构把旧行为改坏了。TDD 的作用是把这个长链条切短。

**1. 它给模型一个可判定目标**。"写得优雅一点"不是目标;"实现用户登录态过期后自动跳回登录页"也还不够具体。更好的目标:

> 当 access token 过期时:① 请求返回 401;② 客户端清理本地 session;③ 用户被重定向到 /login;④ 原始目标地址被保存在 redirect 参数里。

再进一步,把其中一条变成失败测试:

```gherkin
given expired session
when user opens /settings
then app redirects to /login?redirect=/settings
```

这时 AI 不再猜"登录态过期应该怎么处理",而是在完成一个明确行为。

**2. 它把大任务拆成小闭环**。AI 最容易失控的是一口气做完(登录、权限、刷新 token、错误提示、路由跳转一次生成一个大 diff)。TDD 的节奏:一个行为 → 一个失败测试 → 最小实现 → 变绿 → 再下一个行为。小到你能看懂、AI 不容易编故事、失败时能快速定位。

**3. 它限制模型"顺手发挥"**。AI 热心过度:修边界 bug 顺手抽 helper、加测试顺手改实现、重构顺手改行为。TDD 用阶段把这些动作分开:

| 阶段 | 可以做什么 | 不该做什么 |
| --- | --- | --- |
| RED | 写一个失败测试 | 写生产实现 |
| GREEN | 写最小实现 | 改测试凑绿 |
| REFACTOR | 整理结构 | 引入新行为 |

### 红绿重构:三道门,不是三句口号

**第一门 RED — 证明需求还没被满足**。最重要的问题:这个测试如果失败,是否能证明我们还缺一个目标行为?

- 坏 RED:`assert True`(不证明任何缺口);
- 也不太好的 RED:`assert "hello" in format_title("Hello World")`(太宽,很多错误实现也能通过);
- 更好的 RED:`assert slugify("Hello World") == "hello-world"`(指定了输入、输出和行为)。

**第二门 GREEN — 只让当前测试通过**。不是写最终架构,任务只有一个:用最少代码让当前失败测试通过。可能丑,但价值在于**保持设计压力**——中文、重音符号、连续标点、emoji、SEO 特例应该由后面的测试推动,而不是现在一次做完。

```python
def slugify(text: str) -> str:
    return text.lower().replace(" ", "-")
```

**第三门 REFACTOR — 只改结构,不改行为**。重构的定义很窄:**外部行为不变,内部结构变好**。好的重构:改更准确的变量名、抽出重复表达式、拆掉过深的条件分支、移动函数位置。坏的重构:顺手支持新输入、顺手改错误提示、顺手换依赖、顺手改测试断言。判断标准:**如果提交只叫 `refactor:`,测试前后应该一样绿,用户行为也应该一样。**

### 好测试的味道

- **好测试像规格**:读起来像一句业务规格("当用户没有权限时,保存按钮不可点击")——关心外部行为;坏测试像实现笔记("应该调用 validateInput 三次")——实现细节被绑住后,重构会很痛,测试不是在保护代码而是在冻结代码;
- **好测试有边界**:一个测试最好只回答一个问题。同时断言格式、权限、网络请求、toast 文案、数据库状态的"大而全"测试,失败时很难定位问题(AI 特别喜欢写这种);
- **好测试会让实现难以作弊**:只覆盖一个过于特殊输入的测试,AI 可能写出刚好匹配的假实现(`return "hello-world"`);第二条测试(`slugify("Test Driven Development") == "test-driven-development"`)就会逼出真正逻辑。**每一轮只新增一个行为压力,压力逐步增加,设计逐步长出来。**

## 代码 / 实现:四层落地到 Codex

工作流四层(别一上来就问"要配哪些文件",先问"怎么让 Codex 每次都按同一条 TDD 工作流行动"):

| 层级 | 你在做什么 | 放在哪里 | 适合什么时候 |
| --- | --- | --- | --- |
| L1 | 写项目纪律 | AGENTS.md | 所有项目都该有 |
| L2 | 固化流程 | `.agents/skills/tdd-codex/SKILL.md` | 反复用 TDD 做需求 |
| L3 | 隔离阶段 | `.codex/agents/*.toml` | 复杂任务,怕测试和实现互相污染 |
| L4 | 自动提醒 | `.codex/hooks.json` | 重要仓库,怕 AI 偷改测试 |

最小可用版本是 L1 + L2;完整防线是 L1 + L2 + L3 + L4。

### 先定义"完成"是什么

**每一轮交付证据**——让 Codex 每轮报告六项:`Behavior`(实现哪个行为)、`Test`(测试文件和测试名)、`Command`(跑了什么命令)、`RED`(失败原因是否符合预期)、`GREEN`(通过结果)、`REFACTOR`(是否重构,为什么)。这比一句"已完成"有用得多。

**一轮只处理一个行为**——不要一次生成完整测试矩阵("横向铺测试":RED test1..5 → GREEN 一次写一个大实现),要**纵向切片**:`RED test1 → GREEN impl1 → REFACTOR → RED test2 → ...`。第一轮实现会改变你对问题的理解,不要把所有测试一次性写死。

### L1:把纪律写进 AGENTS.md

Codex 会先读全局说明,再从项目根目录一路读到当前目录;越靠近当前目录优先级越高;合并上限 32 KiB——所以 **AGENTS.md 不能写成长篇教程,只写"在这个项目里什么行为不允许"**(像项目交通规则):

```markdown
# TDD Rules

- For new behavior and bug fixes, use red/green TDD.
- RED: write exactly one failing behavior test first.
- Run the smallest relevant test command and confirm the failure is expected.
- Do not edit production implementation during RED.
- GREEN: write the minimum production code required to pass the current failing test.
- Never modify, delete, skip, or weaken tests to make implementation pass.
- REFACTOR only after tests are green.
- Keep structural changes and behavior changes separate.
- Report Behavior, Test, Command, RED, GREEN, and REFACTOR for each cycle.
```

再补项目命令(Verification 小节)。**坏的 AGENTS.md**:写满 TDD 历史、所有测试哲学、框架教程、复杂 prompt 模板——稀释真正重要的规则。AGENTS.md 只放常驻纪律,长流程放 skill。

### L2:把流程做成 Codex Skill

```markdown
---
name: tdd-codex
description: Implementing or fixing maintainable code with Codex using strict red-green-refactor TDD. Use for new behavior, bug reproduction, behavior tests, or safe AI coding.
---

# TDD Codex Workflow

Use one behavior slice per cycle.

## Phase 0: Scope
Identify one observable behavior. Name the public API, user flow, or integration boundary under test. Do not edit production code.

## Phase 1: RED
Write exactly one failing behavior test. Prefer public behavior over implementation details.
Run the smallest relevant test command. Confirm the failure is expected. Stop and report: Behavior / Test file / Command / Failure reason.

## Phase 2: GREEN
Write the minimum production code to pass the current failing test.
Never modify, delete, skip, or weaken tests to pass. Do not add speculative features or abstractions.
Run the same test command. Report the passing result.

## Phase 3: REFACTOR
Only refactor after tests are green. If the code is already simple, skip.
If refactoring, make one structural change at a time. Run tests after each refactor. Do not change behavior.

## Cycle Report
Return: Behavior / Test / Command / RED / GREEN / REFACTOR / Next slice
```

调用方式:"用 tdd-codex skill 做这个需求。每轮只处理一个行为。先 RED,确认失败后停下来,不要直接写实现。"——重点不是 prompt 多漂亮,而是**每次都能把 Codex 拉回同一条轨道**。

### L3:用 Subagents 隔离红绿重构

适合拆:权限、计费、状态机、多模块功能、bug 很隐蔽(先写复现测试)、模型总是改测试凑绿、希望有人只负责 review 测试质量。不适合拆:小工具函数、文案改动、纯视觉微调、一次性脚本。**拆 agent 的成本真实存在,只在隔离收益大于沟通成本时使用。**

三个 agent 的 `.codex/agents/*.toml`(均 `sandbox_mode = "workspace-write"`):

- **RED agent**(`tdd_test_writer`):只写一个行为测试并确认 RED,不编辑生产实现,不加多个测试;
- **GREEN agent**(`tdd_implementer`):读失败测试,写最小实现通过当前测试,永不改测试凑绿,不加投机性功能/helper/抽象;
- **REFACTOR agent**(`tdd_refactorer`):先跑测试确认绿,找重复/命名不清/分支过深/职责错位,跳过已简单代码,一次只改一处结构,每次改后跑测试,绝不改行为。

主会话指挥:按三阶段做 slice——test_writer 只写一个失败测试并确认 RED → 等确认后 implementer 写最小实现确认 GREEN → refactorer 判断是否需要重构。**重点是隔离上下文:写测试的人不被实现细节影响,写实现的人不能随手动测试,重构的人不能引入新行为。**

### L4:用 Hooks 盯住测试 diff

最常见的越界是:**测试红了,模型为了变绿顺手把测试改了**。hooks 的价值不是"绝对安全",而是把这种动作立刻暴露出来。

```bash
# ~/.codex/config.toml 或 <repo>/.codex/config.toml
[features]
codex_hooks = true
```

```json
// <repo>/.codex/hooks.json(项目级,跟着仓库走)
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "apply_patch|Edit|Write",
        "hooks": [
          { "type": "command",
            "command": "bash \"$(git rev-parse --show-toplevel)/.codex/hooks/watch-test-edits.sh\"",
            "timeout": 10, "statusMessage": "Checking test file edits" }
        ]
      },
      {
        "matcher": "Bash|apply_patch|Edit|Write",
        "hooks": [
          { "type": "command",
            "command": "bash \"$(git rev-parse --show-toplevel)/.codex/hooks/run-fast-check.sh\"",
            "timeout": 120, "statusMessage": "Running fast checks" }
        ]
      }
    ]
  }
}
```

`watch-test-edits.sh` 检查 `git diff --name-only` 是否命中测试文件(正则匹配 `__tests__/`、`.test.`/`.spec.`、`_test.go`、`test_*.py` 等),命中则返回 `{"continue": false}` 并提示"测试文件可以改,但必须说明为什么改——是补充规格,还是为了凑绿而改测试?"。`run-fast-check.sh` 按项目类型(pyproject/pytest、package.json 的 types:check、go.mod)跑快速检查。

**不要神化 hooks**:它是 guardrail,不是完整 enforcement boundary。它能提醒、能阻断常见路径,但不能替代 review、CI 和人的判断。测试确实需要修改时,正确做法不是永远禁止,而是要求模型解释:为什么要改测试?是新需求、新边界,还是旧测试写错?生产实现有没有被同步验证?

### 与 TDD-Guard 的关系

TDD-Guard 是 Claude Code plugin 路线(核心思想:阻止 AI 违反 TDD,尤其阻止改测试凑绿)。迁移到 Codex 时**借思想,不照搬路径**:CLAUDE.md → AGENTS.md;`.claude/agents/*.md` → `.codex/agents/*.toml`;plugin → hooks + git diff 检查 + CI;slash command → skill 或 prompt。Codex 侧更现实的组合:**AGENTS.md 写纪律 + skill 固化流程 + subagents 隔离角色 + hooks 检查测试 diff + CI 做最后兜底**。

## 实践 / 应用:完整走查(slugify)

**Step 0 — 先问边界,不写代码**:让 Codex 先问 5 个边界问题(大小写、空格、标点、unicode、空字符串),把确认后的规格写成 SPEC.md:

```markdown
# slugify SPEC
- "Hello World" -> "hello-world"
- trim leading/trailing spaces
- collapse repeated spaces into one hyphen
- remove punctuation
- normalize "Café" -> "cafe"
- empty input returns empty string
```

**Step 1 — 第一盏红灯**:只实现第一条行为,先 RED(写一个失败测试并确认失败,不写生产实现)。

**Step 2 — 最小变绿**:`def slugify(text: str) -> str: return text.lower().replace(" ", "-")`,然后报告 GREEN + REFACTOR(skipped,还很简单)+ Next slice。

**Step 3 — 第二盏红灯**:`assert slugify("  Hello World  ") == "hello-world"`——如果当前实现输出 `-hello-world-`,红灯成立;然后 GREEN:`return text.strip().lower().replace(" ", "-")`。

**Step 4 — 别急着抽象**:很多 AI 会想抽 normalizeInput、removePunctuation、toAscii——先别急。**TDD 的设计应该被测试压力推出来,不是被想象推出来**。等加到 unicode、标点、空字符串,结构压力真的出现再重构。

### 日常用法速查

- **新功能**:用 TDD 实现这个需求。每轮只处理一个行为。先写一个失败测试并运行确认 RED。不要写生产实现,直到我说 go。
- **修 bug**:先写一个能复现这个 bug 的失败测试。确认它因为这个 bug 失败后,再写最小修复。不要改测试来适配当前实现。
- **复杂功能**:先不要写代码,请给出 TDD 分解计划——外圈集成测试是什么、内圈每个行为 slice 是什么、每轮用什么命令验证、哪些地方不能 mock。
- **Review**:重点看是否先有失败测试、测试是否测行为而非实现、是否存在为了通过而弱化测试、结构改动和行为改动是否混在一起、是否缺少外圈集成测试。

### 最后的检查清单

| 问题 | 合格标准 |
| --- | --- |
| 真的先红了吗 | 有失败命令和失败原因 |
| 红得对吗 | 失败原因对应目标行为缺失 |
| 一轮只做一个行为吗 | 没有批量铺测试 |
| GREEN 改测试了吗 | 没有改测试凑绿 |
| 测试测行为吗 | 不依赖内部实现细节 |
| 重构混行为了吗 | 结构改动和行为改动分开 |
| 有完整验证吗 | 目标测试和必要全量检查都跑过 |

**这张表过不了,就不要急着合并。**

## 总结

- **本质**:AI 时代 TDD 是刹车系统——把"相信模型"换成"相信反馈";关键不是测试文件出现得早,而是**失败反馈出现得足够早**;
- **三道门**:RED(证明缺口,失败必须因目标行为缺失且符合预期)→ GREEN(最小实现,保持设计压力)→ REFACTOR(只改结构不改行为);
- **好测试**:像规格(测外部行为)、有边界(一个问题一个测试)、让实现难以作弊(行为压力逐步增加);
- **四层落地**:AGENTS.md 写纪律 + Codex Skill 固化流程 + Subagents 隔离红绿重构 + Hooks 盯防测试 diff;
- **下一步**:对照 [Agentic Code Review](agentic-code-review.md)(审查侧配套)、[AI Coding Harness 设计经验](ai-coding-harness-design.md)(护栏设计)、[得物 Spec-Driven 五道关口](../../04-practice/ai-native-order-system-spec-driven.md)(TDD 关口在企业实践中的位置)。

## 延伸阅读

- 理念:Kent Beck TDD 经典著作;Roman (Mentat) 相关讨论
- 站内:[Agentic Code Review](agentic-code-review.md)、[AI Coding Harness 设计经验](ai-coding-harness-design.md)、[得物 AI Native 交易系统](../../04-practice/ai-native-order-system-spec-driven.md)、[用 Agent 持续交付](agent-cognitive-complexity-gates.md)、[mattpocock-skills](../skills/mattpocock-skills.md)(其 `/tdd` skill)
