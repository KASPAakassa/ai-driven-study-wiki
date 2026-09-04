# 企业 AI 战略:把试点当转型——从"用例列表"到"价值模型组合"

> **一句话摘要**:大多数企业做 AI 是"横幅广告式试点"——每个试点都有成功故事,企业却没有变化。OpenAI 报告指出,领先企业早已把 AI 从"用例列表"升级为"价值模型组合":五种模型各有经济逻辑、回报周期与治理要求,且互为递进。本文给出五模型、三阶段框架与可运行的 Python 评估器。
>
> **来源**:微信公众号《企业 AI 战略的最大误区:把试点当转型》(原文存档 `docs/inbox/enterprise-agent-engineering-src-b10.md`);内容基于 **OpenAI 企业 AI 价值模型报告** 的解读。

## 概念

**核心定义**:企业的 AI 战略有两种形态——

- **用例列表 / 试点列表(banner ad)**:各部门各自试点 AI 场景,每个试点都有成功故事,但成果**不回流、不沉淀、不改变既有流程**——就像互联网时代的横幅广告:"你做了,但错过了真正的革命"。
- **价值模型组合(value model portfolio)**:把 AI 视为一组**互相衔接的价值模型**,每个模型有自己的经济逻辑、回报周期、治理要求,并且**每个模型都会让下一个模型更容易规模化**。

!!! tip "一句话区分"
    试点列表问"AI 能帮我做什么";价值模型组合问"**先建哪个模型?它打什么基础?下一步解锁什么?**"。

## 原理

### 五个价值模型的三件套

OpenAI 给每个模型配了"衡量 / 失败模式 / 领导层行动"三件套——最值得抄走的落地工具:

| 模型 | 核心价值 / 回报周期 | 衡量指标 | 常见失败模式 | 领导层行动 |
| --- | --- | --- | --- | --- |
| 员工赋能 | 全员流畅度 / 最快 | 重复使用率、可复用工作流、跨职能赋能 | **双轨制员工**:超级用户跑前面,其他人停滞 | 建冠军网络 + 入门工作流(绩效/合同/采购审批) |
| AI 原生分发 | 对话中转化 / 中等 | 合格意图数、转化质量、信任信号 | 当传统漏斗,追求数量牺牲信任 | 选一个触点,先定义"转化质量" |
| 专家能力增强 | 压缩专家瓶颈 / 中等 | 周期缩短、质量提升、范围扩展 | 当演示,没嵌入真实工作流 | 选一个专家瓶颈,聚焦"签批决策者" |
| 系统与依赖管理 | 安全升级互联系统 / 较长 | 安全变更时间、审计就绪度、下游一致性 | 治理不成熟就扩大生成,制造技术债 | 从高依赖领域开始,先定依赖图和审批路径 |
| 流程重构 | 端到端自动化 / 最长 | 端到端周期、异常率、合规、创新产出 | 权限/控制/问责不成熟就自动化端到端 | 选一个工作流做"就绪度评估"再上 |

!!! warning "最容易踩的坑"
    五模型的失败模式有个共同特征:**前置不成熟,后置硬上**。价值模型组合的本质是**顺序**,不是清单。

### 递进逻辑与三阶段路径

每个模型解锁下一个的机制:员工赋能让全员会说"AI 能做什么";真实使用沉淀出治理规则;治理兜底后 Agent 才敢碰生产系统;集成暴露系统间依赖,才有依赖图和审批路径;依赖清晰 + 审批明确,自主 Agent 才能安全运行。

三阶段路径把"从更好到不同"切成三步,阶段切换靠**条件**而非时间:

