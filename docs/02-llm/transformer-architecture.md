# Transformer 架构:注意力是一切的核心

> **一句话摘要**:Transformer 是 2017 年提出、完全用**自注意力**取代循环的序列模型:可全并行、擅长长程依赖,是 GPT/LLM 的心脏。
>
> **来源**:论文《Attention Is All You Need》(Vaswani et al., 2017, NeurIPS)。

## 概念

- **定义**:Transformer 是**纯注意力**架构:每个 token 同时看序列里所有其他 token 并加权聚合,不像 RNN 逐个处理。原文是**编码器-解码器**结构。
- **GPT 只用解码器**:GPT 砍掉编码器,只用**解码器**做**自回归**生成(只看左边、预测右边)。绝大多数 LLM(GPT、Llama、DeepSeek)都是"仅解码器":每层 = 注意力块 + 前馈网络 FFN。
- **为什么赢**:①全并行,②任意两位置路径 O(1),③随数据/参数平滑扩展——大模型时代事实标准。

!!! note "注意力不是 Transformer 发明的"
    注意力 2014 年起就在机器翻译中用于给 RNN 加权上下文;Transformer 的贡献是**去掉 RNN,只靠注意力**。

## 原理

### 1. Self-Attention:Q / K / V

每个 token 同时扮演三个角色——**Q(query)**"我在找什么"、**K(key)**"我是什么"、**V(value)**"我能提供什么";经三个投影矩阵 $q_i=x_iW^Q$、$k_i=x_iW^K$、$v_i=x_iW^V$ 后,输出是"所有 value 按相似度加权求和":

$$Attention(Q, K, V) = \mathrm{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V$$

即权重 $\alpha_{ij} \propto \exp(q_i \cdot k_j / \sqrt{d_k})$,输出 $z_i = \sum_j \alpha_{ij} v_j$。

**为什么除以 $\sqrt{d_k}$**:$d_k$ 大时,两个独立随机向量点积分差≈$d_k$,softmax 输入饱和、梯度消失;缩放后方差≈1(见代码第 4 段实证)。

### 2. Multi-Head:多头

把 Q/K/V 切成 $h$ 份,各自做注意力再拼接投影:

$$\text{MultiHead}(Q,K,V) = \text{Concat}(\text{head}_1,\dots,\text{head}_h) W^O, \quad \text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$$

各头学到不同模式:指代消解、语法依存、共现等。参数量不变(每头维度减半),表达力大增。

### 3. 位置编码:给并行的序列补"顺序"

注意力是**置换等变**的——打乱 token 顺序结果只是跟着乱,必须注入位置信息。原文用正弦编码:

$$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d_{model}}}\right), \quad PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d_{model}}}\right)$$

不同频率可表达相对位置且能外推;Llama 等后来改用**旋转位置编码 RoPE**,把相对位置直接编进 Q/K 内积。

### 4. 残差连接与 LayerNorm

每个子层外都套"残差 + LayerNorm",保证深层梯度通畅、训练稳定:

$$x' = x + \mathrm{SubLayer}(\text{LayerNorm}(x)), \qquad \text{LayerNorm}(x) = \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}} \odot \gamma + \beta$$

现代模型多用 **Pre-LN**(先归一化再进子层)。

### 5. 相比 RNN 的优势

| 维度 | RNN / LSTM | Transformer |
|---|---|---|
| 训练并行 | 顺序依赖上一步,不可并行 | 整序列一次算完 |
| 长程依赖 | 路径长度 O(T),信息衰减 | 任意两位置 O(1) |
| 计算复杂度 | O(T·d²) | O(T²·d) |

代价是注意力 $O(T^2)$:序列翻倍计算量翻四倍,是上下文窗口扩展难、需要 FlashAttention 的原因。

## 代码 / 实现

纯 NumPy 实现 Self-Attention 前向(含 softmax、因果 mask、多头),并验证"为什么缩放":

