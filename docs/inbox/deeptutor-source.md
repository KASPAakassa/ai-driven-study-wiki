# 原始资料:25k Star,港大开源了一款 AI 个性化辅导私教,在 GitHub 上杀疯了!(DeepTutor)

> 来源:微信公众号「极客之家」;原文链接:https://mp.weixin.qq.com/s/MfTnEwjQlBJX4bf0JsqbRw
> 抓取日期:2026-08-09;状态:已整理为 docs/04-practice/deeptutor-agent-workspace.md
> 性质:香港大学数据科学实验室 DeepTutor(25k Star)开源 AI 学习工作空间拆解:六模式共享 Agent 引擎、Partners 接入本地 Claude Code/Codex、三层记忆、多引擎 RAG、Book/Co-Writer/My Agents 等九模块

---

GitHub 25k Star，香港大学数据科学实验室的DeepTutor，开源100天左右冲到20k。
我翻了代码，Agent循环写在底层，Chat、Quiz、Research、Solve、Visualize、Mastery Path六种模式共享一个runtime，支持本地模型和Docker一键部署。
这是一个智能体原生的学习工作区，提供终身个性化辅导，出题、解题、辅导学习全包了干，非常具有普惠意义的AI工具。
简介
DeepTutor是一个开源的AI学习工作空间，辅导、解题、测验、研究、可视化、掌握练习六种学习模式塞进同一个Agent引擎，数据在所有工作流里共享，项目由港大数据科学实验室维护。
功能详情
1、Chat：六种模式共享一个Agent引擎
打开DeepTutor，左边导航栏挂着九个模块：Home、Partners、My Agents、Co-Writer、Book、Learning Space、Memory、Knowledge Center、Settings。
Chat表面看是个聊天窗口，实际上六种学习模式都从这里进。切到解题模式，刚才聊过的知识点还在上下文里，切到测验模式，系统自动把讨论内容收进题库，换目标，引擎是不会变的。
2、Partners：接入本地Claude Code和Codex
Partners可以在任意对话轮次里接入本地跑的Claude Code或Codex，Partner有自己的Persona、私有知识库和技能，保持独立记忆。
对话支持分支、续聊、删除，带可回放的操作轨迹，后来又加了Mattermost通道。在DeepTutor里问代码问题，它调的是我本地跑的Claude Code，上下文全在，不用复制粘贴到IDE再粘回来。
3、My Agents：自定义Agent的独立空间
My Agents 这里可以创建和管理我们自己的Agent，给每个Agent配不同的Persona、知识库和技能。
Agent之间记忆隔离，但可以通过Chat统一调度。
4、Co-Writer：多文档协同写作
Co-Writer支持多文档协同写作，同时打开多个文档，AI根据知识库内容辅助写作。支持智能编辑、自动标注和TTS朗读，写完后可以直接保存到笔记本，或者导出Markdown。
5、Book：活书编译器
Book Engine能把笔记和对话内容编译成HTML书籍。左边章节导航，右边内容区，支持插入文本、标注、测验、代码、时间线、闪卡、图表、交互式动画和深度探索。
每个章节都可以直接对话提问。
6、Knowledge Center：多引擎RAG与知识库版本管理
Knowledge Center管理知识库和检索引擎，RAG支持LlamaIndex、PageIndex、GraphRAG、LightRAG，还能链Obsidian Vault。文档支持PDF、DOCX、XLSX、PPTX，浏览器里直接预览，索引做了版本管理，重新建不会覆盖旧的。
7、Learning Space：技能市场与掌握路径
Learning Space是技能管理和学习路径的入口，Skills面板展示已安装的技能，可以从EduHub导入社区技能。Mastery Path是掌握练习的仪表盘，每类题目必须达标才能往下走。
8、Memory：三层记忆与Graph溯源
Memory比聊天记录复杂，L1存原始对话，L2做摘要，L3做综合提炼，Memory Graph能把每条结论追溯到原始证据。
打开面板，它确实记了之前问过的内容，而且告诉我是从哪段对话里摘出来的。这比那些只会说"我记住了"的AI实在。Memory面板在v1.4.6升到了顶级导航，随时可查可编辑。删错记忆也不会影响其他层，三层独立管理。
9、Settings：统一配置面板
Settings把模型、嵌入、TTS、搜索、端口配置全收进一个面板。
LLM提供商支持OpenAI、Anthropic、Google、Azure等主流接口，也支持Ollama、LM Studio、llama.cpp、VLLM等本地模型。
Embedding可以单独配置，不跟LLM绑死。我配了DeepSeek当聊天模型，BGE-M3当嵌入模型，互不干扰。
还可以自定义选择界面主题，深色/浅色，还可以选择展示的语言中文/英文。
快速开始
我实际用的是PyPI安装，五分钟跑起来。
mkdir my-deeptutor && cd my-deeptutor
pip install -U deeptutor
deeptutor init
deeptutor startdeeptutor init会提示选端口、LLM提供商、API key和embedding模型，默认前端跑在3782端口，后端在8001。
Docker也有官方镜像，ghcr.io/hkuds/deeptutor:latest，挂个卷就能跑，配置和知识库不会丢。
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest只暴露3782就行，Next.js中间件在容器内部转发API和WebSocket。
本地Ollama或LM Studio的用户，Docker里连host服务要加--add-host=host.docker.internal:host-gateway，然后在Settings里把Base URL指向http://host.docker.internal:11434/v1。
CLI-only模式也有，deeptutor chat进交互式REPL，deeptutor kb create建知识库，deeptutor memory show看记忆状态。
我的看法
DeepTutor的代码结构不一样，Agent循环写在底层。Partners能直接@Claude Code，我本地跑的模型和知识库它都能读到，这个设计对我这种习惯本地部署的人很友好。
问题也有，迭代太快，文档有时候比代码慢半拍。RAG引擎给了四个选择，我没看出来官方推荐哪个，对新手不友好。Memory三层设计理论上不错，但我没长期用，L3提炼会不会丢细节，现在还不好说。
我装完之后第一件事是配Ollama，embedding模型选错了，知识库建到一半报错。翻文档没找到明确说明，最后看了眼源码才搞懂，这种地方对普通用户不友好。
需要把AI学习工具串起来，还要接本地模型，DeepTutor是GitHub上少数认真做基建的，25k Star有它的道理。
GitHub地址：
https://github.com/HKUDS/DeepTutor

点击下方卡片，关注极客之家
这个公众号曾分享过许多有趣的开源项目。如果你不想逐篇翻阅历史文章，也可以直接关注微信公众号“极客之家”，通过后台留言与我们互动交流