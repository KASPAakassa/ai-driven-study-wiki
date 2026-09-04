> 原文存档:微信文章《3天7个步骤,基于 AgentLoop 的游戏 Agent 效果优化实践》(公众号:阿里云云原生)
> 原始链接:https://mp.weixin.qq.com/s/VOB7IHobrWnmmyS5FDoHGA
> 抓取日期:2026-08-11(手机 UA curl,避开微信环境验证)
> 用途:整理收件箱素材(用户标注:agent 实战经验),正文原样保留供追溯。

---



***写在前面***

*Cloud Native*

UGC 游戏平台把 Coding Agent 接进创作链路之后，通常会经历同一个阶段：Demo 很惊艳，线上很难受。用户一句"给我做一个射击类的生存 100 天玩法"，Agent 洋洋洒洒写几千行 Lua、调几十次工具，最后回一句"All done"。但玩家进去发现枪发了、怪刷了、HUD 也有，就是没有地面——Agent 压根没搭场景，而它的自述里对此只字未提。

这类问题的共性是：Agent 的"自述"不可信，只有"轨迹"可信。而绝大多数团队卡在这里的原因也很一致——没有可取证的轨迹，没有能对齐业务的评估标准，没有能回归验证的数据集。于是优化全靠人肉试，改完不知道好没好，好了不知道为什么好。

这篇指南给出的是一条已经跑通的路径：观测取证 → 分层评估 → 根因定位 → 优化回写 → 数据集回归 → 常态化监控。这条路径在实战中用 3 天完成了首轮闭环，抓出了 5 个以上生产环境的代码生成 Bug 与 API 文档缺陷。下面按步骤拆开讲，每一步都给验收标准和踩过的坑。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/bvDbzNRia8j2KM3J3UKQoXjmKXM4kym40mYfqicBCMwSmicASY5rd1xTJoeagkGVqAZmnwhWYP9ZHv5icQU42pegSnsEtqqAU3Vk2ibLGR0IQ4Wc/640?wx_fmt=png&from=appmsg)

******

***再动手接数据***

*Cloud Native*

这是最容易被跳过、也最致命的一步。UGC 游戏 Agent 的质量问题不是一个维度，混在一起评就会得到一个既解释不了也优化不了的总分。落地阶段建议先做两层，把确定性最高、收益最直接的部分拿下。

![](https://mmbiz.qpic.cn/mmbiz_png/bvDbzNRia8j1yjshN2LNjW2I1au3ib7o51YhPE91640HlYqNTPG9AUVXCxPkQicToTqvhB3DPvib5By0kAjHdDVZ8klmjCibwE9ldNwg4t2s8VRU/640?wx_fmt=png&from=appmsg)

通用层先上（当天就能出结果），事实层紧跟（收益最大）。实战中第一天就是靠内置的"工具调用成功率"评估器，在测试环境和生产环境同时抓到了工具调用失败问题，且通过了专家二次复核——这是让业务侧相信这套方法有效的第一个抓手。第二天上线的 API 事实性评估器，则直接在生产环境挖出 5 个以上代码生成 Bug 与 API 文档缺陷。

还有一层是"玩法层"——判断做出来的东西是不是用户想要的那个东西。这一层价值很大，但风险同样大：UGC 平台的玩法是玩家想出来的，不是我们列出来的。评估标准一旦写死，就会变成创意的天花板。所以我们把它放在通用层与事实层跑稳之后再做，本文末尾会简单展开思路。

***第 1 步：观测接入——***

***目标不是“看到数据”，是“能取证”***

*Cloud Native*

### ▍**1.1 选接入方式**

UGC 游戏场景的 Agent 架构通常分为游戏客户端 - Go 网关 - Agent 运行时（如 Claude Code） - 外部依赖（模型、工具、知识库等），接入方式有两条路：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/bvDbzNRia8j2blNibqrV5SB4TGFy8q9XGC8ldAwCZmuJbebz7acUSERbUGcw53dw9lmk4MGJ9ZQ9icT2iafKJfiawfo1lA8VQP5qiapIZ0vqyz4IY/640?wx_fmt=png&from=appmsg)

