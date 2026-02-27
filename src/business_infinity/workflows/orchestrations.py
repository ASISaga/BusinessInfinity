"""Purpose-driven perpetual orchestrations for BusinessInfinity.

The **boardroom session** is the primary perpetual orchestration — a continuous
autonomous boardroom where all C-suite agents collaborate on strategic decisions,
operational reviews, and governance indefinitely.  All other orchestrations are
specialised sub-sessions that can be initiated from within the boardroom or
independently.

Each workflow starts an ongoing orchestration guided by a purpose.  Agents
work toward the purpose continuously — there is no finite task to complete.
"""

from __future__ import annotations

from typing import Any, Dict, List

from aos_client import AgentDescriptor, WorkflowRequest

from ._app import app, c_suite_orchestration, logger, select_c_suite_agents


# ── Primary Perpetual Orchestration ──────────────────────────────────────────


@app.workflow("boardroom-session")
async def boardroom_session(request: WorkflowRequest) -> Dict[str, Any]:
    """Start the primary perpetual autonomous boardroom session.

    This is the central orchestration of BusinessInfinity.  The boardroom
    runs continuously — all C-suite agents collaborate on strategic decisions,
    operational reviews, and governance indefinitely.  All other orchestrations
    originate from, or feed back into, the boardroom.

    Request body::

        {"agenda": ["Q1 review", "hiring plan"], "mode": "autonomous"}
    """
    return await c_suite_orchestration(
        request,
        agent_filter=lambda a: True,
        purpose="Run autonomous boardroom with perpetual strategic governance and decision-making",
        purpose_scope="Full C-suite collaboration, strategic planning, operational reviews, and covenant compliance",
    )


# ── Specialised Perpetual Orchestrations ─────────────────────────────────────


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
