"""
Covenant Management System for Business Infinity

Implements covenant-based compliance management as specified in the
Business Infinity Compliance Standard. Handles covenant creation,
validation, publication, peer recognition, and amendment processes.
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import jsonschema
from pathlib import Path

# Import existing network components
from .verification import LinkedInVerificationService, VerificationStatus
from .covenant_ledger import CovenantLedger, AgreementType, AgreementStatus

class CovenantStatus(Enum):
    """Status of a covenant in the network"""
    DRAFT = "draft"
    PENDING = "pending"
    RECOGNIZED = "recognized"
    SUSPENDED = "suspended"
    REVOKED = "revoked"

class ComplianceBadgeLevel(Enum):
    """Business Infinity Compliant (BIC) badge levels"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

@dataclass
class CovenantValidationResult:
    """Result of covenant validation"""
    is_valid: bool
    score: float
    issues: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validation_timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PeerRecognition:
    """Peer recognition record"""
    recognizer_id: str
    recognizer_enterprise: str
    recognition_type: str
    recognized_at: datetime
    signature: str
    notes: Optional[str] = None

@dataclass
class CovenantAmendment:
    """Covenant amendment proposal"""
    amendment_id: str
    proposer_agent: str
    proposed_changes: Dict[str, Any]
    rationale: str
    proposed_at: datetime
    voting_deadline: datetime
    votes: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "pending"  # pending, approved, rejected