实战节奏是：Day 1 用 Hook 快速把链路打通验证价值，Day 2 按需切换成探针接入。切换后通过 Node.js 探针完成了 Coding Agent 的接入，LLM 调用、Tool 调用、RAG 召回三类数据均验证无问题。

#### 方式一：LoongSuite Pilot Hook（推荐用于首日接入）

一条命令完成安装与配置，无需改动 Agent 代码：

-
-
-
-
-
-
-
-
-
-

```
curl -fsSL https://aliyun-observability-release-cn-shanghai.oss-cn-shanghai.aliyuncs.com/loongsuite-pilot/installer.sh -o /tmp/loongsuite-pilot-installer.sh && bash /tmp/loongsuite-pilot-installer.sh install \  --collect-log "true" \  --collect-trace "true" \  --sls-project "agentloop-xxx" \  --sls-logstore "agent-event-webtracking" \  --sls-endpoint "cn-hongkong.log.aliyuncs.com" \  --cms-license-key "xxx" \  --cms-endpoint "https://proj-xtrace-xxx-cn-hongkong.cn-hongkong.log.aliyuncs.com/apm/trace/opentelemetry" \  --cms-workspace "default-cms-xxx-cn-hongkong" \  --service-name-prefix "ai-coding-agent"
```

参数取值都能在接入中心对应卡片里拿到，完整说明见官方文档：https://help.aliyun.com/zh/document_detail/3033878.html

只强调一个参数：--service-name-prefix 决定了后面评估任务过滤条件好不好写。一开始就把环境和角色编进前缀里（如 ai-coding-agent-dev / ai-coding-agent-prod），比上线后再回来改省事得多。

#### 方式二：语言探针接入（需要业务埋点时）

以 Node.js 运行时为例，两步完成。

第一步，安装依赖包：

-

```
npm install @loongsuite/cms_node_sdk
```

第二步，配置环境变量并以探针方式启动应用：

-
-
-
-
-
-

```
export ARMS_LICENSE=<接入中心获取的 License>export CMS_SERVICE_NAME=ugc-agent-dev        # 服务名，建议区分 dev / prodexport ARMS_REGION_ID=cn-hongkong            # 与工作空间同地域# 如果是默认 workspace，则不需要设置export ARMS_WORKSPACE=default-cms-xxx-cn-hongkongnode -r @loongsuite/cms_node_sdk/register app.js
```

需要在 Span 里加业务属性（关卡 ID、玩法类型、创作会话来源等）时必须走这条路。前面提到的跨进程标签透传，也只有探针方式能彻底解决。

多环境是刚需。这个项目同时接了测试环境和海外生产环境，建议一开始就按环境拆分智能体空间或应用名，否则后面评估任务的过滤条件会比较麻烦。

### ▍**1.2 验收标准**

打开 AI Agent 可观测 → 链路追踪，随便点开一条 Trace，检查以下几项是否齐全：

-

基础指标：Agents 数、总 Token / 输入 Token / 输出 Token、缓存命中率、LLM 调用次数、工具调用次数、TTFT 等。

-

推理轨迹页签：能按 System / User / Assistant / Tool 顺序展开完整消息流，且每个 [tool_call] 能看到 args 与工具返回值。

真实样例给个参照：一条"复刻灾难模拟器"的会话，耗时 2 分 1 秒，Agents 数 1，总 Token 1,367,194（输入 1,360,361 / 输出 6,833），缓存命中率 82%，LLM 调用 11 次，工具调用 14 次。输入 Token 占比 99.5%、缓存命中 82%——这个数据本身就是成本优化的重要输入，说明上下文工程还有很大空间。

***第 2 步：评估器设计***

***——通用层打底，事实层攻坚***

*Cloud Native*

评估器是整套方法的核心资产。AgentLoop 支持预置评估器和自定义评估器，自定义评估器又分两种形态：纯 LLM Judge（一段评分 Prompt），以及 Agent Judge（评分 Prompt + 挂载 Skills / MCP，评委可以按流程取证再判分）。

判断口诀：能一眼看出对错的用 LLM Judge，需要"动手查手册"才能定论的用 Agent Judge。UGC 游戏的 API 事实层评估，必须用 Agent Judge。

### ▍**2.1 通用层：先把平台内置的通用评估器用透**

