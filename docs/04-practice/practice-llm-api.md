# 调用 LLM API 构建应用:Chat Completions 实战手册

> **一句话摘要**:以 OpenAI 兼容 API 为例,讲清 chat completions、系统提示、流式输出、function calling、结构化输出这五大能力,给出可直接复制的代码与成本/限流/重试工程要点。
>
> **来源**:OpenAI API 官方文档、OpenAI 兼容协议(DeepSeek / Moonshot / vLLM 均遵循),代码为本项目整理。

## 概念

- **Chat Completions API**:当前 LLM 应用的主流接口。客户端把"消息列表"发给服务端,模型返回补全回复,专为多轮对话设计。
- **OpenAI 兼容协议**:`POST {base_url}/v1/chat/completions`,请求/响应均为 JSON。OpenAI、DeepSeek、Moonshot 与本地 vLLM、Ollama 都实现该协议——学会一次,处处可用。
- **消息结构**:每条消息有 `role`(system / user / assistant / tool)与 `content`。对话 = 消息列表,模型"记得"列表里的一切。
- **为什么值得学**:RAG、Agent、微调的前置能力都是"会调用模型";把 API 工程要点吃透,后续所有 LLM 应用都受益。

## 原理

### 一次请求发生了什么

```
你的代码 --(HTTP POST, JSON)--> API 网关 --> 模型推理 --> 流式返回 token --> 解析使用量
```

- **temperature**:采样随机性。0 接近贪心(稳定、适合工具/结构化输出),0.7~1.3 更有创造力;它不是"准确度旋钮",而是"随机性旋钮"。
- **max_tokens**:限制本次输出的最大 token 数,截断时 `finish_reason` 为 `length`。
- **token**:模型处理文本的基本单位,约 0.75 英文单词/汉字,计费与上下文窗口都以它计。
- **上下文窗口**:`input + output tokens` 不能超过模型上限(如 128k),历史过长会被截断或报错。

### 响应结构(关键字段)

```json
{
  "id": "chatcmpl-...",
  "choices": [{"message": {"role": "assistant", "content": "回复内容"}, "finish_reason": "stop"}],
  "usage": {"prompt_tokens": 30, "completion_tokens": 45, "total_tokens": 75}
}
```

## 代码 / 实现

!!! note
    依赖 `pip install openai`(v1+)。代码**不要求本地运行**,但需设置环境变量 `OPENAI_API_KEY`。

```python
import os
from openai import OpenAI

# 兼容其他服务商可加 base_url,如 OpenAI(base_url="https://api.deepseek.com")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# ---------- 1. 基础对话 + 系统提示 ----------
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    temperature=0.7,
    messages=[
        {"role": "system", "content": "你是一位严谨的数学老师,回答必须分步骤。"},
        {"role": "user", "content": "解释一下梯度下降的原理"},
    ],
)
print(resp.choices[0].message.content)

# ---------- 2. 流式输出(SSE):首字快、体验好 ----------
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "写一首关于 numpy 的四句诗"}],
    stream=True,
)
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
print()

# ---------- 3. Function Calling:让模型调用你的函数 ----------
def get_weather(city: str) -> str:
    return "晴天 26°C"            # 你的真实函数:查数据库 / 调外部 API

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询指定城市的天气",
        "parameters": {"type": "object",
                       "properties": {"city": {"type": "string"}},
                       "required": ["city"]},
    },
}]

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "北京今天天气如何?"}],
    tools=tools,
)
msg = resp.choices[0].message
if msg.tool_calls:                 # 模型请求调用函数,参数在 tool_calls 里
    call = msg.tool_calls[0]
    city = eval(call.function.arguments)["city"]   # 生产环境用 json.loads
    result = get_weather(city)
    # 把函数结果以 tool 角色回填,让模型组织成自然语言回复
    reply = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "北京今天天气如何?"}, msg,
                  {"role": "tool", "tool_call_id": call.id, "content": result}],
    )
    print(reply.choices[0].message.content)

# ---------- 4. 结构化输出:强制 JSON,喂给下游程序 ----------
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "从「北京今天 30 度,明天降温到 22 度」中提取信息"}],
    response_format={"type": "json_object"},
)
print(resp.choices[0].message.content)   # 输出为合法 JSON
```

