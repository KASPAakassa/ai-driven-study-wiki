# Gate 模式详解:在 Agent 流水线中植入人工确认点

> **一句话摘要**:Gate 模式是"用 Agent 持续交付"的关键控制手段——**在不可逆动作之前,插入一个人工确认点,人必须理解并确认方向/方案正确后才放行**。它回答一个核心问题:工具越强,人该在哪些环节停下来认真理解?Gate 不是审批瓶颈,而是**认知债务的转移点**:要么人前期主动消化,要么系统后期被动暴露。本文专门讲透:gate 是什么、三要素、语义性判定、放哪、怎么治理粒度,以及与其他控制机制(权限审批/hooks/checkpoint/abstention)的区别。
>
> **来源**:微信公众号「flyer」《用 Agent 持续交付:控制认知复杂度》中提炼的 Gate 控制模式,https://mp.weixin.qq.com/s/Il5Cr_O5EiG1hLptnAqh8A;原始资料存档于 `docs/inbox/agent-gate-pattern-source.md`;实践背景见站内 [用 Agent 持续交付:控制认知复杂度](agent-cognitive-complexity-gates.md)

## 概念:Gate 是什么

!!! tip "一句话定义**
    **Gate = 在流水线中预先指定的人工确认点:Agent 执行到该点必须暂停,由人理解并确认后才能继续。** 它不是"每次都问",而是"在特定条件下、特定位置、用轻量方式确认一次"。

### 为什么需要 Gate:认知债务与错误成本

1. **错误成本指数上升**:软件变更的错误成本随阶段指数增长——设计/规范分钟级 → 编码小时级 → 上线不可逆。**校验前移到最便宜的阶段**(设计期),关键节点暂停做对抗性 review;
2. **Agent 没有"理解责任"**:agent 能高效执行,但它不会为"方向是否正确"负责——它只对你给的目标负责;
3. **认知债务不会消失,只会转移**:要么人在前期主动消化(在 gate 处理解),要么系统在后期被动暴露(上线事故)。

!!! warning "Gate 的本质**
    Gate 不是不信任 agent,而是**把"理解核心决策"的责任明确分配给人类**。认知负担不是越少越好——**把该承担的认知负担放到最低成本阶段**,才是 gate 模式的精髓。

## 原理:Gate 的三要素与判定

### 1. Gate 三要素

| 要素 | 内容 | 例子 |
| --- | --- | --- |
| **触发条件** | 什么变更/事件触发 gate(必须是清晰可判定的) | "语义性变更才触发" |
| **判定标准** | gate 处人要确认什么(聚焦、轻量) | "确认对抗性推演自洽 + 接口/行为 delta" |
| **位置** | gate 放在流水线哪一步(不可逆动作之前) | "spec 完成后、编码前" |

### 2. 语义性判定速查表(触发条件的具体化)

| 变更类型 | 需要 gate? | 说明 |
| --- | --- | --- |
| 新增/修改**接口契约** | ✅ | 对外边界变化 |
| **状态机 / 持久化语义** | ✅ | 状态迁移与存储语义 |
| **权限 / 安全边界** | ✅ | 信任边界变化 |
| **对外行为变更** | ✅ | 用户可感知变化 |
| 纯文档 / 注释 | ❌ | 无语义变化 |
| 为既有行为补测试 | ❌ | 只加验证不加行为 |
| 不改语义的重构 | ❌ | 行为等价 |
| 构建脚本 / 依赖升级 | ❌ | 不改变业务语义 |
| **拿不准** | **默认走 gate** | 向 human 确认,不赌 |

!!! tip "为什么判定表要写死**
    把触发条件写进 AGENTS.md(而不是"重要决策需要确认"),**Agent 自己能判断是否需要暂停,人不需要全程盯着**——gate 从"人的主观抽查"变成"流水线的既定关卡"。

### 3. Gate 放哪:不可逆动作之前

| 场景 | gate 位置 | 确认什么 |
| --- | --- | --- |
| **Coding Agent**(单次变更) | spec 完成后、编码前 | 对抗性推演自洽 + 接口/行为 delta |
| **Research Agent**(hermes 类) | 每轮方向确认(Align) | 下一轮改进方向 |
| **通用原则** | 任何**不可逆动作**之前(上线/外发/大额/删数据) | 方向与方案正确 |

!!! note "两种 gate 的位置差异(原则一致)**
    Coding agent 的 gate 在**具体变更的 spec 确认**环节;hermes 的 gate 在**每轮 research 的方向确认**环节。位置不同,原则一致:**在不可逆动作之前,人必须确认方向正确**。

## 代码 / 实现:Gate 判定器与粒度复盘(纯 Python)

### 1. Gate 判定器(对应语义性速查表)

