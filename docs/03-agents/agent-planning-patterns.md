# Agent 规划与工作流模式:推理四模式 + 工作流四模式

> **一句话摘要**:Agent 面对复杂任务如何安排先后?两条主线:推理模式(模型怎么思考)——ReAct 边想边做、Plan-and-Execute 先谋后动、Reflexion 做完复盘、ToT 多想几条路;工作流模式(系统怎么组织步骤)——线性管道、ReAct 循环、管道编排、人机协作,外加三条选型铁律。本文讲清每种模式的机制、适用场景、代码示例与选型经验。
>
> **来源**:综合公开资料,基于《2026 AI Agent 技术栈全景图》(merlinfeng,https://mp.weixin.qq.com/s/hy35QS327__ntlNWAPFHeQ)与《Agent工作流设计:4种模式+3个原则》(人间尘埃,https://mp.weixin.qq.com/s/Jc2lo4qM07kAw0ABZh090w)整合深化;参考论文:CoT(Wei et al. 2022)、ReAct(Yao et al. 2022)、Reflexion(Shinn et al. 2023)、ToT(Yao et al. 2023)

## 概念:为什么需要规划

LLM 单次推理擅长"回答一个问题",但真实任务往往需要**多步、有序、可调整**的执行:查数据 → 分析 → 写报告 → 发出去。规划(Planning)解决的就是"**如何安排这些步骤**"——什么时候动手、什么时候思考、失败了怎么办。

!!! note "规划的层次"
    规划不等于"写一份计划"。四种推理模式代表四种对"计划"的态度:不计划(ReAct)、先计划后执行(Plan-and-Execute)、边做边复盘(Reflexion)、并行探索多条路径(ToT)。

!!! tip "推理模式 vs 工作流模式"
    **推理模式**回答"模型单次/多次推理怎么思考"(本文四模式);**工作流模式**回答"系统整体怎么组织步骤"(线性管道 / ReAct 循环 / 管道编排 / 人机协作,见实践篇)。两者正交:一个 Agent 可以是"ReAct 推理 + 管道编排工作流"的组合。

## 原理 1:ReAct——边想边做(默认选择)

**机制**:不预先定计划,走一步看一步——每步根据观察结果决定下一步。

```
Thought(推理)→ Action(行动)→ Observation(观察)→ Thought → ... → Final Answer
```

**真实循环中模型看到的 prompt**(文本协议版):

```
Question: 特斯拉现在的股价比上周涨了多少?
Thought: 我需要先查特斯拉现在的股价。
Action: search
Action Input: 特斯拉 股价
--(系统执行 search,回填)--
Observation: 特斯拉当前股价 $248.50,上周收盘价 $232.10。
Thought: 我知道了当前股价和上周股价,需要计算涨幅。
Action: calculator
Action Input: (248.50 - 232.10) / 232.10 * 100
--(系统执行 calculator,回填)--
Observation: 7.07%
Final Answer: 特斯拉股价比上周上涨了约 7.07%。
```

**关键洞察**:所谓 Agent 的"思考",是一场**精心设计的文本接龙**——模型每一步生成的内容被代码解析、执行、回填,循环终止于模型输出 Final Answer 或撞上最大循环次数。

| 优点 | 缺点 | 适合 |
| --- | --- | --- |
| 灵活、容错好,失败能自己换路 | 没有全局观,容易短视、做一步忘一步 | 步骤少、路径不固定的任务(查资料、问答) |

!!! warning "死循环是生产必考题"
    模型一直不输出 Final Answer、或工具一直返回不满意结果,就会一圈圈转、Token 哗哗烧。**生产环境里最大循环次数和 Token 上限是必选项,不是可选项**(见下方代码示例)。

## 原理 2:Plan-and-Execute——先谋后动

**机制**:先用一个**规划 Agent** 把整个任务拆成步骤清单,再由**执行 Agent** 逐步执行。

```
[规划] 分析任务 → 输出步骤清单 [1. 调研行业  2. 收集数据  3. 写报告]
[执行] 逐步执行,每步可调工具
```

| 优点 | 缺点 | 适合 |
| --- | --- | --- |
| 全局观强,长任务不容易跑偏 | 计划赶不上变化,中间一步失败后续计划全要重来 | 步骤多、结构清晰的任务(调研行业并写报告) |

!!! tip "升级版:动态重规划"
    生产实现通常允许"计划之外"的偏差:执行 Agent 遇到意外结果时,可以回到规划 Agent 重新生成剩余步骤,而不是死守原计划。

## 原理 3:Reflexion——做完复盘

**机制**:在 ReAct 基础上加**自我批评**——每次行动后让模型评估"我刚才做得对吗?哪里能改?",把反思记入**内部记忆**指导后续行动。

```
Thought → Action → Observation → 反思(Reflection)→ 更新记忆 → 下一轮(带着上轮反思)
```

- 论文数据亮眼:HumanEval 代码任务 91% pass@1,对代码生成类任务提升明显;
- **代价**:每步多一次 LLM 调用,Token 消耗接近翻倍;
- 工程上可与 [Agent 持续进化](agent-continuous-evolution.md) 的"轨迹评价"结合:反思结果可作为更新 Skill/知识候选。

## 原理 4:Tree of Thoughts(ToT)——多想几条路

**机制**:不再单线推理,而是**同时展开多个推理分支**,像下棋一样评估每条分支前景、砍差保好。

```
          问题
        /   |   \
    想法A  想法B  想法C     ← 并行生成多个候选
      |     |     |
    评估    评估   评估      ← 每个分支打分/前景评估
      \     |     /
    保留 A、C → 继续展开     ← 剪枝差的,保留好的
```

- **理论上最强**:搜索空间内找到最优路径;
- **实践中极贵**:Token 消耗是单线的几倍到十几倍;
- 适用:数学、逻辑谜题等"值得一掷千金"的难题。

## 代码 / 实现:四种模式的骨架对比

用纯 Python 演示四种模式的核心循环差异(可运行):

```python
MAX_STEPS = 5  # 生产必选:最大循环次数

def react(tools, question, max_steps=MAX_STEPS):
    """ReAct:边走边看,带步数上限(防止死循环)"""
    obs = ""
    for i in range(max_steps):
        thought = f"第{i+1}步推理(看到:{obs[:40]})"
        action = pick_action(tools, thought)      # 模拟模型选工具
        if action == "finish":
            return f"完成: {thought}"
        obs = execute(tools, action)              # 执行并观察
    return "撞到最大步数上限(强制停止)"            # 关键:不收敛也停

def plan_and_execute(tools, question):
    """Plan-and-Execute:先出清单,再逐步执行"""
    plan = ["调研", "收集数据", "写报告"]           # 规划 Agent 产出
    results = [execute(tools, f"执行[{s}]") for s in plan]
    return " -> ".join(results)

def reflexion(tools, question, rounds=3):
    """Reflexion:每轮执行后自我批评,把反思带进下一轮"""
    memory = ""
    for r in range(rounds):
        out = execute(tools, f"第{r+1}轮尝试(memory:{memory[:30]})")
        memory = f"反思:上次{'成功' if 'ok' in out else '失败'},下次改进X"  # 自我批评
    return memory

def tree_of_thoughts(tools, question, branches=3):
    """ToT:并行展开分支,评估剪枝"""
    alive = [f"分支{i}" for i in range(branches)]
    for depth in range(3):
        scores = {b: len(b) % 3 for b in alive}    # 模拟评估打分
        alive = [b for b, s in scores.items() if s >= 1]  # 砍掉差分支
        alive = [f"{b}->扩展" for b in alive]
    return alive

def pick_action(tools, thought): return "finish" if "ok" in thought else list(tools)[0]
def execute(tools, action): return f"工具[{action}]执行,结果ok"

tools = {"search": "搜索", "calculator": "计算"}
q = "查特斯拉股价涨幅"
print("ReAct:", react(tools, q))
print("P&E  :", plan_and_execute(tools, q))
print("Refl :", reflexion(tools, q))
print("ToT  :", tree_of_thoughts(tools, q))
```

**运行结果**:四种模式输出形态各不相同——ReAct 单线带步数上限、P&E 先清单后执行、Reflexion 记忆带反思、ToT 并行分支剪枝。真实实现中,"选工具/评估分支"都是 LLM 调用,这里用模拟函数替代。

## 实践 / 应用:选型经验与工程要点

**选型经验**(实用优先):

1. **默认 ReAct**:80% 的业务场景,ReAct + 好工具就够用;
2. **任务超过五步 → Plan-and-Execute**:结构清晰的长任务先规划;
3. **代码场景 → 加 Reflexion**:测试失败反馈驱动修正,提升明显;
4. **ToT 等有充足 Token 预算再说**:数学/逻辑难题专用。

### 工作流四模式(系统怎么组织步骤)

!!! tip "别从零开始造轮子"
    常见场景就那么几种,对应几种成熟的工作流模式;选对模式,能避开"先搭 Agent → 挂工具 → 加 RAG → 拆了重来"的弯路。**新项目头两周,强制只用最简模式跑通,再考虑加复杂度。**

| 模式 | 机制 | 适用场景 | 复杂度 | 风险提示 |
| --- | --- | --- | --- | --- |
| **线性管道** | 输入 → LLM 处理 → 输出,一步到位 | FAQ/摘要/翻译等单轮任务 | 低 | 生产稳定性最高,无循环无死循环,无多步状态 |
| **ReAct 循环** | 推理-行动-观察,直到完成 | 多步推理 + 工具调用(数据分析/排障/多源检索) | 中 | **不可控**:循环硬限制 5 次(90% 正常任务 3 次内),超限走兜底 |
| **管道编排** | 任务拆阶段,每阶段专门 prompt/模型,前输出接后输入 | 多阶段复杂任务(如合同审查:便宜模型提取 → 大模型对比 → 便宜模型格式化) | 中 | 线性流转、无循环、好调试;**与多 Agent 协作是两回事**,能解决就别碰多 Agent |
| **人机协作** | Agent 自动跑到决策点暂停,人确认后继续 | 高风险决策(医疗/法务审批/大额交易) | 高 | 合规场景几乎唯一选择 |

!!! warning "ReAct 的三个实战经验"
    - **循环硬限制 5 次**:超过直接走兜底(返回预设话术 + 转人工);
    - **每步记 trace**:调了什么工具、传了什么参数、返回什么结果全记录——没接 trace 的 ReAct 上线等于裸奔;
    - **工具描述写人话**:写"当用户提到自己的订单、账户或个人信息时调用此工具",而不是"该工具用于获取用户信息"——前者模型一看就明白什么时候该用。

!!! tip "人机协作的实现要点"
    - **暂停-恢复机制**:决策点持久化状态(存数据库),审核后加载继续——中间可能隔几小时甚至几天;
    - **审核信息要翻译**:把"模型置信度 0.72"翻译成"中等可信度,建议关注第 3 条风险",别丢原始输出给业务人员;
    - **记录每一步人工决策**:既是审计需要,也是后续模型效果分析与训练数据来源。

### 三条选型铁律(原则不能丢)

1. **最小可用原则**:永远从最简单的模式开始——能用线性管道就别上 ReAct,能用管道编排就别上多 Agent;**每加一层复杂度,调试成本和线上风险都翻倍**;
2. **可观测原则**:每步留痕(工具/参数/结果/Token/耗时)——**没接 trace 的 Agent 不许上生产**;
3. **兜底原则**:每个可能失败的地方都要 fallback(模型超时、工具不通、循环超限)——最简"返回预设话术 + 转人工"就够,但必须有。

**完整选型矩阵**(先选复杂度最低的,跑通再迭代):

| 场景特征 | 推荐模式 | 复杂度 |
| --- | --- | --- |
| 单轮问答、文本处理 | 线性管道 | 低 |
| 需要调工具、多步推理 | ReAct 循环 | 中 |
| 多阶段复杂任务 | 管道编排 | 中 |
| 高风险决策需人工确认 | 人机协作 | 高 |

**工程要点**:

- **循环控制是铁律**:最大步数 + Token 上限 + 超时,三者必备;
- **与工具质量强耦合**:规划再强,工具 schema 定义不清(见 [工具调用](tool-calling.md))也会翻车;
- **规划结果要可观测**:把每步 Thought/Action 记入 trace([可观测性](ai-infra-layering.md) 的 L8);
- **别追新**:很多团队一上来追最新推理模式,其实用不上——先评估任务复杂度再选。

## 总结

- **ReAct** 灵活容错、默认选择;本质是"文本接龙",循环收敛靠工程约束;
- **Plan-and-Execute** 全局观强,适合步骤多、结构清晰的任务;
- **Reflexion** 自我批评 + 记忆,代码生成提升明显,Token 翻倍;
- **ToT** 并行分支 + 评估剪枝,理论最强、实践最贵;
- 推理模式选型:**默认 ReAct,超五步上 P&E,代码加 Reflexion,难题才上 ToT**;
- 工作流模式选型:**先线性管道,需工具上 ReAct,多阶段上管道编排,高风险上人机协作**;三铁律:最小可用、可观测、兜底;
- **别从零造轮子**:选对模式比写对代码更能避开"搭了拆、拆了搭"的弯路;先跑通最简闭环,再加复杂度。

## 延伸阅读

- 站内:[AI Agent 入门](agent-intro.md)(think-act-observe)、[工具调用](tool-calling.md)、[Context Engineering](context-engineering.md)(循环与上下文)、[生产级 Agent 9 层架构](ai-infra-layering.md)
- 外部:CoT(Wei et al. 2022)、ReAct(Yao et al. 2022)、Reflexion(Shinn et al. 2023)、Tree of Thoughts(Yao et al. 2023)论文;原文《2026 AI Agent 技术栈全景图》《Agent工作流设计:4种模式+3个原则》(人间尘埃)
