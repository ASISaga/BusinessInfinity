"""BusinessInfinity workflows — purpose-driven perpetual orchestrations.

Each workflow function is decorated with ``@app.workflow`` from the AOS Client
SDK.  The SDK handles all Azure Functions scaffolding (HTTP triggers,
Service Bus triggers, authentication, health endpoints).

Orchestrations are **perpetual and purpose-driven**: each workflow starts an
ongoing orchestration guided by a purpose.  Agents work toward the purpose
continuously — there is no finite task to complete.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from aos_client import AOSApp, AOSClient, AgentDescriptor, WorkflowRequest

logger = logging.getLogger(__name__)

app = AOSApp(name="business-infinity")

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
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents]

    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose="Drive strategic review and continuous organisational improvement",
        purpose_scope="C-suite strategic alignment and cross-functional coordination",
        context={
            "quarter": request.body.get("quarter", "current"),
            "focus_areas": request.body.get("focus_areas", ["revenue", "growth", "efficiency"]),
        },
        workflow="collaborative",
    )
    logger.info("Strategic review orchestration started: %s", status.orchestration_id)
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}


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
    agents = await select_c_suite_agents(request.client)
    # Risk governance: CSO + CTO + COO
    agent_ids = [a.agent_id for a in agents if a.agent_id in ("cso", "cto", "coo")]

    if not agent_ids:
        # Fall back to all available C-suite
        agent_ids = [a.agent_id for a in agents]

    if not agent_ids:
        raise ValueError("No C-suite agents available for risk assessment")

    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose="Continuously monitor, assess, and mitigate enterprise risks",
        purpose_scope="Risk identification, assessment, mitigation, and governance across all domains",
        context={
            "risk_domain": request.body.get("risk_domain", "enterprise"),
            "risk_tolerance": request.body.get("risk_tolerance", "moderate"),
        },
        workflow="collaborative",
    )
    logger.info("Risk assessment orchestration started: %s", status.orchestration_id)
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}


@app.workflow("boardroom-session")
async def boardroom_session(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a perpetual autonomous boardroom session with all C-suite agents.

    The orchestration runs a continuous boardroom where all C-suite agents
    collaborate on strategic decisions, operational reviews, and governance.

    Request body::

        {"agenda": ["Q1 review", "hiring plan"], "mode": "autonomous"}
    """
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents]

    if not agent_ids:
        raise ValueError("No C-suite agents available for boardroom session")

    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose="Run autonomous boardroom with perpetual strategic governance and decision-making",
        purpose_scope="Full C-suite collaboration, strategic planning, operational reviews, and covenant compliance",
        context={
            "agenda": request.body.get("agenda", []),
            "mode": request.body.get("mode", "autonomous"),
        },
        workflow="collaborative",
    )
    logger.info("Boardroom session orchestration started: %s", status.orchestration_id)
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}


@app.workflow("covenant-compliance")
async def covenant_compliance(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a perpetual covenant compliance monitoring orchestration.

    The orchestration continuously ensures all business operations comply
    with established covenants and governance standards.

    Request body::

        {"compliance_standard": "BIC", "scope": "global"}
    """
    agents = await select_c_suite_agents(request.client)
    # Compliance: CEO + COO + CSO
    agent_ids = [a.agent_id for a in agents if a.agent_id in ("ceo", "coo", "cso")]

    if not agent_ids:
        agent_ids = [a.agent_id for a in agents]

    if not agent_ids:
        raise ValueError("No agents available for covenant compliance monitoring")

    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose="Ensure continuous covenant compliance and governance adherence",
        purpose_scope="Compliance monitoring, audit trail validation, and covenant enforcement",
        context={
            "compliance_standard": request.body.get("compliance_standard", "BIC"),
            "scope": request.body.get("scope", "global"),
        },
        workflow="collaborative",
    )
    logger.info("Covenant compliance orchestration started: %s", status.orchestration_id)
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}


@app.workflow("talent-management")
async def talent_management(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a perpetual talent management orchestration led by CHRO.

    The orchestration continuously manages talent strategy, organizational
    development, and HR governance.

    Request body::

        {"focus": "retention", "departments": ["engineering", "marketing"]}
    """
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents if a.agent_id in ("chro", "ceo", "coo")]

    if not agent_ids:
        raise ValueError("CHRO and/or CEO agents not available in the catalog")

    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose="Drive talent strategy, organizational development, and workforce optimization",
        purpose_scope="Talent acquisition, retention, development, culture, and HR governance",
        context={
            "focus": request.body.get("focus", "strategy"),
            "departments": request.body.get("departments", []),
        },
        workflow="hierarchical",
    )
    logger.info("Talent management orchestration started: %s", status.orchestration_id)
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}


@app.workflow("technology-review")
async def technology_review(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a perpetual technology review orchestration led by CTO.

    The orchestration continuously evaluates technology strategy, architecture
    decisions, and engineering excellence.

    Request body::

        {"focus_areas": ["cloud", "ai", "security"], "review_scope": "quarterly"}
    """
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents if a.agent_id in ("cto", "ceo", "cso")]

    if not agent_ids:
        raise ValueError("CTO and/or CEO agents not available in the catalog")

    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose="Drive technology strategy, architecture excellence, and innovation",
        purpose_scope="Technology roadmap, architecture review, engineering practices, and innovation pipeline",
        context={
            "focus_areas": request.body.get("focus_areas", ["cloud", "ai", "security"]),
            "review_scope": request.body.get("review_scope", "quarterly"),
        },
        workflow="collaborative",
    )
    logger.info("Technology review orchestration started: %s", status.orchestration_id)
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}
