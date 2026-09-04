# 自进化 Agent 综述:三大技术路线与 14 篇论文全景

> **一句话摘要**:Self-Evolving Agent(自进化 Agent)要让 Agent 自己越用越聪明——把交互经验存下来、训进权重、甚至零人工数据自我循环。腾讯 PCG 团队调研 14 篇论文,梳理出三大路线(经验存储型 / RL 训练型 / 0 数据自学型)与范式演进脉络。本文在综述基础上做第二轮扩展:补全每篇论文的机制细节、扩展 GRPO/课程学习/信用分配等基础概念、并提炼研究空白与工程启示。
>
> **来源**:微信公众号「腾讯程序员」《Agent 开始"自我进化":会出题、会反思,还会自己长出新技能》(作者:horacebao、ashexie,腾讯 PCG 大数据平台部),https://mp.weixin.qq.com/s/fsVJiorPBN4ylGjUYBcIPw;原始资料存档于 `docs/inbox/self-evolving-agents-source.md`

## 概念:什么是自进化 Agent

**自进化 Agent** 指能够在与环境/用户交互过程中**自动积累经验、提炼能力、并在后续任务中复用与提升**的智能体。核心诉求拆成三件事:

1. **能存**:把交互中沉淀的价值(成功模式、失败教训、可迁移技能)存下来;
2. **能用**:新任务中能检索/调用/内化之前的经验;
3. **能进化**:经验本身动态更新、合并、淘汰,避免越攒越乱。

!!! note "为什么现在被重视"
    四个老大难问题驱动:①**静态知识**(训练完认知冻结);②**上下文有限**(再长也有边界,多轮"断片");③**重复犯错**(今天教会明天又犯);④**训练贵**(每次增强都要重跑 SFT/RL)。学术上并不新(强化学习 + 经验回放是雏形),大模型时代被点燃是因为:**LLM 自己能给自己写笔记**、长程交互 Agent 有了真实需求、高质量标注越来越贵。

!!! tip "与站内工程文章的视角分工"
    站内 [Agent 的持续进化](../03-agents/agent-continuous-evolution.md) 讲**工程视角**(保存≠学习、四种载体:上下文/文件/参数/外部存储);本文讲**学术视角**(论文机制、RL 训练、研究空白)。两篇互补:工程篇回答"我现在怎么落地",本文回答"学术界在往哪走"。

## 原理:三大技术路线

按"**是否更新模型权重**"和"**是否依赖人工数据**"两个维度分三类:

| 路线 | 更新权重 | 依赖人工数据 | 代表工作 | 一句话类比 |
| --- | --- | --- | --- | --- |
| **一、经验/Skill 存储型** | ❌ | ❌(靠反馈) | AutoSkill、EvoSkill、MemSkill、CoEvoSkills、SE-Agent | 给 Agent 配"工作笔记",模型不动,需要时翻阅 |
| **二、RL 训练型** | ✅ | ❌(靠反馈) | EvolveR、SAGE、SkillRL、SKILL0、SkillOS、AgentEvolver | 把笔记上的经验通过 RL 写进权重,真正"长本事" |
| **三、0 数据自学型** | ✅ | ✅(完全无人工) | Agent0、Tool-R0、Absolute Zero | 连老师都不要,Agent 互相出题互相考试 |

!!! warning "注意'依赖人工数据'的措辞"
    第一、二类虽然标"❌ 依赖人工数据",但**仍然需要训练/反馈数据**——人为交互反馈或训练集反馈本质上都是数据,只是不再需要逐条人工标注。真正零数据的是第三类。

### 路线一:经验/Skill 存储型(不更新权重)

特征:不训练、跨会话保留上下文、文件式存储;base LLM 冻结,所有"成长"发生在外挂里。

