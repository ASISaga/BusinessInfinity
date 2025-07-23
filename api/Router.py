import json, uuid, datetime
import logging
import azure.functions as func
from api.Orchestrator import Orchestrator
from azure.functions import HttpRequest, HttpResponse

from api.AuthHandler import AuthHandler

app = func.FunctionApp()

class Router:
    def __init__(self):
        self.orchestrator = Orchestrator()

    @app.function_name(name="http_trigger")
    @app.route(methods=["GET", "POST"], route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
    def http_trigger(self, req: func.HttpRequest) -> func.HttpResponse:
        logging.info('Python HTTP trigger function processed a request.')
        resp_str, status_code = self.orchestrator.extract_name(req)
        return func.HttpResponse(resp_str, status_code=status_code)

    @app.function_name(name="auth_login")
    @app.route(methods=["POST"], route="auth/login", auth_level=func.AuthLevel.FUNCTION)
    def auth_login(self, req: func.HttpRequest) -> func.HttpResponse:
        auth_handler = AuthHandler()
        return auth_handler.login(req)

    @app.function_name(name="auth_refresh")
    @app.route(methods=["POST"], route="auth/refresh", auth_level=func.AuthLevel.FUNCTION)
    def auth_refresh(self, req: func.HttpRequest) -> func.HttpResponse:
        auth_handler = AuthHandler()
        return auth_handler.refresh(req)

    @app.function_name(name="start_conv")
    @app.route(methods=["POST"], route="conversations", auth_level=func.AuthLevel.FUNCTION)
    def start_conv(self, req: func.HttpRequest) -> func.HttpResponse:
        claims = self.orchestrator.require_auth(req)
        if not isinstance(claims, dict):
            return claims

        body = req.get_json()
        domain = body.get("domain")
        if not self.orchestrator.agent_manager.get_agent(domain):
            return func.HttpResponse("Invalid domain", status_code=400)

        conv_id = str(uuid.uuid4())
        self.orchestrator.conversation_manager.create_conversation(conv_id, domain)
        return func.HttpResponse(json.dumps({"conversationId": conv_id}),
                                 mimetype="application/json", status_code=201)

    @app.function_name(name="post_message")
    @app.route(methods=["POST"], route="conversations/{id}/messages", auth_level=func.AuthLevel.FUNCTION)
    async def post_message(self, req: func.HttpRequest) -> func.HttpResponse:
        claims = self.orchestrator.require_auth(req)
        if not isinstance(claims, dict):
            return claims
        convid = req.routeparams.get("id")
        body = req.get_json()
        user_input = body.get("message", "")
        # Fetch conversation 
        conv = self.orchestrator.conversation_manager.get_conversation(convid)
        if not conv:
            return func.HttpResponse("Conversation not found", status_code=404)

        domain = conv["domain"]
        user_msg = {"sender": "user", "text": user_input,
                    "time": datetime.datetime.utcnow().isoformat()}
        conv["messages"].append(user_msg)

        # Call the domain agent using encapsulated method
        answer_json = await self.orchestrator.agent_manager.ask_agent(domain, user_input)
        # Upsert conversation and create agent_msg inside CosmosManager
        self.orchestrator.conversation_manager.upsert_conversation(conv, domain, answer_json)

        return func.HttpResponse(answer_json,
                                 mimetype="application/json")

    @app.function_name(name="get_messages")
    @app.route(methods=["GET"], route="conversations/{id}/messages", auth_level=func.AuthLevel.FUNCTION)
    def get_messages(self, req: func.HttpRequest) -> func.HttpResponse:
        claims = self.orchestrator.require_auth(req)
        if not isinstance(claims, dict):
            return claims
        convid = req.routeparams.get("id")
        conv_json = self.orchestrator.conversation_manager.get_conversation(convid)
        if not conv_json:
            return func.HttpResponse("Not found", status_code=404)

        return func.HttpResponse(conv_json, mimetype="application/json")

    @app.function_name(name="mentor_test")
    @app.route(methods=["POST"], route="mentor/test", auth_level=func.AuthLevel.FUNCTION)
    async def mentor_test(self, req: func.HttpRequest) -> func.HttpResponse:
        body = req.get_json()
        domain = body.get("domain")
        question= body.get("question")
        agent_func = self.orchestrator.agent_manager.get_agent(domain)
        if not agent_func or not question:
            return func.HttpResponse("domain and question required", status_code=400)

        # Invoke the same semantic agent for testing
        answer_json = await self.orchestrator.agent_manager.ask_agent(domain, question)
        return func.HttpResponse(
            answer_json,
            mimetype="application/json",
            status_code=200
        )

    @app.function_name(name="mentor_submit_qa")
    @app.route(methods=["POST"], route="mentor/qapair", auth_level=func.AuthLevel.FUNCTION)
    def mentorsubmitqa(self, req: func.HttpRequest) -> func.HttpResponse:
        body = req.get_json()
        domain = body.get("domain")
        q = body.get("question")
        a = body.get("answer")
        if not domain or not q or not a:
            return func.HttpResponse("domain, question, answer required", status_code=400)

        # Append to mentor Q&A blob for that domain
        self.orchestrator.training_data_manager.upload_mentor_qa_pair(domain, q, a)
        return func.HttpResponse(status_code=201)

    @app.function_name(name="mentor_list_qa")
    @app.route(methods=["GET"], route="mentor/qapairs", auth_level=func.AuthLevel.FUNCTION)
    def mentorlistqa(self, req: func.HttpRequest) -> func.HttpResponse:
        domain = req.params.get("domain")
        if not domain:
            return func.HttpResponse("domain query param required", status_code=400)

        pairs_json = self.orchestrator.training_data_manager.get_mentor_qa_pairs(domain)
        return func.HttpResponse(pairs_json, mimetype="application/json")

    @app.function_name(name="mentor_trigger_fine_tune")
    @app.route(methods=["POST"], route="mentor/fine-tune", auth_level=func.AuthLevel.FUNCTION)
    def mentortriggerfine_tune(self, req: func.HttpRequest) -> func.HttpResponse:
        body = req.get_json()
        domain = body.get("domain")
        if not domain:
            return func.HttpResponse("domain required", status_code=400)

        # Invoke the pipeline endpoint using MLClientManager encapsulation
        result_json = self.orchestrator.ml_client_manager.invoke_pipeline(domain)
        return func.HttpResponse(
            result_json,
            mimetype="application/json",
            status_code=202
        )

    @app.function_name(name="list_agents")
    @app.route(methods=["GET"], route="agents")
    def list_agents(self, req: HttpRequest) -> HttpResponse:
        claims = self.orchestrator.require_auth(req)
        if not isinstance(claims, dict):
            return claims

        # Get agent profiles from AgentManager
        agents_json = self.orchestrator.agent_manager.get_agent_profiles()
        return HttpResponse(
            agents_json,
            mimetype="application/json",
            status_code=200
        )

    @app.function_name(name="get_agent")
    @app.route(methods=["GET"], route="agents/{agentId}")
    def get_agent(self, req: HttpRequest) -> HttpResponse:
        claims = self.orchestrator.require_auth(req)
        if not isinstance(claims, dict):
            return claims

        aid = req.route_params.get("agentId")
        prof_json = self.orchestrator.agent_manager.get_agent_profile(aid)
        if not prof_json:
            return HttpResponse("Agent not found", status_code=404)

        return HttpResponse(
            prof_json,
            mimetype="application/json",
            status_code=200
        )

    @app.function_name(name="chat_agent")
    @app.route(methods=["POST"], route="chat/{agentId}")
    async def chat(self, req: func.HttpRequest):
        claims = self.orchestrator.require_auth(req)
        if not isinstance(claims, dict):
            return claims

        aid = req.route_params["agentId"]
        msg = req.get_json().get("message")
        answer_json = await self.orchestrator.agent_manager.ask_agent(aid, msg)
        if not answer_json:
            return func.HttpResponse("Unknown agent", status_code=400)
        return func.HttpResponse(answer_json, mimetype="application/json")

router = Router()