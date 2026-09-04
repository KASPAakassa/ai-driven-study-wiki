# 原始资料:Palantir本体构建解密:人工、自动还是人机协同?

> 来源:微信公众号(本体论/案例分析系列);抓取日期:2026-08-09
> 状态:已提炼整合进 06-enterprise/ontology-agent-adoption/ 的 Palantir 操作型本体论系列文章

---

摘要
Palantir Ontology 凭什么值4000亿，理论体系已经拆过了。但有个问题一直悬着：这东西到底怎么建？是纯手工一砖一瓦地砌，还是有自动化工具批量生成？成本和准确性怎么平衡？

一、先说结论：不是自动生成，是"映射+推断+审核"
很多人第一次听说 Palantir Ontology 的概念，第一反应是：这不就是知识图谱吗？既然是大模型时代了，AI 能不能自动从数据里"生"出一个本体来？

答案是不能。至少截至目前的公开文档里，Palantir 没有任何工具能从一堆原始数据里自动"设计"出 Object Type、Link Type 和 Action Type 的结构。

社区里有一篇帖子《本体与 Pipeline 设计原则》，说得非常直白：本体不是数据仓库，而是一个需要被精心设计和持续维护的 API。别把源系统的数据表原封不动同步过来就完事。

这句话基本定调了 Palantir 对本体构建的态度——本体设计是人主导的创造性工作，自动化只出现在辅助环节。

那自动化的辅助具体在哪？三个地方：

第一，数据集模式自动推断。Foundry 有一个叫 foundry-schema-inference 的能力，你上传一个 CSV 或 JSON 文件，系统会根据数据样本自动推断每一列的数据类型——字符串、整数、日期或布尔值。

第二，列到属性的自动映射。当你在 Ontology Manager 里给一个对象类型选了底层数据集后，系统会自动把数据集的每一列映射成属性，同时自动推断属性 ID、显示名称和基础类型。你可以后续删除不需要的自动映射。

第三，Pipeline Builder 自动生成转换代码。用户在可视化界面里点选定义对象类型的目标模式，后端会自动写出数据转换代码。

但请注意，这三个自动化环节都不涉及"设计本体结构"本身。推断模式是在数据集层面，自动映射是在列到属性层面，自动生成代码是在数据流水线层面。真正决定"有哪些对象类型、它们之间怎么连接、每个对象上挂哪些操作"这些本体架构问题，仍然是人工决策。

用一句话概括：Palantir 的本体构建是"人工设计架构 + 机器辅助映射 + 人工审核确认"的三段式流程。

二、本体构建的完整流程：从数据到对象
根据公开文档，在 Foundry 里构建本体的标准路径是这样的。

第一步：数据接入（Data Connection）
数据从外部系统同步进 Foundry。官方的做法是"As-Is"——数据从最原始的源系统原样接入，不做外部预处理。这样做的原因是，Foundry 内部有分支和版本控制的流水线，它要成为数据从原始状态到进入本体的"唯一变更来源"。如果你在外面先做了一层预处理，Foundry 就无法追踪数据变更的完整历史。

Foundry 提供 200 多个数据连接器，覆盖常见的数据库、文件系统、API 和流式数据源。接入过程支持自动重试和批量拉取，降低对源系统的压力。

第二步：数据转换（Pipeline Builder）
数据进来之后，用 Pipeline Builder 做清洗和转换。这是 Foundry 的旗舰数据工程工具，核心特点是"点选式"操作——你不需要写代码，通过可视化界面描述数据转换逻辑，后端自动生成转换代码。

关键能力是流水线的输出可以直接是本体组件。也就是说，你可以在流水线构建器里直接定义和创建对象类型，不需要再跳回本体管理器操作。

这里有个设计细节值得注意：Pipeline Builder 支持批量数据和流式数据两种输入，但对于流式数据，不能配置编辑功能和多对多链接。这是一个功能性约束，不是 bug——流式数据的特性决定了实时写入和复杂关联之间存在性能取舍。

第三步：本体定义（Ontology Manager）
这是核心环节。Palantir 有一个专门的工具叫 Ontology Manager（有时也叫 OMA），负责构建和维护组织范围内的本体。
在这个界面里，你完成以下操作：