| 论文 | 核心机制 | 评估与亮点 |
| --- | --- | --- |
| **AutoSkill** (2603.01145) | 双环结构:在线服务环(查询重写 → 混合检索 Embedding+BM25 → 技能注入生成)+ 技能进化环(提取 → Add/Merge/Discard → 版本化合并) | WildChat-1M,但**没有性能指标**,只统计 skill 数量——暴露该类工作"评估缺位"的通病 |
| **EvoSkill** (2603.02766) | 三 Agent 分工:**Executor**(执行+留档失败轨迹)→ **Proposer**(根因分析,新建或修改 Skill)→ **SkillBuilder**(落地为结构化 Skill 文件夹+单元校验);**Pareto Frontier 精英池**(新 Skill 至少一维严格优于现有才入库) | OfficeQA 60.6%→67.9%(+7.3pp,靠自学到的 data extraction validation 等两条 Skill);跨任务迁移 +5.3pp(search persistence protocol 从 SealQA 迁到 BrowseComp) |
| **MemSkill** (2602.02474) | 只对"操作 Memory 的 Skill"做自进化:Retriever(Qwen0.6B Emb)+ Controller(MLP,接受 RL 训练,是这一类里少见的"有训练")+ Executor(冻结);双更新 Loop(Controller 用下游 F1/Success Rate 当 reward;Hard Case 交给 Designer 更新 Skill 库) | **迁移评估**:LLaMA 训练的 Controller/Skill 迁到 Qwen 仍有效;LoCoMo 训练的迁到 LongMemEval 仍有效;给"无评估"的工作提供了"训练集建 Skill、测试集评估"的思路 |
| **CoEvoSkills** (2604.01687v2) | Generator(生成 Skill + 同步生成单元测试)+ **Surrogate Verifier**(隔离 sandbox 跑 Skill 与测试,返回带失败原因/修改方向的反馈);Skill 与 Test **共进化**(TDD 理念);两阶段验证:廉价 Surrogate → 昂贵 Oracle(Claude Code/CodeX 端到端,失败整条打回) | **self-evo 优于 cross-model transfer**:Opus 4.6 self-evo 30.6%→71.1%(+40.5);把强模型 Skill 迁给弱模型,提升明显低于弱模型自己 self-evo——Skill 与模型"风格"耦合 |
| **SE-Agent** (2508.02085, NeurIPS 2025) | 五阶段:**多策略轨迹生成**(5 种"性格":贪心/先测试/关注代码风格/防御式/最小可行)→ 反思修订(纵向)→ 质量过滤(综合评分)→ **跨轨迹重组**(横向:Crossover 交叉/Transfer 迁移/Restructure 重构)→ 最终方案选取,可迭代 N=4 收敛 | SWE-Bench Verified 上多个 LLM 显著提升,最高 +55% 相对改善;与 Claude Code 对比验证"轨迹级进化"与底层模型正交 |

!!! note "横向 vs 纵向总结"
    这是贯穿全文的锚点概念:**纵向总结** = 基于单条历史轨迹/对话总结(所有第一类其他工作);**横向总结** = 基于多次采样的多条轨迹交叉融合(SE-Agent 独有)。第二类工作基本仍以纵向为主。

### 路线二:RL 训练型(更新权重)⭐ 当前主流

通过 RL 直接更新模型权重,让模型从根本上变强。

