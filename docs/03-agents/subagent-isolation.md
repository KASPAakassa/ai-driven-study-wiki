# Subagent:复杂任务的上下文隔离与职责分工

> **一句话摘要**:复杂任务需要 Subagent,不是因为"一个 Agent 不够多",而是因为**一个任务不该把全部上下文、全部职责和全部中间过程塞进同一个运行单元**。本文讲清 Subagent 的定位、任务契约、串行委派、结构化结果,以及与 Tool/Permission/Hook/Executor 的边界。
>
> **来源**:微信公众号「智趣AI笔记」《Subagent:为什么复杂任务需要上下文隔离和职责分工》,https://mp.weixin.qq.com/s/sH_LStPJ5BJqcE7mZAi6rQ(含配套 Python 最小参考实现)

## 概念:Subagent 是什么

**Subagent(子代理)** 是主 Agent 为一项受限任务或角色调用的**接口单元**:协调器显式传入当前 `SubagentTask`,接收**结构化结果**,再由主 Agent 审核、汇总并决定下一步。

!!! note "一句话定位"
    Subagent 处在**主 Agent 的任务组织之后、最终决策之前**——它不是新的主控,也不是另一种执行器。

!!! warning "隔离 ≠ 数量"
    Subagent 的核心价值首先是**隔离**,而不是数量。它不是把主上下文复制 N 份再各自发挥,而是:复杂任务目标 → 主 Agent 判断是否值得拆分 → 为子任务建立受限契约 → 协调器传入契约并回收结构化结果 → 主 Agent 审核汇总。

## 原理 1:为什么需要 Subagent——三类上下文问题

主 Agent 通常要长期维护稳定规则、用户目标、已知事实、工具观察与当前进度,全都混在**同一个上下文**里,会出现三类问题:

| 问题 | 表现 | 后果 |
| --- | --- | --- |
| **信息污染** | 局部搜索中已失效或无关的细节持续影响后续判断 | 主 Agent 被错误信息带偏 |
| **职责漂移** | 调研、约束核对、方案草拟彼此打断 | 无法说清每个结论由谁、基于什么得出 |
| **结果难验收** | 一段自由文本同时含过程、猜测和结论 | 主流程无法稳定识别哪些子目标已完成 |

!!! tip "与上下文工程的关系"
    这正是 [Context Engineering](context-engineering.md) 中"**Isolate 隔离**"杠杆的机制化实现:主 Agent 的上下文成本固定,子 Agent 在受限契约内深度工作,只交回结构化结果。

## 原理 2:委派是一份任务契约,不是一句提示词

如果主 Agent 只说"帮我审查这个模块",Subagent 不知道范围、可用事实和完成条件。**委派 = 不可变任务对象**(原文的最小参考实现):

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class StepBudget:
    max_steps: int

@dataclass(frozen=True)
class ContextItem:
    label: str
    content: str

@dataclass(frozen=True)
class SubagentTask:
    task_id: str            # 让主流程把结果关联回原职责
    role: str               # 工作视角
    objective: str          # 固定子目标
    context: tuple[ContextItem, ...]  # 主流程显式交付该任务所需事实
    budget: StepBudget      # 步骤预算
```

!!! warning "最少必要上下文的代价"
    隔离不是信息天然更少,而是要求主流程把需要交接的信息**显式化**——遗漏关键约束后得到的结论,仍可能不完整。

## 原理 3:结构化结果——局部未完成不能伪装成完成

Subagent 返回的不是"看起来合理的一段话",而是**带状态的结果**:

```python
from enum import Enum
from dataclasses import dataclass, field

class SubagentStatus(str, Enum):
    COMPLETED = "completed"
    STEP_BUDGET_EXHAUSTED = "step_budget_exhausted"
    REJECTED = "rejected"

@dataclass(frozen=True)
class Finding:
    description: str

@dataclass(frozen=True)
class SubagentResult:
    task_id: str
    status: SubagentStatus
    steps_used: int
    summary: str
    findings: tuple[Finding, ...] = ()
    reason: str | None = None
```

**模型层拒绝矛盾组合**(构造时校验):COMPLETED 必须带非空 summary 且不能带失败原因;STEP_BUDGET_EXHAUSTED 与 REJECTED 必须说明 reason;steps_used 必须是非负整数。

**协调器回收时再验证两件事**:

```python
def _validate(self, task, result):
    if result.task_id != task.task_id:
        raise ValueError("subagent result task_id does not match the delegated task")
    if result.steps_used > task.budget.max_steps:
        raise ValueError("subagent result exceeds the delegated step budget")
