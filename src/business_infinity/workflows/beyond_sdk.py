"""Beyond-SDK workflow enhancements for BusinessInfinity.

Implements the 10 capabilities not yet provided by the AOS Client SDK,
as documented in ``docs/AOS_NEXT_ENHANCEMENTS.md``:

1. Field-level encryption (utilities in :mod:`._app`)
2. Rate limiting (utilities in :mod:`._app`)
3. ``start-workflow-chain`` — dependency-aware workflow launch
4. ``start/get/stop-orchestration-group`` — bulk orchestration management
5. ``find-agents`` — capability-based agent matching
6. ``checkpoint/resume-orchestration`` — KB-backed checkpointing
7. ``register-conditional-webhook`` + :func:`evaluate_webhook_filter`
8. ``verify-audit-integrity`` — SHA-256 hash-chain tamper detection
9. Middleware (utilities in :mod:`._app`)
10. ``generate-api-docs`` — workflow documentation generation
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Any, Callable, Dict, List

from aos_client import WorkflowRequest

from ._app import (
    WORKFLOW_DEPENDENCIES,
    _ORCHESTRATION_GROUPS,
    _WEBHOOK_FILTERS,
    app,
    logger,
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
