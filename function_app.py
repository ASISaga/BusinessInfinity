import json
import logging
import azure.functions as func
from pathlib import Path

# Create the main function app instance  
app = func.FunctionApp()

# FastAPI ASGI integration - handle as regular HTTP function for now
@app.route(route="{*route}", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "POST", "PUT", "DELETE"])
async def http_asgi(req: func.HttpRequest) -> func.HttpResponse:
    """ASGI HTTP handler for FastAPI routes"""
    try:
        from app.app import app as fastapi_app
        from fastapi.testclient import TestClient
        import asyncio
        
        # Simple ASGI handling - in production would use proper ASGI middleware
        client = TestClient(fastapi_app)
        
        # Convert Azure Functions request to FastAPI format
        method = req.method
        url = f"/{req.route_params.get('route', '')}"
        headers = dict(req.headers)
        body = req.get_body()
        
        # Make request to FastAPI app
        if method == "GET":
            response = client.get(url, headers=headers, params=dict(req.params))
        elif method == "POST":
            response = client.post(url, headers=headers, content=body)
        else:
            response = client.request(method, url, headers=headers, content=body)
        
        return func.HttpResponse(
            response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            mimetype=response.headers.get("content-type", "application/json")
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
@app.service_bus_topic_trigger(arg_name="msg", topic_name="bi-events", 
                              subscription_name="governance",
                              connection="AZURE_SERVICE_BUS_CONNECTION_STRING")
def process_decision_event(msg: func.ServiceBusMessage):
    """Process decision events from service bus"""
    body = msg.get_body().decode("utf-8")
    subject = msg.subject
    logging.info(f"[GOV] Event: {subject} Payload: {body}")
    # Add side effects: persist to Cosmos DB, trigger notifications, etc.