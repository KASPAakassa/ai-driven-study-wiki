> 原文存档:微信文章《Outlines Index:一种渐进式披露大量文档给 AI Agent 的方法》(公众号:Linkly AI)
> 原始链接:https://mp.weixin.qq.com/s/ugvuxJi42lAviOG9_r5XfA
> 抓取日期:2026-08-14(手机 UA curl,避开微信环境验证)
> 用途:整理收件箱素材,正文原样保留供追溯。

---



![](https://mmbiz.qpic.cn/sz_mmbiz_png/hOeJH0Licq63YOJW49bRZ2iaC1l2GHNRH4CZJbJI7vEUgKhibK9EvNibsaCW9qs002DMUhPOIGjQn4GibMGwicqlpV2Sv3Rm1r3icgFB7vg4NdOdBc/640?wx_fmt=png&from=appmsg)

主流答案是 RAG：把文档切成 chunk，向量化，存进向量数据库。

用户提问时检索最相关的几个 chunk 塞进 prompt。 这套方案在过去两年被广泛采用，但它有一个根本性的问题：AI 拿到的永远是预切碎片，而不是文档本身。碎片化的文档块最终会污染 AI 的上下文，在准确率和维护性上陷入泥潭。 

所以在 2025 年，我们会不断地看到 RAG 已死，直到 Claude Code 等 AI Agent 使用最原始的 Grep 和 Glob 来检索文档，取得瞩目的效果以后，RAG 似乎很少被人所关注。

但是检索是一个基础能力，我们参考 Skills 的渐进式披露思想，实现了一种全新的检索方式，叫 **Outlines Index**。

核心思想一句话说清：**为每个文档建立一份结构化“名片”，让 AI 按 search → outline → read 的路径渐进式访问文档，而不是一次性灌入切碎的片段。**

**问题出在哪**

AI Agent 要访问用户本地非结构化文档，面临两个障碍：**
**

**障碍一：路径无语义。** 

代码库里 `src/services/auth.ts` 这个路径本身就在告诉你这是认证服务的代码。但 `2024年度总结(修改版)(最终版).docx`路径告诉你的信息约等于零。AI 没法像 Claude Code 用 glob 模式匹配文件名来定位文档。**
**

**障碍二：格式不可读。**

PDF、DOCX 是二进制格式，grep 读不了。即使提取出纯文本，一个没有章节标题的 200 页 PDF 也只是一大坨文字，AI 无从下手。

传统 RAG 的做法是绕过这两个问题：不管文档结构，全部切成固定大小的 chunk，向量化后靠语义相似度检索。

但这带来了很多问题：

1. **上下文丢失**：chunk 被切碎后与前后文脱节，AI 不知道这段话出自哪个章节、前后在讲什么

2. **不可控**：搜到的 chunk 可能不够用，但 AI 无法“再多看一点”

3. **Token 浪费**：返回 10 个 chunk，5000+ tokens，其中可能只有一个真正相关

4. **质量不稳定**：切片策略影响结果，一个关键段落被切成两个 chunk 后可能都无法被单独检索到 

5. *丢失语义*： 传统 RAG 依赖 Rerank 做最后的精排序，但这是一种成本比较高的方式，并且许多专有名词 Rerank 模型无法捕捉到语义

**一个来自 Claude Code 的灵感**

转折点来自一个观察：Claude Code 不用 RAG，但它能高效探索整个代码库。

它只用三个工具：**Glob**（按模式找文件）、**Grep**（搜关键词）、**Read**（读文件内容）。

工作方式不是“搜索引擎返回碎片”，而是像研究员翻阅文件柜——先扫描文件名找到候选，打开文件快速浏览结构，确定哪一部分有用，然后精准阅读。这种方式有一个名字：**渐进式披露**（Progressive Disclosure）。

>

渐进式披露是一个界面设计原则：不要一次性展示所有信息，而是根据用户当前的需要逐层展开。在 AI Agent 的语境下，就是让 Agent 自主决定“看多少”。

问题是：Glob+Grep 只适用于纯文本的代码库。文档需要一个等价的“目录索引”系统。

这就是我们提出 Outlines Index 的原因。

**Outlines Index 是什么**

为每个被索引的文档生成一份结构化信息，包含两部分：

**Metadata（元数据）**——文档的“身份证”：

• 标题（多级回退：文档元数据 → 首个标题 → 文件名）

• 作者、语言、字数

• 摘要（文档开头约 200 字）

• 关键词（自动提取）

• `brief` 标记（字数 < 500 时为 true）

**Outline（结构大纲）**——文档的“目录”：

**章节标题、层级关系、每节的首句摘要、关键词、行号范围。**以树形结构存储。

关键：**Outline 不存储原文，只存储导航信息。** 它是一张地图，不是领土本身。

**三层渐进式披露**

Outlines Index 灵感来自于 Agent Skills。Agent Skills 采用渐进式披露技术，即使载入几十个技能，依然能有效过滤且防止上下文爆炸。

同样的，我们基于 Outlines Index 实现了三个 MCP 工具，对应三个披露层次：

**Layer 1: search — 发现文档**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/hOeJH0Licq63lP43qKXUXMicBaSUdBOzRQVITO38PXXAc6HJI5pJXdSG9TdB6ezDicNtjxwo05H73GSj9O9GrmcHvjS0CgYicQaAQW1LaWecmyw/640?wx_fmt=png&from=appmsg)

