# 上下文工程官方一手资料:Anthropic 定义、Claude Code 实践与 AGENTS.md 标准

> **一句话摘要**:上下文工程(Context Engineering)的权威来源四件套——Anthropic 官方定义与注意力预算模型、《Claude Code best practices》的上下文管理实践、Claude Code 五层记忆体系、Linux Foundation 的 AGENTS.md 开放标准。本文是 [上下文工程管理方案](context-engineering-playbook.md) 的官方一手资料深化篇。
>
> **来源**:四篇官方资料(Anthropic 工程博客 ×2、Claude Code 官方文档、agents.md 规范),文献清单见 `docs/inbox/context-engineering-references-source.md`

## 概念:官方定义与核心模型

### Anthropic《Effective context engineering for AI agents》

**定义**:上下文工程是**提示工程的自然演进**——提示工程聚焦"如何写出高效指令(尤其 system prompt)";上下文工程覆盖**在 LLM 推理期间策展并维护最优 token(信息)集合的整套策略**,包括系统指令、工具、MCP、外部数据、消息历史等所有可能进入上下文的内容。它是**迭代式**的:每一次决定"把什么传给模型"都是一次策划。

**Context Rot(上下文腐化)**:借鉴 needle-in-a-haystack 基准——上下文窗口内 token 数增加,**模型准确回忆其中信息的能力下降**(所有模型都如此,只是退化曲线缓急不同)。上下文必须被视为**边际收益递减的有限资源**。

**注意力预算模型**:LLM 有类似人类工作记忆的"注意力预算",每引入一个新 token 都消耗一部分。根源是架构性约束——Transformer 让每个 token 可关注所有 token,产生 **n² 对两两关系**;上下文越长,模型捕获这些关系的能力被稀释;且训练数据中短序列占多,模型对长程依赖经验不足。位置编码插值可扩展窗口但损失位置精度。**性能是渐变梯度而非硬悬崖**。

**System prompt 的 "right altitude"(正确高度)**:两个失败模式之间的"金发姑娘区间"——一端是硬编码复杂 if-else 逻辑(脆弱易坏),另一端是过于笼统的高层指引(缺乏信号)。**最佳高度 = 足够具体以引导行为,又足够灵活以提供强启发式**。做法:用 XML/Markdown 把 prompt 划分为 `<background_information>`、`<instructions>`、工具指南、输出描述等独立区块;先跑最小 prompt,再基于失败模式增量补充。

### 关键技术建议

- **工具**:保持精简、自包含、健壮、意图清晰("人类都无法判断该用哪个工具,智能体更做不到");
- **示例**:策展**多样化、有代表性的范式示例**,而非堆砌边缘用例清单;
- **Just-in-time 检索**:用轻量标识符(文件路径、存储查询、Web 链接)在运行时按需加载,而非预处理全部数据;元数据(目录层级、命名、时间戳)本身就是行为信号;
- **长时程任务三大技术**:压缩(总结近满上下文后重启,最轻量形式是**清除工具调用与结果**)、结构化笔记(上下文外写 NOTES.md/待办清单)、多智能体架构(主 agent 计划综合、子 agent 干净窗口探索只回传 1-2K 摘要);
- **总原则**:始终寻找"最大化期望结果概率的**最小高信号 token 集合**";"做最简单有效的事"。

## 原理:Claude Code best practices 的上下文管理

### 核心原则:上下文窗口是最重要的资源

Claude Code 是 agentic 编码环境——自动读文件、跑命令、改代码。几乎所有最佳实践源于同一约束:**窗口很快被填满,模型性能随填充下降**。窗口快满时模型"忘记"早期指令、犯更多错。

### 给 agent 可验证的检查手段

> 不给 Claude 可运行的检查,它只能靠"看起来完成"收尾,你就成了验证循环。

- **检查 = 任何返回 pass/fail 的信号**:测试套件、构建退出码、linter、diff 脚本、截图对比;
- **Prompt 写法**:给验证标准(写 `validateEmail` 附示例测试并"实现后跑测试")、UI 用"贴截图→实现→对比→修差异"、错误处理"贴真实报错,修到构建通过";
- **门控强度四档**:单条 prompt 内迭代;跨会话用 `/goal` 条件;确定性门控用 Stop hook;CI 级门控。

### 探索 → 计划 → 编码 → 提交四阶段工作流

- **Explore**:`Shift+Tab` 进 plan mode,只读探索不改文件;
- **Plan**:让 Claude 产出详细实现计划,`Ctrl+G` 可在编辑器直接改计划;
- **Implement**:批准后按计划编码并对照验证(写测试、跑套件、修失败);
- **Commit**:写描述性 commit 信息并开 PR;
- **权衡**:小修直接做;方案不确定/改多文件/不熟悉代码时才值得计划——**能一句话描述 diff 就跳过计划**。

### token 监控与上下文管理技巧

- **监控**:自定义 status line 持续跟踪上下文占用;`/context` 确认 CLAUDE.md 加载、`/cost` 看花费;
- **清理与压缩**:无关任务间勤用 `/clear`;接近上限自动压缩;手动定向压缩 `/compact <instructions>`;`/rewind`(Esc+Esc)按 checkpoint 局部摘要;侧边问题用 `/btw`(不进入历史);
- **隔离**:subagent 在独立窗口读大量文件、只回传摘要;
- **纠错尽早**:同一问题纠错 2 次以上就 `/clear` + 重写更精准 prompt——**新会话好 prompt 永远胜过堆满失败尝试的长会话**;
- **五类失败模式**:kitchen sink(贪多)、反复纠错、过度指定 CLAUDE.md、信任后不验证、无边界探索。

