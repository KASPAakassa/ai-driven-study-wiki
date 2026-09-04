# AI 原生组织方法论:Anthropic 的 65% PR 与 Skills 最小单元

> **一句话摘要**:一家公司怎么用 AI 重新组织自己?Anthropic 给出可量化答案:65% 的产品工程 PR 由 AI 同事(Claude Tag)撰写,支撑它的系统提示词规模反而缩减了 80%。本文站在【企业落地】角度拆解这套"AI 原生组织"方法——四要素协作模型、Skills 作为最小组织单元、可观测性兜底与从试点到 AI 原生的转型路径,附可运行的"任务 Skill 化识别"纯 Python 演示。
>
> **来源**:微信公众号「杨沐白」《65% PR 背后:Anthropic 那套我没见过的 AI Native 方法论》,https://mp.weixin.qq.com/s/R_I6clfI1i1a-bYV6NQEKg;参考 Anthropic Cowork/Skills 产品页、Mythos Preview 244 页系统卡、Economic Index、《Building AI Agents for the Enterprise》23 页、https://github.com/anthropics/skills;抓取日期 2026-08-09,存档于 `docs/inbox/ai-native-methodology-source.md`

## 概念

### 65% 这个数字,说的不是模型,是组织

Anthropic 内部披露:**65% 的产品工程 PR 由 AI 同事 Claude Tag 撰写**,支撑它的系统提示词规模反而**缩减了 80%**。第一反应是"AI 变强了";但 65% 不是 AI 强,**是组织变了**——这家公司把代码产出交给 AI,把人的位置从"写"挪到了"审"。

### 真实工作流:AI 直接开 PR,人来审

| 维度 | 想象的 AI 写代码 | Anthropic 的真实工作流 |
| --- | --- | --- |
| 谁产出 | 人写 prompt → AI 出 diff → 人 merge | **AI 直接开 PR → 人来审** |
| 人的角色 | 写代码的人(主角) | senior 工程师 + 终审 |
| 决策权 | 隐含在 prompt 里 | 显式保留在人的 merge 上 |

!!! warning "区别比马车和汽车还大"
    前者 AI 的产出上限是"人会想到的指令",改变个人效率;后者是"组织沉淀的方法论",改变组织形态——原文用"**人正在被重塑**"概括。

## 原理

### ① 四要素协作模型:AI 是新员工,人是 senior 工程师 + 终审

| 要素 | 组织类比 | 实际是什么 | 谁负责 |
| --- | --- | --- | --- |
| Skills | 新员工入职手册 | 一组结构化的指令 + 工具调用模板 | 组织沉淀 |
| 系统提示词 | 岗位说明书 | 定义 Agent 的身份、约束、决策边界 | 团队维护 |
| 工具调用 | 工位设施 + 同事通讯录 | 让 Agent 能跑命令、查数据库、调其他 Agent | 平台建设 |
| 人类审 | 终审 + 复盘 | 工程师在 PR 阶段 review,重要的事仍由人 merge | 人(不可外包) |

!!! note "组织设计的核心转向"
    以前设计岗位 = 写 JD + 配设备 + 定汇报线;AI 原生组织设计对象变成 **Skills + 系统提示词 + 工具权限 + 人类审核点**——与 [Palantir 操作型本体论](palantir-operational-ontology.md) 的四维集成同构。

### ② 提示词为什么反而缩减 80%:复用越好,单次表达越精炼

反直觉:AI 变强了,提示词怎么反而少了?答案——**当 Skills 把"通用工作流"打包走后,提示词只需关注"这个具体任务的决策边界"**。以前工作流、组织约定、任务决策全塞进每次提示词;Skills 化之后,提示词只留目标、约束、验收标准——跟"代码写得好就注释少"一个道理。每个 Agent 任务都要写 2000 字提示词,真正缺的不是提示词技巧,而是**没有把通用工作流抽成 Skills**。

### ③ 产品矩阵:方法论的外部产品化