创建 Object Type。 选择一个 底层数据集 作为数据源，系统自动把列映射为属性。然后你需要配置几个关键信息：主键用于唯一标识每个对象，标题键用于在界面上显示对象的名称。还可以设置 icon、显示名称、plural name、description 等元数据。

定义 Link Type。 连接两个 Object Type，类似数据库的外键关系。但比外键更丰富——Link Type 可以携带属性，比如"客户A下了订单B"这个链接上可以挂"下单时间"、"下单渠道"等信息。

配置 Action Type。 这是 Palantir 本体区别于传统知识图谱的关键。Action 定义了"能对对象做什么操作"，比如"修改订单状态"、"审批采购申请"。每个 Action 可以配置校验规则、审批流程和权限控制。

整个创建过程有一个 7 步向导引导你完成：创建 Object Type → 选 底层数据集 → 配置元数据 → 创建 properties（自动映射+手动调整）→ 配置主键和标题键 → 生成 actions（可选）→ 保存。

有个细节：一个数据集只能支撑一个 Object Type，这是硬约束。但反过来，一个 Object Type 可以由多个数据集支撑，这叫 Multi-Datasource Object Type（MDO），后面会展开讲。

第四步：本体消费（Applications + AIP）
本体建好后，上层的 Workshop、Quiver、Object Explorer 等应用直接消费 Ontology 里的数据。AIP（Palantir 的 AI 平台）也是在 Ontology 之上构建的——它消费已有本体，不负责生成本体。官方架构文档写得很清楚：AIP 的开发工具支持在 Ontology 之上构建生产级的 AI 工作流、智能体和函数
三、AI 在本体构建中到底干了什么？
这是我最想搞清楚的问题。大模型时代，AI 在 Palantir 的本体构建流程里扮演什么角色？我逐层拆解。

3.1 数据层：Schema 推断
这是 AI 辅助最成熟的地方。Foundry 的 foundry-schema-inference API 能对 CSV、JSON 文件自动推断列类型——字符串、整数、日期、布尔值，根据数据样本自动判断。这个能力在数据集层面工作，不涉及语义理解，纯粹是数据类型推断。

3.2 映射层：列到属性的自动填充
当 Object Type 选了 底层数据集 后，系统自动把每列映射成 property，属性 ID、显示名称和基础类型从列名中自动推断出来。
这更像是一个规则推断——从列名推导 property 名，从列类型推导 property 类型。没有 NLP，没有语义理解，就是命名规则的转换。

3.3 实例层：AIP Logic 的非结构化数据映射
这里有一个有意思的能力。AIP Logic 可以把非结构化数据（比如 PDF 文档）映射到已有的 Object Type 上。Palantir YouTube 上有一个演示视频，标题叫《使用 Palantir AIP 进行高级搜索》，里面展示了一个场景：把一份非结构化 PDF 的内容抽取出来，映射到 Ontology 里的 object。
但请注意——这是在已有 Object Type 上创建 object 实例，不是生成新的 Object Type schema。你得先定义好"合同"这个 Object Type 有哪些 property，AIP 才能把 PDF 里的信息填进去。AI 干的是信息提取和实例填充，不是 schema 设计。

3.4 架构层：AI FDE——Palantir 的新赌注
这是 2024 年最重要的更新。Palantir 推出了 AI FDE（AI-powered Forward Deployed Engineer），它是一个通过对话指令操作 Foundry 的交互式智能体。

它的能力列表里明确包含本体编辑：创建和更新构成本体的对象、链接和操作。

这意味着什么？Palantir 开始用 AI agent 来辅助本体构建了。但有几个关键约束：

第一，AI FDE 需要 AIP 启用，而且推荐开启 Global Branching 来支持本体编辑。这说明本体编辑是在分支上进行的，不是直接改主分支。

第二，AI FDE 继承用户现有权限——所有操作都继承用户现有的权限范围，不会越权操作。

第三，从整体架构看，AI agent 不直接改本体，而是创建"提案"（proposals）。官方平台概述文档说：AI 智能体不直接修改本体，而是创建提案。这些提案需要人工审核后才合并到主分支。

