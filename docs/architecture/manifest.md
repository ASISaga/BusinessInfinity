# Boardroom Manifest – Composite Architecture, Action Legend, Flow Narrative & Full Schema‑Pure Contract

This document is now **visual + narrative + executable** — it contains:
1. Composite architecture diagram  
2. Action legend  
3. Flow narrative  
4. Full schema‑pure manifest contract with parameter definitions, output types, and role/scope constraints

---

## Composite Architecture Diagram
*(same as before — omitted here for brevity in this snippet, but keep in your repo)*

---

## Action Legend
*(same as before — IDs 1–20 with bindings)*

---

## Flow Narrative
*(same as before — UI‑Driven Agent Call + Direct AML Control)*

---

## Full Schema‑Pure Manifest Contract

```jsonc
{
  "$schema": "https://business-infinity.ai/manifest.schema.json",
  "version": "1.0.0",
  "roles": [
    "CEO", "CFO", "CTO", "COO", "Investor", "Governance", "Network"
  ],
  "scopes": [
    "local", "network"
  ],
  "actions": {
    "manifest.mcpUi.load": {
      "id": 1,
      "roles": "*",
      "scopes": "*",
      "params": {
        "roleScope": { "type": "string", "enum": ["CEO","CFO","CTO","COO","Investor","Governance","Network"] }
      },
      "returns": { "type": "object", "properties": { "schema": { "type": "object" } } }
    },
    "mcpUi.schema": {
      "id": 2,
      "roles": "*",
      "scopes": "*",
      "params": {},
      "returns": { "type": "object", "properties": { "uiSchema": { "type": "object" } } }
    },
    "mcpUi.action.invoke": {
      "id": 3,
      "roles": "*",
      "scopes": "*",
      "params": {
        "actionId": { "type": "string" },
        "payload": { "type": "object" }
      },
      "returns": { "type": "object", "properties": { "status": { "type": "string" } } }
    },
    "gov.validate": {
      "id": [4, 12, 16],
      "roles": "*",
      "scopes": "*",
      "params": {
        "context": { "type": "string", "enum": ["inference","message","training"] },
        "payload": { "type": "object" }
      },
      "returns": { "type": "object", "properties": { "approved": { "type": "boolean" } } }
    },
    "gov.approve": {
      "id": [5, 17],
      "roles": ["Governance"],
      "scopes": "*",
      "params": { "requestId": { "type": "string" } },
      "returns": { "type": "object", "properties": { "approved": { "type": "boolean" } } }
    },
    "agent.invoke": {
      "id": 6,
      "roles": "*",
      "scopes": "*",
      "params": {
        "agentId": { "type": "string" },
        "input": { "type": "string" }
      },
      "returns": { "type": "object", "properties": { "output": { "type": "string" } } }
    },
    "aml.endpoint.call": {
      "id": 7,
      "roles": "*",
      "scopes": "*",
      "params": {
        "endpointName": { "type": "string" },
        "input": { "type": "string" }
      },
      "returns": { "type": "object", "properties": { "result": { "type": "string" } } }
    },
    "aml.result": {
      "id": 8,
      "roles": "*",
      "scopes": "*",
      "params": {},
      "returns": { "type": "object", "properties": { "result": { "type": "string" } } }
    },
    "agent.result": {
      "id": 9,
      "roles": "*",
      "scopes": "*",
      "params": { "output": { "type": "string" } },
      "returns": { "type": "object", "properties": { "status": { "type": "string" } } }
    },
    "agent.emit": {
      "id": 10,
      "roles": "*",
      "scopes": "*",
      "params": { "message": { "type": "string" } },
      "returns": { "type": "object", "properties": { "queued": { "type": "boolean" } } }
    },
    "queue.trigger": {
      "id": 11,
      "roles": "*",
      "scopes": "*",
      "params": { "queueName": { "type": "string" } },
      "returns": { "type": "object", "properties": { "triggered": { "type": "boolean" } } }
    },
    "table.persist": {
      "id": 13,
      "roles": "*",
      "scopes": "*",
      "params": {
        "tableName": { "type": "string" },
        "record": { "type": "object" }
      },
      "returns": { "type": "object", "properties": { "success": { "type": "boolean" } } }
    },
    "table.query": {
      "id": 14,
      "roles": "*",
      "scopes": "*",
      "params": {
        "tableName": { "type": "string" },
        "filter": { "type": "object" }
      },
      "returns": { "type": "array", "items": { "type": "object" } }
    },
    "aml.control.request": {
      "id": 15,
      "roles": "*",
      "scopes": "*",
      "params": {
        "mode": { "type": "string", "enum": ["train","infer"] },
        "payload": { "type": "object" }
      },
      "returns": { "type": "object", "properties": { "status": { "type": "string" } } }
    },
    "aml.job.run": {
      "id": 18,
      "roles": "*",
      "scopes": "*",
      "params": {
        "jobName": { "type": "string" },
        "parameters": { "type": "object" }
      },
      "returns": { "type": "object", "properties": { "jobId": { "type": "string" } } }
    },
    "aml.registry.register": {
      "id": 19,
      "roles": ["CTO","Governance"],
      "scopes": "*",
      "params": {
        "modelName": { "type": "string" },
        "version": { "type": "string" },
        "metadata": { "type": "object" }
      },
      "returns": { "type": "object", "properties": { "registered": { "type": "boolean" } } }
    },
    "agent.bindLoRA": {
      "id": 20,
      "roles": ["CTO","Governance"],
      "scopes": "*",
      "params": {
        "agentId": { "type": "string" },
        "modelName": { "type": "string" },
        "version": { "type": "string" }
      },
      "returns": { "type": "object", "properties": { "bound": { "type": "boolean" } } }
    }
  }
}
```

---

## Unified Core Feature Reference

All core features referenced in this manifest (agent orchestration, storage, environment, ML pipeline, MCP, authentication) are now implemented and maintained in the AgentOperatingSystem (AOS) under `RealmOfAgents/AgentOperatingSystem`. For implementation details, API contracts, and usage, refer to the AOS documentation and codebase. BusinessInfinity only defines business-specific contracts and UI schemas.