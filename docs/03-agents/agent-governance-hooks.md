# Agent 治理设计:用 Hook 堵住 LLM 的偷懒、越权与失忆

> **一句话摘要**:prompt 是软约束,不是安全边界。数仓 Agent 引擎 DECO 的实践证明:LLM 处理长文本会"偷懒"(截断/略写)、对生产环境会"越权"(未确认发布)、上下文传递会"失忆"(该查的不查)——这三类问题**不是 prompt engineering 能解决的**。唯一解法是在 Agent 框架层用 Hook 切面做确定性兜底:读写两侧 offload + 引用句柄治偷懒、beforeTool 守卫 + HITL 治越权、Hook 采集 → state → Attachment 闭环治失忆。
>
> **来源**:微信公众号「腾讯程序员」《Agent 治理:用 Hook 堵住 LLM 的偷懒、越权与失忆》(作者:xiangnzhang,DECO 实践系列·护栏层),https://mp.weixin.qq.com/s/ISwjIw5lj7JlcQJV7BOx5g;原始资料存档于 `docs/inbox/deco-hooks-source.md`

## 概念:三类"prompt 管不住"的问题

!!! tip "一句话定位"
    **prompt 定意图,Skill 定规矩,框架 Hook 定边界——能用确定性兜底的,别交给模型。**

| 问题 | 表现 | 为什么 prompt 管不住 |
| --- | --- | --- |
| **LLM 偷懒** | 处理上千行 SQL/Python ETL 时截断、占位略写(`-- 其他字段...`)、跳步骤、复印式重写到 token 耗尽 | 长 SQL 是**物理上超出 token 预算** |
| **越权操作** | 发布、回刷、冻结/解冻、终止实例等不可逆动作,不打招呼直接调 | 模型无法区分"查询"和"发布"的**可逆性差异** |
| **上下文失忆** | 改完表不去分析下游风险、产出图表不知告诉用户("需要查的就不查") | 主动探测 = 额外一次 tool call = 多耗 token,模型追求**最短完成路径** |

!!! warning "设计原则:基础设施和推理逻辑解耦"
    Hook 切面上的逻辑独立运作,模型的 ReAct 循环不用感知;新增/删除一个 Hook,**主流程一行代码都不用改**。

## 原理:三道护栏的设计

### 护栏一:长文本完整性(治偷懒)——读写两侧 offload + 引用句柄

**核心思路:让长 SQL 从 LLM 上下文里"消失",全文走文件通道**——LLM 永远不直接接触脚本全文,上下文里只有一句引用句柄:

```
<offloaded to /sandbox/order_detail.remote.etl (read-only snapshot, length=37814 chars).
 To start editing, run copy_file(...) first, then str_replace.>
```

| 侧 | Hook | 动作 | 失败语义 |
| --- | --- | --- | --- |
| **拉取侧 Offload** | afterTool | 含 `scriptContent` 的响应 → 全文写沙箱只读快照 → 替换为引用句柄 | **降级透传**(落盘失败返回原内容,承担自截断风险,不阻塞主流程);数组逐条独立判定,一条失败仅该条降级 |
| **写回侧 Onload** | beforeTool | 从沙箱文件读全文**覆盖**入参 → 转发前剥离 `scriptFilePath` 字段 | **阻断**(文件不在白名单/身份缺失/内容为空 → 抛异常,杜绝发布残缺脚本) |

**关键设计**:
- **只读快照 / 工作副本分离**:必须显式 `copy_file` 才能开始编辑(防提前误改),LLM 只用 `str_replace` 小步改写;
- **scriptContent / scriptFilePath 互补参数协议**:`scriptFilePath` 是纯框架契约——下游实现侧不消费它(无感知,协议不用改),Hook 层独立演化;下游对 `scriptFilePath` 留 `log.warn`(到达工具时它本应已被剥离,还在就是 Hook 失效信号);
- **效果**:修改任务时模型只输出脚本路径,全文由框架后台对齐——**工具调用输出 token 直降约 90%**;SQL 复印自截断从"概率近 100%"物理消除(只走 str_replace 小步改)。

!!! note "行业对比:现成的 vs 必须自研"
    ADK Artifacts 和 LangGraph DeepAgents 都有**读侧** offload(工具结果落盘),但都没有**写侧** onload——因为大部分 Agent 场景不需要把长产物原样发回外部 API。DECO 的数仓场景有"写长 SQL"的保存工具,所以必须两端对称 offload,并自研写回加固(参数交换契约/快照副本分离/注释块按字段名剥离/列级 offload/失败语义按代价差异化)。

### 护栏二:危险操作确认(治越权)——配置驱动 beforeTool 守卫 + HITL

