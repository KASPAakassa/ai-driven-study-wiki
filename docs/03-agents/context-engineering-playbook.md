# Agent Coding 上下文工程管理方案:从概念到落地路线图

> **一句话摘要**:Context Engineering(上下文工程)是 2025-2026 年 Agent Coding 的核心技能——管理"模型每轮推理时看到什么"。本文整合全网调研(Anthropic/OpenAI/Google 官方资料 + Claude Code/Cursor/Codex 等工具实践 + 记忆系统生态 + 中英社区文章),给出完整体系:**理论基石**(context rot/漂移/四大失败模式/token 预算)、**六大工具机制对比**、**指令文件标准**(AGENTS.md)、**四大动态技术**(Compaction/Eviction/Caching/JIT)、**外部记忆系统**、**架构模式**与**分阶段落地路线图**。
>
> **来源**:全网资料调研报告《Agent Coding 上下文工程管理方案》(2026-08-10),原始资料存档于 `docs/inbox/context-engineering-survey-source.md`;配套文献清单见 `docs/inbox/context-engineering-references-source.md`;与站内 [Context Engineering 四杠杆](context-engineering.md) 互补(那篇讲基础杠杆,本文讲完整管理体系)

## 概念:为什么上下文工程成为核心

2023 年开发者学 Prompt Engineering(把指令写好);2025-2026 年行业转向 **Context Engineering**(管理模型每轮推理时看到什么)。Anthropic 官方定义:

> Context engineering 指为 LLM 推理期间**策划并维护最优 token 集合**的策略集,涵盖 System Prompt、工具定义、MCP、外部数据、消息历史等所有可能进入上下文的要素。与一次性写好提示词不同,上下文工程是**迭代式**的——每次决定"把什么传给模型"都是一次策划。

**五个必须做上下文工程的原因**:

| 原因 | 说明 |
| --- | --- |
| 有限注意力预算 | Transformer 是 n² pairwise attention,token 越多每个 token 分到的注意力越少;长上下文召回精度下降(needle-in-a-haystack 证实) |
| **Context Rot(上下文腐化)** | 上下文填充到 **70%-80%** 时推理质量就开始下降(不是等窗口满才崩);遗忘早期指令、重复劳动、重新引入已修复 bug |
| **Lost in the Middle** | 信息位于上下文**中段**时召回率大幅下降(多文档 QA 可掉 30+ 个百分点),两端最好 |
| 成本失控 | Agent 是输入密集型负载(Manus 输入/输出 token 比约 100:1);未优化长会话成本数量级增长 |
| 失败模式复合 | 污染(poisoning)→ 分心(distraction)→ 混淆(confusion)→ 冲突(clash)四种失败模式互相强化 |

> **结论:上下文必须当作"边际收益递减的有限资源"管理。大窗口 ≠ 可以乱塞。窗口是工作集(working set),不是数据库。**
>
> 中文社区比喻:Prompt Engineering 是教厨师做菜的口诀,Context Engineering 是配备齐全的厨房——食材、刀具、菜谱、计时器一切就位。模型不是缺资料,而是缺一张干净的工作台。

## 原理:核心概念速查

- **Context Rot(上下文腐化)**:随窗口填充推理质量渐进下降(Transformer 固有特性);触发阈值 70-80%;症状:矛盾前期决策、重复生成、遗忘开局约束、重引入已修复 bug;对策:主动压缩 + 结构化状态外置;
- **Context Drift(上下文漂移)**:agent 的"人设/目标/约束"因累积历史逐渐偏离原始意图(如"性能优先后端工程师"30 轮调试后变成"只顾眼前错误的调试助手");对策:定期重置/强化 system prompt;
- **四大失败模式**:poisoning(幻觉进上下文当事实扩散)/ distraction(被大量历史分心)/ confusion(无关内容干扰)/ clash(矛盾信息导致不一致);
- **Token 预算参考**(128K 窗口):System+规则 3% / 工具定义 2% / Few-shot 3% / RAG 检索 15% / 对话历史 25% / 工作记忆 28% / 安全缓冲 22%;32K 小模型下 **Compaction 是刚需**(10-15 次复杂工具交互即触顶)。

## 原理:六大工具上下文机制对比

### Claude Code——体系最完整的参考系