```python
import numpy as np


def softmax(x):
    """数值稳定的 softmax:减去每行最大值防止 exp 溢出"""
    x = x - x.max(axis=-1, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=-1, keepdims=True)


def scaled_dot_product_attention(Q, K, V, mask=None):
    """缩放点积注意力。Q/K/V: (T, d_k),返回 (输出, 注意力权重)"""
    d_k = K.shape[-1]
    scores = Q @ K.T / np.sqrt(d_k)          # (T, T) 缩放点积
    if mask is not None:                     # 因果 mask:只允许看左侧
        scores = np.where(mask, -1e9, scores)
    attn = softmax(scores)                   # 每行是归一化的注意力权重
    return attn @ V, attn                    # (T, d_k), (T, T)


def multi_head_attention(X, W_qkv, W_o, num_heads, mask=None):
    """多头注意力(前向示意)。X: (T, d_model);W_qkv: (d_model, 3*d_model)"""
    T, d_model = X.shape
    d_k = d_model // num_heads
    Q, K, V = np.split(X @ W_qkv, 3, axis=-1)            # 各 (T, d_model)
    # 切头:(H, T, d_k)
    Q = Q.reshape(T, num_heads, d_k).transpose(1, 0, 2)
    K = K.reshape(T, num_heads, d_k).transpose(1, 0, 2)
    V = V.reshape(T, num_heads, d_k).transpose(1, 0, 2)
    scores = Q @ K.transpose(0, 2, 1) / np.sqrt(d_k)     # (H, T, T)
    if mask is not None:
        scores = np.where(mask, -1e9, scores)
    attn = softmax(scores)
    heads = attn @ V                                     # (H, T, d_k)
    concat = heads.transpose(1, 0, 2).reshape(T, -1)     # (T, d_model)
    return concat @ W_o, attn                            # (T, d_model), (H,T,T)


rng = np.random.default_rng(42)
T, d_model, H = 6, 32, 4
d_k = d_model // H
X = rng.normal(size=(T, d_model))

# 1. 单头自注意力:输出形状正确、注意力行和为 1
Wq = rng.normal(size=(d_model, d_k))
Wk = rng.normal(size=(d_model, d_k))
Wv = rng.normal(size=(d_model, d_k))
Q, K, V = X @ Wq, X @ Wk, X @ Wv
out, attn = scaled_dot_product_attention(Q, K, V)
print("单头输出形状:", out.shape)
print("注意力行和(应为1):", attn.sum(axis=1).round(6))

# 2. 因果 mask:GPT 生成时第 i 个 token 只能看 0..i
mask = np.triu(np.ones((T, T)), k=1).astype(bool)
out_c, attn_c = scaled_dot_product_attention(Q, K, V, mask)
print("因果注意力行和:", attn_c.sum(axis=1).round(6))
print("对角线以上权重全为0:", attn_c[np.triu_indices(T, 1)].max() < 1e-6)

# 3. 多头:输出拼回 d_model,每个头独立归一化
W_qkv = rng.normal(size=(d_model, 3 * d_model))
W_o = rng.normal(size=(d_model, d_model))
out_m, attn_m = multi_head_attention(X, W_qkv, W_o, H)
print("多头输出形状:", out_m.shape, "注意力块形状:", attn_m.shape)
print("多头每个头权重行和:", attn_m.sum(axis=-1).round(6).flatten()[:4])

# 4. 为什么缩放:随机向量点积分差 ≈ d_k,除以 sqrt(d_k) 后方差 ≈ 1
qd = rng.normal(size=(200, 128))
kd = rng.normal(size=(200, 128))
dots = qd @ kd.T
print("未缩放点积分差(理论≈128):", round(float(dots.var()), 1))
print("缩放后方差(理论≈1):", round(float((dots / np.sqrt(128)).var()), 2))
```

- 第 1/2 段:因果 mask 用 `np.where(mask, -1e9, scores)` 把未来位置压成 0 权重;第 3 段多头只多 reshape/transpose;第 4 段实证缩放意义。

**PyTorch 实践**:`pip install torch`;直接 `nn.MultiheadAttention(embed_dim, num_heads)` 即可,框架自动处理掩码与批量。

## 实践 / 应用

- **超参**:`d_model=768`(大模型 4096+),`num_heads=12~32`,`d_k=d_v=d_model//num_heads`;FFN 中间层 $4\times d_{model}$。
- **KV Cache**:新 token 的 K/V 与历史相同,缓存复用,是 [推理与部署](inference-deployment.md) 提速核心。
- **O(T²) 之敌**:FlashAttention 分块降显存;RoPE、滑动窗口也是常用手段。

## 总结

- Transformer = 自注意力(并行、长程依赖)+ 多头 + 位置编码 + 残差与 LayerNorm。
- 核心公式只有一个:$Attention(Q,K,V)=\mathrm{softmax}(QK^T/\sqrt{d_k})V$。
- GPT 用**仅解码器 + 因果 mask** 自回归生成;编码器-解码器是原文形态。
- 相比 RNN:全并行、路径 O(1),代价是 O(T²)。
- $\sqrt{d_k}$ 缩放防 softmax 饱和,代码有实证。

**下一步**:学 [Tokenizer](tokenizer.md) 与 [预训练与规模定律](pretraining.md)。

## 延伸阅读

- 站内:[大语言模型概述](llm-intro.md)、[Tokenizer 与词表](tokenizer.md)、[预训练与规模定律](pretraining.md)、[神经网络入门](../01-ai-basics/dl-neural-network-basics.md)
- 外部:论文《Attention Is All You Need》(2017)、博客 *The Illustrated Transformer* (Jay Alammar)、视频 *Let's build GPT* (Andrej Karpathy)
