# 现代智能体自我改进综述:从模型更新到脚手架演化(Self-Improvements in Modern Agentic Systems)

> **一句话摘要**:97 页学术综述(含 Schmidhuber)给出自我改进智能体的统一框架——现代 Agent = **基础模型 + 操作脚手架**,改进路径分两条:改模型参数(FM 改进,慢而稳,能力固化进权重)与改脚手架(改 prompt/memory/tool/控制逻辑,快而可回滚)。论文核心贡献:统一形式化(自诱导更新算子)、系统分类(更新什么 × 信号从哪来)、六类应用、评测范式与开放问题。
>
> **来源**:论文《Self-Improvements in Modern Agentic Systems: A Survey》(arXiv:2607.13104,cs.AI,2026-07-14,97 页 12 图),https://arxiv.org/abs/2607.13104;公众号解读「专知」(https://mp.weixin.qq.com/s/49PhPHlhxdZbqLxiYdQWbQ);官方 GitHub:github.com/selfimproving-agent/awesome-Self-Improving-Agents(312 条目);原始资料存档于 `docs/inbox/self-improving-survey-source.md`

## 概念:什么是现代自我改进智能体

### 背景:从概念到工程系统

自我改进是 AI 的长期核心命题——从 Good 的"智能爆炸",到 Schmidhuber 的自指学习框架(1987)与 **Gödel Machine**(2003),早期研究已设想过能检查、修改、提升自身的系统。但过去这类系统必须在**底层代码、规则或权重空间**中搜索,工程上很难扩展。

**现代基础模型改变了格局**:LLM/VLM 提供了统一的自然语言接口,使推理、执行、反馈和修改都可以通过语义化对象表达。语言把"自我修改的搜索空间"从机器码压缩到自然语言——这是从 1987 年自指学习到现代 Agent 自我改进的解锁关键。现代 Agent 通常被包裹在**操作脚手架**(prompt、记忆、工具接口、控制逻辑)中,于是自我改进不再只是"模型自己改权重",也可以是"系统自己改运行方式"。

### 核心定义:Agent = 基础模型 + 脚手架

论文把现代 Agent 形式化为配置 \(\mathcal{A}_t=(\theta_t,\Sigma_t)\):

- \(\theta_t\):基础模型参数(提供通用认知能力);
- \(\Sigma_t=(p_t,m_t,\mathcal{T}_t,g_t)\):脚手架——prompt、记忆、工具集、控制逻辑(负责构造上下文、接入记忆、选择工具、执行控制逻辑并与环境交互)。

**自我改进的形式化定义(自诱导更新)**:Agent 通过自身执行产生学习信号(轨迹、失败、批评、验证结果或候选修改),提交到**更新算子 \(\mathcal{U}\)**,**持久修改**模型参数或脚手架组件。关键:这种更新不是临时上下文变化,而是影响后续执行的**持久配置变化**。

**两种自我指涉模式**:

1. **分布级(间接)**:行为塑造数据分布,供外部优化;
2. **执行级(直接)**:通过动作直接编辑脚手架。

**与相关概念的区别**:

| 概念 | 与自我改进的区别 |
| --- | --- |
| 在线学习 / RL | θ 更新≈标准 RL 策略优化(RLHF/PPO/DPO);但**Σ 更新重塑 MDP 本身**(动态改变状态-动作空间),用搜索/生成/符号编辑而非梯度,超出经典 RL 框架 |
| 元学习 | 自我改进强调对自身配置的**可持续修改**(模型权重 + 操作结构) |
| 自我反思 | 自我改进是持久配置变化,反思只是其中一种信号来源 |

**Skill 定义(论文独特点)**:skill 是更新算子的**可复用实例**,可序列化到任一 substrate(工具/prompt/记忆/权重/控制逻辑);**object-level skill**(作用于任务/世界状态,≈HRL 的 option)vs **meta-level skill**(作用于自身配置)——后者使"算子成为自身操作数",恢复自我指涉闭环。

## 原理:两大改进路径与系统分类

论文最重要的分类轴是**"更新什么"**:更新基础模型参数 = **foundation model improvement**;保持参数不变、更新 prompt/memory/tool/控制逻辑 = **scaffolding improvement**。另一个轴是**"信号从哪里来"**:模型自己生成的示范、自己产生的评价反馈、或真实/模拟环境中的交互经验。

> **慢循环 vs 快循环**:基础模型改进把经验固化到权重,收益可跨任务复用,但训练成本高、可能灾难性遗忘;脚手架改进改系统外围结构,更便宜、易回滚,适合任务级快速适配。

### 路径一:基础模型改进(FM Improvement,更新参数)

按学习信号分三类:

**1. 内生生成示范 \(\mathcal{D}_t\)**(Agent 自己生成训练样本:指令-回答对、推理轨迹、执行日志、代码、测试样例)

