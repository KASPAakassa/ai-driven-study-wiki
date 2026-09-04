# 原始资料:Palantir Foundry:5步把数据变对象

> 来源:微信公众号(作者:阿铁)
> 原文链接:https://mp.weixin.qq.com/s/Stw8OUq5DNznvw-mq7x3Dw;参考:Palantir 官方文档(Data Connection、Pipeline Builder、Code Repositories、Ontology、Object Backend、Action types 等)
> 抓取日期:2026-08-09;状态:已整理为正式文章 docs/06-enterprise/ontology-agent-adoption/palantir-foundry-5-steps.md(Palantir 系列第四篇:数据变对象操作手册)

---

Palantir Foundry：5步把数据变对象
Foundry 到底怎么把一堆表、文件、流式数据，变成业务人员能理解、能操作、能写回的对象？
答案可以压缩成 5 步：
安全接入 → 管线转换 → 质量与血缘 → Ontology 建模 → 应用与行动。

图：主线可以压缩成一句话：数据先可信进入平台，再被管线、血缘和 Ontology 转成可操作业务对象。

如果你只记住一个判断：Foundry 的数据工程不是为了多做一张表，而是为了让数据最终进入客户、订单、设备、航班、病床这些业务对象，并支持真实决策。
一、第一步：数据先安全进来
Foundry 接入私有网络数据源，核心组件叫 Data Connection agent。
官方文档把 agent 描述成：
"a downloadable program installed within your organizational network..."

以及：
"functions as a secure intermediary."

换成白话就是：它不是简单从外部把数据“拉走”，而是在客户自己的网络里部署一个受控中介，由 Foundry 管理连接和摄取。
研究底稿里有几个关键事实：
• Foundry 支持 200+ 连接器；

• 支持 agent、REST、JDBC 等多种接入拓扑；

• 支持结构化、非结构化、流式、IoT、地理空间等多模态数据；

• 摄取过程使用受限访问令牌，不是无边界开放。

这一步看似是数据接入，实际已经开始埋下 Foundry 的核心差异：权限、来源、血缘从数据进入平台的第一刻就开始被管理。
二、第二步：转换不是脚本，而是工程体系
很多公司也有数据管线，但常见问题是：脚本散落、版本不清、失败没人知道、上游变了下游全炸。
Foundry 的管线体系分两条线：
场景
组件
特点
可视化/低代码管线
Pipeline Builder
图形化构建，覆盖批处理和流处理
生产级代码管线
Code Repositories
git 化 IDE，支持 Python、Java、SQL

Pipeline Builder 不是简单 no-code。研究核验中特别纠偏：它更准确的说法是 no-code / low-code / pro-code。
批处理和流处理也不是一个东西换个按钮：
类型
底层引擎
行为
Batch 批管线
Spark
对变化数据集做重算
Streaming 流管线
Flink
持续运行，新数据到达即处理

官方对流式管线的描述是：
"run continuously and process new data as it arrives"

更重要的是，Foundry 文档提到流式数据进入 Ontology 的平均时间可以做到 <15 秒。这说明它不是只做离线分析，而是把实时业务变化送进后面的对象世界。
三、第三步：数据质量和血缘不是事后补丁
Foundry 里有两个容易被低估的能力：
• Data Expectations：在管线里声明数据应该满足什么条件；

• Data Health：监控数据健康、告警、影响分析。

这听起来像“数据治理标准配置”，但 Foundry 的重点在于它和血缘、权限、Job Spec、应用对象连在一起。
白皮书里有一句关键表述：
"Treating Data like Code"

意思不是把数据写成代码，而是用软件工程纪律管理数据：
• 版本化；

• 分支；

• 回退；

• 受保护分支；

• 单元测试 / CI 门控；

• 增量计算；

• 完整 provenance。

对于企业 AI 来说，这很关键。
因为当上层 AIP 或模型给出建议时，业务方会追问：
• 这个结果来自哪份数据？

• 数据是否通过质量检查？

• 最近一次管线变更是谁合并的？

• 模型看到的是全量、增量，还是某个受限视图？

没有血缘，AI 建议只是一个黑箱答案；有血缘，它才有机会变成可审计的业务判断。
四、第四步：Ontology 把表变成业务世界
这一步是 Foundry 最容易被误解的地方。
Ontology 不是哲学课，也不是独立数据库。
官方定义非常直接：
"The Palantir Ontology is an operational layer..."

它 sits on top of：
• datasets；

• virtual tables；

• models。

然后把底层资产映射成真实业务世界：
数据层
Ontology 层
行 rows
对象 Objects
列 columns
属性 Properties
关系 relationships
链接 Links

比如：
• 一行订单数据，不再只是 order_id = 10086，而是一个 Order 对象；

• 一列交付日期，不再只是字段，而是 Order 的属性；

• 订单和客户的关联，不再只是 join，而是 Order 到 Customer 的链接；

• 预测延期风险，不再是模型输出表，而是挂在 Order 对象上的业务判断。

