# 原始资料:别把RAG当架构:Ontology(本体)才是Agent的业务世界

> 来源:微信公众号(本体论/案例分析系列);抓取日期:2026-08-09
> 状态:已提炼整合进 06-enterprise/ontology-agent-adoption/ 的 Palantir 操作型本体论系列文章

---

如果一个企业 AI 项目已经做过 RAG，大概率会遇到一个很尴尬的问题。
一开始，效果看起来不错。
员工问制度，能答。
售后团队问知识库，能答。
销售问产品资料，能答。
但只要业务方继续往前推一步，问题就变了。

他不再问“这份资料里写了什么”，而是问：
业务方真正想问的
RAG 很容易卡住的地方
这个客户该不该升级处理
客户等级、合同、历史投诉、SLA、当前队列不是一段文本
这台设备是不是要提前保养
设备状态、遥测、工单、备件库存、经销商能力要放在一起判断
这张订单能不能改交期
订单、库存、产能、物流、客户优先级和审批规则互相牵连
这份合同能不能自动进入下一步
合同状态、风险项、授权人、例外条款和审批动作都要受控

这时候你会发现，RAG 能帮模型找到资料，但它没有天然告诉模型：
RAG 不天然知道什么
企业 Agent 为什么需要
谁是客户，客户当前处于什么状态
Agent 要按客户等级和历史行为判断
设备、工单、备件、经销商之间是什么关系
Agent 要判断原因、责任和下一步动作
哪个动作可以自动做，哪个动作必须人工确认
Agent 一旦写回系统，就有操作风险
这个用户能不能看到这些数据、调用这个工具
Agent 不能绕过企业权限体系
这次判断以后，状态应该如何变化
Agent 不是回答器，而是流程参与者

所以这篇文章先把一句话说清楚：
RAG 是 Agent 的资料检索层。Ontology 才是 Agent 的业务世界。

RAG 解决的是：模型应该看到哪些上下文。
Ontology 解决的是：企业里到底有哪些对象、关系、状态、动作、权限和业务逻辑。
如果没有这个业务世界，Agent 再会说话，也只能在文档片段里猜。
一、先别把 Ontology 翻译成“知识图谱”

先把这个词说清楚。
Ontology，中文常见翻译是 本体，也有人译成 本体论。
在哲学里，本体论讨论的是“世界上到底存在什么”。换句话说，它关心的不是某个句子怎么表达，而是一个世界里有哪些东西、这些东西是什么、彼此之间是什么关系。
到了 AI 和知识工程里，这个词变得更工程化。
Tom Gruber 对 ontology 有一个经典定义：它是对某个概念化的显式规格。用工程语言说，就是把一个领域里默认存在的对象、概念、关系和约束，用机器和人都能对齐的方式写清楚。
W3C 的 OWL，也就是 Web Ontology Language，做的也是类似的事：用来表示事物、事物集合，以及它们之间的关系。
所以，放到企业 Agent 里，Ontology 不应该被理解成一个玄学词。
它更像是 Agent 的 业务世界说明书。
词
在企业 Agent 里应该怎么理解
本体 / Ontology
这个业务世界里有哪些对象、概念、关系、状态和约束
本体论
先回答“这个世界由什么构成”，再谈 Agent 如何推理和行动
知识库
存放文档、制度、案例和资料
知识图谱
用图结构表达实体和关系，常用于检索和推理
企业 Ontology
业务对象、关系、状态、动作、权限、逻辑和审计共同组成的运行模型

这也是为什么最近国内外做 Agent、GraphRAG、Agent Memory、企业知识层的人，都重新开始讨论 ontology。
原因并不复杂：
Agent 项目遇到的问题
为什么会把 Ontology 推到前台
RAG 只拿到文档片段
Agent 需要知道片段背后的对象和关系
多跳关系很难靠向量相似解决
需要显式的对象、关系和约束
Agent 要执行动作
必须知道哪些状态可以变、哪些动作可调用
企业权限很复杂
权限不能只靠 prompt 约束
记忆和上下文会过期
需要记录事实来源、时间和版本