这一层的核心价值是"零成本起步"——不需要写任何 Prompt，新建评估任务时直接勾选内置评估器即可，当天就能出第一份带证据的评估结果。UGC 游戏场景建议按下面的优先级来选：

![](https://mmbiz.qpic.cn/mmbiz_png/bvDbzNRia8j2dOQ9yJFXLGoIEKKtnJwicYpiaN1SJqq0gafJ8TnJNR1HaySChS5rff8RwXGfA3Cuoh6fb2LUOeRXzEN7AZptx50sSlc6xEpAwI/640?wx_fmt=png&from=appmsg)

这一层不要贪多，先上"工具调用成功率 + 工具选择合理性"两个，把 Agent 的执行健康度摸清楚。这两个指标掉下来，说明问题在工具层和 Skill 层，跟玩法设计无关，修起来最快、收益最直接。

真实输出示例（脱敏后），工具调用成功率给出 0.9：

#

Agent 共进行了约 45 次工具调用。其中 3 次调用失败：1 次尝试读取不存在的参考文档；2 次在设置属性时因参数格式错误（未正确包裹 JSON 字符串）导致报错，但 Agent 随后修正并成功执行；1 次尝试通过命令行直接注入 Lua 代码失败，后改用 run-lua 成功。其余所有 Skill、CLI 命令、API 查询及文件操作均成功返回预期结果。成功率约为 42/45，得分 0.9。

这段理由的价值在于：它不只给了 0.9，还告诉你三类失败模式——文档索引缺失、参数序列化规范缺失、工具选择不当。这三条后面全都能变成 Skill 里的防错护栏。

### ▍**2.2 事实层：API 事实性评估器——投入产出比最高的一个**

这是整个项目里价值最大的评估器。UGC 平台的脚本 API 有几百个模块，Agent 幻觉最集中的地方就是 API 调用：参数顺序记错、把服务模块函数当实例方法调、直接编一个不存在的方法名。

设计要点是把"唯一事实依据"钉死。评估器 Prompt 的开头必须明确：

#

你是一个客观、严格的 UGC 脚本 API 事实性评测专家。你的任务是根据用户的原始指令和 Agent 的完整执行轨迹，评估 Agent 在轨迹中生成、修改、解释或执行的代码是否严格遵循 ugc-api-reference-skill 中记录的 API 定义。

唯一事实依据：可使用的 API 查询 Skill 是 ugc-api-reference-skill。评测时必须完整读取该 Skill 的 SKILL.md，再按照其中的查阅纪律，只读取与待检查 API 对应的 reference 文件。

ugc-api-reference-skill 及其 references 是本次评测的唯一 API 事实依据。禁止使用模型记忆、函数名相似性、其他游戏引擎经验、常识推断或 Agent 自己的说法替代 Skill 证据。Skill 中未明确支持的事实不得判为正确；Skill 中已有明确定义的事实不得被外部说法推翻。

配置上对应三件事：

1. 参考变量：平台提供多个对话/会话轨迹变量。这个评估器只需要把 input（用户输入内容）、output（最终内容）和 agent_trajectory（Agent 工具调用轨迹）设为必填即可。

2. 能力挂载：在评估器的"能力挂载"里挂上 ugc-api-reference-skill。这是 Agent Judge 与 LLM Judge 的分水岭——评委在打分时会真的去读 Skill 手册。

3. 计分方式：比率型，score = 正确项 / (正确项 + 错误项)，"无法核验"项不计入分母，保留一位小数。

实战产出：对一条"参考某平台的灾难模拟器玩法，给我还原复刻一个"的请求，评估得分 0.4。评委共检查 16 项：正确 5 项、错误 9 项、无法核验 2 项。错误明细全部带证据文件定位（原文涉及代码细节，不在此列出）。

注意最后那两项"无法核验"：self:xxx / DoXXX 属于框架方法，Skill 的 bindings 里提及但 API reference 中没有独立定义。这类"无法核验"项恰恰是 API 文档体系的缺口，它不是 Agent 的错，是文档的错——这也是这个评估器的额外收益：它同时在评测 Agent，也在体检你的 API 文档。

### ▍**2.3 写评估器的通用规范**

不管是内置评估器的微调还是自定义评估器，Prompt 都建议按六段式组装，顺序固定：

1. 角色定义：一句话设定为"客观、精准、严格的某领域评测专家"。

2.（可选）前置提取步骤：需要动态基准时，显式要求模型先从轨迹里提取再打分。

3. 评估维度：逐条列出审查点与判断标准，多维时标注权重。

4. 评分标准：计分公式、精度、边界情况（无工具调用 / 幻觉 / 外部中断各给什么分）。

5. 评估内容：只放真正参与打分的占位符，每个前面加中文标签。

6. 输出要求 + 示例：强约束只输出合法 JSON（score 浮点 + explanation 字符串），禁止 Markdown 代码围栏和问候语。

几个硬约束，违反了评估器直接报废：

-

占位符必须来自平台字段白名单，不能凭空造 {{reference}}、{{ground_truth}} 这类字段，否则字段映射做不了。缺基准就用"前置提取步骤"从 {{agent_trajectory}} 现场抽。

-

结果与过程分离：判断"结果达成"用 {{output}}，判断"流程与约束遵守"用 {{agent_trajectory}}，在 Prompt 里写清每个维度的证据来源。

-

explanation 必须可复核：要求模型写出计算过程（检查几项、各子分、扣分原因、加权公式），这是人工抽检和申诉的唯一依据。

-

权重要能分摊：某维度不适用时，权重按比例分摊给生效维度，否则总分被系统性拉低。

AgentLoop 平台内置了模板库（当前 18 个模板），冷启动阶段建议先套模板再改，不要从零写。

***第 3 步：跑评估任务***

***——采样策略比评估器更影响成本***

*Cloud Native*

评估器建好后，去"评估 → 评估任务 → 新建评估任务"配置。有四个参数直接决定成本和有效性：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/bvDbzNRia8j0xSw3mYehqReHfyplFicdnEiawSlURyMTgBwd1F8ric6gNZTIFGyIv7lPuQYtXxpYrR2TyrqEkpNUSfXiaZWnuAfFIYLoVcaIgUPg/640?wx_fmt=png&from=appmsg)

