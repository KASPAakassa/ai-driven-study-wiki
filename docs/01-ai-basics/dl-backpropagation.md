# 反向传播与梯度下降:让网络学会"调参"的引擎

> **一句话摘要**:反向传播(Backpropagation)是深度学习训练的核心算法——用链式法则高效计算损失对每个参数的梯度,配合梯度下降更新参数。本文从零推导并手写一个完整可训练的 2 层网络。
>
> **来源**:综合公开资料,参见文末延伸阅读。

## 概念

- **问题**:训练网络 = 最小化损失函数 `L`。损失是"预测与答案差多远",参数是网络里的所有 `w`、`b`。怎么知道**每个参数该往哪个方向调、调多少**?答案:算梯度 `∂L/∂w`。
- **梯度下降(Gradient Descent)**:`w ← w − lr · ∂L/∂w`,沿损失下降最快的方向更新。这个思路在 [线性回归](ml-linear-models.md) 里已经见过,神经网络只是参数量从几个变成几百万个。
- **反向传播(Backpropagation)**:高效计算这百万个梯度的算法。核心是**链式法则**:从输出层开始,把"误差对输出的梯度"逐层往回传,每一层只做局部计算。
- **为什么不用"数值梯度"**:也可以 `∂L/∂w ≈ (L(w+ε) − L(w))/ε` 暴力算,但每个参数要两次前向传播,百万参数就百万次——慢几个数量级。反向传播一次前向 + 一次反向就拿到**所有**梯度。

## 原理

### 链式法则:误差如何"流"回每一层

以 2 层网络(输入 x → 隐藏层 h → 输出 ŷ)为例,前向传播是:

```
x → z₁ = W₁x + b₁ → h = σ(z₁) → z₂ = W₂h + b₂ → ŷ → L(ŷ, y)
```

损失对中间量的偏导用链式法则逐层展开(从后往前):

$$
\frac{\partial L}{\partial W_2} = \underbrace{\frac{\partial L}{\partial \hat y} \cdot \frac{\partial \hat y}{\partial z_2}}_{=\delta_2} \cdot \frac{\partial z_2}{\partial W_2}
$$

记输出层误差信号 `δ₂ = ∂L/∂z₂`。对隐藏层,误差信号继续往回传:

$$
\delta_1 = \delta_2 \cdot W_2 \odot \sigma'(z_1), \qquad \frac{\partial L}{\partial W_1} = \delta_1 \cdot x^\top
$$

**直觉**:输出层的"错误量" δ₂ 经过 W₂ 反着传回隐藏层,再乘以激活函数的导数(ReLU 的导数是 0/1,sigmoid 的导数小 → 解释梯度消失),得到隐藏层每个神经元的"应负责任",最后与输入相乘得到梯度。**每一层的梯度只依赖本层的前向缓存(z、a)和上一层传回来的 δ。**

### 梯度下降的三种粒度

| 变体 | 每次更新用多少样本 | 特点 |
| --- | --- | --- |
| 批量梯度下降(BGD) | 全部 | 稳定但慢,内存大 |
| 随机梯度下降(SGD) | 1 个 | 快但噪声大、震荡 |
| 小批量 SGD(Mini-batch, 默认) | 32/64/128 个 | 平衡,GPU 高效利用 |

### 梯度下降的改良(优化器)

- **Momentum(动量)**:累积历史梯度方向,加速收敛、抑制震荡。
- **AdaGrad / RMSProp**:按参数历史梯度幅度自动缩放学习率,稀疏特征大更新、频繁特征小更新。
- **Adam(最常用)**:Momentum + RMSProp 的结合,自适应学习率,几乎免调参,是深度学习默认优化器。

## 代码 / 实现

用 numpy 完整实现 2 层网络的训练(前向 + 反向 + 更新),解决一个可解释的 XOR 问题——感知机学不会的那个:

