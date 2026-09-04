# 原始资料:Palantir本体论③:技术架构

> 来源:微信公众号(本体论/案例分析系列);抓取日期:2026-08-09
> 状态:已提炼整合进 06-enterprise/ontology-agent-adoption/ 的 Palantir 操作型本体论系列文章

---

本系列共五篇，这是第三篇。 上一篇我们理解了四维集成模型和读写回路的理论框架。本篇深入工程实现——五大构建块如何定义类型系统，五个微服务如何支撑读写回路，以及从建模到部署的完整方法论。

引言：理论落地的工程挑战
理论再漂亮，不落地就是空中楼阁。

四维集成模型说要把"数据、逻辑、操作、安全"统一在一个架构里。但怎么统一？用什么数据结构？怎么保证事务一致性？怎么让数十万对象的高并发查询不卡顿？

Palantir的答案是两套工程体系：一套类型系统（五大构建块）定义"Ontology里有什么"，一套微服务架构（五个核心服务）定义"Ontology怎么跑"。
一、五大构建块：类型系统的骨架
Palantir Ontology的类型系统由五个核心构建块组成。如果你熟悉面向对象编程，会发现很多概念可以类比——但每个都有关键的差异。

1. Object Types（对象类型）
Object Type是真实世界实体或事件的Schema定义——如员工、货运、航班、事件。一个Object实例是特定的一名员工或一次航班。用数据库来类比：Object Type类似于表Schema，Object实例类似于行，Object Set类似于过滤后的行集合。

Object Type的定义包括：
• Properties：属性定义，包括基础类型、格式化、条件格式、编辑控制
• Structs：结构化属性组合
• Shared Properties：跨Object Type共享的属性定义
• Metadata：类型类、渲染提示、状态标记
• Object Type Groups：对象类型分组

关键点：Object是有身份的。数据仓库里的一行记录没有身份，只是一个数据点；而Ontology里的一个Object有唯一标识、有类型、有关系、可被操作。这个区别看似微妙，却是整个操作型本体论的基石。

2. Link Types（链接类型）
Link Type是两个Object Type之间关系的Schema定义，Link是其单实例，类比于两个数据集之间的JOIN。Link Type定义包括基数（ONE/MANY）和方向性。
和图数据库的边相比，Palantir的Link Type同样是类型化的——有Schema、有权限、受治理。这不是一个随意的指针，而是一个有类型约束的关系。

3. Action Types（操作类型）
这是Palantir最核心的创新之一。
Action Type是用户可一次执行的一组变更定义。它包括：
• 参数：默认值、过滤下拉框、安全覆盖、性能配置
• 提交条件：操作生效的前置校验
• 副作用：通知、Webhook调用
• 函数支持的操作：批量执行
• 撤销/回退：操作的可逆性
• 监控与日志：操作指标和审计

传统应用代码中，"修改订单状态"可能就是一个函数调用，没有Schema、没有审计、没有前置校验。而Action Type将操作定义为类型化的、受治理的事务。每个操作都有明确的Schema（输入什么参数）、权限（谁能执行）和审计记录（谁在什么时候执行了什么）。

4. Functions（函数）
Functions是在Foundry治理执行环境中针对Ontology对象运行的服务端代码。它们可以读取属性、遍历链接、进行编辑。支持TypeScript（v1/v2）和Python，具有版本控制、发布、监控、遥测和权限管理。

Functions的类型包括：
• 查询函数（通过API网关）
• 编辑函数（Ontology编辑）
• 流式函数
• 模型集成函数（LLM接口）
• 通知函数和API调用函数

把逻辑放在Functions而非应用代码中，意味着同一个业务逻辑可以被多个应用、多个Agent复用，而更新只需发布新版本——这就是上一篇文章说的"逻辑作为Ontology的一等公民"。

5. Interfaces（接口）
Interface是"描述Object Type形状及其能力的Ontology类型"。它提供Object Type多态性，使具有共同形状的不同Object Type可以被一致地建模和交互。

概念类似于面向对象编程中的Interface或Rust的Trait——定义一组能力契约，任何实现该Interface的Object Type都必须满足。

Interface的理论意义在于将类型多态性引入本体论。 传统本体论的类层次（OWL的subClassOf）是单继承的包含关系，而Interface允许多个独立的"能力"组合，更接近"组合优于继承"的现代类型系统设计理念。

