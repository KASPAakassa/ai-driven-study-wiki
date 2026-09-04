# 原始资料:拒绝盲目重试,腾讯AI Lab联合港中文提出Agent"推理时验证"新范式

> 来源:微信公众号(作者:jude_zkh),《拒绝盲目重试,腾讯AI Lab联合港中文提出Agent"推理时验证"新范式(附4K开源数据集)》
> 原文链接:https://mp.weixin.qq.com/s/q5Iw_nZ0gFR0vH-81ezbXA
> 抓取日期:2026-08-09;状态:已拆解为两篇:09-agent-research(学术解析)+ 03-agents(设计范式)
> 论文:Wan, Y., Fang, T., Li, Z., et al. (2026). Inference-Time Scaling of Verification. arXiv:2601.15808

---

导语最近，Deep Research Agent火爆出圈，从OpenAI到各大厂纷纷入局。但在动辄几十页、上百步的长链路任务中，Agent“一本正经地胡说八道”或“静默失败”的问题依然让人头疼。
传统的Test-Time Scaling（如Best-of-N并行采样）往往只是让Agent在同一个坑里反复跌倒。如何低成本、高效率地让Agent在推理时“自我进化”？
近日，腾讯AI Lab联合港中文、人大发布最新论文《Inference-Time Scaling of Verification》，提出了一种基于评分标准（Rubric）引导的验证框架 DeepVerifier。不仅在GAIA等硬核榜单上狂飙 8%~11% 的准确率，还开源了 DeepVerifier-4K 反思数据集！

💡 一、 痛点：Agent为什么总是“翻车”？
在长周期（Long-horizon）的自动化知识发现任务中，Agent面临着巨大的挑战：
错误级联：早期找错了一个网页，后续几十步推理全盘皆输。

监督成本极高：让人类去盯几百个Step的轨迹，根本不现实。

传统Test-Time Scaling失效：像Reflexion或Best-of-N这样的方法，让Agent重新解一遍题，它大概率还是会犯同样的逻辑错误或幻觉。

破局点在哪里？论文引入了一个极具启发性的概念：验证的不对称性（Asymmetry of Verification）。
“解出一道复杂的综合题很难，但拿着答案去查证其中的几个关键线索，却容易得多。”

基于此，作者放弃了“让Agent重新做一遍题”的传统思路，转而将复杂的验证任务拆解为简单的“信息检索子任务”，通过定向查错来实现自我进化。
📊 二、 核心干货 1：首份《DRA失败分类学》
要想让Agent学会反思，首先得知道它到底是怎么错的。 作者团队在WebAggregatorQA数据集上收集了近3000个Step的轨迹，人工标注了555个错误点，并归纳出了一份极具工业参考价值的 《DRA Failure Taxonomy》（深度研究Agent失败分类学）。
这5大类“翻车”原因，简直精准踩中了每一个Agent开发者的痛点：
🕵️ Finding Sources（找源错误 - 占比最高）

症状：病急乱投医，依赖二手营销号或无关网页，导致关键证据缺失。

🧠 Reasoning（推理错误）

症状：强行脑补、滑坡谬误、 premature conclusions（ prematurely 下结论），或者对检索到的信息过度自信。

🎯 Problem Understanding（理解偏差）

症状：没看懂Prompt，目标漂移，做着做着就偏离了用户的原始意图。

⚙️ Action Execution（执行错误）

症状：API调用失败、UI点击错位、代码格式报错。

🔄 Trajectory Efficiency（效率低下）

症状：陷入死循环，为了一个错误疯狂重试，直到耗尽Max Step。

👨‍💻 开发者启示：在做Agent评测和Debug时，不要再只看“最终答案对不对”，而应该建立类似的Taxonomy，针对高频错误（如找源和推理）设计专门的干预机制。
🛠️ 三、 核心干货 2：DeepVerifier 架构拆解
基于上述分类学，作者提出了 DeepVerifier 框架。它不是一个简单的“LLM-as-a-Judge”，而是一个多模块协同的“找茬”流水线。
📍 Step 1: 轨迹摘要与“找茬” (Decomposition Module)
Agent的轨迹动辄几百万Token，直接喂给Judge模型必死无疑。 Decomposition Agent 会先做两件事：
压缩轨迹：提取每一步访问的URL和获取的核心事实（Fact/Number）。