-

评估结果页支持按分数区间筛选（0~1，0.1 精度）。日常只看 0.8 以下的那一档，这是 Bad Case 的主战场。

-

高级筛选支持 traceId / spanId / sessionId、experimentId / datasetId等。做版本对比时靠 experimentId 过滤。

-

明细里点 traceId 可以秒级跳到调用链分析页，这是"从分数到证据"的关键动作，务必让业务同学养成习惯。

-

分组视图能把同一条样本下所有评估器的结果聚合，一眼看出这条 Trace 在"工具调用成功率"和"API 正确性"上的综合表现。

***第 4 步：从低分到根因***

***——建立三级取证链***

*Cloud Native*

拿到一个 0.4 分，不能直接去改 Prompt。UGC 游戏场景我们固定走三级取证：

第一级：读评估理由，定位问题类型。评估器给的 explanation 和评估过程已经把错误项、证据文件、错误类型列清楚了。先分类：是参数顺序错、方法不存在、调用形态错（模块函数 vs 实例方法 vs 组件方法），还是缺参数。

第二级：回轨迹看现场。点 traceId 跳到调用链，切到"推理轨迹"页签，按关键词搜索定位到具体的 [toolcall]，确认 Agent 当时拿到的上下文是什么、工具返回了什么。这一步是为了区分"Agent 判断错了"还是"Agent 拿到的信息本来就是错的"。

第三级：回官方 API 文档核对。打开平台的脚本 API Wiki，核对事件参数表和函数签名。这一步经常有意外收获——实战中就是在这一级发现了 API 文档本身的问题，评估器标记的"无法核验"项，回溯后确认是文档缺少独立定义，而不是 Agent 幻觉。

三级走完，每个低分样本都会归到三类根因之一：