| 论文 | 核心机制 | 评估与亮点 |
| --- | --- | --- |
| **EvolveR** (2510.16079) | 两阶段:离线把所有轨迹提炼成通用"策略原则"存入原则库 → 在线实时检索原则指导行动,新轨迹反哺下一轮蒸馏;Reward = 最终结果 + 格式 reward | NQ/HotpotQA/TriviaQA/PopQA;看似 "RL by talking",但仍靠标注集 Ground Truth 训练 |
| **SAGE** (2512.17102) | **Sequential Rollout**:每次 rollout 串行跑一串相似任务,前序任务积累的技能在后续任务直接用——训练中模型被迫学会"生成技能 + 复用技能";额外 **Skill-integrated Reward** 激励技能生成与调用 | AppWorld(APP 交互数据集) |
| **SkillRL** (2602.08234) ⭐ | 强模型(o3)蒸馏 Skill → 弱模型(Qwen2.5-7B)RL 训练学会使用 → 递归进化技能库;总结者总结成功轨迹的决策点/可迁移模式 + 失败轨迹的失败教训(压缩比 10–20×) | ALFWorld 89.9% vs 77.6%(+12.3pp)、WebShop SR +6.6pp、Search-QA +8.6pp;Skill 库 55→100 条;本质是**蒸馏而非真正的进化** |
| **SKILL0** (2604.02268) ⭐ | 把 Skill 从推理时"外挂上下文"**内化到模型参数**:三阶段渐进课程(6 条 Skill 学会调用 → 3 条减少依赖 → 0 条完全内化),消除检索成本/Token 开销/噪声,零样本执行(每步 <0.5K tokens) | 继承 SkillRL 的 SkillBank 与 o3 总结者;不关心 Skill 从哪来,只关心如何内化——是 SkillRL 的"下游消费者" |
| **SkillOS** (2605.06614) ⭐⭐ | **训练专门 Curator 学会"管理" SkillRepo**(增/改/删),Executor 冻结;出题者 Gemini-2.5-Pro 仅离线标注分组(group_size=8);长周期间接奖励信号 | 两个关键结论:①**训练过的小模型总结者 > 冻结的大模型总结者**(RL 过的 Qwen3-8B Curator 超过冻结 Gemini-2.5-Pro);②**不动解题者性能也涨**——换 Curator 比换 Executor 更轻量 |
| **AgentEvolver** (2511.10395) ⭐ | 三环自演化(自出题/自解题/自总结),无人工标注;**Self-Questioning 四步**(探索:高温 LLM 广深优先 → 合成:轨迹蒸馏+用户偏好 → 筛选:去重+相似度+可行性 → 混合);出题与解题用同一 Qwen2.5-7B/14B,RL 后双重提升 | Experience Manager 调 Qwen-MAX API(阿里 Reme 记忆机制);步骤级信用分配 |

### 路线三:0 数据自学型(完全无人工)

精神最激进:连数据集都不要,Agent 自己出题自己考自己。

| 论文 | 核心机制 | 评估 |
| --- | --- | --- |
| **Agent0** (2511.16043) | 双 Agent:Curriculum Agent(RL,出题;reward = 解题者不确定性 + 工具使用频率)+ Executor Agent(RL,解题;reward = 成功率);先训出题者(解题者冻结当 reward model),再训解题者 | 数学类(GSM8K、AIME 等);**隐患:答案来自出题者自己多采样投票的 sliver answer** |
| **Tool-R0** (2602.21320) | 同 Agent0 但做 general tool:Generator(格式 + 合法性不能有幻觉 tool + 难度 reward)、Solver(格式 + 准确性 reward) | ToolAlpaca、SealTool、NexusRaven;答案仍是 sliver answer |
| **Absolute Zero** (2505.03335) | 单模型双角色;题目为 **[输入, 代码, 输出] 三元组**,随机删一个让答题者猜,**以代码执行器为唯一验证来源**——把判分外包给绝对客观的执行环境;出题 reward = 1 − 成功率(成功率为 0 时 reward 也为 0,避免出太难的题) | 代码(HumanEval、MBPP、LCB)+ 数学(AIME24/25、AMC、MATH-500、Minerva、Olympiad) |

!!! warning "第三类共同隐患"
    出题 Agent 自己生成的 sliver answer 可靠性存疑——**最好有自动化的客观判断标准**(如 Absolute Zero 的代码执行器);出题难度是核心难点(reward shaping:太难学不懂、太简单学不到);评估很混乱,只有数学类 benchmark 勉强多次出现,可比性差。

## 代码 / 实现:两个核心机制的最小演示

### 演示 1:混合技能检索 + 注入(路线一的核心)

AutoSkill/EvoSkill 式:检索时语义相似度 + 词汇相关性(BM25 简化)双管齐下,选出 top-k Skill 注入上下文。纯 Python 演示——注意注入是"选最相关的少量 Skill",而不是把整个库倒进去:

