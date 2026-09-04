# Agent 如何理解业务:对象、状态与权限的设计方法

> **一句话摘要**:意图识别只是业务理解的入口——真正"理解业务",是系统能在明确边界内把正确的业务对象从当前状态推进到目标状态,并留下可核对的依据。本文从设计方法论角度回答"Agent 系统该怎么设计才能理解业务":业务理解六要素、状态三元、编译式决策记录、理解/决策/执行三层架构,以及一条可运行的最小执行链路。
>
> **来源**:微信公众号「架构师 JiaGouX」《一文讲清 Agent 如何理解业务:把对象、状态和权限接进执行流程》,https://mp.weixin.qq.com/s/LYF3_RaXhe50DNb_ZW0KZg

## 概念

用户问客服 Agent:"上次那单还没发,能不能直接取消,优惠券也退回来?"识别"取消订单"不难,麻烦从这里才开始:"上次那单"是哪一单?履约状态真的未发货吗?券是哪种券?退款原路退还是退余额?用户有没有权操作这张订单?没有答案,Agent 只是听懂了这句话,**还没有理解这笔业务**。

!!! tip "为什么不能靠继续补 Prompt"
    补 Prompt 前几轮可能有效,但 **Prompt 能提醒模型怎样分析,却不能证明订单此刻处于什么状态,也不能替权限系统批准退款**。

对会执行动作的 Agent,"理解业务"落到一件**可验收的事**上:

> **Agent 能否在明确边界内,把正确的业务对象从当前状态推进到目标状态,并留下可核对的依据。**

意图识别只是入口;真正理解业务要证明整件事做得对——对象绑定、状态新鲜度、权限边界、端到端完成。本文聚焦**设计方法论**;落地节奏由另一篇文章负责。一句话原则贯穿全文:**模型负责整理用户表达,真实状态和副作用仍由业务系统负责。**

## 原理

### 原理 1:业务理解六要素——先给业务一套共同语言

DDD 强调**统一语言与限界上下文**:"客户"在销售、合同、售后系统里含义完全不同;"取消"在不同场景的状态变化也不同。先把一条小流程里的六样东西写清楚(以取消订单为例):

| 业务要素 | 取消订单场景里要回答什么 |
| --- | --- |
| **统一术语** | "未发货""已出库""退款完成"分别指什么 |
| **业务对象** | 操作哪张订单、哪笔支付、哪张优惠券 |
| **实时状态** | 订单、履约、支付和优惠券当前是什么状态 |
| **规则版本** | 当前适用哪版取消和退款政策 |
| **权限边界** | 谁能查询、谁能取消、谁能批准例外退款 |
| **可执行动作** | 查询、取消、退款、退券分别调用哪个工具 |

!!! warning "RAG 能找文档,不能当裁判"
    文档里是术语/政策/流程/案例;真实业务还多出三类**动态事实**:对象此刻的状态、当前用户在当前组织的权限、刚才那次动作成功/失败/只完成一半。前者可检索,后者必须回订单、账户、权限、支付、审计系统读取。*Context engineering != process engineering*:上下文工程管"模型看见什么",流程工程管"业务允许发生什么"。

### 原理 2:状态三元——别把三个状态放进一个字段

多轮对话里用户常只说半句话("换成明天吧")。系统要知道当前任务、用户在延续/切换/取消/修正、哪些参数已确认、上次工具调用返回了什么——这些是**对话状态**,但它**不等于**业务对象此刻的真实状态。

| 状态 | 回答的问题 | 更可信的来源 |
| --- | --- | --- |
| **对话状态** | 用户当前想继续、修改还是取消什么 | 会话记录与结构化槽位 |
| **业务状态** | 订单、账户、库存现在是什么状态 | 业务 API 和事实数据库 |
| **执行状态** | 动作是否开始、完成、重试或进入补偿 | 工作流、任务队列和审计日志 |

!!! warning "这条红线必须写进代码"
    "用户刚才说订单没发货"只能进入对话状态,**不能直接写成 `fulfillment=not_shipped`**——后一个值必须从履约系统重新读取。同理,"订单还没发,取消吧"只是候选,不是事实。复合任务(如"查账单,超预算就暂停测试环境再通知负责人")还需要一张小型执行图来表达动作间的依赖。

### 原理 3:编译式业务决策记录——模型只填它该填的字段

模型适合做第一段工作:把自然语言整理成**候选目标、对象线索和待确认项**。但它不该凭聊天记录猜订单状态,更不该根据"用户说还没发"就执行取消。一份更可用的中间结果:

```json
{
  "goal": "cancel_order",
  "object": {"type": "order", "id": "resolved_by_tool"},
  "observed_state": {"payment": "paid", "fulfillment": "not_shipped", "coupon": "consumed"},
  "policy_refs": ["order_cancel_policy:v7", "coupon_restore_policy:v3"],
  "unresolved": ["refund_destination"],
  "planned_actions": ["cancel_order", "refund_payment", "restore_coupon"],
  "approval": {"required": true, "reason": "financial_side_effect"}
}
```

这些字段**不能都交给模型填写**:`goal` 与对象线索由 LLM 解析,`observed_state` 由业务系统读取,`policy_refs` 绑定明确版本,`planned_actions` 经规则与权限校验,`approval` 由风险策略决定——**模型不能自己给自己放行**。从架构上看它像一个小型编译过程:`自然语言 -> 候选目标 -> 绑定对象 -> 读取实时状态 -> 应用规则与权限 -> 生成动作计划 -> 确认后执行 -> 校验状态变化`。

### 原理 4:理解、决策、执行——分三层,而不是加三个 Agent

原型 Demo 常让同一个 Agent 完成整条链路。生产问题会**混在一起**——一次退款失败,是意图错、状态旧、规则版本不对、权限漏判,还是支付接口超时?如果所有逻辑都在一段上下文里,排查时只能重放整段对话。

| 层 | 职责 | 设计要点 | 允许的行为 |
| --- | --- | --- | --- |
| **理解层** | 把人话变成业务候选 | 输出目标、对象线索、参数、置信信息、待确认项 | 概率判断、拒识、追问 |
| **决策层** | 把候选放进业务现场 | 读取实时状态、应用规则版本、检查权限、生成可执行计划 | 高风险规则尽量用确定性代码 / 决策表 / 状态机 |
| **执行层** | 让动作可控地产生副作用 | 工具合同(输入/输出/前置条件/幂等键/错误类型);资金、删除、外发、不可逆动作停在"已选择工具,尚未调用" | 暂停确认、幂等重放、记录证据 |

!!! tip "三层不意味着三个 Agent"
    完全可以是一个 Agent + 两层普通代码。架构目标是**分清责任,不是增加角色**;控制流要支持暂停和恢复,**在副作用发生前停住**。

## 代码 / 实现

最小执行链路,九个步骤各有责任方(完整实现中逐行注释)。两个**最容易被省掉的细节**:① `principal`——当前**以谁的身份行动**,工具调用能力不等于继承管理员权限;② `verify`——不是复述工具的成功消息,而是**重新读取业务对象**核对预期状态是否真的出现。

