"""
Generic Messaging Abstractions for Runtime

Provides generic messaging interfaces that can be used by any application.
These delegate to AgentOperatingSystem when available.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Awaitable
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class Message:
    """
    Generic message structure.
    
    Can be used for any messaging system (Service Bus, Event Hub, etc.)
    """
    id: str
    type: str
    body: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_json(self) -> str:
        """Serialize message to JSON."""
        return json.dumps({
            'id': self.id,
            'type': self.type,
            'body': self.body,
            'timestamp': self.timestamp.isoformat(),
            'correlation_id': self.correlation_id,
            'causation_id': self.causation_id,
            'metadata': self.metadata
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Deserialize message from JSON."""
        data = json.loads(json_str)
        return cls(
            id=data['id'],
            type=data['type'],
            body=data['body'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            correlation_id=data.get('correlation_id'),
            causation_id=data.get('causation_id'),
            metadata=data.get('metadata', {})
        )


# Type alias for message handlers
MessageCallback = Callable[[Message], Awaitable[None]]


class IMessagingProvider(ABC):
    """
    Generic messaging provider interface.
    
    Applications should use this interface instead of directly using
    Azure Service Bus, Event Hub, etc.
    """
    
    @abstractmethod
    async def publish(self, message: Message, topic: Optional[str] = None) -> bool:
        """Publish a message to a topic/queue."""
        pass
    
    @abstractmethod
    async def subscribe(
        self,
        topic: str,
        callback: MessageCallback,
        subscription_name: Optional[str] = None
    ) -> str:
        """
        Subscribe to a topic with a callback.
        
        Returns:
            Subscription ID that can be used to unsubscribe
        """
        pass
    
    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from a topic."""
        pass


class MemoryMessagingProvider(IMessagingProvider):
    """
    In-memory messaging provider for development/testing.
    
    Uses simple pub/sub pattern with callbacks.
    """
    
    def __init__(self):
        self._subscriptions: Dict[str, Dict[str, MessageCallback]] = {}
    
    async def publish(self, message: Message, topic: Optional[str] = None) -> bool:
        """Publish message to all subscribers of the topic."""
        topic = topic or "default"
        
        if topic in self._subscriptions:
            for callback in self._subscriptions[topic].values():
                try:
                    await callback(message)
                except Exception as e:
                    # Log error but continue with other subscribers
                    print(f"Error in message callback: {e}")
        
        return True
    
    async def subscribe(
        self,
        topic: str,
        callback: MessageCallback,
        subscription_name: Optional[str] = None
    ) -> str:
        """Subscribe to a topic."""
        import uuid
        
        subscription_id = subscription_name or str(uuid.uuid4())
        
        if topic not in self._subscriptions:
            self._subscriptions[topic] = {}
        
        self._subscriptions[topic][subscription_id] = callback
        return subscription_id
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from all topics."""
        for topic_subs in self._subscriptions.values():
            if subscription_id in topic_subs:
                del topic_subs[subscription_id]
                return True
        return False


class AOSMessagingProvider(IMessagingProvider):
    """
    Messaging provider that delegates to AgentOperatingSystem.
    
    This wraps AOS messaging services to provide a consistent interface.
    """
    
    def __init__(self, aos_messaging_manager=None):
        """
        Initialize with AOS messaging manager.
        
        Args:
            aos_messaging_manager: AgentOperatingSystem messaging manager instance
        """
        if aos_messaging_manager is None:
            # Try to import and create AOS messaging manager
            try:
                from AgentOperatingSystem.messaging.manager import UnifiedMessagingManager
                self.messaging_manager = UnifiedMessagingManager()
            except ImportError:
                raise RuntimeError(
                    "AgentOperatingSystem is not installed. "
                    "Install with: pip install AgentOperatingSystem"
                )
        else:
            self.messaging_manager = aos_messaging_manager
    
    async def publish(self, message: Message, topic: Optional[str] = None) -> bool:
        """Publish message via AOS messaging."""
        try:
            await self.messaging_manager.publish(
                topic=topic or "default",
                message=message.body,
                message_type=message.type,
                correlation_id=message.correlation_id,
                causation_id=message.causation_id
            )
            return True
        except Exception:
            return False
    
    async def subscribe(
        self,
        topic: str,
        callback: MessageCallback,
        subscription_name: Optional[str] = None
    ) -> str:
        """Subscribe to topic via AOS messaging."""
        try:
            # Wrap callback to convert AOS message to runtime Message
            async def aos_callback(aos_message):
                message = Message(
                    id=aos_message.get('id', ''),
                    type=aos_message.get('type', ''),
                    body=aos_message.get('body', {}),
                    timestamp=datetime.utcnow(),
                    correlation_id=aos_message.get('correlation_id'),
                    causation_id=aos_message.get('causation_id'),
                    metadata=aos_message.get('metadata', {})
                )
                await callback(message)
            
            subscription_id = await self.messaging_manager.subscribe(
                topic=topic,
                callback=aos_callback,
                subscription_name=subscription_name
            )
            return subscription_id
        except Exception:
            return ""
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe via AOS messaging."""
        try:
            await self.messaging_manager.unsubscribe(subscription_id)
            return True
        except Exception:
            return False


def create_messaging_provider(
    provider_type: str = "memory",
    **kwargs
) -> IMessagingProvider:
    """
    Factory function to create messaging provider.
    
    Args:
        provider_type: Type of messaging ("memory", "aos")
        **kwargs: Additional arguments for the provider
        
    Returns:
        Messaging provider instance
    """
    if provider_type == "memory":
        return MemoryMessagingProvider()
    elif provider_type == "aos":
        return AOSMessagingProvider(kwargs.get('aos_messaging_manager'))
    else:
        raise ValueError(f"Unknown messaging provider type: {provider_type}")
