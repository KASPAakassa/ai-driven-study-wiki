# 个人 AI 思维:从"写代码的人"到"AI 协作者"

> **一句话摘要**:Anthropic 内部 65% 的产品工程 PR 由 Claude 写成——这个数字的真正含义不是"AI 越来越强",而是"人正在被重塑"。本文从【个人认知】角度回答:在 AI 原生时代,技能树怎么改、今天能做什么。核心结论:**AI 鸿沟是"用多久"而非"用不用";你竞争的对手,是已经学会跟 AI 协作的人。**
>
> **来源**:微信公众号「杨沐白」《65% PR 背后:Anthropic 那套我没见过的 AI Native 方法论》;数据来源 Anthropic Economic Index(2025-02 首版 / 2026-05 更新)。原文存档 `docs/inbox/ai-native-methodology-source.md`
>
> **原文链接**:https://mp.weixin.qq.com/s/R_I6clfI1i1a-bYV6NQEKg

!!! note "归类说明"
    本文属于 **AI 组织转型与超级个体** 子主题的【个人 AI 思维提升】角度,与 [超级个体](super-individual-to-super-org.md)、[企业 AI 价值模型](ai-value-models-openai.md) 组成"个人 → 组织 → 企业"三层视角;**组织形态角度(65% PR / 4 要素 / 产品矩阵)由另一篇文章负责,本文只回答"个人如何应对 AI 原生时代的技能重塑"**。

## 概念

### 一种正在发生的身份转变

最近一次用 Claude 做项目时,你可能会突然意识到:你不再是那个"写代码的人"了。

你没有亲手写每一行 `import`、调每一个 bug;你做的是:**告诉 AI 哪里出错 → 让它重写 → review → merge**。

整个过程,你更像一个"代码审阅者"+"产品经理"——一个 **AI 协作者**。

!!! tip "关键区分:两种"AI 写代码""
    - 我们以为的:人写 prompt → AI 出 diff → 人 review → merge;
    - Anthropic 真实的:AI 直接开 PR,人来审。
    作者说这两个的区别"比马车和汽车还大":前者只换工具,后者**换了分工方式**。

### 蒸汽机时代类比:从"做"到"看 + 调 + 修"

19 世纪蒸汽机出现后,工人不再手工做鞋,而是看着蒸汽机做鞋,工作从"做"变成"看"+"调"+"修";今天工程师的处境很像:

| 维度 | 蒸汽机时代工人 | 今天的工程师 |
| --- | --- | --- |
| 执行 | 蒸汽机替代体力 | AI 替代编码/常规任务 |
| 核心能力 | 对机器的理解与监控 | 对 AI 的调度与判断 |

!!! warning "先校准认知"
    65% 不是"AI 牛啊",而是"**人正在被重塑**",而且"这件事正在你身上发生"。下面所有原理都在回答:**重塑有没有规律?个人怎么应对?**

## 原理

### ① 首版 Economic Index:AI 在"增强人",不是"取代人"

2025 年 2 月首版 Economic Index(基于 Claude 真实使用数据)核心数据:

| 维度 | 数字 | 解读 |
| --- | --- | --- |
| AI 增强人类能力 vs 自动化 | **57% 增强 vs 43% 自动化** | AI 更多时候是"给人搭把手",而非全自动顶替 |
| 编码 + 数学占总使用量 | **37.2%** | 技术岗位是当前主力,但 AI 的用途远不止写代码 |
| 中高收入职业 AI 使用率 | **最高** | 会用的知识工作者先吃到红利 |
| 极低 / 极高收入职业 AI 使用率 | **反而低** | 使用率呈"倒 U 形":体力岗位用不上,顶尖专家觉得不值 |

!!! note "为什么个人要关注这个数据"
    它说明 AI 变革的割裂在"**会不会用**"而非"穷/富"。中高收入职业(大多数工程师/产品/运营)使用率最高——你正处于被重塑的第一现场。

### ② 5 月新版:AI 鸿沟是"用多久",不是"用不用"

新版核心发现更反常识:

> "用 AI 越久的人越强,而且 AI 学习曲线比想象的更陡。"

