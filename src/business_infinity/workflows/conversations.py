"""Boardroom conversation workflows for BusinessInfinity.

Boardroom conversations and A2A messaging are orchestrated via the AOS
infrastructure service, which manages agent lifecycle, messaging, storage,
and monitoring.  The client app supplies only business context; AOS handles
the rest.

Conversation listings and event polling still query the AOS knowledge base,
which persists orchestration artefacts as searchable documents.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from aos_client import WorkflowRequest

from ._app import app, logger, select_c_suite_agents

# Document type used to persist boardroom conversations in the knowledge base.
_CONVERSATION_DOC_TYPE = "boardroom-conversation"


@app.workflow("list-conversations")
async def list_conversations(request: WorkflowRequest) -> Dict[str, Any]:
    """List boardroom conversations with optional filtering.

    Conversations are stored as knowledge-base documents so they survive
    AOS restarts.

    Request body::

        {"champion": "ceo", "status": "open", "limit": 50}
    """
    query_parts: List[str] = []
    champion: Optional[str] = request.body.get("champion")
    status_filter: Optional[str] = request.body.get("status")
    limit: int = int(request.body.get("limit", 50))

    if champion:
        query_parts.append(f"champion:{champion}")
    if status_filter:
        query_parts.append(f"status:{status_filter}")
    query = " ".join(query_parts) if query_parts else "boardroom conversation"

    docs = await request.client.search_documents(
        query=query,
        doc_type=_CONVERSATION_DOC_TYPE,
        limit=limit,
    )
    conversations = [
        d.model_dump(mode="json") if hasattr(d, "model_dump") else dict(d)
        for d in docs
    ]
    return {"conversations": conversations, "count": len(conversations)}


@app.workflow("create-conversation")
async def create_conversation(request: WorkflowRequest) -> Dict[str, Any]:
    """Create and start a new boardroom conversation via AOS orchestration.

    Starts an AOS orchestration involving the relevant C-suite agents for the
    given conversation, with the champion leading the discussion.  AOS manages
    the agent lifecycle, messaging, storage, and monitoring.

    Request body::

        {
            "conversation_type": "strategic-decision",
            "champion": "ceo",
            "title": "Q2 Market Expansion",
            "content": "Proposal to expand into APAC markets in Q2...",
            "context": {}
        }
    """
    required = ["conversation_type", "champion", "title", "content"]
    for field in required:
        if field not in request.body:
            raise ValueError(f"Missing required field: {field}")

    champion = request.body["champion"]
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents]
    # Ensure champion leads the orchestration
    if champion not in agent_ids:
        agent_ids.insert(0, champion)

    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose=f"Boardroom conversation: {request.body['title']}",
        purpose_scope=request.body["conversation_type"],
        context={
            "champion": champion,
            "title": request.body["title"],
            "content": request.body["content"],
            **request.body.get("context", {}),
        },
        workflow="collaborative",
    )
    logger.info(
        "Boardroom conversation orchestration started: %s (champion: %s)",
        status.orchestration_id,
        champion,
    )
    return {
        "conversation_id": status.orchestration_id,
        "status": status.status.value,
        "message": "Conversation orchestration started",
    }


@app.workflow("sign-conversation")
async def sign_conversation(request: WorkflowRequest) -> Dict[str, Any]:
    """Sign a boardroom conversation.

    Appends a signer record to the conversation document in the knowledge base.

    Request body::

        {
            "conversation_id": "<doc-id>",
            "signer_role": "cfo",
            "signer_name": "Jane Smith"
        }
    """
    from datetime import datetime as dt, timezone

    for field in ("conversation_id", "signer_role", "signer_name"):
        if field not in request.body:
            raise ValueError(f"Missing required field: {field}")

    update_fields = {
        "signature": {
            "role": request.body["signer_role"],
            "name": request.body["signer_name"],
            "signed_at": dt.now(timezone.utc).isoformat(),
        }
    }
    await request.client.update_document(request.body["conversation_id"], update_fields)
    logger.info(
        "Conversation %s signed by %s (%s)",
        request.body["conversation_id"],
        request.body["signer_name"],
        request.body["signer_role"],
    )
    return {
        "conversation_id": request.body["conversation_id"],
        "status": "signed",
        "signer": {
            "name": request.body["signer_name"],
            "role": request.body["signer_role"],
        },
    }


@app.workflow("create-a2a-message")
async def create_a2a_message(request: WorkflowRequest) -> Dict[str, Any]:
    """Initiate an Agent-to-Agent (A2A) communication via AOS orchestration.

    Delegates agent messaging, storage, and monitoring to AOS.  The client app
    supplies only the business context; AOS handles the agent interaction
    lifecycle.

    Request body::

        {
            "from_agent": "ceo",
            "to_agent": "cfo",
            "conversation_type": "budget-query",
            "message": "What is the runway at current burn rate?"
        }
    """
    required = ["from_agent", "to_agent", "conversation_type", "message"]
    for field in required:
        if field not in request.body:
            raise ValueError(f"Missing required field: {field}")

    status = await request.client.start_orchestration(
        agent_ids=[request.body["from_agent"], request.body["to_agent"]],
        # AOS purpose field is capped at 240 characters; longer messages are
        # carried in full inside the structured context dict below.
        purpose=request.body["message"][:240],
        purpose_scope=request.body["conversation_type"],
        context={
            "from_agent": request.body["from_agent"],
            "to_agent": request.body["to_agent"],
            "message": request.body["message"],
            **request.body.get("context", {}),
        },
        workflow="sequential",
    )
    logger.info(
        "A2A orchestration started between %s and %s: %s",
        request.body["from_agent"],
        request.body["to_agent"],
        status.orchestration_id,
    )
    return {
        "conversation_id": status.orchestration_id,
        "from_agent": request.body["from_agent"],
        "to_agent": request.body["to_agent"],
        "status": status.status.value,
    }


@app.workflow("get-conversation-events")
async def get_conversation_events(request: WorkflowRequest) -> Dict[str, Any]:
    """Get recent boardroom conversation events.

    Fetches the latest conversation documents created after an optional
    ISO-8601 timestamp so that web clients can poll for incremental updates.

    Request body::

        {"since": "2026-01-01T00:00:00Z", "limit": 100}
    """
    from datetime import datetime as dt, timezone

    limit: int = int(request.body.get("limit", 100))
    docs = await request.client.search_documents(
        query="boardroom conversation event",
        doc_type=_CONVERSATION_DOC_TYPE,
        limit=limit,
    )
    events = [
        d.model_dump(mode="json") if hasattr(d, "model_dump") else dict(d)
        for d in docs
    ]
    return {
        "events": events,
        "count": len(events),
        "since": request.body.get("since"),
        "timestamp": dt.now(timezone.utc).isoformat(),
    }
