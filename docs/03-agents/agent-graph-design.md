# Agent 图工作流设计:节点、边与验证的工程方法

> **一句话摘要**:很多人第一次做多步 Agent,写出来的其实是一条直线——不路由、不分支、不并行,只是在同一个上下文窗口里排队,窗口越来越长,Agent 也忘了最初要做什么。图工作流把工作本身设计成一张图:**节点负责任务、边传递结果、代码负责调度**。本文从设计角度讲透节点契约、数据边、扇出/扇入、钻石拓扑、验证器、收敛循环与模型分层,并给出 Claude Code dynamic workflows 的真实 JavaScript 写法与可运行的钻石拓扑演示。
>
> **来源**:微信公众号「山行AI」《Claude Graph Engineering:从线性 Agent 到图工作流架构师的 14 步路线》,https://mp.weixin.qq.com/s/6xqI5LlOPM8_SQ6Emexz4w;原文(0xCodez):https://x.com/0xCodez/status/2079165300625330317;原始资料存档于 `docs/inbox/agent-graph-design-source.md`

## 概念:把工作设计成图,而不是一串提示词

!!! tip "定位一段话"
    **提示词是一句话,循环是一种节奏,harness 是 Agent 站立的地板;真正决定 Agent 能跑多远的,是任务本身的拓扑结构。**

Claude Code 的 dynamic workflows 让 Claude 写一段普通 JavaScript 编排脚本,再启动一组 subagent 协同执行;**调度本身由代码完成,不持续占用主会话上下文**。核心观点:工作流的形状本身就是图——哪些步骤能同时跑、哪些必须等待、哪些结果要汇总、哪些发现要复核,这些不是"提示词写得好不好"的问题,而是**图结构问题**。

画出节点和边,就能看见三个机会:

1. 哪些步骤其实没有依赖,可以并行;
2. 哪些步骤只是数据清洗,应该用代码完成;
3. 哪些结果必须经过验证节点,才能进入最终答案。

!!! note "与站内 [Graph Engineering 14 步](../07-agent-coding/experience/graph-engineering-14-steps.md) 的分工"
    那篇是**使用经验路线图**(14 步怎么走、六张图怎么搭);本文是**设计方法**(为什么节点要契约、边为什么是数据、验证器怎么设计),并补上真实的 JavaScript workflow 代码。两篇互补,建议对照阅读。

## 原理:图工作流的十个设计决策

### 1. 节点是任务,边是流动的数据

图只有两个基础对象:节点(一段有边界的工作:一个 Agent、明确任务、输入输出)和边(依赖关系)。最常见的误区是把"然后"当成边——"总结这个文件,然后告诉我天气":天气查询不读取文件总结,它们是两个独立节点,只是被线性脚本硬绑。

!!! tip "判断边是否真实,问一句就够"
    **下一步是否读取上一步的输出?** 把工作画成盒子和箭头:盒子是一次 `agent()` 调用,箭头是返回值传入另一个节点 prompt 的变量。**画不出变量箭头,两个盒子就是独立的**——等待就是浪费。

### 2. 线性脚本是一种退化图

"先 A 再 B 再 C 再 D"也是一张图,只是退化成了链:每个节点一条输入边一条输出边。能跑,但慢且脆——C 卡住,D 永远不会发生。图工程的第一项能力:**重画这条链**——拿着每一条箭头问"这里真的有数据依赖吗",剪掉假边,线性链条就会变宽:独立节点同时跑,再汇入真正需要全量结果的节点。

### 3. 给每个节点一份契约

如果一个节点的输入输出说不清,就很难并行。契约三要素:**输入有边界**(显式传入,不假设能读共享上下文)、**输出有结构**(schema 验证,下游直接消费)、**任务只做一件事**。Claude workflow 里在 `agent()` 调用中提供 JSON schema,子 Agent 必须返回符合结构的数据,不匹配则验证层让它重试——而不是把自由文本丢给你手动解析:

```javascript
// 一个有契约的节点:输入有边界,输出被验证,只做一个任务
const ITEM = {
  type: 'object',
  additionalProperties: false,
  properties: {
    title:   { type: 'string' },
    url:     { type: 'string' },
    impact:  { type: 'string', enum: ['high', 'medium', 'low'] },
  },
  required: ['title', 'url', 'impact'],
};

const result = await agent(source.prompt, {
  label: `research:${source.key}`,
  schema: ITEM,
  agentType: 'general-purpose',
});
```

### 4. 把边当作数据契约

边不是"B 在 A 后面",而是"A 产出一种结构,B 消费这种结构"。用数据命名边之后:能看清边是否真实、只要结构不变两端节点就能替换。**很多边只是普通 JavaScript(展开/去重/过滤/排序),不需要模型判断**:

!!! warning "别为接线付 token"
    如果"合并结果"只是 `flatMap` 和 `Set`,就别启动一个 Agent。**Agent 应该用来做判断,不该用来搬管道;边如果全是 Agent,整张图就在为自己的接线付 token。**

### 5. parallel() 扇出 + 6. barrier 扇入

