
# Logical Descriptions of Python Projects in ASISaga Workspace

---

## BusinessInfinity
**Purpose:** Unified business system integrating Azure, AI, and agent modules for business automation and orchestration.
	- **Key dependencies:** CEO, CFO, CMO, COO, CSO, Founder, Investor, Leader, Poet, Seeker, AgentOperatingSystem

---

### BusinessInfinity Submodules
**framework-server:** FastAPI-based backend for business logic and orchestration (now merged into main project).
**framework-functions:** Azure Functions integration for serverless business logic (now merged into main project).
**framework-mcp:** FastAPI/uvicorn-based microservice for MCP (Model Context Protocol) integration (now merged into main project).
**dashboard:** Dashboard and orchestration UI, integrating Azure Functions, Semantic Kernel, and OpenAI (now merged into main project).

---

## RealmOfAgents
**AgentOperatingSystem:** Core agent OS, supporting semantic kernel, async, telemetry, and web APIs for agent operations.
	- **Key dependencies:** (none)

**PurposeDrivenAgent:** Agent framework for purpose-driven, composable agents, with ChromaDB, OpenAI, and MCP integration. Depends on SelfLearningAgent.
	- **Key dependencies:** SelfLearningAgent

**FineTunedLLM:** Fine-tuning and orchestration for LLMs, supporting OpenAI, Azure, AWS, and local dev workflows.
	- **Key dependencies:** (none)
	- **finetuning-pipeline:** Azure Functions pipeline for LLM fine-tuning, supporting OpenAI and Anthropic.
	- **summarization-pipeline:** Azure Functions pipeline for LLM summarization, supporting Anthropic.

**SelfLearningAgent:** Self-learning agent core, with extensible agent logic and MCP integration.
	- **Key dependencies:** (none)

---

## MCP (Model Context Protocol)
**spec-kit-mcp:** MCP server for Specify spec-driven development tools, with CLI and server entrypoints.
	- **Key dependencies:** (none)

**mcp-reddit-server:** Reddit data integration for MCP, supporting Reddit APIs and fastmcp.
	- **Key dependencies:** (none)

**mcp-asisaga-com:** Azure Functions-based MCP server for asisaga.com integration.
	- **Key dependencies:** (none)

**mcp-asisaga-com-src:** Source code for asisaga.com MCP server, with JSON-RPC and Azure Functions.
	- **Key dependencies:** (none)

**ERPNext-MCP:** MCP server for ERPNext, exposing business operations via Python APIs, supporting Frappe and Uvicorn.
	- **Key dependencies:** (none)

**linkedin-mcp-server:** LinkedIn API integration for MCP, with Azure Functions and CLI entrypoint.
	- **Key dependencies:** (none)

---

## Project pyproject.toml Links

- [BusinessInfinity](../../BusinessInfinity/pyproject.toml)
- [AgentOperatingSystem](../../RealmOfAgents/AgentOperatingSystem/pyproject.toml)
- [PurposeDrivenAgent](../../RealmOfAgents/PurposeDrivenAgent/pyproject.toml)
- [SelfLearningAgent](../../RealmOfAgents/SelfLearningAgent/pyproject.toml)
- [spec-kit-mcp](../../MCP/spec-kit-mcp/pyproject.toml)
- [mcp-reddit-server](../../MCP/mcp-reddit/pyproject.toml)
- [mcp-asisaga-com](../../MCP/mcp.asisaga.com/pyproject.toml)
- [ERPNext-MCP](../../MCP/ERPNext-MCP/pyproject.toml)
- [linkedin-mcp-server](../../MCP/linkedin-mcp-server/pyproject.toml)
- [CSO](../../Buddhi/CSO/pyproject.toml)
