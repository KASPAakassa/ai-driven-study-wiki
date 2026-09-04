# 原始资料:生产级 Agent 应用架构(Claude Agent SDK 系列第六篇·终篇)

> 来源:微信公众号「数字拾荒」;参考:Claude Agent SDK 官方文档(Permissions/Multi-Agent/Hosting/Secure Deployment/Cost Tracking)
> 原文链接:https://mp.weixin.qq.com/s/Iq5qXb0NZhZLbCThIvhIlQ
> 抓取日期:2026-08-09;状态:双章节沉淀——生产架构角度进 docs/03-agents/agent-production-architecture.md,企业落地角度进 docs/06-enterprise/ontology-agent-adoption/enterprise-agent-production-deployment.md

---

权限不是"全开或全关"的二选一——SDK 提供了一个六层洋葱模型，从 Hooks 到 Deny 规则到 Permission Mode 到 Allow 规则再到 canUseTool 回调，每一层都可以拦截、放行或改写工具调用。理解这个评估顺序，是构建安全 Agent 的前提。

前情概要：前五篇我们从零构建了一个完整的 Agent 系统——Agent Loop 让它自动循环执行任务，自定义工具让它调用外部能力，Hooks 编排让它自我审查和多专家协作，Session 管理让它拥有对话记忆和文件回滚能力，流式输出让用户实时看到思考过程。至此，Agent 在功能层面已经齐活了。但要上生产环境，还差最关键的一环：安全、权限和容错。

本篇定位：系列终篇，解决生产级部署的四大核心问题——谁能做什么（权限）、多个 Agent 怎么协作（架构）、出错了怎么恢复（容错）、上线后怎么控成本保安全（运维）。

核心看点：

• 权限模型的六层洋葱：Hooks → Deny → Permission Mode → Allow → canUseTool → 最终裁决——每一层的职责和评估顺序
• 多 Agent 协作架构：三种创建方式、四个核心优势、混合模型策略（用便宜模型跑子任务，贵模型只做决策）
• 错误处理与恢复：SDK 异常层级、分层 try-catch、文件检查点回滚、Session 崩溃恢复——让 Agent 从容应对网络超时和 API 错误
• 生产部署四道防线：部署模式选择、纵深安全策略、成本控制（maxTurns / token 预算 / 实时监控）、可观测性接入

权限模型：六层洋葱

当 Claude 请求使用一个工具时，SDK 按严格的六步顺序评估权限。理解这个顺序是安全设计的基础——任何一层都可以终止评估链。

评估顺序

第一层是 Hooks。PreToolUse 钩子最先执行，可以直接拒绝（返回 deny）或放行（返回 allow）。但注意：Hook 返回 allow 不会跳过后续的 deny/ask 规则，它只是表示"我这一层没意见"。

第二层是 Deny 规则。来自 disallowedTools 配置。裸名规则（如 Bash）直接从 Claude 的工具列表中移除——Claude 根本看不到这个工具。作用域规则（如 Bash(rm *)）保留工具但拦截特定调用。Deny 规则在所有模式下生效，包括 bypassPermissions。

第三层是 Ask 规则。来自 settings.json。匹配时路由到 canUseTool 回调等待人工确认。在 dontAsk 模式下，匹配 ask 规则的调用直接被拒绝（永远不弹确认）。

第四层是 Permission Mode。SDK 提供六种模式：

type PermissionMode =
  | "default"       // 未匹配的工具触发 canUseTool
  | "dontAsk"       // 未预批准的一律拒绝，永不弹确认
  | "acceptEdits"   // 自动批准文件编辑和文件系统操作
  | "bypassPermissions"  // 全部放行（除非有显式 ask 规则）
  | "plan"          // 只读模式，编辑类工具强制走确认
  | "auto";         // 模型分类器自动判断（仅 TS）

第五层是 Allow 规则。来自 allowedTools 配置。匹配的工具自动批准。

