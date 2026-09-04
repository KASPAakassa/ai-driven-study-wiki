# 聚类:无监督学习的核心——把数据自然分组

> **一句话摘要**:聚类(Clustering)是无监督学习的代表任务——**没有标签**,让算法自己发现数据的内在结构,把相似样本归为一组。核心问题不是"分得对"(没有标准答案),而是"分组是否有意义"。本文覆盖 K-Means(最常用)、层次聚类、DBSCAN(密度聚类)三大类算法,以及"如何选 K"与"如何评估聚类质量"。
>
> **来源**:综合公开资料(scikit-learn 官方文档 https://scikit-learn.org/stable/modules/clustering.html、CS229 讲义),由 AI 助手按站内模板整理

## 概念

**聚类(Clustering)** 是把数据集划分成若干个组(簇,cluster),使得**同一簇内样本相似、不同簇间样本差异大**。它是无监督学习:训练数据**没有标签**,算法自己发现结构。

**聚类 vs 分类**:

| | 分类(监督) | 聚类(无监督) |
| --- | --- | --- |
| 是否有标签 | 有 | 无 |
| 目标 | 学习标签到特征的映射 | 发现数据内在分组 |
| 评价 | 准确率等(有标准答案) | 簇内紧凑度/簇间分离度(无标准答案) |

**典型应用**:客户分群(营销)、图像分割(像素聚类)、文档主题分组、异常检测(离群点单独成簇/不成簇)、数据探索的预处理步骤。

## 原理:三大类聚类算法

### 1. K-Means(最常用、最直观)

**思想**:预先指定簇数 K,迭代地"分配样本到最近质心 → 更新质心为簇内均值",直到收敛。

**算法步骤**:

1. 随机初始化 K 个质心;
2. **分配**:每个样本归入最近质心所在的簇;
3. **更新**:把每个质心移到其簇内所有样本的均值位置;
4. 重复 2-3 直到质心不再变化(或达到最大迭代次数)。

**优化目标**:最小化簇内平方和(inertia,惯性)——\(\sum_{i}\min_k \|x_i - \mu_k\|^2\)。

**特点与坑**:

- 简单、快(O(n·k·iterations))、适合大规模数据;
- **必须指定 K**(见下文"如何选 K");
- **对初始质心敏感**:可能收敛到局部最优,用 K-Means++ 初始化可缓解;
- 对**离群点敏感**(均值会被拉偏);
- 假设簇是**凸的、大小相近**的——球形簇表现好,任意形状不行。

### 2. 层次聚类(Hierarchical Clustering)

**思想**:不要求预先指定 K,而是构建一棵**聚类树(树状图,dendrogram)**,从中按需切出任意数量的簇。

- **凝聚式(自底向上)**:每个样本自成一簇,每次合并最近的两簇,直到只剩一簇;
- **分裂式(自顶向下)**:所有样本一簇,每次分裂最不紧凑的簇。

**簇间距离(链接准则)**:single(最近点)、complete(最远点)、average(平均)、ward(方差增量,常用)。

**特点**:不需要 K、可看到层次关系、但计算量大(O(n²)),适合小数据集。

### 3. DBSCAN(密度聚类)

**思想**:基于密度——把**密度相连**的区域聚成一簇,把低密度区域的点标记为**噪声**。

**两个参数**:

- **eps(ε)**:邻域半径;
- **min_samples**:成为核心点所需的最少邻居数。

**特点**:

- **不需要指定 K**;
- 能发现**任意形状**的簇;
- **自带离群点检测**(噪声点即离群点);
- 对 eps 参数敏感、样本密度差异大时效果差。

## 代码 / 实现:三种算法最小示例

```python
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.datasets import make_blobs
import numpy as np

# 生成 3 簇数据
X, _ = make_blobs(n_samples=300, centers=3, cluster_std=0.8, random_state=42)

# 1. K-Means(指定 K=3)
kmeans = KMeans(n_clusters=3, init='k-means++', n_init=10, random_state=42)
labels_km = kmeans.fit_predict(X)

# 2. 层次聚类(ward 链接)
agg = AgglomerativeClustering(n_clusters=3, linkage='ward')
labels_agg = agg.fit_predict(X)

# 3. DBSCAN(密度聚类,自动发现簇+噪声)
dbscan = DBSCAN(eps=1.2, min_samples=5)
labels_db = dbscan.fit_predict(X)   # 噪声点标签为 -1
print(f"DBSCAN 发现簇数: {len(set(labels_db)) - (1 if -1 in labels_db else 0)}")
```

## 实践 / 应用:如何选 K 与评估质量

### 如何选 K(对 K-Means)

1. **肘部法(Elbow Method)**:画 inertia 随 K 变化的曲线,找"拐点"(再增加 K 收益骤减处);
2. **轮廓系数(Silhouette Score)**:衡量每个样本"与自身簇的紧凑度 vs 与最近其他簇的分离度",取值 [-1,1],**越高越好**;对不同 K 计算,取最高者;
3. 结合业务:分群结果是否可解释、可落地。

```python
from sklearn.metrics import silhouette_score

scores = {}
for k in range(2, 8):
    km = KMeans(n_clusters=k, random_state=42).fit(X)
    scores[k] = silhouette_score(X, km.labels_)
best_k = max(scores, key=scores.get)
print(f"轮廓系数最优 K = {best_k}")
```

### 评估聚类质量(无标签时的"好"怎么定义)

- **内部指标**(无需标签):轮廓系数、inertia、Davies-Bouldin 指数——衡量紧凑度与分离度;
- **外部指标**(有真实标签可对比):调整兰德指数 ARI、归一化互信息 NMI——衡量与真实分组的一致性;
- **最重要的评估是业务验证**:分出来的组是否在业务上有意义、可采取不同策略。

### 工程要点

- **特征标准化**几乎总是必要(距离计算对尺度敏感);
- 数据量大用 K-Means/MiniBatchKMeans;形状任意用 DBSCAN;要层次关系用层次聚类;
- 聚类结果可作为**特征工程**的一部分(给样本打"簇标签"作为新特征)。

## 总结

- **本质**:无监督发现数据内在分组,没有标准答案,分组是否有意义是关键;
- **三大算法**:K-Means(快、需指定 K、球形簇)、层次聚类(不需 K、有树状图、慢)、DBSCAN(任意形状、自带噪声检测、不需 K);
- **选 K**:肘部法 + 轮廓系数 + 业务判断;
- **评估**:内部指标(紧凑/分离)+ 外部指标(ARI/NMI)+ 业务验证;
- **下一步**:聚类常用于特征工程与探索,之后可进入 [特征工程与模型评估](ml-feature-engineering.md) 或 [SVM](ml-svm.md) 等分类算法。

## 延伸阅读

- scikit-learn 聚类文档:https://scikit-learn.org/stable/modules/clustering.html
- 站内:[学习范式与核心概念](ml-learning-paradigms.md)(无监督学习定位)、[特征工程与模型评估](ml-feature-engineering.md)、[线性回归与逻辑回归](ml-linear-models.md)