```python
"""最小业务理解执行链路(纯 Python,可运行):understand -> resolve -> read_state
-> resolve_policy -> decide -> (pause) -> execute(幂等) -> verify -> record
要点:principal 不继承管理员权限;verify 不信任工具成功消息;幂等键防重放。"""
import json

DB = {"o_1024": {"status": "paid", "fulfillment": "not_shipped",
                 "payment": "paid", "coupon": "consumed",
                 "coupon_async_slow": False}}   # 业务系统:唯一事实源

def read_order(order_id): return dict(DB[order_id])

def cancel_order(order_id, operator):
    row = DB[order_id]
    if row["fulfillment"] != "not_shipped":
        raise ValueError("政策 v7:仅未发货订单可取消")
    row["status"] = "cancelled"
    return {"status": "cancelled"}

def refund_payment(order_id, operator):
    DB[order_id]["payment"] = "refunded"
    return {"payment": "refunded"}

def restore_coupon(order_id, operator):
    row = DB[order_id]
    if row["coupon_async_slow"]:    # 受理成功但业务未达成
        return {"coupon": "restore_accepted"}
    row["coupon"] = "restored"
    return {"coupon": "restored"}

SERVICES = {"cancel_order": cancel_order, "refund_payment": refund_payment,
            "restore_coupon": restore_coupon}
EXECUTED = []                        # (action, object, idempotency_key)

def execute_tool(action, order_id, principal, idempotency_key):
    key = (action, order_id, idempotency_key)
    if key in EXECUTED:
        return {"skipped": True, "reason": "idempotency_key_replayed"}
    EXECUTED.append(key)
    return SERVICES[action](order_id, principal)

def understand(user_input):          # 理解层:真实系统里是 LLM 调用,这里规则模拟
    if "取消" in user_input and "订单" in user_input:
        return {"goal": "cancel_order", "object_ref": "o_1024",
                "unresolved": ["refund_destination"]}
    return {"goal": "unknown", "object_ref": None, "unresolved": []}

def resolve(candidate):              # 决策层:确定性代码
    if candidate["object_ref"] not in DB:
        raise ValueError(f"对象不存在: {candidate['object_ref']}")
    return {"type": "order", "id": candidate["object_ref"]}

def read_state(obj):
    """用户说"没发货"只是对话状态;状态从事实源读。"""
    return read_order(obj["id"])

def resolve_policy(goal, state, now):
    if goal != "cancel_order":
        return {"policy_refs": [], "allowed_actions": []}
    if state["fulfillment"] != "not_shipped":
        raise ValueError("政策 v7:当前已出库,不允许取消,需重新决策")
    return {"policy_refs": ["order_cancel_policy:v7", "coupon_restore_policy:v3"],
            "allowed_actions": ["cancel_order", "refund_payment", "restore_coupon"]}

ROLES = {"agent_support":      {"granted": ["query_order"]},
         "agent_support_lead": {"granted": ["query_order", "cancel_order",
                                            "refund_payment", "restore_coupon"]}}

def decide(candidate, state, policy, principal, obj):
    actions = [a for a in policy["allowed_actions"]
               if a in ROLES[principal]["granted"]]
    if not actions:
        return {"denied": True,
                "reason": f"principal={principal} 无该计划的动作权限"}
    return {"goal": candidate["goal"], "object": {"type": "order", "id": obj["id"]},
            "principal": principal, "planned_actions": actions,
            "requires_confirmation": "refund_payment" in actions,  # 资金副作用
            "expected_state": {"status": "cancelled", "payment": "refunded",
                               "coupon": "restored"}}

def run(user_input, principal, confirm=False, idempotency_key=None):
    candidate = understand(user_input)                      # 1 理解
    try:
        obj = resolve(candidate)                            # 2 绑定对象
        state = read_state(obj)                             # 3 读实时状态
        policy = resolve_policy(candidate["goal"], state, "2026-01-01")  # 4 规则
    except ValueError as e:
        return {"status": "rejected", "reason": str(e)}
    decision = decide(candidate, state, policy, principal, obj)          # 5 决策
    if decision.get("denied"):
        return {"status": "denied", "decision": decision}
    if decision["requires_confirmation"] and not confirm:
        return {"status": "paused", "decision": decision}               # 6 暂停
    key = idempotency_key or f"key-{obj['id']}"
    results = {}
    for action in decision["planned_actions"]:
        results[action] = execute_tool(action, obj["id"], principal, key)  # 7 执行
    final = read_state(obj)                                 # 8 verify:重读状态
    ok = all(final.get(k) == v for k, v in decision["expected_state"].items())
    return {"status": "done" if ok else "partial_failure",
            "record": {"decision": decision, "results": results,
                       "verified": ok, "final_state": final}}

if __name__ == "__main__":
    print(run("取消订单", principal="agent_support")["status"])  # denied
```

**运行**:存为独立文件后 `python3 agent-business-understanding.py`,纯标准库。`run()` 返回五类状态:`denied`/`paused`/`done`/`partial_failure`/`rejected`,分别对应权限拒绝、确认暂停、执行成功、部分完成、事实源拒绝。

## 实践 / 应用

### 五份小合同,比知识库大全更容易起步

不要一上来做"企业知识库大全"。更稳的起点是挑一条窄流程,写五份小合同:

| 合同 | 要点 | 生产意义 |
| --- | --- | --- |
| **1. 术语合同** | 业务对象、关键字段、同义词、易混词及边界 | "退款完成"指支付机构已受理还是资金已到账,会带来完全不同的客服回复 |
| **2. 状态合同** | 对象有哪些状态、允许怎样迁移、谁是事实源 | `paid -> cancel_pending -> cancelled -> refund_pending -> refunded`;支付已退但券恢复失败要能表达"部分完成",不能只剩一个 `success` |
| **3. 规则与权限合同** | 政策拆成条件/结论/例外/版本/责任人;写清自动额度、审批角色、必须转人工的情况 | 高频、稳定、高风险规则优先进代码或决策表;执行阶段要知道用的是哪版规则 |
| **4. 工具合同** | 每个工具只做一件清楚的事,写明前置条件、参数、返回值、副作用、幂等方式、可重试/终止错误 | 工程师自己都说不清该用哪个工具,就很难期待 Agent 选对 |
| **5. 验收合同** | 对象不明确、状态变化、政策冲突、权限不足、重复请求、工具超时、部分成功、用户改口,都单独留样本 | 验收里只有"正常取消成功"这类正例,很多生产问题不会出现 |

