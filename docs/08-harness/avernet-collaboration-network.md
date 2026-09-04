# Avernet:蚂蚁开源的 Agent 协作层"操作系统"——BCS 组网实战

> **一句话摘要**:当行业还在卷单个 Agent 的推理能力时,蚂蚁开源 **Avernet**(社区版 V0.1,Apache 2.0)尝试解决 Agent 之间的"关系网"问题——构建协作层的"操作系统",让异构、分散的 Agent 像成熟软件服务一样**被发现、被调度、被连接**。核心是 Rust 实现的 **BCS(Bot Coordination Service)**,通过 Plugin/Gateway 双路径集成,不绑定单一引擎。
>
> **来源**:微信公众号「赫文派」《蚂蚁开源 Avernet:破解多智能体协作难题,更要学会组网实战》,https://mp.weixin.qq.com/s/uMSfd1yUlYJnVaQOVt1uJg;原始资料存档于 `docs/inbox/avernet-source.md`;官方仓库与文档见 https://github.com/alipay/avernet(或蚂蚁开源公告)

## 概念:为什么要一个"协作层操作系统"

**单兵作战困境**:单个大模型的逻辑推理能力在提升,但跨业务、跨领域的复杂任务一旦涉及多个 Agent,系统往往变得极其脆弱且难以扩展。

**Avernet 的技术转向**:不卷模型本身的推理,而是构建一套**协作层的"操作系统"**——处理 Agent 的"社会关系"管理。核心价值:让异构 Agent 能够无缝集成,不需要把所有功能塞进一个大模型,而是像搭积木一样,用专门负责财务审计的 Agent 配合专门负责代码审查的 Agent,通过 Avernet 统一的路由与会话管理实现业务闭环。

> **真正的挑战不在于模型本身,而在于如何管理这些模型的"社会关系"。**

## 原理:解决四类协作痛点

| 痛点 | 问题 | Avernet 的解法 |
| --- | --- | --- |
| **找不到** | 能力发现难题:公司里 10 个部门用不同模型/Prompt 各自搞出一套 Agent,新业务流程不知道去哪里调用、如何识别能力边界 | **Agent 发现与市场**:支持 Agent 注册与发现,不同来源的 Agent 通过统一协议加入同一协作网络,能力标准化暴露 |
| **对不齐** | 共识达成难题:多 Agent 在同一语境下达成共识难;传统主 Agent 协调会导致高延迟和单点风险 | **群组、会话与共享上下文**:把不同 Agent 的信息、视角与输出汇聚到同一空间,复杂任务输出不再是零散碎片,而是有完整上下文的协作成果 |
| **跑不快** | 任务流转难题:任务依赖需大量人工干预或复杂硬编码,转交效率低 | **BCS 核心架构(Rust 实现)**:高性能低延迟,通过路由与消息投递把多 Agent 协作的不确定性转化为可编排、可追踪的工作流 |
| **留不住** | 经验沉淀难题:优秀的 Agent 系统不应只"执行任务",更要"学会任务" | **进化闭环**:对 Agent 能力与协作模式的反馈,形成观察→评估→复用→优化的闭环 |

## 原理:BCS 架构——协作层的"大脑"

**BCS(Bot Coordination Service)** 不负责模型层的推理,但负责管理"谁在说话、谁在听、谁在做"。

**双路径集成设计**(不绑定单一引擎):

1. **Plugin 集成(主动连入)**:Agent 通过 WebSocket 的 `/ws/bot` 接口直连 BCS——适合构建自定义 Agent 或通过 OpenClaw TypeScript 插件扩展,让 Agent 主动接入协作网络;
2. **Gateway 集成(被动调度)**:针对已有 Bot 平台的集成方式——即使已有运行良好的 Agent 平台,也可以通过 Avernet 网关调度起来,实现异构 Agent 生态接入。

无论是 OpenClaw、自定义 Agent 还是第三方 Bot 平台,只要接入 Avernet 就能享受统一的**注册、路由与会话管理**能力。

## 代码 / 实现:快速跑通第一个协作流

```bash
# 一键启动本地开发栈:Avernet 进程 + 5 个本地测试 Bot + Web 前端工作台
./scripts/singlebox.sh --local

# 生产级环境:Docker 源码构建
docker compose up --build
```

- **注意**:基础协作能力不需要配置模型 API key;但若希望 Demo Bot 给出真实回复,需在环境变量配置 `OPENCLAW_OPENAI_*` 等相关参数;
- 浏览器访问 **127.0.0.1:8000** 进入前端工作台——直观看到不同 Agent 之间的消息流转、会话状态与协作过程的可视化反馈;
- 快速上手建议:不要从复杂配置开始,用 `singlebox.sh` 一键启动即可。

## 实践 / 应用:工程师视角与局限

### 定位判断:"操作系统"还是"粘合剂"?

作者观点:**不是取代现有 Agent 推理引擎,而是定义 Agent 之间的通信协议**——为 Agent 的大规模落地铺设"路基"。它的价值在于协作层基础设施:让异构 Agent 无缝集成,像搭积木一样组合不同能力的 Agent。

### 使用建议

1. **不要试图用一个模型解决所有问题**:通过 Avernet 插件机制,将不同能力的 Agent 解耦与重组;
2. **关注协作过程的可观测性**:利用工作台实时监控 Agent 间通信,对定位复杂逻辑错误至关重要;
3. **关注长效记忆构建**:结合 Avernet 的会话管理能力,实现 Agent 经验的沉淀与复用。

### 当前局限(社区版 V0.1)

尚未完全开放:**审计追踪、可观测性评测、记忆优化、容器集群管理**等高级功能。但 BCS 已解决 Agent 的"身份、连接与路由"问题,为后续"记忆与持续进化"打下工程基础。

## 总结

- **定位**:蚂蚁开源的多智能体协作基础设施(社区版 V0.1,Apache 2.0)——协作层的"操作系统",让异构 Agent 被发现、被调度、被连接;
- **四痛点**:找不到(Agent 发现与市场)/ 对不齐(群组会话共享上下文)/ 跑不快(BCS 路由消息投递)/ 留不住(观察-评估-复用-优化进化闭环);
- **BCS 架构**:Rust 实现的高性能 Bot Coordination Service,管理"谁在说、谁在听、谁在做";Plugin(主动连入 WebSocket)/ Gateway(被动调度已有平台)双路径,不绑定单一引擎;
- **快速上手**:`./scripts/singlebox.sh --local` 一键起 5 Bot + Web 工作台,无需 API key;
- **局限**:V0.1 未开放审计追踪/可观测性评测/记忆优化/容器集群管理;
- **下一步**:对比站内其他协作类 harness([Multica](multica.md) 编码 Agent 调度中台、[OpenWorker](openworker-architecture.md) 桌面 Agent),或看 [统一索引](orchestration-frameworks.md) 中其他编排框架。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/uMSfd1yUlYJnVaQOVt1uJg;蚂蚁开源公告与官方文档(仓库见 GitHub)
- 站内:[通用编排框架索引](orchestration-frameworks.md)(Avernet 已收录)、[Harness 章节首页](index.md)、[Multica:编码 Agent 统一调度中台](multica.md)(同类协作调度)、[OpenWorker 桌面 Agent](openworker-architecture.md)、[Agent 协作规则](../03-agents/agent-collaboration-rules.md)(协作设计)
