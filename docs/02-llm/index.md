# 💬 大语言模型

> LLM 全链路:Transformer 架构、Tokenizer、预训练、指令微调、RLHF、量化与推理、RAG、Agent 基础。

## 本章节文章

- [大语言模型概述](llm-intro.md) — 什么是 LLM、核心能力与局限、训练三步总览
- [Transformer 架构](transformer-architecture.md) — 自注意力、多头、位置编码,GPT 的心脏
- [Tokenizer 与词表](tokenizer.md) — 分词原理与 BPE
- [预训练与规模定律](pretraining.md) — 语言建模目标、scaling laws、困惑度
- [微调](fine-tuning.md) — 指令微调 SFT、LoRA/QLoRA
- [对齐:RLHF 与 DPO](rlhf-alignment.md) — 奖励模型、PPO、DPO
- [推理与部署](inference-deployment.md) — KV Cache、量化、vLLM
- [检索增强生成 RAG](rag.md) — 流程、向量检索、RAG vs 微调
- [模型后训练:预训练/SFT/RL](agent-post-training.md) — 三阶段分工、"SFT 记忆 vs RL 泛化"、数据与环境比算法重要(整理自《深入理解 AI Agent》)
- [LLM 推理的预训练-后训练接口](reasoning-pretraining-posttraining.md) — 象棋测试床:联合缩放律(预训练损失预测 RL 后 pass@1、算力越多越该投 RL)、RL 非简单锐化(易题放大/难题浮现)、计算最优分配(arXiv:2607.16097)

## 待整理 / 规划

<!-- 从 inbox 收件箱转入本主题的素材,梳理前先登记在这里 -->

## 学习指引

- 前置:先了解 [AI / ML / DL 基础](../01-ai-basics/index.md) 中的神经网络与注意力机制。
- 入门顺序:Transformer → Tokenizer → 预训练 → 微调/RLHF → 推理与部署 → RAG 与应用。
- 学完基础后进入 [Agent 章节](../03-agents/index.md) 学习 Agent 使用与开发。
