"""
Generic Service Bus Integration for Azure Functions Runtime

Provides generic Azure Service Bus integration that can be used by any
application built on the runtime.
"""

import logging
import json
from typing import Dict, Any, Optional, Callable, List, Awaitable
from dataclasses import dataclass
from enum import Enum

try:
    import azure.functions as func
    AZURE_FUNCTIONS_AVAILABLE = True
except ImportError:
    AZURE_FUNCTIONS_AVAILABLE = False
    func = None


class MessageType(Enum):
    """Common message types for service bus."""
    EVENT = "event"
    COMMAND = "command"
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"


# Type alias for message handlers
MessageHandler = Callable[[Dict[str, Any]], Awaitable[bool]]


@dataclass
class MessageRoute:
    """
    Service bus message route definition.
    
    Maps message types to handler functions.
    """
    message_type: str
    handler: MessageHandler
    description: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ServiceBusRegistry:
    """
    Generic registry for service bus message handlers.
    
    Similar to RouteRegistry but for service bus messages instead of HTTP routes.
    """
    
    def __init__(self):
        self.handlers: Dict[str, MessageRoute] = {}
        self.logger = logging.getLogger(__name__)
    
    def register(
        self,
        message_type: str,
        handler: MessageHandler,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> MessageRoute:
        """
        Register a message handler.
        
        Args:
            message_type: Type of message to handle (e.g., "agent_request", "decision_event")
            handler: Async function to handle the message
            description: Human-readable description
            tags: Tags for grouping/filtering
            
        Returns:
            The registered MessageRoute
        """
        if tags is None:
            tags = []
        
        route = MessageRoute(
            message_type=message_type,
            handler=handler,
            description=description,
            tags=tags
        )
        
        self.handlers[message_type] = route
        self.logger.info(f"Registered message handler for type: {message_type}")
        return route
    
    def get_handler(self, message_type: str) -> Optional[MessageHandler]:
        """Get handler for a message type."""
        route = self.handlers.get(message_type)
        return route.handler if route else None
    
    def get_all_handlers(self) -> Dict[str, MessageRoute]:
        """Get all registered handlers."""
        return self.handlers.copy()
    
    async def dispatch(self, message: Dict[str, Any]) -> bool:
        """
        Dispatch a message to the appropriate handler.
        
        Args:
            message: Message data (should include "type" field)
            
        Returns:
            True if message was handled successfully, False otherwise
        """
        message_type = message.get("type", "unknown")
        handler = self.get_handler(message_type)
        
        if handler:
            try:
                return await handler(message)
            except Exception as e:
                self.logger.error(f"Error handling message type {message_type}: {e}")
                return False
        else:
            self.logger.warning(f"No handler registered for message type: {message_type}")
            return False


class ServiceBusRuntime:
    """
    Generic Service Bus runtime for Azure Functions.
    
    Provides:
    - Queue trigger handling
    - Topic/subscription handling
    - Message routing and dispatching
    - Error handling and retry
    """
    
    def __init__(
        self,
        message_registry: Optional[ServiceBusRegistry] = None,
        connection_string_env_var: str = "AzureServiceBusConnectionString"
    ):
        """
        Initialize Service Bus runtime.
        
        Args:
            message_registry: Optional pre-configured message registry
            connection_string_env_var: Environment variable name for connection string
        """
        self.message_registry = message_registry or ServiceBusRegistry()
        self.connection_string_env_var = connection_string_env_var
        self.logger = logging.getLogger(__name__)
    
    def create_queue_handler(self, queue_name: str) -> Callable:
        """
        Create a queue trigger handler function.
        
        Args:
            queue_name: Name of the queue
            
        Returns:
            Async function that can be used as Azure Functions queue trigger
        """
        async def queue_handler(msg: func.ServiceBusMessage) -> None:
            """Handle service bus queue message."""
            try:
                # Parse message body
                message_body = msg.get_body().decode('utf-8')
                
                try:
                    message_data = json.loads(message_body)
                except json.JSONDecodeError:
                    message_data = {"raw_message": message_body}
                
                # Add metadata
                message_data["_queue"] = queue_name
                message_data["_message_id"] = msg.message_id
                
                # Dispatch to handler
                success = await self.message_registry.dispatch(message_data)
                
                if not success:
                    self.logger.error(f"Failed to process message from queue {queue_name}")
                    # In a real implementation, might want to dead-letter the message
                    
            except Exception as e:
                self.logger.error(f"Error processing queue message: {e}")
                raise
        
        return queue_handler
    
    def create_topic_handler(self, topic_name: str, subscription_name: str) -> Callable:
        """
        Create a topic/subscription trigger handler function.
        
        Args:
            topic_name: Name of the topic
            subscription_name: Name of the subscription
            
        Returns:
            Async function that can be used as Azure Functions topic trigger
        """
        async def topic_handler(msg: func.ServiceBusMessage) -> None:
            """Handle service bus topic message."""
            try:
                # Parse message body
                message_body = msg.get_body().decode('utf-8')
                
                try:
                    message_data = json.loads(message_body)
                except json.JSONDecodeError:
                    message_data = {"raw_message": message_body}
                
                # Add metadata
                message_data["_topic"] = topic_name
                message_data["_subscription"] = subscription_name
                message_data["_message_id"] = msg.message_id
                
                # Dispatch to handler
                success = await self.message_registry.dispatch(message_data)
                
                if not success:
                    self.logger.error(
                        f"Failed to process message from topic {topic_name}, "
                        f"subscription {subscription_name}"
                    )
                    
            except Exception as e:
                self.logger.error(f"Error processing topic message: {e}")
                raise
        
        return topic_handler
    
    def register_to_azure_functions(
        self,
        func_app: Any,
        queue_name: Optional[str] = None,
        topic_name: Optional[str] = None,
        subscription_name: Optional[str] = None
    ):
        """
        Register service bus handlers to Azure Functions app.
        
        Args:
            func_app: Azure Functions FunctionApp instance
            queue_name: Optional queue name for queue trigger
            topic_name: Optional topic name for topic trigger
            subscription_name: Optional subscription name for topic trigger
        """
        if not AZURE_FUNCTIONS_AVAILABLE:
            raise RuntimeError("azure-functions package is not installed")
        
        # Register queue trigger
        if queue_name:
            handler = self.create_queue_handler(queue_name)
            
            func_app.service_bus_queue_trigger(
                arg_name="msg",
                queue_name=queue_name,
                connection=self.connection_string_env_var
            )(handler)
            
            self.logger.info(f"Registered queue trigger for: {queue_name}")
        
        # Register topic trigger
        if topic_name and subscription_name:
            handler = self.create_topic_handler(topic_name, subscription_name)
            
            func_app.service_bus_topic_trigger(
                arg_name="msg",
                topic_name=topic_name,
                subscription_name=subscription_name,
                connection=self.connection_string_env_var
            )(handler)
            
            self.logger.info(
                f"Registered topic trigger for: {topic_name}/{subscription_name}"
            )


def create_servicebus_runtime(
    message_registry: Optional[ServiceBusRegistry] = None,
    connection_string_env_var: str = "AzureServiceBusConnectionString"
) -> ServiceBusRuntime:
    """
    Factory function to create Service Bus runtime.
    
    Args:
        message_registry: Optional pre-configured message registry
        connection_string_env_var: Environment variable name for connection string
        
    Returns:
        Configured ServiceBusRuntime instance
    """
    return ServiceBusRuntime(
        message_registry=message_registry,
        connection_string_env_var=connection_string_env_var
    )
