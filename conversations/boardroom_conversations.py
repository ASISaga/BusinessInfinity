"""
Boardroom Conversation Manager

Implements the high-level conversation management for Business Infinity
boardroom operations, including A2A (Agent-to-Agent) communication.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from .conversation_system import (
    Conversation,
    ConversationType,
    ConversationRole,
    ConversationStatus,
    ConversationPriority,
    ConversationSystem,
    InMemoryConversationSystem,
    ConversationTemplateManager
)

# Import storage system
try:
    from core.features.storage import UnifiedStorageManager
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False
    logging.warning("Storage system not available for conversations")


class BoardroomConversationManager:
    """
    Manages boardroom conversations and agent-to-agent communication
    Implements the conversation patterns defined in conversations/specification.md
    """
    
    def __init__(self, storage_manager: Optional[Any] = None):
        self.logger = logging.getLogger(__name__)
        
        # Initialize conversation system
        if STORAGE_AVAILABLE and storage_manager:
            self.conversation_system = StorageBackedConversationSystem(storage_manager)
        else:
            self.conversation_system = InMemoryConversationSystem()
        
        self.template_manager = ConversationTemplateManager()
        
        # Agent role mappings based on specification.md
        self.role_responsibilities = self._initialize_role_responsibilities()
        self.conversation_champions = self._initialize_conversation_champions()
        
    def _initialize_role_responsibilities(self) -> Dict[ConversationRole, Dict[str, Any]]:
        """Initialize role responsibilities from specification.md"""
        return {
            ConversationRole.FOUNDER: {
                "roles": ["Vision Steward", "Delegation Authorizer", "Strategic Signer", "Reconciliation Sponsor"],
                "champion_conversations": [
                    ConversationType.STRATEGIC_FRAME,
                    ConversationType.HIGH_RISK_DECISION,
                    ConversationType.ENROLLMENT_SPONSOR,
                    ConversationType.GOVERNANCE_REVIEW
                ],
                "responsibilities": [
                    "Open strategic Frames with declarative Conversions",
                    "Issue and revoke Delegation Conversions",
                    "Sign AUTHORITATIVE Decision and Enrollment Conversions for thresholds",
                    "Initiate Reconciliation Conversions for major Integrity Exceptions"
                ]
            },
            ConversationRole.CEO: {
                "roles": ["Organizational Steward", "Public Face", "Cross-domain Enrollment Sponsor", "Governance Co-signer"],
                "champion_conversations": [
                    ConversationType.COMPANY_FRAME,
                    ConversationType.EXECUTIVE_COORDINATION,
                    ConversationType.MAJOR_ENROLLMENT,
                    ConversationType.PARTNER_SPONSOR
                ],
                "responsibilities": [
                    "Translate Founder vision into company Frames",
                    "Sign high-level Commitment and Enrollment Conversions",
                    "Steward Relationship Snapshot Conversions with external stakeholders"
                ]
            },
            ConversationRole.CFO: {
                "roles": ["Financial Steward", "Budget Signer", "Contract and Boundary Steward", "Compliance Verifier"],
                "champion_conversations": [
                    ConversationType.BUDGET_COMMITMENT,
                    ConversationType.PAYMENT_OCCURRENCE,
                    ConversationType.CONTRACTING_BOUNDARY
                ],
                "responsibilities": [
                    "Issue financial Delegation Conversions with numeric thresholds",
                    "Require HUMAN_GATE Conversions for spends above thresholds",
                    "Confirm financial Occurrence Conversions and sign reconciliations"
                ]
            },
            ConversationRole.CTO: {
                "roles": ["Technology Steward", "Telemetry Owner", "Data Boundary Steward", "Integration Lead"],
                "champion_conversations": [
                    ConversationType.TECHNICAL_DECISION,
                    ConversationType.TELEMETRY_OCCURRENCE,
                    ConversationType.BOUNDARY_DATA_PRIVACY,
                    ConversationType.INTEGRATION_COORDINATION
                ],
                "responsibilities": [
                    "Authorize Delegation Conversions for Telemetry Voice",
                    "Declare Occurrence Conversions from system events",
                    "Enforce Privacy Flag Conversions and require human gates for sensitive data"
                ]
            },
            ConversationRole.CMO: {
                "roles": ["Market Steward", "Enrollment Script Champion", "Relationship Builder", "Recognition Lead"],
                "champion_conversations": [
                    ConversationType.MARKET_POSSIBILITY,
                    ConversationType.CUSTOMER_ENROLLMENT,
                    ConversationType.RECOGNITION,
                    ConversationType.PARTNER_MARKETING_ENROLLMENT
                ],
                "responsibilities": [
                    "Draft Enrollment Conversions and enrollment micro-stories",
                    "Vet coercion risk flags before autonomous sends",
                    "Update Relationship Snapshot Conversions after campaigns"
                ]
            },
            ConversationRole.COO: {
                "roles": ["Operational Steward", "Commitment Owner", "Occurrence Verifier", "Handoff Coordinator"],
                "champion_conversations": [
                    ConversationType.OPERATIONAL_FRAME,
                    ConversationType.COORDINATION_HANDOFF,
                    ConversationType.COMPLETION
                ],
                "responsibilities": [
                    "Propose and finalize Commitment Conversions for operations",
                    "Verify Occurrence Conversions",
                    "Enforce Observation-first verification before completion"
                ]
            },
            ConversationRole.CHRO: {
                "roles": ["People Steward", "Culture and Recognition Owner", "Conflict and Repair Lead"],
                "champion_conversations": [
                    ConversationType.HIRING_ONBOARDING_FRAME,
                    ConversationType.RECOGNITION_DEVELOPMENT,
                    ConversationType.CONFLICT_RESOLUTION,
                    ConversationType.RECONCILIATION
                ],
                "responsibilities": [
                    "Issue Responsibility and Completion Conversions for people processes",
                    "Run Reconciliation Conversions for interpersonal Integrity Exceptions",
                    "Steward psychological safety snapshots"
                ]
            },
            ConversationRole.INVESTOR: {
                "roles": ["Resource Steward", "Risk Gatekeeper", "Network Enroller", "Governance Reviewer"],
                "champion_conversations": [
                    ConversationType.INVESTMENT_DECISION,
                    ConversationType.RISK_ASSESSMENT,
                    ConversationType.STRATEGIC_PARTNERSHIP,
                    ConversationType.QUARTERLY_GOVERNANCE
                ],
                "responsibilities": [
                    "Declare funding Conversions",
                    "Issue HUMAN_GATE prompts for risk",
                    "Sign tranche and milestone Decision Conversions",
                    "Convene Governance Conversions"
                ]
            }
        }
    
    def _initialize_conversation_champions(self) -> Dict[ConversationType, List[ConversationRole]]:
        """Initialize which roles can champion which conversation types"""
        champions = {}
        for role, info in self.role_responsibilities.items():
            for conv_type in info["champion_conversations"]:
                if conv_type not in champions:
                    champions[conv_type] = []
                champions[conv_type].append(role)
        return champions
    
    async def create_conversation(self, 
                                conversation_type: ConversationType,
                                champion: ConversationRole,
                                title: str,
                                content: str,
                                context: Dict[str, Any] = None,
                                participants: List[ConversationRole] = None,
                                priority: ConversationPriority = ConversationPriority.MEDIUM) -> str:
        """Create a new boardroom conversation"""
        
        # Validate champion can handle this conversation type
        if champion not in self.conversation_champions.get(conversation_type, []):
            self.logger.warning(f"Role {champion.value} is not typically a champion for {conversation_type.value}")
        
        # Get template for this conversation type
        template = self.template_manager.get_template(conversation_type)
        
        # Create conversation
        conversation = Conversation(
            type=conversation_type,
            champion=champion,
            title=title,
            content=content,
            context=context or {},
            priority=priority,
            participants=set(participants or []),
            required_signers=set(template.get("required_signers", [champion]))
        )
        
        # Apply template context
        conversation.context.update(template.get("default_context", {}))
        
        # Set status based on conversation type and context
        if conversation.requires_human_gate or conversation.financial_threshold:
            conversation.status = ConversationStatus.REQUIRES_HUMAN_GATE
        else:
            conversation.status = ConversationStatus.DRAFT
        
        conversation_id = await self.conversation_system.create_conversation(conversation)
        
        self.logger.info(f"Created {conversation_type.value} conversation {conversation_id} "
                        f"championed by {champion.value}")
        
        return conversation_id
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        return await self.conversation_system.get_conversation(conversation_id)
    
    async def sign_conversation(self, conversation_id: str, signer_role: ConversationRole, 
                              signer_name: str) -> bool:
        """Sign a conversation with proper authorization"""
        conversation = await self.conversation_system.get_conversation(conversation_id)
        if not conversation:
            return False
        
        # Check if signer is authorized for this conversation type
        if not self._is_authorized_signer(conversation, signer_role):
            self.logger.error(f"Role {signer_role.value} not authorized to sign conversation {conversation_id}")
            return False
        
        # Check for human gate requirements
        if conversation.requires_human_gate and signer_role not in [ConversationRole.ADMINISTRATOR]:
            self.logger.warning(f"Conversation {conversation_id} requires HUMAN_GATE approval")
            return False
        
        success = await self.conversation_system.sign_conversation(conversation_id, signer_role, signer_name)
        
        if success:
            self.logger.info(f"Conversation {conversation_id} signed by {signer_name}[{signer_role.value}]")
            
            # Check for completion and trigger next steps
            await self._check_conversation_completion(conversation_id)
        
        return success
    
    async def list_conversations_by_agent(self, agent_role: ConversationRole) -> Dict[str, List[Conversation]]:
        """List conversations organized by status for a specific agent"""
        championed = await self.conversation_system.list_conversations_by_champion(agent_role)
        pending_signatures = await self.conversation_system.list_pending_signatures(agent_role)
        
        return {
            "championed": championed,
            "pending_signatures": pending_signatures,
            "flagged": [conv for conv in championed if conv.integrity_flags or conv.coercion_risk_flags],
            "requires_human_gate": [conv for conv in championed if conv.requires_human_gate]
        }
    
    async def create_a2a_communication(self, 
                                     from_agent: ConversationRole,
                                     to_agent: ConversationRole,
                                     conversation_type: ConversationType,
                                     message_content: str,
                                     context: Dict[str, Any] = None) -> str:
        """Create Agent-to-Agent communication"""
        
        # Determine if this is external stakeholder communication
        external_agents = {ConversationRole.CUSTOMER, ConversationRole.PARTNER, 
                          ConversationRole.SUPPLIER, ConversationRole.REGULATOR}
        
        is_external = to_agent in external_agents or from_agent in external_agents
        
        title = f"A2A Communication: {from_agent.value} → {to_agent.value}"
        if is_external:
            title = f"External A2A: {from_agent.value} → {to_agent.value}"
        
        # Create conversation for A2A communication
        conversation_id = await self.create_conversation(
            conversation_type=conversation_type,
            champion=from_agent,
            title=title,
            content=message_content,
            context={
                **(context or {}),
                "communication_type": "A2A",
                "from_agent": from_agent.value,
                "to_agent": to_agent.value,
                "is_external_stakeholder": is_external
            },
            participants=[from_agent, to_agent],
            priority=ConversationPriority.HIGH if is_external else ConversationPriority.MEDIUM
        )
        
        self.logger.info(f"Created A2A communication {conversation_id}: {from_agent.value} → {to_agent.value}")
        return conversation_id
    
    def _is_authorized_signer(self, conversation: Conversation, signer_role: ConversationRole) -> bool:
        """Check if a role is authorized to sign a conversation"""
        # Champion can always sign their own conversations
        if conversation.champion == signer_role:
            return True
        
        # Check if role is in required signers
        if signer_role in conversation.required_signers:
            return True
        
        # Check role-specific authorization based on conversation type
        role_info = self.role_responsibilities.get(signer_role, {})
        champion_conversations = role_info.get("champion_conversations", [])
        
        return conversation.type in champion_conversations
    
    async def _check_conversation_completion(self, conversation_id: str) -> None:
        """Check if conversation is complete and trigger next steps"""
        conversation = await self.conversation_system.get_conversation(conversation_id)
        if not conversation:
            return
        
        # Check if all required signatures are present
        signed_roles = {sig.signer_agent for sig in conversation.signatures}
        if conversation.required_signers.issubset(signed_roles):
            conversation.status = ConversationStatus.COMPLETED
            await self.conversation_system.update_conversation(conversation)
            
            self.logger.info(f"Conversation {conversation_id} completed with all required signatures")
            
            # Trigger any follow-up actions based on conversation type
            await self._trigger_conversation_followup(conversation)
    
    async def _trigger_conversation_followup(self, conversation: Conversation) -> None:
        """Trigger follow-up actions after conversation completion"""
        # Implementation depends on conversation type
        if conversation.type == ConversationType.INVESTMENT_DECISION:
            self.logger.info(f"Investment decision {conversation.id} completed - triggering funding workflow")
        elif conversation.type == ConversationType.BUDGET_COMMITMENT:
            self.logger.info(f"Budget commitment {conversation.id} completed - updating financial systems")
        elif conversation.type == ConversationType.TECHNICAL_DECISION:
            self.logger.info(f"Technical decision {conversation.id} completed - triggering implementation")
        
        # Add more specific follow-up logic as needed


class StorageBackedConversationSystem(ConversationSystem):
    """Storage-backed implementation using UnifiedStorageManager"""
    
    def __init__(self, storage_manager):
        self.storage_manager = storage_manager
        self.logger = logging.getLogger(__name__)
        self.container_name = "conversations"
    
    async def create_conversation(self, conversation: Conversation) -> str:
        """Create a new conversation in storage"""
        try:
            # Store conversation data
            conversation_data = conversation.to_dict()
            
            # Use storage manager to persist conversation
            # This is a simplified implementation - actual storage would depend on UnifiedStorageManager API
            self.logger.info(f"Created conversation {conversation.id} in storage")
            return conversation.id
        except Exception as e:
            self.logger.error(f"Failed to create conversation in storage: {e}")
            raise
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve conversation from storage"""
        try:
            # Retrieve from storage - simplified implementation
            self.logger.info(f"Retrieved conversation {conversation_id} from storage")
            # Return None for now - actual implementation would deserialize from storage
            return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve conversation {conversation_id}: {e}")
            return None
    
    async def update_conversation(self, conversation: Conversation) -> None:
        """Update conversation in storage"""
        try:
            conversation_data = conversation.to_dict()
            self.logger.info(f"Updated conversation {conversation.id} in storage")
        except Exception as e:
            self.logger.error(f"Failed to update conversation {conversation.id}: {e}")
            raise
    
    async def list_conversations_by_champion(self, champion: ConversationRole) -> List[Conversation]:
        """List conversations by champion from storage"""
        try:
            # Query storage - simplified implementation
            self.logger.info(f"Listed conversations for champion {champion.value}")
            return []
        except Exception as e:
            self.logger.error(f"Failed to list conversations for champion {champion.value}: {e}")
            return []
    
    async def list_pending_signatures(self, signer: ConversationRole) -> List[Conversation]:
        """List pending signatures from storage"""
        try:
            # Query storage - simplified implementation  
            self.logger.info(f"Listed pending signatures for {signer.value}")
            return []
        except Exception as e:
            self.logger.error(f"Failed to list pending signatures for {signer.value}: {e}")
            return []
    
    async def sign_conversation(self, conversation_id: str, signer_role: ConversationRole, 
                              signer_name: str) -> bool:
        """Sign conversation in storage"""
        try:
            # Update conversation with signature in storage
            self.logger.info(f"Signed conversation {conversation_id} by {signer_name}[{signer_role.value}]")
            return True
        except Exception as e:
            self.logger.error(f"Failed to sign conversation {conversation_id}: {e}")
            return False


# Global conversation manager instance
_conversation_manager: Optional[BoardroomConversationManager] = None


def get_conversation_manager(storage_manager=None) -> BoardroomConversationManager:
    """Get or create the global conversation manager"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = BoardroomConversationManager(storage_manager)
    return _conversation_manager


# Convenience functions
async def create_conversation(conversation_type: ConversationType,
                            champion: ConversationRole,
                            title: str,
                            content: str,
                            **kwargs) -> str:
    """Create a new conversation"""
    manager = get_conversation_manager()
    return await manager.create_conversation(conversation_type, champion, title, content, **kwargs)


async def get_conversation(conversation_id: str) -> Optional[Conversation]:
    """Get a conversation by ID"""
    manager = get_conversation_manager()
    return await manager.get_conversation(conversation_id)


async def list_conversations_by_agent(agent_role: ConversationRole) -> Dict[str, List[Conversation]]:
    """List conversations for an agent"""
    manager = get_conversation_manager()
    return await manager.list_conversations_by_agent(agent_role)


async def sign_conversation(conversation_id: str, signer_role: ConversationRole, signer_name: str) -> bool:
    """Sign a conversation"""
    manager = get_conversation_manager()
    return await manager.sign_conversation(conversation_id, signer_role, signer_name)