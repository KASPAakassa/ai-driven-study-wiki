# Harness Handbook:行为定位与可演化 Agent 系统(论文解析 + 知识库汇总)

> **一句话摘要**:当 Agent 真正在电脑里读文件、调用工具、保存记忆并持续运行时,模型只是"发动机"——把发动机变成可工作的机器,还需要一整套 harness(运行框架/执行外壳)。但 harness 越来越复杂时,一个更前置的问题浮现:**"某个行为到底由哪些代码共同实现?"**(behavior localization,行为定位)。论文《Harness Handbook》(arXiv:2607.13285)用三层文档树 + 状态寄存器视图 + BGPD 工作流回答这个问题:改代码之前,先找到完整的行为。
>
> **来源**:微信公众号「V1ki」《模型之外,谁在决定 Agent 的上限?读懂 Harness Handbook》(Zero 协助,论文解读),https://mp.weixin.qq.com/s/2flGfsCAevLXPTIy8iEGXw;论文:Ruhan Wang 等《Harness Handbook: Making Evolving Agent Harnesses Readable, Navigable, and Editable》,arXiv:2607.13285v1 (2026-07-14, CC BY 4.0),https://arxiv.org/abs/2607.13285;项目:https://ruhan-wang.github.io/Harness-Handbook/;代码:https://github.com/Ruhan-Wang/Harness_Handbook;原始资料存档于 `docs/inbox/harness-handbook-wx-source.md` 与 `docs/inbox/harness-handbook-paper-source.md`

## 概念:harness 不再只是"胶水代码"

!!! tip "一个概括性公式(非论文原文)**
    **Agent 的可用能力 = 模型能力 × harness 提供的观察、行动、状态与约束。** 换模型不一定改变系统行为;但改掉一次重试、一次状态清空或一个工具返回值的处理方式,可能立刻改变 Agent 的可靠性。

一个现代 Agent 的 harness 负责:**提示词构造、上下文装配、状态管理、工具调用、权限边界、循环控制、错误恢复、子 Agent 协调、外部环境交互**。麻烦在于——需求用"行为语言"表达("任务完成后必须二次确认"),仓库却按文件、类和函数组织;一个行为可能散落在提示模板、主循环、解析器、状态对象和异常分支中。**知道"要改什么",不等于知道"该改哪里"。**

!!! note "行为定位(behavior localization)"
    找出实现某项目标行为的**全部**代码位置——重点是"全部":只找到主路径而漏掉冷门分支,计划看似合理,落地后却出现行为不一致。论文指出:这是 **harness 演化的核心瓶颈**,尤其影响跨文件功能、低频路径和跨模块状态交互。

**为什么在 Agent harness 中更尖锐**(论文观点 + 作者判断):harness 高度状态化,控制流常由模型输出、工具结果和环境事件共同决定;同一行为可能跨越多轮执行。普通"代码地图"记录结构,harness 更需要一张"**运行语义地图**"。传统关键词搜索擅长找名称不擅长找语义;调用图答"谁调用谁"不答"哪些节点共同实现任务完成语义";把整个仓库塞进长上下文只是扩大可见范围,不能自动建立行为到实现的映射。

## 原理:Harness Handbook 表示与 BGPD 工作流

### 1. Handbook:三层文档树 + 状态寄存器视图

| 层 | 内容 |
| --- | --- |
| **L1 系统级总览** | 整体运行方式和主要阶段 |
| **L2 阶段级概览** | 各阶段职责、输入输出与关系 |
| **L3 源码支撑细节单元** | 落到函数/函数片段/文件,带可回到当前代码的 locator |

**状态寄存器视图**("寄存器"不是 CPU 寄存器,是跨阶段共享状态的抽象):记录关键状态由哪个阶段**写入、读取、清空或重置**。例如"连续完成确认次数"可能在结果解析阶段写入、循环控制阶段读取、新任务开始时重置——只看目录树容易漏掉其中一处,状态视图沿数据生命周期追踪行为。

!!! tip "构建流水线 + 安全阀**
    先用静态分析提取程序事实(Phase I),再借助 LLM 做行为化组织(Phase II:function-as-leaf / file-as-leaf),最后分层综合与打包(Phase III)。关键约束不是"自动生成文档",而是三项组合:**行为优先、源码可追溯、变更后可同步**——L3 定位必须回到当前仓库验证,失效条目被冻结排除(不让旧文档凌驾于源码),代码变化后触发局部重同步。

### 2. BGPD:不要一上来就把整个仓库倒给 Agent

