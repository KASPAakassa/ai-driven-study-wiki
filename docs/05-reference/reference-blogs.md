# 博客与社区清单:持续学习的情报源

> **一句话摘要**:按英文 / 中文两类收录高质量博客与社区,每项说明它"擅长什么、解决什么问题",让你按需订阅而不是被动刷屏。
>
> **来源**:各博客 / 社区官网。

## 概念

### 为什么博客是学习 AI 的重要一环?

- **比论文快、比书新**:论文有数月的审稿周期,书有数年的出版周期;博客是研究者**第一时间**表达新想法的场所。
- **比论文容易读**:作者面向普通读者写作,省去了论文的严谨但难读的推导,保留直觉与动机。
- **比课程细**:课程讲主线,博客讲专题——某个具体模型、某个工程坑、某段推导,博客往往讲得更透。

### 如何"正确"地看博客

- **作者优先**:认准一线研究者/工程师的个人博客,他们的判断力比"搬运工"网站高一个量级。
- **追源头**:很多公众号、聚合站的内容,源头就是这些一手博客;**直接订阅源头**省时省力。
- **配合实践**:看博客时把关键结论对应到 [工具清单](reference-tools.md) 与 [论文清单](reference-papers.md),形成"读-跑-查"闭环。

## 清单主体

### 英文博客

- **Lil'Log(Lilian Weng)** — OpenAI 研究科学家,Agent、RLHF、扩散模型等**综述级长文**,被引用率极高(如 "LLM Powered Autonomous Agents");<https://lilianweng.github.io/>
- **Andrej Karpathy 博客** — 前 Tesla AI 总监、OpenAI 创始成员,讲训练神经网络的工程直觉,金句与"Recipe"式经验并存;<https://karpathy.github.io/>
- **Jay Alammar** — "The Illustrated Transformer / GPT / RAG" 系列作者,用精致配图把复杂架构讲成绘本,入门必读;<https://jalammar.github.io/>
- **Distill** — 交互式可视化论文期刊,把机制做成可动手玩的图表(注:已于 2022 年停更,但经典依旧);<https://distill.pub/>
- **Chris Olah** — 可解释性研究先驱,单篇文章的深度罕见,适合想理解"模型内部到底学了什么"的人;<https://colah.github.io/>
- **Sebastian Ruder** — 前 DeepMind、NLP 方向,长篇综述(如多任务学习、涌现能力)条理极佳;<https://ruder.io/>
- **Hugging Face Blog** — 模型发布与开源生态的一手消息,技术深度与时效兼备;<https://huggingface.co/blog>
- **Sebastian Raschka** — 《从零构建 LLM》作者,每周论文速递与 LLM 手把手教程,想跟进最新研究的高性价比选择;<https://magazine.sebastianraschka.com/>
- **Chip Huyen** — 《AI Engineering》作者,LLM 工程、MLOps 与职业发展的深度文章,务实且发人深省;<https://huyenchip.com/blog/>
- **Simon Willison's Weblog** — 一线 LLM 应用工程师,大量"这周我做了什么"式实战记录与工具评测,贴近真实开发;<https://simonwillison.net/>

### 中文博客与社区

- **机器之心** — 中文 AI 媒体老牌代表,论文解读与技术报道覆盖面最广,适合每日速览;<https://www.jiqizhixin.com/>
- **量子位 (QbitAI)** — 行业动态与产品新闻更灵敏,关注"谁发布了什么模型"这类消息;<https://www.qbitai.com/>
- **PaperWeekly** — 专注论文精读与分享的知乎机构号,每周精选值得读的论文,含作者解读;<https://www.zhihu.com/org/paperweekly>
- **苏剑林《科学空间》** — 民间数学与 LLM 推导大神,Transformer、RoPE 等主题的公式推导细致到能跟着推,硬核派必收藏;<https://spaces.ac.cn/>
- **李沐(知乎 / B 站)** — 《动手学深度学习》作者,论文精读视频与读书分享,讲解深入浅出,中文学习者的老朋友;<https://www.zhihu.com/people/mli65>
- **智源社区 (BAAI)** — 北京智源研究院旗下社区,聚合论文、专栏、知识树,国产模型动态的一手来源;<https://hub.baai.ac.cn/>
- **Hugging Face 中文博客** — HF 官方中文频道,中文社区关心的模型与教程都有;<https://huggingface.co/blog/zh>
- **Datawhale** — 开源 AI 学习社区,组织"组队学习"与开源课程,适合想找学习搭子的人;<https://datawhale.cn/>

## 实践:如何用博客与社区制定学习计划

- **每日 10 分钟速览**:机器之心 / 量子位 / Simon Willison 任选一个,通勤时刷,保持对行业的"体感温度"。
- **每周精读 1 篇**:从 Lil'Log、Karpathy、Jay Alammar、苏剑林这些"深内容源"里挑一篇,读两遍——第一遍懂大概,第二遍对照 [论文清单](reference-papers.md) 里的原文把细节捋清。
- **学新主题时先搜博客**:比如学 RAG,先在 Lil'Log、Jay Alammar、LangChain 博客里各找一篇综述,建立地图后再深入论文。
- **用社区破圈**:PaperWeekly、Datawhale 的讨论区能找到"同道";在 Hugging Face 社区提 issue / 看模型卡,是了解真实使用的捷径。
- **订阅而非收藏**:用 RSS(如 <https://www.jiqizhixin.com/rss> 之类)或邮件订阅把"刷"变成"读",收藏夹只是墓地。

**避坑提示**:

- 新闻类内容看**趋势与结论**,别把自媒体对论文的解读当论文本身——解读可能有误,细节一律回原文。
- 中文媒体标题常有夸张,学会"标题党过滤器":先看正文的实验与数据,再决定是否值得深入了解。
- 同一主题会反复出现;**遇到第二次就直接归档进自己的 Wiki**,这是本知识库 [收件箱](../inbox/README.md) 的用途。

## 延伸阅读

- 站内:[必读论文清单](reference-papers.md)、[书籍与课程](reference-books-courses.md)、[工具与库](reference-tools.md)
- 外部:RSS 阅读器 Feedly <https://feedly.com/>;Hacker News <https://news.ycombinator.com/>
