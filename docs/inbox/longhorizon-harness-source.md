> 原文存档:微信文章《LongHorizon-Harness 深度剖析:长程 Agent 的核心不是更长上下文,而是让任务状态脱离上下文》(公众号:SOTA AI研报)
> 原始链接:https://mp.weixin.qq.com/s/KalxQye81xn3uFCYwy5SfQ
> 抓取日期:2026-08-11(手机 UA curl,避开微信环境验证)
> 对应论文:LongHorizon-Harness: Advancing Long-Horizon Agents for Real-World Tasks(arXiv:2608.01964)
> 开源项目:https://github.com/AMAP-ML/LongHorizon-Harness
> 用途:整理收件箱素材,正文原样保留供追溯。

---



# LongHorizon-Harness 深度剖析：长程 Agent 的核心不是更长上下文，而是让任务状态脱离上下文

作者：SOTA AI

从 Manage-Execute-Audit、外置任务状态、独立审计、能力边界、AgentAdapter 与跨基准结果，拆解 LongHorizon-Harness 如何把长程执行改造成可核验的状态机。

长程 Agent 失败时，表面现象常常是“模型忘了前面做过什么”。更深一层的问题是：执行轨迹、任务状态和完成判定被塞进同一段不断膨胀的上下文。Agent 一边修改环境，一边根据自己的叙述判断是否成功；一旦错误判断写进后续推理的前提，局部失误会被放大为全局偏航。

LongHorizon-Harness 提出了一种更接近控制系统而非长对话的解法：将长程执行重述为**任务状态管理**。每轮由 Manager 从外置状态构造一个有限的子任务契约，Executor 在新鲜且有预算上限的上下文中执行，Auditor 用只读权限独立检查环境。只有审计得到的事实，才可以推动持久状态进入下一轮。

这看似只是多了一个审核 Agent，实则改变了系统的信任边界：执行报告不再等于事实；上下文不再等于记忆；完成也不再是执行者的自我声明。本文以该论文披露的实现与实验为边界，分析它解决了什么、成本在哪里，以及如何将其转化为生产级 Agent 的运行时架构。

