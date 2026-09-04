# 后端架构 AI Friendly 的标准与路径:面向无人值守开发时代的系统重构

> **一句话摘要**:当 AI Agent 开始 7×24 小时参与开发、排障、重构、发布,后端系统需要从"可维护系统"变成"可被智能体维护的系统"。本文给出 AI Friendly 的标准(六类事实、Architecture Map、Service Card)、工程能力(SKILL/Harness/测试门禁)、安全边界(权限分级)与落地路线。
>
> **来源**:刘瑞洲《后端架构 AI Friendly 的标准与路径:面向无人值守开发时代的系统重构》,微信公众号 https://mp.weixin.qq.com/s/T2MlWKTESxB_4d9LKc29bg

## 概念

过去十几年,后端系统的核心目标围绕"人类工程师友好":架构清晰、接口稳定、日志可查、发布可控。这些原则没有过时,但当 AI Agent 开始**无人值守**地执行开发、排障、测试、发布时,新问题出现了:**现有后端系统是否足够 AI Friendly?**

!!! note "AI Friendly 不是这些"
    不是"给项目加一份 README",也不是"让代码风格更规范一点"。

真正的 AI Friendly,是让一个 AI Agent 在**有限上下文、有限权限、有限试错成本**的前提下,正确理解系统、定位边界、拆解任务、修改代码、验证结果、评估风险、生成变更说明,并在自动化规则约束下**安全地推进系统演进**。

> 过去我们建设的是「可维护系统」,未来要建设的是「**可被智能体维护的系统**」。

**核心命题**:把隐藏在人脑、群聊、口头约定、历史事故里的系统知识,**显式化、结构化、可检索化、可执行化、可验证化**。人类老员工凭经验知道"这个字段不能乱动、这个 topic 有历史包袱、这个接口看着没人用但小程序还在调用",AI Agent 不知道——它只能通过代码、文档、工具、日志、测试、运行环境去推断。

## 原理:六类事实(Architecture Facts Clarity)

AI Friendly 的第一步,是建立**机器可读的系统事实层**:

| 事实类型 | 内容 | 对 AI 的价值 |
| --- | --- | --- |
| **架构事实** | 业务域划分、服务分层、核心链路、调用/消息拓扑、数据流向、强弱依赖、同步异步边界、发布与故障隔离边界、历史演进约束 | 系统级方向感 |
| **服务事实** | 服务名、业务域、职责、上下游、数据库/缓存/消息依赖、三方依赖、核心接口/表、owner、告警入口、发布与降级方式(建议 `service.yaml`/`domain.yaml`/`dependencies.yaml` 结构化维护) | 节点身份 |
| **领域事实** | 实体、状态机、生命周期、关键不变量、异常分支、幂等要求、补偿机制 | 业务语义,避免"语法正确、业务错误" |
| **接口事实** | 调用方、幂等性、可重试性、超时、限流、鉴权、错误码、兼容性、字段废弃策略、灰度字段、历史坑点(BFF/网关/开放平台必须说明端版本兼容) | 协作契约 |
| **数据事实** | 表结构、字段含义、索引、分库分表、冷热/归档策略、敏感字段、枚举说明(`status=3` 到底代表什么)、逻辑删除、修复脚本 | 状态基础 |
| **运行事实** | QPS、TP99、错误率、是否核心链路、是否强依赖、降级情况、历史事故、consumer lag、热点 key | 真实反馈 |

!!! warning "最危险的风险点"
    AI 对**字段语义的猜测**,是未来自动化开发中最危险的风险点之一——`status=3` 到底是"已支付""已取消"还是"处理中",必须有枚举说明。

这六类事实合起来构成"AI 可理解底座":架构事实给地图,服务事实给身份,领域事实给语义,接口事实给契约,数据事实给状态,运行事实给反馈。没有这层底座,AI Coding 只能停留在"看懂某个文件";有了它,AI 才可能参与跨服务开发、架构治理和无人值守运维。

