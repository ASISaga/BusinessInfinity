"""
Consolidated Azure Functions Module
Consolidates all Azure Functions functionality from scattered directories
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import azure.functions as func
    AZURE_FUNCTIONS_AVAILABLE = True
except ImportError:
    AZURE_FUNCTIONS_AVAILABLE = False


# Import orchestrator from BusinessInfinityOrchestrator
try:
    from core.BusinessInfinityOrchestrator import orchestrator
    from core import (
        unified_server, storage_manager, ml_manager, env_manager, api_orchestrator,
        auth_handler, triggers_manager, utils_manager
    )
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False
    orchestrator = None


class ConsolidatedAzureFunctions:
    """
    Consolidated Azure Functions handler that brings together:
    - All agent operations from server/Operations/
    - HTTP route handling
    - Queue and Service Bus triggers
    - Legacy Azure Functions compatibility
    """
    
    def __init__(self):
        self.core_available = CORE_AVAILABLE
        self.azure_available = AZURE_FUNCTIONS_AVAILABLE
        
        if not self.core_available:
            logging.warning("Core system not available - Azure Functions will have limited functionality")
        
        # Legacy agent configurations (from server/Operations/)
        self.legacy_agents = {
            "operations": {
                "name": "Operations Agent",
                "description": "Handles operational decisions and processes"
            },
            "finance": {
                "name": "Finance Agent", 
                "description": "Manages financial analysis and budgeting"
            },
            "marketing": {
                "name": "Marketing Agent",
                "description": "Handles marketing strategy and campaigns"
            },
            "hr": {
                "name": "HR Agent",
                "description": "Manages human resources and recruitment"
            },
            "quality": {
                "name": "Quality Assurance Agent",
                "description": "Ensures quality standards and testing"
            },
            "accounts": {
                "name": "Accounts Agent",
                "description": "Manages accounting and financial records"
            },
            "purchase": {
                "name": "Purchase Agent", 
                "description": "Handles procurement and vendor management"
            }
        }
    
    def register_all_functions(self, app: func.FunctionApp):
        """Register all Azure Functions with the app"""
        if not self.azure_available:
            raise ImportError("Azure Functions not available")
        
        # Register HTTP routes
        self._register_http_routes(app)
        
        # Register queue triggers  
        self._register_queue_triggers(app)
        
        # Register Service Bus triggers
        self._register_service_bus_triggers(app)
        
        # Register timer triggers
        self._register_timer_triggers(app)
    
    def _register_http_routes(self, app: func.FunctionApp):
        """Register consolidated HTTP routes"""
        
        @app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
        async def health_check(req: func.HttpRequest) -> func.HttpResponse:
            """Health check endpoint"""
            status = {
                "status": "healthy",
                "core_available": self.core_available,
                "timestamp": utils_manager.get_current_timestamp() if self.core_available else None
            }
            return func.HttpResponse(
                json.dumps(status),
                mimetype="application/json",
                status_code=200
            )
        
        @app.route(route="agents", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
        async def list_agents(req: func.HttpRequest) -> func.HttpResponse:
            """List all available agents"""
            try:
                if self.core_available and orchestrator:
                    agents = orchestrator.agent_manager.get_agent_profiles()
                    return func.HttpResponse(agents, mimetype="application/json")
                else:
                    # Fallback to legacy agents
                    agents = [{"agentId": k, **v} for k, v in self.legacy_agents.items()]
                    return func.HttpResponse(json.dumps(agents), mimetype="application/json")
            except Exception as e:
                logging.error(f"Error listing agents: {e}")
                return func.HttpResponse(
                    json.dumps({"error": "Failed to list agents"}),
                    mimetype="application/json",
                    status_code=500
                )
        
        @app.route(route="agents/{agent_id}/chat", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
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
                
                if self.core_available and orchestrator:
                    response = await orchestrator.agent_manager.ask_agent(agent_id, message)
                    if response:
                        return func.HttpResponse(response, mimetype="application/json")
                    else:
                        return func.HttpResponse(
                            json.dumps({"error": "Agent not found"}),
                            mimetype="application/json",
                            status_code=404
                        )
                else:
                    # Fallback response
                    if agent_id in self.legacy_agents:
                        response = {
                            "answer": f"Legacy response from {agent_id}: {message}",
                            "agent": agent_id
                        }
                        return func.HttpResponse(json.dumps(response), mimetype="application/json")
                    else:
                        return func.HttpResponse(
                            json.dumps({"error": "Agent not found in legacy mode"}),
                            mimetype="application/json", 
                            status_code=404
                        )
                        
            except Exception as e:
                logging.error(f"Error chatting with agent {agent_id}: {e}")
                return func.HttpResponse(
                    json.dumps({"error": "Chat failed"}),
                    mimetype="application/json",
                    status_code=500
                )
        
        @app.route(route="mcp", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
        async def mcp_endpoint(req: func.HttpRequest) -> func.HttpResponse:
            """MCP endpoint for dashboard communication"""
            try:
                body = req.get_json()
                
                if self.core_available and orchestrator:
                    response = await orchestrator.mcp_handler.handle_mcp_request(body)
                else:
                    # Basic MCP fallback
                    response = {
                        "jsonrpc": "2.0",
                        "id": body.get("id"),
                        "result": {"status": "fallback_mode"}
                    }
                
                return func.HttpResponse(
                    json.dumps(response),
                    mimetype="application/json"
                )
            except Exception as e:
                logging.error(f"MCP endpoint error: {e}")
                return func.HttpResponse(
                    json.dumps({
                        "jsonrpc": "2.0",
                        "id": body.get("id") if 'body' in locals() else None,
                        "error": {"code": -32000, "message": str(e)}
                    }),
                    mimetype="application/json",
                    status_code=500
                )
        
        # Additional HTTP routes can be added here
        
    def _register_queue_triggers(self, app: func.FunctionApp):
        """Register Azure Storage Queue triggers"""
        
        @app.queue_trigger(
            arg_name="msg", 
            queue_name="agent-requests",
            connection="AzureWebJobsStorage"
        )
        async def agent_requests_trigger(msg: func.QueueMessage) -> None:
            """Process agent request messages from queue"""
            try:
                logging.info(f"Processing agent request: {msg.get_body().decode()}")
                
                if self.core_available:
                    result = await triggers_manager.process_queue_message("agent-requests", msg)
                    logging.info(f"Agent request processed: {result}")
                else:
                    logging.info("Agent request processed in fallback mode")
                    
            except Exception as e:
                logging.error(f"Error processing agent request: {e}")
        
        @app.queue_trigger(
            arg_name="msg",
            queue_name="agent-events", 
            connection="AzureWebJobsStorage"
        )
        async def agent_events_trigger(msg: func.QueueMessage) -> None:
            """Process agent event messages from queue"""
            try:
                logging.info(f"Processing agent event: {msg.get_body().decode()}")
                
                if self.core_available:
                    result = await triggers_manager.process_queue_message("agent-events", msg)
                    logging.info(f"Agent event processed: {result}")
                else:
                    logging.info("Agent event processed in fallback mode")
                    
            except Exception as e:
                logging.error(f"Error processing agent event: {e}")
    
    def _register_service_bus_triggers(self, app: func.FunctionApp):
        """Register Azure Service Bus triggers"""
        
        @app.service_bus_topic_trigger(
            arg_name="msg",
            topic_name="decision-events", 
            subscription_name="default",
            connection="SERVICE_BUS_CONNECTION_STRING"
        )
        async def decision_events_trigger(msg: func.ServiceBusMessage) -> None:
            """Process decision events from Service Bus"""
            try:
                logging.info(f"Processing decision event: {str(msg.body)}")
                
                if self.core_available:
                    result = await triggers_manager.process_service_bus_message("decision-events", msg)
                    logging.info(f"Decision event processed: {result}")
                else:
                    logging.info("Decision event processed in fallback mode")
                    
            except Exception as e:
                logging.error(f"Error processing decision event: {e}")
    
    def _register_timer_triggers(self, app: func.FunctionApp):
        """Register timer-based triggers"""
        
        @app.timer_trigger(schedule="0 */5 * * * *", arg_name="timer", run_on_startup=False)
        async def health_monitor_timer(timer: func.TimerRequest) -> None:
            """Periodic health monitoring"""
            try:
                logging.info("Running periodic health check")
                
                if self.core_available:
                    # Could check system health, cleanup resources, etc.
                    env_status = env_manager.validate_environment()
                    storage_status = storage_manager.validate_configuration()
                    logging.info(f"System health - env: {env_status['valid']}, storage: {storage_status['valid']}")
                else:
                    logging.info("Health check in fallback mode")
                    
            except Exception as e:
                logging.error(f"Error in health monitoring: {e}")
    
    # Legacy compatibility methods
    
    def get_legacy_agent_operation(self, agent_type: str, operation: str) -> Dict[str, Any]:
        """Get legacy agent operation details"""
        if agent_type in self.legacy_agents:
            return {
                "agent": agent_type,
                "operation": operation,
                "description": self.legacy_agents[agent_type]["description"],
                "status": "available"
            }
        else:
            return {"error": f"Legacy agent {agent_type} not found"}
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate Azure Functions configuration"""
        issues = []
        
        if not self.azure_available:
            issues.append("Azure Functions runtime not available")
        
        if not self.core_available:
            issues.append("Core system not available - running in fallback mode")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "azure_functions_available": self.azure_available,
            "core_system_available": self.core_available,
            "legacy_agents_count": len(self.legacy_agents)
        }


# Create singleton instance
consolidated_functions = ConsolidatedAzureFunctions()

# Export main registration function
def register_consolidated_functions(app: func.FunctionApp):
    """Register all consolidated Azure Functions"""
    return consolidated_functions.register_all_functions(app)

# Export for backward compatibility
__all__ = ['consolidated_functions', 'ConsolidatedAzureFunctions', 'register_consolidated_functions']