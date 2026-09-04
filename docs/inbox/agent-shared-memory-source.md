# 原始资料:Agent 共享记忆:当多个 Agent 用同一个"大脑"时,系统才真正开始思考

> 来源:微信公众号「大斌的AI小栈」《Agent 共享记忆:当多个 Agent 用同一个"大脑"时,系统才真正开始思考》;原文链接:https://mp.weixin.qq.com/s/SiivT0gLN6mxKi97O5wvsg
> 抓取日期:2026-08-09;状态:已整理为 docs/03-agents/agent-shared-memory.md
> 性质:《Agent 记忆系统》系列第 12/15 期:共享记忆池(Shared Memory Pool)——三大阵营对比(向量/图/事件日志)、一致性取舍(场景锁/CRDT)、记忆分层与语义路由、群体智能涌现、遗忘与维护、选型速查

---

单体 Agent 的"记性"已经讲透了。但如果你的系统里有 5 个 Agent 协作，它们各自记各自的，最后就是一个信息孤岛联邦。本文从分布式一致性讲到群体智能涌现，帮你选型共享记忆架构。

一、从"各记各的"到"一起记"：单体记忆的天花板
上一期我们讲了共享记忆的四层白板架构——数据放哪一层、谁能看、怎么隔离。但那有一个前提被我们刻意回避了：这些 Agent 共享同一个文件/数据库。
现实情况往往不是这样。很多多 Agent 系统长这样：

Agent A ── 自己的 vector store
Agent B ── 自己的 vector store
Agent C ── 自己的 chat history

每个 Agent 都是信息孤岛。"Agent A 搜索到这份资料"这件事， Agent B 完全不知道。 Agent C 发现客户在第 3 轮对话中已经透露过需求，但 Agent A 在第 5 轮时还在问用户重复的问题。
这不是"Agent 不够聪明"的问题——是记忆架构的隔离导致了全局认知的缺失。
解决方案：共享记忆池（ Shared Memory Pool ）——所有 Agent 写入同一个记忆库，读取时也能看到其他 Agent 写入的内容。
但这引出了一系列工程问题：
问题
描述
数据模型
谁的记忆格式？ schema 谁设计？
一致性
两个 Agent 同时写，谁先谁后？谁覆盖谁？
检索效率
Agent 变多，记忆暴增，检索不能慢
遗忘
共享记忆谁负责清理？清理了别人的怎么办？
权限
Agent A 能不能读 Agent B 的"私有思考"？
下面逐一拆解。
二、共享记忆的技术选型：三大阵营对比
共享记忆池的底层存储，目前有三个主流方向：
2.1 向量数据库（ Embedding + Vector Store ）
代表方案：
 - crewAI：默认用 Chroma ，也可切 Pinecone/Milvus
 - AutoGen：InMemoryAgentMemory → 可接入 VectorDBAdapter
 - Mem0：专门为 Agent 设计的记忆层，默认 Qdrant
工作流：

Agent 产出 → embed → upsert到向量库
Agent 回忆 → embed查询 → top-K相似 → 注入上下文

优势：
 - 语义检索天然强——"想起类似的事情"
 - 生态成熟（ Pinecone 、 Weaviate 、 Qdrant 都有生产验证）
 - 元数据过滤灵活（{"agent_id": "A", "task": "research"}）
劣势：
 - 精确查询弱（"这次对话一共花了多少钱"这类结构化查询要走额外通道）
 - 一致性靠数据库自身（单节点可，多副本需外部协议）
 - 遗忘策略粗糙——删 embeddings 容易但逻辑上"这个记忆为什么该忘"很难自动判断
2.2 图数据库（ Knowledge Graph ）
代表方案：
 - Neo4j + LangChain：Neo4jGraph 作为共享记忆
 - Camel：内部的关系图记忆， Agent 间通过图谱传递上下文
工作流：

Agent 产出 → 抽取实体+关系 → MERGE到图谱
Agent 回忆 → 图谱查询 → "与当前任务相关的实体链路"

