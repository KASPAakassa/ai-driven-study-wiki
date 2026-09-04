> 原文存档:微信文章《Vibe Coding 最佳实践:从"让 AI 写代码"到构建可验证的软件工程闭环》(公众号:Coggle数据科学)
> 原始链接:https://mp.weixin.qq.com/s/nREHkoo50j6oPKQ4w6jOzg
> 抓取日期:2026-08-11(手机 UA curl,避开微信环境验证)
> 用途:整理收件箱素材(用户标注:agent coding 的思路;要求总结 + 评估是否与其他合并),正文原样保留供追溯。

---



Vibe Coding 正在经历一个非常明显的变化，最大的震撼确实来自**代码生成速度**：过去需要自己查文档、设计接口、写实现、调试错误，一个下午才能完成的功能，现在可能只需要描述几句话，Agent 就能搜索项目、修改代码、运行命令并给出一个可以运行的版本。但使用时间越长，就越容易发现一个**反直觉**的现象：

>

*代码生成速度提升得非常快，真正的软件交付效率却没有同比例增长。*

Skill 越来越多，Workflow 越来越复杂，Agent 一次能够修改的代码越来越多，但需求理解错误、上下文丢失、架构偏离、测试不足、修改范围失控、长任务漂移等问题依然存在。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/U2KthBqSEeibBbkiaibxkUVrpT4wRJgFdn27WzWv7EKnhmn1Q0NCFuIFgn3Q3zOjPITzicia7tDSMMPymDQLERzhibOMnRFmUEOto9HyddaZx6aRQ/640?wx_fmt=png&from=appmsg)

****

早期的问题是“模型能不能写代码”，现在的问题逐渐变成“模型怎样稳定地完成一个工程任务”。这两者看起来只差几个字，工程含义却完全不同。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/U2KthBqSEeibvCESJiaQC9zl5kS8DlfSuLqfbmA3cKVmiaJbvR2wib6juIXqXHzPVM44qrR7tCibUdRibdjyelYnibGgNMUn5DZc8Ou361mCiaScDj8/640?wx_fmt=png&from=appmsg)

-

Prompt Engineering 负责把人的意图转化为清晰任务
-

Context Engineering 负责让 Agent 在恰当时机看到正确的信息
-

Harness Engineering 负责提供工具、权限、沙箱、状态、验证和观测环境
-

Loop Engineering 则负责让 Agent 在执行结果的反馈中继续判断、修正、重试或者停止

```
Specification
      ↓
Prompt Engineering
      ↓
Context Engineering
      ↓
Harness Engineering
      ↓
Loop Engineering
      ↓
Verifiable Software

```

### Agent 最大的问题通常不是不会写，而是不知道什么才算完成

很多 Vibe Coding 的失败，表面上看起来是模型能力不足，实际上更经常发生在任务定义阶段。

但对于刚进入项目上下文的 Agent 来说，这些信息并不存在。模型只能根据训练数据和当前代码猜测“优化”到底意味着什么，于是它可能优化代码结构，而你真正关心的是 Redis 故障降级；可能重写整个组件，而你只是希望修一个视觉细节；可能引入新的缓存方案，而项目实际上有严格的基础设施限制。此时问题不在模型有没有能力写代码，而在于**模型没有获得判断正确方向所需的边界条件**。

![](https://mmbiz.qpic.cn/mmbiz_png/U2KthBqSEeib76ibLrXCV4aibevu4v73s3QBc4t3Jkkv9iarY0XqsL1WBRVRHHmME41voziaolozhlcsEZuBqGqvuc65yJnwEME5R9Cnia7XumSpg/640?wx_fmt=png&from=appmsg)

这一变化看似只是 Prompt 写得更详细，实际上对应的是 Vibe Coding 中一个非常关键的思想转变：**不要只告诉 Agent 做什么，还要告诉它什么情况下可以认为已经做完。**

在传统人工开发里，程序员会在实现过程中不断依靠经验判断任务是否完成，因此很多验收标准没有必要全部写下来；但当执行者变成 Agent，如果没有显式定义完成条件，它就只能自己推测何时应该停止。

### Agent 越能写，实施之前反而越值得投入时间

Coding Agent 带来的一个重要变化，是代码生产成本急剧下降。传统软件开发中，真正把一个方案写成几千行代码通常需要大量时间，因此“边实现边思考”虽然不理想，但很多时候仍然是可以接受的，因为开发者会在编码过程中不断发现问题并进行修正。Agent 出现以后，这种成本结构发生了改变。

一份模糊需求可能在短时间内被扩展成几十个文件和数千行修改，而一旦方向错误，生成速度越快，错误实现的规模反而越大。所以一个非常重要、但看起来有些反直觉的结论是：**Agent 的编码能力越强，实施前的需求澄清和设计阶段反而应该越厚。**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/U2KthBqSEeibSkibtnc8mTNvibvQibaWgtFJOByt4mDicFP1cTFyQ4rp3FC1PgZmcKMt9pibKwSjwnlgicOKV3pPtkgdb5gKxkiavNW959G3ialSGEDg/640?wx_fmt=png&from=appmsg)