所以 AI FDE 的定位是：通过对话式交互辅助本体编辑，但在 人工审核环节 框架下运行。它降低了本体构建的操作门槛（不用手动在 Ontology Manager 里一步步点），但决策权仍在人手里。
四、实体对齐：Palantir 怎么处理"同一个人"
本体构建里有个经典难题：不同数据源里的同一实体怎么合并？比如 CRM 系统里叫"张三"，ERP 系统里叫"Zhang San"，物流系统里只有一个手机号——这三个记录指向同一个人，怎么对齐？

这是知识图谱领域的经典难题，学术上叫 Entity Resolution（实体解析）或 Entity Alignment（实体对齐）。Palantir 在这个环节的处理方式，是我这次调研中最意外的发现。

4.1 独立的 Entity Resolution 产品
Palantir 有一个专门的 Entity Resolution 产品，不是 Ontology 里的一个小功能，而是独立的 Foundry 能力。它能对来自不同系统的百万级记录进行持续匹配，并对实体解析的每个步骤提供端到端的透明度。

在金融行业案例中，ML 模型自动从全球海量数据中解析十亿级记录。

技术栈方面，用了 hashing methods 和 AI/ML models 来提升速度并降低计算成本，同时用 fuzzy matching techniques（模糊匹配）提升准确性。零售行业白皮书中也提到了模糊匹配的用法。技术、人工审核验证，以及能够从配对建议中持续学习和改进的机器学习模型

此外还实现了全流程覆盖，从模糊匹配到特征生成到模型训练到人工验证，每个环节都有工具支持。同时面向 no/low-code 用户和 code-based 用户。

4.2 人机协同的解析流程
Palantir 的实体解析不是全自动的 ML 管道，而是ML 推荐匹配 + 人工审核确认的模式。

具体来说，ML 模型会给出匹配建议（pairing suggestions），人工审核后确认或拒绝。模型会从人工反馈中学习，持续改进匹配质量。官方声称这种方式比客户自己做的准确率高 40%——"40% increased accuracy over customer-led attempts"。

这就是 Palantir 在成本和准确性之间的平衡策略：ML 负责大规模粗筛（降本），人工负责边界 case 确认（保准确性），反馈循环持续提升模型质量。

4.3 Gotham 的 Object Resolution API
除了 Foundry 的 Entity Resolution 产品，Palantir 另一个平台 Gotham 也有 Object Resolution 的 API 级实现，定义了对象合并的具体机制。

官方 API 文档的定义是：对象解析是将两个或多个对象合并为一个的操作。比如，将来自不同源系统中指向同一现实实体的对象合并，避免创建重复对象

设计上有两个亮点：

可逆性。合并后的对象保留了各子对象的独立历史——如果需要反合并，每个子对象的更新记录都能完整保留这意味着实体合并不是一次性的不可逆操作，你可以"反合并"。

隔离写入。合并时会创建一个内部 winner object，用于隔离新写入的属性。这样如果需要拆分，可以把 winner object 上的新属性干净地剥离出来。解析元数据有三个组件：canonicalObjectPrimaryKey（合并后对象主键）、winnerObjectPrimaryKey（隔离新写入的内部对象）、otherObjectPrimaryKeys（被合并的其他对象）。

这个设计思路跟 Git 的分支合并有异曲同工之处——合并不是覆盖，而是创建一个新的"合并提交"，保留了所有原始信息。

4.4 透明度：每一步都可追踪
Entity Resolution 产品强调的一个特性是端到端可见性——对齐过程的每一步都可见可追踪。这意味着当两个记录被合并时，你能看到：是哪条规则触发了匹配？ML 模型的置信度是多少？是否经过了人工确认？谁确认的？

这种透明度在企业场景里至关重要。反洗钱（AML）场景中，如果两个客户记录被错误合并，可能意味着漏报一笔可疑交易——监管要求你必须能解释为什么合并了这两条记录。Palantir 的设计显然考虑了这类合规需求。

五、成本与准确性的平衡术
讲完流程和技术细节，回到一个更本质的问题：Palantir 怎么在构建成本和本体准确性之间做平衡？

