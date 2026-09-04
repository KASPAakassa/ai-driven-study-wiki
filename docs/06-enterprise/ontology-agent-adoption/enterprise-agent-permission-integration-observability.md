# 企业 Agent 工程化(三):权限、集成与可观测性

> **一句话摘要**:企业 Agent 从 Demo 走向生产要过三关——"它替谁做事"必须落在身份与数据边界里;"接口通了"不等于"接稳业务系统";可观测性"不是更多日志,而是执行链路可还原"。本文给出身份三层边界、集成契约四现实、四类记录与最小记录契约。
>
> **来源**:微信公众号《企业 Agent 工程化手记》第 6/7/8 篇(《企业 Agent 替谁做事:权限、数据边界和用户身份》《企业 Agent 接口明明通了,为什么还是接不稳业务系统?》《企业 Agent 出问题时,别只看最终回复:执行链路必须看得见》),原文链接见收件箱登记,抓取日期 2026-08-09

## 概念

三篇原文是同一条逻辑线的三段:

| 问题 | 一句回答 | 素材 |
| --- | --- | --- |
| Agent 能不能进业务系统 | 权限不是技术问题,是**身份与数据边界**问题 | 第 6 篇 |
| 进去后会不会把事情做坏 | 接口通了 ≠ 接稳,**契约、幂等、失败语义**才是边界 | 第 7 篇 |
| 出了事你第一时间看不看得见 | 可观测性不是更多日志,是**链路可还原** | 第 8 篇 |

三个核心命题:

1. **Agent 没有自己的业务权限,只有借来的权限**——它是执行能力而非业务主体:张三看不到的客户它也不该看到,张三只能提交草案它也不能直接让草案生效。
2. **接口可访问只代表技术通道存在**——本地类型能编译不代表真实环境的字段、键、返回结构已对齐;接口报错时普通程序会停下等人,Agent 会重试、换工具、继续推进,一次偏差被放大成整条链路的不确定性。
3. **可观测性要解释决策行为而非系统行为**——Agent 错的往往不是一行代码,而是一条决策链路:为什么选这个工具、为什么判这条数据匹配、为什么在这停又接着走。没记下来,事后只能猜。

!!! warning "最容易被偷懒破坏的一层"
    给它配一个能看所有数据的公共账号,再靠 Prompt 约束"不要看不该看的数据"。它没有攻击系统、没有绕过登录——只是用了你给它的权限,**而你给多了**。界面能跑、接口能通、模型解释得头头是道,但权限边界已经被打穿。

## 原理

### 1. 身份三层边界:登录人 / 被代理人 / 工具身份

| 层 | 是谁 | 职责 | 典型错误 |
| --- | --- | --- | --- |
| 登录人(发起人) | 真实登录用户 | 谁发起按谁鉴权,谁批准记谁责任 | 审计只记"Agent 改了数据",答不出谁让它改的 |
| 被代理人(借用身份) | Agent 替谁做事 | 决定能看什么、能改什么 | 切换身份后仍夹带登录人的 admin 角色 |
| 工具身份(技术通道) | 服务端凭证 / 系统 token | 只承担调用通道,不承担业务授权 | 技术账号当业务授权用,抹平所有数据权限 |

!!! tip "一句话说白"
    系统 token 可以存在,但必须被包在有副作用声明、有可见范围、有审计标签的**只读工具**里。Agent 可以走技术通道,**业务授权必须回到发起人和原有权限体系**。

数据边界 = **用户身份(按谁的权限查)+ 数据范围(组织/团队/客户/订单)+ 动作范围(查询/草案/修改/生效,各是不同权限等级)**。工具要有治理元数据(`side_effect`、`approval_mode`、`visible_to_systems`、`audit_tags`),读权限不许和写权限绑在同一工具里。

### 2. 集成不稳的四个典型原因

| 现实 | 失败形态 | 工程对策 |
| --- | --- | --- |
| 契约漂移 | 代码用的字段在真实环境元数据里不存在;行 ID 被当备选键,但目标表没定义这个键 | 接入前用真实元数据/探测接口确认实体、字段、键;运行时校验必要字段、业务状态与影响对象,不满足就停在集成层 |
| 幂等缺失 | 外部系统把同一笔回调推两次;重试对已产生的副作用再执行一次 | 稳定幂等键 + 存储层唯一约束 + 检查点/outbox,而不是"先查再写" |
| 事务边界(半成功) | 批量导入前几行成功、某行失败;标成功会隐藏失败,标失败会掩盖已写入 | 保留成功行继续处理,记录新建/更新/失败数与失败行号,批次状态为 `partial_failed` |
| 权限上下文丢失 | 集成层用技术账号调用,发起人身份没透传,原有数据权限失效 | 身份透传:凭证只当技术通道,业务鉴权仍按发起人 |

