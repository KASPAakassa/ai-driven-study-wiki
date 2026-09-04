# AutoAgent:全自动、零代码的 LLM Agent 框架(HKUDS)

> **一句话摘要**:AutoAgent 是一个"**用自然语言就能创建和部署 LLM Agent**"的全自动、零代码框架——不必写代码、不用配技术栈,纯对话即可生成工具、Agent 甚至多 Agent 工作流。论文将其设计为"自主的 Agent 操作系统"(Agent OS),由 **Agentic System Utilities、LLM 驱动的可执行引擎、自管理文件系统、Self-Play 定制模块** 四部分组成;项目提供 `user mode`(Deep Research)、`agent editor`、`workflow editor` 三种模式。另附**开发规范与可维护性五维实践**(命名/模块化/错误处理/文档/测试),并与其他模块交叉印证。
>
> **来源**:GitHub 仓库 https://github.com/HKUDS/AutoAgent(README + 论文 arXiv:2502.05957,作者 HKUDS 香港大学数据科学实验室);原始资料存档于 `docs/inbox/autoagent-source.md`

## 概念:零代码 Agent 框架是什么

- **AutoAgent 是什么**:港大 HKUDS 团队(与站内 [DeepTutor](../04-practice/deeptutor-agent-workspace.md) 同一实验室)开源的 LLM Agent 框架,前身是 MetaChain(v0.2.0 更名)。**核心主张**:全球只有 0.03% 的人具备编程能力,Agent 框架却普遍服务于开发者——AutoAgent 要"让不懂代码的人也能用自然语言构建自己的 Agent"。
- **三个关键词**:
  - **Fully-Automated(全自动)**:自动构建和编排协作式 Agent 系统,无需手工编码或技术配置;
  - **Zero-Code(零代码)**:任何人(无论有无编程经验)用自然语言创建、定制自己的 Agent、工具和工作流;
  - **Self-Developing(自进化)**:能自己创建新工具、新 Agent、新工作流,并反过来**更新 AutoAgent 自身**(通过克隆仓库镜像、自动提交改动)。
- **与其他框架的差异**:LangChain/AutoGen 等框架主要服务有技术背景的开发者;AutoAgent 把"框架"变成了一个**会用自然语言对话来生成代码并落盘的 Agent 系统**——你描述需求,它写代码、建工具、编排流程。

## 原理:Agent Operating System 的四组件

论文将 AutoAgent 设计为"自主的 Agent 操作系统",四个核心组件:

1. **Agentic System Utilities(Agent 化系统工具)**:把操作系统级能力(文件、Shell、环境)封装成 Agent 可调用的工具集;
2. **LLM-powered Actionable Engine(LLM 驱动的可执行引擎)**:根据高层任务描述**动态创建、优化、适配 Agent 工作流**——即使你无法完整说明实现细节,它也能生成可执行流程;
3. **Self-Managing File System(自管理文件系统)**:管理生成的工具/Agent/工作流代码的存取与组织,支撑"系统自我更新";
4. **Self-Play Agent Customization(Self-Play 定制模块)**:通过**受控的代码生成 + 迭代式自我改进**创建工具、Agent 与工作流——单 Agent 创建和多 Agent 工作流生成都走这条"Self-Play"路径。

!!! tip "关键机制:受控代码生成"
    AutoAgent 不是让模型直接"凭空变出"Agent,而是**在一个容器化( Docker)的 agent 交互环境里,克隆 AutoAgent 仓库镜像 → 生成新工具/Agent 的代码 → 写回仓库 → 更新索引**。这样"零代码"对用户成立,但对系统内部而言仍是受控、可审计的代码生成(支持 `git_clone` 与 `test_pull_name` 分支配置)。

## 代码 / 实现

### 安装

```bash
git clone https://github.com/HKUDS/AutoAgent.git
cd AutoAgent
pip install -e .
```

