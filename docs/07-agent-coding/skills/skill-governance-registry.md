# Skill 治理:用 Nacos AI Registry 给团队 Skill 一份可信来源

> **一句话摘要**:Skill 散在个人电脑、群文件和各个 Agent 目录时,团队无法判断"哪份可信、哪个版本在线、出了问题退回哪里"。本文整理 Nacos AI Registry 的 Skill 治理链路——**本机统一 → 进 Registry → 元数据 → 安全准入 → 权限隔离 → 版本/标签/回滚 → 同步进 Agent**,并给出文档格式 Skill 的完整落地案例与两种部署形态。
>
> **来源**:微信公众号「Cloud Native」《一份可信来源,终结 Skill 管理混乱:Skill 治理最佳实践》(墨松、席翁),https://mp.weixin.qq.com/s/b88VRdAQ2u7IhQBqvNcnVg;原始资料存档于 `docs/inbox/skill-governance-source.md`

## 概念:Skill 管理混乱的五个症状

AI Agent 正在进入日常工作——写代码、做评审、整理文档、排查问题时,人们把反复使用的经验沉淀成 Skill。以**文档格式 Skill** 为例:你先把标题层级、参数表字段、风险说明、评审清单写成 Markdown Skill,在 Codex 里跑通;很快同事要在 Claude Code 生成同样格式的接口文档,项目成员想在 Cursor 或 Qoder 复用同一套规范——Skill 从"一个人的本地文件"变成"多人共用的团队规范",真正的麻烦随之出现:

1. **版本不一致**:Codex 里已补风险说明,Claude Code 还停在旧版,另一个成员的 Cursor 目录里又有一份同名 Skill;
2. **手动同步成本高**:每次改完要复制到其他 Agent 并提醒更新,漏掉一个目录或一个人,下次生成就回到旧规则;
3. **冲突不好判断**:两个 Agent/成员手里有同名 Skill 但内容不同,使用者很难确定该保留哪份;
4. **状态不可见**:哪些已同步、哪些有本地改动、哪些与其他副本冲突,单靠目录文件看不出来;
5. **共享缺少边界**:作为团队规范时,谁能改、谁能用、哪版稳定、怎么退回,都需要明确规则。

> **根因:不是 Agent 数量造成的,而是 Skill 没有统一入口。** 没有可信来源,使用者只能在本地目录、群文件和 Agent 配置之间反复确认。

**解决思路**:先把本机多个 Agent 的 Skill 收拢成一份,再把需要跨设备、团队共享、审核和发布的 Skill 放进 **Registry**,形成**远端可信来源**。

## 原理:六步治理链路

Nacos AI Registry 给出的路径,让 Skill 管理从"保存文件"变成"治理资产":

### 第一步:先本机统一,再进入 Registry

**Nacos Skill Sync 的 Local mode** 负责本机统一:在本机建立中心仓库,通过**软链接或复制**关联 Codex、Claude Code、Cursor、Qoder 等 Agent 目录。同一份 Skill 只维护一份,后续修改自动同步到本机多个 Agent,减少手动复制和同名副本冲突。

Local mode 的边界在本机。涉及**跨设备、团队共享、安全审核、版本发布和回滚**时,就需要远端统一入口——这就是 Registry 要解决的问题。Registry 支持多种来源:本地 Skill 通过 Nacos CLI 上传、平台内新建、外部市场/开源社区/存量目录导入。不同来源的 Skill 收敛到同一个资源入口,进入元数据、生命周期、安全审核和版本发布流程。

### 第二步:让 Skill 具备可管理的资源属性

进入 Registry 后,Skill 不再只是一份 Markdown 文件,而会带上:**名称、描述、owner、适用场景、标签、版本和生命周期状态**。这些信息展示:Skill 是干什么的、谁负责维护、适合哪些 Agent 或场景、当前处于 draft/review/online。Agent 也能按版本或 label 拉取(latest、stable、dev),关键工作流还能**锁定某个稳定版本**。

> 这一步解决"哪份可信"的问题。没有元数据和生命周期,只能靠人记;进入 Registry 后,Skill 才开始具备**资产属性**。

### 第三步:共享之前先完成准入

**能共享只解决效率,敢共享才进入工作流。** Registry 在 Skill 发布前承接安全扫描和审核流程。外部 Skill 可能包含外部 URL、危险命令、敏感信息、数据外发逻辑或不合规依赖;内部自研 Skill 也可能在迭代中引入错误规则。Registry 先把风险暴露出来,再交给 owner 结合业务判断——扫描发现可疑 Token、危险命令或外链则打回修改;误报或可接受风险则继续推进。

### 第四步:用隔离和权限控制共享边界

