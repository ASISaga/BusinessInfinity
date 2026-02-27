# Migration Guide: BusinessInfinity — AOS Client SDK

## Overview

BusinessInfinity is a lean Azure Functions app powered by the `aos-client-sdk`. All Azure Functions scaffolding, Service Bus communication, authentication, and deployment are handled by the SDK. BusinessInfinity contains **only business workflow definitions**.

### v4.0.0 — Enterprise Capabilities (current)

v4.0.0 integrates all 14 AOS Client SDK enhancements:

- **ObservabilityConfig** — structured logging, correlation tracking, health checks
- **workflow_template** — reusable orchestration patterns (`c_suite_orchestration`)
- **6 new enterprise workflows** — knowledge-search, risk-register, risk-assess, log-decision, covenant-create, ask-agent
- **Orchestration update handler** — `@app.on_orchestration_update("strategic-review")`
- **MCP tool integration** — `@app.mcp_tool("erp-search")`
- **14 total workflows** (up from 8 in v3.0)

### v3.0 — SDK-Only Rewrite

v3.0 was a complete rewrite from custom runtime to `aos-client-sdk`. All infrastructure code was removed and archived to `.archive/pre-sdk-refactor/`.

## Architecture Change

### Before (v2.0 — Custom Runtime)
```
BusinessInfinity
├── runtime/                    ← Custom infrastructure layer
│   ├── azure_functions_runtime.py
│   ├── routes_registry.py
│   ├── config_loader.py
│   ├── storage.py
│   └── messaging.py
├── src/
│   ├── app.py                  ← Custom application lifecycle
│   ├── config.py               ← Custom configuration
│   ├── handlers.py             ← Custom HTTP handlers
│   ├── aos_client.py           ← Custom Service Bus client
│   ├── agents/                 ← Agent implementations
│   ├── orchestration/          ← Custom orchestration
│   └── ... (79 Python files)
└── function_app.py             ← Complex initialization (114 lines)
```

### After (v3.0 — AOS Client SDK)
```
BusinessInfinity
├── src/
│   └── business_infinity/
│       ├── __init__.py
│       └── workflows.py        ← All business workflows (@app.workflow)
├── function_app.py             ← Zero boilerplate (2 lines)
├── tests/
│   └── test_workflows.py
└── pyproject.toml              ← Single dependency: aos-client-sdk[azure]
```

## What Changed

| Component | v2.0 | v3.0 |
|-----------|------|------|
| Entry point | 114-line `function_app.py` with runtime init | 2-line `function_app.py` |
| HTTP routing | Custom `RouteRegistry` + `handlers.py` | `@app.workflow` decorators |
| Auth | Custom middleware | SDK's `AOSAuth` |
| Service Bus | Custom `AOSServiceBusClient` (460 lines) | SDK's `AOSServiceBus` |
| Configuration | Custom `BusinessInfinityConfig` + `RuntimeConfig` | SDK env var convention |
| Agent management | Local `AgentInfo` + agent coordinator | RealmOfAgents catalog via SDK |
| Orchestration | Custom `BoardroomOrchestrator` | SDK's `AOSClient.start_orchestration()` |
| Dependencies | 30+ packages | 1 package: `aos-client-sdk[azure]` |

## What Was Removed

All infrastructure code that is now provided by the SDK:

- `runtime/` — Replaced by `AOSApp` framework
- `src/app.py` — Replaced by `AOSApp`
- `src/config.py` — Replaced by SDK env var convention
- `src/handlers.py` — Replaced by `@app.workflow` decorators
- `src/aos_client.py` — Replaced by `AOSClient`
- `src/agents/` — Agents are in RealmOfAgents, accessed via SDK
- `src/orchestration/` — Replaced by SDK orchestration
- All other `src/` modules — Business logic is expressed as workflows

All removed files are preserved in `.archive/pre-sdk-refactor/`.

## How to Add a New Workflow

```python
# In src/business_infinity/workflows.py

@app.workflow("my-new-workflow")
async def my_new_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents]
    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose="Description of what the workflow achieves",
        context=request.body,
    )
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}
```