**50 tokens**。20 个结果总共约 **1000 tokens**。

AI 拿到这个列表后，LLM 可以看到：

• `has_outline: yes` → 可以用 outline 工具深入

• `words: 3200` → 中等长度文档

• `relevance: 0.92` → 高度相关

**Layer 2: outline — 浏览结构**

接着 LLM 借助自己的工具调用能力，进一步使用 `outline` 工具批量的查看认为相关的文档的大纲，进一步确认。这一点与人类看书的方式是完全一致的。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/hOeJH0Licq62cX0puibAoeBOxPZUZgNPaqEGObxj2Gpol09SLhFBSsToOvdKdn8ze945JYgIibBibDepp2IBwkJ9Edl6ibUmYIfbHkz2vxtLVaqU/640?wx_fmt=png&from=appmsg)

**200-500 tokens**。

注意每个节点后面的 `[L42-65, 24行]`——这是行号范围，直接对应 read 工具的参数。AI 看完大纲就知道该读哪里。

**Layer 3: read — 精准阅读**

这个工具与 Claude 的 Agent SDK 完全一致。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/hOeJH0Licq60ZialliaUvEDs5UdY38W4ibt0jknlyTcb3rQulxTvsyZm7eMrVIicibibPwW4OGy7Ax6wadvicHjzjHNVB1tO6cQrPdoSxcOIaQ8aGS8/640?wx_fmt=png&from=appmsg)

**整个流程消耗约 800 tokens**。同样的场景，传统 RAG 返回 10 个 chunk，消耗 4000-6000 tokens，且 AI 对文档结构一无所知，只能依赖嵌入模型和 ReRank 模型的理解能力。

**真实案例：从搜索到精准阅读**

让我们再看一个更复杂的案例。假设你问 AI：“帮我找关于 Docker 部署的文档。”

**AI 的操作过程**

**第一步：search**

AI 调用 `search("Docker 部署")`，返回 5 个文件。其中一个是 `deployment-guide.pdf`，2400 行，`has_outline: yes`。另一个是 `.env.example`，20 行，`brief: true`。

**第二步：分流决策**

• `.env.example` → `brief: true`，20 行 → 跳过 outline，直接 `read`，一次读完

• `deployment-guide.pdf` → 2400 行 → 先 `outline`

**第三步：outline**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/hOeJH0Licq62hB2FWaZSbZ8soFUGic2PnDsQicqnmZkBWxyNIvicOF3jg5cs4nnhkZvpRIzdb9VXjpMAtc4FoT4JftHORV4B7zvpVBtxFffMyAM/640?wx_fmt=png&from=appmsg)

**第四步：精准 read**

![](https://mmbiz.qpic.cn/mmbiz_png/hOeJH0Licq62E5DNkGQCayicxiaFRhRF6L4nbxmeYEO8Zicnc6sEf8gnfHlMasCRGxAbuVxpAImgoOVick9SQZH889QVHI1ZZlsu8Mw0j8eicsyoc/640?wx_fmt=png&from=appmsg)

`offset=201, limit=110`。

**总消耗**：search 1000 + outline 400 + read 2000 ≈ **3400 tokens**，拿到了精确的、有完整上下文的信息。

RAG 方式？返回从 2400 行文档里随机切出的 10 个 chunk，5000+ tokens，可能恰好漏掉了 Docker Compose 的配置示例。

**brief 标记：让 AI 自己判断要不要看目录**

一个小但重要的设计细节：`brief` 布尔字段。

当文档字数 < 500 时，`brief` 设为 `true`。AI 在 search 结果中看到 `brief: true`，就知道这个文档很短，可以跳过 outline 直接 read 全文。

不需要在工具层面做任何强制逻辑。LLM 天然理解“这个文件很短，直接读吧”。**把决策权交给 AI，而不是硬编码在代码里。**

**大纲生成：不同格式，不同策略**

不同文档格式的大纲提取方式不同：

格式

策略

大纲质量

Markdown

解析 # 标题层级

高

PDF（有书签）

提取 PDF Bookmark 树

高

DOCX

解析 Heading 样式

高

HTML

转 Markdown 后提取

高

PDF（无书签）

启发式规则识别

中等

纯文本

ALL CAPS / 编号模式 / 下划线标记

中等或无

对于纯文本文件，我们用启发式规则识别可能的标题：

• `===` 或 `---` 下划线标记的行

• 编号模式：`1.`、`1.2`、`Chapter N`、`Section N`

• 全大写行（ALL CAPS）

当启发式无法识别出可靠的大纲时，`outline_quality` 标记为 `none`，outline 工具会返回：“No reliable outline available. Use `read` to browse this document line by line.”——优雅降级，而非报错。

**Budget 策略：无论文档多大，大纲输出都可控**

一个 2000 页的学术论文，大纲可能有几百个节点。直接输出会占用太多 token。

我们实现了多级降级策略：

1. **完整输出**：如果在 token 预算内，返回全部节点（含摘要和关键词）

2. **去掉摘要**：只保留标题和行号

3. **降低层级**：从 Level 5 开始逐级去掉，最终只展示 Level 1 顶级标题

4. **硬截断**：最终兜底

这保证了无论面对多大的文档，outline 的输出都在合理范围内。

**每文档一个向量：不需要 Chunking**

传统 RAG 需要把文档切成 chunk 再向量化。一个 100 页的文档可能产生 200 个向量。10000 个文档就是 200 万个向量。

Outlines Index 的做法不同：**Embedding 的对象不是原文，而是 Outline Index 本身**。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/hOeJH0Licq62ZPDld2ExhnPBQVfV8haAyzq3sewV0IPVo1ichBfFyTJ3cGSUiasB4xqubBHdf9ibjGTVdIQv13tR7l2v29xTAnhuXv3lXXSffIk/640?wx_fmt=png&from=appmsg)