官方还把 Ontology 形容为：
"a digital twin of an organization"

这句话有营销味，但它对应的组件事实很具体：Object、Link、Property、Action、Function、Interface。
五、第五步：对象必须能被应用和行动使用
如果 Ontology 只是让对象名字更好听，那价值有限。
Foundry 继续往上提供一组应用工具：
工具
用途
Object Views
可复用对象视图
Object Explorer
搜索、浏览、筛选对象
Quiver
多维分析、图表探索、实时流数据
Workshop
构建面向业务用户的对象应用
Slate
构建运营应用和交互仪表盘

官方文档对这些工具的总结是：
"Users can create reusable Object Views, search for objects of interest in Object Explorer, perform complex analyses in Quiver, build high-quality applications in Workshop."

区别在于：这些应用不是围绕“表”设计，而是围绕“对象”设计。
业务用户看到的不是：
dim_customer
fact_order
inventory_daily_snapshot而是：
客户
订单
物料
工厂
供应商
风险方案
审批动作这就是从数据工程到企业运营的关键跳跃。
六、技术上它背后怎么读写
如果你想稍微深入一点，可以记住 Ontology 对象后端的四个名字：
服务
负责什么
OMS
定义对象、链接、动作等元数据
OSS
负责对象查询读取
Object Databases
存储已索引对象数据
Object Data Funnel
编排写入与索引

可以把它理解成：
读路径：应用 / LLM → OSS → Object Databases
写路径：数据源 / 用户 Action → Object Data Funnel → Object Databases
元数据：OMS 定义对象、链接、动作类型这个技术细节解释了一个问题：
为什么 Foundry 能把实时流、用户编辑、Action 写回和对象视图放在同一个业务语义里？

因为它不是在应用层临时拼对象，而是在平台层有一套对象后端。
图：读路径、写路径和元数据治理都围绕对象数据库展开，这是 Ontology 能承接应用、LLM 和 Action 的技术原因。

七、一个供应链例子
Data Connection、Pipeline、Ontology、Function、Scenario、Action 和 Decision Lineage 串起来。
注意：这不是对某个真实客户战绩的独立证明，而是基于 Foundry 官方能力组合出的供应链场景，用来解释“数据如何变成业务对象，并进一步变成受控行动”。
假设一家制造企业收到预警：核心供应商 SUP-027 因工厂停产，未来 14 天无法交付关键零部件 PART-884。
如果只停留在传统数据平台层，业务团队通常要分别查 ERP、WMS、MES、CRM、质量系统，再靠会议协调采购、库存、排产、客户沟通和审批。问题不是查不到数据，而是数据没有被组织成可操作的业务对象。
图：供应商中断不是单表查询问题，而是 Supplier、Part、Order、Inventory、ProductionLine 等对象之间的业务联动问题。

1. 传统数据平台会怎么做
1. 查供应商表；

2. 查订单表；

3. 查库存表；

4. 做一个报表；

5. 让业务自己判断怎么办。

这套流程的问题是：数据虽然被看见了，但业务行动仍然断在系统外。
采购要去 ERP 改供应商，仓储要去 WMS 预留库存，制造要去 MES 改排产，销售要去 CRM 通知客户，质量团队还要单独建验证任务。每一步都可能变成新的 Excel、新邮件、新会议。
2. Foundry 会先把供应链建成对象网络
在 Foundry / Ontology 视角里，这个问题首先不是“查几张表”，而是把供应链世界建成一组可操作对象：
业务对象
典型属性
关键链接
Supplier（供应商）
status、lead_time、quality_score、region
supplies → Part
Part（零部件）
criticality、approved_alternatives、safety_stock
used_by → Product / ProductionLine
PurchaseOrder（采购订单）
delivery_date、quantity、supplier、risk_status
orders → Part；from → Supplier
InventoryLot（库存批次）
quantity、warehouse、reserved_for
stores → Part
ProductionLine（产线）
schedule、capacity、downtime_cost
consumes → Part
CustomerOrder（客户订单）
customer、revenue、due_date、priority
depends_on → Product / Part
Scenario（方案）
option、impact、risk、approval_status
changes → Orders / Inventory / Schedule
ActionRequest（动作请求）
action_type、caller、risk_level、result
writes_to → ERP / MES / WMS / CRM

有了这些对象，业务问题可以从一句模糊的话：
“SUP-027 停产会影响哪些订单？”

变成一组可计算、可审批、可写回的问题：
1. 哪些 CustomerOrder 依赖 PART-884？

2. 当前 InventoryLot 能覆盖多少天生产？

3. 哪些替代 Supplier 已经通过质量认证？

4. 如果切换供应商，会影响哪些 PurchaseOrder、ProductionLine 和客户交期？

5. 哪些动作只是查询，哪些动作会改写生产系统，必须审批？

