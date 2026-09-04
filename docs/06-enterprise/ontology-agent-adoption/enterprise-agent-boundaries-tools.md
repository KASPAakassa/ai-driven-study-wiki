# 企业 Agent 工程化(一):任务边界与工具治理

> **一句话摘要**:企业 Agent 在生产里真正的敌人不是"不会做",而是"停不下来"。本文拆两条失控链路——任务边界被一轮轮放大、工具数量变成持续负债,给出六要素派工法与"默认暴露面治理"工具收敛法,附候选工具筛选与 schema 校验代码。
>
> **来源**:微信公众号《企业 Agent 工程化手记》第 1 篇《真正拖慢 Agent 协作的,不是犯错,而是停不下来》与第 2 篇《企业 Agent 工具治理:工具太多后为什么一定会失控》;原文链接见收件箱登记(`docs/inbox/enterprise-agent-engineering-src-b8.md`、`src-b7.md`)

## 概念

### 最慢的不是出错,是停不下来

作者复盘一天里 **51 个 AI Coding 会话、8 个项目**,原本预期最高频的信号是模型答错、工具失败、代码质量不稳定——结果都不是,最突出的是**范围蔓延型出现了 47 次**。

**Agent 最容易失控的地方,不是第一步不会做,而是做完一轮之后,下一轮的任务边界被放大了**——它顺着上下文继续补、继续猜,不是故意越界,而是上下文给了它一个"继续推进"的惯性。

!!! warning "Demo 与生产的本质差异"
    主动性在 Demo 里是亮点,在生产里是风险。Demo 阶段看 Agent **能不能多走一步**;生产环境看它**知不知道哪一步不能走**。一个连当前任务边界都守不住的 Agent,不应该直接接业务状态。

### 工具是负债,不是资产

我们天然觉得"能力 = 工具数量",能查得越多、调得越多,Agent 就越万能;Demo 阶段这个直觉几乎不出错,因为那时工具少、任务单一、上下文干净。**问题从工具变多开始**:每个工具都要被**每一步重新权衡**、可能被**错误调用**、说明与回传要**每轮背进上下文**,构成**有持续开销的负债**。工具越多,上下文越脏,注意力越散,越界机会越多,Agent **不是可能失控,而是一定会失控**。

## 原理

### 任务边界失控的机制:边界扩散 + 验证缺失

- **边界扩散**:你只想把某条连接线改细一点,它顺手整理了组件结构、调整了布局、改掉相邻样式——每一步都不大,几轮之后任务已经不是原来的任务。
- **验证缺失**:验证被用来"补救问题",却没有**前置到任务定义阶段**——测试失败被扩成大范围重构,审查回传后没有重新压缩目标。

对照几组容易误读的"看起来高效"现象与真实风险:

| 现象 | 看起来很 | 实际风险 |
| --- | --- | --- |
| 继续派工 | 高效 | 没有重新定义边界 |
| 自动补救 | 主动 | 验收条件被后置 |
| 多代理并行 | 强大 | 上下文噪音变多 |
| 一次多改 | 省事 | 回归风险变大 |

数据上,范围蔓延型 47 次、返工修正 90 次、重复推进 58 次、安装/配置反复 49 次、验证补跑 24 次——前两者说明任务在多轮补救里来回拉扯,后两者说明验证常在问题暴露后才补上。**返工是结果,范围蔓延更像上游原因。**(注:这些数字是作者某一天的个人 AI 协作日报、按用户消息级计数,不能直接推成行业结论,但能证明边界失控是反复出现的**协作结构问题**。)

### 工具的三类失控

**第一类:选择噪音。** 工具一多,先要决定用哪个;功能相近的工具并存时,模型会来回试——本该用 A 却挑了 B,再补救。**挑工具这一步本身就在消耗推理预算**,成了干活前最容易出错的一步。

