# 大语言模型 LLM:用"预测下一个词"撬动智能

> **一句话摘要**:LLM 是在万亿 token 上学到概率分布、能续写一切文本的神经网络。本文讲清 LLM 是什么、三大核心能力、训练三步走及其局限。
>
> **来源**:综合公开资料 —— OpenAI GPT 系列技术报告、《Language Models are Few-Shot Learners》(Brown et al., 2020)、DeepMind Chinchilla 报告,详见文末延伸阅读。

## 概念

- **定义**:大语言模型(Large Language Model, LLM)是**参数量巨大(数十亿到数万亿)的深度神经网络**,在**海量文本**上做**自监督预训练**,学会以条件概率 $P(y \mid x)$ 续写任意文本。代表:GPT、Llama、DeepSeek、Claude、Gemini。
- **"大"体现在哪**:参数多(GPT-3 为 175B)、数据多(预训练语料数万亿 token)、算力多(训练耗数万 GPU·时)。"大"带来的质变是本章 [预训练与规模定律](pretraining.md) 的核心话题。
- **本质是语言模型**:一个概率模型 $P(w_1,...,w_n)$,对文本序列打分或采样。统计时代也有 n-gram 语言模型,LLM 的区别是**用 Transformer 在更大数据上学习**,见 [Transformer 架构](transformer-architecture.md)。
- **为什么重要**:把"理解"与"生成"统一成同一件事——任务都表达为"给文本、预测下一段",一个模型通吃,是生成式 AI 的底座。

!!! note "LLM 与聊天机器人"
    聊天只是 LLM 的**一种界面**。无论怎么包装,模型内部始终在做同一件事:根据已有 token 预测下一个 token。这是理解后续所有文章(微调、RLHF、Agent)的前提。

## 原理

### 三大核心能力

| 能力 | 含义 | 例子 |
|---|---|---|
| **文本生成**(generation) | 自回归采样,逐个 token 续写 | 作文、补全代码、翻译 |
| **理解**(understanding) | 内部表征编码句法、语义与常识 | 摘要、分类、情感分析 |
| **上下文学习**(in-context learning, ICL) | **不改权重**,输入里给示例就现场学会新任务 | few-shot 提示给 3 个示例即照做 |

ICL 是 LLM 的标志性能力(GPT-2 没有,GPT-3 才涌现),分 **zero-shot**(只给指令)与 **few-shot**(给示例);它靠注意力机制把示例"带到"生成位置。

### 训练三步走总览

| 阶段 | 数据 | 目标 | 产物 |
|---|---|---|---|
| **预训练** | 无标注原始文本 | 预测下一个 token(自监督) | 续写机器(基座模型) |
| **微调 SFT** | 少量「指令-回答」 | 监督学习学会"听话" | 指令模型 |
| **对齐** | 人类偏好排序 | RLHF/DPO 更安全有用 | 对齐模型 |

```text
原始文本 ──预训练──▶ 基座模型 ──SFT──▶ 指令模型 ──RLHF──▶ 对齐模型
```

分别详见 [预训练与规模定律](pretraining.md)、[微调 Fine-tuning](fine-tuning.md)、[RLHF 与对齐](rlhf-alignment.md)。

### 语言建模的数学本质

按链式法则,文本联合概率拆成逐位置条件概率:

$$P(w_1, \dots, w_n) = \prod_{i=1}^{n} P(w_i \mid w_1, \dots, w_{i-1})$$

训练时把"预测下一个词"当分类问题:每个位置模型输出覆盖**整个词表**的分布 $\hat{p}$,与真实下一个词 $y_i$ 算**交叉熵**:

$$\mathcal{L} = -\frac{1}{n}\sum_{i=1}^{n} \log P_\theta(y_i \mid w_{<i})$$

**模型在训练中唯一学会的技能就是"续写"**;翻译、推理、代码等一切能力都是从"续写"里隐式长出来的——这是理解 LLM 最重要的一句话。

## 代码 / 实现

用纯 Python 实现最简 **bigram 语言模型**——只根据上一个词预测下一个词(真实 LLM 是"看过任意长上文"的 bigram):

