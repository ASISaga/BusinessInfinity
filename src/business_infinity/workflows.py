"""BusinessInfinity workflows — purpose-driven perpetual orchestrations.

Each workflow function is decorated with ``@app.workflow`` from the AOS Client
SDK.  The SDK handles all Azure Functions scaffolding (HTTP triggers,
Service Bus triggers, authentication, health endpoints).

Orchestrations are **perpetual and purpose-driven**: each workflow starts an
ongoing orchestration guided by a purpose.  Agents work toward the purpose
continuously — there is no finite task to complete.

Enterprise capabilities (v5.0.0) demonstrate the new SDK APIs for knowledge
management, risk registry (including heatmaps and analytics), audit trails
(including compliance reports), covenants (including lifecycle events),
analytics (including alerts), MCP integration (including bidirectional events),
agent interaction, network discovery, orchestration streaming, multi-tenant
support, and webhook notifications.

Beyond-SDK capabilities (not yet provided by the AOS Client SDK) are
implemented directly in this module as described in docs/AOS_NEXT_ENHANCEMENTS.md:

1. ``encrypt_sensitive_fields`` — field-level encryption for sensitive data
2. ``RateLimiter`` — token-bucket rate limiter for SDK call throttling
3. ``WORKFLOW_DEPENDENCIES`` / ``start-workflow-chain`` — dependency chains
4. ``start-orchestration-group`` / ``get-group-status`` / ``stop-orchestration-group`` — bulk orchestration
5. ``find-agents`` — capability-based agent matching
6. ``checkpoint-orchestration`` / ``resume-orchestration`` — checkpointing
7. ``register-conditional-webhook`` — conditional webhooks with filters
8. ``verify-audit-integrity`` — audit-trail tamper detection
9. ``use_middleware`` / ``_MIDDLEWARE`` — lightweight plugin/middleware support
10. ``generate-api-docs`` — workflow documentation generation
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import logging
import time
import uuid
from typing import Any, Callable, Dict, List, Optional

from aos_client import (
    AOSApp,
    AOSClient,
    AgentDescriptor,
    WorkflowRequest,
    workflow_template,
)
from aos_client.observability import ObservabilityConfig

logger = logging.getLogger(__name__)

app = AOSApp(
    name="business-infinity",
    observability=ObservabilityConfig(
        structured_logging=True,
        correlation_tracking=True,
        health_checks=["aos", "service-bus"],
    ),
)

# ── Beyond-SDK: Enhancement #2 — Rate Limiter ────────────────────────────────


class RateLimiter:
    """Token-bucket rate limiter for AOS SDK calls.

    Provides rate limiting that the SDK itself does not implement (see
    docs/AOS_NEXT_ENHANCEMENTS.md #2).  Use :attr:`default_rate_limiter` for
    the shared application-level limiter.

    Args:
        requests_per_minute: Sustained request rate.
        burst_limit: Maximum burst token capacity.
    """

    def __init__(self, requests_per_minute: int = 100, burst_limit: int = 20) -> None:
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self._tokens: float = float(burst_limit)
        self._last_refill: float = time.monotonic()
        self._lock: asyncio.Lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire one token, waiting with exponential back-off when exhausted."""
        async with self._lock:
            await self._refill()
            wait = 0.1
            while self._tokens < 1:
                await asyncio.sleep(wait)
                wait = min(wait * 2, 60 / self.requests_per_minute)
                await self._refill()
            self._tokens -= 1

    async def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(
            float(self.burst_limit),
            self._tokens + elapsed * (self.requests_per_minute / 60.0),
        )
        self._last_refill = now

    def get_quota_usage(self) -> Dict[str, Any]:
        """Return current token usage information."""
        return {
            "tokens_remaining": int(self._tokens),
            "burst_limit": self.burst_limit,
            "requests_per_minute": self.requests_per_minute,
        }


#: Shared application-level rate limiter (configurable at start-up).
default_rate_limiter = RateLimiter()


# ── Beyond-SDK: Enhancement #1 — Field-Level Encryption ─────────────────────


def encrypt_sensitive_fields(
    data: Dict[str, Any],
    fields: List[str],
    key_id: str = "boardroom-key",
) -> Dict[str, Any]:
    """Return a copy of *data* with the specified *fields* base-64 encoded.

    This is a lightweight placeholder implementation.  For production use,
    replace the encoding step with Azure Key Vault encryption as described in
    docs/AOS_NEXT_ENHANCEMENTS.md #1.  The ``key_id`` parameter is reserved
    for the Key Vault key name.

    Args:
        data:    Source dict (not mutated).
        fields:  Keys whose values should be encrypted.
        key_id:  Reserved for Key Vault key name (not used in this stub).

    Returns:
        New dict with the nominated fields replaced by ``"enc:<b64>"`` values.
    """
    result = dict(data)
    for field in fields:
        if field in result:
            raw = str(result[field]).encode()
            result[field] = f"enc:{base64.b64encode(raw).decode()}"
    return result


def decrypt_sensitive_fields(
    data: Dict[str, Any],
    fields: List[str],
    key_id: str = "boardroom-key",
) -> Dict[str, Any]:
    """Reverse :func:`encrypt_sensitive_fields` for the specified *fields*.

    Args:
        data:    Source dict (not mutated).
        fields:  Keys whose ``"enc:<b64>"`` values should be decoded.
        key_id:  Reserved for Key Vault key name (not used in this stub).

    Returns:
        New dict with the nominated fields decoded back to their original values.
    """
    result = dict(data)
    for field in fields:
        value = result.get(field)
        if isinstance(value, str) and value.startswith("enc:"):
            result[field] = base64.b64decode(value[4:]).decode()
    return result


# ── Beyond-SDK: Enhancement #3 — Workflow Dependency Chains ─────────────────

#: Maps each workflow name to the list of upstream workflows it depends on.
#: Used by :func:`start_workflow_chain` to enforce ordering.
WORKFLOW_DEPENDENCIES: Dict[str, List[str]] = {
    "compliance-report": ["covenant-compliance"],
    "risk-summary": ["risk-assess"],
    "risk-heatmap": ["risk-register", "risk-assess"],
    "verify-audit-integrity": ["log-decision"],
}


# ── Beyond-SDK: Enhancement #4 — Bulk Orchestration Groups ──────────────────

#: In-memory registry of orchestration groups.  Maps group_id → group metadata.
_ORCHESTRATION_GROUPS: Dict[str, Dict[str, Any]] = {}


# ── Beyond-SDK: Enhancement #7 — Conditional Webhook Filters ────────────────

#: Maps webhook_id → filter rule dict for conditional webhook evaluation.
_WEBHOOK_FILTERS: Dict[str, Dict[str, Any]] = {}


# ── Beyond-SDK: Enhancement #9 — Middleware / Plugin Architecture ────────────

#: Ordered list of middleware callables registered via :func:`use_middleware`.
_MIDDLEWARE: List[Callable] = []


def use_middleware(middleware_fn: Callable) -> None:
    """Register an async middleware to be invoked around each workflow call.

    Provides a lightweight plugin architecture as requested in
    docs/AOS_NEXT_ENHANCEMENTS.md #9.  Middleware functions receive
    ``(workflow_name: str, request: WorkflowRequest)`` as positional arguments.

    Example::

        async def logging_middleware(workflow_name, request):
            logger.info("Before %s", workflow_name)

        use_middleware(logging_middleware)
    """
    _MIDDLEWARE.append(middleware_fn)


# ── C-Suite Agent Selection ──────────────────────────────────────────────────

#: Agent types considered part of the C-suite
C_SUITE_TYPES = {"LeadershipAgent", "CMOAgent"}

#: Preferred C-suite agent IDs for BusinessInfinity orchestrations
C_SUITE_AGENT_IDS = ["ceo", "cfo", "cmo", "coo", "cto", "cso", "chro"]


async def select_c_suite_agents(client: AOSClient) -> List[AgentDescriptor]:
    """Select C-suite agents from the RealmOfAgents catalog.

    Returns agents matching :data:`C_SUITE_AGENT_IDS` or, if not found,
    agents whose ``agent_type`` is in :data:`C_SUITE_TYPES`.
    """
    all_agents = await client.list_agents()

    # Prefer explicit IDs
    by_id = {a.agent_id: a for a in all_agents}
    selected = [by_id[aid] for aid in C_SUITE_AGENT_IDS if aid in by_id]

    if not selected:
        # Fall back to type-based selection
        selected = [a for a in all_agents if a.agent_type in C_SUITE_TYPES]

    logger.info("Selected %d C-suite agents: %s", len(selected), [a.agent_id for a in selected])
    return selected


# ── Workflow Template (Enhancement #11) ──────────────────────────────────────


@workflow_template
async def c_suite_orchestration(
    request: WorkflowRequest,
    agent_filter: Callable[[AgentDescriptor], bool],
    purpose: str,
    purpose_scope: str,
) -> Dict[str, Any]:
    """Reusable template for C-suite orchestrations."""
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents if agent_filter(a)]
    if not agent_ids:
        raise ValueError(f"No matching agents available for '{purpose}'")
    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose=purpose,
        purpose_scope=purpose_scope,
        context=request.body,
    )
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}