需要先安装 [Docker](https://www.docker.com/)——AutoAgent 用 Docker 容器化 agent 交互环境,首次运行会自动按机器架构拉取预构建镜像。

### API Keys 配置

创建 `.env` 文件(参考 `.env.template`),按需填写;不是所有 Key 都必须:

```bash
# Required Github Tokens of your own
GITHUB_AI_TOKEN=

# Optional API Keys
OPENAI_API_KEY=
DEEPSEEK_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
HUGGINGFACE_API_KEY=
GROQ_API_KEY=
XAI_API_KEY=
```

### 启动 CLI

```bash
auto main            # 完整版:user mode + agent editor + workflow editor
auto deep-research   # 轻量版:仅 user mode(即 Auto-Deep-Research 项目)
```

常用参数:

- `--container_name`:Docker 容器名(默认 `deepresearch`);
- `--port`:容器端口(默认 12346);
- `COMPLETION_MODEL`:LLM 模型名,按 [LiteLLM](https://github.com/BerriAI/litellm) 命名规则(默认 `claude-3-5-sonnet-20241022`);
- `API_BASE_URL`:LLM provider 的 base URL;
- `FN_CALL`:是否启用 function calling(大多数情况默认值已按模型名配好);
- `git_clone` / `test_pull_name`:agent editor / workflow editor 模式需要克隆仓库镜像并让 AutoAgent 自动更新自身(`auto main` 默认 True)。

```bash
# 例:用 DeepSeek 跑
# 在 .env 设置 DEEPSEEK_API_KEY,然后:
COMPLETION_MODEL=deepseek/deepseek-chat auto main
```

## 实践 / 应用

### 三种使用模式

| 模式 | 用途 | 特点 |
| **user mode**(Deep Research Agents) | 现成可用的多 Agent 系统:信息检索、复杂分析、综合报告生成 | 用 Claude 3.5 达到接近 Deep Research 的效果(而非 OpenAI o3);兼容任意 LLM(Deepseek-R1/Grok/Gemini 等);开源替代 $200/月的订阅;支持文件上传 |
| **agent editor** | 不用工作流,纯对话创建 Agent | 描述想要什么 Agent → 自动 profiling → 输出 Agent 档案;可再创建所需工具;也可选填"你想用这个 Agent 完成什么" |
| **workflow editor** | 用自然语言创建多 Agent 工作流 | 描述工作流 → 自动 profiling → 输出档案 → 创建(注意:此模式暂不支持工具创建) |

### 工程要点与注意

- **agent editor / workflow editor 依赖 git_clone**:需要把 AutoAgent 仓库镜像克隆进容器环境,让系统"自更新"——首次使用务必确认 `git_clone=True` 且设置了 `test_pull_name`(如 `autoagent_mirror`);
- **模型灵活性**:`COMPLETION_MODEL` 用 LiteLLM 命名,`API_BASE_URL` 可指向任意兼容端点——不锁死单一模型厂商;
- **定位**:更适合"**快速搭建 Agent 原型 / 非技术用户自助构建**"的场景;生产级深度定制(如精细权限、复杂 Harness 组装)仍建议看站内其他 Harness 框架的工程化方案。

### 核心知识抽取:AutoAgent 开发规范与可维护性(五维)

> 本小节由 CSDN《告别混乱代码:AutoAgent 开发规范与可维护性最佳实践指南》(https://blog.csdn.net/gitblog_00933/article/details/151784123)提炼。AutoAgent 是"零代码框架",但其**内部代码结构**同样需要工程化——以下五维规范不只是 AutoAgent 特有,而是"Agent 框架源码怎么写才可维护"的通用范式,与站内各模块交叉印证。

**① 命名规范:领域驱动命名,让代码自我解释**

- 代理类用 `*Agent` 后缀(如 `AgentCreatorAgent`)、工具类用 `*Tool` 后缀(如 `FileSurferTool`);
- 常量全大写 + 下划线(`MAX_RETRY_COUNT`);私有方法单下划线前缀(`_validate_agent_form`);
- 典范实现:`autoagent/agents/meta_agent/agent_creator.py` 中 `@register_agent(name="Agent Creator Agent", func_name="get_agent_creator_agent")` 装饰器 + 一句 docstring 说明职责。

**② 模块化设计:松耦合 + 装饰器注册 + 构造注入**

```text
agents/
├── meta_agent/          # 元代理模块(负责代理创建)
├── system_agent/        # 系统代理模块(处理系统级任务)
├── math/                # 领域专用代理
└── tool_retriver_agent.py  # 工具检索代理
```

- 新代理放对应功能目录;通过 `@register_agent` 装饰器注册(**声明式注册**,新增能力不侵入既有代码);
- 工具依赖用**构造函数注入**而非硬编码引用——这正是站内 [AI Friendly 后端架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md) 强调的"依赖显式化"在 Agent 框架里的落地。

**③ 错误处理:统一重试 + 自定义异常 + 上下文日志**

```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
def execute_command_with_retry(command: str):
    try:
        return execute_command(command)
    except CommandExecutionError as e:
        logger.error(f"Command failed (agent_id={current_agent_id}): {str(e)}")
        if "permission denied" in str(e):
            raise FatalError("权限不足，无法继续执行") from e
        raise  # 其他错误触发重试
```

- 可恢复错误用 tenacity 重试(指数退避);自定义异常继承 `AutoAgentBaseError`;
- **错误日志必须带上下文**(agent_id / task_id)——对应站内 [Agent 容错设计](../03-agents/agent-fault-tolerance-design.md) 中"错误分类→分层应对"的思路,以及 [企业 Agent 工程化(二)](../06-enterprise/ontology-agent-adoption/enterprise-agent-recovery-handoff.md) 的"后果半径四档"——注意区分**可重试错误 vs 致命错误**(权限不足直接抛 `FatalError` 而非无限重试)。

**④ 文档撰写:代码与文档同步**

- 类文档说明核心职责与使用场景;方法文档含 Args/Returns/Raises;复杂逻辑配流程图;
- 这正是站内 [文档漂移治理](../03-agents/context-engineering-doc-drift.md) 的微观形态——规范文档写在代码里,避免"代码变了文档没变"。

**⑤ 测试规范:三场景覆盖 + evaluation 目录**

- 每个代理/工具配套单元测试(Happy Path / 边界条件 / 异常场景),测试文件放对应模块 `tests/`;
- AutoAgent 提供 `evaluation/` 自动化评测框架,`python -m evaluation.math500.run_infer` 可跑;
- 与站内 [AI 时代 TDD 实践](../07-agent-coding/experience/ai-tdd-practice.md)(TDD 四层落地)呼应:Agent 代码同样要测试,且要测"模型行为"这类非确定性输出。

!!! tip "融合小结"
    AutoAgent 的五维规范(命名/模块化/错误处理/文档/测试)与站内知识是**同一套工程哲学在不同层的投影**:命名与模块化 → [AI Friendly 架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md);错误处理 → [Agent 容错设计](../03-agents/agent-fault-tolerance-design.md);文档 → [文档漂移治理](../03-agents/context-engineering-doc-drift.md);测试 → [AI TDD 实践](../07-agent-coding/experience/ai-tdd-practice.md);代码审查保障 → [Agentic Code Review](../07-agent-coding/experience/agentic-code-review.md)。

## 总结

1. **AutoAgent = 零代码 Agent 框架**:用自然语言对话即可生成工具、Agent 与多 Agent 工作流,瞄准全球 99.97% 的非开发者;
2. **四个设计组件**:System Utilities、Actionable Engine、Self-Managing File System、Self-Play 定制模块——本质是"会自我更新的 Agent OS";
3. **三种模式**:user mode(开箱即用的 Deep Research)、agent editor(纯对话建 Agent)、workflow editor(自然语言建工作流);
4. **实现关键**:Docker 容器 + 仓库镜像 + 受控代码生成,让"零代码"对用户成立而对系统可审计;
5. **开发规范五维**(命名/模块化/错误处理/文档/测试)是 Agent 框架源码可维护性的通用范式,与站内 [AI Friendly 架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md)、[Agent 容错设计](../03-agents/agent-fault-tolerance-design.md)、[AI TDD 实践](../07-agent-coding/experience/ai-tdd-practice.md) 等模块交叉印证;
6. **下一步**:对比站内 [PenguinHarness](penguin-harness.md)(同样"让 Agent 自主构建 Agent")理解两条自进化路径的差异,或对照 [Agent 框架总览](../03-agents/agent-frameworks.md) 看 AutoAgent 在框架谱系中的位置。

## 延伸阅读

- 站内:[PenguinHarness:让 Agent 自主构建 Agent](penguin-harness.md)(自进化平台对照)、[Pi Agent](pi-agent-plugins.md)(极简 Harness 对照)、[Agent 框架对比](../03-agents/agent-frameworks.md)、[Harness 章节首页](index.md)、[DeepTutor(同实验室)](../04-practice/deeptutor-agent-workspace.md)
- 规范融合点:[AI Friendly 后端架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md)(命名/模块化)、[Agent 容错设计](../03-agents/agent-fault-tolerance-design.md)(错误处理)、[文档漂移治理](../03-agents/context-engineering-doc-drift.md)(文档)、[AI TDD 实践](../07-agent-coding/experience/ai-tdd-practice.md)(测试)、[Agentic Code Review](../07-agent-coding/experience/agentic-code-review.md)(代码审查)
- 外部:GitHub https://github.com/HKUDS/AutoAgent;论文《AutoAgent: A Fully-Automated and Zero-Code Framework for LLM Agents》https://arxiv.org/abs/2502.05957;项目页 https://autoagent-ai.github.io;Auto-Deep-Research https://github.com/HKUDS/Auto-Deep-Research;开发规范指南《告别混乱代码:AutoAgent 开发规范与可维护性最佳实践指南》https://blog.csdn.net/gitblog_00933/article/details/151784123