第六层是 canUseTool 回调。如果前五层都没有给出明确结论，最终由这个回调决定。在 dontAsk 模式下，这一层永远不会被触发（未批准的直接拒绝）。

锁定模式：最小权限原则

生产环境最推荐的组合是 allowedTools + dontAsk——白名单之外的一切都被拒绝，不需要人工介入：

import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "分析项目代码质量",
  options: {
    allowedTools: ["Read", "Glob", "Grep"],  // 只允许只读工具
    permissionMode: "dontAsk",               // 白名单外一律拒绝
    maxTurns: 15,
  },
})) {
  // Agent 只能读取文件，不能编辑、不能执行命令
}

动态审批：canUseTool 回调

对于需要人工审批的场景（比如 Agent 要执行危险命令），canUseTool 提供了运行时拦截能力：

import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "修复项目中的安全漏洞",
  options: {
    allowedTools: ["Read", "Glob", "Grep", "Edit", "Bash"],
    canUseTool: async (toolName, input) => {
      // 读取类工具自动放行
      if (["Read", "Glob", "Grep"].includes(toolName)) {
        return { behavior: "allow" };
      }

      // Bash 命令需要审批
      if (toolName === "Bash") {
        console.log(`⚠️ Agent 想执行: ${input.command}`);
        const approved = await askUserForApproval(input.command);
        if (approved) {
          return { behavior: "allow" };
        }
        return { behavior: "deny", message: "用户拒绝了此命令" };
      }

      // 文件编辑：展示 diff 后审批
      if (toolName === "Edit") {
        console.log(`📝 修改 ${input.file_path}`);
        console.log(`  - ${input.old_string}`);
        console.log(`  + ${input.new_string}`);
        return { behavior: "allow" };  // 自动批准编辑
      }

      return { behavior: "allow" };
    },
  },
})) {
  // 处理消息...
}

canUseTool 的返回值支持三种行为：allow（批准，可选 updatedInput 改写参数）、deny（拒绝，Claude 会看到拒绝原因并调整策略）。

子 Agent 权限继承

一个关键的安全约束：当父 Agent 使用 bypassPermissions、acceptEdits 或 auto 模式时，所有子 Agent 自动继承该模式且不可覆盖。这意味着你不能在一个宽松的父 Agent 下创建一个严格的子 Agent——权限只能收紧，不能放松。

多 Agent 协作架构

单个 Agent 处理所有任务会导致上下文膨胀、工具集过大、指令冲突。SDK 的子 Agent 机制解决这个问题——把复杂任务分解给专门的 Agent，每个 Agent 有独立的上下文、工具集和系统提示。

三种创建方式

SDK 支持三种定义子 Agent 的方式：

编程式定义（推荐）——通过 agents 参数在 query() 调用时传入：

import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "审查这个 PR 的代码质量和安全性",
  options: {
    allowedTools: ["Read", "Grep", "Glob", "Agent"],  // Agent 工具必须显式允许
    agents: {
      "code-reviewer": {
        description: "代码质量审查专家。检查可维护性、设计模式、性能问题。",
        prompt: "你是一个资深代码审查专家。关注代码质量、设计模式使用、性能瓶颈和可维护性。输出结构化的审查报告。",
        tools: ["Read", "Grep", "Glob"],  // 只读工具
        model: "sonnet",
      },
      "security-scanner": {
        description: "安全漏洞扫描专家。检查注入、认证、数据泄露等安全问题。",
        prompt: "你是一个安全审计专家。检查 SQL 注入、XSS、认证绕过、敏感数据泄露、依赖漏洞等安全问题。",
        tools: ["Read", "Grep", "Glob"],
        model: "sonnet",
      },
      "test-runner": {
        description: "测试执行专家。运行测试套件并分析覆盖率。",
        prompt: "你是一个测试工程师。运行测试、分析失败原因、报告覆盖率。",
        tools: ["Bash", "Read", "Grep"],  // 需要 Bash 来跑测试
        model: "haiku",  // 用更便宜的模型跑测试
      },
    },
  },
})) {
  // 父 Agent 会自动决定何时委派给哪个子 Agent
  // 子 Agent 的中间过程不会污染父 Agent 的上下文
}