1. **记忆文件体系**:CLAUDE.md 五层作用域(企业托管→用户级→项目级→本地级→路径级规则),后加载覆盖先加载;`@import` 拆分子文件;Auto Memory 自动记录模式;目标 **<200 行**,只放"团队约定+构建命令+红线",领域知识用引用;
2. **Skills(渐进式披露杀手锏)**:三阶段——仅 frontmatter(约 100 token/技能)→ 相关时加载完整 SKILL.md(<5K)→ 用时加载脚本资源;**10 个技能不激活只付 ~1,000 token 而非 50,000+**(社区称 98% 节省);description 写得好不好决定能否被触发;
3. **Hooks(零 token 自动化)**:PreToolUse/PostToolUse/UserPromptSubmit/Stop/PreCompact 触发 shell;是"强制执行的规则",不占 context;**PreCompact hook 降低压缩关键信息丢失约 30%**;
4. **Subagents(上下文隔离)**:独立 200K 窗口,只回传 1-2K 高密度结论;
5. **会话级工具**:`/compact`(恢复约 70%)、`/clear`(100%)、`/cost`/`/status`/`/context` 监控;Plan mode 用轻量模型(token 减半);自动压缩阈值默认约 98%,**建议降到 85% 提前触发**;
6. **降本技巧**:自定义 statusline 显示上下文用量、`.claudeignore`、精简工具列表、给可运行验证手段。

### Cursor / Codex / 其他工具

- **Cursor**:Rules(Always/Auto/Glob/Manual 四种应用方式,建议 <500 行、引用 @file 而非复制)+ Skills(按需注入)+ Hooks(stop hook 实现"迭代到测试全绿"循环);新对话引用 @Past Chats;
- **OpenAI Codex**:AGENTS.md 合并上限 **32 KiB**;压缩配置示例(`model_context_window=272000`、`model_auto_compact_token_limit=240000`);**一刀切压缩不如 Claude Code 三层渐进,因此"避免触发压缩"比依赖压缩更好**;实战:一个任务一个线程、@文件名精准引用、同会话不切模型、prompt cache 约 5 分钟 TTL、工具结果占 token 大头(实测约 81%);
- **其他**:Windsurf(Cascade 记忆)、Cline(conditional rules + Auto Compact)、Aider(**Repo Map 仓库地图**)、GitHub Copilot(copilot-instructions.md)、Gemini CLI/Jules/Amp/Factory/CodeRabbit(均支持 AGENTS.md)。

## 原理:指令文件体系标准(静态上下文层)

**AGENTS.md**(Linux Foundation 下 Agentic AI Foundation 托管,GitHub 60,000+ 仓库,OpenAI 内部用了 88 个)——项目级"README for AI agents",回答"这个项目怎么做":

- 内容建议(约 100 行指针式):项目简介 + 构建/测试命令;非显然约束;代码风格/Git 约定/红线(Always/Ask first/Never 三段式);领域文档用引用;
- 加载规则:仓库根一份;monorepo 嵌套,agent 读最近的、最近者优先;用户聊天提示覆盖一切;
- 与私有格式:AGENTS.md 是跨工具通用层;CLAUDE.md(hooks 等特有)、.cursorrules(Cursor 特有)作补充;
- 编写纪律:小(一屏最佳)、引用优于内联、犯错驱动增长、元数据化(frontmatter:last_updated/owner/scope)、进 Git。

## 原理:四大动态上下文管理技术

### 1. Compaction(压缩)——三层递进策略

| 层级 | 策略 | 说明 |
| --- | --- | --- |
| Layer 1: Raw | 完整保留 | 最新工具调用结果不压缩(模型下一步决策高度依赖) |
| Layer 2: Compact | 精简结构 | 较早历史工具输出结构化摘录(路径/ID/错误码/关键数字/决策点) |
| Layer 3: Summarize | 语义摘要 | 更早轮次压成高密度叙事摘要(目标/子目标/关键决策/当前状态/待办) |

实现:滚动摘要 / 分层摘要 / Map-Reduce 摘要(Google Gemini 生产方案)。**触发阈值建议 60-75% 容量即压缩**。

**压缩的代价(必须知道)**:Factory.ai 对 36,611 条生产消息基准测试——三家摘要方法在"工件追踪(哪些文件被改)"仅得 2.19-2.45/5.0,自由摘要会静默丢失精确技术细节;ACON 论文(arxiv:2510.00615)证实 naive 摘要多步任务精度严重退化。缓解:PreCompact hook 保存关键状态;优先避免触发压缩。