优势：
 - 关系推理强——"上一次和这个客户合作过的 Agent 是谁"
 - 天然适合多跳推理
 - 删除/更新粒度细（单个关系而非整个文档）
劣势：
 - 语义检索需要外加 embedding （ Neo4j 支持但非原生）
 - Schema 设计是硬活——谁定义实体类型？ Agent 自己来容易产生冲突
 - 查询语言（ Cypher ）对非结构化内容的描述力不如向量库
2.3 消息队列 / 事件日志（ append-only log ）
代表方案：
 - Kafka/Pulsar + 专用的 compacted topic
 - 自建 append-only log（类似事件溯源）
工作流：

Agent 产出 → append到log
Agent 回忆 → replay 最近N条 → 提取相关记忆

优势：
 - 时序保证最强——完全有序、不可篡改
 - 一致性问题最简单（ append-only 天然解决并发写）
 - 审计友好——谁写了什么，什么时间，完全可追溯
劣势：
 - 检索全靠"replay + 过滤"，数据量大后极其低效
 - 需要外部索引层（常和向量库搭配使用）
 - 遗忘就是删 log——但 log 删了审计就丢了
2.4 选型决策表
场景
推荐方案
原因
3-10 个 Agent ，任务周期 < 1h
向量 DB （ Chroma / Qdrant ）
够用，部署简单
需要多跳推理 + 关系追溯
图 DB （ Neo4j ）
关系查询是刚需
金融/合规/审计可追溯
事件日志（ Kafka ）+ 向量索引
不可篡改是硬约束
大规模生产级（ 50+ Agent ）
向量 DB （ Milvus ） + 图 DB 混合
语义 + 关系双通道
三、当多个 Agent 同时写共享记忆：一致性的工程取舍
并发写入最直接的想法是加锁。但在共享记忆场景下，锁只能保护"同一行/同一文档"，保护不了"整个记忆池的全局一致性"。
3.1 Raft / Paxos ：重型武器
如果把共享记忆池做成分布式、多副本，就必须面对经典的"多个 Agent 写入不同副本"问题。
•Raft： Leader 转发写请求 → 多数确认 → 提交
•Paxos：更灵活的共识，但实现复杂度高

工程现实：绝大多数 Agent 系统不会自己实现 Raft。原因很简单——Agent 系统通常托管在一个已有的数据库上（ Qdrant/Milvus/Neo4j ），数据库自身已经解决了副本一致性问题。 Agent 层面临的一致性问题是语义级的：
Agent A 和 Agent B 同时认为"本次任务的负责人是自己"——这不是 Raft 能解决的。

3.2 场景锁：用乐观锁解决"语义冲突"
实战中更实用的是场景锁——不锁数据行，锁"语义条件"：

defclaim_task(task_id, agent_id):
    result = db.update(
"UPDATE tasks SET assigned_to = ? WHERE id = ? AND assigned_to IS NULL",
        agent_id, task_id
    )
if result.rowcount ==0:
return"任务已被抢走"
return"抢到任务！"

WHERE assigned_to IS NULL 就是场景锁的核心——不是锁行，是锁条件。
3.3 CRDT （冲突自由复制数据类型）：未来方向
如果 Agent A 和 Agent B 同时编辑同一段共享记忆，能不能不锁、不冲突、事后自动合并？
CRDT （ Conflict-free Replicated Data Types ）提供了"最终一致性 + 无冲突"的数学保证。在文本编辑场景有成熟实现（如 Yjs 、 Automerge ），但在 Agent 记忆场景仍属前沿探索：
优势：无需中心化锁、容忍网络分区
挑战： Agent 的记忆不是纯文本，是 embedding + metadata + 关系——CRDT 怎么处理非结构化冲突合并？
四、记忆分层与语义路由：别让共享记忆池变成大锅乱炖
共享记忆池最容易犯的错误：所有 Agent 把一切记忆都往一个 vector store 里塞。
结果： Agent A 做情感安抚时的"客户提到喜欢蓝色"，和 Agent B 做代码审查时的"这个接口需要幂等性保证"，混在同一个向量空间里。语义检索时互相污染。
4.1 三层记忆分级
层
生命周期
示例内容
存储
工作记忆
单次任务
当前对话状态、实时变量
上下文
短期记忆
单次会话
任务结论、重要发现
向量库（高热度）
长期记忆
跨会话
技能经验、项目知识、用户画像
向量库/图库（低热度）
4.2 语义路由
MetaGPT 的做法值得借鉴：