文件系统定义——在 .claude/agents/ 目录下放置 Markdown 文件，适合团队共享的固定 Agent 配置。

内置通用 Agent——不需要任何定义，Claude 可以随时通过 Agent 工具调用一个通用子 Agent 来处理子任务。

四个核心优势

上下文隔离：每个子 Agent 运行独立的对话。中间的工具调用和结果留在子 Agent 内部，只有最终结论返回给父 Agent。这让主上下文保持精简。

并行执行：多个子 Agent 可以并发运行。三个独立的审查任务（代码质量 + 安全扫描 + 测试覆盖）的总耗时等于最慢的那个，而不是三者之和。

专业化指令：每个子 Agent 有独立的系统提示，可以针对特定任务深度优化，不会和其他任务的指令冲突。

工具限制：子 Agent 只能使用你显式授予的工具。一个只做代码审查的 Agent 不需要也不应该有文件编辑权限。

AgentDefinition 完整配置

interface AgentDefinition {
  description: string;      // 必填：何时使用这个 Agent（驱动自动委派）
  prompt: string;           // 必填：Agent 的系统提示
  tools?: string[];         // 允许的工具列表（省略则继承全部）
  disallowedTools?: string[];  // 禁止的工具
  model?: string;           // 'haiku' | 'sonnet' | 'opus' | 'inherit' | 完整模型 ID
  maxTurns?: number;        // 最大轮次
  mcpServers?: (string | object)[];  // MCP 服务器
}

成本优化：混合模型策略

多 Agent 架构的一个隐藏优势是可以按任务复杂度分配模型。主 Agent 用 Opus 做决策和协调，子 Agent 用 Sonnet 或 Haiku 做执行：

// 主 Agent: Opus（默认）负责理解需求、拆分任务、综合结论
// code-reviewer: Sonnet 做深度代码分析
// test-runner: Haiku 跑测试（不需要深度推理）
// doc-generator: Haiku 生成文档（模板化工作）

ResultMessage 的 modelUsage 字段会按模型分别统计 token 用量和成本，方便你追踪混合模型策略的实际效果。

错误处理与恢复策略

生产环境的 Agent 必须优雅地处理各种失败场景。SDK 的错误体系分为两个层面：进程级错误（SDK 本身的异常）和任务级错误（Agent 执行过程中的问题）。

SDK 异常层级

ClaudeSDKError                    # 所有 SDK 错误的基类
├── CLINotFoundError              # Claude Code 二进制文件未找到
├── CLIConnectionError            # 无法连接到 CLI 进程
├── ProcessError                  # CLI 进程异常退出
│   └── exit_code, stderr        # 退出码和错误输出
├── CLIJSONDecodeError            # 无法解析 CLI 输出的 JSON
│   └── line, original_error     # 原始行和解析错误
└── MessageParseError             # JSON 有效但不符合消息 schema
    └── data                     # 原始数据

分层错误处理

import { query } from "@anthropic-ai/claude-agent-sdk";

