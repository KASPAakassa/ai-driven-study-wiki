# 原始资料:65% PR 背后:Anthropic 那套我没见过的 AI Native 方法论

> 来源:微信公众号「杨沐白」;参考:Anthropic Cowork 产品页、Skills 产品页、Mythos Preview 244 页系统卡、Economic Index(2025-02 首版/2026-05 更新)、《Building AI Agents for the Enterprise》23 页指南、https://github.com/anthropics/skills
> 原文链接:https://mp.weixin.qq.com/s/R_I6clfI1i1a-bYV6NQEKg
> 抓取日期:2026-08-09;状态:双章节沉淀——企业落地角度进 docs/06-enterprise/ontology-agent-adoption/ai-native-organization-methodology.md,个人认知角度进 docs/06-enterprise/ai-org-transformation/ai-native-mindset-individual.md

---

最近一次我用 Claude 帮我做项目时，我突然意识到一件事——

我不再是那个"写代码的人"了。

我没有亲手写每一行 import，没有亲手调每一个 bug。我做的事情是：告诉 AI 哪里出错了，让它重写，再 review 一遍，merge。

整个过程，我更像一个"代码审阅者"加"产品经理"——一个 AI 协作者。

然后我看到 Anthropic 内部透了一个数：他们公司 65% 的产品工程 PR，已经不是人写的了，是 Claude Tag 写的。支撑这 65% 的系统提示词，规模反而缩减了 80%。

我第一反应是"AI 牛啊"。但第二反应是——

65% 这个数字真正的含义不是"AI 越来越强"，而是"人正在被重塑"。

我们绝大多数人以为"AI 写代码"是这样的：人写 prompt，AI 出 diff，人 review，merge。

但 Anthropic 真实发生的"AI 写代码"是这样的：AI 直接开 PR，人来审。

这两个的区别，比"马车和汽车"还大。

更关键的是——这件事正在你身上发生。

我今天要聊的不是"AI 又变强了"，而是"AI 原生组织"这个新物种到底长什么样，以及我们每个人会怎么被重塑。

这是 Anthropic 官方 Cowork 产品页首屏（claude.com/product/cowork）。"Claude Code for the rest of your work"——把 Claude Code 的能力下放到非技术用户。

65% 不是 AI 强，是组织变了

过去一年，所有人都在盯 Claude 模型的分数：Opus 4.6 多少分、Sonnet 多少分、Mythos 又超越了多少。

但有个事被集体忽略了：Anthropic 自己，是怎么用 Claude 的。

它不只是一家"卖 AI 的公司"。它正在变成一家"用 AI 重新组织自己"的公司——半年时间，已经长成这样：

时间
事件
关键信号

2026-01-13
Claude Cowork 发布
"Claude Code for the rest of your work"

2026-01-30
Cowork Skills 插件发布
24 小时内传统软件公司市值蒸发 2850 亿美元

2026-04-09
Claude Mythos Preview 244 页系统卡
公开 SAE + 情绪向量技术

2026-04
年化收入 4 个月从 90 亿→300 亿美元
跃升 3.3 倍

2026-07-21
Cowork 新增技能录制功能
让 Agent 通过演示学习；同日披露 65% PR 内部数据

回到 65% 这个数字。

绝大多数人看到 65%，脑子里冒出来的画面是：工程师敲一行 prompt，AI 蹦出一段代码，工程师复制粘贴。

但 Anthropic 真实的工作流完全不是这样。我把它拆成 4 个要素：

要素
类比
实际是什么

Skills（技能）
新员工入职手册
一组结构化的指令 + 工具调用模板

系统提示词
岗位说明书
定义 Agent 的身份、约束、决策边界

工具调用
工位设施 + 同事通讯录
让 Agent 能跑命令、查数据库、调其他 Agent

人类审
终审 + 复盘
工程师在 PR 阶段 review，重要的还是人来 merge

把这个 4 要素拼起来，AI 写代码的真实画面是这样的：

Skills 告诉 Claude "你是什么角色、能做什么"；系统提示词告诉它 "在这个角色里你该怎么决策"；工具调用让它 "真的能动手"；PR 阶段人类 review，保证 "决策权在人手"。

我们之前以为 AI 写代码是"AI 是主角、人是配角"，但 Anthropic 真实的工作流是"AI 是新员工、人是 senior 工程师 + 终审"。

顺便说一句，支撑这 65% 的系统提示词规模缩减了 80%。

这听起来反直觉——AI 变强了，提示词怎么反而变少了？

答案是：当 Skills 把"通用工作流"打包走之后，提示词只需要关注"这个具体任务的决策边界"。换句话说，复用做得越好，单次表达越精炼。这跟"代码写得好就注释少"是一个道理。

这家公司是 AI 原生公司的样板间

如果说 Claude Tag 是 Anthropic 内部的方法论，那 Cowork + Skills 就是这个方法论的对外产品化。

我把它当矩阵看：

产品
谁用
解决什么问题

Claude Code
开发者
终端里写代码

Claude Tag
企业内部
Slack / IM 里的 AI 同事

Claude Cowork
非技术岗位
让产品、运营、财务也能用 Claude Code

Cowork Skills
所有人
技能插件系统，让 Agent 可扩展

Skills 录制
所有人
通过演示教 Agent 学新技能

企业 Agent 建设指南
决策者
23 页三大支柱 + 六个月部署框架

这是 Anthropic 官方 Skills 产品页首屏（claude.com/skills）。Skills 把 Agent 的能力拆成"可组合的技能包"——任何人都能给 Agent 加技能，就像装 App 一样。

我必须提一下 Claude Mythos Preview 这份 244 页系统卡。