| 阶段 | 重点 | 典型动作 | 衡量 |
| --- | --- | --- | --- |
| **一:建立流畅度和信任** | 全员 + 治理基础 | 角色化工作流 + 冠军网络;定清"允许/审核/日志/谁负责" | 重复使用率、可复用工作流 |
| **二:捕获价值、提高天花板** | 高价值场景 + 再投资 | 选 2-3 个场景(分发/专家瓶颈/工作流);胜利再投资到数据/身份/集成/可观测性 | 转化质量、周期缩短、风险降低 |
| **三:自信规模化、重塑业务** | 端到端 + 运营模型 | 权限/审计/异常成熟后进入端到端工作流,重设计运营模型 | 端到端周期、异常率、合规、创新产出 |

## 代码 / 实现

**纯 Python、零第三方依赖**的"价值模型组合评估器":输入五个模型成熟度(0-5),输出当前阶段与推荐路径。

```python
"""value_model_portfolio.py — 企业 AI 价值模型组合评估器(纯 Python)"""

MODELS = [
    {"key": "empowerment", "label": "员工赋能", "payoff": "最快(季度级)", "needs": []},
    {"key": "distribution", "label": "AI 原生分发", "payoff": "中等(半年~1年)", "needs": ["empowerment"]},
    {"key": "expertise", "label": "专家能力增强", "payoff": "中等(半年~1年)", "needs": ["empowerment"]},
    {"key": "systems", "label": "系统与依赖管理", "payoff": "较长(1~2年)", "needs": ["distribution", "expertise"]},
    {"key": "reengineering", "label": "流程重构", "payoff": "最长(2年+)", "needs": ["systems"]},
]


def stage(scores):
    """三阶段判定:0=试点列表 1=建立流畅度 2=捕获价值 3=自信规模化"""
    def ok(k, t=3):
        return scores.get(k, 0) >= t

    if ok("empowerment") and ok("distribution") and ok("expertise") and ok("systems") and ok("reengineering"):
        return 3
    if ok("empowerment") and (ok("distribution") or ok("expertise")):
        return 2
    if ok("empowerment", 2):
        return 1
    return 0


def recommend(scores):
    """推荐路径:按递进顺序,找所有'前置已成熟、自身未成熟'的模型"""
    path = []
    for m in MODELS:
        if scores.get(m["key"], 0) < 3:
            if all(scores.get(n, 0) >= 3 for n in m["needs"]):
                path.append(m)
            else:
                break
    return path


STAGE_NAMES = ["试点列表(还没转型)", "阶段一:建立流畅度和信任",
               "阶段二:捕获价值、提高天花板", "阶段三:自信规模化、重塑业务"]


def report(scores, company):
    lines = ["==" + company + "=="]
    lines.append("  成熟度(0-5): " + " | ".join(f"{m['label']}={scores[m['key']]}" for m in MODELS))
    lines.append(f"  当前阶段: {STAGE_NAMES[stage(scores)]}")
    rec = recommend(scores)
    if rec:
        lines.append("  推荐路径: " + "、".join(f"{m['label']}(回报周期:{m['payoff']})" for m in rec))
    else:
        lines.append("  全部模型已成熟 → 进入端到端流程重构与商业模式重塑")
    return "\n".join(lines)


if __name__ == "__main__":
    company_a = {"empowerment": 3, "distribution": 2, "expertise": 1, "systems": 0, "reengineering": 0}
    company_b = {"empowerment": 5, "distribution": 4, "expertise": 3, "systems": 2, "reengineering": 1}
    company_c = {"empowerment": 5, "distribution": 4, "expertise": 4, "systems": 4, "reengineering": 3}
    for scores, name in [(company_a, "A 公司(试点列表)"),
                         (company_b, "B 公司(价值捕获中)"),
                         (company_c, "C 公司(自信规模化)")]:
        print(report(scores, name))
        print()
```

**逐段解释**:

- `MODELS` 的 `needs` 字段固化递进依赖(`distribution`/`expertise` → `empowerment`,`systems` → 前两者,`reengineering` → `systems`);
- `stage()` 把三阶段翻译成可判定条件:员工赋能 ≥2 离开展、分发/专家任一 ≥3 进阶段二、五模型全 ≥3 才算自信规模化;
- `recommend()` 返回"前置已成熟、自身未成熟"的模型,允许分发与专家**并行**。

