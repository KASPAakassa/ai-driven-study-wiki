# 经典多智能体系统:从 Agent 分类到涌现智能(微软 AI 课程 23 章)

> **一句话摘要**:LLM Agent 之前,多智能体系统(MAS)已是 AI 的重要分支——基于**涌现智能**(许多相对简单 agent 的组合行为产生更复杂的整体智能)。经典 MAS 的 Agent 定义(活在环境中、可感知、可行动)、分类(反应式/慎思式、静态/移动、被动/主动/认知)、建模工具(NetLogo)与通信协议(KIF/KQML)是理解现代多 Agent 协作的**理论源头**。本文整理自微软《AI for Beginners》第 23 章,并与站内现代多智能体内容对照。
>
> **来源**:微软开源课程《AI for Beginners》第 23 章 Multi-Agent Systems(作者:Dmitry Soshnikov),https://github.com/microsoft/AI-For-Beginners/blob/main/lessons/6-Other/23-MultiagentSystems/README.md;原始全文存档于 `references/ai-for-beginners/lessons/6-Other/23-MultiagentSystems/README.md`

## 概念:涌现智能与 Agent 定义

!!! tip "核心思想**
    许多相对简单的 agent 的组合行为,可以产生系统整体的更复杂(更智能)行为——基于 **Collective Intelligence(集体智能)、Emergentism(涌现主义)、Evolutionary Cybernetics(进化控制论)**,高层次系统从低层次系统正确组合中获得增值(元系统跃迁原则)。

**Agent 定义(经典)**:一个活在**环境(environment)**中的实体,能**感知(perceive)**环境并**行动(act upon)**。这是非常宽泛的定义——现代 LLM Agent(工具调用/ReAct)是这个定义的延续(感知=上下文,行动=工具调用)。

## 原理:Agent 分类、建模与通信

### 1. Agent 分类(三维度)

| 维度 | 类型 | 说明 |
| --- | --- | --- |
| **推理能力** | **Reactive(反应式)** | 简单请求-响应行为 |
| | **Deliberative(慎思式)** | 逻辑推理和/或规划能力(现代 Agent 的 ReAct/Plan-and-Execute 即此) |
| **代码位置** | Static | 工作在固定网络节点 |
| | Mobile | 代码可在网络节点间移动 |
| **行为** | Passive | 无特定目标,只对外部刺激反应 |
| | Active | 追求某些目标 |
| | Cognitive | 复杂规划与推理 |

!!! note "与现代 LLM Agent 的对照"
    现代 Agent(站内 [AI Agent 入门](../03-agents/agent-intro.md))本质是 **Deliberative + Active/Cognitive** 的组合——本课程的经典分类是理解现代 Agent 位置的理论框架。

### 2. 多智能体建模:NetLogo

NetLogo 是经典的多智能体建模环境(基于 Logo 语言):

- **对象**:Agents(turtles,可移动)/ Patches(agent 生活的方格区域)/ Observer(控制世界的唯一 agent);
- **并行执行**:turtle 模式或 patch 模式的代码被所有 agent **同时并行执行**——写少量个体行为代码,产生整体复杂行为;
- **Models Library**:内置大量可运行模型(生物群集、交通、社交派对等)。

**Flocking(鸟群)经典案例**——复杂集体行为由每个 agent 仅观察短距离邻居的三条简单规则涌现:

1. **Alignment(对齐)**:朝邻居平均航向转向;
2. **Cohesion(凝聚)**:朝邻居平均位置转向(远距吸引);
3. **Separation(分离)**:离得太近时移开(近距排斥)。

!!! tip "可调参数实验**
    把 viewing range 降到 0(所有鸟变盲)→ 群集停止;把 separation 降到 0 → 所有鸟聚成直线。**个体规则 × 观察范围 = 整体行为**——这就是涌现智能的最小演示。

### 3. Deliberative Agents 与通信协议

慎思式 agent(能推理和规划)的例子:个人 agent 接受"预订假期旅行"指令 → 联系互联网上多个 agent → 协商航班/酒店价格 → 计划确认后预订。为此 agent 需要**通信**:

- **标准知识交换语言**:KIF(Knowledge Interchange Format)、KQML(Knowledge Query and Manipulation Language)——基于 **Speech Act theory(言语行为理论)**;
- **协商协议**:基于不同**拍卖类型**(auction types)。

