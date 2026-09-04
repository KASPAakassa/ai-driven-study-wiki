# 原始资料:论文 Harness Handbook(英文核心内容存档,中文翻译见正式文章)

> 论文:《Harness Handbook: Making Evolving Agent Harnesses Readable, Navigable, and Editable》
> 作者:Ruhan Wang (Indiana Univ) 等;Tencent HY LLM Frontier + Indiana + UMD + UGA + NUS
> arXiv:2607.13285v1 [cs.AI],2026-07-14,License: CC BY 4.0
> 链接:https://arxiv.org/abs/2607.13285;项目:https://ruhan-wang.github.io/Harness-Handbook/;代码:https://github.com/Ruhan-Wang/Harness_Handbook

## Abstract(原文)
The capability of a modern AI agent depends not only on its foundation model but also on its harness, which constructs prompts, manages state, invokes tools, and coordinates execution. As models, APIs, execution environments, and application requirements change, the harness must be continually modified... Before a human developer or coding agent can make such a change, they must identify all code locations that implement the target behavior. This is difficult because production harnesses are often large, tightly coupled, and behaviorally distributed across files, functions, execution stages, and state transitions... Behavior localization is therefore a central bottleneck in harness evolution. We introduce the Harness Handbook, a behavior-centric representation synthesized automatically from a harness codebase through static program analysis and LLM-assisted behavioral structuring... We also introduce Behavior-Guided Progressive Disclosure (BGPD)... Handbook-Assisted planning improves behavior localization and edit-plan quality while using fewer planner tokens. The largest gains appear for changes involving scattered implementation sites, rarely executed code paths, and cross-module interactions.

## Core definitions
- behavior localization: identifying ALL implementation sites associated with a behavioral request(重点是"全部";漏掉冷门分支 → 行为不一致)
- Harness Handbook: operational behavior representation,三层文档树 L1(系统级总览)/ L2(阶段级概览)/ L3(源码支撑细节单元,带 locator)+ 状态寄存器视图(记录关键状态由哪个阶段写入/读取/清空/重置)
- BGPD (Behavior-Guided Progressive Disclosure): 从 L1/L2 判断需求涉及哪些阶段 → 沿状态寄存器补入共享状态耦合的远端阶段 → 选 L3 条目取候选源码位置 → 沿调用关系适度扩展 → 打开当前仓库重新验证 locator → 只基于验证后的证据生成编辑计划

## Construction (Appendix A, 三阶段)
- Phase I: Shared Static Fact Extraction(共享静态事实提取)
- Phase II: Behavioral Organization(function-as-leaf:初始分配→review 收敛→验证定稿;file-as-leaf:文件卡片→推断阶段并分配→阶段内组织)
- Phase III: Hierarchical Synthesis and Packaging(文档树合成/状态寄存器视图构建/grounding 与失败处理/渲染与同步状态)
- 安全阀:L3 定位必须回到当前仓库验证;失效条目冻结排除;代码变化后局部重同步

## Experiment (Section 4 + Appendix C)
- 两个开源 harness:Codex、Terminus-2;每 harness 30 个修改请求,共 60 个
- 规划器统一 DeepSeek-V4-Pro;评审 GPT-5.5、Opus 4.8、DeepSeek-V4-Pro
- 计划胜率:Codex 28.3%→38.3%;Terminus-2 26.7%→45.6%
- 规划 token:Codex 10.2万→8.9万(-12.7%);Terminus-2 5.8万→5.3万(-8.6%)
- 文件/符号粒度 Recall/Precision/F1 共 24 项全部提高;F1 增益 5.0-18.8pp;"完全零重合"的 Wrong 指标最多下降 25.9pp
- 局限:只评编辑计划不验证补丁与测试;样本小且 LLM 裁判非人工金标准;构建/重同步成本未完整计入;静态分析难覆盖反射/动态加载/配置驱动/外部服务;缺消融与成熟代码索引对比;仓库无明确 LICENSE,完整评测代码未公开

## Appendix E walkthrough(Q1 三次完成确认)
- 请求:模型需连续三次标记 task_complete 才被评分(改 Terminus-2 的 completion handshake)
- 路由:SKILL.md → overview(L1) → index.md → stages/stage-4.8(Completion Gate)+ stage-4.7 → registers.md(reg-pending-completion 读写站点跨 loop/初始化/per-run reset)
- 验证:search_file_content(_pending_completion) 7 处,全在 terminus_2.py;三处站点:__init__(~L292 初始化)、_reset_per_run_state(~L1574 清空)、_run_agent_loop(~L1427-1440, L1552-1559 读写)
- 编辑:Boolean _pending_completion → 整数计数器 _completion_confirmations;四个 modify(初始化/per-run reset/loop 两分支)
- 计划格式:EDIT BLOCK(old_string 必须 byte-exact 从 read_file 复制)+ declarations JSON(will_modify/will_add/will_remove,供 handbook-resync 管道消费)
