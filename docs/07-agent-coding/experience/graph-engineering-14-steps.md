# Graph Engineering:用 Claude 构建多 Agent 工作流的 14 步路线图

> **一句话摘要**:大多数人搭多步 Agent,最后都做成了直线——步骤一、二、三,一半的步骤根本不需要等待。Graph Engineering 把工作流的形状从"单文件直线"变成"图":在独立处扇出(fan-out)、在需要信任处设卡验证、在不需要判断力处分层调配模型。本文精讲 14 步路线图,并给出可运行的 fan-out/收敛循环代码。
>
> **来源**:微信公众号《用 Claude 做 Graph Engineering:从 0 到 graph 架构师的 14 步路线图》(转载自 X,作者 0xCodez),https://mp.weixin.qq.com/s/MhcPo5RMdg-alL0bZplinQ;原文 https://x.com/0xCodez/status/2079165300625330317;原始资料存档于 `docs/inbox/graph-engineering-source.md`

## 概念:工作本身的形状是一张图

!!! tip "没人明说的思维转变"
    **Prompt 是一句话。Loop 是一个环。Harness 是 Agent 立足的地板。但工作本身的形状——什么先运行、什么可以同时运行、什么必须等待其他一切——那个形状是一张图。Node 负责思考,Edge 负责传递结果。**

Claude Code 已推出直接构建这些图的工具:**Dynamic Workflows(动态工作流)**——Claude 写一段纯 JavaScript 编排脚本,生成一支协同的子 Agent 集群去执行;**协调本身不消耗任何模型 token,因为它是代码,不是对话**。

## 原理:14 步路线图

### 01 Node 是任务,Edge 是流动的东西

一张 graph 只有两样东西:Node 是工作单元(有边界的 job,输入进、输出出);Edge 是依赖关系("这个 node 的输出喂给那个 node 的输入")。

常见错误是把"然后(and then)"当作 edge——"总结文件,然后告诉我天气"之间没有 edge(天气不消费摘要),那只是两个互不连接的 node 被线性脚本硬串在一起。

!!! tip "对每个「然后」发问"
    下一步会不会读上一步的 output?不会 → 没有 edge,等待就是浪费。**把它画成方框和箭头**:方框是一次 agent() 调用,箭头是从一次调用的返回值传入另一次调用 prompt 的变量。画不出箭头 = 两个方框独立——独立性就是你要利用的核心。

### 02 你的线性脚本,是一张退化的 graph

「先 A 再 B 再 C 再 D」= 一条没有分支的单链:每个 node 恰好一条 edge 进、一条 edge 出。能跑,但慢且脆弱——链没有冗余,C 卡住,D 永远不会发生。

第一项技能:对每一条箭头问 01 的问题,剪掉不携带数据的箭头,链就会塌成更宽的结构:几个可以同时跑的独立 node,共同喂给一个需要它们全部结果的 node。

### 03 给每个 node 一份 contract

**你无法推理的 node,就是你无法并行化的 node**。契约(contract)三要素:有边界的输入(显式传入,绝不假设来自共享上下文)、确定的输出结构(最好经校验)、只做一件事。

在 workflow 里 contract 由 **JSON schema** 强制执行——校验发生在工具调用层,不匹配时 Claude 重试,而不是甩给你一段自由文本让你自己解析。

### 04 把 edge 当作 data contract

Edge 不只是"B 在 A 之后",而是"关于什么会跨过去的承诺":A 产出这个 shape,B 被设计成消费这个 shape。用数据而非顺序命名 edge 后:你能一眼看出 edge 是否真实;只要 shape 成立,就能替换任一端的 node 而不弄坏整张图。

!!! warning "别为接线付租金"
    诱惑在于派生一个 agent 来"合并结果"。如果合并只是扁平化加去重,那就是 `results.flatMap(...)` 加一个 Set——确定性、瞬时、**零 token**。**把 agent 留给需要判断力的事,而不是管道工程;一张每条边都是 agent 的图,是在为自己的接线付租金。**

### 05 用 parallel() 做 Fan-out(扇出)

N 个独立节点(检查 N 个信息源/审查 N 个文件/审计 N 条路由)不该串成链,应该 Fan-out 并行运行。两个细节:

1. **parallel() 是一个屏障(barrier)**:等待所有 thunk 完成才返回,下一阶段看到完整结果集合;
2. **抛异常的 thunk 被解析为 null** 而非让整批失败——一个不稳定的 agent 不会拖垮整次运行;务必对结果 `.filter(Boolean)`。

并发度以核心数为上限,超出排队执行;传入上百个 thunk 最终都会完成。**Fan-out 存在于 Claude 编写的代码里,不在模型对话里**——Claude 自己的上下文不需要同时容纳九个信息源,每个子 agent 携带自己的上下文,只有最终答案返回。这就是能扩展到数百个子 agent 而不淹没会话的原因。

### 06 在 barrier 处 Fan-in(收拢)

Fan-out 只有在有东西收拢时才有用。Fan-in 是 edge 汇合的 node——一次性看到所有上游结果,做需要"完整集合"的事:跨 source 去重、按 impact 排序、总数为空就 early-exit。