## 代码 / 实现:Flocking 三规则的最小演示(纯 Python)

把"三条局部规则涌现群体行为"落成可运行演示(一维简化版):

```python
import random

# —— Flocking 三规则的最小实现(1D 简化:鸟在一条线上)——
def flock_step(birds, view_range=3, sep_dist=1.0):
    """每只鸟只观察短距离邻居,应用三规则更新速度(简化 1D)"""
    new = []
    for i, x in enumerate(birds):
        neighbors = [b for j, b in enumerate(birds) if j != i and abs(b - x) <= view_range]
        if not neighbors:
            new.append(x)                       # 看不见邻居 → 保持
            continue
        avg = sum(neighbors) / len(neighbors)
        # Alignment(对齐):朝平均位置微调 + Cohesion(凝聚):靠近邻居
        # Separation(分离):离太近则远离
        if abs(x - avg) < sep_dist and len(neighbors) >= 2:
            x += 0.3 if x < avg else -0.3       # 分离:保持间距
        else:
            x += 0.1 * (1 if avg > x else -1)   # 凝聚:向平均靠拢
        new.append(x)
    return new

birds = [random.uniform(-10, 10) for _ in range(20)]
print("初始:", [round(b, 1) for b in birds])
for _ in range(10):
    birds = flock_step(birds)
print("10 轮后:", [round(b, 1) for b in birds])
print("范围:", round(min(birds), 1), "~", round(max(birds), 1), "(初始分散 → 逐渐聚集)")
```

## 实践 / 应用:经典 MAS 的现实应用与知识库对照

### 经典 MAS 的应用场景

- **游戏**:NPC 的 AI(每个 NPC 是智能 agent);
- **视频制作**:渲染含人群的复杂 3D 场景(多智能体仿真);
- **系统建模**:模拟复杂系统行为——如预测 COVID-19 全球传播、建模城市交通对规则变化的反应;
- **复杂自动化**:每个设备作为独立 agent,系统更少单体化、更健壮。

### 与站内现代多智能体内容的对照

| 经典(本章) | 现代(站内) |
| --- | --- |
| Reactive/Deliberative agent 分类 | [AI Agent 入门](../03-agents/agent-intro.md)(ReAct 循环) |
| 通信协议 KIF/KQML/拍卖 | [多智能体协作设计](../03-agents/agent-team-room-collaboration.md)(inbox/草稿板/令牌) |
| NetLogo 多 agent 建模 | [多 Agent 协作](../03-agents/multi-agent.md)(编排/辩论模式) |
| 涌现智能(局部规则→整体行为) | [云端软件工厂](../08-harness/cloud-software-factory.md)(Factory 自治光谱) |

!!! tip "经典 vs 现代的本质差异"
    经典 MAS 的 agent 是**简单规则驱动**(反应式为主);现代 LLM Agent 是**推理驱动的慎思式 agent**——但"多 agent 通信、协商、涌现协作"的核心问题一脉相承。理解经典分类,能帮你看清现代 Agent 在设计空间中的位置。

## 总结

- **涌现智能**:许多简单 agent 的组合产生复杂整体行为(集体智能/涌现主义/进化控制论);
- **Agent 分类**:反应式 vs 慎思式、静态 vs 移动、被动 vs 主动 vs 认知;
- **NetLogo 建模**:turtles/patches/observer 并行执行;Flocking 三规则(对齐/凝聚/分离)是涌现智能的最小案例;
- **慎思式 agent 通信**:KIF/KQML + 协商协议(拍卖);
- **一句话**:LLM Agent 之前,多智能体系统已经回答了"多个 agent 如何协作"——局部规则、通信协议与涌现,至今仍是现代多 Agent 协作的理论源头。

## 延伸阅读

- 课程原文:https://github.com/microsoft/AI-For-Beginners/blob/main/lessons/6-Other/23-MultiagentSystems/README.md;NetLogo:https://ccl.northwestern.edu/netlogo/;KIF/KQML:知识交换格式与知识查询操作语言
- 站内:[AI Agent 入门](../03-agents/agent-intro.md)、[多 Agent 协作](../03-agents/multi-agent.md)、[多智能体协作设计](../03-agents/agent-team-room-collaboration.md)、[微软 AI for Beginners 课程导读](../01-ai-basics/microsoft-ai-for-beginners.md)