```python
import math, re

def tokenize(text: str) -> list[str]:
    # 中文按单字切分、英文按单词,保证中英文都能产生有效重叠
    return re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", text.lower())

def bm25_simplified(query_tokens, doc_tokens, avg_dl, N, k1=1.5, b=0.75):
    """简化 BM25:IDF × 词频饱和。doc_tokens 为单文档;此处 doc 是 Skill 的文本。"""
    dl = len(doc_tokens)
    score = 0.0
    for qt in set(query_tokens):
        tf = doc_tokens.count(qt)
        if tf == 0:
            continue
        n_q = 1  # 简化:假定该词出现在 1 篇文档(演示用)
        idf = math.log((N - n_q + 0.5) / (n_q + 0.5) + 1)
        score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avg_dl))
    return score

def cosine_sim(vec_a: dict, vec_b: dict) -> float:
    common = set(vec_a) & set(vec_b)
    dot = sum(vec_a[t] * vec_b[t] for t in common)
    na = math.sqrt(sum(v * v for v in vec_a.values()))
    nb = math.sqrt(sum(v * v for v in vec_b.values()))
    return dot / (na * nb) if na and nb else 0.0

def retrieve(query: str, skill_bank: dict, top_k: int = 2) -> list:
    """混合检索:词频向量余弦(伪语义)+ 简化 BM25,综合打分取 top-k。"""
    qt = tokenize(query)
    q_vec = {t: qt.count(t) for t in set(qt)}
    avg_dl = sum(len(tokenize(s)) for s in skill_bank.values()) / len(skill_bank)
    scored = []
    for name, text in skill_bank.items():
        dt = tokenize(text)
        d_vec = {t: dt.count(t) for t in set(dt)}
        sem = cosine_sim(q_vec, d_vec)                       # 语义(词袋近似)
        lex = bm25_simplified(qt, dt, avg_dl, len(skill_bank))  # 词汇(BM25)
        scored.append((name, sem * 0.6 + lex * 0.4))
    scored.sort(key=lambda x: -x[1])
    return scored[:top_k]

skill_bank = {
    "data_extraction_validation": "提取财务表格数据后,必须校验单元格对齐,发现错位立即修正再继续",
    "quant_analysis_checkpoints": "金融数值计算过程强制加入校验点,每步结果与上一步交叉核对",
    "search_persistence": "搜索无结果时不要放弃,换关键词或换数据源持续尝试,直到拿到证据",
}
query = "分析这份财务报告的表格,数字要对得上"
for name, score in retrieve(query, skill_bank):
    print(f"注入 Skill: {name} (score={score:.3f})")
```

### 演示 2:Pareto 精英池筛选(EvoSkill 核心机制)

新生成的 Skill 必须**至少在一个维度严格优于**已有 Skill 才入库,保证库"精而不滥":

```python
def pareto_dominates(a: tuple, b: tuple) -> bool:
    """a 是否严格支配 b:所有维度 >= 且至少一维 >"""
    return all(x >= y for x, y in zip(a, b)) and any(x > y for x, y in zip(a, b))

def try_add_skill(pool: list, candidate: tuple) -> bool:
    """候选 (通用性, 准确率, 可迁移性)。返回是否入库;同时清掉被支配的旧 Skill。"""
    pool_snapshot = pool[:]
    for old in pool_snapshot:
        if pareto_dominates(old, candidate):
            print(f"  候选 {candidate} 被 {old} 支配 → 丢弃")
            return False
    for old in list(pool):
        if pareto_dominates(candidate, old):
            pool.remove(old)
            print(f"  候选 {candidate} 支配旧 {old} → 旧 Skill 淘汰")
    pool.append(candidate)
    print(f"  候选 {candidate} 入库,当前库: {pool}")
    return True

pool = [(0.7, 0.8, 0.6), (0.5, 0.9, 0.4)]  # 已有两条 Skill
try_add_skill(pool, (0.8, 0.7, 0.5))   # 通用性更高 → 入库
try_add_skill(pool, (0.6, 0.6, 0.6))   # 被支配 → 丢弃
```

## 第二轮扩展:论文之外的知识

### 概念扩展(综述没展开、但读懂论文必需)

