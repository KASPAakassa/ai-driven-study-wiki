# 企业 Agent 工程化(二):异常恢复与人工接管

> **一句话摘要**:能进生产的 Agent 不是不出错,而是出错后知道该怎么停——重试、回滚、人工接管三种恢复动作按动作性质选,不看模型信心;接管与否看后果半径。附可运行的 should_handoff 决策函数与带 waiting_for_human 的状态机。
>
> **来源**:微信公众号《企业 Agent 工程化手记》第 3 篇《企业 Agent 出错后:该重试、回滚,还是交给人?》与第 5 篇《企业 Agent 什么时候必须停下来等人?看后果,不看信心》;原文链接见收件箱登记(`docs/inbox/enterprise-agent-engineering-src-b6.md`、`src-b5.md`)

## 概念

### 三种恢复动作,三种代价

作者复盘连续几天的协作日报,发现验证补跑、返工修正、重复推进反复出现——很多任务不是没做完,而是在"出错—重试—再出错"里打转。**重试、回滚、人工接管是三种代价完全不同的动作,让 Agent 自己挑,迟早挑错。**

| 恢复动作 | 解决什么 | 前提 |
| --- | --- | --- |
| 重试 | 可安全重复的瞬时失败 | 动作可安全重复(幂等) |
| 回滚 | 已产生副作用、但有可信状态可退 | 动作可逆 + 记录过原始状态 |
| 人工接管 | 系统无法安全判断,继续自动处理会扩大风险 | 停止条件写得清 |

### 接管看后果,不看信心

很多人设计人工接管,第一反应是"模型不确定的时候就问人"——但模型对很多危险动作恰恰很"确定",对无关紧要的小事反复犹豫。**用信心做触发,结果是:人被一堆"确认吗"淹没,真正危险的动作却被自信地放过。**

!!! tip "核心原则"
    **草稿可以自动,生效必须确认;内部分析可以自动,对外触达默认确认。** 判断接管点,判断的是动作的**后果**会不会进入真实业务系统,不是模型的把握有多大。Agent 可以自动生成建议,但不能自动替人承担业务后果。

## 原理

### 重试:前提是这一步能安全重复

重试不是"再试一次",而是**在动作可以安全重复时,用有限次数消除瞬时失败**。它只对可安全重复的动作有效:一次只读查询、一次纯计算、一次幂等写入——重复多少遍结果都一样。

一旦动作有副作用,重试就变味:发消息、扣费、提交、改状态——盲目重试就是重复发送、重复提交、重复扣费,**错误没被修复,只是又发生了一次**。更隐蔽的是**重试风暴**:Agent 在一长串工具调用里反复试、反复补,看起来一直在推进,其实在制造垃圾。所以重试之前先回答:**这一步,重复做会不会出新问题?答不上来,就不该自动重试。**

### 回滚:前提是你留了后路

回滚不是"撤销错误"这么简单,它的准确含义是**把系统带回一个已经记录过、仍然可信的状态**。能不能回滚取决于两件事:动作本身可不可逆;你有没有记录"改之前长什么样"。很多 Agent 根本回滚不了,因为它一路往前补,既没有检查点,也没留下原始状态,等发现错了已经退无可退。**要能回滚,先得有状态**——一个动作执行前没留下"原来的样子",出错时就没有退路。

### 人工接管:前提是系统知道自己处理不了

人工接管不是让人替 Agent 干活,而是**系统确认自己无法安全决策时,把上下文、已执行动作和风险点交回给人**。不可逆的动作、涉及金额或客户数据的动作、判断依据不足时——正确的恢复不是重试也不是回滚,而是停下来,把上下文交回给人。

!!! warning "频繁确认才是问题"
    人工接管是设计的一部分,关键在于**停止条件写清楚**:满足什么条件就停、停在哪一步、把什么信息交回给人。它的反面是"频繁确认"——如果每一步都要人点一下确认,那不是接管设计得好,而是边界没划清,人在替工具的越界风险持续买单。

### 后果半径四档:动作分级

判断接管点,先问三件事:**可不可逆?代价超没超阈值?有没有越权?** 据此把动作分成四档:

