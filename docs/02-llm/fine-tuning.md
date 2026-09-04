# 微调 Fine-tuning:把通用大模型调教成你的专属助手

> **一句话摘要**:基础大模型只会"续写",微调用少量高质量数据教会它"听话办事"。本文讲清 SFT、全参 vs LoRA(PEFT)、QLoRA 的原理与实践。
>
> **来源**:综合公开资料 —— LoRA 论文《LoRA: Low-Rank Adaptation of Large Language Models》(Hu et al., 2021)、QLoRA 论文《QLoRA: Efficient Finetuning of Quantized LLMs》(Dettmers et al., 2023)、Hugging Face 官方文档。

## 概念

- **为什么需要微调**:预训练大模型(GPT、Llama)只会"续写",不听话;从头训练需数万张 GPU 和上亿美元。微调(Fine-tuning)在**预训练权重上继续训练**,用少量高质量数据让模型学会对话、代码、客服等新能力。
- **微调 vs 提示工程**:提示工程不改权重,零成本但天花板有限;微调把行为**固化进参数**,更稳更快,还能学到提示词说不清的"隐性风格"。
- **微调 ≠ 增加知识**:微调改变**行为方式**(格式、语气、指令遵循),很难注入事实知识;新知识靠 [RAG](rag.md) 或继续预训练。

## 原理

### 第一步:指令微调 SFT(Supervised Fine-Tuning)

把「指令 + 回答」样本整理成**对话格式**,用**语言建模交叉熵损失**继续训练:

- 对话格式(如 ChatML):`<|user|>...<|assistant|>` 标记角色边界,让模型学会"谁在说话"。
- **损失只算 assistant 回答部分**,user 输入掩码(mask)掉。
- 损失函数(与预训练相同,只是数据不同):

$$L = -\frac{1}{|Y|}\sum_{i=1}^{|Y|} \log P_\theta(y_i \mid x, y_{<i})$$

- 这是**监督学习**(有标准答案),不是强化学习;"答得好不好"交给 [RLHF 对齐](rlhf-alignment.md)。

!!! note "SFT 的本质"
    SFT 就是"换一批有监督数据继续做 next-token prediction",区别只在数据分布与损失掩码——复用普通语言建模训练脚本即可。

### 第二步:全参微调 vs 参数高效微调

| 维度 | 全参微调(Full FT) | PEFT(如 LoRA) |
|---|---|---|
| 更新参数 | 全部(70B 模型改 70B 参数) | 仅 0.1%~1% |
| 显存 | 极高(梯度+优化器状态) | 低,单卡可微调 7B~70B |
| 效果 | 上限最高 | 通常达全参的 90%~100% |
| 产物 | 每任务一份完整权重 | 几 MB~几十 MB 适配器 |
| 适用 | 数据多、GPU 充足 | 个人与中小团队主流 |

全参微调开销主要来自**优化器状态**:Adam 每参数保存一阶/二阶矩,7B 模型仅优化器状态就约 $7B\times16$ 字节 ≈ 112GB 显存。

### LoRA 原理:低秩分解

核心洞察:**微调时权重的变化量 ΔW 是低秩的**——无需全部参数表达"学会了什么"。LoRA 把 ΔW 分解为两个小矩阵:

$$W' = W + BA, \quad B \in \mathbb{R}^{d \times r}, \quad A \in \mathbb{R}^{r \times k}, \quad r \ll \min(d,k)$$

- 训练时**冻结 W**,只训 A、B;推理时把 $BA$ 合并回 W(零额外延迟),或保留多个适配器切换。
- 参数量对比:全量更新需 $d \times k$ 个参数,LoRA 只需 $dr + rk$ 个。以 $d=k=4096$、$r=16$ 为例:

$$\frac{dk}{dr + rk} = \frac{4096^2}{2 \times 4096 \times 16} = \frac{16,777,216}{131,072} \approx 128 \text{ 倍节省}$$

- 常见设定:$r \in \{8,16,64\}$,只作用于 Attention 的 **Q/K/V/O 投影层**;$\alpha$ 为缩放系数,最终权重 $W + \frac{\alpha}{r} BA$。

### QLoRA:量化版 LoRA

QLoRA 让 65B 模型也能在单张 48GB 显卡上微调:

1. **4-bit NF4 量化**:冻结的 W 量化到 4-bit(NormalFloat4),权重显存缩到 1/8;
2. **双重量化**:对量化常数再量化一次,再省一笔;
3. **分页优化器**:显存不足时把优化器状态换页到 CPU 内存;
4. LoRA 参数保持**高精度(FP16/BF16)**训练,梯度只反传进小适配器。

### 数据质量与过拟合

- 数据量通常 **1k~100k 条**即可见效,**质量永远第一**:重复、错别字、风格混杂的数据会教坏模型。
- 过拟合信号:几十 epoch 后"背诵训练数据",验证 loss 反弹、同义改写不泛化。对策:数据多样、早停、秩不宜过大。
- 配比:**指令遵循数据 + 通用语料混合**,避免灾难性遗忘。