**Behavior-Guided Progressive Disclosure(行为引导的渐进式披露)** 路径:

```
① 从 L1/L2 判断需求涉及哪些执行阶段
② 沿状态寄存器补入共享状态耦合的远端阶段
③ 选择 L3 条目,取得候选源码位置
④ 沿调用关系适度扩展
⑤ 打开当前仓库,重新验证 locator(源码是最终裁判)
⑥ 只基于验证后的证据生成编辑计划
```

它不是用文档替代代码搜索,而是**先用行为地图缩小搜索空间,再让源码作最终裁判**;上下文不是越多越好——先给轮廓,再按任务揭示阶段、状态与实现细节,减少噪声。

!!! note "编辑计划与重同步(附录 B)**
    计划用 EDIT BLOCK 格式:old_string 必须从 `read_file` 输出 **byte-exact 复制**(绝不重打、绝不意译),同文件块不重叠、按序执行;结束时输出 declarations JSON(`will_modify`/`will_add`/`will_remove`,重命名 = remove+add),供 handbook-resync 管道消费。自动重同步四步:版本对齐 → 范围更新 → 保守处理 → 验证打包。

## 代码 / 实现:状态寄存器追踪 + BGPD 路由模拟(纯 Python)

把论文最核心的两个机制落成可运行演示(以附录 E 的"三次完成确认"为例):

```python
# —— 1) 状态寄存器视图:追踪一个状态的所有读写清站点 ——
REGISTER = {"name": "completion_confirmations"}

def register_sites():
    """reg-pending-completion 的读写清站点(附录 E 真实定位)"""
    return {
        "write":   ["Terminus2.__init__ (~L292) 初始化为 0",
                    "Terminus2._run_agent_loop (~L1427-1440) 每次完成标记 +1"],
        "read":    ["Terminus2._run_agent_loop (~L1552-1559) 完成门判断"],
        "reset":   ["Terminus2._reset_per_run_state (~L1574) 每次 run 前清零"],
    }

# —— 2) BGPD 路由:从行为 → 阶段 → 寄存器 → 源码位置(渐进披露)——
def bgpd_route(request, handbook_l1, stages, registers):
    """先缩小搜索空间(L1/L2/寄存器),再给候选源码位置;源码最后验证"""
    intent_stages = [s for s in stages if s in request]       # L2 阶段匹配
    regs = [r["name"] for r in registers
            if any(s in request for s in r.get("related_stages", []))]
    return {"stages": intent_stages, "registers": regs,
            "advice": "再沿寄存器读写站点打开候选源码验证,不要凭目录猜"}

# —— 演练:附录 E 的请求 ——
request = "模型需连续三次标记 task_complete 才被评分(完成门确认)"
route = bgpd_route(request,
                   "L1: 运行主循环含完成门",
                   stages=["完成门", "命令执行", "运行前重置"],
                   registers=[{"name": "reg-pending-completion",
                               "related_stages": ["完成门", "运行前重置"]}])
print("BGPD 路由:", route)
print("\n状态寄存器站点:")
for kind, sites in register_sites().items():
    for s in sites:
        print(f"  [{kind:5}] {s}")
```

## 实践 / 应用:实验数字、局限与知识库汇总

### 实验数字(论文报告,注意测了什么)

| 指标 | Codex | Terminus-2 |
| --- | --- | --- |
| 计划胜率 | 28.3% → **38.3%** | 26.7% → **45.6%** |
| 规划 token | 10.2万 → 8.9万(-12.7%) | 5.8万 → 5.3万(-8.6%) |
| 文件/符号粒度 F1 | 全部 24 项提高(+5.0-18.8pp) | 同 |
| "完全零重合" Wrong | 最多下降 25.9pp | 同 |

- 实验配置:两个开源 harness × 各 30 修改请求 = 60;规划器统一 DeepSeek-V4-Pro;GPT-5.5/Opus 4.8/DeepSeek-V4-Pro 评审;
- **最大增益出现在**:散落实现站点、低频执行路径、跨模块交互的改动;
- **"弱模型匹配强模型"**:Handbook 辅助下,弱规划器对参考计划位置的接近程度显著提升。

### 局限(论文自陈 + 作者核验)

1. 只评**编辑计划质量**,不验证补丁与测试(端到端正确率未知);
2. 样本小(两个 harness、60 请求),LLM 裁判不是人工金标准;
3. Handbook 构建与重同步成本未完整计入;
4. 静态分析难覆盖反射、动态加载、配置驱动流程和外部服务;
5. 缺各组件消融、缺与成熟代码索引/RAG 系统的充分对比;
6. 仓库目前无明确 LICENSE,完整评测代码未公开(作者核验:静态分析流水线可运行,但不应把基础运行包装成"复现成功")。

