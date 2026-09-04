# Palantir Foundry:5 步把数据变对象——从表到可行动的业务世界

> **一句话摘要**:Foundry 怎么把一堆表、文件、流式数据变成业务人员能理解、能操作、能写回的对象?答案压缩成 5 步:安全接入 → 管线转换 → 质量与血缘 → Ontology 建模 → 应用与行动。本文拆解每一步的工程机制,并用一个供应链中断场景走查"对象 → Function → Scenario → Action → Decision Lineage"的完整落地链路。
>
> **来源**:微信公众号《Palantir Foundry:5步把数据变对象》(作者:阿铁),https://mp.weixin.qq.com/s/Stw8OUq5DNznvw-mq7x3Dw;参考 Palantir 官方文档(Data Connection、Pipeline Builder、Code Repositories、Ontology、Object Backend、Action types);原始资料存档于 `docs/inbox/palantir-foundry-5steps-source.md`

## 概念:数据变对象意味着什么

!!! tip "一句话判断"
    Foundry 的数据工程**不是为了多做一张表**,而是为了让数据最终进入客户、订单、设备、航班、病床这些**业务对象**,并支持真实决策。数据先可信进入平台,再被管线、血缘和 Ontology 转成可操作业务对象。

传统数据平台让业务"看见"数据;Ontology 让业务能**围绕对象做决策和行动**。缺少从"数据"到"对象"再到"行动"的任何一层,企业 AI 就很容易退化成"会总结、会建议,但不能安全行动"。

!!! note "与 Palantir 系列其他篇的关系"
    本文是 Palantir 系列的操作手册视角:[理论篇](palantir-operational-ontology.md)讲范式与四维集成、[OAG 篇](palantir-oag-agent.md)讲 AI 时代、[构建案例篇](palantir-cases-and-reflection.md)讲建模流程与五大案例;本文聚焦**从数据接入到行动写回的全流程 5 步**,并以供应链走查串起全部组件。

## 原理:5 步把数据变对象

### 第一步:数据先安全进来

核心组件 **Data Connection agent**——一个部署在**客户自己网络内部**的可下载程序,充当"安全中介":不是简单从外部把数据拉走,而是在客户网络里部署受控中介,由 Foundry 管理连接与摄取。

关键事实:200+ 连接器;支持 agent / REST / JDBC 等接入拓扑;支持结构化/非结构化/流式/IoT/地理空间多模态;摄取使用**受限访问令牌**而非无边界开放。

!!! tip "第一步就已经埋下差异"
    权限、来源、血缘从数据进入平台的第一刻就开始被管理——治理不是后补,是起点。

### 第二步:转换不是脚本,是工程体系

| 场景 | 组件 | 特点 |
| --- | --- | --- |
| 可视化/低代码管线 | Pipeline Builder | 图形化构建,覆盖批处理和流处理(no-code/low-code/pro-code) |
| 生产级代码管线 | Code Repositories | git 化 IDE,支持 Python、Java、SQL |

批流不是"换个按钮":**Batch 管线**用 Spark 对变化数据集做重算;**Streaming 管线**用 Flink 持续运行、新数据到达即处理。官方文档提到流式数据进入 Ontology 的平均时间可以做到 **<15 秒**——不是只做离线分析,而是把实时业务变化送进对象世界。

### 第三步:数据质量和血缘不是事后补丁

两个容易被低估的能力:**Data Expectations**(在管线里声明数据应满足什么条件)+ **Data Health**(监控数据健康、告警、影响分析)。

白皮书关键表述 **"Treating Data like Code"**——用软件工程纪律管理数据:版本化、分支、回退、受保护分支、单元测试/CI 门控、增量计算、完整 provenance(血缘)。

!!! warning "血缘是 AI 建议可审计的前提"
    当上层 AIP 或模型给出建议,业务方会追问:结果来自哪份数据?数据是否通过质量检查?最近一次管线变更是谁合并的?模型看到的是全量、增量还是受限视图?**没有血缘,AI 建议只是黑箱答案;有血缘,它才有机会变成可审计的业务判断。**

### 第四步:Ontology 把表变成业务世界

Ontology 不是哲学课,也不是独立数据库,而是 sits on top of datasets / virtual tables / models 的 **operational layer**。映射关系:

