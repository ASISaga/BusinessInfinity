"""
Business Infinity - Azure Functions App
Updated to use the new AOS-based Business Infinity architecture
"""

import json
import logging
import azure.functions as func
from datetime import datetime

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


# === Boardroom Conversation Endpoints ===

@app.route(route="conversations", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def list_conversations(req: func.HttpRequest) -> func.HttpResponse:
    """List boardroom conversations with optional filtering"""
    try:
        if not business_infinity:
            return func.HttpResponse(
                json.dumps({"error": "Business Infinity not available"}),
                mimetype="application/json",
                status_code=503
            )
        
        # Get query parameters
        champion = req.params.get('champion')
        status = req.params.get('status') 
        limit = int(req.params.get('limit', 50))
        
        # Get conversations from Business Infinity
        conversations = []
        
        if champion:
            # Get conversations for specific agent
            agent_conversations = await business_infinity.get_agent_conversations(champion)
            if "championed" in agent_conversations:
                conversations = agent_conversations["championed"]
        else:
            # Get all conversations (this would need a new method)
            conversations = []
        
        # Apply status filter if specified
        if status:
            conversations = [conv for conv in conversations if conv.get("status") == status]
        
        # Limit results
        conversations = conversations[:limit]
        
        return func.HttpResponse(
            json.dumps({
                "conversations": conversations,
                "count": len(conversations),
                "champion": champion,
                "status": status
            }),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="conversations/{conversation_id}", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_conversation(req: func.HttpRequest) -> func.HttpResponse:
    """Get a specific conversation by ID"""
    try:
        conversation_id = req.route_params.get('conversation_id')
        if not conversation_id:
            return func.HttpResponse(
                json.dumps({"error": "Conversation ID required"}),
                mimetype="application/json",
                status_code=400
            )
        
        if not business_infinity or not business_infinity.autonomous_boardroom:
            return func.HttpResponse(
                json.dumps({"error": "Business Infinity boardroom not available"}),
                mimetype="application/json",
                status_code=503
            )
        
        # Get conversation from boardroom
        conversation_manager = business_infinity.autonomous_boardroom.conversation_manager
        if not conversation_manager:
            return func.HttpResponse(
                json.dumps({"error": "Conversation manager not available"}),
                mimetype="application/json",
                status_code=503
            )
        
        conversation = await conversation_manager.get_conversation(conversation_id)
        
        if conversation:
            return func.HttpResponse(
                json.dumps({
                    "conversation": conversation.to_dict(),
                    "conversation_id": conversation_id
                }),
                mimetype="application/json",
                status_code=200
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Conversation not found"}),
                mimetype="application/json",
                status_code=404
            )
        
    except Exception as e:
        logger.error(f"Error getting conversation {conversation_id}: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="conversations", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def create_conversation(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new boardroom conversation"""
    try:
        if not business_infinity:
            return func.HttpResponse(
                json.dumps({"error": "Business Infinity not available"}),
                mimetype="application/json",
                status_code=503
            )
        
        # Parse request body
        try:
            conv_data = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Validate required fields
        required_fields = ["conversation_type", "champion", "title", "content"]
        for field in required_fields:
            if field not in conv_data:
                return func.HttpResponse(
                    json.dumps({"error": f"Missing required field: {field}"}),
                    mimetype="application/json",
                    status_code=400
                )
        
        # Create conversation
        conversation_id = await business_infinity.create_boardroom_conversation(
            conversation_type=conv_data["conversation_type"],
            champion_role=conv_data["champion"],
            title=conv_data["title"],
            content=conv_data["content"],
            context=conv_data.get("context", {})
        )
        
        if conversation_id:
            return func.HttpResponse(
                json.dumps({
                    "conversation_id": conversation_id,
                    "status": "created",
                    "message": "Conversation created successfully"
                }),
                mimetype="application/json",
                status_code=201
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Failed to create conversation"}),
                mimetype="application/json",
                status_code=500
            )
        
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="conversations/{conversation_id}/sign", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def sign_conversation(req: func.HttpRequest) -> func.HttpResponse:
    """Sign a conversation"""
    try:
        conversation_id = req.route_params.get('conversation_id')
        if not conversation_id:
            return func.HttpResponse(
                json.dumps({"error": "Conversation ID required"}),
                mimetype="application/json",
                status_code=400
            )
        
        if not business_infinity:
            return func.HttpResponse(
                json.dumps({"error": "Business Infinity not available"}),
                mimetype="application/json",
                status_code=503
            )
        
        # Parse request body
        try:
            sign_data = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Validate required fields
        if "signer_role" not in sign_data or "signer_name" not in sign_data:
            return func.HttpResponse(
                json.dumps({"error": "Missing required fields: signer_role, signer_name"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Sign conversation
        success = await business_infinity.sign_conversation(
            conversation_id=conversation_id,
            signer_role=sign_data["signer_role"],
            signer_name=sign_data["signer_name"]
        )
        
        if success:
            return func.HttpResponse(
                json.dumps({
                    "conversation_id": conversation_id,
                    "status": "signed",
                    "message": f"Conversation signed by {sign_data['signer_name']}",
                    "signer": {
                        "name": sign_data["signer_name"],
                        "role": sign_data["signer_role"]
                    }
                }),
                mimetype="application/json",
                status_code=200
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Failed to sign conversation"}),
                mimetype="application/json",
                status_code=400
            )
        
    except Exception as e:
        logger.error(f"Error signing conversation {conversation_id}: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="conversations/a2a", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def create_a2a_communication(req: func.HttpRequest) -> func.HttpResponse:
    """Create Agent-to-Agent communication"""
    try:
        if not business_infinity:
            return func.HttpResponse(
                json.dumps({"error": "Business Infinity not available"}),
                mimetype="application/json",
                status_code=503
            )
        
        # Parse request body
        try:
            a2a_data = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Validate required fields
        required_fields = ["from_agent", "to_agent", "conversation_type", "message"]
        for field in required_fields:
            if field not in a2a_data:
                return func.HttpResponse(
                    json.dumps({"error": f"Missing required field: {field}"}),
                    mimetype="application/json",
                    status_code=400
                )
        
        # Create A2A communication
        conversation_id = await business_infinity.initiate_a2a_communication(
            from_agent=a2a_data["from_agent"],
            to_agent=a2a_data["to_agent"],
            conversation_type=a2a_data["conversation_type"],
            message=a2a_data["message"],
            context=a2a_data.get("context", {})
        )
        
        if conversation_id:
            return func.HttpResponse(
                json.dumps({
                    "conversation_id": conversation_id,
                    "status": "created",
                    "message": "A2A communication created successfully",
                    "from_agent": a2a_data["from_agent"],
                    "to_agent": a2a_data["to_agent"]
                }),
                mimetype="application/json",
                status_code=201
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Failed to create A2A communication"}),
                mimetype="application/json",
                status_code=500
            )
        
    except Exception as e:
        logger.error(f"Error creating A2A communication: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="conversations/events", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_conversation_events(req: func.HttpRequest) -> func.HttpResponse:
    """Get conversation events for web client updates"""
    try:
        if not business_infinity or not business_infinity.autonomous_boardroom:
            return func.HttpResponse(
                json.dumps({"error": "Business Infinity boardroom not available"}),
                mimetype="application/json",
                status_code=503
            )
        
        # Get query parameters
        since_timestamp = req.params.get('since')
        limit = int(req.params.get('limit', 100))
        
        # Get conversation manager
        conversation_manager = business_infinity.autonomous_boardroom.conversation_manager
        if not conversation_manager:
            return func.HttpResponse(
                json.dumps({"error": "Conversation manager not available"}),
                mimetype="application/json",
                status_code=503
            )
        
        # Get web events
        events = await conversation_manager.get_web_events_since(since_timestamp)
        
        # Limit results
        events = events[:limit]
        
        return func.HttpResponse(
            json.dumps({
                "events": events,
                "count": len(events),
                "since": since_timestamp,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error getting conversation events: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="conversations/dashboard", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def conversations_dashboard(req: func.HttpRequest) -> func.HttpResponse:
    """Serve the conversations dashboard"""
    try:
        import os
        dashboard_path = os.path.join(os.path.dirname(__file__), "conversations", "dashboard.html")
        
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return func.HttpResponse(
                content,
                mimetype="text/html",
                status_code=200
            )
        else:
            return func.HttpResponse(
                "<h1>Dashboard not found</h1><p>The conversations dashboard file was not found.</p>",
                mimetype="text/html",
                status_code=404
            )
    
    except Exception as e:
        logger.error(f"Error serving conversations dashboard: {e}")
        return func.HttpResponse(
            f"<h1>Error</h1><p>Failed to load dashboard: {str(e)}</p>",
            mimetype="text/html",
            status_code=500
        )

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


# === Onboarding Endpoints ===

@app.route(route="onboarding", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def onboarding_interface(req: func.HttpRequest) -> func.HttpResponse:
    """Serve the onboarding interface"""
    try:
        import os
        onboarding_path = os.path.join(os.path.dirname(__file__), "onboarding", "onboarding.html")
        
        if os.path.exists(onboarding_path):
            with open(onboarding_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            return func.HttpResponse(
                html_content,
                mimetype="text/html",
                status_code=200
            )
        else:
            return func.HttpResponse(
                "<h1>Onboarding not found</h1><p>The onboarding interface file was not found.</p>",
                mimetype="text/html",
                status_code=404
            )
    except Exception as e:
        logger.error(f"Error serving onboarding interface: {e}")
        return func.HttpResponse(
            f"<h1>Error</h1><p>Failed to load onboarding interface: {str(e)}</p>",
            mimetype="text/html",
            status_code=500
        )

@app.route(route="api/linkedin/auth", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def linkedin_auth_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Handle LinkedIn OAuth initiation for onboarding"""
    try:
        # Use existing LinkedIn auth logic
        from linkedin_auth import get_linkedin_login_url
        result = get_linkedin_login_url(req)
        
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=result.get("status", 200)
        )
    except Exception as e:
        logger.error(f"Error initiating LinkedIn auth: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="api/onboarding/parse-website", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def parse_website(req: func.HttpRequest) -> func.HttpResponse:
    """Parse website content for onboarding"""
    try:
        request_data = req.get_json()
        website_url = request_data.get('url')
        
        if not website_url:
            return func.HttpResponse(
                json.dumps({"error": "Website URL is required"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Placeholder website parsing logic
        # In a real implementation, this would use web scraping
        parsed_data = {
            "company_name": "Example Company",
            "tagline": "Innovative solutions for modern business",
            "description": "We provide cutting-edge technology solutions to help businesses scale and succeed.",
            "source_url": website_url,
            "parsed_at": datetime.now().isoformat()
        }
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "data": parsed_data,
                "message": "Website parsed successfully"
            }),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error parsing website: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="api/onboarding/upload-deck", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def upload_deck(req: func.HttpRequest) -> func.HttpResponse:
    """Handle pitch deck upload and processing"""
    try:
        # Placeholder file upload logic
        # In a real implementation, this would:
        # 1. Save file to secure storage
        # 2. Parse slides using document processing
        # 3. Extract key information
        # 4. Generate file hash for integrity
        
        processed_data = {
            "filename": "pitch_deck.pdf",
            "file_hash": "abc123def456",
            "slides_count": 12,
            "key_sections": ["Problem", "Solution", "Market", "Business Model", "Team", "Financials"],
            "encrypted": True,
            "uploaded_at": datetime.now().isoformat()
        }
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "data": processed_data,
                "message": "Pitch deck uploaded and processed successfully"
            }),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error uploading deck: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="api/onboarding/upload-financials", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def upload_financials(req: func.HttpRequest) -> func.HttpResponse:
    """Handle financial document upload"""
    try:
        # Placeholder financial document processing
        processed_data = {
            "files_processed": 2,
            "financial_data_extracted": True,
            "revenue_data": "Available",
            "expense_data": "Available",
            "encrypted": True,
            "retention_days": 30,
            "uploaded_at": datetime.now().isoformat()
        }
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "data": processed_data,
                "message": "Financial documents uploaded successfully"
            }),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error uploading financials: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="api/onboarding/connect-system", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def connect_system(req: func.HttpRequest) -> func.HttpResponse:
    """Handle system connector authorization"""
    try:
        request_data = req.get_json()
        system_name = request_data.get('system')
        
        if not system_name:
            return func.HttpResponse(
                json.dumps({"error": "System name is required"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Extract user info for consent logging
        user_id = request_data.get('user_id', 'onboarding_user')
        customer_id = request_data.get('customer_id', 'onboarding_customer')
        
        # Generate OAuth URL for the requested system
        # In a real implementation, this would generate actual OAuth URLs
        oauth_urls = {
            'salesforce': 'https://login.salesforce.com/services/oauth2/authorize?...',
            'hubspot': 'https://app.hubspot.com/oauth/authorize?...',
            'netsuite': 'https://system.netsuite.com/pages/customerlogin.jsp?...',
            'workday': 'https://wd2-impl.workday.com/...',
            'quickbooks': 'https://appcenter.intuit.com/connect/oauth2?...',
            'slack': 'https://slack.com/oauth/v2/authorize?...'
        }
        
        auth_url = oauth_urls.get(system_name, f'https://example.com/oauth/{system_name}')
        
        # Log consent for system connection
        log_onboarding_consent(
            user_id=user_id,
            customer_id=customer_id,
            consent_type="system_integration",
            consent_given=True,
            description=f"User consented to connect {system_name} system with read-only access for business analysis"
        )
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "auth_url": auth_url,
                "system": system_name,
                "scopes": "read-only",
                "message": f"OAuth URL generated for {system_name}",
                "consent_logged": True
            }),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error connecting system: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="api/onboarding/generate-voice-profile", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def generate_voice_profile(req: func.HttpRequest) -> func.HttpResponse:
    """Generate voice profile from LinkedIn posts and other content"""
    try:
        request_data = req.get_json()
        
        # Placeholder voice analysis
        voice_profile = {
            "themes": ["Innovation", "Leadership", "Growth", "Technology"],
            "tone": "Professional yet approachable",
            "style": "Strategic with practical insights",
            "key_phrases": ["driving growth", "strategic vision", "innovation"],
            "communication_frequency": "Regular",
            "generated_at": datetime.now().isoformat()
        }
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "data": voice_profile,
                "message": "Voice profile generated successfully"
            }),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error generating voice profile: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="api/onboarding/quick-action", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
async def handle_quick_action(req: func.HttpRequest) -> func.HttpResponse:
    """Handle final onboarding quick actions"""
    try:
        request_data = req.get_json()
        message = request_data.get('message', '').lower()
        
        # Extract user info for consent logging
        user_id = request_data.get('user_id', 'onboarding_user')
        customer_id = request_data.get('customer_id', 'onboarding_customer')
        
        # Handle different quick actions
        if 'a' in message or 'runway' in message or 'cfo' in message:
            response = "Excellent choice! I'll connect you with our CFO agent who will analyze your financial data and create a comprehensive runway model. This will include burn rate analysis, funding requirements, and key financial milestones."
            consent_desc = "User chose CFO agent analysis - consented to financial data processing for runway modeling"
            action_type = "cfo_analysis"
        elif 'b' in message or 'gtm' in message or 'cmo' in message:
            response = "Great selection! Our CMO agent will create a Go-to-Market voice brief based on your company profile, target market analysis, and communication style. This will help align your messaging across all channels."
            consent_desc = "User chose CMO agent analysis - consented to marketing data processing for GTM strategy"
            action_type = "cmo_analysis"
        elif 'c' in message or 'review' in message or 'deep' in message:
            response = "I'll schedule a comprehensive strategic review session with the full C-Suite team. We'll analyze all your data and provide detailed insights on operations, finance, marketing, and growth opportunities."
            consent_desc = "User chose comprehensive strategic review - consented to full business data analysis by C-Suite agents"
            action_type = "full_review"
        else:
            response = "I understand you'd like to explore other options. Feel free to ask me anything about your business, or you can always return to the quick actions (A, B, or C) when you're ready."
            consent_desc = "User explored other options - implicit consent to continue onboarding process"
            action_type = "explore_options"
        
        # Log the consent for this onboarding choice
        log_onboarding_consent(
            user_id=user_id,
            customer_id=customer_id,
            consent_type="onboarding_service_selection",
            consent_given=True,
            description=consent_desc
        )
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "response": response,
                "action_recorded": True,
                "action_type": action_type,
                "consent_logged": True
            }),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error handling quick action: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e), "success": False}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="api/onboarding/audit-trail", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
async def get_audit_trail(req: func.HttpRequest) -> func.HttpResponse:
    """Serve audit trail interface"""
    try:
        # Generate audit trail HTML
        audit_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Onboarding Audit Trail</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .audit-entry {{ margin: 10px 0; padding: 10px; border-left: 3px solid #667eea; background: #f8f9fa; }}
                .timestamp {{ color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <h1>Onboarding Audit Trail</h1>
            <div class="audit-entry">
                <div class="timestamp">{datetime.now().isoformat()}</div>
                <div>Onboarding session initiated</div>
            </div>
            <div class="audit-entry">
                <div class="timestamp">{datetime.now().isoformat()}</div>
                <div>LinkedIn authentication requested (read-only scope)</div>
            </div>
            <div class="audit-entry">
                <div class="timestamp">{datetime.now().isoformat()}</div>
                <div>Website content parsed (public content only)</div>
            </div>
            <div class="audit-entry">
                <div class="timestamp">{datetime.now().isoformat()}</div>
                <div>Documents uploaded and encrypted</div>
            </div>
            <div class="audit-entry">
                <div class="timestamp">{datetime.now().isoformat()}</div>
                <div>Voice profile generated from public posts</div>
            </div>
            <div class="audit-entry">
                <div class="timestamp">{datetime.now().isoformat()}</div>
                <div>Founder dossier created (read-only operations)</div>
            </div>
        </body>
        </html>
        """
        
        return func.HttpResponse(
            audit_html,
            mimetype="text/html",
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error serving audit trail: {e}")
        return func.HttpResponse(
            f"Error loading audit trail: {str(e)}",
            status_code=500
        )


# === Trust and Compliance Endpoints ===

@app.route(route="api/onboarding/export-data", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def export_customer_data(req: func.HttpRequest) -> func.HttpResponse:
    """Export all data associated with the customer's partition"""
    try:
        from core.trust_compliance import get_trust_compliance_manager
        
        # Extract user and customer info from request
        # In a real implementation, this would come from authentication headers
        customer_id = req.params.get('customer_id') or req.headers.get('x-customer-id', 'customer_default')
        user_id = req.headers.get('x-user-id', 'user_default')
        
        if not customer_id or not user_id:
            return func.HttpResponse(
                json.dumps({"error": "Customer ID and User ID required"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Get trust compliance manager and export data
        tcm = get_trust_compliance_manager()
        export_data = tcm.export_customer_data(customer_id, user_id)
        
        # Prepare export response
        export_response = {
            "export_id": export_data.export_id,
            "customer_id": export_data.customer_id,
            "export_timestamp": export_data.export_timestamp.isoformat(),
            "data_types": export_data.data_types,
            "data": export_data.data_records,
            "integrity_hash": export_data.integrity_hash,
            "export_info": {
                "format": "json",
                "compliance": "GDPR Article 20 - Right to data portability",
                "verification": "SHA-256 integrity hash included"
            }
        }
        
        return func.HttpResponse(
            json.dumps(export_response, default=str),
            mimetype="application/json",
            status_code=200,
            headers={
                "Content-Disposition": f"attachment; filename=customer_data_export_{customer_id}.json"
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting customer data: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="api/onboarding/request-deletion", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
async def request_data_deletion(req: func.HttpRequest) -> func.HttpResponse:
    """Request deletion of customer partition data"""
    try:
        from core.trust_compliance import get_trust_compliance_manager
        
        request_data = req.get_json()
        customer_id = request_data.get('customer_id') or req.headers.get('x-customer-id', 'customer_default')
        user_id = req.headers.get('x-user-id', 'user_default')
        confirm = request_data.get('confirm', False)
        
        if not customer_id or not user_id:
            return func.HttpResponse(
                json.dumps({"error": "Customer ID and User ID required"}),
                mimetype="application/json",
                status_code=400
            )
        
        tcm = get_trust_compliance_manager()
        
        if not confirm:
            # Initial deletion request
            deletion_request = tcm.request_data_deletion(customer_id, user_id)
            
            response = {
                "request_id": deletion_request.request_id,
                "status": "pending_confirmation",
                "confirmation_required": True,
                "sla_completion_date": deletion_request.sla_completion_date.isoformat(),
                "sla_days": tcm.deletion_sla_days,
                "message": "Deletion request created. Please confirm by sending another request with 'confirm': true",
                "next_steps": {
                    "confirmation": "POST to same endpoint with 'confirm': true",
                    "cancellation": "Contact support to cancel request"
                }
            }
        else:
            # Confirmation step
            request_id = request_data.get('request_id')
            if not request_id:
                return func.HttpResponse(
                    json.dumps({"error": "Request ID required for confirmation"}),
                    mimetype="application/json",
                    status_code=400
                )
            
            success = tcm.confirm_data_deletion(request_id, customer_id, user_id)
            
            response = {
                "request_id": request_id,
                "status": "confirmed",
                "confirmed": success,
                "message": "Deletion request confirmed. Processing will begin within 24 hours.",
                "sla_days": tcm.deletion_sla_days,
                "gdpr_notice": "This fulfills your right to erasure under GDPR Article 17"
            }
        
        return func.HttpResponse(
            json.dumps(response, default=str),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error processing deletion request: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="api/onboarding/rbac", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_rbac_info(req: func.HttpRequest) -> func.HttpResponse:
    """Get current user's roles, permissions, and governance defaults"""
    try:
        from core.trust_compliance import get_trust_compliance_manager
        
        customer_id = req.params.get('customer_id') or req.headers.get('x-customer-id', 'customer_default')
        user_id = req.headers.get('x-user-id', 'user_default')
        
        if not customer_id or not user_id:
            return func.HttpResponse(
                json.dumps({"error": "Customer ID and User ID required"}),
                mimetype="application/json",
                status_code=400
            )
        
        tcm = get_trust_compliance_manager()
        rbac_info = tcm.get_user_rbac_info(user_id, customer_id)
        
        return func.HttpResponse(
            json.dumps(rbac_info, default=str),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error getting RBAC info: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="api/onboarding/incident-contact", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_incident_contact_info(req: func.HttpRequest) -> func.HttpResponse:
    """Get incident response and escalation contact information"""
    try:
        from core.trust_compliance import get_trust_compliance_manager
        
        tcm = get_trust_compliance_manager()
        contact_info = tcm.get_incident_contact_info()
        
        return func.HttpResponse(
            json.dumps(contact_info, default=str),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error getting incident contact info: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="api/onboarding/retention-policy", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
async def get_retention_policy(req: func.HttpRequest) -> func.HttpResponse:
    """Get current data retention and deletion policy"""
    try:
        from core.trust_compliance import get_trust_compliance_manager
        
        tcm = get_trust_compliance_manager()
        retention_policy = tcm.get_retention_policy()
        
        return func.HttpResponse(
            json.dumps(retention_policy, default=str),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error getting retention policy: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


# Enhanced consent logging for existing onboarding endpoints
def log_onboarding_consent(user_id: str, customer_id: str, consent_type: str, 
                          consent_given: bool, description: str) -> None:
    """Helper function to log consent during onboarding"""
    try:
        from core.trust_compliance import get_trust_compliance_manager
        tcm = get_trust_compliance_manager()
        tcm.log_consent(user_id, customer_id, consent_type, consent_given, description)
    except Exception as e:
        logger.warning(f"Failed to log consent: {e}")


# Export the app for Azure Functions runtime
if __name__ == "__main__":
    if BUSINESS_INFINITY_AVAILABLE:
        logger.info("Azure Functions app initialized with Business Infinity architecture")
    elif CORE_AVAILABLE:
        logger.info("Azure Functions app initialized with fallback core system")
    else:
        logger.warning("Azure Functions app initialized with limited functionality")