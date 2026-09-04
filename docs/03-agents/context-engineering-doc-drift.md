# 文档漂移治理:从单一来源到 CI 文档门禁

> **一句话摘要**:文档漂移(documentation drift)是"代码变了、文档没变"的系统性问题,根源是文档游离在开发流程之外。本文整合三篇方法论文献(MadCap/Docuwiz/Everdone,营销型但方法论可参考):**Single-Source Governance 四要素、Docs-as-Code 工作流与"仅放 Git 不够需自动发布"的关键洞见、文档门禁做成 CI pass/fail**,并衔接站内已有的 [SSOT 方法论](../06-enterprise/ai-friendly-architecture/documentation-ssot-governance.md)(Falconer)。
>
> **来源**:MadCap《How to Prevent Content Drift Across Channels in 2026》、Docuwiz《Docs-as-Code: How to Prevent API Documentation Drift》、Everdone《Docs as a CI/CD Gate》,文献清单见 `docs/inbox/context-engineering-references-source.md`

## 概念:内容漂移与文档漂移

**内容漂移(content drift)**(MadCap 视角):同一内容源在各渠道(Web、PDF、帮助系统、移动端)或各文档副本之间逐渐失同步——分散的副本被独立修改后彼此矛盾,不再指向同一事实。危害:向用户传达相互冲突的信息、损害品牌信任与合规性、维护成本复利式增长。根源:多渠道手工维护同一内容;集中存放但无管理机制仍会漂移。

**文档漂移(documentation drift)**(Docuwiz 视角):文档不再反映软件/API 的真实行为。典型场景:API 新增 `role` 参数后代码正常运行,文档却仍显示旧请求结构。早期信号:工程师说"文档和 API 对不上"、示例跑不通、工程师改读后端源码而不信文档、文档更新滞后发版数天/数周、文档与代码分处两套系统。

## 原理:两大方法框架

### 框架一:Single-Source Governance 四要素(MadCap)

传统"纪律式"方案(季度评审/负责人/检查清单)**治标不治本**——评审发生在业务/发布变更流程之外、执行时上下文已褪色、依赖人的记忆与自觉、属"事后补救"而非"事前预防"。真正的 **Single-Source Governance** 四要素:

1. **清晰的所有权**——每个内容资产有明确、可追溯的负责人,决策与责任落到具体人;
2. **版本控制与变更追踪**——单一来源配版本历史与变更记录,任何改动可回溯、可回滚,始终能回答"哪个版本是正确版本";
3. **绑定业务触发器的评审周期**——评审不按日历(季度),而由业务事件(产品发布、规则变更、渠道上线)触发,**在上下文新鲜时更新**(呼应 SSOT 的"更新应成为发布副产品");
4. **自动化发布工作流**——单一来源经自动化流水线统一发布到所有渠道,消除手工多点复制。

**成熟治理的标志**:各渠道由同一来源驱动、几乎零手工复制;内容在业务事件发生时即时更新;任何资产的所有者与变更历史随时可指认。

### 框架二:Docs-as-Code 工作流与关键洞见(Docuwiz)

**文档漂移四成因**:

1. **文档在代码库之外**(Confluence/Notion/Google Docs):更新成为与开发流程脱节的额外手工任务;
2. **所有权分散**:开发者建 API、技术写手维护文档、DevRel 做开发者内容,沟通断层使代码变更不能及时到达;
3. **CI/CD 管道忽略文档**:构建/测试/部署已自动化,唯独文档游离在管道之外——漂移的最大来源之一;
4. **API 迭代快于文档更新**:没有自动化,文档根本跟不上高频发版。

**Docs-as-Code 工作流**(把文档当软件对待):

1. **文档进 Git**:与 API 代码同仓,开发者改端点时在同一 commit 更新文档;
2. **同 PR 评审**:一次 PR 同时含 API 改动、文档、示例 payload,评审者合并前核对文档是否如实反映新行为;
3. **版本控制**:每个改动可追踪、可评审、可回滚、可审计(多版本 API 场景尤为关键);
4. **CI/CD 校验**:自动化检查断链、缺失页面、过期示例、与 OpenAPI schema 不匹配。

!!! danger "关键洞见:仅放 Git 不够,需 Git 同步自动发布"
    即使已采纳 Docs-as-Code、文档已进 Git,漂移仍会出现——**因为发布环节仍是手动的**。流程常止步于"Git 更新→PR 评审→合并→手动发布";代码在 CI/CD 无缝流转,文档发布却依赖人工触发。合并后若无人显式发布,线上文档继续展示旧信息。**真正的解法是 Git 同步自动发布:merge 时自动发布文档,让"合并"与"文档可见"几乎没有间隙**。

## 代码 / 实现:文档门禁做成 CI pass/fail(Everdone)

**Documentation Gate(文档门禁)**:把文档校验做成 CI 的 **pass/fail 检查**,与编译、测试、静态检查并列,成为合并管线的硬性门槛。