async function runAgentWithRecovery(prompt: string, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const results = [];

      for await (const message of query({
        prompt,
        options: {
          allowedTools: ["Read", "Edit", "Bash"],
          maxTurns: 20,
          abortController: createTimeoutController(60_000),  // 60 秒超时
        },
      })) {
        if (message.type === "result") {
          switch (message.subtype) {
            case "success":
              return { success: true, cost: message.total_cost_usd, turns: message.num_turns };

            case "error_max_turns":
              // Agent 陷入循环，缩小任务范围重试
              console.warn(`⚠️ 达到最大轮次 (${message.num_turns})，尝试缩小范围`);
              prompt = `${prompt}\n\n注意：上次尝试超时了。请只处理最关键的部分，不要试图一次解决所有问题。`;
              break;

            case "error_during_execution":
              // 执行错误，记录后重试
              console.error(`❌ 执行错误 (尝试 ${attempt}/${maxRetries})`);
              break;
          }
        }
      }
    } catch (err) {
      if (err.name === "AbortError") {
        console.error(`⏱️ 超时 (尝试 ${attempt}/${maxRetries})`);
        continue;
      }

      // SDK 级别错误
      if (err.constructor.name === "CLINotFoundError") {
        throw new Error("Claude Code 未安装，无法恢复");
      }
      if (err.constructor.name === "ProcessError") {
        console.error(`进程错误: exit=${err.exit_code}, stderr=${err.stderr}`);
        if (attempt < maxRetries) {
          await sleep(1000 * attempt);  // 指数退避
          continue;
        }
      }

      throw err;  // 未知错误，向上抛出
    }
  }

  return { success: false, error: "达到最大重试次数" };
}

function createTimeoutController(ms: number): AbortController {
  const controller = new AbortController();
  setTimeout(() => controller.abort(), ms);
  return controller;
}

文件检查点：可回滚的修改

当 Agent 修改文件出错时，File Checkpointing 提供了"后悔药"。结合错误检测，可以实现自动回滚：

import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "重构认证模块",
  options: {
    allowedTools: ["Read", "Edit", "Write", "Bash"],
    rewindFiles: true,  // 开启文件检查点
  },
})) {
  if (message.type === "result") {
    if (message.subtype !== "success") {
      // 任务失败，回滚所有文件修改
      console.log("任务失败，正在回滚文件修改...");
      // rewindFiles 会自动恢复到任务开始前的状态
    }
  }
}

Session 恢复：崩溃后继续

结合第四篇的 Session 机制，可以实现崩溃恢复：

import { query } from "@anthropic-ai/claude-agent-sdk";

const SESSION_ID = "migration-task-001";
const sessionStore = new RedisSessionStore(redisClient);

// 尝试恢复之前的会话
async function runOrResume(prompt: string) {
  const existingSession = await sessionStore.load(SESSION_ID);

  for await (const message of query({
    prompt: existingSession ? undefined : prompt,  // 恢复时不需要新 prompt
    options: {
      resume: existingSession ? SESSION_ID : undefined,
      sessionStore,
      allowedTools: ["Read", "Edit", "Write", "Bash"],
    },
  })) {
    if (message.type === "result") {
      if (message.subtype === "success") {
        console.log("✅ 任务完成");
        await sessionStore.delete(SESSION_ID);
      }
      // 失败时 session 自动保存，下次启动可恢复
    }
  }
}

生产部署：安全与成本

部署模式选择

SDK 的子进程模型决定了部署架构。query() 每次调用都会启动一个 claude CLI 子进程，通过 stdio 通信。选择部署模式时需要考虑会话生命周期：

短任务（Ephemeral）模式：一个容器处理一个任务，完成后销毁。适合一次性任务（bug 修复、文档翻译、数据提取）。冷启动要快。

长驻（Long-running）模式：持久容器，内部运行多个 SDK 进程。适合持续服务（邮件分类、Slack 机器人、实时监控）。用 startup() 预热，按最大并发会话数规划内存。

混合（Hybrid）模式：容器按需启动，通过 SessionStore 恢复状态。适合交互间隔长的场景（跨天的代码审查、多轮文档协作）。SessionStore 是必需的——没有它，容器销毁时会话就丢了。

安全：纵深防御

Agent 的核心安全风险是提示注入——恶意指令可能嵌入在 README、网页、用户输入中。SDK 内置了多层防护，但生产环境需要额外加固：

容器隔离：

