# 用 numpy 从零实现神经网络:三分类多层感知机实战

> **一句话摘要**:不依赖任何深度学习框架,用 numpy 手写一个「输入 2 维 → 隐藏层(tanh)→ softmax 三分类」的多层感知机,跑通前向传播、反向传播、训练循环与评估,并对比手写与框架的差异。
>
> **来源**:综合公开资料(CS231n、Karpathy micrograd),代码为本项目自研验证。

## 概念

- **多层感知机(MLP)**:由「输入层 → 一个或多个隐藏层 → 输出层」堆叠而成的神经网络。每层做一次线性变换 + 非线性激活,叠加后即可逼近任意连续函数(通用近似定理)。
- **为什么还要手写一遍?** 框架(torch/tf)把反向传播封装成了魔法,报错时无从下手。手写一遍,你会真正理解每个 `loss.backward()` 背后发生了什么——这也是[反向传播章节](../01-ai-basics/dl-backpropagation.md)的实战延伸。
- **softmax + 交叉熵**:多分类的标准输出层。softmax 把 logits 压成概率分布(和为 1),交叉熵衡量预测分布与真实 one-hot 分布的距离。二者搭配的梯度形式极简:`dz = p - y`(预测概率减真实标签),这就是"好调"的秘诀。

## 原理

### 前向传播(预测路径)

```
x(2维) --W1,b1--> z1 --tanh--> a1 --W2,b2--> z2 --softmax--> p(3维概率)
```

- 隐藏层用 **tanh** 激活:`a1 = tanh(X @ W1 + b1)`,输出范围 (-1, 1),中心对称、梯度比 sigmoid 更平稳。
- 输出层用 **softmax**:`p_i = exp(z_i) / Σ exp(z_j)`,得到"属于每一类的概率"。
- 预测类别 = `argmax(p)`。

### 反向传播(误差回传)

基于链式法则,从输出层向输入层逐层求梯度:

| 符号 | 含义 | 梯度公式 |
|---|---|---|
| `dz2` | 输出层误差 | `p - Y`(softmax+交叉熵的简并形式) |
| `dW2` | 输出层权重梯度 | `a1ᵀ @ dz2 / m` |
| `dz1` | 隐藏层误差 | `(dz2 @ W2ᵀ) * (1 - a1²)`(tanh 导数为 `1-tanh²`) |
| `dW1` | 隐藏层权重梯度 | `Xᵀ @ dz1 / m` |

> 常见误解:反向传播不是"把梯度存起来",而是**同一套链式法则的工程化**——每层只需要知道"上游误差 × 本层局部导数",即可算出对参数的梯度。

### 数值稳定性

softmax 直接算 `exp(z)` 会溢出(如 `exp(1000) = inf`)。标准做法先减去最大值:`exp(z - z.max())`,结果不变但保证不溢出。

## 代码 / 实现

> 环境:`python3` + `numpy`。无需 GPU,几秒即可跑完。完整脚本保存为 `mlp_iris.py` 直接运行。

```python
import numpy as np

# ---------- 1. 数据:模拟三分类鸢尾花(sepal, petal) ----------
rng = np.random.default_rng(0)
means = np.array([[5.0, 3.4], [5.9, 4.2], [6.6, 5.6]])   # 3 类中心
X = np.vstack([rng.normal(m, 0.35, (50, 2)) for m in means])
y = np.repeat([0, 1, 2], 50)

# 划分 + 标准化(只 fit 训练集)
idx = rng.permutation(150)
tr, te = idx[:120], idx[120:]
mean, std = X[tr].mean(axis=0), X[tr].std(axis=0)
Xtr = (X[tr] - mean) / std
Xte = (X[te] - mean) / std
Y = np.eye(3)[y[tr]]                                    # one-hot 标签

# ---------- 2. 前向与反向的核心函数 ----------
def softmax(z):
    e = np.exp(z - z.max(axis=1, keepdims=True))        # 数值稳定
    return e / e.sum(axis=1, keepdims=True)

# 初始化:小随机权重 + 零偏置
rng2 = np.random.default_rng(1)
W1 = rng2.normal(0, 0.5, (2, 8)); b1 = np.zeros(8)      # 2 -> 8
W2 = rng2.normal(0, 0.5, (8, 3)); b2 = np.zeros(3)      # 8 -> 3

losses = []
lr = 0.3
for epoch in range(2000):
    # ---- 前向 ----
    a1 = np.tanh(Xtr @ W1 + b1)                          # 隐藏层
    p = softmax(a1 @ W2 + b2)                            # 输出概率
    loss = -np.mean(np.sum(Y * np.log(p + 1e-12), axis=1))
    losses.append(loss)
    # ---- 反向传播 ----
    dz2 = p - Y                                          # 输出层误差
    dW2 = a1.T @ dz2 / len(Xtr); db2 = dz2.mean(axis=0)
    dz1 = (dz2 @ W2.T) * (1 - a1 ** 2)                   # tanh 链式
    dW1 = Xtr.T @ dz1 / len(Xtr); db1 = dz1.mean(axis=0)
    # ---- 更新(梯度下降) ----
    W1 -= lr * dW1; b1 -= lr * db1
    W2 -= lr * dW2; b2 -= lr * db2

# ---------- 3. 评估:准确率 ----------
def predict(X):
    a1 = np.tanh(X @ W1 + b1)
    return softmax(a1 @ W2 + b2).argmax(axis=1)

acc_tr = (predict(Xtr) == y[tr]).mean()
acc_te = (predict(Xte) == y[te]).mean()
print(f"训练集准确率 = {acc_tr*100:.1f}%   测试集准确率 = {acc_te*100:.1f}%")
print(f"loss: {losses[0]:.3f} -> {losses[-1]:.4f}")

# ---------- 4. 可视化损失曲线(无 matplotlib 的 ASCII 版) ----------
def plot_curve(losses, width=60, height=12):
    lo, hi = min(losses), max(losses)
    step = (hi - lo) / (height - 1) if hi > lo else 1
    rows = [[" "] * len(losses) for _ in range(height)]
    for i, v in enumerate(losses):
        r = min(max(int(round((hi - v) / step)), 0), height - 1)
        rows[r][i] = "#"
    return "\n".join("".join(row) for row in rows)

print("loss 曲线(每 50 epoch 一个点,行越高=loss 越大):")
print(plot_curve(losses[::50]))
```