**具体机制**:

- **触发规则**:函数/模块发生变更,若 PR 中没有对应文档更新,CI 判定 fail 并**阻塞合并**;
- **粒度**:变更映射定位到函数/模块级——"代码改了什么 → 哪段文档必须跟着改",而非笼统检查仓库里有没有人顺手改文档;
- **方法论实质**:把文档更新从"口头约定"提升为与测试同级的**强制性验收条件**——测试保护行为正确性,文档门禁保护知识一致性。

**AI 驱动文档门禁(语义比对而非文本比对)**:

- **传统文本比对的局限**:文档措辞变了但语义没变会被**误报**;代码行为变了而文档是复制粘贴(文本层无差异)会被**漏过**;
- **AI 语义比对**:理解代码变更的实际语义,判断现有文档是否仍准确描述该行为,仅在语义不一致时判 fail——容忍合理措辞差异,抓住真正的文档漂移。

```python
# 文档门禁概念示意(函数级变更映射到文档)
def documentation_gate(pr_changes, docs_index):
    """PR 中每个函数/模块变更,都必须在 docs_index 中找到对应文档更新"""
    for change in pr_changes:
        doc_key = docs_index.get(change.module)
        if not doc_key:
            return FAIL(f"{change.module} 变更但无对应文档更新,阻塞合并")
    return PASS
```

## 实践 / 应用:三篇文献的落地整合

### 与站内 SSOT 方法论的衔接

这三篇与站内 [SSOT 方法论](../06-enterprise/ai-friendly-architecture/documentation-ssot-governance.md)(Falconer)构成完整治理链条:

| 文献 | 贡献 | 对应 SSOT 步骤 |
| --- | --- | --- |
| MadCap | Single-Source Governance 四要素(所有权/版本追踪/业务触发评审/自动发布) | 所有权落实 + 持续更新 |
| Docuwiz | 漂移四成因 + Docs-as-Code + "自动发布"洞见 | 持续更新(PR 绑定)的深化 |
| Falconer(站内) | 审计→迁移→治理五步法 + 集中化≠SSOT | 全流程 |
| Everdone | 文档门禁 = CI pass/fail + AI 语义比对 | 工具侧自动化(CI 门禁) |

### 最佳实践清单

1. **把文档当代码**:存 Git、走 PR/评审/版本控制/分支策略;
2. **用 OpenAPI 等 schema 驱动文档**:自动生成端点、请求/响应、认证流;
3. **文档验证纳入 CI**:断链检查、schema 与文档一致性、缺页检测、构建成功;
4. **启用基于 Git 的发布**:merge 即自动更新文档;
5. **鼓励开发者所有权**:API 变更时文档必须同步变更;
6. **进阶**:把"文档是否更新"本身做成门禁项(函数级映射),用 AI 语义比对替代文本比对。

> **结论**:文档漂移是手工流程的必然结果,但完全可通过自动化和 Docs-as-Code 预防——"写更多文档不是解法,修复产出文档的流程才是",文档应与代码同速演进。

## 总结

- **两类漂移**:内容漂移(多渠道副本失同步)与文档漂移(代码变了文档没变),根源都是文档游离在开发流程之外;
- **Single-Source Governance 四要素**:清晰所有权 + 版本控制变更追踪 + 绑定业务触发器的评审周期 + 自动化发布工作流;
- **Docs-as-Code**:文档进 Git、同 PR 评审、版本控制、CI/CD 校验;**仅放 Git 不够,需 Git 同步自动发布**;
- **文档门禁**:函数/模块变更无文档更新则 CI 阻塞合并;AI 语义比对替代文本比对解决误报/漏报;
- **落地**:与站内 SSOT 五步法衔接,从"把文档当代码"开始,逐步到 CI 门禁;
- **下一步**:结合 [上下文工程管理方案](context-engineering-playbook.md)(文档是静态上下文层)与 [SSOT 方法论](../06-enterprise/ai-friendly-architecture/documentation-ssot-governance.md) 的完整链条。

## 延伸阅读

- MadCap:https://www.madcapsoftware.com/blog/prevent-content-drift-across-channels/
- Docuwiz:https://blog.docuwiz.io/p/docs-as-code-how-to-prevent-api-documentation
- Everdone:https://everdone.ai/whats-new/guides-resources/Docs-as-a-CI-CD-Gate-The-Simple-Pass-Fail-That-Keeps-Knowledge-Current
- 站内:[SSOT 方法论](../06-enterprise/ai-friendly-architecture/documentation-ssot-governance.md)(审计→迁移→治理五步法)、[上下文工程管理方案](context-engineering-playbook.md)(文档漂移治理章节)、[Gate 模式详解](../07-agent-coding/experience/gate-pattern.md)(门禁思路呼应)、[AI Friendly 后端架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md)
