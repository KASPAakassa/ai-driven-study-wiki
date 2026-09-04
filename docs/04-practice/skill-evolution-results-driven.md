# SKILL.md 结果驱动自进化:用评测和轨迹把 Agent 拉回正轨

> **一句话摘要**:改 Skill 像打地鼠——修好这个 case,弄坏那几个。阿里技术(代码安全工程师)把这变成一套可重复的工程闭环:**评测 → 规则诊断 → LLM 生成候选 patch → 四层 gate 验证 → 接受或进黑名单**。核心哲学:这不是"AI 自己教自己",而是**用可复查的工程纪律约束 LLM 的不确定性**——诊断/验证/回滚/黑名单全部用确定性规则,LLM 只负责把诊断结论转写成 unified diff。真实数据:自动进化后通过率从 77.8% 提到 88.9%。
>
> **来源**:阿里技术《Agent 越改越乱之后,我用评测和轨迹把它拉回来了》(https://mp.weixin.qq.com/s/h0ZsF5FdYZ_j5XrGmHBdXw)

## 概念

### 问题:改 SKILL.md 像打地鼠

SKILL.md 是 agent 的"工作手册",直接影响一类任务的上限。但 agent 总在某些 case 上稳定栽跟头;改两句修好这个,之前能做对的又错了——**按下这个冒出那个**。

### 五步闭环

```
跑一批测试任务(看哪些 case 错)
  → 自动分析为什么错(有规则,不是瞎猜)
  → 自动生成 patch 改 SKILL.md
  → 验证(改好了这个,没搞坏那个)
  → 通过则接受;不通过则丢弃,记进黑名单
```

### 适用判据:输出能否被客观判定对错

> 能不能跑自进化,只取决于一条标准:**任务的输出,能不能被客观判定对错**。

- **适合**:结论收敛、有标准答案——是不是垃圾邮件、代码有没有漏洞、合同金额对不对(对就是对);
- **不适合**:开放式任务——写文案、总结得漂亮(好坏见仁见智,没法机械判断"这次改得好不好")。

### 核心哲学:不是"AI 自己教自己"

LLM 只负责**把诊断结果写成候选修改**;诊断、验证、回滚、黑名单这些容易出事故的环节,**全部交给可复查的规则**。"我不假设模型会突然变聪明,只是把它容易犯糊涂的地方收进工程约束里。"

## 原理(系统拆解)

### 输入:结果与过程缺一不可

- **results.jsonl**(评测结果,每行一个 case):`case_id` / `ground_truth`(标准答案)/ `judge_verdict`(AI 裁判判定)/ `pass_fail` / `failure_kind`(FN 漏报 or FP 误报);
- **sessions/<case_id>.jsonl**(操作日志轨迹):agent 搜了什么、读了什么、在哪步做了什么决定——诊断引擎靠它判断哪里走偏。

数据来自自建评测平台 sec-code-bench(FastAPI+SQLite):**评测运行在真实任务环境**(通过 OpenAPI 对接真实任务运行平台,agent 用的模型/工具链/环境与日常一致,避免"实验室假象"),一键导出 zip(results + sessions + manifest)。

### 诊断:第一个反直觉设计——不用 LLM

让 LLM 直接判断 skill 好不好,**稳定性明显低于规则方法,部分设置接近随机水平**(换 prompt 或温度结论就漂移)。取舍:**宁可少判,不要飘着判**。

- **第一步 trace_parser 压缩 100:1**:原始 session 10-50 万 token → 几千 token 结构化 JSON(三层:①工具调用骨架 ②阶段统计 ③进度交叉验证——声称走了 STEP1/2/3 但实际有没有对应调用);
- **第二步 flow_diagnosis 规则集**(检测 agent 行为坏习惯,不含业务关键字,可跨任务迁移):

| 规则 | 检测什么 |
| --- | --- |
| `no_tool_calls` | 零工具调用(不干活) |
| `redundant_retry` | 同工具同参数调 ≥3 次(没进展) |
| `repeated_file_edits` | 同文件编辑 ≥5 次(试错型修改) |
| `tool_error_burst` | 真实 error ≥8 条(过滤良性 error,如 Search 空结果) |
| `tool_error_high_rate` | 单工具 error 率 ≥50% |
| `tool_imbalance` | 单工具占 >60% 调用 |
| `progress_mismatch` | 声称走了 STEP 但实际缺步(说一套做一套) |
| `conclusion_missing` | 调了 ≥5 个工具但没给结论(做了不交卷) |

- **联合归因**:结果类型 × 流程问题 = 根因(如 FN + progress_mismatch → 声称追了调用链实际没追到实现层)。**只有"结果错误 + 流程异常"的交集才触发进化**;pass 但流程有瑕疵不急着改(避免过度优化);
- **聚合门槛**:同一根因覆盖 **≥30%** 失败 case 才值得改——低于说明失败太零散,不是系统性问题。

### gt_auditor:质疑测试数据本身

大多数系统假设标注是对的;实际上**标注也可能错**——为迁就错误标注改 SKILL.md 会把系统改歪。给每个失败 case 打 **GT 可疑度**(0~1,五信号加权):agent 与 Judge 一致但跟 GT 相反(0.40)、步骤覆盖完整(0.20)、执行清洁(0.10)、无重试(0.10)、结论明确(0.10);可疑度 ≥0.5 标为"GT 嫌疑"。

关键设计:GT 嫌疑 case **不排除出评测**(仍参与 gate,否则选择性忽略数据),但 patch 生成时告诉 LLM"这些可能是标注错误,别为迁就它们改歪 SKILL.md"。

### patch 引擎:LLM 只生成候选 diff

- **输入刻意压短**(合计 <10KB):当前 SKILL.md + 失败联合归因摘要 + GT 审计结果 + taboo 黑名单——输入越短越不容易带散;
- **输出严格 unified diff**(可直接 `patch` 应用;diff 可机器回滚,描述文字不行);
- **三层过滤**(全确定性规则):
  1. **taboo 拦截**(LLM 调用前):按 rule_id + 诊断方向查黑名单,试过且被拒的跳过,省一次调用;
  2. **结构检查**(返回后):必须含 `---/+++/@@` 三件套、**diff ≤80 行**(learning rate,防灾难性遗忘)、不允许新增标题行(防重组结构);
  3. **文本质量检查(反口号)**:DO/步骤行必须含工具名或文件路径(反引号代码/类名/文件路径/函数调用/CLI 参数,一个都没有就是空话);黑名单短语("无论如何""永远不")直接拒绝;声称"修复 X"必须编码具体动作。

### 四层 gate:改完之后怎么确认没搞坏

| 层 | 检查 | 保证 |
| --- | --- | --- |
| **Target Gate** | 本次想修的 case 至少 1 个从错变对 | 改了有用 |
| **Guardrail Gate** | 之前答对的 case 一个都不能答错 | 没搞坏旧功能 |
| **Holdout Gate**(每 5 轮) | 未参与诊断的隐藏测试 F1 不掉 >1pp | 泛化没退步 |
| **Verify Gate** | SKILL.md 文本质量打分 ≥75 且不掉 >5 分 | 手册没自相矛盾/废话 |

任何一层不过,patch 整体丢弃。**数据集隔离**(防背答案):Selection 60%(target+guardrail,每轮判定)/ Holdout 25%(每 5 轮看)/ Golden 15%(人工审过,verify 校准,永不参与进化)。

### 黑名单:进化的记忆

每次 patch 被拒都记录(`rule_id` + `diff_hash`(SHA256 前 16 位)+ reason)。**跨版本、跨分支共享**(回滚到 v2 仍知道 v3 的失败经验;实验分支教训主线受益);**回滚不清空**。没有它,系统会在几个"看起来合理但实际有害"的修改间反复横跳。

### 收敛判断:知道什么时候该停

四个信号任一满足就建议停止:①F1 ≥ 0.95;②连续 5 轮 gate 没通过;③SKILL.md 超 15000 字节;④达到最大迭代次数。

- **加权停滞**:每轮停滞增量 = 0.3×target 未改善 + **1.0×guardrail 回归** + 0.7×holdout 下降,累到 5.0 触发停止——**搞坏比没改好严重 3 倍多**;
- **自动回滚(负迁移保护)**:当前版本若比历史最佳 holdout 差,回滚——防"每轮单点改善、holdout 慢慢下滑"的累积负迁移;
- **精简模式**:SKILL.md >15KB 后新增规则会互相遮挡,切换为"只允许合并/删除冗余规则,不允许新增"。

### 语义陷阱:换个词,准确率掉 27 个百分点

对照实验:同一份 SKILL.md 只把核心词"漏洞"换成"风险",正确率从 **89.3% → 62.1%**。原因:二元判定任务的词边界影响执行稳定性——"找漏洞"判定空间收敛,"找风险"会把边界放宽,模型从"按标准答案判断"滑向"自由发挥"。落地为 `.claude/rules/semantic-trap.md`(窄边界约束随会话进上下文)。与"反口号"是同一件事两面:**语义陷阱控词的边界,反口号控句子的可执行性**。

## 代码 / 实现

**工程形态:Claude Code Plugin,"薄命令 + 厚 skill"**:

```
commands/evolve.md            ← 唯一显式 slash 命令(极薄,只做参数解析)
skills/
  skill-evolution-core/       ← 主流程:diagnose → patch → gate → write
  skill-evolution-memory/     ← 版本管理:快照/回滚/分支/timeline
  evolution-data-prep/        ← 数据准备:零散评测产物搬进标准目录
  verify-companion-template/  ← verify 层通用自检模板
```

靠 skill 的 description 自动激活("回滚到上一版"→ memory skill 触发),用户不用记命令。

**断点恢复**:每阶段更新 `.pending_round.json`;`session-start` hook 检测到后提示"上一轮卡在 gate 阶段,要不要继续?"——已跑完的 diagnose/patch 不重来。

**版本管理:文件系统就是数据库**(不引 SQLite,rsync/git/tar 天然友好):

```
<skill>/iterations/
├── current → v7/          # 软链,回滚=重指软链(原子操作,不覆盖历史)
├── v1/
│   ├── SKILL.md
│   ├── metrics.json       # F1/precision/recall/guardrail/holdout
│   ├── gate_verdict.json  # accepted|rejected|reverted + 原因
│   ├── patch.diff         # 相对上一版的 unified diff
│   └── provenance.json    # 谁、何时、基于什么 root_causes
├── edit_audit.log         # append-only:每次切换时间/from/to/原因(防静默回退失忆)
├── branches/exp-foo/      # 实验分支(taboo.json 软链共享)
└── taboo.json             # 历史被拒变更签名
```

写入按原子方式(`tmp → mv final`);timeline append-only 形成完整进化史。

**诊断规则与 gate 的 JSONL/阈值**见上文表格;真实 case 演示:28 万 token session 压成几千 token 摘要 → 命中 `progress_mismatch` + FN → 根因"调用链没追到 ServiceImpl 层" → 覆盖 38% 失败 case 触发进化 → 5 行 diff 修复 2 个 target case、28 个历史通过 case 无回归、质量分不降 → 写入 v3。

## 实践 / 应用

### 真实数据(63 case,同一 agent,不同 skill profile)

| 组 | Skill | 通过率 | 说明 |
| --- | --- | --- | --- |
| Kimi v1 → v2 | deepseek → evolution | 77.8% → 84.1% | 修复 10 个、新增 6 个错误 |
| GLM v1 → v2 | deepseek → evolution | 77.8% → **88.9%** | 修复 9 个、新增 2 个 |
| DeepSeek v2 → v3 | deepseek → evolution | 84.1% → 87.3% | 修复 6 个、新增 4 个 |

进化组最好成绩 88.9%(+11.1pp);平均 86.8% vs 基线 80.6%。**教训:总分会掩盖细节——"修复"和"回归"经常一起发生**,guardrail gate 就是拦逐 case 新错误、让 skill 变强不忘"旧账"。

### 七条贯穿全文的设计原则

1. **规则优先**:诊断/gate/GT 审计/语义陷阱检测都交给可复查规则(LLM 判断 skill 好坏稳定性不够);
2. **LLM 只做一件事**:把诊断结论转写成 SKILL.md 的 diff;
3. **防止变坏 > 追求变好**:guardrail 回归惩罚是 target 未改善的 3 倍多,四层 gate 一层不过就整体拒绝;
4. **小步快跑**:单次 patch ≤80 行(learning rate);
5. **记住每一次失败**:taboo 黑名单跨版本跨分支共享,回滚不清空;
6. **怀疑数据本身**:GT 审计承认标注也会错;
7. **极致解耦**:方法论与数据源解耦(只认 JSONL)、存储用文件系统、命令薄 skill 厚。

### 已知局限

- **不能创造新能力**:工具链缺能力(如没有调用链分析工具),patch 救不了;
- **诊断规则覆盖有限**:纯认知错误(流程完整、结论明确就是判断错)检测不到,归"未诊断";
- **依赖评测集质量与规模**:case 太少统计不稳(30% 阈值被噪声触发)、分布有偏会带偏方向;
- **收敛天花板**:F1 0.90+ 后剩 hard case,继续改 SKILL.md 边际递减,更依赖模型/工具/输入质量。

## 总结

1. **适用判据就一条**:输出能否被客观判定对错——收敛/二元结论才适合结果驱动自进化。
2. **不是 AI 自己教自己**:LLM 只把诊断转成候选 diff;诊断/验证/回滚/黑名单全用可复查规则——**用工程纪律约束 LLM 的不确定性**。
3. **四层 gate 防打地鼠**:Target(改了有用)/ Guardrail(没搞坏)/ Holdout(泛化没退步)/ Verify(手册质量),任何一层不过就拒绝。
4. **记住失败 + 怀疑数据**:taboo 黑名单跨版本跨分支共享;GT 审计不为错误标注改歪自己。
5. **小步快跑 + 极致解耦**:patch ≤80 行、文件系统即数据库、薄命令厚 skill;真实收益 77.8% → 88.9%。

**下一步学什么**:对比 [自进化 Agent 综述](../09-agent-research/self-evolving-agents-survey.md)(学术路线)与 [Self-Harness](../09-agent-research/self-harness-paper.md)(harness 自我改造);评测基础见 [Agent 评测](../03-agents/agent-evaluation.md) 与 [Skill 测评(OpenAI evals)](../07-agent-coding/skills/skill-evaluation.md)。

## 延伸阅读

- 站内:[Agent 效果优化实战(AgentLoop)](agent-effect-optimization-practice.md)(同阿里系评测驱动实战)、[自进化 Agent 综述](../09-agent-research/self-evolving-agents-survey.md)、[Self-Harness 论文解析](../09-agent-research/self-harness-paper.md)、[Skill 测评](../07-agent-coding/skills/skill-evaluation.md)、[评估驱动开发 EDD](../03-agents/agent-eval-driven-dev.md)、[Agent 评测](../03-agents/agent-evaluation.md)
- 外部:原文(https://mp.weixin.qq.com/s/h0ZsF5FdYZ_j5XrGmHBdXw);参考资料《别让大模型"想太多":SKILL 开发中的语义陷阱与抗幻觉设计》(https://sumsec.me/2026/skill-semantic-traps-anti-hallucination.html)
