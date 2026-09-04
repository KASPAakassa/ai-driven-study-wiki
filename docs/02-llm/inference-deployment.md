# 推理与部署:让大模型从"算出来"到"跑得快"

> **一句话摘要**:训练好模型只是第一步,生产要的是"快、省、稳"。本文讲清训练 vs 推理差异、自回归生成、KV Cache 提速原理、INT8/INT4 量化,以及 vLLM/PagedAttention。
>
> **来源**:综合公开资料 —— PagedAttention 论文(Kwon et al., 2023)、vLLM 官方文档、Hugging Face 量化文档。

## 概念

- **训练 vs 推理**:训练是**前向+反向**(更新权重),吃显存、对延迟不敏感;推理**只有前向**(逐 token 自回归),对延迟与吞吐极敏感。同一模型训练用 8×A100,推理 1 卡 + 量化 + 批处理即可。
- **两个指标**:**延迟(Latency)** = 单请求从发出到收到回答的时间(聊天体验关键);**吞吐(Throughput)** = 单位时间处理的请求/token 数(决定成本与并发)。两者常**冲突**:批越大吞吐越高但延迟上升。

## 原理

### 自回归生成:一个词一个词地"猜"

LLM 是条件概率分布:给定上文预测下一个 token。生成时循环:序列 $x_{1..t}$ 送入模型 → 取末位 logits 经 softmax 得 $P(x_{t+1}\mid x_{1..t})$ → 采样 → 拼回,直到 `<EOS>` 或长度上限。

$$P(x_1,\dots,x_T) = \prod_{t=1}^{T} P(x_t \mid x_1,\dots,x_{t-1})$$

- 一次前向算整条序列的注意力,但只有**末位 logits** 用于采样;
- 生成 token 数远大于输入,推理时间绝大部分在"逐 token 生成"。

### KV Cache:让历史计算不再重复

每个位置的 Key/Value 只依赖它自己。**朴素做法**每步把整条序列重新前向,历史 K/V 被反复重算;**KV Cache 把算过的 K/V 缓存**,每步只对**新 token** 算 Q/K/V 与新 Query 的注意力。

| 方案 | 第 t 步注意力计算量 | L 步总计 |
|---|---|---|
| 无缓存 | 重算前 t 个 token 的 K/V | $O(L^2 \cdot d)$ |
| KV Cache | 只算新 token 的 Q/K/V + $O(t)$ 注意力 | 每步 $O(t)$,省掉全部 K/V 重投影 |

代价:**缓存随序列线性占显存**,长上下文(128k)下可达数 GB。**PagedAttention** 把 KV Cache 分块分页管理,像虚拟内存一样按需分配、消除碎片——vLLM 因此吞吐提升 2~4 倍。

!!! note "显存去哪了"
    推理显存 = 权重 + KV Cache + 激活。7B FP16 权重约 14GB;KV Cache ≈ $2 \times L \times d_{kv} \times \text{层数} \times 2$ 字节,长序列下比权重还吃显存。

### 量化:用更少的位存权重

把 FP16 权重压到更低 bit,减显存与访存带宽,换更快推理:

- **INT8**:16bit→8bit,显存减半、精度损失小,是"基本无损"默认选择;
- **INT4**:再减一半,显存只需 1/4,但需精细算法补偿。

对称量化核心公式:

$$w_q = \mathrm{round}\left(\frac{w}{s}\right),\quad s = \frac{\max|w|}{2^{b-1}},\quad \hat{w} = w_q \times s$$

- **PTQ(训练后量化)** 最常用:用校准数据统计激活分布,逐通道/逐组缩放;QAT 精度最好但成本高。
- **GPTQ**:基于逐层最小化量化误差的二阶方法(Hessian 近似),INT4 事实标准;
- **AWQ**:根据激活分布找出**重要通道**为其保留更高精度,其余量化,速度更快。

### 推理框架:vLLM 与 PagedAttention

- **vLLM**:把 PagedAttention 引入生产,配合**连续批处理(continuous batching)**——每生成一个 token 就移出完成的请求、补入新请求;
- 其他:**TensorRT-LLM**(延迟最低)、**TGI**(易用)、**llama.cpp**(CPU/边缘,GGUF);
- 服务协议统一走 **OpenAI 兼容 API**,业务代码无缝切换。

## 代码 / 实现

用纯 NumPy 对比自回归生成中**有无 KV Cache 的注意力计算量**(规模加权):

