# OAG 与 Ontology 驱动的企业 Agent:RAG 之后的下一个范式

> **一句话摘要**:RAG 让 LLM"知道",OAG(Ontology Augmented Generation)让 LLM"做到"。本文从 Palantir 实践出发,拆解 OAG 如何以 Ontology 为受治理的业务世界模型,通过五层 Agent-Ontology 架构,把"语义锚定 + 动作执行 + 权限治理 + 审计回放"焊进企业系统——这是 RAG 之后的下一个范式。
>
> **来源**:综合《本体论/案例分析》系列素材三篇(OAG 替代 RAG / 别把 RAG 当架构 / 2500 年哲学概念如何变成 4000 亿市值)与 Palantir 官方 AIP / Ontology 文档。

## 概念

### 为什么 RAG 不够用:解决"知道",不解决"做到"

RAG(Retrieval Augmented Generation)被几乎所有企业试过一轮,结果普遍是"聊天可以、干活不行"。Palantir 归结为三个根本局限:

- **检索的是文本,不是语义**:RAG 检索文本片段,但 LLM 需要的是业务实体的语义——"订单"在 CRM、ERP、物流系统里可能指完全不同的东西。
- **只读不写**:只提供信息检索,不能执行操作或回写。"帮我修改客户 A 的信用额度",它能找到文档,但改不了。
- **缺乏治理**:检索范围基于文档权限,而非业务操作级细粒度控制。能读到"采购审批流程"的 Agent,不代表应该能实际发起采购审批。

!!! note "一句话概括"
    RAG 的三个局限本质是同一个:**RAG 解决"知道",不解决"做到"**。企业 AI 的真正价值恰恰在"做到"——接入系统、读取状态、做出判断、推进流程、留下记录。

业务方真正想问的,往往与 RAG 卡住的地方对不上:

| 业务方真正想问的 | RAG 容易卡住的地方 |
| --- | --- |
| 这个客户该不该升级处理 | 客户等级、合同、历史投诉、SLA、当前队列不是一段文本 |
| 这台设备要不要提前保养 | 设备状态、遥测、工单、备件、经销商能力要放在一起判断 |
| 这张订单能不能改交期 | 订单、库存、产能、物流、客户优先级和审批规则互相牵连 |
| 这份合同能不能自动进入下一步 | 合同状态、风险项、授权人、例外条款和审批动作都要受控 |

### OAG 是什么:从文本检索到语义锚定

**OAG(Ontology Augmented Generation)** 是 Palantir 给出的答案——把 RAG"提升到新水平":LLM 不再检索文本片段,而是通过 Ontology 访问**受治理的、类型化的、实时的、双向的知识图谱**。Object(对象)、Link(关系)、Property(属性)构成名词世界;Action(动作)、Function(逻辑)、Dynamic Security(动态安全)构成动词世界。

!!! tip "一个有用的转译"
    RAG 是 Agent 的**资料检索层**,Ontology 才是 Agent 的**业务世界**:前者解决"应该看到哪些上下文",后者解决"企业里有哪些对象、关系、状态、动作、权限和逻辑"。没有它,Agent 只能猜。

### 世界模型优先于语言模型

OAG 的核心命题:**优先考虑世界模型,而非语言模型**("Prioritize the world model over the language model")——AI 的可靠性不依赖 LLM 的内部知识(可能过时、可能幻觉),而依赖 Ontology 提供的、受治理的业务现实。更直白地说:**别让 LLM 猜你的企业是什么样,直接告诉它。**

!!! warning "比回答错知识更危险"
    用过期世界做当前决策:设备已转移给新客户,Agent 仍按旧客户处理;工单已升级,Agent 仍建议一线处理;员工调岗后,Agent 仍继承旧权限。所以 Ontology 不只是"对象表",还要回答:事实何时成立(时间)、来自哪(provenance)、谁改过(审计)、现在是否有效(版本)、能否回放(trace)。

## 原理

### ① OAG 的三类工具:读、算、做