```

任务 ID 错配和超预算报告是**协议违例**:主流程不能猜测"它大概想表达什么",也不能悄悄改写结果。

## 代码 / 实现:最小串行委派(完整可运行版)

原文的本地最小参考实现只演示**纯内存的串行委派控制流**(不接模型/工具/权限/Hook;不实现并行、递归、工作区隔离、重试、检查点)。下面是补齐后的完整可运行版本:

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

# ---- 任务契约与结果(如上) ----
@dataclass(frozen=True)
class StepBudget: max_steps: int
@dataclass(frozen=True)
class ContextItem: label: str; content: str
@dataclass(frozen=True)
class SubagentTask:
    task_id: str; role: str; objective: str
    context: tuple[ContextItem, ...]; budget: StepBudget

class SubagentStatus(str, Enum):
    COMPLETED = "completed"
    STEP_BUDGET_EXHAUSTED = "step_budget_exhausted"
    REJECTED = "rejected"
@dataclass(frozen=True)
class Finding: description: str
@dataclass(frozen=True)
class SubagentResult:
    task_id: str; status: SubagentStatus; steps_used: int; summary: str
    findings: tuple[Finding, ...] = (); reason: str | None = None
    def __post_init__(self):
        if self.status is SubagentStatus.COMPLETED:
            if not self.summary: raise ValueError("completed must have summary")
            if self.reason is not None: raise ValueError("completed cannot carry reason")
        elif self.reason is None:
            raise ValueError(f"{self.status} must state reason")
        if not isinstance(self.steps_used, int) or self.steps_used < 0 or isinstance(self.steps_used, bool):
            raise ValueError("steps_used must be a non-negative int")

# ---- 委派计划与记录 ----
@dataclass(frozen=True)
class DelegationPlan: tasks: tuple[SubagentTask, ...]
@dataclass(frozen=True)
class DelegationRecord:
    task: SubagentTask
    result: SubagentResult

# ---- Subagent 接口与串行协调器 ----
class Subagent(Protocol):
    def run(self, task: SubagentTask) -> SubagentResult: ...

class SerialSubagentCoordinator:
    """固定串行顺序,校验回传契约并保留记录;不调用模型/工具/权限/Hook"""
    def __init__(self, subagent: Subagent):
        self._subagent = subagent
        self._validate = lambda t, r: (
            (_ for _ in ()).throw(ValueError("task_id mismatch")) if r.task_id != t.task_id else None,
            (_ for _ in ()).throw(ValueError("budget exceeded")) if r.steps_used > t.budget.max_steps else None,
        )[-1]

    def run(self, plan: DelegationPlan) -> tuple[DelegationRecord, ...]:
        records = []
        for task in plan.tasks:                       # 串行:次序稳定
            result = self._subagent.run(task)          # 直接参数只有当前 SubagentTask
            self._validate(task, result)
            records.append(DelegationRecord(task, result))
        return tuple(records)

@dataclass(frozen=True)
class MainSummary:
    status: SubagentStatus
    summaries: tuple[str, ...]
    incomplete_task_ids: tuple[str, ...]
    records: tuple[DelegationRecord, ...]

def summarize(run: tuple[DelegationRecord, ...]) -> MainSummary:
    done = [r for r in run if r.result.status is SubagentStatus.COMPLETED]
    todo = [r for r in run if r.result.status is not SubagentStatus.COMPLETED]
    status = SubagentStatus.COMPLETED if not todo else SubagentStatus.STEP_BUDGET_EXHAUSTED
    return MainSummary(status, tuple(r.result.summary for r in done),
                       tuple(r.task.task_id for r in todo), run)

# ---- 演示:一个"审查模块"的委派 ----
class DemoSubagent:
    def run(self, task: SubagentTask) -> SubagentResult:
        return SubagentResult(task_id=task.task_id, status=SubagentStatus.COMPLETED,
                              steps_used=2, summary=f"[{task.role}] {task.objective} 完成",
                              findings=(Finding("未发现越权"),))

plan = DelegationPlan(tasks=(
    SubagentTask("t1", "审计员", "核对模块边界", (ContextItem("边界", "order-svc 只读"),), StepBudget(5)),
    SubagentTask("t2", "审查员", "检查约束冲突", (ContextItem("约束", "金额必须为正"),), StepBudget(5)),
))
records = SerialSubagentCoordinator(DemoSubagent()).run(plan)
summary = summarize(records)
print("运行状态:", summary.status.value)
print("已完成:", summary.summaries)
print("未完成:", summary.incomplete_task_ids)
```

