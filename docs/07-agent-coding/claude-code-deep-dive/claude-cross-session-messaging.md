# Claude Code Cross-session Messaging:多个 Session 如何直接「对话」

> **一句话摘要**:Anthropic 给 Claude Code 加的实验性能力——**跨 Session 消息通信(Cross-session messaging)**:同时运行的多个 Claude Code Session 直接互发消息。一条消息背后是完整链路:**寻址(磁盘注册 + Inbox Socket)→ 投递(本地 Socket / 远程 Server)→ 进入模型(Idle 触发新 Turn / Active 在 Tool 调用间读取)→ 权限继承(User Message vs Peer Session Message 区分)**。它不是共享 Context,而是"Session 保持独立,任务产生依赖时显式同步必要状态"。
>
> **来源**:微信公众号「AI科技评论」《深度拆解 Claude 新功能:多个 Session 如何实现直接「对话」?》(郑佳美),https://mp.weixin.qq.com/s/OOjo-VCssFismoaIReRxMg;官方文档 https://code.claude.com/docs/en/cross-session-messaging;原始资料存档于 `docs/inbox/claude-cross-session-source.md`

## 概念:不是 Context,是一条消息

**场景**:同时开 3 个 Claude Code Session——数据库、后端 API、测试。以前三者并行工作但互不知情:数据库 Session 改完 Schema,要开发者切到另一个终端把变化告诉后端 Session。Cross-session messaging 让这一步由 Claude 直接完成——数据库 Session 通知后端哪些字段变了,测试 Session 发现接口回归把结果发给正在改相关代码的 Session。

!!! important "关键:没有改变 Session 隔离"
    Session A 给 B 发消息时,**不会**把自己的 Conversation History、读过的文件或整个 Context Window 一起发过去。官方规定跨 Session 传递的是**文本**。需要迁移完整对话/上下文时应 Resume 原 Session,而非用 Cross-session messaging。

**设计思想**:传递的是**任务结果和依赖信息,不是完整工作记忆**——数据库 Session 读了几十个文件、试过几套方案,后端 Session 不需要知道前面的分析过程,只需要最终变化及对 API 的影响。好处:不同任务的局部信息不会不断涌入其他 Session,只有变化开始影响其他任务时才跨过 Session 边界。

> 它与"所有 Agent 共享一个大 Context"是两种不同思路:**让 Session 保持独立,再在任务产生依赖时显式同步必要状态**。

## 原理:一条消息的完整路径

### 第一步:先找到另一个 Session(寻址)

- 每个支持该能力的本地 Session 把相关信息**注册到磁盘**,并绑定一个 **Inbox Socket**;
- Claude 通过 `ListAgents` 查找当前能联系的 Session,再通过 `SendMessage` 发给指定目标——用户不需要操作内部工具,只需告诉 Claude 想联系哪个 Session,或让它在任务产生依赖时主动通知;
- **Session 名字参与寻址**:按名字找目标;名字重复时系统加短标识区分,同时显示 Working Directory 帮助判断;
- **本地消息**直接通过目标 Session 的 Socket 传递,不经 Anthropic Server;**远程**(另一台机器 / Claude Code Web)才通过 Server 和 Remote Control 通信。

**本地通信的边界**:发现依赖磁盘注册信息 + Socket 可达性 + OS 权限——两个 Claude 即使同一台电脑,只要文件系统隔离(Host vs 独立 Container)就可能互相发现不了;同一 Container 内可正常通信;共享服务器上的其他 OS User 无法访问你的 Session。

### 第二步:信息送达后(进入模型)

消息送进 Inbox 后,由 Runtime 决定**何时交给模型**:

- **不立刻中断正在运行的 Tool**;
- 目标 Session **Idle** 时,消息可触发一个新 Turn;
- 目标 **Active Turn** 中,消息先等待,在**两个 Tool Call 之间**被读取。

**原因**:Claude 可能在写文件/跑测试/执行 Migration,如果外部消息任意时间强行改变当前动作,容易出现"工具只执行一部分,Agent 已按新信息重新规划"。**消息影响的是接下来的决策,不抢占正在进行的操作**。

**接入 Agentic Loop**:这使消息成为**异步输入来源**——而且入口不只给其他 Claude Session 用:当前 Session 的 Messaging Socket 暴露给 Hook 和 Bash 启动的 Child Process,长后台任务结束后可主动把结果发回 Session,无需 Claude 轮询。

**不是可靠消息队列**:

- 重复消息受限流(短时间相同内容可能被丢弃);
- 已接受未读取的消息每 Session 最多保留 **50 条**;Hold 状态消息用另一套缓冲区,最多 **100 条**;
- 适合发送状态变化、任务结果、协作通知;**必须长期保存的事实仍应记录在 Git、文件、数据库等持久化系统**。

### 第三步:权限如何继承

**明确区分 User Message 与 Peer Session Message**:

- 另一个 Session 发来的内容**不是用户授权**——不能替用户批准 Permission Prompt,不能通过消息要求修改 Permission Settings、CLAUDE.md 或配置;消息里即使含 Claude Code Command 也只当普通文本;
- 例:Session A 请求 B 删文件,若该操作在 B 中需授权,**原 Permission Prompt 仍会出现**;
- **禁止权限绕过**:若某操作已在当前 Session 被 Permission System 拒绝,Claude **不应转而请求另一个 Session 替自己执行**——否则低权限 Session 可不断转交高权限 Session,权限边界失效;
- **Inbound Control**:接收端可把跨 Session 消息设为 `accept`(交给 Claude)/ `hold`(暂留等待确认)/ `refuse`(直接丢弃);
- 无显式配置时,参考发送方/接收方当前 **Permission Mode**——能绕过普通 Permission Prompt 的 Session 不会被当作普通消息来源;接收端权限较高时外部消息可能先进 Hold。

> **两道判断**:先决定消息能不能进入 Claude(发现/投递/Inbound Control),再决定 Claude 根据消息准备执行的动作有没有权限(Execution Permission)。

## 实践 / 应用:在 Claude Code 能力中的定位

Cross-session messaging 与既有能力的分工:

| 能力 | 解决的问题 |
| --- | --- |
| Resume Session | 继续原来的 Conversation 和 Context |
| Agent Teams | 创建和管理一组协作 Agent |
| Worktree | 隔离不同 Session 的代码修改 |
| Remote Control | 从其他设备继续控制 Session |
| **Cross-session messaging** | **几个独立运行的 Session 在任务产生依赖后,把必要信息传给对方** |

**工程意义**:以前多开 Session 主要解决并行,但开发者仍要观察各终端进度并在人和 Session 之间反复转述任务状态;现在接口变化、测试结果、Migration 完成可直接送到受影响的 Session。**它没有把多个 Claude 合成一个 Agent,而是在原有 Context、工作目录和权限边界之外补上一层通信能力。**

> **更广的视角**:当 Agent 数量增加,问题从"单个 Agent 能做多少事"变成"这些 Agent 之间能不能稳定地交换状态、处理依赖、完成交接"。这种"不同 Agent 不需要共享越来越大的 Context,通过明确通信接口协同"的设计,是另一种多 Agent 思路——任务、状态和权限被拆开后,系统反而更容易扩展。

## 总结

- **本质**:跨 Session 消息通信——传递文本(任务结果+依赖信息),不共享 Context/工作记忆;
- **寻址**:磁盘注册 + Inbox Socket,`ListAgents`/`SendMessage`;名字+短标识+Working Directory;本地走 Socket、远程走 Server;
- **时序**:不抢占正在执行的 Tool——Idle 触发新 Turn,Active 在两个 Tool Call 间读取;接入 Agentic Loop 成为异步输入;
- **权限**:Peer Message ≠ 用户授权;禁止低权限转交高权限绕过;accept/hold/refuse 三道 Inbound Control;
- **定位**:在 Context/工作目录/权限边界外补一层通信能力——"Session 独立 + 依赖时显式同步";
- **下一步**:跨 Session 通信设计提炼见 [03-agents agent 设计](../../03-agents/agent-collaboration-messaging.md),或对比站内 [Worktree 与 Agent Teams](claude-worktree-teams.md)、[Dynamic Workflows](claude-workflows.md)。

## 延伸阅读

- 官方文档:https://code.claude.com/docs/en/cross-session-messaging
- 原文:https://mp.weixin.qq.com/s/OOjo-VCssFismoaIReRxMg
- 站内:[Claude Code 深度解析子主题](index.md)、[Claude Code Worktree 与 Agent Teams](claude-worktree-teams.md)、[Claude Code Dynamic Workflows](claude-workflows.md)、[Claude Code 源码解析](claude-code-harness-analysis.md)(任务/团队章节)、[多智能体协作设计](../../03-agents/agent-team-room-collaboration.md)