其中最隐蔽的是契约漂移:**接口文档和本地类型都不是最后真相,运行环境才是**。Agent 需要的不是"可调用的 API",而是一份能约束结果、失败和副作用的**可执行业务契约**。

### 3. 四类记录与最小记录契约

可观测性要在**设计时埋进去**,事后补的日志永远缺最关键的一段(选工具的理由、规则命中、确认前展示的材料只在执行当下出现)。原文把它收敛成四类记录:

- **决策链路**:来自哪个用户意图、处在哪个 task、命中什么前置事实或规则,而不只是"调用了 `search_customers`";
- **工具调用**:必须可对账——稳定 `tool_id`、参数摘要、返回状态、错误类型、耗时;同一调用流式推送多次时,去重不能丢真正的后续结果;
- **状态变迁**:必须可解释——不只知道是 `running/success/error/waiting_confirmation`,还要知道**为什么**(不可逆?超阈值?权限不够?转移不合法),四种原因接法完全不同;
- **人工接管点**:触发规则、给谁的上下文、决议(批准/驳回/缩小范围/改草案)、处理人、决议后恢复的 task/step/tool call。

四类记录落成最小四类对象,用 ID 串成一条链:

| 对象 | 最小字段 | 回答的问题 |
| --- | --- | --- |
| `Run` | `run_id`、会话引用、`agent`、开始时间、最终状态 | 这次执行从哪来到哪去 |
| `Step` | `step_id`、`run_id`、状态、开始/结束时间、动作理由摘要 | 卡在哪一步、卡了多久、为什么走这一步 |
| `ToolCall` | `tool_id`、`step_id`、工具名、参数摘要、结果引用、错误分类 | 调了哪个工具、传了什么、拿回了什么 |
| `Approval` | `approval_id`、`step_id`、触发规则、决议、处理人、决议时间 | 谁在什么时候接住了风险 |

参数摘要与结果引用要**按数据分级脱敏**:凭据、完整个人信息、不该回放的工具原文不应为了"可观测"被扩散保存;真正需要的是可定位、可核验、可授权查看的证据。

## 代码 / 实现

### 代码 1:权限作用域 `build_scope`(登录用户 + 切换用户)

默认以登录人为准;开发态切换时身份被整体替换,**绝不继承登录人的管理员角色**——钉死"你以为在验证销售视角,实际系统还夹带着管理员身份"这类权限错觉。

```python
# 权限作用域:登录人 / 被代理人 / 鉴权候选 / 审计链 四分离
from dataclasses import dataclass


@dataclass
class Scope:
    user_id: str                # 生效身份:Agent 替谁做事
    role: str                   # 生效角色:按谁的权限鉴权
    org: str                    # 生效组织范围
    identity_candidates: list   # 参与鉴权的候选身份(不含真实登录人邮箱)
    audit_chain: list           # 审计链:真实登录人 -> 被代理人(不参与鉴权)


def build_scope(login_user, dev_switched_user=None, debug=False):
    """构造一次 Agent 运行的作用域。

    - 不切换:身份即登录人,role 沿用登录人;
    - 开发态切换:身份切到被代理人,但绝不继承登录人的角色 / 候选身份。
    """
    user_id = login_user.get("id") or login_user["email"]
    role = login_user["role"]
    org = login_user.get("org", "default")
    candidates = [login_user["email"]]

    if dev_switched_user:
        user_id = dev_switched_user["id"]
        role = dev_switched_user["role"]
        org = dev_switched_user.get("org", org)
        # 关键:候选身份被整体替换,登录人(可能带 admin)不再参与鉴权
        candidates = [f"{dev_switched_user['id']}#{dev_switched_user['role']}"]

    audit_chain = [login_user["email"]]
    if dev_switched_user:
        audit_chain.append(user_id)
    return Scope(user_id=user_id, role=role, org=org,
                 identity_candidates=candidates, audit_chain=audit_chain)


# 开发态身份切换:登录人是 admin,页面切到销售视角
real_login = {"email": "admin@example.com", "role": "admin", "org": "HQ"}
switched_user = {"id": "sales-user-1", "role": "sales", "org": "East"}

scope = build_scope(login_user=real_login, dev_switched_user=switched_user, debug=True)

assert scope.role == "sales"
assert scope.user_id == "sales-user-1"
assert scope.org == "East"
assert "admin@example.com" not in scope.identity_candidates  # 不继承管理员身份
assert "admin@example.com" in scope.audit_chain              # 审计仍可追到真实发起人

print("生效身份:", scope.user_id, "@", scope.role, "/", scope.org)
print("鉴权候选:", scope.identity_candidates)
print("审计链:  ", scope.audit_chain)
```

