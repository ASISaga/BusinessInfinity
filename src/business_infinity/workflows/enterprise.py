"""Enterprise SDK capability workflows and event/MCP/webhook handlers.

Covers knowledge management, risk registry, audit trail, covenant management,
direct agent interaction, analytics, MCP integration, and real-time event
handlers — all backed by the AOS Client SDK v5.0.0.
"""

from __future__ import annotations

from typing import Any, Dict

from aos_client import WorkflowRequest

from ._app import app, logger


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


# ── Orchestration Update Handlers ───────────────────────────────────────────


@app.on_orchestration_update("strategic-review")
async def handle_strategic_review_update(update) -> None:
    """Handle intermediate updates from strategic review orchestrations."""
    logger.info(
        "Strategic review update from agent %s: %s",
        getattr(update, "agent_id", "unknown"),
        getattr(update, "output", ""),
    )


@app.on_orchestration_update("boardroom-session")
async def handle_boardroom_session_update(update) -> None:
    """Handle intermediate updates from boardroom session orchestrations."""
    logger.info(
        "Boardroom session update from agent %s: %s",
        getattr(update, "agent_id", "unknown"),
        getattr(update, "output", ""),
    )


@app.on_orchestration_update("create-conversation")
async def handle_boardroom_conversation_update(update) -> None:
    """Handle intermediate updates from boardroom conversation orchestrations."""
    logger.info(
        "Boardroom conversation update from agent %s: %s",
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
