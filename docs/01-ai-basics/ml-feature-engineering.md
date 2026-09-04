# 特征工程与模型评估:从"能跑"到"可信"

> **一句话摘要**:同样的算法,特征工程做得好与不好,效果可以天差地别——"垃圾进,垃圾出"。特征工程是把原始数据变成模型能高效学习的表示:清洗、变换、编码、选择;模型评估则是回答"模型到底好不好、能不能信":划分数据集、选指标、交叉验证、防过拟合与数据泄漏。这两件事决定了 ML 项目能否落地。
>
> **来源**:综合公开资料(scikit-learn 官方文档 https://scikit-learn.org/stable/、Kaggle 特征工程实践),由 AI 助手按站内模板整理

## 概念

**特征工程(Feature Engineering)** = 从原始数据中构造、变换、选择特征,让模型更容易学到规律。**模型评估(Model Evaluation)** = 用严谨方法衡量模型性能,判断它能否泛化到未见数据。

> **一句话**:特征工程决定模型的天花板,模型评估决定我们是否真的够到了它。

**为什么重要**:

- 模型的上限由**数据与特征**决定,算法只是逼近这个上限;
- 错误的评估方式会让我们**高估模型**(过拟合、数据泄漏)或**低估模型**(选错指标);
- 工程上,特征工程与评估占 ML 项目的大部分时间。

## 原理:特征工程四大步

### 1. 数据清洗

- **缺失值**:删除(样本少时)、均值/中位数/众数填充、或用模型预测填充;
- **异常值**:基于分布(如 3σ)或业务规则识别,决定删除、截断或单独处理;
- **重复数据**去重;**数据格式**统一(日期、单位、大小写)。

### 2. 特征变换

- **标准化(Standardization)**:减去均值除以标准差 → 均值为 0、方差为 1;对距离类模型(SVM/K-Means/线性)几乎必需;
- **归一化(Normalization)**:缩放到 [0,1] 或 [-1,1];适合有界特征;
- **非线性变换**:log/平方根压缩长尾分布(如收入、价格);
- **处理偏态**:Box-Cox / Yeo-Johnson 变换使分布更接近正态。

### 3. 特征编码(分类变量)

| 方法 | 做法 | 适用 |
| --- | --- | --- |
| **独热编码 One-Hot** | 每个类别一列 0/1 | 无序类别、类别数不多(树模型也常用) |
| 标签编码 Label | 类别映射为整数 0,1,2… | 有序类别;或树模型(对数值不敏感) |
| 目标编码 Target | 用类别对应目标均值编码 | 高基数类别(数万种),注意防泄漏 |

### 4. 特征选择与构造

- **特征选择**:过滤法(方差/相关性)、包裹法(递归消除 RFE)、嵌入法(L1 正则、树模型特征重要性)——去掉无关/冗余特征,减少过拟合、加速训练;
- **特征构造**:从领域知识造新特征(如"下单时间-支付时间"= 支付耗时;日期拆成周几/月份;文本做成 TF-IDF/嵌入)。

## 原理:模型评估五件套

### 1. 数据划分:训练/验证/测试

- **训练集**:拟合模型;验证集:调参选择;测试集:最终评估(只碰一次);
- 顺序错了就是**数据泄漏**:用测试集调参 → 模型"记住"了测试集,分数虚高。

### 2. 分类指标

| 指标 | 含义 | 何时重要 |
| --- | --- | --- |
| 准确率 Accuracy | 全对占比 | 类别均衡时 |
| **精确率 Precision** | 预测为正的里有多少真对 | 误报代价高(垃圾邮件别误删) |
| **召回率 Recall** | 真正例里抓到多少 | 漏报代价高(癌症别漏诊) |
| **F1** | Precision 与 Recall 的调和平均 | 类别不均衡 |
| **AUC-ROC** | 不同阈值下 TPR vs FPR 曲线下面积 | 排序能力、类别不均衡 |

**核心权衡:Precision vs Recall 不可兼得**,业务决定侧重哪个。

### 3. 回归指标

- **MAE**(平均绝对误差):直观、对离群点不敏感;
- **MSE/RMSE**(均方误差/根均方):放大大误差,对离群点敏感;
- **R²**(决定系数):模型解释了多少方差,1 为完美,0 为"等于均值"。

### 4. 交叉验证

把训练集分成 K 折,轮流用 K-1 折训练、1 折验证,取 K 次平均——**比单次划分更稳地估计泛化性能**(常用 K=5 或 10)。`GridSearchCV` 用它来调参。

```python
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier

# 5 折交叉验证评估
scores = cross_val_score(RandomForestClassifier(random_state=42),
                         X, y, cv=5, scoring='f1')
print(f"F1: {scores.mean():.3f} ± {scores.std():.3f}")

# 交叉验证调参
grid = GridSearchCV(RandomForestClassifier(random_state=42),
                    {'n_estimators': [50, 100], 'max_depth': [5, 10]},
                    cv=5, scoring='f1')
grid.fit(X_train, y_train)
print(grid.best_params_, grid.best_score_)
```

### 5. 过拟合、欠拟合与数据泄漏

- **欠拟合**:训练/验证都差 → 模型太简单,加复杂度/特征;
- **过拟合**:训练好验证差 → 模型记住噪声,正则化/更多数据/简化模型;
- **数据泄漏**:目标信息混入特征(如用"是否违约"去预测违约)、用全量数据做标准化/填充再划分——**测试集在建模前必须"看不见"**;正确做法是在**训练折内**拟合变换器。

## 代码 / 实现:完整流程最小示例

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# 1. 划分(先划分,再做任何基于数据的变换!)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)

# 2. 管道:标准化 + 模型(变换只在训练折内拟合,防泄漏)
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', RandomForestClassifier(n_estimators=100, random_state=42)),
])