运行结果:生效身份切到 `sales-user-1 @ sales / East`,鉴权候选里不再出现 `admin@example.com`;审计链仍保留 `admin@example.com -> sales-user-1`(事后可追责)。**鉴权要"干净",审计要"完整"**。

### 代码 2:事件 envelope 归一化、去重与 `tool_id` 对账

演示三件事:散乱事件统一成带 `run_id/task_id/agent/sequence` 的 envelope;按 `(type, tool_id)` 去重流式推送的重复;对账校验每个工具调用恰好一次开始、一次结束。

```python
# 工具事件:统一 envelope + 按 tool_id 去重 + 对账
from collections import defaultdict


def normalize(ev, run_id, task_id, agent, sequence):
    """把散乱的工具事件统一成 envelope,带上链路定位字段。"""
    return {
        "run_id": run_id,
        "task_id": task_id,
        "agent": agent,
        "sequence": sequence,
        "type": ev["type"],
        "tool_id": ev.get("tool_id"),
        "tool": ev.get("tool"),
        "ts": ev.get("ts"),
        "payload": ev.get("payload"),
    }


def dedup(events):
    """按 (type, tool_id) 去重:同一个工具调用不重复开始 / 结束。"""
    seen, out = set(), []
    for ev in events:
        key = (ev["type"], ev["tool_id"])
        if key in seen:
            continue
        seen.add(key)
        out.append(ev)
    return out


def balance(events):
    """对账:每个 tool_id 恰好一次 start + 一次 end,否则给出缺失清单。"""
    starts, ends = defaultdict(int), defaultdict(int)
    for ev in events:
        if ev["type"] == "tool_start":
            starts[ev["tool_id"]] += 1
        elif ev["type"] == "tool_end":
            ends[ev["tool_id"]] += 1
    problems = []
    for tool_id in set(starts) | set(ends):
        if starts[tool_id] != 1 or ends[tool_id] != 1:
            problems.append(f"{tool_id}: start={starts[tool_id]} end={ends[tool_id]}")
    return problems


# 流式更新里同一个工具调用可能被推送多次:同一 call_1 只能有
# 一次 tool_start 和一次 tool_end,存储层必须按 tool_id 去重。
raw = [
    {"type": "tool_start", "tool_id": "call_1", "tool": "search_customers",
     "ts": "09:00:01", "payload": {"q": "近期风险客户"}},
    {"type": "tool_start", "tool_id": "call_1", "tool": "search_customers",   # 重复推送
     "ts": "09:00:01", "payload": {"q": "近期风险客户"}},
    {"type": "tool_end", "tool_id": "call_1", "tool": "search_customers",
     "ts": "09:00:03", "payload": {"status": "ok", "hits": 3}},
    {"type": "tool_end", "tool_id": "call_1", "tool": "search_customers",     # 重复推送
     "ts": "09:00:03", "payload": {"status": "ok", "hits": 3}},
    {"type": "tool_start", "tool_id": "call_2", "tool": "gen_report",
     "ts": "09:00:05", "payload": {}},
    {"type": "tool_end", "tool_id": "call_2", "tool": "gen_report",
     "ts": "09:00:09", "payload": {"status": "ok"}},
]

run_id, task_id, agent = "run_88", "task_3", "crm-agent"
envelopes = [normalize(e, run_id, task_id, agent, i) for i, e in enumerate(raw)]
clean = dedup(envelopes)
problems = balance(clean)

print(f"原始事件 {len(raw)} 条 -> 去重后 {len(clean)} 条")
for ev in clean:
    print(f"  seq={ev['sequence']} {ev['type']:<10s} {ev['tool_id']:<6s} {ev['tool']}")
print("对账:", "每对 start/end 都齐全 ✔" if not problems else problems)
```

运行结果:`call_1` 推送两次开始、两次结束,去重后各保留一次,`balance` 返回空清单。若只有 `tool_start` 没有 `tool_end`,它会给出 `call_x: start=1 end=0`——排查"工具卡住"的第一条线索。

!!! note "去重与「不重复开始」是两件事"
    去重保证同一调用不重复展示;"不能丢掉真正的后续结果"是另一件事——去重过度会把新的真实调用也吞掉。`tool_id` 稳定 + 对账校验,才能把"模型说要查 / 工具实际查了 / 返回了结果 / 继续生成报告"连成同一条可复盘的链。

