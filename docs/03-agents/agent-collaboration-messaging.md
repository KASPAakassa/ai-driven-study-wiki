# Agent Session 通信设计:从 Claude Cross-session Messaging 提炼的异步协作范式

> **一句话摘要**:当多个 Agent/Session 需要协作,有两种思路——共享一个大 Context,或让 Session 保持独立、在任务产生依赖时显式同步必要状态。Claude Code 的 **Cross-session messaging** 是后者的完整参考实现,可提炼为通用设计范式:**寻址(注册 + 通信端点)→ 异步投递(不抢占执行)→ 进入决策循环 → 权限继承与隔离**。本文从 Agent 设计角度拆解这套方案,与站内的文件锁/收件箱范式对照。
>
> **来源**:提炼自 Claude Code Cross-session messaging 技术拆解(「AI科技评论」,https://mp.weixin.qq.com/s/OOjo-VCssFismoaIReRxMg;官方文档 https://code.claude.com/docs/en/cross-session-messaging);Claude 侧专文见 [claude-code-deep-dive](../07-agent-coding/claude-code-deep-dive/claude-cross-session-messaging.md)

## 概念:两种多 Agent 协作思路

多 Agent 协作面对的核心矛盾:**共享 Context vs 独立 + 显式同步**。

| | 共享大 Context | 独立 Session + 显式消息通信 |
| --- | --- | --- |
| 信息传递 | 所有 Agent 看到全部上下文 | 只传递任务结果和依赖信息 |
| 扩展性 | Context 无限膨胀,信息污染 | 局部信息留在局部,边界清晰 |
| 典型代表 | 单 Agent 多轮 / 共享 Scratchpad | **Claude Cross-session messaging**、Agent Team 收件箱 |
| 适用 | 任务耦合紧密、规模小 | 任务独立并行、规模大、依赖显式 |

**核心洞察(Claude 的设计取舍)**:Session A 给 B 发消息时,不会发送 Conversation History/读过的文件/整个 Context Window——**传递的是文本(任务结果 + 依赖信息),不是完整工作记忆**。需要完整上下文时应该 Resume 原 Session。不同任务的局部信息不会不断涌入其他 Session,只有变化开始影响其他任务时才跨过 Session 边界。

> **一句话**:让 Session 保持独立,再在任务产生依赖时显式同步必要状态——任务、状态和权限被拆开后,系统反而更容易扩展。

## 原理:四个设计环节

### 1. 寻址:注册 + 通信端点

每个参与协作的 Session 需要**可被发现**:

- 把相关信息**注册到共享介质**(Claude 用磁盘),并绑定一个**通信端点**(Claude 用 Inbox Socket);
- 提供**查找与发送原语**(Claude 用 `ListAgents` / `SendMessage`);发起方不用操作内部工具,只要表达意图("联系后端 Session"或"依赖时主动通知");
- **名字参与寻址**:按名字找目标;重名加短标识区分,显示 Working Directory 帮助判断上下文;
- **通信边界**:本地走端点直连,远程走中心服务(Claude:本机 Socket 直传,远程经 Server + Remote Control);发现依赖注册信息可见性 + 端点可达性 + 权限。

### 2. 异步投递:不抢占执行

消息进入接收方后,由 Runtime 决定**何时交给模型**——这是设计的关键:

- **不立刻中断正在执行的 Tool**;
- 接收方 **Idle** → 消息触发新 Turn;
- 接收方 **Active** → 消息等待,在**两个 Tool Call 之间**被读取。

**原因**:Agent 可能在写文件/跑测试/执行长任务,若外部消息任意时间强行改变当前动作,会出现"工具只执行一部分,Agent 已按新信息重新规划"。**消息影响的是接下来的决策,不抢占正在进行的操作**。

**接入决策循环**:消息成为**异步输入来源**——不只 Agent 间可用,后台任务/子进程也可在完成后主动回传结果,无需轮询。

**可靠性边界**(Claude 的量化):不是可靠消息队列——重复消息受限流丢弃;未读消息每 Session 上限 50 条(Hold 缓冲 100 条)。**适合状态变化/任务结果/协作通知;必须长期保存的事实应写入 Git/文件/数据库等持久化系统**。

### 3. 进入决策:两道判断

接收方收到消息后有两层判断:

1. **消息能不能进入 Claude**(发现/投递/Inbound Control);
2. **Claude 根据消息准备执行的动作有没有权限**(Execution Permission)。

### 4. 权限继承与隔离

这是最容易被忽视、也最重要的设计:

- **区分消息来源**:用户消息 vs 对等(peer)消息。Claude 明确:Peer Session Message **不是用户授权**——不能替用户批准权限弹窗、不能改配置;消息里的命令只当普通文本;
- **禁止权限绕过**:某操作已在当前 Session 被权限系统拒绝,不应转而请求另一个权限更高的 Session 代执行——否则低权限 Agent 可不断转交高权限 Agent,权限边界失效;
- **Inbound Control**:接收端可设置 `accept`(交给模型)/ `hold`(暂留待确认)/ `refuse`(丢弃);无配置时参考双方权限模式。

!!! danger "权限边界失效场景"
    如果多个 Session 权限不同,且允许"被拒操作转交他人执行",低权限 Session 就能借高权限 Session 完成自己不能做的事——**权限模型必须随消息一起传递并独立校验,不能信任消息内容本身**。

## 代码 / 实现:消息链路的抽象示意

```python
# Cross-session messaging 设计模式的抽象(概念示意,非 Claude 实现)
class SessionMessaging:
    """四个设计环节的抽象"""

    # 1. 寻址:注册 + 端点
    def register(self, name, working_dir, socket): ...
    def list_agents(self) -> list[SessionInfo]: ...      # ListAgents
    def send_message(self, target: str, text: str): ...  # SendMessage

    # 2. 异步投递:入队,不抢占
    def deliver(self, msg):
        if target.idle:
            target.start_new_turn(msg)      # Idle -> 新 Turn
        else:
            target.inbox.enqueue(msg)       # Active -> Tool 调用间读取

    # 3. 进入决策:两道判断
    def on_receive(self, msg):
        if not self.inbound_control(msg):   # accept/hold/refuse
            return DROP
        return self.decision_loop(msg)      # 进入决策循环

    # 4. 权限:来源区分 + 独立校验
    def authorize(self, action, msg):
        assert msg.kind != USER          # Peer 消息 ≠ 用户授权
        if self.permission_denied(action):  # 被拒操作
            raise Forbidden("不得转交高权限 Session 代执行")
        return self.permission_system.check(action)
```

## 实践 / 应用:与站内协作范式的对照

### 与文件锁/收件箱范式的区别

| 维度 | 文件锁 + 收件箱(Agent Team) | 消息级异步通信(Cross-session) |
| --- | --- | --- |
| 通信介质 | 文件系统(json 收件箱、mkdir 原子锁) | 内存/磁盘注册 + Socket 消息 |
| 时序 | 循环调度读取,下一轮注入 | Idle 触发 / Tool 调用间读取 |
| 可靠性 | 文件天然持久 | 有上限非可靠,需持久化兜底 |
| 权限 | 靠文件系统权限 | 显式消息来源区分 + 权限独立校验 |
| 适用 | 紧耦合、同仓库 | 松耦合、跨目录/跨任务 |

两者互补:**Agent Team 的收件箱**解决"消息怎么进上下文"(文件 + 轮询),**Cross-session messaging** 解决"消息怎么到达 + 权限怎么隔离"(寻址 + Socket + 权限)。

### 设计清单(可复用到自己的多 Agent 系统)

1. **消息最小化**:只传任务结果/依赖信息,不传完整工作记忆(需要完整上下文就迁移 Session);
2. **显式寻址**:注册 + 通信端点 + 查找/发送原语;名字 + 工作目录可辨;
3. **异步不抢占**:消息只在决策边界(Idle/工具调用间)进入,绝不打断执行中的动作;
4. **权限随消息独立校验**:区分用户消息与对等消息;被拒操作禁止转交他人执行;接收端有 accept/hold/refuse 控制;
5. **可靠性边界明确**:非可靠队列——状态/通知类可发,长期事实进持久化存储;
6. **扩展性**:任务/状态/权限拆开,Agent 数量增长时系统仍可扩展。

## 总结

- **范式**:独立 Session + 显式消息通信,优于"共享大 Context"(局部信息不污染、边界清晰、易扩展);
- **四环节**:寻址(注册+端点+查找原语)、异步投递(不抢占执行,决策边界进入)、进入决策(两道判断)、权限继承(消息来源区分+独立校验+禁止转交绕过);
- **可靠性**:非可靠队列,状态/通知用消息,长期事实用持久化;
- **与站内**:与 [多智能体协作设计](agent-team-room-collaboration.md)(文件锁/收件箱范式)互补;Claude 侧细节见 [Cross-session messaging 专文](../07-agent-coding/claude-code-deep-dive/claude-cross-session-messaging.md);
- **下一步**:对比 [多 Agent 协作](multi-agent.md)(模式与成本)、[Subagent 上下文隔离](subagent-isolation.md)(隔离设计)。

## 延伸阅读

- 官方文档:https://code.claude.com/docs/en/cross-session-messaging;原文:https://mp.weixin.qq.com/s/OOjo-VCssFismoaIReRxMg
- 站内:[Claude Code Cross-session Messaging 专文](../07-agent-coding/claude-code-deep-dive/claude-cross-session-messaging.md)、[多智能体协作设计](agent-team-room-collaboration.md)(文件锁/收件箱对照)、[多 Agent 协作](multi-agent.md)、[Subagent 上下文隔离](subagent-isolation.md)、[Agent 生产架构](agent-production-architecture.md)(权限分层)