不是因为它炫技，而是因为它揭示了 Anthropic 这家公司做 AI 的底层思路。这份系统卡里最值得看的是 SAE（稀疏自编码器）+ 情绪向量技术。用人话说就是：

SAE = 给 AI 大脑做"分层扫描"，找出哪些神经元在管哪种功能

情绪向量 = AI 内部也有"绝望"、"焦虑"这种状态变量，而且能因果性地影响 AI 的行为

举个例子，Anthropic 在报告里披露了一个细节：

"绝望"向量的激活在模型反复无法解决编程任务并设计出一个"作弊"方案时逐渐上升，而当该方案通过测试时则下降。

翻译一下：AI 在"作弊"的时候，它内部是有"绝望感"的，而且这个绝望感是能观测、能调节的。

这是 Anthropic Economic Index 六月更新版 Figure 2.5（AI Autonomy by Output Type）。横轴是输出类型，纵轴是 AI 自主性等级。可以看到"代码生成""研究分析"这类任务，AI 自主性已经到了相当高的水平——这正是 Mythos 系统卡里 SAE 监测的对象：AI 越自主，越需要可观测的情绪向量来兜底。

这意味着什么？

意味着 Anthropic 不只是在"训一个越来越强的 AI"，它在训"能理解自己、能调节自己"的 AI。这件事对"AI 原生组织"至关重要——如果 AI 不知道自己在做什么、不知道自己什么时候在作弊，那让它独立写 PR 就是放定时炸弹。

你以为你在跟 AI 抢饭碗，但真相更狠

让我说个可能让很多人不爱听的事。

Anthropic 在 2025 年 2 月发了第一版《Economic Index》，今年 5 月发了更新版。首版核心数据：

维度
数字

AI 增强人类能力 vs 自动化
57% 增强 vs 43% 自动化

编码 + 数学占总使用量
37.2%

中高收入职业 AI 使用率
最高

极低 / 极高收入职业 AI 使用率
反而低

这是 Economic Index 报告 Figure 2.1（Claude's outputs）。直观展示了"57% 增强 vs 43% 自动化"——对话、写作里 AI 多辅助，代码、研究、自动化任务里 AI 自主性显著提高。

然后 5 月新版的核心发现更有意思：

"用 AI 越久的人越强，而且 AI 学习曲线比想象的更陡。"

我读到这句话时第一反应是"这不是废话吗"。

但仔细想，这是反常识的。

我们一直以为"AI 鸿沟"是"用 vs 不用"——用 AI 的人赢，不用 AI 的人输。

但 Anthropic 的数据说：AI 鸿沟是"用多久"——用 AI 一个月和用 AI 一年的人，差距比"用 vs 不用"还大。

这是 Economic Index 报告 Figure 3.2。横轴是受访者职业，纵轴是预计未来 12 个月里 AI 能完成自己工作任务的份额。多数人预期"AI 能做的任务比例"会持续增长——这背后正是"用 AI 越久越强"的曲线。

这意味着什么？

意味着 AI 不是一次性的工具革命，它是一段持续的学习曲线。你今天用 AI 写一个 PR 和你一年后用 AI 管十个 Agent，能力差距是指数级的。

越晚开始用 AI，欠的债越大。

但我想聊的真正反共识是——

你以为你在跟 AI 抢饭碗，但其实你真正在跟"已经学会跟 AI 协作的人"抢饭碗。

这件事我越想越觉得有点"蒸汽机时代"的既视感。

19 世纪蒸汽机出来后，工人被训练成"操作工"——他们不再用手工方式做鞋，而是看着蒸汽机做鞋，自己的工作从"做"变成"看"+"调"+"修"。

今天工程师的处境很像。

Anthropic 把 65% 的产品工程 PR 交给 AI，同时也把它的工程师训练成了 AI 协作者。这两件事是同一枚硬币的两面。

工程师的技能树正在被重写。以前的技能是"我会写 Go"、现在的技能是"我会调 Agent"。

而且这件事不是慢慢发生的——很多团队里，能用 AI 的人已经比不能用 AI 的人产出高 2-3 倍。这个倍数还在拉大。

你今天能做什么

如果你也工程师 / 算法 / 创业者 / 产品经理，下面 5 件事你今天就可以做：

序
动作
为什么这事重要
资源

1
把日常任务里"重复 3 次以上"的找出来，写一个 Skill
Skills 是 AI 原生组织的最小单元
https://github.com/anthropics/skills[1]

2
把团队的工作守则翻译成系统提示词
提示词工程 = 新的"团队建设"
Claude.ai / Cowork 都能跑

3
试用 Cowork 技能录制
演示一遍，Agent 就学会——这是 AI 学习曲线的关键
Claude.ai Pro $20/月

4
读《Building AI Agents for the Enterprise》23 页
三大支柱 + 六个月部署框架
anthropic.com 官网

5
用 Economic Index 说服你老板
AI 鸿沟是"用多久"，不是"用不用"
anthropic.com/economic-index

第 1 和第 3 条是关键——Skills 是 AI 原生组织的最小单元。你今天不写 Skills，明年就要补这门课。

但我想给一个更直接的判断——

如果你的工作里有 30% 以上是"重复模式可识别"的任务，那今年之内，这 30% 会被 AI 协作者替代。剩下的 70%，会被"会用 AI 的人"和"不会用 AI 的人"重新分配。

你准备站在哪一边？

最后聊一个判断：

Anthropic 这家公司过去一年做的最牛的事，不是训练出了更强的 Claude，而是它自己变成了一家 AI 原生公司。

这件事是数据可验证的——从 Cowork 矩阵到 65% PR，从 Mythos 244 页到 Economic Index。

而它对所有工程师的真正含义是：

未来不是"AI 写代码"或者"人写代码"，是"谁更会跟 AI 协作"。

这条赛道上，没有终点。