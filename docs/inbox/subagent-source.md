# 原始资料:Subagent:为什么复杂任务需要上下文隔离和职责分工

> 来源:微信公众号「智趣AI笔记」,《Subagent:为什么复杂任务需要上下文隔离和职责分工》
> 原文链接:https://mp.weixin.qq.com/s/sH_LStPJ5BJqcE7mZAi6rQ
> 抓取日期:2026-08-09;状态:已整理为正式文章 docs/03-agents/subagent-isolation.md
> 说明:原文含配套 Python 最小参考实现(纯内存串行委派控制流)

---

复杂任务需要 Subagent，不是因为“一个 Agent 不够多”，而是因为一个任务不该把全部上下文、全部职责和全部中间过程塞进同一个运行单元。
设想一个代码变更任务：既要检索模块边界，又要核对既有约束，再要整理修改方案。若主 Agent 把搜索碎片、临时猜测、用户目标和每一步结果一直堆进同一段上下文，它很容易从“解决当前问题”漂移成“回顾所有曾经看过的信息”。此时再开几个聊天窗口并不会自动带来协作；关键是 Harness 能否为子任务定义边界、限制输入、回收结构化结果，并让主 Agent 保留最终判断。
Subagent 是主 Agent 为一项受限任务或角色调用的接口单元：协调器显式传入当前 SubagentTask，接收结构化结果，再由主 Agent 审核、汇总并决定下一步。
配套 Python 标准库本地最小参考实现只演示纯内存的串行委派控制流。它不接入真实模型、Claude Code、HTTP、Shell、MCP、数据库、工具执行器、权限系统或 Hook Runner；不实现并行、递归委派、工作区隔离、自动重试和检查点。它证明的是局部对象契约和控制流，不是生产安全、产品内部实现或完整兼容性保证。

Subagent 的核心价值首先是隔离，而不是数量
主 Agent 通常要维护稳定规则、用户目标、已知事实、工具观察与当前进度。所有内容都长期混在一个上下文中，会出现三类问题：
信息污染：局部搜索中已失效或无关的细节持续影响后续判断；

职责漂移：调研、约束核对、方案草拟彼此打断，无法清楚说明每个结论由谁、基于什么得出；

结果难以验收：一段自由文本同时包含过程、猜测和结论，主流程无法稳定识别哪些子目标已完成。

Subagent 不是把主上下文复制 N 份再让它们各自发挥。更准确的关系是：

复杂任务目标→ 主 Agent 判断是否值得拆分→ 为子任务建立受限契约→ 协调器将当前任务契约直接传给 Subagent 并回收结构化结果→ 主 Agent 审核并汇总
这里的边界是任务级直接参数边界：协调器每次只传入当前 、SubagentTask，不会自动补充其他任务的材料、摘要或发现。它不代表独立实例、私有状态隔离、深复制、独立进程、会话、工作目录、网络隔离、凭据隔离或沙箱；更不能把“自动传入的上下文更少”包装成“外部动作更安全”。

Subagent 在 Harness 中的位置
Subagent 处在主 Agent 的任务组织之后、最终决策之前。它不是新的主控，也不是另一种执行器：

主 Agent / Harness→ DelegationPlan→ SubagentTask→ Subagent→ SubagentResult→ DelegationRecord→ MainSummary→ 主 Agent 的下一步决定
各组件的职责应保持清楚：
机制
负责什么
不负责什么
主 Agent
拆分、委派、审核、汇总和最终决定
不把子结果当成天然事实或授权
SubagentTask
固定一个子目标的角色、目标、输入与预算
协调器不自动附加全部主任务历史或其他任务材料
Subagent
在一份受限任务契约内返回结构化结果
不修改主任务状态，不自行再委派
SerialSubagentCoordinator
固定串行顺序，校验回传契约并保留记录
不调用模型、工具、权限或 Hook
MainSummary
显示已完成摘要与未完成任务
不直接执行任何后续动作
因此：

Subagent≠ Tool≠ Permission≠ Hook≠ Agent Loop≠ Executor
Subagent 可能让模型在一个更聚焦的任务中提出建议；它不会增加工具目录，不会把 ALLOW / ASK / DENY 改成自己的结论，也不会绕过固定生命周期中的 Hook。委派改变的是谁接收哪些任务材料，不是实际动作的治理所有权。
先判断：这个任务值得委派吗
不是任务越复杂，拆得越细越好。一个子任务适合委派，至少要满足以下条件：
目标可独立表达：能用一句话说明它要回答什么；

输出可检查：主 Agent 能说明希望收回摘要、发现项还是未决问题；

上下文可收窄：不需要把全部聊天历史复制进去；

