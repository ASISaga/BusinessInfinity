"""
AOS Service Bus Client for BusinessInfinity

Provides a client interface for BusinessInfinity to communicate with
AgentOperatingSystem over Azure Service Bus.

This replaces direct imports of AOS with message-based communication.
"""

import logging
import asyncio
import os
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

try:
    from azure.servicebus.aio import ServiceBusClient, ServiceBusSender, ServiceBusReceiver
    from azure.servicebus import ServiceBusMessage, ServiceBusReceivedMessage
    AZURE_SERVICE_BUS_AVAILABLE = True
except ImportError:
    AZURE_SERVICE_BUS_AVAILABLE = False
    ServiceBusClient = None
    ServiceBusSender = None
    ServiceBusReceiver = None

# Import message contracts
# These are shared between AOS and BI
from dataclasses import dataclass, field, asdict
import json

logger = logging.getLogger("BusinessInfinity.AOSClient")


# =============================================================================
# Message Types (mirrored from AOS contracts)
# =============================================================================

class AOSMessageType:
    """Message types for AOS communication."""
    AGENT_QUERY = "aos.agent.query"
    AGENT_RESPONSE = "aos.agent.response"
    AGENT_LIST = "aos.agent.list"
    WORKFLOW_EXECUTE = "aos.workflow.execute"
    WORKFLOW_RESULT = "aos.workflow.result"
    STORAGE_GET = "aos.storage.get"
    STORAGE_SET = "aos.storage.set"
    STORAGE_RESULT = "aos.storage.result"
    MCP_CALL = "aos.mcp.call"
    MCP_RESULT = "aos.mcp.result"
    HEALTH_CHECK = "aos.system.health"
    HEALTH_RESPONSE = "aos.system.health.response"
    ERROR = "aos.error"


class AOSQueues:
    """Queue names for AOS communication."""
    AOS_REQUESTS = "aos-requests"
    BUSINESS_INFINITY_RESPONSES = "businessinfinity-responses"