5.1 General Mills 案例的真实数据
目前公开资料中最详实的数据来自 General Mills 的 Impact Study（AIPCon 2024 年 3 月）。General Mills 从 2019 年开始跟 Palantir 合作，构建了一个集成了200 张主数据和运营数据表的本体。业务背景是：4000 家供应商、200 多家工厂、年服务约 120 万订单、运营人员每年做约 5000 万次决策，驱动 100 亿美元 COGS。

这个本体上跑了 Project ELF（端到端物流流系统），基于 AIP 构建。最关键的数据是：

ELF 系统生成的推荐中，超过 70% 被人工审核接受。结果是每天节省 4 万美元，年化 1400 万美元——而且只部署到了部分网络。

70% 的接受率说明什么？AI 自动化承担了高频推荐生成（降本），人工把关约 30% 的高风险或异常决策（保准确性）。这不是"全自动"也不是"全人工"，而是精确计算过的分工比例。

5.2 bp 案例：数字孪生的规模效应
bp 的案例提供了另一个维度的数据。bp CEO Bernard Looney 在公开场合这样描述合作效果：他们帮 General Mills 构建了一个数字孪生系统，每天处理 10 亿条进入数据湖的数据点。原本需要 24 小时的工作，现在只需 20 分钟。

每天 10 亿数据点进入数据湖，原来需要 24 小时的分析缩短到 20 分钟。这里本体扮演的角色是"全组织共享的数字孪生"——官方描述为一个完整、动态的企业业务数字映射，由整个组织共享

规模效应体现在：本体建好之后，每个新增用例的边际成本递减。因为数据已经映射到统一的语义模型上，新用例不需要重新对接数据源，只需要在本体上构建新的应用逻辑。这正是本体的"平台效应"——前期投入大，但边际成本递减。

5.3 人工审核环节：不是口号，是架构
公开文档对人工审核环节的描述不是停留在口号层面，而是嵌在架构里的。AIP 的伦理与治理文档明确提出了三大支柱：

基于本体的决策支持——AI 推荐在 Ontology 的结构化上下文中呈现，增强而不是替代人类判断。
人类监督工作流——通过 Ontology 的 actions 和审批流程，确保关键决策在人类控制之下。
反馈循环——AI agent 创建提案，人工审核后反馈，agent 从反馈中学习。提案模式会生成有价值的元数据，让智能体能从持续反馈中学习和进化。

还有一个设计原则贯穿始终：设计增强而非替代人类决策的 AI 系统

在技术实现上，这个架构依赖两个关键机制：
Actions 作为控制平面。Actions 被称为"企业的动词"。AI agent 被 sandbox 在 Actions 定义的限制范围内，只能操作被授权的数据和工具。Actions 提供的细粒度权限和访问控制构成了一个"控制平面"，智能体在这个平面内被限制在特定的数据和工具使用范围内。
Global Branching 作为变更管理。本体编辑在分支上进行，就像代码的 Git 分支。AI FDE 的本体编辑推荐开启 Global Branching，AI agent 创建的提案是分支上的变更，需要经过 review 和 merge 才进入主分支。这保证了任何 AI 生成的变更都有人工审核环节。

六、治理：本体层面的安全与权限
本体构建不只是"建起来"，还包括"管起来"。一个包含企业核心数据的本体，如果权限管理不到位，就是灾难。Palantir 在这个层面有一套相当精细的体系。

6.1 权限模型的演进
Palantir 的本体权限模型经历了一次重要升级。旧模型使用本体专属角色（Ontology viewer、Ontology editor、Ontology owner），新模型统一到 Compass 文件系统——Palantir 平台的底层文件系统。本体资源与其他资源类型使用同一套权限系统，你只需要学习和管理一套权限逻辑。

统一的好处是：本体的权限管理跟数据集、流水线、模型等其他资源的权限管理用同一套逻辑，不需要单独维护一套本体权限体系。

6.2 Backing Dataset 的权限传递
这是个很关键的设计。每个 Object Type 必须有一个 底层数据集，而 底层数据集 的权限会传递到 Object Type。底层数据集用于派生用户对给定 Object Type 中对象的访问权限，因此是必需的。

这意味着：如果你对一个数据集没有读权限，你通过 Object Type 也看不到这份数据。权限不是在 Ontology 层重新定义的，而是从数据源继承的。这保证了一条——本体的权限不会比底层数据的权限更宽松。

