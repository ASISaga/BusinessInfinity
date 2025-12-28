import json
import azure.functions as func

class MentorEndpoint:
    def __init__(self, business_infinity=None, logger=None):
        self.business_infinity = business_infinity
        self.logger = logger

    async def mentor_list_agents(self, req: func.HttpRequest) -> func.HttpResponse:
        try:
            if self.business_infinity and hasattr(self.business_infinity, 'mentor_mode') and self.business_infinity.mentor_mode:
                agents = await self.business_infinity.mentor_mode.list_agents_with_lora()
                return func.HttpResponse(
                    json.dumps({"agents": agents}),
                    mimetype="application/json",
                    status_code=200
                )
            elif self.business_infinity:
                agents = self.business_infinity.list_agents()
                mentor_agents = []
                for agent in agents:
                    mentor_agents.append({
                        "id": agent.get("role", agent.get("name", "unknown")).lower(),
                        "name": agent.get("name", agent.get("role", "Unknown Agent")),
                        "loraVersion": "v1.0.0",
                        "capabilities": ["chat", "fine-tune"],
                        "status": "available"
                    })
                return func.HttpResponse(
                    json.dumps({"agents": mentor_agents}),
                    mimetype="application/json",
                    status_code=200
                )
            else:
                return func.HttpResponse(
                    json.dumps({"agents": [], "error": "Business Infinity not available"}),
                    mimetype="application/json",
                    status_code=503
                )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error listing mentor agents: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    async def mentor_chat_with_agent(self, req: func.HttpRequest) -> func.HttpResponse:
        try:
            agent_id = req.route_params.get('agent_id')
            if not agent_id:
                return func.HttpResponse(
                    json.dumps({"error": "Agent ID required"}),
                    mimetype="application/json",
                    status_code=400
                )
            try:
                req_body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    mimetype="application/json",
                    status_code=400
                )
            message = req_body.get('message', '')
            if not message:
                return func.HttpResponse(
                    json.dumps({"error": "Message is required"}),
                    mimetype="application/json",
                    status_code=400
                )
            if self.business_infinity:
                if hasattr(self.business_infinity, 'mentor_mode') and self.business_infinity.mentor_mode:
                    response = await self.business_infinity.mentor_mode.chat_with_agent(agent_id, message)
                else:
                    response = await self.business_infinity.ask_agent(agent_id.upper(), message)
                return func.HttpResponse(
                    json.dumps({
                        "agentId": agent_id,
                        "response": response,
                        "timestamp": json.dumps(None, default=str),
                        "system": "mentor_mode"
                    }),
                    mimetype="application/json",
                    status_code=200
                )
            else:
                return func.HttpResponse(
                    json.dumps({"error": "Business Infinity not available"}),
                    mimetype="application/json",
                    status_code=503
                )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in mentor chat with agent {agent_id}: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    async def mentor_fine_tune_agent(self, req: func.HttpRequest) -> func.HttpResponse:
        try:
            agent_id = req.route_params.get('agent_id')
            if not agent_id:
                return func.HttpResponse(
                    json.dumps({"error": "Agent ID required"}),
                    mimetype="application/json",
                    status_code=400
                )
            try:
                req_body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    mimetype="application/json",
                    status_code=400
                )
            dataset_id = req_body.get('datasetId', '')
            if not dataset_id:
                return func.HttpResponse(
                    json.dumps({"error": "Dataset ID is required"}),
                    mimetype="application/json",
                    status_code=400
                )
            if self.business_infinity and hasattr(self.business_infinity, 'mentor_mode') and self.business_infinity.mentor_mode:
                job = await self.business_infinity.mentor_mode.start_fine_tune_job(agent_id, dataset_id)
                return func.HttpResponse(
                    json.dumps(job),
                    mimetype="application/json",
                    status_code=200
                )
            else:
                return func.HttpResponse(
                    json.dumps({
                        "jobId": f"job_{agent_id}_{dataset_id[:8]}",
                        "status": "queued",
                        "startTime": json.dumps(None, default=str),
                        "message": "Fine-tuning job queued (mentor mode not fully available)"
                    }),
                    mimetype="application/json",
                    status_code=200
                )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error starting fine-tune job for agent {agent_id}: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    async def mentor_get_training_logs(self, req: func.HttpRequest) -> func.HttpResponse:
        try:
            job_id = req.route_params.get('job_id')
            if not job_id:
                return func.HttpResponse(
                    json.dumps({"error": "Job ID required"}),
                    mimetype="application/json",
                    status_code=400
                )
            if self.business_infinity and hasattr(self.business_infinity, 'mentor_mode') and self.business_infinity.mentor_mode:
                logs = await self.business_infinity.mentor_mode.get_training_logs(job_id)
                return func.HttpResponse(
                    json.dumps({"logs": logs}),
                    mimetype="application/json",
                    status_code=200
                )
            else:
                return func.HttpResponse(
                    json.dumps({
                        "logs": [
                            f"[INFO] Training job {job_id} started",
                            "[INFO] Loading dataset...",
                            "[INFO] Mentor mode not fully initialized - returning mock logs",
                            "[WARNING] Full mentor mode functionality requires additional setup"
                        ]
                    }),
                    mimetype="application/json",
                    status_code=200
                )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting training logs for job {job_id}: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    async def mentor_deploy_adapter(self, req: func.HttpRequest) -> func.HttpResponse:
        try:
            agent_id = req.route_params.get('agent_id')
            if not agent_id:
                return func.HttpResponse(
                    json.dumps({"error": "Agent ID required"}),
                    mimetype="application/json",
                    status_code=400
                )
            try:
                req_body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    mimetype="application/json",
                    status_code=400
                )
            version = req_body.get('version', '')
            if not version:
                return func.HttpResponse(
                    json.dumps({"error": "Version is required"}),
                    mimetype="application/json",
                    status_code=400
                )
            if self.business_infinity and hasattr(self.business_infinity, 'mentor_mode') and self.business_infinity.mentor_mode:
                result = await self.business_infinity.mentor_mode.deploy_adapter(agent_id, version)
                return func.HttpResponse(
                    json.dumps(result),
                    mimetype="application/json",
                    status_code=200
                )
            else:
                return func.HttpResponse(
                    json.dumps({
                        "success": True,
                        "agentId": agent_id,
                        "version": version,
                        "deployedAt": json.dumps(None, default=str),
                        "message": "Adapter deployment queued (mentor mode not fully available)"
                    }),
                    mimetype="application/json",
                    status_code=200
                )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error deploying adapter for agent {agent_id}: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

    async def mentor_mode_ui(self, req: func.HttpRequest) -> func.HttpResponse:
        try:
            import os
            html_path = os.path.join(os.path.dirname(__file__), 'dashboard', 'mentor_mode.html')
            if os.path.exists(html_path):
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                return func.HttpResponse(
                    html_content,
                    mimetype="text/html",
                    status_code=200
                )
            else:
                return func.HttpResponse(
                    "<html><body><h1>Mentor Mode UI</h1><p>UI file not found</p></body></html>",
                    mimetype="text/html",
                    status_code=404
                )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error serving mentor mode UI: {e}")
            return func.HttpResponse(
                f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>",
                mimetype="text/html",
                status_code=500
            )