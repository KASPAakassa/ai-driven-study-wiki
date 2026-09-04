# Agent 开发实践:从需求到上线的完整流程

> **一句话摘要**:Agent 不是"写好提示词就能上线"的玩具,需要五步工程流程(需求/架构/工具/提示词/评测),并针对死循环、成本失控、上下文爆掉等坑做可靠性设计。
>
> **来源**:综合工程实践(LangChain/LangGraph 文档、Anthropic《Building Effective Agents》等)。

## 概念

- **Agent 开发** vs 普通软件:LLM 输出**不确定**、工具调用有**副作用**、任务**反复调 LLM(花钱)**,要围绕"约束 + 观测 + 兜底"设计。
- **五步流程(闭环迭代)**:需求分析 → 架构选型 → 工具设计 → 提示词 → 评测 → 回到开头。

## 原理

### 各步骤怎么落地

1. **需求分析**:把模糊目标变成可测**成功指标**(如"完成率 ≥ 90%");先跑通单 Agent。
2. **架构选型**:线性任务 → 单 Agent;需互审/多专业 → [多 Agent 协作](multi-agent.md)(5-10 倍成本)。明确谁拆解、谁执行。
3. **工具设计**:输入输出严格 schema;**幂等**、**可审计**、**最小权限**(不裸给删库权限)。
4. **提示词**:system prompt 给**角色/目标/约束/风格**(见 [Prompt 工程](prompt-engineering.md))。
5. **评测**:结果反过来改工具与提示词,闭环。

### 常见坑与可靠性策略

| 坑 | 现象 | 对策 |
| --- | --- | --- |
| **死循环** | 反复调同一工具、无进展 | 最大步数 + 重复检测 |
| **错误处理缺失** | 工具抛异常直接崩 | try/except + 重试 + 错误回传 LLM |
| **成本失控** | 一次任务几十次调用 | token 预算,超限降级 |
| **上下文爆掉** | 历史超出窗口 | 裁剪/摘要历史 |

**四条可靠性支柱**:

- **最大步数(max_steps)**:强制终止的最后防线。
- **重试(retry)**:偶发错误指数退避重试;确定性错误重试无意义,错误**回传 LLM** 换策略。
- **人工审批(HITL)**:危险操作(邮件/删除/转账)前必须人确认。
- **结构化日志**:每步 action/args/result/error 落 JSONL,可回放审计。

## 代码 / 实现

纯 Python 演示**带防护的 agent 循环**如何战胜"会犯错的策略",并与无防护版本对比。

