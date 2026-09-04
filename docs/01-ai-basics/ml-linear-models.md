# 线性回归与逻辑回归:从零手写一个可用的模型

> **一句话摘要**:线性回归(预测连续值)与逻辑回归(分类)是机器学习的地基。用纯 Python 手写两者,彻底搞懂"损失函数 + 梯度下降"如何工作。
>
> **来源**:综合公开资料,参见文末延伸阅读。

## 概念

- **线性回归(Linear Regression)**:假设目标 `y` 与特征 `x` 之间是线性关系 `ŷ = w·x + b`,用于**回归**任务(预测连续值:房价、温度、销量)。
- **逻辑回归(Logistic Regression)**:名字带"回归"但实际是**分类**算法。在线性组合外面套一个 **sigmoid 函数**,把输出压到 (0,1) 之间作为概率,用于二分类(垃圾邮件、患病与否)。
- 两者都是**线性模型**的代表:决策边界是"直线/超平面",简单、可解释、是无数复杂模型的基石。

## 原理

### 线性回归:最小二乘

模型 `ŷ = w·x + b`,损失函数用**均方误差(MSE)**:

$$
L(w,b) = \frac{1}{n}\sum_{i=1}^{n}(y_i - \hat y_i)^2
$$

梯度下降更新参数(学习率 `lr`,通常记为 `α`):

$$
w \leftarrow w - \alpha \cdot \frac{\partial L}{\partial w}, \quad b \leftarrow b - \alpha \cdot \frac{\partial L}{\partial b}
$$

其中对单个样本的偏导为:

$$
\frac{\partial L}{\partial w} = -2(y-\hat y)x, \quad \frac{\partial L}{\partial b} = -2(y-\hat y)
$$

> 直观理解:预测偏高(`ŷ > y`)时,`y-ŷ < 0`,梯度把 `w` 往小的方向推——**每次都在"错误的反方向"迈一小步**。

### 逻辑回归:最大似然

把线性输出过 sigmoid 变成概率:

$$
p = \sigma(z) = \frac{1}{1+e^{-z}}, \quad z = w·x + b
$$

损失函数用**交叉熵(对数损失)**,而不是 MSE(因为 MSE 在 sigmoid 上会产生很多局部平坦区,难以优化):

$$
L = -\frac{1}{n}\sum_{i=1}^{n}\big[ y_i \log p_i + (1-y_i)\log(1-p_i) \big]
$$

神奇的是,交叉熵对 `w` 的梯度形式与线性回归几乎一样:`∂L/∂w = (p - y)·x`——这就是为什么逻辑回归训练起来又快又稳。

### 关键工程细节

- **特征缩放(标准化)**:不同特征量纲差太多(面积 100 vs 房间数 3),梯度下降会来回震荡、收敛极慢。标准做法:`x' = (x - mean) / std`,让特征均值 0、标准差 1。
- **正则化**:线性模型容易在特征多时过拟合,加惩罚项:Ridge(L2,系数趋向小但不为 0)、Lasso(L1,会把不重要的系数**压成 0**,自带特征选择)。

## 代码 / 实现

纯 Python + 手写梯度下降,不依赖任何 ML 库:

```python
import math, random

def standardize(xs):                      # 特征标准化
    mean = sum(xs) / len(xs)
    std  = math.sqrt(sum((x - mean)**2 for x in xs) / len(xs))
    return [(x - mean) / std for x in xs], mean, std

def train_linear(X, y, lr=0.1, epochs=200):
    w, b = 0.0, 0.0
    for _ in range(epochs):
        for xi, yi in zip(X, y):
            pred = w * xi + b
            w -= lr * (-2 * (yi - pred) * xi)   # 梯度下降
            b -= lr * (-2 * (yi - pred))
    return w, b

def sigmoid(z):
    return 1 / (1 + math.exp(-z))

def train_logistic(X, y, lr=0.1, epochs=200):
    w, b = 0.0, 0.0
    for _ in range(epochs):
        for xi, yi in zip(X, y):
            p = sigmoid(w * xi + b)
            w -= lr * ((p - yi) * xi)           # 交叉熵梯度 (p-y)*x
            b -= lr * (p - yi)
    return w, b

# 数据:面积(㎡)→ 房价(万),先标准化再训练
X = [50, 80, 120, 200, 60, 150]
y = [120, 200, 300, 520, 140, 380]
Xs, mean, std = standardize(X)
w, b = train_linear(Xs, y)
new = (95 - mean) / std                        # 预测 95㎡ 的房价
print(f"线性回归: 房价 ≈ {w * new + b:.1f} 万")

# 数据:时长(小时)→ 是否及格(0/1)
X2 = [1, 2, 3, 4, 5, 6, 7, 8]
y2 = [0, 0, 0, 0, 1, 1, 1, 1]
X2s, m2, s2 = standardize(X2)
wl, bl = train_logistic(X2s, y2)
p = sigmoid(wl * ((5.5 - m2) / s2) + bl)
print(f"逻辑回归: 学 5.5 小时及格的概率 ≈ {p:.2f}")
```

**关键点**:

- 两段代码共享同一个骨架:**前向预测 → 算梯度 → 沿负梯度更新**,这就是上一篇文章说的"ML 统一闭环"。
- 标准化让学习率可以设得较大(0.1)而不会发散——**不做标准化的线性模型几乎没法用梯度下降训练**。

## 实践:应用与注意点

- **适用场景**:需要可解释性的基线模型、特征维度不高、关系近似线性时。几乎所有 Kaggle 竞赛都会先用逻辑回归/线性回归打基线。
- **优缺点**:训练极快、可解释(权重就是"特征的影响方向与大小")、对噪声鲁棒;但表达力有限,无法处理复杂非线性关系(那是树模型和神经网络的主场)。
- **常见坑**:
  - 忘记特征缩放 → 收敛慢或发散;
  - 类别不均衡 → 逻辑回归会偏向多数类,可用 class_weight 或换指标;
  - 特征高度共线 → 权重不稳定,考虑 L2 正则化。

## 总结

- 线性回归预测连续值,逻辑回归通过 sigmoid + 交叉熵做分类;两者都是线性模型。
- 核心公式:线性回归用 MSE 梯度 `-2(y-ŷ)x`;逻辑回归用交叉熵梯度 `(p-y)x`。
- 特征标准化是线性模型能顺利训练的前提;Ridge/Lasso 解决过拟合与特征选择。
- 手写一遍比看十遍都管用——它们是一切复杂模型的起点。

## 延伸阅读

- 站内:[学习范式与核心概念](ml-learning-paradigms.md)、[决策树与集成学习](ml-tree-ensemble.md)
- 外部:Andrew Ng 机器学习课程 Week 2(线性回归)、Week 3(逻辑回归);scikit-learn 文档 `linear_model` 模块