!!! warning "证据等级声明(原文)**
    本文讨论的是论文 v1 和作者公开代码——刚刚发布,尚无独立复现、同行评议或长期生产验证。读者应区分"作者结论"与"本文判断"。

### 与现有知识库的汇总整合(五条主线)

1. **Harness 章节(08-harness)**:本论文是"Harness 是一等公民"的学术支撑——与 [云端软件工厂](../08-harness/cloud-software-factory.md)(Loop/Harness/Factory 拓扑)、[Agent Harness 发展史与竞争格局](../08-harness/harness-history-landscape.md)、[AgentScope](../08-harness/agentscope-managed-agents.md)(控制面/数据面)互相印证:harness 是决定 Agent 上限的执行外壳,而本论文补上"**harness 自身如何被演化**"这一环;
2. **行为定位 vs 传统代码索引**:与 [高德知识库](../06-enterprise/ontology-agent-adoption/ai-native-knowledge-base-gaode.md) 的检索哲学同构——高德用"意图识别→路由→直达→并发召回"让查询命中正确知识;Handbook 用"行为→阶段→寄存器→源码验证"让**修改请求**命中正确代码;两者都把"定位"作为一等能力;
3. **可演化性设计**:与 [Agent 架构反熵增](../03-agents/agent-architecture-antientropy.md) 的"可替换性/ADR/双写"互补——反熵增讲**如何设计**让系统可演化,Handbook 讲**演化时如何定位**(先定位影响面,再生成编辑计划);
4. **编辑计划纪律**:EDIT BLOCK 的 byte-exact 原则与 [Agent 系统设计的 5 个决策](../03-agents/agent-system-5-decisions.md)"验证命令硬条件"、[Spec-First 决策栈](../07-agent-coding/experience/spec-first-decision-stack.md)"证据分级"是同一纪律:计划必须建立在**验证过的真实事实**上,不凭记忆、不靠猜;
5. **对 Agent 系统开发的启示**(论文给 Zero 类系统的五点):把"行为目录"提升为一等资产;显式追踪任务、授权、后台句柄、记忆写入和验证状态;让 Agent 先定位影响面再生成编辑计划;让文档条目绑定文件/符号/范围/哈希,验证失败即冻结;把行为条目连接到测试、运行轨迹、权限规则与历史事故。

## 总结

- **核心问题**:behavior localization(行为定位)——找到实现某行为的**全部**代码位置,是 harness 演化的核心瓶颈;
- **核心表示**:Harness Handbook = 三层文档树(L1 总览/L2 阶段/L3 源码单元)+ 状态寄存器视图(状态读写清重置);行为优先、源码可追溯、变更后可同步;
- **核心工作流**:BGPD 渐进披露——先缩小搜索空间(行为地图),再让源码作最终裁判,只基于验证后的证据生成编辑计划;
- **核心数字**:计划胜率 Codex +10pp / Terminus-2 +19pp,规划 token -9%~-13%,24 项定位指标全部提升;
- **一句话**:当软件开始帮助修改自身时,必须先让"**行为如何落到代码**"成为显式、可核验的系统资产——harness 的演化,从"改哪里"的可追溯开始。

## 延伸阅读

- 论文:https://arxiv.org/abs/2607.13285(HTML:https://arxiv.org/html/2607.13285v1);项目:https://ruhan-wang.github.io/Harness-Handbook/;代码:https://github.com/Ruhan-Wang/Harness_Handbook;HF:https://huggingface.co/papers/2607.13285;HN:https://news.ycombinator.com/item?id=48863269;解读原文:https://mp.weixin.qq.com/s/2flGfsCAevLXPTIy8iEGXw
- 站内学术章节:[推理时验证(DeepVerifier)](inference-time-verification.md)、[自进化 Agent 综述](self-evolving-agents-survey.md)(09 学术三篇并列);[云端软件工厂](../08-harness/cloud-software-factory.md)、[Agent Harness 发展史](../08-harness/harness-history-landscape.md)、[高德知识库](../06-enterprise/ontology-agent-adoption/ai-native-knowledge-base-gaode.md)、[Agent 架构反熵增](../03-agents/agent-architecture-antientropy.md)、[Spec-First 决策栈](../07-agent-coding/experience/spec-first-decision-stack.md)
