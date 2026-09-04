# Agent 记忆体系:短期、长期、写入闸门与记忆整合

> **一句话摘要**:LLM 是无状态的——每次调用都是白纸。"记忆"要靠外部系统:短期记忆拼 prompt、长期记忆靠向量库,而**记忆质量取决于写入闸门和整合策略**。本文讲清记忆机制的分层、什么该记、怎么整合,以及 MemGPT/Zep 等产品化的策略。
>
> **来源**:综合公开资料,基于《2026 AI Agent 技术栈全景图》(merlinfeng,https://mp.weixin.qq.com/s/hy35QS327__ntlNWAPFHeQ)深化扩充;参考 Mem0/MemGPT/Zep 文档与 [TencentDB Agent Memory](../08-harness/agent-memory-plugin.md)

## 概念:LLM 无状态,记忆靠外挂

!!! warning "说三遍的事实"
    LLM 是无状态的。上次对话告诉它"我叫张三",这次它不知道——**每次 API 调用都是独立请求**。我们觉得 ChatGPT"记得"对话,是因为应用层把历史消息每次重新塞进 prompt。

因此"Agent 记忆"= **一组外部系统 + 策略**,把需要跨会话/跨任务保留的信息存取起来。它分两条主线:记多久(短期/长期)、记多好(写入/整合/衰减)。

## 原理 1:短期记忆——把历史拼进 context window

短期记忆的真相:**把历史对话拼进 prompt**。简单粗暴,但受两个硬约束:

| 约束 | 说明 |
| --- | --- |
| **窗口长度** | 128K token 听着多,塞长文档 + 几十轮对话就满了 |
| **注意力衰减** | 塞得越多,模型对中间内容关注越差——"lost in the middle"现象 |

!!! tip "短期记忆的工程优化"
    见 [Context Engineering](context-engineering.md):滑动窗口、摘要压缩、外部卸载(Offload)、子 Agent 隔离——"上下文是 Agent 的眼睛",短期记忆的质量直接决定单任务表现。

## 原理 2:长期记忆——向量检索作为标准实现

长期记忆靠外挂,主流方案是**向量检索**:

```
要记的内容 → 切块 → 算 embedding → 存向量库
用时 → 按语义相似度捞相关块 → 塞进 prompt
```

这就是 **RAG**——在 Agent 里它不只做知识库问答,也是**长期记忆的标准实现**。向量库选型:自部署 Milvus/Qdrant、托管 Pinecone、轻量 Chroma(选型细节见 [生产级 Agent 9 层架构](ai-infra-layering.md) L2/L6)。

## 原理 3:写入闸门——"什么该记"比"怎么记"难

!!! warning "最常见的坑"
    无脑记所有对话 → 三个月后向量库里全是"今天天气怎么样"这种垃圾 → 检索质量直线下降。**垃圾进,垃圾出。**

解法:**记忆写入闸门**——写入前让一个 LLM 先判断这条信息值不值得记(用户偏好、关键决定、重要事实才记),垃圾一律丢弃。

```python
# 概念演示:记忆写入闸门(生产中用 LLM 调用替代简单关键词)
def memory_gate(info: str) -> bool:
    """判断一条信息是否值得写入长期记忆"""
    important_markers = ["偏好", "决定", "注意", "喜欢", "不喜欢", "项目",
                         "截止", "客户", "账号", "记住"]
    return any(m in info for m in important_markers)

for info in ["今天天气怎么样", "我偏好简报控制在 200 字", "这个项目 9 月上线"]:
    print(f"{'✅记住' if memory_gate(info) else '❌丢弃'}: {info}")
# 输出:❌丢弃:今天天气怎么样 / ✅记住:我偏好简报控制在 200 字 / ✅记住:这个项目 9 月上线
```

## 原理 4:记忆整合与衰减——从"堆记忆"到"长经验"

人脑不是简单堆记忆的,而是把零散经历**整合成经验**。Agent 的对应做法:

| 机制 | 做法 | 价值 |
| --- | --- | --- |
| **整合(Consolidation)** | 定期后台任务把近一周记忆块聚类、总结、压缩成几条"经验",原始细节删掉 | 去冗余,检索质量不随数据膨胀下降 |
| **衰减(Decay/TTL)** | 记忆带时间戳,过期或不再被引用的自动降权/删除 | 防止旧信息污染新决策 |
| **分层(Staging)** | 短期(上下文)→ 工作记忆(近期)→ 长期(向量库)→ 画像(稳定的用户/项目特征) | 按需加载,成本可控 |

!!! note "产品化服务"
    MemGPT 把"操作系统式"的内存分层(product化),Zep/Mem0 把写入、整合、衰减策略打包成服务——**不用自己造轮子**。四层记忆(L0-L3)的落地案例见 [TencentDB Agent Memory](../08-harness/agent-memory-plugin.md)。

## 代码 / 实现:记忆整合的最小演示

原文为机制介绍。下面用纯 Python 演示"写入闸门 + 定期整合"的协作(可运行):

```python
import collections

class MemorySystem:
    def __init__(self):
        self.raw = []            # 短期:待整合的记忆块
        self.consolidated = []   # 长期:整合后的经验

    def write(self, info, gate_fn):
        """写入闸门:值得记才进短期池"""
        if gate_fn(info):
            self.raw.append(info)
            return "已写入"
        return "已丢弃(垃圾)"

    def consolidate(self, summarize_fn):
        """定期整合:把零散记忆聚合成几条经验"""
        if not self.raw:
            return "无可整合"
        # 简化:按主题前缀聚类,再逐类总结(生产中用 embedding 聚类 + LLM 总结)
        groups = collections.defaultdict(list)
        for m in self.raw:
            groups[m.split(":")[0]].append(m)
        self.consolidated = [summarize_fn(k, v) for k, v in groups.items()]
        self.raw.clear()          # 原始细节删掉(可选:归档)
        return f"整合出 {len(self.consolidated)} 条经验"

def gate(info): return "天气" not in info
def summarize(key, items): return f"[经验:{key}] 共{len(items)}条:首条={items[0][:20]}"

mem = MemorySystem()
print(mem.write("天气:今天晴", gate))            # 丢弃
print(mem.write("偏好:简报 200 字", gate))        # 写入
print(mem.write("项目:9 月上线", gate))           # 写入
print("整合:", mem.consolidate(summarize))
print("长期记忆:", mem.consolidated)
```

**运行结果**:垃圾("天气")被闸门丢弃;两条有用信息写入后,整合任务把同类记忆聚合成"经验",原始细节清空——这就是"短期拼 prompt、长期靠向量库、质量靠写入闸门和整合策略"的最小闭环。

## 实践 / 应用:落地清单

1. **先分层**:明确短期(上下文)/ 长期(向量库)/ 画像(稳定特征),别一锅烩;
2. **写入闸门必装**:宁缺毋滥,垃圾进库比不进更糟;
3. **定期整合**:设后台任务做聚类 + 压缩(频率与业务节奏匹配);
4. **衰减策略**:带 TTL,旧记忆不自动参与决策;
5. **能买不造**:复杂记忆策略直接上 Mem0/Zep/MemGPT/腾讯 Agent Memory,自研投入产出比低;
6. **权限与隐私**:记忆里含 PII 时必须脱敏 + 权限隔离(呼应 [AI Friendly 后端架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md) 的 L0-L5 分级)。

## 总结

- LLM 无状态,"记忆"是外部系统 + 策略;**短期拼 prompt,长期靠向量库(RAG)**;
- 短期受窗口长度与注意力衰减(lost in the middle)约束;
- **记忆质量取决于写入闸门**(什么该记)和**整合/衰减策略**(怎么从堆记忆长成经验);
- 分层(短期/工作/长期/画像)+ 产品化服务(Mem0/Zep/MemGPT)是工程正道。

## 延伸阅读

- 站内:[Context Engineering](context-engineering.md)(短期记忆工程化)、[RAG](../02-llm/rag.md)(长期记忆载体)、[TencentDB Agent Memory](../08-harness/agent-memory-plugin.md)(四层记忆落地)、[Agent 持续进化](agent-continuous-evolution.md)(记忆与学习的区别)
- 外部:MemGPT / Zep / Mem0 文档;原文《2026 AI Agent 技术栈全景图》