| 工具 | 作用 | 对比 RAG |
| --- | --- | --- |
| **数据工具**(Data tools) | 通过 Ontology 查询获取结构化业务数据 | 直接查询客户 A 的 Object(含属性、关联订单、信用记录),而非"关于客户 A 的报告" |
| **逻辑工具**(Logic tools) | 调用 Functions 执行确定性计算(预测器、优化器) | 不是让 LLM 用概率推理猜需求预测,而是调用已验证的需求预测模型 |
| **操作工具**(Action tools) | 通过 Action Types 执行受治理的操作并回写结果 | 不是"建议你修改信用额度",而是直接执行——前提是权限校验通过 |

### ② 五层 Agent-Ontology 交互架构:确定性与概率性分离

| 层 | 名称 | 决策者 | 职责 |
| --- | --- | --- | --- |
| 第 1 层 | **Context Layer** 上下文层 | 系统(确定性) | 按规则自动注入相关 Ontology 上下文(不是 LLM 猜该查什么) |
| 第 2 层 | **Query Layer** 查询层 | LLM | 决策查询哪些对象和关系,通过 OSS 查询 Object Sets |
| 第 3 层 | **Logic Layer** 逻辑层 | LLM | 决策调用哪些 Functions(预测、优化等确定性计算) |
| 第 4 层 | **Action Layer** 操作层 | LLM | 决策执行哪些受治理的操作,敏感操作需人类确认 |
| 第 5 层 | **Governance Layer** 治理层 | 系统(确定性) | 端到端约束权限、审计和安全边界,贯穿前四层 |

关键设计是**把确定性控制(第 1、5 层)与 LLM 概率性决策(第 2-4 层)分离**:上下文注入与安全治理由系统保证,LLM 无法绕过权限;查询、逻辑、操作由 LLM 在受控范围内自主决策。

!!! tip "设计哲学一句话"
    让 LLM 做它擅长的(理解意图、选工具、组参数),让确定性系统做它必须做的(权限、上下文、审计)。

### ③ OAG vs RAG:一张表看清差异

| 维度 | RAG | OAG |
| --- | --- | --- |
| 检索内容 | 文本片段 | 结构化业务对象 |
| 读写能力 | 只读 | 读写双向 |
| 语义理解 | 依赖 LLM 推理 | Ontology 类型系统锚定 |
| 逻辑调用 | 无 | Functions 确定性计算 |
| 操作执行 | 无 | Action Types 事务性操作 |
| 治理范围 | 文档权限 | 业务操作级细粒度控制 |
| 回写能力 | 无 | 回写到 Ontology 和外部系统 |
| 适用场景 | 知识问答 | 企业操作决策 |

锚定方式的差异是根本的:**RAG 是文本锚定**(向量相似度找"看起来相关"的片段,片段间关联靠 LLM 概率性推断);**OAG 是语义锚定**("客户 A 关联了订单 B"由 Link Type 直接给出)。所以 OAG 能说"客户 A 确实关联订单 B,订单 B 已发货",而不是"根据文档,可能有关联"。

### ④ 动词一等公民:Action Type 与三区并列

传统本体(OWL、RDF、知识图谱)的范式是"读":定义概念、查询、推理,回答"是什么"。Palantir 的范式是"读 + 做 + 学",多了一个维度:**动作**。一个 **action type** 是"一组对对象、属性、链接的变更,作为一个事务提交",含输入表单、校验规则、副作用编排、版本控制、审计日志——如"分配员工"不只改 role 字段,还自动创建到新 Manager 的链接,一个事务提交后反映到所有应用并回写源系统。

!!! note "OWL 里没有动词的一等表达"
    OWL 用属性和公理描述状态,不描述受控的状态迁移。Palantir 等于**把状态机、把业务流程直接焊进了本体层**——这是"知识图谱是只读推理工具,Palantir 的 Ontology 是可执行操作面"的本质区别。

反直觉的设计:Action、Function、Security **不是堆叠的三层,而是并列的三个区**。

| 区 | 内容 | 类比 |
| --- | --- | --- |
| Semantic 区 | object、link、property、interface | 名词:谁是谁、有什么属性 |
| Kinetic 区 | action types、functions | 动词:状态怎么变、逻辑怎么算 |
| Governance 区 | security policies | 权限:谁能看、谁能做、谁能批准 |

