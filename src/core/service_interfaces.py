"""
Service Interfaces for Business Infinity

Provides clean service interfaces that wrap AOS infrastructure services,
enabling better testability, decoupling, and future-proofing.

Following AOS_UTILIZATION_ANALYSIS.md Priority 1 recommendations.
"""

from typing import Dict, Any, List, Optional, Protocol
from abc import ABC, abstractmethod


class IStorageService(Protocol):
    """
    Storage Service Interface
    
    Provides abstraction over AOS storage services for better testability
    and decoupling from concrete implementations.
    """
    
    async def save(self, container: str, key: str, data: Any) -> bool:
        """Save data to storage."""
        ...
    
    async def load(self, container: str, key: str) -> Optional[Any]:
        """Load data from storage."""
        ...
    
    async def delete(self, container: str, key: str) -> bool:
        """Delete data from storage."""
        ...
    
    async def list_keys(self, container: str, prefix: str = "") -> List[str]:
        """List keys in container."""
        ...
    
    async def exists(self, container: str, key: str) -> bool:
        """Check if key exists."""
        ...


class IMessagingService(Protocol):
    """
    Messaging Service Interface
    
    Provides abstraction over AOS messaging services for inter-agent
    communication and event-driven architecture.
    """
    
    async def publish(self, topic: str, message: Dict[str, Any]) -> bool:
        """Publish message to topic."""
        ...
    
    async def subscribe(self, topic: str, handler: callable) -> bool:
        """Subscribe to topic with handler."""
        ...
    
    async def send_direct(self, agent_id: str, message: Dict[str, Any]) -> Any:
        """Send direct message to agent."""
        ...
    
    async def send_request(self, agent_id: str, request: Dict[str, Any], timeout: int = 30) -> Any:
        """Send request and wait for response."""
        ...


class IWorkflowService(Protocol):
    """
    Workflow Service Interface
    
    Provides abstraction over AOS orchestration services for workflow
    execution and management.
    """
    
    async def execute_workflow(self, workflow_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow."""
        ...
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution status."""
        ...
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel running workflow."""
        ...
    
    async def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows."""
        ...


class IAuthService(Protocol):
    """
    Authentication Service Interface
    
    Provides abstraction over AOS authentication services.
    """
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Authenticate user/agent."""
        ...
    
    async def authorize(self, principal: str, resource: str, action: str) -> bool:
        """Check authorization."""
        ...
    
    async def get_principal(self, token: str) -> Optional[Dict[str, Any]]:
        """Get principal from token."""
        ...


# Concrete implementations wrapping AOS services

class AOSStorageService(IStorageService):
    """Storage service implementation using AOS UnifiedStorageManager."""
    
    def __init__(self, storage_manager):
        """Initialize with AOS storage manager."""
        self.storage = storage_manager
    
    async def save(self, container: str, key: str, data: Any) -> bool:
        """Save data to storage."""
        try:
            await self.storage.save(container, key, data)
            return True
        except Exception:
            return False
    
    async def load(self, container: str, key: str) -> Optional[Any]:
        """Load data from storage."""
        try:
            return await self.storage.load(container, key)
        except Exception:
            return None
    
    async def delete(self, container: str, key: str) -> bool:
        """Delete data from storage."""
        try:
            await self.storage.delete(container, key)
            return True
        except Exception:
            return False
    
    async def list_keys(self, container: str, prefix: str = "") -> List[str]:
        """List keys in container."""
        try:
            return await self.storage.list_keys(container, prefix)
        except Exception:
            return []
    
    async def exists(self, container: str, key: str) -> bool:
        """Check if key exists."""
        try:
            result = await self.storage.load(container, key)
            return result is not None
        except Exception:
            return False


class AOSMessagingService(IMessagingService):
    """Messaging service implementation using AOS ServiceBusManager."""
    
    def __init__(self, messaging_manager):
        """Initialize with AOS messaging manager."""
        self.messaging = messaging_manager
    
    async def publish(self, topic: str, message: Dict[str, Any]) -> bool:
        """Publish message to topic."""
        try:
            await self.messaging.publish(topic, message)
            return True
        except Exception:
            return False
    
    async def subscribe(self, topic: str, handler: callable) -> bool:
        """Subscribe to topic with handler."""
        try:
            await self.messaging.subscribe(topic, handler)
            return True
        except Exception:
            return False
    
    async def send_direct(self, agent_id: str, message: Dict[str, Any]) -> Any:
        """Send direct message to agent."""
        try:
            return await self.messaging.send_direct(agent_id, message)
        except Exception:
            return None
    
    async def send_request(self, agent_id: str, request: Dict[str, Any], timeout: int = 30) -> Any:
        """Send request and wait for response."""
        try:
            return await self.messaging.send_request(agent_id, request, timeout)
        except Exception:
            return None


class AOSWorkflowService(IWorkflowService):
    """Workflow service implementation using AOS OrchestrationEngine."""
    
    def __init__(self, orchestration_engine):
        """Initialize with AOS orchestration engine."""
        self.orchestration = orchestration_engine
    
    async def execute_workflow(self, workflow_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow."""
        try:
            return await self.orchestration.execute_workflow(workflow_id, context)
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution status."""
        try:
            return await self.orchestration.get_workflow_status(workflow_id)
        except Exception as e:
            return {"status": "unknown", "error": str(e)}
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel running workflow."""
        try:
            await self.orchestration.cancel_workflow(workflow_id)
            return True
        except Exception:
            return False
    
    async def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows."""
        try:
            return await self.orchestration.list_workflows()
        except Exception:
            return []
