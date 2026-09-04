# 企业业务 Agent 落地:从听懂到做对的四步路径

> **一句话摘要**:意图识别只是入口,"听懂一句话"不等于"理解这笔业务"。企业 Agent 的安全落地路径是——先明确四类出口(执行/追问/拒识/确认),再按"规则→分类器→Embedding→LLM→规划器"的级联控制成本,最后用历史回放、只读影子、低风险放行、按失败证据扩权四步渐进上线。附可运行的"意图级联路由 + 执行前状态新鲜度检查"纯 Python 演示。
>
> **来源**:微信公众号「架构师 JiaGouX」《一文讲清 Agent 如何理解业务:把对象、状态和权限接进执行流程》(作者:若飞;参考陈思州/Datawhale 原文、Anthropic context engineering、OpenAI agent guide、Rasa CALM、Microsoft 核心业务流程 Agent 模式、DDD Reference、HumanLayer 12-Factor Agents);原文链接 https://mp.weixin.qq.com/s/LYF3_RaXhe50DNb_ZW0KZg

## 概念

### 听懂一句话,不等于理解这笔业务

用户问客服 Agent:

> 上次那单还没发,能不能直接取消,优惠券也退回来?

识别出"取消订单"并不难,模型甚至可以顺手抽出"未发货""退回优惠券"两个条件,给出一段很像样的回复。麻烦从这里才开始:"上次那单"是哪一单?履约状态是否真的还是未发货?优惠券是平台券、店铺券还是已过期的活动券?取消后原路退款还是退到余额?当前用户有没有权限操作这张订单?

这些问题没有答案,Agent 只是**听懂了这句话,还没有理解这笔业务**。最顺手的改法是继续补 Prompt——遇到"上次那单"优先查最近订单、提到优惠券再补退券规则。前几轮可能真有效,但 **Prompt 能提醒模型怎样分析,却不能证明订单此刻处于什么状态,也不能替权限系统批准退款**;规则越补越长,系统对真实业务的把握却未必增加。

!!! tip "业务理解的可验收定义"
    对会执行动作的 Agent,"理解业务"应该落到一件能验收的事上:**能否在明确边界内,把正确的业务对象从当前状态推进到目标状态,并留下可核对的依据。** 这比"意图识别准确率有多高"多走了好几步。

### 意图识别的四类出口:执行、追问、拒识、确认

进入 Agent 系统以后,意图识别输出不再是一张"转给哪个客服组"的标签,而是控制流的下一步。一次识别最终进入四类出口之一:

| 出口 | 含义 | 典型场景 |
| --- | --- | --- |
| **执行 EXECUTE** | 意图确定、对象明确、风险可控 | 低风险查询、信息补全 |
| **追问 CLARIFY** | 意图可猜但对象/参数/状态缺关键信息 | "退个款吧"——退哪笔、退到哪 |
| **拒识 REJECT** | 请求不在支持范围内,最稳的结果是拒识 | 超范围闲聊,而非硬选一个"最像"的意图 |
| **确认 CONFIRM** | 意图清楚,但动作有副作用,停在执行前等人确认 | 取消订单、退款、外发、生产发布 |

!!! warning "硬选最像意图的代价"
    CLINC150 这类经典数据集专门加入超出支持范围的请求,因为**分类器不能假设每句话都属于已有标签**。到了 Agent 现场这个边界更重要:一个请求不在支持范围内,最稳的结果是拒识、追问或转人工;硬选一个"最像的意图",后面可能就是一次错误写入——把不该退的券退了、把订单取消了。

意图识别做得再好,也只能证明系统听懂了入口,还没有证明整件事做得对。

## 原理

### ① 意图识别技术级联:复杂度上升才加推理成本

任务型对话在意图分类上已有完整技术路线。关键认知是:**这些方法并不是按年代依次淘汰前一种,生产系统更常见的是逐层分流,复杂请求再升级。**

| 层 | 技术 | 擅长 | 成本 |
| --- | --- | --- | --- |
| 规则闸门 | 正则、关键词、安全拦截 | 确定性请求、高危词拦截 | 最低 |
| 轻量分类器 | TF-IDF / FastText + 逻辑回归 / SVM | 标签稳定、数据量够的高频流量 | 低 |
| Embedding Top-K | 向量相似度召回 | 新意图多、每类样本少的少样本场景 | 中 |
| LLM | 大模型判别 | 口语、省略、多轮修正、长尾请求 | 高 |
| 规划器 / 流程 | 状态机、编排 | 多动作、有依赖关系的复合任务 | 最高 |

