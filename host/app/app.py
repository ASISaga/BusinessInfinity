import os, uuid
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
from .models import UiAction, MessagesQuery, Envelope
from .manifest import get_ui_schema
from .governance import validate_request, GovernanceError
from .aml import aml_infer, aml_train
from .storage import enqueue_request, query_messages

app = FastAPI(title="Boardroom Host App")

@app.get("/dashboard")
async def get_dashboard(role: str = Query(...), scope: str = Query("local")):
    schema = get_ui_schema(role, scope)
    return {"uiSchema": schema}

@app.get("/messages")
async def get_messages(boardroomId: str, conversationId: str, since: Optional[str] = None):
    rows = query_messages(boardroomId, conversationId, since)
    return {"messages": rows}

@app.post("/action")
async def post_action(action: UiAction):
    corr = action.correlationId or str(uuid.uuid4())
    env = Envelope(
        correlationId=corr,
        traceId=corr,
        boardroomId=action.boardroomId,
        conversationId=action.conversationId,
        senderAgentId=action.agentId,
        role=action.agentId.upper(),  # map agent to role as needed
        scope=action.scope,
        messageType="chat",
        payload={
            "action": action.action,
            "args": action.args
        }
    ).model_dump()
    try:
        validate_request("inference", {"role": env["role"], "scope": env["scope"], "payload": env["payload"]})
    except GovernanceError as ge:
        raise HTTPException(status_code=403, detail=str(ge))
    enqueue_request(env)
    return {"status": "queued", "correlationId": corr}

@app.post("/aml/infer")
async def aml_infer_endpoint(agentId: str, prompt: str):
    try:
        validate_request("inference", {"role": "Governance", "payload": {"agentId": agentId}})
    except GovernanceError as ge:
        raise HTTPException(status_code=403, detail=str(ge))
    res = await aml_infer(agentId, prompt)
    return res

@app.post("/aml/train")
async def aml_train_endpoint(jobName: str, modelName: str, datasetUri: str, demo: bool = True):
    try:
        validate_request("training", {"role": "Governance", "demo": demo, "payload": {"modelName": modelName}})
    except GovernanceError as ge:
        raise HTTPException(status_code=403, detail=str(ge))
    res = await aml_train(jobName, {"modelName": modelName, "datasetUri": datasetUri})
    return res