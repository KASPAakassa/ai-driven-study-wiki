# RLHF 与对齐:让大模型从"会说话"到"说人话"

> **一句话摘要**:大模型能力强但"野",可能胡编、跑题、有毒。本文讲清为何要对齐、RLHF 三步(监督微调 → 奖励模型 → PPO)、DPO 如何免去强化学习,以及"对齐税"。
>
> **来源**:InstructGPT 论文(Ouyang et al., 2022)、DPO 论文(Rafailov et al., 2023)、Llama 2 对齐论文(Touvron et al., 2023)。

## 概念

- **为什么要对齐(Alignment)**:预训练只优化"预测下一个词",模型可能胡编、有害、废话或拒绝回答。对齐 = **让模型行为符合人类意图**,三大目标:**有用、诚实、无害(Helpful / Honest / Harmless)**。
- **对齐 vs SFT**:SFT 教模型**"怎么答"**(格式、服从指令);RLHF/DPO 教**"答什么更好"**(在多候选回答中学偏好)。两者层级不同,SFT 是对齐的基础。
- **对齐 ≠ 能力增强**:对齐不新增知识,只把输出概率重分配到更讨喜的回答上;极端对齐会损失部分能力——"对齐税"。

## 原理

### RLHF 三步走

**第 1 步:监督微调 SFT**。用人工标注的「指令 + 示范回答」做一轮标准监督训练(见 [微调](fine-tuning.md)),让模型先学会"像助手一样回答",为后续提供稳定的起点。

**第 2 步:训练奖励模型 RM**。让人工对**同一问题的多个回答排序**,用 **Bradley-Terry 模型**把"排序"转成"打分":

$$P(y_w \succ y_l) = \sigma(r_\phi(x, y_w) - r_\phi(x, y_l)), \quad \sigma(z) = \frac{1}{1+e^{-z}}$$

- 目标:获胜回答 $y_w$ 的奖励 $r_\phi$ **尽量高于** $y_l$。RM = SFT 模型去掉输出头、加标量回归头。
- 损失(对数似然):

$$L_{RM} = -\mathbb{E}_{(x, y_w, y_l)}\left[\log \sigma(r_\phi(x, y_w) - r_\phi(x, y_l))\right]$$

**第 3 步:PPO 强化学习**。把 RM 当"教练",用策略梯度优化策略(即 SFT 模型):

- **奖励信号**:$r(x,y) = r_\phi(x,y) - \beta \cdot \mathrm{KL}[\pi_\theta \| \pi_{\mathrm{ref}}]$,减去与参考策略(SFT 模型)的 KL,**防止为了刷分偏离正常语言**;
- **PPO 目标**(忽略 clip 项):$\max_\theta \mathbb{E}[r(x,y)]$,$y \sim \pi_\theta(\cdot|x)$;
- **策略梯度核心公式**:对参数 $\theta$ 的梯度为

$$\nabla_\theta J = \mathbb{E}\left[ r(x,y) \cdot \nabla_\theta \log \pi_\theta(y|x) \right]$$

> 直觉:回答 $y$ 获得的奖励越高,$\log \pi_\theta(y|x)$ 的梯度越"用力"地抬高这个回答的概率;奖励为负则压低。

!!! warning "强化学习为什么难"
    动作空间是词表大小的指数级,每步都要**在线采样+回传奖励**,还要控制方差、维护 KL 约束。7B 模型做 PPO 约需 3~4 倍 SFT 的显存与算力,超参极敏感。

### DPO:把 RL 藏进目标函数

DPO 的洞见:**最优策略的 RL 解可以解析表达**,于是可以绕过奖励模型和 PPO,直接从偏好数据优化:

$$\max_\theta\ \mathbb{E}_{(x, y_w, y_l)}\left[\log \sigma\left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\mathrm{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\mathrm{ref}}(y_l|x)}\right)\right]$$

- 只依赖**隐式奖励** $\beta \log \frac{\pi_\theta(y|x)}{\pi_{\mathrm{ref}}(y|x)}$:策略对某回答比参考策略更"偏爱"(概率比值高),就认为它更受人类偏好。
- 优点:无需 RM、无需在线采样与 PPO 超参,稳定便宜;缺点:无显式奖励,难做"奖励工程"。

### 对齐税(Alignment Tax)

对齐后模型会**轻微变差**:答案啰嗦、多样性降低、推理退化、风格单一。原因是对齐数据把概率质量集中到"偏好回答"上,挤占其他输出。缓解:

- 对齐数据与通用数据**混合**训练;
- KL 系数 $\beta$ 别太大,温和约束;
- 同时盯"能力基准"(MMLU)与"对齐基准",看权衡。

### 对齐 vs SFT:分工对比

