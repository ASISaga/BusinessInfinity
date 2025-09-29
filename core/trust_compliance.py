"""
Trust and Compliance Manager for Business Infinity

Handles trust and compliance features including:
- Data export for customers
- Data deletion requests
- RBAC information
- Incident response contacts
- Retention policies
- Consent logging
"""

import json
import hashlib
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from .audit_trail import get_audit_manager, AuditEventType, AuditSeverity


logger = logging.getLogger(__name__)


@dataclass
class CustomerDataExport:
    """Represents a customer data export with integrity protection"""
    customer_id: str
    export_timestamp: datetime
    data_types: List[str]
    data_records: Dict[str, Any]
    integrity_hash: str
    export_id: str
    
    def __post_init__(self):
        """Calculate integrity hash if not provided"""
        if not self.integrity_hash:
            self.integrity_hash = self._calculate_integrity_hash()
    
    def _calculate_integrity_hash(self) -> str:
        """Calculate SHA-256 hash for export integrity"""
        # Create a copy without the hash for calculation
        data = asdict(self)
        data.pop('integrity_hash', None)
        
        # Convert datetime to string for JSON serialization
        data['export_timestamp'] = self.export_timestamp.isoformat()
        
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()


@dataclass
class DeletionRequest:
    """Represents a customer data deletion request"""
    customer_id: str
    request_id: str
    request_timestamp: datetime
    confirmation_required: bool = True
    confirmed: bool = False
    confirmation_timestamp: Optional[datetime] = None
    sla_completion_date: Optional[datetime] = None
    status: str = "pending"  # pending, confirmed, processing, completed, cancelled