### 2. Selective Eviction(选择性淘汰)

LRU(丢最旧工具结果)/ 重要度打分(注意力权重、KV 向量 L2 范数、注意力熵,只保留 Top-K)/ 去重去噪(同一文件重复读取只留最新、已解决错误清除、工具输出格式化)。零合成成本、无损,但要启发式规则。

### 3. Prompt Caching(提示缓存)——省钱第一杠杆

- **原理**:新请求与前序请求**前缀逐字节相同**则复用 KV 缓存,只算新增部分;
- **各家折扣**:Anthropic 显式 cache_control(TTL 5min-1h,缓存读 0.1x 省 90%);OpenAI 自动缓存(≥1024 token 前缀,约 $0.175/M vs $1.75/M);Google 命名缓存对象;
- **"不可变前缀"架构纪律**(三个毁缓存的坑):会话中途改工具定义 / 切换模型 / 前缀放动态内容(时间戳/request ID/配置);
- **正确布局**:静态前缀(system prompt → 工具定义 → 历史)+ 动态后缀(当前用户消息、工具结果);
- **收益实测**:system-prompt-only 缓存策略跨厂商 41-80% 成本下降、TTFT 提升 13-31%;Manus 称 KV cache 命中率是"生产级 agent 最重要的单一指标";
- **语义缓存**:按 embedding 相似度(cosine>0.95)缓存"意图"而非字面,适合高频 FAQ;自托管:vLLM `--enable-prefix-caching` / SGLang RadixAttention / LMCache。

### 4. Just-in-Time 按需加载 + 工具结果过滤

- **渐进式披露**:先看文件名/目录结构/时间戳建立信息布局,层层探索不一次性全加载(Skills 即此思想);
- **工具懒加载**:向量检索选出 Top-5 最相关工具挂载,而非所有工具描述塞进 system prompt;
- **Observation 清洗**:工具默认返回摘要(完整结果写文件,上下文只留关键错误/路径/ID/计数/下一步);设计工具时就让输出结构化精简("返回 200 个最相关词+来源 URL 比返回 5,000 词抓取文本好");
- **Prompt Injection 防御**:外部内容进上下文前做沙箱清洗。

### 四大策略总纲(Write / Select / Compress / Isolate)

| 策略 | 做什么 | 何时用 |
| --- | --- | --- |
| Write(外置) | 计划/决策/中间结果写外部存储,窗口只留指针/摘要 | 每个主要步骤之后 |
| Select(按需检索) | 只动态加载当前相关文件/事实/工具 | 大型代码库长任务,省 80-95% token |
| Compress(压缩) | 60-70% 容量时压缩最旧历史 | 每个长任务 |
| Isolate(隔离) | 子代理独立上下文处理子任务 | 子任务不需要父代理全部历史时 |

## 实践 / 应用:外部记忆系统与架构模式

### 外部记忆系统(把上下文从"对话内"扩展到"对话外")

| 平台 | 架构 | 核心卖点 | 适合 |
| --- | --- | --- | --- |
| Mem0 | 向量优先 | 上手最快、框架中立(21 框架/20 向量后端)、四层记忆 | 个性化助手/聊天机器人 |
| Zep/Graphiti | 时间知识图谱 | 事实带失效时间,能答"1 月谁负责"与"现在谁负责" | CRM 副驾/合规 agent |
| Letta(原 MemGPT) | OS 式分层 | Agent 自己用工具 promote/archive | 长生命周期自治 agent |
| LangMem | LangGraph 原生 | 深度集成 | 已用 LangGraph 的团队 |

**分层记忆架构**:In-context(当前窗口)→ 短期 Session(Redis)→ 中期 Task(Redis/DB)→ 长期 User/Org(向量库+加密 DB)→ 工作区(文件系统)。实践规则:写入异步化、记忆 TTL(情景设过期、语义永存)、写入前一致性校验保留 `{old_value,new_value,timestamp}` 可回滚、评测基准 LoCoMo/LongMemEval/BEAM。

### 架构模式