![LongHorizon-Harness 的 MEA 审计状态控制环](https://mmbiz.qpic.cn/sz_mmbiz_png/0WtFw2LmfO8yyeEXeElCmqgZia8PmMt1ZMqb4mPZCicgxAA5fYGM0GerztMOOswCWibTqScGicZYQsCia4tHJQkfX04nXL0qbJXQjBTzr7x6jUBE/640?from=appmsg)


连续 Agent loop 通常把三类性质完全不同的信息混在历史消息里：

• **执行轨迹。** 点击、命令、报错、尝试、局部推理和中间观察。它对当前动作有用，但长度增长最快，也最容易带入无关噪声。

• **任务状态。** 原始目标、尚未满足的需求、已生成的工件、已确认的环境事实、阻塞项与依赖关系。它必须短、小、结构化，并在任意回合都可被重新读取。

• **完成证据。** 真实环境中可观察的文件、界面、测试结果、进程状态、日志与元数据。它回答的不是“Agent 说自己做了什么”，而是“系统现在确实处于什么状态”。

当三者共享同一个滚动上下文，会产生三个结构性故障。

第一，**context rot**。旧操作的细节淹没在后续观察与推理中，模型虽未真正遗忘，却越来越难检索并正确使用关键前提。第二，**状态漂移**。执行者把“我已经改了文件”或“看起来像完成了”当作事实，后续计划便建立在未经验证的状态上。第三，**评估与行动耦合**。同一个策略既负责改变环境又负责宣称满足验收条件，缺乏独立制衡。

这也是为什么单纯增加上下文窗口不能根治长程可靠性。更大的窗口扩大了可携带的轨迹，却没有规定哪些记忆可信、哪种观察可以升级为状态、失败后应从哪里恢复。LongHorizon-Harness 的核心是把这些判断变成系统协议，而不是要求模型在提示词中“更认真一点”。

## 二、MEA：把一次 Agent 回合做成受审计的状态转换

论文将一项长期任务写成重复的 Manage-Execute-Audit（MEA）回合。记第 `i` 轮开始时的任务状态为 `S_i`，环境状态为 `e_i`：

```
Manager:  (S_i, audit history, goal) -> subtask contract c_i
Executor: (S_i, c_i, bounded fresh context, e_i) -> e_(i+1), execution report o_i
Auditor:  (S_i, c_i, o_i, read-only inspection of e_(i+1)) -> audit report v_i
Manager:  (S_i, v_i, goal) -> S_(i+1), next decision
```

关键不在于这个顺序本身，而在于状态提交规则：`o_i` 是执行者的主张，`v_i` 才是可用于更新 `S_(i+1)` 的环境证据。换句话说，系统把“执行成功”从一个语言判断转换成一个需要外部读证的提交条件。

### 1. Manager：持有状态，但不接触环境

Manager 拥有原始任务、当前任务状态和累计审计报告，却没有 GUI、CLI 或文件系统权限。这个限制非常关键：如果 Manager 能直接查看环境，它就可能绕过审计，用未校验的观察污染状态。

论文中的状态至少包含三类结构化记录：`requirement` 表示目标或约束，`artifact` 表示已创建或修改的产物，`fact` 表示后续执行需要的环境事实。每个记录标记为 `completed`、`pending`、`blocked` 或 `untrusted`，并保存支持它的审计证据引用。

Manager 的下一步不是泛泛地产生 plan，而是构造一个**子任务契约**：即时目标、验收条件、边界约束、依赖项，以及对本轮必要的历史证据。它可输出 `execute`、`done`、`blocked` 或 `ask`。因此，“请用户补充信息/授权”与“模型已无法继续”成为显式状态，而不是藏在长回复里的模糊失败。

### 2. Executor：只完成一个有限的环境转换

Executor 是唯一有意修改任务环境的角色。它会收到原始目标、当前状态、当前契约和契约引用的少量审计记录；此前回合的原始聊天、工具轨迹和内部推理不会传入。一次执行结束后，原始轨迹被丢弃，留下的只是执行报告 `o_i`。

这不是“无记忆 Agent”，而是**选择性、可证明的记忆**。新鲜上下文让 Executor 不必背负已经完成或已经失败的细节，只聚焦一个可验证的状态变化。Manager 通过契约决定必须携带什么，避免将“上下文压缩”交给模型的临场判断。

论文还把环境能力分为 GUI 与 CLI 两类：前者处理截图、点击、滚动、输入等界面状态转换；后者处理 shell、文件编辑、测试、进程和工作区状态。选择哪个 Executor 是 Manager 对契约的路由决策，而不是让一个全权限会话在所有工具间任意游走。

### 3. Auditor：只读不是形式约束，而是完整性边界

Auditor 从新鲜上下文开始，不拿到 Executor 的原始轨迹和内部推理。它可以读取执行报告来定位文件、窗口、日志或工件，但完成与否必须由环境检查得出，并与契约的验收条件、边界约束逐项对照。

论文要求 Auditor 只读：不得创建、编辑、覆盖、移动或删除受保护产物，也不得执行会改变被检查结果的命令或 GUI 操作。Harness 在审计期监控任务相关的工作区与工件；一旦发生写入，报告会被标为 integrity violation，不能支持“已完成”的状态记录。

审计报告包含三组结论：
维度可取状态对持久状态的意义Completion`complete` / `incomplete` / `blocked`当前契约的验收项是否真的满足Integrity`clean` / `suspect` / `violation`审计过程和工件来源是否可信State delta已证实事实、证据、剩余缺口Manager 在下轮可采纳的状态增量

因此 Auditor 不是“再让一个模型评一次分”。它是一条能力受限的独立读路径：执行者负责写，审计者负责读，Manager 负责把经过证明的读结果写入任务账本。这正是分布式系统中 command / query separation 与 commit gate 在 Agent 运行时里的对应物。

## 三、真正的记忆载体是审计报告，而不是压缩后的对话

MEA 最强的一条约束是：跨回合持久化的不是 Executor 的完整输出，而是任务状态及其支持性审计报告。这带来三个直接效果。

**第一，失败变成可恢复状态。** 一个 GUI 操作卡住、一个命令被拒绝，不能再只作为长轨迹里的失败片段。Auditor 可把“交互未响应”“某文件不存在”“验收项 X 尚未满足”记录为 `blocked` 或 `pending` 的事实；下一轮 Manager 从这些事实重新选路，而非让同一会话反复重试旧动作。

**第二，先后顺序可以被约束。** 一些任务要求在修复前收集证据，或在修改后保留特定元数据。只要这些要求是状态中的 `requirement`，Manager 就不会因为执行者已做出局部优化而遗忘尚未完成的前置证明。

**第三，状态可审计且可复放。** 某个“完成”记录必须能回链到审计证据，而不是回链到一段不可检索的工具日志。生产系统可进一步将 `S_i`、`v_i`、契约版本、环境快照哈希和策略版本放入 append-only ledger，使恢复、复盘和离线评价有稳定边界。

需要注意的是，这不是通过状态机消除模型错误。状态可能不完整，审计可能误判，契约也可能遗漏验收条件。它解决的是错误传播问题：未核验的自我报告不应自动成为后续计划的事实。

![失败传播、审计提交与作者报告的评测结果](https://mmbiz.qpic.cn/mmbiz_png/0WtFw2LmfOib9uYbpweSjp7U44XW9558qia83SBNyU1od6tXt7PYShFyNKwlmpggFBOTpoCvka7VqhiagRfvtx6WrxYUXJHFjqBQMBLOfic1P6o/640?from=appmsg)


论文没有重新实现 Claude Code、Codex CLI 或 OpenClaw 的工具调用和内部 ReAct loop，而是通过轻量 `AgentAdapter` 把它们作为有界 episode 启动。Harness 控制的是输入上下文、可用工具、环境权限、轮次预算和返回报告；后端则保留原有规划、工具使用与修正机制。

这是一个很实际的分层：
层责任不应承担的责任Backend Agent在一个子任务内探索、行动、修正维护全局真相与最终完成判定AgentAdapter统一角色输入、工具面、预算与报告格式改写后端内部决策循环MEA control plane契约、持久状态、审计提交、恢复与终止替代模型的视觉、编码或推理能力Environment真实文件、GUI、进程、测试和工件相信自然语言自述

这种适配层的价值是让“长程可靠性策略”不依赖某个单一模型或 harness。论文用相同 backbone 实例化 Manager、Executor 与 Auditor，以尽量隔离状态管理层的贡献；Executor 则可保留 Claude Code 等后端。对工程团队而言，最小可行迁移路径也因此清晰：先不替换执行 Agent，只在外部加状态、契约和可观测审计。

## 五、实验数据说明了什么，也没有说明什么

作者在 WeaveBench、OSWorld 2.0 和 Terminal-Bench 2.1 上评估该架构，覆盖 GUI 与 CLI 协作、桌面工作流、纯命令行长任务。主比较应优先看同模型、同执行后端的匹配设置，而不是将不同权限、不同基线模式的结果混为一谈。
基准与匹配设置基线LongHorizon-Harness变化WeaveBench，Qwen 3.7-Plus + Claude CodePassRate 51.8%80.7%+28.9 个百分点Terminal-Bench 2.1，Qwen 3.7-Plus + Claude Code成功率 69.7%77.2%+7.5 个百分点OSWorld 2.0，Qwen 3.7-PlusBinary 2.8%，Partial 21.5%Binary 8.3%，Partial 35.2%+5.5 / +13.7 个百分点OSWorld 2.0 34 题子集，Claude Opus 4.7Binary 20.6%，Partial 55.8%Binary 35.3%，Partial 66.9%+14.7 / +11.1 个百分点

这些结果支持一个有价值的结论：在作者的设置中，任务级能力不仅来自 backbone，也来自系统如何切分、验证、恢复并累积每一步的结果。尤其是 WeaveBench 的 matched comparison，保留 Claude Code 作为执行后端而增加 MEA 控制层，较好地把收益归因于状态管理策略。

但以下边界同样重要。

• WeaveBench 表中的外部参考结果存在权限设置差异；论文也明确将它们作为参考而非严格匹配比较。文章中的主要判断应建立在作者自己的 matched configuration 上。

• OSWorld 的 Binary 指标仍然很低。`2.8% -> 8.3%` 是三倍提升，却不代表桌面任务已达到可广泛无人值守的成功率；Partial 的提高说明更多需求被完成，但“全部满足”仍是瓶颈。

• 审计能发现和恢复很多长程过程错误，却不能给模型补上视觉、数学、编码或算法设计能力。论文也观察到，当主瓶颈是单步原子能力而不是状态保持时，收益更小，甚至可能回退。

• 论文报告的结果来自 2026 年 8 月的实现、模型和基准版本，应视为作者实验结论，而不是对所有 Agent 环境的保证。

## 六、成本不是 Manager 的推理，而是“验证 + 返工”

多角色结构自然会增加调用。论文给出的角色分解很有启发：Manager 在 WeaveBench、OSWorld 2.0、Terminal-Bench 2.1 的 token 占比分别只有 2.8%、2.0%、8.1%；Auditor 则为 19.4%、24.8%、38.1%。也就是说，维护状态本身不贵，主要新增成本来自独立检查。

在 Qwen 3.7-Plus 的 OSWorld 设置中，平均输出 token 从 28.9K 增至 104K；WeaveBench 总 token 约为基线的 2.3 倍。相反，在 Terminal-Bench 2.1 上，作者报告系统以更高成功率消耗少 24% token。这说明 MEA 不是固定的 token 倍增器：成本取决于模型需要多少执行-审计-重规划回合才能完成一个有效转换。

一个可操作的成本模型是：

```
cost(task) = sum_rounds (cost_manager + cost_execute + cost_audit)
expected_cost_to_verified_completion
  = cost(task) / P(audited completion)
```

第二个指标比“单次任务 token”更接近生产决策。若审计让错误路径更早终止、避免重复返工，它可能提高单任务 token，却降低每个经验证交付物的实际成本。反之，若验收条件模糊或环境不可观察，Auditor 只会制造昂贵的低置信度循环。

## 七、生产化不能只复制三角色，必须定义状态与证据协议

将 MEA 用于真实业务时，建议先把论文中的抽象状态转化为明确的数据契约。一个最小状态记录可包含：
对象最小字段关键约束Requirement`id`、验收条件、状态、依赖`completed` 必须有审计证据ArtifactURI / 路径、版本或哈希、来源审计需验证存在性与语义有效性Fact值、观察时间、证据引用、可信度不把 Executor 文本当作唯一来源Contract目标、输入、允许动作、禁止动作、验收项每轮范围小且可独立审计Audit reportcompletion、integrity、evidence、remaining gaps只读过程；可定位、可复放

随后，围绕四个工程问题落地。

### 1. 将验收条件编译为可观测断言

“完成部署”不是一个可审计条件；“指定版本在目标环境运行、健康检查返回预期、回滚路径存在、变更记录已生成”才是。验收项应尽可能对应文件哈希、测试结果、API 响应、数据库查询、进程状态或截图中的可比较结构。不可自动判定的体验性要求要明确标记为需要用户确认，而不是让 Auditor 假装精确。

### 2. 把只读权限做成系统能力，而不是提示词

Auditor 的工具账户、网络范围、文件系统挂载和 GUI 控件需要独立配置。运行时还应记录审计窗口内的文件 diff、命令类型和外部副作用；一旦发现写入，审计结果失效。这比在 prompt 中写“请勿修改”可靠得多。

### 3. 用幂等与补偿处理不确定的写操作

“审计未通过”不一定意味着“Executor 没有产生副作用”。对于创建工单、发送消息、支付、部署等动作，契约必须携带 idempotency key、预期资源标识和补偿/升级路径。否则系统在不确定状态下重试，可能把一次错误变成两次真实写入。

### 4. 把人工介入纳入状态机

Manager 的 `ask` 不该是异常分支。授权缺失、歧义需求、无法判定的视觉质量、合规风险和外部系统故障都应进入可观察状态，并携带需要人回答的最小问题、当前证据和安全的恢复点。

## 八、建议用“经核验的推进率”评价长程 Agent

只看最终通过率会掩盖系统的真实失效位置。针对 MEA 类运行时，建议至少持续跟踪以下最小指标集：
指标计算方式它定位的系统问题Verified transition rate通过 `clean + complete` 审计的契约数 / 总契约数子任务切分与执行是否有效Audit disagreement rateExecutor 声称完成但审计判非完成的比例自我评估漂移、验收条件不足Recovery yield审计发现缺口后，后续若干轮最终完成的比例重规划是否真的恢复任务Evidence coverage已完成 requirement 中具有可定位证据的比例状态账本是否可审计Cost per verified completion总成本 / 最终经核验完成数验证开销是否值得Human escalation precision`ask` 后被确认确实需人工的比例Manager 的风险与不确定性识别

这些指标将模型能力、执行稳定性和可验证性分开。一个 Agent 即使最终偶尔完成，也可能长期依赖未证实状态；另一个 Agent 的单轮速度较慢，却能稳定产出可检查、可恢复的工作结果。对长程自动化，后者通常更接近可运营系统。

## 结语：把“我做完了”降级为一个待验证的请求

LongHorizon-Harness 的价值不在于增加三个人格化角色，而在于设定一条很硬的运行时规则：**跨回合的任务事实必须来自独立的环境检查，而不是执行者的自述。**

一旦采用这条规则，长程 Agent 的设计重心会从“怎样让单个会话记得更多”转向“怎样让状态可验证、契约可执行、审计不可写、失败可恢复”。模型仍决定每个局部动作能做到什么；但 harness 决定这些局部动作能否累积成可靠的端到端工作。

对真正需要多小时、多工具、多系统协作的任务，这种从对话轨迹到审计状态机的转向，可能比再次扩大上下文窗口更关键。

## 资料链接

LongHorizon-Harness 论文：https://arxiv.org/abs/2608.01964

LongHorizon-Harness 项目：https://github.com/AMAP-ML/LongHorizon-Harness
