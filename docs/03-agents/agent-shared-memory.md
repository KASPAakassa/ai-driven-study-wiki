# Agent 共享记忆:多 Agent 协作的"同一个大脑"——从共享记忆池到群体智能

> **一句话摘要**:单体 Agent 的"记性"已讲透,但当系统里有 5 个 Agent 协作、各自记各自的,就成信息孤岛联邦——"Agent A 搜到的资料,B 完全不知道;C 发现客户已透露需求,A 还在重复问"。**共享记忆池(Shared Memory Pool)** 让所有 Agent 写入同一个记忆库、互读内容,但随之而来的是数据模型、一致性、检索效率、遗忘与权限五大工程问题。本文给出选型方案:向量库 / 图数据库 / 事件日志三阵营、场景锁与 CRDT、记忆分层与语义路由、遗忘的访问续期。
>
> **来源**:微信公众号「大斌的AI小栈」《Agent 共享记忆:当多个 Agent 用同一个"大脑"时,系统才真正开始思考》(《Agent 记忆系统》系列第 12/15 期),https://mp.weixin.qq.com/s/SiivT0gLN6mxKi97O5wvsg;原始资料存档于 `docs/inbox/agent-shared-memory-source.md`

## 概念:单体记忆的天花板

很多多 Agent 系统长这样:每个 Agent 都有自己的 vector store / chat history——**信息孤岛**。Agent A 搜索到的资料,B 完全不知道;Agent C 发现客户在第 3 轮透露过需求,A 在第 5 轮还在重复问。

> **不是"Agent 不够聪明",是记忆架构的隔离导致了全局认知的缺失。**

**解决方案:共享记忆池**——所有 Agent 写入同一个记忆库,读取时也能看到其他 Agent 写入的内容。但引出五大工程问题:

| 问题 | 描述 |
| --- | --- |
| 数据模型 | 谁的记忆格式?schema 谁设计? |
| 一致性 | 两个 Agent 同时写,谁先谁后?谁覆盖谁? |
| 检索效率 | Agent 变多、记忆暴增,检索不能慢 |
| 遗忘 | 共享记忆谁负责清理?清理了别人的怎么办? |
| 权限 | Agent A 能不能读 Agent B 的"私有思考"? |

## 原理:三大技术阵营对比

### 1. 向量数据库(Embedding + Vector Store)

**代表方案**:crewAI(默认 Chroma,可切 Pinecone/Milvus)、AutoGen(InMemoryAgentMemory → VectorDBAdapter)、Mem0(默认 Qdrant)。

**工作流**:Agent 产出 → embed → upsert 到向量库;Agent 回忆 → embed 查询 → top-K 相似 → 注入上下文。

- **优势**:语义检索天然强("想起类似的事情")、生态成熟(Pinecone/Weaviate/Qdrant 生产验证)、元数据过滤灵活(`{"agent_id": "A", "task": "research"}`);
- **劣势**:精确查询弱(结构化查询要走额外通道)、一致性靠数据库自身、遗忘策略粗糙(删 embeddings 容易但"为什么该忘"难自动判断)。

### 2. 图数据库(Knowledge Graph)

**代表方案**:Neo4j + LangChain(Neo4jGraph 作为共享记忆)、Camel(关系图记忆,Agent 间通过图谱传递上下文)。

**工作流**:Agent 产出 → 抽取实体+关系 → MERGE 到图谱;Agent 回忆 → 图谱查询 → 与当前任务相关的实体链路。

- **优势**:关系推理强("上次和这个客户合作的 Agent 是谁")、天然适合多跳推理、删除/更新粒度细(单个关系而非整个文档);
- **劣势**:语义检索需外加 embedding、Schema 设计是硬活(谁定义实体类型?Agent 自己来易冲突)、Cypher 对非结构化内容描述力弱。

### 3. 消息队列 / 事件日志(append-only log)

**代表方案**:Kafka/Pulsar + compacted topic、自建 append-only log(事件溯源)。