所以这几年你会看到很多相关方向变热：GraphRAG、Knowledge Graph、Agent Memory、Ontology-driven RAG、AI agent world model。
它们背后都在回答同一个问题：
Agent 不能只读文本，它要有一个可查询、可约束、可更新的业务世界。

这里就回到了本体论最有价值的地方。
本体论听起来像哲学课，但它对架构师真正有用的地方很朴素：
它不是先问“系统怎么实现”，而是先问“这个系统承认哪些东西存在”。
如果一个 Agent 的世界里只有文档，那它最多只能围绕文档说话。
如果一个 Agent 的世界里有客户、设备、合同、订单、工单、库存、审批、状态和动作，它才有机会进入业务流程。
哲学问题到了工程现场，会变成下面这张表：
本体论问题
Agent 工程问题
什么东西存在
系统里有哪些业务对象
这些东西是什么
对象有哪些属性、状态和身份
它们如何彼此关联
客户、设备、合同、工单、库存之间是什么关系
什么变化是合法的
哪些状态转换允许发生
谁能改变这些东西
哪些用户、系统和 Agent 可以触发动作
如何知道变化发生过
事件、审计、trace 和版本如何记录

所以不要把本体论理解成“讲概念”。
放到企业 Agent 里，它关心的是一件非常现实的事：
业务世界怎样被机器看见、被模型理解、被系统约束、被人类回放。

这也是为什么国内外这条线都在升温，只是叫法不同。
国内很多时候不会直接说 Ontology，而是说 知识增强、知识图谱、企业知识库、Agent 平台、数据智能。
百度是这条路线里很典型的例子。
早在 ERNIE 3.0 的论文里，百度就把方向写成 Large-scale Knowledge Enhanced Pre-training。论文里明确说，传统大模型主要从 plain text 训练，没有显式引入 linguistic knowledge 和 world knowledge；ERNIE 3.0 则在 plain text 之外，引入 large-scale knowledge graph 做预训练。
这不是 Palantir 意义上的企业 Ontology。
但它说明百度长期在押一个判断：模型不能只吃文本，知识结构也要进入 AI 系统。
到现在的百度千帆，它的官方文档已经把平台定位成“以 Agent 为核心”的企业级服务，围绕 Agent 引擎、工具及 MCP、模型服务、企业级服务来做应用落地；Agent 引擎里也出现了自主规划、工作流、多智能体协同这些模式。再看 EICopilot 这类研究，已经把 LLM-driven agents 和大规模企业知识图谱放在一起，用自然语言查询、生成 Gremlin、探索企业关系。
这条国内路线，大致是这样走的：
国内常见叫法
背后在解决什么
知识增强
不让模型只依赖纯文本语料
知识图谱
把实体、关系和多跳查询显式化
企业知识库 / RAG
让模型接入企业私有知识
Agent 平台 / 工作流
让模型进入任务编排和工具调用
企业知识层
让 Agent 能围绕对象、关系、权限和动作工作

国外更典型的代表是 Palantir。
Palantir 的说法更直接：它把 Ontology 放在 Foundry 和 AIP 的核心位置，不只把它当成知识图谱，而是当成企业的 operational layer。
AIP 的官方文档也很明确：AIP Logic、AIP Chatbot Studio、AIP Evals 这些工具，是在 Ontology 和开发工具链之上构建 production-ready 的 AI workflows、agents 和 functions。AIP 架构文档里还把 Ontology 描述成把 data、logic、action、security 统一到企业决策表示里的系统，并且强调它要建模 operational processes 里的 nouns 和 verbs。
这个区别很关键。
路线
常见表达
对 Agent 的意义
百度 / 国内知识增强路线
知识增强、知识图谱、千帆 Agent、企业知识库
让模型和 Agent 不只依赖文本，而能接入领域知识、关系结构和企业应用能力
Palantir / 海外操作层路线
Ontology、AIP、operational layer
把数据、逻辑、动作、安全、评测放在同一个业务世界里，让 Agent 在其中运行
开源框架路线
GraphRAG、Agent Memory、Temporal Graph
让 RAG 从相似文本检索，走向结构化关系、时间变化和来源追踪