3. Function 先收集事实和计算影响
LLM 或业务应用不应该凭空判断，而是调用受治理的 Function：
Function
输入
输出
find_impacted_orders(part_id)PART-884受影响客户订单、金额、交期
calculate_inventory_coverage(part_id)库存批次、生产计划
可覆盖天数、缺口数量
rank_alternative_suppliers(part_id)合格供应商、质量、交期、价格
替代供应商排序
forecast_revenue_at_risk(order_set)订单集合、延期概率
收入风险、客户优先级
simulate_reallocation(option)方案参数
对排产、库存、成本、交付的影响

这一步体现的是：Function 不是普通脚本，而是挂在 Ontology 对象上下文里的业务逻辑。它知道输入输出对应哪些对象，也能被权限、版本和血缘追踪。
4. Scenario 先分支，不直接改系统
系统可以形成三个 Scenario：
Scenario
方案
可能收益
主要风险
A
等待 SUP-027 恢复供货
成本最低，质量最稳定
关键订单延期，客户影响大
B
切换到 SUP-114 替代供应商
交付风险下降
成本上升，质量验证压力增加
C
调整排产，优先保障高价值客户
保住关键客户和收入
普通订单延期，需要销售协调

每个 Scenario 都不是一段文字建议，而是一组对象状态的临时分支：
被改变的对象
示例变化
PurchaseOrder修改供应商、数量、到货日期
InventoryLot预留给高优先级订单
ProductionLine调整排产窗口和工单顺序
CustomerOrder标记延期风险、生成客户沟通任务
QualityTask创建替代供应商首件验证任务

这就是 Foundry 里 “Treating Your Business Like Code” 的含义：改生产系统前，先像代码分支一样建方案、比较影响，再决定是否合并到主线。
5. Action 受控写回外部系统
如果业务负责人选择 Scenario B，Foundry 不能直接把 LLM 的建议写进 ERP。高风险动作至少要经过：
• 用户身份和角色校验；

• 对象级权限检查；

• Action 参数校验；

• 业务规则校验；

• 风险分级；

• 人工审批；

• 写回结果记录。

审批通过后，Actions Framework 才可能触发一组写回：
Action
写回系统
业务效果
switch_supplierERP
把 PART-884 的采购订单切到 SUP-114
reserve_inventoryWMS
把库存批次预留给高优先级客户订单
adjust_production_planMES
调整产线工单顺序和生产窗口
create_quality_taskQMS
创建替代供应商质量验证任务
notify_customer_ownerCRM
生成客户沟通和延期说明任务

这一步说明 Foundry 的 Action 不是“点按钮调用 API”这么简单。它把对象、权限、审批、写回和血缘放在同一条链路里。
6. Decision Lineage 解释为什么这样做
一条合格的 Decision Lineage 至少要能回答：
审计问题
应该追溯到
为什么判定 PART-884 有风险？
供应商状态、采购订单、库存覆盖天数、生产计划
为什么没有等待原供应商恢复？
Scenario A 的延期影响、收入风险、客户优先级
为什么选择 SUP-114？
替代供应商评分、质量认证、交期、价格
谁批准了切换？
采购负责人、质量负责人、运营负责人审批记录
写回了哪些系统？
ERP、WMS、MES、QMS、CRM 的动作结果
后续效果如何？
是否按期交付、是否超成本、是否出现质量问题

图：流程图的重点是控制顺序——先对象定位和影响计算，再生成 Scenario，审批后才由 Action 写回，最后用 Decision Lineage 复盘。

7. 这个例子真正想说明什么
如果压缩成一张对照表，差异会很清楚：
步骤
Foundry 视角
数据接入
接入 ERP、WMS、MES、供应商系统
管线转换
形成订单、库存、供应商、产线等可信数据集
Ontology
映射成 Order、Part、Supplier、Factory 对象
Function
计算延期风险、收入影响、替代供应商评分
Scenario
模拟切换供应商、调整排产、优先大客户
Action
审批后写回采购、排产、客户通知系统

这就是“数据变对象”的意义：不是为了漂亮建模，而是为了让业务能围绕对象做决策和行动。
Ontology 让供应链事件变成对象网络，Function 计算影响，Scenario 承载试错，Action 负责受控写回，Decision Lineage 保证未来能解释。

如果缺少其中任何一层，企业 AI 或数据平台就很容易退化成“会总结、会建议，但不能安全行动”。
总结
1. Foundry 的数据管线不是单纯 ETL，从接入开始就绑定安全、权限、血缘和治理。

2. Pipeline Builder + Code Repositories 让轻量构建和生产级代码管线并存，底层覆盖 Spark、Flink、Iceberg 等开放技术。

3. Ontology 是数据到业务的翻译层：行变对象、列变属性、关系变链接，模型和动作挂到对象上。

4. 对象必须进入应用和行动，否则 Ontology 只是更复杂的数据目录。

你所在公司的数据现在更像“表”，还是已经变成了业务能操作的“对象”？
参考与来源
Palantir 官方文档：Data Connection、Pipeline Builder、Code Repositories、Ontology、Object Backend、Object Explorer、Quiver、Slate、Action types。