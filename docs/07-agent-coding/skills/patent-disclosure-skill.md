# patent-disclosure-skill:把专利交底书变成可追溯的自动化流程

> **一句话摘要**:做过专利交底书的人都懂那种"又碎又磨人"的痛苦——找创新点、梳技术方案、补实施例、画图、国知局查新、版本越改越乱。`patent-disclosure-skill`(GitHub 4000+ Star,MIT 开源)最聪明的地方不是"会写",而是"**不会乱写**":把整个流程拆成 4 个固定环节、每环节用独立 Prompt 约束 Agent,数据来源、检索结果、图表生成、修改链条全部可追溯——每一步都有来源、可验证、可修订,这是它最有价值的"防幻觉"路线。
>
> **来源**:微信公众号「AI前沿速递」《一个国产开源 Skill 火了:科研专利交底书,终于不用手搓了》,https://mp.weixin.qq.com/s/4TcjXGKVGQZC2PrHdKNiBQ;项目:https://github.com/handsomestWei/patent-disclosure-skill;原始资料存档于 `docs/inbox/patent-disclosure-skill-source.md`

## 概念:这不是"写作机器人",是"专利工作流自动化工具"

!!! tip "为什么不能靠'让大模型一次生成交底书'"
    纯靠大模型一次生成整份交底书,通常会遇到三个典型问题:①**结构松散**——段落齐全但逻辑链不严密,创新点/技术问题/解决方案/实施方式对不上;②**脱离真实材料**——仓库里没有的模块、文档里没的设计,模型会"合理脑补";③**图表不可控**——AI 随便画的图形式像样但不够严谨,后续难改。

专利交底书不是一篇"文笔流畅"的文章,而是一份**对技术方案进行结构化表达和证据化组织的工程文档**。比起"一步到位",更关键的是:每一步的数据来源是什么、判断依据是什么、结果能不能回溯。

## 原理:4 个关键环节的完整闭环

### 环节 1:项目扫描与专利点挖掘

对项目中的代码和文档(Markdown/Word/PPT)做系统扫描提取;**不会在扫描后立刻给"最终答案",而是先列出候选专利点**——相当于先做一次"技术创新点筛查":哪些更像创新、哪些只是常规实现、哪些写法不当会让保护范围过窄、哪些虽新但表述要打磨。本质是**专利视角下的技术重构**。

### 环节 2:新颖性与现有技术检索(查新)

对接国家知识产权局官网,用 Playwright 获取最新专利数据;**四层降级兜底**:Playwright → requests → curl → Google Patents,每层有日志记录(即便某一层失败,也能追踪问题在哪,不让流程黑箱中断)。

!!! tip "最关键的判断设计:先抓真实摘要,再交 LLM 判断相关性"
    不是简单关键词匹配(传统检索经常"看着像、实际不相关"),而是**先抓取真实专利摘要,再交给 LLM 做关联判断**——接近人工审阅逻辑。项目给出的数据:相关性识别准确率从约 **60% 提升到 95% 以上**。查新之后,有创新/已有类似现有技术的点会清晰区分,后续生成聚焦更有价值的部分。

### 环节 3:交底书成稿与图表生成

按**脱敏模板**生成交底书正文;系统框图与流程图先生成 **Mermaid 代码**,再渲染成 PNG,最后打包进 `.docx`。

!!! note "为什么图表要先生成 Mermaid 代码再渲染"
    图不是 AI 随意"画"出来的,而是结构化代码 + 渲染——**可控、可修改、可复现**,相比直接生成不可编辑图片,更适合严肃文档场景。

**版本管理防灾难**:输出文件采用 `{案件名}_{时间戳}` 命名,避免"最终版/最终版2/最终版_修改后_真的最终版"。

### 环节 4:自检与迭代管理

自动检测**逻辑闭环性**并生成单独报告,供 Agent 继续修改。支持两种迭代模式:

| 模式 | 场景 |
| --- | --- |
| **合并新材料** | 新增方案说明/实验结果/参数设计,并入现有交底书 |
| **纠正纠错** | 根据查新意见或人工审核反馈修订纠偏 |

每次迭代产生新文件版本,可回溯("第三版和第二版差什么?为什么改?改的是查新冲突还是实施例不足?"都能保留)。

## 代码 / 实现:查新相关性判断的两种路线对比(纯 Python)

演示"关键词匹配 vs 真实摘要 + LLM 判断"的逻辑差异(对应 60% → 95% 的提升来源):

