"""
Core Conversation System for Business Infinity

Implements the conversation types, roles, and core data structures
as defined in conversations/specification.md
"""

import uuid
import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


class ConversationType(Enum):
    """Types of conversations as defined in specification.md"""
    # Strategy and Frames
    STRATEGIC_FRAME = "strategic_frame"
    HIGH_RISK_DECISION = "high_risk_decision"
    ENROLLMENT_SPONSOR = "enrollment_sponsor" 
    GOVERNANCE_REVIEW = "governance_review"
    COMPANY_FRAME = "company_frame"
    EXECUTIVE_COORDINATION = "executive_coordination"
    MAJOR_ENROLLMENT = "major_enrollment"
    PARTNER_SPONSOR = "partner_sponsor"
    
    # Investment and Funding
    INVESTMENT_DECISION = "investment_decision"
    RISK_ASSESSMENT = "risk_assessment"
    STRATEGIC_PARTNERSHIP = "strategic_partnership"
    QUARTERLY_GOVERNANCE = "quarterly_governance"
    
    # Operations
    OPERATIONAL_FRAME = "operational_frame"
    COORDINATION_HANDOFF = "coordination_handoff"
    COMPLETION = "completion"
    COMMITMENT = "commitment"
    OCCURRENCE_VERIFICATION = "occurrence_verification"
    
    # Financial
    BUDGET_COMMITMENT = "budget_commitment"
    PAYMENT_OCCURRENCE = "payment_occurrence"
    CONTRACTING_BOUNDARY = "contracting_boundary"
    
    # Technology
    TECHNICAL_DECISION = "technical_decision"
    TELEMETRY_OCCURRENCE = "telemetry_occurrence"
    BOUNDARY_DATA_PRIVACY = "boundary_data_privacy"
    INTEGRATION_COORDINATION = "integration_coordination"
    
    # Marketing
    MARKET_POSSIBILITY = "market_possibility"
    CUSTOMER_ENROLLMENT = "customer_enrollment"
    RECOGNITION = "recognition"
    PARTNER_MARKETING_ENROLLMENT = "partner_marketing_enrollment"
    
    # People & Culture
    HIRING_ONBOARDING_FRAME = "hiring_onboarding_frame"
    RECOGNITION_DEVELOPMENT = "recognition_development"
    CONFLICT_RESOLUTION = "conflict_resolution"
    RECONCILIATION = "reconciliation"
    
    # External Stakeholder
    CUSTOMER_ENROLLMENT_EXT = "customer_enrollment_ext"
    CUSTOMER_FEEDBACK = "customer_feedback"
    PARTNER_ENROLLMENT_EXT = "partner_enrollment_ext"
    PARTNER_SLA = "partner_sla"
    SUPPLIER_PROCUREMENT = "supplier_procurement"
    SUPPLIER_DELIVERY = "supplier_delivery"
    REGULATOR_BOUNDARY = "regulator_boundary"
    REGULATOR_AUDIT = "regulator_audit"


class ConversationRole(Enum):
    """Agent roles as defined in specification.md"""
    FOUNDER = "Founder"
    INVESTOR = "Investor" 
    CEO = "CEO"
    COO = "COO"
    CFO = "CFO"
    CTO = "CTO"
    CMO = "CMO"
    CHRO = "CHRO"
    ADMINISTRATOR = "Administrator"
    MENTOR = "Mentor"
    
    # External stakeholders
    CUSTOMER = "Customer"
    PARTNER = "Partner"
    SUPPLIER = "Supplier"
    REGULATOR = "Regulator"
    INVESTOR_NETWORK = "InvestorNetwork"


class ConversationStatus(Enum):
    """Status of conversations"""
    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    SIGNED = "signed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FLAGGED = "flagged"
    REQUIRES_HUMAN_GATE = "requires_human_gate"