这三条线不完全相同。
不能把百度的知识增强，直接等同于 Palantir 的 Ontology。
也不能把开源 GraphRAG，直接等同于企业操作层。
但它们指向同一个趋势：
企业 Agent 的竞争，不会只停在模型层，而会进入业务世界层。

很多人一听 Ontology，会马上想到知识图谱。
这个理解不算错，但放到企业 Agent 里，太窄。
如果只是把文档里的实体和关系抽出来，画成一张图，那更接近 Knowledge Graph 或 GraphRAG。它对检索有帮助，但还没有进入企业 Agent 的核心。
企业 Agent 需要的 Ontology，至少不是一张“概念关系图”。
它更像一套业务操作模型。
层级
普通知识图谱更关注
企业 Ontology 必须关注
对象
实体和关系
业务对象、唯一 ID、属性、生命周期
关系
A 与 B 有什么关联
关系是否实时、是否有方向、是否有权限边界
状态
通常不是重点
订单、工单、设备、合同当前处于哪个状态
动作
很少覆盖
谁可以触发什么动作，动作会写回哪里
逻辑
可能只是文本描述
规则、函数、模型、工作流如何作用在对象上
安全
很少是图谱核心
用户、角色、项目、Agent 的权限如何继承和约束

Palantir 的官方文档里，对 Ontology 的描述很直接。
它不是把 Ontology 说成“知识图谱”，而是说它是组织的 operational layer。它把企业已经接入的平台数据、虚拟表、模型等数字资产，连接到现实世界里的对象，比如工厂、设备、产品、客户订单、金融交易。
更关键的是，Palantir 把 Ontology 拆成两类元素：
Palantir 的拆法
对企业 Agent 的含义
Semantic elements：objects、properties、links
Agent 理解业务对象、属性和关系
Kinetic elements：actions、functions、dynamic security
Agent 能在权限和逻辑约束下推动动作

这组词很重要。
语义层只是 nouns，也就是名词：客户、订单、设备、合同、工单、库存。
但企业 Agent 真正进入生产，必须看到 verbs，也就是动词：创建工单、升级优先级、调整交期、冻结合同、提交审批、触发补货。
只有名词，没有动词，Agent 只能解释业务。
名词和动词都在受控模型里，Agent 才可能参与业务。
二、RAG 为什么撑不起企业级 Agent

RAG 很有价值。
这点不要误解。
没有 RAG，企业 AI 很难接触私有知识、产品文档、制度、历史案例、交付资料和行业语料。RAG 是很多企业 AI 的第一块地基。
但 RAG 的核心动作仍然是检索。
它通常回答的是：
问题
RAG 的工作
用户问了什么
把问题改写成检索 query
哪些资料相关
找出相似 chunk、文档、表格或页面
模型应该看到什么
把检索结果塞进上下文
回答是否有依据
引用文档片段或来源

这对知识问答足够。
但企业 Agent 的问题不是“能不能找到资料”。
它的问题是：
企业 Agent 的问题
只做 RAG 的缺口
这个对象当前是什么状态
chunk 不等于对象状态
这个对象和哪些对象相关
向量相似不等于业务关系
这次动作会改变什么
检索层不负责状态变更
谁有权触发这个动作
文档引用不等于权限判断
动作失败后怎么回滚
RAG 没有运行时语义
错误样本如何进入下一轮迭代
RAG 不自动形成业务评测闭环

这就是很多企业 RAG 项目从 Demo 到生产时变形的原因。
Demo 阶段，用户问一句，模型答一句。只要回答像样，就觉得可以上线。
生产阶段，用户会要求它接系统、读状态、做判断、推流程、留记录。
这时，RAG 不会消失，但它会变成一个局部能力。
它负责知识和证据。
Ontology 负责业务世界。
Harness 负责运行控制。
Evals 和 Observability 负责验收和改进。
把这些东西都塞给 RAG，是架构上偷懒。
三、一个 Agent 如果没有对象层，会发生什么

沿用上一篇的机械制造售后场景。
客户可能说：
我们希望售后工单处理更智能一点，最好能根据设备状态和历史维修记录，自动给出处理建议。