一个相对成熟的 Agent 开发流程不应该是 `Requirement → Code`，而更应该接近 `Requirement → Research → Design → Plan → Implement → Verify → Review`。

假设一个错误架构决策最终会导致 Agent 修改五十个文件，那么在 Design 阶段否掉这个方案的成本，可能只有几分钟；等到代码全部生成以后再发现方向错误，修复成本就会急剧增加。因此，真正高效的 Vibe Coding 并不是不断减少人在流程中的出现次数，而是**让人只出现在最值得决策的位置**。需求是否正确、架构是否合理、边界是否可接受，这些判断仍然需要高质量输入；一旦方向确定，代码搜索、实现、测试和局部修复则可以大量交给 Agent。

### 从每次重新解释项目，到让 仓库 本身成为上下文

很多人在使用 Coding Agent 时会出现一种重复劳动。每次开启新会话，都要告诉 Agent 项目用什么技术栈、目录结构是什么、测试命令怎么运行、什么代码风格不能违反、哪些文件不要修改、数据库 Migration 有什么要求。第一次这么做没有问题，但如果一个团队每天有几十甚至几百次 Agent Session，每次都通过自然语言重新解释相同规则，本质上是在把本应该属于项目基础设施的信息重新放回人工 Prompt 中。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/U2KthBqSEe8sPLbyJB3dFPBib4yyNicRsxvicbd6HxWTK5ovTCJhN7WAEUzIIibsia7zibKnE6u6hQerMqvKP9YQmEfo4KTCYwnx55ALEREP6VqOw/640?wx_fmt=png&from=appmsg)

**``、`CLAUDE.md` 这一类文件的重要性正是在这里。它们并不是简单的“Prompt 文件”，而是在项目内部建立一份面向 Agent 的长期工程说明**。

更成熟的思路应该是：**不要不断告诉 Agent 如何开发项目，而要逐渐让项目本身能够教 Agent 如何开发它。** 一个 Agent Friendly Repository 应该能够快速回答：项目有哪些模块，每个模块负责什么；开发环境怎样启动；常用的测试、Lint、Type Check 命令是什么；新增模块需要遵循什么架构规则；哪些目录允许自动修改；哪些操作需要人工确认；数据库、API、配置、依赖分别有什么兼容性要求。这样 Agent 进入仓库以后，就可以通过项目自身的说明迅速恢复正确上下文。

### 长上下文不是答案，信息选择才是

随着模型上下文窗口从几十 K 增长到几百 K 甚至更大，人们很容易产生一种错觉：只要模型能够装下整个仓库，就不再需要考虑 Context Engineering。但实际使用 Coding Agent 会发现，问题往往不是上下文完全装不下，而是**信息密度不断下降**。几十个代码文件、几千行日志、多个测试失败、历史聊天、设计文档和工具输出混在一个窗口里，即使没有达到 Token 上限，也会显著增加模型找到真正重要信息的难度。上下文越大，并不意味着模型对所有信息拥有同等稳定的注意力。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/U2KthBqSEe9U1eXl1JhrhdUwuHN6wwbZiaPofrwRKsD9XqQd0RrkJw0ZicNw0MqXWiaJxVK1HR9cDhRicrSoD6P7FGnKVTQA2Dp6OFDC5P5qQIs/640?wx_fmt=png&from=appmsg)