**为什么并列而不是堆叠?** 一个 action 的执行要同时裁决语义合法性、业务规则、权限三件事,必须**原子地一起裁决**——分层堆叠的话权限校验会落在动作之后,系统早出事了。权限不是事后 ACL,而是**运行时实时计算**的:生产团队、仓储、供应链分析师对同一对象看到不同字段;触发采购订单与运行场景模拟的权限是两套。

### ⑤ 与主流 Agent 框架对比:四个差距

对照 LangChain、CrewAI、LangGraph:

| 差距 | 主流 Agent 框架 | Palantir AIP + Ontology |
| --- | --- | --- |
| **工具受控度** | 工具是 Python 函数 + docstring,框架不管权限、副作用、审计、回滚 | control plane 内生化:弹确认、校验、留痕;动作是"可信的",主流框架是"裸的" |
| **Context 语义性** | RAG:文档切块、向量化、塞 prompt——文本碎片、无关系、无权限、只读 | OAG:OSDK 查询强类型对象及链接;权限感知;可回写 |
| **应用层** | 搭完 Agent 用户面对一个聊天框 | 面对业务应用(Object Explorer / Quiver / Workshop / AIP Logic),Agent 是嵌在应用里的能力 |
| **可审计性** | trace 靠 LangSmith 等外挂 | 每个 action 有 metrics + logs + version control,"谁在何时调了哪个 action、改了哪些对象、依据什么规则"完整可查 |

!!! note "一个具体场景"
    业务人员问"客户 X 的订单能不能延期"。LangChain agent 检索文档拼答案,可能答错、可能泄露没权限的数据、改不了状态;AIP agent 查 Customer 对象,遍历 Order 链接,调"延期" action type,弹确认,回写 ERP——"agent 真帮我办了事"。

### ⑥ GraphRAG ≠ 企业 Ontology

GraphRAG 是进步(从"找相似文本"走向"找结构化上下文"),但还不是企业 Ontology:

| 维度 | GraphRAG | 企业 Ontology |
| --- | --- | --- |
| 主要目标 | 提升检索和回答质量 | 建立可操作的业务世界 |
| 主要对象 | 文档中的实体、关系、社区、子图 | 企业业务对象、状态、动作、权限、逻辑 |
| 是否负责写回 | 通常不是核心 | 必须定义动作和状态变更 |
| 是否承载权限 | 可以辅助过滤 | 必须与企业权限治理绑定 |
| 是否承载业务生命周期 | 不一定 | 必须覆盖对象生命周期和动作合法性 |

GraphRAG 可以成为 Ontology 的一部分或检索增强层。**GraphRAG 让 Agent 更会找关系;Ontology 让 Agent 处在一个可治理的业务世界里。**

### ⑦ 五类业务结构 + SDD→Ontology 转译

| 结构 | 例子 | 没有它会怎样 |
| --- | --- | --- |
| **Object** 对象 | 客户、订单、设备、工单、合同、备件 | Agent 不知道自己在处理什么 |
| **Relationship** 关系 | 设备属于客户,工单关联设备 | Agent 只能看相似文本,不能跨对象推理 |
| **State** 状态 | 待处理、已派工、等待备件、已关闭 | Agent 不知道动作是否合法 |
| **Action** 动作 | 创建工单、升级、派工、冻结、审批 | Agent 只能建议,不能进入流程 |
| **Policy** 策略 | 谁能看、谁能改、谁能批准 | Agent 可能越权或误操作 |

!!! warning "没有业务结构时的"临时补洞""
    模型拿错客户→在 prompt 里写"请注意客户信息";状态错了→加 if 判断;权限不清→不让 Agent 写回;关系查不到→让模型自己推。这些补丁短期能跑,长期是维护灾难。Ontology 的价值是**让 Agent 不靠猜,让工程师不靠补丁**。

**SDD→Ontology 转译:从 SDD(Solution Design Document)里抽对象。** 例如 SDD 写"售后主管在工单后台查看高风险设备故障;Agent 读取设备遥测、历史维修、服务合同、备件库存和经销商服务能力,判断是否建议升级工单、请求备件或派发现场服务;高价值客户和合同例外必须人工确认;所有建议、采纳和修改写入审计记录",拆成:

| SDD 片段 | Ontology 产物 |
| --- | --- |
| 售后主管 / 工单后台 | User role & permission scope / Interface & trigger point |
| 高风险设备故障 | WorkOrder + Equipment + RiskSignal |
| 设备遥测 / 历史维修 / 服务合同 / 备件库存 / 经销商能力 | Equipment telemetry / MaintenanceHistory / ServiceContract / PartInventory / DealerCapability |
| 升级工单 / 请求备件 / 派发现场服务 | EscalateWorkOrder / RequestPart / DispatchTechnician actions |
| 高价值客户必须人工确认 | Policy / human approval gate |
| 写入审计记录 | Trace / audit event |

SDD 把业务需求写到可执行;Ontology 把可执行规格变成 Agent 可读取、可判断、可调用的对象世界。跳过这一步,后面全都会尴尬:RAG 难绑定业务对象;Tool Calling 参数与对象对不齐;Workflow 状态流转靠硬拼;权限只能在工具或 prompt 里补。**Ontology 应从第一份 SDD 里长出来。**

## 代码 / 实现

纯 Python 演示两个核心机制:**① OAG 式"语义锚定检索"**(按业务对象 + 关系 + 读权限过滤,而非文本相似度);**② 五层架构中"确定性治理层拦截"**(LLM 只能提议动作,权限不足的动作被第 5 层拒绝并留审计)。合并进一个脚本,便于与 RAG 文本检索对照:

```python
"""OAG 演示:语义锚定检索 + 治理层动作拦截。"""
import difflib

# ---------- 1. 业务对象世界(Ontology 的 Object + Link) ----------
CUSTOMERS = [
    {"id": "C001", "name": "Acme 制造", "level": "VIP", "credit_limit": 500_000},
    {"id": "C002", "name": "Beta 贸易", "level": "普通", "credit_limit": 50_000},
]
ORDERS = [
    {"id": "ORD-1001", "customer_id": "C001", "status": "已发货", "amount": 320_000},
    {"id": "ORD-1002", "customer_id": "C002", "status": "待审批", "amount": 80_000},
]
EQUIPMENT = [
    {"id": "EQ-88", "serial": "AC-2201", "status": "高风险", "customer_id": "C001"},
    {"id": "EQ-12", "serial": "AC-3308", "status": "正常", "customer_id": "C002"},
]

# Link Types:显式关系,检索时由系统跟随,不靠 LLM 猜
def orders_of(customer_id):
    return [o["id"] for o in ORDERS if o["customer_id"] == customer_id]

def owner_of(equipment_id):
    cid = next(e["customer_id"] for e in EQUIPMENT if e["id"] == equipment_id)
    return next(c["name"] for c in CUSTOMERS if c["id"] == cid)

# ---------- 2. Action Types(动词)与所需权限 ----------
ACTIONS = {
    "adjust_credit_limit": {"perm": "credit.admin", "desc": "调整客户信用额度"},
    "ship_order":          {"perm": "logistics.ship", "desc": "确认订单发货"},
}
# 当前 Agent 只有读权限,治理层将拦截所有动作
AGENT = {
    "id": "agent-support",
    "read_object_types": {"customer", "order", "equipment"},
    "permissions": set(),
}

# ---------- 3. RAG:文本相似度检索(对照实验) ----------
DOCS = [
    "信用额度政策:VIP 客户调整信用额度需财务审批。",
    "订单发货流程:确认发货后状态变为已发货。",
    "设备保养手册:高风险设备应优先保养。",
]

def rag_retrieve(query):
    """把 query 与文档做字符相似度,返回最像的那段文本。"""
    return max(DOCS, key=lambda d: difflib.SequenceMatcher(None, query, d).ratio())

# ---------- 4. OAG:语义锚定检索(对象 + 关系 + 读权限) ----------
def oag_query(object_type, **filters):
    """查询层(第 2 层)经由类型系统与读权限过滤,返回结构化对象与关系。"""
    if object_type not in AGENT["read_object_types"]:
        return {"error": "access_denied",
                "reason": f"agent 无 {object_type} 读权限"}
    table = {"customer": CUSTOMERS, "order": ORDERS, "equipment": EQUIPMENT}[object_type]
    matched = [o for o in table if all(o.get(k) == v for k, v in filters.items())]
    enriched = []
    for o in matched:
        item = dict(o)
        if object_type == "customer":
            item["orders"] = orders_of(o["id"])       # 跟随 Link Type
        elif object_type == "equipment":
            item["owner"] = owner_of(o["id"])
        enriched.append(item)
    return {"objects": enriched, "count": len(enriched)}

# ---------- 5. 治理层:动作级权限裁决(第 5 层,确定性) ----------
AUDIT = []  # 每次动作尝试都留下审计记录

def governance_gate(action_name, target):
    """LLM 只能'提议'动作;是否执行由治理层裁决。"""
    spec = ACTIONS[action_name]
    if spec["perm"] not in AGENT["permissions"]:
        entry = {"actor": AGENT["id"], "action": action_name,
                 "target": target["id"], "verdict": "denied",
                 "reason": f"缺少权限 {spec['perm']}"}
        AUDIT.append(entry)
        return {"allowed": False, "audit": entry}
    entry = {"actor": AGENT["id"], "action": action_name,
             "target": target["id"], "verdict": "allowed",
             "reason": "permission ok"}
    AUDIT.append(entry)
    # 执行副作用并"回写"(Ontology 变更是事务性的)
    if action_name == "adjust_credit_limit":
        target["credit_limit"] *= 2
    elif action_name == "ship_order":
        target["status"] = "已发货"
    return {"allowed": True, "audit": entry}

if __name__ == "__main__":
    print("=" * 60)
    print("场景 A:RAG 检索 —— 只拿到'看起来相关'的文本")
    print("  用户问:Acme 的订单能不能按期交付?")
    print("  RAG 命中:", rag_retrieve("Acme 的订单能不能按期交付"))
    print()
    print("场景 B:OAG 语义锚定检索 —— 拿到结构化对象与关系")
    res = oag_query("order", customer_id="C001")
    print("  查询 order where customer_id=C001:")
    print(" ", res["objects"])
    print()
    print("  再查订单背后的人:customer C001 的关联订单")
    print(" ", oag_query("customer", id="C001")["objects"])
    print()
    print("场景 C:治理层拦截 —— LLM 提议'调整信用额度',权限不足")
    r = governance_gate("adjust_credit_limit", CUSTOMERS[0])
    print("  动作结果:", r["allowed"], "|", r["audit"]["reason"])
    print()
    print("场景 D:读权限之外的检索被拒绝")
    res = oag_query("contract")  # contract 不在读白名单
    print(" ", res["error"], "-", res["reason"])
    print()
    print("审计日志:")
    for e in AUDIT:
        print(" ", e)
```

