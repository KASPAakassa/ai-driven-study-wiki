# Qwen-Agent:阿里通义官方 Agent 框架——@register_tool 与内置 WebUI

> **一句话摘要**:Qwen-Agent 是阿里通义千问官方开源(16.9k stars,Apache-2.0)的 LLM Agent 框架,基于 Qwen 模型的指令遵循、工具使用、规划与记忆能力构建应用,官方明确表示它正作为 Qwen Chat(chat.qwen.ai)的后端运行。工具注册用 `@register_tool` 装饰器(显式参数定义、强约束),内置 Gradio WebUI 一键启动,自带 code_interpreter 代码解释器。
>
> **来源**:GitHub https://github.com/QwenLM/Qwen-Agent;官方文档 https://qwenlm.github.io/Qwen-Agent/;微信公众号《2026年AI Agent构建指南:框架选型与工程实践》(刘律辰),https://mp.weixin.qq.com/s/NTvoC1GE3zuw6Dlo72FTOg

## 概念

**定位**:基于 Qwen 模型构建 Agent 应用——利用 Qwen 的指令遵循、工具使用、规划与记忆能力。它作为 Qwen Chat(chat.qwen.ai)的后端运行,是阿里生态的原生 Agent 框架。

**选 Qwen-Agent 的场景**:快速 Demo / POC——配置最简单、内置 WebUI 无需前端开发、开箱即用的工具(code_interpreter)。

## 原理:核心概念

- **`@register_tool` 工具注册**:装饰器工厂,把工具类注册进全局 `TOOL_REGISTRY` 注册表。`@register_tool('my_image_gen')` 将字符串自动写入类的 `.name` 属性;工具类需继承 `BaseTool`,声明类属性 `description` 和 `parameters`(OpenAI 兼容 JSON Schema),实现 `call(params)`。注册后即可用字符串名字在 `function_list` 中引用——**显式参数定义,结构清晰,强约束,适合复杂参数**;
- **`system_message` 人设**:`Agent.__init__` 参数,指定 LLM 系统提示词;`run()` 时自动插到消息列表首位——**人设(角色定义)与任务流程(上下文指令)分离,便于复用维护**;
- **Agent**:同步 `Agent` 抽象基类,`run()` 是生成器(输入消息列表,输出消息流);子类仅需实现 `_run()`。内置 `BasicAgent`(纯 LLM)、`Assistant`(通用单 Agent:规划+工具+RAG)、`FnCallAgent`、`ReActChat`;
- **内置 WebUI**:`from qwen_agent.gui import WebUI; WebUI(bot).run()`,基于 Gradio 5 一行启动交互页面;
- **多 Agent 协作**:`GroupChat`(对话型,管理发言顺序,支持 auto/round_robin/random/manual 选人、`@成员名` 定向回复、human-in-the-loop);嵌套式 Agent(流程型,把多个 Agent 按流水线组合,各自用独立 prompt/工具/LLM);`MultiAgentHub` 多 Agent 基类;
- **代码解释器**:`code_interpreter` 内置工具,基于本地 Docker 容器把 Python 代码放到隔离沙箱执行并返回结果。

## 代码 / 实现:最小示例

```python
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool
import json5, urllib.parse

@register_tool('my_image_gen')          # 注册到 TOOL_REGISTRY
class MyImageGen(BaseTool):
    description = 'AI绘画服务,输入文本描述返回图片URL'
    parameters = {'type':'object','properties':{'prompt':{'type':'string'}},'required':['prompt']}
    def call(self, params: str, **kwargs) -> str:
        prompt = urllib.parse.quote(json5.loads(params)['prompt'])
        return json5.dumps({'image_url': f'https://image.pollinations.ai/prompt/{prompt}'})

bot = Assistant(llm={'model':'qwen-max-latest','model_type':'qwen_dashscope'},
                system_message='收到请求先画图,再用代码下载处理',
                function_list=['my_image_gen', 'code_interpreter'])
for response in bot.run(messages=[{'role':'user','content':'画一只狗并旋转90度'}]):
    print(response)   # 流式输出

# 配套 GUI:
from qwen_agent.gui import WebUI
WebUI(bot).run()
```

**system_message 示例**(人设与任务流程分离):

```python
system_instruction = '''你是一个乐于助人的AI助手。在收到用户的请求后,你应该:
- 首先绘制一幅图像,得到图像的url,
- 然后运行代码下载该图像。
你总是用中文回复用户。'''
```

## 实践 / 应用:关键特性与局限

### 关键特性

- **内置 WebUI**:Gradio 5,`WebUI(agent).run()` 一键交互演示;
- **工具生态**:内置 `code_interpreter`、`web_search`/`web_extractor`、`image_search`、`image_zoom_in_qwen3vl`、`amap_weather`、`doc_parser`、`retrieval` 等;支持 MCP,在 `function_list` 里用 `{'mcpServers': {...}}` 动态接入 github/filesystem/sqlite 等服务;
- **模型集成**:通过阿里 DashScope API(qwen_dashscope/qwenvl_dashscope/qwenaudio_dashscope)或 OpenAI 兼容服务(vLLM/SGLang/Ollama)接入 Qwen3、Qwen3-VL、Qwen3-Omni、Qwen3-Coder、QwQ、Qwen2.5 全系;
- **ReAct / Function Calling**:`FnCallAgent`、`ReActChat` 基于函数调用构建;内置 hermes 工具调用解析器,支持**并行、多步、多轮**调用;
- **上下文自动管理**:超 `max_input_tokens` 自动裁剪;内置 RAG(BM25+分块,1M token 长文档 QA)。

### 局限

- 与 Qwen 模型绑定较深,换模型厂商成本高;
- `code_interpreter` 依赖本地 Docker,官方声明沙箱仅基础隔离、**生产环境慎用**;
- 当前仅同步 `Agent`(无官方 AsyncAgent);
- WebUI 要求 Python ≥3.10。

## 总结

- **定位**:阿里通义官方 Agent 框架,Qwen Chat 的后端——Qwen 生态原生;
- **工具注册**:`@register_tool` 显式参数定义、强约束,适合复杂参数;
- **上手最快**:`Assistant` + `function_list` + `WebUI(bot).run()` 一行出交互页面;
- **多 Agent**:GroupChat(对话型)与嵌套式 Agent(流程型)两种;
- **注意**:绑定 Qwen 生态、code_interpreter 依赖 Docker 且生产慎用;
- **下一步**:对比 [nanobot](nanobot-framework.md)(同为快速 Demo 轻量方案)与 [AgentScope](agentscope-framework.md)(同为阿里系但平台级)。

## 延伸阅读

- 官方:https://github.com/QwenLM/Qwen-Agent · https://qwenlm.github.io/Qwen-Agent/
- 站内:[nanobot](nanobot-framework.md)、[AgentScope](agentscope-framework.md)(阿里通义平台级)、[LangChain 1.x](langchain-framework.md)(@tool 对比)、[Agent 框架](agent-frameworks.md)
