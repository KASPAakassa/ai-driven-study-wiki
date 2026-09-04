# Agent 框架:从手写到工程化

> **一句话摘要**:Agent 框架把"大脑 + 工具 + 记忆 + 循环"封装成可复用组件;本文对比主流框架、拆解核心抽象,并给出选型与"框架 vs 手写"的权衡。
>
> **来源**:综合公开资料,参考各框架官方文档(LangChain、LangGraph、AutoGen、CrewAI、OpenAI Assistants、Dify、Coze)与社区实践。

## 概念

**Agent 框架(Framework)** 把四大组件(LLM、Tool、Memory、Planning)与 think-act-observe 循环**封装成可复用的抽象与 API**。它解决三类重复劳动:

1. **模型接入**:统一各家 LLM 提供商的 API;
2. **工具与循环**:提供 `@tool` 装饰器、`Agent` 类与执行循环;
3. **编排与控制流**:用 Chain / Graph 描述分支、循环、重试。

### 主流框架一览

| 框架 | 形态 | 特点 | 适合 |
| --- | --- | --- | --- |
| LangChain | 工具库 | 生态最大、组件全 | 快速集成 / 原型 |
| LangGraph | 图编排 | 状态机,支持分支、循环、持久化 | 生产级复杂流程 |
| AutoGen | 多 Agent | agent 相互对话协作 | 多角色研究 |
| CrewAI | 多 Agent | 角色 / 任务建模清晰 | 结构化团队 |
| OpenAI Assistants | 托管 API | 免运维,内置 RAG、工具 | 快速产品化 |
| Dify / Coze | 低代码平台 | 可视化编排 | 业务快速上线 |

## 原理

### 框架的核心抽象

几乎所有框架都围绕五类抽象展开,理解它们即可快速上手任何框架:

1. **LLM 封装(LLMClient)**:统一各家 API,透传温度、max_tokens、tools;
2. **Tool**:`name` + `description` + `func`,装饰器注册并自动生成 tool schema(见《[工具调用](tool-calling.md)》);
3. **Agent**:执行循环的载体——持有 LLM、工具表、记忆,提供 `run()` 与 `max_steps` 护栏;
4. **Workflow / Graph**:控制流。**Chain** 是线性步骤;**Graph** 用节点 + 边表达分支、循环、条件跳转;
5. **Memory**:短期(消息历史)与长期(向量库)的统一接口。

### 执行循环

`Agent.run()` 内部始终是这个循环:

```text
while 未完成 and step < max_steps:
    decision = llm.decide(messages + tools)   # 思考
    if 无 tool_calls: break                    # 收尾
    obs = dispatch(decision)                   # 行动
    messages.append(tool_result(obs))          # 观察回填
```

框架额外提供:并行调用、失败重试、步数/成本限额、流式输出、检查点持久化。

!!! tip "Chain vs Graph 一句话"
    **Chain 是"流水线",Graph 是"状态机"**:路径固定用 Chain,分支/自我纠正/循环用 Graph。这也是 LangChain 团队把重心迁到 LangGraph 的原因。

### 执行模型差异

| 框架 | 执行模型 | 关键差异 |
| --- | --- | --- |
| LangChain | 链 + AgentExecutor | 抽象多、学习曲线陡 |
| LangGraph | 显式图 + 持久化状态 | 控制流看得见、可恢复 |
| AutoGen | 对话式多 agent | 让 agent 互相"聊"出答案 |
| CrewAI | 角色流水线 | 每 agent 一个角色、一份职责 |

## 代码 / 实现

用纯 Python 实现**最小 Agent 框架核心类**:Tool 抽象 + 注册 + 执行循环,呼应前三篇的组件与协议:

```python
"""
最小 Agent 框架核心:Tool(工具)+ MockLLM(大脑)+ Agent(执行循环)。
"""
from dataclasses import dataclass
from typing import Callable, Dict

@dataclass
class Tool:
    """工具抽象:名字 + 描述 + 实现函数。"""
    name: str
    description: str
    func: Callable

    def run(self, **kwargs):
        return self.func(**kwargs)

class MockLLM:
    """模拟 LLM:根据输入、可用工具和已完成动作返回决策(真实框架由大模型完成)。"""

    def decide(self, prompt: str, tools: Dict[str, Tool], done: set):
        if "天气" in prompt and "get_weather" not in done:
            return {"action": "get_weather", "args": {"city": "北京"}}
        if "加" in prompt and "add" not in done:
            return {"action": "add", "args": {"a": 3, "b": 4}}
        return {"action": None, "args": {}}

class Agent:
    """Agent 编排:注册工具 + 执行循环(think -> act -> observe)。"""

    def __init__(self, llm, max_steps=5):
        self.llm = llm
        self.tools: Dict[str, Tool] = {}
        self.max_steps = max_steps
        self.history = []

    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    def run(self, prompt: str):
        done: set = set()                       # 状态:已完成的动作,防重复
        result = None
        for step in range(self.max_steps):
            decision = self.llm.decide(prompt, self.tools, done)
            if decision["action"] is None:      # 无动作 -> 收尾
                result = f"最终答复:{prompt} 已处理,共 {len(self.history)} 步。"
                break
            tool = self.tools[decision["action"]]
            obs = tool.run(**decision["args"])  # act + observe
            done.add(tool.name)                 # 更新状态
            self.history.append((step, tool.name, obs))
            print(f"step{step+1}: {tool.name}{decision['args']} -> {obs}")
            prompt = prompt + f" (工具结果:{obs})"   # 观察回填
        return result or "达到最大步数"

# 具体工具
def get_weather(city: str) -> str:
    return f"{city} 晴,25°C"

def add(a: float, b: float) -> float:
    return a + b

if __name__ == "__main__":
    agent = Agent(MockLLM())
    agent.register_tool(Tool("get_weather", "查询天气", get_weather))
    agent.register_tool(Tool("add", "加法", add))
    print(agent.run("我想知道北京的天气,并算一下 3 加 4"))
```

**运行**:`python3 mini-framework.py`,纯标准库。对照真实框架:

- `Tool` ≈ LangChain 的 `@tool` 产物,真实框架还会自动生成 tool schema;
- `MockLLM.decide` ≈ `llm.chat(messages, tools=tool_schemas)` 并解析返回的 `tool_calls`;
- `Agent` 循环与 ReAct 同构,真实框架再加并行调用、重试、流式、持久化;
- `history` 是最简记忆;换成向量库检索即长期记忆接入点;
- `done` 集合是"状态管理"的最小示例——没有它 Agent 会反复调用同一工具而卡死。

## 实践 / 应用

### 怎么选型

| 你的情况 | 优先选择 |
| --- | --- |
| 快速原型 / 现成生态 | LangChain |
| 复杂控制流、上生产、需恢复 | LangGraph |
| 多 agent 协作 | AutoGen / CrewAI |
| 不想运维、托管 API | OpenAI Assistants |
| 低代码 / 业务人员 | Dify / Coze |

### 框架 vs 手写

| 维度 | 用框架 | 手写 |
| --- | --- | --- |
| 起步速度 | 快 | 慢 |
| 可控性 | 中,有黑盒 | 高 |
| 依赖风险 | 升级可能破坏 | 零依赖 |
| 调试 | 需懂框架内部 | 直接看代码 |
| 生产稳定性 | 社区 patch 快 | 自己踩坑 |

!!! warning "实践建议"
    建议**先用框架跑通端到端**(验证工具、记忆、护栏是否够用);若瓶颈在框架抽象/性能/黑盒上,再**手写核心循环 + 只依赖 LLM API**。多数中小应用,几百行手写 + 一个工具注册表完全够用——你刚在本文代码里就写出来了。

## 总结

- 框架把四大组件与循环封装成 LLM / Tool / Agent / Graph / Memory 五类抽象。
- 主流:LangChain(生态)、LangGraph(生产图编排)、AutoGen/CrewAI(多 agent)、Assistants(托管)、Dify/Coze(低代码)。
- Chain 是流水线,Graph 是状态机;分支、循环、重试用 Graph。
- 框架省起步、手写保可控:先用框架验证,再按需手写核心。

**下一步**:回到《[AI Agent 入门](agent-intro.md)》复习全貌,或读《[工具调用](tool-calling.md)》深挖协议;多 agent 协作、生产观测可从框架文档继续深入。

## 延伸阅读

- 站内:[AI Agent 入门](agent-intro.md)、[Agent 核心组件](agent-core-components.md)、[工具调用](tool-calling.md)、[LLM 基础](../02-llm/index.md)
- 外部:LangChain / LangGraph 官方文档;Microsoft AutoGen 文档;CrewAI 文档;OpenAI Assistants API 文档;Dify / Coze 平台文档
