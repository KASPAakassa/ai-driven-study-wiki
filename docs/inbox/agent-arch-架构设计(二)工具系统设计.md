# 原始资料:万字长文拆解Agent架构设计(二):工具系统设计

> 来源:微信公众号(Agent 架构设计系列),原文链接:https://mp.weixin.qq.com/s/iD73TPYxZj6s-Jpmpt0ulw
> 抓取日期:2026-08-09;状态:已拆解入库(见归档记录)

---

本系列目标：拆解 Claude Code 源码，理解 Agent 底层架构的设计思路。核心方法：读源码 → 理解设计决策 → 用 TypeScript 手写核心逻辑。
每一篇聚焦一个子系统，讲清楚"为什么这么设计"比"代码怎么写"更重要。

引言
如果记忆系统是 Agent 的"认知基础设施"，那工具系统就是 Agent 的"手脚"。没有工具的 Agent 只能说话，有了工具的 Agent 才能做事——读文件、执行命令、调用 API、甚至派出子 Agent。
Claude Code 的工具系统设计得非常精巧。它不只是一个"函数注册表 + 调用分发器"，而是包含了权限分级、运行时风险评估、子 Agent 递归和两阶段安全分类器。这些机制组合在一起，让 Agent 能安全地操作真实世界。
这篇聚焦四个地方：工具的数据结构定义、权限分级逻辑、子 Agent 作为普通工具的实现方式、以及安全边界的结构性设计。

Part 1：拆解 Claude Code 源码
Claude Code 的工具系统有三个值得精读的地方：工具的数据结构定义、权限分级逻辑、以及子 Agent 作为普通工具的实现方式。
1.1 工具的数据结构：AgentTool 接口
从泄露源码里能看到每个工具的基础契约：

// Claude Code 工具系统的核心接口（简化自源码）type ToolPermission = 'auto' | 'confirm' | 'block'; interface AgentTool { // ── 身份 ──────────────────────────────────── name: string; // 工具名，对应模型输出的 tool_use.name description: string; // 注入系统提示，让模型知道何时调用  // ── Schema（告诉模型参数格式）─────────────── inputSchema: JSONSchema; // 模型必须按此格式输出参数  // ── 权限（工具自带，不在外部配置表里）───────── // 'auto' = 第一档，自动执行（只读/无副作用） // 'confirm' = 第二档，默认需要用户确认 // 'block' = 第三档，默认拦截，需明确授权 defaultPermission: ToolPermission;  // ── 执行 ──────────────────────────────────── execute(input: TInput, context: ToolContext): Promise;  // ── 可选：运行前的快速风险评估 ─────────────── // 返回 null 表示使用 defaultPermission // 返回具体值表示运行时覆盖默认权限 assessRisk?(input: TInput, context: ToolContext): Promise;} interface ToolContext { workingDir: string; // Agent 当前工作目录 sessionId: string; userAllowlist: Set; // 用户在本会话中选择”始终允许”的命令 tokenBudget: TokenBudget;}
关键设计：defaultPermission 是工具的属性，不是外部配置表里的一行。这意味着工具的风险画像和工具本身绑定在一起。文件读取工具永远是 auto，即使你把它放在任何配置组合里，它都不会突然变成需要确认的操作。
1.2 三档权限分级：ToolPermissionManager
这是整个工具系统最核心的逻辑：

// 用户在会话中可以调整权限，但只能比默认更宽松，不能更严格地绕过 'block'interface UserPermissionOverrides { alwaysAllow: Set; // 'bash:rm -rf /tmp/*' 这类用户批准过的具体命令 sessionAllow: Set; // 本会话临时允许} class ToolPermissionManager { constructor(private overrides: UserPermissionOverrides) {}  async decide( tool: AgentTool, input: unknown, context: ToolContext ): Promise<'execute' | 'confirm' | 'block'> {  // 1. 先跑工具自身的运行时风险评估（如果有） const runtimePermission = await tool.assessRisk?.(input, context) ?? null; const effectivePermission = runtimePermission ?? tool.defaultPermission;  // 2. 'block' 是硬限制，不受用户覆盖 if (effectivePermission === 'block') { return 'block'; }  // 3. 检查用户是否已经批准过这个具体调用 const callSignature = this.buildSignature(tool.name, input); if ( this.overrides.alwaysAllow.has(callSignature) || this.overrides.sessionAllow.has(callSignature) ) { return 'execute'; }  // 4. 按默认权限决定 if (effectivePermission === 'auto') return 'execute'; return 'confirm'; // 'confirm' → 等用户响应 }  private buildSignature(toolName: string, input: unknown): string { // 对于 bash 工具，签名包含具体命令（不只是工具名） // 这样”始终允许 git status”不会变成”始终允许所有 bash 命令” if (toolName === 'bash' && typeof input === 'object' && input !== null) { const cmd = (input as { command?: string }).command ?? ''; return `bash:${cmd}`; } return toolName; }}
buildSignature 这个细节很重要。用户选择"始终允许"时，Claude Code 记录的是 bash:git status，而不是 bash。下次调用 rm -rf 时，签名不匹配，依然会触发确认。粒度是命令级别，不是工具级别。
1.3 子 Agent 即工具：AgentTool 的递归性
这是 Claude Code 架构里最优雅的设计之一：

