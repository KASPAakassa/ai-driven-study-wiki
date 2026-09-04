# OpenWorker 拆解:吴恩达团队的开源桌面 Agent 参考实现

> **一句话摘要**:OpenWorker 是吴恩达(Andrew Ng)团队开源的**本地优先桌面 Agent**(MIT,13.8K+ stars):桌面端接需求、本地 Python 服务跑任务,把"一句话"变成**可检查的交付物**。本文沿源码拆解它的四层架构、六条运行线、风险分类与审批机制、以及"模型可换、运行时合同不变"的设计。
>
> **来源**:微信公众号「架构师 JiaGouX」《吴恩达开源版WorkBuddy:拆解OpenWorker的桌面Agent架构》(若飞),https://mp.weixin.qq.com/s/j9aavJfKJyRG6c1mWRC7tw;仓库 https://github.com/andrewyng/openworker

## 概念:OpenWorker 是什么

!!! note "定位(作者原话)"
    第一次看到 OpenWorker,很自然会想到腾讯 WorkBuddy——两者都在尝试把 AI 从"回答问题"往前推一步:接到一句话后,继续查资料、调用工具、完成任务,最后交出一份**可以检查的成品**。标题的"开源版 WorkBuddy"只是产品形态类比,**两者没有官方从属或代码继承关系**。

