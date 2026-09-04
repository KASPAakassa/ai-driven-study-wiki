# Writing effective tools for agents:工具设计五原则 + Advanced tool use

> **一句话摘要**:工具是**确定性系统与不确定 agent 之间的契约**——给工具做 prompt 工程,和给 prompt 做一样重要。Anthropic 给出可操作的工具设计五原则(少而精/命名空间化/返回高信号上下文/Token 效率/描述 prompt 工程)+ 用 agent 自动重构工具的 eval 循环;并补充 2025-11 的三个 beta:Tool Search Tool / Programmatic Tool Calling / Tool Use Examples。
>
> **来源**:
> - Anthropic《Writing effective tools for agents — with agents》(https://www.anthropic.com/engineering/writing-tools-for-agents,2025-09-11)
> - Anthropic《Introducing advanced tool use on the Claude Developer Platform》(https://www.anthropic.com/engineering/advanced-tool-use,2025-11-24)

## 概念

### 工具 = 契约

工具定义与规范,应该得到与整体 prompt 同等的 prompt 工程投入。错误假设:工具只是"接口细节"。实际:**工具是确定性系统与不确定 agent 之间的契约**——agent 只有工具一个途径改变世界、获取信息,工具设计直接决定 agent 行为质量。

### 开发流程:原型 → eval → 让 agent 重构

1. **原型**:先写工具初版;
2. **Eval**:用**真实任务**评估(避免在 sandbox 里过度简化——真实环境才能暴露真实失败);每个 prompt 配**可验证结果**(能程序化判断对错);
3. **把 eval 转录丢给 Claude Code 自动重构工具**:把失败案例喂给 Claude Code,让它重写工具定义——**用 agent 优化工具**("with agents")。

## 原理(工具设计五原则)

### 1. 少而精的工具

少而精优于多而杂:

- 用 `search_contacts`(搜索式)而非 `list_contacts`(全量列表);
- 合并相关操作:`schedule_event` 同时处理 list + create。

理由:每个工具都要模型"了解"并做选择,工具越多选择越难、上下文越贵。

### 2. 命名空间化(namespacing)

用命名空间前缀区分相似工具:`asana_search` / `asana_projects_search`,而不是 `search` / `search_projects`。避免工具名歧义导致模型选错。

### 3. 返回高信号上下文

工具返回值要"高信号"——只给判断所需的信息,并做语义化:

- **UUID → 语义 ID**:返回 `Customer: Alice(acs_2c5)` 而非裸 UUID——显著提升后续检索精度;
- **ResponseFormat enum 控制详细度**:`detailed` / `concise` 枚举;`concise` 用约 **1/3 token**——按需取详细度。

### 4. Token 效率

- Claude Code 默认截断 **25,000 token** 的工具输出——输出太长会被截断丢失;
- 用**分页/过滤**让工具输出可控;
- **错误信息也可以 prompt-engineer**:错误消息本身是给模型的上下文,写清楚"哪里错、怎么修"。

### 5. Prompt 工程工具描述

- 参数名用 `user_id` 而非 `user`(避免与 user role 混淆);
- 描述写得像给初级开发者的优秀 docstring:示例用法、边界情况、输入格式要求、与其它工具的界限;
- 数据点:**仅靠微调工具描述,Claude 3.5 Sonnet 达到 SWE-bench SOTA**——描述的质量直接决定性能。

### 附:Advanced tool use(2025-11,三个 beta 功能)

| 功能 | 机制 | 效果 |
| --- | --- | --- |
| **Tool Search Tool** | `defer_loading` 标记,延迟加载工具定义 | 5 个 MCP server 58 工具的前置开销 ~55K token 降到 ~8.7K(保留 95% context,85% token 削减);Opus 4 准确率 49%→74%、Opus 4.5 79.5%→88.1% |
| **Programmatic Tool Calling** | Claude 写 Python 编排工具调用 | 预算检查示例中间数据 200KB→1KB 结果;平均 token 43,588→27,297(-37%);知识检索 25.6%→28.5%、GIA 46.5%→51.2% |
| **Tool Use Examples** | `input_examples` 字段给示例输入 | 复杂嵌套参数处理准确率 72%→90% |

适用条件(beta 的取舍):工具定义 >10K token 用 Tool Search;3+ 依赖调用用 Programmatic;复杂嵌套参数用 Examples。均需 `advanced-tool-use-2025-11-20` header。

## 代码 / 实现

工具定义示例(五原则落地):

```json
{
  "name": "asana_projects_search",
  "description": "在 Asana 中搜索项目。当用户想找项目而非新建时使用;返回语义化 ID 与标题。",
  "parameters": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "搜索关键词" },
      "response_format": { "enum": ["detailed", "concise"], "default": "concise" }
    }
  }
}
```

eval 循环脚本骨架:

```bash
# 1. 收集真实任务的失败转录
# 2. 喂给 Claude Code:"根据这些失败案例,重构工具定义"
# 3. 跑 eval(每个 prompt 配可验证结果)回归
```

## 实践 / 应用

- **何时重写工具**:eval 失败集中在工具选择/参数错误时,先改工具而非改 prompt;
- **五原则速查**:少而精、命名空间化、高信号上下文(UUID→语义 ID/ResponseFormat)、Token 效率(截断 25K/分页/错误消息)、描述 prompt 工程(docstring 标准);
- **用 agent 优化 agent**:把失败转录给 Claude Code 重构工具,是"with agents"的核心;
- **beta 取舍**:按工具定义体量/调用依赖数/参数复杂度选 Advanced tool use 功能;
- 与 [工具调用](tool-calling.md)(原理与协议)互补:那篇讲"怎么调",这篇讲"怎么设计"。

## 总结

1. **工具是契约**:确定性系统与不确定 agent 之间的接口,值得与 prompt 同等的工程投入。
2. **五原则**:少而精、命名空间化、高信号上下文、Token 效率、描述 prompt 工程——全部可落地。
3. **eval 驱动重构**:真实任务 eval → 转录给 Claude Code → 自动重构工具("with agents")。
4. **Advanced tool use**:Tool Search(大工具集)/Programmatic(多依赖调用)/Examples(复杂参数)三个 beta 各解决一类问题。
5. **量化收益**:描述微调达 SWE-bench SOTA、Tool Search 省 85% token、Examples 提准确率 72%→90%。

**下一步学什么**:读 [工具调用](tool-calling.md)(协议层)与 [Building effective agents](agent-building-effective-agents.md)(工具在五种模式中的位置);动手按五原则审查你现有工具定义,再用 eval 循环验证。

## 延伸阅读

- 站内:[工具调用](tool-calling.md)、[Building effective agents](agent-building-effective-agents.md)、[Agent 多轮对话上下文管理](agent-context-management.md)(tool_call_id 配对)、[Agent 效果优化实战](../04-practice/agent-effect-optimization-practice.md)(工具调用成功率评估)
- 外部:原文 1(https://www.anthropic.com/engineering/writing-tools-for-agents);原文 2(https://www.anthropic.com/engineering/advanced-tool-use);cookbook(https://platform.claude.com/cookbook/tool-evaluation-tool-evaluation)