// 子 Agent 是一个普通的 AgentTool，走同样的权限管道const agentTool: AgentTool = { name: 'agent', description: 'Spawn a sub-agent to handle a delegated task in parallel.',  inputSchema: { type: 'object', properties: { prompt: { type: 'string', description: 'Task description for the sub-agent' }, tools: { type: 'array', description: 'Tool names the sub-agent is allowed to use' }, }, required: ['prompt'], },  // 生成子 Agent 是”确认”级别，不是自动执行 // 因为子 Agent 可能触发一连串后续操作 defaultPermission: 'confirm',  async execute(input: AgentInput, context: ToolContext): Promise { // 子 Agent 继承父 Agent 的工作目录和会话上下文 // 但工具集是受限的子集（input.tools 指定） const subAgent = new AgentRunner({ prompt: input.prompt, allowedTools: input.tools ?? [], workingDir: context.workingDir, // 关键：子 Agent 共享父 Agent 的 token 预算 // 子 Agent 消耗的 token 从同一个预算里扣 tokenBudget: context.tokenBudget, });  return subAgent.run(); },};
AgentTool 可以实例化另一个 AgentRunner，而 AgentRunner 内部又有一个 ToolPermissionManager——整个系统是递归的，但权限不会递归放大。子 Agent 只能拿到父 Agent 显式授权的工具子集。
1.4 安全边界的结构性设计：分类器只看输入
Auto Mode 的两阶段分类器有一个刻意的输入限制，值得单独理解：

// 分类器的输入结构（Auto Mode）interface ClassifierInput { userRequest: string; // ✅ 用户的原始请求 toolName: string; // ✅ 要调用的工具名 toolInput: unknown; // ✅ 工具的参数  // 以下字段刻意不传入分类器： // modelReasoning: string ← ❌ 模型的推理文字（防止模型”解释说服”分类器） // toolOutput: unknown ← ❌ 工具执行结果（防止恶意输出影响判断） // conversationHistory ← ❌ 历史对话（减少 Prompt Injection 攻击面）}
两阶段分类器的执行流程：