!!! tip "通法:写操作不可逆,护栏必须在框架层"
    prompt 是软约束,不是安全边界。任何"做了就回不去"的操作(发布/回刷/冻结/终止)都必须有一道代码级强制确认:**没拿到用户明确授权,工具就是不能执行**。这道闸必须在框架里,不能信 LLM。

**配置驱动的危险工具守卫**(挂在 beforeTool,统一调度):

```yaml
deco:
  dangerous-tools:
    - name: packCommit
      required-state: confirm_pack
      hint: "需要用户先选择发布方式"
      confirmation:
        title: "请确认发布方式"
        options:
          - {id: direct,    label: "直接发布（免审批）", value: direct}
          - {id: approval,  label: "提交审批", value: approval, hasInput: true,
             inputPlaceholder: "请输入审批人RTX", inputType: text}
          - {id: draft,     label: "保存草稿", value: draft}
          - {id: edit_more, label: "我再改改", value: edit_more}
```

**守门流程**:拦截 → 弹框 → 用户选择(写进 session.state)→ 续跑 → 守卫放行。确认框支持带输入控件(填审批人/回刷日期),不只是 yes/no。多个危险工具各配授权标记(confirm_pack/confirm_deploy/confirm_upsert_datasource/confirm_transfer_task_upsert),同一套 Guard 统一管控。

!!! warning "必须框架层拦,不能信 LLM"
    这套机制从框架层阻断 LLM 绕过 prompt 直接调危险工具;确认动作只能由真实用户在前端触发——无论 Agent 是自作主张还是被诱导,只要没有人工确认这一步,危险工具在框架层就物理走不通。

### 护栏三:上下文联动闭环(治失忆)——Hook 采集 → state → Attachment 注入

**范式核心**:把"副作用采集"和"上下文注入"解耦成两段——Hook 管"发生了什么",Attachment 管"下一轮告诉模型什么"。

```
工具调用 → Hook 强制采集(确定性,不靠 LLM 记得去查)
        → 写 state(累积)
        → Attachment 注入下一轮 prompt(时机正确,不污染当前轮)
```

对比"让 LLM 自己记得去查":

| 方案 | 可靠性 | token 开销 | LLM 偷懒风险 |
| --- | --- | --- | --- |
| prompt 写"改表后记得分析风险" | ❌ 软约束 | 无额外 | ✅ 高(可能跳过) |
| 单独发一轮"请分析风险" | 🟡 依赖调度 | 额外一轮 | ✅ 中(可能敷衍) |
| **Hook 采集 → state → Attachment** | ✅ 确定触发 | 无额外(结果复用) | ❌ 零(不依赖 LLM 自觉) |

**案例一 RiskAnalysisHook**(改表后自动注入风险分析):挂在 afterTool,**不看工具名硬判断,看入参**——带 `tableId` 参数的 `upsertTable` 才是改表(新建表不带,跳过);风险结论累积写 state,下一轮一次性注入,LLM 自然输出"⚠️ 风险提示:修改了 dws_order_detail 表字段,下游 dws_channel_report (HIGH) 依赖 order_amount……建议检查 ETL"。

**案例二 PythonImageHook**(自动发现并呈现生成产物):beforeTool 加文件快照、afterTool 对比(比让 LLM 用 bash ls 查可靠);只关注图片格式(.png/.jpg/.svg,不处理脚本数据文件);预签名 URL 写成结构化 JSON,前端据此渲染内联图片。

!!! warning "信息不对称:不是'忘了查',是根本不知道有东西该查"
    LLM 调 Python 工具时只知道脚本跑完了——它不知道脚本产出了 chart.png,因为工具返回的 stdout/stderr 没提。**这不是"忘了查",而是 LLM 是"瞎子"**。确定性兜底只有一个:不让 LLM"决定要不要查",框架在工具执行后强制采集、结果自动注入下一轮 prompt。

## 代码 / 实现:三道护栏的最小演示(纯 Python)

把 offload/HITL/state-Attachment 的核心决策逻辑落成可运行代码:

```python
# —— 1) 写侧 Onload:从文件加载全文覆盖入参;文件不可用则阻断 ——
def onload_script(script_content, script_filepath, sandbox_ok=True):
    if script_filepath and sandbox_ok:
        with open(script_filepath, encoding="utf-8") as f:
            return f.read(), "onload: 全文已从沙箱加载,覆盖入参"
    if len(script_content) > 5000:                      # 无文件可用且超长 → 阻断
        return None, "BLOCK: 长脚本无法落盘校验,禁止提交(防残缺上线)"
    return script_content, "透传: 短内容直接入参"

# —— 2) 危险工具守卫:没授权就物理走不通 ——
DANGEROUS = {"packCommit", "deployCommit", "rollbackTask"}
def tool_guard(tool_name, authorized):
    if tool_name in DANGEROUS and not authorized:
        return "BLOCK", "危险操作:需用户在前端确认(HITL 门禁),框架层拦截"
    return "ALLOW", f"放行 {tool_name}"

# —— 3) state → Attachment:风险分析自动注入下一轮 ——
def attach_facts(state):
    risks = state.get("risks", [])
    return "".join(f"- {r['table']} ({r['level']}) 依赖字段 {r['field']}\n" for r in risks)

state = {"risks": [{"table": "dws_channel_report", "level": "HIGH", "field": "order_amount"},
                   {"table": "ads_daily_summary", "level": "MEDIUM", "field": "order_status"}]}
print(onload_script("长SQL" * 2000, None))      # 8000 字符,超阈值 → 阻断
print(tool_guard("packCommit", authorized=False))
print("下一轮注入:\n" + attach_facts(state))
```

