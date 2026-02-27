"""Health and analytics workflows for BusinessInfinity.

Provides a liveness health check and a KPI / agent-summary analytics
endpoint so load balancers and dashboards can monitor the service.
"""

from __future__ import annotations

from typing import Any, Dict

from aos_client import WorkflowRequest

from ._app import C_SUITE_AGENT_IDS, app, logger


@app.workflow("system-health")
async def system_health(request: WorkflowRequest) -> Dict[str, Any]:
    """Return a health summary for the BusinessInfinity instance.

    Checks agent reachability via ``list_agents`` and reports basic liveness
    so load balancers and monitoring tools can verify the service.

    Request body::

        {}
    """
    from datetime import datetime as dt, timezone

    try:
        all_agents = await request.client.list_agents()
        agent_count = len(all_agents)
        status = "healthy"
    except Exception as exc:  # noqa: BLE001
        logger.warning("Health check agent query failed: %s", exc)
        agent_count = 0
        status = "degraded"

    return {
        "service": "BusinessInfinity",
        "status": status,
        "version": "5.0.0",
        "agents_active": agent_count,
        "timestamp": dt.now(timezone.utc).isoformat(),
    }


@app.workflow("business-analytics")
async def business_analytics(request: WorkflowRequest) -> Dict[str, Any]:
    """Return business KPIs and performance metrics.

    Queries the SDK analytics / KPI dashboard and augments with a
    C-suite agent summary so stakeholders have a single analytics view.

    Request body::

        {"include_kpis": true, "include_agent_summary": true}
    """
    include_kpis: bool = request.body.get("include_kpis", True)
    include_agent_summary: bool = request.body.get("include_agent_summary", True)

    result: Dict[str, Any] = {}

    if include_kpis and hasattr(request.client, "get_kpi_dashboard"):
        dashboard = await request.client.get_kpi_dashboard()
        result["kpi_dashboard"] = (
            dashboard.model_dump(mode="json") if hasattr(dashboard, "model_dump") else dashboard
        )

    if include_kpis and hasattr(request.client, "get_metrics"):
        metrics = await request.client.get_metrics()
        result["metrics"] = (
            [m.model_dump(mode="json") if hasattr(m, "model_dump") else m for m in metrics]
            if isinstance(metrics, list)
            else metrics
        )

    if include_agent_summary:
        agents = await request.client.list_agents()
        result["agent_summary"] = {
            "total_agents": len(agents),
            "c_suite_agents": [
                a.agent_id for a in agents
                if getattr(a, "agent_id", "") in C_SUITE_AGENT_IDS
            ],
        }

    return result
