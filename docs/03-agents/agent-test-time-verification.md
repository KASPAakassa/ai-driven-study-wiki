# 推理时验证:Agent 设计的"验证范式"(拒绝盲目重试)

> **一句话摘要**:Agent 长链路任务最怕"在同一个坑里反复跌倒"——传统重试(Best-of-N/Reflexion)只是重新做题。腾讯 AI Lab + 港中文提出的"推理时验证"范式给出设计答案:**验证的不对称性**(解难题难、查证线索易)+ 失败分类学 + Decomposition-Judge。本文从 **Agent 设计视角**提炼这个范式,与 [学术论文解析](../09-agent-research/inference-time-verification.md) 互补。
>
> **来源**:公众号解读《拒绝盲目重试…》(jude_zkh);论文 Wan et al. (2026) arXiv:2601.15808;详细方法/实验/数据集见 [学术篇](../09-agent-research/inference-time-verification.md)

## 概念:为什么"重试"是错误的设计

长链路 Agent(Deep Research 动辄几十页、上百步)有三个绕不开的痛点:

1. **错误级联**:早期一步找错,后续几十步全盘皆输;
2. **监督成本高**:几百步轨迹靠人盯不现实;
3. **重试失效**:让 Agent 重新解一遍,大概率犯同样的错——**传统 Test-Time Scaling(Best-of-N 并行采样、Reflexion 反思)让 Agent 在同一个坑里反复跌倒**。

!!! tip "设计启示"
    遇到 Agent 反复失败,第一反应不应该是"再多试几次"或"换更强的模型",而是先问:**"这个任务的验证,能不能拆成更简单的子问题?"**——这正是本文范式的核心。

## 设计原则 1:验证的不对称性(Asymmetry of Verification)

!!! note "一句话原则"
    **解出一道复杂的综合题很难,但拿着答案去查证其中的几个关键线索,却容易得多。**

设计含义:

- 不要设计"让 Agent 重新做一遍题"的验证;
- 而是把验证任务**降维成"信息检索子任务"**:针对轨迹里的可疑点,生成可查证的问题(如"Source X 中真的提到了数据 Y 吗?"),再去外部检索交叉验证;
- 效果:复杂推理 → 简单事实核查,验证成本大幅下降,准确率反而提升。

## 设计原则 2:失败分类学(Taxonomy)——评测与 Debug 的前提

在 WebAggregatorQA 上人工标注 555 个错误点,归纳 **5 大类失败**(按占比:找源最高 → 推理 → 理解 → 执行 → 效率):

| 失败类 | 典型症状 | 设计干预方向 |
| --- | --- | --- |
| Finding Sources | 依赖二手/无关网页 | 检索质量与来源可信度约束 |
| Reasoning | 脑补、过早下结论 | 证据-结论绑定校验 |
| Problem Understanding | 目标漂移 | 任务契约/意图锚定 |
| Action Execution | API/UI/代码报错 | 工具契约与错误重试 |
| Trajectory Efficiency | 死循环 | 步数预算与循环检测 |

!!! warning "对评测体系的启示"
    **不要只看"最终答案对不对"**——那是 Holistic Judge 的错误路径。先建立失败分类学,再针对高频错误(找源、推理)设计专门干预,是高质量 Rubric 与反馈的前提(呼应 [Agent 评测](agent-evaluation.md) 的 Rubric 二元化、[EDD](agent-eval-driven-dev.md) 的 Bad Case 收敛)。

## 设计原则 3:Decomposition-Judge——替代 Holistic Judge

!!! warning "Holistic Judge 必幻觉"
    让 LLM 直接看着几万字轨迹判断对错,它一定会幻觉。**必须拆解。**

三模块流水线(DeepVerifier):

```
轨迹(几百万 Token)
  → ① Decomposition:压缩轨迹(URL+核心事实)+ 对照失败分类学找可疑行为 + 生成 Follow-up 问题
  → ② Verification:拿问题去外部网络定向检索交叉验证(降维成事实核查)
  → ③ Judge:基于 Rubric 打分(1-4),≤2 分生成"指令级" corrective feedback 打回重试
```

!!! tip "三个设计要点"
    - **压缩先行**:几百万 Token 直接喂 Judge 必死,先提取 URL + Fact/Number;
    - **反馈要"指令级"**:不是"你错了重来",而是"不要搜通用词,去搜 XX 公司最新财报第 X 页"——给方向,不给重跑;
    - **成本可控**:每轮只检索 ≤3 个 targeted 问题,对比 Best-of-N 重跑几十次,Token 效率极高。

## 设计落地:给 Agent 团队的 checklist

1. **放弃 Holistic Judge**:任何长链路验证都走"拆解 → 可检索的 Yes/No 问题 → 定向核查 → Rubric 打分";
2. **建自己的失败分类学**:参考 5 大类,针对你的业务(代码/数据分析/客服)梳理专属分类——这是 Rubric 和反馈提示词的前提;
3. **反思数据是资产**:收集"犯错 → 被精准指出 → 修正成功"的轨迹(如 DeepVerifier-4K),用于 SFT 训练反思能力——不要只拿成功轨迹训练;
4. **验证成本是设计指标**:验证模块的 Token 开销、轮数上限,要像准确率一样被度量(呼应 [评估驱动开发](agent-eval-driven-dev.md) 的"评估=训练目标+回归测试集");
5. **反馈闭环进循环**:Judge 的 corrective feedback 应作为主 Agent 下一轮的系统提示输入,而不是只做"对/错"标记。

## 总结

- **范式**:从"盲目扩大搜索/重试"走向"精准验证与反馈";
- **三条设计原则**:验证不对称性(降维成检索)、失败分类学(评测前提)、Decomposition-Judge(替代 Holistic Judge);
- **工程启示**:反馈要指令级、成本要度量、反思数据要沉淀;
- 与 [09 学术篇](../09-agent-research/inference-time-verification.md) 的关系:本文讲"怎么设计",学术篇讲"方法细节、实验数据、开源资源"。

## 延伸阅读

- 站内:[学术论文解析](../09-agent-research/inference-time-verification.md)、[Agent 评测](agent-evaluation.md)、[评估驱动开发](agent-eval-driven-dev.md)、[Agent 持续进化](agent-continuous-evolution.md)、[WorkBuddy Bench](workbuddy-bench.md)
- 外部:论文 arXiv:2601.15808;GitHub `Tencent/CognitiveKernel-Pro`、`yxwan123/DeepVerifier`;原始资料存档于 `docs/inbox/deepverifier-source.md`