**选型四问**:① 意图是否多到一份 Prompt 放不下;② 标签是否经常调整、新业务多久上线一次;③ 有没有足够的真实标注数据;④ 一次判断要回看一句话,还是几轮对话和工具结果。

生产里更常见的形态是**级联**:请求先经过规则和安全闸门;稳定流量交给轻量分类器;意图很多时 Embedding 先召回 Top-K 候选;仍有歧义的请求交给 LLM;涉及多动作、多依赖才进入规划器或业务流程。**请求越简单,链路越短;只有复杂度上升,系统才增加推理成本。**

### ② RAG 的边界:知识能检索,不能裁决

很多团队发现 Prompt 不够用,下一步自然想到 RAG:把产品文档、客服手册、历史工单全部放进知识库。这会有帮助,却也很容易制造一种错觉——**资料找到了,Agent 就懂业务了。**

文档里通常写着三类东西:业务术语和政策、操作流程和例外、过去发生过的案例。真实业务还多出三类**动态事实**:对象**此刻的状态**、用户在组织里的**权限**、动作究竟**成功、失败还是只处理了一半**。前一组可从文档检索,后一组必须回到订单、账户、权限、支付和审计系统读取。

| 信息 | 更合适的真相源 | 为什么不能靠 RAG 检索 |
| --- | --- | --- |
| 术语、政策、SOP、案例 | 版本化文档与检索系统 | 知识类信息适合检索 |
| 订单、账户、库存、支付状态 | 业务 API 或数据库服务 | 昨天的工单不能替代今天的状态 |
| 身份、角色、额度、审批权 | 认证与授权系统 | "主管通常可以退款"只是说明,是否越权必须由权限系统判断 |
| 分支、超时、重试、补偿 | 工作流或状态机 | 业务接下来允许发生什么,由流程决定 |
| 调用结果、状态变化、责任人 | 运行记录与审计日志 | 模型说"已经取消"没有意义,要读订单确认 |

!!! note "Context engineering != process engineering"
    Anthropic 在上下文工程文章里强调,上下文是有限资源,目标是给模型最少但高信号的信息——它解决**模型此刻看见什么**;流程工程解决**业务接下来允许发生什么**。放到客服场景很具体:知识库可以把退款政策送到模型眼前,订单状态、额度校验和审批结果仍要由业务系统给出。给模型一份退款政策,它有机会解释政策;把退款条件、金额上限、审批角色和状态变化写进流程,系统才有机会稳定执行政策。

### ③ LLM 的职责与系统的职责边界

业务理解最终落到运行时:**对着当前对象,读取当前状态,套用当前规则,再以当前身份行动。** 模型负责整理用户表达,真实状态和副作用仍由业务系统负责。

| 环节 | 由谁负责 | 说明 |
| --- | --- | --- |
| 解析 goal、对象线索、待确认项 | LLM(理解层) | 允许概率判断、拒识、追问 |
| 读取实时状态 | 业务系统(决策层) | 不能凭聊天记录猜,更不能把"用户说没发货"直接写成 `fulfillment=not_shipped` |
| 应用规则版本、检查权限 | 确定性代码 / 决策表 / 状态机 | 高频、稳定、高风险的规则优先进代码 |
| 产生副作用 | 工具执行器(执行层) | 工具要有幂等键、错误类型;资金/删除/外发停在"已选工具、尚未调用" |
| 验证结果 | 验证器 | 不是复述工具成功消息,而是重读对象核对预期状态 |

HumanLayer 的 12-Factor Agents 特别强调**控制流要支持暂停和恢复**,人工确认不能等 Agent 执行完再看日志。拆三层不意味着要做三个 Agent,可以是一个 Agent 加两层普通代码——目标是分清责任,不是增加角色。

### ④ 上线前写清决策权与自治边界

Microsoft 在核心业务流程 Agent 模式里强调:**决策权和自治边界要在上线前写清,业务结果仍由业务方负责。** OpenAI 的 Agent 实践指南则把以下动作列为需要人工监督的高风险操作:

| 高风险动作 | 落地策略 |
| --- | --- |
| 取消订单 | 默认停在确认点,展示对象、影响范围、规则与预期结果 |
| 大额退款 | 超过自动额度一律转审批或人工 |
| 支付 / 资金动作 | 必须人工监督,权限系统强校验 |
| 删除、外发、生产发布 | 视为不可逆动作,默认确认 |

!!! warning "语言表现不错,业务结果仍然可能是错的"
    一个 Agent 可以把取消政策解释得很漂亮,却把不该退的券退了。所以落地路径的关键词是"渐进"和"证据",而不是"模型已经挺聪明"。

## 代码 / 实现

把"意图级联路由 + 执行前状态新鲜度检查"写成纯 Python(零第三方依赖,`python3` 直接运行):

```python
# -*- coding: utf-8 -*-
# 企业业务 Agent 落地演示:意图级联路由 + 执行前状态新鲜度检查(纯 Python,零依赖)
# 意图名 -> (中文名, 是否有副作用, 风险档)
INTENTS = {
    "order_status":   ("查询订单状态", False, "low"),
    "shipping_fee":   ("咨询运费",     False, "low"),
    "restore_coupon": ("恢复优惠券",   True,  "medium"),
    "refund":         ("退款",         True,  "high"),
    "cancel_order":   ("取消订单",     True,  "high"),
}
OUT_EXECUTE, OUT_CLARIFY, OUT_REJECT, OUT_CONFIRM = "EXECUTE", "CLARIFY", "REJECT", "CONFIRM"

# 第 0 层:规则闸门(确定性规则 + 安全拦截)
def rule_gate(text):
    hits = []
    if any(k in text for k in ("取消", "退单")):
        hits.append("cancel_order")
    if "退款" in text or "退钱" in text:
        hits.append("refund")
    if "券" in text and "退" in text:
        hits.append("restore_coupon")
    if any(k in text for k in ("发货", "物流", "快递", "到哪")):
        hits.append("order_status")
    return hits

# 第 1 层:轻量分类器(关键词命中计数,有歧义则升级)
CLASSIFIER_KEYWORDS = {
    "cancel_order":   ["取消", "退单", "不要了"],
    "refund":         ["退款", "退钱", "退款到"],
    "restore_coupon": ["优惠券", "券", "退回"],
    "order_status":   ["发货", "物流", "到哪", "快递"],
    "shipping_fee":   ["运费", "邮费", "包邮"],
}

def keyword_classifier(text):
    scores = {i: sum(1 for w in ws if w in text)
              for i, ws in CLASSIFIER_KEYWORDS.items()}
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    top, second = ranked[0], ranked[1]
    if top[1] == 0:
        return None                  # 全部未命中,交给 embedding 层
    if top[1] - second[1] >= 1:
        return top[0]                # 唯一领先,自信
    return None                      # 有歧义,升级

# 第 2 层:Embedding Top-K 召回
# 真实系统用 embedding 模型算余弦相似度;这里用"字符 n-gram + 示例"
# 的 Jaccard 相似度近似,行为可预测。
def char_ngrams(text, n=2):
    return set(text[i:i + n] for i in range(len(text) - n + 1))

def jaccard(a, b):
    inter = len(a & b)
    return inter / max(1, len(a | b))

INTENT_EXAMPLES = {
    "cancel_order":   ["取消订单", "订单不要了", "帮我退单"],
    "refund":         ["申请退款", "退钱给我", "退款到账户"],
    "restore_coupon": ["优惠券退回来", "恢复优惠券", "券还给我"],
    "order_status":   ["订单到哪了", "查一下物流", "发货了吗"],
    "shipping_fee":   ["运费多少", "邮费怎么算", "包邮吗"],
}

def text_similarity(a, b):
    a1, b1 = char_ngrams(a, 1), char_ngrams(b, 1)
    a2, b2 = char_ngrams(a, 2), char_ngrams(b, 2)
    return 0.4 * jaccard(a1, b1) + 0.6 * jaccard(a2, b2)

def embedding_score(text, intent):
    kw = sum(1 for w in CLASSIFIER_KEYWORDS[intent] if w in text)
    kw_norm = kw / max(1, len(CLASSIFIER_KEYWORDS[intent]))
    ex_best = max(text_similarity(text, ex) for ex in INTENT_EXAMPLES[intent])
    return round(0.5 * kw_norm + 0.5 * ex_best, 3)

def embedding_topk(text, k=3):
    return sorted(((embedding_score(text, i), i) for i in INTENTS),
                  reverse=True)[:k]

# 第 3 层:LLM 裁决(在 Top-K 候选内做最终判断;生产用真 LLM,这里确定性模拟)
AMBIGUITY_GAP = 0.02

def llm_disambiguate(topk):
    best_sim, best = topk[0]
    if best_sim - topk[1][0] < AMBIGUITY_GAP:
        return None                  # 候选过于接近 -> 追问
    return best

# 第 4 层:规划器(展开动作序列 + 风险/对象闸门)
PLANS = {
    "cancel_order":   ["resolve_order", "read_state", "cancel_order",
                       "refund_payment", "restore_coupon"],
    "refund":         ["resolve_order", "read_state", "refund_payment"],
    "restore_coupon": ["resolve_order", "read_state", "restore_coupon"],
    "order_status":   ["resolve_order", "read_state"],
    "shipping_fee":   ["resolve_order", "read_policy"],
}
OBJECT_HINTS = ("订单", "单", "券", "票", "服务", "会员")

def has_object_hint(text):
    return any(h in text for h in OBJECT_HINTS)

def plan(intents, text):
    if not intents:
        return OUT_REJECT, None, [], "没有可用意图"
    side_effects = [i for i in intents if INTENTS[i][1]]
    if side_effects and not has_object_hint(text):
        return OUT_CLARIFY, side_effects[0], [], "动作有副作用但缺对象线索,需确认对象"
    seq, seen = [], set()
    for i in intents:
        for s in PLANS[i]:
            if s not in seen:
                seen.add(s)
                seq.append(s)
    risk = "high" if any(INTENTS[i][2] == "high" for i in intents) else \
           "medium" if any(INTENTS[i][2] == "medium" for i in intents) else "low"
    if risk in ("high", "medium"):
        return OUT_CONFIRM, "+".join(intents), seq, \
               "含副作用动作,停在已选工具未调用处,等待确认"
    return OUT_EXECUTE, intents[0], seq, "低风险查询,直接执行"

# 级联路由主流程:复杂度上升才动用更贵的层
REJECT_THRESHOLD = 0.06

def cascade_route(text):
    rules = rule_gate(text)
    if rules:
        return plan(rules, text)                 # 规则闸门给出确定/复合意图
    intent = keyword_classifier(text)
    if intent:
        return plan([intent], text)              # 轻量分类器自信
    topk = embedding_topk(text, k=3)
    if topk[0][0] < REJECT_THRESHOLD:
        return OUT_REJECT, None, [], \
               "Top-K 最高相似度 %.3f 低于拒识阈值" % topk[0][0]
    best = llm_disambiguate(topk)
    if best is None:
        return OUT_CLARIFY, None, [], "Top-K 候选接近,需追问澄清"
    return plan([best], text)

# 状态新鲜度检查:执行前重读业务状态(对应"规则对了,状态旧了")
class OrderStore:
    """业务系统的唯一事实源(模拟):状态只从这里读,不写进对话状态"""
    def __init__(self):
        self._orders = {
            "A1001": {"payment": "paid",
                      "fulfillment": "not_shipped", "coupon": "consumed"},
        }
    def read(self, order_id):
        return dict(self._orders[order_id])
    def mark_shipped(self, order_id):
        self._orders[order_id]["fulfillment"] = "shipped"

def check_state_freshness(order_id, snapshot, store):
    """执行前重读状态;返回(是否仍与规划时一致, 最新状态, 变化点)"""
    fresh = store.read(order_id)
    changed = {k: (snapshot.get(k), v)
               for k, v in fresh.items() if snapshot.get(k) != v}
    return (len(changed) == 0), fresh, changed

def main():
    print("== 意图级联路由:四类出口 ==")
    cases = [
        "我的订单到哪里了?",
        "上次那单还没发,能不能直接取消,优惠券也退回来?",
        "退个款吧",
        "明天会下雨吗?",
    ]
    for text in cases:
        route, intent, seq, note = cascade_route(text)
        print("用户输入:", text)
        print("  出口:", route, "| 意图:", intent or "-", "| 计划:", seq)
        print("  说明:", note)
        print()

    print("== 场景:规则对了,状态旧了(执行前重读状态)==")
    store = OrderStore()
    order_id = "A1001"
    snapshot = store.read(order_id)          # 规划时读到的快照:未发货
    store.mark_shipped(order_id)             # 规划之后、执行之前,仓库完成出库
    ok, fresh, changed = check_state_freshness(order_id, snapshot, store)
    print("  规划时读取:", snapshot)
    print("  执行前重读:", fresh)
    print("  变化点:", changed or "无")
    if not ok:
        print("  -> 新鲜度检查失败:中止执行,回到决策层重新决策"
              "(cancel 不再适用,改走 CLARIFY)")

if __name__ == "__main__":
    main()
```