**预期输出**:训练集准确率 ≈ 95~96%,测试集准确率 ≈ 100%,loss 从约 1.05 下降到约 0.10,ASCII 曲线显示"第一点最高、随后一路下降到底部"的收敛形态。

!!! tip "终端显示不下曲线?"
    把 `plot_curve(losses[::50])` 改成 `plot_curve(losses[::100])` 减少点数;若装了 matplotlib,直接用 `plt.plot(losses)` 两行替代 ASCII 版。

**运行说明**:若有 matplotlib,可用两行替换 ASCII 版:`import matplotlib.pyplot as plt; plt.plot(losses); plt.show()`(需 `pip install matplotlib`)。

## 实践 / 应用

### 手写 vs 框架的差异

| 维度 | 手写 numpy | 深度学习框架(torch/tf) |
|---|---|---|
| 反向传播 | 手写链式法则,易错但透明 | `loss.backward()` 自动微分 |
| GPU / 大数据 | 不适用 | 核心优势 |
| 调试 | 报错直接暴露在数学公式里 | 报错藏在封装层,需经验 |
| 扩展性 | 加一层要重写一遍 | 改一行配置 |
| 学习价值 | 极高 | 高 |

### 从这份代码出发的延伸方向

1. **加层加深**:把隐藏层堆成 `2→8→8→3`,前向多写一段、反向多一次链式传播——理解"深度"只是重复同一模式。
2. **换优化器**:引入 momentum(`v = βv + grad; w -= lr·v`)或 Adam,收敛更快更稳(见[训练技巧章节](../01-ai-basics/dl-training-techniques.md))。
3. **正则化**:加 L2 正则或 Dropout(训练时随机丢弃隐藏层神经元)。
4. **batch 化**:把数据按小批量(batch)切分训练,噪声梯度 + 内存可控。
5. **验证反向传播**:用数值梯度检查(见[排查清单](practice-debug-checklist.md)的梯度检查片段)验证每个 `dW` 是否正确。

### 关键坑

- 初始化权重全 0 → 隐藏层神经元完全对称,永远学不动;
- 忘记减去 `z.max()` → `exp` 溢出成 NaN;
- 学习率过大 → loss 震荡甚至发散;过小 → 收敛极慢;
- 用验证集调超参、测试集只评一次,避免"把测试集调聪明"。

## 总结

- MLP = 线性变换 + 非线性激活的堆叠;softmax+交叉熵让多分类梯度退化为 `p - y`。
- 手写一遍前向/反向/更新三件套,才算真正掌握神经网络的底层机制。
- 数据标准化、固定随机种子、数值稳定 softmax,是让训练可复现且稳定的三大基本功。
- ASCII 损失曲线让"无图形环境"也能观察收敛过程。
- 下一步:换用框架复现同一模型做性能对比,或加一层做"深度"的直观体验。

## 延伸阅读

- 站内:[神经网络基础](../01-ai-basics/dl-neural-network-basics.md)、[反向传播与梯度下降](../01-ai-basics/dl-backpropagation.md)、[训练技巧与炼丹心法](../01-ai-basics/dl-training-techniques.md)
- 外部:CS231n 课程笔记(Backpropagation 一节);Karpathy 的 micrograd(约 150 行自动微分实现)