比如，"航班"和"货运"是不同的Object Type，但都可以实现"可调度的"Interface，这样调度优化器就可以统一处理它们，而不需要知道具体是哪个类型。
二、后端微服务架构：读写回路的物理实现
类型系统定义了"有什么"，微服务架构定义了"怎么跑"。
Palantir将Ontology后端描述为"微服务架构，其中多个服务共同构成Ontology后端"。五个核心服务各司其职：

服务一：Ontology Metadata Service（OMS）
OMS定义本体中存在哪些实体：Object Types、Link Types、Action Types和结构元数据。它是模型结构的真相源（source of truth）。
所有关于"有什么类型"的问题，都由OMS回答。Object Type的定义变了？OMS知道。新增了Action Type？OMS记录了。

服务二：Object Databases（对象数据库）
存储索引后的对象数据，优化用于快速检索。存在两代存储架构：
• Object Storage V1：编辑后的对象状态存储在writeback dataset中。Writeback dataset记录用户通过Action提交的编辑，与源数据合并后形成当前对象状态。
• Object Storage V2：以可选的物化数据集替代writeback dataset，用于下游消费。编辑通过Actions应用并索引到Ontology后端。
V1到V2的演进，核心是改善了线性扩展性——V1的writeback dataset在大规模场景下会成为瓶颈。

服务三：Object Set Service（OSS）
OSS负责服务读取。当应用搜索、过滤、聚合或加载对象时，它们与OSS通信。OSS是应用层与对象数据之间的查询接口层。
你可以把OSS理解为一个专门为Object Set优化的查询引擎——不是通用SQL，而是面向类型化对象的查询。

服务四：Object Data Funnel
Funnel编排写入。它从Foundry数据源和Actions Service捕获的用户编辑中读取数据，然后将所有内容索引到Object Databases中。Funnel保持索引数据与底层源变化的同步。
当源数据更新时，Funnel负责将变更传播到索引层。这是保证Ontology"实时性"的关键组件。

服务五：Actions Service
Actions Service应用写入。当用户或Agent提交操作时，此服务应用编辑、触发副作用并提交变更。
一个Action的完整执行链路是：应用/Agent提交Action → Actions Service校验提交条件 → 应用变更到Object Databases → 触发副作用（通知/Webhook） → 记录审计日志。整个过程是事务性的。
三、索引与物化策略：一个关键的工程权衡
Palantir Ontology的一个关键架构决策是采用重度物化策略：源数据不是按需联邦查询，而是被索引到Object Databases中。实时管道和Change Data Capture（CDC）维持同步。

这个策略的工程权衡是：
优势：
• 查询性能高（无需运行时JOIN）
• 支持实时订阅
• 为人类+AI混合团队提供一致的物化视图
代价：
• 存储成本高（数据被复制和索引）
• 写入延迟（索引需要时间）
• 架构复杂度高

这是一个经典的"空间换时间"决策。联邦查询省存储但查询慢，重度物化费存储但查询快。Palantir选择了后者，因为在操作型场景中，查询延迟的代价远高于存储成本——你不会希望飞行员在查询航班状态时等上三秒。
四、可操作方法论：从建模到部署
有了类型系统和微服务架构，具体怎么干活？Palantir提供了一套完整的方法论。
4.1 Ontology建模方法论
建模原则：
1. 实体驱动而非表驱动。 Object Type的设计从业务实体出发，而非从源数据表结构出发。一个Employee Object Type可能整合来自HR系统、payroll系统和门禁系统的数据。
1. 语义与动力学共设计。 在定义Object Type时同步考虑其Action Types——实体不仅"是什么"，还要"能做什么"。Employee可以被Assign（分配角色）、Transfer（调转）、Promote（晋升）。
1. Interface优先的组合设计。 优先通过Interface定义共享能力（如"可追踪的"、"可审批的"），而非通过深层继承层次。
1. 属性粒度的安全设计。 在Property级别定义安全策略，而非仅在Object Type级别。某些属性（如薪资）可能需要比Object Type整体更严格的访问控制。

建模流程：
领域分析 → 数据源映射 → Object Type定义 → Link Type定义 → Action Type定义 → Function定义 → Interface定义 → 权限配置 → 工具绑定

4.2 分支与提案审查（Branching & Proposals）
这是Palantir方法论中最具创新性的部分之一——它把软件工程中的版本控制和同行评审直接引入数据建模。