class CovenantManager:
    """
    Covenant Management System
    
    Manages the lifecycle of enterprise covenants including creation,
    validation, publication, peer recognition, and amendments.
    """
    
    def __init__(self, schema_path: str = None, verification_service: LinkedInVerificationService = None):
        self.logger = logging.getLogger(__name__)
        
        # Load covenant schema
        if schema_path is None:
            schema_path = Path(__file__).parent.parent / "schema" / "covenant.schema.json"
        
        self.schema = self._load_schema(schema_path)
        self.verification_service = verification_service or LinkedInVerificationService()
        self.covenant_ledger = CovenantLedger()
        
        # Storage for covenants and related data
        self.covenants: Dict[str, Dict[str, Any]] = {}
        self.covenant_status: Dict[str, CovenantStatus] = {}
        self.peer_recognitions: Dict[str, List[PeerRecognition]] = {}
        self.pending_amendments: Dict[str, List[CovenantAmendment]] = {}
        
        # Compliance tracking
        self.compliance_badges: Dict[str, Dict[str, Any]] = {}
        self.validation_history: Dict[str, List[CovenantValidationResult]] = {}
        
        self.logger.info("Covenant Manager initialized")
    
    async def create_covenant(self, enterprise_data: Dict[str, Any], 
                            governance_preferences: Dict[str, Any] = None) -> str:
        """Create a new covenant for an enterprise"""
        covenant_id = str(uuid.uuid4())
        
        self.logger.info(f"Creating covenant for {enterprise_data.get('company_name', 'Unknown')}")
        
        try:
            # Verify enterprise identity first
            linkedin_url = enterprise_data.get("linkedin_url")
            if not linkedin_url:
                raise ValueError("LinkedIn URL required for covenant creation")
            
            enterprise_identity = await self.verification_service.verify_enterprise(
                linkedin_url, enterprise_data
            )
            
            if enterprise_identity.verification_status != VerificationStatus.VERIFIED:
                raise ValueError(f"Enterprise verification failed: {enterprise_identity.verification_status}")
            
            # Create initial covenant structure
            covenant = self._create_initial_covenant_structure(
                covenant_id, enterprise_identity, enterprise_data, governance_preferences
            )
            
            # Store covenant
            self.covenants[covenant_id] = covenant
            self.covenant_status[covenant_id] = CovenantStatus.DRAFT
            self.peer_recognitions[covenant_id] = []
            self.pending_amendments[covenant_id] = []
            
            # Initial validation
            validation_result = await self.validate_covenant(covenant_id)
            self.validation_history[covenant_id] = [validation_result]
            
            self.logger.info(f"Covenant created: {covenant_id}")
            return covenant_id
            
        except Exception as e:
            self.logger.error(f"Failed to create covenant: {e}")
            raise
    
    async def validate_covenant(self, covenant_id: str) -> CovenantValidationResult:
        """Validate a covenant against the schema and business rules"""
        if covenant_id not in self.covenants:
            raise ValueError(f"Covenant {covenant_id} not found")
        
        covenant = self.covenants[covenant_id]
        
        try:
            # Schema validation
            jsonschema.validate(covenant, self.schema)
            schema_valid = True
            schema_errors = []
        except jsonschema.ValidationError as e:
            schema_valid = False
            schema_errors = [{"field": ".".join(str(p) for p in e.path), "message": e.message}]
        except Exception as e:
            schema_valid = False
            schema_errors = [{"field": "root", "message": str(e)}]
        
        # Business rule validation
        business_validation = await self._validate_business_rules(covenant)
        
        # Calculate compliance score
        score = self._calculate_compliance_score(covenant, schema_valid, business_validation)
        
        # Compile issues and warnings
        issues = schema_errors + business_validation.get("errors", [])
        warnings = business_validation.get("warnings", [])
        
        validation_result = CovenantValidationResult(
            is_valid=schema_valid and len(business_validation.get("errors", [])) == 0,
            score=score,
            issues=issues,
            warnings=warnings
        )
        
        # Update validation history
        if covenant_id not in self.validation_history:
            self.validation_history[covenant_id] = []
        self.validation_history[covenant_id].append(validation_result)
        
        # Update compliance metadata in covenant
        covenant["compliance_metadata"] = {
            "schema_compliance_version": self.schema.get("$id", "1.0.0"),
            "last_validated": validation_result.validation_timestamp.isoformat(),
            "validation_score": validation_result.score,
            "compliance_issues": validation_result.issues
        }
        
        self.logger.info(f"Covenant validation completed: {covenant_id} - Score: {score:.2f}")
        return validation_result
    
    async def publish_covenant(self, covenant_id: str) -> bool:
        """Publish a covenant to the network for peer validation"""
        if covenant_id not in self.covenants:
            return False
        
        if self.covenant_status[covenant_id] != CovenantStatus.DRAFT:
            self.logger.warning(f"Cannot publish covenant {covenant_id}: status is {self.covenant_status[covenant_id].value}")
            return False
        
        # Final validation before publication
        validation_result = await self.validate_covenant(covenant_id)
        if not validation_result.is_valid:
            self.logger.error(f"Cannot publish invalid covenant {covenant_id}")
            return False
        
        # Update status
        self.covenant_status[covenant_id] = CovenantStatus.PENDING
        
        # Add to provenance
        covenant = self.covenants[covenant_id]
        if "provenance" not in covenant:
            covenant["provenance"] = {"covenant_history": [], "validation_records": []}
        
        # Record publication in covenant history
        covenant["provenance"]["covenant_history"].append({
            "version": covenant.get("covenant_version", "1.0.0"),
            "created_at": datetime.now().isoformat(),
            "changes": ["Initial publication"],
            "approved_by": ["system"],
            "content_hash": self._calculate_content_hash(covenant)
        })
        
        # Update recognition status
        covenant["provenance"]["recognition_status"] = {
            "status": "pending",
            "recognition_count": 0,
            "bic_badge": {"awarded": False}
        }
        
        self.logger.info(f"Covenant published: {covenant_id}")
        return True
    
    async def recognize_covenant(self, covenant_id: str, recognizer_id: str, 
                               recognizer_enterprise: str, recognition_type: str = "initial_validation",
                               notes: str = None) -> bool:
        """Add peer recognition to a covenant"""
        if covenant_id not in self.covenants:
            return False
        
        # Create recognition record
        recognition = PeerRecognition(
            recognizer_id=recognizer_id,
            recognizer_enterprise=recognizer_enterprise,
            recognition_type=recognition_type,
            recognized_at=datetime.now(),
            signature=self._generate_recognition_signature(covenant_id, recognizer_id),
            notes=notes
        )
        
        self.peer_recognitions[covenant_id].append(recognition)
        
        # Update covenant validation records
        covenant = self.covenants[covenant_id]
        covenant["provenance"]["validation_records"].append({
            "validator_id": recognizer_id,
            "validator_enterprise": recognizer_enterprise,
            "validation_type": recognition_type,
            "validated_at": recognition.recognized_at.isoformat(),
            "validation_signature": recognition.signature,
            "validation_notes": notes
        })
        
        # Update recognition count
        recognition_count = len(self.peer_recognitions[covenant_id])
        covenant["provenance"]["recognition_status"]["recognition_count"] = recognition_count
        
        # Check if covenant should be fully recognized
        if recognition_count >= 1 and self.covenant_status[covenant_id] == CovenantStatus.PENDING:
            await self._promote_to_recognized(covenant_id)
        
        self.logger.info(f"Recognition added to covenant {covenant_id} by {recognizer_enterprise}")
        return True
    
    async def propose_amendment(self, covenant_id: str, proposer_agent: str,
                              proposed_changes: Dict[str, Any], rationale: str,
                              voting_period_days: int = 7) -> str:
        """Propose an amendment to a covenant"""
        if covenant_id not in self.covenants:
            raise ValueError(f"Covenant {covenant_id} not found")
        
        if self.covenant_status[covenant_id] != CovenantStatus.RECOGNIZED:
            raise ValueError(f"Can only amend recognized covenants")
        
        amendment_id = str(uuid.uuid4())
        voting_deadline = datetime.now() + timedelta(days=voting_period_days)
        
        amendment = CovenantAmendment(
            amendment_id=amendment_id,
            proposer_agent=proposer_agent,
            proposed_changes=proposed_changes,
            rationale=rationale,
            proposed_at=datetime.now(),
            voting_deadline=voting_deadline
        )
        
        self.pending_amendments[covenant_id].append(amendment)
        
        self.logger.info(f"Amendment proposed for covenant {covenant_id}: {amendment_id}")
        return amendment_id
    
    async def vote_on_amendment(self, covenant_id: str, amendment_id: str,
                              voter_agent: str, vote: str, rationale: str = None) -> bool:
        """Cast a vote on a covenant amendment"""
        if covenant_id not in self.pending_amendments:
            return False
        
        amendment = next((a for a in self.pending_amendments[covenant_id] 
                         if a.amendment_id == amendment_id), None)
        if not amendment:
            return False
        
        if datetime.now() > amendment.voting_deadline:
            self.logger.warning(f"Voting deadline passed for amendment {amendment_id}")
            return False
        
        # Check if agent already voted
        existing_vote = next((v for v in amendment.votes if v["voter"] == voter_agent), None)
        if existing_vote:
            # Update existing vote
            existing_vote["vote"] = vote
            existing_vote["rationale"] = rationale
            existing_vote["voted_at"] = datetime.now().isoformat()
        else:
            # Add new vote
            amendment.votes.append({
                "voter": voter_agent,
                "vote": vote,
                "rationale": rationale,
                "voted_at": datetime.now().isoformat()
            })
        
        # Check if voting is complete
        await self._check_amendment_completion(covenant_id, amendment)
        
        self.logger.info(f"Vote cast on amendment {amendment_id} by {voter_agent}: {vote}")
        return True
    
    async def get_covenant(self, covenant_id: str) -> Optional[Dict[str, Any]]:
        """Get a covenant by ID"""
        return self.covenants.get(covenant_id)
    
    async def get_covenant_status(self, covenant_id: str) -> Optional[str]:
        """Get the current status of a covenant"""
        status = self.covenant_status.get(covenant_id)
        return status.value if status else None
    
    async def award_compliance_badge(self, covenant_id: str, badge_level: ComplianceBadgeLevel) -> bool:
        """Award a Business Infinity Compliant (BIC) badge"""
        if covenant_id not in self.covenants:
            return False
        
        if self.covenant_status[covenant_id] != CovenantStatus.RECOGNIZED:
            self.logger.warning(f"Cannot award badge to non-recognized covenant {covenant_id}")
            return False
        
        # Calculate badge expiry (1 year from now)
        expires_at = datetime.now() + timedelta(days=365)
        
        badge_info = {
            "awarded": True,
            "awarded_at": datetime.now().isoformat(),
            "badge_level": badge_level.value,
            "expires_at": expires_at.isoformat()
        }
        
        # Update covenant
        covenant = self.covenants[covenant_id]
        covenant["provenance"]["recognition_status"]["bic_badge"] = badge_info
        
        # Store in badges registry
        self.compliance_badges[covenant_id] = badge_info
        
        self.logger.info(f"BIC {badge_level.value} badge awarded to covenant {covenant_id}")
        return True
    
    def get_compliance_statistics(self) -> Dict[str, Any]:
        """Get compliance and covenant statistics"""
        total_covenants = len(self.covenants)
        status_counts = {}
        badge_counts = {}
        
        for status in self.covenant_status.values():
            status_counts[status.value] = status_counts.get(status.value, 0) + 1
        
        for badge_info in self.compliance_badges.values():
            level = badge_info.get("badge_level", "none")
            badge_counts[level] = badge_counts.get(level, 0) + 1
        
        return {
            "total_covenants": total_covenants,
            "status_distribution": status_counts,
            "badge_distribution": badge_counts,
            "total_recognitions": sum(len(recognitions) for recognitions in self.peer_recognitions.values()),
            "pending_amendments": sum(len(amendments) for amendments in self.pending_amendments.values()),
            "last_updated": datetime.now().isoformat()
        }
    
    def _load_schema(self, schema_path: Path) -> Dict[str, Any]:
        """Load the covenant schema"""
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            self.logger.info(f"Loaded covenant schema from {schema_path}")
            return schema
        except Exception as e:
            self.logger.error(f"Failed to load schema: {e}")
            raise
    
    def _create_initial_covenant_structure(self, covenant_id: str, 
                                         enterprise_identity, enterprise_data: Dict[str, Any],
                                         governance_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create initial covenant structure"""
        governance_prefs = governance_preferences or {}
        
        covenant = {
            "covenant_version": "1.0.0",
            "preamble": {
                "mission_statement": enterprise_data.get("mission_statement", 
                    f"To operate as an autonomous enterprise boardroom within the global network of verified businesses."),
                "core_values": enterprise_data.get("core_values", [
                    "Transparency", "Innovation", "Collaboration", "Integrity", "Excellence"
                ]),
                "declaration_of_intent": enterprise_data.get("declaration_of_intent",
                    f"We, {enterprise_identity.company_name}, hereby declare our commitment to participate "
                    f"in the global network of autonomous boardrooms, operating with transparency, "
                    f"maintaining immutable provenance of our decisions, and collaborating with peer "
                    f"enterprises for mutual benefit and industry advancement."),
                "ethical_commitments": enterprise_data.get("ethical_commitments", [
                    "Operate with full transparency in decision-making",
                    "Maintain ethical standards in all business practices",
                    "Respect the autonomy and sovereignty of peer boardrooms",
                    "Contribute positively to the global business community"
                ])
            },
            "identity": {
                "company_name": enterprise_identity.company_name,
                "linkedin_verification": {
                    "company_url": enterprise_identity.linkedin_url,
                    "verification_status": enterprise_identity.verification_status,
                    "verified_at": enterprise_identity.verified_at.isoformat(),
                    "verification_expires": (enterprise_identity.verification_expires.isoformat() 
                                           if enterprise_identity.verification_expires else None)
                },
                "registration_details": {
                    "jurisdiction": enterprise_data.get("jurisdiction", "Unknown"),
                    "registration_number": enterprise_data.get("registration_number"),
                    "industry": enterprise_identity.industry,
                    "size": enterprise_identity.size,
                    "location": enterprise_identity.location
                },
                "verification_timestamp": datetime.now().isoformat()
            },
            "constitutional_roles": self._create_default_roles(enterprise_data),
            "obligations": {
                "transparency": {
                    "decision_logging": True,
                    "audit_trail": True,
                    "public_reporting": {
                        "enabled": governance_prefs.get("public_reporting", False),
                        "frequency": governance_prefs.get("reporting_frequency", "quarterly")
                    }
                },
                "provenance": {
                    "decision_provenance": True,
                    "schema_validation": True,
                    "cryptographic_signing": True
                },
                "interoperability": {
                    "standard_protocols": True,
                    "peer_validation": True,
                    "federation_participation": governance_prefs.get("federation_participation", True)
                }
            },
            "governance_protocols": {
                "decision_making": {
                    "quorum_requirement": governance_prefs.get("quorum_requirement", 0.6),
                    "consensus_threshold": governance_prefs.get("consensus_threshold", 0.7),
                    "voting_method": governance_prefs.get("voting_method", "consensus"),
                    "tie_breaking": governance_prefs.get("tie_breaking", "ceo_decides")
                },
                "amendment_process": {
                    "proposal_threshold": governance_prefs.get("amendment_proposal_threshold", 0.3),
                    "approval_threshold": governance_prefs.get("amendment_approval_threshold", 0.7),
                    "cooling_period": governance_prefs.get("amendment_cooling_period", 7),
                    "peer_notification": True
                },
                "dispute_resolution": {
                    "internal_arbitration": True,
                    "external_arbitration": governance_prefs.get("external_arbitration", False),
                    "mediation_preference": governance_prefs.get("mediation_preference", "peer_network")
                }
            },
            "provenance": {
                "covenant_history": [],
                "validation_records": [],
                "recognition_status": {
                    "status": "draft",
                    "recognition_count": 0,
                    "bic_badge": {
                        "awarded": False
                    }
                }
            },
            "federation_memberships": [],
            "compliance_metadata": {
                "schema_compliance_version": self.schema.get("$id", "1.0.0"),
                "validation_score": 0.0
            }
        }
        
        return covenant
    
    def _create_default_roles(self, enterprise_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create default agent roles configuration"""
        return {
            "boardroom_structure": {
                "c_suite": ["CEO", "CFO", "CTO", "COO"],
                "stakeholder_agents": ["Founder", "Investor"]
            },
            "agent_definitions": {
                "CEO": {
                    "role": "Chief Executive Officer",
                    "domain": "executive_leadership",
                    "responsibilities": [
                        "Strategic decision making",
                        "Board and stakeholder communication",
                        "Company vision and direction",
                        "Final decision authority"
                    ],
                    "authorities": [
                        "Final veto power",
                        "Strategic planning approval",
                        "Major partnership decisions"
                    ],
                    "voting_weight": 0.25
                },
                "CFO": {
                    "role": "Chief Financial Officer",
                    "domain": "financial_management",
                    "responsibilities": [
                        "Financial planning and analysis",
                        "Risk management",
                        "Investor relations",
                        "Financial reporting"
                    ],
                    "authorities": [
                        "Budget approval",
                        "Financial risk assessment",
                        "Investment decisions"
                    ],
                    "voting_weight": 0.2
                },
                "CTO": {
                    "role": "Chief Technology Officer",
                    "domain": "technology_leadership",
                    "responsibilities": [
                        "Technology strategy",
                        "Innovation management",
                        "Technical architecture",
                        "Digital transformation"
                    ],
                    "authorities": [
                        "Technology roadmap",
                        "Technical partnerships",
                        "Platform decisions"
                    ],
                    "voting_weight": 0.2
                },
                "COO": {
                    "role": "Chief Operating Officer",
                    "domain": "operations_management",
                    "responsibilities": [
                        "Operational efficiency",
                        "Process optimization",
                        "Quality management",
                        "Supply chain oversight"
                    ],
                    "authorities": [
                        "Operational procedures",
                        "Process improvements",
                        "Vendor management"
                    ],
                    "voting_weight": 0.15
                },
                "Founder": {
                    "role": "Founder",
                    "domain": "vision_innovation",
                    "responsibilities": [
                        "Company vision",
                        "Cultural leadership",
                        "Innovation guidance",
                        "Long-term strategy"
                    ],
                    "authorities": [
                        "Vision direction",
                        "Cultural decisions",
                        "Innovation priorities"
                    ],
                    "voting_weight": 0.1
                },
                "Investor": {
                    "role": "Investor Representative",
                    "domain": "investment_strategy",
                    "responsibilities": [
                        "Investment oversight",
                        "ROI monitoring",
                        "Growth strategy",
                        "Market analysis"
                    ],
                    "authorities": [
                        "Investment approval",
                        "Exit strategies",
                        "Market expansion"
                    ],
                    "voting_weight": 0.1
                }
            }
        }
    
    async def _validate_business_rules(self, covenant: Dict[str, Any]) -> Dict[str, Any]:
        """Validate business rules beyond schema validation"""
        errors = []
        warnings = []
        
        # Check voting weights sum to 1.0
        agent_defs = covenant.get("constitutional_roles", {}).get("agent_definitions", {})
        total_weight = sum(agent.get("voting_weight", 0) for agent in agent_defs.values())
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
            errors.append({
                "field": "constitutional_roles.agent_definitions",
                "message": f"Voting weights must sum to 1.0, got {total_weight:.3f}"
            })
        
        # Check LinkedIn verification is not expired
        linkedin_verification = covenant.get("identity", {}).get("linkedin_verification", {})
        verification_expires = linkedin_verification.get("verification_expires")
        if verification_expires:
            expires_dt = datetime.fromisoformat(verification_expires.replace('Z', '+00:00'))
            if expires_dt < datetime.now():
                errors.append({
                    "field": "identity.linkedin_verification",
                    "message": "LinkedIn verification has expired"
                })
        
        # Check minimum agent requirements
        c_suite = covenant.get("constitutional_roles", {}).get("boardroom_structure", {}).get("c_suite", [])
        if len(c_suite) < 3:
            warnings.append("Boardroom should have at least 3 C-Suite agents for robust governance")
        
        # Check governance thresholds are reasonable
        governance = covenant.get("governance_protocols", {}).get("decision_making", {})
        quorum = governance.get("quorum_requirement", 0)
        consensus = governance.get("consensus_threshold", 0)
        
        if quorum < 0.5:
            warnings.append("Quorum requirement below 50% may lead to decisions without adequate participation")
        
        if consensus < 0.6:
            warnings.append("Consensus threshold below 60% may not represent true consensus")
        
        return {
            "errors": errors,
            "warnings": warnings
        }
    
    def _calculate_compliance_score(self, covenant: Dict[str, Any], 
                                  schema_valid: bool, business_validation: Dict[str, Any]) -> float:
        """Calculate compliance score for a covenant"""
        score = 0.0
        
        # Schema compliance (40 points)
        if schema_valid:
            score += 40.0
        
        # Business rule compliance (20 points)
        if len(business_validation.get("errors", [])) == 0:
            score += 20.0
        
        # LinkedIn verification (20 points)
        linkedin_status = covenant.get("identity", {}).get("linkedin_verification", {}).get("verification_status")
        if linkedin_status == "verified":
            score += 20.0
        
        # Completeness (10 points)
        required_sections = ["preamble", "identity", "constitutional_roles", "obligations", "governance_protocols"]
        complete_sections = sum(1 for section in required_sections if section in covenant and covenant[section])
        score += (complete_sections / len(required_sections)) * 10.0
        
        # Governance quality (10 points)
        governance = covenant.get("governance_protocols", {})
        if governance:
            governance_score = 0
            if "decision_making" in governance:
                governance_score += 3
            if "amendment_process" in governance:
                governance_score += 3
            if "dispute_resolution" in governance:
                governance_score += 4
            score += governance_score
        
        return min(score, 100.0)  # Cap at 100
    
    def _calculate_content_hash(self, covenant: Dict[str, Any]) -> str:
        """Calculate cryptographic hash of covenant content"""
        # Create a normalized version for hashing (excluding metadata)
        content_for_hash = {
            "covenant_version": covenant.get("covenant_version"),
            "preamble": covenant.get("preamble"),
            "identity": covenant.get("identity"),
            "constitutional_roles": covenant.get("constitutional_roles"),
            "obligations": covenant.get("obligations"),
            "governance_protocols": covenant.get("governance_protocols")
        }
        
        content_str = json.dumps(content_for_hash, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def _generate_recognition_signature(self, covenant_id: str, recognizer_id: str) -> str:
        """Generate cryptographic signature for covenant recognition"""
        signature_data = f"{covenant_id}:{recognizer_id}:{datetime.now().isoformat()}"
        return hashlib.sha256(signature_data.encode()).hexdigest()
    
    async def _promote_to_recognized(self, covenant_id: str):
        """Promote a covenant to recognized status"""
        self.covenant_status[covenant_id] = CovenantStatus.RECOGNIZED
        
        # Update covenant recognition status
        covenant = self.covenants[covenant_id]
        covenant["provenance"]["recognition_status"].update({
            "status": "recognized",
            "recognized_at": datetime.now().isoformat()
        })
        
        # Award bronze badge automatically
        await self.award_compliance_badge(covenant_id, ComplianceBadgeLevel.BRONZE)
        
        self.logger.info(f"Covenant promoted to recognized status: {covenant_id}")
    
    async def _check_amendment_completion(self, covenant_id: str, amendment: CovenantAmendment):
        """Check if amendment voting is complete and process results"""
        covenant = self.covenants[covenant_id]
        governance = covenant.get("governance_protocols", {}).get("amendment_process", {})
        
        # Get total possible voters (all agents with voting weight)
        agent_defs = covenant.get("constitutional_roles", {}).get("agent_definitions", {})
        total_voters = len(agent_defs)
        votes_cast = len(amendment.votes)
        
        # Check if voting period ended or all agents voted
        voting_complete = (datetime.now() > amendment.voting_deadline or 
                          votes_cast >= total_voters)
        
        if not voting_complete:
            return
        
        # Calculate results
        approval_threshold = governance.get("approval_threshold", 0.7)
        yes_votes = sum(1 for vote in amendment.votes if vote["vote"].lower() == "yes")
        approval_ratio = yes_votes / votes_cast if votes_cast > 0 else 0
        
        if approval_ratio >= approval_threshold:
            # Amendment approved
            amendment.status = "approved"
            await self._apply_amendment(covenant_id, amendment)
        else:
            # Amendment rejected
            amendment.status = "rejected"
        
        self.logger.info(f"Amendment {amendment.amendment_id} {amendment.status}: {yes_votes}/{votes_cast} votes")
    
    async def _apply_amendment(self, covenant_id: str, amendment: CovenantAmendment):
        """Apply an approved amendment to the covenant"""
        covenant = self.covenants[covenant_id]
        
        # Apply changes
        for path, new_value in amendment.proposed_changes.items():
            self._set_nested_value(covenant, path, new_value)
        
        # Update version
        current_version = covenant.get("covenant_version", "1.0.0")
        version_parts = current_version.split(".")
        minor_version = int(version_parts[1]) + 1
        new_version = f"{version_parts[0]}.{minor_version}.0"
        covenant["covenant_version"] = new_version
        
        # Record in history
        covenant["provenance"]["covenant_history"].append({
            "version": new_version,
            "created_at": datetime.now().isoformat(),
            "changes": [f"Amendment {amendment.amendment_id}: {amendment.rationale}"],
            "approved_by": [vote["voter"] for vote in amendment.votes if vote["vote"].lower() == "yes"],
            "content_hash": self._calculate_content_hash(covenant)
        })
        
        # Re-validate after amendment
        await self.validate_covenant(covenant_id)
        
        self.logger.info(f"Amendment applied to covenant {covenant_id}: version {new_version}")
    
    def _set_nested_value(self, obj: Dict[str, Any], path: str, value: Any):
        """Set a nested value in a dictionary using dot notation"""
        keys = path.split(".")
        current = obj
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value


# Factory function
def create_covenant_manager(schema_path: str = None, 
                          verification_service: LinkedInVerificationService = None) -> CovenantManager:
    """Create a new covenant manager instance"""
    return CovenantManager(schema_path, verification_service)