!!! note "五份合同也是复盘入口"
    每次线上误判都回到五份合同里复盘:术语缺了、状态过期、规则没覆盖、工具重叠,还是测试集没收进例外——业务经验才会逐渐变成**系统能力**。

### 一张"业务理解卡",够小也够实用

梳理具体任务时,用一张 10 行卡片:

```
任务:
业务对象:
当前状态:
目标状态:
事实来源:
适用规则:
允许动作:
必须确认:
完成证据:
失败与补偿:
```

!!! warning "填不出来的行就是流程缺口"
    十行里有三四行填不出来,已经足以暴露流程缺口,说明它还不适合直接交给 Agent 自动执行。以研发任务"修复登录问题,验证后发布"为例:允许动作=隔离分支修改、运行测试、构建候选版本;必须确认=正式发布与生产配置变更;完成证据=失败用例、代码差异、同一提交上的测试结果、发布版本、线上检查。这张卡把一句看似简单的指令拆成几个**不能混报的事实**:代码改了、测试通过了、候选版本构建出来了、生产已切换、线上链路验证正常——彼此有关,却不是一回事。

### 四种"看起来懂了",最值得拿来做测试

测试集只放表达清楚、状态稳定、一步成功的样本,很难看出系统是否真的理解业务。这四种错位更接近生产现场:

| 错位 | 表面现象 | 应有处理 | 暴露的环节 |
| --- | --- | --- | --- |
| **目标对了,对象错了** | 确实要取消订单,却选中同一用户的另一张订单 | 停止执行,补充对象确认 | 对象绑定 |
| **规则对了,状态旧了** | 按"未发货可取消"处理,但仓库刚刚完成出库 | 执行前重新读取状态,发现变化后重新决策 | 状态新鲜度 |
| **动作合法,身份不对** | 退款动作存在,但客服额度不足或跨组织操作 | 由权限系统拒绝,转审批或人工 | 权限边界 |
| **工具成功,业务只完成一半** | 取消成功、退款成功、优惠券恢复失败 | 标记部分完成,进入补偿或人工队列 | 事务完整性 |

这四类失败分别对应**对象绑定、状态新鲜度、权限边界、事务完整性**。推进节奏(历史回放 → 只读影子模式 → 只放开低风险路径 → 按失败证据扩大边界)与分层指标属落地实践角度,见 06 章落地篇。

## 总结

- **意图识别只是入口**。"理解业务"= 在明确边界内把正确的业务对象从当前状态推进到目标状态,并留下可核对的依据。
- **六要素给业务一套共同语言**:统一术语、业务对象、实时状态、规则版本、权限边界、可执行动作;RAG 能找文档,不能当实时状态与权限的裁判。
- **状态三元杜绝把说法当事实**:用户说"没发货"只能进对话状态,业务状态必须从事实源重新读取。
- **编译式决策记录**:模型填 `goal` 与线索,业务系统读 `observed_state`,规则权限校验 `planned_actions`,风险策略定 `approval`——**模型不能自己给自己放行**。
- **三层架构是责任分工**:理解层允许概率与追问,决策层用确定性代码,执行层管幂等与暂停;可以是 1 个 Agent + 2 层代码。`principal` 与 `verify` 是生产可靠性的两个细节。

通用模型越来越强,企业把"自己完成工作的方式"变成**可执行、可验证、可维护的系统**的工作不会消失——模型能帮忙整理规则、发现缺口,但对象怎么定义、状态怎么判断、例外谁批准、失败怎么补偿、做到哪里算完成,仍由企业负责。

**下一步**:落地实践角度看 06 章落地篇;通过 [工具调用](tool-calling.md) 深化执行层设计。

## 延伸阅读

- **站内**:[工具调用](tool-calling.md)(执行层)、[Agent 规划与工作流模式](agent-planning-patterns.md)(理解层)、[生产级 AI Agent 系统:9 层架构](ai-infra-layering.md)(三层在生产级全景的位置)、[WorkBuddy Bench](workbuddy-bench.md)(完成度与验收合同)
- **外部**:
  - 原文《一文讲清 Agent 如何理解业务》:https://mp.weixin.qq.com/s/LYF3_RaXhe50DNb_ZW0KZg
  - 陈思州/Datawhale《一文读懂怎么让 Agent 理解业务,别一上手就写 Prompt!》:https://mp.weixin.qq.com/s/BlF50Z143CfJjeBsr-YrHQ
  - Anthropic *Effective context engineering for AI agents*:https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

