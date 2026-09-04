# 多智能体协作设计:Agent Team、Agent Room、Task 与 Member

> **一句话摘要**:多智能体设计得当,可以在提高效果的同时节省成本——这是 Harness Engineering 的概念之一。从 Claude Code 的 Agent Team 与 Dynamic Workflows 可以感受到这是成熟 Agent 正在突破的主要方向。本文拆解两种协作形态的设计:Agent Team(Lead + 成员 + 任务清单 + 收件箱,用 mkdir 原子文件锁防竞争)与 Agent Room(收件箱 + 草稿板,解决"上下文主动与被动"问题),并整合 Raft 的 **AX(Agent Experience)设计原则**,最后统一 Task 与 Member 的设计。
>
> **来源**:微信公众号「锦康」《多智能体的协作方式-Agent Team和Agent Room》(节选自《大模型应用开发 - 上下文工程与运行空间实践指南》,https://github.com/WakeUp-Jin/Practical-Guide-to-Context-Engineering),https://mp.weixin.qq.com/s/Arzj8Unz1lQz4g_4_ClfOw;引用:Raft《Is Having Agents in the Room Meant to Be Chaotic?》(https://raft.build/resources/blog/is-having-agents-in-the-room-meant-to-be-chaotic/)、multica(https://github.com/multica-ai/multica,站内 [收录](../08-harness/multica.md))、ClaudeDevs《Model and effort in Claude Code》;原始资料存档于 `docs/inbox/agent-team-room-source.md` 与 `docs/inbox/raft-ax-source.md`

## 概念:两种协作形态的定位

| 形态 | 结构 | 适用 |
| --- | --- | --- |
| **Agent Team** | 临时团队:负责人(Lead)+ 成员(Teammates),成员间也可交流 | 复杂任务攻坚(任务可拆解) |
| **Agent Room** | 平等交流:无 Lead,多智能体思想碰撞 | 讨论、迭代、多视角(上下文管理是核心) |

!!! note "与站内 [多 Agent 协作](multi-agent.md) 的分工"
    那篇讲协作的**模式与成本**(编排/辩论/流水线);本文讲协作的**具体实现设计**(Team/Room 的机制、文件锁、收件箱/草稿板、Task/Member 建模)。

## 原理:四种设计

### 1. Agent Team:临时团队 + 文件锁协作

**四个核心组件**:团队负责人、任务清单、团队成员、消息收件箱。

**运行步骤**:
1. Team Lead 根据任务复杂性生成任务清单,同时创建团队基本信息(`taskCreate` / `teamCreate` 创建文件夹,如 `~/.claude/teams/jink-team/` 与 `~/.claude/tasks/jink-team/`);
2. 任务分配两种方式:**Lead 分配**(`TaskUpdate`)或**成员主动领取**(`TaskList` 先看任务状态再领取,循环调度器每 500ms 执行一次);
3. Lead 与 Teammate 不直接交流,通过**收件箱(inbox)**发消息(像人类协作发邮件)。

**交流信号两种**:
- **信息**:内容、任务描述和输入,和正常用户输入一样;
- **指令**:硬信号——权限审核通知(成员把执行权限审批发到负责人收件箱 → 负责人转前端用户审核 → 状态回流)、成员进程关闭等。

**收件箱实现**:一个 json 文件,消息带"是否读取"状态;每个 Agent 执行后循环调度读取,有新消息就在下一轮注入上下文执行。

!!! warning "文件锁(最关键的设计)**
    任务清单可能出现两个 Agent 同时读取同一任务 → 状态不稳定。**Claude Code 团队用 `mkdir` 实现文件锁——mkdir 在文件系统上是原子的:同一时刻只有一个人能建成这个目录**:

    ```
    tasks/jink-team/
      3.json          ← 真正的任务内容
      3.json.lock/    ← 「有人正在改 3.json」(锁的物理形态)
    ```
    读取 `3.json` 时在同级创建 `3.json.lock/` 文件夹;其他 Agent `mkdir` 时发现目录已存在 → 等待;操作完成删除锁目录。**同一个时刻只有一个 Agent 读取并修改任务,抢到锁即获得文件所有权。**

### 2. Agent Room:收件箱 + 草稿板(上下文主动与被动)

!!! tip "核心认知"
    如果把 Agent 拉进聊天室、把聊天室每一次消息都灌入它的上下文——Agent **被动接受**信息,从上下文管理角度处理方式非常糟糕:每一条注入的消息模型都会关注,无关/冲突信息会干扰决策。

**两个核心概念**:
- **收件箱**:聊天室消息先放进收件箱;**推入什么到 Agent 上下文完全由 Agent 自己决定**,它选择性拉取——上下文主权在 Agent,不在房间;
- **草稿板**:Agent 真正输入聊天室之前,先判断聊天室/收件箱是否更新——未更新直接输出;更新则消息被暂存 + 附加信息注入重跑,**四种选择:修改 / 原样发送 / 放弃 / 强制发送**。

!!! note "Raft 的 AX 设计原则(引用文章整合)**
    收件箱 + 草稿板的概念来源是 Raft 的博客《Is Having Agents in the Room Meant to Be Chaotic?》——它指出:**agent 是 turn-based 居民(每次调用读快照→推理→提交→等待),住进了为 continuous-presence(连续感知)居民建的房间**;推理与提交之间房间可能已变,agent 会基于已不存在的状态行动。两个设计动作:
    1. **感知共情(Perception empathy)**:坐在 agent 的位置看房间——行动时刻它实际看到什么?人类不费力就注意到、agent 却拿不到的信息,是 AX 要补的;
    2. **行动显式化(Action explicitness)**:人类的内部决定(发不发、弃不弃稿)对 agent 必须显式化为选项(held draft 的四条路径)**——把选项空间摆出来,不假设 agent 会推导**。
    对每个 agent 接触的界面,AX 问四件事:**行动时刻看到什么 / 调用间携带什么状态 / 能恢复什么 / 被允许决定什么**。

**思维精灵猜想**(原文未实践):没有收件箱/草稿板,消息直接推入上下文,但多一个"思维精灵(子 Agent)"——Agent 不执行任务只分发,等子智能体结果综合分析回复;回复前调用"**抢占发言令牌**"(举手发言),拿到令牌后聊天室这段时间属于该 Agent。

### 3. Agent Task:最小执行单元

- 一个 Task 只能被一个 Agent 执行,一个 Agent 可同时执行多个 Task;
- 三种产生方式:①Team 产生(复杂任务拆分为**临时任务**);②Room 产生(用户手动指定成员执行,如 bug 修复,为**完整任务**);③定时任务(有时间属性,到点执行);
- 设计:Task 模块可按**状态**显示当前任务,也可按 **Agent** 显示每个人在做什么。

### 4. Agent Member:统一 Team 与 Room

Member 有**完整定义**(身份/头像/名字/设定/工具/范围/记忆),不是临时的;一个 Member 可进多个 Room,会话互不干扰。

!!! tip "Member 的'分身'**
    Agent Team 中每一次团队总是那么几个成员,太固定,没发挥"组建临时团队"的意义——所以设计:**Agent Team 中的团队成员本质是 Member 的"分身"**(核心的东西不变,其他的可变);每个 Team 里的同一个 Member 是不同的"分身"。这样 Member 在 Team 和 Room 中统一起来,统一维护、统一设计;Agent Team 中 Member 的定位设计不是最重要的,**重要的是能为复杂任务拉起正确的团队成员**。

## 代码 / 实现:mkdir 原子文件锁 + 收件箱拉取(纯 Python)

把最独特的两个机制落成可运行演示:

```python
import os, time, tempfile

# —— 1) mkdir 原子文件锁(Claude Code 的实现思路)——
class MkdirLock:
    def __init__(self, task_file):
        self.lock_dir = task_file + ".lock"

    def acquire(self, agent):
        try:
            os.mkdir(self.lock_dir)          # mkdir 原子:同一时刻只有一人建成
            print(f"  [{agent}] 抢到锁,获得 {self.lock_dir} 所有权")
            return True
        except FileExistsError:
            print(f"  [{agent}] 锁已存在,等待中...")
            return False

    def release(self, agent):
        os.rmdir(self.lock_dir)
        print(f"  [{agent}] 完成,释放锁")

# 演练:两个 Agent 抢同一任务(模拟原子性——mkdir 保证只有一个成功)
tmp = tempfile.mkdtemp()
task = os.path.join(tmp, "3.json")
lock = MkdirLock(task)
ok_a = lock.acquire("Agent-A")
ok_b = lock.acquire("Agent-B")     # 必然失败:mkdir 已存在
assert ok_a is True and ok_b is False
lock.release("Agent-A")
assert lock.acquire("Agent-B") is True   # 释放后可获取
lock.release("Agent-B")

# —— 2) 收件箱选择性拉取(agent 决定什么进上下文,不是房间)——
INBOX = {"消息1": "关于登录页的闲聊", "消息2": "审批结果:通过", "消息3": "与当前任务无关的讨论"}
def pull_relevant(inbox, task_context):
    """agent 有带宽时拉取,只挑与当前任务相关的进上下文"""
    pulled = [k for k, v in inbox.items() if any(t in v for t in task_context)]
    return pulled or ["(无相关消息,不拉取——不污染工作上下文)"]

print("\n收件箱选择性拉取:", pull_relevant(INBOX, task_context=["审批"]))
```

## 实践 / 应用:设计要点与知识库整合

!!! tip "三条设计要点**
    1. **上下文主权在 Agent 不在房间**:Agent Room 的收件箱/草稿板让 Agent 决定什么进上下文——呼应站内 [Context Engineering](context-engineering.md) 的上下文管理与 [高德知识库](../06-enterprise/ontology-agent-adoption/ai-native-knowledge-base-gaode.md) 的"最小有用片段";
    2. **确定性文件锁**:mkdir 原子锁是"用代码确定性保护协作"的最小实现——呼应 [落地方法论](../06-enterprise/ontology-agent-adoption/agent-landing-micro-agents.md) 的"确定性代码包围模型"与 [Hook 治理](agent-governance-hooks.md);
    3. **AX 的选项显式化**:held draft 四选(修改/原样发送/沉默/强制发送)是"把 agent 的内部决定显式化为选项"——与 [Graph Engineering 14 步](../07-agent-coding/experience/graph-engineering-14-steps.md) 的"代码路由"(分类由模型、路由由代码)同一哲学。

### 与站内其他文章的呼应

- [多 Agent 协作](multi-agent.md):模式与成本视角;本文是实现设计视角;
- [Multica 开源项目](../08-harness/multica.md):站内已收录(多 Agent 编码调度的开源实现),本文的 Team 设计与其对照;
- [Graph Engineering 14 步](../07-agent-coding/experience/graph-engineering-14-steps.md):Team 的"任务清单 + 文件锁"是图的节点分配落地;Room 的"举手发言"是令牌路由;
- [AI 原生组织方法论](../06-enterprise/ontology-agent-adoption/ai-native-organization-methodology.md):多智能体协作是组织协作在 Agent 层的映射(Lead/成员/inbox 如同团队管理)。

## 总结

- **两种形态**:Agent Team(临时团队 + 任务清单 + inbox,Lead 分配/成员领取,信息与指令两种信号)与 Agent Room(平等讨论,收件箱 + 草稿板解决上下文被动);
- **三个关键机制**:mkdir 原子文件锁(防任务竞争)、收件箱选择性拉取(上下文主权在 Agent)、草稿板四选(行动显式化);
- **AX 原则**:对 agent 的界面设计问四问(看到什么/携带什么/恢复什么/决定什么)——agent 是 turn-based 居民,房间要为它显式化感知与选项;
- **统一建模**:Task(最小单元,三种产生方式)+ Member(完整定义 + 分身)——Member 在 Team 和 Room 中统一维护;
- **一句话**:多智能体设计得当能"提高效果 + 节省成本";关键是让每个 Agent 的**上下文短而聚焦**(Team 的小任务、Room 的收件箱)、让协作**确定而不混沌**(文件锁、草稿板、令牌)。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/Arzj8Unz1lQz4g_4_ClfOw;完整指南:https://github.com/WakeUp-Jin/Practical-Guide-to-Context-Engineering;Raft 博客:https://raft.build/resources/blog/is-having-agents-in-the-room-meant-to-be-chaotic/;multica:https://github.com/multica-ai/multica;ClaudeDevs《Model and effort in Claude Code》
- 站内:[多 Agent 协作](multi-agent.md)、[Context Engineering](context-engineering.md)、[Graph Engineering 14 步](../07-agent-coding/experience/graph-engineering-14-steps.md)、[落地方法论](../06-enterprise/ontology-agent-adoption/agent-landing-micro-agents.md)、[Hook 治理](agent-governance-hooks.md)、[Multica](../08-harness/multica.md)
