# 🧪 配套开源方案:协议、沙箱与评测

> Harness 生态的支撑设施:工具调用协议、代码/云沙箱、评测基准与数据集。它们不直接是 Harness,但决定 Harness 的能力边界与可信度。

## 概念

一个可用的 Harness 至少需要三类配套:**协议**(agent 如何调用外部工具)、**沙箱**(agent 在什么环境里执行代码/命令,保证安全)、**评测**(如何量化 agent 的好坏,形成迭代闭环)。本页收录这三类的开源代表。

## 清单

### 协议与工具生态

| 名称 | 仓库 | 一句话定位 |
| --- | --- | --- |
| **MCP(Model Context Protocol)** | [modelcontextprotocol/modelcontextprotocol](https://github.com/modelcontextprotocol/modelcontextprotocol) | Anthropic 提出的工具/上下文接入标准协议,已成为事实上的"工具调用 USB-C";主流框架与客户端普遍支持 |
| **A2A(Agent-to-Agent)** | [a2aproject/a2a](https://github.com/a2aproject/a2a) | Google 主导的 Agent 间通信协议(2025.4 推出,150+ 组织);与 MCP 分工:MCP 管 agent-to-system,A2A 管 agent-to-agent;AAIF/Linux Foundation 托管,正走向 IETF 标准化 |
| **skills.sh**(分发) | 见 [skills.sh](https://skills.sh/mattpocock/skills)(工具站,mattpocock/skills 的 README 使用) | 面向 agent 的 skill 分发/版本管理工具(如 `npx skills@latest add mattpocock/skills`) |

### 沙箱与执行环境

| 名称 | 仓库 | 一句话定位 |
| --- | --- | --- |
| **E2B** | [e2b-dev/E2B](https://github.com/e2b-dev/E2B) | 面向 AI 应用的云沙箱:agent 在隔离容器里安全执行代码,支持超时、快照、恢复 |
| **Daytona** | [daytonaio/daytona](https://github.com/daytonaio/daytona) | 开发环境/沙箱管理平台,可编程创建隔离工作区供 agent 使用 |

### 记忆与上下文管理

| 名称 | 仓库 | 一句话定位 |
| --- | --- | --- |
| **TencentDB Agent Memory** | [TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory) | 团队级 Agent 记忆中枢:L0-L3 四层记忆 + 上下文卸载省 Token,支持 Hermes/OpenClaw,详见 [专题收录](agent-memory-plugin.md) |

### 评测基准与数据集

| 名称 | 仓库 | 一句话定位 |
| --- | --- | --- |
| **SWE-bench** | [princeton-nlp/SWE-bench](https://github.com/princeton-nlp/SWE-bench) | 编码 Agent 事实标准基准:用真实 GitHub issue + 测试修复任务评估 agent 能力 |
| **τ-bench(tau-bench)** | [sierra-research/tau-bench](https://github.com/sierra-research/tau-bench) | 面向"工具调用 agent"的评测:用户模拟 + 结构化工具环境,评估真实场景任务 |
| **PinchBench** | [pinchbench/skill](https://github.com/pinchbench/skill) | 面向 OpenClaw 的长程 Agent 性能基准,强调真实工作场景任务模拟 |
| **WildClawBench** | [InternLM/WildClawBench](https://github.com/InternLM/WildClawBench) | "野生环境"评测:把长程 Agent 丢进真实用户使用场景检验生存能力 |

## 实践 / 应用:怎么用这些配套

1. **接工具**:优先选支持 MCP 的框架/客户端——工具一次编写、到处复用(见 [03-agents/工具调用](../03-agents/tool-calling.md));
2. **控安全**:代码执行类任务配 E2B/Daytona 沙箱,配合 [权限分级](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md) 思路;
3. **建评测**:编码任务用 SWE-bench 风格(真实 issue + 测试),工具调用任务用 τ-bench 风格(用户模拟 + 结构化环境);参考 [Agent 评测](../03-agents/agent-evaluation.md) 的方法论(Rubric 二元化、Bad/Good Case 数据飞轮)。

## 延伸阅读

- 站内:[Harness 章节首页](index.md)、[Agent 评测](../03-agents/agent-evaluation.md)、[工具调用](../03-agents/tool-calling.md)、[AI Friendly 后端架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md)(Harness 七层设计)
- 外部:SWE-bench 论文(ICLR 2024)、《AgentEval》等评测相关文献