| 项 | 内容 |
| --- | --- |
| 仓库 | [andrewyng/openworker](https://github.com/andrewyng/openworker)(MIT,13.8K+ stars) |
| 形态 | 本地优先(local-first)桌面 Agent:React + Tauri 桌面壳 + Python 本地服务 |
| 模型 | 可接 OpenAI/Anthropic/Gemini/GLM/DeepSeek/Kimi/Qwen/MiniMax,或 Ollama 本地模型 |
| 关键设计 | 模型可换、运行时合同稳定;Skills 负责方法、权限由运行时掌握 |

## 原理 1:四层运行架构(从官方三层图细化)

官方 README 画的是三层(桌面应用 → 本地 Agent 服务 → 文件/工具/模型);顺着源码可细分为**四组运行职责**:

| 层 | 职责 | 源码对应 |
| --- | --- | --- |
| **交互层** | React + Tauri 桌面 Surface:会话、进度、交付物、审批卡片、设置 | 桌面端 UI |
| **Agent 运行层** | Python 服务:任务循环、模型调用、Skills、工具编排、工作区 | `coworker/agent.py`、`engine.py`、`agents/cowork.py` |
| **控制层** | 风险分类、权限决策、Inbox(人工待办)、Audit Store(审计) | `risk.py`、`permissions.py`、`inbox.py`、`audit.py` |
| **资源与执行层** | 文件、终端、连接器、MCP、模型提供方构成真实工作环境 | `skills/base.py`、`tools/shell.py` |

!!! tip "分工要点"
    桌面端只是 **Surface(界面)**,Python 服务才是**运行时**——以后加 Slack/CLI 等其他入口,底层可复用同一任务引擎。这正对应 [生产级 Agent 9 层架构](../03-agents/ai-infra-layering.md) 的 L4/L5/L8 分层。

## 原理 2:六条运行线(一次任务贯穿)

把一次任务放进去,六条线相互配合:

1. **任务线**:目标如何拆成步骤、进度如何持续更新;
2. **模型线**:不同模型如何接入、如何与工具层解耦;
3. **工具线**:文件、搜索、命令和外部系统如何被统一调用;
4. **权限线**:哪些动作直接做、哪些等人批准;
5. **状态线**:前台会话、后台任务、待审批事项、审计记录如何衔接;
6. **交付线**:结果如何落成文件/消息/日历变更,而不是停在一段回复里。

## 原理 3:一次任务穿过架构的六个阶段

以"帮我准备 Northwind 的续约电话会"为例:

### ① 桌面端把目标交给本地服务
桌面应用建立会话和工作区上下文,把需求交给本地 Agent 服务;模型密钥、连接器令牌、会话状态默认保存在**本机应用存储**。

### ② Agent 先建立可见进度
Cowork Agent 默认四组核心能力:`COWORK_CAPABILITIES = ["files", "search", "shell", "todo"]`。只要任务需要调用工具,系统指令就要求**先 `todo_write` 建立步骤,且始终只有一个 `in_progress` 状态**;桌面 Progress 面板直接读取这份状态。

!!! tip "为什么强制 todo"
    没有 todo,运行过程就退回成"长时间没有反馈的等待"。`todo_write` 不是完整工作流引擎,但它先解决了桌面 Agent 最常见的反馈问题——**人至少知道它在查什么、卡在哪、下一步做什么**。

### ③ 模型提议动作,工具层负责执行
模型不直接操作电脑,它生成**工具调用**,Agent Engine 交给文件/搜索/终端/连接器执行。自带 20+ 连接器,支持 MCP。多个工具调用时,Engine **逐个先过授权判断**,通过才进执行队列,再按风险决定并发/串行。

!!! tip "执行策略:低风险并行、副作用串行"
    低风险读取可并行;有副作用的写入和命令**保持顺序执行**——牺牲一点表面速度,减少多个写操作互相覆盖,执行记录更容易还原。**对真实工作,可解释的顺序通常比"所有工具一起跑"更可靠。**

### ④ 每个动作先经过风险分类
OpenWorker 把工具动作分成四类:

| 风险类型 | 典型动作 | 运行时关注点 |
| --- | --- | --- |
| **READ** | 读文件、搜索、查询 | 无副作用,可直接执行 |
| **WRITE_LOCAL** | 写文件、修改内容 | 写入模式与允许目录 |
| **EXEC** | 运行命令 | 命令内容、允许规则与审批 |
| **EXTERNAL** | 发消息、改日历、更新外部系统 | 对外副作用与明确授权 |

Permission Engine 结合工作模式、可写目录、命令允许列表、工具元数据决策:

| 模式 | 行为 |
| --- | --- |
| Discuss / Plan | 拒绝有后果的动作 |
| Interactive(默认) | 允许读取;写入/命令/外部操作需确认 |
| Custom | 按配置放行指定工具 |
| Auto | 放行有副作用的动作,但本地写入仍受目录约束 |

!!! warning "shell 命令检查"
    命令检查会处理 `;`、`&&`、管道、重定向、命令替换等 shell 操作符——**只做字符串前缀匹配会允许前半条安全命令、漏掉后面拼接的危险动作**。

`risk.py + permissions.py + inbox.py + audit.py` 合起来构成**控制平面**:动作先分类 → 决策 → 等待人工处理 → 留记录。**模型可以提出动作,控制层决定这个动作此刻能不能发生。**

### ⑤ 前台审批与后台 Inbox 共用一套机制
- 人在电脑前:审批卡片直接出现在当前会话;
- 后台任务:不会默认替用户点同意,请求停在 **Inbox**,等人批准/拒绝/补充信息后再继续;
- 这让"定时生成周报"(本机可形成草稿)与"定时发送周报"(改变外部状态,需单独授权)成为两件不同的事;
- Inbox 是**跨会话的人类注意力队列**:保存待处理事项,暂停的任务收到结果后继续——这正是"无人值守任务"中"稳定输入 + 交接状态 + 证据 + 权限 + 停止条件"的运行时实现(呼应 [Loop Engineering](../07-agent-coding/experience/loop-engineering.md))。

### ⑥ 结果进入 Artifacts 和审计记录
Cowork Agent 指令要求把文档/分析/计划/数据集/小脚本**写成文件,用 `artifact:` 链接交付**;Artifacts 面板可独立展示、打开、刷新产物。同时 Audit Store 记录工具、执行阶段、状态、审批结果、参数摘要、资源引用(敏感字段只留摘要或脱敏)。

!!! tip "任务完成的三份状态"
    - **Progress**:任务走到了哪里;
    - **Artifacts**:交付物在哪里;
    - **Audit**:执行过哪些动作、谁批准了什么。
    聊天记录仍然重要,但不再承担全部事实——与 [WorkBuddy Bench](../03-agents/workbuddy-bench.md) 的"完成 = 交付物可用 + 状态一致 + 证据可复核"完全同源。

## 原理 4:模型可换,运行时合同不能换

Agent Engine 构建在 **aisuite** 之上,统一接口适配不同模型提供方,复用工具/Toolkit/MCP。模型不直接绑定文件系统和外部服务——它看到的是**工具定义**,输出的是**下一步调用建议**;能否执行、在哪执行、是否审批、如何记录,由运行时决定。

模型更换后以下合同仍保留:**工具参数与返回值、风险分类与权限策略、工作区与可写目录、进度状态、审批与 Inbox、交付物链接与审计记录**。

## 原理 5:Skills 负责方法,权限仍由运行时掌握

- Skill = YAML 元数据 + Markdown 指令 + 可选资源;会话开始时**只把名称和描述放进上下文**,需要时 `load_skill` 加载完整内容(**渐进式加载**,避免把所有说明一次性塞给模型);
- 以"生成架构评审报告"为例,Skill 约定:先读 ADR/接口文档/故障记录 → 对照目标/约束/备选/回滚 → 输出风险清单 → 生成固定格式文档;
- **Skill 不会自动扩大工具权限**——即使技能里写着"把报告发到 Slack",发送仍要过连接器配置、风险分类与审批。**方法层与执行层分开,才能复用专业流程,又不让一份 Markdown 绕过安全控制**(呼应 [mattpocock/skills](../07-agent-coding/skills/mattpocock-skills.md) 与 [AI Friendly 架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md) 的 Skill/权限分离)。

## 边界与对比

### 执行器边界:当前还在本机
命令工具建立在 Executor 抽象之上,当前是 **LocalExecutor**(持久 shell,`cd`/环境变量/虚拟环境跨命令保留)。ContainerExecutor/VMExecutor 留有接口但未实现。**审批代表用户同意执行,不代表命令安全,也不提供隔离/幂等/补偿/业务正确性。**

### local-first 的边界
Agent 循环、会话、密钥、连接器令牌默认在本机;用 Ollama 模型可完全本地。但选云模型时必要上下文发给模型提供方,调 Slack/邮箱/CRM 时数据进入对应服务——**本地优先描述的是运行时和状态的默认归属,不等于所有数据永远不离开设备。**

### 与腾讯 WorkBuddy 对比

| 观察角度 | 腾讯 WorkBuddy | OpenWorker |
| --- | --- | --- |
| 产品形态 | 腾讯云产品与企业生态 | MIT 开源桌面应用 |
| 模型与账号 | 平台提供的模型与服务 | 用户自带模型/密钥,可接 Ollama |
| 工具接入 | 腾讯生态与平台能力 | 本地文件/终端/连接器/MCP |
| 运行基础 | Agent Runtime 与安全沙箱 | 本地 Python 服务,LocalExecutor |
| 观察重点 | 企业级工作台与托管运行 | 桌面 Agent 的模块、协议和源码实现 |

## 实践 / 应用:四类任务检验四组能力

| 场景 | 任务 | 检验的架构能力 |
| --- | --- | --- |
| 工作 | 晨会资料 → 简报(HTML/Markdown) | 文件读取、任务进度、交付物、引用完整性 |
| 生活 | 零散行程 → 计划 | "生成文件"与"改外部日历"的风险差异 |
| 架构 | ADR/接口/事故 → 评审草稿 | Skill 复用评审方法、限定资料范围、溯源 |
| 研发 | 仓库状态 → 发布诊断报告 | 文件/搜索/终端/权限/审计全链路 |

**第一次试用模板**(边界清楚的小任务):

```text
目标:根据本目录的会议纪要和项目数据,生成本周项目简报。
输入:只使用 ./meeting-notes 和 ./metrics。
允许访问:可以读取上述目录,可以写入 ./output。
不要做:不要发送邮件,不要修改日历,不要读取其他目录。
交付物:./output/weekly-brief.md
```

## 总结

- OpenWorker = **本地优先桌面 Agent 参考实现**(MIT):桌面 Surface + Python 运行时,一句话 → 可检查交付物;
- **四层架构**(交互/Agent 运行/控制/资源执行)+ **六条运行线**(任务/模型/工具/权限/状态/交付);
- 风险四分类(READ/WRITE_LOCAL/EXEC/EXTERNAL)+ 五工作模式 + shell 操作符检查 = 控制平面;**模型可提出动作,控制层决定动作能否发生**;
- **三份状态**:Progress(走到哪)/ Artifacts(成品在哪)/ Audit(做过什么、谁批准);
- **模型可换、运行时合同不变**;Skills 管方法、权限仍由运行时管;执行器与本机边界要认清;
- 价值:它是 [生产级 Agent 9 层架构](../03-agents/ai-infra-layering.md) 的开源落地样本——权限线、状态线、交付线的具体实现。

## 延伸阅读

- 站内:[Harness 章节首页](index.md)、[通用编排框架](orchestration-frameworks.md)、[生产级 Agent 9 层架构](../03-agents/ai-infra-layering.md)、[WorkBuddy Bench](../03-agents/workbuddy-bench.md)、[Loop Engineering](../07-agent-coding/experience/loop-engineering.md)
- 外部:原文(架构师 JiaGouX);OpenWorker 仓库 https://github.com/andrewyng/openworker;腾讯 WorkBuddy 公开材料;原始资料存档于 `docs/inbox/openworker-source.md`