![](https://mmbiz.qpic.cn/mmbiz_png/bvDbzNRia8j3tXE6XoMfL2zT3c9Sdqc7EV2VWfbNOdOIyLDibp5icpDQNSOLFkkPgb0icXmlNzJhJeMQ0lP03h5IiciahAR3mKCneYb3dAVtMyHw8/640?wx_fmt=png&from=appmsg)

实战中 9 个错误项里绝大多数根因在 Skill 与文档，改 Prompt 是治标。

***第 5 步：优化回写——***

***让评估结论变成 Skill 里的放错护栏***

*Cloud Native*

这是"Agent Loop"真正闭环的地方，也是最容易被忽略的一步。做法是：把低分样本的根因，反向写成 API Skill 里的最小防错规则。

实战中的第一个试点模块选的是"运行时发放道具/枪械"，因为这个模块有一条 0 分样本："开局给我生成一把枪，然后放到我的背包里面"。Agent 用了世界掉落物 API 来回答"放进背包"，玩家背包里根本不会出现枪。

回写进 SKILL.md 的护栏长这样（参考样例，代码函数已脱敏）：

-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-

```
## 评估回写：运行时发放道具/枪械适用「开局脚本给我一把枪」「把道具发到玩家背包/快捷栏」等运行时请求。先填下列三槽，任一槽为空不得写调用：玩家 UIN、道具 ID、落点类型（背包实例 / 地面掉落 / 玩家模板初始背包）。1. 「出生自带 / 初始背包」不是运行时 API：转 ....，   不要用脚本 API 假装已配置。2. 「运行中放入背包」读 api-xxx.md；普通道具实例或枪械实例再读 api-yyy.md。   玩家 ID 来源不明时先读 player-id-xx.md。3. 「放到地上 / 玩家旁可拾取」是世界掉落物，读 api-yyy.md；   不得用 XXX 回答「放进背包」。4. 枪械必须选「创建枪械」相关 API，并保留返回的 instId；   AddItem 的返回数量不是枪械实例 ID。5. 验收只能在运行模式或真实玩家 UIN 下声明成功；无法进入运行模式时   明确写「仅完成源码/API 配置，未验证实际背包」。### 已知陷阱（评估样本得分 0）-- 错：生成的是世界掉落物，玩家背包不会出现枪XXX(x, y, z)-- 对：运行时背包枪械实例，playerUin 必须是数字玩家 UINlocal instId = XXX(x, y, z)-- 再用 api-zzz.md 的读取 API 确认 instId 在该玩家背包中
```

这套护栏的设计逻辑有四个特征，值得复用：

1. 前置槽位校验：把"信息不全就不许写调用"变成硬规则，从源头掐掉猜测。

2. 路由表：把语义请求（"发到背包" vs "放到地上"）映射到确定的 reference 文件，杜绝凭记忆选 API。

3. 回读验证：要求保留返回 ID 并二次读取确认，把"声称成功"变成"可验证成功"。

4. 诚实声明：无法验证时必须写明"仅完成配置，未验证"，直接打掉虚报。

回写纪律：只改 Skill 的护栏部分，不改自动生成的 references；每次回写后跑一次 Skill 库校验，确保 0 errors / 0 warnings；API 事实必须与对应 reference 逐项核对过再写。

推进节奏建议按"低分密度"排序模块，每个模块走同一条路径：低分样本 → 可验证根因 → 最小防错规则 → 下一次评估回归。实战中第一轮试点完成后，下一轮排的是特效资源搜索、生物预制创建、运行模式故障排查三个模块——都是低分集中区。

***第 6 步：BadCase 数据集与实验回归***

***——证明“确实变好了”***

*Cloud Native*

护栏写完必须回归，否则你只是"觉得"变好了。

### ▍**6.1 构建 BadCase 数据集**

数据集是回归的载体。AgentLoop 的数据中心支持自定义 Schema、完整 CRUD、SQL 查询、批量上传和标注管理。UGC 游戏场景的 BadCase 数据集，建议至少包含这几个字段：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/bvDbzNRia8j3zrtm130pjEJp2B6NxUu7GLBPXGMJgJ6wZs1kvwB9ficNibxZ18ia2HiatwzjMQiaqRWEL4GsHAjUlLkdoUOibPgicE6wgVBBMcWVQCk/640?wx_fmt=png&from=appmsg)

强烈建议加 tag 字段做语义标注。原因很实际：不加标注，回归时会把所有样本一股脑送进所有评估器，产生大量无效评估（用 API 事实性评估器去评一条纯咨询问答，纯属烧钱）。按语义标注路由到不同数据集，是控成本的关键动作。

