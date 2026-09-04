# 工具调用(Tool Calling):让模型操纵真实世界

> **一句话摘要**:Tool Calling 让 LLM 输出结构化的"调用意图"而非纯文本,宿主执行真实函数并回填结果;本文讲清原理、API 格式、schema 要点与安全边界。
>
> **来源**:综合公开资料,参考 OpenAI / Anthropic 官方 Function Calling 与 Tool Use 文档。

## 概念

**Tool Calling(工具调用 / Function Calling)** 是 LLM 与外部世界的标准接口,核心约定:

> **模型只输出"想调用哪个函数、参数是什么"的结构化描述;执行永远发生在宿主侧。**

为什么?① **能力边界**:LLM 不会查库、发请求、读写文件;② **可靠性**:`tool_calls` 是训练过的输出形态,比解析自由文本稳定;③ **安全可控**:宿主执行前可做权限校验与审计。

!!! note "为什么不叫 function executing"
    模型只是"提议"调用,决定权与执行权都在宿主。这层剥离是安全的根基:模型可能被骗(被注入),宿主仍可拒绝执行。

## 原理

### 完整流程

```
1. 组装 messages + tools → 调 LLM API
2. 返回 tool_calls[name + arguments] → 宿主解析、执行
3. 结果以 role:"tool" 回填(tool_call_id 关联)
4. 模型再决策:调工具或直接答复;循环至无 tool_calls
```

关键点:回填后模型看到的不仅是结果字符串,还有**哪次调用产生了它**(`tool_call_id` 关联),这是并行调用不错乱的前提。

### OpenAI 兼容 API 的请求与返回

**请求侧发 `tools`**:每个工具是一个 JSON Schema:

```json
{"type": "function", "function": {
  "name": "get_weather",
  "description": "查询指定城市的当前天气",
  "parameters": {
    "type": "object",
    "properties": {"city": {"type": "string"}},
    "required": ["city"]}}}
```

**返回侧收 `tool_calls`**:

```json
{"choices": [{"message": {
  "role": "assistant",
  "content": null,
  "tool_calls": [{
    "id": "call_abc123",
    "type": "function",
    "function": {"name": "get_weather", "arguments": "{\"city\":\"北京\"}"}
  }]
}}]}
```

注意:① `arguments` 是**字符串**,需 `json.loads`;② 这轮 `content` 常为 `null`。宿主把结果追加回对话:

```json
{"role": "tool", "tool_call_id": "call_abc123", "content": "北京 今天晴,25°C"}
```

### tool schema 设计要点

| 要点 | 说明 |
| --- | --- |
| name 简短小写 | 如 `get_weather` |
| description 写清何时用 | 模型靠它选工具 |
| parameters 声明类型 | 缺省会让模型乱传 |
| required 标必需参数 | 可省参数别写进 required |
| 数量适度 | 太多稀释注意力、误选率升高 |

### 工具结果回填的细节

- 一条 `tool_calls` 可含**多个并行调用**,逐条按 `tool_call_id` 回填;
- **失败也要回填**:异常消息作为 `content` 返回,模型据此自愈(重试 / 换工具);
- 循环直到模型输出正常 `content` 或达最大轮数。

!!! warning "安全:两条红线"
    **权限**:按"最小权限"实现——只读可放开,删除/写入/付款必须白名单 + 人工确认。**注入**:工具返回内容可能含恶意指令,须把工具结果当作**不可信数据**,不拼进 system prompt,必要时做指令边界隔离。

### 深化:MCP——工具生态的标准化(N×M → N+M)

Function Calling 解决了"**模型怎么调工具**",MCP(Model Context Protocol,Anthropic 提出)解决"**工具从哪来**":

!!! tip "为什么需要 MCP"
    以前每接一个外部系统都要写一套封装:接 Slack 写一套、接 Notion 写一套、接数据库再写一套——**N 个框架 × M 个外部系统 = N×M 的地狱**。MCP 把"工具提供方"与"工具使用方"解耦:**N+M 替代 N×M**——这就是"Agent 的 USB-C 接口"的含义。

**三层架构**:

```
Host(宿主应用:Claude Desktop / 你的 Agent 框架)
 └─ Client(协议客户端,与 Server 一对一连接)
     └─ Server(能力提供方:GitHub MCP Server、数据库 MCP Server…)
```

**Server 可暴露三类能力**:

| 能力 | 类比 | 说明 |
| --- | --- | --- |
| **Tools** | 可调用的函数 | 执行动作,如"创建 Issue""执行查询" |
| **Resources** | 可读取的数据(GET 接口) | 文件、数据库记录、代码片段 |
| **Prompts** | 预置提示词模板 | 复用特定任务的工作流 |

**传输层**:`stdio`(本地进程,子进程通信)与 `HTTP`(远程服务,跨机器);主流框架与客户端普遍支持。

**与 Function Calling 的分工**(作者判断):Function Calling 是**模型层标准**(已站稳);MCP 是**生态层标准**(2026 年仍早期但势头猛)。工程建议:**新工具优先做成 MCP Server 形态**,换框架不用重写;老工具用 Function Calling 包一层也能跑。

