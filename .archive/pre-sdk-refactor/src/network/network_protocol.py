"""
Network Protocol for Inter-Boardroom Communication

Extends the existing A2A (Agent-to-Agent) protocol to enable
boardroom-to-boardroom communication across the global network
of autonomous boardrooms.
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Import AOS conversation system
try:
    from aos.messaging.conversation_system import ConversationRole, ConversationType, AOSConversationSystem
    CONVERSATION_SYSTEM_AVAILABLE = True
except ImportError:
    CONVERSATION_SYSTEM_AVAILABLE = False
    logging.warning("AOS conversation system not available for network protocol")
    # Fallback classes
    class ConversationRole:
        pass
    class ConversationType:
        pass

class MessageType(Enum):
    """Types of inter-boardroom messages"""
    DISCOVERY = "discovery"
    NEGOTIATION = "negotiation"
    AGREEMENT = "agreement"
    PROPOSAL = "proposal"
    VOTE = "vote"
    COVENANT = "covenant"
    STATUS = "status"
    HEARTBEAT = "heartbeat"

class BoardroomStatus(Enum):
    """Status of a boardroom node"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    NEGOTIATING = "negotiating"
    VERIFIED = "verified"
    SUSPENDED = "suspended"

@dataclass
class EnterpriseIdentity:
    """Enterprise identity for LinkedIn-verified organizations"""
    company_id: str
    company_name: str
    linkedin_url: str
    verification_status: str
    industry: str
    size: str
    location: str
    verified_at: datetime = field(default_factory=datetime.now)
    verification_expires: Optional[datetime] = None

@dataclass
class BoardroomNode:
    """Represents a boardroom node in the network"""
    node_id: str
    enterprise_identity: EnterpriseIdentity
    endpoint_url: str
    status: BoardroomStatus
    capabilities: Set[str] = field(default_factory=set)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    network_joined: datetime = field(default_factory=datetime.now)
    
    # Agent composition
    active_agents: Set[str] = field(default_factory=set)
    agent_capabilities: Dict[str, List[str]] = field(default_factory=dict)
    
    def is_verified(self) -> bool:
        """Check if the boardroom node is LinkedIn verified"""
        return (self.enterprise_identity.verification_status == "verified" and
                (self.enterprise_identity.verification_expires is None or
                 self.enterprise_identity.verification_expires > datetime.now()))

@dataclass
class InterBoardroomMessage:
    """Message for communication between boardroom nodes"""
    message_id: str
    message_type: MessageType
    from_node_id: str
    to_node_id: str
    subject: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    signature: Optional[str] = None
    
    # Context for conversation integration
    conversation_id: Optional[str] = None
    requires_response: bool = False
    priority: str = "medium"

