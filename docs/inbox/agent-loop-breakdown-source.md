> 原文存档:微信文章《拆 Agent:AI 的"自己拿主意"是怎么发生的》(公众号:小九带你玩AI)
> 原始链接:https://mp.weixin.qq.com/s/_QGjNvwnKiFkteC7alEmbA
> 抓取日期:2026-08-13(手机 UA curl,避开微信环境验证)
> 用途:整理收件箱素材;与站内 agent-intro.md 去重后,提炼增量(四步循环教学命名/WorkBuddy 实例/Craft-Plan-Ask 三模式/别打断循环)补充之,正文原样保留供追溯。

---



---

前两篇我说：

>

Skill 是菜，3 件套是菜谱。
Agent 是厨师。

但有读者问：

>

"厨师（Agent）到底是怎么干活的？为啥它能自己拿主意？"

今天这篇，我把 Agent 拆开给你看。

---

# Agent 不是"变聪明"，是"循环"

先纠正一个常见误解：

>

很多人以为 Agent = 更聪明的 AI。

![](https://mmbiz.qpic.cn/mmbiz_png/4G249J20uAgSR0sH7VazQGDkBeNdufyKL8BBicpyib6PIRiaVJFRIMJl7aUibL68bS6JDjOUXHLmjbrgnxdBeFT6BWUtnzFsh9N9oTNKKAOF4n4/640?wx_fmt=png&from=appmsg)

会重复跑一个 4 步循环的协调员：

步骤

行业术语

大白话

第 1 步

Observe（观察）

看看现在情况是啥

第 2 步

Think（思考）

想想要干啥、按啥顺序

第 3 步

Act（执行）

调 Skill / 工具动手做

第 4 步

Reflect（反思）

做完了吗？没完就回第 1 步

这个 4 步循环不是 Anthropic / OpenAI / 腾讯谁发明的 — 是 AI 圈 2022 年 ReAct 论文（Reasoning + Acting）提出来的，到 2026 年已经是所有 Agent 的行业共识标准。

下面，用 WorkBuddy 真实例子拆给你看。

---

# 第 1 步 · 观察（Observe）

观察 = Agent 看看现在情况是啥。

![](https://mmbiz.qpic.cn/mmbiz_png/4G249J20uAgiaqE07v7AyDzFTyGykp3M3QTZZGvwFAIianubgzM7u03ZLhkResbEFyibPgt6dPVSRdEuezVC1p0YBKEic0yophiaMAoNf9ibryzho/640?wx_fmt=png&from=appmsg)

把所有相关信息摆出来：

💬用户输入— "我是运营，本周做了 3 件事..."

📄当前文件— 钉钉文档里的本周聊天记录

🕐历史对话— 上周周报 + 上月数据

📋任务上下文— 今天是周五 + 公司周报模板

Agent 先"看见"这些信息，才能往下想。

>

观察步的核心：把所有需要的信息摆出来，别让 Agent 凭空猜。

---

# 第 2 步 · 思考（Think）

思考 = Agent 想想要干啥、按啥顺序。

![](https://mmbiz.qpic.cn/mmbiz_png/4G249J20uAiauw1oOg4GnoiaylJvZaOFw0620ibsREHsib8eQ1CrgT9cduP6qjIfZKoGMo2S0ZnH0hXic5tnvjiaHSX54wGV5vAiaOJsFnzu4ZzJPc/640?wx_fmt=png&from=appmsg)

把任务拆成几步：

根任务：写周报

├─ 子任务 1：拆解用户说的"本周 3 件事"

├─ 子任务 2：查本周聊天记录补全细节

├─ 子任务 3：匹配公司周报模板

├─ 子任务 4：调"生成周报"Skill 生成

└─ 子任务 5：写到钉钉文档对应位置

思考步的核心：

>

把"一句话需求"拆成"5-10 个子任务"，决定先做哪个后做哪个。

---

# 第 3 步 · 执行（Act）

执行 = Agent 调 Skill / 工具动手做。

![](https://mmbiz.qpic.cn/mmbiz_png/4G249J20uAhcwnlv4XW9ricVAbxt2AEvPv3143sEFs5qZOrDGqBzXtlWduia0fJ1UIlFMKD8MxjR7vGu6EBKMiaHpx9M5xSibI5SyHF82ZIt2jI/640?wx_fmt=png&from=appmsg)

🔧调"读文件 Skill"— 读取聊天记录 + 周报模板

🔧调"调模型 Skill"— 调用混元 / DeepSeek 生成周报正文

🔧调"写文件 Skill"— 把内容写回 Word 文档

🔧调"通知人 Skill"— 钉钉通知直属领导

每一步都调一个 Skill — 这就是 Day 1 说的"Agent 是厨师、Skill 是菜"。

---

# 第 4 步 · 反思（Reflect）

反思 = Agent 做完了吗？没完就回第 1 步。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/4G249J20uAg7XjXdjxlIViasE1teSdjhLxLbibBicxr3ibJib2gPhSadgksAzVM575ibAW0VCDWoAKodIhkueVndYpydRrf19y92ssTmicG2Wekiaiaw/640?wx_fmt=png&from=appmsg)

✅周报字数够了吗？（< 800 字 = 重写）

✅周报结构对吗？（缺"下周计划" = 重写）

✅数据对吗？（本周拉新不是 5000 = 改）

✅通知发出去了吗？（没收到 = 再发）

只要有一项不对，Agent 就会回到第 1 步"观察"— 重新看信息 → 重新想 → 重新做。

这就是 Agent 跟普通 AI 的最大区别：

>

普通 AI 一次性输出；Agent 跑循环，直到事情真做完。

---

# WorkBuddy 内部：6 层架构 + 100 个专家协同

讲了这么多理论，举个真实例子。

![](https://mmbiz.qpic.cn/mmbiz_png/4G249J20uAgwz0d1wsAty9KiatUeUVia9R92t1Kk2ON4bue0QILGv2KOPvStFppliapnt05krPdrQ3Arz087LuhXJb53lZzb5nlhfHZsAxE3EQ/640?wx_fmt=png&from=appmsg)

6 层架构：

任务入口层

— 你从桌面 / 微信 / 飞书下达指令

任务与上下文层

— 拿到任务 + 上下文 + 历史记忆

Agent 编排与推理层

—就是跑"观察→思考→执行→反思"循环的地方

执行能力层

— 调 Skill / MCP / 浏览器 / 第三方服务

数据与交付层

— 生成产物（报告 / 表格 / PPT）+ 分享

横向治理层

— 权限 / 高风险确认 / 审计

第 3 层（Agent 编排与推理层）就是 4 步循环的"工位"。

而且 WorkBuddy 里有100+ 领域专家（通用 Agent + 办公 Agent + 研发 Agent + 运营 Agent + 设计 Agent + 数据 Agent ...）协同工作，每个专家在自己的小循环里跑，再汇集成大循环。

---

# 3 种模式：Craft / Plan / Ask

WorkBuddy 还有 3 大工作模式，决定 Agent 跑到哪一步停：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/4G249J20uAhcia9buHnjrS9hgneiaJc2IeMjQhcicoibYdtK2V4H89azRf5NrRCwxS0HKSib2X77acNVwE5mFOlmvrUzQicmhjyHDv3yxxVke6fog/640?wx_fmt=png&from=appmsg)

干啥

适合啥场景

Craft（执行）

直接干，干完汇报

写周报 / 整理文件

Plan（计划）

先出方案让你审，再干

高风险 / 复杂决策

Ask（询问）

只读不写，纯讨论

技术调研 / 代码审查

---

# 别打断 Agent 的循环

最后讲最关键的一点。

![](https://mmbiz.qpic.cn/mmbiz_png/4G249J20uAiaTfiaIpQO1EicGWjfDUq4J5xa900669eI7TPicOoZY033r7hJupSa3rkfNAXkDibgLn2AfDzdTo4WS4rC0MAaBvoJMFnNPpsllSY8/640?wx_fmt=png&from=appmsg)

最怕的事就是被用户打断：

打断方式

后果

每隔 30 秒插一句"快好了吗？"

Agent 反复回到"观察"步

中途换需求"再加个 PPT"

Agent 推倒重来

关掉窗口 / 杀掉进程

循环中断，下次要从头跑

这就是为什么很多人觉得"AI Agent 不好用" —不是 Agent 不行，是你一直在打断它循环。

---

# 写到最后

前两天讲了 Skill 和菜谱，今天讲了 Agent 怎么干活。

![](https://mmbiz.qpic.cn/mmbiz_png/4G249J20uAjK8OWp0WnBBgTJyQWicT9HOic1jSBgTbhglkXmTVBxhNAdnicmfsgRIy6fzzwlYyBTmeo9vrwpGD98kJO346YIfsszs9RXHGlt6w/640?wx_fmt=png&from=appmsg)

Agent 不是变聪明 — 它在循环

4 步循环 = 观察 → 思考 → 执行 → 反思

WorkBuddy 100+ 专家协同 = 多个小循环组成大循环

别打断 Agent 循环 — 打断一次，重来一次

明天 Day 4，讲 Skill 和 Agent 到底啥关系 — "1 个 Agent + N 个 Skill"是怎么 1+1>2 的。

评论区告诉我：你之前用过哪些 AI 工具？有没有感觉"它好像在来回折腾"的时候？大概率就是 Agent 在循环里重跑。

---