| 维度 | SFT | RLHF / DPO |
|---|---|---|
| 数据 | 指令+示范回答 | 回答排序 / 成对偏好 |
| 目标 | 交叉熵,逼近标准答案 | 奖励/偏好,学"哪个更好" |
| RM/RL | 不需要 | RLHF 要,DPO 都不要 |
| 侧重 | 学会"怎么答" | 学会"答什么更受青睐" |
| 产物 | 基础对话能力 | 安全、有用、会拒答 |

## 代码 / 实现

纯 Python 演示**单步策略梯度**:奖励为正抬高对应动作概率,奖励为负则压低;并加入 KL 约束演示"对齐税"式的防跑偏:

```python
import numpy as np

def softmax(z):
    z = z - np.max(z)                    # 数值稳定
    e = np.exp(z)
    return e / e.sum()

def policy_gradient_step(logits, action, reward, lr=0.2):
    """REINFORCE 一步更新:∇log π(a)/∇logits = onehot(a) - π"""
    probs = softmax(logits)
    grad = np.zeros_like(logits)
    grad[action] += 1
    grad -= probs
    return logits + lr * reward * grad

logits = np.array([0.5, 1.5, -0.5])      # 三个候选动作
action = 1
print("初始策略:", softmax(logits).round(3))

# 奖励为正 → 该动作概率上升
pos = policy_gradient_step(logits, action, +1.0)
print("奖励+1后  :", softmax(pos).round(3))

# 奖励为负 → 该动作概率下降
neg = policy_gradient_step(logits, action, -1.0)
print("奖励-1后  :", softmax(neg).round(3))

# 多步迭代:同一动作被反复奖励,概率单调上升(奖励驱动参数更新)
cur = logits.copy()
for step in range(5):
    cur = policy_gradient_step(cur, action, +0.5)
    print(f"step{step+1}: P(action={action}) = {softmax(cur)[action]:.3f}")

# 加入 KL 惩罚:约束新策略不偏离参考策略(ref),防止"刷分跑偏"
def kl_step(logits, ref_probs, action, reward, lr=0.2, beta=1.0):
    probs = softmax(logits)
    grad = np.zeros_like(logits)
    grad[action] += 1
    grad -= probs
    kl_grad = probs - ref_probs          # KL 散度对 logits 的梯度近似
    return logits + lr * (reward * grad - beta * kl_grad)

ref = softmax(np.array([0.5, 1.5, -0.5]))
cur, unreg = logits.copy(), logits.copy()
for _ in range(20):
    cur = kl_step(cur, ref, action, 1.0)
    unreg = policy_gradient_step(unreg, action, 1.0)
print("无约束 20 步后 P(action=1):", softmax(unreg)[1].round(3))
print("带 KL  20 步后 P(action=1):", softmax(cur)[1].round(3),
      "(更保守,即对齐税的代价)")
```

- 前几段验证方向:同一动作**正奖励升概率、负奖励降概率**——正是 RM 分数驱动参数更新的机制。
- 多步迭代展示"奖励驱动"的单调演化。
- 最后演示 KL 惩罚:无约束时策略迅速极端化,加 KL 后更温和——对应 RLHF 的 $\beta$ 与"对齐税"。

**生产实践**:`pip install trl`;PPO 用 `trl.PPOConfig` + `PPOv2`,DPO 用 `DPOConfig` + `DPOTrainer`,数据格式 `{"prompt","chosen","rejected"}`。

## 实践 / 应用

- **先 SFT 再对齐**:直接对未微调模型做偏好优化,效果差且不稳。
- **小模型起步**:7B 上先跑通 DPO(便宜)再考虑 PPO;$\beta$ 通常 0.1~0.5,偏好数据数千到数万条。
- **数据质量**:偏好对必须"明显可区分";用 AI 生成回答让人类排序(Llama 2 的做法)最省钱。
- **对齐税监测**:对齐前后跑同一套能力基准(MMLU、代码、数学),能力掉得明显就调大 $\beta$ 或混入通用数据。
- **前沿方向**:Constitutional AI(RLAIF,让模型按原则自我批评)、SafeRLHF(同时优化有用性与安全)。产品常叠加安全过滤。

## 总结

- 对齐目标:Helpful / Honest / Harmless;预训练给能力,对齐给"听话"。
- RLHF 三步:SFT → RM → PPO(在线强化 + KL 约束)。
- DPO 把隐式奖励藏进目标函数,免去 RM 与 RL,便宜稳定,是当前主流。
- 对齐税 = 过度集中概率导致的能力损失,用 $\beta$ 与数据混合控制。

**下一步**:读 [推理与部署](inference-deployment.md) 学习如何高效跑起对齐好的模型(自回归、KV Cache、量化);想让模型懂私域知识,读 [RAG](rag.md)。

## 延伸阅读

- 站内:[微调](fine-tuning.md)、[推理与部署](inference-deployment.md)、[RAG](rag.md)
- 外部:InstructGPT 论文;DPO 论文;Llama 2 论文;Hugging Face TRL 文档;《Constitutional AI》
