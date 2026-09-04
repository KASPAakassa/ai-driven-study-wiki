# 深度学习训练技巧:正则化、优化器与"炼丹"心法

> **一句话摘要**:模型"学不会"和"学过火"怎么办?本文讲透过拟合的诊断与四大正则化手段、优化器选择、学习率调度,并给出一份可直接照做的训练流程清单。
>
> **来源**:综合公开资料,参见文末延伸阅读。

## 概念

- **过拟合是深度学习的第一敌人**:参数量常远超样本量,网络有"背答案"的冲动。训练技巧的很大一部分就是在**对抗过拟合**。
- **正则化(Regularization)**:一系列"给模型施加约束、降低复杂度"的技术,牺牲一点训练精度换取更好的泛化。
- **优化器(Optimizer)**:梯度下降的具体实现(见 [反向传播](dl-backpropagation.md)),选对优化器 = 收敛更快更稳。
- **炼丹(Tuning)**:调整超参数(学习率、层数、dropout 等)让模型表现最好的过程,本质是科学 + 经验的结合。

## 原理

### 第一步:诊断过拟合(永远先看曲线)

训练时记录两条曲线:**训练损失 / 验证损失**。三种典型形态:

```
训练损失↓ 验证损失↓      → 正常,继续训练
训练损失↓ 验证损失先↓后↑ → 过拟合开始,该停或该正则化
两者都不降              → 欠拟合/学习率太小/模型太弱
```

!!! warning "关键纪律"
    只有验证集能告诉你"学得对不对",训练集上的数字永远在自我安慰。**一切调参决策都看验证集,测试集最后只碰一次。**

### 四大正则化手段

**1. L1 / L2 正则化(权重衰减)**

在损失函数上加权重的惩罚项,逼迫参数变小:

- L2(Ridge/weight decay):`L + λ·Σw²` —— 权重趋向**小而分散**;PyTorch 里就是优化器的 `weight_decay` 参数。
- L1(Lasso):`L + λ·Σ|w|` —— 把不重要的权重**压成 0**,自带稀疏与特征选择。

**2. Dropout**

训练时**随机"关闭"一部分神经元**(如 50%),让网络不能依赖任何一个神经元,迫使每个神经元都学到有用的独立特征;预测时全部打开并乘以保留概率。相当于**同时训练了很多个共享参数的子网络再取平均**,是最常用的防过拟合手段。

**3. Early Stopping(早停)**

训练过程中监控验证损失,一旦连续若干个 epoch 不再下降就**提前终止**,取验证集最优时的模型。零成本、永远推荐。

**4. 数据增强(Data Augmentation)**

对输入做不影响语义的变换,白赚更多训练样本:图像翻转/旋转/裁剪/加噪,文本同义词替换,语音变速等。**数据量不够时,这是最有效的正则化。**

### 优化器与学习率

- **Adam**:自适应学习率,默认 `lr=0.001`,几乎开箱即用,是大多数任务的起点。
- **SGD + Momentum**:调好了往往泛化略好于 Adam,但需要更仔细调学习率与动量(0.9)。
- 经验:**先 Adam 快速拿到能跑的结果,再考虑换 SGD 精调冲刺精度**。

**学习率调度(Learning Rate Schedule)**:训练后期学习率太大容易在最优解附近震荡,常用策略:

- **Step decay**:每 N 个 epoch 学习率乘 0.1;
- **Cosine annealing**:按余弦曲线从大平滑降到小;
- **Warmup**:前几百步从小学习率线性升到目标值(大模型训练标配,稳定早期梯度)。

### BatchNorm(批归一化)

对每个 batch 的激活做标准化(减均值除方差)再缩放平移。效果:加速收敛、允许更大学习率、对初始化不敏感、有轻微正则化作用。**现代网络的隐藏层几乎默认带 BatchNorm**(或 LayerNorm)。

## 代码 / 实现

用纯 Python 演示 Dropout 与 L2 的**核心计算逻辑**(完整训练框架见 PyTorch 示例):

```python
import numpy as np

def dropout_forward(a, p_drop=0.5, training=True):
    """p_drop: 关闭比例。训练时随机 mask,推理时缩放回原尺度"""
    if not training:
        return a
    mask = np.random.binomial(1, 1 - p_drop, size=a.shape) / (1 - p_drop)
    return a * mask

# 演示:同一批激活,训练时部分被清零,推理时原样输出
a = np.array([1.0, 2.0, 3.0, 4.0])
print("训练:", dropout_forward(a, 0.5, True))    # 约一半变 0,其余×2
print("推理:", dropout_forward(a, 0.5, False))   # 原样

def l2_grad(w, lam):
    """L2 正则的梯度贡献: 2·λ·w,加回主梯度一起更新"""
    return 2 * lam * w

w = np.array([0.5, -1.0, 2.0])
print("L2 梯度:", l2_grad(w, 0.01))              # 每次更新都在"拉小"权重
```

**PyTorch 中的标准训练循环**(需要 `pip install torch`):

```python
import torch, torch.nn as nn

model = nn.Sequential(
    nn.Linear(784, 256), nn.ReLU(), nn.Dropout(0.5),
    nn.Linear(256, 10),
)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
loss_fn = nn.CrossEntropyLoss()

for epoch in range(30):
    model.train()                      # 开 Dropout
    for xb, yb in train_loader:
        optimizer.zero_grad()
        loss = loss_fn(model(xb), yb)
        loss.backward()
        optimizer.step()
    # 每个 epoch 后在验证集上评估,决定是否 early stop
    model.eval()                       # 关 Dropout
    val_loss = evaluate(model, val_loader)
    if not improved(val_loss):
        break                          # early stopping
```

**关键点**:`train()`/`eval()` 切换控制 Dropout 与 BatchNorm 的行为——**忘切换是新手最常见的 bug**(训练时开、推理时忘了关,结果随机抖动)。

## 实践:一份可直接照做的训练清单

1. **搭建能过拟合的小网络**:先用小网络 + 小数据,确认它能**过拟合**(训练损失趋近 0)——这一步验证代码正确。
2. **加数据与数据增强**:能加数据是性价比最高的正则化。
3. **默认配置起步**:Adam(lr=1e-3)+ weight_decay=1e-4 + Dropout(0.2~0.5)+ ReLU + BatchNorm。
4. **盯验证曲线调参**:学习率(10 倍网格:1e-4~1e-1)→ 深度/宽度 → Dropout 比例 → 正则强度。每次只改一个变量。
5. **早停**:验证损失不再下降就停,取最优权重。
6. **学习率调度**:收敛后期用 cosine/step decay 冲精度。
7. **最后**:测试集只评估一次,记录超参数与结果,写进 [实战章节](../04-practice/index.md)。

## 总结

- 先诊断再治疗:**训练/验证损失曲线**决定一切。
- 四大正则化:L1/L2、Dropout、Early Stopping、数据增强;默认组合 weight_decay + Dropout + 早停。
- 优化器:Adam 起步(lr=1e-3),SGD+Momentum 精调;学习率后期衰减。
- 纪律:验证集调参、测试集只用一次、`train()/eval()` 别忘切换。

## 延伸阅读

- 站内:[反向传播与梯度下降](dl-backpropagation.md)、[神经网络基础](dl-neural-network-basics.md)
- 外部:CS231n 讲义《Optimization》《Regularization》;论文《Dropout: A Simple Way to Prevent Neural Networks from Overfitting》(Srivastava et al., 2014)
