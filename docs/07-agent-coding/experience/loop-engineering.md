# Loop Engineering:让 Agent 无人值守地持续迭代(中金自动化因子引擎复盘)

> **一句话摘要**:Loop Engineering 是 Anthropic Claude Code 团队提出的大模型工程范式——把"一次性提示词交互"改造成"触发—执行—校验—记录"的自动化闭环。本文以中金量化团队用 581 轮无人值守迭代挖出 69 个有效因子的实战为例,拆解这个范式,并提炼可复用到自己项目的 Agent Coding 经验。
>
> **来源**:中金研究《大模型系列(7):基于 Loop Engineering 的自动化因子发现引擎》(郑文才、周萧潇、刘均伟,2026-08-03),微信公众号 https://mp.weixin.qq.com/s/hrKdYATh_9rdASVAdjGymg

## 概念:Loop Engineering 是什么

### 大模型用法的四层演进

| 层级 | 形态 | 特征 |
| --- | --- | --- |
| **Prompt Engineering** | 模型当一次性工具 | 输入指令 → 获得输出,质量取决于提示词设计 |
| **Harness** | 引入编排层 | 多个工具和步骤串成固定流水线,模型按预设流程协同 |
| **Loop Engineering** | 赋予自主迭代能力 | 检查点持久化状态、终止条件控制循环、硬性闸门把关质量,**无人值守时持续运行并自我校正** |
| **Graph** | 升级为有向无环图 | 多个 Agent 节点按拓扑并行,各加载专属 Skill,最终汇聚输出 |

!!! note "本文案例所处阶段"
    中金这套系统当前处于 **Loop 阶段**(Sub-agent 分支已初步体现并行);Claude Code 团队在工程实践中率先提出并推广了 Loop Engineering。

### 与 Prompt Engineering 的本质区别

> 提示词工程关心**单次输出**的质量;Loop Engineering 关心的是一套**闭环系统能否在无人值守时依然稳定推进任务**。

核心转变:不再追求把单句提示词写得更好,而是把一次性交互改造成 **"触发—执行—校验—记录"** 的自动化闭环——定时调度驱动模型持续迭代、硬性校验把控产出质量、状态文件在轮次之间传递进度。

!!! tip "与"简单 for 循环调 LLM"的区别"
    每轮独立、无状态传递、无失败学习的 for 循环**不是** Loop。Loop 通过检查点持久化、失败模式规避、动态预算调整,让**每轮搜索方向都受历史经验约束**,效率随迭代累积提升。

## 原理:一个合格的 Loop 系统长什么样

### 核心循环:生成 → 审查 → 验证

```
┌────────────────────────────────────────────────┐
│ 每 5 分钟触发一轮(Loop 定时调度)                │
│                                                 │
│  生成(Sub-agent + Skill)                        │
│  ├─ 变异 25% · 交叉 25% · 参数扰动 15%          │
│  ├─ 随机探索 15% · LLM 机制引导 20%             │
│  └─ FSA 频繁子树规避:超 15% 阈值的骨架冻结      │
│      ↓                                          │
│  审查(Sub-agent + 规则过滤)                     │
│  ├─ 规则:截面算子退化/同质简化/跨量纲拒绝        │
│  └─ LLM 精判边界条件(抽样 5 个)                 │
│      ↓                                          │
│  验证(硬编码回测)                               │
│  ├─ 近 600 交易日、5 日换仓、单边千一成本        │
│  ├─ 11 项联合过滤 + IC 去重                     │
│  └─ 达标入库 + 原子写检查点                     │
│      ↓                                          │
│  记录(Hooks 输出因子库状态摘要)                 │
└────────────────────────────────────────────────┘
```

### 支撑 Loop 的四大工程机制(可复用的经验)

