"""
HTTP Route Triggers for Azure Functions

This module contains all HTTP route handlers consolidated from function_app.py
"""

import json
import logging
import azure.functions as func
from pathlib import Path
import uuid

# Import consolidated feature modules
from agents import agent_manager
from ml_pipeline import ml_manager
from storage import storage_manager
from environment import env_manager

from dashboard.mcp_handlers import handle_mcp
from utils.governance import validate_request, GovernanceError

# === Assimilated from utils/app.py ===
from utils.manifest import get_ui_schema
from utils.storage import enqueue_request, query_messages
from utils.aml import aml_infer as utils_aml_infer, aml_train as utils_aml_train
from utils.models import UiAction, Envelope


def register_http_routes(app: func.FunctionApp):
    """Register all HTTP route handlers with the FunctionApp"""
    
    # FastAPI ASGI integration - simplified approach
    @app.route(route="{*route}", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "POST", "PUT", "DELETE"])
    async def http_asgi(req: func.HttpRequest) -> func.HttpResponse:
        """ASGI HTTP handler for FastAPI routes - simplified for V2 migration"""
        try:
            # For now, just return the original ASGI functionality placeholder
            # The actual FastAPI routes can be accessed via the individual route handlers below
            return func.HttpResponse(
                json.dumps({"message": "ASGI routes available via specific endpoints", "route": req.route_params.get('route', '')}),
                status_code=200,
                mimetype="application/json"
            )
        except Exception as e:
            logging.error(f"ASGI handler error: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Internal server error"}),
                status_code=500,
                mimetype="application/json"
            )

    # Health check function (replaces dashboard/health)
    @app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
    async def health(req: func.HttpRequest) -> func.HttpResponse:
        """Health check endpoint"""
        return func.HttpResponse(
            json.dumps({"ok": True}),
            mimetype="application/json",
            status_code=200
        )

    # === Assimilated FastAPI endpoints from utils/app.py ===

    # /dashboard
    @app.route(route="dashboard", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
    async def get_dashboard(req: func.HttpRequest) -> func.HttpResponse:
        role = req.params.get("role")
        scope = req.params.get("scope", "local")
        schema = get_ui_schema(role, scope)
        return func.HttpResponse(
            json.dumps({"uiSchema": schema}),
            mimetype="application/json",
            status_code=200
        )

    # /messages
    @app.route(route="messages", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
    async def get_messages(req: func.HttpRequest) -> func.HttpResponse:
        boardroomId = req.params.get("boardroomId")
        conversationId = req.params.get("conversationId")
        since = req.params.get("since")
        rows = query_messages(boardroomId, conversationId, since)
        return func.HttpResponse(
            json.dumps({"messages": rows}),
            mimetype="application/json",
            status_code=200
        )

    # /action
    @app.route(route="action", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
    async def post_action(req: func.HttpRequest) -> func.HttpResponse:
        try:
            body = req.get_json()
            action = UiAction(**body)
            corr = action.correlationId or str(uuid.uuid4())
            env = Envelope(
                correlationId=corr,
                traceId=corr,
                boardroomId=action.boardroomId,
                conversationId=action.conversationId,
                senderAgentId=action.agentId,
                role=action.agentId.upper(),
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
                return func.HttpResponse(
                    json.dumps({"error": str(ge)}),
                    mimetype="application/json",
                    status_code=403
                )
            enqueue_request(env)
            return func.HttpResponse(
                json.dumps({"status": "queued", "correlationId": corr}),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            logging.error(f"Error in /action: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to queue action"}),
                mimetype="application/json",
                status_code=500
            )

    # /aml/infer
    @app.route(route="aml/infer", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
    async def aml_infer_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        try:
            body = req.get_json()
            agentId = body.get("agentId")
            prompt = body.get("prompt")
            try:
                validate_request("inference", {"role": "Governance", "payload": {"agentId": agentId}})
            except GovernanceError as ge:
                return func.HttpResponse(
                    json.dumps({"error": str(ge)}),
                    mimetype="application/json",
                    status_code=403
                )
            res = await utils_aml_infer(agentId, prompt)
            return func.HttpResponse(
                json.dumps(res),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            logging.error(f"Error in /aml/infer: {e}")
            return func.HttpResponse(
                json.dumps({"error": "AML inference failed"}),
                mimetype="application/json",
                status_code=500
            )

    # /aml/train
    @app.route(route="aml/train", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
    async def aml_train_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        try:
            body = req.get_json()
            jobName = body.get("jobName")
            modelName = body.get("modelName")
            datasetUri = body.get("datasetUri")
            demo = body.get("demo", True)
            try:
                validate_request("training", {"role": "Governance", "demo": demo, "payload": {"modelName": modelName}})
            except GovernanceError as ge:
                return func.HttpResponse(
                    json.dumps({"error": str(ge)}),
                    mimetype="application/json",
                    status_code=403
                )
            res = await utils_aml_train(jobName, {"modelName": modelName, "datasetUri": datasetUri})
            return func.HttpResponse(
                json.dumps(res),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            logging.error(f"Error in /aml/train: {e}")
            return func.HttpResponse(
                json.dumps({"error": "AML training failed"}),
                mimetype="application/json",
                status_code=500
            )

    # MCP endpoint function (replaces dashboard/mcp_endpoint) 
    @app.route(route="mcp", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
    async def mcp_endpoint(req: func.HttpRequest) -> func.HttpResponse:
        """MCP endpoint handler"""
        try:
            body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Import handle_mcp locally to avoid import issues
        try:
           
            response = await handle_mcp(body)
        except ImportError as e:
            logging.error(f"Failed to import MCP handler: {e}")
            response = {"error": "MCP handler not available"}
        
        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )

    # Get manifest function (replaces dashboard/get_manifest)
    @app.route(route="manifest", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
    async def get_manifest(req: func.HttpRequest) -> func.HttpResponse:
        """Get manifest endpoint"""
        manifest_path = Path(__file__).parent.parent / "dashboard" / "manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
        except Exception as e:
            logging.error(f"Failed to load manifest: {e}")
            manifest = {"error": "Manifest not available"}
        
        return func.HttpResponse(
            json.dumps(manifest),
            mimetype="application/json",
            status_code=200
        )

    # === New unified API endpoints ===

    @app.route(route="agents", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
    async def list_agents(req: func.HttpRequest) -> func.HttpResponse:
        """List available agents"""
        try:
            agents_json = agent_manager.get_agent_profiles()
            return func.HttpResponse(
                agents_json,
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            logging.error(f"Error listing agents: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to list agents"}),
                mimetype="application/json",
                status_code=500
            )

    @app.route(route="agents/{agent_id}", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
    async def get_agent(req: func.HttpRequest) -> func.HttpResponse:
        """Get specific agent details"""
        try:
            agent_id = req.route_params.get("agent_id")
            profile = agent_manager.get_agent_profile(agent_id)
            if not profile:
                return func.HttpResponse(
                    json.dumps({"error": "Agent not found"}),
                    mimetype="application/json",
                    status_code=404
                )
            return func.HttpResponse(
                profile,
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            logging.error(f"Error getting agent {agent_id}: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to get agent"}),
                mimetype="application/json",
                status_code=500
            )

    @app.route(route="agents/{agent_id}/chat", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
    async def chat_with_agent(req: func.HttpRequest) -> func.HttpResponse:
        """Chat with a specific agent"""
        try:
            agent_id = req.route_params.get("agent_id")
            body = req.get_json()
            message = body.get("message", "")
            
            if not message:
                return func.HttpResponse(
                    json.dumps({"error": "Message is required"}),
                    mimetype="application/json",
                    status_code=400
                )
            
            response = await agent_manager.ask_agent(agent_id, message)
            if not response:
                return func.HttpResponse(
                    json.dumps({"error": "Agent not found or failed to respond"}),
                    mimetype="application/json",
                    status_code=404
                )
            
            return func.HttpResponse(
                response,
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            logging.error(f"Error chatting with agent {agent_id}: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Chat failed"}),
                mimetype="application/json",
                status_code=500
            )

    @app.route(route="ml/infer", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
    async def ml_inference(req: func.HttpRequest) -> func.HttpResponse:
        """Perform ML inference"""
        try:
            body = req.get_json()
            agent_id = body.get("agent_id")
            prompt = body.get("prompt")
            
            if not agent_id or not prompt:
                return func.HttpResponse(
                    json.dumps({"error": "agent_id and prompt are required"}),
                    mimetype="application/json",
                    status_code=400
                )
            
            result = await ml_manager.aml_infer(agent_id, prompt)
            return func.HttpResponse(
                json.dumps(result),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            logging.error(f"Error in ML inference: {e}")
            return func.HttpResponse(
                json.dumps({"error": "ML inference failed"}),
                mimetype="application/json",
                status_code=500
            )

    @app.route(route="conversations", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
    async def create_conversation(req: func.HttpRequest) -> func.HttpResponse:
        """Create a new conversation"""
        try:
            body = req.get_json()
            domain = body.get("domain")
            
            if not domain:
                return func.HttpResponse(
                    json.dumps({"error": "domain is required"}),
                    mimetype="application/json",
                    status_code=400
                )
            
            conv_id = str(uuid.uuid4())
            storage_manager.create_conversation(conv_id, domain)
            
            return func.HttpResponse(
                json.dumps({"conversationId": conv_id}),
                mimetype="application/json",
                status_code=201
            )
        except Exception as e:
            logging.error(f"Error creating conversation: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to create conversation"}),
                mimetype="application/json",
                status_code=500
            )

    @app.route(route="conversations/{conv_id}", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
    async def get_conversation(req: func.HttpRequest) -> func.HttpResponse:
        """Get conversation details"""
        try:
            conv_id = req.route_params.get("conv_id")
            conversation = storage_manager.get_conversation(conv_id)
            
            if not conversation:
                return func.HttpResponse(
                    json.dumps({"error": "Conversation not found"}),
                    mimetype="application/json",
                    status_code=404
                )
            
            return func.HttpResponse(
                conversation,
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            logging.error(f"Error getting conversation {conv_id}: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to get conversation"}),
                mimetype="application/json",
                status_code=500
            )

    @app.route(route="status", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
    async def system_status(req: func.HttpRequest) -> func.HttpResponse:
        """Get system status and configuration validation"""
        try:
            env_status = env_manager.validate_environment()
            storage_status = storage_manager.validate_configuration()
            ml_status = ml_manager.validate_configuration()
            
            status = {
                "environment": env_status,
                "storage": storage_status,
                "ml": ml_status,
                "agents": {
                    "available": agent_manager.list_agent_ids(),
                    "count": len(agent_manager.list_agent_ids())
                }
            }
            
            return func.HttpResponse(
                json.dumps(status),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            logging.error(f"Error getting system status: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to get system status"}),
                mimetype="application/json",
                status_code=500
            )