10000 个文档 = 10000 个向量 ≈ 30MB 存储。

这不只是节省空间——单向量检索的速度远快于在 200 万向量中搜索。而且 Outline 浓缩了整个文档的信息，向量质量反而更高。 当我们将目标从**获取相关 chunk**，改为先获取**相关文档**后，整个检索过程变得简洁、通用。

**双路检索：精确匹配 + 语义理解**

过去的 RAG 实践证明，bm25+向量的双路混合检索，是一种简洁有效的方式，所以 `search` 工具内部我们使用了这种策略，同时执行两路检索：

• **BM25 全文搜索**：精确关键词匹配，对技术术语、人名、专有名词不可替代

• **向量语义搜索**（基于 Outline Index 向量）：跨语言能力，“deployment” 能匹配到“部署”

两路结果再通过 RRF（Reciprocal Rank Fusion）融合。

这还给了系统另一个优雅的特性：**渐进可用**。

BM25 索引一般在安装后 1-3 分钟就能建好（同时生成 Outline），关键词搜索立即可用。向量索引需要更长时间（取决于文档数量），完成后语义搜索自动上线。用户无感，不需要等。 正是这种方式，才能确保 C 端产品的体验，可能是市面安装后最快可用的知识库应用。

**可能是面向未来的一种方案**

RAG 的设计假设是：LLM 不够聪明，需要我们帮它把信息准备好、切碎、排好序、塞进 prompt。这在 GPT-3.5 时代是合理的。

但现在的 LLM 已经能自主使用工具完成复杂的多步检索任务。Claude、GPT-4、Gemini 都展示了强大的工具使用能力。 它们不需要预切碎片 —— 它们需要的是**线索**，告诉它文件在哪、结构是什么，它自己能决定读什么、读多少。

Outlines Index 的核心理念：**不要替 AI 预加工信息，而是给它一张地图，让它自己探索。**

三个原子工具（search、outline、read）释放了 LLM 的涌现能力：

• **跨文档对比**：同时 outline 多个文档，对比结构和内容

• **迭代搜索**：一次搜索不满意，自动调整关键词再试

• **深度阅读**：发现某个章节引用了另一个概念，再搜索相关文档

• **基于文档的写作**：读完几份参考资料后，综合生成新内容

这些能力不需要任何 Agent 编排框架。越来越多的 LLM 天然就会组合工具来完成复杂任务。

**试试看**

Outlines Index 是 Linkly AI 的核心技术。Linkly AI 是一个本地优先的文档索引工具，所有数据 100% 存储在本地。

安装后选择文档目录，后台自动建索引。然后通过 MCP 协议或 CLI，任何 AI 工具（Claude、Cursor、ChatGPT 等）都能用 search → outline → read 的方式访问你的文档。

**往期推荐**
[https://mp.weixin.qq.com/s?__biz=MzcwMDM4NDc1Mw==&mid=2247484240&idx=1&sn=b80cb4c2c09fa83ce292c5f0dc363d72&scene=21#wechat_redirect](https://mp.weixin.qq.com/s?__biz=MzcwMDM4NDc1Mw==&mid=2247484240&idx=1&sn=b80cb4c2c09fa83ce292c5f0dc363d72&scene=21#wechat_redirect)
![](https://mmbiz.qpic.cn/mmbiz_png/hOeJH0Licq60s28nIib6gsGINCG8iawibQlLaIKhAGxAWzdKq2ncRnwezPXBT4bnrl0S5BHt28ARFIuialLicPdaGSYWM8AWK754jE86jgPFE32icw/640?wx_fmt=png&from=appmsg)