**工作流**:Agent 产出 → append 到 log;Agent 回忆 → replay 最近 N 条 → 提取相关记忆。

- **优势**:时序保证最强(完全有序、不可篡改)、一致性最简单(append-only 天然解决并发写)、审计友好;
- **劣势**:检索全靠"replay + 过滤"数据量大后低效、需外部索引层(常与向量库搭配)、遗忘=删 log 但审计就丢了。

### 选型决策表

| 场景 | 推荐方案 | 原因 |
| --- | --- | --- |
| 3-10 个 Agent,任务周期 < 1h | 向量 DB(Chroma/Qdrant) | 够用,部署简单 |
| 需要多跳推理 + 关系追溯 | 图 DB(Neo4j) | 关系查询是刚需 |
| 金融/合规/审计可追溯 | 事件日志(Kafka)+ 向量索引 | 不可篡改是硬约束 |
| 大规模生产级(50+ Agent) | 向量 DB(Milvus)+ 图 DB 混合 | 语义 + 关系双通道 |

## 原理:并发写的一致性取舍

### 为什么 Raft/Paxos 不是答案

锁只能保护"同一行/同一文档",保护不了"整个记忆池的全局一致性"。Raft(Leader 转发写请求→多数确认→提交)/ Paxos(更灵活但实现复杂)是重型武器——但 **Agent 系统通常托管在已有数据库上(Qdrant/Milvus/Neo4j),数据库自身已解决副本一致性**。Agent 层面临的一致性问题是**语义级**的:

> Agent A 和 Agent B 同时认为"本次任务的负责人是自己"——这不是 Raft 能解决的。

### 场景锁:乐观锁解决"语义冲突"

实战中更实用——不锁数据行,锁**语义条件**:

```python
def claim_task(task_id, agent_id):
    result = db.update(
        "UPDATE tasks SET assigned_to = ? WHERE id = ? AND assigned_to IS NULL",
        agent_id, task_id
    )
    if result.rowcount == 0:
        return "任务已被抢走"
    return "抢到任务！"
```

**`WHERE assigned_to IS NULL` 就是场景锁的核心——不是锁行,是锁条件。**

### CRDT(冲突自由复制数据类型):未来方向

如果两个 Agent 同时编辑同一段共享记忆,能不能不锁、不冲突、事后自动合并?CRDT 提供"最终一致性 + 无冲突"的数学保证——文本编辑场景有成熟实现(Yjs、Automerge),但 Agent 记忆场景仍属前沿:

- **优势**:无需中心化锁、容忍网络分区;
- **挑战**:Agent 的记忆不是纯文本,是 embedding + metadata + 关系——CRDT 怎么处理非结构化冲突合并?

## 原理:记忆分层与语义路由——别让共享池变成大锅乱炖

**最常见错误**:所有 Agent 把一切记忆往一个 vector store 里塞——情感安抚的"客户喜欢蓝色"和代码审查的"接口需幂等",混在同一向量空间互相污染。

### 三层记忆分级

| 层 | 生命周期 | 示例内容 | 存储 |
| --- | --- | --- | --- |
| 工作记忆 | 单次任务 | 当前对话状态、实时变量 | 上下文 |
| 短期记忆 | 单次会话 | 任务结论、重要发现 | 向量库(高热度) |
| 长期记忆 | 跨会话 | 技能经验、项目知识、用户画像 | 向量库/图库(低热度) |

### 语义路由(MetaGPT 的做法)

- **写时自动打标签**:`task_type`、`agent_role`、`project_id`;
- **读时向量检索 + 标签过滤**:只搜同项目/同类型的记忆。

> **写时打标签,读时过滤——简单到几乎零成本,效果远超裸查向量空间。**

## 实践 / 应用:群体智能涌现与遗忘维护

### 共享记忆的终极价值:群体智能

