# 原始资料:万字长文拆解Agent架构设计(五):技能系统设计

> 来源:微信公众号(Agent 架构设计系列),原文链接:https://mp.weixin.qq.com/s/2nlnrJeAlhZHGMMn_6udTg
> 抓取日期:2026-08-09;状态:已拆解入库(见归档记录)

---

本系列目标：拆解 Claude Code 源码，理解 Agent 底层架构的设计思路。核心方法：读源码 → 理解设计决策 → 用 TypeScript 手写核心逻辑。
每一篇聚焦一个子系统，讲清楚"为什么这么设计"比"代码怎么写"更重要。

引言
前四篇拆完了 Agent 的核心部件：记忆解决"它记得用户什么"，工具解决"它能做什么"，循环把两者串成每一轮的推理，协作让多个循环分工。
万字长文拆解Agent 架构设计（一）：记忆系统设计
万字长文拆解Agent 架构设计（二）：工具系统设计
万字长文拆解Agent 架构设计（三）：Agent Loop 设计
万字长文拆解Agent 架构设计（四）：多 Agent 协作
但有一类东西始终没地方放：某件事该怎么办的知识和流程。模型的训练数据里没有这些，工具又只提供原子动作，不提供办事规程。
Agent 架构怎么安置这种"规程知识"？最朴素的答案是全部写进系统提示——但是行不通：规程会越攒越多，上下文很快被塞满，而且规程越多模型越难聚焦。
Claude Code 的答案是技能系统：每份规程是一个独立的可加载单元，平时只暴露一行简介，模型判断用得上时，才把完整内容取进上下文。这种加载方式业内叫渐进式披露，Anthropic 在 2025 年底把它定为开放标准，生态很快攒到了上千个技能。
这篇讲清楚四件事：技能长什么样、渐进式披露怎么运转、技能和工具的边界在哪、以及为什么技能偏偏用 markdown 写。
Part 1：拆解 Claude Code 源码
1.1 技能的形态：一个文件夹
一个技能就是一个文件夹，里面必有一个 SKILL.md：

<!-- skills/release-checklist/SKILL.md -->---name: release-checklistdescription: 发版前预检：跑测试、核对变更日志、确认分支状态。用户提到”发版””上线””release”时使用。---你是发版守门员。按以下步骤预检： 1. 跑全量测试。2. 核对 CHANGELOG：每个改动都要有对应条目。3. 确认分支干净、已同步主干。 判断点：- 测试失败但只是网络类偶发错误 → 重试一次，仍失败再上报。- CHANGELOG 缺条目 → 从 git log 补齐，不要放过。- 任何一步拿不准 → 停下来问人，不要猜。
frontmatter 里是元数据（名字、简介），正文是指令。文件夹里还可以放辅助文件——脚本、模板、参考文档——供技能执行时按需取用。没有代码，全是文本和资料。
1.2 渐进式披露：三个阶段
技能进入模型视野分三步，每一步加载的内容都不一样：
第一步：启动时只挂目录。所有技能的 name 和 description 拼成一份清单，注入 system prompt。一百个技能也就一百行简介。正文一个字都不加载。

可用技能：- release-checklist：发版前预检：跑测试、核对变更日志……- pdf-extract：从 PDF 提取表格和正文……- weekly-report：按团队模板生成周报……需要时调用 Skill 工具，传入技能名，获取完整指南。
第二步：按需读正文。模型看到目录，判断当前任务要用 release-checklist，就调用 Skill 工具把它读进来。这一步发生之前，这个技能的完整内容不存在于上下文里。
第三步：按需取附件。正文里提到"用 scripts/check.sh 做检查"，模型再用普通文件工具去读那个脚本。附件是最后一层。
为什么要这么抠？算一笔账：一百个技能，每个正文平均两千 token，全量注入就是二十万 token——还没开工，桌子已经堆满了（第三篇讲过的上下文窗口）。目录模式下，同样的技能库只占三千 token 左右，而一次任务真正用到的技能通常只有一两个。
渐进式披露本身不是新发明，它是一个用了三十年的界面设计原则：设置页把常用项摆在明面，"高级选项"折叠起来，点到才展开。Claude Code 只是把同一原则用在了上下文管理上——Anthropic 官方文章的说法是"像一本编排良好的操作手册"。
1.3 技能与工具：操作手册与手头器具
技能看起来和第二篇的工具很像——都是扩展 Agent 能力的方式。但结构上完全不同：
关键区别在一条：技能可以编排工具。release-checklist 的正文里写着"跑测试、改 changelog、查分支"——落到执行上，是模型依次调用 bash、write_file、git 这些工具。工具提供原子动作，技能提供把动作组合成流程的经验：先做什么、后做什么、岔路口怎么选。Agent 缺了工具什么都做不了，缺了技能则什么都做不专业。
Part 2：为什么这样设计——从代码看决策
决策一：用 markdown 承载知识，而不是代码
把技能做成代码插件是最直觉的设计——很多系统就是这么做的。Claude Code 偏偏选了 markdown 文件夹。
这是个生态决策。知识藏在谁脑子里？不只是程序员：最懂发版流程的是运维，最懂客诉话术的是客服主管，最懂报表口径的是财务。写技能如果必须写代码，供给端就只剩程序员一小撮人；写技能如果只要写 markdown，供给端是所有懂行的人。
而且知识是变化最快的部分——流程每季度都在改，代码插件改一次要走构建、发布、升级；markdown 改完就生效，进 git 就有版本历史。第四篇见过同样的选择：子 Agent 的定义也是 markdown 加 frontmatter。Claude Code 对"知识类内容"一以贯之——凡是要让模型读、要让普通人写的，都用 markdown。
决策二：渐进式披露，而不是全量注入
全量注入所有技能，在技能少的时候没问题——三五个技能塞进去，也就几千 token。问题是技能库会增长，而这笔账不是线性的。
第一层成本是空间，1.2 已经算过。第二层成本更隐蔽：注意力。第三篇和第四篇反复讲过同一件事——上下文里的资料越多，模型越难聚焦。目录从十条涨到一百条，模型"选对技能"的难度也在涨，这和桌子越来越乱是一个道理。
渐进式披露同时解决两层：平时上下文里只有轻量目录；技能正文在真正被需要的那一刻才进场，而且一进场就带着任务的具体背景，利用率最高。反过来看全量注入的结局：提前塞进来的规程，等到真用上时，已经被后续对话挤到了上下文中部——第三篇讲过，那是最容易被模型忽略的位置。
决策三：description 是唯一的选中依据——又是 prompt 契约
模型凭什么决定该用哪个技能？只看目录里那一行 description。正文写得再好，description 没写好，技能就死在角落里；description 写得宽泛，技能又会被乱触发。
这已经是这个系列第三次撞见同一个设计了：第二篇里，工具靠 description 让模型知道"该不该调我"；第四篇里，子 Agent 靠 description 让主 Agent 决定"派谁去"；这一篇，技能靠 description 让模型决定"翻哪本手册"。在 Agent 系统里，自然语言描述就是接口契约——写描述不是填表，是做 API 设计。
对比一下：

