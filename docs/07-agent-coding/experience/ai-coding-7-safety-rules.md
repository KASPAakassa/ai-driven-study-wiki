# 和 AI 一起写代码半年:7 条救命操作规范(附 Skill 模板)

> **一句话摘要**:AI 能帮你写实现,但**流程和架构必须自己把关**——它不是故意的,只是按你的需求跑;你不在前面设好边界,后面就得返工。半年 AI 协作 + 一次差点返工后,作者整理出 7 条安全操作规范,做成 OpenCode Skill 每次新任务自动加载:需求边界先确认、架构自己把关、配置单一源、前端必重建、启动即报错、安全校验、测试+冒烟。关键不是"prompt 写得多华丽",而是"约束条件给得够不够清楚"。
>
> **来源**:微信公众号「Simple测试手记」《和AI一起写代码半年后,我给自己定了7条救命操作规范》,https://mp.weixin.qq.com/s/xR6jO-bLIxZZxG15CMYWew;原始资料存档于 `docs/inbox/ai-coding-safety-rules-source.md`

## 概念:一次差点返工,换来一份开工规范

TCP 设备接入测试平台,两周零碎时间 AI 搭出 7 个页面,收尾验收时问题一个接一个:

| 问题 | 根因 |
| --- | --- |
| 改了 .env 忘了改部署脚本,设备连不上 | 配置在多处维护,改一处漏一处 |
| 前端改完用 `--skip-build` 部署,页面上还是旧的 | 跳过构建,上传的还是旧 dist |
| 修复过的问题重复出现(尤其前端样式) | 没有把修复沉淀成规则 |
| 同一业务字段,不同模块用两套字典,前端校验漏了 | 数据口径不统一 |

!!! tip "核心判断"
    **AI 能帮你写实现,但流程和架构必须自己把关。** 没有前置约束时,AI 会按它的"经验"(来自海量代码,不一定符合你的项目约定)自由发挥:引入不必要的第三方库、重复定义已存在的常量、忽略错误处理、不更新文档、用"能用就行"的方式绕过问题。

## 原理:7 条原则详解

### 1. 需求边界先确认,不让 AI 猜

有文档按文档做,模糊的先澄清;涉及多个方案时,列出优缺点请用户确认。避免"我觉得你需要这个"的情况——**"我以为是 A,你要的是 B"是返工的最大来源**。

### 2. 架构合理性要自己把关

AI 给的架构往往"能跑就行",但不一定可持续。开工前多问几句:模块职责单一吗?通用能力散落了吗?后续扩展会大改吗?

!!! note "与站内 [Spec-First 决策栈](spec-first-decision-stack.md) 的呼应"
    "先拆本质再动手"在这里落成具体的三问——职责单一、能力收敛、扩展友好。

### 3. 配置只维护一处

环境变量、代码常量、配置文件各一份,改一处漏一处。规范:**配置必须单一文件处理,不要重复定义**(单一数据源原则,呼应 [Vibe Flowing 的 flow-config](../../04-practice/ai-native-dev-team-vibeflowing.md))。

### 4. 前端改完必须重新构建(最痛的坑)

`.vue`/`.ts` 改完用 `--skip-build` 部署,上传的还是旧 dist。规范:**改前端必须完整构建,部署后检查产物 hash**——"能访问就行"不算数,要验证部署的是新产物。

### 5. 关键配置启动时报错,别等运行到一半

配置缺失时,启动就明确报错——**问题暴露越早,修复成本越低**(与 [5 个决策](../../03-agents/agent-system-5-decisions.md) 的"失败即停、原因清晰"同源)。

### 6. 安全:不硬编码、不泄露、要校验

密钥走环境变量,外部输入做校验,日志不打印敏感字段。**安全这件事,AI 不会主动替你考虑**。

### 7. 改后跑测试,部署后做冒烟

不要只看构建成功:修改后跑已有测试,新功能补测试,部署后验证健康接口和关键页面(呼应 [OpenAI 官方 Prompt 指南](openai-prompt-guide.md) 的"生成后必须验证"与 [生产级 Agent 9 层架构](../../03-agents/ai-infra-layering.md) 的验证纪律)。

## 代码 / 实现:Skill 核心结构 + 开工规范检查器(纯 Python)

### Skill 核心结构(可直接借鉴)

```markdown
## 安全操作规范
### 1. 任务开始 checklist
1. 读取项目 AGENTS.md / README.md / 相关 skill
2. 确认需求边界和验收标准,不猜测、不扩展
3. 列出修改点、验证点、风险点
4. 实施 → 本地验证 → 部署验证 → 交付
### 2. 核心原则
- 单一数据源:配置、IP、状态只维护一处
- 前端变更必须重新构建,严禁用 --skip-build 部署
- 关键配置启动时校验,缺失直接报错
- 不硬编码密钥,日志不泄露敏感信息
- 修改后跑测试,部署后做冒烟测试
```