## 原理进阶 1:Architecture Map 与 System Card

### 全局 Architecture Map

大型分布式系统的复杂性来自**服务之间的关系**,不是单服务内部。Architecture Map 不是 PPT 大图,而是"可被人阅读、可被 AI 检索、可被工具引用、可被 CI 校验、可被 Harness 执行"的系统级地图,至少要回答:

1. 系统有哪些**业务域**(用户/商品/订单/支付/库存/履约/营销/风控/结算…);
2. 服务如何**分层**(网关、BFF、应用服务、领域服务、基础能力、数据平台、运营后台);
3. **核心链路**如何流转(下单/支付/退款/履约…,每步同步还是异步、失败如何补偿);
4. 服务**调用拓扑**(高频/低频、核心链路/后台任务);
5. **消息拓扑**(谁生产谁消费、事件语义、是否允许重复消费、是否要求顺序、死信与补偿);
6. **数据所有权**(谁可写、谁只读、谁禁止直接访问);
7. **强弱依赖**(可降级?有缓存?允许超时跳过?);
8. **发布边界与故障隔离边界**(可独立发布?联动发布?配置灰度?);
9. **历史遗留与演进方向**(legacy / target architecture / 只维护不扩展)。

!!! tip "README vs Architecture Map"
    README 解决"这个仓库如何启动";Architecture Map 解决"整个系统为什么这样组织,以及哪些边界不能被破坏"。

### System Card:每个微服务的"服务身份证"

一张合格的 Service Card 至少包含:服务定位(属于哪个域、解决什么、**不解决什么**)、核心职责(3~7 条,越多说明边界越腐化)、核心实体、数据所有权、接口清单、消息清单、依赖清单、运行特征、变更约束(哪些不能随便改)、测试入口、发布与回滚。

Service Card 应放在服务仓库根目录,由 **CI 检查**其存在性与一致性;并且**部分自动生成**(接口从 IDL/OpenAPI 生成、依赖从调用链生成、表结构从 schema 生成),人类只维护业务解释、边界约束与历史注意事项。对 AI 来说,Service Card 是进入服务前的"第一上下文"。

## 原理进阶 2:领域模型显式化

后端系统最核心的资产不是代码,而是**业务不变量**:已支付订单不能回到未支付、退款不能超过支付金额、优惠券不能重复核销、余额不能变负、同请求不能重复入账、风控拒绝后不能绕过审批。这些规则散落在代码、DB 约束、消息消费和人工流程里,AI 不显式知道就可能在重构时删掉"看似多余的判断"。

领域模型文档重点描述四类内容:

- **不变量**:任何时候都必须成立的规则,写成清晰、可测试、可断言的形式;
- **状态机**:状态枚举、可流转/禁止路径、触发事件、补偿动作;最好有机器可读定义,能生成校验逻辑与测试用例;
- **幂等与一致性策略**:哪个接口靠 requestId 幂等、哪个消息用 businessKey 去重、哪里允许最终一致、哪里必须强一致、哪里需要事务消息/outbox;
- **风险等级**:资金/库存/权限/隐私/风控为高风险域(强制人工 review/双人审批),内容展示/运营配置为中低风险(可自动提交 PR)。

!!! tip "读代码 vs 读领域模型"
    代码告诉 AI "现在怎么做",领域模型告诉 AI "为什么必须这么做"。未来成熟的 AI Friendly 系统,让 AI **先读领域模型,再读代码**。

另外还需要**跨域链路模型**:一条核心链路(下单/退款/会员权益)由哪些服务组成、每步同步还是异步、失败如何补偿、哪里允许最终一致、哪里必须强一致。保护实体不变量的是领域模型,保护系统级一致性的是跨域链路模型。

## 代码 / 实现

原文为方法论文章,无代码。下面用纯 Python 实现一个最小 **Architecture Policy 检查器**(文章第 06 节提到:Harness 应成为全局架构规则的执行器,自动检查变更是否违反架构边界):