面对 N 个独立节点(N 个来源/文件/路由),用 `parallel()` 扇出。两个细节:**parallel() 是 barrier**(等所有 thunk 结束才返回);**抛错的 thunk 变成 null**(不拖垮整批),所以结果要 `.filter(Boolean)`。扇出的好处:主会话不必同时塞下 N 个来源,每个 subagent 携带局部上下文,只把结构化结果返回。

```javascript
phase('Research');
const raw = await parallel(
  SOURCES.map((s) => () =>
    agent(s.prompt, { label: `research:${s.key}`, phase: 'Research',
                      schema: ITEM_SCHEMA, agentType: 'general-purpose' }),
  ),
);
const collected = raw.filter(Boolean);
```

扇入节点是边汇合的地方,做真正需要全量视角的事(跨来源去重/按影响排序/总数为空提前退出)。**规则:只有真的需要所有上游结果时才设 barrier**——跨来源去重需要,单纯展开数组不需要。写出 `parallel -> transform -> parallel` 而 transform 无跨条目依赖,应该改 `pipeline`,别让所有 item 在中间集体等一次。

### 7. 钻石拓扑:fan-out → reduce → synthesize

把扇出和扇入合起来 = 严肃 Agent 图里最常见的拓扑:**钻石结构**——一个节点拆任务、多个节点并行、一个节点合并。市场扫描、依赖审计、代码审查、研究报告都套这副骨架。规范形式:**fan out(取广度)→ reduce(纯代码压缩)→ synthesize(最后 Agent 综合)**。看懂钻石后,问题从"怎样让 Agent 做更多步骤"变成"哪里该拆、哪里该合"。

### 8. 用条件判断在运行时路由

router 节点先分类,再由**代码**决定走哪条边(diff 风险高走完整审计、低走快速审查)。在 workflow 里就是 JavaScript 的 `if/switch`:

```javascript
const { severity } = await agent(`Classify this diff's risk: ${diff}`, {
  schema: { type: 'object', properties: { severity: { enum: ['low', 'high'] } },
            required: ['severity'] },
});
let review;
if (severity === 'high') {
  review = await parallel(FILES.map((f) => () => agent(`Audit ${f}`)));
} else {
  review = await agent(`Quick review of ${diff}`);
}
```

**Claude 负责分类,路由由代码执行**——同样的分类永远走同样的路径,不会出现模型临场跳过审计的意外。

### 9. 在边上放验证器(图的真正杠杆)

验证节点放在结果进入下游之前,唯一任务是**试着推翻这个发现**。三种模式:

| 模式 | 机制 |
| --- | --- |
| **对抗式验证** | 每个发现交给 N 个独立"怀疑者"反驳,多数未推翻才保留 |
| **多视角验证** | 每个 verifier 不同视角(正确性/安全性/可复现),多样性捕捉相同检查漏掉的失败模式 |
| **评委组** | 从多角度生成 N 个候选,评委并行打分,综合获胜者 |

!!! tip "真实案例"
    把 Bun runtime 移植到另一环境时,把对抗式代码审查嵌进循环,能提前挡掉单 Agent 容易漏掉的问题。

### 10. 隔离节点(失败不污染整张图)

线性链里 C 死了 D 就不运行;图要把失败限制在节点内——`parallel()` 异常→null + `.filter(Boolean)` 是 containment,fan-in 要能容忍缺失输入。更隐蔽的问题:**并行 Agent 互相踩文件**——多个 Agent 同时写代码互相覆盖,解法是每个 Agent 在自己的 git worktree 里执行、完成后再干净合并(它不是默认成本,而是"并行写文件"这类拓扑的安全带)。

### 11. 加循环,但必须收敛(loop-until-dry)

未知规模任务(搜索 bug、发现牵出新问题)需要受控循环。**不收敛的循环会无限启动 Agent 直到预算耗尽**。可收敛模式:

```javascript
const seen = new Set();     // 对所有"见过"的去重,不是只对已确认的
const confirmed = [];
let dry = 0;
while (dry < 2) {
  const found = (await parallel(FINDERS.map((f) => () => agent(f.prompt, { schema: BUGS }))))
    .filter(Boolean).flatMap((r) => r.bugs);
  const fresh = found.filter((b) => !seen.has(key(b)));
  if (!fresh.length) { dry++; continue; }
  dry = 0;
  fresh.forEach((b) => seen.add(key(b)));
  // 对 fresh 做多视角验证,通过后才进 confirmed
}
```

!!! warning "最常见的坑"
    对**所有见过的(seen)**去重,而不是只对已确认的(confirmed)——否则被否掉的发现每轮重新出现,循环永远不会干,你造了一台不断付费重新发现死胡同的机器。

### 12. 按节点给模型分层

图结构把"哪些节点重复、哪些节点需要判断"暴露得很清楚:抽字段、分类工单交给便宜模型;合成报告、裁决发现留给强模型。Claude 的 subagent 默认继承会话模型,但单个 `agent()` 可指定模型——**不改变图形状,就能显著改变成本**。

### 13. 拓扑决定成本和延迟

`parallel()` 的 barrier 让所有节点等最慢的那个;`pipeline()` 让每个 item 独立流经所有阶段(快的提前完成)。**默认先考虑 pipeline**,只有确实需要全量结果时才用 barrier(跨集合去重/总量 early-exit/需要对比其他发现的 prompt)。"代码更整齐"不是 barrier 的理由——分阶段不等于同步等待。

### 14. 让 Claude 自己画图(self-routing)

无法提前规划的任务,描述目标让 Claude 写编排脚本:拆任务、选扇出、启动 subagent fleet、合成结果。三个入口:prompt 里说"workflow"、运行已保存/内置 workflow(`/deep-research` 就是 scope→并行搜索→抓取→对抗验证→综合 的生产级图)、开 ultracode。跑得好按 `s` 存进 `.claude/workflows/`(版本控制、按名复跑、团队共享)。

## 代码 / 实现:钻石拓扑演示(纯 Python,可运行)

原文的 fan-out/reduce/synthesize 钻石结构,用纯 Python 落成可运行演示:

```python
def diamond(query: str, extractors: list, reducer, synthesizer):
    """钻石拓扑:fan-out(并行提取)→ reduce(纯代码压缩)→ synthesize(Agent 综合)"""
    # 1. fan-out:并行提取(模拟并行,异常 → None 被过滤)
    parts = [e(query) for e in extractors]
    parts = [p for p in parts if p is not None]
    # 2. reduce:纯代码压缩——去重 + 合并,零 token
    merged = reducer(parts)
    # 3. synthesize:最后一个 Agent 综合撰写
    return synthesizer(merged)