**运行结果**(`python3` 实测):

```text
== 意图级联路由:四类出口 ==
用户输入: 我的订单到哪里了?
  出口: EXECUTE | 意图: order_status | 计划: ['resolve_order', 'read_state']
  说明: 低风险查询,直接执行

用户输入: 上次那单还没发,能不能直接取消,优惠券也退回来?
  出口: CONFIRM | 意图: cancel_order+restore_coupon
  计划: ['resolve_order', 'read_state', 'cancel_order', 'refund_payment', 'restore_coupon']
  说明: 含副作用动作,停在已选工具未调用处,等待确认

用户输入: 退个款吧
  出口: CLARIFY | 意图: refund | 计划: []
  说明: 动作有副作用但缺对象线索,需确认对象

用户输入: 明天会下雨吗?
  出口: REJECT | 意图: - | 计划: []
  说明: Top-K 最高相似度 0.022 低于拒识阈值

== 场景:规则对了,状态旧了(执行前重读状态)==
  规划时读取: {'payment': 'paid', 'fulfillment': 'not_shipped', 'coupon': 'consumed'}
  执行前重读: {'payment': 'paid', 'fulfillment': 'shipped', 'coupon': 'consumed'}
  变化点: {'fulfillment': ('not_shipped', 'shipped')}
  -> 新鲜度检查失败:中止执行,回到决策层重新决策(cancel 不再适用,改走 CLARIFY)
```