如果只按 RAG 做，团队很容易做成这样：
模块
做法
知识库
把维修手册、FAQ、历史案例切 chunk
检索
用户输入故障描述，检索相似案例
生成
模型总结可能原因和处理建议
引用
附上几个文档来源

这当然有用。
但它还不是企业 Agent。
因为真正的售后问题不是一段故障描述，而是一组业务对象正在变化。
对象
Agent 需要知道什么
Machine / 设备
型号、序列号、当前状态、遥测指标、上次保养时间
Dealer / 经销商
服务区域、技师能力、当前工单负载、库存可用性
WorkOrder / 工单
优先级、SLA、故障类型、当前状态、责任人
ServiceContract / 服务合同
保修范围、服务等级、例外条款、响应时限
PartInventory / 备件库存
当前库存、预计到货、替代件、仓库位置
Technician / 技师
资质、排班、地理位置、历史处理表现
Customer / 客户
客户等级、历史投诉、停机影响、业务优先级

RAG 可以告诉模型“这类故障一般怎么处理”。
Ontology 要告诉 Agent：
判断项
业务含义
这台设备是不是同一个型号
避免把相似但不适用的维修案例拿来套
当前故障是否还在保修范围
决定费用、审批和客户沟通方式
备件是否可用
决定建议是远程指导、派工还是延迟
哪个经销商能接
决定工单流向，不只是回答内容
是否触发 SLA 风险
决定是否升级主管或主动通知客户
哪个动作允许自动执行
决定 Agent 是建议、草稿、还是写回系统

这就是 RAG 和 Ontology 的区别。
RAG 帮 Agent 读资料。
Ontology 让 Agent 认对象。
RAG 给上下文。
Ontology 给业务结构。
RAG 让回答更有依据。
Ontology 让动作有边界。
四、Ontology 不是把所有数据做成一张大图

这里也要避免另一个误区。
不是一说 Ontology，就要把全公司数据建成一张宏大的知识图谱。
那会把项目拖死。
企业 Agent 的 Ontology，应该从一个具体业务流开始。
比如售后工单，不需要一开始建完整企业模型。可以先建一条窄链路：
最小对象层
先覆盖什么
Equipment
设备身份、状态、关键遥测
WorkOrder
工单生命周期和优先级
Dealer
服务能力和区域
Part
备件库存和替代件
Contract
服务等级和保修范围
Action
建议派工、升级、请求备件、生成客户通知
Permission
哪些动作自动、哪些动作必须人工确认

这已经足够支撑一个有限但可运行的 Agent。
架构师真正要问的不是“我们有没有企业级大 Ontology”。
而是：
问题
为什么重要
这个 Agent 操作哪些对象
决定数据模型和接口
这些对象的唯一 ID 是什么
决定跨系统能否对齐
对象有哪些状态
决定 Agent 能否判断生命周期
状态之间如何转换
决定动作是否合法
哪些关系是实时的
决定上下文是否可信
哪些动作会写回系统
决定风险等级和 Harness 设计
谁能看、谁能做、谁能批准
决定权限和审计

如果这些问题没回答，所谓 Agent 其实只是在知识库外面包了一层对话。
它可以回答。
但它不能可靠地做事。
五、GraphRAG 是进步，但它不等于企业 Ontology

现在开源生态里，GraphRAG 很热。
这不是偶然。
因为大家已经发现，只靠向量相似度，很难处理复杂关系。
Microsoft 的 GraphRAG 项目，把自己描述成一套从非结构化文本中抽取有意义结构化数据的 pipeline 和 transformation suite，用 knowledge graph memory structures 增强 LLM 输出。它的 README 也提醒，GraphRAG indexing 可能很贵，要从小开始，还需要 prompt tuning。
Neo4j 的 GraphRAG Python 包，则把图检索、向量检索、图遍历、Text2Cypher 等能力放到 RAG 应用里。
LangChain 和 Neo4j 的文章也说得很清楚：图擅长表达异构、互联的信息；向量数据库擅长处理非结构化文本。更好的做法不是二选一，而是把结构化图数据和向量检索结合起来。
这些趋势说明了一件事：
RAG 正在从“找相似文本”走向“找结构化上下文”。

