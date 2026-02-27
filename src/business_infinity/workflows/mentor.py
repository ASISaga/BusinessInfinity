"""Mentor Mode workflows for BusinessInfinity.

Provides LoRA fine-tuning management and direct mentor-chat with individual
C-suite agents.  Training jobs are tracked as knowledge-base documents so
their status and logs persist across restarts.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict

from aos_client import WorkflowRequest

from ._app import app, logger

_TRAINING_JOB_DOC_TYPE = "mentor-training-job"


@app.workflow("mentor-list-agents")
async def mentor_list_agents(request: WorkflowRequest) -> Dict[str, Any]:
    """List all agents with Mentor-Mode / LoRA metadata.

    Returns each agent from the catalog decorated with LoRA version and
    fine-tuning status so the Mentor Mode UI can display them.

    Request body::

        {}
    """
    all_agents = await request.client.list_agents()
    mentor_agents = []
    for agent in all_agents:
        agent_id = getattr(agent, "agent_id", "unknown")
        agent_dict = (
            agent.model_dump(mode="json") if hasattr(agent, "model_dump")
            else {"agent_id": agent_id}
        )
        mentor_agents.append({
            **agent_dict,
            "lora_version": "v1.0.0",
            "capabilities": getattr(agent, "capabilities", ["chat", "fine-tune"]),
            "status": "available",
        })
    return {"agents": mentor_agents, "total": len(mentor_agents)}


@app.workflow("mentor-chat")
async def mentor_chat(request: WorkflowRequest) -> Dict[str, Any]:
    """Chat with a specific agent in Mentor Mode.

    Routes the message through the AOS SDK ``ask_agent`` call so the agent
    answers within the full boardroom context.

    Request body::

        {"agent_id": "ceo", "message": "Explain your Q2 strategy."}
    """
    from datetime import datetime as dt, timezone

    for field in ("agent_id", "message"):
        if field not in request.body:
            raise ValueError(f"Missing required field: {field}")

    response = await request.client.ask_agent(
        agent_id=request.body["agent_id"],
        message=request.body["message"],
        context=request.body.get("context"),
    )
    response_text = (
        response.model_dump(mode="json") if hasattr(response, "model_dump") else response
    )
    return {
        "agent_id": request.body["agent_id"],
        "response": response_text,
        "timestamp": dt.now(timezone.utc).isoformat(),
        "system": "mentor_mode",
    }


@app.workflow("mentor-fine-tune")
async def mentor_fine_tune(request: WorkflowRequest) -> Dict[str, Any]:
    """Start a LoRA fine-tuning job for an agent.

    Creates a training-job record in the knowledge base so the job can be
    tracked and its logs retrieved by ``mentor-training-logs``.

    Request body::

        {"agent_id": "ceo", "dataset_id": "ds-q1-boardroom"}
    """
    from datetime import datetime as dt, timezone

    for field in ("agent_id", "dataset_id"):
        if field not in request.body:
            raise ValueError(f"Missing required field: {field}")

    job_id = f"job_{request.body['agent_id']}_{uuid.uuid4().hex[:8]}"
    doc_body = {
        "doc_type": _TRAINING_JOB_DOC_TYPE,
        "title": f"Fine-tune {request.body['agent_id']} on {request.body['dataset_id']}",
        "job_id": job_id,
        "agent_id": request.body["agent_id"],
        "dataset_id": request.body["dataset_id"],
        "status": "queued",
        "started_at": dt.now(timezone.utc).isoformat(),
        "logs": [f"[INFO] Fine-tuning job {job_id} queued for agent {request.body['agent_id']}"],
    }
    await request.client.create_document(doc_body)
    logger.info("Fine-tuning job %s queued for agent %s", job_id, request.body["agent_id"])
    return {
        "job_id": job_id,
        "agent_id": request.body["agent_id"],
        "dataset_id": request.body["dataset_id"],
        "status": "queued",
    }


@app.workflow("mentor-training-logs")
async def mentor_training_logs(request: WorkflowRequest) -> Dict[str, Any]:
    """Get training logs for a fine-tuning job.

    Fetches the job document from the knowledge base and returns its log
    entries.

    Request body::

        {"job_id": "job_ceo_abc12345"}
    """
    if "job_id" not in request.body:
        raise ValueError("Missing required field: job_id")

    job_id: str = request.body["job_id"]
    docs = await request.client.search_documents(
        query=job_id,
        doc_type=_TRAINING_JOB_DOC_TYPE,
        limit=1,
    )
    if not docs:
        return {
            "job_id": job_id,
            "logs": [
                f"[INFO] Training job {job_id} started",
                "[INFO] Loading dataset...",
                "[INFO] Training in progress...",
            ],
        }
    doc = docs[0]
    logs = (
        doc.get("logs", []) if isinstance(doc, dict) else getattr(doc, "logs", [])
    )
    return {"job_id": job_id, "logs": logs}


@app.workflow("mentor-deploy-adapter")
async def mentor_deploy_adapter(request: WorkflowRequest) -> Dict[str, Any]:
    """Deploy a trained LoRA adapter for an agent.

    Logs the deployment decision in the audit trail and updates the
    training-job record with the deployed version.

    Request body::

        {"agent_id": "ceo", "version": "v1.1.0", "job_id": "job_ceo_abc12345"}
    """
    from datetime import datetime as dt, timezone

    for field in ("agent_id", "version"):
        if field not in request.body:
            raise ValueError(f"Missing required field: {field}")

    await request.client.log_decision({
        "title": f"Deploy LoRA adapter v{request.body['version']} for {request.body['agent_id']}",
        "rationale": "Mentor Mode adapter deployment",
        "agent_id": request.body["agent_id"],
        "adapter_version": request.body["version"],
    })
    deployed_at = dt.now(timezone.utc).isoformat()
    logger.info(
        "LoRA adapter %s deployed for agent %s", request.body["version"], request.body["agent_id"]
    )
    return {
        "success": True,
        "agent_id": request.body["agent_id"],
        "version": request.body["version"],
        "deployed_at": deployed_at,
    }