**** 资料将这一问题概括为：上下文管理需要判断哪些信息必须保留，哪些应该摘要、重新检索、刷新或者剔除；Prompt 解决任务如何表达，而 Context 解决模型在解决任务时到底能够看到什么。 对 Coding Agent 来说，这一点尤其重要，因为代码仓库天然就是一个巨大的潜在上下文源，如果没有筛选机制，Agent 很容易在大量无关代码里浪费推理预算。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/U2KthBqSEeibInYTE5OlZs3epCDKfPrO6h3RaLNuvic031FpyRwQq9YXkLPYTJCaQsmCibDWLIiaRlicjO3f39rxN0pv92fDM8kmeLsW86RKTFKA/640?wx_fmt=png&from=appmsg)

```
Repository
    ↓
Search / Explore
    ↓
Relevant Files
    ↓
Research Summary
    ↓
Design
    ↓
Implementation Plan
    ↓
Current Task Context

```

### 抽象是Agent隔离的有效方法

Multi-Agent 或 Subagent 很容易被理解成一种简单的并行计算方案：既然一个 Agent 工作需要十分钟，那就让五个 Agent 同时工作。但在真实 Coding Workflow 中，Subagent 更重要的价值往往不是速度，而是**隔离不同类型任务产生的大量中间上下文**。

