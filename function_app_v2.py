import json
import logging
import azure.functions as func
from pathlib import Path

# Import FastAPI app for ASGI handling
try:
    from app.app import app as fastapi_app
    # For the main HTTP routes, use ASGI
    app = func.AsgiFunctionApp(app=fastapi_app, http_auth_level=func.AuthLevel.ANONYMOUS)
except Exception as e:
    logging.error(f"Failed to create ASGI app: {e}")
    # Fallback to regular function app
    app = func.FunctionApp()

# Create a separate function app for non-HTTP triggers
function_app = func.FunctionApp()

# Health check function (replaces dashboard/health)
@function_app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def health(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    return func.HttpResponse(
        json.dumps({"ok": True}),
        mimetype="application/json",
        status_code=200
    )

# MCP endpoint function (replaces dashboard/mcp_endpoint) 
@function_app.route(route="mcp", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
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
@function_app.route(route="manifest", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
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
@function_app.queue_trigger(arg_name="msg", queue_name="%QUEUE_AGENT_EVENTS%", 
                   connection="AZURE_QUEUES_CONNECTION_STRING")
async def agent_events_trigger(msg: func.QueueMessage):
    """Agent events queue trigger"""
    data = json.loads(msg.get_body().decode("utf-8"))
    
    try:
        from app.governance import validate_request, GovernanceError
        from app.storage import to_row, table
        
        validate_request("message", {"role": data.get("role"), "payload": data})
        row = to_row(data["boardroomId"], data["conversationId"], data)
        with table() as t:
            t.create_entity(row)
    except ImportError as e:
        logging.error(f"Failed to import dependencies: {e}")
        return
    except Exception as ge:
        logging.warning(f"Message rejected by governance: {ge}")
        return

# Service Bus trigger function (replaces framework/functions/processdecisionevent)
@function_app.service_bus_topic_trigger(arg_name="msg", topic_name="bi-events", 
                              subscription_name="governance",
                              connection="AZURE_SERVICE_BUS_CONNECTION_STRING")
def process_decision_event(msg: func.ServiceBusMessage):
    """Process decision events from service bus"""
    body = msg.get_body().decode("utf-8")
    subject = msg.subject
    logging.info(f"[GOV] Event: {subject} Payload: {body}")
    # Add side effects: persist to Cosmos DB, trigger notifications, etc.