> 原文存档:微信文章《AI Agent 统一插头了,Skill 迎来规范化》(公众号:再跟 AI 死磕的路上)
> 原始链接:https://mp.weixin.qq.com/s/7F7MVlCJzQjd2dVAMqxjBA
> 抓取日期:2026-08-12(手机 UA curl,避开微信环境验证)
> 对应规范:Agent Plugins Specification 1.0.0(https://agent-plugins.org/specification,Working Draft,2026-08-06 发布)
> 用途:整理收件箱素材(用户标注:skill 新规范),正文原样保留供追溯。

---



昨晚谷歌官方博客一篇公告砸下来：

**谷歌、微软、亚马逊、OpenAI、Cursor、Vercel——六巨头联手，给 AI Agent 定了个"统一插头"。**

8 月 6 日，Agent Plugins 1.0.0 正式发布。来源：谷歌开发者博客，2026-08-06。

说真的，我研究了一晚上。这事的重量，比一个新模型发布大多了。

因为它是冲着咱们每一个做 Agent 的人来的。😏

## 01 ｜ 你的 Skill，换个客户端就废了

先说你最痛的一幕。

你在 WorkBuddy 里写了个"查数据库周报"的 Skill，SKILL.md 写得漂漂亮亮。结果换到 Codex 上用——完了，SKILL.md 能读，但**配它的那堆"环境"全乱套**：

脚本路径不一样，有的在沙箱里、有的不在，MCP 连接方式也得重配。

官方一句话点破：

>

**"核心问题不是组件，是 manifest。"**

组件都是好的，装组件的"盒子"每个客户端自己发明一套。**碎片化的根源从来不是内容不通用，是盒子不通用。** 这话说到我心坎里了。💔

## 02 ｜ 解法：一个目录，一份规范

Agent Plugins 的解法，克制得让我意外：**一个插件，就是一个目录。把 skills 放进 reports-plugin 目录内。**

```
reports-plugin/ 
```

```
├── plugin.json          # 就两行：schema + name 
```

```
├── skills/              # SKILL.md 放这，沿用 Agent Skills 标准 
```

```
│   └── summarize/ 
```

```
│       ├── SKILL.md 
```

```
│       ├── scripts/ 
```

```
│       └── references/ 
```

```
├── mcp.json             # 每个 server 显式声明 type 
```

```
└── com.example.client/  # hooks/路径/客户端配置放这
```

plugin.json 就两行：

```
{   
```

```
"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",   
```

```
"name": "reports-plugin" 
```

```
}
```

三个设计，我一个比一个喜欢：

- **MCP 不用"猜"了**

：每个 server 显式声明 type，客户端永远不用从配置形状推断传输方式——你踩过的"沙箱/非沙箱路径差异"，根源就是这种"猜"，现在不猜了。
- **组件独立失败，互不拖累**

：某个 MCP server 挂了，客户端跳过它继续加载，Skill 照常干活。
- **环境问题有家了**

：com.example.client/ 专门放单客户端的环境配置，不认识的客户端直接忽略。可移植的保持纯净，不可移植的有处安放，两边不打架。

规范原文：agent-plugins.org/specification。

>

**一个插件就是一个目录，这种"克制"恰恰是它最聪明的地方。** 🎯

## 03 ｜ 长远看：这是 AI 世界的 USB-C 时刻

这波操作，真正的重点是名单。

**Amazon、Cursor、Microsoft、OpenAI、Vercel 当核心维护者，谷歌 8 月 6 日刚加入。** 你品品——OpenAI 和微软是两家公司，谷歌和它们同台；Cursor 是后起之秀，Vercel 做前端的也来了。

**竞争对手愿意坐一张桌子定标准，说明碎片化已经痛到他们自己都受不了了。**

这就是 AI 世界的 USB-C 时刻。以前每个手机厂商一个充电口，现在统一了，充电线到处能用。Skill 是"充电线"，Plugin 格式就是"USB-C 接口"。

**我个人判断**，三个连锁反应要来了：

- **竞争焦点转移**

：以前比"谁锁死更多开发者"，以后比"谁内容生态更厚"
- **MCP 地位不降反升**

：Plugin 只是"包装盒"，里面的执行层还是 MCP + Skills，地基没变
- **封闭生态被边缘化**

：不支持 Agent Plugins 的工具，长期会被市场淘汰——就像不支持 USB-C 的手机

但有一句边界话必须说：**标准解决"放哪"，不解决"信不信"。** 插件能到处跑，但装谁的插件、它有没有权限碰你的数据，规范明确不负责。安全责任，永远是使用者自己的。🔒

## 04 ｜ WorkBuddy 用户：你先别慌

我知道你真正想问的是这个。

先摆事实（来源：腾讯云官方文档与开发者社区）：

- **WorkBuddy 是腾讯 CodeBuddy 团队做的**

桌面 Agent，2026 年 3 月上线，已经支持 MCP、Skills、插件市场
- **CodeBuddy 目前用的是自己的插件规范**

（.codebuddy-plugin/），不是 Agent Plugins 格式
- **目前没有公开信息**

表明 WorkBuddy/CodeBuddy 已兼容 Agent Plugins 1.0

维度

WorkBuddy（现在）

Agent Plugins（标准）

插件格式.codebuddy-plugin/

（腾讯自家）plugin.json

（开放标准）

Skills 支持

✅ 支持

✅ 标准内含

MCP 支持

✅ 支持

✅ 标准内含

跨工具复用

❌ 只在腾讯生态

✅ 到处跑

我的判断分三层：

**短期（现在）**：对你用 WorkBuddy 没有任何影响，技能照常跑。

**中期（半年到一年）**：腾讯大概率会跟进。原因很简单——开放标准跟进成本低、收益高，不兼容就会流失用户。**判断依据：CodeBuddy 已经是"国内首个支持插件/IDE/CLI 三形态"的工具，没理由逆着行业标准走。**

**迁移成本**：很低。你的 SKILL.md 内容完全不用重写，Plugin 只是外面加一层"包装盒"。

>

**Skill 是内容，Plugin 是包装——包装可以换，内容不用动。**

## 05 ｜ 我的 Skill 到底要不要迁？

直接回答：**不用，至少现在不用。**

这是官方明确表态的，不是我猜的。官方原话：**"不是每个 Skill 都需要做成 Plugin。如果你只发布一个 Skill，或者只接一个 MCP server，单独用原来的方式更简单。"**

Plugin 的适用场景是：**多个组件需要"一起走、一起分发"**——比如"脚本 + 数据库连接 + 周报技能"打包成一套，换客户端不散架。单个 Skill 打包反而画蛇添足。

三条建议，拿走不谢：

- **别急着迁移**

——你现在写的 Skill 不用动
- **盯两个信号**

——Codex CLI 0.146 已支持识别 plugin.json，Chrome DevTools MCP 已支持插件安装。**主流客户端跟进的速度，比想象中快**
- **新写的 Skill，按 Plugin 思维组织**

——SKILL.md、scripts、references 按标准目录放好，未来想打包随时能打，成本趋近于零

---

## 写在最后

Skill 没死，它进化成了 Plugin。

标准统一之后，真正的竞争才刚开始——拼的不再是谁的格式好，而是**谁的内容生态更厚**。对咱们做 Agent 的人来说，这反而是好事：写一次，到处用，把精力省下来做真正有价值的东西。💪

看到这，如果觉得还行，点赞、收藏、转发三连随你挑；想追更就星标⭐。谢谢，我们下篇见。

---

### 📎 新闻来源

-

谷歌开发者博客 https://developers.googleblog.com/agent-plugins-package-your-skills-tools-and-more/

- 规范原文：https://agent-plugins.org/specification

[]() []() []() []() []() []() []() []() []() []()