!!! warning "MCP 是新的信任边界"
    接入第三方 MCP Server 等于把"外部系统"接进 Agent——工具投毒、遮蔽(shadowing)、凭证窃取是真实风险;第三方 Server 要按不可信对待,做权限最小化与审计(详见 [AI Friendly 后端架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md) 的 Harness 工具层与安全横切)。

## 代码 / 实现

纯 Python 模拟 OpenAI 兼容 API 的完整工具调用闭环(组装 tools → 返回 tool_calls → 执行 → 回填):

```python
"""
模拟 OpenAI 兼容 API 的工具调用流程:
组装 tools 请求 → 模型返回 tool_calls JSON → 解析执行 → 结果回填。
"""
import json

# 1. 工具定义(发给模型的 schema)
TOOLS = [
    {"type": "function", "function": {
        "name": "get_weather",
        "description": "查询指定城市的当前天气",
        "parameters": {"type": "object",
                       "properties": {"city": {"type": "string", "description": "城市名"}},
                       "required": ["city"]}}},
    {"type": "function", "function": {
        "name": "calculator",
        "description": "计算一个数学表达式的结果",
        "parameters": {"type": "object",
                       "properties": {"expression": {"type": "string"}},
                       "required": ["expression"]}}},
]

# 2. 工具实现
def get_weather(city: str) -> str:
    return f"{city} 今天晴,25°C"

def calculator(expression: str) -> str:
    return str(eval(expression))  # 演示用;生产环境禁用 eval

IMPLEMENTATIONS = {"get_weather": get_weather, "calculator": calculator}

# 3. 模拟 LLM:按用户输入返回 tool_calls 或最终答复
def mock_llm(messages):
    last = messages[-1]["content"].lower()
    if "天气" in last:
        return {"choices": [{"message": {"role": "assistant", "content": None,
            "tool_calls": [{"id": "call_1", "type": "function",
                "function": {"name": "get_weather", "arguments": json.dumps({"city": "北京"})}}]}}]}
    if "计算" in last:
        return {"choices": [{"message": {"role": "assistant", "content": None,
            "tool_calls": [{"id": "call_2", "type": "function",
                "function": {"name": "calculator", "arguments": json.dumps({"expression": "7 * 8"})}}]}}]}
    return {"choices": [{"message": {"role": "assistant",
        "content": "已处理完毕:北京今天晴,25°C;7×8=56。"}}]}

def run_agent(user_input):
    messages = [{"role": "user", "content": user_input}]
    for _ in range(3):                      # 最多 3 轮工具调用
        msg = mock_llm(messages)["choices"][0]["message"]
        if not msg.get("tool_calls"):       # 没有工具调用 -> 收尾
            return msg["content"]
        messages.append(msg)                # 保留 assistant 消息
        for call in msg["tool_calls"]:      # 4. 逐个执行
            fn = call["function"]
            args = json.loads(fn["arguments"])
            result = IMPLEMENTATIONS[fn["name"]](**args)
            print(f"调用 {fn['name']}{args} -> {result}")
            messages.append({"role": "tool",     # 5. 结果回填
                             "tool_call_id": call["id"], "content": str(result)})
    return "超出最大工具调用轮次"

if __name__ == "__main__":
    print(run_agent("帮我查北京的天气"))
    print(run_agent("帮我计算 7 * 8"))
```

**运行**:`python3 tool-calling-demo.py`,纯标准库。要点:

- `TOOLS` 即真实 API 的 `tools` 参数原样,生产可用工具类自动生成;
- `mock_llm` 的返回字段与真实 OpenAI 响应一致——替换成 `openai` 客户端即可;
- `arguments` 是字符串,必须 `json.loads` 后解包为 `**args`;
- 结果按 `tool_call_id` 回填,循环直到模型给正常 `content`。

## 实践 / 应用

- **何时用**:需要实时数据(天气、搜索、DB)、确定性计算或副作用(发邮件、下单)时;纯问答不需要。
- **成本与调试**:schema 占 token,结果过长可截断/摘要,设最大轮数;打印 `messages` 排查——"工具没生效"多半是回填格式错(缺 `tool_call_id`)。
- **注入防护**:结果含"忽略上文指令"时模型可能照做。对策:工具结果用 `<tool_result>` 包裹并声明不可信;敏感操作加人工确认;关键动作由宿主策略决定。

## 总结

- Tool Calling = 模型输出意图(JSON)+ 宿主执行 + 结果回填,循环至完成。
- 请求侧发 `tools`(JSON Schema),返回侧收 `tool_calls`;schema:描述清、类型全、数量适度。
- 工程三件套:失败也回填、`tool_call_id` 关联、设最大轮数。
- 安全:最小权限 + 工具结果视为不可信数据。

**下一步**:看《[Agent 核心组件](agent-core-components.md)》中工具注册与分发如何与 tool calling 衔接,再学《[Agent 框架](agent-frameworks.md)》中的框架级抽象。

## 延伸阅读

- 站内:[AI Agent 入门](agent-intro.md)、[Agent 核心组件](agent-core-components.md)、[Agent 框架](agent-frameworks.md)
- 外部:OpenAI *Function calling / Tool use* 文档;Anthropic *Tool use* 文档;JSON Schema 规范