| 档位 | 动作类型 | 例子 | 处置 |
| --- | --- | --- | --- |
| 一 | 只读分析 | 查规则、解释字段、列影响对象 | 自动做 |
| 二 | 可撤销草案 | 生成待确认规则、待审批话术、跟进建议 | 自动生成,不自动生效 |
| 三 | 真实写入 | 改客户阶段、写业务状态、创建任务 | 看影响范围,满足条件才继续 |
| 四 | 不可逆外发 | 给客户发消息、提交审批、触发外部系统 | 默认停,除非规则证明可自动 |

四档的关键区别不是技术难度,而是**后果半径**:后果只停留在草稿里,可以自动;后果进入业务系统,要接管;后果发给外部对象,默认接管。

### should_handoff 判断规则

接管判断绕开"模型置信度",只问四件事:

1. **可逆性**:只读/草案不接管;写业务状态默认接管;外发默认接管;
2. **阈值**:影响条数超过自动上限(改 1 条和改 500 条不是一回事);
3. **越权**:动了身份不该动的东西;
4. **业务归属**:归属边界不清(如当前系统只做增强记录,主流程归外部系统)。

## 代码 / 实现

原文给了伪代码。下面转成可运行的纯 Python:先实现 **should_handoff(action) 决策函数**(后果半径判断,不含模型置信度),再实现带 **waiting_for_human 状态的任务状态机**(推进/批准/驳回/缩小范围)。

```python
# 第 1 部分:should_handoff —— 接管看后果,不看信心
# 这个函数里故意没有"置信度"字段

def should_handoff(action, policy):
    """接管看后果,不看信心:可逆性/阈值/越权/业务归属。返回(是否接管, 理由)"""
    if action["kind"] in ("read_only", "draft"):
        return False, "后果停留在草稿/分析层"
    if action["effect"] == "write_business_state":
        return True, "将写入真实业务状态"
    if action["effect"] == "send_to_external_party":
        return True, "将触达外部对象"
    if action["impact_count"] > policy["max_auto_items"]:
        return True, "影响 %d 条,超过自动上限 %d" % (
            action["impact_count"], policy["max_auto_items"])
    if action["owner_boundary"] != "clear":
        return True, "业务归属边界不清,可能越权"
    return False, "可自动执行"

POLICY = {"max_auto_items": 10}
ACTIONS = [
    {"id": "query_rule",        "kind": "read_only", "effect": "none",
     "impact_count": 1,  "owner_boundary": "clear"},
    {"id": "draft_followup",    "kind": "draft",     "effect": "none",
     "impact_count": 1,  "owner_boundary": "clear"},
    {"id": "update_stage",      "kind": "write",     "effect": "write_business_state",
     "impact_count": 1,  "owner_boundary": "clear"},
    {"id": "batch_update",      "kind": "write",     "effect": "write_business_state",
     "impact_count": 500, "owner_boundary": "clear"},
    {"id": "send_reminder",     "kind": "write",     "effect": "send_to_external_party",
     "impact_count": 5,  "owner_boundary": "clear"},
    {"id": "write_rule_effect", "kind": "write",     "effect": "write_business_state",
     "impact_count": 3,  "owner_boundary": "unclear"},
]

print("%-18s %-28s %s" % ("action", "handoff?", "reason"))
for a in ACTIONS:
    handoff, reason = should_handoff(a, POLICY)
    print("%-18s %-28s %s" % (a["id"], "YES -> 等人" if handoff else "no  -> 自动", reason))
```

**运行结果**:六个动作按后果半径各归其位——只读与草案自动;改客户阶段(单条写入)触发接管;批量 500 条既超阈值又写状态,接管;发提醒触达外部对象,接管;规则生效写入且业务归属不清,接管。全程没有用到模型置信度。