```python
# 架构事实(简化):服务分层 + 数据所有权 + 允许的依赖方向
SERVICES = {
    "bff-order":   {"layer": "BFF",        "owns": [],                  "depends": ["order-service"]},
    "order-service": {"layer": "domain",   "owns": ["order", "order_item"], "depends": ["payment-service", "inventory-service"]},
    "payment-service": {"layer": "domain", "owns": ["payment"],         "depends": []},
    "inventory-service": {"layer": "domain", "owns": ["inventory"],     "depends": []},
    "data-report": {"layer": "platform",   "owns": ["report"],          "depends": []},
}
LAYER_RANK = {"BFF": 0, "app": 1, "domain": 2, "basic": 3, "platform": 4}

def check_architecture(change):
    """change: 形如 (service, "calls"|"writes", target) 的变更声明,返回违规清单"""
    violations = []
    svc, action, target = change
    layer = SERVICES[svc]["layer"]
    if action == "calls":
        # 规则1: 禁止反向依赖(基础/平台层调用领域层 = 反向污染)
        tgt_layer = SERVICES[target]["layer"]
        if LAYER_RANK[tgt_layer] < LAYER_RANK[layer]:
            violations.append(f"反向依赖: {svc}({layer}) 调用了更高层 {target}({tgt_layer})")
        # 规则2: 新依赖必须登记
        if target not in SERVICES[svc]["depends"]:
            violations.append(f"未登记依赖: {svc} 新增了对 {target} 的调用")
    elif action == "writes":
        # 规则3: 数据所有权——只有 owner 能写
        if target not in SERVICES[svc]["owns"]:
            owner = [s for s, v in SERVICES.items() if target in v["owns"]]
            violations.append(f"越权写入: {svc} 试图写 {target}(owner: {owner or '未声明'})")
    return violations

# 模拟 AI 提出的三个变更,Harness 在提交前自动检查
changes = [
    ("data-report", "calls", "order-service"),     # 平台层调用领域层 → 反向依赖
    ("bff-order",   "calls", "payment-service"),   # BFF 直接调用支付 → 未登记
    ("order-service", "writes", "payment"),        # 订单服务写支付表 → 越权
]
for c in changes:
    v = check_architecture(c)
    print(f"{c}: {'❌ ' + '; '.join(v) if v else '✅ 通过'}")
```

**运行结果**:三条变更全部被架构策略拦截(反向依赖、未登记依赖、越权写入)——这正是文章说的"过去靠架构师 Code Review 发现,未来由 Harness 自动发现"。真实系统里,`architecture.yaml` 定义规则,Harness 在 AI 提交计划时执行此类检查。

## 实践 / 应用

### SKILL:把团队经验封装成 AI 可调用的工程能力

AI Coding 的效率不靠大模型本身,而靠模型外部的工具、上下文、流程和约束(广义 Harness)。**SKILL** 是可复用的任务包:适用场景、输入信息、相关文件、操作步骤、风险检查、验证命令、输出要求。例如"新增一个数据库字段并完成灰度兼容""排查 Kafka 消费堆积"。

SKILL 化的深层价值:**把资深工程师的经验复制出来**——"加字段要先兼容写、再兼容读、再回填、再切流量、最后清理旧字段"这类经验,沉淀成 SKILL 就是组织经验的可执行资产。

### Harness:为 AI Agent 建立安全的执行轨道

不能让 AI 直接拥有无限权限,必须运行在受控 Harness 里,至少七层:

1. **上下文装载层**:按任务精准加载 Service Card/领域模型/schema/最近 PR/事故,不把整个代码库塞给模型;
2. **工具层**:代码搜索、测试、依赖分析、日志/trace 查询、DB 只读查询、配置查询、mock;工具必须有权边界(生产库默认只读、敏感表脱敏、危险命令禁止);
3. **计划层**:AI 修改前必须输出计划(改哪些文件、为什么、预期影响),低风险自动继续,高风险审批;
4. **执行层**:独立分支/worktree/sandbox,不污染主干;
5. **验证层**:单测、集成、契约、静态检查、安全扫描、schema 检查,没验证不进 PR;
6. **审计层**:AI 读过什么、改过什么、为什么——无人值守不是"不需要责任",而是更强的可追溯性;
7. **回滚层**:变更必须附回滚方案。

更进一步:Harness 应成为**架构规则的执行器**——架构师把分层、依赖方向、数据所有权、核心链路约束写成机器可检查的 **Architecture Policy**,AI 提交变更时自动检查。

### Test-Gated AI Development:测试成为 AI 的红绿灯

测试从"防人出错"升级为"约束和指导 AI 行为":单测(不变量/状态机/金额/权限/风控)、契约测试(防跨服务破坏兼容)、集成测试(完整业务流)、回归用例库(历史事故沉淀,防 AI 反复踩坑)、数据迁移测试(兼容/耗时/锁表/回滚)、性能测试(防 N+1/缓存击穿)、以及**架构级测试**(服务依赖是否违反分层、是否越权访问、核心链路是否新增未备案强依赖、migration 是否锁表)。

> 测试会成为 AI Agent 的**交通信号灯**——"你有没有资格继续往下走"。

### AI-Observable Architecture:可观测性变成 AI 的眼睛

无人值守开发包括排障、修复、自愈,AI 必须能"看见"运行状态:日志统一格式(结构化字段:traceId/spanId/bizId/errorCode/耗时)、错误码有语义(不能全是 SYSTEM_ERROR)、trace 关联业务实体(从 orderId 找到完整调用链)、指标有业务含义(支付成功率/退款失败率/库存扣减失败率/消息积压量)、**告警关联 Runbook**(可能原因/排查步骤/止血方式/修复建议)。没有 Runbook 的告警,对 AI 只是噪音。

### Tiered Access Control:权限分级

AI Friendly 不能以牺牲安全为代价,建议分级权限模型:

| 级别 | 权限 | 典型用途 |
| --- | --- | --- |
| L0 | 只读代码和文档 | 问答、解释、影响面分析 |
| L1 | 本地 sandbox 改代码、跑测试 | 开发,不能碰真实数据 |
| L2 | 查询脱敏日志、测试库、监控指标 | 排障 |
| L3 | 创建 PR、触发 CI、生成灰度配置 | 提交,不能发布 |
| L4 | 低风险服务自动合并与发布(须满足测试/灰度/回滚) | 自动化 |
| L5 | 生产修复动作(回滚/降级/扩容/切配置) | 强审计、强策略、人类预授权 |

数据安全:日志中的手机号/身份证/邮箱/密钥必须脱敏;生产查询默认只读、限行数、限字段、限时间窗口且全量审计;密钥走 secret manager,不进 prompt/日志。

!!! warning "安全悖论"
    一个能力弱的 AI 最多写错代码;一个**能力强但权限失控**的 AI 可能直接制造生产事故。AI 越强,安全边界越重要。

### Code Navigation 与 Docs/Architecture as Code

- **代码可导航**:稳定目录/命名/分层约定(controller/application/domain/infrastructure/repository);减少"隐式魔法"(过度反射、动态代理、运行时拼接)让它可解释可追踪;提供导航锚点(每个接口有入口、每个实体有独立文件、每个状态机有集中定义、每个 topic 有 producer/consumer 定义)。
- **Docs as Code**:文档放仓库、和代码一起 review 和版本管理、参与 CI 检查(新增 controller 必须更新接口文档,否则阻止合并)。
- **Architecture as Code**:架构分层、服务归属、依赖方向、数据所有权、核心链路、风险等级用结构化文件维护(`architecture.yaml`/`ownership.yaml`/`critical-path.yaml`/`risk-policy.yaml`)并参与 CI/CD——全局架构从"PPT 或 Wiki 页面"变成可被 AI 读取、被 CI 校验、被 Harness 执行的工程资产。(与本站 [Ontology as Code](../ontology-agent-adoption/ontology-as-code.md) 同属"把知识变成机器可执行资产"的实践。)