1. **Shared Replay Buffer(强化学习)**:DeepMind 多智能体 RL 研究发现,多个 Agent 共享一个 experience replay buffer 后,**训练效率提升 3-5 倍**——Agent A 踩过的坑,B 在同样状态下不会重蹈覆辙,共享记忆成了"群体第六感";
2. **crewAI 共享上下文**:Agent 间信息传递通过共享 Task 对象——每个 Agent 执行后把产出写回任务上下文,下一个 Agent 能读到串行链上的所有历史。**关键洞察:这不是"Agent 之间对话",而是"Agent 之间共享工作记忆"**——串行链上的记忆累积,让最后一个 Agent 拥有比第一个多得多的上下文。

### 群体智慧 ≠ 越多越好(副作用)

- **信息过载**:5 个 Agent 产出的记忆,第 6 个 Agent 检索 top-10 全是前 5 个的"噪音";
- **路径依赖**:第一个 Agent 的错误认知写入共享记忆 → 后续 Agent 全部继承偏见;
- **责任稀释**:共享记忆里的错误归谁?

### 遗忘与维护:谁给共享记忆"打扫房间"

单体记忆的遗忘策略(TTL、LRU、重要性加权)在共享池面临新问题:

> Agent A 的"临时期中计算过程"TTL 设为 10 分钟;但 Agent B 在第 9 分钟引用它,第 11 分钟还需要——记忆已被清理。

**Mem0 的做法**:记忆有 `expires_at` 字段;每次被检索命中**自动续期**(类似 Redis 的 volatile-lru + access 续期)。**建议:共享记忆的遗忘策略必须支持引用计数/访问续期,不能只有时间驱动——TTL 是起点,不是终点。**

## 实践 / 应用:选型速查与三个"不要"

| 如果系统... | 选型建议 |
| --- | --- |
| < 5 个 Agent,短期任务 | Chroma + 标签过滤,先跑起来 |
| 10+ Agent,需要关系查询 | Qdrant/Milvus + Neo4j 双通道 |
| 审计/合规硬约束 | Kafka append-only log + 外部向量索引 |
| 探索性前沿项目 | CRDT + 语义路由,跟踪社区进展 |

**三个"不要"**:

1. **不要把"共享"当成"全员全量可见"**——语义路由/权限控制在第一天就得设计;
2. **不要指望数据库自带的一致性协议解决"语义冲突"**——场景锁是 Agent 层必须自己写的;
3. **不要忽视遗忘**——共享记忆比单体记忆更需要打扫,因为"这是别人的记忆,我不好删"的心理会让垃圾越积越多。

## 总结

- **问题**:单体记忆的天花板是信息孤岛——共享记忆池让多 Agent 互读,但引入数据模型/一致性/检索/遗忘/权限五大工程问题;
- **三阵营**:向量库(语义强)/ 图数据库(关系强)/ 事件日志(时序审计强),按场景组合(50+ Agent 用向量+图混合);
- **一致性**:Raft/Paxos 解决不了语义冲突——**场景锁(锁条件不锁行)**是 Agent 层必须自己写的;CRDT 是前沿方向;
- **分层与路由**:工作/短期/长期三层分级 + 写时打标签、读时过滤的语义路由,避免大锅乱炖;
- **群体智能**:Shared Replay Buffer 训练效率 3-5 倍、crewAI 串行链记忆累积;副作用是信息过载/路径依赖/责任稀释;
- **遗忘**:TTL 是起点不是终点——必须支持引用计数/访问续期;
- **下一步**:对照站内 [Agent 记忆体系](agent-memory-systems.md)(单体记忆基础),或 [多智能体协作设计](agent-team-room-collaboration.md)(共享机制的另一面)。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/SiivT0gLN6mxKi97O5wvsg(系列第 12/15 期)
- 站内:[Agent 记忆体系](agent-memory-systems.md)(单体记忆:短期/长期/写入闸门/整合衰减)、[多智能体协作设计](agent-team-room-collaboration.md)(收件箱/文件锁协作)、[LLM 记忆综述](../09-agent-research/llm-memory-survey.md)(学术视角)、[TencentDB Agent Memory](../08-harness/agent-memory-plugin.md)(记忆插件)