我们一直以为"AI 鸿沟"是"用 vs 不用"——用 AI 的人赢、不用的人输。但 Anthropic 的数据说:**AI 鸿沟是"用多久"**——用 AI 一个月和用 AI 一年的人,差距比"用 vs 不用"还大。

!!! warning "这意味着什么"
    - AI 更是一次性的工具革命之上,**持续的学习曲线**:今天写一个 PR 和一年后管十个 Agent,差距是**指数级**的;
    - **越晚开始用 AI,欠的债越大**;"用一年 vs 用一个月"的差距 > "用 vs 不用"的差距,是本文代码要模拟的核心结构。

### ③ 工程师技能树被重写

技能从"我会写 Go"变成"我会调 Agent",而且不是慢慢发生的——**能用 AI 的人已比不能用的人产出高 2-3 倍,倍数还在拉大**。

| 旧技能树 | 新技能树 |
| --- | --- |
| 我会写 Go / Python | 我会调 Agent、定义任务边界 |
| 我熟框架 API | 我熟 prompt 结构与 Skills |
| 我能调好 bug | 我能让 AI 自己修,再 review |
| 我读文档快 | 我会把文档翻译成系统提示词 |

### ④ 反共识:你真正在跟谁抢饭碗

你以为你在跟 AI 抢饭碗,但其实你真正在跟"**已经学会跟 AI 协作的人**"抢饭碗。

!!! tip "把竞争对象放对"
    岗位不会因"AI 会写代码"消失,而会因"**别人用 AI 写得更快更好**"消失。你的对手从来不是工具,是**先用好工具的人**。

### ⑤ 30% 判断:你的工作在重新分配

作者给出了一个更直接的判断:

- 如果你的工作里有 **30% 以上是"重复模式可识别"的任务**,今年之内这 30% 会被 AI 协作者替代;
- 剩下 **70%**,会被"会用 AI 的人"和"不会用 AI 的人"重新分配。

!!! danger "你准备站在哪一边?"
    这不是预测未来,是提醒现在:同份工作,第一个人让 AI 一天干完,第二个人还在手工抄。**重复可识别的交给 AI,不可替代的判断留给自己**——这就是分水岭,也与 [超级个体](super-individual-to-super-org.md) 的"瓶颈在人、在意图带宽"一致。

## 代码 / 实现

用两个纯 Python 小工具,把上面两条核心原理"算"出来:①学习曲线到底有多陡;②怎么找出可 Skill 化的重复任务。**纯标准库、零第三方依赖,`python3` 直接运行**。

### ① 学习曲线模拟器(`ai_collab_curve.py`)

```python
"""ai_collab_curve.py — AI 协作学习曲线模拟(纯 Python,零第三方依赖)

对应 Economic Index"用 AI 越久越强、曲线比想象更陡":
幂律模型模拟"连续使用天数 -> 个人产出倍数",对比不用/一个月/一年。
"""

# 参数(可自行调整)
BASE = 1.0      # 不用 AI 的产出基线
A = 0.6         # 一个月(30 天)期望增益
REF = 30        # 参考天数
P = 0.9         # 陡峭指数:越大越"越用越快"


def output_multiplier(days: int) -> float:
    """连续使用 AI days 天后的产出倍数(相对完全不用 AI 的基线)。"""
    if days <= 0:
        return BASE
    return BASE + A * (days / REF) ** P


def main() -> None:
    points = [0, 1, 7, 30, 90, 180, 365]
    print("=" * 48)
    print("AI 协作学习曲线:用 AI 时长 -> 个人产出倍数(示意模型)")
    print("=" * 48)
    print(f"{'使用时长':<8}{'产出倍数':>10}{'相对不用AI的提升':>18}")
    print("-" * 48)
    for d in points:
        m = output_multiplier(d)
        gain = 100 * (m - BASE) / BASE
        label = "不用AI" if d == 0 else f"{d}天"
        print(f"{label:<8}{m:>10.2f}{gain:>16.1f}%")

    m0, m30, m365 = output_multiplier(0), output_multiplier(30), output_multiplier(365)
    print("\n关键对比(同一根曲线,换个问法):")
    print(f"  '用 vs 不用'的差距         : {m30 / m0:5.2f} 倍(用 1 个月时)")
    print(f"  '用一年 vs 用一个月'的差距  : {m365 / m30:5.2f} 倍")
    print(f"\n结论:用一个月和用一年的差距({m365 / m30:.1f}倍)")
    print(f"     > 用和不用的差距({m30 / m0:.1f}倍)")
    print("     => AI 鸿沟是'用多久',不是'用不用';越晚开始,欠的债越大。")


if __name__ == "__main__":
    main()
```