**运行结果**:两个子任务按序执行、契约与预算校验通过、返回结构化结果,主 Agent 拿到 MainSummary(已完成摘要 + 未完成 ID)再决定下一步。**局部未完成(如 STEP_BUDGET_EXHAUSTED)时,协调器仍收回其他任务结果,整次运行标记为 PARTIAL——不自动重试,只是避免一个局部失败掩盖其他成果。**

## 原理 4:执行治理仍在原边界——Subagent ≠ 授权

!!! warning "关键边界"
    委派改变的是**谁接收哪些任务材料**,不是实际动作的治理所有权。

```
Subagent ≠ Tool ≠ Permission ≠ Hook ≠ Agent Loop ≠ Executor
```

- Subagent 可能让模型在更聚焦的任务中提出建议,但**不会增加工具目录**、不会把 ALLOW/ASK/DENY 改成自己的结论、不会绕过生命周期中的 Hook;
- 子结果可以成为主 Agent 下一轮的任务材料,**却不能成为授权**;
- 真实动作仍走原 Harness 链路:`主 Agent 读取 MainSummary → 提出 ToolCall → ToolRegistry 校验 → Permission Gate(ALLOW/ASK/DENY)→ TOOL_PRE Hook → Executor → 结果回流`(详见 [生产级 Agent 9 层架构](ai-infra-layering.md) 与 [工具调用](tool-calling.md));

!!! tip "能力分工"
    Skill 解决"为当前任务装入哪份流程说明";Subagent 解决"是否为一项局部工作建立独立任务上下文";Tool、Permission、Hook 与 Executor 仍分别治理外部能力、是否允许、生命周期门禁与实际动作。

## 实践 / 应用:什么任务值得委派

**适合委派的条件**(全部满足才拆):

1. **目标可独立表达**:能用一句话说明要回答什么;
2. **输出可检查**:主 Agent 能说明希望收回摘要、发现项还是未决问题;
3. **上下文可收窄**:不需要把全部聊天历史复制进去;
4. **边界可限制**:角色、输入材料和步骤预算可以事先说清;
5. **协调成本值得**:拆分带来的清晰度 > 额外输入、等待和汇总成本。

**不值得拆的情形**(拆了反而多一次上下文复制和结果解释):

- 一个确定的小动作;
- 需要持续往返才能理解的高耦合问题;
- 无法定义交付物的"泛泛看看";
- 必须立即由用户决定的高风险动作。

**工程建议**:

- 先定义子任务的**输入、输出和主流程责任**,再把具体产品能力映射到这些边界;
- 不要从"产品支持 Subagent"推出"所有委派都是安全的";更不要从"上下文隔离"推出"文件、网络和凭据已隔离";
- 产品差异(Claude Code Subagents 的工具可见范围、权限交互、嵌套行为)属于**外部可变事实**,接入前逐项核验官方文档,以官方公开能力为准;
- 用测试锁定"委派不会绕过 Harness":校验 task_id、预算、状态组合的协议违例应直接失败。

## 总结

- Subagent 的价值是**隔离**(信息污染/职责漂移/结果难验收),不是数量;
- 委派 = **任务契约**(task_id/role/objective/context/budget),协调器显式传入、结构化回收;
- 结果**带状态**(COMPLETED/STEP_BUDGET_EXHAUSTED/REJECTED),协议违例直接失败,局部未完成不伪装成完成;
- **Subagent ≠ 授权**:执行治理仍在 ToolRegistry/Permission Gate/Hook/Executor 原边界;
- 委派与否看五条件,拆错比不拆更糟;产品能力按官方文档核验。

## 延伸阅读

- 站内:[Context Engineering](context-engineering.md)(Isolate 杠杆)、[核心组件](agent-core-components.md)、[多 Agent 协作](multi-agent.md)、[生产级 Agent 9 层架构](ai-infra-layering.md)、[工具调用](tool-calling.md)
- 外部:原文(智趣AI笔记);Claude Code 官方 Subagents 文档(工具可见范围/权限交互/嵌套行为以官方为准);原始资料存档于 `docs/inbox/subagent-source.md`
