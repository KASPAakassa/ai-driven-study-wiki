# ⌨️ 编码 Agent 工具(CLI / IDE 型 Harness)

> 面向"AI 写代码"场景的 Harness:在终端或 IDE 里运行,能读代码库、改文件、跑命令、提 PR 的 Coding Agent。这是目前最成熟、最常用的一类 Harness。

## 概念

编码 Agent 型 Harness 的共同特征:①以**终端/IDE** 为入口;②能自主完成"理解需求 → 定位代码 → 修改 → 测试 → 提交"的循环;③通常支持工具调用、Agent 规则文件(如 `AGENTS.md`/`CLAUDE.md`)与权限控制。差异主要在:托管方式(官方 API vs 自带模型)、IDE 集成深度、可扩展性(插件/Skill)、自主程度。

## 清单

| 名称 | 仓库 | 一句话定位 | 亮点 / 特点 |
| --- | --- | --- | --- |
| **Claude Code** | [anthropics/claude-code](https://github.com/anthropics/claude-code) | Anthropic 官方终端编码 Agent | 官方插件市场(可装 [mattpocock/skills](../07-agent-coding/skills/mattpocock-skills.md) 这类 Skill 包);规则文件、hooks、子代理能力成熟 |
| **Codex CLI** | [openai/codex](https://github.com/openai/codex) | OpenAI 官方终端编码 Agent | 支持 AGENTS.md 规则、沙箱执行、与 ChatGPT 会话同步 |
| **Gemini CLI** | [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) | Google 开源终端编码 Agent | 多模型接入,轻量,支持交互式与脚本模式 |
| **Aider** | [Aider-AI/aider](https://github.com/Aider-AI/aider) | 老牌开源终端结对编程工具 | 最早流行的一批之一;git 感知、diff 式编辑、多模型支持 |
| **Cline** | [cline/cline](https://github.com/cline/cline) | VS Code 开源编码 Agent(原 Claude Dev) | 深度集成 VS Code,支持自定义 MCP 工具、权限分级 |
| **Roo Code** | [RooCodeInc/Roo-Code](https://github.com/RooCodeInc/Roo-Code) | Cline 的社区 fork 扩展 | 多"模式/角色"切换、自定义提示词、面向重度用户 |
| **OpenHands** | [All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands) | 开源自主软件开发 Agent(原 OpenDevin) | 端到端自主完成开发任务,支持云/本地运行与评估框架 |
| **Goose** | [block/goose](https://github.com/block/goose) | Block 开源的本地 Agent 框架 | 本地运行、可扩展工具集,偏自动化与桌面使用 |
| **Continue** | [continuedev/continue](https://github.com/continuedev/continue) | IDE(VS Code/JetBrains)开源编码 Agent | 开源社区活跃,支持本地模型与自定义 |
| **OpenClaw** | [openclaw/OpenClaw](https://github.com/openclaw/OpenClaw) | 长程(Long-horizon)Agent 框架 | 2026 年社区热潮("龙虾");多步任务、深度工具调用;配套评测见 [PinchBench](harness-tools.md) |

!!! note "待补充"
    Sourcegraph 曾开源的 **Amp** 已更名下架,暂不收录;还有其他你常用但没列出的工具,丢进 `docs/inbox/` 我来补。

## 实践 / 应用:如何选型

1. **先看模型与成本**:官方系(Claude Code / Codex / Gemini CLI)通常绑自家模型,开箱即用;社区系(Aider、Cline、OpenHands)可接入本地或任意 API。
2. **看 IDE 习惯**:重度 VS Code 用户优先 Cline/Roo Code/Continue;纯终端流用户优先 Claude Code/Codex/Aider。
3. **看自主程度**:要"全自动跑任务"选 OpenHands/OpenClaw 这类长程 Agent;要"结对辅助"选 Aider 这类交互式。
4. **可扩展性**:需要自定义 Skill/工具时,优先支持插件与 MCP 的(Claude Code、Cline)。
5. **规则先行**:无论选哪个,`AGENTS.md`/`CLAUDE.md` 规则文件都是让 agent 按团队方式干活的关键(见 [mattpocock/skills](../07-agent-coding/skills/mattpocock-skills.md) 的 `writing-for-agents` 思路)。

## 延伸阅读

- 站内:[Harness 章节首页](index.md)、[mattpocock/skills 总结](../07-agent-coding/skills/mattpocock-skills.md)、[Agent 开发实践](../03-agents/agent-practice.md)
- 外部:各仓库 README(上面的链接)
