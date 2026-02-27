# BusinessInfinity

A lean Azure Functions application that uses the **Agent Operating System** as an infrastructure service. BusinessInfinity contains only business logic — all Azure Functions scaffolding, Service Bus communication, authentication, and deployment are handled by the `aos-client-sdk` v5.0.0.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  BusinessInfinity (this app)                        │
│  ┌───────────────────────────────────────────────┐  │
│  │  workflows.py       @app.workflow decorators  │  │
│  │  function_app.py    app.get_functions()       │  │
│  │    └─ aos-client-sdk handles everything else  │  │
│  └───────────────────────────────────────────────┘  │
│  Zero Azure Functions boilerplate.                  │
│  Zero agent code. Zero infrastructure code.         │
└──────────────┬───────────────────┬──────────────────┘
               │ HTTPS             │ Azure Service Bus
               ▼                   ▼
┌─────────────────────────────────────────────────────┐
│  Agent Operating System (infrastructure)            │
│  ┌──────────────────┐  ┌─────────────────────────┐  │
│  │ aos-function-app  │  │ aos-realm-of-agents     │  │
│  │ Orchestration API │  │ Agent catalog:          │  │
│  │ + Service Bus     │  │  CEO · CFO · CMO · CSO  │  │
│  │   triggers        │  │  COO · CTO · CHRO       │  │
│  └──────────────────┘  └─────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │ aos-kernel                                      │ │
│  │ Orchestration · Messaging · Storage · Auth      │ │
│  └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Key Principle

> **BusinessInfinity focuses only on business logic.  The SDK handles the rest.**

| Concern | Owner |
|---------|-------|
| Business workflows (strategic review, market analysis, budget approval, etc.) | BusinessInfinity |
| Azure Functions scaffolding, HTTP/Service Bus triggers, auth | aos-client-sdk |
| Agent lifecycle, perpetual orchestration, messaging, storage, monitoring | AOS |
| Agent catalog (C-suite agents, capabilities, LoRA adapters) | RealmOfAgents |

## Workflows

### Define workflows with decorators

```python
# src/business_infinity/workflows.py
from aos_client import AOSApp, WorkflowRequest, workflow_template
from aos_client.observability import ObservabilityConfig

app = AOSApp(
    name="business-infinity",
    observability=ObservabilityConfig(
        structured_logging=True,
        correlation_tracking=True,
        health_checks=["aos", "service-bus"],
    ),
)

@workflow_template
async def c_suite_orchestration(request, agent_filter, purpose, purpose_scope):
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents if agent_filter(a)]
    return await request.client.start_orchestration(
        agent_ids=agent_ids, purpose=purpose, purpose_scope=purpose_scope,
        context=request.body,
    )

@app.workflow("strategic-review")
async def strategic_review(request: WorkflowRequest):
    return await c_suite_orchestration(
        request,
        agent_filter=lambda a: True,
        purpose="Drive strategic review and continuous organisational improvement",
        purpose_scope="C-suite strategic alignment and cross-functional coordination",
    )
```

### Azure Functions entry point (zero boilerplate)

```python
# function_app.py
from business_infinity.workflows import app
functions = app.get_functions()
```

### Available Workflows

#### Orchestration Workflows (perpetual, purpose-driven)

| Workflow | Agents | Purpose |
|----------|--------|---------|
| `strategic-review` | All C-suite | Strategic alignment and cross-functional coordination |
| `market-analysis` | CMO + CEO + CSO | Market intelligence and competitive insights |
| `budget-approval` | CEO + CFO | Budget governance and fiscal responsibility |
| `risk-assessment` | CSO + CTO + COO | Enterprise risk monitoring and mitigation |
| `boardroom-session` | All C-suite | Autonomous boardroom with perpetual governance |
| `covenant-compliance` | CEO + COO + CSO | Covenant compliance and governance adherence |
| `talent-management` | CHRO + CEO + COO | Talent strategy and organizational development |
| `technology-review` | CTO + CEO + CSO | Technology strategy and architecture excellence |

#### Enterprise Capability Workflows (SDK v4.0.0)

| Workflow | SDK API | Purpose |
|----------|---------|---------|
| `knowledge-search` | `search_documents()` | Search the AOS knowledge base |
| `risk-register` | `register_risk()` | Register a new risk in the risk registry |
| `risk-assess` | `assess_risk()` | Assess likelihood/impact of a risk |
| `log-decision` | `log_decision()` | Log a boardroom decision to audit trail |
| `covenant-create` | `create_covenant()` | Create a business covenant |
| `ask-agent` | `ask_agent()` | Direct 1:1 agent interaction |

#### Advanced Enterprise Workflows (SDK v5.0.0)

| Workflow | SDK API | Purpose |
|----------|---------|---------|
| `risk-heatmap` | `get_risk_heatmap()` | Risk heatmap for boardroom strategic view |
| `risk-summary` | `get_risk_summary()` | Aggregate risk summary by category/severity |
| `compliance-report` | `generate_compliance_report()` | Compliance report for regulatory submissions |
| `create-alert` | `create_alert()` | Create metric threshold alerts |
| `register-webhook` | `register_webhook()` | Register webhook for external notifications |

#### Event Handlers and MCP Tools

