# 多 Agent 协作:让多个 AI 各司其职、互相制衡

> **一句话摘要**:单 Agent 的上下文、技能、立场都有限;多 Agent 协作以成本为代价,换取更高的任务复杂度上限。
>
> **来源**:综合公开资料(AutoGen、LangGraph、CrewAI 文档等)。

## 概念

- **多 Agent 系统(MAS)**:两个及以上**独立运行、各带提示词(角色/目标/工具)的 Agent** 经**消息通信**协同完成任务。
- **为什么需要多 Agent**:

| 单 Agent 瓶颈 | 多 Agent 解法 |
| --- | --- |
| 上下文窗口有限 | 每个 Agent 只加载局部上下文 |
| 缺少制衡,易自信犯错 | 辩论/审查 Agent 提反对意见 |


## 原理

### 协作模式:四种典型拓扑

| 模式 | 结构 | 适用场景 | 优点 | 缺点 |
| --- | --- | --- | --- | --- |
| **编排(Orchestrator-Worker)** | Orchestrator 拆任务、派发 Worker 汇总 | 数据分析 | 清晰易控 | 单点瓶颈 |
| **辩论(Debate)** | 多立场 Agent 反复发言,带裁判 | 决策、审查 | 暴露盲点 | 成本高 |
| **流水线(Pipeline)** | 前一 Agent 输出是后一输入 | ETL、生成 | 可分段评测 | 错误逐级放大 |
| **黑盒团队(Blackboard)** | 共享"黑板",异步读写 | 探索任务 | 解耦、动态增减 | 难调试 |

### 角色分工与提示词设计

- system prompt 应含**角色**、**目标**、**约束**、**风格**。
- **角色隔离**:不同 Agent 用不同上下文与工具,避免互相污染。
- **裁决者(Judge)**:辩论常有第三个 Agent 评分/投票。

### 消息通信协议

Agent 之间传**结构化消息**:

| 字段 | 含义 | 示例 |
| --- | --- | --- |
| `sender` / `recipient` | 路由:谁发给谁 | `researcher` → `writer` |
| `kind` | 类型:statement / tool_call / final | `tool_call` |
| `content` / `meta` | 正文 / 元数据 | `搜索结果:...` |

通信分**直接消息**(一对一)与**黑板**(广播写、订阅读)。每轮重发**完整历史**(LLM 无状态),故消息总数最坏 $O(N^2 \cdot T)$:

$$
\text{cost}_{total} \approx \sum_{t=1}^{T}\sum_{a=1}^{N} \text{tokens}(\text{history}_t^{(a)})
$$

## 代码 / 实现

纯 Python(仅标准库)模拟两个 Agent 的**辩论式对话**。

