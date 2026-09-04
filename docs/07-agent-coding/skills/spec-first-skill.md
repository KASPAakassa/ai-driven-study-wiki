# Spec-First:把 AI Coding 判断装进可重复工程闭环

> **一句话摘要**:Spec-First 是一套 AI Coding Harness——把不稳定的 AI 推理放进可重复、可验证的工程闭环。它由一组 skill(spec-prd / spec-brainstorm / spec-plan / spec-write-tasks / spec-code-review)组成,核心机制是需求澄清、scope 锁定、**证据四等级分级**与非法组合拦截、经验沉淀(`docs/solutions/`)。本文收藏并拆解这套 skill 体系。
>
> **来源**:微信公众号「leokuang」《Spec-First:我用 16 个思维模型,重新想清了 AI 工程怎么做》,https://mp.weixin.qq.com/s/lqChZsjZAnqtSpAQd-XVhQ;GitHub:http://github.com/sunrain520/spec-first;官网:http://spec-first.cn/;原始资料存档于 `docs/inbox/spec-first-source.md`

## 概念:Spec-First 是什么

!!! tip "一句话定位"
    **Spec-First = 一层 AI Coding Harness:把不稳定的 AI 推理,放进可重复、可验证的工程闭环。**

它不只是"写 prompt 的技巧",而是一套**决策操作系统**——把复杂工程判断拆成若干可复用的机制:先澄清需求(意图显式化)、再锁计划边界(scope + non-goals)、然后切片执行(只允许重排顺序、不允许改 scope)、最后证据分级验证与经验沉淀。

## 原理:核心机制

### 1. 需求澄清与 scope 锁定(掐断"蝴蝶效应"传播路径)

- `spec-prd` / `spec-brainstorm`:需求澄清,把意图显式化——"优化一下登录"必须被逼成"只加错误提示、不动认证逻辑";
- `spec-plan`:写清 scope 与 non-goals,锁定边界;
- `spec-write-tasks`:任务切片,只允许重排执行顺序,**不能改 scope**;
- 原则:越往后纠偏成本越高——需求阶段改一句话,review 阶段就是整段回滚。

### 2. 证据四等级分级(防幻觉伪装成事实)

AI 的每个结论都要贴等级标签,而不是当成确定事实:

| 等级 | 含义 | 示例 |
| --- | --- | --- |
| **primary** | 已确认:由源码、测试、schema 或命令结果支撑 | 跑过引用查找后说"没有调用方" |
| **session-local** | 只在本次会话成立,未被持久确认 | 本次会话里临时推断 |
| **advisory** | 只是线索,如 provider 给的一个 pointer | "看起来像是这个问题" |
| **stale** | 已过期,不能再当真 | 上周的文档、过期镜像 |

!!! warning "非法组合表(最堵 AI 幻觉的机制)"
    能力 `unavailable` 却声称证据 `primary` 是**不允许的**——堵的正是"工具没用上,却假装拿到了确认"这种最常见的 AI 幻觉。例如:Agent 说"这个函数没有别的调用方,可以安全删除",必须先问:这是 primary(真跑了引用查找)还是 advisory(扫了一眼觉得没有)?

### 3. 共享上下文产权边界(防公地悲剧)

多人、多 agent 共用上下文/memory/skill 池,不加约束必然被过度消耗。Spec-First 给上下文划产权:

- 普通任务**默认不读**易过期或带噪声的材料(如 `.spec-first/audits/**`、`.claude/**`、`.codex/**`);
- 任务引用必须指向**最小有用片段**(`context_refs`),而不是整库投喂;
- 警惕"影子真相":从 source 生成出来的运行时副本(如 `.claude/` 里的过期镜像)会被当成真相去读——**别让公共池里的脏数据污染每一次判断**。

### 4. 经验沉淀(让复利生效)

一次 bugfix、一次 review failure 写进 `docs/solutions/`,成为下一次任务的上下文资产(`spec-plan`、`spec-code-review` 通过 `context_refs` 按需召回)。**聊天记录里的经验等于没有**——不可搜索、不可被 workflow 引用,下周就蒸发。

## 代码 / 实现:证据分级校验器(纯 Python)

把"证据四等级 + 非法组合拦截"落成可运行校验器:

```python
VALID = {"primary", "session-local", "advisory", "stale"}

def check_evidence(claim: dict) -> dict:
    """claim: {"capability": "used"|"unavailable", "level": str, "text": str}
    非法组合:能力不可用却声称 primary → 拦截(最常见 AI 幻觉)"""
    level, cap = claim["level"], claim["capability"]
    if level not in VALID:
        return {"verdict": "invalid", "reason": f"未知证据等级 {level}"}
    if level == "primary" and cap == "unavailable":
        return {"verdict": "blocked", "reason": "能力不可用却声称 primary(非法组合,疑似幻觉)"}
    return {"verdict": "ok", "action": "按等级降权使用"}

# 演练
cases = [
    {"capability": "used",       "level": "primary",        "text": "跑过 grep,确认无调用方"},
    {"capability": "unavailable","level": "primary",        "text": "扫了一眼,应该没调用方"},
    {"capability": "used",       "level": "advisory",       "text": "provider 提示可能相关"},
    {"capability": "unavailable","level": "stale",          "text": "上周文档里的结论"},
]
for c in cases:
    r = check_evidence(c)
    print(f"  [{r['verdict']:7}] {c['text']} → {r['reason'] if 'reason' in r else '通过'}")
```

## 实践 / 应用:怎么装、怎么用

- **安装**:GitHub http://github.com/sunrain520/spec-first(文末"阅读原文"直达);官网 http://spec-first.cn/;
- **最小上手**:先只跑 `spec-prd` 做需求澄清 + `spec-code-review` 带证据分级 review,其余 skill 按需加入;
- **与 16 思维模型的关系**:本套 skill 的硬约束几乎一一对应四层决策栈(详见站内 [Spec-First 决策栈:16 个思维模型](../experience/spec-first-decision-stack.md))——模型管"脑子里怎么判断",skill 管"项目里怎么落地";
- **证据纪律**:对 AI 的每个关键结论贴等级标签;落地前必须有源码/测试级证据回扣(地图不是疆域)。

## 总结

- **定位**:AI Coding Harness,把 AI 推理放进可重复、可验证的闭环;
- **四机制**:需求澄清与 scope 锁定、证据四等级 + 非法组合拦截、上下文产权边界、经验沉淀;
- **一条纪律**:AI 说"可以删/没问题"时,先问证据等级——primary 还是 advisory,决定你该承担多少风险;
- **价值**:把"AI 该不该这么改"从直觉变成可逐层追问的链路。

## 延伸阅读

- GitHub:http://github.com/sunrain520/spec-first;官网:http://spec-first.cn/;原文:https://mp.weixin.qq.com/s/lqChZsjZAnqtSpAQd-XVhQ
- 站内:[Spec-First 决策栈(16 思维模型)](../experience/spec-first-decision-stack.md)(判断力方法论)、[Eval Engineering Skill](eval-engineering-skill.md)(评估驱动)、[handoff Skill](handoff-skill.md)(交接)、[Skill 收藏](index.md)、[得物 Spec-Driven 五道关口](../../04-practice/ai-native-order-system-spec-driven.md)(同为 Spec 驱动方法论)