## 实践 / 应用

### 上线前六条检查线

| # | 检查线 | 不合格的样子 |
| --- | --- | --- |
| 1 | 事件有没有统一 envelope | 没有 `run_id/task_id/agent/sequence/timestamp`,事件无法排序和重放 |
| 2 | 工具调用有没有稳定 ID | 没有 `tool_id`,工具开始/进度/结果/展示/后续输出串不起来 |
| 3 | 步骤有没有状态和耗时 | 只看到"加载中",不知道卡在哪一步、卡了多久、是执行/等待/失败 |
| 4 | 进度日志能否在完成后回放 | 流式结束后只剩最终回答,工程复盘无据可查 |
| 5 | 结果展示和模型上下文是否分开 | 大结果塞回上下文,模型省了 token,人丢了证据 |
| 6 | 错误能否分类 | 网络/权限/业务校验/契约不匹配/人工拒绝全变成"执行失败" |

### 权限检查清单:四个"默认"

| 默认 | 含义 | 反例 |
| --- | --- | --- |
| 默认只读 | 查询、生成草案、修改状态、触发外部流程是不同权限等级 | 读权限和写权限绑在同一个工具里 |
| 默认拆分读写 | 系统 token 只包在只读工具里,带副作用声明与审计标签 | 一个全量账号既查又写 |
| 默认高风险接管 | 超范围、不可逆、批量动作进入人工接管而非模型临场判断 | 越界时模型自己决定降级或继续 |
| 默认可审计 | 每步都能回答"谁发起 / 以谁身份 / 看了什么改了什么 / 谁批准" | 只记录"Agent 执行成功" |

每个动作上线前再过六个问题:**谁发起?能看到哪些数据?谁保证只能看到这些?能写什么?超过范围时怎么办?事后怎么查?**——"理论上能看全部,但 Prompt 会限制"这类答案不合格,答不上来就不要上线。

### 每个工具补一份"最小集成契约"

**一个接口地址只回答"怎么调用",集成契约回答"调用之后发生了什么,失败时怎么收场"**,六个字段:

| 字段 | 要回答的问题 |
| --- | --- |
| 动作性质 | 只读查询,还是会改数据、发通知、提交审批? |
| 成功定义 | 除 HTTP 200 外,必要字段、业务状态、影响对象须同时出现? |
| 重复语义 | 再执行一次得到同一结果,还是再次产生副作用?(决定幂等键) |
| 中间状态 | 任一步失败后,哪些已完成、哪些可继续或补偿?(决定半成功) |
| 真相来源 | 字段、键、返回结构以元数据、服务定义还是真实探测为准? |
| 失败出口 | 重试 / 查状态 / 回滚 / 暂停 / 转人工 / 降级只读,按风险分档 |

只读查询可能只需要返回校验和超时上限;改状态、提交审批、发通知的动作必须补齐幂等、状态、补偿、审计和人工接管——**风险不同集成成本不同,但不能只留一个接口地址和一段提示词**。

## 总结

- **黑盒不应直接获得生产写权限。** 一个会自己做决定、还能改业务数据的东西,若无法还原动作依据,就不应获得生产写权限——上线前先问"出问题时我能不能还原它当时的完整执行和决策依据"。
- 权限:Agent 只有**借来的权限**;三层身份各司其职,数据边界 = 用户身份 + 数据范围 + 动作范围,判断权限的**位置**要从模型移到系统。
- 集成:接口通了只代表通道存在;**契约、幂等、半成功、超时降级**才是接稳的边界;模型可提意图,但不能重新定义外部系统的事务、契约和失败语义。
- 可观测性:把**决策链路、工具调用、状态变迁、人工接管点**四类记录在设计时埋进去,用 `run_id/task_id/step_id/tool_id` 串成可还原的链;最小记录契约就是 `Run/Step/ToolCall/Approval` 四类对象。

## 延伸阅读

- 站内:[Ontology 与 Agent 企业落地](index.md)、[Ontology 的四大技术](ontology-four-technologies.md)、[Agent 开发实践](../../03-agents/agent-practice.md)、[Agent 工具调用与工具治理](../../03-agents/tool-calling.md)、[OpenWorker 架构与 Harness](../../08-harness/openworker-architecture.md)
- 外部:微信公众号《企业 Agent 工程化手记》第 6/7/8 篇(原文链接见收件箱登记);原始资料存档于 `docs/inbox/enterprise-agent-engineering-src-b4.md`、`src-b3.md`、`src-b1.md`