```python
import numpy as np

def to_onehot(idx, vocab):
    v = np.zeros(vocab); v[idx] = 1.0
    return v

def gen_without_cache(W_emb, W_q, W_k, W_v, tokens, T_new):
    """朴素版:每步对整条序列重算 embedding 与 K/V,返回规模加权计算量。"""
    seq = tokens.copy()
    cost = 0
    for _ in range(T_new):
        L = len(seq)
        emb = seq @ W_emb                                   # (L,V)@(V,d)
        Q = emb @ W_q.T; K = emb @ W_k.T; V = emb @ W_v.T  # 3 次 L 规模投影
        scores = Q @ K.T                                    # L×L 注意力
        cost += L * vocab + 3 * L + L * L
        p = np.exp(scores - scores.max(-1, keepdims=True))
        p /= p.sum(-1, keepdims=True)
        nxt = int(np.argmax(p[-1]))
        seq = np.vstack([seq, to_onehot(nxt, vocab)[None, :]])
    return seq, cost

def gen_with_kv_cache(W_emb, W_q, W_k, W_v, tokens, T_new):
    """缓存版:只对每个新 token 算 embedding 与 Q/K/V,历史 K/V 复用。"""
    seq = tokens.copy()
    K = seq @ W_emb @ W_k.T
    V = seq @ W_emb @ W_v.T
    cost = len(seq) * vocab + 2 * len(seq)
    for _ in range(T_new):
        x = seq[-1:]
        e = x @ W_emb                            # 新 token embedding(规模 1)
        q = e @ W_q.T                            # 新 token 的 Q
        cost += vocab + 1
        scores = q @ K.T                         # 与当前缓存长度成正比
        cost += len(K)
        p = np.exp(scores - scores.max(-1, keepdims=True))
        p /= p.sum(-1, keepdims=True)
        nxt = int(np.argmax(p))
        seq = np.vstack([seq, to_onehot(nxt, vocab)[None, :]])
        K = np.vstack([K, e @ W_k.T]); V = np.vstack([V, e @ W_v.T])
        cost += 2
    return seq, cost

vocab, d, L, T_new = 64, 16, 8, 12               # 词表/隐藏维/初始长度/新生成数
rng = np.random.default_rng(0)
W_emb = rng.normal(0, 0.1, (vocab, d))
W_q = rng.normal(0, 0.1, (d, d)); W_k = W_q.copy(); W_v = W_q.copy()
tokens = np.zeros((L, vocab))                    # 初始 token 序列(one-hot)
tokens[np.arange(L), rng.integers(0, vocab, L)] = 1.0

_, c_naive = gen_without_cache(W_emb, W_q, W_k, W_v, tokens, T_new)
_, c_cache = gen_with_kv_cache(W_emb, W_q, W_k, W_v, tokens, T_new)
print(f"朴素版注意力计算量  : {c_naive:,}")
print(f"KV Cache 版计算量   : {c_cache:,}")
print(f"加速比: {c_naive / c_cache:.1f}x  (序列越长差距越大)")
```

- 朴素版每步重算整条序列的 embedding、K/V 投影($3L$)与全量注意力($L^2$);缓存版每步只算新 token。
- 本示例(初始 8 token、再生成 12 个)约 **9 倍**;真实系统端到端常提速 2~10 倍(MLP 等开销仍占一部分)。
- KV Cache 是所有主流推理框架的默认组件。

**生产示例**(需要 `pip install vllm`):

```python
from vllm import LLM, SamplingParams
llm = LLM(model="meta-llama/Llama-2-7b-chat-hf",
          quantization="awq", dtype="float16")
out = llm.generate(["用一句话解释 KV Cache。"],
                   SamplingParams(temperature=0.7, max_tokens=128))
print(out[0].outputs[0].text)
```

## 实践 / 应用

- **选框架**:极致延迟 TensorRT-LLM;省心高吞吐 vLLM;边缘 llama.cpp + GGUF INT4。
- **并发 vs 延迟**:动态批处理(max_num_seqs)+ 最长等待上限兼顾两者;分别盯**TTFT** 与 **TPOT**。
- **量化决策**:先 INT8(基本无损),再 INT4(GPTQ/AWQ);敏感任务 QAT;量化后重跑能力基准。
- **常见坑**:长上下文缓存爆炸(设 max-model-len);AWQ 权重与设备不匹配;知识敏感任务别直接量化。
- **服务化**:OpenAI 兼容接口 + 前缀缓存 + 流式输出(SSE);按显存规划单卡并发与多副本。

## 总结

- 推理只有前向,逐 token 自回归生成。
- KV Cache 缓存历史 K/V,避免重复投影;PagedAttention 用分页解决缓存碎片。
- 量化(INT8→INT4)以 bit 换显存与速度;GPTQ/AWQ 是主流 PTQ 方法。
- 延迟与吞吐按场景权衡;vLLM/TensorRT-LLM 封装了上述全部优化。

**下一步**:读 [RAG](rag.md) 学用检索补知识;回顾 [微调](fine-tuning.md) 与 [RLHF](rlhf-alignment.md) 了解上线前完整链路。

## 延伸阅读

- 站内:[微调](fine-tuning.md)、[RLHF 与对齐](rlhf-alignment.md)、[RAG](rag.md)
- 外部:PagedAttention 论文;vLLM 文档;Hugging Face 量化指南;GPTQ 论文;AWQ 论文
