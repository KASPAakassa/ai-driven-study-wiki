# 神经网络基础:感知机、多层感知机与激活函数

> **一句话摘要**:从"一个神经元"讲到"多层感知机",讲透神经网络的前向传播、为什么需要非线性激活函数,并手写一个能跑通前向传播的迷你网络。
>
> **来源**:综合公开资料,参见文末延伸阅读。

## 概念

- **感知机(Perceptron, 1958)**:最早的神经网络单元。输入 `x`,加权求和 `z = Σ wᵢxᵢ + b`,过一个**阶跃函数**输出 0/1。它是个线性分类器——这也注定了它的致命缺陷(见下)。
- **多层感知机(MLP, Multi-Layer Perceptron)**:把感知机堆叠成"输入层 → 隐藏层 → 输出层",层与层**全连接**。这是现代深度学习的基本构件。
- **激活函数(Activation Function)**:神经元输出的非线性变换。它是神经网络"有深度"的关键(见原理)。
- **深度神经网络 = 很多层的 MLP**。今天的大语言模型、CNN、RNN 都是"层"的不同堆叠方式。

## 原理

### 一个神经元做了什么

```
输入 x₁ ──w₁──┐
输入 x₂ ──w₂──┼→ z = Σ wᵢxᵢ + b → 激活 σ(z) → 输出
输入 x₃ ──w₃──┘
```

权重 `w` 表示"这个输入有多重要",偏置 `b` 表示"阈值"。**训练 = 调整 w 和 b**,让输出接近目标。

### 为什么必须非线性:感知机的困局

1958 年感知机很轰动,1969 年 Minsky 证明它**连 XOR(异或)都学不会**——因为 XOR 数据在平面上不是线性可分的,而单层感知机的决策边界只是一条直线。这直接引发了第一次 AI 寒冬。

**解决办法**:加入非线性激活函数,再堆多层。非线性让每一层能表示"弯曲"的决策边界,多层叠加能逼近任意函数(通用近似定理:足够宽的隐藏层可以逼近任意连续函数)。**没有激活函数,多层也只是线性变换的叠加,等价于一层——白堆了。**

### 常用激活函数

| 激活函数 | 公式 | 输出范围 | 特点 | 适用 |
| --- | --- | --- | --- | --- |
| Sigmoid | σ(z)=1/(1+e⁻ᶻ) | (0,1) | 可当概率;但两端梯度≈0(梯度消失) | 输出层二分类 |
| Tanh | (eᶻ−e⁻ᶻ)/(eᶻ+e⁻ᶻ) | (−1,1) | 零中心,比 sigmoid 好 | 隐藏层(旧) |
| ReLU | max(0,z) | [0,+∞) | 计算快、缓解梯度消失;**默认首选** | 隐藏层 |
| Leaky ReLU | max(0.01z, z) | ℝ | 解决 ReLU 死神经元 | 隐藏层 |
| Softmax | eᶻⁱ/Σeᶻʲ | 概率分布 | 多分类输出层 | 输出层多分类 |

!!! tip "ReLU 为什么是默认"
    Sigmoid 在 z 很大/很小时导数趋近 0,反向传播连乘后梯度"消失",深层网络学不动。ReLU 正区间导数恒为 1,梯度传播畅通,且只需一次比较运算——深度学习的"炼丹"利器。

### MLP 前向传播(3 层为例)

设输入 `x`(d 维)、隐藏层 `h`(m 个神经元)、输出 `y`(k 类):

1. 隐藏层加权: `z_h = W₁·x + b₁`(W₁ 是 m×d 矩阵)
2. 隐藏层激活: `h = σ(z_h)`
3. 输出层加权: `z_y = W₂·h + b₂`(W₂ 是 k×m 矩阵)
4. 输出层激活: `ŷ = softmax(z_y)`(分类)或 `ŷ = z_y`(回归)

矩阵写法把"对所有神经元循环"压缩成一次矩阵乘法——GPU 大规模并行的基础。

## 代码 / 实现

用 numpy 手写 MLP 前向传播(训练见下一篇 [反向传播](dl-backpropagation.md)):

```python
import numpy as np

def relu(z):
    return np.maximum(0, z)

def softmax(z):
    e = np.exp(z - z.max(axis=-1, keepdims=True))   # 减最大值防溢出
    return e / e.sum(axis=-1, keepdims=True)

class MLP:
    def __init__(self, d_in, d_hidden, d_out, seed=0):
        rng = np.random.default_rng(seed)
        # 初始化:小随机数打破对称性;Xavier 缩放让信号在前向传播中不爆炸不消失
        self.W1 = rng.normal(0, np.sqrt(2 / d_in), (d_hidden, d_in))
        self.b1 = np.zeros(d_hidden)
        self.W2 = rng.normal(0, np.sqrt(2 / d_hidden), (d_out, d_hidden))
        self.b2 = np.zeros(d_out)

    def forward(self, X):
        self.z1 = X @ self.W1.T + self.b1      # (n, d_hidden)
        self.a1 = relu(self.z1)
        self.z2 = self.a1 @ self.W2.T + self.b2  # (n, d_out)
        return softmax(self.z2)

# 例子:4 维特征 → 3 类
X = np.array([[0.2, 0.9, 0.1, 0.4], [0.8, 0.3, 0.6, 0.2]])
model = MLP(d_in=4, d_hidden=8, d_out=3)
print(model.forward(X).round(3))   # 每行是概率分布,和为 1
```

**关键点**:

- 权重用**小随机数**初始化:全 0 会让所有神经元学成一样的东西(对称性破坏不掉),大随机数会让输出爆炸。
- softmax 输出是概率分布(每行和为 1),配合交叉熵损失使用。

## 实践:设计一个网络要决定什么

1. **结构**:输入维度由特征决定;隐藏层数量与宽度决定表达力(深而窄 vs 浅而宽,通常深度更有用)。
2. **激活函数**:隐藏层默认 ReLU,输出层按任务选(sigmoid 二分类 / softmax 多分类 / 无激活回归)。
3. **从"能跑"开始**:先搭一个能过拟合的小网络验证代码正确,再逐步加大数据、正则化、调参(训练技巧见 [深度学习训练技巧](dl-training-techniques.md))。

## 总结

- 感知机 = 线性分类器,学不会 XOR;MLP = 多层感知机,是深度学习的地基。
- **非线性激活函数是深度的前提**——没有它多层等于一层。
- 默认配置:隐藏层 ReLU,输出层 sigmoid/softmax;权重小随机初始化。
- 前向传播 = 矩阵乘法 + 激活的层层传递;训练 = 下一篇要讲的反向传播。

## 延伸阅读

- 站内:[反向传播与梯度下降](dl-backpropagation.md)、[深度学习训练技巧](dl-training-techniques.md)
- 外部:3Blue1Brown《Neural networks》系列(可视化直觉);CS231n 讲义《Neural Networks Part 1》
