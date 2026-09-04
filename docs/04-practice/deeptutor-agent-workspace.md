# DeepTutor:港大开源的 AI 个性化辅导工作空间——六模式共享一个 Agent 引擎

> **一句话摘要**:DeepTutor 是香港大学数据科学实验室开源(25k Star,100 天冲 20k)的 **AI 学习工作空间**——Chat、Quiz、Research、Solve、Visualize、Mastery Path 六种学习模式共享同一个 Agent 引擎,数据在所有工作流间共享;支持本地模型(Ollama/LM Studio)、Docker 一键部署、Partners 接入本地 Claude Code/Codex、三层记忆与多引擎 RAG。是"智能体原生学习应用"的完整参考实现。
>
> **来源**:微信公众号「极客之家」《25k Star,港大开源了一款 AI 个性化辅导私教,在 GitHub 上杀疯了!》,https://mp.weixin.qq.com/s/MfTnEwjQlBJX4bf0JsqbRw;GitHub https://github.com/HKUDS/DeepTutor;原始资料存档于 `docs/inbox/deeptutor-source.md`

## 概念:Agent 原生的学习工作区

**DeepTutor** 是香港大学数据科学实验室维护的开源 AI 学习工作空间——**辅导、解题、测验、研究、可视化、掌握练习六种学习模式塞进同一个 Agent 引擎,数据在所有工作流里共享**。它提供**终身个性化辅导**:出题、解题、辅导学习全包,定位普惠 AI 工具。

**核心设计**:Agent 循环写在底层,六种模式共享一个 runtime——切换模式不丢失上下文,知识在所有工作流间流动。

## 原理:九大模块拆解

### 1. Chat:六种模式共享一个 Agent 引擎

左边导航栏九个模块:Home、Partners、My Agents、Co-Writer、Book、Learning Space、Memory、Knowledge Center、Settings。**Chat 表面是聊天窗口,实际六种学习模式都从这里进**:切到解题模式,刚才聊过的知识点还在上下文里;切到测验模式,系统自动把讨论内容收进题库。**换目标,引擎不变**——这是 Agent 应用"多模式共享引擎"的典型设计。

### 2. Partners:接入本地 Claude Code 和 Codex

可以在任意对话轮次接入本地跑的 Claude Code 或 Codex。Partner 有自己的 **Persona、私有知识库和技能,保持独立记忆**。对话支持分支、续聊、删除,带**可回放的操作轨迹**,后来加了 Mattermost 通道。价值:在 DeepTutor 里问代码问题,调用的是本地 Claude Code,上下文全在,**不用复制粘贴到 IDE 再粘回来**。

### 3. My Agents:自定义 Agent 的独立空间

创建和管理自己的 Agent,给每个 Agent 配不同 Persona、知识库和技能。**Agent 之间记忆隔离,但可以通过 Chat 统一调度**。

### 4. Co-Writer:多文档协同写作

同时打开多个文档,AI 根据知识库内容辅助写作。支持智能编辑、自动标注和 TTS 朗读,写完后可保存到笔记本或导出 Markdown。

### 5. Book:活书编译器

**Book Engine 能把笔记和对话内容编译成 HTML 书籍**——左边章节导航,右边内容区,支持插入文本、标注、测验、代码、时间线、闪卡、图表、交互式动画和深度探索。每个章节都可以直接对话提问(文档即交互入口)。

### 6. Knowledge Center:多引擎 RAG 与知识库版本管理

管理知识库和检索引擎,**RAG 支持 LlamaIndex、PageIndex、GraphRAG、LightRAG**,还能链 Obsidian Vault。文档支持 PDF、DOCX、XLSX、PPTX,浏览器里直接预览;**索引做了版本管理,重新建不会覆盖旧的**。

### 7. Learning Space:技能市场与掌握路径

Skills 面板展示已安装技能,可从 **EduHub 导入社区技能**;Mastery Path 是掌握练习仪表盘(追踪学习进度与掌握程度)。

### 8. Memory:三层记忆设计

三层记忆架构(理论上不错,但作者坦言 L3 提炼会不会丢细节"现在还不好说")——与站内 [Agent 记忆体系](../03-agents/agent-memory-systems.md) 的分层思路一致。

## 代码 / 实现:部署与接入

- **Docker 一键部署**;本地 Ollama 或 LM Studio 用户,Docker 里连 host 服务要加 `--add-host=host.docker.internal:host-gateway`,然后 Settings 里把 Base URL 指向 `http://host.docker.internal:11434/v1`;
- **CLI-only 模式**:`deeptutor chat` 进交互式 REPL、`deeptutor kb create` 建知识库、`deeptutor memory show` 看记忆状态;
- **架构细节**:后端只暴露 3782 端口,Next.js 中间件在容器内部转发 API 和 WebSocket。

## 实践 / 应用:评价与参考价值

### 值得学习的设计

- **Agent 循环写在底层**:六种模式共享一个 runtime,上下文与数据跨工作流流动——这是"多能力 Agent 应用"的关键架构选择(对比"每种能力一个独立 bot"的碎片化方案);
- **Partners 接入本地工具**:直接 @ Claude Code/Codex,本地模型和知识库都能读到——对本地部署用户友好;
- **记忆隔离 + 统一调度**:My Agents 各自独立记忆,通过 Chat 统一调度;
- **知识库版本管理**:索引重建不覆盖旧版,避免 RAG 升级丢数据。

### 已知问题(作者实测)

- 迭代太快,**文档有时候比代码慢半拍**;
- RAG 给了四个引擎但**看不出官方推荐哪个**,对新手不友好;
- 三层记忆 L3 提炼**可能丢细节**;
- embedding 模型选错时知识库建到一半报错,文档没说明,**需要翻源码**——对普通用户不友好。

## 总结

- **定位**:香港大学开源(25k Star)的 AI 个性化辅导工作空间——六种学习模式共享一个 Agent 引擎,终身个性化辅导;
- **九模块**:Chat(六模式入口)/ Partners(接本地 Claude Code/Codex)/ My Agents(自定义 Agent,记忆隔离)/ Co-Writer(多文档协同写作)/ Book(活书编译器)/ Knowledge Center(多引擎 RAG+版本管理)/ Learning Space(技能市场+掌握路径)/ Memory(三层记忆)/ Settings;
- **核心架构**:Agent 循环写在底层、多模式共享 runtime、数据跨工作流流动、记忆隔离+统一调度;
- **部署**:Docker 一键 / CLI 模式 / 本地模型接入;
- **参考价值**:作为"智能体原生应用"的完整参考——多能力共享引擎、外部工具接入、知识资产管理(Book/RAG/记忆)三件套;
- **下一步**:对照站内 [Agent 应用开发实践](../03-agents/agent-practice.md)、[Agent 记忆体系](../03-agents/agent-memory-systems.md)、[RAG 检索增强生成](../02-llm/rag.md),理解教育类 Agent 应用的完整技术栈。

## 延伸阅读

- GitHub:https://github.com/HKUDS/DeepTutor;原文:https://mp.weixin.qq.com/s/MfTnEwjQlBJX4bf0JsqbRw
- 站内:[Agent 应用开发实践](../03-agents/agent-practice.md)、[Agent 记忆体系](../03-agents/agent-memory-systems.md)、[Agent 共享记忆](../03-agents/agent-shared-memory.md)(多 Agent 记忆池)、[RAG 检索增强生成](../02-llm/rag.md)(多引擎 RAG 原理)、[腾讯 Vibe Flowing](ai-native-dev-team-vibeflowing.md)(AI 原生应用案例)