**运行**:`python3 palantir-oag-agent-demo.py`(纯标准库)。逐段解读:

- **1. 业务对象世界**是 Object + Link;`orders_of`/`owner_of` 是显式 Link Type——Agent 不用推断"谁属于谁"。
- **2. Action Types** 定义"动词"及所需权限(调整信用额度要 `credit.admin`,发货要 `logistics.ship`);当前 Agent **没有写权限**,演示"读与写是两套权限"。
- **3. RAG 对照**:`difflib.SequenceMatcher` 模拟文本相似度检索。
- **4. OAG 语义锚定检索**:首行做**读权限检查**(治理前置于查询层),随后跟随 Link 附加关联对象。
- **5. 治理层**:`governance_gate` 是"确定性拦截器"——LLM 只能提议动作,是否执行由权限裁决;无论放行还是拒绝都写入 `AUDIT`,形成可回放审计链。

**预期输出**(python3 实测):

```
============================================================
场景 A:RAG 检索 —— 只拿到'看起来相关'的文本
  用户问:Acme 的订单能不能按期交付?
  RAG 命中: 订单发货流程:确认发货后状态变为已发货。

场景 B:OAG 语义锚定检索 —— 拿到结构化对象与关系
  查询 order where customer_id=C001:
  [{'id': 'ORD-1001', 'customer_id': 'C001', 'status': '已发货', 'amount': 320000}]

  再查订单背后的人:customer C001 的关联订单
  [{'id': 'C001', 'name': 'Acme 制造', 'level': 'VIP', 'credit_limit': 500000, 'orders': ['ORD-1001']}]

场景 C:治理层拦截 —— LLM 提议'调整信用额度',权限不足
  动作结果: False | 缺少权限 credit.admin

场景 D:读权限之外的检索被拒绝
  access_denied - agent 无 contract 读权限

审计日志:
  {'actor': 'agent-support', 'action': 'adjust_credit_limit', 'target': 'C001', 'verdict': 'denied', 'reason': '缺少权限 credit.admin'}
```