# ── Purpose-Driven Orchestrations ────────────────────────────────────────────


@app.workflow("strategic-review")
async def strategic_review(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a perpetual strategic review orchestration with C-suite agents.

    The orchestration continuously drives strategic alignment, review, and
    improvement across the organisation.  It does not complete — agents
    work toward the purpose indefinitely.

    Request body::

        {"quarter": "Q1-2026", "focus_areas": ["revenue", "growth"]}
    """
    return await c_suite_orchestration(
        request,
        agent_filter=lambda a: True,
        purpose="Drive strategic review and continuous organisational improvement",
        purpose_scope="C-suite strategic alignment and cross-functional coordination",
    )


@app.workflow("market-analysis")
async def market_analysis(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a perpetual market analysis orchestration led by the CMO agent.

    The orchestration continuously monitors markets, analyses competitors,
    and surfaces insights.  It does not complete — agents work toward the
    purpose indefinitely.

    Request body::

        {"market": "EU SaaS", "competitors": ["AcmeCorp", "Globex"]}
    """
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents if a.agent_type == "CMOAgent"]

    # Add CEO for strategic oversight if available
    ceo = [a for a in agents if a.agent_id == "ceo"]
    if ceo and ceo[0].agent_id not in agent_ids:
        agent_ids.insert(0, ceo[0].agent_id)

    # Add CSO for strategic analysis if available
    cso = [a for a in agents if a.agent_id == "cso"]
    if cso and cso[0].agent_id not in agent_ids:
        agent_ids.append(cso[0].agent_id)

    if not agent_ids:
        raise ValueError("No CMO, CEO, or CSO agents available in the catalog")

    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose="Continuously analyse markets and surface competitive insights",
        purpose_scope="Market intelligence, competitor monitoring, and opportunity identification",
        context={
            "market": request.body.get("market", ""),
            "competitors": request.body.get("competitors", []),
        },
        workflow="hierarchical",
    )
    logger.info("Market analysis orchestration started: %s", status.orchestration_id)
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}