第一版数据集不用大，实战中首批只有 3 条（得分分别是 0、0.4、0.5），照样跑通了闭环。BadCase 数据集的价值在于代表性，不在于规模。

### ▍**6.2 发起实验**

SDK 离线实验：适合需要接自己 Agent 服务、做灰度回归的场景。

-

```
pip install agentloop-sdk
```

-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-

```
from agentloop_sdk import (    AgentLoopBenchmark, AgentLoopConfig,    AgentLoopEvaluatorStorage, GeneralEvaluator,    SolutionOutput, Task,)config = AgentLoopConfig(    workspace="<你的工作空间>",    dataset="api_badcase",        # 换成你的 BadCase 数据集    region_id="cn-hangzhou",)async def agent_solution(task: Task, pre_hook) -> SolutionOutput:    # task.input 是数据集一行记录的全部内容    output = await call_your_agent(task.input)    return SolutionOutput(        success=True,        output=output,        trajectory=[],            # 有轨迹务必回传，评估器要靠它取证        meta={"task": task.input},    )storage = AgentLoopEvaluatorStorage(    save_dir="./results",    config=config,    experiment_name="api-skill-guardrail-v2",    experiment_type="agent",    experiment_config={"agent_name": "ugc-coding-agent"},)evaluator = GeneralEvaluator(    name="BadCase Regression",    benchmark=AgentLoopBenchmark(config=config, name="badcase"),    n_repeat=1,    storage=storage,    n_workers=4,                  # 并行，样本多时改用 RayEvaluator)await evaluator.run(agent_solution)
```

运行后终端会打印 Experiment exp-run-xxxx completed，实验记录同步回流平台。

### ▍**6.3 关键动作：透传 experiment_id**

这是很多团队第一次做实验会漏的一步。实验发起时要通过 Context 把 experiment_id 透传到 Agent 轨迹里，评估阶段再从轨迹 context 中提取出来，记录进评估结果。这样才能：

-

在评估结果页用 experiment_id 过滤，看某一次实验的完整表现。

-

在仪表盘上按实验维度聚合，做优化前后对比。

-

在实验记录里用对比分析（支持设 Baseline，逐条比对输出差异与评分详情）。

另外一个实操建议：实验开始前给每道题目新建独立 session，避免多条样本共用会话导致上下文污染，评估结果失真。

***第 7 步：仪表盘与告警***

***——从项目制走向常态化***

*Cloud Native*

前六步做完是一次成功的攻坚，加上这一步才是可持续的机制。

仪表盘：按业务需求构建评估与实验的自定义大盘，建议至少配三块——

1. 线上效果盘：各评估器分数趋势、低分样本数、按模块（特效/背包/UI/生物）的分数分布。

2. 变更验证盘：按 experiment_id 聚合，展示每次 Skill 回写 / Prompt 变更前后的分数对比。

3. 成本盘：Token 消耗、缓存命中率等，避免出现成本黑洞。

告警：配置业务告警规则，主动预警效果与性能劣化。UGC 游戏场景建议至少配：工具调用成功率跌破阈值、API 事实性评估周均分下滑、单会话 Token 异常上涨等。

***三天落地节奏表（可直接照抄）***

*Cloud Native*