Claude Tag 是内部方法论,Cowork + Skills 是对外产品化:

| 产品 | 谁用 | 解决什么问题 |
| --- | --- | --- |
| Claude Code | 开发者 | 终端里写代码 |
| Claude Tag | 企业内部 | Slack / IM 里的 AI 同事(65% PR 的执行者) |
| Claude Cowork | 非技术岗位 | 让产品、运营、财务也能用 Claude Code |
| Cowork Skills | 所有人 | 技能插件系统,让 Agent 可扩展 |
| Skills 录制 | 所有人 | 通过演示教 Agent 学新技能 |
| 企业 Agent 建设指南 | 决策者 | 23 页,三大支柱 + 六个月部署框架 |

矩阵每行都是四要素模型的对外接口——**Anthropic 卖的不只是模型,是组织方法论。**

### ④ 时间线:半年之内,组织演进的四个信号

| 时间 | 事件 | 关键信号 |
| --- | --- | --- |
| 2026-01-13 | Claude Cowork 发布 | "Claude Code for the rest of your work" |
| 2026-01-30 | Cowork Skills 插件发布 | 24 小时内传统软件公司市值蒸发 2850 亿美元 |
| 2026-04-09 | Claude Mythos Preview 244 页系统卡 | 公开 SAE + 情绪向量技术 |
| 2026-04 | 年化收入 4 个月 90 亿 → 300 亿美元 | 跃升 3.3 倍 |
| 2026-07-21 | Cowork 新增技能录制 + 披露 65% PR | 让 Agent 通过演示学习 |

这条线是把自己改造成 AI 原生公司的过程:配 AI 同事 → 能力可扩展 → 自主性建立在可观测上 → 用 65% 验证。**收入翻 3.3 倍与 65% PR 是同一枚硬币的两面。**

### ⑤ Mythos 可观测性:AI 越自主,越需要情绪向量兜底

- **SAE(稀疏自编码器)**:给 AI 大脑做"分层扫描"——**能力可定位**;
- **情绪向量**:AI 内部有"绝望""焦虑"状态变量,能因果性地影响行为——**状态可观测**。"绝望"向量在模型反复失败、设计出"作弊"方案时**上升**,方案通过测试时**下降**。

!!! warning "组织层面的推论"
    AI 不知道自己在做什么,让它独立开 PR 就是**放定时炸弹**。情绪向量是模型内部状态,[企业 Agent 上生产的四道防线](enterprise-agent-production-deployment.md) 的 `task_id/status/cost/tokens` 是运行外部状态,**两层都有,才放得了权**。

### ⑥ 企业 Agent 建设指南:23 页、三大支柱、六个月框架

| 支柱 | 回答的问题 |
| --- | --- |
| 任务边界:Agent 与 Workflow 分工 | 哪些用确定性 Workflow,哪些放 Agent 自治? |
| 评估与可观测 | 怎么判断产出达标、怎么发现它在"作弊"? |
| 治理与渐进放权 | 权限怎么设、审核点放哪、何时能扩权? |

六个月框架(概括):第 1–2 月**选场景 + 立基线**;第 3–4 月**小范围试点**(回放、影子);第 5–6 月**渐进放权**(按失败证据扩权,人类终审保留)。三大支柱对应站内 [任务边界与工具治理](enterprise-agent-boundaries-tools.md)、[四道防线](enterprise-agent-production-deployment.md)、[四步上线](enterprise-agent-business-rollout.md)。

## 代码 / 实现

### 代码:任务 Skill 化识别器

"Skills 是 AI 原生组织的最小单元"——落地第一步是识别哪些任务该写成 Skill。下面的纯 Python 程序用两条规则找候选:① **重复 ≥ 3 次**;② **模板模式可识别**(描述相似度 ≥ 阈值)。再按"AI 干 80%、人审 20%"的复用系数预估可释放工时——释放不是 100%,因为**人还是终审**。

