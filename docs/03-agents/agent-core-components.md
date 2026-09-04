# Agent 核心组件:大脑、工具、记忆与规划如何协作

> **一句话摘要**:Agent 由 LLM(大脑)、工具(行动)、记忆(经验)、规划(策略)四部分组成;本文拆解每部分职责与实现机制,并演示协作骨架。
>
> **来源**:综合公开资料,参考 Lilian Weng《LLM Powered Autonomous Agents》、LangChain 文档与 ReAct 论文(Yao et al., 2022);Planner/Executor 角色拆分与落地清单补充自微信公众号《AI Agent 系统架构:Planner、Executor、Memory、Tools 如何协作》(小加号编程笔记,https://mp.weixin.qq.com/s/ydW5OMVOFE5JGCdrtlwzOA),素材存档于 `docs/inbox/agent-architecture-4modules-source.md`

## 概念

Agent 是**四类组件 + 一个编排循环**的组合:

| 组件 | 英文 | 职责 | 类比 |
| --- | --- | --- | --- |
| 大模型 | LLM | 理解、推理、决策 | 大脑 |
| 工具 | Tool | 执行外部操作 | 手脚 |
| 记忆 | Memory | 保存上下文与经验 | 笔记 |
| 规划 | Planning | 拆解目标、排顺序 | 项目经理 |

四者由 **agent loop(编排循环)** 串起:LLM 思考 → 规划定步骤 → 工具执行 → 观察回填记忆 → 再次思考。

## 原理

### LLM 作为大脑

LLM 承担三种认知职能:

1. **理解**:把用户意图、工具返回、历史状态解析成结构化信息;
2. **推理**:基于当前状态推导下一步(调哪个工具?参数是什么?);
3. **决策输出**:通过 **tool calling** 输出机器可解析的动作指令。

!!! tip "LLM 为什么能当大脑"
    LLM 经过指令微调,能遵循"你是一个 Agent"的设定并按 JSON schema 输出动作;它的**上下文学习**能力让它能靠 few-shot 学会新工具——"换一套工具"几乎不用改代码。

### 工具调用(tool calling)

**Tool Calling** 是 LLM 与外部世界的接口:模型不直接执行代码,而是输出**结构化的"调用意图"**(函数名 + 参数 JSON),由宿主真正执行。

宿主侧解决两件事:

- **注册(register)**:维护"名字 → 函数实现"的映射表;
- **分发(dispatch)**:按 LLM 输出的名字查表调用,并处理"名字不存在"等异常。

这正是本文代码的核心,也是各类框架 Tool 抽象的雏形。

### 记忆:短期 vs 长期

| 维度 | 短期记忆 | 长期记忆 |
| --- | --- | --- |
| 载体 | 上下文窗口、消息数组 | 向量数据库 + embedding |
| 内容 | 当前任务、最近对话、工具结果 | 历史任务、用户偏好、领域知识 |
| 访问 | 全部直接可见 | 检索式:相似度取 top-k |
| 问题 | 上下文爆掉 | 检索不准、时效差 |

长期记忆的本质是 **RAG**:信息切块 → embedding → 存向量库 → 按相似度召回。窗口一关短期记忆即清空;长期记忆却在下次任务继续可用——这是"越用越懂你"的关键。

### 规划:三种典型模式

1. **任务分解(Task Decomposition)**:把大目标拆成有序子任务,如"写报告" → "收集 → 分析 → 起草 → 校对"。
2. **ReAct**:推理与行动**交替**,每一步按最新观察决定(见《[AI Agent 入门](agent-intro.md)》),适合探索性任务。
3. **Plan-and-Execute**:先产出**完整计划**再逐条执行,可修订;适合步骤明确的长期任务,减少中途决策的 LLM 调用。

| 模式 | 计划时机 | 灵活性 | 调用次数 | 适用 |
| --- | --- | --- | --- | --- |
| 任务分解 | 先拆分 | 中 | 中 | 独立子任务 |
| ReAct | 边做边想 | 高 | 高 | 探索 / 不确定 |
| Plan-and-Execute | 先计划 | 中 | 低 | 长流程、步骤已知 |

### 组件如何协作

```text
LLM 思考 → 规划定步骤 → tool calling 输出 get_weather("北京")
→ 工具执行返回结果 → 观察写回记忆 → LLM 再次思考 → ... → 汇总答复
```

记忆是"全局变量",规划是"控制流",工具是"函数调用",LLM 是"决策执行器"——理解分层后读任何框架文档都很快。

### Planner 与 Executor:角色拆分的工程视角

在复杂系统里,"规划"这一职责常被拆成两个显式角色——**Planner(决定怎么做)** 与 **Executor(负责去做)**,再配合 Memory(记住该记的)与 Tools(连接外部世界):

| 模块 | 像团队里的谁 | 主要作用 |
| --- | --- | --- |
| Planner | 架构师/项目经理 | 理解目标、拆解计划、排优先级,决定"怎么做" |
| Executor | 执行工程师 | 按计划一步步执行,调用工具、读取反馈 |
| Memory | 记事本 | 保存上下文与经验,带上"该带的"上下文 |
| Tools | 工具箱 | 连接外部世界:查资料、改文件、跑命令 |

**关键:Planner 和 Executor 不一定要拆成两个模型**——可以是同一个模型在不同阶段扮演不同角色,也可以用不同模型分别负责。关键是**职责要分清**:规划阶段先想清楚怎么做,执行阶段专注把每一步做对,避免"边想边做"在复杂任务中失控(这与 [AI Agent 入门](agent-intro.md) 中 ReAct vs Plan-and-Execute 的模式选择呼应——计划先行适合步骤明确的长任务)。

### 一次 Agent 任务的完整时序

```
用户目标 → Planner 确认目标与边界(改风格?改结构?改错别字?)
  → Planner 拆解为计划(需要什么信息、分几步、哪些要查证)
  → Executor 逐步执行:调用 Tools(读文件/查资料/跑命令)
  → 每步结果写入 Memory(带上该带的上下文,丢弃无关历史)
  → 遇到不确定:查证 / 转人工 / 承认不确定
  → 完成后检查结果(改了代码要跑测试,生成了图要看图)
```

**靠谱的 Agent 会在动手前先确认目标和边界**——比如你说"帮我改文章",它最好知道是改风格、改结构、改错别字,还是改成另一种受众,而不是马上开干。

## 代码 / 实现

下面用纯 Python 实现**工具注册表 + 按名字分发**的调度器,这正是"工具"组件的最小骨架。顺带用标准库 `ast` 实现一个安全的表达式计算器(不依赖 `eval`):

```python
"""最小工具调度器:注册 + 按名字分发,演示"工具"组件的骨架。"""
import ast
import inspect
import operator

_BINOPS = {ast.Add: operator.add, ast.Sub: operator.sub,
           ast.Mult: operator.mul, ast.Div: operator.truediv,
           ast.Pow: operator.pow}

def safe_calc(expr: str) -> float:
    """白名单安全求值:数字 + 四则 + 幂(不用 eval)。"""
    def _eval(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _BINOPS:
            return _BINOPS[type(n.op)](_eval(n.left), _eval(n.right))
        raise ValueError(f"不支持的表达式:{expr}")
    return _eval(ast.parse(expr, mode="eval").body)

class ToolRegistry:
    """按名字管理工具的注册表。"""

    def __init__(self):
        self._tools = {}

    def register(self, name=None):
        """装饰器:把函数注册为工具。"""
        def decorator(fn):
            self._tools[name or fn.__name__] = fn
            return fn
        return decorator

    def dispatch(self, name, *args, **kwargs):
        """按名字调用工具;未注册则抛 KeyError。"""
        if name not in self._tools:
            raise KeyError(f"未注册的工具:{name}")
        return self._tools[name](*args, **kwargs)

    def list_tools(self):
        """列出可用工具及签名,供 LLM 参考。"""
        return {n: str(inspect.signature(f)) for n, f in self._tools.items()}

registry = ToolRegistry()

@registry.register()
def get_weather(city: str) -> str:
    return f"{city} 25°C 晴"

@registry.register(name="calculator")
def calc(expr: str) -> float:
    return safe_calc(expr)

@registry.register()
def save_note(content: str) -> str:
    return f"已保存笔记,共 {len(content)} 字"

if __name__ == "__main__":
    print("可用工具:", registry.list_tools())
    for name, arg in [("get_weather", "北京"),
                      ("calculator", "7 * 8 + 2 ** 3"),
                      ("save_note", "明日计划")]:
        print(f"{name}({arg!r}) -> {registry.dispatch(name, arg)}")
    try:
        registry.dispatch("nonexist")
    except KeyError as e:
        print("异常捕获:", e)
```

**运行**:`python3 tool-registry-demo.py`,纯标准库。要点:

- `register` 装饰器把函数登记进 `_tools`(可起别名)——框架靠它把 LLM 输出的名字映射到实现;
- `dispatch` 是"分发"核心:查表、调用、异常兜底,比写一长串 `if-else` 简洁,新增工具只需一行装饰器;
- `list_tools` 暴露签名信息,真实场景中会被转成 tool schema 交给 LLM(见《[工具调用](tool-calling.md)》);
- `safe_calc` 用 AST 白名单求值,演示"工具内部也要防恶意输入"。

## 实践 / 应用

- **记忆选型**:对话助手用短期记忆即可;需"记住偏好/历史事实"时上向量库;预算紧张可用 `sqlite` 或搜索索引替代。
- **规划选型**:探索型任务用 ReAct;批量流水线用 Plan-and-Execute;独立子任务用分解 + 并行。
- **工程要点**:① 工具注册带**描述与参数 schema**,否则 LLM 不会用;② dispatch 捕获异常,报错回填让 LLM 自愈;③ 记忆设上限(TTL/条数),防上下文膨胀。

### 工具权限分级(工程事故高发区)

Agent 工程里很多事故,不是模型不够聪明,而是**工具边界太随意**。工具要分级:

- **读工具和写工具分开**——读操作放开,写操作收紧;
- **高风险工具默认不开放**——删除、支付、部署等默认拒绝,按需显式授权;
- **写操作保留审计**——谁、何时、改了什么,全程可追溯;
- **重要操作需要用户确认**——human-in-the-loop;
- **工具返回结果要结构化**——便于 LLM 解析与后续决策。

### 普通用户判断 Agent 靠不靠谱的五个问题

即使不是开发者,也可以用这套框架判断一个 Agent 的表现:

1. **它有没有先理解目标?** 靠谱的 Agent 会先确认目标和边界,而不是马上开干;
2. **它有没有计划?** 复杂任务里完全不说明计划,后面很容易跑偏(计划不需要长,但应该让你知道它准备怎么做);
3. **它会不会使用外部证据?** 涉及事实/代码/文件/数据时,靠谱的 Agent 会查资料、读文件、跑命令,而不是凭空回答;
4. **它会不会承认不确定?** 该查证时查证,该转人工时转人工,该说"不确定"时说"不确定";
5. **它有没有检查结果?** 改了代码却不跑测试、生成图片却不看图、写文章却不检查链接——那只是完成了动作,还没完成任务。

## 总结

- 四大组件:LLM(推理决策)、Tool(外部执行)、Memory(短期上下文 + 长期向量记忆)、Planning(三种模式)。
- 协作骨架:**LLM 决策 → 工具执行 → 观察回填记忆 → 再决策**,由 agent loop 驱动。
- 工具组件最小实现是"注册表 + 按名分发",代码可复用。
- 选型:记忆看"是否需跨任务保留",规划看"任务是否可预判"。

**下一步**:深入《[工具调用](tool-calling.md)》看 LLM 与工具间的 JSON 协议,再看《[Agent 框架](agent-frameworks.md)》如何工程化。

## 延伸阅读

- 站内:[AI Agent 入门](agent-intro.md)、[工具调用](tool-calling.md)、[Agent 框架](agent-frameworks.md)、[LLM 基础](../02-llm/index.md)
- 外部:Lilian Weng, *LLM Powered Autonomous Agents* (2023);Yao et al., *ReAct* (2022);OpenAI *Function calling* 文档
