# 原始资料:The 7-Hour Problem: How Production AI Agents Survive Crashes, Context Limits, and Tool Failures

> 来源:AgentMarketCap 博客,https://agentmarketcap.ai/blog/2026/04/05/agent-state-persistence-long-running-task-recovery
> 抓取日期:2026-08-09;状态:已整理为 docs/03-agents/agent-persistence-patterns.md
> 性质:Agent 持久化运行的三大工程范式——Temporal Durable Execution(事件回放)/ LangGraph Checkpointing(图状态快照)/ Harness-Level Checkpointing(文件系统即状态)+ 幂等约束 + 企业部署意义

---

There is a dirty secret at the heart of the agentic AI revolution: the longer you let an agent run, the more likely it is to fail. Research from production deployments shows that every AI agent experiences a measurable success rate decrease after just 35 minutes of runtime — and that doubling the task duration quadruples the failure rate.

 This is the 7-Hour Problem. As enterprises start assigning AI agents to day-long tasks — refactoring a 200,000-line codebase, running a multi-step due diligence workflow, automating a quarterly compliance audit — the reliability math becomes brutal. A 1% failure rate per step compounds to a 63% overall failure rate across 100 steps. For a system that's supposed to run autonomously overnight, that's not an occasional hiccup. It's a broken product.

 The good news: 2025 and early 2026 produced three distinct engineering patterns for solving this problem. Teams at Temporal, LangChain/LangGraph, and Anthropic (via Claude Code's harness architecture) have each published production-grade approaches to keeping agents alive across crashes, context window exhaustion, network failures, and tool timeouts. The bad news: most enterprises are still deploying agents without any of them.

 Here's what the engineering actually looks like — and which pattern fits which workload.

 Why Long-Running Agent Sessions Break

 Before examining solutions, it's worth being precise about failure modes. Long-running agent sessions fail in three distinct ways, and they require different remedies:

 Context window exhaustion. Modern frontier models — Claude Sonnet 4.6, GPT-5.4, Gemini 3.1 Ultra — have massive context windows, but multi-step agentic tasks burn through them fast. Every tool call appends its result to the conversation. After 40-50 sequential decisions, even a 200,000-token context window starts to fill. Claude Code's architecture addresses this with five distinct context management strategies: time-based clearing of old tool results, conversation summarization, session memory extraction, full history summarization, and oldest-message truncation. But these strategies lose information. When context overflows, agents forget what they were doing.

 Process-level crashes. LLM API calls time out. Network requests fail. Container orchestrators kill pods under memory pressure. A local developer machine goes to sleep. Any of these events terminates the running process — and without external state, the entire session is lost. In a 7-hour autonomous run, the probability of at least one such event approaches near-certainty.

 Tool failure and non-idempotent side effects. When an agent writes to a database, sends an email, or deploys code, failure mid-sequence creates an inconsistent state. Naive retry logic re-executes already-completed steps, causing duplicate writes, double-sent emails, or partially applied migrations. This is arguably the most dangerous failure mode: the agent recovers, but the world is now in a broken state.

 Between October 2025 and January 2026, the 99th percentile turn duration in interactive Claude Code sessions nearly doubled — from under 25 minutes to over 45 minutes — as users pushed agents toward longer horizons. The infrastructure question of what happens when those sessions break has gone from theoretical to urgent.

 Pattern 1: Temporal's Durable Execution — Event History as Ground Truth

 Temporal's approach to agent reliability is architecturally distinct from anything in the LLM ecosystem. Rather than checkpointing state, Temporal checkpoints events .

 Every action the agent takes — every LLM call, every tool invocation, every external API request — is written to an append-only Event History before execution. When a process crashes, the workflow engine replays the Event History from the beginning, skipping already-completed Activities by substituting their recorded return values. The workflow code re-runs deterministically; the external side effects do not.

 For AI agents, this separation between Workflows (deterministic orchestration logic) and Activities (non-deterministic work like LLM calls and tool use) is the key. An LLM call is an Activity. It gets recorded. If the process dies after the LLM responds but before the agent acts on that response, Temporal replays the workflow, skips the LLM call (returning the cached result), and continues from the next step. No tokens are wasted. No state is lost.

 As of March 2026, Temporal's integration with the OpenAI Agents SDK is Generally Available. The pattern extends cleanly to any framework: wrap your agent loop in a Temporal Workflow, promote each LLM call and tool invocation to a Temporal Activity, and your agent becomes crash-proof by construction.

 The constraint: Workflows must be deterministic. Random number generation, timestamp reads, and non-deterministic branching must all route through Temporal's determinism-safe equivalents. For teams already building with Temporal, this is second nature. For teams coming from LangChain or custom agent loops, it's a meaningful refactor.

 Best for: Long-running background tasks (overnight research runs, autonomous code migrations, multi-day compliance workflows) where crash tolerance is the primary constraint and the engineering team is comfortable with Temporal's programming model.

 Pattern 2: LangGraph Checkpointing — Graph State as First-Class Citizen

 LangGraph's approach starts from a different premise: the agent is a directed graph, and every node in that graph is a natural checkpoint boundary.

 When you build an agent in LangGraph, each node — each LLM decision, each tool call, each conditional branch — writes its output state to a configured checkpointer before passing control to the next node. If the process crashes between nodes, the agent resumes from the last successfully written checkpoint. Unlike Temporal's replay model, LangGraph doesn't re-execute previous steps; it loads the serialized state snapshot and continues forward.

 For production deployments, LangGraph supports multiple storage backends:

 MemorySaver — in-process, development only

 SqliteSaver / PostgresSaver — single-machine persistence, small teams

 DynamoDBSaver — AWS-native, production scale

 The DynamoDBSaver (maintained by AWS via the langgraph-checkpoint-aws package) handles an important production edge case: large checkpoints. Agent state that exceeds 350 KB is automatically offloaded to S3, with DynamoDB storing pointer references. This matters in practice — a multi-turn agent that has accumulated tool results, long documents, and intermediate outputs can easily exceed DynamoDB's 400 KB item limit. The tiered storage approach handles this transparently.

 Production configurations typically enable two additional features: TTL-based expiration (e.g., ttl_seconds=86400 * 7 for 7-day retention) and checkpoint compression to reduce storage costs. For long-running tasks with hundreds of checkpoints per session, compression can cut storage costs by 60-70%.

 The checkpointing approach also enables human-in-the-loop workflows naturally. An agent can checkpoint at any node, pause for human review, and resume days later — with full state restored. This is increasingly important for enterprise deployments where regulated workflows require human sign-off at intermediate stages.

 Best for: Interactive and semi-autonomous agents where human-in-the-loop is required, multi-tenant deployments where many concurrent sessions need isolation, and teams already using LangGraph who want minimal architectural change.

 Pattern 3: Harness-Level Checkpointing — Claude Code's Approach

 The third pattern doesn't come from a workflow framework. It comes from studying how production coding agents actually handle long sessions.

 Claude Code's leaked harness architecture (documented extensively in early 2026) reveals a layered approach to state management that doesn't rely on an external orchestration framework. The harness — the infrastructure wrapping the model — manages five distinct strategies for context pressure, as noted above. But beyond context management, it separates session state from task state .

 Session state (the conversation history, tool call results, model responses) is volatile. Task state (the filesystem, the git repository, the set of completed subtasks) is durable. Claude Code exploits this separation by treating the filesystem as its checkpoint store. At any recovery point, the agent can reconstruct task progress by reading git history, inspecting modified files, and examining markers left in the repository.

 This approach generalizes into a pattern that several teams have implemented independently:

 Decompose the task into verifiable subtasks with explicit completion markers (e.g., a git commit, a status file, a database record).

 Write completion state externally before moving to the next subtask.

 On recovery , scan the external state to determine which subtasks are complete and resume from the first incomplete one.

 This is essentially a manually implemented event log — simpler than Temporal, less structured than LangGraph, but requiring no additional infrastructure. Devin's approach to long-running coding tasks follows a similar pattern: each PR represents a checkpointed unit of work. Devin can be interrupted between PRs and resume cleanly. Cognition's 2025 annual performance review noted that 67% of Devin's PRs are now merged (up from 34% in 2024), and attributed much of this improvement to better task decomposition and checkpointed subtask management.

 Replit Agent 4 applies the same insight to development environments: the Repl itself is the checkpoint. Every meaningful state change is persisted to Replit's cloud storage. If the agent session crashes, restarting from the Repl restores the working environment, installed dependencies, and file state. The agent replays only the planning step, not the work.

 Best for: Coding agents and developer tools where the artifact of work (code, files, git history) is itself the state. Lower overhead than Temporal, no framework dependency, but requires careful task decomposition and marker design.

 The Idempotency Constraint

 All three patterns share a hard prerequisite that's easy to overlook: every tool that writes external state must be idempotent .

 If an agent calls a payment API, sends a webhook, or writes a database record, and then crashes before the checkpoint commits, the recovery mechanism will retry that action. Without idempotency — typically implemented via idempotency keys tied to workflow/checkpoint IDs — the retry causes a duplicate side effect.

 This is not a theoretical concern. In practice, the most damaging agent failures in production are not crashes themselves but the inconsistent state left by non-idempotent retries: duplicate customer emails, double-applied database migrations, redundant API charges. Teams adopting any of the three patterns above need to audit every external tool call for idempotency before trusting the recovery path.

 What This Means for Enterprise Deployments

 The reliability gap between benchmark-optimized agents and production-grade agents is wide — and it's primarily an infrastructure gap, not a model capability gap. SWE-bench tests whether an agent can solve a problem at all. It says nothing about whether the agent can solve it reliably over hours, across failures, at scale.

 Pattern Best For Infrastructure Required Recovery Granularity 
 Temporal Durable Execution Overnight/background tasks Temporal cluster or cloud Activity-level (step-by-step) 
 LangGraph + DynamoDB/S3 Interactive + HITL workflows AWS infra or Postgres Node-level (graph step) 
 Harness Checkpointing Coding agents, file-based work External storage (git, DB, S3) Subtask-level (manual) 

 By the end of 2026, Gartner projects 40% of enterprise applications will include task-specific AI agents — up from under 5% in 2025. The teams that build durable state management now will have a structural advantage over those still running stateless loops when that wave hits.

 The 7-Hour Problem isn't solved by a better model. It's solved by treating agent state as infrastructure — the same way we treat database transactions, message queues, and distributed locks. The patterns are here. The frameworks are mature. The remaining question is which engineering teams will build them in time.

 Track how the leading coding agents — Devin, Claude Code, Replit Agent, and 500+ others — handle real-world reliability benchmarks at AgentMarketCap where production metrics matter more than leaderboard peaks.