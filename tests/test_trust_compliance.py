"""
Tests for Trust and Compliance Manager

Tests the trust and compliance features including:
- Data export functionality
- Data deletion requests
- RBAC information
- Incident response contacts
- Retention policies
- Consent logging
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from core.trust_compliance import (
    TrustComplianceManager, CustomerDataExport, DeletionRequest, 
    get_trust_compliance_manager
)
from core.audit_trail import AuditEventType, AuditSeverity


class TestTrustComplianceManager:
    """Test the trust and compliance manager"""
    
    def setup_method(self):
        """Setup test environment"""
        self.tcm = TrustComplianceManager()
        
    def test_customer_data_export(self):
        """Test customer data export functionality"""
        customer_id = "test_customer_123"
        user_id = "test_user_456"
        
        export_data = self.tcm.export_customer_data(customer_id, user_id)
        
        # Verify export structure
        assert isinstance(export_data, CustomerDataExport)
        assert export_data.customer_id == customer_id
        assert export_data.export_id.startswith("export_")
        assert export_data.integrity_hash is not None
        assert len(export_data.integrity_hash) == 64  # SHA-256 length
        
        # Verify data content
        assert "customer_profile" in export_data.data_records
        assert "onboarding_data" in export_data.data_records
        assert "governance_settings" in export_data.data_records
        
        # Verify integrity hash calculation
        expected_hash = export_data._calculate_integrity_hash()
        assert export_data.integrity_hash == expected_hash
        
    def test_data_deletion_request(self):
        """Test data deletion request functionality"""
        customer_id = "test_customer_123"
        user_id = "test_user_456"
        
        deletion_request = self.tcm.request_data_deletion(customer_id, user_id)
        
        # Verify request structure
        assert isinstance(deletion_request, DeletionRequest)
        assert deletion_request.customer_id == customer_id
        assert deletion_request.request_id.startswith("del_")
        assert deletion_request.confirmation_required is True
        assert deletion_request.confirmed is False
        assert deletion_request.status == "pending"
        
        # Verify SLA date
        expected_sla = datetime.utcnow() + timedelta(days=self.tcm.deletion_sla_days)
        time_diff = abs((deletion_request.sla_completion_date - expected_sla).total_seconds())
        assert time_diff < 60  # Within 1 minute
        
    def test_deletion_confirmation(self):
        """Test deletion confirmation functionality"""
        customer_id = "test_customer_123"
        user_id = "test_user_456"
        request_id = "del_test_request"
        
        result = self.tcm.confirm_data_deletion(request_id, customer_id, user_id)
        
        assert result is True
        
    def test_rbac_info(self):
        """Test RBAC information retrieval"""
        user_id = "test_user_456"
        customer_id = "test_customer_123"
        
        rbac_info = self.tcm.get_user_rbac_info(user_id, customer_id)
        
        # Verify structure
        assert rbac_info["user_id"] == user_id
        assert rbac_info["customer_id"] == customer_id
        assert "role" in rbac_info
        assert "permissions" in rbac_info
        assert "restrictions" in rbac_info
        assert "governance_defaults" in rbac_info
        
        # Verify default customer role
        assert rbac_info["role"] == "customer"
        assert "view_own_data" in rbac_info["permissions"]
        assert "export_own_data" in rbac_info["permissions"]
        
    def test_incident_contact_info(self):
        """Test incident contact information retrieval"""
        contact_info = self.tcm.get_incident_contact_info()
        
        # Verify structure
        assert "incident_response" in contact_info
        assert "breach_notification" in contact_info
        assert "compliance_officer" in contact_info
        
        # Verify incident response details
        incident_response = contact_info["incident_response"]
        assert "primary_contact" in incident_response
        assert "escalation_path" in incident_response
        
        # Verify escalation path
        escalation_path = incident_response["escalation_path"]
        assert len(escalation_path) >= 3
        assert all("level" in step for step in escalation_path)
        assert all("role" in step for step in escalation_path)
        assert all("contact" in step for step in escalation_path)
        
    def test_retention_policy(self):
        """Test retention policy retrieval"""
        retention_policy = self.tcm.get_retention_policy()
        
        # Verify structure
        assert "data_retention" in retention_policy
        assert "deletion_policies" in retention_policy
        assert "backup_policy" in retention_policy
        assert "gdpr_compliance" in retention_policy
        
        # Verify data retention details
        data_retention = retention_policy["data_retention"]
        assert "customer_data" in data_retention
        assert "audit_logs" in data_retention
        assert "temporary_data" in data_retention
        
        # Verify GDPR compliance
        gdpr = retention_policy["gdpr_compliance"]
        assert "right_to_be_forgotten" in gdpr
        assert "data_portability" in gdpr
        assert "consent_management" in gdpr
        
    def test_consent_logging(self):
        """Test consent logging functionality"""
        user_id = "test_user_456"
        customer_id = "test_customer_123"
        consent_type = "privacy_policy"
        consent_given = True
        description = "User accepted privacy policy during onboarding"
        
        # Mock the audit manager to verify logging
        with patch.object(self.tcm.audit_manager, 'log_event') as mock_log:
            mock_log.return_value = "test_event_id"
            
            event_id = self.tcm.log_consent(
                user_id, customer_id, consent_type, consent_given, description
            )
            
            # Verify the audit log was called correctly
            mock_log.assert_called_once()
            call_args = mock_log.call_args
            
            assert call_args[1]["event_type"] == AuditEventType.ACCESS_CONTROL
            assert call_args[1]["subject_id"] == user_id
            assert call_args[1]["action"] == "consent_given"
            assert call_args[1]["target"] == customer_id
            
            # Verify context
            context = call_args[1]["context"]
            assert context["consent_type"] == consent_type
            assert context["consent_given"] == consent_given
            assert context["description"] == description
            
            # Verify compliance tags
            compliance_tags = call_args[1]["compliance_tags"]
            assert "gdpr" in compliance_tags
            assert "consent" in compliance_tags
            assert consent_type in compliance_tags
            
    def test_consent_withdrawal(self):
        """Test consent withdrawal logging"""
        user_id = "test_user_456"
        customer_id = "test_customer_123"
        consent_type = "marketing_communications"
        consent_given = False
        description = "User withdrew consent for marketing communications"
        
        with patch.object(self.tcm.audit_manager, 'log_event') as mock_log:
            mock_log.return_value = "test_event_id"
            
            event_id = self.tcm.log_consent(
                user_id, customer_id, consent_type, consent_given, description
            )
            
            # Verify withdrawal is logged correctly
            call_args = mock_log.call_args
            assert call_args[1]["action"] == "consent_withdrawn"
            
    def test_default_roles_configuration(self):
        """Test default roles and permissions configuration"""
        # Test customer role
        customer_perms = self.tcm.default_roles["customer"]["permissions"]
        assert "view_own_data" in customer_perms
        assert "export_own_data" in customer_perms
        assert "request_deletion" in customer_perms
        
        customer_restrictions = self.tcm.default_roles["customer"]["restrictions"]
        assert "no_cross_customer_access" in customer_restrictions
        
        # Test admin role
        admin_perms = self.tcm.default_roles["admin"]["permissions"]
        assert "view_all_data" in admin_perms
        assert "manage_customers" in admin_perms
        assert "view_audit_logs" in admin_perms
        
    def test_governance_defaults(self):
        """Test governance defaults configuration"""
        defaults = self.tcm.governance_defaults
        
        assert defaults["data_visibility"] == "private_to_customer"
        assert defaults["notification_frequency"] == "weekly"
        assert defaults["access_logging"] == "enabled"
        assert defaults["retention_period_days"] == 2555  # 7 years
        assert defaults["backup_retention_days"] == 90
        
    def test_global_manager_instance(self):
        """Test the global manager instance"""
        manager1 = get_trust_compliance_manager()
        manager2 = get_trust_compliance_manager()
        
        # Should return the same instance
        assert manager1 is manager2
        assert isinstance(manager1, TrustComplianceManager)


class TestCustomerDataExport:
    """Test the CustomerDataExport dataclass"""
    
    def test_integrity_hash_calculation(self):
        """Test integrity hash is calculated correctly"""
        export_data = CustomerDataExport(
            customer_id="test_customer",
            export_timestamp=datetime.utcnow(),
            data_types=["profile", "settings"],
            data_records={"profile": {"name": "Test"}, "settings": {"theme": "dark"}},
            integrity_hash="",  # Will be calculated
            export_id="export_123"
        )
        
        # Hash should be calculated automatically
        assert export_data.integrity_hash != ""
        assert len(export_data.integrity_hash) == 64  # SHA-256
        
        # Manual calculation should match
        manual_hash = export_data._calculate_integrity_hash()
        assert export_data.integrity_hash == manual_hash
        
    def test_integrity_hash_consistency(self):
        """Test that identical data produces identical hashes"""
        timestamp = datetime.utcnow()
        data_records = {"test": "data"}
        
        export1 = CustomerDataExport(
            customer_id="customer1",
            export_timestamp=timestamp,
            data_types=["test"],
            data_records=data_records,
            integrity_hash="",
            export_id="export1"
        )
        
        export2 = CustomerDataExport(
            customer_id="customer1",
            export_timestamp=timestamp,
            data_types=["test"],
            data_records=data_records,
            integrity_hash="",
            export_id="export1"
        )
        
        # Same data should produce same hash
        assert export1.integrity_hash == export2.integrity_hash


class TestDeletionRequest:
    """Test the DeletionRequest dataclass"""
    
    def test_default_values(self):
        """Test default values for deletion request"""
        request = DeletionRequest(
            customer_id="test_customer",
            request_id="del_123",
            request_timestamp=datetime.utcnow()
        )
        
        assert request.confirmation_required is True
        assert request.confirmed is False
        assert request.confirmation_timestamp is None
        assert request.sla_completion_date is None
        assert request.status == "pending"


if __name__ == "__main__":
    pytest.main([__file__])