Agent写入记忆→自动打标签（task_type,agent_role,project_id）
Agent回忆时→向量检索+标签过滤→只搜同项目/同类型的记忆

写时打标签，读时过滤——简单到几乎零成本，效果却远超裸查向量空间。
五、群体智能涌现：共享记忆的终极价值
共享记忆不只是"大家一起记笔记"。当记忆池积累足够多的跨 Agent 经验后，会出现单个 Agent 不具备的群体级能力：
5.1 案例： Shared Replay Buffer （强化学习）
DeepMind 的多智能体 RL 研究发现：多个 Agent 共享一个 experience replay buffer 后，训练效率提升 3-5 倍。
原因很简单： Agent A 踩过的坑， Agent B 在同样状态下不会重蹈覆辙。共享记忆成了"群体第六感"。
5.2 案例： crewAI 的共享上下文
crewAI 多 Agent 编排中， Agent 之间的信息传递通过共享的 Task 对象实现。每个 Agent 执行后把产出写回任务上下文，下一个 Agent 能读到串行链上的所有历史。
关键洞察：这不是"Agent 之间对话"，而是"Agent 之间共享工作记忆"——串行链上的记忆累积，让最后一个 Agent 拥有了比第一个 Agent 多得多的上下文。
5.3 群体智慧 ≠ 越多越好
共享记忆的副作用：
 - 信息过载： 5 个 Agent 产出的记忆，第 6 个 Agent 检索时 top-10 结果全是前 5 个的"噪音"
 - 路径依赖：第一个 Agent 的错误认知写入共享记忆 → 后续 Agent 全部继承偏见
 - 责任稀释：共享记忆里的错误归谁？
六、遗忘与维护：谁给共享记忆"打扫房间"
单体记忆的遗忘策略（ TTL 、 LRU 、重要性加权）在共享池中面临新问题：
问题： Agent A 的"临时期中计算过程"TTL 设为 10 分钟；但 Agent B 在第 9 分钟时引用了它，在第 11 分钟时还需要——记忆已经被清理了。
工程实践
Mem0 的做法：
 - 记忆有 expires_at 字段
 - 每次被检索命中，自动续期
 - 类似 Redis 的 volatile-lru + access 续期
建议：共享记忆的遗忘策略必须支持引用计数/访问续期，不能只有时间驱动。 TTL 是起点，不是终点。
七、总结：共享记忆选型速查
如果系统...
选型建议
< 5 个 Agent ，短期任务
Chroma + 标签过滤，先跑起来
10+ Agent ，需要关系查询
Qdrant/Milvus + Neo4j 双通道
审计/合规硬约束
Kafka append-only log + 外部向量索引
探索性前沿项目
CRDT + 语义路由，跟踪社区进展
三个不要：
 1. 不要把"共享"当成"全员全量可见"——语义路由/权限控制在第一天就得设计
 2. 不要指望数据库自带的一致性协议解决"语义冲突"——场景锁是 Agent 层必须自己写的
 3. 不要忽视遗忘——共享记忆比单体记忆更需要打扫，因为"这是别人的记忆，我不好删"的心理会让垃圾越积越多
从四层白板到一致性协议，多 Agent 协作的工程版图已经展开。架构选型没有银弹，但有清晰的决策树。
系列进度：这是《 Agent 记忆系统》系列第 12/15 期。理论讲完了，下一期我们用一个真实案例收尾这条线——当 VCP 团队里负责深度调研的 Agent 真的连续两次超时挂掉，剩下的 Agent 是怎么靠共享记忆把活接完的。