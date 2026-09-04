# 训练与开发排查清单:症状 → 原因 → 排查顺序

> **一句话摘要**:训练不收敛、loss 变 NaN、过拟合、显存不足、LLM 输出乱、Agent 死循环……给出八大高频问题的「症状 → 原因 → 排查顺序」速查表与可运行的诊断脚本片段。
>
> **来源**:综合公开资料(CS231n 调参指南、PyTorch 论坛常见问题),诊断代码为本项目自研验证。

## 概念

- **排障(debugging)是硬技能**:ML 项目 70% 的时间在"为什么结果不对",只有 30% 在"写模型"。系统化的排查顺序能救回大量时间。
- **症状-原因-对策模型**:每个问题都从**症状**(可观测的信号)出发,列**候选原因**,按**概率与验证成本**排序逐一排除——而不是瞎试参数。
- **关键纪律:一次只改一个变量**。同时改学习率 + 换模型 + 加数据,失败了也说不清是哪一步救回来的。

## 原理

### 通用排查方法论(五步)

1. **复现**:固定随机种子,把问题稳定复现出来——偶发现象无法定位。
2. **二分定位**:把管线切两半(数据?模型?训练循环?),哪一半出错。
3. **最小复现**:删到只剩触发问题的极小用例。
4. **改一个变量并记录**:每个假设对应一次实验,记录日志。
5. **验证修复**:修复后跑回归,确认没引入新问题。

### 诊断三角:数据 / 模型 / 训练

| 环节 | 问自己 | 常见信号 |
|---|---|---|
| 数据 | 标签对吗?归一化了吗?有泄漏吗? | 训练 loss 立刻降但验证很差 |
| 模型 | 前向对不对?梯度对不对? | loss 不降 / 不变 |
| 训练过程 | 学习率合适吗?数值稳定吗? | loss 震荡 / NaN |

## 代码 / 实现

以下诊断片段均为纯 Python + numpy,可直接保存运行。

### 1) 梯度检查:验证反向传播是否正确

```python
import numpy as np

def gradient_check(f, grad_f, x, eps=1e-6):
    """数值梯度 vs 解析梯度:相对误差 < 1e-5 说明反向传播没错。"""
    numeric = np.zeros_like(x, dtype=float)
    for i in range(x.size):
        xp, xm = x.copy(), x.copy()
        xp.flat[i] += eps; xm.flat[i] -= eps
        numeric.flat[i] = (f(xp) - f(xm)) / (2 * eps)
    denom = np.linalg.norm(numeric - grad_f(x)) / (
        np.linalg.norm(numeric) + np.linalg.norm(grad_f(x)))
    return denom

err = gradient_check(lambda z: np.sum(z ** 3), lambda z: 3 * z ** 2,
                     np.array([1.0, 2.0, 3.0]))
print(f"相对误差 = {err:.2e}")     # 预期 ~1e-10,若 >1e-5 则公式有 bug
```

### 2) 训练状态监测:NaN / 停滞 / 震荡

```python
import numpy as np

def check_loss(losses, window=5):
    if any(l != l for l in losses):
        return "发现 NaN:检查学习率过大、数据含 inf、初始化过大"
    recent = [l for l in losses[-window:] if l == l]
    if len(recent) >= 3 and recent[-1] >= recent[-3] * 0.999:
        return "loss 停滞:增大学习率 / 换优化器 / 检查特征缩放"
    return "训练状态正常"

print(check_loss([3.0, 1.5, 0.8, 0.5, np.nan]))   # NaN 场景
```

### 3) 过拟合检测:训练 / 验证差距

```python
def detect_overfit(train_loss, val_loss):
    gap = val_loss - train_loss
    if gap > 0.15 * val_loss:
        return f"疑似过拟合:gap={gap:.3f},超过验证 loss 的 15%"
    return "拟合正常"

print(detect_overfit(0.01, 0.90))    # gap=0.89 → 过拟合信号
```

### 4) 学习率扫描:最小的"炼丹"实验

```python
import numpy as np

def lr_scan(X, y, lrs=(1e-4, 1e-2, 1.0), epochs=500):
    def train(lr):
        m, d = X.shape
        w = np.zeros(d); b = 0.0
        for _ in range(epochs):
            pred = X @ w + b
            w -= lr * (X.T @ (pred - y) / m)
            b -= lr * (pred - y).mean()
        return np.mean((X @ w + b - y) ** 2)
    return {lr: round(train(lr), 6) for lr in lrs}

rng = np.random.default_rng(7)
X = rng.uniform(-1, 1, (100, 2))
y = 3 * X[:, 0] - 2 * X[:, 1] + rng.normal(0, 0.1, 100)
print(lr_scan(X, y))   # 预期 1e-4 收敛很慢,1e-2 与 1.0 较好
```