# —— 场景:研究"并行扇出 N 个来源,去重后综合报告" ——
def extract_a(q): return f"{q}:来源A 的发现(重复项)"
def extract_b(q): return f"{q}:来源A 的发现(重复项)"   # 与 A 重复
def extract_c(q): return f"{q}:来源B 的发现"
def extract_fail(q): return None                        # 模拟失败的来源

reducer = lambda parts: sorted(set(parts))              # 去重 + 排序(纯代码)
synthesizer = lambda merged: "综合报告:\n" + "\n".join(f"  - {m}" for m in merged)

report = diamond("供应链风险", [extract_a, extract_b, extract_c, extract_fail],
                 reducer, synthesizer)
print(report)
```

## 实践 / 应用:本周就能构建的六张图

| 图 | 形状 | 关键机制 |
| --- | --- | --- |
| **全路由安全扫描** | 每路由一个 agent → 验证器通道 | 覆盖单个上下文装不下的范围 |
| **带引用的深度研究** | 拆角度 → 并行搜索 → 去重 → 对抗验证 → 撰写 | `/deep-research` 生产级图 |
| **逐文件移植模块** | 按文件扇出 → 测试 gate → 失败回环 | 文件级并行 + 测试门禁 + 对抗审查 |
| **diff 对抗式审查** | 按大小/风险路由,大改动多视角并行审计 + 评委组 | 正确性/安全性/性能多视角 |
| **定时生态扫描** | 并行抓取 → barrier 按影响排序 → 摘要 | 存 `.claude/workflows/` 长期复跑 |
| **未知规模发现** | 并行 finder → 对 seen 去重 → 验证幸存 → 连续两轮空手停 | loop-until-dry 收敛 |

**设计要点收束**:先画盒子箭头再写代码;默认 `pipeline()`,只有真需要全量结果才 `parallel()`;边用代码不用 Agent;验证器放在高信任需求的边上;重复节点降模型档;并行写文件用 worktree 隔离;循环对 seen 去重。

## 总结

- **核心转变**:不要只要求 Agent"多做几步",要让工作图变宽——独立任务扇出、需要信心处加验证、判断不强的节点换便宜模型、真需要全量视角时再合并;
- **十条设计决策**:节点契约、数据边、扇出/扇入、钻石拓扑、代码路由、验证器三模式、节点隔离、收敛循环、模型分层、拓扑选型;
- **三条铁律**:fan-out 在独立处、验证在信任处、降模型在无判断力处;
- **一句话**:普通 prompter 会问一个问题,架构师会画一张图——线性 Agent 不是上限,它只是最容易写出来的第一种形状。

## 延伸阅读

- 原文:https://x.com/0xCodez/status/2079165300625330317;中文:https://mp.weixin.qq.com/s/6xqI5LlOPM8_SQ6Emexz4w
- 站内:[Graph Engineering 14 步路线图](../07-agent-coding/experience/graph-engineering-14-steps.md)(使用经验,对照阅读)、[Agent 规划与工作流模式](agent-planning-patterns.md)(工作流四模式与菱形呼应)、[Git Worktree 并行开发](../07-agent-coding/experience/git-worktree-parallel-agents.md)(第 10 步落地)、[Loop Engineering](../07-agent-coding/experience/loop-engineering.md)(循环收敛)、[云端软件工厂](../08-harness/cloud-software-factory.md)(Graph 状态机控制面)、[Agent 交接方法论](../07-agent-coding/experience/handoff-handover-methodology.md)(节点 contract 的交接视角)
