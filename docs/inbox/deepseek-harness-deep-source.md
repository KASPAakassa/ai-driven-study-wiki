> 素材说明(2026-08-14):DeepSeek Harness 深度解析(子系统/源码级)。
>
> 基于 research 子代理对 deepseek-ai/deepseek-harness master 分支 14 个文档的一手抓取(raw.githubusercontent.com):
> docs/cordis-primer.md、docs/subsystems/{core,session,tools,system-prompt,subagent,scope,llm-streaming,README}.md、docs/event-producer-consumer.md、docs/capability-seams.md、docs/agent-lifecycle.md、docs/tool-execution-pipeline.md、packages/core/agent-loop/README.md。
>
> 深度增量:六包 spine 与可替换 loop、事件词汇三域明细(emit/waterfall/parallel/serial 四种分派)、会话日志 reconstructability(EpochHeader+invariants)、工具执行管线三层策略(waterfall/guard/finalizeContent)、子代理 providers 与续谈机制(持久 Session+Activation+inbox FIFO)、scope 原语、事务化创建与取消语义、Cordis 集成(gen-cordis-catalog 校验/可逆 effect)。
>
> 去向:**扩展进** `docs/08-harness/deepseek-harness.md`(新增「深度解析(子系统与运行时机制)」章节,不新建文章避免碎片化)。
> 最值得深读源码:packages/core/agent-loop/README.md、packages/core/tools/src/index.ts、packages/core/session/src/index.ts + docs/agent-lifecycle.md 时序图。