关键点解读:

- **出口即控制流**:低风险查询走规则闸门短链路直接 `EXECUTE`;复合任务(取消 + 退券)由规划器展开动作序列并停在确认点 `CONFIRM`;缺对象线索时 `CLARIFY`;与意图库零重叠的请求走 `REJECT`,不硬选最像的意图。
- **状态只从业务系统读**:`OrderStore` 是唯一事实源,对话状态里"用户说没发货"不能替代 `fulfillment` 的真实值。
- **执行前重读**:`check_state_freshness` 用规划时快照与执行前实时状态比对,发现 `not_shipped -> shipped` 就中止重新决策——对应"规则对了,状态旧了"。

## 实践 / 应用

### 优先场景:5 个真跑通清单(先从哪开始)

!!! tip "一个现实反差"
    很多团队还在写"AI 战略 PPT",另一批团队已经让 Agent 接手周报、客服、销售线索、知识检索和内容分发。**差距不在模型能力,而在有没有把任务拆成可执行流程。** 先跑通的不是"全自动替代人",而是**高频、规则清晰、结果可校验的流程型工作**——如果你还在问"Agent 到底能落在哪",先看这 5 类被反复验证的场景:

| 场景 | 典型链路 | 为什么能跑通 | 最容易踩的坑 |
| --- | --- | --- | --- |
| **① 内部运营自动化**(周报/日报/会议纪要/任务同步) | 飞书/企微/Jira/Notion 拉数据 → 汇总进展 → 生成角色版周报 → 发群/邮件 | 数据在内部、流程固定、**出错可人工兜底**(普通团队最先见效的入口) | 权限配置复杂、数据源格式多变 |
| **② 客服与售后分流** | 先判断意图 → 再答复 → 最后转人工 | 高频、规则边界清晰、结果可校验 | 误判直接答错;必须保留转人工通道(呼应"四类出口"与确认点) |
| **③ 销售线索处理** | 清洗 → 打标 → 跟进建议 → CRM 回填 | 结构化流程、结果可校验 | CRM 写回权限;重复写入 |
| **④ 企业知识库问答** | 跨文档检索 → 摘要 → 引用来源 | 语义检索成熟(参见站内 [高德知识库案例](ai-native-knowledge-base-gaode.md)) | 引用不溯源、权限泄露(知识可见范围) |
| **⑤ 内容生产与分发** | 选题 → 改写 → 多平台适配 → 数据复盘 | 生成型任务、验收直观 | 平台规则变化、风格一致性 |