![](https://mmbiz.qpic.cn/mmbiz_png/U2KthBqSEe8GcX0ntTViaz05HF5ScYF1et5O3f4Mll6p0zNsVlqSgNNpznibXoxGfNsrNv93ibG4F4icAjbnlPtAQnKaOX8IUzDPBkk8WTwfjuY/640?wx_fmt=png&from=appmsg)

```
                Main Agent
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
    Research      Verify      Review
     Agent         Agent       Agent
        │           │           │
     代码探索      测试分析      独立审查
        │           │           │
        └────── Summary ─────────┘
                    ↓
                Main Context

```

**按照认知任务和上下文边界拆 Agent，而不是机械地按照开发角色拆 Agent。** 需要阅读大量代码但输出结论很短的任务适合 Subagent；需要独立观点避免实现者自我确认的 Review 任务适合 Subagent；彼此可以并行、依赖较弱的代码探索也适合 Subagent。反过来，一个存在紧密顺序依赖的小功能，没有必要为了 Multi-Agent 而 Multi-Agent。

### Skill 的价值，是把偶然成功变成可重复流程

很多人使用 Coding Agent 一段时间以后，会积累大量“好用的 Prompt”。比如一个 Prompt 用来写单元测试，一个用来做代码 Review，一个用来分析日志，一个用来生成 API 文档。短期来看，这确实有价值，但随着使用次数增加，真正高效的做法应该继续往前一步：把稳定、重复出现的操作流程沉淀成 Skill。

**Skill 与普通 Prompt 最大的区别，在于它不仅描述“模型应该怎么回答”，而是可以进一步组织任务步骤、参考资料、脚本、工具甚至验证方式。** 比如一个“修复 Python Bug”的 Skill，可以要求 Agent 首先复现 Bug，然后定位调用链，新增失败测试，执行最小修改，运行 Ruff、BasedPyright 和 pytest，最后输出修改摘要与验证结果。这个流程一旦被验证有效，就不应该要求每个开发者下一次重新发明同样的 Prompt。

![](https://mmbiz.qpic.cn/mmbiz_png/U2KthBqSEeibjYwEoNcSvib72QuJCeZibljK2PibaiagI5TIEM9oQm5CzvxHzhwxSjxc2zlDm73Q6mR30PN5ibqGibjqMyushxHdA8I7WTnmdSeuJU/640?wx_fmt=png&from=appmsg)

**重复出现的自然语言经验，最终应该尽可能转化为结构化工程资产。**

因此，一个成熟项目的 Agent 能力不会只是一个巨大的 `CLAUDE.md`，而更可能逐渐演化为项目规则、Skills、工具、MCP、Hooks、Subagents 和验证体系的组合。规则负责长期约束，Skill 负责可复用流程，MCP 和工具负责扩展行动能力，Subagent 负责上下文隔离，而 Hook 则负责把必须执行的要求从自然语言建议变成确定性程序行为。它们组合起来之后，Coding Agent 才真正开始拥有一个稳定的工作环境。

### Agent 可靠性最终是环境问题，而不只是模型问题

当 Coding Agent 只能在聊天框里生成代码时，模型犯错的代价相对有限。但当 Agent 获得 Shell、文件系统、Git、浏览器、数据库、云服务甚至部署系统的操作能力以后，风险会快速上升。此时开发者真正需要考虑的，不再只是模型写代码准不准，而是 Agent 在什么环境里执行、能够访问什么资源、哪些操作需要审批、任务失败以后怎么恢复、长任务如何保存状态、如何知道 Agent 做过什么，以及什么时候必须强制停止。

![](https://mmbiz.qpic.cn/mmbiz_png/U2KthBqSEeicCrjUUFtwXqMqaj2RDzGarFvAYx1PlBdCP8Aic4AZ1gENMUSyuibfnZ4y0VAOTFer5rgLvAJGkPtPUM6BeRtvVcE3lsm3tOIklY/640?wx_fmt=png&from=appmsg)

**Agent 权限越大，Harness 越重要。** 不是因为 Agent 一定会做坏事，而是因为一个能够高速执行错误计划的系统，本身就需要更强的防护和回滚能力。

### Workflow 告诉 Agent 下一步做什么，Loop 决定它能不能自己收敛

很多所谓 Coding Agent Workflow，本质上仍然只是一个固定流水线：先计划，然后写代码，再运行测试，最后结束。相比完全自由的 Agent，这已经有很大进步，因为流程更加稳定。但固定 Workflow 仍然没有解决一个关键问题：如果测试失败怎么办？如果实现与设计不一致怎么办？如果第一次方案证明不可行怎么办？如果 Agent 连续三次修改都没有改善结果，又应该什么时候停止？

这就是 Loop Engineering 与普通 Workflow 的区别。Workflow 描述一个预期路径，而 Loop 关注系统在真实反馈下如何动态决定下一步。资料中的定义非常清楚：Loop Engineering 的核心对象包括观察、评估、重试、终止条件和人类介入，它解决的是系统做完一步以后如何根据反馈继续推进或停止。 对 Coding Agent 而言，这意味着“测试”不再只是流程中的一个阶段，而变成了 Agent 理解自己是否正确的重要观察信号。

```
        Plan
          ↓
       Execute
          ↓
       Observe
          ↓
        Verify
          ↓
    ┌── Success? ──┐
    │              │
   Yes             No
    │              ↓
    │          Diagnose
    │              ↓
    │           Revise
    │              │
    └──── Done  ←──┘

```

真正的闭环至少需要解决几件事：Agent 能够执行动作，能够看到动作产生的结果，能够判断结果与目标之间是否存在差距，能够根据失败信息调整策略，并且拥有明确的重试、回滚和停止机制。资料中对此有一句非常值得记住的话：**权限解决的是“Agent 能不能做”，反馈和验收解决的是“Agent 做得对不对”。**

### TDD 为什么特别适合 Coding Agent

传统开发里，测试经常被放在编码之后理解：开发者先完成功能，再通过测试检查有没有问题。但在 Agentic Coding 中，测试的意义更加基础，因为模型本身无法像人一样直接感知软件运行状态。Agent 修改代码以后，必须依赖外部信号判断自己的实现到底正确与否，而测试恰好提供了一种结构化、可重复、相对低歧义的反馈。

![TDD for LLMs: Using Test-Driven Development to Prevent AI Hallucinations |  Vijay Anant](https://mmbiz.qpic.cn/mmbiz_jpg/U2KthBqSEe8nCMm2rFgoal5Ypxq2nlqZ7V4AoQWFf98TGQqpXon2qGCF3I0D9ic1ZXVMLsU0Rmp7KLnAAFJfxvvjD87fv0Sgp3dJDmnByfOs/640?wx_fmt=webp&from=appmsg)

**** 如果测试仍然失败，Agent 可以读取错误、分析原因、再次修改。整个开发过程从“模型凭感觉判断自己写对了没有”，变成“模型不断根据客观信号逼近目标”。

### 当 Agent 写得比人看得快，Review 模式必然变化

随着 Coding Agent 生成代码速度不断提高，一个不可避免的问题会出现：代码生产速度最终超过人的逐行阅读能力。如果一个 Agent 一天只修改几十行，人类 Review 完全没有问题；但如果多个 Agent 并行完成任务，每天产生数千甚至数万行 Diff，再坚持所有代码必须由高级工程师逐行审查，人很快就会成为整个系统的吞吐瓶颈。

，当 Agent 生成代码量超过人的逐行 Review 能力以后，架构设计、详细设计、开发计划和验收方式反而变得更加重要；人的注意力应该逐渐从“这一行代码写了什么”，转向“边界是否正确、验证证据是否可信、失败后是否能够恢复”。

### Agent 很容易优化正确性，却可能同时积累复杂性

Agentic Coding 的另一个长期问题，是模型非常容易围绕明确指标优化。如果 Harness 唯一告诉它的是“pytest 必须通过”，那么 Agent 最终最容易学会的是想办法让 pytest 通过。**这在短期任务中通常没有问题，但对于一个持续维护数年的大型系统而言，仅仅“当前测试通过”并不能代表工程质量。**

当前 Coding Agent 的训练和评测通常更加关注任务有没有完成、测试有没有通过、回归有没有发生，但模型完全可能通过一个非常复杂的实现获得正确结果。某次需求的测试全部通过，**并不意味着代码库未来仍然容易修改**。 例如一个 Agent 为了快速解决问题，在五个模块之间增加大量特殊判断，从测试角度可能完全正确，但半年以后增加一个类似功能时，团队才发现一个小改动需要同时理解十五处隐藏逻辑。

![](https://mmbiz.qpic.cn/mmbiz_png/U2KthBqSEe9tIfMwU5X23JMC3My7xdzQkm0rgY6gCJXWNMILuKJ0ibfF11QPUermnXS97uGT7NMsuBUlBnttXK13Le1LPjWj0U1IbZBHok1M/640?wx_fmt=png&from=appmsg)

### Vibe Coding 最终不是工具竞赛

现在围绕 Coding Agent 已经出现大量 Workflow、Skills、MCP、Plugin、Subagent Framework 和所谓“最佳配置”。很容易让人形成另一种焦虑：是不是没有安装某个 Skill，就落后了；是不是没有 Multi-Agent，就不算真正 Agentic；是不是 MCP 越多，Agent 就越强。

工具列表太长会增加模型的选择难度和上下文消耗，复杂方案本身也可能引入新的规则冲突和维护成本。 Vibe Coding 并不存在一套所有项目都应该复制的 Workflow。一个个人原型项目与一个金融核心系统，对测试、权限、Review 和可恢复性的要求完全不同；一个两千行代码的小工具与一个百万行 Monorepo，也不可能使用完全相同的上下文策略。

因此，最好的做法是从自己的失败模式反推工程机制。如果 Agent 经常误解需求，就增加 Requirement Interview，让 Agent 在动手前主动提出未知项；如果经常在大仓库中迷失，就优化代码搜索、Research 和 Context Compression。

### Vibe Coding 的真正指标，不应该是生成了多少代码

当代码生成变得极其便宜以后，“一天写了多少代码”会越来越失去价值。甚至 Agent 完成了多少次 Tool Call、修改了多少文件，也只是过程指标。真正决定软件团队效率的，是需求从提出到形成可验证交付需要多长时间，以及失败以后恢复需要多长时间。

假设一个 Agent 一小时生成五万行代码，但其中大量实现需要人工返工，那么高代码产量并没有任何意义。相反，如果另一个 Workflow 只生成五千行代码，但需求理解准确、测试充分、几乎不需要返工，后者的实际交付效率可能高得多。**因此评价 Vibe Coding 最终应该越来越接近软件工程本身的指标：任务 Lead Time、首次验证通过率、回归率、平均失败恢复时间、人工干预次数、每个任务的 Token 与算力成本，以及下一次修改同一模块需要付出的理解成本。**

Vibe Coding 最容易引发的一种讨论，是“程序员会不会消失”。但如果从实际工程流程看，一个更加准确的描述可能是：**人的位置正在不断向上移动。** 在最早的开发模式里，人负责把代码写出来；在简单 Vibe Coding 阶段，人负责告诉模型要写什么；进入结对编程以后，人更多负责需求、设计和验收；进入 Harness 阶段以后，人开始负责环境、权限、反馈回路和停止条件；如果进一步进入 Agent 软件工厂，人主要负责 Specification、Evaluation、风险边界和异常决策。资料也用类似方式总结了这条能力阶梯：从新手阶段负责把想法说清楚，到结对阶段负责设计和验收，再到 Harness 阶段负责反馈回路和停止条件，最终在更高阶段守住规格、风险和系统可理解性。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/U2KthBqSEeib9wGxicic1O1rHCJghQKicAViaaKrXb42ic8MFfjO8ALpKCIEw3rEE2B8tvgAAuaGd18Yn2aRgkqu2fkM7ZNN1YGpxuLrAOTIXPF7o/640?wx_fmt=png&from=appmsg)

**Agent 负责大量探索、实现、测试和局部修正，人负责决定方向、设计边界、定义反馈和处理例外。** 当这种分工建立以后，开发效率提升才不再只是“打字更快”，而会真正变成整个 SDLC 的效率提升。

### Vibe Coding 的最佳实践，本质是设计一个让 AI 持续写对代码的系统

回到最开始的问题：什么才是 Vibe Coding 最佳实践？

答案其实不是某一个 Prompt，也不是某一个 Coding Agent，更不是安装最多的 Skill、MCP 或 Plugin。真正成熟的方法，是逐渐建立一套围绕 Agent 的工程系统：任务开始前有明确的 Specification；Agent 能够通过 Context Engineering 获得恰当的信息；项目本身能够通过 `AGENTS.md`、设计文档和规则暴露长期知识；重复流程被沉淀成 Skill；确定性要求通过 Hook、Test 和 CI 固化；Agent 在 Sandbox 和权限边界中运行；执行过程能够被观察；失败之后能够重试或回滚；最终结果必须通过可执行证据验证；对于大型系统，还需要额外守住架构和长期可维护性。

所以 Vibe Coding 的演进可以概括成一条非常清晰的路线：

```
Prompt
“告诉 Agent 做什么”
        ↓
Context
“让 Agent 看见正确的信息”
        ↓
Workflow
“让 Agent 按合理步骤执行”
        ↓
Harness
“让 Agent 在可靠环境中工作”
        ↓
Loop
“让 Agent 根据反馈自主修正”
        ↓
Software Engineering System
“让整个开发过程持续可验证”

```

这里真正发生的变化，是我们不再把大模型看成一个“特别聪明的代码生成器”，而开始把它看成软件系统中的一个概率性执行组件。既然它是概率性的，就不能假设每一步一定正确；既然不能保证正确，就需要上下文、工具、验证、权限、反馈和恢复机制；而当这些机制逐渐成熟以后，Agent 的能力才真正能够从偶然的 Demo 效果变成稳定的软件工程生产力。

因此，2026 年讨论 Vibe Coding，真正值得关注的问题已经不再是“AI 一次能写多少代码”，而是：

**它能不能理解正确的问题，能不能在正确的上下文里行动，能不能获得可靠反馈，犯错以后能不能恢复，以及最后能不能拿出足够的证据证明任务已经完成。**

真正成熟的 Vibe Coding，是把 Specification、Context、Tools、Harness、Verification 和 Feedback 组合起来，建立一条从需求到可验证交付的完整闭环。

**最好的 Vibe Coding 系统，不是让 AI 写更多代码，而是让 AI 即使不断写代码、不断修改代码，整个软件系统仍然处于可理解、可验证、可恢复和可持续演进的状态。**

# * 学习大模型 & 讨论Kaggle  *#

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/uoTGEibAZUEgGtr0ib3fibjtZGGiawJxeZb8NEPR0DibUlaMhD1mD7NiajMfbiaBiarSpbLMkrct2I5dsSVoOnCFD7zElg/640?wx_fmt=other&wxfrom=5&wx_lazy=1&wx_co=1&tp=webp#imgIndex=5)

每天大模型、算法竞赛、干货资讯

与 36000+来自竞赛爱好者一起交流~
![图片](https://mmbiz.qpic.cn/mmbiz_png/uoTGEibAZUEgjVMpibbLcunLvNOo6YlvekSTegqBSKoMSyrUbWVDkq5jNG5Hf3uwt71tAq11staN0STb2VPxa1CA/640?wx_fmt=other&wxfrom=5&wx_lazy=1&wx_co=1&tp=webp#imgIndex=6)