## 实践进阶:三个阶段与落地路线

### Copilot → Coworker → Operator

1. **Copilot**:AI 辅助写代码/解释/生成文档,只需基本文档与测试入口;
2. **Coworker**:AI 独立完成中低风险任务(新增接口、修 bug、补单测、写 migration、生成 PR),需要 Service Card、SKILL、领域模型、契约测试、CI 约束——当前业界 Vibe Coding Agent 基本达到此水平;
3. **Operator**:AI 参与线上值守(接收告警、定位问题、执行回滚、沉淀 Runbook),需要完整可观测性、权限分级、审计、自动化发布——这就是 Vibe Coding 时代的"**黑灯工厂**"。

> 7×24 无人化值守不是一步到位让 AI 接管生产,而是**逐步扩大 AI 的可信半径**:先低风险、强验证区域自动化,再逐步进入复杂系统与生产运维。

### 可落地的改造 Roadmap

1. 选一个中等复杂度、风险可控的业务域试点(不要选玩具服务,也不要选支付/资金);
2. 先建立**最小可用的全局 Architecture Map**——可以粗,但必须真实;可以不完整,但不能误导;
3. 为试点服务补齐 **Service Card**;
4. 梳理**核心领域模型**(实体、状态机、不变量、幂等);
5. 沉淀 **5~10 个高频 SKILL**;
6. 补**测试与契约**(先覆盖核心链路与高频变更点);
7. 建立 **AI PR 模板**(变更说明/影响面/测试结果/风险点/回滚方案);
8. **CI 变成硬门槛**(没通过测试/文档检查/安全扫描不能合并);
9. 接入**只读可观测工具**(脱敏、限权、审计);
10. 允许 **AI 低风险自动 PR**(先人工 review);
11. 逐步扩大到更多服务与更复杂任务。

!!! tip "路线关键"
    不要先追求"无人化",要先追求"**可验证**"。无人化不是目标本身,可验证的自动化才是目标。

## 总结

- **AI Friendly = 可被智能体维护的系统**:把系统知识从人脑资产变成机器可读资产(显式化、结构化、可检索化、可执行化、可验证化)。
- **底座是六类事实**:架构、服务、领域、接口、数据、运行;上层是 Architecture Map 与 System Card。
- **能力靠 SKILL + Harness**:经验沉淀为可调用任务包,AI 在受控执行轨道(上下文/工具/计划/执行/验证/审计/回滚)中干活,架构规则由 Policy 自动执行。
- **安全靠测试门禁 + 权限分级**:测试是 AI 的红绿灯(L0~L5 分级授权),数据脱敏与强审计不可省。
- **演进分三阶段**:Copilot → Coworker → Operator(黑灯工厂);落地从最小 Architecture Map 起步,先求"可验证"再求"无人化"。
- **最终改变组织方式**:文档给 Agent 装载上下文,测试约束 AI 边界,Runbook 是 AI 排障图谱,架构治理由规则/CI/权限/Harness 自动执行。

## 延伸阅读

- 站内:[AI Friendly 架构子主题](index.md)、[Ontology as Code](../ontology-agent-adoption/ontology-as-code.md)、[Agent 开发实践](../../03-agents/agent-practice.md)、[Agent 评测](../../03-agents/agent-evaluation.md)
- 外部:原文《后端架构 AI Friendly 的标准与路径》(刘瑞洲,https://mp.weixin.qq.com/s/T2MlWKTESxB_4d9LKc29bg);原始资料存档于 `docs/inbox/ai-friendly-backend-source.md`
