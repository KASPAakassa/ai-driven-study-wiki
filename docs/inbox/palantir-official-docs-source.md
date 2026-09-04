# 原始资料:Palantir 官方文档摘录(英文原文,已翻译进正式文章)

> 来源:Palantir 官方文档(抓取 2026-08-09,状态:英文原文存档于此,中文翻译见 docs/06-enterprise/ontology-agent-adoption/palantir-company-overview.md)
> 链接:Ontology overview https://www.palantir.com/docs/foundry/ontology/overview/;The Ontology system https://www.palantir.com/docs/foundry/architecture-center/ontology-system/;Platform overview https://www.palantir.com/docs/foundry/platform-overview/overview/

---

## 1. Ontology overview(节选)

"The Palantir Ontology is an operational layer for the organization. The Ontology sits on top of the digital assets integrated into the Palantir platform (datasets, virtual tables, and models) and connects them to their real-world counterparts, ranging from physical assets like plants, equipment, and products to concepts like customer orders or financial transactions. In many settings, the Ontology serves as a digital twin of the organization, containing both the semantic elements (objects, properties, links) and kinetic elements (actions, functions, dynamic security) needed to enable use cases of all types."

"Defining the semantics of your organization happens by mapping existing datasources into objects, properties, and links in the Ontology. Far beyond data cataloging or schema design solutions, the Ontology allows you to define a robust foundation for end-user workflows, including rich metadata for all fields and complete with granular security and governance for all changes."

"The kinetics of the organization—enabling change while complying with organizational controls and governance—are defined in the Ontology using action types and functions. Action types enable you to capture data from operators in your organization or orchestrate decision-making processes that connect to your existing systems, while functions provide a way to author and evolve business logic with arbitrary complexity."

"An interface is an Ontology type that describes the shape of an object type and its capabilities. Interfaces provide object type polymorphism, allowing for consistent modeling of and interaction with object types that share a common shape."

"The goal of investing in the Ontology is to facilitate better decision-making in an organization at scale... users can create reusable Object Views, search for objects of interest in Object Explorer, perform complex analyses in Quiver, build high-quality applications in Workshop, and more."

## 2. The Ontology system(节选)

"The Ontology is the system at the heart of Palantir's architecture. The Ontology is designed to represent the complex, interconnected decisions of an enterprise, not simply the data. This enables both humans and AI agents to collaborate, across operational workflows that must orchestrate with the physical world."

"The Ontology models decisions through the four-fold integration of data, logic, action, and security."

"The data objects, or 'nouns', however, must be complemented by 'verbs' in order to model decisions; semantics must be paired with kinetics."

"The Ontology is not a 'semantic layer'; the fourfold integration and operationalization of data, logic, action, and security cannot be accomplished with a thin semantic layer or a monolithic design. Rather, the Ontology is a multimodal system consisting of dozens of underlying components, which can conceptually be grouped into a Language, an Engine, and Toolchain."

- Language: models the semantic objects, links, and properties; along with the kinetic actions and automations; and the literal pieces of logic.
- Engine: provides the modular read architecture (high-scale SQL queries, real-time subscription to state changes, materializations for mixed Human + AI teams) and a scalable write architecture (atomic and durable transactional updates, high-scale batch mutations, high-scale streams, Change Data Capture for extremely low-latency mirroring).
- Toolchain: the Ontology SDK (OSDK) and a rich collection of DevOps tooling.

"The Ontology serves as the dynamic, compounding core of the cybernetic enterprise. Every data integration helps build a full-fidelity representation of the operational world, shared by humans and AI-enabled agents. Every piece of feedback gathered within a workflow can be securely incorporated into continuous learning loops, and used to power the journey from augmentation to automation."

## 3. Platform overview(节选)

"Palantir AIP powers real-time, AI-driven decision-making in the most critical commercial and government contexts... Palantir AIP connects generative AI to operations. Together with Foundry - Palantir's data operations platform - and Apollo - Palantir's mission control for autonomous software deployment, AIP is part of an AI Mesh that can deliver the full gamut of AI-driven products... the key differentiator is a software architecture which revolves around the Palantir Ontology."

Decision components:
- Data: What are the relevant facts or truth about the world and our operations that form the context for this decision?
- Logic: What organizational or business rules act as guardrails for this decision? What are the probabilities of certain outcomes under different assumptions? What are the inputs from our forecasting and optimization models?
- Actions: What are the 'kinetics' or effects of this decision - how does the decision manifest in the world?

"Actions define the 'verbs' of the enterprise - the things that are done - and control how human operators or AI agents can ensure that their decision persists."

"Rather than directly make changes, AI agents create proposals either synchronously through direct integration with AIP Logic functions integrated into Workshop, or asynchronously through Automate or the Use LLM node in Pipeline Builder. The resulting proposal can then be surfaced to an operator for refinement, feedback, and a resulting decision. This proposal-based pattern... also generates valuable metadata that enables a positive cycle where the Agent can learn and evolve with continuous feedback."

Platform capabilities: data connectivity & integration; model connectivity & development; ontology building; use case development; analytics; product delivery; security & governance.
