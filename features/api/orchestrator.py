import os, json, uuid, datetime, requests
from ..environment import env_manager
from ..agents import agent_manager
from ..storage import storage_manager
from ..ml_pipeline import ml_manager

from ..authentication import validate_jwt, UNAUTHORIZED_MSG

class Orchestrator:
    def handle_servicebus_message(self, message_body):
        """
        Handle messages received from Azure Service Bus queue trigger.
        You can add custom business logic here, e.g. process, store, or forward the message.
        """
        import logging
        logging.info(f"Processing Service Bus message: {message_body}")
        # Example: Add your business logic here
        return True
    def linkedin_auth_redirect(self, req):
        # Redirect user to LinkedIn OAuth
        client_id = "YOUR_LINKEDIN_CLIENT_ID"
        redirect_uri = "YOUR_REDIRECT_URI"  # e.g. https://yourapp.com/auth/linkedin/callback
        state = str(uuid.uuid4())
        linkedin_auth_url = (
            f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={client_id}"
            f"&redirect_uri={redirect_uri}&state={state}&scope=r_liteprofile%20r_emailaddress"
        )
        return {"redirect_url": linkedin_auth_url, "mimetype": "text/html"}

    def linkedin_auth_callback(self, req):
        # Exchange code for access token and get user info
        import requests, json
        code = req.params.get("code")
        state = req.params.get("state")
        client_id = "YOUR_LINKEDIN_CLIENT_ID"
        client_secret = "YOUR_LINKEDIN_CLIENT_SECRET"
        redirect_uri = "YOUR_REDIRECT_URI"
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret
        }
        token_resp = requests.post(token_url, data=data)
        token_json = token_resp.json()
        access_token = token_json.get("access_token")
        # Get user info
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_resp = requests.get("https://api.linkedin.com/v2/me", headers=headers)
        email_resp = requests.get("https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))", headers=headers)
        profile = profile_resp.json()
        email = email_resp.json()["elements"][0]["handle~"]["emailAddress"]
        # Here, create or update user in your system, issue JWT, etc.
        # For demo, just return profile and email
        return {"profile": profile, "email": email, "mimetype": "application/json"}
    def __init__(self):
        self.env = env_manager
        self.STORAGE_CONN = env_manager.get_required("AzureWebJobsStorage")
        self.MLURL = env_manager.get_required("MLENDPOINT_URL")
        self.MLKEY = env_manager.get_required("MLENDPOINT_KEY")

        # Use consolidated managers
        self.storage_manager = storage_manager
        self.agent_manager = agent_manager
        self.ml_manager = ml_manager
        
        # Get agent data from storage manager
        self.AGENTDIRS = self.storage_manager.get_agent_dirs()
        self.AGENTPROFILES = self.storage_manager.get_agent_profiles()
        self.DOMAINKNOW = self.storage_manager.get_domain_knowledge()

    def start_conversation(self, req):
        claims = self.require_auth(req)
        if not isinstance(claims, dict):
            return {"error": "unauthorized", "status_code": 401}

        body = req.get_json()
        domain = body.get("domain")
        if not self.agent_manager.get_agent(domain):
            return {"error": "Invalid domain", "status_code": 400}

        conv_id = str(uuid.uuid4())
        self.storage_manager.create_conversation(conv_id, domain)
        return {"conversationId": conv_id, "status_code": 201}

    async def post_message(self, req):
        claims = self.require_auth(req)
        if not isinstance(claims, dict):
            return {"error": "unauthorized", "status_code": 401}
        convid = req.routeparams.get("id")
        body = req.get_json()
        user_input = body.get("message", "")
        conv = self.storage_manager.get_conversation(convid)
        if not conv:
            return {"error": "Conversation not found", "status_code": 404}

        # Parse conversation JSON
        conv_data = json.loads(conv) if isinstance(conv, str) else conv
        domain = conv_data["domain"]
        user_msg = {"sender": "user", "text": user_input,
                    "time": datetime.datetime.utcnow().isoformat()}
        messages = conv_data.get("messages", [])
        if isinstance(messages, str):
            messages = json.loads(messages)
        messages.append(user_msg)
        conv_data["messages"] = messages
        
        answer_json = await self.agent_manager.ask_agent(domain, user_input)
        self.storage_manager.upsert_conversation(conv_data, domain, answer_json)
        return {"answer_json": answer_json, "status_code": 200}

    def get_messages(self, req):
        claims = self.require_auth(req)
        if not isinstance(claims, dict):
            return {"error": "unauthorized", "status_code": 401}
        convid = req.routeparams.get("id")
        conv_json = self.storage_manager.get_conversation(convid)
        if not conv_json:
            return {"error": "Not found", "status_code": 404}
        return {"conv_json": conv_json, "status_code": 200}

    async def mentor_test(self, req):
        body = req.get_json()
        domain = body.get("domain")
        question= body.get("question")
        agent_func = self.agent_manager.get_agent(domain)
        if not agent_func or not question:
            return {"error": "domain and question required", "status_code": 400}
        answer_json = await self.agent_manager.ask_agent(domain, question)
        return {"answer_json": answer_json, "status_code": 200}

    def mentorsubmitqa(self, req):
        body = req.get_json()
        domain = body.get("domain")
        q = body.get("question")
        a = body.get("answer")
        if not domain or not q or not a:
            return {"error": "domain, question, answer required", "status_code": 400}
        self.storage_manager.upload_mentor_qa_pair(domain, q, a)
        return {"status_code": 201}

    def mentorlistqa(self, req):
        domain = req.params.get("domain")
        if not domain:
            return {"error": "domain query param required", "status_code": 400}
        pairs_json = self.storage_manager.get_mentor_qa_pairs(domain)
        return {"pairs_json": pairs_json, "status_code": 200}

    def mentortriggerfine_tune(self, req):
        body = req.get_json()
        domain = body.get("domain")
        if not domain:
            return {"error": "domain required", "status_code": 400}
        result_json = self.ml_manager.invoke_pipeline(domain)
        return {"result_json": result_json, "status_code": 202}

    def list_agents(self, req):
        claims = self.require_auth(req)
        if not isinstance(claims, dict):
            return {"error": "unauthorized", "status_code": 401}
        agents_json = self.agent_manager.get_agent_profiles()
        return {"agents_json": agents_json, "status_code": 200}

    def get_agent(self, req):
        claims = self.require_auth(req)
        if not isinstance(claims, dict):
            return {"error": "unauthorized", "status_code": 401}
        aid = req.route_params.get("agentId")
        prof_json = self.agent_manager.get_agent_profile(aid)
        if not prof_json:
            return {"error": "Agent not found", "status_code": 404}
        return {"prof_json": prof_json, "status_code": 200}

    async def chat(self, req):
        claims = self.require_auth(req)
        if not isinstance(claims, dict):
            return {"error": "unauthorized", "status_code": 401}
        aid = req.route_params["agentId"]
        msg = req.get_json().get("message")
        answer_json = await self.agent_manager.ask_agent(aid, msg)
        if not answer_json:
            return {"error": "Unknown agent", "status_code": 400}
        return {"answer_json": answer_json, "status_code": 200}

    def login(self, req):
        from core.api.AuthHandler import AuthHandler
        auth_handler = AuthHandler()
        return auth_handler.login(req)

    def refresh(self, req):
        from core.api.AuthHandler import AuthHandler
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
            return {"message": f"Hello, {name}. This HTTP triggered function executed successfully.", "status_code": 200}
        else:
            return {
                "message": "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
                "status_code": 200
            }

    def require_auth(self, req):
        claims = validate_jwt.from_request(req)
        if not claims:
            return None
        return claims
