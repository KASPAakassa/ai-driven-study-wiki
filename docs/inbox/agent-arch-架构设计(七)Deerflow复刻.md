# 原始资料:万字长文拆解Agent架构设计(七):用 Deerflow 复刻 Claude Code

> 来源:微信公众号(Agent 架构设计系列),原文链接:https://mp.weixin.qq.com/s/APBfdOzDTFXVGtMj8MSvZw
> 抓取日期:2026-08-09;状态:已拆解入库(见归档记录)

---

本系列目标：拆解 Claude Code 源码，理解 Agent 底层架构的设计思路。核心方法：读源码 → 理解设计决策 → 用 TypeScript 手写核心逻辑。
每一篇聚焦一个子系统，讲清楚"为什么这么设计"比"代码怎么写"更重要。

引言
前五篇拆完了 Claude Code 的五个子系统：记忆、工具、循环、协作、技能，每个都手写了实现。第六篇使用 LangChain 进行了验证，复刻 Claude Code。

万字长文拆解Agent 架构设计（一）：记忆系统设计
万字长文拆解Agent 架构设计（二）：工具系统设计
万字长文拆解Agent 架构设计（三）：Agent Loop 设计
万字长文拆解Agent 架构设计（四）：多 Agent 协作
万字长文拆解Agent 架构设计（五）：技能系统设计
万字长文拆解Agent 架构设计（六）：用 LangChain 复刻 Claude Code
这一篇换个验证对象——字节跳动开源的 DeerFlow 2.0。先澄清一个常见误会：它不是深度研究工具，那只是 1.0 的出圈作品。2.0 的官方定义是"构建和运营 Agent 系统的框架"，核心是一个叫 Harness 的运行时底座：模型、工具、记忆、技能、子 Agent、沙箱都插在它上面。一句话，它和 Claude Code 是同一类东西——一个是闭源的产品形态底座，一个是开源的框架形态底座。
Part 1：拆解 DeerFlow 2.0
1.1 骨架：同一个循环，打包成了底座
DeerFlow 的文档开篇就在区分两个词：framework 给你零件，让你自己写胶水把它们接起来；harness 更进一步，直接打包一套开箱即用的运行时——用官方原话说，"你不需要从零设计编排层，底座本身就是编排层"。
DeerFlow 整体分两层：Harness 是运行时底座（也是 Python SDK），Lead Agent、中间件链、五大能力都在这一层；DeerFlow App 是建在底座之上的参考应用，那套出名的深度研究体验。
底座建在 LangGraph 和 LangChain 之上，中心执行者叫 Lead Agent。官方给出的执行流程：

