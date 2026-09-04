# 预训练与规模定律:大模型的"学习"与"涌现"

> **一句话摘要**:预训练让模型在万亿 token 上自学"预测下一个词",是 LLM 一切能力的来源;规模定律说损失随参数/数据/算力按幂律下降。本文讲预训练目标、数据清洗、Scaling Laws、Chinchilla、涌现与困惑度。
>
> **来源**:论文《Scaling Laws for Neural Language Models》(Kaplan et al., 2020)、《Training Compute-Optimal Large Language Models》(Hoffmann et al., 2022)、GPT 系列技术报告。

## 概念

- **定义**:预训练(pretraining)是在**大规模无标注文本**上的**自监督学习**,任务为**因果语言建模(causal language modeling)**——只看左边 token,预测下一个。
- **为什么重要**:预训练是 LLM 能力的**唯一来源**,微调/对齐只是"修剪与引导";数据、参数、算力决定上限(即规模定律)。
- **预训练 vs 微调**:预训练用海量语料学"语言与知识",成本极高;[微调](fine-tuning.md) 用少量数据改"行为方式",成本低。两者目标相同(都是 next-token prediction),区别在**数据分布**。

## 原理

### 1. 预训练目标:next token prediction

给定序列 $x_1,...,x_T$,模型在每个位置输出下一 token 的分布,最小化平均交叉熵:

$$\mathcal{L}(\theta) = -\frac{1}{T}\sum_{t=1}^{T} \log P_\theta(x_{t} \mid x_1, \dots, x_{t-1})$$

两个关键工程点:

- **因果 mask**:注意力只允许看 $x_{<t}$(见 [Transformer 架构](transformer-architecture.md) 代码),防止"偷看答案";
- **每个 token 都贡献梯度**:一句 1000 token = 1000 个训练样本,自监督因此能吃下万亿 token。

### 2. 训练数据与清洗

语料 = 网页 + 书籍 + 论文 + 代码 + 百科等,清洗是**隐藏的质量关键**:

- **去重**:重复文本会让模型背诵、损失失真;
- **质量过滤**:规则 + 分类器筛掉垃圾网页、错误内容;
- **混合配比**:不同来源按比例混合,配比决定模型"性格";
- **去污染**:排除下游评测集,防"数据泄漏"虚高成绩。

### 3. 规模定律 Scaling Laws

Kaplan et al. (2020) 发现:测试损失随参数量 $N$ 按**幂律**下降:

$$L(N) \approx A_N \cdot N^{-\alpha_N}$$

对数据量 $D$、算力 $C$ 也有类似幂律 $L(D)\approx A_D D^{-\alpha_D}$、$L(C)\approx A_C C^{-\alpha_C}$,典型指数 $\alpha \in [0.05, 0.1]$。含义:

- **无天花板**:砸更多参数/数据/算力,损失稳定下降,不存在平台期;
- **三维联动**:最优配比下损失 ∝ 总算力的幂次,模型与数据应同步放大。

!!! note "规模定律曲线长什么样"
    loss-D 曲线横轴取对数后近似一条直线(幂律)。因此"再翻十倍数据还能降多少"可用当前点斜率直接外推——正是用**小规模实验预测大规模效果**的依据。

### 4. Chinchilla:最优配比

Kaplan 原报告主张"参数主导";Chinchilla (Hoffmann et al., 2022) 用 400+ 实验重新拟合,结论:**参数量与训练 token 数同步缩放,约 20 token/参数**。

| 参数规模 | Kaplan 建议 token | Chinchilla 建议 token |
|---|---|---|
| 70B | ~0.2T | ~1.4T |
| 7B | ~0.02T | ~0.14T |

此前模型普遍"**欠训练**";此后行业转向同规模训练更久,或用**小模型 + 更多数据**达到同等效果(如 Llama 用 1~2T token 训 7B)。

### 5. 涌现能力

规模超过阈值后,模型突然获得小模型没有的能力:few-shot 推理、代码生成等。两种解释:

- **涌现派**:能力随规模**台阶式突变**,有阈值;**平滑派**:其实平滑增长,只是用**非线性指标**(准确率)让它像"突变"。

两派都承认:**小模型测不出的能力,大模型有**——这是 [大语言模型概述](llm-intro.md) 中"为什么重要"的答案。

## 代码 / 实现

纯 NumPy 演示**交叉熵与困惑度**,并模拟规模定律形状:

```python
import numpy as np

rng = np.random.default_rng(0)
V = 32000        # 词表大小
N = 2000         # 待预测的 token 数量

def evaluate(logits, target):
    """给定模型对 N 个位置输出的 logits 与真实 token,计算平均交叉熵与困惑度"""
    logits = logits - logits.max(axis=1, keepdims=True)    # 数值稳定
    logsumexp = np.log(np.sum(np.exp(logits), axis=1))
    ce = logsumexp - logits[np.arange(N), target]          # 每个位置的交叉熵
    return float(np.mean(ce)), float(np.exp(np.mean(ce)))  # (平均CE, 困惑度)

target = rng.integers(0, V, size=N)

# 1. 随机猜测:logits 全 0 → 均匀分布,困惑度 ≈ 词表大小
ce0, ppl0 = evaluate(np.zeros((N, V)), target)
print(f"随机猜测:      平均CE={ce0:8.3f}  困惑度={ppl0:9.1f}  (理论≈{V})")

# 2. 中等模型:正确 token 的 logit 平均高出 5
mid = rng.normal(0, 1, size=(N, V))
mid[np.arange(N), target] += 5
ce1, ppl1 = evaluate(mid, target)
print(f"中等模型:      平均CE={ce1:8.3f}  困惑度={ppl1:9.1f}")

# 3. 强模型:正确 token 的 logit 平均高出 12
strong = rng.normal(0, 1, size=(N, V))
strong[np.arange(N), target] += 12
ce2, ppl2 = evaluate(strong, target)
print(f"强模型:        平均CE={ce2:8.3f}  困惑度={ppl2:9.1f}")

# 4. 困惑度的直觉:困惑度 k ≈ 平均从 k 个等概率候选中选择
print("\n困惑度含义:困惑度 k 表示模型平均像'从 k 个等概率候选中选择'")
for k in (32000, 100, 15):
    p = 1.0 / k
    ce = -np.log(p)
    print(f"  均匀 k={k:>6}: 交叉熵={ce:.3f}, 困惑度={np.exp(ce):.0f}")

# 5. 规模定律演示:损失随数据量按幂律 L(D)=A·D^(-α) 下降(α≈0.095)
D = np.array([1e8, 1e9, 1e10, 1e11, 1e12])   # 训练 token 数
loss = 4.0 * D ** -0.095
print("\n规模定律模拟(损失随数据量下降):")
for d, l in zip(D, loss):
    print(f"  D={d:.0e} token -> 验证损失≈{l:.3f}")

# 6. Chinchilla 最优配比:每参数约 20 个 token
print("\nChinchilla 最优配比(参数:token ≈ 1:20):")
for params in (7e9, 13e9, 70e9):
    print(f"  参数 {params/1e9:.0f}B -> 最优训练 token ≈ {params*20/1e12:.2f}T")
```

- **第 1~3 段**:随机模型困惑度=32000(词表大小),强模型≈1.5——困惑度越低模型越"确定"正确的下一个词。
- **第 4 段**:困惑度 ≈ "平均从 k 个等概率候选中挑"。
- **第 5~6 段**用解析式模拟"损失随数据幂律下降"与"20 token/参数"规则。

运行:`python3 ppl_demo.py`(仅标准库 + numpy)。**真实训练**:`pip install torch`,`nn.CrossEntropyLoss` + 掩码即可复现预训练目标。

## 实践 / 应用

- **评估**:困惑度与下游任务强相关但不完全一致;上线前要做人类评测与基准(MMLU、HumanEval)。
- **困惑度受分词影响**:同一模型换 [tokenizer](tokenizer.md),数值不可直接比较。
- **训练预算**:先用小规模实验拟合自己的规模定律曲线,再决定参数/数据/算力分配。
- **商用启示**:GPT-4 级参数+数万亿 token 按 Chinchilla 配比;个人更接近**继续预训练**或 [微调](fine-tuning.md)。
- **涌现的工程含义**:小模型测不出的能力别急着下结论,换连续指标。

## 总结

- 预训练 = 万亿 token 上的**因果语言建模**(next token prediction)。
- 数据清洗(去重、过滤、配比、去污染)决定模型上限。
- 规模定律:损失随参数/数据/算力按**幂律**下降,不存在平台期。
- Chinchilla:**参数:token ≈ 1:20**,同步缩放。
- 涌现能力让大模型具备小模型没有的能力;困惑度是核心指标。

**下一步**:读 [微调 Fine-tuning](fine-tuning.md) 与 [RLHF 与对齐](rlhf-alignment.md)。

## 延伸阅读

- 站内:[大语言模型概述](llm-intro.md)、[Transformer 架构](transformer-architecture.md)、[Tokenizer 与词表](tokenizer.md)、[微调 Fine-tuning](fine-tuning.md)
- 外部:论文《Scaling Laws for Neural Language Models》(Kaplan 2020)、《Training Compute-Optimal Large Language Models》(Chinchilla 2022)、《Are Emergent Abilities a Mirage?》(Schaeffer 2023)