!!! note "这些场景的共同点"
    都满足"高频、规则清晰、结果可校验"三要素——这也是判断一个业务能否先落地 Agent 的**筛选标准**:不满足三要素的流程,先不要上,等它被拆得更可执行再说。

### 四步落地路径:上线初期,让 Agent 少做一点

一次退款失败到底错在哪(意图识别、状态读旧、规则版本、权限漏判、接口超时),若所有逻辑藏在一段上下文里根本分不清。更稳的节奏是四步渐进,**让 Agent 少做一点,用证据换自治权**:

| 步骤 | 做什么 | 能发现什么 | 产出 |
| --- | --- | --- | --- |
| ① 历史回放 | 用已处理完的真实案例,遮掉敏感信息,Agent **只生成业务决策记录,不调用写工具** | 对象、状态、规则、追问、拒绝是否正确 | 一批人工核对的决策记录 |
| ② 只读影子模式 | Agent 跟着真实流量**读取数据、给出计划,不产生副作用** | 文档规则与线上状态不一致、接口字段含义混乱、权限信息拿不到 | 状态/规则/权限边界清单 |
| ③ 放开低风险路径 | 查询、信息补齐、草稿自动完成;退款/删除/外发/发布停在确认点 | 高风险动作的确认体验与误执行率 | 确认点展示规范 |
| ④ 按失败证据扩权 | 按具体流程、金额或对象范围增加自治权 | 边界是否真的稳定 | 分流程/分金额的自治策略 |

!!! warning "扩权依据是失败证据,不是感觉"
    **误执行、人工接管、补偿和业务结果数据,应该成为扩大边界的依据,不能只凭团队感觉模型"已经挺聪明"。** 这套节奏看起来慢一点,实际上省掉了不少上线后的返工:早期自动化比例说明不了太多,一批经过核对的失败案例,以及逐渐清楚的状态、规则和权限边界,往往更有价值。

每个确认点都要向人展示四样东西:**对象是谁、影响范围多大、采用哪一版规则、预期结果是什么**——让人能快速判断"要不要放行",而不是猜 Agent 想干什么。

### 分层指标:别只留一个整体 Accuracy

意图系统常看的 Accuracy、Macro-F1、混淆矩阵、Recall@K 仍然有价值,可以定位理解层的问题。Agent 进入业务流程后,还要再看四组指标:

| 层次 | 更值得观察的指标 |
| --- | --- |
| 理解层 | 拒识率、追问率、对象绑定准确率、字段级 F1 |
| 决策层 | 规则命中准确率、状态读取新鲜度、权限拦截率、例外路由准确率 |
| 执行层 | 工具成功率、重复执行率、补偿成功率、高风险误执行率 |
| 业务结果 | 端到端完成率、人工接管率、处理周期、客诉与资金差错 |

**级联系统尤其要分层看指标**,排查顺序固定:① 意图**没进 Top-K** → 查向量索引、样本覆盖和召回策略;② **已召回仍选错** → 查意图定义、混淆反例和判断上下文;③ **计划对但动作失败** → 问题已离开意图层,去看权限、工具和流程状态。

!!! warning "只留一个整体 Accuracy 的代价"
    这三类故障会被揉成同一个数字,团队很难知道该改数据、改 Prompt,还是改业务流程。Microsoft 的核心业务流程模式同样强调:评估应回到处理周期、吞吐、准确率、例外率和既有业务指标,而不是只看模型回答得像不像。

### 四种"看起来懂了",最值得拿来做测试

测试集如果只放表达清楚、状态稳定、一步成功的样本,很难看出系统是否真的理解业务。下面四种错位更接近生产现场:

| 错位 | 表面现象 | 应有处理 |
| --- | --- | --- |
| 目标对了,对象错了 | 确实要取消订单,却选中了同一用户的另一张订单 | 停止执行,补充对象确认 |
| 规则对了,状态旧了 | 按"未发货可取消"处理,但仓库刚刚完成出库 | 执行前重新读取状态,发现变化后重新决策 |
| 动作合法,身份不对 | 退款动作存在,但当前客服额度不足或跨组织操作 | 由权限系统拒绝,转审批或人工 |
| 工具成功,业务只完成一半 | 订单取消成功,退款成功,优惠券恢复失败 | 标记部分完成,进入补偿或人工队列 |

