"""
Covenant Ledger for Inter-Boardroom Agreements

Implements a ledger system for recording, tracking, and validating
inter-boardroom agreements, contracts, and covenants as part of
the Global Network of Autonomous Boardrooms.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import hashlib
import json

class AgreementType(Enum):
    """Types of inter-boardroom agreements"""
    PARTNERSHIP = "partnership"
    SUPPLY_CHAIN = "supply_chain"  
    JOINT_VENTURE = "joint_venture"
    SERVICE_CONTRACT = "service_contract"
    LICENSING = "licensing"
    COALITION = "coalition"
    FEDERATION = "federation"
    TREATY = "treaty"
    STANDARDS = "standards"
    ARBITRATION = "arbitration"

class AgreementStatus(Enum):
    """Status of an agreement"""
    DRAFT = "draft"
    PROPOSED = "proposed"
    NEGOTIATING = "negotiating"
    SIGNED = "signed"
    ACTIVE = "active"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    DISPUTED = "disputed"

@dataclass
class AgreementSignature:
    """Signature on an inter-boardroom agreement"""
    signer_node_id: str
    signer_enterprise: str
    signer_agent: str  # Which agent signed (e.g., CEO, CFO)
    signature_hash: str
    signed_at: datetime = field(default_factory=datetime.now)
    signature_method: str = "digital"  # digital, blockchain, etc.

@dataclass
class InterBoardroomAgreement:
    """Represents an agreement between boardrooms"""
    agreement_id: str
    agreement_type: AgreementType
    title: str
    description: str
    
    # Parties involved
    participating_nodes: Set[str] = field(default_factory=set)
    initiator_node_id: str = ""
    
    # Agreement content
    terms: Dict[str, Any] = field(default_factory=dict)
    conditions: List[str] = field(default_factory=list)
    deliverables: List[Dict[str, Any]] = field(default_factory=list)
    
    # Status and lifecycle
    status: AgreementStatus = AgreementStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    
    # Signatures
    signatures: List[AgreementSignature] = field(default_factory=list)
    required_signers: Set[str] = field(default_factory=set)
    
    # Validation and integrity
    schema_version: str = "1.0"
    content_hash: str = ""
    
    # Associated data
    conversation_id: Optional[str] = None
    negotiation_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = self._calculate_content_hash()
    
    def _calculate_content_hash(self) -> str:
        """Calculate hash of agreement content for integrity checking"""
        content_data = {
            "agreement_type": self.agreement_type.value,
            "title": self.title,
            "description": self.description,
            "terms": self.terms,
            "conditions": self.conditions,
            "deliverables": self.deliverables
        }
        content_str = json.dumps(content_data, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def is_fully_signed(self) -> bool:
        """Check if all required signers have signed"""
        signed_nodes = {sig.signer_node_id for sig in self.signatures}
        return self.required_signers.issubset(signed_nodes)
    
    def is_valid(self) -> bool:
        """Validate agreement integrity"""
        # Check content hash
        current_hash = self._calculate_content_hash()
        if current_hash != self.content_hash:
            return False
        
        # Check if all participants are in required signers
        if not self.participating_nodes.issubset(self.required_signers):
            return False
        
        return True

class CovenantLedger:
    """
    Covenant Ledger for Inter-Boardroom Agreements
    
    Maintains an immutable ledger of all agreements, contracts,
    and covenants between boardrooms in the network.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agreements: Dict[str, InterBoardroomAgreement] = {}
        self.ledger_entries: List[Dict[str, Any]] = []
        
        # Indices for efficient querying
        self.node_agreements: Dict[str, Set[str]] = {}  # node_id -> agreement_ids
        self.type_agreements: Dict[AgreementType, Set[str]] = {}  # type -> agreement_ids
        self.status_agreements: Dict[AgreementStatus, Set[str]] = {}  # status -> agreement_ids
        
        self.ledger_created: datetime = datetime.now()
    
    async def create_agreement(self, agreement_type: AgreementType, title: str,
                             description: str, initiator_node_id: str,
                             participating_nodes: Set[str], terms: Dict[str, Any],
                             conversation_id: str = None) -> str:
        """Create a new inter-boardroom agreement"""
        agreement_id = str(uuid.uuid4())
        
        agreement = InterBoardroomAgreement(
            agreement_id=agreement_id,
            agreement_type=agreement_type,
            title=title,
            description=description,
            initiator_node_id=initiator_node_id,
            participating_nodes=participating_nodes,
            required_signers=participating_nodes.copy(),  # All participants must sign
            terms=terms,
            conversation_id=conversation_id
        )
        
        # Store agreement
        self.agreements[agreement_id] = agreement
        self._update_indices(agreement)
        
        # Record ledger entry
        await self._record_ledger_entry("agreement_created", {
            "agreement_id": agreement_id,
            "type": agreement_type.value,
            "initiator": initiator_node_id,
            "participants": list(participating_nodes),
            "title": title
        })
        
        self.logger.info(f"Created agreement {agreement_id}: {title}")
        return agreement_id
    
    async def propose_agreement(self, agreement_id: str) -> bool:
        """Propose an agreement to all participants"""
        if agreement_id not in self.agreements:
            return False
        
        agreement = self.agreements[agreement_id]
        if agreement.status != AgreementStatus.DRAFT:
            self.logger.warning(f"Cannot propose agreement {agreement_id}: status is {agreement.status.value}")
            return False
        
        agreement.status = AgreementStatus.PROPOSED
        
        await self._record_ledger_entry("agreement_proposed", {
            "agreement_id": agreement_id,
            "proposed_by": agreement.initiator_node_id,
            "participants": list(agreement.participating_nodes)
        })
        
        self.logger.info(f"Proposed agreement {agreement_id}")
        return True
    
    async def sign_agreement(self, agreement_id: str, signer_node_id: str,
                           signer_enterprise: str, signer_agent: str,
                           signature_hash: str = None) -> bool:
        """Sign an agreement"""
        if agreement_id not in self.agreements:
            self.logger.error(f"Agreement {agreement_id} not found")
            return False
        
        agreement = self.agreements[agreement_id]
        
        # Verify signer is authorized
        if signer_node_id not in agreement.required_signers:
            self.logger.error(f"Node {signer_node_id} not authorized to sign agreement {agreement_id}")
            return False
        
        # Check if already signed by this node
        existing_signer = next((sig for sig in agreement.signatures 
                              if sig.signer_node_id == signer_node_id), None)
        if existing_signer:
            self.logger.warning(f"Node {signer_node_id} already signed agreement {agreement_id}")
            return True
        
        # Generate signature if not provided
        if not signature_hash:
            signature_hash = self._generate_signature_hash(agreement_id, signer_node_id)
        
        # Create signature
        signature = AgreementSignature(
            signer_node_id=signer_node_id,
            signer_enterprise=signer_enterprise,
            signer_agent=signer_agent,
            signature_hash=signature_hash
        )
        
        agreement.signatures.append(signature)
        
        # Check if agreement is now fully signed
        if agreement.is_fully_signed():
            agreement.status = AgreementStatus.SIGNED
            agreement.effective_date = datetime.now()
            
            await self._record_ledger_entry("agreement_fully_signed", {
                "agreement_id": agreement_id,
                "effective_date": agreement.effective_date.isoformat()
            })
        
        await self._record_ledger_entry("agreement_signed", {
            "agreement_id": agreement_id,
            "signer_node": signer_node_id,
            "signer_enterprise": signer_enterprise,
            "signer_agent": signer_agent
        })
        
        self.logger.info(f"Agreement {agreement_id} signed by {signer_enterprise}")
        return True
    
    async def activate_agreement(self, agreement_id: str) -> bool:
        """Activate a signed agreement"""
        if agreement_id not in self.agreements:
            return False
        
        agreement = self.agreements[agreement_id]
        
        if agreement.status != AgreementStatus.SIGNED:
            self.logger.warning(f"Cannot activate agreement {agreement_id}: status is {agreement.status.value}")
            return False
        
        if not agreement.is_fully_signed():
            self.logger.warning(f"Cannot activate agreement {agreement_id}: not fully signed")
            return False
        
        agreement.status = AgreementStatus.ACTIVE
        
        await self._record_ledger_entry("agreement_activated", {
            "agreement_id": agreement_id,
            "activated_at": datetime.now().isoformat()
        })
        
        self.logger.info(f"Activated agreement {agreement_id}")
        return True
    
    async def terminate_agreement(self, agreement_id: str, terminator_node_id: str,
                                reason: str) -> bool:
        """Terminate an active agreement"""
        if agreement_id not in self.agreements:
            return False
        
        agreement = self.agreements[agreement_id]
        
        # Verify terminator is a participant
        if terminator_node_id not in agreement.participating_nodes:
            self.logger.error(f"Node {terminator_node_id} not authorized to terminate agreement {agreement_id}")
            return False
        
        agreement.status = AgreementStatus.TERMINATED
        
        await self._record_ledger_entry("agreement_terminated", {
            "agreement_id": agreement_id,
            "terminated_by": terminator_node_id,
            "reason": reason,
            "terminated_at": datetime.now().isoformat()
        })
        
        self.logger.info(f"Terminated agreement {agreement_id} by {terminator_node_id}")
        return True
    
    def get_agreement(self, agreement_id: str) -> Optional[InterBoardroomAgreement]:
        """Get an agreement by ID"""
        return self.agreements.get(agreement_id)
    
    def get_agreements_by_node(self, node_id: str) -> List[InterBoardroomAgreement]:
        """Get all agreements involving a specific node"""
        agreement_ids = self.node_agreements.get(node_id, set())
        return [self.agreements[aid] for aid in agreement_ids]
    
    def get_agreements_by_type(self, agreement_type: AgreementType) -> List[InterBoardroomAgreement]:
        """Get all agreements of a specific type"""
        agreement_ids = self.type_agreements.get(agreement_type, set())
        return [self.agreements[aid] for aid in agreement_ids]
    
    def get_agreements_by_status(self, status: AgreementStatus) -> List[InterBoardroomAgreement]:
        """Get all agreements with a specific status"""
        agreement_ids = self.status_agreements.get(status, set())
        return [self.agreements[aid] for aid in agreement_ids]
    
    def get_active_agreements_for_node(self, node_id: str) -> List[InterBoardroomAgreement]:
        """Get all active agreements for a node"""
        node_agreements = self.get_agreements_by_node(node_id)
        return [agreement for agreement in node_agreements 
                if agreement.status == AgreementStatus.ACTIVE]
    
    def validate_agreement(self, agreement_id: str) -> Dict[str, Any]:
        """Validate an agreement's integrity and status"""
        if agreement_id not in self.agreements:
            return {"valid": False, "error": "Agreement not found"}
        
        agreement = self.agreements[agreement_id]
        
        validation_result = {
            "valid": True,
            "agreement_id": agreement_id,
            "content_hash_valid": agreement.is_valid(),
            "fully_signed": agreement.is_fully_signed(),
            "status": agreement.status.value,
            "validation_timestamp": datetime.now().isoformat()
        }
        
        if not agreement.is_valid():
            validation_result["valid"] = False
            validation_result["error"] = "Content hash validation failed"
        
        return validation_result
    
    def get_ledger_stats(self) -> Dict[str, Any]:
        """Get covenant ledger statistics"""
        total_agreements = len(self.agreements)
        status_counts = {}
        type_counts = {}
        
        for agreement in self.agreements.values():
            status = agreement.status.value
            agreement_type = agreement.agreement_type.value
            
            status_counts[status] = status_counts.get(status, 0) + 1
            type_counts[agreement_type] = type_counts.get(agreement_type, 0) + 1
        
        return {
            "total_agreements": total_agreements,
            "status_distribution": status_counts,
            "type_distribution": type_counts,
            "total_ledger_entries": len(self.ledger_entries),
            "ledger_created": self.ledger_created.isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _update_indices(self, agreement: InterBoardroomAgreement):
        """Update search indices for an agreement"""
        agreement_id = agreement.agreement_id
        
        # Update node index
        for node_id in agreement.participating_nodes:
            if node_id not in self.node_agreements:
                self.node_agreements[node_id] = set()
            self.node_agreements[node_id].add(agreement_id)
        
        # Update type index
        if agreement.agreement_type not in self.type_agreements:
            self.type_agreements[agreement.agreement_type] = set()
        self.type_agreements[agreement.agreement_type].add(agreement_id)
        
        # Update status index
        if agreement.status not in self.status_agreements:
            self.status_agreements[agreement.status] = set()
        self.status_agreements[agreement.status].add(agreement_id)
    
    async def _record_ledger_entry(self, event_type: str, event_data: Dict[str, Any]):
        """Record an entry in the ledger"""
        entry = {
            "entry_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "event_data": event_data
        }
        
        self.ledger_entries.append(entry)
        self.logger.info(f"Recorded ledger entry: {event_type}")
    
    def _generate_signature_hash(self, agreement_id: str, signer_node_id: str) -> str:
        """Generate a signature hash for an agreement"""
        signature_data = f"{agreement_id}:{signer_node_id}:{datetime.now().isoformat()}"
        return hashlib.sha256(signature_data.encode()).hexdigest()

# Factory function
def create_covenant_ledger() -> CovenantLedger:
    """Create a new covenant ledger"""
    return CovenantLedger()