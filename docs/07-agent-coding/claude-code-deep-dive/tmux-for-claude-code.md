# Tmux 入门:Claude Code 用户的终端复用器指南

> **一句话摘要**:Tmux(Terminal Multiplexer)让一个终端窗口跑多个会话、会话在后台持续运行(关掉终端也不断)、断线重连后恢复完整上下文——是 Claude Code Agent Teams、长任务后台运行、多实例并行、SSH 远程开发的**必备配套工具**。本文覆盖三核心概念、命令速查、Claude Code 集成与四个实战工作流。
>
> **来源**:Tmux Wiki,https://github.com/tmux/tmux/wiki;中文解读整理自 Yu 的赛博工位(https://yudesk.dev/docs/notes)

## 概念:为什么 Claude Code 用户需要 Tmux

**Tmux (Terminal Multiplexer)** 是终端复用器:在一个终端窗口中创建和管理多个终端会话。核心特性是**会话持久化**——即使断开连接,会话也会继续运行,重新连接后恢复到原来的状态。

如果你用过 Claude Code 的 **Agent Teams**,或者想同时运行多个 Claude 实例,Tmux 几乎是必备工具:

- **Agent Teams 的 Split-pane 模式**:每个 Teammate 显示在独立窗格中;
- **后台运行**:任务继续执行,即使关闭终端;
- **会话持久化**:断线重连后恢复完整上下文;
- **多实例管理**:同时运行多个 Claude 会话,Claude 可以在 Tmux 中自动生成和管理多个 Agent。

### 三个核心概念

| 概念 | 类比 | 说明 |
| --- | --- | --- |
| **Session(会话)** | 工作空间 | 最顶层容器,即使断开连接也持续运行 |
| **Window(窗口)** | 浏览器标签页 | 一个会话可以包含多个窗口 |
| **Pane(窗格)** | 分屏 | 一个窗口可以分割成多个窗格 |

```
Session(会话)
└── Window 1: Development        Window 2: Testing
    ├── Pane 1 (Claude 1)
    ├── Pane 2 (Claude 2)
    └── Pane 3 (Logs)
```

## 代码 / 实现:安装、命令速查与配置

### 安装

```bash
# macOS
brew install tmux

# Ubuntu/Debian/WSL
sudo apt-get install tmux

# CentOS/RHEL
sudo yum install tmux

tmux -V   # 验证,输出类似 tmux 3.6a
```

**前缀键**:Tmux 所有命令都以前缀键开始,默认 `Ctrl+B`——按下 `Ctrl+B`(不松开)后按命令键。例如分割窗口:`Ctrl+B` 然后按 `%`。

### 命令速查

**会话管理**

| 命令 | 说明 |
| --- | --- |
| `tmux` | 创建新会话 |
| `tmux new -s name` | 创建命名会话 |
| `tmux ls` | 列出所有会话 |
| `tmux attach -t name` | 连接到会话 |
| `tmux kill-session -t name` | 关闭会话 |
| `Ctrl+B d` | 分离当前会话(后台运行) |

**窗口管理**:`Ctrl+B c`(新建)、`Ctrl+B n/p`(下一个/上一个)、`Ctrl+B 0-9`(切换)、`Ctrl+B ,`(重命名)、`Ctrl+B &`(关闭)。

**窗格管理**:`Ctrl+B %`(垂直分割)、`Ctrl+B "`(水平分割)、`Ctrl+B 方向键`(移动)、`Ctrl+B x`(关闭)、`Ctrl+B z`(最大化/还原)、`Ctrl+B {` `}`(移动窗格)。

**其他**:`Ctrl+B [`(复制模式可滚动)、`q`(退出复制模式)、`Ctrl+B ?`(显示所有快捷键)。

### 推荐的 ~/.tmux.conf

```tmux
# 使用 Ctrl+A 作为前缀键(更容易按)
set -g prefix C-a
unbind C-b
bind C-a send-prefix

# 启用鼠标支持
set -g mouse on

# 增加历史缓冲区(Claude 输出很多)
set -g history-limit 50000

# vim 风格的窗格导航
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

# 更直观的分割快捷键
bind | split-window -h
bind - split-window -v

# 快速重载配置
bind r source-file ~/.tmux.conf \; display "Config reloaded!"

# 256 色支持
set -g default-terminal "screen-256color"
set -ga terminal-overrides ",*256col*:Tc"

# 窗口编号从 1 开始(0 太远了)
set -g base-index 1
setw -g pane-base-index 1

# 状态栏优化
set -g status-position bottom
set -g status-left-length 40
set -g status-right-length 60
```

重载:`tmux source-file ~/.tmux.conf`。

### Claude Code 专用配置:按目录的 Claude 弹窗

