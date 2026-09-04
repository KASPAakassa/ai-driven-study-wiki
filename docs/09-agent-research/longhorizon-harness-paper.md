# LongHorizon-Harness:让长程 Agent 的任务状态脱离上下文

> **一句话摘要**:长程 Agent 失败的根因不是"模型忘了",而是执行轨迹、任务状态、完成判定被塞进同一段膨胀上下文;LongHorizon-Harness(arXiv:2608.01964)用 Manage-Execute-Audit(MEA)状态机把执行重述为**受独立审计的任务状态管理**,让跨回合事实只来自环境验证而非执行者自述。这是 agent 长程任务设计的一条新思路:harness 决定局部动作能否累积成可靠的端到端工作。
>
> **来源**:
> - 微信解读:SOTA AI研报《LongHorizon-Harness 深度剖析》(https://mp.weixin.qq.com/s/KalxQye81xn3uFCYwy5SfQ)
> - 论文:[LongHorizon-Harness: Advancing Long-Horizon Agents for Real-World Tasks](https://arxiv.org/abs/2608.01964)(arXiv:2608.01964,Ziyu Ma 等 8 人,2026-08-03)
> - 开源:[github.com/AMAP-ML/LongHorizon-Harness](https://github.com/AMAP-ML/LongHorizon-Harness)(MIT,`uv tool install lh-harness`)

## 概念

### 长程任务为什么失败:三类信息被混在同一个上下文里

长程(long-horizon)任务需要跨多小时、多工具、多系统持续推理、行动与修正。连续 Agent loop 通常把三类性质完全不同的信息混在历史消息里:

| 信息类型 | 内容 | 特性 |
| --- | --- | --- |
| **执行轨迹** | 点击、命令、报错、尝试、局部推理、中间观察 | 对当前动作有用,但增长最快、噪声最多 |
| **任务状态** | 原始目标、未满足需求、已生成工件、已确认的环境事实、阻塞项与依赖 | 必须短、小、结构化,任意回合可重新读取 |
| **完成证据** | 真实环境中可观察的文件、界面、测试结果、进程状态、日志与元数据 | 回答"系统现在确实处于什么状态",而非"Agent 说它做了什么" |

三者共享同一滚动上下文时,产生三个结构性故障:

1. **Context rot(上下文腐化)**:旧操作细节淹没在后续观察与推理中,模型未真正遗忘,却越来越难检索并正确使用关键前提。
2. **状态漂移(State drift)**:执行者把"我已经改了文件""看起来像完成了"当作事实,后续计划建立在未经验证的状态上。
3. **评估与行动耦合(Coupled evaluation & action)**:同一个策略既负责改变环境,又负责宣称满足验收条件,缺乏独立制衡。

因此**单纯加大上下文窗口不能根治长程可靠性**——更大的窗口只是扩大了可携带的轨迹,却没有规定哪些记忆可信、哪种观察可以升级为状态、失败后从哪恢复。LongHorizon-Harness 的立场是把这些判断变成**系统协议**,而不是要求模型在提示词里"更认真一点"。

### LongHorizon-Harness 是什么

> LLM agents increasingly undertake long-horizon tasks... existing agent harnesses maintain task execution, task state, and completion assessment within a growing context, making the state difficult to track and allowing incorrect self-assessments to propagate into later decisions. We reformulate long-horizon execution as a **task-state management problem** and propose LongHorizon-Harness, which maintains the task state explicitly **outside** execution and updates it only with facts **independently verified from the environment**. —— 论文摘要

一句话:它不训练新模型、不替换已有 Agent,而是**在现有 Agent(Claude Code / Codex 等)外面套一层"执行 + 状态管理 + 结果验证"的运行时**,把长程执行改造成**可核验的状态机**。它更像控制系统,而不是长对话。

## 原理

### MEA 回合:把一次 Agent 回合做成受审计的状态转换

论文把一项长期任务写成重复的 **Manage-Execute-Audit(MEA)** 回合。记第 `i` 轮开始的任务状态为 `S_i`、环境状态为 `e_i`:

```
Manager:  (S_i, audit history, goal) -> subtask contract c_i
Executor: (S_i, c_i, bounded fresh context, e_i) -> e_(i+1), execution report o_i
Auditor:  (S_i, c_i, o_i, read-only inspection of e_(i+1)) -> audit report v_i
Manager:  (S_i, v_i, goal) -> S_(i+1), next decision
```

关键不在于角色顺序,而在于**状态提交规则**:`o_i` 是执行者的主张(claim),`v_i` 才是可用于更新 `S_(i+1)` 的环境证据(evidence)。系统把"执行成功"从**语言判断**转换成**需要外部读证的提交条件**——这正是分布式系统中 command/query separation 与 commit gate 在 Agent 运行时里的对应物。

### 三个角色的职责与约束

**1. Manager:持有状态,但不接触环境**

Manager 拥有原始任务、当前任务状态和累计审计报告,**却没有 GUI、CLI 或文件系统权限**。这个限制是关键:如果 Manager 能直接查看环境,就可能绕过审计、用未校验的观察污染状态。

状态至少包含三类结构化记录:`requirement`(目标或约束)、`artifact`(已创建/修改的产物)、`fact`(后续执行需要的环境事实);每条记录标记为 `completed` / `pending` / `blocked` / `untrusted`,并保存支持它的审计证据引用。

Manager 的下一步不是泛泛的 plan,而是构造一个**子任务契约**:即时目标、验收条件、边界约束、依赖项、本轮必要的历史证据。它可输出 `execute` / `done` / `blocked` / `ask`——"请用户补充信息/授权"与"模型已无法继续"成为显式状态,而不是藏在长回复里的模糊失败。

**2. Executor:只完成一个有限的环境转换**

Executor 是唯一有意修改任务环境的角色。它收到原始目标、当前状态、当前契约和契约引用的少量审计记录;**此前回合的原始聊天、工具轨迹和内部推理不会传入**。一次执行结束后原始轨迹被丢弃,留下的只是执行报告 `o_i`。

这不是"无记忆 Agent",而是**选择性、可证明的记忆**:新鲜上下文让 Executor 不必背负已成功/已失败的细节,只聚焦一个可验证的状态变化;Manager 通过契约决定必须携带什么,避免把"上下文压缩"交给模型的临场判断。

环境能力分两类:**GUI**(截图、点击、滚动、输入等界面状态转换)与 **CLI**(shell、文件编辑、测试、进程、工作区状态)。选择哪个 Executor 是 Manager 对契约的路由决策,而不是让一个全权限会话在所有工具间任意游走。

**3. Auditor:只读不是形式约束,而是完整性边界**

Auditor 从新鲜上下文开始,**不拿到 Executor 的原始轨迹和内部推理**;可读取执行报告来定位文件/窗口/日志/工件,但完成与否必须由**环境检查**得出,并与契约的验收条件、边界约束逐项对照。它不得创建、编辑、覆盖、移动或删除受保护产物,也不得执行会改变被检查结果的命令/GUI 操作。Harness 在审计期监控任务相关的工作区与工件,一旦发现写入,报告标为 **integrity violation**,不能支持"已完成"的状态记录。

审计报告包含三组结论:

| 维度 | 可取状态 | 对持久状态的意义 |
| --- | --- | --- |
| Completion | `complete` / `incomplete` / `blocked` | 当前契约的验收项是否真的满足 |
| Integrity | `clean` / `suspect` / `violation` | 审计过程和工件来源是否可信 |
| State delta | 已证实事实、证据、剩余缺口 | Manager 在下轮可采纳的状态增量 |

所以 Auditor 不是"再让一个模型评一次分",而是一条**能力受限的独立读路径**:执行者负责写,审计者负责读,Manager 负责把经过证明的读结果写入任务账本。

### 真正的记忆载体是审计报告,而不是压缩后的对话

MEA 最强的一条约束:**跨回合持久化的不是 Executor 的完整输出,而是任务状态及其支持性审计报告**。三个直接效果:

1. **失败变成可恢复状态**:GUI 操作卡住、命令被拒绝,不再只是长轨迹里的失败片段;Auditor 可把"交互未响应""某文件不存在""验收项 X 未满足"记为 `blocked`/`pending` 事实,下一轮 Manager 从事实重新选路,而非同一会话反复重试旧动作。
2. **先后顺序可以被约束**:要求"修复前收集证据""修改后保留元数据"这类约束写进状态中的 `requirement`,Manager 不会因执行者做出局部优化而遗忘未完成的前置证明。
3. **状态可审计且可复放**:每个"完成"记录必须回链到审计证据,而非一段不可检索的工具日志;生产系统可把 `S_i`、`v_i`、契约版本、环境快照哈希、策略版本放入 append-only ledger。

注意:**这不是通过状态机消除模型错误**(状态可能不完整、审计可能误判、契约可能遗漏验收条件),它解决的是**错误传播问题**:未核验的自我报告不应自动成为后续计划的事实。

### AgentAdapter:不重写执行 Agent,只包一层控制面

论文没有重新实现 Claude Code / Codex / OpenClaw 的工具调用和内部 ReAct loop,而是通过轻量 `AgentAdapter` 把后端作为**有界 episode** 启动。分层职责:

| 层 | 责任 | 不应承担的责任 |
| --- | --- | --- |
| Backend Agent | 在一个子任务内探索、行动、修正 | 维护全局真相与最终完成判定 |
| AgentAdapter | 统一角色输入、工具面、预算与报告格式 | 改写后端内部决策循环 |
| MEA control plane | 契约、持久状态、审计提交、恢复与终止 | 替代模型的视觉/编码/推理能力 |
| Environment | 真实文件、GUI、进程、测试和工件 | 相信自然语言自述 |

价值:让"长程可靠性策略"不依赖某个单一模型或 harness。论文用相同 backbone 实例化 Manager/Executor/Auditor 以隔离状态管理层的贡献;Executor 则可保留 Claude Code 等后端。**最小可行迁移路径**:先不替换执行 Agent,只在外部加状态、契约和可观测审计。

## 代码 / 实现

开源项目(552★,MIT,Python)实际可跑,核心链路如下。

### 安装与初始化

```bash
uv tool install lh-harness      # 或 pip install lh-harness
lh-harness doctor               # 只读环境检查(Python/agent CLI/Node/插件)

# GUI 任务需装 computer-use 插件(纯 CLI 可跳过)
lh-harness plugin install codex-computer-use     # Codex 官方插件
lh-harness plugin install open-computer-use      # npm,Claude Code / Codex 通用

cd /path/to/your/project
lh-harness init                 # 生成 ./.lh-harness/config.toml(不会覆盖已有文件)
```

### 跑一个任务

```bash
TASK="Inspect the current directory and summarize its files."
lh-harness run --task "${TASK}" --agent codex
```

Agent 在启动目录工作;`./.lh-harness/` 自身保持隔离(运行日志与状态不会被误当任务内容)。每次运行存于 `./.lh-harness/runs/<run-id>/`,结束时给出**仅基于已验证状态**的平实语言总结;Dashboard 展示每轮 plan / execution / audit / rework,并提供人工闸门(完成、阻塞、需输入、反复失败时)。

### 关键配置(config.toml)

| 字段 | 默认 | 说明 |
| --- | --- | --- |
| `[run] agent` | `"codex"` | 后端:`codex` 或 `claude_code` |
| `[run] model` | `"gpt-5.6-sol"` | 各角色默认模型,须是后端暴露的模型 |
| `[run] max_rounds` | `30` | MEA 回合数上限 |
| `[run] env` | `"local"` | 执行环境(目前仅 local) |
| `[run.timeouts]` | manager 600s / executor 1800s / auditor 600s | 单 episode 超时,不是整轮 |
| `[run.roles.*]` | 继承 `[run]` | 每个角色可单独配 agent/model(gui_executor → executor → [run] 逐级回退) |

**三角色可用不同模型/后端**:能力强的 Manager + Auditor 配便宜 Executor,按需平衡质量/速度/成本。CLI 参数(如 `--agent`、`--max-rounds`、`--gui-executor-model`)优先于配置文件。

### 最小成本模型

```
cost(task) = sum_rounds (cost_manager + cost_execute + cost_audit)
expected_cost_to_verified_completion = cost(task) / P(audited completion)
```

第二个指标比"单次任务 token"更接近生产决策:审计让错误路径更早终止、避免重复返工,可能提高单任务 token 却降低**每个经验证交付物**的实际成本;反之若验收条件模糊或环境不可观察,Auditor 只会制造昂贵的低置信度循环。

## 实践 / 应用

### 实验数据(arXiv 摘要口径)

| 基准 | 匹配设置 | 基线 | LongHorizon-Harness | 变化 |
| --- | --- | --- | --- | --- |
| WeaveBench | Qwen 3.7-Plus | PassRate 51.8% | **80.7%** | +28.9 pp |
| Terminal-Bench 2.1 | Qwen 3.7-Plus | 成功率 69.7% | **77.2%** | +7.5 pp |
| OSWorld 2.0 | Qwen 3.7-Plus | Binary 2.8% | **8.3%** | +5.5 pp(Partial 21.5%→35.2%) |
| OSWorld 2.0 子集 | Claude Opus 4.7 | Binary 20.0% | **34.3%** | +14.3 pp |

结论:任务级能力不只来自 backbone,也来自**系统如何切分、验证、恢复并累积每一步结果**。尤其 WeaveBench 的 matched comparison 保留 Claude Code 作执行后端、仅增加 MEA 控制层,较好地把收益归因于状态管理策略。论文同时报告:同模型同执行后端、只换 harness,约 50% 的 OSWorld 任务出现可靠提升。

**边界(论文与解读都强调)**:

- 外部参考结果存在权限设置差异,应视为参考而非严格匹配比较;
- OSWorld 的 Binary 指标仍然很低(2.8%→8.3% 是三倍提升,但"全部满足"仍是瓶颈);
- 审计能发现并恢复很多长程过程错误,**不能补模型单步原子能力**(视觉/数学/编码/算法);当瓶颈是单步能力而非状态保持时,收益更小甚至回退;
- 数字来自 2026-08 的实现/模型/基准版本,是作者实验结论而非对所有环境的保证。
- ⚠️ 微信文章表格中 OSWorld 子集写作 20.6%→35.3%,与 arXiv 摘要(20.0%→34.3%)略有出入,本站以 arXiv 摘要为准。

### 成本结构

Manager 在 WeaveBench / OSWorld 2.0 / Terminal-Bench 2.1 的 token 占比分别只有 **2.8% / 2.0% / 8.1%**;Auditor 为 **19.4% / 24.8% / 38.1%**——**维护状态本身不贵,主要新增成本来自独立检查**。OSWorld(Qwen 3.7-Plus)平均输出 token 从 28.9K 增至 104K;WeaveBench 总 token 约为基线 2.3 倍;而 Terminal-Bench 2.1 以更高成功率**少消耗 24% token**。MEA 不是固定 token 倍增器,成本取决于需要多少"执行-审计-重规划"回合才能完成有效转换。

### 生产化四步(从论文到真实业务)

1. **把验收条件编译为可观测断言**:"完成部署"不可审计;"指定版本在目标环境运行、健康检查返回预期、回滚路径存在、变更记录已生成"才可审计。验收项尽量对应文件哈希、测试结果、API 响应、数据库查询、进程状态、截图中的可比较结构;不可自动判定的体验性要求显式标记为需用户确认。
2. **把只读权限做成系统能力,而不是提示词**:Auditor 的工具账户、网络范围、文件系统挂载、GUI 控件独立配置;运行时记录审计窗口内的文件 diff、命令类型、外部副作用,发现写入即判审计失效。
3. **用幂等与补偿处理不确定的写操作**:"审计未通过"≠"没有副作用"。对创建工单、发消息、支付、部署等动作,契约必须携带 idempotency key、预期资源标识和补偿/升级路径,避免不确定状态下重试把一次错误变成两次真实写入。
4. **把人工介入纳入状态机**:Manager 的 `ask` 不该是异常分支;授权缺失、歧义需求、无法判定的视觉质量、合规风险、外部系统故障都应进入可观察状态,并携带最小问题、当前证据、安全恢复点。

### 用"经核验的推进率"评价长程 Agent

只看最终通过率会掩盖真实失效位置,建议持续跟踪:

| 指标 | 计算方式 | 定位的问题 |
| --- | --- | --- |
| Verified transition rate | `clean + complete` 审计的契约数 / 总契约数 | 子任务切分与执行是否有效 |
| Audit disagreement rate | Executor 声称完成但审计判非完成的比例 | 自我评估漂移、验收条件不足 |
| Recovery yield | 审计发现缺口后,后续若干轮最终完成的比例 | 重规划是否真的恢复任务 |
| Evidence coverage | 已完成 requirement 中具有可定位证据的比例 | 状态账本是否可审计 |
| Cost per verified completion | 总成本 / 最终经核验完成数 | 验证开销是否值得 |
| Human escalation precision | `ask` 后被确认确实需人工的比例 | Manager 的风险与不确定性识别 |

这些指标把**模型能力、执行稳定性、可验证性**分开:一个 Agent 可能偶尔完成却长期依赖未证实状态;另一个单轮较慢但稳定产出可检查、可恢复的结果——对长程自动化,后者通常更接近可运营系统。

## 总结

1. **长程 Agent 的核心不是更长上下文,而是让任务状态脱离上下文**:执行轨迹、任务状态、完成证据必须拆开,跨回合事实只来自独立环境验证。
2. **MEA 状态机是它的机制**:Manager 持状态不触环境、Executor 用新鲜有界上下文执行、Auditor 只读独立核验;`o_i` 是主张,`v_i` 才是可提交状态。
3. **记忆载体从"压缩对话"换成"审计报告"**:失败变可恢复状态、先后顺序可约束、状态可审计可复放——解决的是错误传播,而非消除模型错误。
4. **AgentAdapter 让它不绑死单一模型/harness**:现有 Claude Code / Codex 可作有界 episode 直接接入,最小迁移路径是"只加状态、契约、可观测审计"。
5. **生产化要点**:验收条件编译为断言、只读权限系统化、写操作幂等补偿、人工介入进状态机;用"经核验的推进率"类指标而非最终通过率评价。

**下一步学什么**:对比站内 [推理时验证设计范式](../03-agents/agent-test-time-verification.md)(Auditor 与验证不对称性、DRA 失败分类学的呼应)、[Agent 持久化运行](../03-agents/agent-persistence-patterns.md)(7 小时问题与跨回合状态);想动手就按上文安装 `lh-harness` 在本地项目试跑一个长任务,再看它每轮的 audit report 与 rework 路径。

## 延伸阅读

- 站内:[推理时验证(DeepVerifier)论文解析](inference-time-verification.md)、[Self-Harness:Agent 自我改造](self-harness-paper.md)、[Harness Handbook:行为定位](harness-handbook.md)、[Agent 评测(含长程)](../03-agents/agent-evaluation.md)、[Harness 框架与开源方案](../08-harness/index.md)(DeerFlow 等长程 harness)、[Agent 记忆体系](../03-agents/agent-memory-systems.md)、[上下文压缩与提示缓存](../03-agents/context-engineering-compression-caching.md)
- 外部:
  - 论文:[arXiv:2608.01964](https://arxiv.org/abs/2608.01964)(29 页,含 WeaveBench / OSWorld-V2 / Terminal-Bench 2.1 三套 frozen 评测复现 `eval/`)
  - 开源:[github.com/AMAP-ML/LongHorizon-Harness](https://github.com/AMAP-ML/LongHorizon-Harness)(MIT,中文 README、Dashboard、计算机使用插件生态)
  - 项目站点:[lh-harness.pages.dev](https://lh-harness.pages.dev)
  - 解读原文:SOTA AI研报《LongHorizon-Harness 深度剖析:长程 Agent 的核心不是更长上下文,而是让任务状态脱离上下文》(https://mp.weixin.qq.com/s/KalxQye81xn3uFCYwy5SfQ)
