"""
Unified Triggers System
Consolidates functionality from triggers/ directory
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime

try:
    import azure.functions as func
    from azure.storage.queue import QueueClient
    from azure.servicebus import ServiceBusClient, ServiceBusMessage
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


class UnifiedTriggersManager:
    """
    Unified triggers manager that consolidates:
    - HTTP route handlers
    - Queue triggers (Azure Storage Queues)
    - Service Bus triggers
    - Event processing and orchestration
    """
    
    def __init__(self):
        # Import core components
        try:
            from . import agent_manager, mcp_handler, orchestrator, storage_manager, ml_manager
            self.agent_manager = agent_manager
            self.mcp_handler = mcp_handler
            self.orchestrator = orchestrator
            self.storage_manager = storage_manager
            self.ml_manager = ml_manager
        except ImportError:
            # Graceful degradation
            self.agent_manager = None
            self.mcp_handler = None
            self.orchestrator = None
            self.storage_manager = None
            self.ml_manager = None
        
        # Configuration
        try:
            from .features.environment import env_manager
            self.storage_conn = env_manager.get_required("AzureWebJobsStorage")
            self.service_bus_conn = env_manager.get_optional("SERVICE_BUS_CONNECTION_STRING")
        except (ImportError, Exception):
            import os
            self.storage_conn = os.getenv("AzureWebJobsStorage")
            self.service_bus_conn = os.getenv("SERVICE_BUS_CONNECTION_STRING")
        
        # Queue names
        self.agent_requests_queue = "agent-requests"
        self.agent_events_queue = "agent-events"
        self.decision_events_topic = "decision-events"
        
        # Registered handlers
        self.queue_handlers: Dict[str, Callable] = {}
        self.service_bus_handlers: Dict[str, Callable] = {}
        self.http_handlers: Dict[str, Callable] = {}
        
        # Initialize default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default message handlers"""
        # Queue handlers
        self.queue_handlers["agent-requests"] = self._handle_agent_request
        self.queue_handlers["agent-events"] = self._handle_agent_event
        
        # Service Bus handlers
        self.service_bus_handlers["decision-events"] = self._handle_decision_event
        
        # HTTP handlers will be registered by the HTTP routes module
    
    # === Queue Trigger Processing ===
    
    async def process_queue_message(self, queue_name: str, message: Any) -> Dict[str, Any]:
        """Process a queue message using registered handler"""
        try:
            if queue_name in self.queue_handlers:
                handler = self.queue_handlers[queue_name]
                result = await handler(message)
                return {"status": "success", "result": result}
            else:
                logging.warning(f"No handler registered for queue: {queue_name}")
                return {"status": "error", "error": f"No handler for queue {queue_name}"}
        except Exception as e:
            logging.error(f"Error processing queue message from {queue_name}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_agent_request(self, message: Any) -> Dict[str, Any]:
        """Handle agent request messages"""
        try:
            # Parse message content
            if hasattr(message, 'get_body'):
                content = message.get_body().decode('utf-8')
            else:
                content = str(message)
            
            msg_data = json.loads(content)
            
            # Extract key information
            agent_id = msg_data.get('agentId', msg_data.get('senderAgentId'))
            user_input = msg_data.get('message', msg_data.get('payload', {}).get('message'))
            conversation_id = msg_data.get('conversationId')
            
            if not agent_id or not user_input:
                return {"error": "Missing agent_id or message"}
            
            # Process with agent manager
            if self.agent_manager:
                response = await self.agent_manager.ask_agent(agent_id, user_input)
                
                # Store conversation if available
                if self.storage_manager and conversation_id:
                    conv = self.storage_manager.get_conversation(conversation_id)
                    if conv:
                        conv_data = json.loads(conv)
                        self.storage_manager.upsert_conversation(
                            conv_data, agent_id, response
                        )
                
                return {"agent_response": response}
            else:
                return {"error": "Agent manager not available"}
                
        except Exception as e:
            logging.error(f"Error handling agent request: {e}")
            return {"error": str(e)}
    
    async def _handle_agent_event(self, message: Any) -> Dict[str, Any]:
        """Handle agent event messages"""
        try:
            # Parse message content
            if hasattr(message, 'get_body'):
                content = message.get_body().decode('utf-8')
            else:
                content = str(message)
            
            msg_data = json.loads(content)
            
            # Log the event
            event_type = msg_data.get('eventType', 'unknown')
            agent_id = msg_data.get('agentId')
            timestamp = msg_data.get('timestamp', datetime.utcnow().isoformat())
            
            logging.info(f"Agent event: {event_type} from {agent_id} at {timestamp}")
            
            # Process event based on type
            if event_type == 'agent_response':
                # Handle agent response events
                return await self._process_agent_response_event(msg_data)
            elif event_type == 'agent_error':
                # Handle agent error events
                return await self._process_agent_error_event(msg_data)
            else:
                # Generic event logging
                return {"status": "logged", "event_type": event_type}
                
        except Exception as e:
            logging.error(f"Error handling agent event: {e}")
            return {"error": str(e)}
    
    async def _process_agent_response_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process agent response events"""
        # This could trigger additional workflows, notifications, etc.
        agent_id = event_data.get('agentId')
        response = event_data.get('response')
        
        logging.info(f"Agent {agent_id} provided response: {response[:100]}...")
        
        # Could enqueue follow-up actions, update metrics, etc.
        return {"status": "response_processed", "agent_id": agent_id}
    
    async def _process_agent_error_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process agent error events"""
        agent_id = event_data.get('agentId')
        error = event_data.get('error')
        
        logging.error(f"Agent {agent_id} encountered error: {error}")
        
        # Could trigger error handling, alerting, etc.
        return {"status": "error_logged", "agent_id": agent_id}
    
    # === Service Bus Trigger Processing ===
    
    async def process_service_bus_message(self, topic_name: str, message: Any) -> Dict[str, Any]:
        """Process a Service Bus message using registered handler"""
        try:
            if topic_name in self.service_bus_handlers:
                handler = self.service_bus_handlers[topic_name]
                result = await handler(message)
                return {"status": "success", "result": result}
            else:
                logging.warning(f"No handler registered for topic: {topic_name}")
                return {"status": "error", "error": f"No handler for topic {topic_name}"}
        except Exception as e:
            logging.error(f"Error processing Service Bus message from {topic_name}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_decision_event(self, message: Any) -> Dict[str, Any]:
        """Handle decision event messages from Service Bus"""
        try:
            # Parse message content
            if hasattr(message, 'body'):
                content = str(message.body)
            else:
                content = str(message)
            
            msg_data = json.loads(content)
            
            # Extract decision information
            decision_type = msg_data.get('decisionType')
            context = msg_data.get('context', {})
            options = msg_data.get('options', [])
            
            logging.info(f"Processing decision event: {decision_type}")
            
            # Process with orchestrator
            if self.orchestrator:
                decision_result = await self.orchestrator.process_decision(
                    decision_type, context, options
                )
                return {"decision_result": decision_result}
            else:
                return {"error": "Orchestrator not available"}
                
        except Exception as e:
            logging.error(f"Error handling decision event: {e}")
            return {"error": str(e)}
    
    # === Message Publishing ===
    
    async def enqueue_agent_request(self, agent_id: str, message: str, context: Dict[str, Any] = None) -> bool:
        """Enqueue an agent request message"""
        if not AZURE_AVAILABLE:
            logging.error("Azure libraries not available for queue operations")
            return False
        
        try:
            queue_client = QueueClient.from_connection_string(
                self.storage_conn, 
                queue_name=self.agent_requests_queue
            )
            
            request_data = {
                "agentId": agent_id,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "context": context or {}
            }
            
            await queue_client.send_message(json.dumps(request_data))
            return True
            
        except Exception as e:
            logging.error(f"Error enqueuing agent request: {e}")
            return False
    
    async def enqueue_agent_event(self, event_type: str, agent_id: str, data: Dict[str, Any] = None) -> bool:
        """Enqueue an agent event message"""
        if not AZURE_AVAILABLE:
            logging.error("Azure libraries not available for queue operations")
            return False
        
        try:
            queue_client = QueueClient.from_connection_string(
                self.storage_conn, 
                queue_name=self.agent_events_queue
            )
            
            event_data = {
                "eventType": event_type,
                "agentId": agent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data or {}
            }
            
            await queue_client.send_message(json.dumps(event_data))
            return True
            
        except Exception as e:
            logging.error(f"Error enqueuing agent event: {e}")
            return False
    
    async def publish_decision_event(self, decision_type: str, context: Dict[str, Any], options: list = None) -> bool:
        """Publish a decision event to Service Bus"""
        if not AZURE_AVAILABLE or not self.service_bus_conn:
            logging.error("Service Bus not available")
            return False
        
        try:
            async with ServiceBusClient.from_connection_string(self.service_bus_conn) as client:
                sender = client.get_topic_sender(topic_name=self.decision_events_topic)
                
                event_data = {
                    "decisionType": decision_type,
                    "context": context,
                    "options": options or [],
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                message = ServiceBusMessage(json.dumps(event_data))
                await sender.send_messages(message)
                
            return True
            
        except Exception as e:
            logging.error(f"Error publishing decision event: {e}")
            return False
    
    # === Handler Registration ===
    
    def register_queue_handler(self, queue_name: str, handler: Callable) -> None:
        """Register a custom queue handler"""
        self.queue_handlers[queue_name] = handler
        logging.info(f"Registered queue handler for: {queue_name}")
    
    def register_service_bus_handler(self, topic_name: str, handler: Callable) -> None:
        """Register a custom Service Bus handler"""
        self.service_bus_handlers[topic_name] = handler
        logging.info(f"Registered Service Bus handler for: {topic_name}")
    
    def register_http_handler(self, route: str, handler: Callable) -> None:
        """Register a custom HTTP handler"""
        self.http_handlers[route] = handler
        logging.info(f"Registered HTTP handler for: {route}")
    
    # === Azure Functions Integration ===
    
    def get_azure_queue_trigger(self, queue_name: str):
        """Get Azure Functions queue trigger decorator"""
        if not AZURE_AVAILABLE:
            raise ImportError("Azure Functions not available")
        
        def queue_trigger_wrapper(func_app: func.FunctionApp):
            @func_app.queue_trigger(arg_name="msg", queue_name=queue_name, connection="AzureWebJobsStorage")
            async def queue_trigger_func(msg: func.QueueMessage) -> None:
                try:
                    result = await self.process_queue_message(queue_name, msg)
                    logging.info(f"Queue trigger result for {queue_name}: {result}")
                except Exception as e:
                    logging.error(f"Queue trigger error for {queue_name}: {e}")
            
            return queue_trigger_func
        
        return queue_trigger_wrapper
    
    def get_azure_service_bus_trigger(self, topic_name: str):
        """Get Azure Functions Service Bus trigger decorator"""
        if not AZURE_AVAILABLE:
            raise ImportError("Azure Functions not available")
        
        def service_bus_trigger_wrapper(func_app: func.FunctionApp):
            @func_app.service_bus_topic_trigger(
                arg_name="msg", 
                topic_name=topic_name, 
                subscription_name="default",
                connection="SERVICE_BUS_CONNECTION_STRING"
            )
            async def service_bus_trigger_func(msg: func.ServiceBusMessage) -> None:
                try:
                    result = await self.process_service_bus_message(topic_name, msg)
                    logging.info(f"Service Bus trigger result for {topic_name}: {result}")
                except Exception as e:
                    logging.error(f"Service Bus trigger error for {topic_name}: {e}")
            
            return service_bus_trigger_func
        
        return service_bus_trigger_wrapper
    
    # === Configuration Validation ===
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate triggers configuration"""
        issues = []
        
        if not self.storage_conn:
            issues.append("Missing AzureWebJobsStorage connection string")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "storage_configured": bool(self.storage_conn),
            "service_bus_configured": bool(self.service_bus_conn),
            "handlers_registered": {
                "queue": list(self.queue_handlers.keys()),
                "service_bus": list(self.service_bus_handlers.keys()),
                "http": list(self.http_handlers.keys())
            }
        }


# Create singleton instance
triggers_manager = UnifiedTriggersManager()

# Export for backward compatibility
__all__ = ['triggers_manager', 'UnifiedTriggersManager']