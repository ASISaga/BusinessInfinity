# Orchestration Boundaries: Shared vs. Business-Specific Code

## Shared (Reusable) Code
**Location:** `RealmOfAgents/AgentOperatingSystem/orchestration.py`

- `Workflow`, `WorkflowStep`: Core data structures for multi-agent workflows and steps.
- `OrchestrationEngine`: Implements generic workflow execution, dependency management, and agent coordination strategies (parallel, sequential, hierarchical).
- All logic in this module is designed to be agnostic to any specific business domain. It can be reused by any project needing multi-agent orchestration.

## Business-Specific Code
**Location:** `BusinessInfinity/core/orchestrator.py`

- `BusinessInfinityOrchestrator`: Application-layer orchestrator that:
  - Integrates the shared `OrchestrationEngine` for workflow and agent coordination.
  - Adds business logic for event handling (e.g., budget alerts, quality issues, market changes, operational alerts).
  - Connects to domain-specific components (e.g., MCP handler, decision engine, governance validation).
  - Exposes business-specific APIs for process_decision, handle_business_event, and system status.
- Only business logic, event types, and integrations unique to BusinessInfinity should reside here.

## Usage Pattern
- **Add new orchestration strategies or primitives:** Implement in `AgentOperatingSystem/orchestration.py` for reuse.
- **Add new business processes, event types, or integrations:** Implement in `BusinessInfinity/core/orchestrator.py`.

## Summary
- **Shared code** = orchestration engine, workflow primitives, agent coordination logic (generic, reusable).
- **Business-specific code** = event handling, business process logic, integrations (application/domain-specific).

---
For further development, always keep orchestration logic generic and reusable in `AgentOperatingSystem`, and keep business rules and integrations in `BusinessInfinity`.
