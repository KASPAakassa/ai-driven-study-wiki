# Claude Code Worktree 与 Agent Teams:并行开发与多智能体协作

> **一句话摘要**:Claude Code 的两大并行机制:**Worktree** 让多个 Claude 实例在隔离工作目录中并行开发互不冲突(2025.2 发布,创始人 Boris Cherny 称为"#1 productivity tip");**Agent Teams** 让多个 Claude 实例组成团队(Lead + Teammates 直接通信、共享任务列表),实现真正多智能体协作——16 个 Agent 从零构建了能编译 Linux 内核的 C 编译器。本文拆解两者的完整工作流、最佳实践与适用边界。
>
> **来源**:Yu 的赛博工位笔记《Claude Worktree 完全指南》与《Claude Agent Teams 完全指南》,https://yudesk.dev/docs/notes/claude-worktree、https://yudesk.dev/docs/notes/claude-agent-teams;原始内容存档于 `docs/inbox/yudesk-claude-code/`

## 一、Worktree:并行开发的隔离底座

### 概念:为什么需要 Worktree

手上有三个独立任务,但在同一目录跑多个 Claude 实例会导致代码冲突——一个 Agent 改文件,另一个也动同样的文件,合并时一团糟。Worktree 让多个 Agent 在**隔离的工作目录**中并行开发。

!!! tip "建筑师比喻"
    传统方式在同一张图纸上画三个房间,改来改去容易弄乱;Worktree 给你三张独立图纸,最后合并到主图纸。

### 与多次 Clone 的对比

| 方案 | 磁盘占用 | 同步难度 | 清理复杂度 |
| --- | --- | --- | --- |
| 多次 Clone | 每份完整仓库 | 手动 pull/push | 手动删除目录 |
| **Git Worktree** | 只复制工作文件,共享 .git | 自动共享历史 | `git worktree remove` |
| **Claude --worktree** | 同上 | 同上 | **退出时自动清理** |

!!! note "关键:所有 worktree 共享同一个 .git 数据库——一个 worktree 里创建的 commit,其他 worktree 立刻可见,无需 push/pull。**

### 什么时候该用 Worktree

**经验法则:任务超过 30 分钟才考虑用 worktree**——短任务创建环境/装依赖/合并的成本可能比任务本身还久。

| 适合 | 不适合 |
| --- | --- |
| 独立的功能开发 | 10 分钟就能完成的小改动 |
| 不同模块的并行重构 | 需要频繁交互的任务 |
| 长时间运行的任务 | 强依赖其他正在进行的修改 |
| 需要隔离测试的实验性改动 | 简单的 bug fix |

### 完整工作流

**① 创建**(`claude -w feature-auth` 或 `claude -w` 自动随机名):在 `<repo>/.claude/worktrees/<name>/` 创建目录 + 创建 `worktree-<name>` 分支 + **从远端默认分支检出**(不是当前分支)+ 启动 Claude。注意 `-w` 总是从远端默认分支检出;要基于当前分支,三种方式:手动 `git worktree add -b`、**在对话中让 Claude 创建(推荐,自动基于当前分支)**、先 `-w` 再切换(有分支冲突风险)。进阶:用 Makefile 封装成 `make worktree name=xxx` 一键命令。

**② 初始化环境**:每个新 worktree 是独立目录,`node_modules`/虚拟环境/`.env` 不会自动带过来。配置 **WorktreeCreate Hook** 自动初始化(`npm install && cp ../.env .env`),否则每个会话开头跑 `/init`。

**③ 提交与合并**:直接说"提交所有改动,推送到远端,然后创建一个 PR 到 main"(或 `--base feature-x`);也可以选择性 cherry-pick 需要的 commit。

**④ 退出与清理**:无更改 → 自动删除 worktree 和分支;有更改/提交 → 提示保留或删除。可用 WorktreeRemove Hook 自动化。手动管理:`git worktree list / remove / prune`(**不要直接 rm -rf**)。

### 并行开发模式

```bash
# 终端 1:处理用户认证功能
claude -w feature-auth
# 终端 2:修复支付 bug
claude -w bugfix-payment
# 终端 3:重构 API 模块
claude -w refactor-api
```