对照体会:场景 A 只给"流程文本",场景 B 返回订单**真实状态**;场景 C 证明"读到文档 ≠ 有权限执行";场景 D 证明读权限也被类型系统约束——正是 ④ 节"三区并列"的运行时形态。

## 实践 / 应用

### 何时需要 Ontology:一张判断表

不是所有场景都需要完整 Ontology——制度问答、文档检索、材料总结,RAG 可能足够。真正的问题是**不要把 RAG 场景包装成 Agent 项目**:

| 场景特征 | RAG 可能够用 | 需要 Ontology |
| --- | --- | --- |
| 用户目标 | 查资料、问制度、找案例 | 判断业务状态、推进流程、触发动作 |
| 数据形态 | 主要是文档和知识库 | 文档 + ERP/CRM/MES/工单/合同/库存/传感器 |
| 业务对象 | 不需要显式对象 | 必须识别客户、订单、设备、合同等对象 |
| 关系复杂度 | 单文档或少量上下文 | 跨对象、多系统、多跳关系 |
| 动作风险 | 不写回系统 | 会改状态、发通知、创建记录、提交审批 |
| 权限要求 | 简单文档权限 | 对象级、字段级、动作级、场景级权限 |
| 验收方式 | 回答准确率和引用 | 任务完成率、动作正确率、人工采纳率、错误回放 |

右侧占多数,就不要再纠结"RAG 怎么调得更准"——**先把对象层建起来**。

### 第一个 Ontology 不要大:从单一 Agent 场景开始的 8 步

| 步骤 | 产物 | 判断标准 |
| --- | --- | --- |
| 1. 从 SDD 抽对象 | Object list | 这条业务链里出现哪些对象 |
| 2. 定义对象属性 | Properties | 哪些字段是 Agent 判断必须读的 |
| 3. 定义对象关系 | Links | 哪些关系决定判断或动作 |
| 4. 定义状态机 | Lifecycle | 对象可以处于哪些状态 |
| 5. 定义动作 | Actions | 哪些动作由 Agent 建议、草稿或触发 |
| 6. 定义权限 | Policy | 谁能看、谁能改、谁能批准 |
| 7. 定义事件和审计 | Trace | 每次判断和动作如何回放 |
| 8. 定义样本 | Eval set | 什么案例证明 Agent 做对了 |

这不是多写文档,是给 Agent **建运行环境**。已有数据仓库、权限系统、流程引擎时不用推倒重来——Ontology 先做薄层:ERP/CRM/MES 映射核心对象和状态,文档库提供 RAG 证据,工作流承接审批、派工等动作,Observability 记录对象、动作和结果。**先有对象层意识,否则 Agent 架构会退回聊天框。**

### MCP:让 Ontology 成为 Agent 的标准后端

Palantir 通过 **Ontology MCP** 把 Ontology 暴露为 MCP 服务器:任何支持 MCP 的 Agent 框架(Claude、GPT、开源框架)都能访问其查询、逻辑和操作能力,不用为每个框架写适配层,类型安全、权限受控、审计可追溯。

!!! note "与站内《工具调用》的衔接"
    站内 [工具调用(Tool Calling)](../../03-agents/tool-calling.md) 讲"模型怎么调工具",MCP 解决"工具从哪来"(N×M → N+M);Ontology 解决"工具**是什么**":当工具不再是任意 Python 函数,而是受治理的 action types 与 functions 时,MCP 就成为把"业务世界"暴露给所有 Agent 的**标准后端**。

### Apollo 与气隙部署:AI 在断网环境下运行

Palantir Apollo 支持**气隙部署**(air-gapped deployment):Ontology 和 AIP 可在完全隔离的网络中运行。军事和高度敏感场景里通信被干扰、互联网不可用,依赖云端 API 的 AI 系统完全瘫痪,本地 Ontology + AIP 继续工作,数据不离网、操作可审计。**Agent 的可靠性不依赖网络连接,而依赖本地 Ontology 的完整性与正确性**。