!!! note "parallel vs pipeline 的第一条准则"
    只有当某阶段真的需要把先前所有结果凑在一起时,才用 barrier。只是 flatten 一个 list?那是 edge,内联处理。**如果写出 parallel → transform → parallel 而中间 transform 不存在跨条目依赖,你本该用 pipeline,完全跳过这道屏障。**

### 07 菱形拓扑:拆分 → 处理 → 归并

把 fan-out 和 fan-in 合在一起 = 每一张严肃 agent 图的主力拓扑:**Diamond(菱形)**——一个节点拆分任务、多个节点并行处理、一个节点归并结果。市场扫描、依赖审计、代码审查、研究报告都是这个形状,换掉信息源和 prompt,骨架不变。

规范形式:**fan-out(取广度)→ reduce(纯代码压缩)→ synthesize(最后一个 agent 综合撰写)**。看懂菱形后,问题从"如何让我的 agent 做更多步骤"变成"哪里拆分、哪里合并"——这才是能扩展规模的问题。

### 08 用条件语句在运行时路由 edge

不是所有 graph 都固定:路由(router)节点检查一个结果,决定哪条下游路径被触发(工单分类→分支到处理器;diff 大小→快速审查或完整审计)。

**确定性成为优势**:路由器的判断可以由 Claude 驱动(子 agent 分类),但路由本身是 Claude 写下的代码——对同一个分类结果,它每次都相同方式运行。**你在 node 上获得 Claude 的判断力,在 edge 上获得脚本的可靠性**,不会出现"Claude 突然决定跳过审计"的意外。

### 09 在 edge 放置验证器(verifier)

Graph 真正的杠杆不是更多 agent,而是**围绕它们构建的、产生信心的结构**。验证器节点坐在结果流向下游之前的边上,唯一工作是**尝试推翻这个发现**。三种模式:

| 模式 | 机制 |
| --- | --- |
| **对抗式验证** | 对每个发现生成 N 个独立"怀疑者",专门被提示去反驳;多数怀疑者未能推翻才保留 |
| **多视角验证** | 每个验证者不同视角(正确性/安全性/能否复现)——多样性捕捉 N 个相同检查抓不住的失败模式 |
| **评审团(Judge panel)** | 不同角度生成 N 次尝试,并行评委打分,综合获胜者并嫁接其他方案的最好部分 |

### 10 隔离节点,避免一次失败污染整张 graph

链里失败级联传播;graph 里失败应被限制在节点内。`parallel()` 内异常 → null + `.filter(Boolean)` 就是 containment(隔离防线);设计 fan-in 节点要能容忍缺失输入。

更隐蔽的失败:多 agent 并行写文件互相踩脚 → 用 **worktree 隔离**(每个 agent 在自己的 git worktree 运行、沙盒内完成、干净合并回去)。只在节点确实需要并行写入时才用它——它是安全带的角色,不是每次都要缴的税。

### 11 添加循环——但要确保它能收敛

有些任务规模做起来才知道(未知规模的发现、bug 排查牵出新 bug),需要一个受控的循环。危险:不收敛 = 无限循环烧光 Token。

可收敛的模式:**loop-until-dry(循环直到枯竭)**——持续生成"探测者"节点,直到连续 K 轮什么新东西都没发现才停。

!!! warning "几乎所有人第一次都会犯的错误:拿什么去重"
    要针对**所有见过的(seen)**去重,而不是只针对已确认的(confirmed)。否则被否决的发现会在每一轮重新出现,循环永远跑不干——你造了一台不断付费重新发现同样死胡同的机器。

### 12 在各节点之间分层调配模型

不是每个节点都需要最好的模型:有界且重复的(提取字段、工单分类)跑便宜模型;真正承载判断的(综合报告、裁定发现)用贵模型。Claude 派生的子 agent 默认继承会话模型,但单次 `agent()` 的 `model` 选项可路由到别的模型。大型运行前先检查 `/model`。**不改 graph 形状,就能把吃 token 的 graph 从昂贵变成划算。**

### 13 拓扑结构决定你的成本与延迟

Graph 形状是影响实际运行时间的最大杠杆:`parallel()` 的屏障让所有任务等待最慢节点;`pipeline()` 让每个条目独立流经所有阶段、快的提前完成。

!!! tip "默认使用 pipeline()"
    只有当某阶段确实需要一次性拿到所有先前结果时才用屏障(跨集合去重/根据总数 early-exit/需要与其他发现逐一比对的 prompt)。"代码更干净""各阶段感觉是分开的"都不是理由——**separate(分开)≠ synchronized(同步)**,屏障造成的延迟是真实的、可测量的、被浪费的时间。

### 14 让 Claude 自己画 graph——self-routing

对无法提前规划的活,别手动画图。借助 dynamic workflows:你只描述目标,Claude 自己写出编排脚本——拆任务、选 fan-out 方式、生成协同子 agent 集群、综合结果。三种入口:

1. prompt 里说"workflow"这个词 → Claude 为该任务写工作流;
2. 运行已保存的工作流 → `/deep-research` 就是一张真实的图(确定范围 → 并行搜索 → 抓取 → 对抗式验证 → 综合);
3. 开启 ultracode → 为每项重大任务规划工作流;运行效果好按 `s` 保存进 `.claude/workflows/`(版本控制、可按名重跑)。

## 代码 / 实现:fan-out + 去重 + 收敛循环(纯 Python 演示)

把第 05/06/11 步的核心机制(parallel 屏障、对 seen 去重、loop-until-dry)落成可运行代码:

```python
# —— 模拟 graph:fan-out → 去重 → 验证 → loop-until-dry ——
def fan_out(find_funcs):
    """parallel() 模拟:并行执行;异常/无结果的返回 None(屏障后 filter)"""
    return [f() for f in find_funcs]

def loop_until_dry(find_funcs, key, verify, K=2, max_rounds=10):
    """发现器并行找 bug → 对 SEEN 去重(含同轮重复)→ 验证存活者 → 连续 K 轮无新发现停止"""
    seen, confirmed, dry = set(), [], 0
    for _ in range(max_rounds):
        found = [x for x in fan_out(find_funcs) if x is not None]
        # 对 seen 去重:同一轮内 key 相同的也只保留一个
        fresh = list({key(b): b for b in found if key(b) not in seen}.values())
        if not fresh:
            dry += 1
            if dry >= K:
                break
            continue
        dry = 0
        for b in fresh:
            seen.add(key(b))          # 对 seen 去重,而非 confirmed
            if verify(b):
                confirmed.append(b)
    return confirmed

# —— 场景:三个"发现器",会产生重复与假阳性 ——
bug_1 = {"desc": "空指针在 login", "real": True}
bug_2 = {"desc": "空指针在 login", "real": True}    # 与 bug_1 重复(key 相同)
bug_3 = {"desc": "XSS in search", "real": True}
bug_4 = {"desc": "内存泄漏", "real": False}          # 假阳性,验证不过

finders = [
    lambda: bug_1, lambda: bug_2, lambda: bug_3,  # 第一轮发现 3 个
    lambda: None,                                 # 模拟一个失败的 agent
    lambda: bug_4, lambda: None, lambda: None,    # 第二轮:假阳性 + 两个空
]
verify = lambda b: b["real"]
confirmed = loop_until_dry(finders, key=lambda b: b["desc"], verify=verify)
print("确认的 bug:", [b["desc"] for b in confirmed])
```

## 实践 / 应用:本周就能和 Claude 一起构建的六张图

| 图 | 形状 | 关键机制 |
| --- | --- | --- |
| **全路由安全扫描** | 每路由文件一个 agent → 验证器通道 | 任何单一上下文都无法承载的广度 |
| **/deep-research 报告** | 分解角度 → 并行搜索 → 去重 → 三票怀疑者对抗验证 → 撰写 | Claude Code 随附的真实 graph |
| **逐文件移植模块** | fan-out 到各文件 → 测试套件做 gate → 失败循环回炉 | 对抗式评审拦下单次遍历带 bug 上线 |
| **diff 对抗式评审** | 按 diff 大小路由:小=快评,大=全面并行审计 | 评审者各持视角(正确性/安全/性能)+ 评审团 |
| **定时生态扫描** | 并行检查多源 → barrier 处按影响排序 → 摘要 | 保存到 `.claude/workflows/`,按名启动 |
| **未知规模探索** | 并行发现者 → 对 seen 去重 → 验证存活者 → 连续两轮空手停止 | loop-until-dry 收敛 |

**使用要点**(贯穿 14 步):先画方框箭头再写代码;默认 pipeline、只有真需要完整集合才 barrier;edge 用代码不用 agent;验证器放在高信任需求的边上;重复节点降模型档;多 agent 并行写文件用 worktree 隔离。

## 总结

- **核心思维**:Node(任务)与 Edge(流动);对每个「然后」发问——数据真的跨过去吗?
- **14 步主线**:线性脚本 → 剪掉空箭头 → contract → edge 即数据契约 → fan-out → fan-in → 菱形拓扑 → 路由 → 验证器 → 隔离 → 收敛循环 → 模型分层 → 拓扑选型 → self-routing;
- **三条铁律**:fan-out 在独立处、验证在信任处、降模型在无判断力处;
- **一句话**:Prompter 问问题,Architect 画 graph——多数人继续把步骤排成一条线,学会画 graph 的人开一支集群。

## 延伸阅读

- 原文:https://x.com/0xCodez/status/2079165300625330317;中文:https://mp.weixin.qq.com/s/MhcPo5RMdg-alL0bZplinQ
- 站内:[Loop Engineering](loop-engineering.md)(循环与收敛)、[Git Worktree 并行开发](git-worktree-parallel-agents.md)(第 10 步隔离落地)、[Agent 规划与工作流模式](../../03-agents/agent-planning-patterns.md)(工作流四模式与菱形呼应)、[子代理隔离](../../03-agents/subagent-isolation.md)(上下文隔离原理)、[OpenAI 官方 Prompt 指南](openai-prompt-guide.md)(验证才算完成)、[Superpowers v6](../skills/mattpocock-skills.md)(并行 worktrees + 审查优化)