docker run \
  --cap-drop ALL \                          # 移除所有 Linux capabilities
  --security-opt no-new-privileges \        # 禁止提权
  --security-opt seccomp=/path/to/profile.json \  # seccomp 限制系统调用
  --read-only \                             # 只读文件系统
  --tmpfs /tmp:rw,noexec,nosuid \           # 临时目录禁止执行
  --network=none \                          # 无网络（或用代理限制）
  my-agent-image

代理模式（Proxy Pattern）：敏感凭证不进入 Agent 的边界。在 Agent 外部放一个代理，Agent 发出的 API 请求经过代理时自动注入认证信息：

Agent → HTTP Request (无凭证) → Proxy (注入 API Key) → 外部服务

这样即使 Agent 被提示注入攻击，攻击者也拿不到凭证。

最小权限清单：

资源
限制方式

文件系统
只挂载必要目录，优先只读

网络
通过代理限制可访问的域名

凭证
代理注入，Agent 永远看不到

系统能力
容器内 drop 所有 capabilities

工具
allowedTools + dontAsk 白名单

成本控制：四道防线

第一道：maxTurns 限制。防止 Agent 陷入无限循环。根据任务复杂度设置合理上限。

第二道：AbortController 超时。防止单次任务耗时过长。

第三道：实时成本监控。通过 ResultMessage.total_cost_usd 追踪每次调用的成本：

import { query } from "@anthropic-ai/claude-agent-sdk";

const COST_LIMIT_PER_TASK = 1.00;  // 单任务上限 $1
const COST_LIMIT_DAILY = 50.00;    // 日上限 $50
let dailyCost = 0;

async function runWithCostGuard(prompt: string) {
  const controller = new AbortController();

  for await (const message of query({
    prompt,
    options: {
      abortController: controller,
      maxTurns: 30,
      allowedTools: ["Read", "Edit", "Write", "Bash"],
    },
  })) {
    if (message.type === "result") {
      const cost = message.total_cost_usd;
      dailyCost += cost;

      if (cost > COST_LIMIT_PER_TASK) {
        console.warn(`⚠️ 单任务成本超限: $${cost.toFixed(4)}`);
      }
      if (dailyCost > COST_LIMIT_DAILY) {
        console.error(`🚨 日成本超限: $${dailyCost.toFixed(2)}，暂停所有任务`);
        controller.abort();
      }

      // 按模型分别统计
      if (message.modelUsage) {
        for (const [model, usage] of Object.entries(message.modelUsage)) {
          console.log(`  ${model}: $${usage.costUSD.toFixed(4)} (${usage.inputTokens}+${usage.outputTokens} tokens)`);
        }
      }
    }
  }
}

第四道：混合模型策略。主 Agent 用高能力模型，子 Agent 按需降级：

agents: {
  "complex-analysis": { model: "opus", ... },    // 复杂推理用 Opus
  "code-generation": { model: "sonnet", ... },   // 代码生成用 Sonnet
  "simple-tasks": { model: "haiku", ... },       // 简单任务用 Haiku
}

可观测性

生产环境需要追踪 Agent 的行为。关键指标：

// 每次 query 结束时记录
if (message.type === "result") {
  metrics.record({
    task_id: taskId,
    status: message.subtype,
    duration_ms: message.duration_ms,
    api_duration_ms: message.duration_api_ms,
    turns: message.num_turns,
    cost_usd: message.total_cost_usd,
    input_tokens: message.usage.input_tokens,
    output_tokens: message.usage.output_tokens,
    cache_hit_tokens: message.usage.cache_read_input_tokens,
    model_breakdown: message.modelUsage,
  });
}

建议接入 OpenTelemetry 分布式追踪，每个 query() 调用作为一个 span，子 Agent 调用作为子 span。

完整示例：生产级代码审查 Agent

把前面所有知识组合起来，这是一个可以部署到生产环境的代码审查 Agent：

import { query } from "@anthropic-ai/claude-agent-sdk";

interface ReviewResult {
  success: boolean;
  findings: string;
  cost: number;
  duration: number;
}