### 与站内文章的呼应

- **[工具调用(Tool Calling)](../../03-agents/tool-calling.md)**:OAG 的"操作工具"就是受治理的 tool calling——差别在执行前有权限裁决、执行后有审计。
- **[企业 Agent 工程化(一):任务边界与工具治理](enterprise-agent-boundaries-tools.md)** 与 **[企业 Agent 工程化(三):权限、集成与可观测性](enterprise-agent-permission-integration-observability.md)**:**工具是负债、替谁做事、最小记录契约**正是 OAG"工具受控度"与治理层的落地形态。
- **[企业 Agent 工程化(四):Tool、MCP、Skills、Harness 四件套](enterprise-agent-tooling-harness.md)**:Harness 的"运行时控制"在 OAG 里被内生化进第 5 层治理。
- **[Ontology as Code](ontology-as-code.md)** 与 **[Ontology 的四大技术](ontology-four-technologies.md)**:前者讲本体如何像代码一样被管理(继承/引用/版本/行为),后者讲 RDF/OWL/SPARQL/SHACL 知识表示层;OAG 在它们之上加了"动词"。
- **[RAG 与向量检索](../../02-llm/rag.md)**、**[Agent 框架选型](../../03-agents/agent-frameworks.md)**、**[AI Friendly 后端架构](../ai-friendly-architecture/ai-friendly-backend.md)**:分别对应本文的边界(RAG 的极限)、对照物(主流框架缺什么)、承接(Ontology 是"系统为 Agent 准备好"的语义骨架)。

## 总结

1. **RAG 检索文本,OAG 操作语义**——前者解决"知道",后者解决"做到";企业 AI 的价值在"做到"。
2. **确定性与概率性分离**——上下文注入与安全治理(第 1、5 层)由系统保证,查询/逻辑/操作(第 2-4 层)由 LLM 在受控范围内自主决策。
3. **动词是一等公民**——action type 把状态机焊进本体层,Action/Function/Security 三区并列、原子裁决;权限是运行时实时计算,不是事后 ACL。
4. **世界模型优先于语言模型**——别让 LLM 猜你的企业是什么样,直接告诉它。
5. **从一个小场景开始**——第一个 Ontology 从单一 Agent 场景的 8 步做起,不要一步建大平台。

**下一步学什么**:想看"动作被治理层拦截后 Agent 如何自愈",读 [企业 Agent 工程化(二):异常恢复与人工接管](enterprise-agent-recovery-handoff.md);想看纯检索侧的本体落地,读 [Ontology 的四大技术](ontology-four-technologies.md) 与 [RAG 与向量检索](../../02-llm/rag.md)。

## 延伸阅读

- 站内:[Ontology 与 Agent 企业落地](index.md)、[Ontology as Code](ontology-as-code.md)、[Ontology 的四大技术](ontology-four-technologies.md)、[企业 Agent 工程化(一):任务边界与工具治理](enterprise-agent-boundaries-tools.md)、[企业 Agent 工程化(四):Tool、MCP、Skills、Harness 四件套](enterprise-agent-tooling-harness.md)、[工具调用(Tool Calling)](../../03-agents/tool-calling.md)、[Agent 框架选型](../../03-agents/agent-frameworks.md)、[RAG 与向量检索](../../02-llm/rag.md)、[AI Friendly 后端架构](../ai-friendly-architecture/ai-friendly-backend.md)
- 外部:
  - Palantir AIP overview: https://www.palantir.com/docs/foundry/aip/overview/
  - Palantir AIP architecture overview: https://www.palantir.com/docs/foundry/architecture-center/aip-architecture/
  - Palantir Ontology overview: https://www.palantir.com/docs/foundry/ontology/overview/
  - Palantir The Ontology system: https://www.palantir.com/docs/foundry/architecture-center/ontology-system
  - Tom Gruber, *Definition of Ontology*: https://tomgruber.org/writing/definition-of-ontology.pdf
  - W3C OWL - Semantic Web Standards: https://www.w3.org/OWL/
  - Microsoft GraphRAG: https://github.com/microsoft/graphrag
  - Neo4j GraphRAG Python: https://github.com/neo4j/neo4j-graphrag-python
