import json, uuid, datetime
import logging
import azure.functions as func
from azure.functions import HttpRequest, HttpResponse

from api.Orchestrator import Orchestrator

app = func.FunctionApp()

class Router:
    """
    Router class for Azure Functions HTTP API endpoints.
    Each method is decorated with @app.function_name and @app.route to define the HTTP route and method.
    Delegates business logic to the Orchestrator class.
    """
    def __init__(self):
        # Initialize orchestrator for business logic delegation
        self.orchestrator = Orchestrator()

    # Azure Service Bus queue trigger example
    # This function will be triggered when a message arrives in the specified Service Bus queue
    @app.function_name(name="servicebus_queue_trigger")
    @app.service_bus_queue_trigger(arg_name="msg", queue_name="myqueue", connection="AzureServiceBusConnection")
    def servicebus_queue_trigger(self, msg: func.ServiceBusMessage):
        # Process the Service Bus message
        message_body = msg.get_body().decode('utf-8')
        # You can call orchestrator logic or log/process the message as needed
        logging.info(f"Received Service Bus message: {message_body}")
        # Example: pass to orchestrator for custom handling
        self.orchestrator.handle_servicebus_message(message_body)

    # LinkedIn OAuth redirect endpoint
    @app.function_name(name="auth_linkedin")
    @app.route(methods=["GET"], route="auth/linkedin", auth_level=func.AuthLevel.ANONYMOUS)
    def auth_linkedin(self, req: func.HttpRequest) -> func.HttpResponse:
        result = self.orchestrator.linkedin_auth_redirect(req)
        # Returns a script that redirects the browser to LinkedIn OAuth
        return func.HttpResponse(f"<script>window.location.href='{result['redirect_url']}'</script>", mimetype=result["mimetype"])

    # LinkedIn OAuth callback endpoint
    @app.function_name(name="auth_linkedin_callback")
    @app.route(methods=["GET"], route="auth/linkedin/callback", auth_level=func.AuthLevel.ANONYMOUS)
    def auth_linkedin_callback(self, req: func.HttpRequest) -> func.HttpResponse:
        result = self.orchestrator.linkedin_auth_callback(req)
        # Returns user profile and email after LinkedIn authentication
        return func.HttpResponse(json.dumps({"profile": result["profile"], "email": result["email"]}), mimetype=result["mimetype"])

    # Example HTTP trigger endpoint
    @app.function_name(name="http_trigger")
    @app.route(methods=["GET", "POST"], route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
    def http_trigger(self, req: func.HttpRequest) -> func.HttpResponse:
        logging.info('Python HTTP trigger function processed a request.')
        result = self.orchestrator.extract_name(req)
        return func.HttpResponse(result["message"], status_code=result["status_code"])

    # Login endpoint
    @app.function_name(name="auth_login")
    @app.route(methods=["POST"], route="auth/login", auth_level=func.AuthLevel.FUNCTION)
    def auth_login(self, req: func.HttpRequest) -> func.HttpResponse:
        result = self.orchestrator.login(req)
        # Returns login result (token, user info, etc.)
        return result

    # Token refresh endpoint
    @app.function_name(name="auth_refresh")
    @app.route(methods=["POST"], route="auth/refresh", auth_level=func.AuthLevel.FUNCTION)
    def auth_refresh(self, req: func.HttpRequest) -> func.HttpResponse:
        result = self.orchestrator.refresh(req)
        # Returns refreshed token
        return result

    # Start a new conversation
    @app.function_name(name="start_conv")
    @app.route(methods=["POST"], route="conversations", auth_level=func.AuthLevel.FUNCTION)
    def start_conv(self, req: func.HttpRequest) -> func.HttpResponse:
        result = self.orchestrator.start_conversation(req)
        if "error" in result:
            return func.HttpResponse(result["error"], status_code=result["status_code"])
        return func.HttpResponse(json.dumps({"conversationId": result["conversationId"]}), mimetype="application/json", status_code=result["status_code"])

    # Post a message to a conversation
    @app.function_name(name="post_message")
    @app.route(methods=["POST"], route="conversations/{id}/messages", auth_level=func.AuthLevel.FUNCTION)
    async def post_message(self, req: func.HttpRequest) -> func.HttpResponse:
        result = await self.orchestrator.post_message(req)
        if "error" in result:
            return func.HttpResponse(result["error"], status_code=result["status_code"])
        return func.HttpResponse(result["answer_json"], mimetype="application/json", status_code=result["status_code"])

    # Get all messages for a conversation
    @app.function_name(name="get_messages")
    @app.route(methods=["GET"], route="conversations/{id}/messages", auth_level=func.AuthLevel.FUNCTION)
    def get_messages(self, req: func.HttpRequest) -> func.HttpResponse:
        result = self.orchestrator.get_messages(req)
        if "error" in result:
            return func.HttpResponse(result["error"], status_code=result["status_code"])
        return func.HttpResponse(result["conv_json"], mimetype="application/json", status_code=result["status_code"])

    # Mentor test endpoint
    @app.function_name(name="mentor_test")
    @app.route(methods=["POST"], route="mentor/test", auth_level=func.AuthLevel.FUNCTION)
    async def mentor_test(self, req: func.HttpRequest) -> func.HttpResponse:
        result = await self.orchestrator.mentor_test(req)
        if "error" in result:
            return func.HttpResponse(result["error"], status_code=result["status_code"])
        return func.HttpResponse(result["answer_json"], mimetype="application/json", status_code=result["status_code"])

    # Submit mentor Q&A pair
    @app.function_name(name="mentor_submit_qa")
    @app.route(methods=["POST"], route="mentor/qapair", auth_level=func.AuthLevel.FUNCTION)
    def mentorsubmitqa(self, req: func.HttpRequest) -> func.HttpResponse:
        result = self.orchestrator.mentorsubmitqa(req)
        if "error" in result:
            return func.HttpResponse(result["error"], status_code=result["status_code"])
        return func.HttpResponse(status_code=result["status_code"])

    # List mentor Q&A pairs
    @app.function_name(name="mentor_list_qa")
    @app.route(methods=["GET"], route="mentor/qapairs", auth_level=func.AuthLevel.FUNCTION)
    def mentorlistqa(self, req: func.HttpRequest) -> func.HttpResponse:
        result = self.orchestrator.mentorlistqa(req)
        if "error" in result:
            return func.HttpResponse(result["error"], status_code=result["status_code"])
        return func.HttpResponse(result["pairs_json"], mimetype="application/json", status_code=result["status_code"])

    # Trigger mentor fine-tuning
    @app.function_name(name="mentor_trigger_fine_tune")
    @app.route(methods=["POST"], route="mentor/fine-tune", auth_level=func.AuthLevel.FUNCTION)
    def mentortriggerfine_tune(self, req: func.HttpRequest) -> func.HttpResponse:
        result = self.orchestrator.mentortriggerfine_tune(req)
        if "error" in result:
            return func.HttpResponse(result["error"], status_code=result["status_code"])
        return func.HttpResponse(result["result_json"], mimetype="application/json", status_code=result["status_code"])

    # List all agents
    @app.function_name(name="list_agents")
    @app.route(methods=["GET"], route="agents")
    def list_agents(self, req: HttpRequest) -> HttpResponse:
        result = self.orchestrator.list_agents(req)
        if "error" in result:
            return HttpResponse(result["error"], status_code=result["status_code"])
        return HttpResponse(result["agents_json"], mimetype="application/json", status_code=result["status_code"])

    # Get agent profile by agentId
    @app.function_name(name="get_agent")
    @app.route(methods=["GET"], route="agents/{agentId}")
    def get_agent(self, req: HttpRequest) -> HttpResponse:
        result = self.orchestrator.get_agent(req)
        if "error" in result:
            return HttpResponse(result["error"], status_code=result["status_code"])
        return HttpResponse(result["prof_json"], mimetype="application/json", status_code=result["status_code"])

    # Chat with agent by agentId
    @app.function_name(name="chat_agent")
    @app.route(methods=["POST"], route="chat/{agentId}")
    async def chat(self, req: func.HttpRequest):
        result = await self.orchestrator.chat(req)
        if "error" in result:
            return func.HttpResponse(result["error"], status_code=result["status_code"])
        return func.HttpResponse(result["answer_json"], mimetype="application/json", status_code=result["status_code"])

router = Router()