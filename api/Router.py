import json, uuid, datetime
import logging
import azure.functions as func
from azure.functions import HttpRequest, HttpResponse

from api.Orchestrator import Orchestrator

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
        return self.orchestrator.login(req)

    @app.function_name(name="auth_refresh")
    @app.route(methods=["POST"], route="auth/refresh", auth_level=func.AuthLevel.FUNCTION)
    def auth_refresh(self, req: func.HttpRequest) -> func.HttpResponse:
        return self.orchestrator.refresh(req)

    @app.function_name(name="start_conv")
    @app.route(methods=["POST"], route="conversations", auth_level=func.AuthLevel.FUNCTION)
    def start_conv(self, req: func.HttpRequest) -> func.HttpResponse:
        return self.orchestrator.start_conversation(req)

    @app.function_name(name="post_message")
    @app.route(methods=["POST"], route="conversations/{id}/messages", auth_level=func.AuthLevel.FUNCTION)
    async def post_message(self, req: func.HttpRequest) -> func.HttpResponse:
        return await self.orchestrator.post_message(req)

    @app.function_name(name="get_messages")
    @app.route(methods=["GET"], route="conversations/{id}/messages", auth_level=func.AuthLevel.FUNCTION)
    def get_messages(self, req: func.HttpRequest) -> func.HttpResponse:
        return self.orchestrator.get_messages(req)

    @app.function_name(name="mentor_test")
    @app.route(methods=["POST"], route="mentor/test", auth_level=func.AuthLevel.FUNCTION)
    async def mentor_test(self, req: func.HttpRequest) -> func.HttpResponse:
        return await self.orchestrator.mentor_test(req)

    @app.function_name(name="mentor_submit_qa")
    @app.route(methods=["POST"], route="mentor/qapair", auth_level=func.AuthLevel.FUNCTION)
    def mentorsubmitqa(self, req: func.HttpRequest) -> func.HttpResponse:
        return self.orchestrator.mentorsubmitqa(req)

    @app.function_name(name="mentor_list_qa")
    @app.route(methods=["GET"], route="mentor/qapairs", auth_level=func.AuthLevel.FUNCTION)
    def mentorlistqa(self, req: func.HttpRequest) -> func.HttpResponse:
        return self.orchestrator.mentorlistqa(req)

    @app.function_name(name="mentor_trigger_fine_tune")
    @app.route(methods=["POST"], route="mentor/fine-tune", auth_level=func.AuthLevel.FUNCTION)
    def mentortriggerfine_tune(self, req: func.HttpRequest) -> func.HttpResponse:
        return self.orchestrator.mentortriggerfine_tune(req)

    @app.function_name(name="list_agents")
    @app.route(methods=["GET"], route="agents")
    def list_agents(self, req: HttpRequest) -> HttpResponse:
        return self.orchestrator.list_agents(req)

    @app.function_name(name="get_agent")
    @app.route(methods=["GET"], route="agents/{agentId}")
    def get_agent(self, req: HttpRequest) -> HttpResponse:
        return self.orchestrator.get_agent(req)

    @app.function_name(name="chat_agent")
    @app.route(methods=["POST"], route="chat/{agentId}")
    async def chat(self, req: func.HttpRequest):
        return await self.orchestrator.chat(req)

router = Router()