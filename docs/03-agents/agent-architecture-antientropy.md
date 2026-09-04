# Agent 架构反熵增:复杂度、技术债与架构演进的长期治理

> **一句话摘要**:架构师的日常不是在学新名词,而是在几个看似独立的概念之间建立连接。复杂度治理、技术债、架构演进——在 Agent 项目的设计文档里各占一个 section,但它们实际上指向同一个核心问题:**怎样让 Agent 在复杂环境中持续做出正确的决策?** 本文把三者的关系与落地方法讲透:复杂度不会自己消失,它只会换个地方收利息;技术债不是罪,装作没有才是;架构不是一次画完的图,而是一套允许系统长大的骨架。
>
> **来源**:微信公众号「岚岚」《Agent架构反熵增:系统复杂度的长期治理》,https://mp.weixin.qq.com/s/LmpSWgL-O9aXs_QBwlnwmg;原始资料存档于 `docs/inbox/agent-antientropy-source.md`

## 概念:Agent 系统的复杂度为什么涨得比传统系统快

Agent 系统的复杂度来源比传统系统更"纠缠":**Prompt 版本、工具数量、模型路由、评估集、权限策略**会互相缠绕——改一个工具描述可能影响路由判断,加一条规则可能吃掉评估集覆盖率,调一次权限可能破坏已有流程。复杂度不是线性增长,而是互相放大。

!!! tip "三个概念的关系(不是线性)**
    ```
    复杂度治理 → 基础(没有它,后面都是空中楼阁)
    技术债      → 工程化保障(把复杂度治理的能力可靠地落地)
    架构演进    → 质量的最后一道防线(确保整个链路不在最后一步翻车)
    ```

## 原理:三个治理维度的落地

### 1. 复杂度治理:模块边界、版本化、废弃机制、评审

靠四件事对抗熵增:**模块边界、配置版本化、废弃机制、架构评审**。外加三个"每"问(每次变更都要回答):

| 每问 | 目的 |
| --- | --- |
| 每新增一个工具,是否已有能力可复用? | 防止重复造轮子(工具数量是 Agent 复杂度的大头) |
| 每新增一条特殊规则,三个月后谁维护? | 防止无人区规则(规则是有维护成本的) |
| 每绕过一次标准流程,记录技术债了吗? | 防止"临时方案"变成永久的坑 |

!!! warning "复杂度不会自己消失"
    **它只会换个地方收利息。** 今天省下的架构评审,明天变成排查事故的加班;今天塞进 Prompt 的临时规则,三个月后变成没人敢动的黑盒。

### 2. 技术债:Agent 技术债比传统系统更隐蔽

一个临时 Prompt、一段没有评估的路由规则、一个过宽的工具权限——**短期都能跑,长期都会变成事故入口**。Agent 技术债的隐蔽性在于:它不报错,只在某个边界条件下悄悄失效。

**债务台账**(治理工具):每个债项记录七要素——问题是什么、风险多大、触发条件、还债成本、负责人、截止时间(以及可选的:评估集/日志/权限/错误处理 的关联项)。**每个迭代固定留出还债预算**,优先还:评估集、日志、权限、错误处理——这四类是 Agent 事故最集中的入口。

!!! warning "技术债不是罪,装作没有才是"
    **系统不会忘,你只是暂时没收到报警。** 承认技术债并记入台账,是把它变成可管理项的第一步;假装不存在,它只会在你最忙的时候爆出来。

### 3. 架构演进:从"可替换性"开始设计

Agent 技术栈的换件频率远高于传统系统:**模型会换、框架会换、向量库会换、工具协议会升级**。如果核心业务逻辑和这些实现绑死,未来每次升级都是拆房重建。

**演进友好的架构**四个要求:

1. **分层**:接口、配置、状态、执行引擎分离——换实现不动核心逻辑;
2. **ADR 记录**:关键决策有架构决策记录(决策/背景/备选/后果),后人知道"为什么"而不是只看"是什么";
3. **迁移路径**:换件时有双写(新旧并行写入)或影子验证(新旧并行运行对比)——不是"停机切换",而是"平滑过渡";
4. **允许长大的骨架**:架构不是一次画完的图,而是一套**允许系统长大的骨架**——骨架歪了,长得越快越疼。

!!! note "与站内 [AI Coding Harness 设计经验](../07-agent-coding/experience/ai-coding-harness-design.md) 的呼应"
    "护栏随需求生长"是运行期治理;本文是**架构期治理**——护栏长出来之前,先想清楚骨架允不允许它长。两者是同一反熵增原则的两个阶段。

## 代码 / 实现:技术债台账管理器(纯 Python)

把"债务台账 + 每迭代还债预算"落成可运行实现:

```python
# —— 技术债台账:记录、按风险排序、用迭代预算还债 ——
class DebtLedger:
    FIELDS = ["problem", "risk", "trigger", "cost", "owner", "due"]

    def __init__(self):
        self.items = []                     # 每个债项:六要素 dict

    def add(self, problem, risk, trigger, cost, owner, due):
        self.items.append({"problem": problem, "risk": risk, "trigger": trigger,
                           "cost": cost, "owner": owner, "due": due})
        print(f"  记账: {problem}(风险 {risk},负责人 {owner},截止 {due})")

    def by_risk(self):
        """按风险降序:risk ∈ {高, 中, 低}"""
        order = {"高": 0, "中": 1, "低": 2}
        return sorted(self.items, key=lambda d: order.get(d["risk"], 9))

    def pay_off_with_budget(self, budget):
        """本轮还债预算:优先还高风险且成本可承担的债"""
        paid, remaining = [], budget
        for debt in self.by_risk():
            if debt["cost"] <= remaining:
                paid.append(debt["problem"])
                remaining -= debt["cost"]
        return paid, remaining

ledger = DebtLedger()
ledger.add("临时 Prompt 未版本化", "高", "模型换版后行为漂移", 2, "Alice", "本周")
ledger.add("路由规则无评估集", "高", "简单任务误路由到贵模型", 3, "Bob", "两周内")
ledger.add("工具权限过宽(可删生产数据)", "高", "注入攻击后可删库", 5, "Carol", "本周")
ledger.add("旧 skill 未废弃", "低", "误触发过期流程", 1, "Alice", "月底")
paid, rest = ledger.pay_off_with_budget(budget=5)
print(f"\n本轮还债预算 5:还了 {paid},剩余 {rest}")
```

## 实践 / 应用:反熵增落地 checklist

### 每个迭代的四道工序

1. **变更三问**(新工具复用了吗/新规则有人维护吗/绕过的流程记账了吗);
2. **还债预算**:固定留出预算,优先还评估集/日志/权限/错误处理四类债;
3. **架构评审**:变更是否触碰模块边界/配置版本化/废弃机制;
4. **演进检查**:新增依赖是否与核心逻辑解耦(可替换性)/有 ADR/有迁移路径(双写或影子)。

### 判断信号(熵增警报)

| 信号 | 含义 |
| --- | --- |
| Prompt 越来越长,没人敢删 | 复杂度在 Prompt 里堆叠(呼应 [OpenAI Prompt 指南](../07-agent-coding/experience/openai-prompt-guide.md) 的"做减法") |
| 工具越来越多,重复功能 | 缺少复用审查 |
| 路由规则没有评估集覆盖 | 技术债在关键路径上(呼应 [Spec-First 决策栈](../07-agent-coding/experience/spec-first-decision-stack.md) 的证据分级) |
| 换模型/换框架需要大改 | 可替换性设计缺失 |

### 与站内其他文章的呼应

- [Agent 系统设计的 5 个决策](agent-system-5-decisions.md):5 决策是**建设期**的复杂度管理,本文是**长期治理**;
- [生产级 Agent 9 层架构](ai-infra-layering.md):分层架构正是"允许系统长大的骨架";
- [Spec-First 决策栈](../07-agent-coding/experience/spec-first-decision-stack.md):规则沉淀与证据分级 = 技术债台账的"评估集"维度;
- [Agent 性能剖析](agent-performance-analysis.md)(同作者):性能剖析管"当下有多慢",本文管"长期会不会烂"——同一架构师思考的两面。

## 总结

- **三个概念一条主线**:复杂度治理(基础)→ 技术债(工程化保障)→ 架构演进(质量最后防线),共同回答"怎样让 Agent 在复杂环境中持续做出正确的决策";
- **三条警句**:复杂度不会自己消失,它只会换个地方收利息;技术债不是罪,装作没有才是(系统不会忘,你只是暂时没收到报警);架构不是一次画完的图,而是一套允许系统长大的骨架(骨架歪了,长得越快越疼);
- **三件工具**:变更三问(复用/维护/记账)、债务台账(六要素+还债预算)、演进设计(可替换性/ADR/双写影子);
- **一句话**:反熵增不是一次治理,是每次变更时都问一句"这笔账记了吗、这个依赖换得了吗、这条规则三个月后谁懂"。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/LmpSWgL-O9aXs_QBwlnwmg;原始资料存档于 `docs/inbox/agent-antientropy-source.md`
- 站内:[Agent 系统设计的 5 个决策](agent-system-5-decisions.md)、[生产级 Agent 9 层架构](ai-infra-layering.md)、[Spec-First 决策栈](../07-agent-coding/experience/spec-first-decision-stack.md)(规则与证据)、[AI Coding Harness 设计经验](../07-agent-coding/experience/ai-coding-harness-design.md)(护栏生长)、[Agent 性能剖析](agent-performance-analysis.md)(同作者姊妹篇)、[OpenAI 官方 Prompt 指南](../07-agent-coding/experience/openai-prompt-guide.md)(Prompt 做减法)