**实测输出(Python 3.14.3 验证通过)**:

```
使用时长   产出倍数   相对不用AI的提升
不用AI         1.00       0.0%
1天           1.03       2.8%
7天           1.16      16.2%
30天          1.60      60.0%
90天          2.61     161.3%
180天         4.01     300.9%
365天         6.69     568.6%
用 vs 不用: 1.60 倍
用一年 vs 用一个月: 4.18 倍
```

**逐段解释**:

- `M(days) = BASE + A * (days / REF) ** P`:幂律模型,`A` 是一个月期望增益,`P` 控制陡峭程度;
- 数值是示意、非 Anthropic 原始数据,重点在**结构**:一个月(1.6 倍)和一年(6.7 倍)的差距,显著大于"用 vs 不用"(1.6 倍)——这就是"AI 鸿沟是'用多久'"的数学表达;
- 把 `P` 改大(如 1.2)曲线更陡:越陡,晚起步代价越大,也解释"产出高 2-3 倍且差距在拉大"。

### ② 重复任务识别器(`skillable_finder.py`)

```python
"""skillable_finder.py — 重复任务识别器(纯 Python)

"重复 3 次以上"的任务值得写成 Skill(Skills 是 AI 原生组织的最小单元,
https://github.com/anthropics/skills)。输入一列任务描述,输出重复候选。
"""

import re
from collections import Counter


def normalize(task: str) -> str:
    """归一化:小写 + 归并 commit hash + 规整空白,便于聚类。"""
    task = task.lower()
    task = re.sub(r"[0-9a-f]{8,}", "<hash>", task)
    task = re.sub(r"[_\"']", " ", task)
    return re.sub(r"\s+", " ", task).strip()


def find_skillable(tasks: list[str], min_count: int = 3) -> list[tuple[str, int]]:
    counter = Counter(normalize(t) for t in tasks)
    return [(t, n) for t, n in counter.most_common() if n >= min_count]


if __name__ == "__main__":
    # 用一份"日常任务日志"演示
    log = [
        "Review PR #102", "Review PR #103", "Review PR #104",
        "Deploy to staging", "Deploy to staging", "Deploy to staging", "Deploy to staging",
        "Fix import error in main.py", "Fix import error in api.py",
        "Write weekly report", "Write weekly report", "Write weekly report",
        "Investigate CI failure", "Investigate CI failure",
    ]
    hits = find_skillable(log)
    print("可 Skill 化候选(重复 >= 3 次):")
    for task, n in hits:
        print(f"  [{n} 次] {task}")
    if not hits:
        print("  (没有发现重复任务——再攒一攒,或调低 min_count)")
```

**实测输出**:

```
可 Skill 化候选(重复 >= 3 次):
  [4 次] deploy to staging
  [3 次] write weekly report
```

!!! tip "怎么用这两个脚本"
    把第二个脚本的 `log` 换成你这一周的 commit message / 工单标题,跑一遍就是"**Skill 化候选清单**";重复 3 次以上的任务写成 Skill,是个人版的最小 AI 原生改造(对应实践第 1 条)。

## 实践 / 应用

### 今天就能做的 5 件事

作者给的 5 个动作(按个人认知角度整理):

| 序 | 动作 | 为什么重要 | 资源 |
| --- | --- | --- | --- |
| 1 | 把日常任务里"重复 3 次以上"的找出来,写一个 Skill | **Skills 是 AI 原生组织的最小单元** | https://github.com/anthropics/skills |
| 2 | 把团队的工作守则翻译成系统提示词 | **提示词工程 = 新的团队建设** | Claude.ai / Cowork 都能跑 |
| 3 | 试用 Cowork 技能录制 | 演示一遍,Agent 就学会——这是 AI 学习曲线的关键 | Claude.ai Pro $20/月 |
| 4 | 读《Building AI Agents for the Enterprise》23 页 | 三大支柱 + 六个月部署框架 | anthropic.com 官网 |
| 5 | 用 Economic Index 说服你老板 | AI 鸿沟是"用多久",不是"用不用" | anthropic.com/economic-index |