```python
# —— 查新相关性判断:关键词匹配 vs 摘要判断 ——
def keyword_match(keywords: list, patent_title: str) -> bool:
    """传统路线:标题含关键词就算相关(容易'看着像,实际不相关')"""
    return any(k in patent_title for k in keywords)

def abstract_judge(claim: str, abstract: str, llm_like) -> bool:
    """升级路线:先抓真实摘要,再判断技术方案是否实质相关"""
    return llm_like(claim, abstract)   # 模拟 LLM 对摘要做语义关联判断

# —— 模拟:一个"数据缓存"专利点,两篇标题像但摘要不同的专利 ——
claim = "基于分层索引的分布式数据缓存"
keywords = ["缓存"]
patents = [
    {"title": "一种分布式数据缓存系统", "abstract": "面向 Web 服务的分布式缓存,含一致性哈希与过期策略",
     "llm_verdict": True},    # 摘要实质相关(都讲缓存)
    {"title": "基于缓存的分布式计算任务调度", "abstract": "调度器利用本地缓存加速任务分发,不涉及缓存本身设计",
     "llm_verdict": False},   # 摘要不相关(缓存只是配角)
]

for p in patents:
    kw = keyword_match(keywords, p["title"])
    ai = abstract_judge(claim, p["abstract"], lambda c, a: p["llm_verdict"])
    print(f"  标题: {p['title']}")
    print(f"    关键词匹配: {'相关' if kw else '不相关'} | 摘要+LLM 判断: {'相关' if ai else '不相关'}")
```

## 实践 / 应用:怎么上手与边界

### 安装与触发

```bash
git clone https://github.com/handsomestWei/patent-disclosure-skill.git
cd patent-disclosure-skill
pip install -r requirements.txt
# 打开 Codex,输入:帮我安装 https://github.com/handsomestWei/patent-disclosure-skill
# 安装后自然语言触发:
#   "帮我做专利挖掘" / "梳理专利点" / "写技术交底书"
```

用户真正需要做的可能只有一句自然语言指令,剩下的扫描、查新、成稿、图表渲染基本全自动。

### 边界(必须讲清楚)

1. **不能替代法律意见**:生成内容是辅助性技术材料,真正申请时仍需专业人士审核把关;
2. **默认只查中国国知局**:不含 USPTO、EPO 等国际数据库——有国际布局需求需额外补充检索;
3. **定位**:不是在替代专利代理工作,而是大幅降低前期资料整理、检索、初稿组织和版本管理成本。

!!! tip "与站内其他文章的呼应"
    - 本 skill 的"防幻觉"设计(先固定数据来源/检索结果/图表方式/修改链条,每一步可追溯可修订)正是 [Spec-First 决策栈](../experience/spec-first-decision-stack.md) 的"证据分级"在专业流程上的落地;
    - 4 环节固定 Prompt + 独立约束 = [AI Coding Harness 设计经验](../experience/ai-coding-harness-design.md) 的"护栏"思想;
    - 四层降级抓取(Playwright→requests→curl→Google Patents)= [Agent 系统 5 决策](../../03-agents/agent-system-5-decisions.md) 的"Fallback"与 [生产级 9 层架构](../../03-agents/ai-infra-layering.md) 的容错;
    - 时间戳命名防版本混乱 = [Agent 交接方法论](../experience/handoff-handover-methodology.md) 的"可追踪交付物";
    - 与站内科研系列 [科研领域现成 Skill 收藏](research-skills-collection.md) 互补。

## 总结

- **定位**:专利工作流自动化工具(不是写作机器人)——把"生成交底书"拆成可执行、可追溯、可迭代的流程;
- **4 环节**:扫描挖掘(先列候选不武断下结论)→ 查新检索(真实摘要 + LLM 判断,60%→95%)→ 成稿图表(Mermaid 可控渲染 + 时间戳命名)→ 自检迭代(逻辑闭环报告 + 合并/纠错两种模式);
- **最有价值的"防幻觉"路线**:不是追求模型一句话把所有事做完,而是**让每一步都有来源、可追溯、可验证、可修订**;
- **边界**:辅助材料非法律意见;默认仅中国国知局;降低的是前期整理成本,替代不了专业审核。

## 延伸阅读

- 项目:https://github.com/handsomestWei/patent-disclosure-skill;原文:https://mp.weixin.qq.com/s/4TcjXGKVGQZC2PrHdKNiBQ
- 站内:[科研领域现成 Skill 收藏](research-skills-collection.md)、[Eval Engineering Skill](eval-engineering-skill.md)(评估驱动)、[Spec-First 决策栈](../experience/spec-first-decision-stack.md)(证据分级)、[AI Coding Harness 设计经验](../experience/ai-coding-harness-design.md)(护栏)、[Agent 系统设计的 5 个决策](../../03-agents/agent-system-5-decisions.md)(Fallback/容错)