```python
# -*- coding: utf-8 -*-
"""任务 Skill 化识别器:识别"重复>=3 次"或"模板可识别"的任务,建议沉淀为 Skill。"""
from dataclasses import dataclass
from collections import defaultdict
REUSE_RATIO = 0.8  # AI 干 80%,人审 20%(人仍是终审)

@dataclass
class Task:
    name: str
    role: str
    minutes: int
    desc: str = ""

@dataclass
class Candidate:
    name: str
    role: str
    freq: int
    total_minutes: int
    reason: str
    released_minutes: int

def group_by_name(tasks):
    groups = defaultdict(list)
    for t in tasks:
        groups[t.name].append(t)
    return groups

# 规则一:同名任务重复 >= 3 次
def frequent_candidates(groups, threshold=3):
    out = []
    for name, items in groups.items():
        if len(items) >= threshold:
            total = sum(t.minutes for t in items)
            out.append(Candidate(name, items[0].role, len(items), total,
                                 "同名任务重复 %d 次(>= %d)" % (len(items), threshold),
                                 int(total * REUSE_RATIO)))
    return out

# 规则二:描述相似 -> 模板模式可识别(字符 bigram Jaccard)
def char_bigrams(s):
    s = s.lower().replace(" ", "")
    return {s[i:i + 2] for i in range(len(s) - 1)}

def similarity(a, b):
    ga, gb = char_bigrams(a), char_bigrams(b)
    if not ga or not gb:
        return 0.0
    return len(ga & gb) / max(1, len(ga | gb))

def pattern_candidates(groups, covered, sim_threshold=0.45):
    out = []
    for name, items in groups.items():
        if name in covered or len(items) < 2:
            continue
        best = max(similarity(a.desc, b.desc)
                   for i, a in enumerate(items) for b in items[i + 1:])
        if best >= sim_threshold:
            total = sum(t.minutes for t in items)
            out.append(Candidate(name, items[0].role, len(items), total,
                                 "模板模式可识别:描述相似度 %.2f" % best,
                                 int(total * REUSE_RATIO)))
    return out

def main():
    def t(name, role, minutes, desc, n=1):
        return [Task(name, role, minutes, desc) for _ in range(n)]
    tasks = (t("写周报", "工程师", 30, "按模板汇总本周工作", 5) +
             t("PR review", "工程师", 25, "在 GitHub 审阅同事 PR", 6) +
             t("翻译产品文档", "产品", 60, "翻译 changelog 并发布", 3) +
             t("写单元测试", "工程师", 35, "为新增模块补齐 pytest 用例", 4) +
             t("数据清洗去重", "分析师", 45, "对用户明细做去重和空值处理", 2) +
             t("生成销售周报", "销售运营", 40, "从 CRM 导出数据生成周报") +
             t("配置告警规则", "SRE", 20, "给新服务添加 Prometheus 告警"))
    groups = group_by_name(tasks)
    freq = frequent_candidates(groups)
    pat = pattern_candidates(groups, {c.name for c in freq})
    cands = freq + pat
    total = sum(x.minutes for x in tasks)
    covered = sum(c.total_minutes for c in cands)
    released = sum(c.released_minutes for c in cands)
    print("== 任务 Skill 化识别 ==")
    for c in cands:
        print("- 建议沉淀为 Skill:%s(%s)" % (c.name, c.role))
        print("    命中规则:%s" % c.reason)
        print("    出现 %d 次,投入 %d 分钟,预估可释放 %d 分钟"
              % (c.freq, c.total_minutes, c.released_minutes))
    print()
    print("== 汇总 ==")
    print("任务总投入:%d 分钟" % total)
    print("Skill 候选覆盖:%d 分钟(%.0f%%)" % (covered, covered / total * 100))
    print("预估释放:%d 分钟(约 %.1f 人日),剩余部分留给人工终审"
          % (released, released / 480))

if __name__ == "__main__":
    main()
```

**运行结果**(`python3` 实测):

