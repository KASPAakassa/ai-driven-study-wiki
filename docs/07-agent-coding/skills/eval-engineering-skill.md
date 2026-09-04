# Eval Engineering Skill:让 Agent 自己帮你设计评估测试(LangChain 开源)

> **一句话摘要**:LangChain 开源的 Eval Engineering Skill——装进 Claude Code/Codex 后,它能读懂你的 Agent 代码仓库、分析生产 traces,通过"面试式"交互帮你设计可执行的评估测试,形成"评估驱动改进"的持续学习闭环。
>
> **来源**:微信公众号《LangChain 刚开源了个 Eval Engineering Skill》(seebin),https://mp.weixin.qq.com/s/HpejKK3-rbYbqPmG3RuB-Q;仓库 https://github.com/langchain-ai/langchain-skills

## 概念:这是什么 Skill

**Eval Engineering Skill** 是 LangChain 开源仓库 `langchain-ai/langchain-skills` 中的一个 Skill(已核验,1111+ stars),定位:**
帮 Agent 开发者解决"评估太难"的问题**——不是一键生成测试,而是**跟你一起迭代**设计评估。

!!! note "归类"
    本页属于 **Skill 收藏**(可复用 Skill 索引);它背后"评估驱动开发"的 Agent 基础方法论见 [评估驱动开发:把评估变成开发流程的一部分](../../03-agents/agent-eval-driven-dev.md)。

## 原理:它解决哪三个痛点

| 痛点 | 说明 | 本 Skill 的解法 |
| --- | --- | --- |
| 评估与真实使用脱节 | 手写测试凭经验猜,生产场景没覆盖 | 读代码仓库 + 分析真实 traces |
| 生产 traces 藏金矿 | 工具调用/返回/错误全在轨迹里,但难转测试 | 从 traces 提取真实参数/返回/错误,还原真实行为 |
| 改了没法快速验证 | 换模型/调 prompt 不知道变好还是变坏 | 标准化评估 + 多轮迭代对比 |

## 工作方式:四步流程

1. **读代码仓库**:自动扫描 Agent 仓库,识别 prompt、模型、工具、API 调用等组件,搞清整体结构;
2. **分析 traces**:提供生产轨迹时,提取真实工具调用参数、返回结果、错误信息,还原生产环境真实行为;
3. **"面试"式确认**(最聪明的设计):不一次性生成一堆测试,先提出几个值得测试的能力方向,通过对话确认——哪些工具真实调用?哪些模拟?哪些最值得测?**由你拍板**;
4. **输出标准 Harbor 格式评估**:

| 组成部分 | 内容 |
| --- | --- |
| **Instruction** | 给 Agent 的任务指令 |
| **Environment** | 用 Dockerfile 定义的可复现环境 |
| **Verifier** | 验证器,判断任务是否真正完成 |

## 关键洞察:为什么不能一键生成

!!! tip "反直觉的事实"
    团队发现:**最好的评估,几乎都是经过多轮反馈才出来的**——尤其是验证器,第一版特别容易被 Agent 钻空子。

**验证器的三种典型作弊方式**:

1. **过度引用无关文档来刷分**;
2. **假装完成了某个动作其实没做**;
3. **利用暴露的答案信息走捷径**。

**修复方法**:同时看 Agent 的运行轨迹和验证器的运行轨迹,快速定位问题,再修正。

## 实践 / 应用:怎么用

```bash
# 仓库:https://github.com/langchain-ai/langchain-skills
# 路径:config/skills/eval-engineering
# 装进 Claude Code 或 Codex,打开要评估的 Agent 仓库,可选提供 traces,用一句话启动
```

启动后它会:先读代码仓库 → 提出几个评估方向让你选 → 建好完整评估任务 → 跑一遍 → 看结果 → 再迭代。

!!! tip "实测成果(官方口径)"
    LangChain 在自己的文档问答 Agent `chat-langchain` 上跑通这套流程;在 **Terminal-Bench 2.0** 上,光靠调整 harness(提示词、工具、编排策略)在评估指标上 hill-climbing,拿到 **13.7% 提升**——没换模型、没做微调,就是"更好的 harness engineering + 评估驱动"。

## 总结

- Eval Engineering Skill = **读仓库 + 分析 traces + 面试式确认 + 输出 Harbor 格式评估**;
- 价值:解决评估与真实脱节、traces 金矿难转化、改完无法快速验证三大痛点;
- 关键认知:**评估不能一键生成**,验证器要靠多轮反馈打磨(防作弊:过度引用/假完成/走捷径);
- 落地形态:评估成为 Agent 的训练目标与回归测试集,环境容器化支持模型/提示词/工具随意替换对比。

## 延伸阅读

- 站内:[Skill 收藏](index.md)、[评估驱动开发](../../03-agents/agent-eval-driven-dev.md)、[Agent 评测](../../03-agents/agent-evaluation.md)、[WorkBuddy Bench](../../03-agents/workbuddy-bench.md)
- 外部:仓库 https://github.com/langchain-ai/langchain-skills;Harbor 评估格式;原始资料存档于 `docs/inbox/eval-engineering-source.md`
