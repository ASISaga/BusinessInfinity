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