class TwoStageClassifier { async classify(input: ClassifierInput): Promise<'safe' | 'suspicious' | 'dangerous'> { // 第一阶段：单 token 快速过滤（低延迟，大部分请求在这里通过） const quickResult = await this.quickFilter(input); if (quickResult === 'safe') return 'safe';  // 第二阶段：CoT 推理（只有被标记为可疑的才进这里） return this.deepAnalysis(input); }  private async quickFilter(input: ClassifierInput): Promise<'safe' | 'suspicious'> { // 用一个小模型，输出单 token: Y（安全）或 N（可疑） // 延迟 < 100ms const response = await callModel({ model: 'claude-haiku-4-5', prompt: `Is this tool call safe? Respond Y or N only.\n${JSON.stringify(input)}`, maxTokens: 1, }); return response === 'Y' ? 'safe' : 'suspicious'; }  private async deepAnalysis(input: ClassifierInput): Promise<'suspicious' | 'dangerous'> { // 用 Sonnet，带 CoT，分析可疑调用 // 延迟 500-2000ms，但只对少数可疑调用触发 const response = await callModel({ model: 'claude-sonnet-4-6', prompt: buildCoTPrompt(input), maxTokens: 500, }); return parseDecision(response); }}
两阶段设计的本质是把计算资源集中在真正需要的地方。99% 的正常操作走快速过滤，毫秒级决策；只有可疑的 1% 才进入昂贵的 CoT 推理。
Part 2：为什么这样设计——从代码看决策
看完代码，三个设计决策值得提炼。
决策一：defaultPermission 住在工具里，不在配置表里
传统做法是维护一张 {toolName: permission} 的配置表。Claude Code 把权限内聚进工具本身。
好处是工具是自描述的——你看一个工具的代码，立刻知道它的风险画像，不需要去查另一个文件。代价是权限调整需要修改工具代码，不够灵活。
但对于 Agent 工具这种高安全风险的场景，内聚比灵活更重要。你不想看到一个"文件删除"工具因为配置错误变成了 auto 执行。
决策二：签名粒度是命令，不是工具名
buildSignature 返回 bash:git status 而不是 bash。
这个细节防止了**"始终允许 bash"变成一个全量授权漏洞**。每次用户批准的是一个具体操作的指纹，而不是一整类工具。

用户批准 git status → 签名: ”bash:git status” → 只允许这一条命令 而不是 ”bash” → 允许所有命令
决策三：分类器的信息边界是结构性的，不是提示词约束
不传入 modelReasoning 不是靠一句"你不能看推理文字"的提示来限制的，而是在调用分类器时根本就不构造这个字段。
这是程序级别的约束，不会被 Prompt Injection 绕过。

❌ 提示词约束: ”请不要看 modelReasoning” → 模型可能被说服忽略这个指令✅ 结构性约束: 调用时就不传 modelReasoning → 分类器物理上看不到这个字段
Part 3：手写核心逻辑（TypeScript）
把上面的理解写成代码。覆盖工具注册、权限分级、拦截执行，以及一个简单的 Agent Loop 把一切串起来。
3.0 项目结构

tool-system/├── src/│ ├── types.ts # 工具的数据结构契约│ ├── permission.ts # 权限决策（三档 + 用户覆盖 + 命令级签名）│ ├── tools.ts # 具体工具实现（含运行时风险评估）│ └── agent.ts # Agent Loop，把一切串联起来├── package.json└── tsconfig.json
四个文件，职责清晰：契约 → 决策 → 实现 → 编排。
3.1 数据结构契约：types.ts
不需要太多代码，关键是定义清楚三个角色之间的关系：

// 三档权限：auto / confirm / blocktype ToolPermission = 'auto' | 'confirm' | 'block'; // 权限决策结果type Decision = 'execute' | 'confirm' | 'block'; // 工具上下文——工具执行时能拿到什么interface ToolContext { workingDir: string; sessionId: string; userAllowlist: Set;} // 工具接口——每个工具必须实现这些interface AgentTool { name: string; description: string; inputSchema: object; defaultPermission: ToolPermission; execute(input: unknown, context: ToolContext): Promise; // 可选：运行时覆盖默认权限 assessRisk?(input: unknown, context: ToolContext): Promise;}
核心洞察：defaultPermission 和 assessRisk 都在工具接口里。权限是工具的属性，不是外部配置。
3.2 权限决策：permission.ts
这是最关键的模块。核心逻辑就一个 decide() 方法，决策链是：

工具运行时风险评估 → 硬限制检查 → 用户白名单检查 → 默认权限

class PermissionManager { private alwaysAllow = new Set(); // 永久允许的命令签名 private sessionAllow = new Set(); // 本会话临时允许  async decide( tool: AgentTool, input: unknown, context: ToolContext, ): Promise { // 第一步：运行时风险评估（工具自己最了解自己） const runtime = await tool.assessRisk?.(input, context) ?? null; const effective = runtime ?? tool.defaultPermission;  // 第二步：block 是硬限制，不可覆盖 if (effective === 'block') return 'block';  // 第三步：检查用户白名单 const signature = this.buildSignature(tool.name, input); if (this.alwaysAllow.has(signature) || this.sessionAllow.has(signature)) { return 'execute'; }  // 第四步：按默认权限决定 return effective === 'auto' ? 'execute' : 'confirm'; }  // 关键：签名粒度是命令，不是工具名 private buildSignature(toolName: string, input: unknown): string { if (toolName === 'bash' && typeof input === 'object' && input !== null) { const cmd = (input as { command?: string }).command ?? ''; return `bash:${cmd}`; } return toolName; }  // 用户选择”始终允许”时调用 grantAlwaysAllow(signature: string): void { this.alwaysAllow.add(signature); }}
buildSignature是整个权限系统的安全基石。它决定了"始终允许"的粒度。现在是命令级别（bash:git status），如果要改成更粗（工具级 bash）或更细（参数哈希 bash:sha256(abc)），只需要改这一个函数。
3.3 工具实现：tools.ts
每个工具是一个独立对象。这里展示两个典型工具：一个只读的（auto），一个有副作用的（confirm），以及 bash 工具的运行时风险评估。

// === 只读工具：自动执行 ===const readFileTool: AgentTool = { name: 'read_file', description: 'Read a file from disk.', inputSchema: { type: 'object', properties: { path: { type: 'string' } } }, defaultPermission: 'auto', // 只读操作，无风险  async execute(input: unknown, context: ToolContext) { const { path } = input as { path: string }; return await fs.readFile(join(context.workingDir, path), 'utf-8'); },}; // === 有副作用的工具：需要确认 ===const writeFileTool: AgentTool = { name: 'write_file', description: 'Write content to a file.', inputSchema: { type: 'object', properties: { path: { type: 'string' }, content: { type: 'string' } } }, defaultPermission: 'confirm', // 写操作，默认需确认  async execute(input: unknown, context: ToolContext) { const { path, content } = input as { path: string; content: string }; await fs.writeFile(join(context.workingDir, path), content); return `Written to ${path}`; },}; // === bash 工具：运行时风险评估 ===const bashTool: AgentTool = { name: 'bash', description: 'Execute a shell command.', inputSchema: { type: 'object', properties: { command: { type: 'string' } } }, defaultPermission: 'confirm', // 默认需确认  // 关键：运行时根据具体命令调整权限 async assessRisk(input: unknown): Promise { const cmd = (input as { command: string }).command;  // 只读命令 → 降级为 auto const SAFE_PREFIXES = ['ls', 'cat', 'head', 'tail', 'grep', 'git status', 'git log', 'pwd', 'echo']; if (SAFE_PREFIXES.some(p => cmd.startsWith(p))) return 'auto';  // 危险命令 → 升级为 block const DANGEROUS = ['rm -rf /', 'mkfs', 'dd if=', ':(){ :|:& };:']; if (DANGEROUS.some(p => cmd.includes(p))) return 'block';  // 其他 → 使用默认权限（confirm） return null; },  async execute(input: unknown, context: ToolContext) { const { command } = input as { command: string }; return execSync(command, { cwd: context.workingDir }).toString(); },};
assessRisk 的设计思路：工具自己最了解自己的风险。bash 工具能根据具体命令判断风险级别，权限管理器不需要知道 bash 命令的细节——它只需要信任工具的评估结果。
SAFE_COMMAND_PREFIXES 和 DANGEROUS_PATTERNS 这两个列表是你最容易调整的地方。改这两个列表就能改变 bash 的默认行为，不需要动权限系统的核心逻辑。
3.4 Agent Loop：agent.ts
把所有组件串起来。Agent Loop 的核心循环是：构建上下文 → 调用模型 → 解析工具调用 → 权限检查 → 执行或确认 → 记录结果 → 重复。

class AgentRunner { private tools: Map = new Map(); private permissions: PermissionManager;  constructor( private llm: LLMClient, private onConfirm: (tool: string, input: unknown) => Promise, ) { this.permissions = new PermissionManager(); }  registerTool(tool: AgentTool): void { this.tools.set(tool.name, tool); }  async run(userMessage: string): Promise { const messages: Message[] = [{ role: 'user', content: userMessage }];  // Agent Loop：持续执行直到模型不再调用工具 while (true) { const response = await this.llm.chat({ system: this.buildSystemPrompt(), messages, });  // 如果模型没有调用工具，直接返回文本 if (!response.toolCalls?.length) return response.content;  // 处理每个工具调用 for (const call of response.toolCalls) { const tool = this.tools.get(call.name); if (!tool) continue;  // 权限决策 const decision = await this.permissions.decide( tool, call.input, this.getContext(), );  let result: string; switch (decision) { case 'execute': result = await tool.execute(call.input, this.getContext()) as string; break; case 'confirm': // 调用外部确认回调（CLI 用 readline，Web 用 WebSocket） const approved = await this.onConfirm(call.name, call.input); if (!approved) { result = 'Tool call rejected by user.'; break; } // 用户批准后，记录签名以供后续自动放行 this.permissions.grantAlwaysAllow( this.buildSignature(call.name, call.input) ); result = await tool.execute(call.input, this.getContext()) as string; break; case 'block': result = 'Tool call blocked by security policy.'; break; }  // 工具结果追加到消息历史 messages.push({ role: 'assistant', content: response.content, toolCalls: [call] }); messages.push({ role: 'tool', content: result, toolCallId: call.id }); } } }  private buildSystemPrompt(): string { const toolDefs = Array.from(this.tools.values()).map(t => ({ name: t.name, description: t.description, input_schema: t.inputSchema, })); return `You are a helpful assistant with access to tools:\n${JSON.stringify(toolDefs)}`; }  private getContext(): ToolContext { return { workingDir: process.cwd(), sessionId: 'default', userAllowlist: new Set() }; }  private buildSignature(name: string, input: unknown): string { if (name === 'bash') return `bash:${(input as any).command}`; return name; }}
onConfirm 回调是你的 UI 插入点。CLI 模式用 readline，Web 模式用 WebSocket 推到前端，CI 模式直接返回 true。所有差异都在这个回调里，不影响其他逻辑。
3.5 使用示例

const agent = new AgentRunner( new AnthropicClient(), // CLI 确认回调 async (tool, input) => { console.log(`\n[Confirm] Call ${tool} with:`, JSON.stringify(input)); const answer = await ask('Allow? (y/n) '); return answer === 'y'; },); // 注册工具agent.registerTool(readFileTool);agent.registerTool(writeFileTool);agent.registerTool(bashTool); // 运行await agent.run('Read package.json and show me the dependencies');// readFileTool → auto → 直接执行 await agent.run('Create a new file called hello.txt with ”Hello World”');// writeFileTool → confirm → 等待用户批准 → 执行// 下次再写 hello.txt → 签名匹配 → 自动放行
Part 4：扩展方向
扩展一：子 Agent 即工具
把子 Agent 注册为一个普通工具，走同样的权限管道：

const agentTool: AgentTool = { name: 'agent', description: 'Spawn a sub-agent for a delegated task.', inputSchema: { type: 'object', properties: { prompt: { type: 'string' }, tools: { type: 'array', items: { type: 'string' } }, // 子 Agent 可用工具 }, }, defaultPermission: 'confirm', // 生成子 Agent 需要确认  async execute(input: unknown, context: ToolContext) { const { prompt, tools } = input as { prompt: string; tools?: string[] }; const subAgent = new AgentRunner(this.llm, this.onConfirm); // 子 Agent 只能拿到父 Agent 授权的工具子集 for (const name of tools ?? []) { const tool = this.tools.get(name); if (tool) subAgent.registerTool(tool); } return subAgent.run(prompt); },};
权限不会递归放大——子 Agent 的工具集是父 Agent 的子集，不是超集。
扩展二：两阶段安全分类器
在权限决策前加一个分类器，快速过滤明显安全的调用：

class SafetyClassifier { async classify(toolName: string, input: unknown): Promise<'safe' | 'suspicious'> { // 第一阶段：Haiku 单 token 判断（< 100ms） const quick = await callModel({ model: 'claude-haiku-4-5', maxTokens: 1, prompt: `Is calling ${toolName} with ${JSON.stringify(input)} safe? Y or N`, }); return quick === 'Y' ? 'safe' : 'suspicious'; }}
99% 的正常调用走快速过滤，只有可疑的 1% 才需要人工确认。
扩展三：工具插件化
把工具注册从硬编码改为文件系统发现：

// 从 plugins/ 目录自动加载工具async function discoverTools(pluginsDir: string): Promise { const files = await fs.readdir(pluginsDir); const tools: AgentTool[] = []; for (const file of files.filter(f => f.endsWith('.ts'))) { const mod = await import(join(pluginsDir, file)); if (mod.default && mod.default.name) tools.push(mod.default); } return tools;}
总结
这篇拆解了 Claude Code 工具系统的四个核心设计核心设计：
原则
实现
为什么
权限内聚
defaultPermission 在工具接口里
工具自描述，不依赖外部配置
命令级签名
buildSignature() 返回 bash:cmd
防止"始终允许"变成全量授权
运行时评估
assessRisk() 按具体输入调权限
同工具不同调用有不同风险
结构性约束
分类器输入字段在程序级控制
不受 Prompt Injection 影响
和 Claude Code 的区别：我们的实现去掉了两阶段分类器（需要 API 调用），简化了子 Agent 的 token 预算共享。但核心的三档权限 + 命令级签名 + 运行时评估都保留了——这是工具系统的安全骨架。