- **RAM vs Disk 心智模型**:上下文窗口当 RAM(快、有限、会话间清空),外部存储当 Disk(便宜、大、需显式检索);
- **Two-Pass Assembly**:第一遍加载静态上下文(可前缀缓存),第二遍注入动态上下文(最小化)——附带收益:行为异常要么是静态配置问题要么是动态状态问题,调试定位容易;
- **Subagent/多智能体隔离**:共享 Scratchpad / 消息总线 / Handoff 协议 / 角色隔离(子 agent 只看自己相关切片,orchestrator 保留全局视图);
- **长任务持久化三件套**:Compaction + 结构化笔记(TODO.md/progress.md/known_issues.md/decisions.md)+ Sub-agent 分层;
- **监控与评测**(没有指标就是玄学调参):context review 指标(单次任务 prompt tokens、工具结果 tokens、重复比例、压缩次数、无效检索)、缓存健康度(命中率 >80%)、上下文健康度仪表盘(Context Bloat Rate/Memory Recall Accuracy/Isolation Breach Count/Compression Fidelity Score,连续 3 天偏离基线 ±15% 触发自动调优)、回放评测。

## 实践 / 应用:从零搭建落地路线图

按性价比排序(最高杠杆先做):

**第一阶段:打地基(当天见效)**
1. 写一份 AGENTS.md(<100 行:项目简介、构建/测试命令、代码风格、红线边界);
2. 调好 system prompt 的 altitude(具体到能引导行为,抽象到不脆弱);
3. 精简工具加载(5-8 个、职责不重叠)。

**第二阶段:控窗口(长任务触顶时)**
4. 配置 auto-compact 阈值 85% + PreCompact hook 备份关键状态;
5. 开启结构化笔记纪律(progress.md/decisions.md);
6. 任务切分:一个任务一个会话。

**第三阶段:省成本**
7. 设计缓存友好前缀(静态在前、动态在后、会话内不动工具列表/不切模型);
8. 工具输出默认摘要化。

**第四阶段:扩规模**
9. Subagent 隔离耗 token 子任务;
10. 引入外部记忆(Mem0 起步 → 按需升级 Zep/Letta)。

> **始终记住的核心原则**:上下文是有限资源,目标是"**下一步所需的最小高信号 token 集**";从最简单的能工作的方案开始,根据失败模式逐步加机制(Anthropic 明确建议);有监控有评测,否则一切都是玄学调参。

## 总结

- **本质**:Context Engineering 是管理"模型每轮看到什么"的迭代式策划——有限注意力预算、context rot(70-80% 触顶)、lost-in-the-middle、100:1 输入比、四失败模式复合;
- **工具全景**:Claude Code 最完整(Skills 98% 节省/Hooks 零 token/Subagents 隔离/PreCompact)、Cursor Rules+Skills+Hooks、Codex 缓存敏感(避免触发压缩优于依赖压缩)、Aider Repo Map;
- **标准**:AGENTS.md 是跨工具通用层(60k+ 仓库),<100 行指针式、引用优于内联、犯错驱动增长;
- **四技术**:Compaction 三层(触发阈值 60-75%)、Selective Eviction、Prompt Caching(静态前缀+动态后缀,命中率是核心指标)、JIT 按需加载 + Observation 清洗;
- **记忆与架构**:Mem0/Zep/Letta 选型 + 五层记忆 + RAM/Disk 心智模型 + Two-Pass 组装 + 监控指标;
- **落地**:10 步路线图按性价比排序,从 AGENTS.md + altitude + 精简工具开始;
- **下一步**:逐篇文献深化见配套系列文章(官方一手资料/文档漂移治理/注释纪律/补充阅读),或对照站内 [四杠杆基础](context-engineering.md)、[Claude Code 深度解析](../07-agent-coding/claude-code-deep-dive/index.md)、[Agent 记忆体系](agent-memory-systems.md)。

## 延伸阅读

- 调研报告原文:`docs/inbox/context-engineering-survey-source.md`;文献清单:`docs/inbox/context-engineering-references-source.md`
- 官方一手资料:Anthropic《Effective context engineering for AI agents》《Claude Code best practices》、Claude Code《How Claude remembers your project》、AGENTS.md 规范(agents.md)
- 站内:[Context Engineering 四杠杆](context-engineering.md)(基础框架)、[Agent 记忆体系](agent-memory-systems.md)(记忆深化)、[Claude Code 深度解析](../07-agent-coding/claude-code-deep-dive/index.md)、[Headroom 上下文压缩](../08-harness/headroom-context-compression.md)(压缩实践)、[给 Coding Agent 立规矩](../07-agent-coding/experience/agent-rules-agents-md.md)(AGENTS.md 实战)