# 3. 交叉验证 + 最终测试
scores = cross_val_score(pipe, X_train, y_train, cv=5, scoring='f1')
pipe.fit(X_train, y_train)
print(f"CV F1: {scores.mean():.3f} ± {scores.std():.3f}")
print(classification_report(y_test, pipe.predict(X_test)))
```

## 实践 / 应用:工程要点与坑

1. **先划分,再变换**:所有基于数据的操作(标准化/填充/编码)都必须只在训练集上拟合,否则泄漏;
2. **特征工程优先级**:缺失处理 → 数值变换 → 类别编码 → 特征选择 → 特征构造,每步用交叉验证验证收益;
3. **树模型 vs 线性模型的预处理差异**:树模型对尺度不敏感、可吃标签编码;线性/SVM/KNN 必须标准化、类别用独热;
4. **类别不均衡**:用 F1/AUC 而非准确率;可考虑 class_weight、过采样(SMOTE);
5. **记录基线**:先跑一个简单模型(如逻辑回归/均值预测)作为基线,复杂模型必须**显著超过基线**才有意义。

## 总结

- **特征工程**:清洗 → 变换 → 编码 → 选择/构造,决定模型上限,"垃圾进垃圾出";
- **模型评估**:先划分(训练/验证/测试)→ 选对指标(分类 F1/AUC、回归 RMSE/R²)→ 交叉验证 → 防过拟合与数据泄漏;
- **核心纪律**:测试集只碰一次、变换只在训练折内拟合、Precision/Recall 权衡按业务定;
- **下一步**:把特征工程与评估应用到具体模型上——先学 [线性模型](ml-linear-models.md)、[树模型](ml-tree-ensemble.md)、[SVM](ml-svm.md),或先了解 [学习范式与评估概念](ml-learning-paradigms.md)。

## 延伸阅读

- scikit-learn 文档:https://scikit-learn.org/stable/(preprocessing/model_selection/metrics 模块)
- 站内:[学习范式与核心概念](ml-learning-paradigms.md)(评估指标基础)、[线性回归与逻辑回归](ml-linear-models.md)、[决策树与集成学习](ml-tree-ensemble.md)、[聚类](ml-clustering.md)(无监督评估)