6.3 Markings：细粒度的数据分类
除了角色权限，Palantir 还有 Markings 机制，用于标记敏感数据。你可以给一个 Object Type 打上 Marking，只有拥有对应 Marking 权限的用户才能看到。通过给资源打上标记来隐藏敏感的本体内容。

Markings 是全局授予用户的——标记权限是全局授予用户的。但拥有 Marking 不等于能看到所有标记该 Marking 的内容，用户还需要有角色权限。这是一个双重保险机制。

更重量级的是 CBAC（Classification-Based Access Control）。分类标记的配置需要 Palantir 介入——这套机制不是自助开通的，需要 Palantir 介入配置。它的特性包括层级控制（Hierarchy）、析取组件（Disjunctive elements）和全覆盖性（Ubiquity，所有 Project 必须设置 classification）。

6.4 MDO：多数据源对象类型与列级权限
前面提到 MDO（Multi-Datasource Object Type），它的一个重要用途是支持列级权限控制。列级 MDO 可以用来支持需要列级权限控制的场景。

比如一个"客户"对象，基本信息（姓名、手机号）来自 CRM 数据集，财务信息（信用额度、欠款）来自 ERP 数据集。通过 MDO，你可以控制：销售团队只能看到基本信息，财务团队能看到全部。列级权限直接在 Object Type 层面配置，不需要在应用层做过滤。

顺便澄清一个术语混淆——之前有人把 MDO 理解成"任务决策目标"，但公开文档里 MDO 就是 Multi-Datasource Object Type 的缩写，纯粹是技术术语。官方真正用于"模型与业务目标对齐"的概念叫 Model Objectives——Model Objectives 允许你通过业务运营结果来定义一个具体的建模问题

七、FDE 模式：本体构建的人力引擎
最后聊一个不太技术但很关键的问题：谁来构建本体？

7.1 Forward Deployed Engineer 模式
Palantir 的本体构建不是客户自己搞的，而是由 FDE（Forward Deployed Engineer，前驻工程师）主导。这个角色是 Palantir 在 2005 年发明的，核心特点是工程师驻场客户现场，深入理解客户业务，直接在客户数据上写生产代码。

第三方分析 getperspective.ai 对 FDE 模式的总结是：前驻工程师是驻场数周至数月的软件工程师，他们深入理解客户业务全貌，直接在客户数据上编写生产级代码，并将产品反馈带回平台团队

FDE 在本体构建中的具体角色是：理解客户的业务流程和数据分布，设计 Object Type 和 Link Type 的结构，配置 Action 的校验规则和审批流程。说白了，FDE 就是本体架构师+数据工程师+业务分析师的合体。

7.2 从 FDE 到 AI FDE：成本结构的变迁
FDE 模式的问题很明显——人力成本极高。每个客户都需要驻场工程师，工程师需要数周数月深入业务，这直接限制了 Palantir 的扩展速度。

AI FDE 的推出，本质上是 Palantir 在尝试打破这个人力瓶颈。用一个 AI agent 来承担 FDE 的部分工作——通过对话式交互操作 Foundry，辅助本体编辑——可以降低每个客户所需的 FDE 投入。

但文档的措辞很谨慎。AI FDE 的定位是通过对话指令来操作 Foundry，而不是替代 FDE。它继承用户权限，创建提案而非直接修改，需要 Global Branching 支持审核流程。所有这些设计都在说同一件事：AI 降低的是操作成本，不是决策成本。

7.3 Use Case Lifecycle：本体构建的项目化
文档把本体构建定义为"use case"——用例是一个有时限的任务，由专门团队为特定用户群体交付平台新能力

这意味着本体不是一次性"建好"的，而是随着用例逐步生长的。每个 use case 带来新的 Object Type、新的 Link、新的 Action，本体在迭代中扩展。

官方的 Solution Design 流程明确说明了本体设计与业务目标的关系：方案设计的流程，就是把用例需求提炼成能指导接口实现和数据丰富化的决策。这些决策反过来指导本体设计，本体充当用例的 API

翻译过来就是：先明确业务用例需要什么决策，再反推需要什么数据和本体结构。实施伙伴 BD Emerson 给了一个更直白的建议：从你希望操作人员下个季度做出不同决策的那个决策点出发，反向推导该决策需要的对象、链接和操作