但 GraphRAG 仍然不是企业 Ontology。
二者的区别可以这样看：
维度
GraphRAG
企业 Ontology
主要目标
提升检索和回答质量
建立可操作的业务世界
主要对象
文档中的实体、关系、社区、子图
企业业务对象、状态、动作、权限、逻辑
典型输出
更好的上下文、更好的答案
应用、工作流、Agent 动作、审计和反馈
是否负责写回
通常不是核心
必须定义动作和状态变更
是否承载权限
可以辅助过滤
必须与企业权限治理绑定
是否承载业务生命周期
不一定
必须覆盖对象生命周期和动作合法性

GraphRAG 可以成为 Ontology 的一部分，或者成为 Ontology 之外的检索增强层。
但不要把它们混成一个词。
GraphRAG 让 Agent 更会找关系。
Ontology 让 Agent 处在一个可治理的业务世界里。

六、Agent 需要的不是更多 chunk，而是五类业务结构

企业 Agent 的上下文，不能只有文档片段。
至少要有五类结构。
结构
例子
没有它会怎样
Object / 对象
客户、订单、设备、工单、合同、备件
Agent 不知道自己在处理什么
Relationship / 关系
设备属于客户，工单关联设备，合同约束服务等级
Agent 只能看相似文本，不能跨对象推理
State / 状态
待处理、已派工、等待备件、已关闭、已升级
Agent 不知道动作是否合法
Action / 动作
创建工单、升级、派工、发通知、冻结、审批
Agent 只能建议，不能进入流程
Policy / 策略
谁能看，谁能改，谁能批准，哪些情况必须人工确认
Agent 可能越权或误操作

把这五类结构写出来，Agent 的架构才会清楚。
否则你会在实现阶段不断临时补洞。
生产问题
没有 Ontology 时的临时补洞
模型拿错客户
在 prompt 里写“请注意客户信息”
工单状态错了
加一个 if 判断
权限不清
先让 Agent 不写回
动作风险太高
每一步都人工确认
回答依据不稳定
再加一些 chunk
关系查不到
让模型自己推

这些补丁短期能跑，长期会变成维护灾难。
因为业务结构没有被工程化，只是被 prompt、代码分支和人工兜底散落在系统里。
Ontology 的价值，是把这些结构显式化。
让 Agent 不靠猜。
让工程师不靠补丁。
让业务方知道系统到底按什么世界模型运行。

七、时间和来源，也是 Ontology 的一部分

还有一个问题，在企业里很容易被低估。
对象关系不是永远不变的。
客户等级会变。
合同条款会变。
设备状态会变。
经销商服务能力会变。
库存会变。
组织权限会变。
如果 Agent 只拿到一段旧文档，它很难判断“现在是否仍然成立”。
这也是为什么一些开源 Agent memory 项目开始往 temporal graph 方向走。
Graphiti 的 README 里把自己描述成给 AI agents 用的 temporal context graph engine。它强调 facts change over time，保留 provenance，支持 prescribed and learned ontology，还能把用户交互、结构化和非结构化企业数据、外部信息持续整合进一个可查询的 graph。
这对企业 Agent 很关键。
因为 Agent 不是做一次性问答。
Agent 会在持续变化的业务环境里运行。
上下文问题
Agent 为什么会出错
关系过期
设备已经转移给新客户，Agent 仍按旧客户处理
状态过期
工单已经升级，Agent 仍建议一线处理
权限过期
员工调岗后，Agent 仍继承旧权限
来源不清
模型拿到结论，但不知道是谁在何时给出的
版本不清
合同条款更新后，旧解释仍被检索出来

所以企业 Ontology 不只是“对象表”。
它还要回答：
问题
对应能力
这个事实什么时候变成真的
时间有效性
它来自哪个系统或哪次人工输入
来源和 provenance
谁修改过它
审计
它现在是否仍然有效
状态和版本
如果 Agent 基于它做了动作，能不能回放
trace