| 数据层 | Ontology 层 |
| --- | --- |
| 行 rows | 对象 Objects |
| 列 columns | 属性 Properties |
| 关系 relationships | 链接 Links |

一行订单数据不再是 `order_id = 10086`,而是一个 Order 对象;预测延期风险不再是模型输出表,而是挂在 Order 对象上的业务判断。组件事实很具体:Object、Link、Property、**Action、Function、Interface**。

### 第五步:对象必须能被应用和行动使用

| 工具 | 用途 |
| --- | --- |
| Object Views | 可复用对象视图 |
| Object Explorer | 搜索、浏览、筛选对象 |
| Quiver | 多维分析、图表探索、实时流数据 |
| Workshop | 构建面向业务用户的对象应用 |
| Slate | 构建运营应用和交互仪表盘 |

关键区别:这些应用**围绕"对象"设计,而不是围绕"表"**。业务用户看到的不是 `dim_customer`、`fact_order`,而是"客户、订单、物料、工厂、供应商、风险方案、审批动作"。

### 技术后端:读路径、写路径与元数据

| 服务 | 负责什么 |
| --- | --- |
| OMS | 定义对象、链接、动作等元数据 |
| OSS | 对象查询读取 |
| Object Databases | 存储已索引对象数据 |
| Object Data Funnel | 编排写入与索引 |

```
读路径:应用 / LLM → OSS → Object Databases
写路径:数据源 / 用户 Action → Object Data Funnel → Object Databases
元数据:OMS 定义对象、链接、动作类型
```

对象后端在平台层,所以实时流、用户编辑、Action 写回、对象视图能放进**同一个业务语义**——不是在应用层临时拼对象。

## 代码 / 实现:供应链影响分析的最小演示(纯 Python)

用供应链场景演示"对象网络 + 影响传播":供应商 SUP-027 停产,找出所有依赖 PART-884 的客户订单、计算库存覆盖天数、列出替代供应商:

```python
# —— 供应链对象网络(对象 + 链接)——
orders = [
    {"id": "CO-1001", "part": "PART-884", "due": 3,  "revenue": 80000,  "priority": "high"},
    {"id": "CO-1002", "part": "PART-884", "due": 10, "revenue": 25000,  "priority": "normal"},
    {"id": "CO-1003", "part": "PART-512", "due": 5,  "revenue": 40000,  "priority": "normal"},
]
inventory = {"PART-884": {"qty": 2000, "daily_demand": 500}}   # 库存 2000,日耗 500
alternatives = {"PART-884": [("SUP-114", 0.95), ("SUP-019", 0.88)]}  # (供应商, 质量评分)

def find_impacted_orders(part_id: str) -> list:
    """Function:find_impacted_orders —— 找出依赖该零件的客户订单"""
    return [o for o in orders if o["part"] == part_id]

def calculate_coverage(part_id: str) -> float:
    """Function:calculate_inventory_coverage —— 库存可覆盖天数"""
    inv = inventory[part_id]
    return inv["qty"] / inv["daily_demand"]

def rank_alternatives(part_id: str) -> list:
    """Function:rank_alternative_suppliers —— 替代供应商排序"""
    return sorted(alternatives[part_id], key=lambda x: -x[1])

print("受影响订单:", [o["id"] for o in find_impacted_orders("PART-884")])
print(f"库存覆盖: {calculate_coverage('PART-884'):.1f} 天")
print("替代供应商:", rank_alternatives("PART-884"))
```

## 实践 / 应用:供应链走查——数据如何变成受控行动

场景:核心供应商 **SUP-027** 因工厂停产,未来 14 天无法交付关键零部件 **PART-884**。

**传统数据平台的做法**:查供应商表 → 查订单表 → 查库存表 → 做报表 → 让业务自己判断。数据被看见了,但业务行动断在系统外——每一步都可能变成新的 Excel、邮件、会议。

**Foundry 的做法**是把它建成**可操作的对象网络**:

| 业务对象 | 关键属性 | 关键链接 |
| --- | --- | --- |
| Supplier | status、lead_time、quality_score | supplies → Part |
| Part | criticality、approved_alternatives、safety_stock | used_by → Product/ProductionLine |
| PurchaseOrder | delivery_date、quantity、risk_status | orders → Part;from → Supplier |
| InventoryLot | quantity、warehouse、reserved_for | stores → Part |
| ProductionLine | schedule、capacity、downtime_cost | consumes → Part |
| CustomerOrder | due_date、priority、revenue | depends_on → Product/Part |
| Scenario | option、impact、risk、approval_status | changes → Orders/Inventory/Schedule |
| ActionRequest | action_type、risk_level、result | writes_to → ERP/MES/WMS/CRM |

业务问题从模糊的"SUP-027 停产会影响哪些订单?"变成一组可计算、可审批、可写回的问题:哪些 CustomerOrder 依赖 PART-884?库存能覆盖几天?哪些替代供应商已通过认证?切换供应商影响哪些订单与交期?哪些动作是查询、哪些改写生产系统必须审批?

**四个受控组件**:

1. **Function 收集事实与计算影响**:`find_impacted_orders(part_id)`、`calculate_inventory_coverage(part_id)`、`rank_alternative_suppliers(part_id)`、`forecast_revenue_at_risk(order_set)`、`simulate_reallocation(option)`——不是普通脚本,是挂在 Ontology 对象上下文里、可被权限/版本/血缘追踪的业务逻辑;
2. **Scenario 先分支,不直接改系统**:方案 A(等待恢复,成本最低质量最稳但关键订单延期)、方案 B(切到 SUP-114,交付风险下降但成本上升)、方案 C(调整排产优先高价值客户)。每个 Scenario 是一组**对象状态的临时分支**——"Treating Your Business Like Code":改生产系统前,先像代码分支一样建方案、比较影响,再决定是否合并到主线;
3. **Action 受控写回外部系统**:写回 ERP 前至少经过——用户身份/角色校验、对象级权限检查、Action 参数校验、业务规则校验、风险分级、人工审批、写回结果记录。审批通过后触发 `switch_supplier`(ERP)、`reserve_inventory`(WMS)、`adjust_production_plan`(MES)、`create_quality_task`(QMS)、`notify_customer_owner`(CRM);
4. **Decision Lineage 解释为什么这样做**:为什么判定 PART-884 有风险(供应商状态/订单/库存覆盖/生产计划)?为什么没等原供应商恢复(Scenario A 的延期影响/收入风险/客户优先级)?为什么选 SUP-114(评分/认证/交期/价格)?谁批准的(采购/质量/运营审批记录)?写回了哪些系统(ERP/WMS/MES/QMS/CRM 动作结果)?后续效果如何(是否按期交付/超成本/质量问题)?

!!! tip "控制顺序(Foundry 视角)"
    ```
    对象定位 + 影响计算(Function)
      → 生成 Scenario(分支试错)
      → 审批(用户/权限/规则/风险)
      → Action 写回(受控)
      → Decision Lineage(复盘)
    ```

## 总结

- **5 步流程**:安全接入(Data Connection agent,治理从入口开始)→ 管线转换(Pipeline Builder + Code Repositories,Spark/Flink)→ 质量与血缘(Treating Data like Code)→ Ontology 建模(行变对象/列变属性/关系变链接)→ 应用与行动(Object Views/Explorer/Quiver/Workshop/Slate);
- **数据管线不是单纯 ETL**:从接入开始就绑定安全、权限、血缘和治理;
- **Ontology 是数据到业务的翻译层**:模型和动作挂到对象上;对象必须进入应用和行动,否则只是更复杂的数据目录;
- **供应链走查的启示**:Function 计算影响、Scenario 承载试错、Action 负责受控写回、Decision Lineage 保证未来能解释——**缺少任何一层,企业 AI 就会退化成"会建议但不能安全行动"**。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/Stw8OUq5DNznvw-mq7x3Dw;Palantir 官方文档(Data Connection / Pipeline Builder / Code Repositories / Ontology / Object Backend / Object Explorer / Quiver / Slate / Action types)
- 站内系列:[操作型本体论(理论)](palantir-operational-ontology.md)、[OAG 企业 Agent](palantir-oag-agent.md)、[构建案例与边界](palantir-cases-and-reflection.md)、[Ontology as Code](ontology-as-code.md)、[企业 Agent 工程化(三):权限、集成与可观测性](enterprise-agent-permission-integration-observability.md)(Action 写回与权限呼应)
