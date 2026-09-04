# 项目上下文工程 · 参考文献来源清单

> 用途：配套《项目上下文工程维护手册》（`project-context-engineering-playbook.md`）与《Agent Coding 上下文工程管理方案调研报告》（`agent-coding-context-engineering.md`）的资料出处，可直接导入知识库。
> 收录时间：2026-08-10
> 说明：所有链接均已验证可访问；标注「营销型文章」的条目，其方法论部分可参考，产品推广部分按需取舍。

---

## 一、官方一手资料（权威性最高）

### 1. Anthropic《Effective context engineering for AI agents》
- **原始链接**：https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- **类型**：官方工程博客
- **核心内容**：上下文工程（Context Engineering）的概念定义、与提示词工程的区别、context rot（上下文腐化）、注意力预算模型、系统提示词的"right altitude"等
- **对应手册章节**：〇 诊断 / 一 信息模型

### 2. Anthropic《Claude Code best practices》
- **原始链接**：https://anthropic.com/engineering/claude-code-best-practices
- **类型**：官方工程博客
- **核心内容**：Claude Code 使用最佳实践——上下文窗口是最重要的资源、给 agent 可验证的检查手段、探索→计划→编码→提交四阶段工作流、token 用量监控
- **对应手册章节**：八 工具侧自动化

### 3. Claude Code 官方文档《How Claude remembers your project》
- **原始链接**：https://code.claude.com/docs/en/memory
- **类型**：官方产品文档
- **核心内容**：CLAUDE.md 五层记忆体系（企业托管/用户/项目/本地/路径规则）、Auto Memory 自动记忆机制、/init 生成、编写有效指令的规范
- **对应手册章节**：三 AGENTS.md 模板 / 六 运行时状态

### 4. Linux Foundation《AGENTS.md》开放规范
- **原始链接**：https://agents.md
- **类型**：开放标准官方站点
- **核心内容**：AGENTS.md 是什么（"给 agent 的 README"）、60k+ 开源项目采用、跨工具支持清单（Aider/Cursor/Codex/Gemini CLI/Copilot/RooCode/Windsurf/Jules 等）、monorepo 嵌套用法、OpenAI 主仓库 88 个 AGENTS.md 的示例
- **备注**：页面上标注 60k+ 项目；「由 Linux Foundation 下属 Agentic AI Foundation 托管」的说法来自社区二手文章，官方页面未直接声明，如需引用建议以 agents.md 官网为准
- **对应手册章节**：三 AGENTS.md 模板

---

## 二、文档漂移治理专题（内容工程方法）

### 5. MadCap《How to Prevent Content Drift Across Channels in 2026》
- **原始链接**：https://www.madcapsoftware.com/blog/prevent-content-drift-across-channels/
- **作者**：Angela Drury（MadCap 内容经理）
- **发布日期**：2026-07-23
- **类型**：厂商博客（MadCap 产品导向，营销型，方法论可参考）
- **核心内容**：内容漂移定义与危害；传统"纪律式"方案（季度评审/负责人/清单）治标不治本；单一来源治理（Single-Source Governance）四要素——**清晰的所有权、版本控制与变更追踪、绑定业务触发器的评审周期、自动化发布工作流**；成熟治理的标志与衡量指标
- **对应手册章节**：〇 诊断 / 七 维护流程

### 6. Falconer《How to consolidate documentation into one source of truth for engineering teams》
- **原始链接**：https://falconer.com/guides/consolidate-documentation
- **发布方**：Falconer Guides（营销型技术指南，作者未署名）
- **发布日期**：2026-06-04
- **核心内容**：集中化 ≠ 单一事实来源（还需版本控制+权限+治理三层）；**文档衰减是维护问题不是写作问题**——过时文档比缺失文档更危险；季度评审失效的根本原因（更新时上下文已褪色）；落地方法论：审计→选型→具名负责人治理→分阶段迁移
- **对应手册章节**：〇 诊断 / 九 快速启动

### 7. Docuwiz《Docs-as-Code: How to Prevent API Documentation Drift》
- **原始链接**：https://blog.docuwiz.io/p/docs-as-code-how-to-prevent-api-documentation
- **发布日期**：2026-03-18
- **类型**：技术营销文章（末尾推广 Docuwiz 产品，方法论部分可参考）
- **核心内容**：文档漂移四成因（文档在代码库外/所有权分散/CI 忽略文档/迭代快于更新）；Docs-as-Code 工作流——文档进 Git、与代码同 PR 评审、版本控制、CI/CD 校验（死链/OpenAPI schema 匹配）；关键洞见：**仅把文档放进 Git 不够，手动发布仍会漂移，需要 Git 同步自动发布**
- **对应手册章节**：七 维护流程 / 八 工具侧自动化

### 8. Everdone《Docs as a CI/CD Gate: The Simple Pass/Fail That Keeps Knowledge Current》
- **原始链接**：https://everdone.ai/whats-new/guides-resources/Docs-as-a-CI-CD-Gate-The-Simple-Pass-Fail-That-Keeps-Knowledge-Current
- **发布日期**：2025-12-03
- **类型**：厂商博客（营销型，方法论可参考）
- **核心内容**：文档门禁（Documentation Gate）——把文档校验做成 CI 的 pass/fail 检查（函数/模块变更却无对应文档更新则阻塞合并）；AI 驱动的文档门禁（语义比对而非文本比对）
- **对应手册章节**：八 工具侧自动化（CI 文档门禁）

---

## 三、注释纪律（代码内上下文）

