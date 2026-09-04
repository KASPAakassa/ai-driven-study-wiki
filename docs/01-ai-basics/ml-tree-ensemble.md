# 决策树与集成学习:随机森林、GBDT 为什么是表格数据的王者

> **一句话摘要**:从"用一系列 if-else 做预测"的决策树出发,讲清 Bagging(随机森林)与 Boosting(GBDT/XGBoost)两种集成思想,以及为什么它们在表格数据上至今难逢敌手。
>
> **来源**:综合公开资料,参见文末延伸阅读。

## 概念

- **决策树(Decision Tree)**:一棵"自动学出来的 if-else 规则树"。根节点问"面积 < 80㎡?",是 → 走左子树,否 → 走右子树,叶节点给出预测值/类别。可解释性最强,一条预测能完整讲出推理路径。
- **集成学习(Ensemble Learning)**:单个树容易过拟合、不稳定(数据小扰动 → 树结构大变)。**把很多棵弱树组合起来**取平均/投票,显著提升稳定性与精度,这就是"三个臭皮匠"思想。
- **两大流派**:
  - **Bagging**(代表:随机森林 Random Forest)—— 并行训练,降低**方差**;
  - **Boosting**(代表:AdaBoost、GBDT、XGBoost、LightGBM)—— 串行训练,降低**偏差**。

## 原理

### 决策树怎么选分裂点

树生长的核心问题是:**在哪个特征、哪个阈值上分裂,信息增益最大?** 常用两种纯度指标:

- **基尼不纯度(Gini)**:随机抽两个样本类别不一致的概率。越接近 0 越纯。`Gini = 1 - Σ p_k²`。
- **信息熵(Entropy)**:`H = -Σ p_k log p_k`。信息增益 = 分裂前熵 − 分裂后加权熵,增益越大说明分得越"干净"。

以 CART(分类回归树,工业最常用)为例:遍历所有特征 × 所有候选阈值,选让基尼下降最多的分裂点,递归生长,直到满足停止条件(最大深度、最小叶节点样本数等)。

### 过拟合与控制

树可以无限生长直到每个叶节点只有一个样本——这必然过拟合。控制手段:

- **预剪枝**:限制最大深度、最少样本数、最小信息增益;
- **后剪枝**:先长满再剪掉对验证集无提升的分支;
- 深度 3–10 的小树往往泛化最好,**单棵决策树的精度通常不高,它的价值在于作为集成的基础单元**。

### Bagging 与随机森林

**Bagging(Bootstrap Aggregating)**:对训练集**有放回抽样**生成多份子集,各自训练一棵树,预测时投票/平均。每棵树只见过部分数据 → 单棵方差大,但**平均后方差显著下降**。

**随机森林 = Bagging + 随机选特征**:每棵树的每个分裂点只从**随机抽出的 m 个特征**里选最优(而不是全部),进一步降低树间相关性,让"三个臭皮匠"真的各有所长。两个超参数很关键:`n_estimators`(树的数量)与 `max_features`(每节点候选特征数)。

### Boosting 与 GBDT

**Boosting**:串行训练,每棵新树**重点学习前面所有树的残差/错误**,最终加权组合。

**GBDT(Gradient Boosting Decision Tree)** 的核心思想:第 t 棵树拟合的是**损失函数对当前模型预测的负梯度**(对 MSE 而言就是残差 `y - ŷ`)。用数学说:

$$
F_{t}(x) = F_{t-1}(x) + \eta \cdot h_t(x)
$$

其中 `h_t` 是拟合负梯度 `-∂L/∂F` 的树,`η`(learning rate)控制每步贡献,一般取 0.01–0.1 并配合更多棵树。

**XGBoost / LightGBM** 是 GBDT 的高性能工程实现:加入二阶导数、正则项、直方图分桶、并行化等,成为 Kaggle 表格数据竞赛的常胜将军。

## 代码 / 实现

手写一棵"玩具决策树"理解分裂逻辑(完整版需要递归,这里展示核心的分裂选择):

```python
def gini(groups):
    """计算按某特征分裂后的加权基尼不纯度"""
    total = sum(len(g) for g in groups)
    score = 0.0
    for g in groups:
        if not g:
            continue
        size = len(g)
        p1 = sum(1 for _, y in g for y in [y] if y == 1) / size
        score += (size / total) * (1 - p1**2 - (1-p1)**2)
    return score

def best_split(X, y):
    """遍历所有特征与阈值,找基尼下降最大的分裂点(示意)"""
    data = list(zip(X, y))
    best = None
    for feat in range(len(X[0])):
        vals = sorted(set(row[feat] for row in X))
        for i in range(len(vals) - 1):
            thr = (vals[i] + vals[i+1]) / 2
            left  = [row for row in data if row[0][feat] < thr]
            right = [row for row in data if row[0][feat] >= thr]
            g = gini([left, right])
            if best is None or g < best[0]:
                best = (g, feat, thr)
    return best

X = [[1, 1], [1, 0], [0, 1], [0, 0], [2, 2], [2, 0]]
y = [1, 0, 0, 0, 1, 0]
print(best_split(X, y))   # (基尼, 特征序号, 阈值)—— 第一个特征、阈值 1.5 附近最优
```

**工业实践(真实项目用现成库)**:

```python
# 需要 pip install scikit-learn xgboost
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

model = XGBClassifier(n_estimators=200, learning_rate=0.05, max_depth=6)
# model.fit(X_train, y_train); model.predict(X_test)
```

## 实践:何时用树模型

- **表格数据(结构化数据)首选**:特征类型混杂(数值+类别)、量纲不一致、有缺失值时,树模型天然健壮——**不需要特征缩放**,这是相对线性模型/神经网络的最大便利。
- **可解释性需求**:单棵小决策树可以可视化、可以直接给人讲;随机森林可以输出特征重要性。
- **与深度学习的分工**:图像、语音、文本等非结构化数据交给深度学习;带 ID、金额、类别列的表格数据,GBDT 家族(LightGBM/XGBoost)通常是默认最优解。
- **常见坑**:Boosting 对噪声/异常值敏感(会拼命拟合残差);超参数(树数、深度、学习率)需要调;树多时推理变慢、内存变大。

## 总结

- 决策树 = 自动学的 if-else 规则,靠基尼/熵选分裂点,需要剪枝防过拟合。
- Bagging/随机森林:并行多棵树取平均,**降方差**;Boosting/GBDT:串行拟合残差,**降偏差**。
- GBDT 的高性能实现(XGBoost/LightGBM)统治表格数据;树模型免特征缩放,可解释,是结构化数据的默认起点。

## 延伸阅读

- 站内:[学习范式与核心概念](ml-learning-paradigms.md)、[线性回归与逻辑回归](ml-linear-models.md)
- 外部:scikit-learn 文档《Decision Trees》《Ensemble methods》;XGBoost 官方文档"Introduction to Boosted Trees"(作者手把手推导)