```python
import numpy as np

def relu(z):            return np.maximum(0, z)
def relu_deriv(z):      return (z > 0).astype(float)
def sigmoid(z):         return 1 / (1 + np.exp(-z))

# XOR 数据:输入 4 个组合,标签 异或结果
X = np.array([[0,0],[0,1],[1,0],[1,1]], dtype=float)
y = np.array([0,1,1,0]).reshape(-1,1)

rng = np.random.default_rng(0)
W1 = rng.normal(0, 1, (8,2)); b1 = np.zeros((1,8))   # 隐藏层 8 个神经元
W2 = rng.normal(0, 1, (1,8)); b2 = np.zeros((1,1))

lr = 0.5
for epoch in range(10000):
    # ---- 前向 ----
    z1 = X @ W1.T + b1
    a1 = relu(z1)
    z2 = a1 @ W2.T + b2
    a2 = sigmoid(z2)
    loss = -np.mean(y * np.log(a2 + 1e-9) + (1-y) * np.log(1 - a2 + 1e-9))

    # ---- 反向传播 ----
    dL_da2 = (a2 - y) / len(X)          # 交叉熵对 sigmoid 输出的梯度
    dL_dz2 = dL_da2                     # sigmoid 的导数被交叉熵抵消(数学巧合但真实)
    dL_dW2 = dL_dz2.T @ a1
    dL_db2 = dL_dz2.sum(axis=0, keepdims=True)

    dL_da1 = dL_dz2 @ W2
    dL_dz1 = dL_da1 * relu_deriv(z1)    # 链式法则:误差 × 激活导数
    dL_dW1 = dL_dz1.T @ X
    dL_db1 = dL_dz1.sum(axis=0, keepdims=True)

    # ---- 参数更新 ----
    W2 -= lr * dL_dW2; b2 -= lr * dL_db2
    W1 -= lr * dL_dW1; b1 -= lr * dL_db1

    if epoch % 2000 == 0:
        print(f"epoch {epoch:5d}  loss = {loss:.4f}")

print("预测:", np.round(a2.ravel(), 3))   # 应接近 [0, 1, 1, 0]
```

**运行结果**:损失从 0.87 持续降到 ~0.0001,最终预测 `[0, 1, 1, 0]`——**两层网络 + 非线性激活轻松解决 XOR**,而单层感知机做不到。这就是"深度"带来的质变。

**关键点**:

- 反向传播三行核心:`dL_dz2 → dL_dW2 / dL_da1 → dL_dz1(=δ₁)→ dL_dW1`,严格对应推导中的 δ₂、δ₁。
- 交叉熵 + sigmoid 的组合让输出层梯度恰好是 `(a2 − y)`,简洁漂亮;隐藏层则必须乘 `relu_deriv(z1)`——这就是 ReLU 不消失、sigmoid 会消失的原因。
- 实际工程中你不会手写反向传播(PyTorch 的 `loss.backward()` 自动完成),但**看懂这三行,你就懂了所有深度学习训练的本质**。

## 实践:训练中的工程要点

1. **验证梯度正确**:实现初期用数值梯度 `(L(w+ε)−L(w−ε))/2ε` 对比手写梯度,误差 < 1e-6 才算对(本网络可自行验证)。
2. **学习率是头号超参数**:太大发散,太小龟速。常见策略:从 0.01~0.001 起步,用 Adam 默认 lr=0.001。
3. **loss 不下降排查顺序**:学习率 → 数据归一化 → 网络初始化 → 梯度实现 → 数据/标签对齐。
4. **监控**训练/验证曲线,而不是只看最终精度(见 [训练技巧](dl-training-techniques.md))。

## 总结

- 反向传播 = 链式法则,从输出层把误差信号逐层传回,一次前向 + 一次反向算出全部梯度。
- 梯度下降(及其改良 Adam)负责用梯度更新参数;两者合起来是训练引擎。
- 交叉熵+sigmoid 梯度是 `(a₂−y)`;隐藏层要乘激活导数,ReLU 因此胜出。
- 手写一遍 2 层 XOR 网络,胜过读十篇教程。

## 延伸阅读

- 站内:[神经网络基础](dl-neural-network-basics.md)、[深度学习训练技巧](dl-training-techniques.md)
- 外部:3Blue1Brown《But what is a gradient?》与《Backpropagation calculus》两集;CS231n 讲义《Backpropagation》