**第二类:注意力稀释。** 每次工具调用都回传一段结果,工具说明被整段灌进上下文;工具越多,真正重要的目标、约束、验收越容易被淹没在一片工具输出里。**模型的注意力是有限预算**,上下文越脏,该聚焦的地方反而越看不清。这不是个人体感——论文 *MCP Tool Descriptions Are Smelly!* 与 *Evidence from 177,000 MCP tools* 都在研究工具描述质量与工具调用风险。

**第三类:动作面放大。** 前两类是"看不清",这一类是"做错事"。工具数量直接决定 Agent 的**动作面**:只读工具多,最多是噪音;可写、可发送、可提交的工具一多,越界和不可逆动作的概率就上升——每个能改数据、能发消息、能提交审批的工具,都是一条可能越界的路。

!!! warning "授权确认堆积是危险信号"
    682 次授权确认转录,说明人已经在为工具的越界风险持续买单——每一次确认,都是在替一个动作面太大的 Agent 兜底。确认频率不是"很可控",而是"边界没划清"的报警器。

### 为什么企业 Agent 上更危险

Coding Agent 多改一个文件,还能靠差异检查、测试、代码审查拦下来,成本变高但通常能回退;企业 Agent 一旦接入 CRM、OA、ERP、邮件、审批与客户数据,**每个动作都带着身份、权限、数据范围和业务后果**。所以:查客户资料时不能顺手改客户状态;生成跟进建议时不能自动发送邮件;分析商机时不能越权读取其它区域数据;工具失败时不能无限重试乱试;数据不完整时不能用猜测补齐业务事实。**企业 Agent 不能只定义"它能做什么",还必须定义"它当前这一轮被允许做什么"。**

## 代码 / 实现

原文为方法论文章,无代码。下面用纯 Python 演示两个核心机制:**先按任务约束缩小候选工具面再让模型选**;以及**调用前的参数 schema 校验**。

```python
# 第 1 部分:候选工具筛选 + 模型选择(先缩候选面,再让模型选)
PERM_LEVEL = {"read": 0, "write": 1, "irreversible": 2}

TOOL_REGISTRY = [
    {"id": "crm_query_contact", "cat": "crm", "perm": "read", "desc": "按 id 查询单个客户"},
    {"id": "crm_query_deal", "cat": "crm", "perm": "read", "desc": "按 id 查询商机"},
    {"id": "crm_update_stage", "cat": "crm", "perm": "write", "desc": "修改客户阶段"},
    {"id": "mail_send", "cat": "mail", "perm": "irreversible", "desc": "发送邮件"},
    {"id": "mail_draft", "cat": "mail", "perm": "write", "desc": "生成邮件草稿"},
    {"id": "approval_submit", "cat": "oa", "perm": "irreversible", "desc": "提交审批"},
    {"id": "erp_post_invoice", "cat": "erp", "perm": "irreversible", "desc": "过账发票"},
    {"id": "sql_query", "cat": "data", "perm": "read", "desc": "只读 SQL 查询"},
    {"id": "search_kb", "cat": "web", "perm": "read", "desc": "知识库搜索"},
    {"id": "code_edit_file", "cat": "code", "perm": "write", "desc": "编辑文件"},
]

def filter_tools(registry, task):
    """按任务约束过滤:类别 + 权限上限 + 业务关键词命中,得到本轮候选面"""
    return [t for t in registry
            if t["cat"] in task["allowed_categories"]
            and PERM_LEVEL[t["perm"]] <= PERM_LEVEL[task["max_perm"]]
            and any(k in t["desc"] for k in task["needed_keywords"])]

def select_tool(cands, intent):
    """模拟模型选择:按意图关键词给候选打分,选最高分(真实实现换成 LLM)"""
    return max(cands, key=lambda t: sum(1 for w in intent if w in t["desc"]))

def context_cost(tools, per_tool_tokens=25):
    return len(tools) * per_tool_tokens

# 本轮任务:整理客户跟进建议 + 生成邮件草稿(不发送、不改状态)
TASK = {"allowed_categories": ["crm", "mail"], "max_perm": "write",
        "needed_keywords": ["查询", "草稿"]}
INTENT = ["查询", "客户", "草稿", "邮件"]

cands = filter_tools(TOOL_REGISTRY, TASK)
print("候选工具面(缩到 %d 个):" % len(cands))
for t in cands:
    print("  - %-18s perm=%-12s %s" % (t["id"], t["perm"], t["desc"]))
print("模型选中:", select_tool(cands, INTENT)["id"])
print("上下文成本: 全量 %d token -> 候选 %d token (省 %d%%)"
      % (context_cost(TOOL_REGISTRY), context_cost(cands),
         (1 - context_cost(cands) / context_cost(TOOL_REGISTRY)) * 100))
print("-" * 60)
print("未筛选时模型可能看到的越界工具:")
for t in TOOL_REGISTRY:
    if t["perm"] == "irreversible":
        print("  * %s(%s): %s" % (t["id"], t["perm"], t["desc"]))
```

