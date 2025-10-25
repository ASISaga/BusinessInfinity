"""
Risk Registry System

This module provides comprehensive risk tracking and management capabilities
for Business Infinity. It enables:
- Risk identification and registration
- Risk assessment (likelihood, impact, severity)
- Mitigation plan tracking
- Risk owner assignment
- SLA tracking and escalation
- Integration with decision workflows
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict


class RiskSeverity(Enum):
    """Risk severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RiskStatus(Enum):
    """Risk status states"""
    IDENTIFIED = "identified"
    ASSESSING = "assessing"
    MITIGATING = "mitigating"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"


class RiskCategory(Enum):
    """Risk categories"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    REPUTATIONAL = "reputational"
    TECHNICAL = "technical"
    MARKET = "market"


@dataclass
class RiskAssessment:
    """Risk assessment data"""
    likelihood: float  # 0.0 to 1.0
    impact: float  # 0.0 to 1.0
    severity: RiskSeverity
    assessment_date: datetime
    assessor: str
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['assessment_date'] = self.assessment_date.isoformat()
        data['severity'] = self.severity.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RiskAssessment':
        """Create from dictionary"""
        data['assessment_date'] = datetime.fromisoformat(data['assessment_date'])
        data['severity'] = RiskSeverity(data['severity'])
        return cls(**data)


@dataclass
class Risk:
    """Risk data structure"""
    id: str
    title: str
    description: str
    category: RiskCategory
    status: RiskStatus
    owner: str
    identified_date: datetime
    assessment: Optional[RiskAssessment] = None
    mitigation_plan: Optional[str] = None
    mitigation_owner: Optional[str] = None
    mitigation_deadline: Optional[datetime] = None
    review_cadence_days: int = 30
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    resolution_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    related_decisions: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize calculated fields"""
        if self.next_review_date is None and self.identified_date:
            self.next_review_date = self.identified_date + timedelta(days=self.review_cadence_days)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['category'] = self.category.value
        data['status'] = self.status.value
        data['identified_date'] = self.identified_date.isoformat()
        if self.assessment:
            data['assessment'] = self.assessment.to_dict()
        if self.mitigation_deadline:
            data['mitigation_deadline'] = self.mitigation_deadline.isoformat()
        if self.last_review_date:
            data['last_review_date'] = self.last_review_date.isoformat()
        if self.next_review_date:
            data['next_review_date'] = self.next_review_date.isoformat()
        if self.resolution_date:
            data['resolution_date'] = self.resolution_date.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Risk':
        """Create from dictionary"""
        data['category'] = RiskCategory(data['category'])
        data['status'] = RiskStatus(data['status'])
        data['identified_date'] = datetime.fromisoformat(data['identified_date'])
        if data.get('assessment'):
            data['assessment'] = RiskAssessment.from_dict(data['assessment'])
        if data.get('mitigation_deadline'):
            data['mitigation_deadline'] = datetime.fromisoformat(data['mitigation_deadline'])
        if data.get('last_review_date'):
            data['last_review_date'] = datetime.fromisoformat(data['last_review_date'])
        if data.get('next_review_date'):
            data['next_review_date'] = datetime.fromisoformat(data['next_review_date'])
        if data.get('resolution_date'):
            data['resolution_date'] = datetime.fromisoformat(data['resolution_date'])
        return cls(**data)


