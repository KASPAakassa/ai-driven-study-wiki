# TencentDB Agent Memory:给 Agent 加外部记忆,长任务省 50% Token

> **一句话摘要**:腾讯云数据库开源的 **Agent Memory 插件**(18K+ stars):把对话沉淀为 L0-L3 四层记忆、跨会话召回,并把大段源码/日志卸载到外部文件、只留轻量任务图——实测让长任务 Token 消耗减少约 55.7%。Hermes、OpenClaw 等 Harness 均可接入。
>
> **来源**:微信公众号《接入这个开源插件,让我 Token 直接省了 50%》(郭震AI),https://mp.weixin.qq.com/s/0fPugD831YYhjWxkw8QV5w;仓库 https://github.com/TencentCloud/TencentDB-Agent-Memory

## 概念:为什么需要"外部记忆"

让 AI 完成同一任务,怎么少用 Token?代码分析、资料搜索这类**长任务**的问题在于:对话越往后,AI 每次都要带着前面的代码、日志和要求重新思考一遍——**任务没完成,Token 已消耗不少**。

会话内的记忆(上下文)不是答案,因为它会随着换会话而丢失,还会随长度膨胀而越来越贵。方案是给 Agent 加**外部记忆**:把暂时用不到的长内容先存起来,只把当前真正需要的信息留在对话里。

!!! note "与 Harness 的关系"
    记忆是 Harness 的核心能力之一(对应 [AI Friendly 架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md) 中 Harness 的"上下文装载层"与记忆组件)。这个插件是"外部记忆"能力的现成开源落地。

## 原理:四层记忆 + 上下文卸载

### L0-L3 四层记忆:从事实到画像

插件把每次协作自动沉淀成**可查看、可纠错、可复用**的四层记忆资产:

| 层级 | 内容 | 例子 |
| --- | --- | --- |
| **L0** | 原始对话事实 | 完整保存每次对话内容 |
| **L1** | 长期要求 | "Project-47""中文输出""先结论、后证据"等要求;退出会话仍保留 |
| **L2** | 项目/任务场景 | 按项目归类成可复用场景块(如"Excel 可视化项目""Agent Memory 分析任务") |
| **L3** | 用户画像 | 多轮对话后形成的稳定画像:开发能力、协作方式、工具偏好 |

**跨会话召回**:新会话中,Agent Memory 自动注入项目场景与用户画像——无需重新搜索就能恢复工作要求和协作习惯,"让 AI 越用越懂你"。

### 上下文卸载(Offload):省 Token 的核心逻辑

面对长任务:

1. 工具产生的大段原始结果(源码、日志、搜索结果)自动保存到**外部 `refs` 目录**;
2. 任务完成后生成一份 **Offload 索引文件**(实测 23KB),供按需回查;
3. 把长任务压缩成一张 **Mermaid 任务图**:做过什么、进展到哪一步、哪里受阻,通过 `node_id` 保留;

!!! tip "省 Token 的核心逻辑"
    主上下文只保留**任务摘要 + 索引**;需要核对细节时,再通过 `node_id` 找回原始内容——上下文从"全量携带"变成"按需取用"。

## 代码 / 实现:接入 Hermes / OpenClaw

```bash
# 1. 获取源码到本地,切到对应目录执行安装脚本(Windows 示例)
.\scripts\setup-hermes-memory-tencentdb.bat

# 2. 为插件配置一个大模型,管理长短任务记忆处理(启动后 8420 端口监听即成功)

# 3. 在 Hermes 中接入
hermes config set memory.provider memory_tencentdb
```

OpenClaw 接入方法类似。**默认使用本地 SQLite**——个人开发者不需要先买云数据库,也不用自己搭一套复杂的 RAG 工作流。

## 实践 / 应用

### 实测效果(作者个人数据,非官方基准)

- 同一个会话、同一个模型、同一份提示词:压缩前单次调用 **32,935 Token** → 开启后 **15,974 Token**;
- 长任务实测整体 **Token 消耗减少约 55.7%**;
- 折线图显示:第六轮发生一次压缩后,后续上下文直接缩短。

### Memory Hub:从单 Agent 到团队记忆资产

团队版提供 **Memory Hub**,把 Chat Memory、Skill、Wiki 和 CodeGraph **统一变成可查看、可审核、可分配的团队记忆资产**(管理团队、Agent、记忆资产、版本、权限、绑定关系)。对**一人公司(OPC)和多 Agent Loop** 特别实用:

> 调研 Agent 找到的信息 → 交给开发 Agent;测试和复盘经验 → 沉淀为 Skill。一个人也能组建一支**会共享记忆、不断积累经验的 Agent 小队**。

### 借鉴意义

1. **记忆是省 Token 的杠杆**:上下文卸载(摘要 + 索引 + 按需取回)比"全量塞上下文"高效得多,可复刻到任何长任务 harness;
2. **记忆分层是通用的**:L0-L3(事实→要求→场景→画像)的分层思路,比单层记忆更利于跨会话复用与治理;
3. **选型注意**:默认 SQLite 适合个人起步;团队规模上量后再考虑云数据库;不同 Harness 的接入方式看各自插件生态。

## 总结

- TencentDB Agent Memory = **团队级记忆中枢**:L0-L3 四层记忆 + 跨会话召回 + 上下文卸载;
- 省 Token 核心:**长内容外置、上下文只留摘要和任务图、node_id 按需回查**(实测省 ~55.7%);
- 默认本地 SQLite、免云数据库/RAG,上手成本低;Memory Hub 支持团队记忆资产治理;
- 记忆是 Harness 的标配能力——"没有记忆的 AI 只是工具,有记忆的 AI 才会随使用不断升值"。

## 延伸阅读

- 站内:[Harness 章节首页](index.md)、[配套开源方案](harness-tools.md)(记忆类条目)、[AI Friendly 后端架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md)(Harness 上下文装载层)、[Loop Engineering](../07-agent-coding/experience/loop-engineering.md)(无人值守长任务)
- 外部:仓库 https://github.com/TencentCloud/TencentDB-Agent-Memory;原始资料存档于 `docs/inbox/agent-memory-source.md`