1. **Skill 封装**:把项目背景、算子字段定义、回测参数、工程约束固化为 Skill 模块——agent 无需重复交代背景;
2. **Sub-agents 分离**:生成与审查的 LLM 调用从编排脚本中独立出来、各自加载对应 Skill,**与验证端的硬编码回测形成隔离**——降低"单一模型自我说服"的风险;
3. **Hooks 钩子**:每轮迭代结束自动输出因子库状态摘要,便于观测与中断;
4. **检查点持久化**:记录已测试因子的哈希集合、入库因子完整信息(含 IC 序列快照与多维评分)、动量追踪器状态、迭代计数;每轮**原子写入**,任意时点中断都能断点续跑,进度不落空。

### 质量闸门:多维度把关,防"指标被反向拟合"

- **11 项联合过滤**:`|IC| > 0.03`、分年超额 > 0、夏普 > 0.5、Calmar > 1.0、近 9/12 月超额 > 0、IC 相关性 < 0.70——从预测能力、稳定性、多样性、换手率、过拟合风险多维度筛选,而非单靠 IC;
- **失败模式库**:被拒因子表达式写入库,生成阶段自动排除(失败学习);
- **FSA(频繁子树规避)**:定期统计结构骨架使用频次,超过 15% 阈值即禁止复用,防止搜索陷入同质化。

### 探索与利用的动态平衡

五种生成策略本身是"探索—利用"的具象化:

- **利用**:变异(替换子树,25%)、交叉(交换子树,25%)、参数扰动(动量引导微调窗口,15%)——在已验证的高分因子上精调;
- **探索**:随机探索(15%)保持结构广度、LLM 机制引导(20%)按未覆盖的机制族定向扩新;
- **动态预算**:某方向持续高产 → 提高变异/扰动比例;高 IC 候选大量相关性去重 → 提高随机/机制引导;某机制族长期空白 → 机制引导优先补充;入库率下降 → 提高交叉比例。

## 代码 / 实现:最小可用的 Loop 骨架

原文为研究报告,无代码。下面用纯 Python 演示 Loop 的核心——**检查点持久化 + 质量闸门 + 失败学习**,并对比"无状态 for 循环":

```python
import json, os, random

class SimpleLoop:
    """最小 Loop:带检查点、质量闸门与失败学习的迭代器"""
    def __init__(self, checkpoint=".loop-checkpoint.json"):
        self.ckpt = checkpoint
        # 断点续跑:状态全部从检查点恢复
        self.tested, self.accepted, self.failures = self._load()  # (hash集合, 已入库, 失败模式)

    def _load(self):
        if os.path.exists(self.ckpt):
            with open(self.ckpt) as f:
                d = json.load(f)
                return set(d["tested"]), d["accepted"], set(d["failures"])
        return set(), [], set()

    def _save(self):
        tmp = self.ckpt + ".tmp"                 # 原子写:先写临时文件再替换
        with open(tmp, "w") as f:
            json.dump({"tested": sorted(self.tested), "accepted": self.accepted,
                       "failures": sorted(self.failures)}, f)
        os.replace(tmp, self.ckpt)               # 中断也不会损坏状态

    def iterate(self, candidate, score):
        """一轮迭代:去重 → 质量闸门 → 记录 → 持久化"""
        h = hash(candidate)
        if h in self.tested:
            return "skipped(重复)"
        self.tested.add(h)
        if score >= 0.5:                          # 质量闸门
            self.accepted.append({"expr": candidate, "score": score})
            return "accepted"
        self.failures.add(candidate)              # 失败学习
        return "rejected"

# 模拟:无人值守跑 2000 轮(含两次中断恢复),候选质量随时间因失败学习而上升
random.seed(7)
loop = SimpleLoop()
for epoch in range(2000):
    # 失败模式学习:已失败过的结构模板不再生成
    cand = f"ma({random.choice(['overnight','amplitude','shadow'])},{random.randint(5,100)})"
    if cand in loop.failures:
        continue
    loop.iterate(cand, score=random.random() * (1 + len(loop.accepted) * 0.01))
    if epoch in (500, 1500):                      # 模拟两次中断,下次从断点续跑
        loop._save()

print(f"已测试 {len(loop.tested)} 个候选,入库 {len(loop.accepted)} 个,失败模式 {len(loop.failures)} 个")
restored = SimpleLoop()                           # 新会话:从检查点恢复,进度不丢
print(f"重启后恢复:已测试 {len(restored.tested)} 个,入库 {len(restored.accepted)} 个(断点续跑 ✓)")
os.remove(".loop-checkpoint.json")
```

