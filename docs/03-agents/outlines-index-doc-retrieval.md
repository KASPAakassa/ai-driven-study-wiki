# Outlines Index:用渐进式披露替代 RAG 的文档检索方法

> **一句话摘要**:RAG 把文档切碎成 chunk 再向量化,AI 拿到的永远是预切碎片;Claude Code 不用 RAG,靠 Glob+Grep+Read 就能高效探索代码库。Outlines Index 把这种**渐进式披露**思想迁移到非结构化文档:为每个文档生成结构化"名片"(Metadata + Outline,不存原文),通过 `search → outline → read` 三个 MCP 工具让 AI 自主决定"看多少"——约 800 tokens 完成一次精准检索,而传统 RAG 要 4000-6000 tokens 且对文档结构一无所知。核心理念:**不要替 AI 预加工信息,给它一张地图,让它自己探索**。
>
> **来源**:Linkly AI《Outlines Index:一种渐进式披露大量文档给 AI Agent 的方法》(https://mp.weixin.qq.com/s/ugvuxJi42lAviOG9_r5XfA)

## 概念

### RAG 的问题:AI 拿到的永远是预切碎片

传统 RAG:文档切成固定 chunk → 向量化 → 存向量库 → 检索相关 chunk 塞进 prompt。它绕过了两个障碍(路径无语义、格式不可读),但带来五个问题:

1. **上下文丢失**:chunk 切碎后与前后文脱节,不知道出自哪个章节;
2. **不可控**:搜到的 chunk 不够用,AI 无法"再多看一点";
3. **Token 浪费**:返回 10 个 chunk 5000+ tokens,可能只有一个相关;
4. **质量不稳定**:切片策略影响结果,关键段落被切成两个 chunk 后可能都检索不到;
5. **丢失语义**:Rerank 成本高,且许多专有名词 Rerank 模型捕捉不到。

### 灵感:Claude Code 的 Glob + Grep + Read

Claude Code 不用 RAG,只用三个工具:**Glob**(按模式找文件)、**Grep**(搜关键词)、**Read**(读文件)。工作方式不是"搜索引擎返回碎片",而是像研究员翻阅文件柜——先扫文件名找候选、打开文件浏览结构、确定哪部分有用、精准阅读。这就是**渐进式披露(Progressive Disclosure)**:让 Agent 自主决定"看多少"。

问题是 Glob+Grep 只适用纯文本代码库;文档需要一个等价的"目录索引"系统——这就是 **Outlines Index**。

### Outlines Index 是什么

为每个被索引的文档生成一份结构化信息(两部分):

| 部分 | 内容 |
| --- | --- |
| **Metadata(身份证)** | 标题(多级回退:文档元数据→首个标题→文件名)、作者、语言、字数、摘要(开头约 200 字)、关键词、`brief` 标记(字数<500 为 true) |
| **Outline(目录)** | 章节标题、层级关系、每节首句摘要、关键词、**行号范围**——树形结构 |

> 关键:**Outline 不存储原文,只存储导航信息**——它是一张地图,不是领土本身。

## 原理(三层渐进式披露)

基于 Outlines Index 实现三个 MCP 工具,对应三个披露层次:

| 层 | 工具 | 作用 | 成本 |
| --- | --- | --- | --- |
| **L1** | `search` | 发现文档(返回元数据列表:标题/字数/has_outline/relevance/brief) | 50 tokens/结果,20 结果 ≈ **1000 tokens** |
| **L2** | `outline` | 浏览结构(树形目录,每节点带行号范围如 `[L42-65, 24行]`,直接对应 read 参数) | **200-500 tokens** |
| **L3** | `read` | 精准阅读(与 Claude Agent SDK 一致,`offset/limit` 按行读) | 按需 |

**整个流程约 800 tokens**;传统 RAG 同场景 4000-6000 tokens 且 AI 对文档结构一无所知,只能依赖嵌入与 Rerank 模型。

### 关键设计细节

- **brief 标记**:字数<500 时 `brief: true`,AI 在 search 结果看到就跳过 outline 直接 read 全文——**把决策权交给 AI,不硬编码**(LLM 天然理解"文件很短直接读");
- **大纲生成策略**(按格式):Markdown 解析 `#` 层级 / PDF 提取书签树 / DOCX 解析 Heading 样式 / HTML 转 Markdown / 纯文本用启发式(ALL CAPS、`===` 下划线、编号模式 `1.`/`Chapter N`);无法识别时 `outline_quality: none`,outline 返回"Use read to browse line by line"——**优雅降级而非报错**;
- **Budget 策略**(2000 页论文的大纲也可能几百节点):完整输出 → 去摘要(只留标题+行号)→ 降低层级(从 L5 逐级去掉,最终只留 L1)→ 硬截断——保证任何文档输出可控;
- **每文档一个向量**:Embedding 对象是 **Outline Index 本身**,而非原文 chunk——10000 文档=10000 向量≈30MB;单向量检索更快,且 Outline 浓缩整篇信息、向量质量更高;目标从"获取相关 chunk"变为"先获取相关文档";
- **双路检索**:BM25 精确匹配(技术术语/人名/专有名词不可替代)+ 向量语义搜索(跨语言,"deployment" 匹配"部署"),**RRF 融合**;
- **渐进可用**:BM25 索引 1-3 分钟建好(同时生成 Outline),关键词搜索立即可用;向量索引后台完成后语义搜索自动上线——用户无感。

### 真实案例(Docker 部署)

1. `search("Docker 部署")` → 5 个文件(`deployment-guide.pdf` 2400 行 has_outline: yes;`.env.example` 20 行 brief: true);
2. **分流**:`.env.example` brief → 直接 read 一次读完;`deployment-guide.pdf` 2400 行 → 先 outline;
3. `outline` → 看到章节与行号;
4. `read(offset=201, limit=110)` → 精准命中 Docker Compose 配置示例;
5. 总消耗 search 1000 + outline 400 + read 2000 ≈ **3400 tokens**,拿到精确、有完整上下文的信息;RAG 方式从 2400 行随机切 10 chunk 5000+ tokens,还可能恰好漏掉关键示例。

## 代码 / 实现

以 MCP 工具形式暴露(任何 AI 工具 Claude/Cursor/ChatGPT 都可调用);产品形态是本地优先文档索引工具(Linkly AI,数据 100% 本地):

```text
# search 返回示例(20 结果 ≈ 1000 tokens)
[{"title": "deployment-guide", "has_outline": true, "words": 3200, "relevance": 0.92}, ...]

# outline 返回示例(树形 + 行号范围,直接对应 read 参数)
Docker 部署指南
├── 环境准备        [L1-30, 30行]
├── 安装 Docker     [L31-80, 50行]
└── Compose 配置    [L201-310, 110行]   ← read(offset=201, limit=110)

# 格式无关:Markdown 解析 # 层级 / PDF 书签 / DOCX Heading / 纯文本启发式
# 优雅降级:outline_quality=none → "No reliable outline available. Use read to browse line by line."
```

## 实践 / 应用

- **适用**:本地非结构化文档库(PDF/DOCX/Markdown/HTML/纯文本)、个人知识库、企业文档接入 AI Agent;追求"安装后最快可用"(渐进可用)的 C 端场景;
- **与站内知识呼应**:
  - 渐进式披露与 [Agent Skills 设计理念](../07-agent-coding/skills/agent-skills-design.md)(三级披露)、[Claude Code 官方最佳实践](../07-agent-coding/claude-code-deep-dive/claude-code-best-practices.md)(CLAUDE.md 目录化)、[上下文工程官方一手资料](context-engineering-official-sources.md)(just-in-time 检索/最小高信号 token 集)一脉相承;
  - 与 [RAG](../02-llm/rag.md) 是"检索范式"之争:不是替代所有检索,而是对**结构可解析的文档**更优;对超碎片化/无结构内容,RAG 仍有价值;
  - "不要替 AI 预加工信息,给它地图"呼应 [Agent 上下文管理](agent-context-management.md) 的"信息选择"与 [Building effective agents](agent-building-effective-agents.md) 的工具设计哲学;
- **局限与注意**:Outline 依赖文档可解析出结构(纯文本启发式质量中低);大纲质量决定检索质量(嵌入的是 Outline 而非原文);对需要跨 chunk 语义聚合的任务,单文档向量可能不够细。

## 总结

1. **RAG 的根本问题**:AI 拿到预切碎片而非文档本身——上下文丢失、不可控、Token 浪费、质量不稳、丢语义。
2. **Outlines Index = 文档的"目录索引系统"**:Metadata 身份证 + Outline 地图(不存原文),让 Glob+Grep+Read 的渐进式披露在非结构化文档上成立。
3. **三层工具**:search(发现)→ outline(浏览,带行号)→ read(精准读),约 800 tokens 完成传统 RAG 4000-6000 tokens 的事;brief 把"读不读目录"决策交给 AI。
4. **工程细节**:按格式生成大纲 + 优雅降级、Budget 多级降级、每文档单向量(30MB/万文档)、BM25+向量双路 RRF、渐进可用。
5. **理念**:GPT-3.5 时代 RAG 假设"LLM 不够聪明要替它切碎";现在 LLM 需要的是**线索而非预切碎片**——"给它一张地图,让它自己探索",三个原子工具释放涌现能力(跨文档对比/迭代搜索/深度阅读/基于文档写作)。

**下一步学什么**:读 [RAG](../02-llm/rag.md)(对比两种检索范式)、[上下文工程官方一手资料](context-engineering-official-sources.md)(just-in-time 检索与渐进式披露)、[Agent Skills 设计理念](../07-agent-coding/skills/agent-skills-design.md)(三级披露同源)。

## 延伸阅读

- 站内:[上下文工程官方一手资料](context-engineering-official-sources.md)、[Agent Skills 设计理念](../07-agent-coding/skills/agent-skills-design.md)、[Agent 多轮对话上下文管理](agent-context-management.md)、[RAG](../02-llm/rag.md)、[Claude Code 官方最佳实践](../07-agent-coding/claude-code-deep-dive/claude-code-best-practices.md)
- 外部:原文(https://mp.weixin.qq.com/s/ugvuxJi42lAviOG9_r5XfA);Linkly AI(本地优先文档索引,MCP/CLI)