class TrustComplianceManager:
    """Manager for trust and compliance operations"""
    
    def __init__(self):
        self.audit_manager = get_audit_manager()
        
        # Default SLA for deletion requests (30 days)
        self.deletion_sla_days = 30
        
        # Default roles and permissions
        self.default_roles = {
            "customer": {
                "permissions": ["view_own_data", "export_own_data", "request_deletion"],
                "restrictions": ["no_cross_customer_access"]
            },
            "admin": {
                "permissions": ["view_all_data", "manage_customers", "view_audit_logs"],
                "restrictions": ["audit_logged_access"]
            },
            "operator": {
                "permissions": ["view_own_customer_data", "support_customers"],
                "restrictions": ["no_admin_operations", "audit_logged_access"]
            }
        }
        
        # Governance defaults
        self.governance_defaults = {
            "data_visibility": "private_to_customer",
            "notification_frequency": "weekly",
            "access_logging": "enabled",
            "retention_period_days": 2555,  # 7 years default
            "backup_retention_days": 90
        }
    
    def export_customer_data(self, customer_id: str, requesting_user_id: str) -> CustomerDataExport:
        """
        Export all data for a customer partition
        
        Args:
            customer_id: The customer partition ID
            requesting_user_id: The user making the request (for audit)
        
        Returns:
            CustomerDataExport object with all customer data
        """
        # Log the export request
        export_id = f"export_{customer_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        self.audit_manager.log_event(
            event_type=AuditEventType.BUSINESS_DATA_ACCESS,
            subject_id=requesting_user_id,
            subject_type="user",
            action="data_export_request",
            severity=AuditSeverity.HIGH,
            target=customer_id,
            context={
                "export_id": export_id,
                "request_type": "full_customer_export",
                "compliance_purpose": "gdpr_data_portability"
            },
            compliance_tags={"gdpr", "data_export", "customer_rights"}
        )
        
        # In a real implementation, this would query all customer data
        # For now, we'll create a mock export structure
        export_data = {
            "customer_profile": {
                "customer_id": customer_id,
                "onboarding_date": "2024-01-15T10:30:00Z",
                "business_name": f"Business_{customer_id}",
                "contact_info": {"email": f"contact@business_{customer_id}.com"}
            },
            "onboarding_data": {
                "linkedin_profile": {"connected": True, "profile_url": "https://linkedin.com/in/example"},
                "website_analysis": {"url": f"https://business_{customer_id}.com"},
                "financial_documents": {"uploaded": True, "count": 3}
            },
            "audit_trail": {
                "note": "Detailed audit trail available separately",
                "total_events": 42
            },
            "governance_settings": self.governance_defaults.copy()
        }
        
        export = CustomerDataExport(
            customer_id=customer_id,
            export_timestamp=datetime.utcnow(),
            data_types=list(export_data.keys()),
            data_records=export_data,
            integrity_hash="",  # Will be calculated in __post_init__
            export_id=export_id
        )
        
        # Log successful export
        self.audit_manager.log_event(
            event_type=AuditEventType.BUSINESS_DATA_ACCESS,
            subject_id=requesting_user_id,
            subject_type="user",
            action="data_export_completed",
            severity=AuditSeverity.HIGH,
            target=customer_id,
            context={
                "export_id": export_id,
                "data_types": export.data_types,
                "integrity_hash": export.integrity_hash,
                "records_count": len(export_data)
            },
            compliance_tags={"gdpr", "data_export", "completed"}
        )
        
        return export
    
    def request_data_deletion(self, customer_id: str, requesting_user_id: str) -> DeletionRequest:
        """
        Request deletion of customer data
        
        Args:
            customer_id: The customer partition ID
            requesting_user_id: The user making the request
        
        Returns:
            DeletionRequest object with request details
        """
        request_id = f"del_{customer_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        sla_date = datetime.utcnow() + timedelta(days=self.deletion_sla_days)
        
        deletion_request = DeletionRequest(
            customer_id=customer_id,
            request_id=request_id,
            request_timestamp=datetime.utcnow(),
            sla_completion_date=sla_date
        )
        
        # Log the deletion request
        self.audit_manager.log_event(
            event_type=AuditEventType.BUSINESS_DATA_ACCESS,
            subject_id=requesting_user_id,
            subject_type="user",
            action="data_deletion_request",
            severity=AuditSeverity.CRITICAL,
            target=customer_id,
            context={
                "request_id": request_id,
                "sla_completion_date": sla_date.isoformat(),
                "confirmation_required": deletion_request.confirmation_required
            },
            compliance_tags={"gdpr", "data_deletion", "customer_rights"}
        )
        
        return deletion_request
    
    def confirm_data_deletion(self, request_id: str, customer_id: str, requesting_user_id: str) -> bool:
        """
        Confirm a data deletion request
        
        Args:
            request_id: The deletion request ID
            customer_id: The customer partition ID
            requesting_user_id: The user confirming the request
        
        Returns:
            True if confirmation successful
        """
        # Log the confirmation
        self.audit_manager.log_event(
            event_type=AuditEventType.BUSINESS_DATA_ACCESS,
            subject_id=requesting_user_id,
            subject_type="user",
            action="data_deletion_confirmed",
            severity=AuditSeverity.CRITICAL,
            target=customer_id,
            context={
                "request_id": request_id,
                "confirmation_timestamp": datetime.utcnow().isoformat()
            },
            compliance_tags={"gdpr", "data_deletion", "confirmed"}
        )
        
        return True
    
    def get_user_rbac_info(self, user_id: str, customer_id: str) -> Dict[str, Any]:
        """
        Get RBAC information for a user
        
        Args:
            user_id: The user ID
            customer_id: The customer partition ID
        
        Returns:
            Dictionary containing role and permission information
        """
        # In a real implementation, this would query the user management system
        # For now, return default customer role
        user_role = "customer"  # Default role
        
        rbac_info = {
            "user_id": user_id,
            "customer_id": customer_id,
            "role": user_role,
            "permissions": self.default_roles.get(user_role, {}).get("permissions", []),
            "restrictions": self.default_roles.get(user_role, {}).get("restrictions", []),
            "governance_defaults": self.governance_defaults.copy(),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Log RBAC information access
        self.audit_manager.log_event(
            event_type=AuditEventType.ACCESS_CONTROL,
            subject_id=user_id,
            subject_type="user",
            action="rbac_info_accessed",
            severity=AuditSeverity.MEDIUM,
            target=customer_id,
            context={"role": user_role},
            compliance_tags={"rbac", "access_control"}
        )
        
        return rbac_info
    
    def get_incident_contact_info(self) -> Dict[str, Any]:
        """
        Get incident response and escalation contact information
        
        Returns:
            Dictionary containing contact and escalation information
        """
        # Based on trust-compliance.md specifications
        contact_info = {
            "incident_response": {
                "primary_contact": {
                    "email": "security@businessinfinity.asisaga.com",
                    "response_time_sla": "4 hours",
                    "escalation_threshold": "critical security incidents"
                },
                "escalation_path": [
                    {
                        "level": 1,
                        "role": "Customer Success",
                        "contact": "support@businessinfinity.asisaga.com",
                        "response_time": "2 hours"
                    },
                    {
                        "level": 2,
                        "role": "App Developers",
                        "contact": "dev@businessinfinity.asisaga.com",
                        "response_time": "4 hours"
                    },
                    {
                        "level": 3,
                        "role": "Infra Maintainers",
                        "contact": "infra@businessinfinity.asisaga.com",
                        "response_time": "8 hours"
                    }
                ]
            },
            "breach_notification": {
                "contact": "breach@businessinfinity.asisaga.com",
                "sla": "72 hours to regulatory authorities, 24 hours to affected customers"
            },
            "compliance_officer": {
                "contact": "compliance@businessinfinity.asisaga.com",
                "role": "Data Protection Officer"
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return contact_info
    
    def get_retention_policy(self) -> Dict[str, Any]:
        """
        Get current data retention and deletion policies
        
        Returns:
            Dictionary containing retention policy information
        """
        retention_policy = {
            "data_retention": {
                "customer_data": {
                    "retention_period": "7 years",
                    "rationale": "Business records retention requirement",
                    "auto_deletion": False
                },
                "audit_logs": {
                    "retention_period": "10 years",
                    "rationale": "Compliance and audit requirements",
                    "immutable": True
                },
                "temporary_data": {
                    "retention_period": "90 days",
                    "rationale": "Processing and backup purposes",
                    "auto_deletion": True
                }
            },
            "deletion_policies": {
                "customer_request": {
                    "sla": f"{self.deletion_sla_days} days",
                    "process": "Customer initiated, requires confirmation",
                    "exceptions": "Legal hold, active investigations"
                },
                "automated_cleanup": {
                    "temporary_files": "Daily cleanup of files older than 24 hours",
                    "expired_sessions": "Hourly cleanup of expired user sessions",
                    "log_rotation": "Monthly rotation of non-compliance logs"
                }
            },
            "backup_policy": {
                "frequency": "Daily incremental, weekly full backup",
                "retention": "90 days for incremental, 1 year for full backups",
                "encryption": "AES-256 encryption at rest and in transit"
            },
            "gdpr_compliance": {
                "right_to_be_forgotten": "Supported via deletion request process",
                "data_portability": "Supported via data export functionality",
                "consent_management": "Tracked in audit logs with timestamps"
            },
            "last_updated": datetime.utcnow().isoformat(),
            "policy_version": "1.0"
        }
        
        return retention_policy
    
    def log_consent(self, user_id: str, customer_id: str, consent_type: str, 
                   consent_given: bool, description: str) -> str:
        """
        Log user consent for compliance
        
        Args:
            user_id: The user giving consent
            customer_id: The customer partition
            consent_type: Type of consent (privacy, governance, terms, etc.)
            consent_given: Whether consent was given or withdrawn
            description: Description of the consent action
        
        Returns:
            Event ID of the logged consent
        """
        action = f"consent_{'given' if consent_given else 'withdrawn'}"
        
        return self.audit_manager.log_event(
            event_type=AuditEventType.ACCESS_CONTROL,
            subject_id=user_id,
            subject_type="user",
            action=action,
            severity=AuditSeverity.HIGH,
            target=customer_id,
            context={
                "consent_type": consent_type,
                "consent_given": consent_given,
                "description": description,
                "consent_timestamp": datetime.utcnow().isoformat()
            },
            compliance_tags={"gdpr", "consent", "privacy", consent_type}
        )


# Global instance
_trust_compliance_manager: Optional[TrustComplianceManager] = None


def get_trust_compliance_manager() -> TrustComplianceManager:
    """Get the global trust and compliance manager instance"""
    global _trust_compliance_manager
    if _trust_compliance_manager is None:
        _trust_compliance_manager = TrustComplianceManager()
    return _trust_compliance_manager