- 代表方法:Self-Instruct、Evol-Instruct(复杂度进化)、self-consistency 过滤(Huang et al.《Large Language Models Can Self-Improve》)、verifier 过滤(STaR 类,Singh et al. 用单元测试选正确解)、LADDER(递归分解课程)、DIVE(多样性池扩展)、TT-SI(不确定性驱动的测试时 LoRA 定向微调);
- 优势:减少人工标注依赖;
- **风险:模型把自己错误/偏见/低多样性样本反复训练进去 → 模型坍缩、知识泡沫**。

**2. 内生评价反馈 \(e_t\)**(Agent 或内部评估器对候选输出打分、排序、偏好比较、critique)

- 代表方法:rubric 反馈(评分/偏好/置信度 → SFT/RL)、consistency 反馈(自一致性聚合)、corrective 反馈(批评+修订:ReST meets ReAct、SELF、RISE、Reflect-Retry-Reward、AlphaAllM);
- **风险:生成器与评估器同源会放大盲点**——系统学会迎合评估表面形式而非真正提升能力。

**3. 外生探索经验 \(\tau_t\)**(来自真实或模拟环境)

- grounded 环境:程序验证器(Agent-RLVR)、学习奖励模型(WebRL、UI-Genie、MobileGUI-RL 用 GRPO)、自生成任务(Absolute Zero、ETO)、平台 AgentGym;
- 模拟代理环境(世界模型):WebEvolver、WebSynthesis、WebDreamer、SPA、WMPO、GLoW(GLoW 达 100–800× 更少真实交互);
- 挑战:语言 reward hacking、能力回退、幻觉动力学、轨迹长度/上下文张力。

**启示:参数级自我改进需要可靠信号、质量过滤、外部锚点和回滚机制——没有验证的自训练循环可能越改越偏。**

### 路径二:脚手架改进(Scaffolding Improvement,参数不变)

**1. Prompt(四范式)**

| 范式 | 代表方法 | 特点 |
| --- | --- | --- |
| 标量反馈 | APE、OPRO、RLPrompt、InstructZero、BBT、DSPy、BPO | 用数值分数优化 prompt |
| 定性反馈 | Self-Refine、Reflexion、MAPS、Chain-of-Hindsight、ACE(Generator–Reflector–Curator)、Scrable | 用语言批评迭代 |
| 种群进化 | Promptbreeder、STOP、GPTSwarm、AutoDAN、Evol-Instruct、GEPA | 群体搜索 |
| 文本梯度 | APO、TextGrad、metaTextGrad、SkillOpt | 把梯度概念搬到文本 |

信号越结构化,优化越自动。**风险:prompt 优化容易过拟合 benchmark 或评测器**——只是学会利用评分漏洞,而非获得通用能力。

**2. Memory(三个维度)**

- **记忆对象**:交互轨迹、筛选后的原始内容、外部知识、向量嵌入;
- **记忆结构**:扁平、层级、图结构、向量库;
- **记忆处理**:CRUD(Create-Read-Update-Delete)信号驱动循环 + 压缩 + 信用分配。

代表:MemoryBank、H2HMem(多模态记忆基准)。**关键:记忆不是"存得越多越好"**——过度存储引入噪声/隐私泄漏/检索压力,过度删减丢失关键经验。真正的自我改进记忆应当是**信号驱动**的:根据任务结果和反馈决定哪些经验值得保留、重写或遗忘。

**3. Tool(三类)**

- **动态工具路由**:检索/图路由(ToolNet、OrchDAG、MassTool)、策略学习路由(AUTOACT、MCP-Flow、Tool-Star、DeepEyesV2、AGENTFLOW、SPORT、AutoTIR、ToolGen)、主动/交互路由(MCP-Zero、ASKTOACT、Tool-Planner、ToolACE-R);
- **迭代工具修复**:Voyager、STELLA、SkillWeaver、PyVision、DRAFT;
- **自主工具创建**:ATLASS、FRIDAY、TOOLMAKER、Alita、Code2MCP、AgentOrchestra(生命周期自动化 + MCP 标准化集成)。

共同把 Agent 从静态工具使用者推向**可扩展的行动系统**(工具治理:何时路由到哪个工具、失败后如何修复、何时创建新工具)。

**4. Full Scaffolding(最深层的结构改进)**

把整个操作逻辑甚至自身代码库视为可修改对象:\(\Sigma_{t+1}=\mathcal{I}_{\Sigma_t}(\Sigma_t;\mathcal{S}_t)\)(可序列化编码、exec、**验证器门控**)。代表:AlphaEvolve、ShinkaEvolve、ADAS、EvoFlow、**Self-Taught Optimizer**、Agent Symbolic Learning、Gödel Agent(monkey-patching)、**Darwin Gödel Machine**、Huxley-Gödel Machine(CMP 度量)、Live-SWE-Agent。

**风险最高:必须有单元测试、回归测试、安全检查、版本回滚,否则 Agent 可能把自己的运行结构改坏。**

## 代码 / 实现:自我改进的工程要点

### 系统设计三条启示