!!! tip "与站内 [Git Worktree 并行开发](../experience/git-worktree-parallel-agents.md) 的分工"
    那篇讲 Git worktree 原理与多 Agent 任务契约;本篇是 **Claude Code 对 worktree 的封装**(`-w` 命令、WorktreeCreate/Remove Hook、自动清理)。

## 二、Agent Teams:多智能体协作团队

### 概念:与 Subagent 的本质区别

Agent Teams(实验性功能)允许多个 Claude 实例组成团队:一个 **Team Lead** 负责协调,多个 **Teammates** 独立工作,共享任务列表并**可以直接相互通信**。

| 特性 | Subagent | Agent Teams |
| --- | --- | --- |
| 上下文 | 独立上下文,结果返回主 Agent | 独立上下文,完全独立运行 |
| 通信方式 | 只能向主 Agent 汇报 | **Teammates 之间直接通信** |
| 任务协调 | 主 Agent 管理所有工作 | 共享任务列表,自行协调 |
| 适用场景 | 只需要结果的聚焦任务 | 需要讨论和协作的复杂工作 |
| Token 成本 | 较低(结果摘要返回) | 较高(每个 Teammate 是独立实例) |

!!! tip "一句话:Subagent 是你派出去执行任务的承包商;Agent Teams 是坐在同一个房间里协作的项目团队。**

### 为什么有效:专业化带来专注

核心洞察(Addy Osmani):**LLMs perform worse as context expands**——单个 Agent 处理复杂多步骤任务时上下文不断膨胀,经常需要 `/clear` 重置;Agent Teams 让每个 Teammate 保持狭窄专注领域,**上下文干净,性能更稳定**。

### 启用与核心用法

```bash
# 启用(实验性,默认关闭)
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1   # 或 settings.json 的 env 里配置
# 创建团队:说 "create an agent team" / "spawn an agent team"(不要只说 spawn agents,会混淆 Subagent)
```

- **显示模式**:`in-process`(所有 Teammates 在主终端)/ `split panes`(每 Teammate 独立窗格,需 tmux/iTerm2);
- **快捷键**:Shift+Down/Up 切换 Teammate、Ctrl+T 任务列表、Escape 中断、Shift+Tab 启用 Delegate Mode、Enter 进入 Teammate 会话;
- **Delegate Mode(重要)**:启动团队后立即启用——普通模式 Lead 可能自己写代码"抢活干";Delegate Mode 下 **Lead 被强制成为纯粹的项目经理,只能管理任务/沟通/审查,不能写代码跑测试**。

### 六个实战案例

| 案例 | 结构 | 关键机制 |
| --- | --- | --- |
| ① 并行代码审查 | 3 个审查者(安全/性能/测试)各自审查后相互讨论 | 维度拆分避免单一审查者深挖偏科 |
| ② 竞争性假设调试 | 5 个调查者调查不同假设,**相互反驳** | 辩论结构:存活下来的假设更可能是根因 |
| ③ 内容批量生产 | 1 个视频脚本 → 4 个平台作者 | 独立创作 + 内容一致性 |
| ④ QA 质量检查集群 | 5 个 Agent 并行测不同方面 | 优先级排序的问题报告 |
| ⑤ 多轮讨论模式 | 4 个 Teammates 3 轮讨论,含 Red Team 视角 | 架构决策/技术选型 |
| ⑥ **C 编译器项目** | 16 个 Agent,~2000 会话,$20K,10 万行代码,20 亿输入 token | x86/ARM/RISC-V 上构建可启动 Linux 6.9 的 Rust 编译器 |

### 团队管理最佳实践

1. **规模控制**:3-5 个 Teammates 起步(3 个简单多视角审查 / 4-5 个标准开发 / 6+ 大规模迁移);每个 Teammate 分配 5-6 个任务;
2. **任务粒度**:刚好 = 独立完整、产出清晰的工作单元(一个函数/一个测试文件/一份审查报告)——太小协调开销超收益,太大无检查点浪费风险增加;
3. **避免文件冲突**:每个 Teammate 负责不同文件集(Teammate 1: src/auth/,Teammate 2: src/api/...);
4. **监控引导**:定期检查进度,及时纠正方向;Lead 开始自己实现时提醒"等待 teammates 完成任务后再继续";
5. **给足上下文**:Teammates 自动加载项目上下文(CLAUDE.md/MCP/skills),但**不继承 Lead 的对话历史**——生成时提供足够任务细节;
6. **自报告验证模式**:任务描述含验证标准("向 Lead 报告:检查了哪些文件/发现了什么问题/做了什么");
7. **清理**:始终通过 Lead 清理,不要让 Teammates 执行清理(可能导致资源状态不一致)。