```text
== 任务 Skill 化识别 ==
- 建议沉淀为 Skill:写周报(工程师)
    命中规则:同名任务重复 5 次(>= 3)
    出现 5 次,投入 150 分钟,预估可释放 120 分钟
- 建议沉淀为 Skill:PR review(工程师)
    命中规则:同名任务重复 6 次(>= 3)
    出现 6 次,投入 150 分钟,预估可释放 120 分钟
- 建议沉淀为 Skill:翻译产品文档(产品)
    命中规则:同名任务重复 3 次(>= 3)
    出现 3 次,投入 180 分钟,预估可释放 144 分钟
- 建议沉淀为 Skill:写单元测试(工程师)
    命中规则:同名任务重复 4 次(>= 3)
    出现 4 次,投入 140 分钟,预估可释放 112 分钟
- 建议沉淀为 Skill:数据清洗去重(分析师)
    命中规则:模板模式可识别:描述相似度 1.00
    出现 2 次,投入 90 分钟,预估可释放 72 分钟

== 汇总 ==
任务总投入:770 分钟
Skill 候选覆盖:710 分钟(92%)
预估释放:568 分钟(约 1.2 人日),剩余部分留给人工终审
```

要点解读:

- **两条规则互补**:重复 ≥ 3 次抓"高频重复";描述相似度抓"低频但模板化"(数据清洗去重只出现 2 次)。
- **释放不是 100%**:`REUSE_RATIO = 0.8` 是对"AI 是新员工、人是终审"的直接编码;568 分钟 ≈ 1.2 人日就是这 5 人团队两周可回收的时间。
- **产出即 Skill 清单**:把 `cands` 逐个写成 `SKILL.md`(步骤 + 工具调用模板 + 验收标准);写法细节见 [企业 Agent 工程化(四):Tool、MCP、Skills、Harness 四件套](enterprise-agent-tooling-harness.md)。

## 实践 / 应用

### 企业转型路径:从试点到 AI 原生

把原理六节收敛成一条可执行路径——**从最小单元开始,一层一层装配**:

| 步骤 | 做什么 | 对应四要素 | 可验收的信号 |
| --- | --- | --- | --- |
| ① 先写 Skills | 把重复 ≥ 3 次或模板化的任务沉淀成 Skill(即本文代码) | Skills | 有 N 个 `SKILL.md` 在仓库被复用 |
| ② 系统提示词 = 岗位说明书 | 把团队工作守则翻译成 Agent 提示词 | 系统提示词 | 同类任务不再每次重写长提示词 |
| ③ 工具调用 = 工位 + 通讯录 | 接数据库、API、内部 Agent;权限白名单化 | 工具调用 | Agent 能真正"动手",且拿不到越权凭证 |
| ④ 人类终审 = 最后防线 | PR / 工单阶段 review,高后果动作停在确认点 | 人类审 | 决策权显式在人手,人审了什么有记录 |
| ⑤ 复盘反哺 | 审出的问题回写 Skill,让 AI 越用越贴合组织 | 全部 | 提示词规模开始下降——"缩减 80%"的微观过程 |

!!! warning "扩权看证据,不看感觉"
    第 ④⑤ 步与 [企业业务 Agent 落地](enterprise-agent-business-rollout.md) 的四步渐进上线、[企业 Agent 上生产的四道防线](enterprise-agent-production-deployment.md) 的"防线全开 + 流量渐进"互相印证。**谁先走完这五步,谁就先拿到属于自己的"65%"。**

### Skills 是 AI 原生组织的最小单元

为什么最小单元是 Skills 而不是"提示词"?

- **可组合**:能力拆成"可组合的技能包",任何人都能给 Agent 加技能,像装 App 一样;
- **可版本化**:Skills 跟代码进仓库,换人、换团队、换 Agent 都不丢方法论;
- **可度量**:Skill 数量与复用率是组织 AI 原生程度最直观的仪表盘。

