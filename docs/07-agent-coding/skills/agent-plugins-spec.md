# Agent Plugins 1.0:Skill 的"统一插头"规范

> **一句话摘要**:2026-08-06 谷歌、微软、亚马逊、OpenAI、Cursor、Vercel 六方联合发布 **Agent Plugins 1.0.0**——给 AI Agent 的扩展(Skill/MCP)定了一个跨客户端统一的"插头":**一个插件就是一个目录**(`plugin.json` + `skills/` + `mcp.json` + 客户端扩展目录)。碎片化的根源不是内容不通用,是"盒子"(manifest)不通用;这是 AI 世界的 USB-C 时刻。本文融合微信解读与规范原文,拆解目录模型、闭合 manifest、MCP 显式传输、组件独立失败、PLUGIN_ROOT/DATA 与迁移决策。
>
> **来源**:
> - 微信解读:再跟 AI 死磕的路上《AI Agent 统一插头了,Skill 迎来规范化》(https://mp.weixin.qq.com/s/7F7MVlCJzQjd2dVAMqxjBA)
> - 规范原文:Agent Plugins Specification 1.0.0(https://agent-plugins.org/specification,Working Draft,2026-08-06)
> - 发布公告:谷歌开发者博客(https://developers.googleblog.com/agent-plugins-package-your-skills-tools-and-more/)

## 概念

### 痛点:你的 Skill,换个客户端就废了

在 WorkBuddy 里写好的 Skill,换到 Codex 上:`SKILL.md` 能读,但**配它的那堆"环境"全乱套**——脚本路径不一样、有的在沙箱里有的不在、MCP 连接方式要重配。

> 官方点破:**"核心问题不是组件,是 manifest。"** 组件都是好的,装组件的"盒子"每个客户端自己发明一套。碎片化的根源从来不是内容不通用,是盒子不通用。

### Agent Plugins 是什么

- **定义**:跨客户端分发可复用 Agent 扩展(组件)的可移植插件格式规范;
- **发布**:2026-08-06,谷歌/微软/亚马逊/OpenAI/Cursor/Vercel——竞争对手愿意坐一张桌子定标准,说明碎片化已经痛到他们自己都受不了了;
- **类比**:Skill 是"充电线",Plugin 格式是"USB-C 接口";一次写好,到处用;
- **范围克制**:v1 只标准化 **Agent Skills + MCP**(两者已有成熟外部规范且有跨客户端采纳);commands / hooks / agents / rules / LSP 等仍太客户端特定,**不入 v1**。

## 原理(规范核心)

### 1. 插件 = 一个目录(而不是压缩包/registry)

为什么用目录而非 `.zip`/`.tar.gz`:可被标准工具检查(`ls`/`cat`/`git`)、开发期可原地编辑、兼容版本控制。固定顶层位置(`skills/`、`mcp.json`)消除了发现间接层。

**标准布局**:

```
reports-plugin/
├── plugin.json            # manifest:必填 $schema + name
├── skills/                # SKILL.md 放这,沿用 Agent Skills 标准
│   └── summarize/
│       ├── SKILL.md
│       ├── scripts/       # 脚本
│       └── references/    # 参考文档
├── mcp.json               # 每个 server 显式声明 type
├── com.example.client/    # 客户端扩展目录(reverse-domain)
│   └── hooks/
├── LICENSE
└── CHANGELOG.md
```

### 2. plugin.json:闭合的 manifest

- **必填**:`$schema`(必须是 `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`)+ `name`;
- **可选**:`version`(建议 SemVer)、`description`、`author`、`homepage`、`repository`、`license`、`keywords`、`extensions`;
- **schema 闭合**:顶层只允许上述字段。未知顶层字段 → 客户端**报告并忽略**(不致命,继续加载);非对象 `extensions` 不致命;**其它任何 schema 违规致命**(拒绝整个插件,不发现/不执行任何组件);
- 客户端-specific 数据放 `extensions` 的 reverse-domain key 下,不得占用顶层。

最小示例:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "reports-plugin"
}
```

### 3. 组件发现与路径包含(containment)

- 固定位置发现:`skills/`(每个子目录下 `SKILL.md`)、`mcp.json`;缺失的固定位置**不报错忽略**(§6.2);
- **路径包含**:plugin-relative 路径必须以 `./` 开头、解析后必须在 plugin root 内;`../bin/server` 这类越界路径**客户端必须拒绝**;`command` 裸名走平台可执行搜索,`./` 路径直接解析到 plugin root;
- 越界失败边界按最窄适用:manifest 越界拒插件 / 组件越界判该组件类型无效 / SKILL.md 越界跳过该 skill / MCP server 越界判该 entry 无效。

### 4. mcp.json:显式声明传输,不用"猜"

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "server": {
      "type": "stdio",              // 显式:stdio / streamable-http(区分 legacy HTTP+SSE)
      "command": "./bin/server",    // ./ 相对 plugin root
      "cwd": "./data"
    }
  }
}
```

- 每个 server **显式声明 type**,客户端永远不用从配置形状推断传输方式——"沙箱/非沙箱路径差异"的根源就是这种"猜";
- 客户端可只支持一种传输(stdio 或 Streamable HTTP),**跳过不支持的 entry 不影响其它 server/组件**。

### 5. 组件独立失败,互不拖累(§11.3)

某个 MCP server 挂了 → 客户端跳过它继续加载,Skill 照常干活。规范把"组件失败非致命"与"诊断要求"配对——失败可见而非静默。客户端还**必须忽略不支持的组件类型**(skills-only 客户端可以不支持 MCP,只要满足适用要求)。

### 6. 环境变量与占位符(§9)

- 客户端启动插件子进程(stdio MCP)时,提供 **`PLUGIN_ROOT`**(插件根)与 **`PLUGIN_DATA`**(客户端管理的可写状态目录,插件更新后仍保留);
- 在 `args` / `env` / `cwd` 中展开 **`${PLUGIN_ROOT}` / `${PLUGIN_DATA}`** 两个占位符;`command` 字段**不做插值**(`./` 直接解析、裸名走搜索,避免解析用户 shell 字符串)。

### 7. 客户端扩展:reverse-domain 命名空间(§8)

`com.example.client/` 专门放单客户端的环境配置(hooks/路径/配置),**不认识的客户端直接忽略**。可移植的保持纯净,不可移植的有处安放。同一 reverse-domain 标识可同时用于 manifest 的 `extensions` 数据和顶层扩展目录,两者可独立存在。

### 8. 一致性底线(§11)

- 每个合规模块客户端必须检查 root `plugin.json`(一致性地板);
- 支持至少一种组件类型(skills 或 MCP);
- 增量采纳:客户端不要求支持所有组件类型。

## 代码 / 实现

完整 manifest 示例(官方):

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "plugin-name",
  "version": "1.2.0",
  "description": "Brief plugin description",
  "author": { "name": "Author Name", "email": "author@example.com", "url": "https://example.com" },
  "homepage": "https://docs.example.com/plugin",
  "repository": "https://github.com/example/plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "extensions": { "com.example.client": { "setting": true } }
}
```

**按 Plugin 思维组织新 Skill**(迁移成本趋近于零):SKILL.md、scripts、references 按标准目录放好,未来想打包随时能打。

**打包适用场景**:多个组件需要"一起走、一起分发"——如"脚本 + 数据库连接 + 周报技能"打包成一套,换客户端不散架;单个 Skill 打包反而画蛇添足。

## 实践 / 应用

### 要不要迁移?(官方明确表态)

> "不是每个 Skill 都需要做成 Plugin。如果你只发布一个 Skill,或者只接一个 MCP server,单独用原来的方式更简单。"

三条建议:

1. **别急着迁移**——现有 Skill 不用动(包装可以换,内容不用动);
2. **盯两个信号**——Codex CLI 0.146 已支持识别 plugin.json、Chrome DevTools MCP 已支持插件安装;主流客户端跟进速度比想象中快;
3. **新写的 Skill 按 Plugin 思维组织**——标准目录布局,随时可打包。

### WorkBuddy 用户视角(腾讯)

| 维度 | WorkBuddy(现在) | Agent Plugins(标准) |
| --- | --- | --- |
| 插件格式 | `.codebuddy-plugin/`(腾讯自家) | `plugin.json`(开放标准) |
| Skills 支持 | ✅ | ✅ 标准内含 |
| MCP 支持 | ✅ | ✅ 标准内含 |
| 跨工具复用 | ❌ 只在腾讯生态 | ✅ 到处跑 |

判断:短期(现在)无影响;中期(半年到一年)腾讯大概率跟进(开放标准跟进成本低收益高,CodeBuddy 已是国内首个插件/IDE/CLI 三形态工具);迁移成本很低(`SKILL.md` 内容不用重写,Plugin 只是外层包装)。

### 三个连锁反应(微信解读的行业判断)

- **竞争焦点转移**:以前比"谁锁死更多开发者",以后比"谁内容生态更厚";
- **MCP 地位不降反升**:Plugin 只是"包装盒",里面执行层还是 MCP + Skills,地基没变;
- **封闭生态被边缘化**:不支持 Agent Plugins 的工具长期会被市场淘汰(像不支持 USB-C 的手机)。

### 安全边界(必须说清)

**标准解决"放哪",不解决"信不信"。** 插件能到处跑,但装谁的插件、它有没有权限碰你的数据,规范明确不负责——安全责任永远是使用者自己的。

## 总结

1. **碎片化的根源是 manifest,不是内容**:Agent Plugins 用"一个插件一个目录"的克制设计统一了装组件的"盒子"。
2. **核心机制**:闭合 `plugin.json`(必填 $schema+name)、固定位置组件发现、路径包含约束、`mcp.json` 显式声明传输、组件独立失败非致命、`PLUGIN_ROOT`/`PLUGIN_DATA` 环境变量、reverse-domain 客户端扩展。
3. **v1 只做 Skills + MCP**:两者已有成熟标准;commands/hooks/rules 等仍太客户端特定,不进 v1。
4. **迁移决策**:单 Skill/单 MCP 不用打包;多组件"一起走"才需要;现有 Skill 不用动,新 Skill 按标准目录组织。
5. **安全在用户**:标准只管可移植性,权限与信任责任在安装方。

**下一步学什么**:对比站内 [Skill 治理(Nacos AI Registry)](skill-governance-registry.md)(团队级 Skill 可信来源)、[Agent Skill 版本管理](skill-version-management.md)(SemVer/灰度)、[Skill 测评](skill-evaluation.md)(五维评测)——Agent Plugins 是"分发格式层",与治理/版本/评测互补。

## 延伸阅读

- 站内:[Skill 治理:用 Nacos AI Registry 给团队 Skill 一份可信来源](skill-governance-registry.md)、[Agent Skill 版本管理](skill-version-management.md)、[Skill 测评:五大维度与测试闭环](skill-evaluation.md)、[腾讯 SkillHub:10 万+ Skill 的质量评测与分发](skillhub-trace-evaluation.md)、[Skill 收藏首页](index.md)
- 外部:规范原文(https://agent-plugins.org/specification);发布公告(https://developers.googleblog.com/agent-plugins-package-your-skills-tools-and-more/);规范仓库(https://github.com/agentplugins/agent-plugins-spec);解读原文(https://mp.weixin.qq.com/s/7F7MVlCJzQjd2dVAMqxjBA)