## 代码 / 实现:两个机制的最小演示(纯 Python)

```python
# —— 1) Worktree 隔离(Claude -w 的语义:共享 .git,独立工作区)——
class Worktree:
    def __init__(self, name, base_branch):
        self.name = name
        self.branch = f"worktree-{name}"
        self.base = base_branch      # 默认从远端分支检出,不是当前分支

def create_worktree(name, base_branch="origin/main"):
    w = Worktree(name, base_branch)
    print(f"  创建 {w.name}: 目录 .claude/worktrees/{w.name}/,分支 {w.branch} ← {w.base}")
    return w

wt1 = create_worktree("feature-auth")
wt2 = create_worktree("bugfix-payment")
print(f"  两个 worktree 共享同一 .git → {wt1.name} 的 commit 在 {wt2.name} 立即可见")

# —— 2) Agent Teams:Delegate Mode 让 Lead 只协调不干活 ——
class TeamLead:
    def __init__(self, delegate_mode):
        self.delegate_mode = delegate_mode
    def act(self, task):
        if self.delegate_mode:
            return "委托给 Teammates,只管理/审查(不自己写代码)"
        return "自己实现任务(可能抢活干)"

lead_normal = TeamLead(delegate_mode=False)
lead_delegate = TeamLead(delegate_mode=True)
print("\n普通模式 Lead:", lead_normal.act("修 bug"))
print("Delegate Mode Lead:", lead_delegate.act("修 bug"))
assert "委托" in lead_delegate.act("修 bug")
print("\n代码验证通过 ✔")
```

## 实践 / 应用:选型与知识库整合

### 什么时候用哪个

| 场景 | 选择 |
| --- | --- |
| 多个独立任务并行开发 | **Worktree**(任务 >30 分钟) |
| 需要多视角审查/讨论/辩论 | **Agent Teams**(3-5 Teammates) |
| 简单子任务(只拿结果) | **Subagent**(成本低) |
| 单文件小改动 | 什么都不用,直接对话 |

### 与站内其他文章的呼应

- [多智能体协作设计](../../03-agents/agent-team-room-collaboration.md):Agent Teams 的"共享任务列表 + 直接通信"正是 Agent Room 的团队版实现;
- [Git Worktree 并行开发](../experience/git-worktree-parallel-agents.md):任务契约六要素与 Worktree 配合;
- [多 Agent 协作](../../03-agents/multi-agent.md):Teammates 直接通信 = 辩论模式的官方实现;
- [云端软件工厂](../../08-harness/cloud-software-factory.md):16 Agent C 编译器是"Factory 2.0 自治光谱"的真实案例。

## 总结

- **Worktree**:一条命令创建隔离工作区(共享 .git、自动清理);>30 分钟任务才值得;WorktreeCreate/Remove Hook 自动化环境;`-w` 从远端分支检出,基于当前分支用对话创建;
- **Agent Teams**:Lead + Teammates 直接通信 + 共享任务列表;**Delegate Mode 是精髓**(Lead 只协调不干活);3-5 个 Teammates 起步,每个 5-6 任务,文件集错开,给足上下文;
- **两条经验法则**:Worktree 治"并行不冲突",Agent Teams 治"多视角协作"——前者是隔离,后者是沟通;
- **一句话**:Claude Code 的并行能力分两层——**Worktree 让多个 Agent 同时工作不打架,Agent Teams 让多个 Agent 一起工作会讨论**。

## 延伸阅读

- 原页面:https://yudesk.dev/docs/notes/claude-worktree、https://yudesk.dev/docs/notes/claude-agent-teams
- 站内:[Claude Code 架构与工具系统](claude-architecture-tools.md)、[Skills/Plugin/Subagent](claude-skills-plugin-subagent.md)、[Claude Code 隐藏技巧](claude-code-tips.md)(本子主题其他篇);[多智能体协作设计](../../03-agents/agent-team-room-collaboration.md)、[Git Worktree 并行开发](../../07-agent-coding/experience/git-worktree-parallel-agents.md)、[多 Agent 协作](../../03-agents/multi-agent.md)