class ConversationPriority(Enum):
    """Priority levels for conversations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ConversationSignature:
    """Represents a signature on a conversation"""
    signer_agent: ConversationRole
    signer_name: str
    timestamp: datetime
    signature_type: str = "AUTHORITATIVE"  # AUTHORITATIVE, DELEGATION, HUMAN_GATE
    
    def to_string(self) -> str:
        """Format signature as specified: 'Signed by [Agent][Role] at [ISO ts] Conversion'"""
        return f"Signed by {self.signer_name}[{self.signer_agent.value}] at {self.timestamp.isoformat()} Conversion"


@dataclass
class Conversation:
    """Core conversation data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: ConversationType = ConversationType.STRATEGIC_FRAME
    champion: ConversationRole = ConversationRole.CEO
    title: str = ""
    content: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    status: ConversationStatus = ConversationStatus.DRAFT
    priority: ConversationPriority = ConversationPriority.MEDIUM
    
    # Participants and signatures
    participants: Set[ConversationRole] = field(default_factory=set)
    required_signers: Set[ConversationRole] = field(default_factory=set)
    signatures: List[ConversationSignature] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Flags and gates
    integrity_flags: List[str] = field(default_factory=list)
    coercion_risk_flags: List[str] = field(default_factory=list)
    privacy_flags: List[str] = field(default_factory=list)
    requires_human_gate: bool = False
    
    # Delegation and thresholds
    delegation_scope: Optional[str] = None
    financial_threshold: Optional[float] = None
    
    def add_signature(self, signer_role: ConversationRole, signer_name: str, 
                     signature_type: str = "AUTHORITATIVE") -> None:
        """Add a signature to the conversation"""
        signature = ConversationSignature(
            signer_agent=signer_role,
            signer_name=signer_name,
            timestamp=datetime.now(timezone.utc),
            signature_type=signature_type
        )
        self.signatures.append(signature)
        self.updated_at = datetime.now(timezone.utc)
        
        # Update status if all required signers have signed
        signed_roles = {sig.signer_agent for sig in self.signatures}
        if self.required_signers.issubset(signed_roles):
            if self.status == ConversationStatus.PENDING_SIGNATURE:
                self.status = ConversationStatus.SIGNED
    
    def is_signed_by(self, role: ConversationRole) -> bool:
        """Check if conversation is signed by a specific role"""
        return any(sig.signer_agent == role for sig in self.signatures)
    
    def get_signature_string(self) -> str:
        """Get formatted signature strings"""
        return "\n".join([sig.to_string() for sig in self.signatures])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary"""
        return {
            "id": self.id,
            "type": self.type.value,
            "champion": self.champion.value,
            "title": self.title,
            "content": self.content,
            "context": self.context,
            "status": self.status.value,
            "priority": self.priority.value,
            "participants": [p.value for p in self.participants],
            "required_signers": [r.value for r in self.required_signers],
            "signatures": [
                {
                    "signer_agent": sig.signer_agent.value,
                    "signer_name": sig.signer_name,
                    "timestamp": sig.timestamp.isoformat(),
                    "signature_type": sig.signature_type
                }
                for sig in self.signatures
            ],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "integrity_flags": self.integrity_flags,
            "coercion_risk_flags": self.coercion_risk_flags,
            "privacy_flags": self.privacy_flags,
            "requires_human_gate": self.requires_human_gate,
            "delegation_scope": self.delegation_scope,
            "financial_threshold": self.financial_threshold
        }


class ConversationTemplateManager:
    """Manages conversation templates for different types and roles"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[ConversationType, Dict[str, Any]]:
        """Initialize conversation templates based on specification.md"""
        templates = {}
        
        # Strategic Frame conversations
        templates[ConversationType.STRATEGIC_FRAME] = {
            "title_template": "Strategic Frame: {topic}",
            "champion_roles": [ConversationRole.FOUNDER, ConversationRole.CEO],
            "required_signers": [ConversationRole.FOUNDER],
            "default_context": {"frame_type": "strategic", "scope": "company_wide"}
        }
        
        templates[ConversationType.INVESTMENT_DECISION] = {
            "title_template": "Investment Decision: {amount} for {purpose}",
            "champion_roles": [ConversationRole.INVESTOR, ConversationRole.CFO],
            "required_signers": [ConversationRole.INVESTOR, ConversationRole.CFO],
            "default_context": {"decision_type": "investment", "requires_due_diligence": True}
        }
        
        templates[ConversationType.BUDGET_COMMITMENT] = {
            "title_template": "Budget Commitment: {budget_item}",
            "champion_roles": [ConversationRole.CFO],
            "required_signers": [ConversationRole.CFO],
            "default_context": {"financial_category": "budget", "approval_required": True}
        }
        
        templates[ConversationType.TECHNICAL_DECISION] = {
            "title_template": "Technical Decision: {technology} implementation",
            "champion_roles": [ConversationRole.CTO],
            "required_signers": [ConversationRole.CTO],
            "default_context": {"technical_category": "architecture", "impact_assessment_required": True}
        }
        
        # Add more templates as needed
        return templates
    
    def get_template(self, conversation_type: ConversationType) -> Dict[str, Any]:
        """Get template for a conversation type"""
        return self.templates.get(conversation_type, {
            "title_template": "{topic}",
            "champion_roles": [ConversationRole.CEO],
            "required_signers": [ConversationRole.CEO],
            "default_context": {}
        })


