import json
import logging
import azure.functions as func
from pathlib import Path

# Import consolidated core modules
from core.agents import agent_manager
from core.ml import ml_manager
from core.storage import storage_manager
from core.environment import env_manager

# Create the main function app instance  
app = func.FunctionApp()

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
        from dashboard.mcp_handlers import handle_mcp
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
    manifest_path = Path(__file__).parent / "dashboard" / "manifest.json"
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

# Queue trigger function (replaces functions/agent_events_trigger)
@app.queue_trigger(arg_name="msg", queue_name="%QUEUE_AGENT_EVENTS%", 
                   connection="AZURE_QUEUES_CONNECTION_STRING")
async def agent_events_trigger(msg: func.QueueMessage):
    """Agent events queue trigger"""
    data = json.loads(msg.get_body().decode("utf-8"))
    
    try:
        from app.governance import validate_request, GovernanceError
        
        validate_request("message", {"role": data.get("role"), "payload": data})
        row = storage_manager.to_row(data["boardroomId"], data["conversationId"], data)
        with storage_manager.get_table_client() as t:
            t.create_entity(row)
    except ImportError as e:
        logging.error(f"Failed to import dependencies: {e}")
        return
    except Exception as ge:
        logging.warning(f"Message rejected by governance: {ge}")
        return

# Service Bus trigger function (replaces framework/functions/processdecisionevent)
@app.service_bus_topic_trigger(arg_name="msg", topic_name="bi-events", 
                              subscription_name="governance",
                              connection="AZURE_SERVICE_BUS_CONNECTION_STRING")
def process_decision_event(msg: func.ServiceBusMessage):
    """Process decision events from service bus"""
    body = msg.get_body().decode("utf-8")
    subject = msg.subject
    logging.info(f"[GOV] Event: {subject} Payload: {body}")
    # Add side effects: persist to Cosmos DB, trigger notifications, etc.

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
        import uuid
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