```tmux
# Claude 会话弹窗快捷键(Ctrl+A 然后按 y)
bind -r y run-shell '\
  SESSION="claude-$(echo #{pane_current_path} | md5sum | cut -c1-8)"; \
  tmux has-session -t "$SESSION" 2>/dev/null || \
  tmux new-session -d -s "$SESSION" -c "#{pane_current_path}" "claude"; \
  tmux display-popup -w80% -h80% -E "tmux attach-session -t $SESSION"'
```

效果:按 `Ctrl+A y` 打开 Claude 弹窗;**每个目录有独立 Claude 会话**;关闭弹窗后会话继续运行;重新打开恢复之前的对话。

## 实践 / 应用:与 Claude Code 的四种工作流

### 基础用法:后台运行 Claude

```bash
tmux new -s claude-work
claude
# Ctrl+B d 分离(Claude 继续运行)
tmux attach -t claude-work   # 稍后重新连接
```

**`--tmux` 原生集成**:Claude Code 原生支持 Tmux——自动创建新 tmux 会话(命名 `claude-{随机ID}`)并在其中启动 Claude:

```bash
claude --tmux
claude -w feature-auth --tmux   # 配合 worktree
```

### 工作流一:多项目并行

```bash
tmux new -s project-a
claude -w feature-x          # 分离后(Ctrl+B d)创建另一个会话
tmux new -s project-b
claude -w bugfix-y

tmux switch -t project-a     # 会话间切换
tmux switch -t project-b
# 或 Ctrl+B s 列出所有会话选择
```

### 工作流二:开发仪表盘(Claude + Logs + Tests 三窗格)

```bash
tmux new -s dev
# Ctrl+B % 垂直分割,Ctrl+B " 水平分割右侧
# 布局:左上 Claude / 右上 Logs / 右下 Tests
claude                 # 第一个窗格
tail -f logs/app.log   # 第二个窗格
npm test -- --watch    # 第三个窗格
```

### 工作流三:远程开发(SSH 持久化)

Tmux 最强大的特性是会话持久化,特别适合 SSH 远程开发:

```bash
ssh user@server
tmux new -s remote-claude
claude
# Ctrl+B d 分离,exit 断开 SSH(Claude 继续运行)

# 稍后重新连接
ssh user@server
tmux attach -t remote-claude   # Claude 会话完整恢复
```

### 工作流四:Agent Teams 监控

```bash
# 使用 tmux 显示模式(每个 Teammate 独立窗格)
claude --teammate-mode tmux
# 或 settings.json 配置 {"teammateMode": "tmux"}

# 创建 Agent Team("创建 agent team 审查代码...")
# → 屏幕自动分割:Team Lead 上方,每个 Teammate 一个窗格
# → 点击不同窗格直接与对应 Teammate 交流
```

### 故障排除

| 问题 | 解决方案 |
| --- | --- |
| 颜色显示不正确 | 确保 `TERM=xterm-256color` |
| 鼠标不工作 | 配置加 `set -g mouse on` |
| 复制粘贴问题 | 复制模式下用 Enter 复制 |
| 会话消失了 | 检查 `tmux ls`,可能是系统重启 |

清理孤儿会话(Claude Code 有时会留下未清理的 tmux 会话):`tmux ls` 查看 → `tmux kill-session -t session-name` 杀指定 → `tmux kill-server` 全杀(谨慎!)。iTerm2 用户可用原生集成 `tmux -CC` 把窗格转成原生标签页和分屏。

## 总结

- **本质**:终端复用器,核心是**会话持久化**——断开连接会话继续运行,重连后恢复;
- **三概念**:Session(工作空间)/ Window(标签页)/ Pane(分屏);
- **Claude Code 集成**:`claude --tmux` 原生支持、`--teammate-mode tmux` 让 Agent Teams 每个 Teammate 独立窗格、`claude -w <branch> --tmux` 配合 worktree;
- **何时需要**:长任务(需要)、Agent Teams(强烈推荐)、远程开发(必须)、多项目并行(推荐);简单单次对话不需要;
- **最小命令集**:`tmux new -s work` → `Ctrl+B d` → `tmux attach -t work` → `Ctrl+B %` / `"` 分割 → `Ctrl+B 方向键` 切换;
- **下一步**:把 Tmux 与会话隔离配合,见站内 [Git Worktree](../experience/git-worktree-parallel-agents.md) 与 [Agent Teams](claude-worktree-teams.md)。

## 延伸阅读

- Tmux Wiki:https://github.com/tmux/tmux/wiki
- 站内:[Claude Code Worktree 与 Agent Teams](claude-worktree-teams.md)(Agent Teams 的 tmux 显示模式)、[Git Worktree 多 Agent 并行](../experience/git-worktree-parallel-agents.md)(worktree + tmux 组合)、[Claude Code 深度解析子主题](index.md)