class NetworkProtocol:
    """
    Network Protocol for Global Network of Autonomous Boardrooms
    
    Handles inter-boardroom communication, discovery, negotiation,
    and covenant management across the distributed network.
    """
    
    def __init__(self, local_node: BoardroomNode):
        self.local_node = local_node
        self.logger = logging.getLogger(__name__)
        self.connected_nodes: Dict[str, BoardroomNode] = {}
        self.message_queue: List[InterBoardroomMessage] = []
        self.pending_negotiations: Dict[str, Dict[str, Any]] = {}
        
        # Integration with AOS conversation system
        self.conversation_manager = None
        if CONVERSATION_SYSTEM_AVAILABLE:
            try:
                self.conversation_manager = AOSConversationSystem()
            except Exception as e:
                self.logger.warning(f"Could not initialize AOS conversation manager: {e}")
    
    async def join_network(self) -> bool:
        """Join the global network of boardrooms"""
        if not self.local_node.is_verified():
            self.logger.error("Cannot join network: LinkedIn verification required")
            return False
        
        self.logger.info(f"Joining network as {self.local_node.enterprise_identity.company_name}")
        
        # Send discovery message to announce presence
        discovery_message = InterBoardroomMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.DISCOVERY,
            from_node_id=self.local_node.node_id,
            to_node_id="*",  # Broadcast
            subject="Network Discovery",
            content={
                "action": "join",
                "enterprise": {
                    "name": self.local_node.enterprise_identity.company_name,
                    "industry": self.local_node.enterprise_identity.industry,
                    "capabilities": list(self.local_node.capabilities),
                    "agents": list(self.local_node.active_agents)
                }
            }
        )
        
        await self._broadcast_message(discovery_message)
        self.local_node.status = BoardroomStatus.ACTIVE
        
        self.logger.info("Successfully joined network")
        return True
    
    async def discover_boardrooms(self, criteria: Dict[str, Any] = None) -> List[BoardroomNode]:
        """Discover other boardrooms in the network"""
        discovery_message = InterBoardroomMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.DISCOVERY,
            from_node_id=self.local_node.node_id,
            to_node_id="*",  # Broadcast
            subject="Boardroom Discovery",
            content={
                "action": "discover",
                "criteria": criteria or {}
            },
            requires_response=True
        )
        
        await self._broadcast_message(discovery_message)
        
        # Wait for responses (simplified for now)
        await asyncio.sleep(2)
        
        discovered_nodes = list(self.connected_nodes.values())
        self.logger.info(f"Discovered {len(discovered_nodes)} boardrooms")
        return discovered_nodes
    
    async def initiate_negotiation(self, target_node_id: str, negotiation_type: str, 
                                 proposal: Dict[str, Any]) -> str:
        """Initiate negotiation with another boardroom"""
        negotiation_id = str(uuid.uuid4())
        
        negotiation_message = InterBoardroomMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.NEGOTIATION,
            from_node_id=self.local_node.node_id,
            to_node_id=target_node_id,
            subject=f"Negotiation: {negotiation_type}",
            content={
                "negotiation_id": negotiation_id,
                "type": negotiation_type,
                "proposal": proposal,
                "from_enterprise": self.local_node.enterprise_identity.company_name
            },
            requires_response=True
        )
        
        # Create conversation for negotiation tracking
        if self.conversation_manager:
            try:
                conversation_id = await self.conversation_manager.create_a2a_communication(
                    from_agent=ConversationRole.CEO,  # Default to CEO for inter-boardroom
                    to_agent=ConversationRole.EXTERNAL_STAKEHOLDER,
                    conversation_type=ConversationType.NEGOTIATION,
                    message_content=f"Inter-boardroom negotiation: {negotiation_type}",
                    context={
                        "negotiation_id": negotiation_id,
                        "target_node": target_node_id,
                        "negotiation_type": negotiation_type,
                        "inter_boardroom": True
                    }
                )
                negotiation_message.conversation_id = conversation_id
            except Exception as e:
                self.logger.warning(f"Could not create conversation for negotiation: {e}")
        
        await self._send_message(negotiation_message)
        
        # Track negotiation
        self.pending_negotiations[negotiation_id] = {
            "target_node_id": target_node_id,
            "type": negotiation_type,
            "status": "pending",
            "initiated_at": datetime.now(),
            "conversation_id": negotiation_message.conversation_id
        }
        
        self.logger.info(f"Initiated negotiation {negotiation_id} with {target_node_id}")
        return negotiation_id
    
    async def send_proposal(self, target_node_id: str, proposal_type: str, 
                          proposal_data: Dict[str, Any]) -> str:
        """Send a proposal to another boardroom"""
        proposal_message = InterBoardroomMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.PROPOSAL,
            from_node_id=self.local_node.node_id,
            to_node_id=target_node_id,
            subject=f"Proposal: {proposal_type}",
            content={
                "type": proposal_type,
                "data": proposal_data,
                "from_enterprise": self.local_node.enterprise_identity.company_name
            },
            requires_response=True
        )
        
        await self._send_message(proposal_message)
        self.logger.info(f"Sent proposal to {target_node_id}: {proposal_type}")
        return proposal_message.message_id
    
    async def handle_incoming_message(self, message: InterBoardroomMessage):
        """Handle incoming messages from other boardrooms"""
        self.logger.info(f"Received {message.message_type.value} from {message.from_node_id}")
        
        # Route message based on type
        if message.message_type == MessageType.DISCOVERY:
            await self._handle_discovery_message(message)
        elif message.message_type == MessageType.NEGOTIATION:
            await self._handle_negotiation_message(message)
        elif message.message_type == MessageType.PROPOSAL:
            await self._handle_proposal_message(message)
        elif message.message_type == MessageType.AGREEMENT:
            await self._handle_agreement_message(message)
        elif message.message_type == MessageType.HEARTBEAT:
            await self._handle_heartbeat_message(message)
        else:
            self.logger.warning(f"Unknown message type: {message.message_type}")
    
    async def _handle_discovery_message(self, message: InterBoardroomMessage):
        """Handle discovery messages"""
        content = message.content
        
        if content.get("action") == "join":
            # Another boardroom is joining the network
            enterprise_info = content.get("enterprise", {})
            self.logger.info(f"Boardroom joined network: {enterprise_info.get('name')}")
            
        elif content.get("action") == "discover":
            # Respond to discovery request
            response_message = InterBoardroomMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.DISCOVERY,
                from_node_id=self.local_node.node_id,
                to_node_id=message.from_node_id,
                subject="Discovery Response",
                content={
                    "action": "response",
                    "enterprise": {
                        "name": self.local_node.enterprise_identity.company_name,
                        "industry": self.local_node.enterprise_identity.industry,
                        "capabilities": list(self.local_node.capabilities),
                        "agents": list(self.local_node.active_agents),
                        "verified": self.local_node.is_verified()
                    }
                }
            )
            await self._send_message(response_message)
    
    async def _handle_negotiation_message(self, message: InterBoardroomMessage):
        """Handle negotiation messages"""
        content = message.content
        negotiation_id = content.get("negotiation_id")
        
        self.logger.info(f"Received negotiation from {content.get('from_enterprise')}")
        
        # Create conversation for tracking this negotiation
        if self.conversation_manager:
            try:
                conversation_id = await self.conversation_manager.create_a2a_communication(
                    from_agent=ConversationRole.EXTERNAL_STAKEHOLDER,
                    to_agent=ConversationRole.CEO,
                    conversation_type=ConversationType.NEGOTIATION,
                    message_content=f"Incoming negotiation: {content.get('type')}",
                    context={
                        "negotiation_id": negotiation_id,
                        "from_node": message.from_node_id,
                        "from_enterprise": content.get('from_enterprise'),
                        "inter_boardroom": True,
                        "external_negotiation": True
                    }
                )
                self.logger.info(f"Created conversation {conversation_id} for negotiation")
            except Exception as e:
                self.logger.warning(f"Could not create conversation for incoming negotiation: {e}")
    
    async def _handle_proposal_message(self, message: InterBoardroomMessage):
        """Handle proposal messages"""
        content = message.content
        self.logger.info(f"Received proposal from {content.get('from_enterprise')}: {content.get('type')}")
        
        # Log proposal for boardroom consideration
        # In a full implementation, this would trigger the boardroom decision process
    
    async def _handle_agreement_message(self, message: InterBoardroomMessage):
        """Handle agreement messages"""
        self.logger.info(f"Received agreement from {message.from_node_id}")
        
    async def _handle_heartbeat_message(self, message: InterBoardroomMessage):
        """Handle heartbeat messages"""
        if message.from_node_id in self.connected_nodes:
            self.connected_nodes[message.from_node_id].last_heartbeat = datetime.now()
    
    async def _send_message(self, message: InterBoardroomMessage):
        """Send message to specific node"""
        # In a real implementation, this would use actual networking
        self.logger.info(f"Sending {message.message_type.value} to {message.to_node_id}")
        # Simulate message sending
        self.message_queue.append(message)
    
    async def _broadcast_message(self, message: InterBoardroomMessage):
        """Broadcast message to all connected nodes"""
        # In a real implementation, this would use actual networking
        self.logger.info(f"Broadcasting {message.message_type.value}")
        self.message_queue.append(message)
    
    async def send_heartbeat(self):
        """Send heartbeat to maintain network presence"""
        heartbeat_message = InterBoardroomMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.HEARTBEAT,
            from_node_id=self.local_node.node_id,
            to_node_id="*",
            subject="Heartbeat",
            content={
                "status": self.local_node.status.value,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        await self._broadcast_message(heartbeat_message)
    
    async def get_network_status(self) -> Dict[str, Any]:
        """Get current network status"""
        return {
            "local_node": {
                "id": self.local_node.node_id,
                "enterprise": self.local_node.enterprise_identity.company_name,
                "status": self.local_node.status.value,
                "verified": self.local_node.is_verified(),
                "agents": list(self.local_node.active_agents),
                "capabilities": list(self.local_node.capabilities)
            },
            "connected_nodes": len(self.connected_nodes),
            "pending_negotiations": len(self.pending_negotiations),
            "message_queue_size": len(self.message_queue)
        }