边界可限制：角色、输入材料和步骤预算可以事先说清；

协调成本值得：拆分带来的清晰度大于额外输入、等待和汇总成本。

反过来，下列情形通常不值得拆：一个确定的小动作、需要持续往返才能理解的高耦合问题、无法定义交付物的“泛泛看看”，以及必须立即由用户决定的高风险动作。把它们拆成 Subagent，只会让主流程多出一次上下文复制和结果解释，而不会减少真正的不确定性。

委派不是一句提示词，而是一份任务契约
如果主 Agent 只说“帮我审查这个模块”，Subagent 不知道范围、可用事实和完成条件；主 Agent 收回一段文本后，也无法判断它是否对应原任务。本地最小参考实现将委派建模为不可变对象：

@dataclass(frozen=True)class StepBudget: max_steps: int @dataclass(frozen=True)class ContextItem: label: str content: str @dataclass(frozen=True)class SubagentTask: task_id: str role: str objective: str context: tuple[ContextItem, ...] budget: StepBudget
task_id 让主流程将结果关联回原职责；role 表达工作视角；objective 固定子目标；context 由主流程显式交付该任务所需事实，协调器不会自动补充其他任务材料；StepBudget 则限制教学快照中允许报告的步骤数量。
这里的 max_steps 不是 Token、费用、时长、模型调用次数或真实工具调用上限。它只让控制流能够表达：“该子任务报告的步骤数是否仍在主流程分配的预算内。”真正的资源治理需要计量具体 Runtime 和外部动作，不能由这个值对象替代。
最少必要上下文也有代价：Subagent 不会知道主 Agent 没有传入的事实。隔离不是信息天然更少，而是要求主流程把需要交接的信息显式化；遗漏关键约束后得到的结论，仍可能不完整。

最小串行委派：顺序确定，不隐式共享结果
配套实现只覆盖同步串行路径。Subagent 通过一个窄 Protocol 注入协调器：

class Subagent(Protocol): def run(self, task: SubagentTask) -> SubagentResult: ...
协调器按 DelegationPlan.tasks 的既定顺序调用：

任务 A 的专属契约→ Subagent.run(A)→ 校验 task_id 与步骤预算→ 记录 A 的 DelegationRecord→ 任务 B 的专属契约→ Subagent.run(B)→ 校验并记录 B→ 主 Agent 汇总全部记录
核心代码保持很短：

for task in plan.tasks: result = self._subagent.run(task) self._validate_result(task, result) records += (DelegationRecord(task, result),)
串行只表示 A、B、C 的调用次序稳定。协调器在构造时注入一个Subagent 实例，并在循环中按顺序复用这个对象调用run(task)；role 是任务字段，不会创建 A、B、C 三个不同实体。每次run() 的直接参数只有当前SubagentTask，A 的context、summary 或findings 不会自动注入 B；主流程保留DelegationRecord，但不会自动把前一项材料塞给下一项。该实现不复制任务对象，因此不能证明实例没有跨调用私有状态，更不构成会话、进程、目录、网络或凭据隔离。
这个最小参考实现只覆盖确定的串行调用顺序，不需要线程、协程、队列或并发预算。

结构化结果：局部未完成不能伪装成完成
Subagent 返回的不是“看起来合理的一段话”，而是带状态的结果：

class SubagentStatus(str, Enum): COMPLETED = ”completed” STEP_BUDGET_EXHAUSTED = ”step_budget_exhausted” REJECTED = ”rejected” @dataclass(frozen=True)class SubagentResult: task_id: str status: SubagentStatus steps_used: int summary: str findings: tuple[Finding, ...] = () reason: str | None = None
模型层在构造时拒绝矛盾组合：COMPLETED 必须带非空 summary 且不能带失败原因；STEP_BUDGET_EXHAUSTED 与 REJECTED 必须说明 reason；steps_used 必须是非负、非布尔整数。
协调器回收时还验证两件事：

if result.task_id != task.task_id: raise ValueError(”subagent result task_id does not match the delegated task”)if result.steps_used > task.budget.max_steps: raise ValueError(”subagent result exceeds the delegated step budget”)
任务 ID 错配和超预算报告是协议违例：主流程不能猜测“它大概想表达什么”，也不能悄悄改写结果。教学实现直接抛出 ValueError，且不会启动后续任务。
而 STEP_BUDGET_EXHAUSTED 或 REJECTED 是已经被定义的局部状态，不等于整个任务必须立刻消失。对于预先声明、彼此独立的任务，协调器仍会收回其他任务的结果，最终把整次运行标记为 PARTIAL。这不是自动恢复或重试；只是避免一个局部未完成掩盖其他已获得的材料。
主 Agent 汇总结果，执行治理仍在原边界
协调器将每一对“任务契约 + 子结果”保留为 DelegationRecord。主流程最后再显式生成总览：