**运行结果**:10 个工具的注册表被压成 3 个候选(`crm_query_contact`、`crm_query_deal`、`mail_draft`),`mail_send`、`approval_submit`、`erp_post_invoice` 等不可逆工具在进入模型视野前就被拦下;上下文成本从 250 token 降到 75 token。这就是"先缩候选、再让模型选"——**模型在真实工程里从不需要看到整个工具箱**。

```python
# 第 2 部分:工具 schema 校验(缺参/错类型/越枚举/越权,调用前拦截)
PERM_LEVEL = {"read": 0, "write": 1, "irreversible": 2}  # 与前一块保持一致
import re

SCHEMAS = {
    "crm_update_stage": {"perm": "write",
        "required": ["contact_id", "stage"],
        "properties": {"contact_id": {"type": "string"},
                       "stage": {"type": "string",
                                 "enum": ["lead", "qualified", "proposal", "won", "lost"]}}},
    "mail_send": {"perm": "irreversible",
        "required": ["to", "subject", "body"],
        "properties": {"to": {"type": "string", "pattern": "(.+)@(.+)\\.(.+)"},
                       "subject": {"type": "string"}, "body": {"type": "string"}}},
}

def validate_call(tool_id, args, current_perm="read"):
    """校验顺序:先看这轮允许做什么,再看参数契约"""
    schema = SCHEMAS[tool_id]
    errs = []
    if PERM_LEVEL[schema["perm"]] > PERM_LEVEL[current_perm]:
        errs.append("越权: %s 需要 %s 权限,本轮只允许 %s"
                    % (tool_id, schema["perm"], current_perm))
    for p in schema["required"]:
        if p not in args or args[p] in (None, ""):
            errs.append("缺少必需参数: %s" % p)
    for name, spec in schema["properties"].items():
        if name not in args:
            continue
        val = args[name]
        if spec.get("type") == "string" and not isinstance(val, str):
            errs.append("参数 %s 应为 string,实际 %s" % (name, type(val).__name__))
        if "enum" in spec and val not in spec["enum"]:
            errs.append("参数 %s 取值 %r 不在枚举 %s 内" % (name, val, spec["enum"]))
        if "pattern" in spec and re.match(spec["pattern"], val) is None:
            errs.append("参数 %s 格式不合法: %r" % (name, val))
    return errs

cases = [
    ("crm_update_stage", {"contact_id": "c-1001", "stage": "won"}, "read", "本轮只读,却想改客户阶段"),
    ("crm_update_stage", {"contact_id": "c-1001", "stage": "vip"}, "write", "枚举越界:没有 vip 阶段"),
    ("crm_update_stage", {"contact_id": "c-1001"}, "write", "缺必需参数 stage"),
    ("mail_send", {"to": "lead@corp.com", "subject": "s", "body": "b"}, "write", "不可逆动作未授权"),
]
for tool_id, args, cur_perm, note in cases:
    errs = validate_call(tool_id, args, cur_perm)
    print("[%s] %s" % (tool_id, note))
    for e in errs:
        print("   拦截: %s" % e)
    if not errs:
        print("   通过,放行")
```

**运行结果**:四种调用全部在动作发生前被拦截——权限不够、枚举越界、缺参、不可逆未授权。校验发生在**调用前**、由规则代码执行,而不是靠模型自觉:**模型负责执行,规则负责拦截**。

