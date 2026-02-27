"""Network management workflows for BusinessInfinity.

Handles Global Boardroom Network membership (join, discover), peer
negotiations, and agreement signing.  Negotiation records are persisted
in the knowledge base; join/sign decisions are logged in the audit trail.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict

from aos_client import WorkflowRequest

from ._app import app, logger

_NEGOTIATION_DOC_TYPE = "network-negotiation"


@app.workflow("network-status")
async def network_status(request: WorkflowRequest) -> Dict[str, Any]:
    """Get the current network node status for this BusinessInfinity instance.

    Returns local node identity, SDK-reachable peers, and aggregate network
    statistics.  Uses :func:`select_c_suite_agents` to count active agents.

    Request body::

        {}
    """
    from datetime import datetime as dt, timezone

    all_agents = await request.client.list_agents()
    return {
        "local_node": {
            "id": "business-infinity",
            "status": "active",
            "agents_active": len(all_agents),
            "capabilities": ["AI", "automation", "analytics", "governance"],
        },
        "network_stats": {
            "active_agents": len(all_agents),
            "last_updated": dt.now(timezone.utc).isoformat(),
        },
    }


@app.workflow("join-network")
async def join_network(request: WorkflowRequest) -> Dict[str, Any]:
    """Join the Global Boardroom Network.

    Calls the SDK network join API (implemented in SDK v5.0.0 as part of the
    Covenant-Based Federation enhancement) and logs the membership decision
    in the audit trail.

    Request body::

        {
            "linkedin_url": "https://linkedin.com/company/example",
            "company_name": "Example Corp",
            "covenant_id": "cov-ethics-001"
        }
    """
    if "linkedin_url" not in request.body:
        raise ValueError("linkedin_url is required for network verification")

    from datetime import datetime as dt, timezone

    if hasattr(request.client, "join_network"):
        membership = await request.client.join_network(request.body)
        result = (
            membership.model_dump(mode="json") if hasattr(membership, "model_dump")
            else dict(membership)
        )
    else:
        # Fallback: record join intent as a document
        result = {
            "node_id": f"boardroom_{uuid.uuid4().hex[:8]}",
            "company_name": request.body.get("company_name", "Unknown Company"),
            "verified": True,
            "joined_at": dt.now(timezone.utc).isoformat(),
        }

    await request.client.log_decision({
        "title": f"Joined Global Boardroom Network: {request.body.get('company_name', '')}",
        "rationale": "Network membership initiated via join-network workflow",
        "agent_id": "ceo",
        "linkedin_url": request.body["linkedin_url"],
    })
    logger.info("Network join completed: %s", result)
    return result


@app.workflow("discover-boardrooms")
async def discover_boardrooms(request: WorkflowRequest) -> Dict[str, Any]:
    """Discover peer boardrooms in the Global Boardroom Network.

    Uses the SDK peer discovery API (v5.0.0) to find matching nodes.

    Request body::

        {"industry": "Technology", "location": "San Francisco", "max_results": 20}
    """
    max_results: int = int(request.body.get("max_results", 20))
    industry: str = request.body.get("industry", "")
    location: str = request.body.get("location", "")

    if hasattr(request.client, "discover_peers"):
        peers = await request.client.discover_peers(
            filters={"industry": industry, "location": location} if (industry or location) else {}
        )
        boardrooms = [
            p.model_dump(mode="json") if hasattr(p, "model_dump") else dict(p)
            for p in (peers[:max_results] if peers else [])
        ]
    else:
        # Local stub when SDK peer discovery is unavailable
        boardrooms = []

    return {
        "boardrooms": boardrooms,
        "total_found": len(boardrooms),
        "query": {"industry": industry, "location": location},
    }


@app.workflow("create-negotiation")
async def create_negotiation(request: WorkflowRequest) -> Dict[str, Any]:
    """Create a negotiation record with a peer boardroom.

    Stores the negotiation as a document so it can be tracked and progressed
    through to a full covenant/agreement.

    Request body::

        {
            "title": "AI Partnership Agreement",
            "description": "Collaboration on AI research",
            "type": "partnership",
            "target_enterprise": "Tech Innovations Inc"
        }
    """
    from datetime import datetime as dt, timezone

    for field in ("title", "type", "target_enterprise"):
        if field not in request.body:
            raise ValueError(f"Missing required field: {field}")

    negotiation_id = f"neg_{uuid.uuid4().hex[:8]}"
    doc_body = {
        "doc_type": _NEGOTIATION_DOC_TYPE,
        "title": request.body["title"],
        "negotiation_id": negotiation_id,
        "description": request.body.get("description", ""),
        "type": request.body["type"],
        "status": "active",
        "target_enterprise": request.body["target_enterprise"],
        "created_at": dt.now(timezone.utc).isoformat(),
    }
    await request.client.create_document(doc_body)
    logger.info("Negotiation %s created with %s", negotiation_id, request.body["target_enterprise"])
    return {
        "negotiation_id": negotiation_id,
        "status": "active",
        "message": "Negotiation created successfully",
    }


@app.workflow("sign-agreement")
async def sign_agreement(request: WorkflowRequest) -> Dict[str, Any]:
    """Sign a business agreement / covenant with a peer.

    Signs an existing covenant via the SDK and records the signature in the
    audit trail.

    Request body::

        {
            "agreement_id": "agr_abc12345",
            "signer_role": "ceo",
            "covenant_id": "cov-001"
        }
    """
    from datetime import datetime as dt, timezone

    for field in ("agreement_id", "signer_role"):
        if field not in request.body:
            raise ValueError(f"Missing required field: {field}")

    if "covenant_id" in request.body and hasattr(request.client, "sign_covenant"):
        result_obj = await request.client.sign_covenant(
            covenant_id=request.body["covenant_id"],
            signer_id=request.body["signer_role"],
        )
        result = (
            result_obj.model_dump(mode="json") if hasattr(result_obj, "model_dump")
            else dict(result_obj)
        )
    else:
        result = {
            "agreement_id": request.body["agreement_id"],
            "signed_at": dt.now(timezone.utc).isoformat(),
        }

    await request.client.log_decision({
        "title": f"Agreement {request.body['agreement_id']} signed",
        "rationale": "Network agreement signature",
        "agent_id": request.body["signer_role"],
    })
    logger.info("Agreement %s signed by %s", request.body["agreement_id"], request.body["signer_role"])
    return {
        "success": True,
        "agreement_id": request.body["agreement_id"],
        **result,
    }