!!! note "第 1 和 3 条是关键"
    作者原话:"你今天不写 Skills,明年就要补这门课。" Skills 把一次性 prompt 沉淀为可复用"技能包",是个人学习曲线的**复利单元**;技能录制让 Agent 通过演示学习——都作用于"用多久"的曲线。

### 行动判断:30% 会被替代,你准备站在哪一边?

1. **识别你的 30%**:把工作清单过一遍,标出"重复模式可识别"的任务(报表、部署、常规 PR、周报……),这些今年内会被 AI 协作者替代;
2. **守住你的 70%**:判断、边界、取舍、Review、信任——这些会流向"会用 AI 的人";
3. **用一年换陡峭曲线**:把"用 AI"当**能力建设项目**持续做,而不是零散工具切换。

### 与站内的交叉印证

!!! tip "三层视角:个人 → 组织 → 企业"
    - **组织**:[超级个体](super-individual-to-super-org.md)——李志飞"超级个体被高估、瓶颈在人"与本文"跟已学会协作的人抢饭碗"是同一枚硬币:个人产能需被组织容器承接;
    - **企业**:[价值模型](ai-value-models-openai.md)——"员工赋能"是五模型第一优先级,正是个人学习曲线的组织版;本文"30% 判断"也是个人维度的"双轨制员工"预警。

- **07-agent-coding(个人实践层)**:[Agent 编码经验总览](../../07-agent-coding/index.md) 讲"个人怎么用 Agent",本文讲"个人怎么被重塑";[Loop Engineering](../../07-agent-coding/experience/loop-engineering.md) 是"重复任务 → 自动化闭环"的进阶;[Skills 方法论](../../07-agent-coding/skills/mattpocock-skills.md) 有现成 Skill 写法;[AGENTS.md](../../07-agent-coding/experience/agent-rules-agents-md.md) 对应第 2 条"工作守则 → 系统提示词"。

!!! warning "三个常见误区"
    1. **把"用 AI"当工具切换,不当能力建设**——红利属于"持续用 + 沉淀 Skill"的人;
    2. **只追 prompt 技巧,不沉淀 Skills**——一次性对话没有复利,Skill 才是复利单元;
    3. **等组织统一部署再学**——等安排完,你已在曲线零点站了一年。

## 总结

- **身份在变**:从"写代码的人"到"AI 协作者"——代码审阅者 + 产品经理,像蒸汽机时代工人从"做"变"看 + 调 + 修";
- **鸿沟在变**:首版 Economic Index 说 AI 在"增强人"(57% vs 43%),5 月新版更残酷——**差距不在"用不用",在"用多久"**;
- **竞争在变**:你在跟"已经学会跟 AI 协作的人"抢饭碗;
- **工作在重分配**:重复可识别的 30% 交给 AI,剩下 70% 流向"会用 AI 的人";
- **动作要快**:写 Skill、翻译工作守则、试技能录制——**今天就能开始,这条赛道没有终点**。

**下一步学什么**:深挖"重复任务 → 自动化闭环"读 [Loop Engineering](../../07-agent-coding/experience/loop-engineering.md);组织层面读 [超级个体](super-individual-to-super-org.md);企业战略读 [价值模型](ai-value-models-openai.md)。

## 延伸阅读

- 站内:[子主题首页](index.md)、[从超级个体到超级组织](super-individual-to-super-org.md)、[企业 AI 价值模型](ai-value-models-openai.md)、[07-agent-coding](../../07-agent-coding/index.md)([Loop Engineering](../../07-agent-coding/experience/loop-engineering.md)/[Skills](../../07-agent-coding/skills/mattpocock-skills.md)/[AGENTS.md](../../07-agent-coding/experience/agent-rules-agents-md.md));原文存档于 `docs/inbox/ai-native-methodology-source.md`
- 外部:原文 https://mp.weixin.qq.com/s/R_I6clfI1i1a-bYV6NQEKg;Anthropic Economic Index https://anthropic.com/economic-index;Anthropic Skills https://github.com/anthropics/skills;《Building AI Agents for the Enterprise》23 页指南(anthropic.com)
