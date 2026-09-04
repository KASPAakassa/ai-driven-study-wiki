> 素材说明(2026-08-13):OpenAI 官方技术文章检索,全部为 web_fetch 抓取的一手官方源。
>
> **本轮处理 4 篇**:
>
> 1. **Harness engineering: leveraging Codex in an agent-first world** — openai.com/index/harness-engineering(Ryan Lopopolo 团队,约 2026-02)
>    - 5 个月内部 beta 0 行手写代码、~100 万行代码、~1500 PR、人均 3.5 PR/天;AGENTS.md 是目录非百科全书;固定分层 + 自定义 linter;agent legibility;熵管理
>    - 归档:`07-agent-coding/experience/openai-harness-engineering.md`(新文章)
>
> 2. **Shell + Skills + Compaction: Tips for long-running agents that do real work** — developers.openai.com/blog/skills-shell-tips
>    - 三件套(Skills/hosted shell/server-side compaction)、skill description 路由逻辑(缺负例 Glean 触发率掉 ~20%)、确定性优先、双层 allowlist + domain_secrets、/mnt/data 交接、Glean Salesforce skill eval 73%→85% TTFT -18.1%
>    - 归档:`03-agents/agent-long-running-openai.md`(新文章,与 Anthropic harness-long-running 交叉)
>
> 3. **Testing Agent Skills Systematically with Evals** — developers.openai.com/blog/eval-skills
>    - eval = prompt → run → 少量检查 → 可比分数;outcome/process/style/efficiency 四类检查;10-20 prompt;should_trigger 正反例;codex exec --json 事件流;--output-schema + rubric
>    - 归档:**补充进** `07-agent-coding/skills/skill-evaluation.md`(新增 OpenAI 官方方法章节)
>
> 4. **Prompt engineering(官方指南 2026 版)** — developers.openai.com/api/docs/guides/prompt-engineering
>    - 与站内 Datawhale 旧版相比新增:Responses API(output 数组)、developer 角色优先级与消息结构、prompt 对象 2026-06-03 降级/v1/prompts 2026-11-30 关停(prompt 版本化进代码)、GPT-5 系列 prompting、agentic 三实践
>    - 归档:**补充进** `07-agent-coding/experience/openai-prompt-guide.md`(新增 2026 版变化章节)
>
> **未抓到**:A practical guide to building agents(2025-04)与 Reducing hallucinations 均已从 openai.com 下线(404),不收录。
