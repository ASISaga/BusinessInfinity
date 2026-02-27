# AOS Client SDK — Next Enhancement Requests

**From:** BusinessInfinity  
**To:** AgentOperatingSystem / aos-client-sdk  
**Date:** 2026-02-27  
**Context:** After integrating all 26 enhancements (14 in v4.0.0 + 12 in v5.0.0) into BusinessInfinity, we've identified additional improvements for production-hardening and the Global Boardroom Network rollout. These emerge from exercising the v5.0.0 APIs in production-style workflows with the full C-suite agent ensemble.

> **Note:** Until the AOS Client SDK implements these enhancements natively,
> BusinessInfinity implements them directly in
> `src/business_infinity/workflows.py`.  Each item below links to its local
> implementation.

---

## Priority 1 — Critical for Production Hardening

### 1. End-to-End Encryption for Sensitive Data

**Problem:** Boardroom decisions, financial data, and risk assessments transit through AOS and Service Bus in plaintext. Enterprise customers require end-to-end encryption for sensitive workflow data beyond transport-layer TLS.

**Requested Enhancement:**

```python
# AOSClient additions
client = AOSClient(
    endpoint="...",
    encryption=EncryptionConfig(
        key_vault_url="https://my-vault.vault.azure.net",
        key_name="boardroom-key",
        encrypt_fields=["context", "output"],
    ),
)
```

**Rationale:** Financial governance workflows (budget-approval, compliance-report) contain sensitive data that must be encrypted at rest and in transit within the AOS pipeline.

---

### 2. Rate Limiting and Quota Management

**Problem:** BusinessInfinity's 19 workflows can generate significant AOS API traffic, especially during boardroom sessions with all 7 C-suite agents. There is no SDK-level rate limiting or quota management to prevent resource exhaustion.

**Requested Enhancement:**

```python
# AOSClient additions
client = AOSClient(
    endpoint="...",
    rate_limit=RateLimitConfig(
        requests_per_minute=100,
        burst_limit=20,
        backoff_strategy="exponential",
    ),
)

# Quota tracking
quota = await client.get_quota_usage()
print(quota.requests_remaining, quota.reset_at)
```

**Rationale:** Production workloads need predictable resource consumption. Without rate limiting, a runaway orchestration could exhaust AOS capacity.

---

### 3. Workflow Dependency Chains

**Problem:** BusinessInfinity has logical dependencies between workflows (e.g., `compliance-report` should run after `covenant-compliance` produces findings). The SDK has no mechanism to express or enforce workflow ordering.

**Requested Enhancement:**

```python
@app.workflow("compliance-report", depends_on=["covenant-compliance"])
async def compliance_report(request: WorkflowRequest):
    # Automatically receives outputs from covenant-compliance orchestration
    covenant_findings = request.upstream_outputs.get("covenant-compliance")
    ...
```

**Rationale:** Enterprise workflow pipelines require ordered execution with data passing between stages.

---

### 4. Bulk Orchestration Management

**Problem:** The boardroom session spawns multiple orchestrations (strategic-review, risk-assessment, covenant-compliance simultaneously). There is no SDK mechanism to manage these as a group — e.g., stop all orchestrations for a boardroom session, get aggregate status.

**Requested Enhancement:**

```python
# AOSClient additions
async def create_orchestration_group(
    self, name: str, orchestration_ids: List[str],
) -> OrchestrationGroup

async def get_group_status(self, group_id: str) -> OrchestrationGroupStatus
async def stop_group(self, group_id: str) -> None
```

**Rationale:** The boardroom paradigm requires grouped orchestration lifecycle management.

---

## Priority 2 — Important for Feature Completeness

### 5. Agent Capability Matching

**Problem:** `select_c_suite_agents` currently matches by agent ID or type. For dynamic agent selection, the SDK should support capability-based matching with scoring.

**Requested Enhancement:**

```python
# AOSClient additions
async def find_agents(
    self,
    required_capabilities: List[str],
    preferred_capabilities: List[str] = None,
    min_score: float = 0.5,
) -> List[AgentMatch]

class AgentMatch(BaseModel):
    agent: AgentDescriptor
    score: float  # 0.0–1.0 based on capability match
    matched_capabilities: List[str]
```

**Rationale:** As the agent catalog grows, capability-based matching enables more flexible and maintainable agent selection.

---

### 6. Orchestration Checkpointing and Resume