```python
"""稳健 Agent 循环:max_steps + 重试 + 重复检测 + 人工审批 + 日志。仅标准库。"""
import time
from dataclasses import dataclass

@dataclass
class Tool:
    name: str; fn: callable

def make_tools():
    def divide(a, b):
        if b == 0:
            raise ZeroDivisionError("除数不能为 0")
        return a / b
    def search(q):
        return "文档:除数为 0 时应使用 lookup_reference 查询安全结果"
    def lookup_reference(key):
        return "42"
    def send_email(to, content):
        return f"邮件已发送给 {to}"
    return {t.name: t for t in [
        Tool("divide", divide), Tool("search", search),
        Tool("lookup_reference", lookup_reference), Tool("send_email", send_email)]}

class StrategyLLM:
    def __init__(self, stubborn=False):
        self.stubborn = stubborn

    def decide(self, history):
        intervened = any(h.get("note") == "intervention" for h in history)
        did = lambda act: any(h.get("action") == act for h in history)
        if not did("divide") or self.stubborn or not intervened:
            return ("call", "divide", {"a": 5, "b": 0})
        if not did("send_email"):
            return ("call", "send_email", {"to": "customer", "content": "订单已发货"})
        if not did("search"):
            return ("call", "search", {"q": "除数为 0 的处理"})
        if not did("lookup_reference"):
            return ("call", "lookup_reference", {"key": "safe_div_result"})
        return ("final", "42")

def agent_loop(llm, tools, robust=True, max_steps=10, max_retries=2,
               repeat_threshold=2, approval_tools=("send_email",), human_approver=None):
    logs, st = [], f"max_steps={max_steps}"
    if not robust:
        max_retries, repeat_threshold = 0, 99
        st = "无防护"
    print(f"=== {("robust" if robust else "naive")} loop:{st} ===\n")
    for step in range(1, max_steps + 1):
        decision = llm.decide(logs)
        if decision[0] == "final":
            print(f"  step {step}: 答案 {decision[1]}")
            logs.append({"kind": "final", "answer": decision[1]})
            return decision[1]
        name, args = decision[1], decision[2]
        if robust and name in approval_tools:
            approved = human_approver(name, args)
            print(f"  [人工审批] {name} -> {approved and "批准" or "拒绝"}")
            if not approved:
                continue
        for attempt in range(max_retries + 1):
            try:
                result = tools[name].fn(**args)
                logs.append({"kind": "tool", "action": name, "result": result, "error": ""})
                print(f"  step {step}: {name}{args} -> {result}")
                break
            except Exception as e:
                last_error = f"{type(e).__name__}: {e}"
                if attempt < max_retries:
                    time.sleep(0.001 * (2 ** attempt))
                    print(f"  step {step}: {name} 抛错,重试...")
                else:
                    logs.append({"kind": "tool", "action": name, "result": "", "error": last_error})
                    print(f"  step {step}: {name} 最终失败 {last_error}")
        recent = logs[-repeat_threshold:]
        same = len({r.get("action") for r in recent}) == 1 and len({r.get("error") for r in recent}) == 1
        if len(recent) == repeat_threshold and same and recent[0].get("error"):
            logs.append({"kind": "intervention", "note": "intervention"})
            print(f"  >>> 重复失败,注入干预")
    print(f"  达到 max_steps={max_steps},强制终止。")
    return None

if __name__ == "__main__":
    tools = make_tools()
    print("任务: 计算 5/0;若除数为 0,查询知识库得到安全结果\n")
    agent_loop(StrategyLLM(stubborn=True), tools, robust=False, max_steps=6)
    print()
    agent_loop(StrategyLLM(stubborn=False), tools, robust=True, max_steps=10,
               human_approver=lambda name, args: True)
```

**逐段解释**:

1. **工具层**:`Tool` 封装名字与函数,注册表即白名单;`divide` 故意抛 `ZeroDivisionError`。
2. **策略模拟**:`StrategyLLM.decide()` 读历史决策下一步;`stubborn=True` 模拟"重复犯错"。
3. **统一 agent_loop**:`robust=False` 不重试不干预,靠 `max_steps` 截断;`robust=True` 启用:① 指数退避重试;② 同动作同错误连续 → 注入干预;③ 危险操作审批;④ 每步写 `logs`。

**运行结果**(`python3` 直跑):无防护版 6 步重复 `divide(5,0)` 后截断;防护版经 2 次失败 + 干预改走 `search → lookup_reference`,含一次审批,第 6 步输出 `42`。

!!! tip "把 StrategyLLM 换成真实 LLM"
    把 `StrategyLLM.decide()` 换成真实 LLM,四道防线代码结构不变。

## 实践 / 应用

### 评测方法

| 方法 | 指标 |
| --- | --- |
| 单元评测(工具/单轮) | 成功率、格式合法率 |
| 端到端评测(黄金集) | 完成率、平均步数/成本、失败率 |
| 回归 / 成本评测 | 指标不退步、每任务成本/P95 |

## 总结

- Agent 开发是**约束 + 观测 + 兜底**的工程,五步流程闭环迭代。
- 四大坑与四条支柱一一对应:死循环→max_steps+重复检测;错误缺失→重试+错误回传;成本失控→预算;上下文爆掉→裁剪。
- 评测用黄金集做端到端 + 回归 + 成本三件事;下一步学 [Prompt 工程](prompt-engineering.md),再看 [多 Agent 协作](multi-agent.md)。

## 延伸阅读

- 站内:[多 Agent 协作](multi-agent.md)、[Prompt 工程](prompt-engineering.md)、[LLM 基础](../02-llm/index.md)
- 外部:Anthropic《Building Effective Agents》;LangGraph 文档;《Patterns for Building LLM-based Systems & Products》