这个方法论跟传统的"先建数据仓库再找用例"完全反过来了。Palantir 的逻辑是：从决策出发，反推本体结构。不是"有什么数据就建什么本体"，而是"要做什么决策就建什么本体"。

八、总结：Palantir 本体构建的三个核心判断
扒完所有公开资料，我对 Palantir 的本体构建方式有三个核心判断。

第一，本体设计是人工主导的创造性工作，没有银弹。 截至目前的公开文档，Palantir 没有任何工具能自动从数据"生成"本体结构。AI/ML 的角色局限在辅助环节：数据集模式推断、列到 property 的自动映射、Pipeline 转换代码的自动生成。本体架构——有哪些 Object Type、它们怎么连接、挂什么 Action——仍然是 FDE 和客户业务专家共同决策的结果。AI FDE 的出现降低了操作门槛，但没有改变"人设计、机器辅助"的基本格局。

第二，实体对齐是人机协同的，ML 粗筛+人工审核是标配。 Palantir 有独立的 Entity Resolution 产品，用 hashing + ML + 模糊匹配做大规模匹配，但在关键环节保留人工验证。模型从人工反馈中学习，持续提升匹配质量。这种模式在成本和准确性之间取得了平衡——ML 处理大规模数据的粗筛（降本），人工处理边界 特殊情况的确认（保准确性），反馈循环让模型越来越准。Gotham 的 Object Resolution API 还设计了可逆合并机制，合并可以撤销，历史完整保留。

第三，成本与准确性的平衡是架构层面的设计，不是临时补救。 人工审核环节 在 Palantir 不是口号，而是嵌在架构里的——Actions 作为控制平面限制 AI agent 的操作范围，Global Branching 作为变更管理确保 AI 生成的变更经过审核，提案式工作流让 AI 创建提案、人工审核合并。General Mills 案例 70% 的 AI 推荐接受率，就是这个架构的实际运行效果：AI 承担 70% 的高频决策（降本），人工把关 30% 的高风险决策（保准确性），最终年化节省 1400 万美元。

Palantir 的本体构建方式，本质上是一种"精确的妥协"——在全自动和全人工之间找到了一个经过计算的平衡点，每个环节的自动化程度都对应着特定的成本/准确性权衡。这种平衡不是一成不变的，AI FDE 的出现意味着天平正在向自动化一侧倾斜。但至少在可预见的未来，"人设计架构、机器辅助执行"的基本格局不会变。
参考资料
Palantir Ontology 概览：https://palantir.com/docs/foundry/ontology/overview
Ontology Manager：https://palantir.com/docs/foundry/ontology-manager/overview
Object Type 创建：https://palantir.com/docs/foundry/object-link-types/create-object-type
AIP 架构：https://palantir.com/docs/foundry/architecture-center/aip-architecture
AI FDE：https://palantir.com/docs/foundry/ai-fde/overview
Entity Resolution 产品：https://www.palantir.com/foundry-entity-resolution
Gotham Object Resolution API：https://palantir.com/docs/gotham/api/revdb-resources/resolution/resolution-basics
Pipeline Builder Outputs：https://palantir.com/docs/foundry/pipeline-builder/outputs-overview
模式推断：https://palantir.com/docs/foundry/building-pipelines/infer-schema
Data Connection：https://palantir.com/docs/foundry/data-connection/overview
Object Backend / Object Storage V2：https://palantir.com/docs/foundry/object-backend/overview
本体权限模型：https://palantir.com/docs/foundry/object-permissioning/ontology-permissions
Multi-Datasource Object Types：https://palantir.com/docs/foundry/object-permissioning/multi-datasource-objects
AIP 伦理与治理：https://palantir.com/docs/foundry/aip/ethics-governance
Platform Overview（提案式工作流）：https://palantir.com/docs/foundry/platform-overview/overview
Use Case Lifecycle：https://palantir.com/docs/foundry/use-case-life-cycle/overview
General Mills Impact Study (AIPCon 2024)
bp Energy Offering：https://www.palantir.com/offerings/energy
Palantir 社区：Ontology and Pipeline Design Principles：https://community.palantir.com/t/ontology-and-pipeline-design-principles/5481