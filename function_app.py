"""
Business Infinity - Azure Functions App
Updated to use the new AOS-based Business Infinity architecture
"""

import json
import logging
import azure.functions as func

# Import new Business Infinity system
try:
    from business_infinity import BusinessInfinity, BusinessInfinityConfig
    from core.agents import UnifiedAgentManager, get_unified_manager
    BUSINESS_INFINITY_AVAILABLE = True
except ImportError:
    BUSINESS_INFINITY_AVAILABLE = False
    
# Fallback to consolidated core if available
if not BUSINESS_INFINITY_AVAILABLE:
    try:
        from core.azure_functions import register_consolidated_functions
        CORE_AVAILABLE = True
    except ImportError:
        CORE_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Azure Functions app
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Initialize Business Infinity system
business_infinity = None
unified_manager = None

if BUSINESS_INFINITY_AVAILABLE:
    try:
        config = BusinessInfinityConfig()
        business_infinity = BusinessInfinity(config)
        unified_manager = get_unified_manager()
        logger.info("Business Infinity system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Business Infinity: {e}")
        BUSINESS_INFINITY_AVAILABLE = False


# === Core Business Infinity Endpoints ===

@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def health(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    try:
        if business_infinity:
            status = await business_infinity.get_business_status()
            return func.HttpResponse(
                json.dumps({"status": "healthy", "system": "business_infinity", "details": status}),
                mimetype="application/json",
                status_code=200
            )
        else:
            return func.HttpResponse(
                json.dumps({"status": "limited", "system": "fallback", "message": "Business Infinity not available"}),
                mimetype="application/json", 
                status_code=200
            )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"status": "error", "error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="agents", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def list_agents(req: func.HttpRequest) -> func.HttpResponse:
    """List all available business agents"""
    try:
        if business_infinity:
            agents = business_infinity.list_agents()
            return func.HttpResponse(
                json.dumps({"agents": agents}),
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
        logger.error(f"Error listing agents: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="agents/{agent_role}/ask", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def ask_agent(req: func.HttpRequest) -> func.HttpResponse:
    """Ask a specific agent a question"""
    try:
        agent_role = req.route_params.get('agent_role')
        if not agent_role:
            return func.HttpResponse(
                json.dumps({"error": "Agent role required"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                mimetype="application/json",
                status_code=400
            )
        
        message = req_body.get('message', '')
        context = req_body.get('context', {})
        
        if not message:
            return func.HttpResponse(
                json.dumps({"error": "Message is required"}),
                mimetype="application/json",
                status_code=400
            )
        
        if business_infinity:
            response = await business_infinity.ask_agent(agent_role, message, context)
            return func.HttpResponse(
                json.dumps({
                    "agent": agent_role,
                    "response": response,
                    "system": "business_infinity"
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
        logger.error(f"Error asking agent {agent_role}: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="decisions", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def make_decision(req: func.HttpRequest) -> func.HttpResponse:
    """Make a strategic business decision"""
    try:
        # Parse request body
        try:
            decision_context = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                mimetype="application/json",
                status_code=400
            )
        
        if business_infinity:
            result = await business_infinity.make_strategic_decision(decision_context)
            return func.HttpResponse(
                json.dumps(result),
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
        logger.error(f"Error making decision: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="workflows/{workflow_name}", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def execute_workflow(req: func.HttpRequest) -> func.HttpResponse:
    """Execute a business workflow"""
    try:
        workflow_name = req.route_params.get('workflow_name')
        if not workflow_name:
            return func.HttpResponse(
                json.dumps({"error": "Workflow name required"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Parse request body
        try:
            workflow_params = req.get_json()
        except ValueError:
            workflow_params = {}
        
        if business_infinity:
            workflow_id = await business_infinity.execute_business_workflow(workflow_name, workflow_params)
            return func.HttpResponse(
                json.dumps({
                    "workflow_id": workflow_id,
                    "workflow_name": workflow_name,
                    "status": "started"
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
        logger.error(f"Error executing workflow {workflow_name}: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


# === Fallback Functions ===
if CORE_AVAILABLE and not BUSINESS_INFINITY_AVAILABLE:
    try:
        register_consolidated_functions(app)
        logger.info("Registered fallback consolidated functions")
    except Exception as e:
        logger.error(f"Failed to register fallback functions: {e}")


# === Service Bus and Queue Triggers ===
@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="business-decisions",
    connection="ServiceBusConnection"
)
async def process_decision_queue(msg: func.ServiceBusMessage) -> None:
    """Process decisions from Service Bus queue"""
    try:
        message_body = msg.get_body().decode('utf-8')
        decision_context = json.loads(message_body)
        
        logger.info(f"Processing decision from queue: {decision_context}")
        
        if business_infinity:
            result = await business_infinity.make_strategic_decision(decision_context)
            logger.info(f"Decision result: {result}")
        else:
            logger.warning("Business Infinity not available for queue processing")
            
    except Exception as e:
        logger.error(f"Error processing decision queue message: {e}")

@app.service_bus_topic_trigger(
    arg_name="msg",
    topic_name="business-events",
    subscription_name="workflow-processor",
    connection="ServiceBusConnection"
)
async def process_business_events(msg: func.ServiceBusMessage) -> None:
    """Process business events from Service Bus topic"""
    try:
        message_body = msg.get_body().decode('utf-8')
        event_data = json.loads(message_body)
        
        event_type = event_data.get('type', 'unknown')
        logger.info(f"Processing business event: {event_type}")
        
        if business_infinity and event_type in ['workflow_request', 'agent_task']:
            # Process business events through Business Infinity
            workflow_name = event_data.get('workflow', 'generic')
            workflow_params = event_data.get('params', {})
            
            workflow_id = await business_infinity.execute_business_workflow(workflow_name, workflow_params)
            logger.info(f"Started workflow {workflow_id} for event {event_type}")
        else:
            logger.info(f"Event {event_type} processed (no action required)")
            
    except Exception as e:
        logger.error(f"Error processing business event: {e}")


# === Mentor Mode Endpoints ===

@app.route(route="mentor/agents", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def mentor_list_agents(req: func.HttpRequest) -> func.HttpResponse:
    """List all agents with their LoRA versions for mentor mode"""
    try:
        if business_infinity and hasattr(business_infinity, 'mentor_mode') and business_infinity.mentor_mode:
            agents = await business_infinity.mentor_mode.list_agents_with_lora()
            return func.HttpResponse(
                json.dumps({"agents": agents}),
                mimetype="application/json",
                status_code=200
            )
        elif business_infinity:
            # Fallback to basic agent list if mentor mode not available
            agents = business_infinity.list_agents()
            # Transform to mentor mode format
            mentor_agents = []
            for agent in agents:
                mentor_agents.append({
                    "id": agent.get("role", agent.get("name", "unknown")).lower(),
                    "name": agent.get("name", agent.get("role", "Unknown Agent")),
                    "loraVersion": "v1.0.0",  # Default version if LoRA not available
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
        logger.error(f"Error listing mentor agents: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="mentor/chat/{agent_id}", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def mentor_chat_with_agent(req: func.HttpRequest) -> func.HttpResponse:
    """Chat with a specific agent via mentor mode"""
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
        
        if business_infinity:
            # Try mentor mode first, fallback to regular agent interaction
            if hasattr(business_infinity, 'mentor_mode') and business_infinity.mentor_mode:
                response = await business_infinity.mentor_mode.chat_with_agent(agent_id, message)
            else:
                # Fallback to regular agent interaction
                response = await business_infinity.ask_agent(agent_id.upper(), message)
            
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
        logger.error(f"Error in mentor chat with agent {agent_id}: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="mentor/fine-tune/{agent_id}", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def mentor_fine_tune_agent(req: func.HttpRequest) -> func.HttpResponse:
    """Start fine-tuning job for an agent"""
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
        
        if business_infinity and hasattr(business_infinity, 'mentor_mode') and business_infinity.mentor_mode:
            job = await business_infinity.mentor_mode.start_fine_tune_job(agent_id, dataset_id)
            return func.HttpResponse(
                json.dumps(job),
                mimetype="application/json",
                status_code=200
            )
        else:
            # Return a mock response if mentor mode not available
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
        logger.error(f"Error starting fine-tune job for agent {agent_id}: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="mentor/logs/{job_id}", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def mentor_get_training_logs(req: func.HttpRequest) -> func.HttpResponse:
    """Get training logs for a fine-tuning job"""
    try:
        job_id = req.route_params.get('job_id')
        if not job_id:
            return func.HttpResponse(
                json.dumps({"error": "Job ID required"}),
                mimetype="application/json",
                status_code=400
            )
        
        if business_infinity and hasattr(business_infinity, 'mentor_mode') and business_infinity.mentor_mode:
            logs = await business_infinity.mentor_mode.get_training_logs(job_id)
            return func.HttpResponse(
                json.dumps({"logs": logs}),
                mimetype="application/json",
                status_code=200
            )
        else:
            # Return mock logs if mentor mode not available
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
        logger.error(f"Error getting training logs for job {job_id}: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="mentor/deploy/{agent_id}", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def mentor_deploy_adapter(req: func.HttpRequest) -> func.HttpResponse:
    """Deploy a LoRA adapter for an agent"""
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
        
        if business_infinity and hasattr(business_infinity, 'mentor_mode') and business_infinity.mentor_mode:
            result = await business_infinity.mentor_mode.deploy_adapter(agent_id, version)
            return func.HttpResponse(
                json.dumps(result),
                mimetype="application/json",
                status_code=200
            )
        else:
            # Return mock deployment result
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
        logger.error(f"Error deploying adapter for agent {agent_id}: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="mentor/ui", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def mentor_mode_ui(req: func.HttpRequest) -> func.HttpResponse:
    """Serve the mentor mode web UI"""
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
        logger.error(f"Error serving mentor mode UI: {e}")
        return func.HttpResponse(
            f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>",
            mimetype="text/html",
            status_code=500
        )


# Export the app for Azure Functions runtime
if __name__ == "__main__":
    if BUSINESS_INFINITY_AVAILABLE:
        logger.info("Azure Functions app initialized with Business Infinity architecture")
    elif CORE_AVAILABLE:
        logger.info("Azure Functions app initialized with fallback core system")
    else:
        logger.warning("Azure Functions app initialized with limited functionality")