## 实践 / 应用:Hook 全景与设计要点

### DECO 实际挂了十余个 Hook(分类全景)

| 分类 | Hook 示例 | 挂载点 |
| --- | --- | --- |
| 长文本护栏 | TaskScriptOffload/Onload、TableColumnsOffload、DdlBodyOffload | afterTool / beforeTool |
| 危险操作护栏 | DangerousToolGuard | beforeTool |
| 工具返回处理 | LineageResponseOffload、ToolResponseTruncator(超阈值触发 Rerank 重排保留最相关片段,截断前写 COS 可回捞)、ToolResponseFormatter | afterTool |
| 可观测与持久化 | ToolCallLogHook(toolName@threadId 配对)、LoggingHook、ConversationPersistenceHook | 多点 |
| 前端刷新与业务事件 | SqlExecuteHook(execute_sql 前存盘推 FILE_TREE_CHANGED)、CopyFileHook、ReleaseItemCollectorHook、DocumentSaveHook | before/afterTool |
| Hook→Attachment 联动 | RiskAnalysisHook、PythonImageHook | before/afterTool |
| 沙箱环境 | EnvVarCaptureHook(bash export → .sandbox_env,重启恢复) | afterTool |

### 设计要点(四条)

1. **失败语义按代价差异化**:读侧降级透传(可重试,不污染生产)、写侧阻断(杜绝残缺上线)——不是一刀切;
2. **判定条件精确化**:改表看 `tableId` 参数而非工具名,避免新建表误触发风险分析;
3. **累积写入 state**:一次会话多次事件累积,下一轮一次性注入(省 token、不丢信息);
4. **结构化注入**:预签名 URL/风险结论写成 JSON,前端直接渲染,不只是文本。

### 与站内其他文章的呼应

- [生产级 Agent 架构](agent-production-architecture.md):Hook 护栏与权限洋葱/熔断是同一"确定性兜底"原则;
- [企业 Agent 工程化(二)](../06-enterprise/ontology-agent-adoption/enterprise-agent-recovery-handoff.md):HITL 守卫 = "后果半径"的代码级实现(不可逆动作必须人工);
- [Agentic Abstention](agentic-abstention.md):三类问题的"停止判断"在这里变成框架强制——不依赖模型自觉;
- [AI Coding Harness 设计经验](../07-agent-coding/experience/ai-coding-harness-design.md):护栏生长的具体技术形态(Hook 切面);
- 使用角度(切面 API/ADK 8 模式/行业框架对比)详见站内 [Agent Hook 使用指南](../07-agent-coding/experience/agent-hooks-usage.md)。

## 总结

- **三类问题三个解法**:长文本偷懒 → 读写两侧 offload + 引用句柄(token 直降 90%);越权操作 → 配置驱动 beforeTool 守卫 + HITL 富交互确认;上下文失忆 → Hook 采集 → state → Attachment 注入闭环;
- **一条总原则**:能用确定性兜底的,别交给模型——prompt 定意图,Skill 定规矩,**框架 Hook 定边界**;
- **两条失败纪律**:读侧降级、写侧阻断(按代价差异化);没拿到用户授权,危险工具物理走不通;
- **一句话**:不是模型能力不够,而是它"图省事"或"自作主张"——把偷懒和越权的路径代码级强制走不通,把失忆的已知盲区确定性补齐。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/ISwjIw5lj7JlcQJV7BOx5g;原始资料存档于 `docs/inbox/deco-hooks-source.md`
- 站内:[Agent Hook 使用指南](../07-agent-coding/experience/agent-hooks-usage.md)(切面机制/ADK 8 模式/框架对比)、[生产级 Agent 架构](agent-production-architecture.md)、[企业 Agent 工程化(二)](../06-enterprise/ontology-agent-adoption/enterprise-agent-recovery-handoff.md)、[Agentic Abstention](agentic-abstention.md)、[AI Coding Harness 设计经验](../07-agent-coding/experience/ai-coding-harness-design.md)、[Agent 架构反熵增](agent-architecture-antientropy.md)
