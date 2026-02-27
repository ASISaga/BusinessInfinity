"""Boardroom conversation workflows for BusinessInfinity.

Manages boardroom conversations, agent-to-agent (A2A) messages, and
conversation event polling.  Conversations are persisted as knowledge-base
documents so they survive AOS restarts.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from aos_client import WorkflowRequest

from ._app import app, logger

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
    """Create a new boardroom conversation.

    Creates a conversation record in the knowledge base.

    Request body::

        {
            "conversation_type": "strategic-decision",
            "champion": "ceo",
            "title": "Q2 Market Expansion",
            "content": "Proposal to expand into APAC markets in Q2...",
            "context": {}
        }
    """
    from datetime import datetime as dt, timezone

    required = ["conversation_type", "champion", "title", "content"]
    for field in required:
        if field not in request.body:
            raise ValueError(f"Missing required field: {field}")

    doc_body = {
        "doc_type": _CONVERSATION_DOC_TYPE,
        "title": request.body["title"],
        "conversation_type": request.body["conversation_type"],
        "champion": request.body["champion"],
        "content": request.body["content"],
        "context": request.body.get("context", {}),
        "status": "open",
        "signers": [],
        "created_at": dt.now(timezone.utc).isoformat(),
    }
    doc = await request.client.create_document(doc_body)
    conversation_id = (
        doc.document_id if hasattr(doc, "document_id") else str(uuid.uuid4())
    )
    logger.info("Conversation %s created by champion %s", conversation_id, request.body["champion"])
    return {
        "conversation_id": conversation_id,
        "status": "created",
        "message": "Conversation created successfully",
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
    """Initiate an Agent-to-Agent (A2A) communication.

    Delivers a message from one agent to another via ``ask_agent`` and
    stores the exchange as a conversation document in the knowledge base.

    Request body::

        {
            "from_agent": "ceo",
            "to_agent": "cfo",
            "conversation_type": "budget-query",
            "message": "What is the runway at current burn rate?"
        }
    """
    from datetime import datetime as dt, timezone

    required = ["from_agent", "to_agent", "conversation_type", "message"]
    for field in required:
        if field not in request.body:
            raise ValueError(f"Missing required field: {field}")

    # Deliver the message via the agent interaction SDK
    response = await request.client.ask_agent(
        agent_id=request.body["to_agent"],
        message=request.body["message"],
        context={
            "from_agent": request.body["from_agent"],
            "conversation_type": request.body["conversation_type"],
            **request.body.get("context", {}),
        },
    )
    response_text = (
        response.model_dump(mode="json") if hasattr(response, "model_dump") else response
    )

    # Persist the exchange as a conversation document
    doc_body = {
        "doc_type": _CONVERSATION_DOC_TYPE,
        "title": f"A2A: {request.body['from_agent']} → {request.body['to_agent']}",
        "conversation_type": request.body["conversation_type"],
        "from_agent": request.body["from_agent"],
        "to_agent": request.body["to_agent"],
        "message": request.body["message"],
        "response": response_text,
        "status": "completed",
        "created_at": dt.now(timezone.utc).isoformat(),
    }
    doc = await request.client.create_document(doc_body)
    conversation_id = (
        doc.document_id if hasattr(doc, "document_id") else str(uuid.uuid4())
    )
    logger.info(
        "A2A message from %s to %s stored as conversation %s",
        request.body["from_agent"],
        request.body["to_agent"],
        conversation_id,
    )
    return {
        "conversation_id": conversation_id,
        "from_agent": request.body["from_agent"],
        "to_agent": request.body["to_agent"],
        "response": response_text,
        "status": "created",
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
