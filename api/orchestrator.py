import os, json, uuid, datetime, requests
from .EnvManager import EnvManager
import azure.functions as func
from api.ConversationManager import ConversationManager
from api.TrainingDataManager import TrainingDataManager
from api.AgentManager import AgentManager
from api.MLClientManager import MLClientManager
from api.AuthHandler import validate_jwt, UNAUTHORIZED_MSG

class Orchestrator:
    def __init__(self):
        self.env = EnvManager()
        self.STORAGE_CONN = self.env.get_required("AzureWebJobsStorage")
        self.MLURL = self.env.get_required("MLENDPOINT_URL")
        self.MLKEY = self.env.get_required("MLENDPOINT_KEY")

        self.conversation_manager = ConversationManager()
        self.training_data_manager = TrainingDataManager()
        self.AGENTDIRS = self.training_data_manager.AGENTDIRS
        self.AGENTPROFILES = self.training_data_manager.AGENTPROFILES
        self.DOMAINKNOW = self.training_data_manager.DOMAINKNOW
        self.agent_manager = AgentManager(self.AGENTDIRS, self.DOMAINKNOW)
        self.ml_client_manager = MLClientManager()
        self.ml_client = self.ml_client_manager.get_client()

    def start_conversation(self, req):
        claims = self.require_auth(req)
        if not isinstance(claims, dict):
            return func.HttpResponse(UNAUTHORIZED_MSG, status_code=401)

        body = req.get_json()
        domain = body.get("domain")
        if not self.agent_manager.get_agent(domain):
            return func.HttpResponse("Invalid domain", status_code=400)

        conv_id = str(uuid.uuid4())
        self.conversation_manager.create_conversation(conv_id, domain)
        return func.HttpResponse(json.dumps({"conversationId": conv_id}),
                                 mimetype="application/json", status_code=201)

    async def post_message(self, req):
        claims = self.require_auth(req)
        if not isinstance(claims, dict):
            return claims
        convid = req.routeparams.get("id")
        body = req.get_json()
        user_input = body.get("message", "")
        # Fetch conversation 
        conv = self.conversation_manager.get_conversation(convid)
        if not conv:
            return func.HttpResponse("Conversation not found", status_code=404)

        domain = conv["domain"]
        user_msg = {"sender": "user", "text": user_input,
                    "time": datetime.datetime.utcnow().isoformat()}
        conv["messages"].append(user_msg)

        # Call the domain agent using encapsulated method
        answer_json = await self.agent_manager.ask_agent(domain, user_input)
        # Upsert conversation and create agent_msg inside CosmosManager
        self.conversation_manager.upsert_conversation(conv, domain, answer_json)

        return func.HttpResponse(answer_json,
                                 mimetype="application/json")

    def get_messages(self, req):
        claims = self.require_auth(req)
        if not isinstance(claims, dict):
            return claims
        convid = req.routeparams.get("id")
        conv_json = self.conversation_manager.get_conversation(convid)
        if not conv_json:
            return func.HttpResponse("Not found", status_code=404)

        return func.HttpResponse(conv_json, mimetype="application/json")

    async def mentor_test(self, req):
        body = req.get_json()
        domain = body.get("domain")
        question= body.get("question")
        agent_func = self.agent_manager.get_agent(domain)
        if not agent_func or not question:
            return func.HttpResponse("domain and question required", status_code=400)

        # Invoke the same semantic agent for testing
        answer_json = await self.agent_manager.ask_agent(domain, question)
        return func.HttpResponse(
            answer_json,
            mimetype="application/json",
            status_code=200
        )

    def mentorsubmitqa(self, req):
        body = req.get_json()
        domain = body.get("domain")
        q = body.get("question")
        a = body.get("answer")
        if not domain or not q or not a:
            return func.HttpResponse("domain, question, answer required", status_code=400)

        # Append to mentor Q&A blob for that domain
        self.training_data_manager.upload_mentor_qa_pair(domain, q, a)
        return func.HttpResponse(status_code=201)

    def mentorlistqa(self, req):
        domain = req.params.get("domain")
        if not domain:
            return func.HttpResponse("domain query param required", status_code=400)

        pairs_json = self.training_data_manager.get_mentor_qa_pairs(domain)
        return func.HttpResponse(pairs_json, mimetype="application/json")

    def mentortriggerfine_tune(self, req):
        body = req.get_json()
        domain = body.get("domain")
        if not domain:
            return func.HttpResponse("domain required", status_code=400)

        # Invoke the pipeline endpoint using MLClientManager encapsulation
        result_json = self.ml_client_manager.invoke_pipeline(domain)
        return func.HttpResponse(
            result_json,
            mimetype="application/json",
            status_code=202
        )

    def list_agents(self, req):
        claims = self.require_auth(req)
        if not isinstance(claims, dict):
            return claims

        # Get agent profiles from AgentManager
        agents_json = self.agent_manager.get_agent_profiles()
        return func.HttpResponse(
            agents_json,
            mimetype="application/json",
            status_code=200
        )

    def get_agent(self, req):
        claims = self.require_auth(req)
        if not isinstance(claims, dict):
            return claims

        aid = req.route_params.get("agentId")
        prof_json = self.agent_manager.get_agent_profile(aid)
        if not prof_json:
            return func.HttpResponse("Agent not found", status_code=404)

        return func.HttpResponse(
            prof_json,
            mimetype="application/json",
            status_code=200
        )

    async def chat(self, req):
        claims = self.require_auth(req)
        if not isinstance(claims, dict):
            return claims

        aid = req.route_params["agentId"]
        msg = req.get_json().get("message")
        answer_json = await self.agent_manager.ask_agent(aid, msg)
        if not answer_json:
            return func.HttpResponse("Unknown agent", status_code=400)
        return func.HttpResponse(answer_json, mimetype="application/json")

    def login(self, req):
        from api.AuthHandler import AuthHandler
        auth_handler = AuthHandler()
        return auth_handler.login(req)

    def refresh(self, req):
        from api.AuthHandler import AuthHandler
        auth_handler = AuthHandler()
        return auth_handler.refresh(req)

    def extract_name(self, req):
        name = req.params.get('name')
        if not name:
            try:
                req_body = req.get_json()
            except ValueError:
                req_body = None
            if req_body:
                name = req_body.get('name')
        if name:
            return f"Hello, {name}. This HTTP triggered function executed successfully.", 200
        else:
            return (
                "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
                200
            )

    def require_auth(self, req):
        claims = validate_jwt.from_request(req)
        if not claims:
            return func.HttpResponse(UNAUTHORIZED_MSG, status_code=401)
        return claims
