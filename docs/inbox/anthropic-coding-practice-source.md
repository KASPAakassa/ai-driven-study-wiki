> 素材说明(2026-08-12):Anthropic 官方 coding 实践经验检索成果,经核实可溯源。
>
> **整理来源**(全部为 Anthropic 官方一手资料,非用户投放):
>
> 1. **How we built our multi-agent research system** — Anthropic Engineering 博客,2025-06-13
>    - https://anthropic.com/engineering/built-multi-agent-research-system
>    - 核心:orchestrator-worker 多智能体架构、内部评测(多 Agent 比单 Agent 高 90.2%)、token 经济学(4×/15×)、委派 prompt 原则、LLM-as-judge 评估、生产可靠性
>    - 归档去向:`03-agents/agent-multi-agent-research-system.md`
>
> 2. **Best practices for Claude Code** — Claude Code 官方文档
>    - https://anthropic.com/engineering/claude-code-best-practices(镜像)/ platform.claude.com/docs/en/claude-code/best-practices(旧路径,已 404)
>    - 核心:验证检查四档门控、四阶段工作流(Explore/Plan/Implement/Commit)、提供具体上下文四策略、自动化与规模化(claude -p/Writer-Reviewer/fan-out/auto mode/对抗性审查)、五大失败模式
>    - 归档去向:`07-agent-coding/claude-code-deep-dive/claude-code-best-practices.md`
>
> **已评估未独立成文**:
> - *Building agents with the Claude Agent SDK*(2025-09-29):核心思路已在 `vibe-coding-engineering-practice.md` 扩展章节引用,不重复成文;
> - *How Anthropic teams use Claude Code*(2025-07-24):灵感清单型、方法论密度低,暂不收录;
> - *Effective context engineering for AI agents*(2025-09-29):已由 `03-agents/context-engineering-official-sources.md` 完整覆盖。