**Problem:** Perpetual orchestrations can run for days or weeks. If AOS restarts or an agent fails, there is no checkpoint mechanism. The orchestration loses its accumulated context.

**Requested Enhancement:**

```python
# AOSClient additions
async def checkpoint_orchestration(
    self, orchestration_id: str, checkpoint_data: dict,
) -> Checkpoint

async def resume_orchestration(
    self, orchestration_id: str, from_checkpoint: str = "latest",
) -> OrchestrationStatus
```

**Rationale:** Perpetual orchestrations need durability guarantees. Checkpointing ensures no progress is lost during infrastructure events.

---

### 7. Conditional Webhooks and Event Filtering

**Problem:** The webhook support sends all matching events. BusinessInfinity needs conditional webhooks — e.g., only notify Slack when a decision has "critical" priority, or only when risk score exceeds 8.0.

**Requested Enhancement:**

```python
# AOSClient additions
async def register_webhook(
    self,
    url: str,
    events: List[str],
    filter: dict = None,  # {"field": "priority", "op": "eq", "value": "critical"}
) -> Webhook
```

**Rationale:** Enterprise notification systems need filtering to prevent alert fatigue.

---

### 8. Audit Trail Tamper Detection

**Problem:** The audit trail provides immutable logging, but there is no mechanism to verify that the trail has not been tampered with (e.g., Merkle tree verification, blockchain anchoring).

**Requested Enhancement:**

```python
# AOSClient additions
async def verify_audit_integrity(
    self,
    start_time: datetime = None,
    end_time: datetime = None,
) -> AuditIntegrityReport

class AuditIntegrityReport(BaseModel):
    verified: bool
    entries_checked: int
    integrity_hash: str
    anomalies: List[dict]
```

**Rationale:** Regulatory compliance requires proof that audit trails have not been modified.

---

## Priority 3 — Nice to Have

### 9. SDK Plugin Architecture

**Problem:** BusinessInfinity needs custom middleware for logging, metrics, and request transformation. The SDK has no plugin or middleware architecture.

**Requested Enhancement:**

```python
# AOSApp additions
app.use(LoggingMiddleware())
app.use(MetricsMiddleware(provider="prometheus"))
app.use(RequestTransformMiddleware(transform_fn=add_tenant_context))
```

**Rationale:** Plugin architecture enables extensibility without modifying SDK code.

---

### 10. Workflow Documentation Generation

**Problem:** BusinessInfinity has 19 workflows. There is no automatic way to generate API documentation from the workflow definitions and their docstrings.

**Requested Enhancement:**

```bash
aos docs generate --app business-infinity --format openapi
aos docs serve --port 8080
```

**Rationale:** Enterprise APIs need discoverable documentation for onboarding and integration.

---

## Summary

| # | Enhancement | Priority | Impact | Local Implementation |
|---|-------------|----------|--------|----------------------|
| 1 | End-to-End Encryption | P1 | Data security for sensitive workflows | `encrypt_sensitive_fields` / `decrypt_sensitive_fields` |
| 2 | Rate Limiting & Quotas | P1 | Resource protection in production | `RateLimiter` / `default_rate_limiter` |
| 3 | Workflow Dependency Chains | P1 | Ordered workflow pipelines | `WORKFLOW_DEPENDENCIES` / `start-workflow-chain` |
| 4 | Bulk Orchestration Management | P1 | Boardroom session lifecycle | `start-orchestration-group` / `get-group-status` / `stop-orchestration-group` |
| 5 | Agent Capability Matching | P2 | Dynamic agent selection | `find-agents` workflow |
| 6 | Orchestration Checkpointing | P2 | Durability for perpetual orchestrations | `checkpoint-orchestration` / `resume-orchestration` |
| 7 | Conditional Webhooks | P2 | Alert fatigue prevention | `register-conditional-webhook` / `evaluate_webhook_filter` |
| 8 | Audit Trail Tamper Detection | P2 | Regulatory integrity proof | `verify-audit-integrity` workflow |
| 9 | SDK Plugin Architecture | P3 | Extensibility without SDK changes | `use_middleware` / `_MIDDLEWARE` |
| 10 | Workflow Documentation Generation | P3 | API discoverability | `generate-api-docs` workflow |

---

*This document captures enhancement requests that emerged after integrating AOS Client SDK v5.0.0 into BusinessInfinity v5.0.0. Each enhancement represents a production-hardening gap or strategic capability for the Global Boardroom Network rollout. All 10 enhancements are implemented locally in BusinessInfinity until the SDK provides native support.*