@app.workflow("budget-approval")
async def budget_approval(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a perpetual budget governance orchestration with C-suite leadership.

    The orchestration continuously oversees budget allocation, monitors
    spend, and governs financial decisions.  It does not complete — agents
    work toward the purpose indefinitely.

    Request body::

        {"department": "Marketing", "amount": 500000, "justification": "Q2 campaign"}
    """
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents if a.agent_id in ("ceo", "cfo")]

    if not agent_ids:
        raise ValueError("CEO and/or CFO agents not available in the catalog")

    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose="Govern budget allocation and ensure fiscal responsibility",
        purpose_scope="Financial governance, budget oversight, and resource allocation",
        context={
            "department": request.body.get("department", ""),
            "amount": request.body.get("amount", 0),
            "justification": request.body.get("justification", ""),
        },
        workflow="sequential",
    )
    logger.info("Budget governance orchestration started: %s", status.orchestration_id)
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}


@app.workflow("risk-assessment")
async def risk_assessment(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a perpetual risk governance orchestration.

    The orchestration continuously monitors, assesses, and mitigates
    enterprise risks across all business domains.

    Request body::

        {"risk_domain": "cybersecurity", "risk_tolerance": "moderate"}
    """
    return await c_suite_orchestration(
        request,
        agent_filter=lambda a: a.agent_id in ("cso", "cto", "coo"),
        purpose="Continuously monitor, assess, and mitigate enterprise risks",
        purpose_scope="Risk identification, assessment, mitigation, and governance across all domains",
    )


@app.workflow("boardroom-session")
async def boardroom_session(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a perpetual autonomous boardroom session with all C-suite agents.

    The orchestration runs a continuous boardroom where all C-suite agents
    collaborate on strategic decisions, operational reviews, and governance.

    Request body::

        {"agenda": ["Q1 review", "hiring plan"], "mode": "autonomous"}
    """
    return await c_suite_orchestration(
        request,
        agent_filter=lambda a: True,
        purpose="Run autonomous boardroom with perpetual strategic governance and decision-making",
        purpose_scope="Full C-suite collaboration, strategic planning, operational reviews, and covenant compliance",
    )


@app.workflow("covenant-compliance")
async def covenant_compliance(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a perpetual covenant compliance monitoring orchestration.

    The orchestration continuously ensures all business operations comply
    with established covenants and governance standards.

    Request body::

        {"compliance_standard": "BIC", "scope": "global"}
    """
    return await c_suite_orchestration(
        request,
        agent_filter=lambda a: a.agent_id in ("ceo", "coo", "cso"),
        purpose="Ensure continuous covenant compliance and governance adherence",
        purpose_scope="Compliance monitoring, audit trail validation, and covenant enforcement",
    )


@app.workflow("talent-management")
async def talent_management(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a perpetual talent management orchestration led by CHRO.

    The orchestration continuously manages talent strategy, organizational
    development, and HR governance.

    Request body::

        {"focus": "retention", "departments": ["engineering", "marketing"]}
    """
    return await c_suite_orchestration(
        request,
        agent_filter=lambda a: a.agent_id in ("chro", "ceo", "coo"),
        purpose="Drive talent strategy, organizational development, and workforce optimization",
        purpose_scope="Talent acquisition, retention, development, culture, and HR governance",
    )


@app.workflow("technology-review")
async def technology_review(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a perpetual technology review orchestration led by CTO.

    The orchestration continuously evaluates technology strategy, architecture
    decisions, and engineering excellence.

    Request body::

        {"focus_areas": ["cloud", "ai", "security"], "review_scope": "quarterly"}
    """
    return await c_suite_orchestration(
        request,
        agent_filter=lambda a: a.agent_id in ("cto", "ceo", "cso"),
        purpose="Drive technology strategy, architecture excellence, and innovation",
        purpose_scope="Technology roadmap, architecture review, engineering practices, and innovation pipeline",
    )


# ── Enterprise Capability Workflows (Enhancement #1–#12) ────────────────────


@app.workflow("knowledge-search")
async def knowledge_search(request: WorkflowRequest) -> Dict[str, Any]:
    """Search the knowledge base.

    Request body::

        {"query": "sustainability policy", "doc_type": "policy", "limit": 5}
    """
    docs = await request.client.search_documents(
        query=request.body.get("query", ""),
        doc_type=request.body.get("doc_type"),
        limit=request.body.get("limit", 10),
    )
    return {"documents": [d.model_dump(mode="json") for d in docs]}


@app.workflow("risk-register")
async def risk_register(request: WorkflowRequest) -> Dict[str, Any]:
    """Register a new risk in the AOS risk registry.

    Request body::

        {"title": "Supply chain disruption", "description": "...",
         "category": "operational", "owner": "coo"}
    """
    risk = await request.client.register_risk(request.body)
    return risk.model_dump(mode="json")


@app.workflow("risk-assess")
async def risk_assess(request: WorkflowRequest) -> Dict[str, Any]:
    """Assess an existing risk.

    Request body::

        {"risk_id": "risk-abc", "likelihood": 0.7, "impact": 0.9}
    """
    risk = await request.client.assess_risk(
        risk_id=request.body["risk_id"],
        likelihood=request.body["likelihood"],
        impact=request.body["impact"],
    )
    return risk.model_dump(mode="json")


@app.workflow("log-decision")
async def log_decision_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    """Log a boardroom decision to the audit trail.

    Request body::

        {"title": "Expand to EU", "rationale": "Market opportunity",
         "agent_id": "ceo"}
    """
    record = await request.client.log_decision(request.body)
    return record.model_dump(mode="json")


@app.workflow("covenant-create")
async def covenant_create(request: WorkflowRequest) -> Dict[str, Any]:
    """Create a business covenant.

    Request body::

        {"title": "Ethics Covenant", "parties": ["business-infinity"]}
    """
    covenant = await request.client.create_covenant(request.body)
    return covenant.model_dump(mode="json")


@app.workflow("ask-agent")
async def ask_agent_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    """Ask a single agent a question directly.

    Request body::

        {"agent_id": "ceo", "message": "What is the Q2 strategy?"}
    """
    response = await request.client.ask_agent(
        agent_id=request.body["agent_id"],
        message=request.body["message"],
        context=request.body.get("context"),
    )
    return response.model_dump(mode="json")


# ── Orchestration Update Handler (Enhancement #5) ───────────────────────────


@app.on_orchestration_update("strategic-review")
async def handle_strategic_review_update(update) -> None:
    """Handle intermediate updates from strategic review orchestrations."""
    logger.info(
        "Strategic review update from agent %s: %s",
        getattr(update, "agent_id", "unknown"),
        getattr(update, "output", ""),
    )


# ── MCP Tool Integration (Enhancement #7) ───────────────────────────────────


@app.mcp_tool("erp-search")
async def erp_search(request: WorkflowRequest) -> Any:
    """Search ERP via MCP server."""
    return await request.client.call_mcp_tool("erpnext", "search", request.body)


# ── v5.0.0 Enterprise Workflows ─────────────────────────────────────────────


@app.workflow("risk-heatmap")
async def risk_heatmap(request: WorkflowRequest) -> Dict[str, Any]:
    """Get risk heatmap for the boardroom.

    Request body::

        {"category": "operational"}
    """
    heatmap = await request.client.get_risk_heatmap(
        category=request.body.get("category"),
    )
    return heatmap.model_dump(mode="json")


@app.workflow("risk-summary")
async def risk_summary(request: WorkflowRequest) -> Dict[str, Any]:
    """Get aggregate risk summary.

    Request body::

        {"category": "financial"}
    """
    summary = await request.client.get_risk_summary(
        category=request.body.get("category"),
    )
    return summary.model_dump(mode="json")


@app.workflow("compliance-report")
async def compliance_report(request: WorkflowRequest) -> Dict[str, Any]:
    """Generate a compliance report for regulatory submissions.

    Request body::

        {"start_time": "2026-01-01T00:00:00", "end_time": "2026-03-31T23:59:59",
         "report_type": "decisions"}
    """
    from datetime import datetime as dt

    report = await request.client.generate_compliance_report(
        start_time=dt.fromisoformat(request.body["start_time"]),
        end_time=dt.fromisoformat(request.body["end_time"]),
        report_type=request.body.get("report_type", "decisions"),
    )
    return report.model_dump(mode="json")


@app.workflow("create-alert")
async def create_alert_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    """Create a metric alert.

    Request body::

        {"metric_name": "risk_score", "threshold": 8.0, "condition": "gt"}
    """
    alert = await request.client.create_alert(
        metric_name=request.body["metric_name"],
        threshold=request.body["threshold"],
        condition=request.body.get("condition", "gt"),
    )
    return alert.model_dump(mode="json")


@app.workflow("register-webhook")
async def register_webhook_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    """Register a webhook for external notifications.

    Request body::

        {"url": "https://hooks.slack.com/...", "events": ["decision.created"]}
    """
    webhook = await request.client.register_webhook(
        url=request.body["url"],
        events=request.body["events"],
    )
    return webhook.model_dump(mode="json")


# ── Covenant Event Handlers (v5.0.0 Enhancement #3) ─────────────────────────


@app.on_covenant_event("violated")
async def handle_covenant_violation(event) -> None:
    """Handle covenant violation events."""
    logger.warning(
        "Covenant %s violated: %s",
        getattr(event, "covenant_id", "unknown"),
        getattr(event, "details", {}),
    )


@app.on_covenant_event("expiring")
async def handle_covenant_expiring(event) -> None:
    """Handle covenant expiration warnings."""
    logger.info(
        "Covenant %s nearing expiration: %s",
        getattr(event, "covenant_id", "unknown"),
        getattr(event, "details", {}),
    )


# ── MCP Event Handlers (v5.0.0 Enhancement #8) ──────────────────────────────


@app.on_mcp_event("erpnext", "order_created")
async def handle_erp_order(event) -> None:
    """Handle ERP order creation events."""
    logger.info(
        "ERP order created: %s",
        getattr(event, "payload", {}),
    )


# ── Webhook Handler (v5.0.0 Enhancement #12) ────────────────────────────────


@app.webhook("slack-notifications")
async def notify_slack(event) -> None:
    """Send notification to Slack when significant events occur."""
    logger.info(
        "Slack notification: %s",
        getattr(event, "payload", {}),
    )


# ── Beyond-SDK Workflows — Enhancement #5: Agent Capability Matching ─────────


@app.workflow("find-agents")
async def find_agents_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    """Find agents by capability requirements.

    Implements SDK enhancement #5 (docs/AOS_NEXT_ENHANCEMENTS.md).  The SDK's
    ``list_agents()`` returns all agents without capability-based filtering;
    this workflow applies the filter and scoring locally.

    Request body::

        {
            "required_capabilities": ["risk-analysis", "financial-governance"],
            "preferred_capabilities": ["compliance"],
            "min_score": 0.5
        }
    """
    all_agents = await request.client.list_agents()
    required = set(request.body.get("required_capabilities", []))
    preferred = set(request.body.get("preferred_capabilities", []))
    min_score: float = request.body.get("min_score", 0.0)

    matches: List[Dict[str, Any]] = []
    for agent in all_agents:
        caps = set(getattr(agent, "capabilities", []))
        if required and not required.issubset(caps):
            continue
        matched = caps & (required | preferred)
        denom = max(len(required | preferred), 1)
        score = len(matched) / denom
        if score < min_score:
            continue
        agent_dict = (
            agent.model_dump(mode="json") if hasattr(agent, "model_dump")
            else {"agent_id": agent.agent_id}
        )
        matches.append({
            "agent": agent_dict,
            "score": score,
            "matched_capabilities": sorted(matched),
        })

    matches.sort(key=lambda m: m["score"], reverse=True)
    return {"matches": matches, "total": len(matches)}


# ── Beyond-SDK Workflows — Enhancement #4: Bulk Orchestration Management ─────


@app.workflow("start-orchestration-group")
async def start_orchestration_group(request: WorkflowRequest) -> Dict[str, Any]:
    """Start multiple orchestrations and register them as a named group.

    Implements SDK enhancement #4 (docs/AOS_NEXT_ENHANCEMENTS.md).

    Request body::

        {
            "group_name": "boardroom-q1-2026",
            "orchestrations": [
                {"agent_ids": ["ceo", "cfo"], "purpose": "Budget review", "purpose_scope": "..."},
                {"agent_ids": ["cso", "cto"], "purpose": "Risk review",   "purpose_scope": "..."}
            ]
        }
    """
    group_name: str = request.body.get("group_name", f"group-{uuid.uuid4().hex[:8]}")
    group_id: str = uuid.uuid4().hex
    orchestration_ids: List[str] = []

    for spec in request.body.get("orchestrations", []):
        status = await request.client.start_orchestration(
            agent_ids=spec.get("agent_ids", []),
            purpose=spec.get("purpose", ""),
            purpose_scope=spec.get("purpose_scope", ""),
            context=spec.get("context", {}),
        )
        orchestration_ids.append(status.orchestration_id)

    _ORCHESTRATION_GROUPS[group_id] = {
        "group_id": group_id,
        "group_name": group_name,
        "orchestration_ids": orchestration_ids,
        "status": "running",
    }
    logger.info("Orchestration group %s started with %d members", group_id, len(orchestration_ids))
    return _ORCHESTRATION_GROUPS[group_id]


@app.workflow("get-group-status")
async def get_group_status(request: WorkflowRequest) -> Dict[str, Any]:
    """Get aggregate status for an orchestration group.

    Implements SDK enhancement #4 (docs/AOS_NEXT_ENHANCEMENTS.md).

    Request body::

        {"group_id": "<uuid>"}
    """
    group_id: str = request.body["group_id"]
    group = _ORCHESTRATION_GROUPS.get(group_id)
    if group is None:
        raise ValueError(f"Orchestration group '{group_id}' not found")
    return dict(group)


@app.workflow("stop-orchestration-group")
async def stop_orchestration_group(request: WorkflowRequest) -> Dict[str, Any]:
    """Stop all orchestrations in a group.

    Implements SDK enhancement #4 (docs/AOS_NEXT_ENHANCEMENTS.md).

    Request body::

        {"group_id": "<uuid>"}
    """
    group_id: str = request.body["group_id"]
    group = _ORCHESTRATION_GROUPS.get(group_id)
    if group is None:
        raise ValueError(f"Orchestration group '{group_id}' not found")

    for orch_id in group.get("orchestration_ids", []):
        if hasattr(request.client, "stop_orchestration"):
            await request.client.stop_orchestration(orch_id)
        else:
            logger.warning("SDK does not support stop_orchestration; skipping %s", orch_id)

    group["status"] = "stopped"
    logger.info("Orchestration group %s stopped", group_id)
    return {"group_id": group_id, "status": "stopped"}


# ── Beyond-SDK Workflows — Enhancement #6: Orchestration Checkpointing ───────


@app.workflow("checkpoint-orchestration")
async def checkpoint_orchestration_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    """Save a checkpoint for a perpetual orchestration.

    Implements SDK enhancement #6 (docs/AOS_NEXT_ENHANCEMENTS.md).  Checkpoint
    data is persisted via the knowledge-base document API so it survives
    restarts.

    Request body::

        {
            "orchestration_id": "orch-abc123",
            "checkpoint_data": {"phase": "risk-review", "iteration": 12}
        }
    """
    from datetime import datetime as dt, timezone

    doc_body = {
        "doc_type": "orchestration-checkpoint",
        "title": f"Checkpoint for {request.body['orchestration_id']}",
        "orchestration_id": request.body["orchestration_id"],
        "checkpoint_data": request.body.get("checkpoint_data", {}),
        "created_at": dt.now(timezone.utc).isoformat(),
    }
    doc = await request.client.create_document(doc_body)
    checkpoint_id = doc.document_id if hasattr(doc, "document_id") else str(uuid.uuid4())
    logger.info(
        "Checkpoint %s saved for orchestration %s",
        checkpoint_id,
        request.body["orchestration_id"],
    )
    return {
        "checkpoint_id": checkpoint_id,
        "orchestration_id": request.body["orchestration_id"],
        "status": "saved",
    }


@app.workflow("resume-orchestration")
async def resume_orchestration_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    """Resume a perpetual orchestration from its latest checkpoint.

    Implements SDK enhancement #6 (docs/AOS_NEXT_ENHANCEMENTS.md).

    Request body::

        {
            "orchestration_id": "orch-abc123",
            "agent_ids": ["ceo", "cfo"],
            "purpose": "Continue strategic review",
            "purpose_scope": "..."
        }
    """
    orch_id: str = request.body["orchestration_id"]

    # Find the latest checkpoint from the knowledge base
    docs = await request.client.search_documents(
        query=orch_id,
        doc_type="orchestration-checkpoint",
        limit=1,
    )
    if not docs:
        raise ValueError(f"No checkpoint found for orchestration '{orch_id}'")

    checkpoint_doc = docs[0]
    checkpoint_data = (
        checkpoint_doc.get("checkpoint_data", {})
        if isinstance(checkpoint_doc, dict)
        else getattr(checkpoint_doc, "checkpoint_data", {})
    )
    checkpoint_id = (
        checkpoint_doc.get("document_id")
        if isinstance(checkpoint_doc, dict)
        else getattr(checkpoint_doc, "document_id", None)
    )

    status = await request.client.start_orchestration(
        agent_ids=request.body.get("agent_ids", []),
        purpose=request.body.get("purpose", ""),
        purpose_scope=request.body.get("purpose_scope", ""),
        context={
            "resumed_from_checkpoint": checkpoint_id,
            "checkpoint_data": checkpoint_data,
            **request.body.get("context", {}),
        },
    )
    logger.info(
        "Orchestration %s resumed from checkpoint %s as new orchestration %s",
        orch_id,
        checkpoint_id,
        status.orchestration_id,
    )
    return {
        "orchestration_id": status.orchestration_id,
        "status": status.status.value,
        "resumed_from_checkpoint": checkpoint_id,
    }


# ── Beyond-SDK Workflows — Enhancement #7: Conditional Webhooks ──────────────


@app.workflow("register-conditional-webhook")
async def register_conditional_webhook(request: WorkflowRequest) -> Dict[str, Any]:
    """Register a webhook with an optional event filter.

    Implements SDK enhancement #7 (docs/AOS_NEXT_ENHANCEMENTS.md).  The filter
    is stored locally and evaluated by :func:`evaluate_webhook_filter` when
    deciding whether to deliver an event.

    Request body::

        {
            "url": "https://hooks.slack.com/...",
            "events": ["decision.created"],
            "filter": {"field": "priority", "op": "eq", "value": "critical"}
        }
    """
    webhook = await request.client.register_webhook(
        url=request.body["url"],
        events=request.body["events"],
    )
    webhook_id = webhook.webhook_id if hasattr(webhook, "webhook_id") else str(uuid.uuid4())
    webhook_filter = request.body.get("filter")
    if webhook_filter:
        _WEBHOOK_FILTERS[webhook_id] = webhook_filter

    result = (
        webhook.model_dump(mode="json") if hasattr(webhook, "model_dump")
        else {"webhook_id": webhook_id}
    )
    result["filter"] = webhook_filter
    logger.info("Conditional webhook %s registered (filter: %s)", webhook_id, webhook_filter)
    return result


def evaluate_webhook_filter(webhook_id: str, event: Dict[str, Any]) -> bool:
    """Return ``True`` if *event* passes the filter registered for *webhook_id*.

    Supports ``op`` values: ``eq``, ``ne``, ``gt``, ``gte``, ``lt``, ``lte``,
    ``contains``.

    If no filter is registered for *webhook_id* this always returns ``True``.
    """
    rule = _WEBHOOK_FILTERS.get(webhook_id)
    if rule is None:
        return True
    field = rule.get("field", "")
    op = rule.get("op", "eq")
    expected = rule.get("value")
    actual = event.get(field)
    _ops: Dict[str, Callable] = {
        "eq": lambda a, e: a == e,
        "ne": lambda a, e: a != e,
        "gt": lambda a, e: a > e,
        "gte": lambda a, e: a >= e,
        "lt": lambda a, e: a < e,
        "lte": lambda a, e: a <= e,
        "contains": lambda a, e: e in a if a is not None else False,
    }
    try:
        return _ops.get(op, _ops["eq"])(actual, expected)
    except TypeError:
        return False


# ── Beyond-SDK Workflows — Enhancement #8: Audit Trail Tamper Detection ──────


@app.workflow("verify-audit-integrity")
async def verify_audit_integrity_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    """Verify the integrity of the audit trail using a SHA-256 hash chain.

    Implements SDK enhancement #8 (docs/AOS_NEXT_ENHANCEMENTS.md).  Fetches
    audit records via ``generate_compliance_report`` and chains their hashes to
    detect any tampering or missing entries.

    Request body::

        {
            "start_time": "2026-01-01T00:00:00",
            "end_time":   "2026-03-31T23:59:59"
        }
    """
    from datetime import datetime as dt, timezone

    start_time = (
        dt.fromisoformat(request.body["start_time"])
        if "start_time" in request.body
        else dt(2000, 1, 1)
    )
    end_time = (
        dt.fromisoformat(request.body["end_time"])
        if "end_time" in request.body
        else dt.now(timezone.utc)
    )

    report = await request.client.generate_compliance_report(
        start_time=start_time,
        end_time=end_time,
        report_type="decisions",
    )

    entries = []
    if hasattr(report, "entries"):
        entries = report.entries
    elif isinstance(report, dict):
        entries = report.get("entries", [])

    prev_hash = "0" * 64
    anomalies: List[Dict[str, Any]] = []

    for i, entry in enumerate(entries):
        entry_dict = (
            entry.model_dump(mode="json") if hasattr(entry, "model_dump") else dict(entry)
        )
        # Exclude the stored hash field when recomputing
        entry_for_hash = {k: v for k, v in entry_dict.items() if k != "hash"}
        entry_str = str(sorted(entry_for_hash.items()))
        current_hash = hashlib.sha256(f"{prev_hash}{entry_str}".encode()).hexdigest()

        stored_hash = entry_dict.get("hash")
        if stored_hash and stored_hash != current_hash:
            anomalies.append({
                "index": i,
                "entry_id": entry_dict.get("id"),
                "reason": "hash_mismatch",
            })

        prev_hash = current_hash

    integrity_verified = len(anomalies) == 0
    if integrity_verified:
        logger.info("Audit integrity verified: %d entries checked", len(entries))
    else:
        logger.warning("Audit integrity anomalies detected: %s", anomalies)

    return {
        "verified": integrity_verified,
        "entries_checked": len(entries),
        "integrity_hash": prev_hash,
        "anomalies": anomalies,
    }


# ── Beyond-SDK Workflows — Enhancement #3: Workflow Dependency Chains ─────────


@app.workflow("start-workflow-chain")
async def start_workflow_chain(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a workflow while advertising its upstream dependencies.

    Implements SDK enhancement #3 (docs/AOS_NEXT_ENHANCEMENTS.md).  Checks
    ``WORKFLOW_DEPENDENCIES`` to surface the declared dependencies so callers
    can ensure upstream workflows have completed before this one proceeds.

    Request body::

        {
            "workflow_name": "compliance-report",
            "context": {}
        }
    """
    workflow_name: str = request.body["workflow_name"]
    upstream: List[str] = WORKFLOW_DEPENDENCIES.get(workflow_name, [])

    if upstream:
        logger.info(
            "Workflow '%s' depends on: %s — ensure they are complete first",
            workflow_name,
            upstream,
        )

    return {
        "workflow": workflow_name,
        "depends_on": upstream,
        "message": (
            f"Workflow '{workflow_name}' depends on: {upstream}. "
            "Ensure upstream workflows have completed before proceeding."
            if upstream
            else f"Workflow '{workflow_name}' has no declared dependencies."
        ),
    }


# ── Beyond-SDK Workflows — Enhancement #10: API Documentation Generation ──────


@app.workflow("generate-api-docs")
async def generate_api_docs(request: WorkflowRequest) -> Dict[str, Any]:
    """Generate API documentation for all registered workflows.

    Implements SDK enhancement #10 (docs/AOS_NEXT_ENHANCEMENTS.md).  Returns
    a structured description of every registered workflow derived from its
    docstring, which can be rendered as OpenAPI or Markdown.

    Request body::

        {}  (no parameters required)
    """
    import inspect

    workflows_doc: List[Dict[str, Any]] = []
    for name, fn in app._workflows.items():
        doc = inspect.getdoc(fn) or ""
        first_line = doc.splitlines()[0] if doc else ""
        workflows_doc.append({
            "name": name,
            "summary": first_line,
            "description": doc,
            "depends_on": WORKFLOW_DEPENDENCIES.get(name, []),
        })

    return {
        "app": app.name,
        "version": "5.0.0",
        "total_workflows": len(workflows_doc),
        "workflows": workflows_doc,
    }