@dataclass
class AOSMessageHeader:
    """Message header for AOS messages."""
    message_id: str
    correlation_id: str
    reply_to: str
    timestamp: str
    source: str
    target: str
    message_type: str
    priority: str = "normal"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AOSMessageHeader":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AOSMessage:
    """Message format for AOS communication."""
    header: AOSMessageHeader
    payload: Dict[str, Any]
    
    def to_json(self) -> str:
        return json.dumps({
            "header": self.header.to_dict(),
            "payload": self.payload
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> "AOSMessage":
        data = json.loads(json_str)
        return cls(
            header=AOSMessageHeader.from_dict(data.get("header", {})),
            payload=data.get("payload", {})
        )


# =============================================================================
# AOS Client
# =============================================================================

class AOSServiceBusClient:
    """
    Client for communicating with AgentOperatingSystem over Service Bus.
    
    Provides async methods for:
    - Agent queries
    - Workflow execution
    - Storage operations
    - MCP calls
    - Health checks
    """
    
    def __init__(
        self,
        connection_string: Optional[str] = None,
        request_queue: str = AOSQueues.AOS_REQUESTS,
        response_queue: str = AOSQueues.BUSINESS_INFINITY_RESPONSES,
        timeout_seconds: int = 30
    ):
        """
        Initialize AOS Service Bus client.
        
        Args:
            connection_string: Azure Service Bus connection string
            request_queue: Queue name for sending requests to AOS
            response_queue: Queue name for receiving responses from AOS
            timeout_seconds: Default timeout for requests
        """
        self.connection_string = connection_string or os.getenv("AZURE_SERVICEBUS_CONNECTION_STRING")
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.timeout_seconds = timeout_seconds
        
        self._client: Optional[ServiceBusClient] = None
        self._sender: Optional[ServiceBusSender] = None
        self._receiver: Optional[ServiceBusReceiver] = None
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._receiver_task: Optional[asyncio.Task] = None
        self._initialized = False
        
        self.logger = logger
    
    async def initialize(self):
        """Initialize Service Bus connections."""
        if self._initialized:
            return
        
        if not AZURE_SERVICE_BUS_AVAILABLE:
            self.logger.warning("Azure Service Bus SDK not available")
            return
        
        if not self.connection_string:
            self.logger.warning("No Service Bus connection string provided")
            return
        
        try:
            self._client = ServiceBusClient.from_connection_string(self.connection_string)
            self._sender = self._client.get_queue_sender(self.request_queue)
            self._receiver = self._client.get_queue_receiver(self.response_queue)
            
            # Start response receiver
            self._receiver_task = asyncio.create_task(self._receive_responses())
            
            self._initialized = True
            self.logger.info("AOS Service Bus client initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Service Bus client: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown Service Bus connections."""
        if self._receiver_task:
            self._receiver_task.cancel()
            try:
                await self._receiver_task
            except asyncio.CancelledError:
                pass
        
        if self._sender:
            await self._sender.close()
        if self._receiver:
            await self._receiver.close()
        if self._client:
            await self._client.close()
        
        self._initialized = False
        self.logger.info("AOS Service Bus client shutdown")
    
    async def _receive_responses(self):
        """Background task to receive responses."""
        while True:
            try:
                async for msg in self._receiver:
                    try:
                        body = msg.body.decode('utf-8') if isinstance(msg.body, bytes) else str(msg.body)
                        response = AOSMessage.from_json(body)
                        
                        correlation_id = response.header.correlation_id
                        if correlation_id in self._pending_requests:
                            future = self._pending_requests.pop(correlation_id)
                            if not future.done():
                                future.set_result(response)
                        
                        await self._receiver.complete_message(msg)
                        
                    except Exception as e:
                        self.logger.error(f"Error processing response: {e}")
                        await self._receiver.abandon_message(msg)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in response receiver: {e}")
                await asyncio.sleep(1)
    
    async def _send_request(
        self,
        message_type: str,
        payload: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send a request to AOS and wait for response.
        
        Args:
            message_type: Type of message to send
            payload: Message payload
            timeout: Optional timeout override
            
        Returns:
            Response payload
        """
        if not self._initialized:
            await self.initialize()
        
        if not self._sender:
            raise RuntimeError("Service Bus sender not available")
        
        # Create message
        correlation_id = str(uuid.uuid4())
        message = AOSMessage(
            header=AOSMessageHeader(
                message_id=str(uuid.uuid4()),
                correlation_id=correlation_id,
                reply_to=self.response_queue,
                timestamp=datetime.utcnow().isoformat(),
                source="businessinfinity",
                target="aos",
                message_type=message_type
            ),
            payload=payload
        )
        
        # Create future for response
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending_requests[correlation_id] = future
        
        try:
            # Send message
            sb_message = ServiceBusMessage(
                body=message.to_json(),
                content_type="application/json",
                correlation_id=correlation_id,
                message_id=message.header.message_id,
            )
            await self._sender.send_messages(sb_message)
            
            # Wait for response
            timeout_val = timeout or self.timeout_seconds
            response = await asyncio.wait_for(future, timeout=timeout_val)
            
            # Check for error
            if response.header.message_type == AOSMessageType.ERROR:
                error = response.payload
                raise RuntimeError(f"AOS Error: {error.get('error_message', 'Unknown error')}")
            
            return response.payload
            
        except asyncio.TimeoutError:
            self._pending_requests.pop(correlation_id, None)
            raise TimeoutError(f"Request timed out after {timeout_val} seconds")
        except Exception as e:
            self._pending_requests.pop(correlation_id, None)
            raise
    
    # ==========================================================================
    # Agent Methods
    # ==========================================================================
    
    async def ask_agent(
        self,
        agent_id: str,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Ask an agent a question.
        
        Args:
            agent_id: ID of the agent to query
            query: The question to ask
            context: Optional context for the query
            timeout: Optional timeout override
            
        Returns:
            Agent response including answer, confidence, etc.
        """
        payload = {
            "agent_id": agent_id,
            "query": query,
            "context": context or {}
        }
        
        return await self._send_request(AOSMessageType.AGENT_QUERY, payload, timeout)
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """
        List available agents.
        
        Returns:
            List of agent info dictionaries
        """
        response = await self._send_request(AOSMessageType.AGENT_LIST, {})
        return response.get("agents", [])
    
    # ==========================================================================
    # Workflow Methods
    # ==========================================================================
    
    async def execute_workflow(
        self,
        workflow_name: str,
        inputs: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            workflow_name: Name of the workflow to execute
            inputs: Workflow inputs
            workflow_id: Optional workflow ID
            timeout: Optional timeout override
            
        Returns:
            Workflow result
        """
        payload = {
            "workflow_id": workflow_id or str(uuid.uuid4()),
            "workflow_name": workflow_name,
            "inputs": inputs or {}
        }
        
        return await self._send_request(
            AOSMessageType.WORKFLOW_EXECUTE,
            payload,
            timeout or 60  # Workflows may take longer
        )
    
    # ==========================================================================
    # Storage Methods
    # ==========================================================================
    
    async def storage_get(self, container: str, key: str) -> Optional[Any]:
        """Get value from storage."""
        response = await self._send_request(
            AOSMessageType.STORAGE_GET,
            {"container": container, "key": key}
        )
        return response.get("data") if response.get("success") else None
    
    async def storage_set(self, container: str, key: str, value: Any) -> bool:
        """Set value in storage."""
        response = await self._send_request(
            AOSMessageType.STORAGE_SET,
            {"container": container, "key": key, "value": value}
        )
        return response.get("success", False)
    
    # ==========================================================================
    # MCP Methods
    # ==========================================================================
    
    async def mcp_call(
        self,
        server: str,
        method: str,
        args: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Call an MCP server method.
        
        Args:
            server: MCP server name
            method: Method to call
            args: Method arguments
            
        Returns:
            Method result
        """
        response = await self._send_request(
            AOSMessageType.MCP_CALL,
            {"server": server, "method": method, "args": args or {}}
        )
        return response.get("result")
    
    # ==========================================================================
    # System Methods
    # ==========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Check AOS health."""
        return await self._send_request(AOSMessageType.HEALTH_CHECK, {})
    
    @property
    def is_available(self) -> bool:
        """Check if client is available."""
        return self._initialized and self._sender is not None


# =============================================================================
# Singleton Instance
# =============================================================================

_aos_client: Optional[AOSServiceBusClient] = None


def get_aos_client() -> AOSServiceBusClient:
    """Get or create the AOS Service Bus client singleton."""
    global _aos_client
    if _aos_client is None:
        _aos_client = AOSServiceBusClient()
    return _aos_client


async def initialize_aos_client() -> AOSServiceBusClient:
    """Initialize and return the AOS client."""
    client = get_aos_client()
    await client.initialize()
    return client


__all__ = [
    "AOSServiceBusClient",
    "AOSMessageType",
    "AOSQueues",
    "get_aos_client",
    "initialize_aos_client",
]