```python
import random
from collections import defaultdict

# 小型语料:每行一个句子(真实预训练是数万亿 token 的网页/书籍语料)
corpus = """the cat sat on the mat
the dog ran in the park
the cat and the dog are friends
a bird sat on the tree""".strip().splitlines()

# 1. 统计 bigram 计数:从词 a 后面出现词 b 的次数
counts = defaultdict(lambda: defaultdict(int))
for line in corpus:
    words = ["<s>"] + line.split() + ["</s>"]   # 句首/句尾哨兵
    for a, b in zip(words, words[1:]):
        counts[a][b] += 1

# 2. 计数转概率 P(b|a)
def next_word_probs(word):
    total = sum(counts[word].values())
    return {b: c / total for b, c in counts[word].items()}

# 3. 句子联合概率:所有位置条件概率连乘
def sentence_prob(sentence):
    words = ["<s>"] + sentence.split() + ["</s>"]
    p, probs = 1.0, []
    for a, b in zip(words, words[1:]):
        pr = counts[a].get(b, 0) / sum(counts[a].values()) if counts[a] else 0.0
        probs.append(pr)
        p *= pr
    return p, probs

# 4. 采样生成:每一步只根据"上一个词"决定"下一个词"
def generate(n_words=8, seed=42):
    rng = random.Random(seed)
    w, out = "<s>", []
    for _ in range(n_words):
        w = rng.choices(list(counts[w]), weights=list(counts[w].values()))[0]
        if w == "</s>":
            break
        out.append(w)
    return " ".join(out)

print("P(mat | the)     =", round(next_word_probs("the").get("mat", 0.0), 3))
print("P(the | <s>)     =", round(next_word_probs("<s>").get("the", 0.0), 3))
p, ps = sentence_prob("the cat sat on the mat")
print("P('the cat sat on the mat') =", round(p, 4), "各步:", [round(x, 2) for x in ps])
for seed in (1, 2, 3):
    print(f"生成(seed={seed}):", generate(seed=seed))
```

- **第 1 步**统计条件频率即"学习"雏形:知识全在 `counts` 表里(真实 LLM 编码在数十亿参数中)。
- **第 3 步**演示核心公式 $P(w)=\prod P(w_i|w_{<i})$:好句子概率高、病句低,这就是"打分能力"。
- **第 4 步**演示**自回归生成**:按学到的分布采样,每次吐一个词。句子通顺但语义飘忽——它只看了上一个词,**长距离依赖正是 Transformer 要解决的**。

运行:`python3 llm_bigram.py`(仅标准库)。

## 实践 / 应用

### 三大局限

- **幻觉(hallucination)**:编造看似合理实则错误的事实。根源是模型只学"像不像"不保证"对不对"。缓解:检索增强 [RAG](rag.md)、限定来源、人工审核。
- **上下文窗口**:一次只能"看到"有限长度上文,超出记不住,长上下文算力陡增。对策:分块、RAG。
- **成本**:生成 1000 token 要做 1000 次前向;显存放不下 70B 模型需量化/蒸馏,见 [推理与部署](inference-deployment.md)。

### 场景与选型

| 场景 | 方案 | 关键点 |
|---|---|---|
| 写作/翻译/摘要 | 直接对话或 API | 提示词工程 |
| 代码补全 | 续写式 completion API | 给足上下文 |
| 私有知识问答 | RAG | 检索质量决定效果 |
| 固定格式/风格助手 | 微调 | 数据质量第一 |

**选型建议**:任务简单 → 提示词;需私有知识 → RAG;需固定格式与风格 → 微调;要安全合规 → 对齐优先。

## 总结

- LLM = 大参数 Transformer + 万亿 token 自监督预训练,**唯一技能是"预测下一个词"**。
- 三大核心能力:生成、理解、上下文学习(ICL);ICL 不改权重、现场学任务。
- 训练三步走:预训练(续写)→ SFT(听话)→ 对齐(安全有用)。
- 语言建模的数学:链式法则 + 交叉熵(见本页代码)。
- 三大局限:幻觉、上下文窗口、成本;对策是 RAG、分块、量化。

**下一步**:先读 [Transformer 架构](transformer-architecture.md) 弄清"预测引擎"长什么样,再依次读 [Tokenizer](tokenizer.md) 与 [预训练与规模定律](pretraining.md)。

## 延伸阅读

- 站内:[AI/ML/DL 基础](../01-ai-basics/ai-ml-dl.md)、[神经网络入门](../01-ai-basics/dl-neural-network-basics.md)、[Transformer 架构](transformer-architecture.md)、[预训练与规模定律](pretraining.md)、[微调 Fine-tuning](fine-tuning.md)
- 外部:论文《Language Models are Few-Shot Learners》(GPT-3)、OpenAI GPT-1~4 技术报告、视频 *Andrej Karpathy: Let's build GPT*
