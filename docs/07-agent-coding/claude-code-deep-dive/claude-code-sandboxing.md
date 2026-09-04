# Claude Code Sandboxing:双边界隔离与凭证外置

> **一句话摘要**:Anthropic 用 **OS 级原语(bubblewrap / macOS seatbelt)** 给 Claude Code 做两道独立边界——文件系统隔离(只读写 cwd)+ 网络隔离(unix domain socket 连外部代理,代理按域名白名单放行并做人工确认),内测权限提示减少 **84%**。核心模式:**凭证永不进沙箱**——沙箱内只有 scoped credential,真实 token 由外部代理在验证后才附加。这是自建 agent 安全基线的模板。
>
> **来源**:Anthropic Engineering《Beyond permission prompts: making Claude Code more secure and autonomous》(https://www.anthropic.com/engineering/claude-code-sandboxing,2025-10-20)

## 概念

### 问题:权限提示的困境

早期 Claude Code 靠**权限提示(permission prompts)**让用户逐个批准工具调用。问题:

- 高频打断导致 **approval fatigue**(用户麻木,看到就允许,安全失效);
- 要么全允许(危险),要么被提示淹没(低效)。

### 解法:从"问一次"到"划边界"

Sandboxing 用 **OS 级隔离原语**(Linux bubblewrap / macOS seatbelt)把 agent 关进两道边界,边界内自由行动、边界外系统兜底——**把安全从"每次批准"变成"结构性约束"**。内测效果:**权限提示减少 84%**。

## 原理(两道边界,缺一不可)

### 边界一:文件系统隔离

agent 进程**只能读写 cwd(工作目录)**——看不到也写不到其它文件。若无此边界,agent 可读取 `~/.ssh`、`~/.aws` 等敏感文件,把密钥窃走。

### 边界二:网络隔离

agent 的**所有网络流量走 unix domain socket 连到外部代理**;代理按**域名白名单**放行,超出白名单的请求做**人工确认**。若无此边界,agent 可把窃取的数据外传。

**两者必须同时生效**:只有文件系统隔离而无网络隔离,agent 能把读到的 SSH key 发出去;只有网络隔离而无文件系统隔离,agent 可从外部拉恶意代码执行。两道边界是**组合拳**。

### 凭证外置模式(核心模式)

沙箱内**永远没有真实凭证**:

- **git**:Claude Code on the web 的 git 走自定义代理——沙箱内只有 scoped credential,代理校验分支/目标仓库后才附加真实 token;
- **MCP OAuth**:token 存 vault,经专用 proxy 按 session 取用;
- 原则:**沙箱进程拿不到、也猜不到真实凭证**;凭证的发放与使用由沙箱外的信任代理控制。

### 开放实现

运行时开源:`github.com/anthropic-experimental/sandbox-runtime`——可自建、可审计、可改造。

## 代码 / 实现

```text
┌─────────────────────────────────────────────┐
│ Sandbox(agent 进程)                          │
│  • 只能读写 cwd(文件系统隔离)                │
│  • 网络:unix socket → 外部代理               │
│  • 只有 scoped credential,无真实 token       │
└──────────┬──────────────────────────────────┘
           │ unix domain socket
┌──────────▼──────────────────────────────────┐
│ Proxy(沙箱外)                                │
│  • 域名白名单放行 + 人工确认                  │
│  • 验证请求后附加真实凭证(git token / OAuth) │
│  • 凭证存在 vault / 本地,永不进沙箱          │
└─────────────────────────────────────────────┘
```

自建安全基线的检查项:

1. 文件系统隔离:agent 是否读不到 `~/.ssh`、`~/.aws`、`/etc/passwd` 等;
2. 网络隔离:所有出网流量是否经白名单代理,敏感域名是否人工确认;
3. 凭证外置:沙箱内是否有任何真实 token;删除凭证后 agent 是否仍能完成任务(通过代理);
4. 组合验证:同时关闭两道边界各测一次,确认没有单边绕过的路径(读密钥 → 外传)。

## 实践 / 应用

- **对自建 agent 平台**:双边界 + 凭证外置是最小安全基线;权限提示(approval fatigue)本质是"人肉防火墙",应被结构性约束取代;
- **威胁模型**:agent 可能被 prompt injection 操纵——安全不能依赖"agent 不会做坏事",而要让**做不了坏事**;
- **取舍**:白名单网络牺牲灵活性,但保住机密;人工确认保留给高价值/高风险动作;
- 与 [Agent 效果优化实战](../../04-practice/agent-effect-optimization-practice.md) 的"只读权限做成系统能力"同理念:安全靠系统能力,不靠提示词。

## 总结

1. **从"权限提示"到"结构性边界"**:沙箱用 OS 级原语把安全变成约束,权限提示减少 84%,缓解 approval fatigue。
2. **两道边界是组合拳**:文件系统隔离(只读写 cwd)+ 网络隔离(白名单代理),缺一不可。
3. **凭证永不进沙箱**:沙箱内只有 scoped credential,真实 token 由外部代理验证后附加——这是最值得抄的模式。
4. **开放实现**:sandbox-runtime 开源,可自建、可审计。
5. **威胁模型**:防的不是"agent 会做坏事",而是让"做不了坏事"——prompt injection 也带不走机密。

**下一步学什么**:读 [Agent 生产架构](../../03-agents/agent-production-architecture.md)(权限洋葱/部署)与 [企业四道防线](../../06-enterprise/ontology-agent-adoption/enterprise-agent-production-deployment.md);想动手用 sandbox-runtime 或 bubblewrap/seatbelt 自建沙箱。

## 延伸阅读

- 站内:[Agent 生产架构](../../03-agents/agent-production-architecture.md)、[AI Coding Harness 设计经验](../experience/ai-coding-harness-design.md)、[Agent 安全审计实战](../../04-practice/agent-security-audit-practice.md)、[和 AI 写代码:7 条安全规范](../experience/ai-coding-7-safety-rules.md)
- 外部:原文(https://www.anthropic.com/engineering/claude-code-sandboxing);sandbox-runtime(https://github.com/anthropic-experimental/sandbox-runtime)