```python
# 第 2 部分:带 waiting_for_human 状态的任务状态机
# waiting_for_human 是正式状态,不是异常;批准后按决策继续
def should_handoff(action, policy):
    """与本文件前一块保持一致:接管看后果,不看信心"""
    if action["kind"] in ("read_only", "draft"):
        return False, "后果停留在草稿/分析层"
    if action["effect"] == "write_business_state":
        return True, "将写入真实业务状态"
    if action["effect"] == "send_to_external_party":
        return True, "将触达外部对象"
    if action["impact_count"] > policy["max_auto_items"]:
        return True, "影响 %d 条,超过自动上限 %d" % (
            action["impact_count"], policy["max_auto_items"])
    if action["owner_boundary"] != "clear":
        return True, "业务归属边界不清,可能越权"
    return False, "可自动执行"

class Task:
    def __init__(self, task_id):
        self.id = task_id
        self.status = "pending"        # pending/running/waiting_for_human/stopped/done
        self.pending_action = None
        self.handoff_context = None
        self.approved_by = None
        self.history = []

def advance(task, action, policy):
    """推进一步:该接管就停住并记录上下文;否则执行"""
    if task.status == "waiting_for_human":
        # 合法状态守卫:等人时不允许继续偷跑,只有批准信号能解除
        print("[%s] 正在等待人工,拒绝继续推进 %s" % (task.id, action["id"]))
        return
    handoff, reason = should_handoff(action, policy)
    if handoff:
        task.status = "waiting_for_human"      # 合法状态,不是异常
        task.pending_action = action
        task.handoff_context = build_context(action, reason)
        task.history.append(("handoff", action["id"]))
        print("[%s] 停在 waiting_for_human: %s (%s)" % (task.id, action["id"], reason))
        return
    execute(action)
    task.status = "done"
    task.history.append(("executed", action["id"]))
    print("[%s] 自动执行 %s -> %s" % (task.id, action["id"], task.status))

def resume_after_approval(task, approval):
    """批准信号:批准、驳回、缩小范围三种结果都要接住"""
    if task.status != "waiting_for_human":
        return
    if approval["decision"] == "reject":
        task.status = "stopped"
        print("[%s] 人工驳回,任务停止" % task.id)
        return
    if approval["decision"] == "narrow_scope":
        task.pending_action = dict(task.pending_action, impact_count=approval["scope"])
    execute(task.pending_action)
    task.status = "done"
    task.approved_by = approval["owner"]
    task.history.append(("executed", task.pending_action["id"]))
    print("[%s] 人工批准(owner=%s),执行 %s -> done"
          % (task.id, approval["owner"], task.pending_action["id"]))

def execute(action):
    pass  # 真实实现里这里才是工具调用

def build_context(action, reason):
    """给人足够上下文:动作、对象、影响、理由、建议、恢复路径"""
    return {"action": action["id"], "reason": reason,
            "impact_count": action["impact_count"],
            "suggest": "approve / reject / narrow_scope",
            "recovery": "retry / rollback / pause"}

# 演练:批量更新客户阶段 + 发提醒的任务(验证命令、恢复策略已写进计划)
POLICY2 = {"max_auto_items": 10}
task = Task("t-2026-0616")
step1 = {"id": "update_stage", "kind": "write", "effect": "write_business_state",
         "impact_count": 1, "owner_boundary": "clear"}
step2 = {"id": "send_reminder", "kind": "write", "effect": "send_to_external_party",
         "impact_count": 5, "owner_boundary": "clear"}
advance(task, step1, POLICY2)              # 写客户阶段 -> 接管
advance(task, step2, POLICY2)              # 等人时继续推进 -> 被守卫拒绝
print("  已接管上下文:", task.handoff_context)
resume_after_approval(task, {"decision": "narrow_scope", "scope": 1, "owner": "sales-owner"})
print("  最终状态:", task.status, "| 历史:", task.history)

# 再来一个被驳回的任务
task2 = Task("t-2026-0617")
advance(task2, step2, POLICY2)
resume_after_approval(task2, {"decision": "reject", "owner": "risk-owner"})
print("  任务2最终状态:", task2.status)
```

**运行结果**:写客户阶段触发生成接管,任务停在 `waiting_for_human` 并带上六块上下文;等待期间继续推进第二步,被守卫拒绝——**waiting_for_human 是合法状态,不能偷跑**。人工选择"缩小范围"后,状态机把影响条数限到 1,执行动作推进到 `done` 并留痕 `approved_by`;第二个任务则演示驳回路径——`reject` 让任务停到 `stopped`,不再往下走。