## 实践 / 应用

### 从哪个模型开始、打什么基础、解锁什么下一步

| 起点模型 | 要打的基础 | 解锁的下一步 |
| --- | --- | --- |
| 员工赋能 | 入门工作流 + 冠军网络 + 使用日志 | 治理规则 → 分发与专家场景 |
| AI 原生分发 | 单触点 + 转化质量定义 + 信任信号 | 用真实转化数据争取下一轮投资 |
| 专家能力增强 | 一个专家瓶颈 + 真实工作流嵌入 | 把"签批决策者"变成 AI 高频用户 |
| 系统与依赖管理 | 依赖图 + 审批路径 + 审计就绪 | 端到端流程自动化的资格 |
| 流程重构 | 权限/控制/问责就绪度评估 | 运营模型与商业模式的重新设计 |

### 每个模型落地时的关键问题

- **员工赋能**:入门工作流覆盖了多少比例的员工?冠军网络有没有被"双轨制"架空?
- **AI 原生分发**:定义清楚"转化质量"了吗?指标会不会诱导我们牺牲信任?
- **专家能力增强**:瓶颈是不是"最终签批的决策者"?还是又做成了演示?
- **系统与依赖管理**:依赖图和审批路径先于生成规模了吗?
- **流程重构**:就绪度评估(权限/审计/异常)真的达标了吗?

!!! warning "与「超级个体到超级组织」的呼应"
    [从超级个体到超级组织](super-individual-to-super-org.md) 验证了同一逻辑的**反面教材风险**:超级个体跑在前面 = OpenAI 说的"**双轨制员工**"极端形态,价值模型组合要求把产能**铺到全员**;
    "任务在哪里,沟通就在哪里"(CodeBanana)正是 **AI 原生分发 + 系统依赖管理**在组织内部的落地;
    李志飞自评"匹配度 6-7 分"——正是"从**更好**到**不同**"的那道坎:前四个模型产出"更好的现在",**流程重构**才通向"不同的未来"。

## 总结

- **试点的本质是横幅广告**:用例列表做一百个,企业也不会因此变得不同;战略单位应从"用例"升级为"**价值模型组合**";
- **五模型递进而非并列**:流畅度 → 治理 → 集成 → 依赖管理 → 代理安全运行;前置不成熟就追后置,是失败的结构性根源;
- **三阶段路径**:建立流畅度和信任 → 捕获价值、提高天花板 → 自信规模化、重塑业务;切换靠**条件**而非时间;
- **终极顺序**:AI 先改进任务,再重新设计流程,再改变控制层与运营模式,**最终改变商业模式**——零售不是靠"让门店稍微高效一点"变成电商,而是在领导者构建全新价值主张、完全绕过门店、把营销与物流整合成单一用户中心动作时才完成范式转移。AI 会遵循同样的模式。

**下一步学什么**:关心工程落地读 [AI Friendly 架构](../ai-friendly-architecture/ai-friendly-backend.md) 与 [Agent 的权限/集成/可观测性](../ontology-agent-adoption/enterprise-agent-permission-integration-observability.md);关心组织转型读 [从超级个体到超级组织](super-individual-to-super-org.md)。

## 延伸阅读

- 站内:[从超级个体到超级组织](super-individual-to-super-org.md)、[AI 组织转型子主题](index.md)、[FDE 崛起](../fde-methodology/fde-rising.md)、[Agent 的权限/集成/可观测性](../ontology-agent-adoption/enterprise-agent-permission-integration-observability.md)
- 外部:微信公众号《企业 AI 战略的最大误区:把试点当转型》;OpenAI 企业 AI 价值模型报告(《The AI value models reshaping enterprise》等系列解读)