收到消息 → 中间件前处理（记忆注入、历史压缩等） → 模型推理（直接回答，或发起工具调用） → 工具执行（沙箱工具 / 外部工具 / task 工具派子 Agent） → 中间件后处理（生成标题等） → 循环，或输出最终响应
Lead Agent 不硬编码任何特定工作流，靠模型推理适应任意任务。涌现式编排，和 Claude Code 一字不差。
1.2 中间件链：行为是可插拔的零件
DeerFlow 的一条核心设计原则：行为由中间件链组合。每一轮模型调用都穿过这条链，每个中间件只管一件事。
顺序也有讲究：压缩排最前（先给上下文减负，后面所有处理都受益），澄清排最后（所有中间件处理完再决定要不要问人）。
1.3 五大能力：收敛到了名字层面
子 Agent（第四篇）。Lead Agent 通过 task 工具派发子 Agent——工具名和 Claude Code 一模一样。内置两个子 Agent（general-purpose 和 bash，连类型名都撞了），支持自定义 Agent 作为子 Agent、接入外部 Agent，并行数由 SubagentLimitMiddleware 封顶。
技能（第五篇）。官方设计原则：技能按需加载，基座保持通用（exactly when relevant and no further）。 ——平时只暴露一行简介，判断用得上时才取完整内容。
记忆（第一篇）。MemoryMiddleware 会话开始时注入持久记忆，会话结束后后台把新信息沉淀进记忆库。
工具与 MCP（第二篇）。沙箱工具、社区工具、MCP 工具、技能自带的工具，统一注册进循环。MCP（连接外部系统的标准协议）是一等公民：支持 OAuth、工具搜索、按需懒加载。
沙箱（前五篇没有）。代码执行的隔离环境，支持路径映射和自定义挂载，另有 SandboxAuditMiddleware 做审计。
1.4 长时任务：循环长在状态图上
同样是循环，DeerFlow 的循环跑在 LangGraph 状态图之上，编译时挂 checkpointer。看得见（执行到哪是图上点亮的节点）、停得下（任意节点可设中断）、续得上（每步存档，进程崩了、人隔天回来都从断点继续）、分得出（子任务并行派发，全部完成再汇总）。
Part 2：对照看设计——收敛到哪里，分叉在哪里
决策一：连 DeerFlow 都收敛到了涌现式循环
让 DeerFlow 出名的 1.0 不是循环，是一条固定流水线：Coordinator 接待分诊 → Planner 生成研究计划 → 人审 → Researcher 和 Coder 并行执行 → Reporter 汇总成文。分解、并行、汇总，每一步都是图上固定的节点。
2.0 做通用底座时，它把这条流水线拆掉了，换成 Lead Agent 的循环：不硬编码工作流，模型临场决定调什么工具、派不派子 Agent。
决策二：长时任务逼出来的三大基础设施
循环长在状态图上。状态图 + checkpoint 把执行变成可随时存档的进度：每过一个节点存一次档，恢复就是读档接着走。
LoopDetectionMiddleware。模型可能陷进死循环：同一个工具反复调、没有进展。人在场时敲一下回车就能打断；长任务人不在场，得由中间件自动检测、注入警告、强制跳出。
ClarificationMiddleware。模型拿不准时怎么办？长任务里"问用户"被做成一个正式中间件动作：拦截澄清请求，转成面向用户的结构化提问。人不在场不等于人不参与——参与点从"随时打断"变成了"被正式询问"。
三件事指向同一条：任务时长一旦超过人的耐心，工程设施就必须接替人做看门人——看门状态（checkpoint）、看门循环（loop detection）、看门沟通（clarification）。
Part 3：用 DeerFlow 复刻
DeerFlow 是配置驱动的 SDK 底座，所以这一篇的"手写"是"组装"——两步：先组装底座，再往上加能力。
3.1 方式一：SDK 组装自己的底座
要造自己的 Agent 产品，就用 SDK 把这副骨架搭起来。写出来会眼熟——第六篇已经用过同一个构造器：

from langchain.agents import create_agent # 示意：中间件与工具来自 deerflow 包，导入路径从简agent = create_agent( model=make_model(), tools=[ sandbox_tools(),  # 沙箱文件/命令工具（决策四的信任底座） mcp_tools(), # MCP 外部系统工具（下一篇的主题） task_tool(subagents=[general_purpose, bash, custom_agents]),# 子 Agent 派发，工具名和 Claude Code 一样 ], system_prompt=BASE_PROMPT, # 基座提示词保持通用，专业能力由技能按需注入（第五篇） middleware=[ SummarizationMiddleware(...), # 历史压缩（第三篇），排最前 MemoryMiddleware(...), # 跨会话记忆注入（第一篇） SubagentLimitMiddleware(max=3), # 并行子 Agent 封顶（第四篇） LoopDetectionMiddleware(), # 死循环检测（决策三） ClarificationMiddleware(), # 拿不准时正式询问用户，排最后 ],) # 运行时挂 checkpoint：长任务可中断、可恢复（1.4）
3.2 方式二：往底座上加能力
底座搭好之后，扩展全是配置和数据，不碰代码。
加技能。一个文件夹加一个 markdown 文件：

skills/data-analysis/├── SKILL.md # frontmatter（name / description）+ 指令正文├── scripts/ # 配套脚本，按需读取└── references/ # 参考材料
加载流程是：发现 → 解析 → 安全扫描 → 相关时注入上下文。注意"安全扫描"这一步——技能是别人写的文本，注入前要先过安检，这是低门槛生态必须配的保险。
加自定义 Agent。写一份 Agent 配置（名字、description、提示词、可用工具），它就自动进入 task 工具的可选名单，供 Lead Agent 按 description 选派——和第四篇子 Agent 定义的三个字段、三个读者完全一致。
接外部系统。在配置里挂 MCP 服务器，外部工具就进了统一注册表，支持 OAuth 鉴权和按需懒加载。连接器标准化到这个程度，已经不需要为每个外部服务写胶水了——这正是下一篇的主题。