# 🧠 Claude Code 深度解析

> 从"使用技巧"到"源码级架构":深入理解 Claude Code 的系统架构、工具调用系统、Worktree/Agent Teams 并行机制、Skills/Plugin/Subagent 扩展体系,以及来自创始人与社区的隐藏技巧。Claude Code 不只是"模型加一堆工具",而是一套把工具调用组织成**可验证 agent loop** 的运行时。

## 本章节文章

- [Claude Code 架构与工具系统](claude-architecture-tools.md) — 组件全景(MCP/Skills/Subagents/Hooks/Plugins)+ 工具调用系统:从"会调工具"到"可收束的 agent runtime"
- [Claude Code 官方最佳实践](claude-code-best-practices.md) — 验证检查四档门控、四阶段工作流(Explore/Plan/Implement/Commit)、具体上下文四策略、自动化规模化(claude -p/Writer-Reviewer/fan-out/auto mode/对抗性审查)、五大失败模式(上下文细节见 03-agents official-sources)
- [Claude Code Sandboxing:双边界隔离与凭证外置](claude-code-sandboxing.md) — OS 级双边界(文件系统+网络隔离)组合拳、权限提示减少 84%、凭证永不进沙箱(git token/MCP OAuth 由外部代理附加)、sandbox-runtime 开源(agent 安全基线模板)
- [Claude Code Worktree 与 Agent Teams](claude-worktree-teams.md) — 并行开发的隔离底座与多智能体协作团队
- [Claude Code Cross-session Messaging](claude-cross-session-messaging.md) — 多个 Session 直接对话:寻址(磁盘注册+Inbox Socket)→ 异步投递 → 进入决策循环 → 权限继承(设计提炼见 03-agents)
- [Claude Code Dynamic Workflows(/workflow,ultracode)](claude-workflows.md) — 多智能体编排的底层实现:把计划从上下文窗口搬进 JS 运行时,几十到上百 Agent 并行、确定性执行、对抗性验证
- [Claude Code Skills / Plugin / Subagent](claude-skills-plugin-subagent.md) — 扩展体系三件套
- [Claude Code 隐藏技巧](claude-code-tips.md) — 创始人与社区的实用技巧聚合
- [Claude Code 源码解析(20 章全整合)](claude-code-harness-analysis.md) — learn-claude-code:从 30 行 Agent Loop 到完整 Harness——工具分发/权限/hooks/压缩/记忆/任务/团队/自治/Worktree/MCP 逐章源码机制
- [Tmux 入门:Claude Code 用户的终端复用器指南](tmux-for-claude-code.md) — Agent Teams split-pane 显示、`claude --tmux` 原生集成、长任务后台运行、SSH 远程开发会话持久化

## 收录说明

- 本子主题内容整理自 **Yu 的赛博工位**(https://yudesk.dev/docs/notes)的 Claude Code 系列笔记(约 19 篇),原始内容已抓取存档于 `docs/inbox/yudesk-claude-code/`;
- 定位与 [🔧 项目 Agent 配置](../agent-config/index.md)(搭建自己的配置)互补:本子主题讲 **Claude Code 本身的设计与使用**;
- "源码解析"指对 Claude Code 架构与机制(工具调用 loop、权限分层、组件协同)的深入拆解,非源码逐行注释。