**共享不等于人人可改。** Registry 通过**命名空间隔离**不同团队、项目或环境(A 团队 Skill 不影响 B 团队,测试环境沉淀的 Skill 不直接进生产)。Skill 维度有**可见性控制**:适合共用的设为公开可用;涉及敏感流程、内部系统或特定项目的限定在成员范围内。owner 负责维护内容和发布节奏,协作者参与修改后新版本仍要经过审核和发布流程——避免"谁都能改、改完就生效"的失控状态。

### 第五步:用版本、Label 和回滚控制影响面

Skill 和代码一样需要可控发布:**draft → review → online**,发布后的版本保持稳定,不被随意覆盖。通过 **label 管理使用范围**:

- 文档格式 Skill 用 **stable** 标签,团队生成文档用同一套规则;
- 项目接入 Skill 保留 **dev** 标签,用来验证新流程;
- 排障 Skill 影响值班流程,先小范围验证再扩大。

Skill 出现错误版本时:下线问题版本、切回上一个稳定版本、或把 label 重新指向已验证版本。Registry 记录**谁上传、谁审核、谁发布、绑定了哪个 label**——问题定位不再靠事后猜测。

### 第六步:通过 Nacos CLI 和 Skill Sync 进入 Agent

Registry 里的可信版本最终要进入 Agent 日常工作流。**Nacos CLI** 负责连接 AI Registry:拉取已发布 Skill、上传本地沉淀的 Skill;**Skill Sync** 负责把同一份 Skill 同步到 Codex、Claude Code、Cursor、Qoder 等 Agent 目录。

这个环节只需要理解两件事:先在 Registry 中完成审核和发布,再通过 CLI / Skill Sync 把对应版本同步到本地 Agent。**只有完成这一步,Skill 才不只是平台里的资产,而是 Agent 实际执行任务时会遵守的工作方法。**

## 代码 / 实现:两种落地形态

AI Registry 有两种落地形态,服务同一个目标:**让 Skill 和其他 AI 资源进入统一治理入口**。差异主要在部署成本、网络可达性、治理能力接入方式。

| 方式 | 部署成本 | 核心能力 |
| --- | --- | --- |
| 开箱即用的 AI 治理中心 | 托管服务,免自建和维护 Registry 实例 | 公网/私网访问、安全护栏、工作空间/命名空间隔离,快速跑通上传、审核、发布、Agent 使用链路 |
| 自行部署的开源 Nacos AI Registry | 需要准备运行环境、存储、网络、运维和升级机制 | 私有化部署,企业认证/权限集成,安全扫描平台接入,发布系统和自研 Agent 平台集成 |

**开箱即用的 AI 治理中心**(阿里云 MSE 旗下 AI 资产管理平台):先跑通 Skill 管理闭环再逐步加深治理策略——进入创建工作空间/命名空间,上传高频 Skill,配置访问控制,本地 Agent 拉取已发布版本。公网访问让本地开发机、远程办公设备、新成员电脑不必先入同一私网;需要更强网络隔离时支持私网访问。

**自己部署的开源 Nacos AI Registry**:把 Registry 纳入企业自己的基础设施和治理流程——接入内部账号、权限系统、安全扫描平台、发布系统和自研 Agent 平台;基于 Nacos 开放能力扩展审核、分发和资源管理策略。

> **两种形态并不割裂**:先用开箱即用的 AI 治理中心验证链路;当私有化、定制化和平台集成成为核心诉求,再基于开源 Nacos AI Registry 做长期建设。

```bash
# 关键工具:Nacos CLI(连接 AI Registry,拉取/上传 Skill)
# https://github.com/nacos-group/nacos-cli
# Nacos Skill Sync(把同一份 Skill 同步到多个 Agent 目录)
# https://nacos.io/skill-sync/SKILL.md
```

## 实践 / 应用:文档格式 Skill 跑通闭环

比起一次性设计完整治理体系,更稳妥的方式是**先选一个高频 Skill,把接入、审核、发布和使用链路跑通**,再补充更细的权限、版本和回滚策略。

**场景**:团队文档格式不一致——技术方案、接口文档、故障复盘需要统一格式,标题层级、参数表字段、风险说明、评审清单没有固定规则时,Agent 生成的文档因人而异。过去发模板很容易变旧(有人复制上个月版本、有人复制去年版本,新同学还要问最新模板在哪)。

**落地五步**:

1. **第一次沉淀**:把标题层级、参数表字段、风险说明、评审检查项写进 `doc-format` Skill,由 owner 维护初始版本;进入 Registry,补充描述、owner、适用场景和标签,让成员能在统一入口找到它;
2. **准入**:文档格式 Skill 风险相对低,但仍走准入流程——Registry 发布前检查敏感信息、外部链接、危险命令;owner 处理误报或修改问题内容;外部市场导入的 Skill 走同一条路径;
3. **发布**:审核通过后发布为稳定版本并绑定 **stable** 标签,日常文档生成都使用 stable;调整参数表字段或风险说明时先发 **dev** 标签让少量成员试用,确认稳定再把 stable 指向新版本,出问题直接切回上一版;
4. **使用**:团队成员通过 Nacos CLI / Skill Sync 同步已发布 Skill 到本地 Agent,Codex、Claude Code、Cursor、Qoder 使用的都是 Registry 中经过审核和发布的版本——**复用的不再是一份容易过期的模板,而是一套持续进入 Agent 工作流的文档规范**;新成员加入、换设备、切换 Agent 都不需要重新找文件、复制目录、确认哪份最新;
5. **扩展**:跑通后同一条路径扩展到 PR Review、项目接入、发布检查、线上排障等高频场景——每个 Skill 都先有 owner 和适用场景,再进入审核、发布、分发和回滚流程。

## 展望:从 Skill 治理到 AI 资源自进化

Skill 管理只是第一步。Nacos AI Registry 后续要承接两类问题:

1. **Skill 自闭环进化**:Agent 在真实任务中产生经验 → 经验沉淀为候选 Skill → Registry 负责审核、发布和分发 → Agent 使用已发布 Skill 并在新任务中继续产生反馈。实践路径如 **SkillClaw**:从 Agent 的任务执行和反馈中提炼可复用经验、生成候选 Skill,再交由人审核后进入 Registry;
2. **接入 ARD,走向统一 AI Resource Registry**:ARD(Agentic Resource Discovery)是一套面向 Agentic Resources 的发现与搜索规范,用统一的 `ai-catalog`、搜索接口和版本化产物描述 **MCP、A2A Agent、Skill** 等资源(规范见 https://agenticresourcediscovery.org/spec/)。接入 ARD 后,治理对象从 Skill 扩展到 Prompt、MCP、AgentSpec 等 AI 资源——Agent 不需要分别理解每套资源管理方式,也能在同一套入口里处理资源来源、可信度、权限、版本和止损。

> **结语**:多 Agent 协作会越来越常见,团队真正需要管理的,不只是用哪个 Agent,而是这些 Agent 共同依赖的 Skill、Prompt 和其他 AI 资源。当 Skill 还散在个人电脑、群文件和临时脚本里,团队很难判断哪份可信、哪个版本在线、出了问题该退回哪里。把 Skill 放进 Registry,团队才能把"能用的经验"变成**可审核、可分发、可追溯的资产**。

## 总结

- **问题**:Skill 从个人文件变成团队规范后,出现版本不一致、手动同步成本高、冲突难判断、状态不可见、共享无边界——根因是**没有统一入口、没有可信来源**;
- **六步链路**:本机统一(Local mode)→ 进 Registry → 元数据化(名称/owner/标签/生命周期)→ 安全准入(扫描 + owner 审核)→ 权限隔离(命名空间 + 可见性)→ 版本/label/回滚 → 同步进 Agent;
- **两种形态**:开箱即用的 AI 治理中心(托管,快速跑通)vs 自建开源 Nacos AI Registry(私有化、深度集成),可先托管验证再自建长期建设;
- **落地方法**:选一个高频 Skill(如 doc-format)先跑通闭环,用 stable/dev 标签控制发布节奏,再横向扩展治理;
- **与站内关系**:本篇是**团队级治理体系**,与 [Agent Skill 版本管理](skill-version-management.md)(机制级:源码层 Git + 运行时层锁定)互补;下一步关注 Skill 自进化(SkillClaw)与 ARD 统一资源发现。

## 延伸阅读

- 原文:微信公众号「Cloud Native」《一份可信来源,终结 Skill 管理混乱:Skill 治理最佳实践》;姊妹篇《别再手动复制 Skill 了:多 Agent 时代的 Skill 管理方案》
- 资源:AI 治理中心控制台 https://mse.console.aliyun.com/#/ai-registry/workspace;Skill 管理指南 https://help.aliyun.com/zh/mse/user-guide/ai-registry-skill-management-guide;Nacos CLI https://github.com/nacos-group/nacos-cli;Nacos https://github.com/alibaba/nacos;Nacos Skill Sync https://nacos.io/skill-sync/SKILL.md;ARD 规范 https://agenticresourcediscovery.org/spec/
- 站内:[Agent Skill 版本管理](skill-version-management.md)(机制级版本管理)、[Skill 测评](skill-evaluation.md)(质量验证闭环)、[gstack 角色化虚拟团队](gstack-skills.md)(其 Skill 架构/升级/学习系统)、[mattpocock-skills](mattpocock-skills.md)(setup 外显化约定对照)、[Skill 收藏](index.md)