![](https://mmbiz.qpic.cn/sz_mmbiz_png/bvDbzNRia8j2iaDzcKKED4ibR6YZLXaI1gQpibicuicSH5K6ib0HHgETzbpead6RrbbSic2UacickTvytuAQicShRqte8ibvw9jXCCDH51H294KibFoWvSM/640?wx_fmt=png&from=appmsg)

******

*Cloud Native*

用实战数据说话，脱敏后如实列出：

质量收益

-

API 事实性评估器上线后，在生产环境发现 5 个以上代码生成 Bug 或 API 文档问题，其中多个错误在多个脚本中重复出现（同类错误批量存在，人工抽检几乎不可能全部发现）。

-

单条样本的 16 项 API 检查中查出 9 项错误，每项都定位到具体函数签名与证据文件，可直接转研发工单。

-

玩法层的先导验证也跑出了价值：在一条"生存 100 天"的请求里，识别出 Agent 全程没有搭建可站立场景的执行证据，而 output 对此只字未提。这类"声称完成、轨迹无证据"的问题，人工验收极易漏过。

-

工具调用成功率评估在测试和生产双环境同时抓到失败调用，并归纳出三类失败模式，全部转化为 Skill 护栏。

效率收益

-

从"人工试玩找问题"变成"自动打分 + 证据定位"，单条样本评估 3 分钟出结论且带完整推理链。

-

回归验证从"不可做"变成"快速验证"。

-

3 天完成从零到闭环，包含接入、评估器建设、实验回归和优化验证。

机制收益（最长期的一项）

-

建立了"低分样本 → 可验证根因 → 最小防错规则 → 下一次评估回归"的标准动作，优化不再依赖个人经验。

-

评估器同时体检 API 文档，把"Agent 老出错"的锅拆成 Agent 问题和文档问题两部分，分别有人认领。

-

观测数据顺带暴露成本优化空间：单会话输入 Token 占比 99.5%、缓存命中率 82%，为上下文工程提供了明确靶子。

***后续规划：玩法层评估展望***

*Cloud Native*

通用层解决"Agent 干活顺不顺"，事实层解决"代码写得对不对"，但还有一个问题没被覆盖：做出来的东西，是不是玩家想要的那个东西。这就是我们规划中的玩法层。

前面提到的先导验证已经证明了它的价值——那条"生存 100 天"的请求里，枪、怪、计分、氛围都做了，唯独没有可站立的场景，玩家进去会掉进虚空，而 Agent 的自述完全没提。这种问题通用层和事实层都抓不到：工具调用全部成功，API 也没写错，唯独东西不对。

真正要谨慎的是怎么评。最直觉的做法是列一张平台主流玩法清单（跑酷、塔防、生存、解谜……），每种玩法配一套固定 Rubric。这个方向我们判断是错的：UGC 平台的玩法是玩家想出来的，不是我们列出来的。清单一旦写死，玩家发明的新玩法会被系统性判低分，Agent 也会为了迎合评分逐渐收敛到那几种标准形态，评估器就成了创意的天花板。

所以玩法层的设计原则可以改为：评估器不预设任何玩法，需求清单每次从用户输入里动态抽取，只判断"用户要的有没有正确做出来"。沿着这条原则，我们初步考虑的是一组玩法无关的维度：需求覆盖度（有没有漏）、可运行与可进入（玩家能不能玩到）、被请求功能的实现正确性（做的是不是用户说的那个意思）、反馈可见性（要求的状态玩家能不能看到，形式不限）、表达达成度（氛围风格方向是否一致）。这些维度对射击、经营、解谜还是玩家自创的新品类都成立。

配套还有几条需要在设计阶段就定死的纪律：只对用户显式要求的内容计分，用户没提的独立玩法项缺失不扣分、Agent 主动创新也不扣分；一切结论以轨迹证据为准，output 声称但轨迹无证据的一律按未完成处理；不评审美、不评好玩程度——"这个关卡不好玩"不是 Agent 的可优化信号，"用户要的传送门没做"才是；玩法专属判据如果要沉淀，只能作为可选插件细化"某项要求怎样算做对"，绝不能新增强制项，也不能因为没有匹配的 Rubric 就降分或拒评。

推进节奏上，建议等通用层和事实层的评估结果被业务方认可、Bad Case 数据集积累到一定规模之后再启动。玩法层的主观性最强，需要先有一批人工标注样本来校准评委，否则很容易出现分数波动大、业务方不认账的情况。

***实战避坑清单***

*Cloud Native*

1. 别用 output 判分。Agent 自述倾向乐观，一切结论以轨迹证据为准，这条写进每个评估器的铁则里。

2. 别给用户没要求的功能扣分。用户没提"难度递增"，缺了不扣分；Agent 主动多做了创新内容也不扣分。否则分数会系统性偏低，业务方不认，创意也会被压制。

3. 别在评估器里硬编码工具名。按语义匹配，平台工具名会变。

4. 别跳过语义标注。不做数据集路由，就会把不相关样本送进 Agent Judge，产生大量无效评估。

5. 别忘了透传 experiment_id。不透传就没法做优化前后对比，实验白跑。

6. 别在实验里复用 session。每道题新建 session，避免上下文污染。

7. 别只改 Prompt。根因多在 Skill 与 API 文档，改 Prompt 是治标，且会让 Prompt 越来越长、规则互相打架。

8. 长会话要单独验采集。20 分钟以上的会话轨迹容易缺失，接入后专门验一次。

9. fork 起子进程要处理上下文透传。否则轨迹断裂，评估器取不到证据。

## 附录 A：API 事实性评估器骨架（可直接改用）

-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-

```
你是一个客观、严格的 UGC 脚本 API 事实性评测专家。你的任务是根据用户的原始指令和 Agent 的完整执行轨迹，评估 Agent 在轨迹中生成、修改、解释或执行的代码是否严格遵循 {API_SKILL_NAME} 中记录的 API 定义。【唯一事实依据】可使用的 API 查询 Skill 是 {API_SKILL_NAME}。评测时必须完整读取该 Skill 的SKILL.md，再按其中的查阅纪律，只读取与待检查 API 对应的 reference 文件。禁止使用模型记忆、函数名相似性、其他引擎经验、常识推断或 Agent 自己的说法替代 Skill 证据。Skill 中未明确支持的事实不得判为正确；Skill 中已有明确定义的事实不得被外部说法推翻。【评测目标】严格检查 Agent 轨迹是否遵循 API 定义，包括：1. 函数是否存在2. 调用形态是否正确（全局模块函数 / 对象实例方法 / 组件方法）3. 参数顺序、个数、类型是否与签名一致4. 返回值的使用方式是否正确仅统计最终写入项目且未被撤销的调用点。【评分标准】score = 正确项 /(正确项 + 错误项)，保留一位小数。"无法核验"项不计入分母，但必须在 explanation 中列出并说明原因。轨迹中无任何 API 调用且指令不需要调用 → score = 1.0。轨迹为空或因平台报错中断 → 按已完成部分评分并注明。【评估内容】用户指令：{{input}}最终输出：{{outputput}}执行轨迹：{{agent_trajectory}}【输出要求】只输出合法 JSON，不要 Markdown 代码块，不要问候语。字段：score（浮点，一位小数）、explanation（字符串，需写明：共检查几项、正确几项、错误几项、无法核验几项，每个错误项给出错误调用、正确签名、证据文件定位，最后给出计算公式）。
```

```

```

## 附录 B：上线前验收清单

-

[ ] 观测：Trace 可下钻到 Span，LLM / RAG / Tool 三类调用齐全，长会话已验证。

-

[ ] 观测：多环境按应用名区分，Trace 上下文在子进程场景可透传。

-

[ ] 观测：Hook 接入时 --collect-trace 已开启，--service-name-prefix 已按环境与角色区分。

-

[ ] 评估器：六段结构齐全，占位符全部来自平台字段白名单。

-

[ ] 评估器：铁则写入（以显式要求为准、强校验轨迹证据）。

-

[ ] 评估器：explanation 要求写出计算过程，可人工复核。

-

[ ] 通用层：内置评估器（工具调用成功率、工具选择合理性等）已勾选，并已加场景过滤。

-

[ ] 评估任务：采样比例与最大样本数已设，过滤条件已按环境/场景锁定。

-

[ ] 数据集：字段含 input / output / score_value / explanation / 语义标注。

-

[ ] 实验：experiment_id 已透传并可在评估结果中过滤。

-

[ ] 实验：每条样本独立 session。

-

[ ] 回写：Skill 护栏与 reference 逐项核对，Skill 库校验 0 error / 0 warning。

-

[ ] 常态化：仪表盘（效果 / 变更 / 成本）与告警规则已配置。

Agent 评估和进化，开启北京、深圳、上海三城巡回沙龙，分享靠谱的 Agent Engineering 实践，现场指导实操，赢取阿里云官方证书，扫描下方海报二维码报名。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/bvDbzNRia8j0vNn8PbPH6xbcrPq9CpfzmETOtibgh8caGRfb1ibgcM6q5umrssOjKeLSibicC81WiaFLSo5mC1PAtNg4LB9X1k2WUS94fMS1paBeE/640?wx_fmt=png&from=appmsg)
