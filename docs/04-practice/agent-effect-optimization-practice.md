# Agent 效果优化实战:3 天 7 步建立"观测→评估→优化"闭环(阿里云 AgentLoop)

> **一句话摘要**:Agent 的"自述"不可信,只有"轨迹"可信。本文以阿里云 AgentLoop 在 UGC 游戏平台的真实落地为例,拆解一套 3 天跑通的 Agent 效果优化闭环——观测取证 → 分层评估(通用/事实/玩法)→ 根因定位 → 优化回写 → 数据集回归 → 常态化监控,并给出评估器设计规范、Skill 护栏四特征、避坑清单与可复用的评估器 Prompt 骨架。
>
> **来源**:阿里云云原生《3天7个步骤,基于 AgentLoop 的游戏 Agent 效果优化实践》(https://mp.weixin.qq.com/s/VOB7IHobrWnmmyS5FDoHGA);平台:阿里云 AgentLoop

## 概念

### 问题:Demo 很惊艳,线上很难受

UGC 游戏平台把 Coding Agent 接进创作链路后,常见现象:用户一句"做一个射击类生存 100 天玩法",Agent 写几千行 Lua、调几十次工具,最后回一句 "All done"——但玩家进去发现枪发了、怪刷了、HUD 也有,**就是没有地面**(Agent 压根没搭场景,自述里只字未提)。

这类问题的共性是:**Agent 的"自述"不可信,只有"轨迹"可信**。卡住团队的三个原因:没有可取证的轨迹、没有能对齐业务的评估标准、没有能回归验证的数据集。于是优化全靠人肉试,改完不知道好没好、好了不知道为什么好。

### 核心路径:7 步闭环

```
观测取证 → 分层评估 → 根因定位 → 优化回写 → 数据集回归 → 常态化监控
```

实战用 3 天完成首轮闭环,抓出 5 个以上生产环境代码生成 Bug 与 API 文档缺陷。

### 分层评估:不要混在一起评一个总分

Agent 质量不是一个维度,混在一起评只会得到"解释不了也优化不了的总分"。先做两层,确定性最高、收益最直接:

| 层 | 回答的问题 | 手段 | 节奏 |
| --- | --- | --- | --- |
| **通用层** | Agent 干活顺不顺(执行健康度) | 平台内置评估器:工具调用成功率、工具选择合理性 | 当天出结果 |
| **事实层** | 代码写得对不对(API 调用是否遵循事实依据) | 自定义 Agent Judge,挂载 API 参考 Skill | 收益最大,第二天上线 |
| **玩法层** | 做出来的东西是不是用户想要的 | 不预设玩法的动态需求抽取评估 | 前两层跑稳后再做 |

实战中,第一天靠内置"工具调用成功率"评估器在测试+生产双环境抓到工具调用失败(通过专家二次复核,让业务侧相信方法有效);第二天上线的 API 事实性评估器在生产环境挖出 5+ 代码生成 Bug 与文档缺陷。

## 原理(七步拆解)

### 第 1 步:观测接入——目标不是"看到数据",是"能取证"

架构:游戏客户端 - Go 网关 - Agent 运行时(如 Claude Code) - 外部依赖(模型/工具/知识库)。两条接入路:

- **Hook 接入(LoongSuite Pilot,推荐首日)**:一行命令安装配置,不改 Agent 代码;参数 `--service-name-prefix` 一开始就把**环境和角色编进前缀**(`ai-coding-agent-dev` / `ai-coding-agent-prod`),决定后面评估过滤条件好不好写;
- **语言探针接入(Node.js,需要业务埋点时)**:`npm install @loongsuite/cms_node_sdk` + 环境变量 + `node -r @loongsuite/cms_node_sdk/register app.js`;需要在 Span 加业务属性(关卡 ID、玩法类型、创作会话来源)或做跨进程标签透传时必须走探针。

实战节奏:Day 1 Hook 快速打通验证价值 → Day 2 切探针;多环境是刚需(测试+海外生产按环境拆分应用名)。

**验收标准**:打开链路追踪点开 Trace,检查——基础指标(Agents 数、输入/输出 Token、缓存命中率、LLM/工具调用次数、TTFT)、推理轨迹页签(能按 System/User/Assistant/Tool 顺序展开完整消息流,每个 `[tool_call]` 能看到 args 与工具返回值)。真实样例:一条"复刻灾难模拟器"会话,总 Token 1,367,194,输入占比 99.5%、缓存命中 82%——这本身就是成本优化输入(上下文工程还有空间)。

### 第 2 步:评估器设计——通用层打底,事实层攻坚

评估器是整套方法的核心资产。AgentLoop 支持预置评估器 + 自定义评估器;自定义又分两种:

- **LLM Judge**:一段评分 Prompt,一眼能看出对错的场景;
- **Agent Judge**:评分 Prompt + 挂载 Skills / MCP,**评委可以按流程取证再判分**——需要"动手查手册"才能定论的场景必须用它。UGC 游戏 API 事实层评估必须是 Agent Judge。

**通用层**:零成本起步,勾选内置评估器即可。先上"工具调用成功率 + 工具选择合理性"两个,指标掉了说明问题在工具层/Skill 层,与玩法无关,修起来最快。真实输出示例(成功率 0.9,45 次调用 3 次失败)揭示三类失败模式:文档索引缺失、参数序列化规范缺失、工具选择不当——**每条都能变成 Skill 里的防错护栏**。

**事实层(API 事实性评估器,投入产出比最高)**:UGC 脚本 API 几百个模块,Agent 幻觉最集中在 API 调用(参数顺序记错、服务模块函数当实例方法调、编造方法名)。设计要点是**把"唯一事实依据"钉死**——评估器 Prompt 开头明确:唯一 API 事实依据是 `ugc-api-reference-skill`,评测时必须完整读 SKILL.md 再按查阅纪律只读对应 reference 文件;禁止用模型记忆/函数名相似性/其他引擎经验/常识推断/Agent 自述替代 Skill 证据。配置对应三件事:参考变量(input/output/agent_trajectory 必填)、能力挂载(挂 `ugc-api-reference-skill`,这是 Agent Judge 与 LLM Judge 的分水岭)、计分方式(比率型 `score = 正确项/(正确项+错误项)`,无法核验项不计入分母)。

实战产出:一条"还原复刻灾难模拟器"请求评估 0.4 分——16 项检查:正确 5、错误 9、无法核验 2,错误明细全部带证据文件定位。**"无法核验"项恰恰是 API 文档体系的缺口**(框架方法在 bindings 提及但 reference 无独立定义)——评估器同时在评测 Agent、也在体检 API 文档,把"Agent 老出错"的锅拆成两部分分别认领。

**评估器 Prompt 六段式规范**(顺序固定):

1. 角色定义:一句话"客观、精准、严格的某领域评测专家";
2. (可选)前置提取步骤:需要动态基准时,先从轨迹提取再打分;
3. 评估维度:逐条列出审查点与判断标准,多维标注权重;
4. 评分标准:计分公式、精度、边界情况(无工具调用/幻觉/外部中断各给什么分);
5. 评估内容:只放真正参与打分的占位符,每个前加中文标签;
6. 输出要求+示例:强约束只输出合法 JSON(`score` 浮点 + `explanation` 字符串),禁 Markdown 围栏和问候语。

**硬约束**(违反则评估器报废):占位符必须来自平台字段白名单(不能凭空造 `{{ground_truth}}`);结果与过程分离(`{{output}}` 判结果、`{{agent_trajectory}}` 判流程约束);`explanation` 必须可复核(写清检查几项/各子分/扣分原因/加权公式,这是人工抽检和申诉的唯一依据);权重要能分摊(维度不适用时按比例分摊,否则总分被系统性拉低)。

### 第 3 步:跑评估任务——采样策略比评估器更影响成本

四个参数直接决定成本与有效性:采样比例、最大样本数、过滤条件、评估器组合。日常只看 0.8 以下那档(低分主战场);按 `experimentId` 过滤做版本对比;明细点 traceId **秒级跳到调用链分析页**——"从分数到证据"的关键动作,务必让业务同学养成习惯;分组视图聚合同一样本下所有评估器结果。

### 第 4 步:从低分到根因——三级取证链

拿到 0.4 分不能直接改 Prompt,固定走三级取证:

1. **读评估理由,定位问题类型**:先分类——参数顺序错/方法不存在/调用形态错(模块函数 vs 实例方法 vs 组件方法)/缺参数;
2. **回轨迹看现场**:点 traceId,在推理轨迹页按关键词定位具体 `[tool_call]`,确认 Agent 当时拿到什么上下文、工具返回什么——**区分"Agent 判断错了"还是"Agent 拿到的信息本来就是错的"**;
3. **回官方 API 文档核对**:经常有意外收获——评估器标记的"无法核验"项,回溯确认是文档缺少独立定义而非 Agent 幻觉。

### 第 5 步:优化回写——把根因变成 Skill 护栏

每个低分样本归到根因后,回写成**最小防错规则**(护栏)。实战示例——背包发放接口的护栏(前置槽位校验 + 路由表 + 回读验证 + 诚实声明):

```lua
-- ① 前置槽位校验:信息不全就不许写调用(硬规则,源头掐掉猜测)
if not config.item_id or not config.count then
    return {ok = false, reason = "缺少 item_id/count"}
end

-- ② 路由表:语义请求("发到背包" vs "放到地上")→ 确定 reference 文件,杜绝凭记忆选 API
local route = route_table[config.destination]  -- 只从 API reference 派生

-- ③ 回读验证:保留返回 ID 并二次读取确认("声称成功" → "可验证成功")
local result = grant_item(player_id, config)
local verify = read_back(result.record_id)

-- ④ 诚实声明:无法验证时写明"仅完成配置,未验证",打掉虚报
if not verify.ok then return {ok = true, note = "仅完成配置,未验证"} end
```

护栏设计四特征(可复用):前置槽位校验、路由表、回读验证、诚实声明。**回写纪律**:只改 Skill 护栏部分,不改自动生成的 references;每次回写后跑 Skill 库校验(0 errors / 0 warnings);API 事实与对应 reference 逐项核对过再写。推进节奏按"低分密度"排序模块,每个模块走:低分样本 → 可验证根因 → 最小防错规则 → 下一次评估回归。

### 第 6 步:BadCase 数据集与实验回归——证明"确实变好了"

**构建 BadCase 数据集**:字段至少含 input / output / score_value / explanation(可扩展自定义 Schema + SQL 查询 + 批量上传 + 标注管理)。**强烈建议加 tag 语义标注**——不加标注会把所有样本送进所有评估器,产生大量无效评估(用 API 评估器评纯咨询问答纯属烧钱);按语义标注路由到不同数据集是控成本关键动作。**第一版不用大**(实战首批只有 3 条:0 / 0.4 / 0.5 照样跑通闭环)——价值在代表性,不在规模。

**SDK 离线实验**(接自己 Agent 服务做灰度回归):

```python
from agentloop_sdk import (AgentLoopBenchmark, AgentLoopConfig,
    AgentLoopEvaluatorStorage, GeneralEvaluator, SolutionOutput, Task)

config = AgentLoopConfig(workspace="<你的工作空间>", dataset="api_badcase", region_id="cn-hangzhou")

async def agent_solution(task: Task, pre_hook) -> SolutionOutput:
    output = await call_your_agent(task.input)   # task.input 是数据集一行
    return SolutionOutput(success=True, output=output,
        trajectory=[],        # 有轨迹务必回传,评估器要靠它取证
        meta={"task": task.input})

storage = AgentLoopEvaluatorStorage(save_dir="./results", config=config,
    experiment_name="api-skill-guardrail-v2", experiment_type="agent",
    experiment_config={"agent_name": "ugc-coding-agent"})
evaluator = GeneralEvaluator(name="BadCase Regression",
    benchmark=AgentLoopBenchmark(config=config, name="badcase"),
    n_repeat=1, storage=storage, n_workers=4)
await evaluator.run(agent_solution)
```

**关键动作:透传 experiment_id**——实验发起时通过 Context 透传到 Agent 轨迹,评估阶段再从轨迹提取记录进结果,才能做优化前后对比(评估结果页过滤、仪表盘按实验聚合、对比分析设 Baseline 逐条比对)。**另一个实操建议:实验开始前每道题新建独立 session**,避免多条样本共用会话导致上下文污染、评估结果失真。

### 第 7 步:仪表盘与告警——从项目制走向常态化

前六步是一次成功的攻坚,这一步才是可持续的机制。仪表盘至少三块:

1. **线上效果盘**:各评估器分数趋势、低分样本数、按模块(特效/背包/UI/生物)分数分布;
2. **变更验证盘**:按 experiment_id 聚合,展示每次 Skill 回写 / Prompt 变更前后对比;
3. **成本盘**:Token 消耗、缓存命中率,避免成本黑洞。

告警至少配:工具调用成功率跌破阈值、API 事实性评估周均分下滑、单会话 Token 异常上涨。

## 代码 / 实现

**观测接入(Hook,一行命令)**:

```bash
curl -fsSL https://aliyun-observability-release-cn-shanghai.oss-cn-shanghai.aliyuncs.com/loongsuite-pilot/installer.sh \
  -o /tmp/loongsuite-pilot-installer.sh && bash /tmp/loongsuite-pilot-installer.sh install \
  --collect-log "true" --collect-trace "true" \
  --sls-project "agentloop-xxx" --sls-logstore "agent-event-webtracking" \
  --sls-endpoint "cn-hongkong.log.aliyuncs.com" \
  --cms-license-key "xxx" --cms-endpoint "<接入中心获取的 Endpoint>" \
  --cms-workspace "default-cms-xxx-cn-hongkong" \
  --service-name-prefix "ai-coding-agent"    # ⚠️ 一开始就把环境/角色编进前缀
```

**API 事实性评估器骨架**(附录 A,可直接改用)——六段式 + 唯一事实依据 + 比率计分 + JSON 输出,核心见上文"六段式规范";完整 Prompt 存于原文附录(`docs/inbox/agent-effect-optimization-source.md`)。

**评估任务与实验**:评估任务参数(采样比例/最大样本/过滤/评估器组合)决定成本;SDK 离线实验代码见上;`pip install agentloop-sdk`。

## 实践 / 应用

### 三天落地节奏表

| 天 | 目标 | 关键动作 |
| --- | --- | --- |
| Day 1 | 观测打通 + 通用层评估 | Hook 接入,勾选"工具调用成功率 + 工具选择合理性",测试+生产双环境出第一份带证据结果 |
| Day 2 | 事实层评估器上线 | 建 API 事实性评估器(Agent Judge 挂 `ugc-api-reference-skill`),生产环境跑出 5+ Bug/文档缺陷 |
| Day 3 | 根因→护栏→回归 | 三级取证定位根因,回写 Skill 护栏,BadCase 数据集(3 条)+ SDK 实验回归,搭仪表盘雏形 |

### 实战收益(脱敏)

- **质量**:API 评估器上线后生产环境发现 5+ 代码生成 Bug/API 文档问题(同类错误批量存在,人工抽检几乎不可能全发现);单条样本 16 项 API 检查查 9 项错误,每项定位到函数签名与证据文件,可直接转研发工单;玩法层先导验证识别出"声称完成、轨迹无证据"(做生存 100 天但没搭可站立场景);
- **效率**:从"人工试玩找问题"变"自动打分+证据定位",单条样本评估 3 分钟出结论且带完整推理链;回归从"不可做"变"快速验证";
- **机制(最长期)**:建立"低分样本 → 可验证根因 → 最小防错规则 → 下一次评估回归"标准动作,优化不再依赖个人经验;评估器同时体检 API 文档;观测数据暴露成本优化空间(输入 Token 99.5%、缓存 82%)。

### 实战避坑清单(9 条)

1. **别用 output 判分**——Agent 自述倾向乐观,一切结论以轨迹证据为准(写进每个评估器铁则);
2. **别给用户没要求的功能扣分**——用户没提"难度递增"缺了不扣分、Agent 主动创新也不扣分,否则分数系统性偏低、创意被压制;
3. **别在评估器里硬编码工具名**——按语义匹配,平台工具名会变;
4. **别跳过语义标注**——不做数据集路由,不相关样本送进 Agent Judge 产生大量无效评估;
5. **别忘了透传 experiment_id**——不透传没法做优化前后对比,实验白跑;
6. **别在实验里复用 session**——每道题新建 session,避免上下文污染;
7. **别只改 Prompt**——根因多在 Skill 与 API 文档,改 Prompt 是治标且会越来越长、规则打架;
8. **长会话要单独验采集**——20 分钟以上会话轨迹容易缺失,接入后专门验一次;
9. **fork 起子进程要处理上下文透传**——否则轨迹断裂,评估器取不到证据。

### 玩法层评估展望(设计原则)

问题:通用层解决"干活顺不顺",事实层解决"写得对不对",但"是不是玩家想要的东西"没覆盖(枪怪计分氛围都做了,唯独没有可站立场景——工具全成功、API 没错,唯独东西不对)。

**错误做法**:列一张平台主流玩法清单,每种配固定 Rubric——UGC 玩法是玩家想出来的,清单写死会把玩家新发明系统性判低分,Agent 也会迎合评分收敛到标准形态,**评估器成了创意的天花板**。

**正确原则**:评估器不预设任何玩法,需求清单每次从用户输入动态抽取,只判断"用户要的有没有正确做出来"。玩法无关五维度:**需求覆盖度**(有没有漏)、**可运行与可进入**(玩家能不能玩到)、**被请求功能实现正确性**(做的是不是用户说的那个意思)、**反馈可见性**(要求的状态玩家能不能看到,形式不限)、**表达达成度**(氛围风格方向是否一致)。设计纪律:只对用户显式要求计分(没提的独立玩法缺失不扣分、主动创新不扣分);一切以轨迹证据为准(output 声称但轨迹无证据按未完成);不评审美不评好玩程度("关卡不好玩"不是可优化信号,"用户要的传送门没做"才是);玩法专属判据只能作为可选插件细化"某项要求怎样算做对",绝不能不匹配就降分或拒评。推进节奏:等通用层/事实层被业务认可、BadCase 数据集积累到一定规模后再启动,先有一批人工标注样本校准评委。

## 总结

1. **自述不可信,轨迹可信**:评估的铁则是以轨迹证据为准,output 声称无轨迹证据一律按未完成处理。
2. **分层评估,不要总分**:通用层(执行健康度,内置评估器零成本)→ 事实层(API 正确性,Agent Judge 挂 Skill 手册,投入产出比最高)→ 玩法层(需求达成,不预设玩法动态抽取)。
3. **评估器质量决定方法上限**:六段式 Prompt + 占位符白名单 + 结果过程分离 + explanation 可复核 + 权重分摊;"唯一事实依据"钉死幻觉。
4. **优化回写 Skill 护栏,不是改 Prompt**:前置槽位校验/路由表/回读验证/诚实声明四特征,只改护栏不改 references,按低分密度排模块逐个回归。
5. **机制化收尾**:BadCase 数据集(代表性>规模)+ tag 语义标注路由控成本 + experiment_id 透传做对比 + 仪表盘/告警常态化;避坑清单 9 条可直接照抄。

**下一步学什么**:对比站内 [Agent 评测](../03-agents/agent-evaluation.md)(评测方法论)与 [评估驱动开发(EDD)](../03-agents/agent-eval-driven-dev.md)(traces 金矿/验证器);同平台实战见 [Agent 安全审计实战(AgentLoop)](agent-security-audit-practice.md);想落地可直接复用附录 A 评估器 Prompt 骨架与附录 B 验收清单。

## 延伸阅读

- 站内:[Agent 安全审计实战(阿里云 AgentLoop)](agent-security-audit-practice.md)、[Agent 评测方法论](../03-agents/agent-evaluation.md)、[评估驱动开发 EDD](../03-agents/agent-eval-driven-dev.md)、[Agent 性能剖析](../03-agents/agent-performance-analysis.md)、[推理时验证设计范式](../03-agents/agent-test-time-verification.md)、[企业 Agent 工程化(四):Tool/MCP/Skills/Harness](../06-enterprise/ontology-agent-adoption/enterprise-agent-tooling-harness.md)
- 外部:原文《3天7个步骤,基于 AgentLoop 的游戏 Agent 效果优化实践》(https://mp.weixin.qq.com/s/VOB7IHobrWnmmyS5FDoHGA);阿里云 AgentLoop 文档(https://help.aliyun.com/zh/document_detail/3033878.html)