坏：description: 发版助手好：description: 发版前预检：跑测试、核对变更日志、确认分支状态。 用户提到”发版””上线””release”时使用。
好的 description 有两半：做什么（给模型匹配任务用）、什么时候用（给模型触发时机用）。缺哪一半都会出错。
Part 3：手写核心逻辑（TypeScript）
延续系列的项目结构。这一篇的代码是系列里最少的一篇——因为技能系统本来就没多少"逻辑"，它的精髓全在信息编排上。
3.0 项目结构

skills/├── src/│ ├── skill-loader.ts # 发现技能文件夹，解析 SKILL.md│ ├── skill-menu.ts # 目录组装：注入 system prompt 的那一段│ └── skill-tool.ts # Skill 工具：按需取正文├── skills/ # 技能目录（每个子文件夹一个技能）├── package.json└── tsconfig.json
3.1 发现与解析：skill-loader.ts

interface SkillDefinition { name: string; description: string; // 进目录的那一行，决定技能何时被选中 body: string; // 完整指令，按需才加载 dir: string; // 技能文件夹路径，附件从这里取} function loadSkills(skillsDir: string): Map { const skills = new Map(); for (const dir of fs.readdirSync(skillsDir)) { const file = path.join(skillsDir, dir, 'SKILL.md'); if (!fs.existsSync(file)) continue;  const [, frontmatter, body] = fs.readFileSync(file, 'utf-8') .match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/)!; const meta = parseYaml(frontmatter); skills.set(meta.name, { name: meta.name, description: meta.description, body, dir }); } return skills;}
3.2 目录组装：skill-menu.ts

// 启动时注入 system prompt 的就是这一段——一百个技能也只占一百行function buildSkillMenu(skills: Map): string { const lines = [...skills.values()].map(s => `- ${s.name}：${s.description}`); return `可用技能：\n${lines.join('\n')}\n需要时调用 skill 工具，传入技能名，获取完整指南。`;}
skills 目录在启动时注入 system prompt 每轮都在。注意它和记忆系统的分工：记忆放"这个用户是谁"，技能目录放"会做哪些事"。
3.3 Skill 工具：skill-tool.ts

function createSkillTool(skills: Map): AgentTool { return { name: 'skill', description: '按名字加载一个技能的完整指南。技能清单见系统提示中的”可用技能”。', parameters: { name: { type: 'string' } }, async execute(_id, { name }) { const skill = skills.get(name); if (!skill) return { content: `未知技能：${name}` }; // 正文 + 附件清单。附件本身不进上下文，要用时模型自己用文件工具读 const files = fs.readdirSync(skill.dir).filter(f => f !== 'SKILL.md'); const fileList = files.length ? `\n\n附件（按需读取）：\n${files.join('\n')}` : ''; return { content: skill.body + fileList }; }, };}
渐进式披露在代码里就是这点东西：目录常驻，正文一次工具调用取回。
3.4 使用示例

const skills = loadSkills('./skills');systemPrompt += '\n\n' + buildSkillMenu(skills); // 目录上墙toolRegistry.set('skill', createSkillTool(skills)); // 取阅入口 await agentLoop.run('准备发个版，先帮我预检一下', sessionId); // 模型的执行流：// 1. 扫目录，”发版”命中 release-checklist 的 description// 2. 调 skill 工具取回完整指南（正文这时才进上下文）// 3. 按指南跑：bash 跑测试 → 发现一个网络类失败 → 命中”判断点”，重试一次// 4. write_file 补齐 CHANGELOG → 汇报预检结果// 第 3 步的重试决策不是代码写死的，是正文里的判断点 + 模型临场判断
到这里，前五篇覆盖了 Agent 架构的五个子系统——记忆、工具、循环、协作、技能。它们之间的依赖关系是：记忆和工具在最底层，相互独立；循环架在两者之上，把它们组装成每一轮的推理；协作是循环的复用（子 Agent 就是一个新循环），技能是循环的给养（目录注入上下文，正文按需进场，最终仍由工具落地）。理解依赖关系比理解每个子系统的细节更重要——它决定了你改一处的时候，哪些地方会受影响，哪些不会。
核心部件到这里就拆完了，系列下一步该看 Agent 怎么连进真实世界：连接器、外部系统、远程指挥。