def summarize(run: DelegationRun) -> MainSummary: completed_records = tuple( record for record in run.records if record.result.status is SubagentStatus.COMPLETED ) incomplete_records = tuple( record for record in run.records if record.result.status is not SubagentStatus.COMPLETED ) return MainSummary( run.status, tuple(record.result.summary for record in completed_records), tuple(record.task.task_id for record in incomplete_records), run.records, )
全部子任务完成时，运行是 COMPLETED；存在预算耗尽或拒绝结果时，则是 PARTIAL。MainSummary 收录已完成摘要和未完成任务 ID，但不替主 Agent 接受任何结论，更不会把 Finding 变成工具调用。
真实动作仍应走原有 Harness 链路：

主 Agent 读取 MainSummary→ 模型提出文本或 ToolCall→ ToolRegistry 校验名称与参数→ Permission Gate: ALLOW / ASK / DENY→ TOOL_PRE Hook→ Executor→ ToolResult 回流 Agent Loop
子结果可以成为主 Agent 下一轮的任务材料，却不能成为授权。Skill 解决“为当前任务装入哪份流程说明”；Subagent 解决“是否为一项局部工作建立独立任务上下文”；Tool、Permission、Hook 与 Executor 仍分别治理外部能力、是否允许、生命周期门禁与实际动作。

Claude Code Subagents 的公开边界
Claude Code Subagents 的配置、工具可见范围、权限交互、嵌套行为和版本差异都属于外部可变事实。需逐项核验 Claude Code Subagents、overview、permissions 官方页面中公开支持的调用方式、任务或上下文说明、工具可见范围、权限交互、嵌套、配置和版本限制；页面不可访问、更新或不能确认的产品表述须删除，或降级为本地最小参考实现的设计原则。
配套的 Subagent Protocol 与 SerialSubagentCoordinator 是受限本地接口模型：只有一份内存任务契约、同步 run() 调用、结构化回传、任务 ID 与步骤预算校验，以及末尾显式汇总。它没有复刻 Claude Code 的内部调度、会话管理、工具隔离、权限继承、模型选择或执行环境；也没有声称与任何产品或规范完全兼容。
对工程设计而言，更稳定的原则是：先定义子任务的输入、输出和主流程责任，再把具体产品能力映射到这些边界。不应从“产品支持 Subagent”推出“所有委派都是安全的”，更不能从“上下文隔离”推出“文件、网络和凭据已隔离”。
用测试证明“委派不会绕过 Harness”
在项目根目录运行：

python -B -m unittest discover -s ”articles/agent-harness全景/code/18-subagents” -p ”test_subagents.py” -v
当前 5 个 unittest 测试覆盖：
空字段、非法步骤预算、空计划、重复任务 ID 与状态字段矛盾都会被拒绝；StepBudget 和 steps_used 的布尔、浮点、字符串、None 与范围边界都有覆盖；

两个任务严格按 A → B 的顺序调用；协调器传给 B 的任务契约只含 B 已声明的 ContextItem，不自动含 A 的上下文或摘要；

steps_used == max_steps 可以完成，steps_used == 0 合法；任务 ID 错配或超过预算会阻止后续任务；

预算耗尽或拒绝会保留局部原因，其他独立任务仍可运行，最终总览为 PARTIAL；

AST 边界拒绝生产模块中的动态加载、网络、命令执行、文件写入与并发依赖。

测试中的 _ScriptedSubagent 是内存替身，不调用模型，也不执行工具。测试不能证明真实模型遵从任务契约、同一 Subagent 实例没有跨调用私有状态、任务对象已深复制、生产系统确实隔离会话或环境、产品权限正确继承，或外部副作用安全可控；它只证明本篇教学快照将委派限制在结构化、串行、可校验的 Harness 控制流中。

小结
Subagent 的工程价值不在于把一个任务变成更多模型调用，而在于让 Harness 有机会明确分开：谁负责哪项局部工作、收到哪些事实、最多消耗多少步骤、如何报告未完成，以及谁最终决定采纳和执行。
最小闭环可以写成：

主 Agent 拆分→ 受限任务契约→ 显式的任务级输入→ 结构化结果→ 主 Agent 审核与汇总
这条链路不会替代 Tool、Permission、Hook 或 Agent Loop。它只把复杂任务中的上下文与职责边界变成可测试的对象。下一篇将讨论：当多个任务都独立且值得委派时，为什么不能简单“开几个线程”，而要处理 Fan-out、Fan-in、并发上限、预算与部分失败。