这四类失败分别对应**对象绑定、状态新鲜度、权限边界和事务完整性**——它们比"模型回答是否流畅"更能暴露系统的真实水平,也是四步落地路径里每个确认点、每个指标要盯住的东西。

### 与 Palantir 系列的呼应

本文的落地路径与本章 Palantir 系列的核心主张一致:**企业 Agent 理解业务的终点,都是"受治理的语义 + 动作"。**

- 本文的"业务语义六要素(统一术语/业务对象/实时状态/规则版本/权限边界/可执行动作)"对应 [Palantir 操作型本体论](palantir-operational-ontology.md) 的四维集成 **Data / Logic / Action / Security**——语义锚定数据与逻辑,动作与安全一个都不能少;
- 本文"动作受控写回、高风险停在确认点"对应 [OAG 与 Ontology 驱动的企业 Agent](palantir-oag-agent.md) 的 **Action 层**——敏感操作需人类确认,权限校验通过才能执行;
- 本文"先定义对象/状态/规则/动作再放开执行"对应 [Palantir Foundry:5 步把数据变对象](palantir-foundry-5-steps.md) 的"对象 → Function → Scenario → Action → Decision Lineage"链路。

一句话:**Palantir 用 Ontology 回答"企业里有什么、能做什么、谁能做",本文用级联与四步路径回答"怎么把听懂变成做对,且不失控"**——前者是语义底座,后者是渐进上线节奏。

## 总结

- **听懂 ≠ 理解**:意图识别只是入口,业务理解要落到"正确对象 × 当前状态 × 当前规则 × 当前身份"能否推进到目标状态,并留下证据。
- **级联控制成本**:规则闸门 → 轻量分类器 → Embedding Top-K → LLM → 规划器,请求越简单链路越短;超范围请求走拒识,不硬选最像的意图。
- **RAG 检索 ≠ 裁决**:术语、政策、案例可以检索;实时状态、权限结果、动作结果必须从业务系统读取。`Context engineering != process engineering`。
- **四步落地**:历史回放 → 只读影子模式 → 放开低风险路径 → 按失败证据扩大边界;高风险动作(取消订单/大额退款/支付)上线前写清决策权,默认停在确认点。
- **指标分层看**:理解/决策/执行/业务结果四层指标分开统计,别只留一个整体 Accuracy;**语言表现不错,业务结果仍然可能是错的——业务理解,要看状态有没有正确改变。**

下一步:结合 [企业 Agent 工程化(四)Tool、MCP、Skills、Harness 四件套](enterprise-agent-tooling-harness.md) 把"确认点"和"工具契约"落到具体工具实现;或读 [企业 Agent 工程化(二):异常恢复与人工接管](enterprise-agent-recovery-handoff.md),理解"后果半径四档"与本文"四类出口"如何互相对接。

## 延伸阅读

- 原文:《一文讲清 Agent 如何理解业务:把对象、状态和权限接进执行流程》,微信公众号「架构师 JiaGouX」,https://mp.weixin.qq.com/s/LYF3_RaXhe50DNb_ZW0KZg
- 参考源:Anthropic [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents);OpenAI [A practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/);Microsoft [Core business process transformation](https://learn.microsoft.com/en-us/agents/adoption-patterns/pattern-core-business-process);HumanLayer [12-Factor Agents](https://github.com/humanlayer/12-factor-agents)
- 站内相关:
  - [Palantir 操作型本体论:从范式跃迁到工程实现](palantir-operational-ontology.md) — Data/Logic/Action/Security 四维集成
  - [OAG 与 Ontology 驱动的企业 Agent](palantir-oag-agent.md) — Action 层与人工确认
  - [Palantir Foundry:5 步把数据变对象](palantir-foundry-5-steps.md) — 对象 → Action → Decision Lineage
  - [企业 Agent 工程化(二):异常恢复与人工接管](enterprise-agent-recovery-handoff.md) — 接管看后果,不看信心
  - [企业 Agent 工程化(三):权限、集成与可观测性](enterprise-agent-permission-integration-observability.md) — 替谁做事、四类记录
  - [企业 Agent 工程化(四):Tool、MCP、Skills、Harness 四件套](enterprise-agent-tooling-harness.md) — 工具契约与确认点实现
  - [Agent 是任务执行系统:十个工程要点](agent-as-task-execution-system.md) — 控制循环与工具边界