async function reviewCode(diff: string, sessionStore: SessionStore): Promise<ReviewResult> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 120_000);  // 2 分钟超时

  try {
    let findings = "";
    let result: ReviewResult = { success: false, findings: "", cost: 0, duration: 0 };

    for await (const message of query({
      prompt: `审查以下代码变更，输出结构化的审查报告：\n\n${diff}`,
      options: {
        // 权限：只读 + 不弹确认
        allowedTools: ["Read", "Grep", "Glob", "Agent"],
        permissionMode: "dontAsk",
        maxTurns: 15,
        abortController: controller,
        sessionStore,

        // 子 Agent：并行审查
        agents: {
          "quality-checker": {
            description: "代码质量审查：命名、结构、复杂度、重复代码",
            prompt: "你是代码质量专家。检查命名规范、函数复杂度、代码重复、设计模式使用。输出 JSON 格式的发现列表。",
            tools: ["Read", "Grep", "Glob"],
            model: "sonnet",
          },
          "security-auditor": {
            description: "安全审计：注入、认证、数据泄露、依赖漏洞",
            prompt: "你是安全审计专家。检查 SQL 注入、XSS、CSRF、认证绕过、敏感数据暴露。按严重程度排序输出。",
            tools: ["Read", "Grep", "Glob"],
            model: "sonnet",
          },
        },

        // 流式输出用于实时展示进度
        includePartialMessages: true,
      },
    })) {
      if (message.type === "stream_event") {
        const e = message.event;
        if (e.type === "content_block_start" && e.content_block.type === "tool_use") {
          process.stdout.write(`🔧 ${e.content_block.name}... `);
        }
      }

      if (message.type === "assistant") {
        for (const block of message.content) {
          if (block.type === "text") {
            findings += block.text;
          }
        }
      }

      if (message.type === "result") {
        result = {
          success: message.subtype === "success",
          findings,
          cost: message.total_cost_usd,
          duration: message.duration_ms,
        };
      }
    }

    return result;
  } catch (err) {
    if (err.name === "AbortError") {
      return { success: false, findings: "审查超时", cost: 0, duration: 120_000 };
    }
    throw err;
  } finally {
    clearTimeout(timeout);
  }
}

这个示例综合运用了：权限锁定（dontAsk + 只读工具）、多 Agent 并行（质量 + 安全两个子 Agent）、超时控制（AbortController）、流式输出（实时展示进度）、Session 持久化（崩溃可恢复）、成本追踪（ResultMessage）。

系列总结

六篇文章，我们从零构建了对 Claude Agent SDK 的完整理解：

第一篇 Agent Loop——理解 SDK 的核心循环：prompt → 模型推理 → 工具调用 → 结果反馈 → 继续推理。这是一切的基础。

第二篇 自定义工具——让 Agent 拥有你定义的能力。工具是 Agent 与外部世界交互的唯一接口。

第三篇 Hooks 编排——在工具调用的前后插入自定义逻辑。审计、过滤、改写、通知——Hooks 是控制面。

第四篇 Session 管理——让 Agent 拥有记忆。continue/resume/fork 三种模式，加上 File Checkpointing 的回滚能力。

第五篇 流式输出——让用户看到 Agent 的思考过程。从逐字打字机到完整的 SSE Web UI，再到取消机制。

第六篇 生产架构——把能跑的 Agent 变成能上线的 Agent。权限、多 Agent、错误恢复、安全部署、成本控制。

这六个维度覆盖了从原型到生产的完整路径。掌握它们，你就有能力构建真正可靠的 AI Agent 应用。

参考资料

• Claude Agent SDK - Permissions — 权限模型完整文档
• Claude Agent SDK - Multi-Agent — 多 Agent 协作架构
• Claude Agent SDK - Hosting — 生产部署指南
• Claude Agent SDK - Secure Deployment — 安全部署最佳实践
• Claude Agent SDK - Cost Tracking — 成本追踪与优化