```python
# —— Gate 判定:按变更类型决定是否需要人工确认点 ——
SEMANTIC = {"接口契约", "状态机", "持久化语义", "权限边界", "安全边界", "对外行为"}

def need_gate(change_type: str, unsure: bool = False) -> str:
    if unsure:
        return "需要(拿不准默认走 gate,向 human 确认)"
    if change_type in SEMANTIC:
        return "需要(语义性变更,human 确认后放行)"
    return "不需要(非语义性,直接进入下一步)"

for t in ["接口契约", "纯文档", "补测试", "不改语义重构", "构建脚本"]:
    print(f"  {t:10} → {need_gate(t)}")
print(f"  {'拿不准':10} → {need_gate('?', unsure=True)}")
assert need_gate("接口契约").startswith("需要")
assert need_gate("纯文档").startswith("不需要")
assert need_gate("?", unsure=True).startswith("需要")
print("代码验证通过 ✔")
```

### 2. Gate 粒度复盘(判断门槛是否合适)

```python
# —— 定期复盘 gate 粒度:频繁触发无实质变化 → 门槛太低;上线暴露问题 → 覆盖不足 ——
def review_gate(frequent_triggers_no_change: bool, post_release_issues: bool) -> str:
    if frequent_triggers_no_change:
        return "门槛太低:gate 频繁触发但每次无实质变化 → 合并或删除(或收紧触发条件)"
    if post_release_issues:
        return "覆盖不足:上线后频繁暴露设计问题 → 补充 gate / 扩展语义性判定范围"
    return "粒度合适:gate 轻量且能拦住实质问题"

print(review_gate(True, False))
print(review_gate(False, True))
assert review_gate(True, False).startswith("门槛太低")
assert review_gate(False, True).startswith("覆盖不足")
print("代码验证通过 ✔")
```

## 实践 / 应用:怎么落地与治理

### Gate 落地三步

1. **写进 AGENTS.md**:把触发条件 + 判定速查表写成流程的一部分(变更流程第 3 步),agent 自己判断何时暂停;
2. **保持轻量**:gate 只聚焦语义性决策(对抗性推演是否自洽 + 接口/行为 delta)——不是全 spec 审批,human 确认"通过"即继续;不通过回到 design/spec 修正;
3. **定期复盘粒度**:见粒度复盘逻辑——门槛太低就收紧,覆盖不足就补充。

### 与其他控制机制的区别

| 机制 | 谁触发 | 目的 | 与 Gate 的关系 |
| --- | --- | --- | --- |
| **权限审批(permission)** | 工具调用级 | 拦截危险操作 | gate 是它的"流程级"升级(确认方案而非单次命令) |
| **Hooks(PreToolUse)** | 事件切面 | 确定性拦截/记录 | gate 可由 hook 触发,但 gate 要人**理解语义** |
| **Checkpoint(回退)** | 状态快照 | 可回滚 | 是 gate 的后备(确认错了能退),不替代确认 |
| **Agentic Abstention** | agent 自判停止 | agent 判断该不该继续 | 互补:abstention 让 agent 该停时停,gate 规定人**必须**介入处 |
| **HITL(人工接管)** | 高风险操作 | 副作用前暂停 | gate 是 HITL 的"方案级"形态 |

!!! tip "与站内其他文章的呼应**
    - [用 Agent 持续交付](agent-cognitive-complexity-gates.md):本模式的实践来源(8 步流程 + 判定表 + 复盘);
    - [企业 Agent 工程化(二)](../../06-enterprise/ontology-agent-adoption/enterprise-agent-recovery-handoff.md):gate 是"后果半径四档"的人工确认点实现;
    - [给 Coding Agent 立规矩](agent-rules-agents-md.md):把判定表写进 AGENTS.md = 规则机制的实例;
    - [Agentic Abstention](../../03-agents/agentic-abstention.md):agent 自判停止 vs 人规定 gate——同一"停止判断"问题的两侧。

## 总结

- **Gate 三要素**:触发条件(语义性判定表)+ 判定标准(聚焦轻量)+ 位置(不可逆动作之前);
- **语义性 vs 非语义性**:接口契约/状态机/持久化/权限/对外行为需要 gate;文档/补测试/等价重构/构建脚本不需要;**拿不准默认走 gate**;
- **两条纪律**:①判定表写进 AGENTS.md(agent 自判暂停,人不用全程盯);②gate 保持轻量聚焦语义,定期复盘粒度(门槛太低就收,覆盖不足就补);
- **一句话**:认知复杂度不会消失,只会转移——**gate 就是人主动选择"在哪里消化"的控制点**;在不可逆动作之前,人必须确认方向正确。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/Il5Cr_O5EiG1hLptnAqh8A;原始资料存档于 `docs/inbox/agent-gate-pattern-source.md`
- 站内:[用 Agent 持续交付](agent-cognitive-complexity-gates.md)(实践背景)、[给 Coding Agent 立规矩](agent-rules-agents-md.md)、[企业 Agent 工程化(二)](../../06-enterprise/ontology-agent-adoption/enterprise-agent-recovery-handoff.md)、[Agentic Abstention](../../03-agents/agentic-abstention.md)、[AI 协作规则设计](../../03-agents/agent-collaboration-rules.md)
