# LLM 推理的预训练-后训练接口:联合缩放律与 RL 机制(以象棋为测试床)

> **一句话摘要**:预训练与 RL 后训练通常被分开研究,两个基本问题悬而未决:预训练选择(模型大小/数据)如何塑造 RL 算力的回报?RL 到底对模型做了什么?本文用**国际象棋**作为受控测试床(5M–1B 参数、36 个预训练×RL 组合),给出量化答案:①**联合预训练–RL 缩放律**——预训练损失可预测 RL 后 pass@1,RL 奖励曲线斜率随 log 预训练 token 数近似线性增长;②**RL 不是简单锐化 SFT 策略**——易题放大已有正确走法、难题浮现 SFT 下几乎不存在的正确走法(但也强化错误走法)。
>
> **来源**:论文《Understanding Reasoning from Pretraining to Post-Training》(arXiv:2607.16097,cs.LG,2026-07-17,37 页),https://arxiv.org/abs/2607.16097;作者:Shen/Ang Li/Rahman/Sun/Goldblum/Telgarsky/Izmailov(NYU/Modal Labs/UCLA/UIUC/Columbia);代码 https://github.com/pavelslab-nyu/pre2post-chess;原始资料存档于 `docs/inbox/reasoning-pretraining-source.md`

## 概念:为什么需要"预训练→后训练"的统一视角

**背景**:LLM 训练标准流水线是预训练 → SFT → 带可验证奖励的 RL(RLVR)。随着模型扩展,关于"算力往哪投"出现两种分歧观点:

- **预训练先验派**:扩展模型大小、数据、算力,从人类文本得到更强基础模型(Kaplan 2020 / Chinchilla 2022 缩放律);
- **经验派**:用 RL 从环境交互与结果反馈学习,激发/发展超越直接模仿的能力("experience era",Silver & Sutton 2025;AlphaZero 的极致体现)。

**对 LLM 推理,纯经验 RL 尚不可行**——动作空间巨大、随机初始策略的奖励极稀疏。因此 RL 必然从预训练先验出发,真正的问题**不是"要不要先验",而是"先验要多好"**:固定算力预算如何在"做强预训练"与"多做 RL"之间分配?

**第二个问题**:RL 到底对继承的策略做了什么?现有研究众说纷纭:

- Yue et al. 2025:RL 主要**锐化(sharpening)**基础模型已偏好的推理模式(base 模型在大 k 时 pass@k 可匹敌 RL 模型);
- Yuan et al. 2025:RL **组合出新技能**(composition);
- Sun et al. 2025:两者皆有,部分问题出现 "grokking"、部分直接失败。

**为什么难以研究**:自然语言 LLM 的预训练语料巨大且不可控(难以归因行为是预训练还是 RL 造成)、跨两阶段的系统算力扫描贵得离谱、评估通常只看最终答案正确性(单步行为不透明)。

**解法:以国际象棋为受控测试床**——完整镜像标准 LLM 三段管线,但动作空间紧凑、每步可被引擎精确验证,且 5M–1B 的小模型已能展现有意义的缩放差异,使跨预训练/RL 的算力扫描既负担得起又有信息量。**目标不是造最强象棋模型,而是隔离"预训练规模 × 可验证 RL"如何相互作用。**

## 原理:测试床设计与三大发现

### 测试床:三段管线完整镜像 LLM

1. **预训练**:Lichess 人类棋谱,next-token prediction,每走法 4 token(棋子/源/目标/标志),词表仅 81;可按 Elo、棋局长度可控采样(语料 54B token);
2. **SFT**:合成推理轨迹——从提议模型采样 K 条续走、按公共前缀合并成搜索树、DFS 序列化为 `<T>…<sep>…</T>` 思考块(即"思考令牌"的树形版本),训练模型提交最优解;
3. **RLVR**:可验证拼图环境,二元结果奖励(每一步都对才成功,单步错即终止);数学实验用 GRPO。

规模:5M–1B 参数、36 个预训练×RL 组合、Lichess 拼图按 Elo 分 B1–B5 五档难度。

### 发现一:联合预训练–RL 缩放律

- 固定 RL 计算量下,**RL 后 pass@1 可由预训练损失良好预测**;
- **RL 奖励曲线的局部斜率随 log 预训练 token 数近似线性增长**(数据规模塑造 RL 的"学习速率");
- 与 Chinchilla 式预训练缩放律结合,可对任意配方(N, T, C_RL)评分,画出**计算最优前沿**;
- **关键趋势:总计算增长时,最优分配向 RL 倾斜**——预训练占比应逐渐下降;
- 数学域佐证(GSM8K/MATH500):R_ref 与预训练 eval loss 线性相关 R²≈0.94–0.99,RL 斜率与 log₁₀T 正相关(Spearman +0.75/+0.94);
- 补充视角:后训练饱和(pass@1 边际收益递减)并非预训练与 RL 冲突——**RL 继承预训练策略的部分可达性能水平,学习速率由预训练数据规模塑造**,阶段式饱和是缩放关系的可预测结果。

### 发现二:RL 并非简单锐化 SFT 策略(难度依赖的异质效应)

