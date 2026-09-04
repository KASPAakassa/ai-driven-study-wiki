# Cordis 插件框架深度解析:教程、原理、可靠性与适用性

> **一句话摘要**:Cordis 是 DeepSeek Harness(`dsh`)的底层插件运行时——一个"元框架":**插件 = 挂到共享 Context 的函数**,工具、LLM 适配器、文件访问、甚至 agent loop 本身都是插件;Context 同时是服务仓库、事件总线与 effect 注册表。理论根基是论文《A Programming Paradigm for Spatiotemporal Composability》(时间可组合性=卸载完全回滚副作用,空间可组合性=依赖反应式管理)。本文按"教程 / 原理 / 可靠性 / 适用性"四部分深度解析,并给出 7 章学习主线。
>
> **来源**:
> - Cordis 教程(7 章):https://deepseek-harness.github.io/deepseek-harness/develop/cordis-tutorial/
> - 概念参考(Cordis 入门):https://deepseek-harness.github.io/deepseek-harness/reference/cordis-primer
> - 论文:《A Programming Paradigm for Spatiotemporal Composability》(https://github.com/cordiverse/paper,2026-08-13 预印本)
> - Cordis 仓库:https://github.com/cordiverse/cordis

## 概念

### Cordis 是什么

Cordis 是一个**小型插件运行时**:每项能力(工具、LLM 适配器、文件访问、agent loop)都是挂载到**共享 Context** 的插件。dsh 以 vendor 方式引入它作为底层;`cordis.yml` 即应用组合(基础 `cordis.patch.yml` + 部署 overlay)。

### 理论根基:时空可组合性(Spatiotemporal Composability)

论文提出两个正交维度:

- **时间可组合性(Temporal)**:组件移除时**完全回滚其副作用**(每个上下文变换带逆,由运行时追踪——可逆 effect);
- **空间可组合性(Spatial)**:**声明并反应式管理组件间依赖**(上下文变化按 coeffect 规约通知组件);
- 两者统一到单一 **context type**,把时空可组合性从单组件推广到**整个交错组件系统**;
- Cordis 是其实现:"提供 effect 追踪 + coeffect 解析的核心库,以及带配置调和与热模块替换的声明式组件 loader"。

## 教程(7 章主线)

每章是可运行示例(命令 `node --import tsx ../../vendor/cordis/bin.js`,无需 API key),主线:插件 → 生命周期 → 服务 → 事件 → 配置 → 组合/HMR → 接入真实 harness。

| # | 章 | 核心概念 | 关键代码模式 |
| --- | --- | --- | --- |
| 1 | **第一个插件** | 插件=导出 `apply(ctx)` 的函数;配置即插件列表,配置项**并发启动**(加载顺序由依赖决定,非文件顺序) | `export function apply(ctx){...}` + yml 列 `- name: './hello.ts'` |
| 2 | **生命周期与 effect** | 插件卸载(配置修改/HMR/显式释放/依赖消失)时**自动撤销所有注册**;fiber 状态机 `PENDING→LOADING→ACTIVE→UNLOADING→DISPOSED`(另有 FAILED) | `ctx.effect(() => { const t = setInterval(...); return () => clearInterval(t) })` |
| 3 | **服务** | 服务=具名能力(`ctx.tools`/`ctx.llm`);消费方只指定能力名不 import 提供方;`inject` 声明硬依赖,**依赖持续跟踪**(服务消失→消费方卸载重载) | `class GreeterService extends Service { constructor(ctx){ super(ctx,'greeter') } }` + `export const inject = ['greeter']` |
| 4 | **事件** | 类型化事件(声明合并);**5 种分发模式**:`emit`(同步广播)/`parallel`(并发)/`serial`(顺序,首个非空值胜出短路)/`bail`(serial 同步版)/`waterfall`(环绕中间件) | `ctx.on('demo/transform', async (input, next) => input.includes('blocked') ? '** blocked **' : next())` |
| 5 | **配置** | 插件可带 `config` + 同名 `Config: Schema<Config>`(Schemastery);`apply(ctx, config)` 必收**完整校验后**配置;非法输入→`ValidationError`、FAILED、退出码 1 | `export const Config: Schema<Config> = Schema.object({ greeting: Schema.string().default('Hello') })` |
| 6 | **组合与 HMR** | 配置项元数据 `id`(稳定标识,区分"修改"vs"删除重建")、`disabled`、嵌套组、`isolate`(服务独立实例);HMR 先卸载回卷再加载;`ctx.registry` 诊断 fiber 状态 | 遍历 `ctx.registry` 找 `PENDING` fiber(缺依赖的合法静默态) |
| 7 | **进入 harness** | 用 `ctx.tools.register(defineTool(...))` 注册**模型可调用工具**;组合需 `dsh-system-prompt`(schema 贡献)+ `dsh-tools` | `inject: ['tools']` + `ctx.tools.register({ name, parameters, output, execute })` |

终点:能读懂 `examples/headless-agent/cordis.yml`——"真实 agent 就是这套组合再加 LLM 适配器、agent loop、持久化和运行入口"。

## 原理

### 五个核心概念(primer)

1. **插件 = 实现 Service 的对象**:函数带 `inject`/`apply(ctx)`,或 `Service` 子类,由 Cordis 挂载;
2. **Context = 服务容器**:`ctx.<key>` 按键查找(不 import 具体实现);
3. **inject 声明依赖**:依赖驱动加载顺序(而非手工 boot 排序);插件保持 `PENDING` 直到服务就绪;可选依赖用 `ctx.get()`;
4. **类型化事件**:`emit / parallel / serial / bail / waterfall` 五种分发,各有契约(可否 await、并发、返回值、短路);
5. **注册 = 可逆副作用**:`ctx.effect()/ctx.on()/服务注册` 都是 effect,reload/teardown 时按序撤销;每个注册必须有 disposer。

### 运行时机制

- **fiber 状态机**:每个插件一个 fiber,`PENDING` 是合法状态(依赖未满足)——"插件不输出"先查 fiber 状态;
- **waterfall 纪律**(仓库常设规则):观察型监听器必须调 `next()`,不调即有意吞掉下游(短路);harness 用 waterfall 实现 `agent/request`、`approval/request` 等策略点;
- **Loader/配置**:`@deepseek-ai/cordis-plugin-include` 解析 `!!js` 表达式(在加载时计算 config/disabled 值,其余元数据保持字面量);
- **scope 之上**:dsh 在 Cordis 之上加 scope 层(per-agent 可见性遮蔽,见 [dsh 深度解析](deepseek-harness.md))。

## 可靠性

### 可靠机制(文档验证)

| 机制 | 说明 |
| --- | --- |
| **可逆卸载** | 所有注册是 effect,插件卸载自动回卷;disposer 逆序、异步并发;`fiber.dispose()` 等待异步清理并**递归卸载子树** |
| **HMR 热重载** | 先卸载(回卷全部 effect)→ 依赖就绪后加载新实例;loader 按 `id` 配置调和(只改差异) |
| **配置校验** | apply 前经 Schema 校验;错误→带路径的 `ValidationError`、fiber 进 FAILED、退出码 1——**插件绝不会在配置不完整时启动** |
| **依赖卫生** | inject 持续跟踪;服务消失→依赖方整体卸载重载,防悬垂引用 |
| **事件短路** | serial/bail 首个非空值短路;waterfall 不调 `next()` 即否决——策略点可精确拦截 |
| **回滚语义** | 文档**没有独立"事务"机制**;回滚由"可逆 effect + fiber 状态机 + loader 调和"组合实现(如实标注) |

### 已知弱点(教程明说)

- **启动早期日志可能丢失**:模块解析失败只在 logger(console 导出器)就绪前经 logger 报错,可能看不到;
- **PENDING 是合法静默态**:缺依赖的插件无输出且不报错,需主动用 `ctx.registry` 诊断;
- **waterfall 陷阱**:忘记调 `next()` 会静默吞掉下游监听器。

## 代码 / 实现

**第一个插件**:

```ts
import type { Context } from '@deepseek-ai/cordis'
export const name = 'hello'
export function apply(ctx: Context) { console.log('hello from my first plugin') }
```

```yaml
# cordis.yml —— 配置即插件列表
- name: './hello.ts'
```

**服务 + 依赖**:

```ts
export class GreeterService extends Service {
  constructor(ctx: Context) { super(ctx, 'greeter') }
  greet(who: string) { return `Hello, ${who}!` }
}
declare module '@deepseek-ai/cordis' { interface Context { greeter: GreeterService } }
export const inject = ['greeter']   // 硬依赖:greeter 就绪前保持 PENDING
```

**事件 + waterfall 短路**:

```ts
ctx.on('demo/transform', async (input, next) => {
  if (input.includes('blocked')) return '** blocked **'  // 不调 next() = 否决
  return next()
})
```

**进入 harness(注册模型可调工具)**:

```ts
export const inject = ['tools']
export function apply(ctx: Context) {
  ctx.tools.register(defineTool({ name: 'greet', parameters: {...},
    output: {...}, async execute(args) {...} }))
}
```

## 实践 / 应用(适用性)

### 适合做什么

- **一切皆插件、需可替换提供方/热替换/细粒度组合**的 agent 系统(dsh 就是样板);
- **策略拦截**:approval/agent/request 等 waterfall 策略点,可精确否决/改写;
- **能力解耦**:换 shell/fs 提供方而消费方不动(seam 三角色)。

### 与其它插件系统的对比

| | Cordis | VS Code 扩展 | Obsidian 插件 |
| --- | --- | --- | --- |
| 组合方式 | **单进程内依赖驱动的有序加载** + 配置即组合(cordis.yml) | manifest + activation events | 单进程 API 注册 |
| 运行时 | 可逆 effect、HMR、类型化事件、scope | 无运行时可逆组合 | 无依赖图协调 |
| 定位 | 元框架(meta-framework) | 应用扩展系统 | 应用扩展系统 |

### 门槛与注意

- **概念门槛**:inject/PENDING、fiber 状态机、waterfall 的 `next()` 纪律(有静默吞下游陷阱);扁平服务命名空间需前缀避让(`tools`/`llm` 已被占用);
- **生产风险**:官方 README **明确警告 under active development、API 尚未稳定**——生产采用需评估;
- 教程声称无需深入 TypeScript(仅 3 项特性:类型注解、`import type`、声明合并),实际学习曲线主要在概念而非语法;
- 与站内思想呼应:可逆 effect 与 [SKILL.md 自进化](../04-practice/skill-evolution-results-driven.md) 的"可回滚 patch"、[Pi 的插件热重载](../08-harness/pi-agent-harness-deep-dive.md) 同理念;waterfall 策略点呼应 [Agent 治理 Hook](../03-agents/agent-governance-hooks.md)。

## 总结

1. **Cordis 是什么**:dsh 底层的插件运行时/元框架——Context 是服务仓库 + 事件总线 + effect 注册表,一切能力都是插件;理论根基是时空可组合性论文。
2. **教程主线 7 章**:插件形态 → 生命周期/可逆 effect → 服务/inject 依赖 → 事件(5 种分发)→ 配置校验 → 组合/HMR/诊断 → 接入真实 harness;每章可运行、无需 API key。
3. **可靠性**:可逆卸载(自动回卷+递归)、HMR(先回卷再加载)、配置校验(ValidationError/FAILED)、依赖卫生、事件短路;回滚由"可逆 effect+fiber+loader"组合实现(无独立事务);已知弱点:启动早期日志丢失、PENDING 静默、waterfall 吞下游陷阱。
4. **适用性**:适合"一切皆插件"的 agent 系统、策略拦截、能力解耦;对比 VS Code/Obsidian 更强调单进程内依赖图协调与可逆组合;官方警告 API 未稳定。
5. **学习路径**:先走教程 7 章,再读 primer 概念参考与 `cordis-api/context` 参考页,最后对照 `examples/headless-agent/cordis.yml`。

**下一步学什么**:读 [DeepSeek Harness 深度解析](deepseek-harness.md)(看 Cordis 如何被 dsh 使用:六包 spine/事件三域/scope);范式背景见 [基于插件的 Agent 开发范式](../03-agents/agent-plugin-development-paradigm.md);想上手先跑教程 01 章。

## 延伸阅读

- 站内:[DeepSeek Harness 深度解析](deepseek-harness.md)、[基于插件的 Agent 开发范式](../03-agents/agent-plugin-development-paradigm.md)、[Pi Agent Harness 深度解析](pi-agent-harness-deep-dive.md)(插件化对照)、[Agent 治理 Hook](../03-agents/agent-governance-hooks.md)
- 官方一手:教程总览与 7 章(https://deepseek-harness.github.io/deepseek-harness/develop/cordis-tutorial/);Cordis 入门 primer(https://deepseek-harness.github.io/deepseek-harness/reference/cordis-primer);Cordis 核心 API(https://deepseek-harness.github.io/deepseek-harness/reference/cordis-api/context)
- 底层:Cordis 仓库(https://github.com/cordiverse/cordis);论文《A Programming Paradigm for Spatiotemporal Composability》(https://github.com/cordiverse/paper)