class RiskRegistry:
    """
    Risk Registry System for Business Infinity
    
    Provides comprehensive risk tracking and management:
    - Risk registration and identification
    - Risk assessment and severity calculation
    - Mitigation plan tracking
    - Owner assignment and accountability
    - SLA tracking and escalation
    - Integration with decision workflows
    """
    
    def __init__(self, storage_manager=None, config=None):
        """
        Initialize Risk Registry
        
        Args:
            storage_manager: Storage manager for persistence
            config: Configuration object
        """
        self.storage_manager = storage_manager
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # In-memory risk registry
        self.risks: Dict[str, Risk] = {}
        
        # SLA thresholds (in days)
        self.sla_thresholds = {
            RiskSeverity.CRITICAL: 1,
            RiskSeverity.HIGH: 7,
            RiskSeverity.MEDIUM: 30,
            RiskSeverity.LOW: 90,
            RiskSeverity.INFO: 180
        }
    
    async def register_risk(self, risk_data: Dict[str, Any]) -> Risk:
        """
        Register a new risk
        
        Args:
            risk_data: Risk information
            
        Returns:
            Created Risk object
        """
        risk_id = risk_data.get('id', f"risk_{datetime.utcnow().timestamp()}")
        
        risk = Risk(
            id=risk_id,
            title=risk_data['title'],
            description=risk_data['description'],
            category=RiskCategory(risk_data.get('category', 'operational')),
            status=RiskStatus.IDENTIFIED,
            owner=risk_data['owner'],
            identified_date=datetime.utcnow(),
            tags=risk_data.get('tags', []),
            related_decisions=risk_data.get('related_decisions', []),
            context=risk_data.get('context', {})
        )
        
        self.risks[risk_id] = risk
        
        # Persist to storage if available
        if self.storage_manager:
            await self._persist_risk(risk)
        
        self.logger.info(f"Risk registered: {risk_id} - {risk.title}")
        return risk
    
    async def assess_risk(
        self,
        risk_id: str,
        likelihood: float,
        impact: float,
        assessor: str,
        notes: Optional[str] = None
    ) -> Risk:
        """
        Assess a risk
        
        Args:
            risk_id: Risk identifier
            likelihood: Likelihood score (0.0 to 1.0)
            impact: Impact score (0.0 to 1.0)
            assessor: Who performed the assessment
            notes: Assessment notes
            
        Returns:
            Updated Risk object
        """
        if risk_id not in self.risks:
            raise ValueError(f"Risk {risk_id} not found")
        
        risk = self.risks[risk_id]
        
        # Calculate severity based on likelihood and impact
        severity = self._calculate_severity(likelihood, impact)
        
        assessment = RiskAssessment(
            likelihood=likelihood,
            impact=impact,
            severity=severity,
            assessment_date=datetime.utcnow(),
            assessor=assessor,
            notes=notes
        )
        
        risk.assessment = assessment
        risk.status = RiskStatus.ASSESSING
        
        # Persist update
        if self.storage_manager:
            await self._persist_risk(risk)
        
        self.logger.info(f"Risk assessed: {risk_id} - Severity: {severity.value}")
        return risk
    
    async def add_mitigation_plan(
        self,
        risk_id: str,
        mitigation_plan: str,
        mitigation_owner: str,
        deadline_days: Optional[int] = None
    ) -> Risk:
        """
        Add mitigation plan to a risk
        
        Args:
            risk_id: Risk identifier
            mitigation_plan: Description of mitigation plan
            mitigation_owner: Who is responsible for mitigation
            deadline_days: Days until mitigation deadline
            
        Returns:
            Updated Risk object
        """
        if risk_id not in self.risks:
            raise ValueError(f"Risk {risk_id} not found")
        
        risk = self.risks[risk_id]
        risk.mitigation_plan = mitigation_plan
        risk.mitigation_owner = mitigation_owner
        
        # Set deadline based on severity if not provided
        if deadline_days is None and risk.assessment:
            deadline_days = self.sla_thresholds.get(risk.assessment.severity, 30)
        
        if deadline_days:
            risk.mitigation_deadline = datetime.utcnow() + timedelta(days=deadline_days)
        
        risk.status = RiskStatus.MITIGATING
        
        # Persist update
        if self.storage_manager:
            await self._persist_risk(risk)
        
        self.logger.info(f"Mitigation plan added for risk: {risk_id}")
        return risk
    
    async def update_risk_status(self, risk_id: str, status: RiskStatus) -> Risk:
        """
        Update risk status
        
        Args:
            risk_id: Risk identifier
            status: New status
            
        Returns:
            Updated Risk object
        """
        if risk_id not in self.risks:
            raise ValueError(f"Risk {risk_id} not found")
        
        risk = self.risks[risk_id]
        old_status = risk.status
        risk.status = status
        
        # Set resolution date if resolved
        if status == RiskStatus.RESOLVED and not risk.resolution_date:
            risk.resolution_date = datetime.utcnow()
        
        # Persist update
        if self.storage_manager:
            await self._persist_risk(risk)
        
        self.logger.info(f"Risk {risk_id} status updated: {old_status.value} -> {status.value}")
        return risk
    
    async def review_risk(self, risk_id: str, reviewer: str, notes: Optional[str] = None) -> Risk:
        """
        Review a risk
        
        Args:
            risk_id: Risk identifier
            reviewer: Who performed the review
            notes: Review notes
            
        Returns:
            Updated Risk object
        """
        if risk_id not in self.risks:
            raise ValueError(f"Risk {risk_id} not found")
        
        risk = self.risks[risk_id]
        risk.last_review_date = datetime.utcnow()
        risk.next_review_date = datetime.utcnow() + timedelta(days=risk.review_cadence_days)
        
        # Add review to context
        if not risk.context:
            risk.context = {}
        if 'reviews' not in risk.context:
            risk.context['reviews'] = []
        
        risk.context['reviews'].append({
            'date': datetime.utcnow().isoformat(),
            'reviewer': reviewer,
            'notes': notes
        })
        
        # Persist update
        if self.storage_manager:
            await self._persist_risk(risk)
        
        self.logger.info(f"Risk reviewed: {risk_id} by {reviewer}")
        return risk
    
    async def get_risk(self, risk_id: str) -> Optional[Risk]:
        """Get a risk by ID"""
        return self.risks.get(risk_id)
    
    async def get_risks_by_status(self, status: RiskStatus) -> List[Risk]:
        """Get all risks with a specific status"""
        return [r for r in self.risks.values() if r.status == status]
    
    async def get_risks_by_severity(self, severity: RiskSeverity) -> List[Risk]:
        """Get all risks with a specific severity"""
        return [
            r for r in self.risks.values()
            if r.assessment and r.assessment.severity == severity
        ]
    
    async def get_risks_by_owner(self, owner: str) -> List[Risk]:
        """Get all risks owned by a specific person"""
        return [r for r in self.risks.values() if r.owner == owner]
    
    async def get_overdue_risks(self) -> List[Risk]:
        """Get all risks that are overdue for review or mitigation"""
        now = datetime.utcnow()
        overdue = []
        
        for risk in self.risks.values():
            # Check mitigation deadline
            if risk.mitigation_deadline and risk.mitigation_deadline < now:
                if risk.status not in [RiskStatus.RESOLVED, RiskStatus.ACCEPTED]:
                    overdue.append(risk)
            # Check review deadline
            elif risk.next_review_date and risk.next_review_date < now:
                if risk.status not in [RiskStatus.RESOLVED]:
                    overdue.append(risk)
        
        return overdue
    
    async def get_risks_summary(self) -> Dict[str, Any]:
        """Get summary statistics of all risks"""
        total_risks = len(self.risks)
        
        # Count by status
        by_status = {}
        for status in RiskStatus:
            by_status[status.value] = len([r for r in self.risks.values() if r.status == status])
        
        # Count by severity
        by_severity = {}
        for severity in RiskSeverity:
            by_severity[severity.value] = len([
                r for r in self.risks.values()
                if r.assessment and r.assessment.severity == severity
            ])
        
        # Count by category
        by_category = {}
        for category in RiskCategory:
            by_category[category.value] = len([r for r in self.risks.values() if r.category == category])
        
        # Get overdue count
        overdue = await self.get_overdue_risks()
        
        return {
            'total_risks': total_risks,
            'by_status': by_status,
            'by_severity': by_severity,
            'by_category': by_category,
            'overdue_count': len(overdue),
            'overdue_risks': [r.id for r in overdue]
        }
    
    def _calculate_severity(self, likelihood: float, impact: float) -> RiskSeverity:
        """
        Calculate risk severity based on likelihood and impact
        
        Uses a risk matrix approach:
        - Critical: High likelihood + High impact
        - High: Medium-high likelihood or impact
        - Medium: Medium likelihood and impact
        - Low: Low likelihood or impact
        - Info: Very low likelihood and impact
        """
        risk_score = likelihood * impact
        
        if risk_score >= 0.8:
            return RiskSeverity.CRITICAL
        elif risk_score >= 0.6:
            return RiskSeverity.HIGH
        elif risk_score >= 0.3:
            return RiskSeverity.MEDIUM
        elif risk_score >= 0.1:
            return RiskSeverity.LOW
        else:
            return RiskSeverity.INFO
    
    async def _persist_risk(self, risk: Risk):
        """Persist risk to storage"""
        try:
            if hasattr(self.storage_manager, 'store_risk'):
                await self.storage_manager.store_risk(risk.to_dict())
            else:
                self.logger.warning("Storage manager does not support risk persistence")
        except Exception as e:
            self.logger.error(f"Failed to persist risk {risk.id}: {e}")