- **GRPO**(Group Relative Policy Optimization):SkillRL 用的 RL 算法。PPO 需要单独训练 critic 模型估计 value;GRPO 用**一组采样结果的相对优势**替代 critic——更省显存、更适合可并行采样的生成任务。是当前 LLM 后训练(DeepSeek-R1 等)的主流选择;
- **课程学习(Curriculum Learning)**:SKILL0 的三阶段渐进课程(6→3→0 条 Skill)就是课程学习——先易后难、逐步撤脚手架,让模型"学会调用 → 学会内化";
- **Reward Shaping**:出题难度设计(太难学不懂、太简单学不到)本质是给 reward 塑形;Absolute Zero 的"成功率为 0 时 reward 也为 0"就是防奖励黑客的具体技巧;
- **Self-Play(自博弈)**:第三类"出题者-解题者"闭环是自博弈的 Agent 版——一个 agent 的难度是另一个 agent 的训练信号,类似 AlphaZero 的自我对弈;
- **蒸馏 vs 进化**:SkillRL 用强模型 o3 总结 Skill 再喂弱模型,本质是**蒸馏**(知识从强到弱单向流动);AgentEvolver 自出题自总结是**进化**(能力在自身闭环中生长)。综述作者的评论提醒:别把蒸馏包装成进化;
- **信用分配(Credit Assignment)**:AgentEvolver 的"步骤级信用分配"指长程任务中如何判断"哪一步决策导致了最终成败"——RL 长程稀疏奖励的核心难题。

### 范式演进链(四篇代表工作的关系)

```
SkillRL (2602.08234)     强模型提炼知识 → 弱模型 RL 学会使用 → 递归进化技能库
    ↓
SKILL0 (2604.02268)      同一技能库 → 渐进撤回 → 内化进参数 → 零样本执行(无检索开销)
    ↓
SkillOS (2605.06614)     冻结执行者 → 训练 Curator → 学会如何管理技能(增/改/删)
    ↓
AgentEvolver (2511.10395) 全链路自主 → 自出题 + 自解题 + 自总结 → 步骤级信用分配
```

!!! tip "研究空白(综述核心结论,值得做研究的人注意)"
    - **总结者被严重低估**:14 篇里只有 SkillOS(完整训练 Curator)和 SAGE(算半个)训练了总结者,其余全部外包给闭源大模型(OpenAI o3、Gemini-2.5-Pro、Qwen-MAX)。但 SkillOS 证明**训练过的 8B Curator 优于冻结的 Gemini-2.5-Pro**——"如何管理 Skill"本身是可训练能力;
    - **空白象限**:二维空间(题目自动生成 × 总结者训练)的右上方——既自动出题又训练总结者——目前没有任何工作覆盖;
    - **横向 × 纵向融合**:SE-Agent 的横向总结与其他工作的纵向总结在第二类中未融合,是开放问题。

### 工程启示(超出综述原文的延伸)

1. **别花钱让强模型给产品蒸馏 Skill**:CoEvoSkills 证明 self-evo 优于 cross-model transfer——让产品自己的模型 self-evo,比"GPT-5 蒸馏 → 弱模型使用"更便宜且效果更好;
2. **优化"总结者"是一条轻量路径**:SkillOS 证明换 Curator 比换 Executor 更轻量——产品迭代时,先考虑"谁在总结经验、总结得好不好",而不是盲目换大模型;
3. **Skill 要抽象到可迁移的层级**:EvoSkill 的 search persistence 能从 SealQA 迁到 BrowseComp——抽象对层级,Skill 才能跨任务复用;
4. **评估缺位是第一类工作的最大痛点**:AutoSkill 甚至没有性能指标——做这类产品前先定义好"Skill 库质量"的度量,否则无法迭代;
5. **零数据路线要配客观判分器**:sliver answer 不可靠,引入代码执行器这类客观验证(Absolute Zero)才可信——呼应站内 [推理时验证](inference-time-verification.md) 的"验证不对称性"。

## 实践 / 应用:论文索引与数据集索引

### 14 篇论文索引