没有这些，Agent 就会用过期世界做当前决策。
这比回答错一段知识更危险。
八、Ontology 应该怎么从 SDD 里长出来

上一篇讲 SDD。
SDD 不是文档装饰，而是 Agent 的可执行规格。
那 Ontology 怎么接 SDD？
很简单：从 SDD 里抽对象。
比如 SDD 里有一句：
售后主管在工单后台查看高风险设备故障。Agent 读取设备遥测、历史维修、服务合同、备件库存和经销商服务能力，判断是否建议升级工单、请求备件或派发现场服务。高价值客户和合同例外必须人工确认，所有建议、采纳和修改写入审计记录。

这句话不是直接丢给模型。
它应该拆成下面这些东西：
SDD 片段
Ontology 产物
售后主管
User role / permission scope
工单后台
Interface / trigger point
高风险设备故障
WorkOrder + Equipment + RiskSignal
设备遥测
Equipment telemetry property / event stream
历史维修
MaintenanceHistory relation
服务合同
ServiceContract object
备件库存
PartInventory object
经销商服务能力
DealerCapability object
升级工单
EscalateWorkOrder action
请求备件
RequestPart action
派发现场服务
DispatchTechnician action
高价值客户必须人工确认
Policy / human approval gate
写入审计记录
Trace / audit event

这就是 SDD 到 Ontology 的转译。
SDD 负责把业务需求写到可执行。
Ontology 负责把可执行规格变成 Agent 可以读取、判断和调用的对象世界。
如果这一步跳过，后面所有框架都会变得很尴尬。
后续能力
没有 Ontology 时会怎样
RAG
只能找文档，难以稳定绑定业务对象
Tool Calling
工具参数和业务对象对不齐
Workflow
状态流转靠代码硬拼
Permission
权限只能在工具或 prompt 里补
Evals
很难判断 Agent 是否对某个对象做对了动作
Observability
trace 只剩模型输入输出，缺少业务状态

所以，Ontology 不应该等平台建设后期再补。
它应该从第一份 SDD 里长出来。
九、架构师可以用这张表判断：只做 RAG 够不够

不是所有企业 AI 场景都需要完整 Ontology。
如果只是制度问答、文档检索、材料总结，RAG 可能已经足够。
真正的问题是，不要把 RAG 场景包装成 Agent 项目。
可以用下面这张表判断。
场景特征
RAG 可能够用
需要 Ontology
用户目标
查资料、问制度、找案例
判断业务状态、推进流程、触发动作
数据形态
主要是文档和知识库
文档 + ERP/CRM/MES/工单/合同/库存/传感器
业务对象
不需要显式对象
必须识别客户、订单、设备、合同等对象
关系复杂度
单文档或少量上下文
跨对象、多系统、多跳关系
动作风险
不写回系统
会改状态、发通知、创建记录、提交审批
权限要求
简单文档权限
对象级、字段级、动作级、场景级权限
验收方式
回答准确率和引用
任务完成率、动作正确率、人工采纳率、错误回放

如果右侧特征占多数，就不要再纠结“RAG 怎么调得更准”。
先把对象层建起来。
否则你会在错误的层上反复优化。
十、企业第一个 Ontology 不要大，从一个 Agent 场景开始

这篇不是建议企业先搞一个宏大的 Ontology 项目。
相反，第一版应该很小。
从一个 Agent 场景开始，按下面顺序做。
步骤
产物
判断标准
1. 从 SDD 抽对象
Object list
这条业务链里出现哪些对象
2. 定义对象属性
Properties
哪些字段是 Agent 判断必须读的
3. 定义对象关系
Links
哪些关系决定判断或动作
4. 定义状态机
Lifecycle
对象可以处于哪些状态
5. 定义动作
Actions
哪些动作由 Agent 建议、草稿或触发
6. 定义权限
Policy
谁能看、谁能改、谁能批准
7. 定义事件和审计
Trace
每次判断和动作如何回放
8. 定义样本
Eval set
什么案例证明 Agent 做对了

这不是多写文档。
这是在给 Agent 建运行环境。

