> 素材说明(2026-08-13):Anthropic 官方文章检索(第二轮),全部为 web_fetch 抓取的一手官方源,经核实可溯源。
>
> **本轮收录 4 篇**:
>
> 1. **Effective harnesses for long-running agents** — Anthropic Engineering,2025-11-26
>    - https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
>    - 双 agent 方案(initializer + coding agent)、init.sh + claude-progress.txt + feature_list.json 三件套、JSON 只改 passes 字段、Puppeteer MCP 自测
>    - 归档:`03-agents/agent-harness-long-running.md`
>
> 2. **Equipping agents for the real world with Agent Skills** — Anthropic Engineering,2025-10-16(2025-12-18 更新开源 agentskills.io)
>    - https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
>    - skill = 目录 + SKILL.md、三级 progressive disclosure、捆绑 Python 确定性工具、先 eval 后沉淀、安全审计
>    - 归档:`07-agent-coding/skills/agent-skills-design.md`
>
> 3. **Writing effective tools for agents — with agents** — Anthropic Engineering,2025-09-11
>    - https://www.anthropic.com/engineering/writing-tools-for-agents
>    - 工具五原则(少而精/命名空间化/高信号上下文/Token 效率/描述 prompt 工程)、UUID→语义 ID、eval 循环
>    - **+ Advanced tool use**(2025-11-24,https://www.anthropic.com/engineering/advanced-tool-use):Tool Search Tool / Programmatic Tool Calling / Tool Use Examples 三个 beta
>    - 合并归档:`03-agents/agent-tool-design-practice.md`
>
> 4. **Beyond permission prompts: making Claude Code more secure and autonomous(sandboxing)** — Anthropic Engineering,2025-10-20
>    - https://www.anthropic.com/engineering/claude-code-sandboxing
>    - OS 级双边界(文件系统+网络隔离)、权限提示减少 84%、凭证外置模式(git token/MCP OAuth)、开放沙箱运行时
>    - 归档:`07-agent-coding/claude-code-deep-dive/claude-code-sandboxing.md`
>
> **已评估未收录**:think tool(已被 extended thinking 取代,过时)、Scaling Managed Agents(自建平台场景,偏架构)、prompt-injection-defenses(模型侧防御为主,工程可复制性弱)、How Anthropic teams use Claude Code(灵感清单型)。
>
> **已收录清单**(前两轮):Building effective agents / Effective context engineering / Claude Agent SDK / multi-agent research system / Best practices for Claude Code。
