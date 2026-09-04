# Headroom:AI Agent 的上下文压缩层(开源专题收录)

> **一句话摘要**:Headroom(The context compression layer for AI agents)在一切进入 LLM 之前压缩——**工具输出、日志、RAG 块、文件、对话历史**:相同答案,JSON 数据省 60-95% token、编码 Agent 省 15-20%。四种形态(库/代理/Agent 包装/MCP)、**可逆**(CCR:原始内容缓存,LLM 按需检索)、本地优先、Apache 2.0。示例:实时压缩 10,144 → 1,260 tokens(同一 FATAL 日志仍被找到)。
>
> **来源**:Headroom 开源项目(https://github.com/headroomlabs-ai/headroom,原 chopratejas/headroom;Docs:https://headroom-docs.vercel.app/docs;PyPI/npm:headroom-ai);原始文件存档于 `references/headroom/`

## 概念:为什么需要"上下文压缩层"

Agent 的上下文是稀缺资源:工具输出、日志、RAG 检索块、文件内容、多轮历史——大量内容"携带信息量低但占用 token 高"。Headroom 的定位是给 Agent 加一层**压缩管线**,让模型看到同样的答案、更少的 token。

!!! tip "实测效果**
    - JSON 数据/工具输出:**60-95% token 减少**(SmartCrusher 统计压缩 70-90%);
    - 编码 Agent:15-20% 减少(AST 感知代码压缩);
    - 实时示例:10,144 → 1,260 tokens,关键信息(FATAL)仍被保留。

## 原理:三阶段管线 + 可逆 CCR

### 1. 三阶段压缩管线

```
内容路由(自动识别类型:JSON / code / logs / diffs / text)
  → 分类型压缩器(每类用最合适的压缩器)
  → CCR 可逆存储(原始内容缓存,LLM 按需检索)
```

### 2. 压缩器家族(内容感知)

| 压缩器 | 机制 | 效果 |
| --- | --- | --- |
| **SmartCrusher** | 统计型 JSON/数组压缩(识别重复结构/冗余字段) | 工具输出 70-90% |
| **Code compression** | **tree-sitter AST 感知**——保留 imports、函数签名、类型,压缩实现细节 | 编码 Agent 15-20% |
| **Text & log** | 搜索结果、构建日志、diff 的压缩(识别重复行/模板模式) | 日志类高压缩比 |

!!! note "为什么压缩优于截断**
    截断丢信息、破坏语法;内容感知压缩保留**结构与关键信息**(代码签名、日志中的 FATAL/错误行),LLM 仍能定位问题——这正是"10,144 → 1,260 tokens 同一 FATAL 被找到"的原因。

### 3. CCR:可逆(压缩-缓存-检索)

- **原始内容永不删除**:压缩时缓存,LLM 需要时通过 `headroom_retrieve`(MCP)或 API 按需取回;
- **安全阀**:压缩器误判(如模型需要看到完整 JSON 字段)时,可随时检索原始——**压缩不是有损丢弃,是可逆的**。

### 4. 四种使用形态

| 形态 | 用法 | 适用 |
| --- | --- | --- |
| **Library** | `compress(messages)`(Python/TS),`withHeadroom(anthropic/openai)` | 应用内集成 |
| **Proxy** | `headroom proxy --port 8787`(OpenAI/Anthropic/Gemini 兼容 HTTP 代理) | 零代码,任何语言 |
| **Agent wrap** | `headroom wrap claude`(支持 18 个:claude/codex/copilot/cursor/aider/opencode/cline/continue/goose/openhands/openclaw/vibe/omp/zcode…),`headroom unwrap` 还原 | 一条命令给现有 Agent 加压缩 |
| **MCP server** | `headroom_compress` / `headroom_retrieve` / `headroom_stats` | 任何 MCP 客户端(Claude Code/Cursor) |

### 5. 进阶能力

- **Cross-agent memory**:Claude/Codex/Gemini/Grok 跨 Agent 共享存储 + 自动去重;
- **`headroom learn`**:挖掘失败会话,把修正写入 `CLAUDE.local.md`(默认,gitignored)或 `CLAUDE.md`/`AGENTS.md`/`GEMINI.md`/`GROK.md`;
- **Output token reduction**:不只压缩发送给模型的,**还裁剪模型写回的**(去掉仪式化/复述代码,对例行步骤跳过深度"思考")。

## 代码 / 实现:压缩-可逆检索的最小演示(纯 Python)

把"压缩 + CCR 可逆"的核心落成可运行演示(JSON 数组字段级压缩,能检索回原始):

```python
import json

# —— 压缩器:JSON 数组 → 提取共享结构,值单独存储(示意 SmartCrusher 思路)——
def compress_json_array(items: list) -> dict:
    """压缩:保留结构 + 去重后的值;原始缓存进 CCR 存储"""
    keys = list(items[0].keys()) if items else []
    unique_values = sorted({v for it in items for v in it.values()})
    return {"schema": keys, "count": len(items), "unique_values": unique_values,
            "compressed": True}

# —— CCR:压缩结果缓存原始,按需检索 ——
ccr_store = {}
def compress_and_cache(items):
    c = compress_json_array(items)
    ccr_store[id(c)] = items            # 原始永不删除
    return c
def retrieve(compressed):
    return ccr_store[id(compressed)]    # LLM 需要时取回原始

logs = [{"ts": "09:00", "level": "INFO"}, {"ts": "09:01", "level": "FATAL"},
        {"ts": "09:02", "level": "INFO"}, {"ts": "09:03", "level": "ERROR"}]
c = compress_and_cache(logs)
print("压缩后:", c)
print("检索回原始:", retrieve(c))
assert retrieve(c) == logs                    # 可逆:压缩不丢原始
assert "FATAL" in c["unique_values"]          # 关键信息(FATAL)保留
assert c["count"] == len(logs)                # 结构完整
print("代码验证通过 ✔(可逆压缩:省 token 不丢信息)")
```

## 实践 / 应用:安装、集成与知识库整合

### 快速开始(60 秒)

```bash
pip install headroom-ai          # Python;npm install headroom-ai 为 TS
headroom proxy --port 8787       # 零代码代理:客户端指向 http://127.0.0.1:8787
headroom wrap claude             # 一条命令包装现有 Agent(支持 18 个工具)
# 或 Docker: docker run -p 8787:8787 ghcr.io/chopratejas/headroom:latest
```

### SDK / 框架集成

Anthropic SDK / OpenAI SDK(`withHeadroom()`)、Vercel AI SDK、LangChain(chat models/memory/retrievers/agents)、LiteLLM(100+ providers 单回调)、Agno、Strands。

### 与站内其他文章的呼应

- [Context Engineering](../03-agents/context-engineering.md):Headroom 是"上下文压缩"的工具化实现(理论 → 落地);
- [OpenAI 官方 Prompt 指南](../07-agent-coding/experience/openai-prompt-guide.md):"Token 减少"的工程化手段(精简 prompt + 压缩工具输出);
- [高德知识库](../06-enterprise/ontology-agent-adoption/ai-native-knowledge-base-gaode.md):"最小有用片段/直达短路"与 Headroom 的压缩哲学同源(省 token 不丢关键信息);
- [Agent 系统设计的 5 个决策](../03-agents/agent-system-5-decisions.md):成本控制四道防线中的"缓存/压缩"落地;
- [Graph Engineering 14 步](../07-agent-coding/experience/graph-engineering-14-steps.md):压缩工具输出 = 图的边传递"高信号结果"。

## 总结

- **定位**:Agent 的上下文压缩层——压缩一切进 LLM 的内容(工具输出/日志/RAG/文件/历史),同答案省 token;
- **核心机制**:三阶段管线(内容路由 → 分类型压缩器 → CCR 可逆存储);SmartCrusher(JSON 70-90%)/tree-sitter AST(代码 15-20%)/Text&Log;
- **四种形态**:库 / 代理 / 18 工具 wrap / MCP——覆盖从应用内嵌到一条命令包装现有 Agent;
- **可逆安全阀**:CCR 原始缓存按需检索,压缩不丢信息;
- **一句话**:Headroom 把"上下文管理"从人工纪律变成自动管线——**压缩的是 token,保留的是答案**。

## 延伸阅读

- 仓库:https://github.com/headroomlabs-ai/headroom;Docs:https://headroom-docs.vercel.app/docs;llms.txt:https://headroom-docs.vercel.app/llms.txt;模型:https://huggingface.co/chopratejas/kompress-v2-base
- 站内:[Harness 收录清单](index.md)、[Context Engineering](../03-agents/context-engineering.md)、[高德知识库](../06-enterprise/ontology-agent-adoption/ai-native-knowledge-base-gaode.md)、[Agent 系统设计的 5 个决策](../03-agents/agent-system-5-decisions.md)、[OpenAI 官方 Prompt 指南](../07-agent-coding/experience/openai-prompt-guide.md)