1. **Fast Exploration → Slow Consolidation**:Σ 快可逆、θ 慢但跨域迁移。**参数固化是有损压缩**(丢失罕见错误恢复策略)且使先前安全界失效——噪声反馈应先在脚手架内验证,再考虑参数化;
2. **Critic 是被治理的基础设施**:批评者的 exploit-resistance 是能力天花板——生成者与批评者须解耦,批评者进化须单调(纯增量式测试生成)且受人工审计;
3. **分层门控安全**:自我改进对象非平稳,弱系统推理强后继系统(Vingean reflection)是核心难题——把 Agent 当受保护运行时中的不可信代码,更新须过功能正确性/工具权限/随机扰动鲁棒性检查。

### 可靠自我改进系统的四个条件

- **更新信号可验证**(执行反馈、测试、验证器);
- **改进过程可归因**(知道改了哪、为什么改);
- **失败能够回滚**(版本化、checkpoint);
- **评测不被静态 benchmark 绑架 + 安全边界持续可审计**。

## 实践 / 应用:六类应用与评测

### 六类应用

| 应用领域 | 代表工作 | 特点/挑战 |
| --- | --- | --- |
| 软件工程 | SWE-bench 生态、SE-Agent | 最自然的试验场:编译器/测试/lint/CI 提供可执行反馈 |
| Web 导航 | WebRL、UI-Genie | 真实交互轨迹,但页面变化和 UI 反馈噪声大 |
| 游戏与战略推理 | SeRL、Richelieu | 适合自博弈 + 长期规划 + 课程化技能 |
| 科学发现 | ChemCrow、SciAgents、AI Scientist、AI co-scientist、Coscientist | 挑战:新颖性/可复现性难自验、实验不可逆 |
| 具身 AI 与机器人 | RoboCat、AutoRT、RoboGen、RACAS | 强调物理约束与安全,sim-to-real、安全探索 |
| 通用计算机控制 | Agent S、SEAgent、UI-Genie、PC Agent-E | 面对开放界面/文件系统/OS 自动化;删除文件/密码/交易等安全风险 |

共同点:**环境本身为自我改进提供反馈,但反馈的可靠性、成本和安全边界各不相同**。

### 评测方法

- **形式化目标**:追踪迭代轨迹 \(m_t=\mathbb{E}[\Phi(\cdot)]\),受累计资源预算 \(b_t \le B_{max}\) 约束——**评测"改进过程"而非端点分数**;
- **metric-based measurement**(可执行 oracle):测试通过率、成功率、成本、延迟;
- **judge-based measurement**(无 oracle):偏好、质量、解释性、安全性——需指定判定者与判定预算、防对 judge 过优化(VerifiAgent、Agent-as-a-Judge、ARJudge、EvalAgent);
- **机制 benchmark**(测某类改进机制:FM 级 SWE-Bench+、ToolEmu、GitTaskBench;脚手架级 MINT、TaskBench、MetaTool、BFCL、RSI-Bench)vs **领域 benchmark**(测完整 Agent:SWE-bench、Mind2Web/WebArena、OSWorld/AppWorld 等六领域)。

**论文提醒:静态 benchmark 很容易被过拟合或被 Agent 找到漏洞**——自我改进评测应报告完整学习曲线、回滚策略、消融分析、分布外泛化和安全失败模式。

## 总结

- **统一框架**:现代 Agent = 基础模型 + 脚手架;自我改进 = 自诱导更新算子,持久修改参数或脚手架;
- **两条路径**:FM 改进(内生示范/评价反馈/外生探索,慢而稳,固化进权重)vs Scaffolding 改进(prompt/memory/tool/full scaffolding,快而可回滚);
- **关键风险**:模型坍缩(自训练无验证)、生成器-评估器同源放大盲点、prompt 过拟合 benchmark、记忆过度存储/删减、自改代码无门控;
- **系统设计**:Fast Exploration → Slow Consolidation;Critic 是被治理的基础设施;分层门控安全(Vingean reflection);
- **评测哲学**:改进应作为带资源预算的轨迹来测;judge 是被治理的攻击面;
- **下一步**:对比站内 [自进化 Agent 综述](self-evolving-agents-survey.md)(腾讯 14 篇论文视角,互补)、[LLM 记忆综述](llm-memory-survey.md)(记忆维度深化)、[Agent 持续进化](../03-agents/agent-continuous-evolution.md)(工程视角)。

## 延伸阅读

- 论文:https://arxiv.org/abs/2607.13104(HTML:https://arxiv.org/html/2607.13104v1)
- 官方资源:GitHub awesome 列表 github.com/selfimproving-agent/awesome-Self-Improving-Agents(312 条目)
- 公众号解读:https://mp.weixin.qq.com/s/49PhPHlhxdZbqLxiYdQWbQ(专知)
- 站内:[自进化 Agent 综述(腾讯 14 篇)](self-evolving-agents-survey.md)(论文点集合,互补)、[LLM 记忆综述](llm-memory-survey.md)、[Harness Handbook](harness-handbook.md)(行为定位)、[Agent 的持续进化](../03-agents/agent-continuous-evolution.md)(工程视角)、[Agent 框架七方对比](../03-agents/agent-frameworks-seven-comparison.md)(脚手架实现载体)
