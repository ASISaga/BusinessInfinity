"""
Simple test runner for Trust and Compliance Manager (no pytest dependency)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.trust_compliance import (
    TrustComplianceManager, CustomerDataExport, DeletionRequest, 
    get_trust_compliance_manager
)
from core.audit_trail import AuditEventType, AuditSeverity
from datetime import datetime, timedelta


def test_customer_data_export():
    """Test customer data export functionality"""
    tcm = TrustComplianceManager()
    customer_id = "test_customer_123"
    user_id = "test_user_456"
    
    export_data = tcm.export_customer_data(customer_id, user_id)
    
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
    
    print("✓ Customer data export test passed")


def test_data_deletion_request():
    """Test data deletion request functionality"""
    tcm = TrustComplianceManager()
    customer_id = "test_customer_123"
    user_id = "test_user_456"
    
    deletion_request = tcm.request_data_deletion(customer_id, user_id)
    
    # Verify request structure
    assert isinstance(deletion_request, DeletionRequest)
    assert deletion_request.customer_id == customer_id
    assert deletion_request.request_id.startswith("del_")
    assert deletion_request.confirmation_required is True
    assert deletion_request.confirmed is False
    assert deletion_request.status == "pending"
    
    # Verify SLA date
    expected_sla = datetime.utcnow() + timedelta(days=tcm.deletion_sla_days)
    time_diff = abs((deletion_request.sla_completion_date - expected_sla).total_seconds())
    assert time_diff < 60  # Within 1 minute
    
    print("✓ Data deletion request test passed")


def test_rbac_info():
    """Test RBAC information retrieval"""
    tcm = TrustComplianceManager()
    user_id = "test_user_456"
    customer_id = "test_customer_123"
    
    rbac_info = tcm.get_user_rbac_info(user_id, customer_id)
    
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
    
    print("✓ RBAC info test passed")


def test_incident_contact_info():
    """Test incident contact information retrieval"""
    tcm = TrustComplianceManager()
    contact_info = tcm.get_incident_contact_info()
    
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
    
    print("✓ Incident contact info test passed")


def test_retention_policy():
    """Test retention policy retrieval"""
    tcm = TrustComplianceManager()
    retention_policy = tcm.get_retention_policy()
    
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
    
    print("✓ Retention policy test passed")


def test_consent_logging():
    """Test consent logging functionality"""
    tcm = TrustComplianceManager()
    user_id = "test_user_456"
    customer_id = "test_customer_123"
    consent_type = "privacy_policy"
    consent_given = True
    description = "User accepted privacy policy during onboarding"
    
    event_id = tcm.log_consent(
        user_id, customer_id, consent_type, consent_given, description
    )
    
    assert event_id is not None
    print("✓ Consent logging test passed")


def test_global_manager_instance():
    """Test the global manager instance"""
    manager1 = get_trust_compliance_manager()
    manager2 = get_trust_compliance_manager()
    
    # Should return the same instance
    assert manager1 is manager2
    assert isinstance(manager1, TrustComplianceManager)
    
    print("✓ Global manager instance test passed")


def run_all_tests():
    """Run all tests"""
    print("Running Trust and Compliance Manager tests...")
    
    try:
        test_customer_data_export()
        test_data_deletion_request()
        test_rbac_info()
        test_incident_contact_info()
        test_retention_policy()
        test_consent_logging()
        test_global_manager_instance()
        
        print("\n✓ All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)