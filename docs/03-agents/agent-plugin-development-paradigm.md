# 基于插件的 Agent 开发范式:从"向上封装"到"原子化透明"

> **一句话摘要**:LangChain 范式为了**降低 Agent 开发复杂度**而向上封装;DeepSeek Harness 代表的插件化范式为了**降低 Agent 体验与成本优化的复杂度**而把一切原子化、透明化——模型怎么接、工具怎么调、会话怎么存、主循环本身,全都做成可插拔组件,日志作为唯一真相源。本文拆解插件化范式的四特性、与封装范式的"双层不透明"对比、dsh 的 Bundle→Profile→Patch→Overlay 分层机制,并**扩充思考**:范式光谱、何时该选哪种、与可观测性/评估驱动优化/长时任务思想的呼应及局限。
>
> **来源**:阿里云云原生《一切皆插件之后,Agent 工程的新范式》(https://mp.weixin.qq.com/s/OgYIw9l8PBeRk5MGMhYTmA);配套框架详解见站内 [DeepSeek Harness](../08-harness/deepseek-harness.md)

## 概念

### 插件化:软件可扩展性的老概念,Agent 的新用法

插件是软件架构的常见术语(浏览器翻译插件、手机应用商店都是"操作系统插件"),四特性:

| 特性 | 含义 |
| --- | --- |
| **解耦** | 插件自身是完整功能块,不改主体代码 |
| **可插拔** | 装上就能用,卸下就消失,对原软件无影响 |
| **可替换** | 同一插口可换不同插件(换个更好用的翻译插件) |
| **标准化** | 遵守同一接口规则,不同人写的插件互相兼容 |

放到 Agent 语境,**"一切皆插件"**意味着:模型怎么接、工具怎么调用、会话如何保持、对话怎么记忆、交互怎么呈现、甚至 **Agent 主循环本身**,都做成可插拔组件——把插件**细颗粒度化做到极致**,出发点是**让 Agent 的运行足够透明**:每一次运行有迹可循,全部可回放、可分叉、可审计,从而降低体验与成本优化的复杂度。

> 核心命题:**插件化颗粒度越细,黑盒越少,运行越透明,优化空间越大**。目标不同,架构不同——架构是应用智能的瓶颈。

### 两种范式的目标分野

| | LangChain 范式 | 插件化范式(dsh) |
| --- | --- | --- |
| 代表 | LangChain / LlamaIndex / AutoGen / CrewAI | DeepSeek Harness / Pi |
| 目标 | **降低 Agent 开发复杂度**(快速搭出能跑的应用) | **降低 Agent 体验与成本优化复杂度** |
| 手段 | 向上封装:Chain/Agent/Tool/Memory/Retriever 高度抽象,藏起运行时细节 | 原子化插件:循环/会话/工具/UI 全可插拔,日志即真相源 |
| 代价 | 门槛低,但看清行为难 | 门槛高,但框架层行为可见 |
| 适合 | 快速验证、不熟 LLM 的工程师 | 深度打磨效果与成本、熟悉底层的工程师 |

## 原理

### 问题:双层不透明

1. **模型本身是黑盒**:为什么选这个工具、为什么生成这段推理、为什么在这步失败——只能看到输入输出;
2. **框架再叠一层黑盒**:LangChain 等把 Agent 循环、工具编排、Memory、Prompt 组装、重试、中间件藏进框架;上下文如何拼接、工具结果如何截断/注入、循环如何决定继续或停止,往往要开 tracing、翻源码或依赖外部观测工具才能看清;
3. 结果:**模型黑盒 + 框架黑盒 = 双层不透明**——看到 Agent 做了什么,却难回答"为什么这样做、每步上下文长什么样、哪环节浪费了 token"。

### 解法:原子化插件 + 日志作为唯一真相源

- 模型看到的每一段内容、工具调用与结果、上下文注入、循环决策,都记录在**可回放的事件流**;
- 插件边界清晰,换掉/拦截某一层(如 Prompt 组装、工具执行流水线)影响范围可控且可观察;
- 抽象更少,杜绝"框架替你做决定却不告诉你";
- **代价**:开发需理解更多底层细节、门槛更高;换来的是在模型解释性弱的现实下,把框架层行为尽量看清楚,更有针对性地做效果与成本优化。

### dsh 的分层机制(Bundle → Profile → Patch → Overlay)

```
1. Bundle(组合包)层   基础插件包(npm 包 + cordis.patch.yml 声明挂载哪些插件行)
                      官方:dsh-base(模型/工具/持久化/沙箱/设置/凭据/遥测)、
                      dsh-web-app(Web UI)、dsh-headless(无服务器一次性)
2. Profile(配置档案)层  具名组装方案(~/.dsh/profiles/<name>):列出 Bundle 顺序 + 自己的 patch
3. 用户 Patch 层(两级)  Profile 的 cordis.patch.yml > Home 级 $DSH_HOME/cordis.patch.yml
4. 命令行 Overlay 层    dsh ... --patch xxx.yml(最高优先级,临时)
叠加顺序:Bundle(按列表)→ Profile patch → Home patch → --patch
查看实际树:dsh --profile web --dump-config(打印的每一行都能按 id 替换/新增)
```

另有 **Capability Seam(能力接缝)**:可替换能力 = 接口定义 + Provider 实现 + Consumer 使用,换一个 Provider 影响整条相关链路。

### 与 Pi Agent 的对比

- **Pi**:哲学是"**最小核心 + 按需扩展**"(Read/Write/Edit/Bash 四工具 + 极简 prompt,其余靠 TS 扩展/Skills/Packages 按需加载),适合终端工作流,强调可控、低噪音、高缓存命中——**像一把精巧的手术刀**;
- **dsh**:走得更彻底——不仅工具可扩展,**循环、会话、沙箱、UI、调度本身都是插件**,提供 Web UI 与多种运行模式,Session 事件流更完整,面向**更广泛的 Agent 基础设施**(泛智能体,不止 Coding)——**像一套可自由重组的手术台与器械库**;
- 共同点:都追求透明与可定制;差异在插件化的彻底程度与适用范围。

## 代码 / 实现

**使用插件**:

```bash
npx @deepseek-ai/dsh web                  # 官方组合
dsh --profile web --dump-config          # 查看/调试插件树
dsh plugin --profile web add <npm包|路径> # 安装 Bundle(自动加入 Profile)
dsh web --patch ./my-patch.yml           # 本地临时补丁(insert 或按 id 替换)
```

**写插件(基本模板,注册的一切可逆,卸载自动清理)**:

```ts
import type { Context } from '@deepseek-ai/cordis'
export const name = 'my-plugin'
export const inject = ['tools']          // 可选:声明依赖
export function apply(ctx: Context) {
  // 注册工具、监听事件、提供服务(如 ctx.tools.register(...)、ctx.llm、ctx.sessions)
}
```

**贡献方式**:①写可安装 Bundle(npm 包,`package.json` 声明 `"dsh": { "bundle": { "patch": "./cordis.patch.yml" } }` + cordis.patch.yml + 插件代码,发布 npm,加 `dsh-plugin` topic);②本地插件/直接贡献官方(见 CONTRIBUTING.md 与 docs/cookbook:添加 package/tool/LLM adapter/Chat node 指南)。插件形式支持函数、对象或类(继承 Service)。

## 实践 / 应用

### 对效果与成本调优的帮助

- **效果调优**:可独立替换循环策略、上下文注入逻辑、工具执行流水线、沙箱策略;极简模式做模型基准测试;创造模式在内存中试验新组合;**完整轨迹回放让"为什么失败"一目了然**,而非黑盒猜测;
- **成本调优**:Session 日志暴露每一次 token 消耗来源;针对缓存友好性调整 Prompt 组装、工具 Schema 排序;换更轻量的循环或工具集;做 Provider 级优化——**同一模型换不同插件组合,成功率与单位成本可出现显著差异**;
- **持续迭代**:插件可逆、热替换可行——像调参一样调架构,换沙箱、改事件拦截点、重组 Bundle,立即观察效果与成本变化。

### 我的思考:范式光谱与选型(扩充)

**① 两种范式不是取代关系,是光谱两端。** 封装范式解决"怎么快速跑起来",插件范式解决"怎么精确优化好"。合理路径是**分阶段**:原型期用封装范式快速验证可行性;进入打磨期(有真实用户、有效果/成本指标、有 eval 能力)再迁到插件范式精调。直接上手插件范式,若没有明确优化目标,反而背上了高门槛。

**② "透明"不等于"可解释"。** 插件化消灭的是**框架层黑盒**,模型层黑盒依然存在(为什么选这个工具,模型自己也无法完全说明)。它把问题从"双层黑盒"收窄为"单层黑盒 + 完整行为轨迹"——这已经足够支撑**证据驱动的调试与优化**,但要诚实:轨迹能回答"发生了什么",不能回答"模型内部为什么"。

**③ 与知识库既有思想的呼应**:
- **可观测性至上**:呼应 [Pi 的"文件即状态/事件流"](../08-harness/pi-agent-harness-deep-dive.md)、[Claude Code 官方最佳实践(验证闭环)](../07-agent-coding/claude-code-deep-dive/claude-code-best-practices.md);
- **日志即真相源**:呼应 [LongHorizon-Harness 的"任务状态脱离上下文、审计可复放"](../09-agent-research/longhorizon-harness-paper.md) 与 [阿里 SKILL 自进化的"results+轨迹"](../04-practice/skill-evolution-results-driven.md)——"轨迹可信、自述不可信"是同一套信念;
- **LLM 是概率性执行组件**:插件化范式正是 [Vibe Coding 工程栈](../07-agent-coding/experience/vibe-coding-engineering-practice.md) 中 Harness/Loop 层的极致化——用系统机制补上"不保证每一步正确";
- **评估驱动**:透明的插件树让 [评估驱动开发](../03-agents/agent-eval-driven-dev.md) 与 [Agent 效果优化](../04-practice/agent-effect-optimization-practice.md) 有更精确的干预点。

**④ 局限与风险**:开发门槛高(需理解底层细节);开发者预览、API 会 breaking changes;**过度工程风险**——为透明而插件化,可能让简单任务背上复杂组合的成本;插件生态尚在早期(`dsh-plugin` 刚起步);"颗粒度越细越透明"也有边界——插件太多本身会引入新的选择与组合复杂度(呼应 [Agent 开发方法选型](agent-development-methods.md) 的"避免多套最高指挥部")。

## 总结

1. **范式分野**:LangChain 范式为降低**开发复杂度**向上封装;插件化范式为降低**体验与成本优化复杂度**而原子化透明——目标不同,架构不同。
2. **双层不透明的解法**:模型黑盒无法消除,但插件化 + 日志即真相源能把**框架层黑盒**抹掉,让每一次运行可回放、可分叉、可审计。
3. **dsh 落地机制**:Bundle → Profile → Patch → Overlay 分层叠加,`--dump-config` 所见皆可改;Capability Seam 让换一个 Provider 影响整条链路。
4. **与 Pi 的差别**:Pi 是"最小核心+按需扩展"的手术刀;dsh 是连循环/会话/UI 都可插拔的"手术台+器械库",面向泛智能体。
5. **我的判断**:两种范式是光谱两端,分阶段选型;透明≠可解释(只剩单层模型黑盒);插件化是评估驱动优化的理想底座,但要防过度工程与早期生态风险。

**下一步学什么**:框架细节见 [DeepSeek Harness](../08-harness/deepseek-harness.md);对照 [Pi Agent Harness 深度解析](../08-harness/pi-agent-harness-deep-dive.md) 理解"插件化的两种程度";范式选型见 [Agent 开发方法选型](../03-agents/agent-development-methods.md)。

## 延伸阅读

- 站内:[DeepSeek Harness:一切皆插件](../08-harness/deepseek-harness.md)、[Pi Agent Harness 深度解析](../08-harness/pi-agent-harness-deep-dive.md)、[Agent 开发方法选型](../03-agents/agent-development-methods.md)、[Building effective agents 五种模式](agent-building-effective-agents.md)、[LongHorizon-Harness](../09-agent-research/longhorizon-harness-paper.md)、[SKILL.md 结果驱动自进化](../04-practice/skill-evolution-results-driven.md)、[Vibe Coding 最佳实践](../07-agent-coding/experience/vibe-coding-engineering-practice.md)
- 外部:原文(https://mp.weixin.qq.com/s/OgYIw9l8PBeRk5MGMhYTmA);DeepSeek Harness 官方(https://github.com/deepseek-ai/deepseek-harness、https://deepseek.com/harness)