!!! tip "规范不用长"
    先把最容易踩坑的几条固定下来,后面边用边补——这正是 [AI Coding Harness 设计经验](ai-coding-harness-design.md) 的"护栏随需求生长"。

### 开工规范检查器(纯 Python,可运行)

把 7 条原则落成"每次开工先加载"的检查器:

```python
RULES = {
    "边界确认":  lambda s: s["需求已澄清"],              # 规则 1
    "架构把关":  lambda s: s["已过三问"],                # 规则 2
    "配置单一源": lambda s: s["配置单文件"],              # 规则 3
    "前端重建":  lambda s: not s["用了skip_build"],      # 规则 4
    "启动报错":  lambda s: s["配置启动校验"],            # 规则 5
    "安全校验":  lambda s: s["无硬编码密钥"] and s["输入已校验"],  # 规则 6
    "测试冒烟":  lambda s: s["已跑测试"] and s["已冒烟"],        # 规则 7
}

def open_task_checklist(project: dict) -> dict:
    """开工前检查:未满足的规则列出并给出修复建议(每次新任务先跑)"""
    violations = []
    for rule, check in RULES.items():
        if not check(project):
            violations.append(rule)
    return {"status": "PASS" if not violations else "BLOCK",
            "violations": violations,
            "advice": "先补齐违规项再让 AI 动手,否则后面返工" if violations else "可以开工"}

# 演练:上次返工时的项目状态(缺边界确认、前端跳过构建、无测试冒烟)
bad = {"需求已澄清": False, "已过三问": True, "配置单文件": False,
       "用了skip_build": True, "配置启动校验": False,
       "无硬编码密钥": True, "输入已校验": True, "已跑测试": False, "已冒烟": False}
r = open_task_checklist(bad)
print(f"检查结果: {r['status']} | 违规: {r['violations']} | {r['advice']}")
```

## 实践 / 应用:有规范前后对比与落地

| 维度 | 没有规范 | 有规范后 |
| --- | --- | --- |
| 返工 | "我以为是 A,你要的是 B" | 需求边界先确认,返工变少 |
| 代码质量 | AI 自由发挥,按海量经验 | 设计阶段主动想扩展/配置重复/通用能力 |
| 部署信心 | "能访问就行" | 检查产物 hash、调关键接口、看关键页面 |
| 协作 | 个人经验,新人难理解 | 规范透明,新人快速上手 |

**落地示例**(作者的部署脚本):先备份 `data` 和 `logs` → 清理旧产物 → 调 `/api/health` 接口确认服务正常——**不是"上传完就算了"**。

**适合给自己整理一份的人**:经常用 AI 辅助写代码 / 一人负责多个小项目 / 项目有前后端+部署+配置多环节 / 想减少低级错误和返工 / 正在从测试或业务角色往 AI 开发方向过渡。

!!! tip "与站内其他文章的呼应"
    - [AI 协作规则设计](../../03-agents/agent-collaboration-rules.md):那篇讲规则**怎么设计**(六维度框架),本文是个人实战的**具体规范清单**(7 条)+ Skill 载体;
    - [给 Coding Agent 立规矩](agent-rules-agents-md.md):"先读 AGENTS.md/README 再动手"正是规则文件的第一消费场景;
    - [AI Coding Harness 设计经验](ai-coding-harness-design.md):"开工 checklist"就是"让 AI 看见问题"的最小形态;
    - [AI Native 工作方式](ai-native-manage-5-things.md):"需求边界先确认"= 定目标,"配置单一源"= 定原则沉淀成机制。

## 总结

- **核心观点**:AI 是很好的助手但不是万能的——关键不是"prompt 写得多华丽",而是"**约束条件给得够不够清楚**";
- **7 条规范**:需求边界先确认 / 架构自己把关 / 配置单一源 / 前端必重建(查 hash)/ 启动即报错 / 安全不硬编码 / 测试+冒烟;
- **载体**:写成 Skill 每次新会话自动加载,先读项目文档 → 确认边界 → 列修改点/验证点/风险点 → 实施→本地验证→部署验证→交付;
- **一句话**:规范就是告诉 AI——我的项目是什么样、我喜欢怎么做设计、哪些错误我绝对不能接受;固定下来,效率和质量都稳定很多。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/xR6jO-bLIxZZxG15CMYWew;原始资料存档于 `docs/inbox/ai-coding-safety-rules-source.md`
- 站内:[AI 协作规则设计](../../03-agents/agent-collaboration-rules.md)(六维度设计)、[给 Coding Agent 立规矩](agent-rules-agents-md.md)(规则载体)、[AI Coding Harness 设计经验](ai-coding-harness-design.md)(护栏生长)、[AI Native 工作方式](ai-native-manage-5-things.md)(管理式五件事)、[OpenAI 官方 Prompt 指南](openai-prompt-guide.md)(验证才算完成)、[Spec-First 决策栈](spec-first-decision-stack.md)(先拆本质)
