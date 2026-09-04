> 素材说明(2026-08-14):Cordis 插件框架深度解析(DeepSeek Harness 底层运行时)。
>
> 来源(research 子代理一手抓取,均经官方文档逐字验证):
> - Cordis 教程 7 章:https://deepseek-harness.github.io/deepseek-harness/develop/cordis-tutorial/(01-first-plugin ~ 07-into-the-harness,中文,每章可运行示例,无需 API key)
> - 精简概念:https://deepseek-harness.github.io/deepseek-harness/reference/cordis-primer
> - 论文《A Programming Paradigm for Spatiotemporal Composability》:github.com/cordiverse/paper(2026-08-13 预印本,摘要级)
> - Cordis 官方 README:github.com/cordiverse/cordis
>
> 四部分要点:教程(7 章主线:插件→生命周期/effect→服务→事件→配置→组合/HMR→进入 harness)、原理(Context 服务仓库/fiber 状态机/inject 依赖/5 种事件分发 emit-parallel-serial-bail-waterfall/可逆 effect/时空可组合性)、可靠性(可逆卸载/HMR/配置校验 ValidationError/依赖卫生/事件短路;无显式事务,回滚由可逆 effect+fiber+loader 调和;已知弱点:启动早期日志丢失、PENDING 静默)、适用性(一切皆插件/策略拦截/能力解耦;对比 VS Code/Obsidian 插件系统;README 警告 API 未稳定)。
>
> 去向:`08-harness/cordis-plugin-framework.md`
> 站内关联:deepseek-harness.md(集成部分)、agent-plugin-development-paradigm.md(插件化范式)。