## 代码 / 实现

用纯 NumPy 演示 LoRA 的**参数量节省**与**低秩近似的误差权衡**:

```python
import numpy as np

def count_params(w_shape, r):
    """全参更新 vs LoRA 更新参数量"""
    d, k = w_shape
    full = d * k
    lora = d * r + r * k
    return full, lora

d, k, r = 4096, 4096, 16
full, lora = count_params((d, k), r)
print(f"全参微调: {full:,} 参数 | LoRA(r={r}): {lora:,} 参数")
print(f"节省倍数: {full / lora:.1f}x")

# 演示 2:低秩近似(Eckart-Young 定理)——真实 ΔW 是秩 16 矩阵,
# 最佳秩-r 近似即 SVD 截断,误差随 r 增大单调减小。
rng = np.random.default_rng(42)
d = 64
B_true = rng.normal(0, 1, size=(d, 16))
A_true = rng.normal(0, 1, size=(16, d))
true_delta = B_true @ A_true                     # 真实 ΔW(秩 16)

U, S, Vt = np.linalg.svd(true_delta, full_matrices=False)
for rank in (1, 4, 16):
    approx = (U[:, :rank] * S[:rank]) @ Vt[:rank, :]   # 秩 r 最佳近似
    err = np.linalg.norm(true_delta - approx) / np.linalg.norm(true_delta)
    print(f"r={rank:>2}: 最佳低秩近似相对误差 = {err:.3f}")

# 反例:若 ΔW 是高秩随机噪声,低秩近似必然失真(假设不成立时)
noise = rng.normal(0, 1, size=(d, d))
Un, Sn, Vtn = np.linalg.svd(noise, full_matrices=False)
approx_n = (Un[:, :16] * Sn[:16]) @ Vtn[:16, :]
err_noise = np.linalg.norm(noise - approx_n) / np.linalg.norm(noise)
print(f"高秩随机 ΔW 用 r=16 近似: 相对误差 = {err_noise:.3f}")

# 演示 3:推理时合并 W' = W + ΔW(低秩更新),零额外开销
W = rng.normal(0, 1, size=(d, d))
merged = W + approx          # 复用 r=16 的近似
print("合并后权重形状:", merged.shape)
```

- 第 1 段给出参数量节省的定量答案:16,777,216 → 131,072,约 **128 倍**。
- 第 2 段用 SVD 截断(Eckart-Young 定理)演示:低秩 ΔW 用 r 越大误差越小,而高秩随机矩阵无法被低秩近似——这正是 LoRA 有效的数学前提。
- 第 3 段是部署要点:训练完把 $BA$ 合并进 W,推理时**零额外开销**。

**PyTorch 实践**:`pip install torch peft transformers`;`LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj","k_proj","v_proj","o_proj"])` + `get_peft_model(model, config)` 即冻结原权重只训 A/B;`model.save_pretrained("my-lora")` 只存几 MB 适配器。

## 实践 / 应用

- **选型**:数据 < 10k、低成本 → LoRA/QLoRA;数据 > 100k、GPU 充足 → 全参微调。
- **多适配器福利**:同一底座可挂多套 LoRA(代码、客服、写作),按需切换。
- **超参经验**:学习率 $1\times10^{-4}\sim5\times10^{-4}$(只动少量参数,可略大);epoch 3~10;`lora_alpha=2r` 起步;序列长度 2048+。
- **大坑**:数据重复、回答夹带 user 话术(格式错)是常见翻车原因;验证用**训练分布之外**的样本。
- **后续**:SFT 后再接偏好对齐(DPO/RLHF)让回答更讨喜安全,见 [RLHF 与对齐](rlhf-alignment.md)。

## 总结

- 微调 = 在预训练权重上继续训练,用少量高质量数据改变**行为方式**;知识注入靠 RAG。
- SFT 是掩码对话格式下的交叉熵,只对 assistant 部分算损失。
- LoRA 把 ΔW 分解为 $W+BA$,参数省两个数量级;QLoRA 用 4-bit 量化把门槛降到单卡。
- 数据质量 > 数据数量,警惕过拟合与灾难性遗忘。

**下一步**:继续读 [RLHF 与对齐](rlhf-alignment.md) 了解如何让模型"说人话、守规矩",再读 [推理与部署](inference-deployment.md) 把模型跑起来。

## 延伸阅读

- 站内:[推理与部署](inference-deployment.md)、[RLHF 与对齐](rlhf-alignment.md)、[RAG](rag.md)、[反向传播](../01-ai-basics/dl-backpropagation.md)
- 外部:论文《LoRA: Low-Rank Adaptation of Large Language Models》《QLoRA: Efficient Finetuning of Quantized LLMs》《LIMA: Less Is More for Alignment》;Hugging Face PEFT 文档
