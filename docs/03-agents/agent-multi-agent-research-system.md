# Anthropic 多智能体研究系统:orchestrator-worker 架构与工程实践

> **一句话摘要**:Anthropic Research 功能用 orchestrator-worker 多智能体架构做开放研究:LeadResearcher 规划并并行派生 Subagent 搜索,CitationAgent 做引用归因。本文拆解其架构、内部评测数据(多智能体比单智能体高 90.2%)、token 经济学(4×/15×)、委派 prompt 原则、LLM-as-judge 评估方法与生产可靠性挑战——是构建多智能体系统最完整的一手工程方法论。
>
> **来源**:Anthropic Engineering《How we built our multi-agent research system》(https://anthropic.com/engineering/built-multi-agent-research-system,2025-06-13,Jeremy Hadfield 等 6 人)

## 概念

### 为什么研究任务适合多智能体

研究是**开放问题**:无法预先硬编码固定路径,过程动态且路径依赖,人们会随发现不断调整方向。这要求模型自主运行多个回合,根据中间发现决定下一步。线性单次管线处理不了。

多智能体的本质优势:

- **搜索即压缩**:Subagent 用各自上下文窗口并行探索问题的不同方面,把最重要的 token 压缩后交回 lead agent——每层都是独立上下文、独立工具、独立探索轨迹(separation of concerns),降低路径依赖;
- **规模化性能**:单个智能体有极限,群体协作能完成更多(类比人类社会的集体智能);
- **内部评测**:Opus 4 lead + Sonnet 4 subagents 比单 agent Opus 4 高 **90.2%**。例:查询"IT 板块 S&P 500 所有公司董事",多智能体拆解给 subagent 找到答案,单智能体顺序慢搜失败。

### token 经济学:多智能体为什么有效、又为什么贵

- BrowseComp 评测中,**三个因素解释 95% 的性能方差:token 用量(单独解释 80%)、工具调用次数、模型选择**——多智能体架构本质是"跨独立上下文窗口分布式地多花 token",为并行推理增加容量;
- 模型是 token 的增效器:升级到 Sonnet 4 比在 Sonnet 3.7 上翻倍 token 预算收益更大;
- **成本现实**:agent 通常用约 **4× chat 的 token**,多智能体约 **15×**。经济上只适合高价值任务;
- **不适合多智能体的场景**:需要所有 agent 共享同一上下文、agent 间依赖很多的领域;**大多数 coding 任务并行度不如研究**,且 LLM 还不擅长实时委派协调;
- 适用特征:高价值 + 重并行 + 信息超出单上下文窗口 + 对接众多复杂工具。

## 原理

### 架构:orchestrator-worker 模式

```
用户查询
   ↓
LeadResearcher(主 agent,迭代研究循环)
   ├─ 思考策略 → 计划写入 Memory(防 200K 上下文截断丢计划)
   ├─ 派生 N 个 Subagent(并行):各自独立 web 搜索,
   │    用 interleaved thinking 评估工具结果、返回发现
   ├─ 综合结果 → 决定是否继续(可再派生或调整策略)
   └─ 信息足够 → 退出循环
   ↓
CitationAgent:处理文档与研究报告中引用的具体位置,保证声明有出处
   ↓
最终研究结果(带引用)
```

与传统 RAG(静态检索相似块)不同,这是**多步动态搜索**:动态找相关信息、适应新发现、分析结果生成高质量答案。

### Prompt 工程:多智能体的主要杠杆

协调复杂度随 agent 数快速上升(早期 agent 会为简单查询派生 50 个 subagent、无限搜索、互相干扰)。原则:

1. **Think like your agents**:用 Console 搭"提示词+工具"仿真,逐步观察 agent 行为,失败模式立刻暴露(已有足够结果还继续、搜索词过长、选错工具);
2. **教 orchestrator 委派**:每个 subagent 需要 objective、输出格式、工具与来源指引、清晰任务边界。模糊指令会导致重复劳动、留空档(例:一个 subagent 查 2021 汽车芯片危机,另两个重复查 2025 供应链);
3. **按查询复杂度缩放 effort**(写进 prompt):简单事实查询 = 1 agent + 3-10 次工具调用;直接比较 = 2-4 subagent 各 10-15 次调用;复杂研究 = 10+ subagent 明确分工——防止简单查询过度投入;
4. **工具设计/选择与 HCI 同等关键**:工具接口对 agent 与对人一样重要;用对工具常常是必要条件(在 Slack 才有上下文却去 web 搜注定失败);MCP 使问题加剧(未见过的工具+参差描述)。给显式启发式:先审视全部工具、工具匹配用户意图、宽泛外部探索用 web、专用工具优于通用工具;
5. **让 agent 自我改进**:Claude 4 是优秀 prompt 工程师——给定 prompt 和失败模式能诊断并建议改进。Anthropic 建了工具测试 agent:给有缺陷的 MCP 工具,它反复使用并重写工具描述,多次测试找出细微差别和 bug,**新描述让后续任务完成时间降 40%**;
6. **先宽后窄**:搜索策略模仿专家研究——先短宽泛查询评估可用内容,再渐进收窄;早期 agent 默认用超长具体查询导致结果很少;
7. **引导思考过程**:extended thinking 作为可控草稿纸——lead 用它规划(评估工具、定查询复杂度与 subagent 数);subagent 用 interleaved thinking 在工具结果后评估质量、找缺口、细化下个查询;
8. **并行工具调用**:两级并行——lead 同时派生 3-5 个 subagent(而非串行),subagent 并行 3+ 次工具调用;复杂查询耗时最高降 **90%**。

**提示策略整体**:灌输好启发式而非僵化规则(分解难题、评估来源质量、随新信息调整搜索、深度 vs 广度判断),加显式护栏防失控,靠快速迭代循环 + 可观测性 + 测试用例。

### 评估:多智能体的独特挑战

多智能体不以固定路径运行:相同起点可走完全不同的合法路径(一个搜 3 个来源另一个搜 10 个)。无法预判"正确步骤",需要**判断是否达成正确结果 + 过程是否合理**的灵活评估:

- **立即用小样本开测**:早期改动效果大(一个 prompt 改动成功率可能从 30%→80%),约 **20 条**代表真实用法的查询就能看清效果;别等攒几百条才开始;
- **LLM-as-judge 规模化**:研究输出是自由文本、少唯一答案,LLM 天然适合评分。rubric:事实准确性(声明是否匹配来源)、引用准确性、完整性(所有要求方面是否覆盖)、来源质量(一手优于二手)、工具效率(是否用对工具且次数合理)。尝试多 judge 分开评各组件,但**单个 prompt 输出 0.0-1.0 分 + pass/fail 最一致、最贴合人类判断**;
- **人工测试补漏**:人类发现自动化漏掉的边缘案例——幻觉答案、系统失败、来源选择偏见(早期 agent 一致偏好 SEO 内容农场而非权威但排名低的学术 PDF/博客,加来源质量启发式解决);
- **End-state 评估**(附录):对多回合改状态的 agent,评估最终状态而非逐步过程;复杂工作流拆成离散检查点;
- **涌现行为**:lead 的小改动会不可预测地改变 subagent 行为——最优 prompt 不是严格指令,而是**协作框架**(分工、解题方法、effort 预算)。

### 生产可靠性

- **状态有状态、错误复合**:长时运行跨多次工具调用维护状态,小失败可能灾难化。不能从头重启(贵且烦人),要**可恢复**(从出错点继续)+ 让模型优雅处理(告诉 agent 工具失败让它适应)+ 确定性保障(重试逻辑、定期 checkpoint);
- **调试新方法**:agent 非确定性、动态决策,用户报"找不到明显信息"却看不到原因(坏查询?差来源?工具失败?)——加**全链路 tracing**,监控 agent 决策模式与交互结构(不监控对话内容,保隐私);
- **部署要协调**:agent 系统是高状态化的 prompt/工具/执行逻辑网,几乎持续运行;部署时 agent 可能处于流程任意点,不能一次性全量更新——用 **rainbow deployment**(新旧版本并行、渐进切流量);
- **同步执行是瓶颈**:目前 lead 同步等待 subagent 组完成,简化协调但阻塞信息流(lead 不能中途引导、subagent 不能互协调、被单个慢 subagent 阻塞);异步可加并行但引入结果协调/状态一致性/错误传播挑战;
- **长会话管理**(附录):数百轮对话需智能压缩与记忆——总结已完成阶段存外部记忆,上下文将满时派生干净上下文的新 subagent + 仔细 handoff,可从记忆取回研究计划;
- **Subagent 输出走文件系统**(附录):避免"传话游戏"——subagent 把工作存外部系统,回传轻量引用而非复制大输出(降 token 开销、保信息保真),适合代码/报告/可视化等结构化输出。

## 代码 / 实现

委派 prompt 模板(可复用,来自官方 Cookbook 模式):

```
为 subagent 提供的任务描述必须包含:
- objective:要完成什么
- output format:返回什么格式的结论
- tools & sources:该用哪些工具/来源
- task boundaries:不能做什么、边界在哪
```

effort 缩放规则(写进 lead 的 prompt):

```
简单事实查询 → 1 个 agent,3-10 次工具调用
直接比较   → 2-4 个 subagent,各 10-15 次调用
复杂研究   → 10+ subagent,职责明确分工
```

LLM-as-judge 评估 prompt 骨架(rubric 五维,单次调用):

```
评估该研究输出,给出 0.0-1.0 分 + pass/fail:
- 事实准确性:声明是否与来源匹配?
- 引用准确性:引用来源是否支持声明?
- 完整性:是否覆盖所有要求的方面?
- 来源质量:是否优先一手来源而非低质二手?
- 工具效率:是否用对工具、次数合理?
```

工具描述自优化流程(40% 提速的来源):

```
给"工具测试 agent"一个有缺陷的 MCP 工具 → 反复使用暴露 bug/细微差别
→ 重写工具描述 → 回归测试 → 新描述发布
```

## 实践 / 应用

- **什么时候用多智能体**:高价值、可重并行、信息超单上下文、多复杂工具的研究类任务;**别用**在并行度低的 coding 或强依赖共享上下文的任务;
- **预算**:多智能体约 15× chat token——先评估任务价值是否覆盖;
- **先小样本开测**:20 条查询起步,别等大评测集;人工测试不可省;
- **可观测性先行**:全链路 tracing 才能诊断"找不到信息"类问题;
- **委派要详细**:objective/输出格式/工具来源/边界四要素缺一不可,否则 subagent 重复劳动;
- **工具描述是性能杠杆**:让 agent 自测并重写工具描述可降 40% 完成时间;
- **生产三件套**:checkpoint 可恢复 + tracing + rainbow deployment。

## 总结

1. **多智能体 = orchestrator-worker**:LeadResearcher 委派并行 Subagent + CitationAgent 归因;搜索即压缩,独立上下文窗口是性能来源。
2. **token 经济学**:性能 95% 方差由 token(80%)/工具调用/模型解释;agent 4×、多智能体 15× token——只适合高价值可并行任务。
3. **Prompt 是主要杠杆**:委派四要素、effort 缩放、先宽后窄、extended thinking 草稿纸、工具自我改进(40% 提速)。
4. **评估要灵活**:小样本立即开测、单 prompt LLM-as-judge(rubric 五维)、人工测试补漏、end-state 评估;最优 prompt 是协作框架而非严格指令。
5. **生产难在"最后一公里"**:错误复合需 checkpoint 恢复、tracing 调试、rainbow 部署、子 agent 输出走文件系统防传话游戏。

**下一步学什么**:对比站内 [多 Agent 协作](multi-agent.md)、[Subagent 上下文隔离](subagent-isolation.md)(概念设计)与本文(一手工程实践);委派/评估方法可迁移到 [Agent 评测](agent-evaluation.md) 与 [评估驱动开发](agent-eval-driven-dev.md)。

## 延伸阅读

- 站内:[多 Agent 协作](multi-agent.md)、[Subagent 上下文隔离](subagent-isolation.md)、[Agent Session 通信设计](agent-collaboration-messaging.md)、[Agent 评测](agent-evaluation.md)、[Agent 性能剖析](agent-performance-analysis.md)、[Vibe Coding 最佳实践](../07-agent-coding/experience/vibe-coding-engineering-practice.md)(Agent SDK 印证)
- 外部:原文(https://anthropic.com/engineering/built-multi-agent-research-system);Anthropic Cookbook 多智能体基础工作流(https://platform.claude.com/cookbook/patterns-agents-basic-workflows);BrowseComp(https://openai.com/index/browsecomp/)