### 9. 社区 Skill《code-comments》（jylhis / skillsmp 托管）
- **原始链接**：https://skillsmp.com/zh/creators/jylhis/skills/skills-engineering-code-comments
- **类型**：社区开源 Skill（Claude Code / Codex 可用技能）
- **核心内容**：注释何时值得写 vs 自我文档化代码；**解释 WHY 而非复述 WHAT**；docstring 与行内注释的区分；TODO/FIXME 约定（带 owner/issue 链接）；避免注释腐烂与被注释掉的死代码；AI 过度注释倾向
- **对应手册章节**：五 注释纪律

### 10. 社区 Skill《comment-guidelines》（skillmd.ai 托管）
- **原始链接**：https://skillmd.ai/skills/comment-guidelines
- **类型**：社区开源 Skill
- **核心内容**：注释指南，可自动应用——改代码时删除复述型注释、保留 WHY 注释、注释过期即更新、不为凑篇幅加注释；含 BAD/GOOD 对照示例
- **对应手册章节**：五 注释纪律

### 11. 社区 Skill《code-commenting》（monkilabs/opencastle 系列）
- **原始链接**：https://claudewave.com/en/skills/monkilabs-opencastle-code-commenting
- **类型**：社区开源 Skill（Claude Code 可安装）
- **核心内容**：WHY not WHAT 注释规则表；注释标记约定（TODO/FIXME/HACK/NOTE/WARNING/PERF/SECURITY/DEPRECATED）；反模式清单（注释掉的代码、注释里的 changelog、装饰性分隔线）；注释质量检查清单
- **对应手册章节**：五 注释纪律

---

## 四、补充阅读（上下文工程方法论，非手册直接引用）

> 以下为《Agent Coding 上下文工程管理方案调研报告》中已收录的延伸来源，按需取用。

### 12. 报告：Agent Context Compaction for Long-Running Sessions（Zylos Research）
- **原始链接**：https://zylos.ai/en/research/2026-04-21-agent-context-compaction-long-running-sessions/
- **核心内容**：压缩技术全景（滚动摘要/分层摘要/map-reduce/选择性淘汰 LRU/重要性打分）；压缩的信息损失代价（Factory 基准 2.19-2.45/5.0）；lost-in-the-middle 效应

### 13. 报告：Prompt Caching for AI Agents（Zylos Research）
- **原始链接**：https://zylos.ai/research/2026-02-24-prompt-caching-ai-agents-architecture
- **核心内容**：静态前缀+动态后缀布局、缓存破坏三规则、缓存健康度指标、多租户缓存隔离

### 14. 文章：How prompt caching cuts AI agent costs by 90%（usewire.io）
- **原始链接**：https://usewire.io/blog/how-prompt-caching-cuts-ai-agent-costs
- **核心内容**：三家厂商缓存折扣、system-prompt-only 缓存策略跨厂商降本 41-80%、缓存误用三坑

### 15. 文章：Context Engineering, Compaction & Advanced Vibe Coding（luminhkhuong.dev）
- **原始链接**：https://luminhkhuong.dev/technical-knowledge/ai-agents/context-engineering
- **核心内容**：四大策略（检索/外置/隔离/压缩）、context rot 与 context drift 的区别、token tax 概念

### 16. 文章：Context Engineering: Agent 架构师的核心手艺（中文，cuiliang.ai）
- **原始链接**：https://cuiliang.ai/posts/prompt-caching-context-engineering
- **核心内容**：Compaction 三层策略（Raw→Compact→Summarize）、注意力预算、context rot 三症状

### 17. 文章：Context Engineering 不是写更长 Prompt，而是管理注意力预算（中文，掘金）
- **原始链接**：https://juejin.cn/post/7640643117474201641
- **核心内容**：上下文预算分配示例、RAG/Memory/State 三者分离、回放评测法

### 18. 文章：Codex CLI Context Window Budget（danielvaughan）
- **原始链接**：https://codex.danielvaughan.com/2026/04/20/codex-cli-context-window-budget-token-management-large-codebases
- **核心内容**：Codex 压缩机制、token 去向分析（工具结果占 81%）、单线程单任务纪律

---

## 速查表（一页版）

| # | 标题 | 来源方 | 类型 | 链接 |
|---|------|--------|------|------|
| 1 | Effective context engineering for AI agents | Anthropic | 官方博客 | anthropic.com/engineering/effective-context-engineering-for-ai-agents |
| 2 | Claude Code best practices | Anthropic | 官方博客 | anthropic.com/engineering/claude-code-best-practices |
| 3 | How Claude remembers your project | Claude Code | 官方文档 | code.claude.com/docs/en/memory |
| 4 | AGENTS.md 规范 | Linux Foundation | 开放标准 | agents.md |
| 5 | How to Prevent Content Drift Across Channels | MadCap | 厂商博客 | madcapsoftware.com/blog/prevent-content-drift-across-channels/ |
| 6 | Consolidate documentation into one source of truth | Falconer | 厂商博客 | falconer.com/guides/consolidate-documentation |
| 7 | Docs-as-Code: Prevent API Documentation Drift | Docuwiz | 厂商博客 | blog.docuwiz.io/p/docs-as-code-how-to-prevent-api-documentation |
| 8 | Docs as a CI/CD Gate | Everdone | 厂商博客 | everdone.ai/whats-new/guides-resources/Docs-as-a-CI-CD-Gate-... |
| 9 | code-comments skill | jylhis | 社区 Skill | skillsmp.com/zh/creators/jylhis/skills/skills-engineering-code-comments |
| 10 | comment-guidelines skill | skillmd | 社区 Skill | skillmd.ai/skills/comment-guidelines |
| 11 | code-commenting skill | opencastle | 社区 Skill | claudewave.com/en/skills/monkilabs-opencastle-code-commenting |

*补充阅读 12-18 的完整链接见上文对应条目。*