class ConversationSystem(ABC):
    """Abstract base class for conversation system implementations"""
    
    @abstractmethod
    async def create_conversation(self, conversation: Conversation) -> str:
        """Create a new conversation"""
        pass
    
    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by ID"""
        pass
    
    @abstractmethod 
    async def update_conversation(self, conversation: Conversation) -> None:
        """Update an existing conversation"""
        pass
    
    @abstractmethod
    async def list_conversations_by_champion(self, champion: ConversationRole) -> List[Conversation]:
        """List conversations championed by a specific role"""
        pass
    
    @abstractmethod
    async def list_pending_signatures(self, signer: ConversationRole) -> List[Conversation]:
        """List conversations pending signature from a specific role"""
        pass
    
    @abstractmethod
    async def sign_conversation(self, conversation_id: str, signer_role: ConversationRole, 
                              signer_name: str) -> bool:
        """Sign a conversation"""
        pass


class InMemoryConversationSystem(ConversationSystem):
    """In-memory implementation for development and testing"""
    
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.template_manager = ConversationTemplateManager()
        self.logger = logging.getLogger(__name__)
    
    async def create_conversation(self, conversation: Conversation) -> str:
        """Create a new conversation"""
        conversation.id = str(uuid.uuid4())
        conversation.created_at = datetime.now(timezone.utc)
        conversation.updated_at = datetime.now(timezone.utc)
        
        self.conversations[conversation.id] = conversation
        self.logger.info(f"Created conversation {conversation.id} of type {conversation.type.value}")
        return conversation.id
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by ID"""
        return self.conversations.get(conversation_id)
    
    async def update_conversation(self, conversation: Conversation) -> None:
        """Update an existing conversation"""
        conversation.updated_at = datetime.now(timezone.utc)
        self.conversations[conversation.id] = conversation
        self.logger.info(f"Updated conversation {conversation.id}")
    
    async def list_conversations_by_champion(self, champion: ConversationRole) -> List[Conversation]:
        """List conversations championed by a specific role"""
        return [conv for conv in self.conversations.values() if conv.champion == champion]
    
    async def list_pending_signatures(self, signer: ConversationRole) -> List[Conversation]:
        """List conversations pending signature from a specific role"""
        pending = []
        for conv in self.conversations.values():
            if (signer in conv.required_signers and 
                not conv.is_signed_by(signer) and
                conv.status in [ConversationStatus.DRAFT, ConversationStatus.PENDING_SIGNATURE]):
                pending.append(conv)
        return pending
    
    async def sign_conversation(self, conversation_id: str, signer_role: ConversationRole, 
                              signer_name: str) -> bool:
        """Sign a conversation"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return False
        
        if signer_role not in conversation.required_signers:
            self.logger.warning(f"Role {signer_role.value} not required to sign conversation {conversation_id}")
            return False
        
        if conversation.is_signed_by(signer_role):
            self.logger.warning(f"Conversation {conversation_id} already signed by {signer_role.value}")
            return False
        
        conversation.add_signature(signer_role, signer_name)
        self.logger.info(f"Conversation {conversation_id} signed by {signer_name}[{signer_role.value}]")
        return True