- **易题**:放大 SFT 已偏好的正确走法(ground-truth amplification);
- **难题**:浮现 SFT 下几乎不存在的正确走法(tail discovery)——例如难题 B5 中预训练给错误走法约 95% 概率、正确走法几乎缺失,RL 50–750 步间正确走法升至首选;
- **同时**:RL 也会强化错误走法(wrong-mode amplification)——难题上错误走法同样被放大;
- 这些异质效应解释了 **RL 提高 pass@1 却不一致提高 pass@k**(大 k 时 base 模型可匹敌 RL 模型);
- **定量锐化检验**:KL 幂锐化系数 α* 随 RL 从 1.05→1.35,但 ExplainedSharp 全局仅 0.03→0.17——RL 大部分分布变化**无法用单一幂锐化解释**;"锐化"只是部分真相。

### 发现三:CoT 演化机制

- RL 增加搜索**宽度**(分支因子↑)而深度大致持平;
- 走法质量(Stockfish 归一化排名)持续提升;
- DFS 序列化一致性下降、节点重访增多(重新探索旧前缀);
- **深层覆盖(4-ply)增益随深度锐减**——RL 提升候选生成/选择快于长程搜索,提示 SFT 数据构造应鼓励更深系统化搜索。

## 代码 / 实现:实验配置要点

- **模型**:Qwen 风格 decoder-only + GQA,5M–1B 十档规模(层数 6–32、hidden 256–1536);
- **预训练**:54B token Lichess 语料(过滤 <10 ply、Elo 800–3000 平衡采样)、1 epoch、AdamW、cosine 调度;
- **SFT**:156K 拼图(Elo>800、popularity>100),42K 用于 SFT(难度平衡),3 epochs,H100×4;
- **RL**:GRPO(verl 框架),group size G=8、KL β=0.001、clip ε=0.2、温度 1.0、规则奖励(正确=1 否则 0)、H200×8;
- **去污染**:预训练语料中任何经过后训练/测试局面位置的棋局整体剔除;拼图按起始局面去重。

## 实践 / 应用:结论与启示

### 对计算分配的启示

1. **RL 不是万能的起点**:从弱预训练 checkpoint 过早开始 RL 收益有限——RL 仍**依赖初始化**,需要足够预训练暴露后才有效;
2. **算力越多越该投 RL**:计算最优前沿显示最优预训练占比随总预算增长而下降;
3. **pass@1 vs pass@k 分歧**:RL 优化 pass@1 不等于优化 pass@16——**提升 pass@k 需要减少错误模式放大、扩展正确解的支持(support),而不只是锐化当前策略**;
4. **两阶段配方可能不是最优**:固定"先预训练后 RL"可能次优,未来可研究**交错策略**(何时额外预训练数据比额外 RL 更新更有价值)。

### 局限(论文明确声明)

- 象棋词表小(81 token)、验证精确、推理不纠缠世界知识与流畅性——**缩放指数与类别比例是受控环境下的结构刻画,不是语言模型的定量预测**;
- 模型 ≤1B,大尺度下趋势(如最优预训练占比下降)可能不同;
- RL 环境是唯一指定解 + 二元奖励的受限验证形式;
- 结构化 CoT 使用特定树形序列化,不同推理轨迹格式可能产生不同 CoT 演化动力学。

### 可复用的测试床价值

论文提供了一个**受控测试床方法论**:把不可控、昂贵的 LLM 管线压缩成可负担、可逐走法检验的科学实验平台——可用于研究合成数据设计、self-play、transcendence、weak-to-strong generalization 等。

## 总结

- **核心问题**:预训练选择如何塑造 RL 算力回报?RL 对模型做了什么?——用象棋测试床给出量化答案;
- **联合缩放律**:预训练损失预测 RL 后 pass@1 水平,预训练数据规模塑造 RL 学习速率;计算最优前沿显示**总预算增长时最优分配向 RL 倾斜**;
- **RL 机制**:不是简单锐化——易题放大已有正确走法、难题浮现近乎缺失的正确走法但也强化错误走法;异质效应解释"pass@1 升而 pass@k 不一定升";
- **RL 依赖初始化**:从弱预训练 checkpoint 开始 RL 收益有限,需要足够预训练暴露;
- **下一步**:结合站内 [预训练](pretraining.md)(缩放律基础)与 [Agent 后训练](agent-post-training.md)(SFT 记忆 vs RL 泛化),理解"预训练先验质量 × RL 优化"的完整接口。

## 延伸阅读

- 论文:https://arxiv.org/abs/2607.16097(HTML:https://arxiv.org/html/2607.16097v1);代码 https://github.com/pavelslab-nyu/pre2post-chess;数据 https://huggingface.co/pavelslab-nyu/pre2post-chess
- 引用关键工作:Kaplan 2020 / Chinchilla 2022(预训练缩放律)、DeepSeek-R1(Guo 2025)/ Tulu 3 / DAPO / SimpleRL(RLVR 实践)、Yue 2025(锐化论)/ Yuan 2025(组合论)/ Sun 2025(两者皆有)、AlphaZero、Searchformer(Ruoss 2024)
- 站内:[预训练](pretraining.md)(Scaling Laws/Chinchilla 基础)、[Agent 后训练](agent-post-training.md)(SFT vs RL 分工)、[RLHF 对齐](rlhf-alignment.md)(RL 算法基础)、[推理时验证](../09-agent-research/inference-time-verification.md)(pass@k 与验证)
