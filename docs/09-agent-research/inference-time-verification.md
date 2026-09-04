# 推理时验证(DeepVerifier):Agent"自我进化"的新范式

> **一句话摘要**:腾讯 AI Lab 联合港中文、人大提出《Inference-Time Scaling of Verification》——用"验证的不对称性"取代"盲目重试":把长链路 Agent 的复杂验证拆成可定向检索的事实核查,配合首份 DRA 失败分类学与 Rubric 引导的裁判,在 GAIA 上提升 12%,并开源 4K 反思数据集。
>
> **来源**:公众号解读《拒绝盲目重试…》(jude_zkh);论文 Wan, Y., Fang, T., Li, Z., et al. (2026), *Inference-Time Scaling of Verification: Self-Evolving Deep Research Agents via Test-Time Rubric-Guided Verification*, arXiv:2601.15808;代码与数据 [github.com/Tencent/CognitiveKernel-Pro](https://github.com/Tencent/CognitiveKernel-Pro)、[github.com/yxwan123/DeepVerifier](https://github.com/yxwan123/DeepVerifier)(已核验);原始资料存档于 `docs/inbox/deepverifier-source.md`

## 概念:研究问题与核心洞察

### 痛点:长链路 Deep Research Agent 为什么"翻车"

在长周期(Long-horizon)自动化知识发现任务中,Agent 面临三个困境:

1. **错误级联**:早期找错一个网页,后续几十步推理全盘皆输;
2. **监督成本极高**:让人类盯几百个 Step 的轨迹不现实;
3. **传统 Test-Time Scaling 失效**:Reflexion 或 Best-of-N 让 Agent"重新解一遍题",它大概率还会犯同样的逻辑错误或幻觉——**在同一个坑里反复跌倒**。

### 破局点:验证的不对称性(Asymmetry of Verification)

!!! tip "论文最核心的洞察"
    > **"解出一道复杂的综合题很难,但拿着答案去查证其中的几个关键线索,却容易得多。"**

基于此,作者放弃"让 Agent 重新做一遍题"的传统思路,转而将**复杂的验证任务拆解为简单的"信息检索子任务"**,通过定向查错实现自我进化——从"扩大搜索/重试"转向"精准验证与反馈"。

## 方法 1:DRA 失败分类学(Deep Research Agent Failure Taxonomy)

要让 Agent 学会反思,先得知道它怎么错的。作者在 **WebAggregatorQA** 数据集上收集近 **3000 个 Step 轨迹**,人工标注 **555 个错误点**,归纳出 5 大类:

| 类别 | 症状 | 占比 |
| --- | --- | --- |
| **Finding Sources(找源错误)** | 病急乱投医,依赖二手营销号/无关网页,关键证据缺失 | 最高 |
| **Reasoning(推理错误)** | 强行脑补、滑坡谬误、过早下结论(premature conclusions)、过度自信 | 高 |
| **Problem Understanding(理解偏差)** | 没看懂 Prompt,目标漂移,偏离用户原始意图 | — |
| **Action Execution(执行错误)** | API 调用失败、UI 点击错位、代码格式报错 | — |
| **Trajectory Efficiency(效率低下)** | 陷入死循环,为一个错误疯狂重试直到耗尽 Max Step | — |

!!! note "开发者启示"
    做 Agent 评测和 Debug 时,不要只看"最终答案对不对"——**建立类似的失败分类学,针对高频错误(如找源、推理)设计专门干预机制**。这是写高质量 Rubric 与反馈提示词的前提。

## 方法 2:DeepVerifier 架构(三模块"找茬"流水线)

不是简单的 "LLM-as-a-Judge",而是多模块协同的验证框架:

### Step 1:轨迹摘要与"找茬"(Decomposition Module)

Agent 轨迹动辄几百万 Token,直接喂 Judge 必死。Decomposition Agent 先做两件事:

- **压缩轨迹**:提取每一步访问的 URL 和获取的核心事实(Fact/Number);
- **对号入座**:拿着失败分类学扫描摘要,找出"可疑行为",生成**高杠杆 Follow-up 问题**(如"Source X 中真的提到了数据 Y 吗?")。

### Step 2:定向验证(Verification Agent)

**最精妙的一步**:验证 Agent **不去重新解原题**,而是拿着 Follow-up 问题去外部网络**定向检索与交叉验证**——把"复杂推理"降维成"简单的事实核查"。

### Step 3:基于 Rubric 的裁判(Judge Module)

Judge Agent 结合验证结果与预设 Rubric 打分(1-4 分):

| 分数 | 含义 |
| --- | --- |
| 1 | 完全错误 |
| 2 | 大部分错误 |
| 3 | 大部分正确 |
| 4 | 完全正确 |

分数 ≤ 2 时,生成**带明确指令的 corrective feedback**(如"不要搜通用词,去搜 XX 公司最新财报第 X 页")打回主 Agent 重试——反馈是"指令级的",不是"重新做一遍"。

## 实验结果:推理时计算的"缩放奇迹"

| 实验 | 结果 |
| --- | --- |
| **GAIA-Web**(Claude-3.7-Sonnet 底座) | 51.1% → **63.3%**(+12%,3-4 轮反馈达峰值) |
| 其他底座 | GPT-4.1、开源 Qwen3-8B 也有显著涨点 |
| **成本收益** | 对比 Best-of-N(完整重跑几十次),每轮只检索 **≤3 个 targeted 问题**,Token 成本与准确率取得极佳 Trade-off |

## 开源资源:DeepVerifier-4K 反思数据集

- **规模**:4,646 条高质量 Prompt-Response 对;
- **来源**:从 400 个真实 Agent 验证轨迹中,过滤出 True Positive(精准抓出错误)和 True Negative(精准放过正确答案)的**黄金反思样本**;
- **用途**:专门用于 SFT,训练开源模型的 Reflection & Self-Critique(反思与自我批评)能力;
- **实测**:基于 Qwen3-8B 微调的 DeepVerifier-8B(配反思模块)比原版提升 **5.5%**,超越许多未经反思训练的更大模型;
- **代码**:`Tencent/CognitiveKernel-Pro`、`yxwan123/DeepVerifier`(均已核验)。

## 对 Agent 开发者的三条实操建议

1. **放弃 Holistic Judge(整体评判)**:不要让 LLM 直接看着几万字轨迹判断对错,它一定会幻觉——**必须引入 Decomposition(拆解),把验证转化为外部可检索的 Yes/No 问题**;
2. **建立你的 Failure Taxonomy**:参考论文 5 大类,针对自己的业务(代码生成、数据分析等)梳理专属错误分类学——这是高质量 Rubric 和 Feedback Prompt 的前提;
3. **重视"反思数据"的构建**:不要只拿成功轨迹做 SFT——**"Agent 犯错 → 被精准指出 → 修正成功"**的轨迹(如 DeepVerifier-4K)才是训练 Agent 自我进化能力的无价之宝。

## 总结

- **范式纠偏**:Test-Time Scaling 从"盲目扩大搜索/重试"走向"精准验证与反馈";
- **验证的不对称性**是核心洞察:解难题难,查证线索易——把验证降维成定向检索;
- **三模块**:Decomposition(压缩+找茬)→ Verification(定向核查)→ Judge(Rubric 打分 + 指令级反馈);
- **两份开源资产**:DRA 失败分类学(5 类)+ DeepVerifier-4K(4,646 条反思样本);
- **三条建议**:放弃 Holistic Judge、建自己的失败分类学、重视反思数据——全部可迁移到任何 Agent 评测/落地团队。

## 延伸阅读

- 站内:[设计范式视角(03-agents)](../03-agents/agent-test-time-verification.md)、[Agent 评测](../03-agents/agent-evaluation.md)、[评估驱动开发](../03-agents/agent-eval-driven-dev.md)、[Agent 持续进化](../03-agents/agent-continuous-evolution.md)
- 外部:论文 arXiv:2601.15808(编号以原文为准);GitHub `Tencent/CognitiveKernel-Pro`、`yxwan123/DeepVerifier`