## 实践 / 应用:八大问题速查表

!!! warning "排查纪律"
    一次只改一个变量;动手前先记录当前实验的 seed、超参与指标,否则失败时无从归因。

| # | 症状 | 高概率原因(按排查顺序) |
|---|---|---|
| 1 | **loss 不下降** | ① 学习率过小/过大 → ② 特征未标准化 → ③ 梯度算错(跑梯度检查)→ ④ 数据/标签没对齐 → ⑤ 初始化不当 |
| 2 | **loss = NaN** | ① 学习率过大 → ② 数据含 inf/异常值 → ③ log(0)、exp 溢出(缺数值稳定)→ ④ 除零(分母 0) |
| 3 | **过拟合** | ① 训练 loss 低、验证高:模型过大/特征太多 → ② 数据太少 → ③ 缺正则化 → ④ 训练过久(早停) |
| 4 | **欠拟合** | ① 模型表达能力不足 → ② 特征太少/太弱 → ③ 训练不充分 → ④ 数据没标准化导致收敛慢 |
| 5 | **GPU 显存不足** | ① batch size 过大 → ② 序列过长/图片过大 → ③ 中间变量未释放 → ④ 数据加载重复累积 |
| 6 | **数据泄漏** | ① 预处理统计量在全量数据上算 → ② 划分在去重/清洗之前 → ③ 测试信息进入特征(如目标编码)→ ④ 重复样本跨划分 |
| 7 | **LLM 输出格式错乱** | ① 未用 json_schema/response_format → ② 提示词没说清格式 → ③ 输出被截断(finish_reason=length)→ ④ 温度过高(降 temperature) |
| 8 | **Agent 死循环** | ① 缺最大迭代上限 → ② 工具结果未正确回填(tool_call_id 错)→ ③ 循环条件不可判定 → ④ 模型重复调用同一工具(加去重/护栏) |

### 展开几个关键案例

**loss = NaN 的排查顺序**:先看数据(`np.isfinite(X).all()`),再看数值稳定性(softmax 是否减 max、是否用 `log(p+1e-12)` 防 log0),最后逐步调小学习率(直接砍 10 倍验证)。

**GPU 显存不足(OOM)** 顺序:先减半 batch size 验证问题性质 → 关闭不必要梯度(`no_grad`)、释放中间变量 → 用梯度累积模拟大 batch → 最后才考虑混合精度/换小模型。显存是"最高峰瞬时占用",峰值由最大张量决定。

**数据泄漏**是最隐蔽的:训练集指标完美、线下验证虚高、上线就崩。三处高频泄漏点见上表第 6 行——**先划分、后预处理**是铁律。

**LLM 输出乱 / Agent 死循环**是 2024 年后最常踩的坑:结构化输出永远配 `json.loads` + 异常兜底,并设置 `max_tokens` 防截断;Agent 循环必须内置**最大步数上限 + 工具去重 + 超时**,把"失控"变成"可观测的失败"。

### 排查工具箱

- 记录一切:每个实验的 seed、超参、指标进表格(或 CSV);
- 打印/绘制训练与验证 loss 曲线,一眼看出震荡、停滞、gap;
- 用断言守护数据管线:形状、dtype、有限值、标签范围;
- 失败时"缩小问题":1 个 batch、10 个样本、1 个 epoch 能不能跑通?

## 总结

- 排查 = 症状 → 候选原因排序 → 一次改一个变量 → 记录验证。
- 三大高频根因:**学习率**、**数据/标签**、**数值稳定性**——先怀疑它们。
- 先划分后预处理、固定随机种子,能提前消灭一大半"玄学"问题。
- 梯度检查是验证手写反向传播的唯一可靠手段。
- 下一步:把[端到端项目实战](practice-end-to-end-ml.md)的复盘清单和本文速查表一起用起来。

## 延伸阅读

- 站内:[端到端机器学习实战](practice-end-to-end-ml.md)、[训练技巧与炼丹心法](../01-ai-basics/dl-training-techniques.md)、[调用 LLM API 构建应用](practice-llm-api.md)
- 外部:CS231n "Troubleshooting Neural Networks" 一节;Andrej Karpathy《A Recipe for Training Neural Networks》;PyTorch 论坛常见问题帖
