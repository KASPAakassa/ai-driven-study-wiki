# Anthropic《Building effective agents》:workflow 与 agent 的五种模式

> **一句话摘要**:Anthropic 2024-12-19 经典文章——**"最成功的实现往往是简单、可组合的模式,而不是过度设计的框架"**。原文系统区分了 **workflows(LLM 通过预定义代码路径编排)与 agents(LLM 动态自主引导过程)**,给出五种生产级 workflow 模式(prompt chaining / routing / parallelization / orchestrator-workers / evaluator-optimizer)与自主 agent 的构建块、适用场景和三原则(简单、透明、精心设计 ACI)。本文是原文完整整理;EasyClaw 转载文里"五部分(trigger/context/tools/decision rule/human checkpoint)"是其解读,非原文术语。
>
> **来源**:Anthropic《Building effective agents》(2024-12-19,Erik Schluntz & Barry Zhang,https://www.anthropic.com/research/building-effective-agents)

## 概念

### 核心观点:简单、可组合 > 复杂框架

过去一年 Anthropic 与几十个行业团队合作构建 LLM agent,**最成功的实现用的不是复杂框架或专用库,而是简单、可组合的模式**。框架常增加抽象层,掩盖底层 prompt 与响应,难以调试,还诱使人"该简单时却加复杂度"。

建议:**先用 LLM API 直接实现**(很多模式几行代码就能写);即使用框架,也要理解底层代码——对框架底层的不正确假设是客户错误的常见来源。

### workflows vs agents(原文的关键架构区分)

| | Workflows | Agents |
| --- | --- | --- |
| 定义 | LLM 与工具通过**预定义代码路径**编排 | LLM **动态**引导自己的过程和工具使用,控制如何完成任务 |
| 适合 | 定义良好的任务:可预测、一致 | 需要灵活性 + 模型驱动决策的大规模场景 |
| 权衡 | 低延迟低成本 | 以延迟和成本换任务性能 |

**何时用(或不用)**:先找最简单方案,只在需要时加复杂度——**可能根本不用构建 agentic 系统**;对很多应用,优化单次 LLM 调用(检索 + 上下文示例)通常就够了。

### 澄清:五个部分 vs 五种模式

站内 [10 个 AI Agent 工作流模板](agent-workflow-templates.md) 引用了本文观点,但其"五部分框架(trigger/context/tools/decision rule/human checkpoint)"是**转载作者的解读**;原文的体系是 **构建块(augmented LLM)→ 五种 workflow 模式 → 自主 agents → 组合定制**,术语不同,本文以原文为准。

## 原理(五种模式 + agents)

### 构建块:Augmented LLM(增强型 LLM)

一切 agentic 系统的基础是**经过增强的 LLM**——检索、工具、记忆。当前模型能主动使用这些能力:自己生成搜索查询、选工具、决定保留什么信息。实现要关注两点:裁剪能力适配用例、提供易用且文档良好的接口(MCP 是途径之一)。

### Workflow 1:Prompt chaining(提示链)

把任务分解为步骤序列,每个 LLM 调用处理前一个的输出;**中间步骤可加程序化检查(gate)**确保仍在正轨。

- **适用**:任务可干净分解为固定子任务;用延迟换精度,让每次调用更简单;
- **例子**:写营销文案 → 翻译成另一语言;写大纲 → 检查是否符合标准 → 再按大纲写正文。

### Workflow 2:Routing(路由)

分类输入并导向专门的后续任务,实现关注点分离、构建更专用的 prompt。

- **适用**:存在不同类别需分开处理、且分类可准确完成(LLM 或传统分类模型);
- **例子**:客服查询分流(普通问题/退款/技术支持到不同流程);简单问题路由到便宜小模型、难问题路由到强模型(成本优化)。

### Workflow 3:Parallelization(并行化)

LLM 同时处理任务、输出程序化聚合。两种变体:

- **Sectioning(分区)**:任务拆成独立子任务并行;
- **Voting(投票)**:同一任务多次运行取多样化输出。

- **适用**:子任务可并行提速,或需多视角/多次尝试提置信度;复杂任务各考量用独立 LLM 调用处理,注意力更聚焦;
- **例子(分区)**:护栏——一个模型实例处理用户查询、另一个筛不当内容;自动化 evals 每调用评一个维度;
- **例子(投票)**:多 prompt 审查代码漏洞;多 prompt 评内容不当性,用投票阈值平衡误报漏报。

### Workflow 4:Orchestrator-workers(编排-工人)

中央 LLM 动态拆解任务、委派给 worker LLM、综合结果。

- **适用**:无法预判子任务的复杂任务(如编码要改哪些文件、怎么改取决于任务);与 parallelization 拓扑相似但**灵活性更高**——子任务不由预定义,由 orchestrator 按输入决定;
- **例子**:编码产品(每次多文件复杂改动);跨多来源检索分析的研究任务。
- (Anthropic 实战见站内 [多智能体研究系统](agent-multi-agent-research-system.md):LeadResearcher + 并行 Subagent + CitationAgent。)

### Workflow 5:Evaluator-optimizer(评估-优化器)

一个 LLM 生成响应,另一个在循环中提供评估与反馈。

- **适用**:有清晰评估标准、迭代改进可带来可度量价值;两个信号——人工给出反馈时 LLM 响应可证明地改进,且 LLM 能给出这种反馈(类似作者打磨文稿);
- **例子**:文学翻译(译者 LLM 漏掉细微差别,评估 LLM 给批评);复杂搜索任务多轮搜索分析,评估器决定是否继续搜索。

### Agents(自主 agent)

agent 以人类命令或交互讨论开始,任务明确后**独立规划与运行**,执行中每步从环境获得"ground truth"(工具结果、代码执行)评估进度;可在 checkpoints 或遇阻时暂停等人类反馈;任务通常以完成为终止,也常加停止条件(如最大迭代数)保持控制。

- **适用**:开放问题——无法预测所需步骤数、无法硬编码固定路径;必须有一定程度对模型决策的信任;自主性适合可信环境的规模化;
- **代价**:更高成本、错误复合的可能;**必须在沙箱充分测试 + 加护栏**;
- **例子**:解决 SWE-bench 任务的编码 agent(基于任务描述改多文件);computer use 参考实现。

### 组合与定制

这些构建块**不是处方,是常见模式**,可塑形组合。关键是**度量性能并迭代**——只在复杂度可证明改善结果时才加。

### 三原则(总结)

1. **保持简单**(maintain simplicity in design);
2. **透明优先**(显式展示 agent 的规划步骤);
3. **精心设计 agent-computer interface(ACI)**:通过彻底的工具文档与测试打磨工具。

## 代码 / 实现

原文给出了 cookbook 示例(https://platform.claude.com/cookbook/patterns-agents-basic-workflows)。五种模式的骨架(伪代码):

```python
# Prompt chaining:每步处理上一步输出,可加 gate
out1 = llm.call(step1_prompt, input)
if not check_gate(out1): return
out2 = llm.call(step2_prompt, out1)

# Routing:分类后分发
category = classify(input)          # LLM 或传统分类器
handler = route_table[category]     # 专用 prompt/工具/模型
return handler(input)

# Parallelization(sectioning):独立子任务并行
results = [llm.call(p, input) for p in section_prompts]  # 可并行
return aggregate(results)

# Orchestrator-workers:中央动态委派
plan = orchestrator.plan(input)     # 拆解出子任务(运行时决定)
results = [worker.run(sub) for sub in plan]
return orchestrator.synthesize(results)

# Evaluator-optimizer:生成-评估循环
candidate = generator(input)
while evaluator(candidate).score < threshold and iterations < max:
    candidate = generator(input, feedback=evaluator(candidate))
```

**工具工程要点(Appendix 2,ACI)**:

- 工具格式决策:给模型足够 token "思考"再动手;格式贴近模型在互联网文本中自然见过的样子;避免格式"开销"(精确计数数千行、转义);
- **HCI 投入多少,ACI 就投入多少**:站在模型角度想工具是否明显好用;参数名/描述写得像给初级开发者的优秀 docstring(相似工具多时尤其重要);用 workbench 跑大量示例输入观察模型错误并迭代;**Poka-yoke 工具**(改参数让它更难犯错)——SWE-bench 实例:模型在离开根目录后误用相对路径,改为**强制绝对路径**后模型用得完美。

## 实践 / 应用

### 两个高价值领域(Appendix 1)

- **客户支持**:对话流 + 工具集成(客户数据/订单历史/知识库文章)+ 程序化动作(退款/更新工单)+ 可度量的成功标准(用户定义解决);已有公司按"仅成功解决才收费"的用量定价,验证有效性;
- **编码 agent**:代码可自动化测试验证、可用测试结果作反馈迭代、问题空间定义良好、输出可客观度量——但仍需人类审查确保符合更大系统需求。

### 与站内文章的对应

| 原文概念 | 站内对应 |
| --- | --- |
| 五种 workflow 模式(理论分类) | 本文(原文整理)↔ [10 个 AI Agent 工作流模板](agent-workflow-templates.md)(EasyClaw 业务实例,解读版"五部分框架") |
| orchestrator-workers 实战 | [Anthropic 多智能体研究系统](agent-multi-agent-research-system.md)(LeadResearcher/90.2%/token 经济学) |
| workflows vs agents | [Agent 规划与工作流模式](agent-planning-patterns.md)(推理四模式/工作流四模式,另一套分类) |
| ACI / 工具设计 | [工具调用](tool-calling.md)、[Agent 多轮对话上下文管理](agent-context-management.md)(tool_call_id 配对) |
| 简单可组合 vs 框架 | [Vibe Coding 最佳实践](../07-agent-coding/experience/vibe-coding-engineering-practice.md)(工程栈总纲) |

### 选型速查

| 遇到什么 | 选什么 |
| --- | --- |
| 任务可固定拆解成几步、要更高精度 | Prompt chaining |
| 输入分明显类别、各自处理更优 | Routing |
| 独立子任务可并行 / 要多视角置信 | Parallelization(分区/投票) |
| 子任务运行时才确定、需中央协调 | Orchestrator-workers |
| 有清晰评估标准、迭代有可度量改进 | Evaluator-optimizer |
| 开放问题、无法预定义路径、信任决策 | Agents(沙箱测试 + 护栏) |
| 简单的单次调用 + 检索就够 | **别建 agentic 系统** |

## 总结

1. **核心观点**:最成功的 agent 用简单可组合模式,而非过度设计框架;先 LLM API 直接实现,用框架也要懂底层。
2. **架构区分**:workflows 走预定义代码路径(可预测),agents 由 LLM 动态引导(灵活);以延迟成本换任务性能,想清楚再上。
3. **五种 workflow 模式**:prompt chaining / routing / parallelization / orchestrator-workers / evaluator-optimizer,各有适用信号与例子。
4. **agents 三原则**:保持简单、透明展示规划、精心设计 ACI(工具文档/测试/poka-yoke)。
5. **组合与度量**:模式可组合;只在复杂度可证明改善结果时才加;从简单 prompt + 全面评估起步。

**下一步学什么**:读 [10 个 AI Agent 工作流模板](agent-workflow-templates.md)(把模式落到业务实例)、[多智能体研究系统](agent-multi-agent-research-system.md)(orchestrator-workers 实战)、[Agent 评测](agent-evaluation.md)(如何度量迭代);动手看 cookbook 示例实现。

## 延伸阅读

- 站内:[10 个 AI Agent 工作流模板](agent-workflow-templates.md)、[Anthropic 多智能体研究系统](agent-multi-agent-research-system.md)、[Agent 规划与工作流模式](agent-planning-patterns.md)、[工具调用](tool-calling.md)、[Subagent 上下文隔离](subagent-isolation.md)、[Vibe Coding 最佳实践](../07-agent-coding/experience/vibe-coding-engineering-practice.md)
- 外部:原文(https://www.anthropic.com/research/building-effective-agents);Cookbook 示例(https://platform.claude.com/cookbook/patterns-agents-basic-workflows);SWE-bench Sonnet(https://www.anthropic.com/research/swe-bench-sonnet)