如果团队已经有数据仓库、主数据、权限系统、流程引擎和业务系统，也不用全部推翻。
Ontology 可以先是一个薄层：
现有系统
Ontology 要做的事
ERP / CRM / MES / FSM
映射核心对象和状态
数据仓库 / Lakehouse
提供对象属性和分析特征
文档库 / 知识库
提供 RAG 证据和解释材料
工作流系统
承接审批、派工、升级等动作
权限系统
约束用户和 Agent 的访问与动作
Observability
记录对象、动作、工具调用和结果

你不一定要一次建成一个大平台。
但必须先有对象层意识。
没有对象层，Agent 架构会一直退回聊天框。
十一、这篇的结论

RAG 是必要的。
但 RAG 不是企业 Agent 的架构终点。
如果一个 Agent 只是回答文档问题，它可以停在 RAG。
如果一个 Agent 要进入业务流程，它必须理解业务对象。
如果一个 Agent 要触发动作，它必须受到状态、权限、策略和审计约束。
所以，企业 AI 的下一层不是“更大的知识库”，而是更清楚的业务世界。
换成架构语言：
层
解决什么
SDD
Agent 要在什么场景里做什么
RAG
Agent 可以读取哪些知识和证据
Ontology
Agent 操作的业务对象、关系、状态、动作和权限是什么
Harness
Agent 如何在运行时受控执行
Evals / Observability
Agent 怎么被验证、回放和持续改进

把 RAG 当全部，企业 AI 会停在知识助手。
把 Ontology 建起来，Agent 才开始拥有业务世界。

下一篇进入 Harness：有了 SDD 和 Ontology，Agent 仍然不能直接放飞。真正上线时，谁来控制上下文、权限、工具、人工确认、失败重试、回滚和日志？这就是 Harness Engineering 要解决的问题。
我们会持续迭代企业 AI 落地应用，沉淀一线项目里的实战经验、踩坑记录和方法论。如果你也在关注企业 AI、Agent 和 Harness Engineering，欢迎持续关注，后面会继续拆具体案例。关注不迷路～
参考资料

• W3C: OWL - Semantic Web Standards
https://www.w3.org/OWL/

• Tom Gruber: Definition of Ontology
https://tomgruber.org/writing/definition-of-ontology.pdf

• Stanford / Protégé: Ontology Development 101
https://protege.stanford.edu/publications/ontology\_development/ontology101-noy-mcguinness.html

• Palantir: Ontology overview
https://www.palantir.com/docs/foundry/ontology/overview/

• Palantir: The Ontology system
https://www.palantir.com/docs/foundry/architecture-center/ontology-system

• Palantir: Solution Design
https://www.palantir.com/docs/foundry/use-case-life-cycle/solution-design

• Palantir: Platform overview
https://www.palantir.com/docs/foundry/platform-overview/overview/

• Palantir: AIP overview
https://www.palantir.com/docs/foundry/aip/overview/

• Palantir: AIP architecture overview
https://www.palantir.com/docs/foundry/architecture-center/aip-architecture/

• Baidu / arXiv: ERNIE 3.0 - Large-scale Knowledge Enhanced Pre-training for Language Understanding and Generation
https://arxiv.org/abs/2107.02137

• 百度智能云：百度千帆·大模型服务及 Agent 开发平台 - 平台简介
https://cloud.baidu.com/doc/qianfan/s/rmh8khvwu

• arXiv: EICopilot - Search and Explore Enterprise Information over Large-scale Knowledge Graphs with LLM-driven Agents
https://arxiv.org/abs/2501.13746

• Microsoft GraphRAG GitHub
https://github.com/microsoft/graphrag

• Neo4j GraphRAG Python GitHub
https://github.com/neo4j/neo4j-graphrag-python

• LangChain: Enhancing RAG-based application accuracy by constructing and leveraging knowledge graphs
https://www.langchain.com/blog/enhancing-rag-based-applications-accuracy-by-constructing-and-leveraging-knowledge-graphs

• LangChain: Self-Reflective RAG with LangGraph
https://www.langchain.com/blog/agentic-rag-with-langgraph

• Graphiti GitHub
https://github.com/getzep/graphiti