**运行结果**:2000 轮无人值守迭代产出有效入库,且重启后从检查点**完整恢复进度**——这正是 Loop 与一次性调用的分水岭:状态在轮次之间传递,失败被学习,中断不可怕。

## 实践 / 应用:中金案例复盘 + 可复用的经验

### 案例结果(中金,A 股全市场)

- 581 轮迭代(每 5 分钟一轮,约 3 天)、测试 **16,939** 个候选、保留 **69** 个独立因子(成功率 0.41%);
- 28 个大类代表因子平均夏普 1.63、平均年化超额 14.5%(费后);Top 5 等权复合**夏普 3.14、年化超额 18.3%**(2025/2026 分别为 17.3%/13.9%);
- 搜索全程**三次自适应转向**:冷启动(前 50 轮)随机探索 → 平稳积累期在 overnight 骨架上密集产出(50-400 轮)→ 401-450 轮爆发(51 个因子)→ 450 轮后 FSA 冻结 overnight 骨架、方向自动扩散到影线/价格结构——**三次转向均无需人工设定规则**。

### 从中学到的 Agent Coding 经验

1. **无人值守 ≠ 放任自流**:可靠性的来源是工程机制(定时调度、检查点、硬闸门),不是模型自觉;
2. **先搭质量闸门,再放开自主性**:11 项过滤是"跑偏保险";闸门定义不清,迭代越快越危险;
3. **用状态和失败喂养循环**:检查点传状态、失败模式库传教训——每次迭代都比上次聪明一点;
4. **隔离"自我说服"**:生成与审查分开(Sub-agent),验证用硬编码,避免模型自产自销;
5. **探索与利用要显式平衡**:纯随机(探索)或纯精调(利用)都会输;动态预算让系统自己找平衡;
6. **Skill 化领域知识**:项目背景、参数、约束进 Skill 文件,换任务只改 Skill 不重构流程(呼应本站 [mattpocock/skills](../skills/mattpocock-skills.md) 与 [AI Friendly 架构](../../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md) 的 SKILL 化思想)。

### 局限(诚实的一面)

信号源高度集中(overnight 出现率 85%)、多样性不足;搜索仅 3 天,替代信号源尚未建立同等质量;数据限于日频价量,天花板受输入维度限制——**Loop 能加速收敛,但不能凭空创造信息源**。

## 总结

- Loop Engineering = 把单次交互改造成"触发—执行—校验—记录"的自动化闭环,让系统**无人值守地持续迭代并自我校正**;
- 四大工程机制:**Skill 封装、Sub-agent 分离、Hooks 观测、检查点持久化**;
- 质量靠**多维度闸门 + 失败学习 + 结构规避**;方向靠**探索-利用动态平衡**;
- 中金案例证明其真实生产力(3 天无人值守挖出 69 个有效因子),也暴露局限;
- 对个人 Agent Coding 的启示:做任何"让 agent 反复迭代出结果"的任务(调参、写文章、改代码),都可以套用这个 Loop 骨架。

## 延伸阅读

- 站内:[个人 Agent Coding 经验](../index.md)、[Harness 框架与开源方案](../../08-harness/index.md)(Harness → Loop → Graph 的层级)、[Agent 评测](../../03-agents/agent-evaluation.md)(质量闸门与评测方法论)、[AI Friendly 后端架构](../../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md)
- 外部:原文《大模型系列(7):基于 Loop Engineering 的自动化因子发现引擎》(中金研究);Anthropic 关于 Loop Engineering 的工程实践材料;原始资料存档于 `docs/inbox/loop-engineering-source.md`