## 代码 / 实现:Claude Code 五层记忆体系

按作用域分五层,**后加载覆盖先加载,越具体优先级越高**:

| 层级 | 位置 | 用途 |
| --- | --- | --- |
| ① 企业托管 | macOS `/Library/Application Support/ClaudeCode/CLAUDE.md` | 企业统一策略,只读下发 |
| ② 用户级 | `~/.claude/CLAUDE.md` | 个人全局偏好,跨项目 |
| ③ 项目级 | `./CLAUDE.md`(或 `./.claude/CLAUDE.md`) | 团队共享,进 Git |
| ④ 本地级 | `./CLAUDE.local.md` | 个人笔记,gitignore |
| ⑤ 路径级规则 | `.claude/rules/*.md` | 带 glob/文件类型作用域,按路径触发 |

**Auto Memory**:Claude 自己在 `~/.claude/projects/<项目>/memory/MEMORY.md` 持续记录项目模式(命令、调试洞见、隐含约定),每次新会话自动加载前 200 行/25KB——跨会话学习沉淀。

**/init 生成**:扫描项目自动生成初始 CLAUDE.md。**注意:产物会包含模型能从代码推断的"废话",生成后建议删掉大半**再人工补全团队特有约定。

**编写有效指令规范**:

- **长度**:目标 <200 行(宽松 <300);超过 200 行遵循度明显下降(每段对话全量加载,过长浪费 token 稀释注意力);
- **内容**:只放"团队约定 + 构建命令 + 红线(Always/Ask first/Never)",领域知识用**引用文件**而非内联;
- **纪律**:每条规则是可执行指令;犯错驱动增长(让 Claude 犯过的错写回文件);CLAUDE.md 是软约束,硬拦截需 Hooks/CI 兜底。

## 实践 / 应用:AGENTS.md 开放标准

### 定义与定位

AGENTS.md 是 Linux Foundation 旗下 **Agentic AI Foundation** 维护的简单开放文件格式——**"给 agent 看的 README"**:一个专用且可预测的位置,存放为 AI 编码智能体提供工作所需上下文与指令的内容。与 README.md(给人看)严格区分;不搞专有文件,采用"任何生态都能用"的名字与格式。

### 采纳规模与跨工具支持

- GitHub **60,000+ 开源项目**采纳(openai/codex、apache/airflow 等);
- 跨工具兼容:OpenAI Codex、Google Jules、Factory、Aider、Cursor、RooCode、Gemini CLI、GitHub Copilot Coding Agent、Windsurf、VS Code、Zed、Warp、Devin、JetBrains Junie 等 20+;
- 源自 OpenAI Codex、Amp、Google Jules、Cursor、Factory 等生态协作。

### Monorepo 嵌套与加载规则

- **大型 monorepo 可在各子包放嵌套 AGENTS.md**,智能体自动读取目录树中**最近**的,距离最近者优先级最高(就近覆盖);OpenAI 主仓库有 88 个;
- 加载规则:无必需字段,agent 仅解析文本;**指令冲突时距被编辑文件最近的 AGENTS.md 胜出,用户显式聊天提示覆盖一切**;若列出测试命令,agent 会自动执行相关程序化检查并在完成前修复失败;文档可随时更新(活的文档)。

### 内容建议(~100 行指针式)

项目概览、构建与测试命令、代码风格规范、测试说明、安全注意事项、提交信息/PR 规范、安全陷阱、部署步骤——"你会告诉新同事的一切"。Aider 配置 `.aider.conf.yml` 写 `read: AGENTS.md`;Gemini CLI 在 `.gemini/settings.json` 设 `{ "context": { "fileName": "AGENTS.md" } }`。

## 总结

- **官方定义**:上下文工程 = 迭代式策划"每轮传给模型的最优 token 集合";注意力预算模型(n² 注意力稀释)+ context rot(有限资源);
- **right altitude**:system prompt 足够具体引导行为、足够灵活提供启发式;工具精简、示例有代表性、JIT 检索、长任务三大技术;
- **Claude Code 实践**:上下文窗口是最重要资源;给可验证检查(四档门控);Explore→Plan→Implement→Commit 四阶段;勤 /clear、/compact、subagent 隔离、纠错尽早;
- **五层记忆**:企业/用户/项目/本地/路径级,后加载覆盖先加载;Auto Memory 自动沉淀;CLAUDE.md <200 行、引用优于内联;
- **AGENTS.md**:给 agent 的 README,60k+ 仓库、20+ 工具、monorepo 就近嵌套、"最近者优先、用户提示覆盖一切";
- **下一步**:工具侧机制对比见 [上下文工程管理方案](context-engineering-playbook.md),AGENTS.md 实战见 [给 Coding Agent 立规矩](../07-agent-coding/experience/agent-rules-agents-md.md)。

## 延伸阅读

- Anthropic《Effective context engineering for AI agents》:https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic《Claude Code best practices》:https://anthropic.com/engineering/claude-code-best-practices(已重定向至 code.claude.com/docs/en/best-practices)
- Claude Code《How Claude remembers your project》:https://code.claude.com/docs/en/memory
- AGENTS.md 规范:https://agents.md
- 站内:[上下文工程管理方案](context-engineering-playbook.md)(完整体系)、[Context Engineering 四杠杆](context-engineering.md)(基础)、[给 Coding Agent 立规矩](../07-agent-coding/experience/agent-rules-agents-md.md)、[Claude Code 深度解析](../07-agent-coding/claude-code-deep-dive/index.md)