```python
"""多 Agent 辩论演示:两个立场 agent 围绕议题交替发言。仅标准库。"""
import random, time
from dataclasses import dataclass, field

@dataclass
class Message:
    sender: str; recipient: str; kind: str; round: int; content: str
    meta: dict = field(default_factory=dict)

class MockLLM:
    # 确定性 mock:回应对方论点不重复,偶发超时重试
    def __init__(self, seed=42, fail_prob=0.2):
        self.rng = random.Random(seed); self.fail_prob = fail_prob
        self.calls, self.used = 0, {}

    def chat(self, system, prompt, retries=3):
        for attempt in range(1, retries + 1):
            try:
                self.calls += 1
                if self.rng.random() < self.fail_prob:
                    raise TimeoutError("mock LLM 超时")
                return self._reply(system, prompt)
            except TimeoutError:
                time.sleep(0.001 * (2 ** attempt))
        return "[concede] 模型连续失败,我暂不坚持己见。"

    def _reply(self, system, prompt):
        used = self.used.setdefault(id(system), set())
        keys = [k for k in system if k != "default"]
        pick = [k for k in keys if k in prompt and k not in used] or \
               [k for k in keys if k not in used] or ["default"]
        k = pick[0]; used.add(k)
        return system[k]

class Debater:
    def __init__(self, name, system, llm):
        self.name, self.system, self.llm = name, system, llm

    def act(self, messages, r):
        last = messages[-1]
        reply = self.llm.chat(self.system, f"对方({last.sender})说:{last.content}")
        kind = "concede" if ("部分同意" in reply or "暂不坚持" in reply) else "statement"
        return Message(self.name, last.sender, kind, r, reply)

def debate(topic, agents, max_rounds=6):
    messages = [Message("moderator", "all", "statement", 0, topic)]
    print(f"=== 辩论议题:{topic} ===\n")
    for r in range(1, max_rounds + 1):
        for agent in agents:
            msg = agent.act(messages, r); messages.append(msg)
            print(f"[回合 {r}] {msg.sender}(→{msg.recipient}, {msg.kind}): {msg.content}")
            if msg.kind == "concede":
                print(">>> 辩论收敛,提前结束。"); return messages
    print(">>> 达到最大回合数。"); return messages

if __name__ == "__main__":
    pro = {"电池": "回收闭环已规模化,污染担忧被夸大。",
           "电网": "错峰充电可平滑负荷曲线,电网数字化是既定投资。",
           "成本": "电动车全生命周期成本更低。",
           "就业": "新能源岗位更多,是就业升级。",
           "污染": "空气污染致数十万例过早死亡,禁售刻不容缓。",
           "default": "禁售燃油车是必要的公共卫生行动。"}
    con = {"电池": "回收产业刚起步,回收率不足一半,会留下环境债。",
           "电网": "电网高峰已近极限,大规模充电需数千亿改造。",
           "成本": "换车成本数万,让低收入家庭买单。",
           "就业": "数百万工人转型困难,不能只谈岗位净增。",
           "污染": "污染主因未必是私家车,公交电动化更划算。",
           "default": "渐进式混动过渡更现实,应给产业留时间。"}
    llm = MockLLM(seed=7, fail_prob=0.2)
    agents = [Debater("支持派", pro, llm), Debater("反对派", con, llm)]
    msgs = debate("城市是否应在 2030 年全面禁售燃油汽车?", agents)
    print(f"\nLLM 调用次数: {llm.calls}(含重试)")
    print("消息字段示例:", msgs[1])
```

**逐段解释**:

1. **消息协议**:`sender/recipient/kind/round/content` 让消息可路由、可追踪,真实系统再加 `msg_id`、`timestamp` 去重。
2. **模拟 LLM**:`chat()` 用随机超时 + 指数退避模拟 API 抖动;`_reply()` 用关键词匹配模拟语义检索,`used` 保证论点不重复("上下文记忆")。
3. **Agent 与编排**:`Debater` 绑定"身份 + 行为"(对应"system prompt + LLM + 工具");`debate()` 控制轮次,检测到 `concede` 提前收敛。

**运行结果**(`python3` 直跑):双方 6 回合依次交锋"电池、电网、成本、就业、污染";LLM 调用 19 次(含重试);未达成共识,应触发仲裁。

!!! tip "接入真实 LLM"
    把 `MockLLM.chat()` 换成 LLM API、`system` 换成真正的系统提示词,其余骨架可直接复用。

## 实践 / 应用

### 成本

- **Token 成倍增长**:每轮重发完整历史,5 轮辩论 ≈ 单 Agent 的 5-10 倍。
- **延迟叠加**:串行延迟为各 Agent 之和,并行受最慢者限制。
- **复杂度**:状态管理、消息持久化、失败恢复都要设计。

### 失败风险

| 风险 | 现象 | 缓解 |
| --- | --- | --- |
| 级联错误 | 前一个 Agent 的错被下游放大 | 每段校验 + 审批点 |
| 共识泡沫 | 互相"赞同",群体思维 | 强制一人持反对立场 |
| 死循环 | 无限互发"你再说一遍" | 最大回合 + 重复检测 |
| 成本失控 | 任务烧几十次调用 | 设预算超限降级 |

**框架**:AutoGen(群聊)、LangGraph(图式编排)、CrewAI(角色化);框架管消息路由,**角色与评测仍要自己做**。

## 总结

- 多 Agent 的本质:**角色隔离 + 结构化消息 + 编排拓扑**突破单 Agent 上限。
- 消息协议要有 sender/recipient/kind/round;历史重发是成本膨胀根源。
- 收益与代价一起算;先跑通单 Agent 再升级。
- 下一步:学 [Agent 开发实践](agent-practice.md) 的评测与可靠性策略。

## 延伸阅读

- 站内:[Agent 开发实践](agent-practice.md)、[Prompt 工程](prompt-engineering.md)、[LLM 基础](../02-llm/index.md)
- 外部:AutoGen 论文《Enabling Next-Gen LLM Applications via Multi-Agent Conversation》;LangGraph 文档。