对号入座：拿着《失败分类学》去扫描摘要，找出“可疑行为”，并生成高杠杆的Follow-up问题（例如：“Source X 中真的提到了数据 Y 吗？”）。

📍 Step 2: 定向验证 (Verification Agent)
这是最精妙的一步！ 验证Agent不去重新解原题，而是拿着Step 1生成的Follow-up问题，去外部网络进行定向检索和交叉验证。这就把“复杂推理”降维成了“简单的事实核查”。
📍 Step 3: 基于Rubric的裁判 (Judge Module)
Judge Agent 根据验证结果，结合预设的 Rubric（评分标准） 进行打分（1-4分）。
1分：完全错误； 2分：大部分错误； 3分：大部分正确； 4分：完全正确。如果分数 ≤ 2，Judge 会生成带有明确指令的 corrective feedback（例如：“不要搜通用词，去搜XX公司的最新财报第X页”），打回给主Agent重试。

📈 四、 实验结果：推理时计算的“缩放奇迹”
这套“不重新做题，只查漏洞”的机制，效果如何？论文在多个硬核榜单上给出了答案：
1. GAIA 榜单狂飙
在需要极强Web浏览和推理能力的 GAIA 数据集上：
使用 Claude-3.7-Sonnet 作为底座，经过 DeepVerifier 的迭代反馈（通常在3-4轮达到峰值），GAIA-Web 子集准确率从 51.1% 飙升至 63.3%（提升超12%）！

即使是 GPT-4.1 和开源的 Qwen3-8B，也能获得显著的涨点。

2. 成本与收益的完美平衡
相比于 Best-of-N 需要完整重跑几十次，DeepVerifier 每轮只需要检索 ≤3 个 targeted 问题。在推理成本（Token消耗）和准确率之间，取得了极佳的 Trade-off。

🎁 五、 开源福利：DeepVerifier-4K 数据集
闭源模型虽然强，但开源社区如何获得“反思能力”？ 论文团队不仅授人以鱼，还授人以渔，直接开源了 DeepVerifier-4K 数据集！
数据规模：4,646 条高质量 Prompt-Response 对。

数据来源：从400个真实的Agent验证轨迹中，过滤出True Positive（精准抓出错误）和True Negative（精准放过正确答案）的“黄金反思样本”。

用途：专门用于 SFT（监督微调），训练开源模型的 Reflection & Self-Critique（反思与自我批评） 能力。

实验证明：用该数据集微调后的 DeepVerifier-8B（基于Qwen3-8B），在配备反思模块后，准确率比原版 Qwen3-8B 提升了 5.5%，甚至超越了许多未经反思训练的更大模型！
🔗 代码与数据获取：
GitHub: github.com/Tencent/CognitiveKernel-Pro

GitHub: github.com/yxwan123/DeepVerifier

🚀 六、 总结与对Agent开发者的3条实操建议
这篇论文不仅提出了一个SOTA的框架，更是对Agent Test-Time Scaling 范式的一次重要纠偏：从“盲目扩大搜索/重试”走向“精准验证与反馈”。
对于正在做 Agent 落地或评测的团队，本文提供以下3条实操建议：
🛑 放弃 Holistic Judge（整体评判）：不要让LLM直接看着几万字轨迹判断对错，它一定会幻觉。必须引入Decomposition（拆解），把验证转化为外部可检索的Yes/No问题。

📝 建立你的 Failure Taxonomy：参考论文的5大类，针对你的业务场景（如代码生成、数据分析）梳理出专属的错误分类学，这是写出高质量 Rubric 和 Feedback Prompt 的前提。

🔄 重视“反思数据”的构建：不要只拿成功轨迹做SFT。那些“Agent犯错 -> 被精准指出 -> 修正成功”的轨迹（如DeepVerifier-4K），才是训练Agent自我进化能力的无价之宝。

👇 互动时间你在开发或测试 Agent 时，遇到过最离谱的“静默失败”或“幻觉”是什么？欢迎在评论区吐槽交流！
如果觉得这篇文章对你有启发，别忘了点赞、在看、分享三连支持！我们将持续追踪全球最前沿的 AI Agent 技术干货。
参考文献
Wan, Y., Fang, T., Li, Z., et al. (2026). Inference-Time Scaling of Verification: Self-Evolving Deep Research Agents via Test-Time Rubric-Guided Verification. arXiv:2601.15808.