## 实践 / 应用

### 任务边界重新声明:每轮派工的六要素

"继续处理上面的审查意见"这类指令非常自然、也非常危险——"继续"没有告诉 Agent 当前轮次的目标、范围和验收,只是把上一轮上下文原样交给下一轮。**上下文越长,Agent 越容易把噪音当成任务。** 回传信息不是任务本身,必须先压缩成一个可验收请求。每次派工前,把六个要素重新声明一遍:

| 要素 | 含义 | 企业 Agent 示例 |
| --- | --- | --- |
| 目标 | 这轮只解决什么问题 | 只生成客户跟进建议 |
| 上下文 | 为什么现在要做 | 销售基于最近一次沟通准备下一步动作 |
| 范围 | 只允许碰哪里 | 只读当前客户、商机与有权限的互动记录 |
| 约束 | 哪些事情不能做 | 不发送邮件、不改客户状态、不创建任务 |
| 验收 | 怎么证明完成 | 输出建议、依据与缺失信息 |
| 交付物 | 最后要给什么 | 给销售确认的跟进草案 |

!!! tip "危险词提醒"
    **"继续"是一个危险词。** 每一次继续,都应该重新声明目标、范围和验收。更稳的写法是:"请只处理当前项目里的类型检查失败;范围限报错模块与对应测试;验收为指定测试通过且不改无关文件。"

### 工具治理 checklist:默认暴露面治理五步

作者用一次真实的 skills 分类(63 个 SKILL.md、默认可见面太大触发 context budget 警告)总结出五条,放之企业 Agent 工具同样成立:

1. **最小工具集**:默认只挂当前任务必须的工具,而不是能挂的全挂;
2. **按任务装载**:工具随任务进出,用完就卸,不让上下文长期背着一堆用不上的能力;
3. **工具分级**:只读、可写、不可逆三级,区别对待;
4. **确认与接管**:可写和不可逆的工具必须配确认或人工接管,不能只靠模型自信;
5. **可观测**:把工具回传、技能灌入、授权确认这类噪音指标当健康信号去盯,而不是等堆满了才发现。

单条工具的说明,写**接口契约四要素**(而非散文):① 做什么;② 参数 schema;③ 副作用与权限等级;④ 典型调用示例。工具说明写得越多越乱,模型在选择和调用时要消化的噪音就越多。

!!! note "记忆压缩的取舍"
    工具回传是上下文的主要污染源。取舍原则:只保留"本轮可复用的结论"(如查询到的客户字段),丢弃大段原始回传(如 SQL 结果全量、日志全文)。

## 总结

- **真正拖慢 Agent 的,不是犯错,而是停不下来**:任务边界在多轮执行中被上下文惯性一轮轮放大,返工是结果,范围蔓延是上游原因。
- **工具是负债,不是资产**:工具数量同时放大选择噪音、注意力稀释与动作面放大三类失控,工具越多,越界入口越多。
- **每轮重新声明边界 + 收敛默认暴露面**:工具库可以很大,但每次任务暴露给 Agent 的工具面必须很小——先筛选候选,再让模型选;schema 校验与权限分级放在调用前由规则执行。
- **一句话判断**:能进生产的 Agent,不是工具最多的那个,而是工具最干净、最受控、最知道边界在哪的那个。

## 延伸阅读

- 站内:[企业 Agent 工程化(二):异常恢复与人工接管](enterprise-agent-recovery-handoff.md)、[Ontology 与 Agent 企业落地](index.md)、[Agent 工具调用机制](../../03-agents/tool-calling.md)、[上下文工程](../../03-agents/context-engineering.md)、[Agent 记忆系统](../../03-agents/agent-memory-systems.md)
- 外部:微信公众号《企业 Agent 工程化手记》第 1、2 篇(原文链接见收件箱登记);论文 *MCP Tool Descriptions Are Smelly!*、*How are AI agents used? Evidence from 177,000 MCP tools*