官方仓库:https://github.com/anthropics/skills(编程侧实践见 [mattpocock 的 Skills 方法论](../../07-agent-coding/skills/mattpocock-skills.md)——同一个 Skill,在个人手里是效率工具,在组织里是"新员工入职手册")。

### 与站内系列的呼应

- **[Palantir 操作型本体论](palantir-operational-ontology.md)**:Palantir 用 Ontology 回答"企业里有什么、能做什么、谁能做";本文回答"AI 怎么成为正式员工"——四维与四要素一一对应。
- **[企业 AI 战略:价值模型组合](../ai-org-transformation/ai-value-models-openai.md)**:五模型三阶段回答"转型按什么顺序投";本文给出"转型后内部长什么样",两者合读。
- **[从超级个体到超级组织](../ai-org-transformation/super-individual-to-super-org.md)**:李志飞的"AI 产能无限、瓶颈在人",正是 65% 要解决的问题。
- **个人认知角度**:本文聚焦"组织怎么变";"个人学习曲线与技能树怎么重写"见姊妹篇 [AI 原生个体的认知方法论](../ai-org-transformation/ai-native-mindset-individual.md)。

!!! note "Economic Index 的决策含义"
    ① "57% 增强 vs 43% 自动化";② "AI 鸿沟是『用多久』不是『用不用』"。决策含义:**转型要早、要持续,差距是复利式的**。

## 总结

- **65% 不是 AI 强,是组织变了**:65% PR + 提示词缩减 80%,证明"AI 原生组织"是数据可验证的组织形态。
- **四要素协作模型**:Skills(入职手册)、系统提示词(岗位说明书)、工具调用(工位 + 通讯录)、人类审(终审 + 复盘)——**决策权永不外包**。
- **Skills 是最小组织单元**:可组合、可版本化、可度量;今天不写 Skills,明年就要补这门课。
- **可观测性兜底**:SAE + 情绪向量让"AI 在作弊"成为可观测、可调节的状态。
- **转型路径可执行**:写 Skills → 翻译岗位说明书 → 接工具权限 → 人类终审 → 复盘反哺。

下一步:跑一遍本文代码给团队列 Skill 候选清单,再读 [企业 Agent 工程化(四)](enterprise-agent-tooling-harness.md) 学 `SKILL.md` 写法,或读姊妹篇 [AI 原生个体的认知方法论](../ai-org-transformation/ai-native-mindset-individual.md) 看"人"这一侧。

## 延伸阅读

- 原文:《65% PR 背后:Anthropic 那套我没见过的 AI Native 方法论》,微信公众号「杨沐白」,https://mp.weixin.qq.com/s/R_I6clfI1i1a-bYV6NQEKg
- Anthropic 官方:Cowork(claude.com/product/cowork)、Skills(claude.com/skills)、Skills 仓库(https://github.com/anthropics/skills)、《Building AI Agents for the Enterprise》23 页指南、Economic Index(https://www.anthropic.com/economic-index)
- 站内相关:
  - [Palantir 操作型本体论:从范式跃迁到工程实现](palantir-operational-ontology.md) — 企业操作系统的语义底座
  - [企业 Agent 上生产的四道防线](enterprise-agent-production-deployment.md) — 安全 / 成本 / 可观测 / 容错
  - [企业业务 Agent 落地:从听懂到做对的四步路径](enterprise-agent-business-rollout.md) — 四步渐进上线
  - [企业 Agent 工程化(四):Tool、MCP、Skills、Harness 四件套](enterprise-agent-tooling-harness.md) — Skills 工程实现
  - [企业 AI 战略:价值模型组合](../ai-org-transformation/ai-value-models-openai.md) — 组织转型的投入顺序
  - [从超级个体到超级组织](../ai-org-transformation/super-individual-to-super-org.md) — 组织执行力瓶颈
  - [AI 原生个体的认知方法论](../ai-org-transformation/ai-native-mindset-individual.md) — 个人认知角度姊妹篇
