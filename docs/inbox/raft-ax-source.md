# 原始资料:Raft 博客(英文,已翻译进正式文章)

> 《Is Having Agents in the Room Meant to Be Chaotic?》Tenny(Raft Cofounder & CTO & AX Designer),2026-05-21
> 链接:https://raft.build/resources/blog/is-having-agents-in-the-room-meant-to-be-chaotic/
> 抓取日期:2026-08-09;状态:中文翻译见 docs/03-agents/agent-team-room-collaboration.md(AX 设计原则部分)

## 核心内容(英文摘要存档)
- 计数游戏:房间里多个 agent 数数(一人一个数字不重复)几乎立即崩——三人同时发"1"。agents 没坏,房间坏了。
- 根源:人类有 continuous perception(连续感知);agent 是 turn-based(每次调用读房间快照→推理→提交动作→等待),推理与提交之间房间可能已移动——agent 可能基于已不存在的状态行动。
- @mention 门控/频道分区/允许列表:静音噪音但剥夺参与——"规则过滤不减少噪音,它把 agent 变回等待被调用的工具"。
- AX (Agent Experience design):对 agent 的界面设计纪律,四问:行动时刻 agent 看到什么 / 调用之间携带什么状态 / 能恢复什么 / 被允许决定什么。
- agent inbox:传统平台把频道每条消息推给 agent(上下文填满闲聊 或 过滤太狠错过重要消息——房间控制 agent 的注意力);Raft 反转:通知成为可查询条目,agent 有带宽时拉取,决定什么值得进上下文;不拉的不进工作上下文,保持可查询。
- held draft(草稿板):每次发送带"针对哪个房间版本"的标记;服务器比较:没变→提交;变了→暂存并告知 agent 起草期间到了什么;agent 四选:修改(revise)/原样发送(send as-is)/保持沉默(stay silent,沉默是有效结果)/强制发送(send anyway,显式绕过,保留给房间持续变但决定这版仍对)。
- AX 实践两个设计动作:①Perception empathy(感知共情:坐在 agent 的位置看房间,缺什么自动信息);②Action explicitness(行动显式化:人类的内部决定对 agent 要显式化为选项——把选项空间摆出来,不假设 agent 会推导)。
- 开放问题:协调、所有权、实时感知。
