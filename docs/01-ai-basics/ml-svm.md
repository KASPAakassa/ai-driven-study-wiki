# 支持向量机 SVM:最大化间隔的分类器

> **一句话摘要**:支持向量机(SVM)是经典机器学习中最优雅的分类算法之一——它不满足于"把两类分开",而是寻找**间隔最大的分界面**(最大间隔超平面),并用**核技巧**把线性分类器扩展到非线性。理解 SVM 的关键是三个概念:间隔最大化、对偶与支持向量、核函数。
>
> **来源**:综合公开资料(Vapnik 统计学习理论、scikit-learn 官方文档 https://scikit-learn.org/stable/modules/svm.html、CS229 讲义),原始素材由 AI 助手按站内文章模板整理

## 概念

**SVM(Support Vector Machine,支持向量机)** 是一种监督学习分类算法(也可用于回归,即 SVR)。它的核心思想:

> 给定两类样本,SVM 找到**能把两类分开且间隔最大的超平面**——而不是任意一个能分开的平面。

**为什么在乎间隔?** 间隔(margin)是分界面到最近训练样本的距离。间隔越大,对新样本的泛化能力越强(决策边界越"稳");间隔越小,边界越贴着训练点,越容易过拟合。SVM 的出发点正是**结构风险最小化**——不是只追求在训练集上分类正确,而是追求在未知数据上的表现。

**与逻辑回归的区别**:逻辑回归输出概率、用所有样本拟合;SVM 只关注**边界附近的样本**(支持向量),远离边界的样本对模型没有影响。

## 原理:三个核心概念

### 1. 间隔最大化(最大间隔超平面)

线性可分情况下,我们要找超平面 \(w^T x + b = 0\),使得所有样本满足 \(y_i(w^T x_i + b) \ge 1\)(其中 \(y_i \in \{-1,+1\}\))。几何间隔等于 \(2/\|w\|\),所以最大化间隔等价于**最小化 \(\frac{1}{2}\|w\|^2\)**,约束是所有样本都被正确分类且在间隔之外:

$$\min_{w,b} \frac{1}{2}\|w\|^2 \quad \text{s.t.} \quad y_i(w^T x_i + b) \ge 1, \forall i$$

这是一个凸二次规划问题——**有全局最优解,没有局部极小值**,这是 SVM 在数学上的重要优势。

### 2. 软间隔与惩罚参数 C

现实数据通常线性不可分(有噪声、有重叠)。软间隔 SVM 引入松弛变量 \(\xi_i\),允许少量样本违反间隔约束,并在目标里加惩罚:

$$\min_{w,b} \frac{1}{2}\|w\|^2 + C\sum_i \xi_i \quad \text{s.t.} \quad y_i(w^T x_i + b) \ge 1 - \xi_i, \xi_i \ge 0$$

**参数 C 控制"间隔大小 vs 分类错误"的权衡**:

- **C 大**:更严格惩罚误分类 → 间隔小、可能过拟合;
- **C 小**:更容忍误分类 → 间隔大、更平滑、可能欠拟合。

### 3. 支持向量与对偶

拉格朗日对偶后,决策函数只依赖**训练样本的内积**:

$$f(x) = \text{sign}\left(\sum_i \alpha_i y_i \langle x_i, x\rangle + b\right)$$

其中大部分 \(\alpha_i = 0\)——**只有间隔边界上的样本(支持向量)\(\alpha_i > 0\),它们决定了模型**。支持向量的数量通常远小于样本总数,这也是 SVM 训练后模型紧凑、推理快的原因。

### 4. 核技巧:让线性分类器处理非线性

对偶形式里样本只以内积 \(\langle x_i, x\rangle\) 出现。核技巧(Kernel Trick)用核函数 \(K(x_i, x_j)\) 替代内积,隐式地把数据映射到高维空间再做线性分割——**计算复杂度不变,却获得了非线性分类能力**。

常用核:

| 核 | 公式 | 适用场景 |
| --- | --- | --- |
| 线性核 | \(K(x,z) = \langle x, z\rangle\) | 线性可分、高维稀疏数据(如文本) |
| 多项式核 | \(K(x,z) = (\gamma\langle x,z\rangle + r)^d\) | 有阶数关系的特征 |
| **RBF 核(高斯核)** | \(K(x,z) = \exp(-\gamma\|x-z\|^2)\) | **最常用**:能逼近任意形状的边界 |

RBF 核的参数 \(\gamma\) 控制单样本影响半径:**\(\gamma\) 大 → 边界复杂、易过拟合;\(\gamma\) 小 → 边界平滑、易欠拟合**。

## 代码 / 实现:scikit-learn 最小示例

```python
from sklearn import svm
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 生成二分类数据
X, y = make_classification(n_samples=300, n_features=2,
                           n_informative=2, n_redundant=0,
                           random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

# RBF 核 SVM
clf = svm.SVC(kernel='rbf', C=1.0, gamma='scale')
clf.fit(X_train, y_train)

pred = clf.predict(X_test)
print(f"accuracy: {accuracy_score(y_test, pred):.3f}")
print(f"支持向量数: {len(clf.support_vectors_)} / {len(X_train)}")
```

**要点**:

- `C` 和 `gamma` 是两个最重要的超参数,建议用 `GridSearchCV` 调参;
- 特征需要**先标准化**(SVM 对特征尺度敏感);
- 数据量大(>10 万样本)时,线性核 + `LinearSVC` 更快;RBF 核训练较慢。

## 实践 / 应用:何时用 SVM

**适合**:

- 中小规模数据集(<10 万样本);
- 特征维度较高但样本不太多(如文本分类);
- 需要清晰决策边界、可解释的场景;
- 非线性分类但不想用神经网络时。

**不适合 / 已被替代的场景**:

- 大规模数据(神经网络/GBDT 通常更好);
- 特征极多且稀疏(线性核的 Logistic Regression 更简单);
- 深度学习能碾压的图像/语音等任务。

!!! tip "SVM vs 神经网络"
    SVM 在小数据、高维、需要可解释性的场景仍是可靠选择;神经网络在大数据、自动特征学习场景占优。两者不是取代关系——**数据量是主要分水岭**。

## 总结

- **核心思想**:找**间隔最大**的分类超平面,间隔越大泛化越好;
- **两个关键参数**:C(间隔 vs 错误权衡)、gamma(RBF 核的影响半径);
- **支持向量**:只有边界附近的少数样本决定模型,模型紧凑;
- **核技巧**:内积替换为核函数,线性分类器获得非线性能力;
- **适用边界**:中小规模数据、高维、可解释场景;大数据用神经网络/GBDT;
- **下一步**:对比 [决策树与集成](ml-tree-ensemble.md)(树模型在表格数据上通常更强),或进入 [神经网络基础](dl-neural-network-basics.md)。

## 延伸阅读

- scikit-learn SVM 文档:https://scikit-learn.org/stable/modules/svm.html
- 经典教材:Vapnik《The Nature of Statistical Learning Theory》;CS229 讲义(SVM 章节)
- 站内:[线性回归与逻辑回归](ml-linear-models.md)(判别模型对比)、[决策树与集成学习](ml-tree-ensemble.md)(表格数据首选)、[神经网络基础](dl-neural-network-basics.md)(大数据场景)