| Type | Name | Description |
|------|------|-------------|
| Update Handler | `strategic-review` | Handles intermediate orchestration updates |
| MCP Tool | `erp-search` | Search ERP via MCP server integration |
| Covenant Event | `violated` | Handles covenant violation events |
| Covenant Event | `expiring` | Handles covenant expiration warnings |
| MCP Event | `erpnext:order_created` | Handles ERP order creation events |
| Webhook | `slack-notifications` | External Slack notification handler |

### Invoke via HTTP

```bash
# Strategic Review
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/strategic-review \
  -H "Content-Type: application/json" \
  -d '{"quarter": "Q1-2026", "focus_areas": ["revenue", "growth", "efficiency"]}'

# Market Analysis
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/market-analysis \
  -H "Content-Type: application/json" \
  -d '{"market": "EU SaaS", "competitors": ["AcmeCorp", "Globex"]}'

# Budget Approval
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/budget-approval \
  -H "Content-Type: application/json" \
  -d '{"department": "Marketing", "amount": 500000, "justification": "Q2 brand campaign"}'
```

All responses follow the perpetual orchestration pattern:
```json
{"orchestration_id": "...", "status": "active"}
```

#### Enterprise Capability Examples

```bash
# Knowledge Search
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/knowledge-search \
  -H "Content-Type: application/json" \
  -d '{"query": "sustainability policy", "doc_type": "policy", "limit": 5}'

# Register a Risk
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/risk-register \
  -H "Content-Type: application/json" \
  -d '{"title": "Supply chain disruption", "category": "operational", "owner": "coo"}'

# Log a Decision
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/log-decision \
  -H "Content-Type: application/json" \
  -d '{"title": "Expand to EU", "rationale": "Market opportunity", "agent_id": "ceo"}'

# Ask an Agent Directly
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/ask-agent \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "ceo", "message": "What is the Q2 strategy?"}'
```

#### v5.0.0 Advanced Capability Examples

```bash
# Risk Heatmap
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/risk-heatmap \
  -H "Content-Type: application/json" \
  -d '{"category": "operational"}'

# Risk Summary
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/risk-summary \
  -H "Content-Type: application/json" \
  -d '{"category": "financial"}'

# Compliance Report
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/compliance-report \
  -H "Content-Type: application/json" \
  -d '{"start_time": "2026-01-01T00:00:00", "end_time": "2026-03-31T23:59:59", "report_type": "decisions"}'

# Create Alert
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/create-alert \
  -H "Content-Type: application/json" \
  -d '{"metric_name": "risk_score", "threshold": 8.0, "condition": "gt"}'

# Register Webhook
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/register-webhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://hooks.slack.com/...", "events": ["decision.created"]}'
```

## Registration with AOS

Register this app with AOS to provision Service Bus infrastructure:

```python
from aos_client import AOSRegistration

async with AOSRegistration(aos_endpoint="https://my-aos.azurewebsites.net") as reg:
    info = await reg.register_app(
        app_name="business-infinity",
        workflows=[
            "strategic-review", "market-analysis", "budget-approval",
            "risk-assessment", "boardroom-session", "covenant-compliance",
            "talent-management", "technology-review",
            "knowledge-search", "risk-register", "risk-assess",
            "log-decision", "covenant-create", "ask-agent",
            "risk-heatmap", "risk-summary", "compliance-report",
            "create-alert", "register-webhook",
        ],
    )
```

## Local Development

```bash
pip install -e ".[dev]"
func start
```

Set environment variables:
```
AOS_ENDPOINT=http://localhost:7071       # AOS Function App
REALM_ENDPOINT=http://localhost:7072     # RealmOfAgents (if separate)
SERVICE_BUS_CONNECTION=                  # Service Bus (optional for local dev)
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `aos-client-sdk[azure]` ≥5.0.0 | SDK + Azure Functions + Service Bus + Auth + Enterprise APIs |

**No AOS kernel, agent, or infrastructure dependencies.** BusinessInfinity knows nothing about agent internals.

## Project Structure

```
BusinessInfinity/
├── function_app.py                  # Azure Functions entry point (2 lines)
├── pyproject.toml                   # Depends only on aos-client-sdk[azure]>=5.0.0
├── host.json                        # Azure Functions config
├── manifest.json                    # System architecture map
├── src/
│   └── business_infinity/
│       ├── __init__.py              # Package init (v5.0.0)
│       └── workflows.py             # All business workflows, event handlers, MCP tools, webhooks
├── tests/
│   └── test_workflows.py            # Workflow tests (14 tests)
└── docs/
    ├── AOS_ENHANCEMENT_REQUESTS.md  # Original SDK enhancement requests (implemented in v4.0.0)
    ├── AOS_FURTHER_ENHANCEMENTS.md  # Further SDK enhancement requests (implemented in v5.0.0)
    └── AOS_NEXT_ENHANCEMENTS.md     # Next SDK enhancement requests
```

## Related Repositories

- [AgentOperatingSystem](https://github.com/ASISaga/AgentOperatingSystem) — AOS meta-repository
- [aos-client-sdk](https://github.com/ASISaga/aos-client-sdk) — Client SDK & App Framework
- [aos-function-app](https://github.com/ASISaga/aos-function-app) — AOS orchestration API
- [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) — Agent catalog
- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel
- [businessinfinity.asisaga.com](https://github.com/ASISaga/businessinfinity.asisaga.com) — Web frontend

## License

MIT License — see [LICENSE](LICENSE)