Global Branching：从分支选择器创建分支，分支内的变更不影响main分支。满意后创建Proposal进行审查并合并到main。

Ontology Proposals：全局分支创建时自动生成Ontology Proposal，提供四个审查标签页：
1. Proposal Overview：提案概览
2. Preview Status：预览状态
3. Review Changes：变更审查（逐项对比）
4. Changelog：变更日志

这一机制使Ontology的演化受控于同行评审流程——任何对类型系统的变更（新增Object Type、修改Action Type、调整Link Type）都必须经过审查和批准，类似于代码的Pull Request。

传统本体论的版本控制通常仅限于文件级（如OWL文件的Git版本），缺乏语义级别的变更审查。Palantir的Proposal机制在语义层面实现了变更治理——审查者可以看到"新增了哪些Object Type"、"哪些Action Type的参数被修改"，而非仅看到文件diff。

4.3 权限与安全治理
Project权限模型：Ontology权限基于Project模型。要查看Object Type需要View权限；要查看具体Object需要Object Type View权限加数据源访问权限。

Markings（安全标记）：提供额外的访问控制层。用户必须是所有已应用Marking的成员才能访问资源——这是合取（boolean AND）逻辑。关键设计：Owner角色也不能绕过Marking要求，确保安全策略的不可绕过性。

Classification-based Access Controls（CBAC）：通过分类标记限制访问。与普通Markings的区别在于支持析取组件（OR逻辑）——用户只需满足任一分类标记即可访问。CBAC可以与非分类标记的合取组件组合使用，形成AND+OR混合逻辑。

这一安全模型的理论意义在于：它将多级安全（Multi-Level Security, MLS）模型引入本体论。传统本体论没有原生的安全标记概念，而Palantir的Markings + CBAC组合实现了Bell-LaPadula模型的变体——不同安全级别的信息可以被不同权限的用户访问，且控制在本体层面而非存储层面实现。

AI Agent的安全范围：Agent不能超越其代理人类的权限。不同操作可能有不同的权限要求，底层LLM调用可能有独立的安全范围。

4.4 OSDK开发实践
Ontology SDK（OSDK）允许从开发环境直接访问Ontology全部能力。支持TypeScript、Python、Java和OpenAPI Spec。

OSDK 2.0的关键改进是性能与可用性：1.x与整个Ontology紧耦耦合，2.0线性扩展于Ontology的形状和元数据而非实际Ontology大小。

开发流程：在Developer Console中配置Ontology子集 → 生成强类型SDK → 在应用中引入SDK → 通过OAuth认证连接Foundry后端 → 应用通过SDK查询对象、执行操作、调用函数。

OSDK的核心价值在于：将Ontology的类型系统延伸到应用代码中。开发者操作的不是原始JSON或SQL结果，而是强类型的Object实例和Action方法——类型错误在编译时而非运行时被发现。

4.5 South/North Ontology Team协作模型
CodeStrap Operating Model提出了Palantir Foundry的团队协作模型：
• South Ontology Team：负责数据集成与建模。发布ERD图作为数据契约，定义数据源到Object Type的映射规则。
• North Ontology Team：负责应用开发与价值实现。基于South团队提供的Object Types和Action Types构建Workshop应用和OSDK服务。

关键区别在于：两个团队通过Ontology类型系统而非API契约协作。South团队对Object Type的变更通过Proposal机制通知North团队，类型系统的强约束确保变更的影响可追溯。
本篇小结
把本篇的内容串联起来，Palantir的工程实现可以概括为三层：
• 类型系统层（五大构建块）：定义Ontology的结构——有什么对象、什么关系、什么操作、什么逻辑、什么接口。
• 微服务层（五个核心服务）：实现Ontology的运行——元数据管理、数据存储、查询服务、索引同步、操作执行。
• 方法论层（建模→审查→安全→开发→协作）：规范Ontology的使用——怎么建模、怎么审查变更、怎么控制权限、怎么开发应用、怎么团队协作。

三层叠加，才让"操作型本体论"从理论概念变成了可运行的工程系统。
但这一切最终要服务于什么？在AI Agent时代，操作型本体论如何让LLM从"聊天机器人"变成"企业操作员"？
下篇预告： OAG vs RAG——当AI Agent遇到操作型本体论，企业AI的范式正在发生怎样的升级？

本文基于Palantir官方文档及多篇深度分析文献撰写。系列共五篇，欢迎关注后续更新。