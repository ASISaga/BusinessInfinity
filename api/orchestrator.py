import os, json, uuid, datetime, requests
from .EnvManager import EnvManager
import azure.functions as func
from api.CosmosManager import CosmosManager
from api.BlobManager import BlobManager
from api.AgentManager import AgentManager
from api.MLClientManager import MLClientManager
from api.AuthHandler import validate_jwt, UNAUTHORIZED_MSG
from azure.functions import HttpRequest, HttpResponse
from azure.functions import http_router

STORAGE_CONN = EnvManager().get_required("AzureWebJobsStorage")
MLURL = EnvManager().get_required("MLENDPOINT_URL")
MLKEY = EnvManager().get_required("MLENDPOINT_KEY")

cosmos_manager = CosmosManager()

# Authorization check is now handled by AuthHandler

blob_manager = BlobManager()
AGENTDIRS = blob_manager.AGENTDIRS
AGENTPROFILES = blob_manager.AGENTPROFILES
DOMAINKNOW = blob_manager.DOMAINKNOW

agent_manager = AgentManager(AGENTDIRS, DOMAINKNOW)


def require_auth(req):
    claims = validate_jwt.from_request(req)
    if not claims:
        return func.HttpResponse(UNAUTHORIZED_MSG, status_code=401)
    return claims


router = http_router.HttpRouter()

@router.route(methods=["POST"], route="conversations", auth_level=func.AuthLevel.FUNCTION)
def start_conv(req: func.HttpRequest) -> func.HttpResponse:
    claims = require_auth(req)
    if not isinstance(claims, dict):
        return claims

    body = req.get_json()
    domain = body.get("domain")
    if not agent_manager.get_agent(domain):
        return func.HttpResponse("Invalid domain", status_code=400)

    conv_id = str(uuid.uuid4())
    cosmos_manager.create_conversation(conv_id, domain)
    return func.HttpResponse(json.dumps({"conversationId": conv_id}),
                             mimetype="application/json", status_code=201)

@router.route(methods=["POST"], route="conversations/{id}/messages", auth_level=func.AuthLevel.FUNCTION)
async def post_message(req: func.HttpRequest) -> func.HttpResponse:
    claims = require_auth(req)
    if not isinstance(claims, dict):
        return claims
    convid = req.routeparams.get("id")
    body = req.get_json()
    user_input = body.get("message", "")
    # Fetch conversation 
    conv = cosmos_manager.get_conversation(convid)
    if not conv:
        return func.HttpResponse("Conversation not found", status_code=404)

    domain = conv["domain"]
    user_msg = {"sender": "user", "text": user_input,
                "time": datetime.datetime.utcnow().isoformat()}
    conv["messages"].append(user_msg)

    # Call the domain agent using encapsulated method
    answer_json = await agent_manager.ask_agent(domain, user_input)
    # Upsert conversation and create agent_msg inside CosmosManager
    cosmos_manager.upsert_conversation(conv, domain, answer_json)

    return func.HttpResponse(answer_json,
                             mimetype="application/json")

@router.route(methods=["GET"], route="conversations/{id}/messages", auth_level=func.AuthLevel.FUNCTION)
def get_messages(req: func.HttpRequest) -> func.HttpResponse:
    claims = require_auth(req)
    if not isinstance(claims, dict):
        return claims
    convid = req.routeparams.get("id")
    conv_json = cosmos_manager.get_conversation(convid)
    if not conv_json:
        return func.HttpResponse("Not found", status_code=404)

    return func.HttpResponse(conv_json, mimetype="application/json")

ml_client_manager = MLClientManager()
ml_client = ml_client_manager.get_client()

# –– Mentor: Test LLM/Adapter ––
@router.route(methods=["POST"], route="mentor/test", auth_level=func.AuthLevel.FUNCTION)
async def mentor_test(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    domain = body.get("domain")
    question= body.get("question")
    agent_func = agent_manager.get_agent(domain)
    if not agent_func or not question:
        return func.HttpResponse("domain and question required", status_code=400)

    # Invoke the same semantic agent for testing
    answer_json = await agent_manager.ask_agent(domain, question)
    return func.HttpResponse(
        answer_json,
        mimetype="application/json",
        status_code=200
    )

# –– Mentor: Submit Q&A Pair ––
@router.route(methods=["POST"], route="mentor/qapair", auth_level=func.AuthLevel.FUNCTION)
def mentorsubmitqa(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    domain = body.get("domain")
    q = body.get("question")
    a = body.get("answer")
    if not domain or not q or not a:
        return func.HttpResponse("domain, question, answer required", status_code=400)

    # Append to mentor Q&A blob for that domain
    blob_manager.upload_mentor_qa_pair(domain, q, a)
    return func.HttpResponse(status_code=201)

# –– Mentor: List Q&A Pairs ––
@router.route(methods=["GET"], route="mentor/qapairs", auth_level=func.AuthLevel.FUNCTION)
def mentorlistqa(req: func.HttpRequest) -> func.HttpResponse:
    domain = req.params.get("domain")
    if not domain:
        return func.HttpResponse("domain query param required", status_code=400)

    pairs_json = blob_manager.get_mentor_qa_pairs(domain)
    return func.HttpResponse(pairs_json, mimetype="application/json")

# –– Mentor: Trigger Batch Nuance Fine-Tuning ––
@router.route(methods=["POST"], route="mentor/fine-tune", auth_level=func.AuthLevel.FUNCTION)
def mentortriggerfine_tune(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    domain = body.get("domain")
    if not domain:
        return func.HttpResponse("domain required", status_code=400)

    # Invoke the pipeline endpoint using MLClientManager encapsulation
    result_json = ml_client_manager.invoke_pipeline(domain)
    return func.HttpResponse(
        result_json,
        mimetype="application/json",
        status_code=202
    )

@router.route(methods=["GET"], route="agents")
def list_agents(req: HttpRequest) -> HttpResponse:
    claims = require_auth(req)
    if not isinstance(claims, dict):
        return claims

    # Get agent profiles from AgentManager
    agents_json = agent_manager.get_agent_profiles()
    return HttpResponse(
        agents_json,
        mimetype="application/json",
        status_code=200
    )

@router.route(methods=["GET"], route="agents/{agentId}")
def get_agent(req: HttpRequest) -> HttpResponse:
    claims = require_auth(req)
    if not isinstance(claims, dict):
        return claims

    aid = req.route_params.get("agentId")
    prof_json = agent_manager.get_agent_profile(aid)
    if not prof_json:
        return HttpResponse("Agent not found", status_code=404)

    return HttpResponse(
        prof_json,
        mimetype="application/json",
        status_code=200
    )

@router.route(methods=["POST"], route="chat/{agentId}")
async def chat(req: func.HttpRequest):
    claims = require_auth(req)
    if not isinstance(claims, dict):
        return claims

    aid = req.route_params["agentId"]
    msg = req.get_json().get("message")
    answer_json = await agent_manager.ask_agent(aid, msg)
    if not answer_json:
        return func.HttpResponse("Unknown agent", status_code=400)
    return func.HttpResponse(answer_json,
                             mimetype="application/json")