- 关键点:系统提示负责"行为约束";function calling 的 `tools` 描述就是"工具手册"。流式输出用 SSE 逐 token 返回,首字延迟大幅降低;function calling 是 Agent 基石——模型只生成参数,真正执行在你的进程里。结构化输出务必 `json.loads` + 异常兜底。

> 生产环境的 function calling 参数解析应使用 `import json; args = json.loads(call.function.arguments)`,而不是 `eval`。

## 实践 / 应用

### 成本估算(纯 Python,可直接运行)

```python
def estimate_tokens(text):
    """粗略估算 token 数:英文约 4 字符/token。"""
    return max(1, len(text) // 4)

def cost_usd(in_tokens, out_tokens, price_in=0.50, price_out=1.50):
    """单价单位:美元/每百万 token。"""
    return in_tokens * price_in / 1e6 + out_tokens * price_out / 1e6

in_t, out_t = estimate_tokens("请总结这篇文章" * 10), 800
print(f"约 {in_t} 输入 + {out_t} 输出 token, 成本 ≈ ${cost_usd(in_t, out_t):.5f}")
```

!!! tip "计价要点"
    按 prompt_tokens + completion_tokens 分开计费,输出通常更贵(1.5~3 倍);长上下文 RAG 的成本大头是反复发送的 prompt,可用缓存或压缩历史降低。

### 限流、重试与超时工程要点

| 问题 | 现象 | 对策 |
|---|---|---|
| 超时 | 请求挂起 | 设 `timeout=30`;流式用 `max_retries` 控制 |
| 限流(429) | 并发一高就报错 | 指数退避重试 + 请求限速 |
| 服务错误(5xx) | 偶发失败 | 指数退避重试(3~5 次) |
| 输出截断 | `finish_reason=length` | 调大 `max_tokens` 或让模型精简 |
| token 超限 | 400 错误 | 截断历史消息、摘要压缩旧轮次 |

**指数退避重试(纯 Python,可直接运行)**:

```python
import random, time

def retry_with_backoff(fn, max_retries=3, base=1.0, errors=(Exception,)):
    """失败后 1s/2s/4s 递增等待 + 随机抖动,防雪崩。"""
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except errors:
            if attempt == max_retries:
                raise
            wait = base * (2 ** attempt) + random.uniform(0, 0.5)
            time.sleep(wait)

# 用法: retry_with_backoff(lambda: client.chat.completions.create(...))
```

### 工程清单

- [ ] 密钥用环境变量/密钥管理,绝不硬编码进仓库;
- [ ] 所有外部响应先 `json.loads` 再使用,失败有兜底;
- [ ] 结构化输出优先用 `json_schema`,生产用流式 + 超时 + 重试 + mock 测试。

## 总结

- Chat Completions 是"消息列表进、回复出"的统一协议,OpenAI 兼容端点处处可用。
- 四大能力:系统提示控人设、流式控体验、function calling 接外部世界、结构化输出喂程序。
- 工程三件套:**超时 + 指数退避重试 + 限流**,是 LLM 应用稳定性的底线。
- 成本按输入/输出分开计费,长上下文 RAG 是成本大头,需缓存与压缩。
- 下一步:把它接进 Agent 循环,或学 RAG 的检索与上下文组装。

## 延伸阅读

- 站内:[工具调用 Tool Calling](../03-agents/tool-calling.md)、[Agent 核心组件](../03-agents/agent-core-components.md)
- 外部:OpenAI Cookbook(streaming / function_calling 示例);DeepSeek / Moonshot 兼容模式文档;Anthropic "Building effective agents"。