| 简称 | arXiv | 路线 | 一句话 |
| --- | --- | --- | --- |
| AutoSkill | 2603.01145 | 存储型 | 双环结构,Skill 动态增删改查防爆库 |
| EvoSkill | 2603.02766 | 存储型 | 三 Agent 分工 + Pareto 精英池,"失败即学习" |
| MemSkill | 2602.02474 | 存储型 | 只进化 Memory 操作的 Skill,带 RL 训练的 Controller |
| CoEvoSkills | 2604.01687v2 | 存储型 | Generator+Verifier 双子星,Skill 与测试共进化 |
| SE-Agent | 2508.02085 | 存储型 | 多策略轨迹 + 跨轨迹重组(横向总结) |
| EvolveR | 2510.16079 | RL 型 | 离线提炼原则库,在线检索指导行动 |
| SAGE | 2512.17102 | RL 型 | Sequential Rollout,序列化跑相似任务 |
| SkillRL | 2602.08234 | RL 型 | o3 蒸馏 Skill + 弱模型 RL 学会使用(蒸馏) |
| SKILL0 | 2604.02268 | RL 型 | Skill 内化进参数,三阶段渐进课程,零样本执行 |
| SkillOS | 2605.06614 | RL 型 | 训练 Curator 学会管理 SkillRepo,Executor 冻结 |
| AgentEvolver | 2511.10395 | RL 型 | 自出题/自解题/自总结,无人工标注 |
| Agent0 | 2511.16043 | 0 数据 | 出题者-解题者双 Agent 闭环(数学) |
| Tool-R0 | 2602.21320 | 0 数据 | 同 Agent0 但面向 general tool |
| Absolute Zero | 2505.03335 | 0 数据 | 单模型双角色,代码执行器当唯一判分器 |

### 评估数据集索引(17 个)

| 数据集 | 使用工作 | 类型 |
| --- | --- | --- |
| WildChat-1M | AutoSkill | 用户对话 |
| OfficeQA | EvoSkill | 办公图表(财务文档数值推理) |
| LoCoMo / LongMemEval | MemSkill | 长程对话记忆 |
| SkillBench | CoEvoSkills | 技能 |
| ALFWorld / WebShop | SkillRL、SKILL0、SkillOS | 具身/Agentic、网页购物 |
| Search-QA | SkillRL、SKILL0 | 检索问答 |
| AppWorld | SAGE | APP 交互 |
| NQ / HotpotQA / TriviaQA / PopQA | EvolveR | 检索问答 |
| DeepMath-103k | SkillOS | 数学推理 |
| GSM8K / AIME | Agent0 | 数学 |
| ToolAlpaca / SealTool / NexusRaven | Tool-R0 | 工具使用 |
| HumanEval / MBPP / LCB | Absolute Zero | 代码 |
| AIME24/25、AMC、MATH-500、Minerva、Olympiad | Absolute Zero | 数学 |

## 总结

- **三大路线**:存储型(经验写文件,模型不动)、RL 训练型(经验训进权重,当前主流)、0 数据自学型(Agent 互相出题,无人工数据);
- **范式演进**:蒸馏使用(SkillRL)→ 内化参数(SKILL0)→ 管理技能库(SkillOS)→ 全链路自主(AgentEvolver);
- **最大研究空白**:总结者训练被集体忽视(14 篇仅 2 篇涉及),"既自动出题又训练总结者"的象限无人覆盖;
- **本质问题**:如何在没有人工干预的情况下,把交互的副产物转化为下一次更强的能力——存文件、训权重、互相出题,都在回答这一个问题的不同侧面;
- **工程结论**:self-evo 优于跨模型蒸馏;训练小总结者优于冻结大总结者;零数据路线必须有客观判分器。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/fsVJiorPBN4ylGjUYBcIPw;原始资料存档于 `docs/inbox/self-evolving-agents-source.md`
- 站内:[Agent 的持续进化](../03-agents/agent-continuous-evolution.md)(工程视角:保存≠学习)、[推理时验证](inference-time-verification.md)(DeepVerifier,验证不对称性)、[评估驱动开发](../03-agents/agent-eval-driven-dev.md)、[Agent 评测](../03-agents/agent-evaluation.md)
- 基础概念延伸:GRPO(DeepSeek-R1 技术报告)、课程学习(Bengio et al. 2009)、Self-Play(Silver et al., AlphaZero)、强化学习经验回放(Lin 1992)