## 实践 / 应用

### 把失败处理写在出错之前(五条)

安装、配置、写操作这类请求,**必须先写清验证命令和失败退出条件,而不是让 Agent 边做边补**。具体五条:

1. **动作分级**:先分清只读、可写、不可逆,三类恢复方式完全不同;
2. **重试前置条件**:只有能安全重复的动作才允许自动重试,并设上限避免重试风暴;
3. **回滚后路**:可写动作执行前先记录原始状态或留检查点,否则一律当不可逆处理;
4. **停止条件**:不可逆、涉及金额或客户数据、判断依据不足时,停下来交回给人;
5. **写进计划文件**:把验证命令、失败退出条件、恢复策略写在任务开始之前,而不是出错后临时补。

!!! note "团队类比"
    你不会让新人在生产环境出错后自己看着办、自己反复改。你会先和他约定:什么情况重试,什么情况回滚,什么情况必须停下来叫人。Agent 也一样——它的可靠性不取决于出不出错,而取决于你有没有在出错之前,替它把"怎么收场"想清楚、写下来。

### 人工接管请求的六块信息

真正有价值的接管,是让人**基于足够上下文做业务判断**。少了六块,人工接管很容易退化成一个按钮——按钮看起来让人参与了,实际上只是把责任甩给人:

| # | 信息 | 说明 |
| --- | --- | --- |
| 1 | 动作类型 | 只读/草案/真实写入/不可逆外发 |
| 2 | 业务对象 | 哪类客户、账号、订单、审批或任务,不要只写"一批数据" |
| 3 | 影响范围 | 多少条、哪些状态、是否跨组织或跨流程 |
| 4 | 触发理由 | 不可逆、超阈值、越权,还是业务归属不清 |
| 5 | 建议动作 | 批准/驳回/缩小范围/改成草案/转给业务 owner |
| 6 | 恢复路径 | 批准后失败,下一步是重试、回滚、暂停还是继续交人 |

### 接管四设计点:把"等人"做成工程

1. **合法状态**:`waiting_for_human` 是正式状态,不是流程中断——Agent 进到这一步就停住、持久化、不往下走,等批准信号再续跑;
2. **显式规则**:不可逆/超阈值/越权写成代码能判断的条件,不靠模型自觉——**模型负责执行,规则负责拦截**;
3. **足够上下文**:告诉人它想做什么、为什么这么判断、影响哪些数据,人要能在三秒内看懂做决定,否则审批会变成无脑点"同意";
4. **留痕**:谁批的、什么时候批的、基于什么信息批的——企业系统里,"谁负责"必须有答案。

## 总结

- **能进生产的 Agent,不是不出错,而是出错后知道该怎么停**:重试看幂等、回滚看状态、接管看停止条件,三者是代价不同的岔路口,不能靠模型临场发挥。
- **接管看后果,不看信心**:草稿可以自动,生效必须确认;内部分析可以自动,对外触达默认确认。
- **动作分级四档**:只读 → 草案 → 真实写入 → 不可逆外发,越往后越要接管;`should_handoff` 判断可逆性、阈值、越权、业务归属。
- **waiting_for_human 是合法状态**:不是异常,不是弹窗——是刹车系统,平时不打扰,真到业务后果要落地时必须踩住。
- **设计它怎么失败**:失败处理写在出错之前——动作分级、重试前置条件、回滚后路、停止条件、写进计划文件。

## 延伸阅读

- 站内:[企业 Agent 工程化(一):任务边界与工具治理](enterprise-agent-boundaries-tools.md)、[Ontology 与 Agent 企业落地](index.md)、[Agent 工具调用机制](../../03-agents/tool-calling.md)、[上下文工程](../../03-agents/context-engineering.md)、[Agent 记忆系统](../../03-agents/agent-memory-systems.md)
- 外部:微信公众号《企业 Agent 工程化手记》第 3 篇《企业 Agent 出错后:该重试、回滚,还是交给人?》、第 5 篇《企业 Agent 什么时候必须停下来等人?看后果,不看信心》(原文链接见收件箱登记)
