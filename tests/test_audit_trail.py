"""
Test Comprehensive Audit Trail System

Tests for the comprehensive audit trail functionality including:
- Boardroom decision and voting audit logs
- MCP server interaction audit logs
- Business action audit logs  
- Social media action audit logs
- Access control audit logs
- Audit log integrity and compliance
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.audit_trail import (
    AuditTrailManager, AuditEventType, AuditSeverity, AuditEvent, AuditQuery,
    audit_log, get_audit_manager
)
from src.core.mcp_access_control import MCPAccessControlManager


class TestAuditTrailManager:
    """Test the comprehensive audit trail manager"""
    
    def setup_method(self):
        """Setup test environment with temporary storage"""
        self.temp_dir = tempfile.mkdtemp()
        self.audit_manager = AuditTrailManager(storage_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_audit_event_creation(self):
        """Test creating audit events with integrity protection"""
        event = AuditEvent(
            event_id="test_event_1",
            event_type=AuditEventType.BOARDROOM_DECISION,
            timestamp=datetime.utcnow(),
            severity=AuditSeverity.HIGH,
            subject_id="test_boardroom",
            subject_type="system",
            action="Test decision made",
            context={"test": "data"}
        )
        
        # Verify checksum is calculated
        assert event.checksum is not None
        assert len(event.checksum) == 64  # SHA-256 hex length
        
        # Verify integrity
        assert event.verify_integrity() is True
        
        # Test tampering detection
        event.action = "Modified action"
        assert event.verify_integrity() is False
    
    def test_boardroom_decision_logging(self):
        """Test logging boardroom decisions"""
        event_id = self.audit_manager.log_boardroom_decision(
            decision_id="decision_123",
            decision_type="strategic",
            proposed_by="ceo_agent",
            final_decision="Expand into new market",
            rationale="Market analysis shows strong opportunity",
            votes=[
                {"voter_id": "ceo", "vote_value": 0.8, "rationale": "Strong growth potential"},
                {"voter_id": "cfo", "vote_value": 0.6, "rationale": "Financially viable"}
            ],
            confidence_score=0.85,
            consensus_score=0.75
        )
        
        assert event_id is not None
        
        # Verify event was created correctly
        query = AuditQuery(
            event_types=[AuditEventType.BOARDROOM_DECISION],
            limit=1
        )
        events = self.audit_manager.query_events(query)
        
        assert len(events) == 1
        event = events[0]
        assert event.subject_id == "decision_123"
        assert event.action == "Made decision: strategic"
        assert event.metrics["confidence_score"] == 0.85
        assert "business_governance" in event.compliance_tags
    
    def test_agent_vote_logging(self):
        """Test logging individual agent votes"""
        event_id = self.audit_manager.log_agent_vote(
            voter_id="ceo_agent",
            voter_role="CEO",
            decision_id="decision_123",
            vote_value=0.8,
            rationale="Strategic alignment with company goals",
            evidence=["Market research report", "Financial projections"],
            confidence=0.9
        )
        
        assert event_id is not None
        
        # Verify event details
        query = AuditQuery(event_types=[AuditEventType.AGENT_VOTE])
        events = self.audit_manager.query_events(query)
        
        assert len(events) == 1
        event = events[0]
        assert event.subject_id == "ceo_agent"
        assert event.subject_role == "CEO"
        assert event.metrics["vote_value"] == 0.8
        assert len(event.evidence) == 2
    
    def test_mcp_interaction_logging(self):
        """Test logging MCP server interactions"""
        # Test successful interaction
        success_id = self.audit_manager.log_mcp_interaction(
            mcp_server="linkedin",
            operation="create_post",
            subject_id="marketing_agent",
            subject_type="agent",
            success=True,
            request_data={"content": "New product announcement"},
            response_data={"post_id": "12345", "status": "published"}
        )
        
        # Test failed interaction
        failure_id = self.audit_manager.log_mcp_interaction(
            mcp_server="erpnext",
            operation="create_invoice", 
            subject_id="finance_agent",
            subject_type="agent",
            success=False,
            request_data={"customer": "ABC Corp", "amount": 1000},
            error_details="Insufficient permissions"
        )
        
        # Verify both interactions were logged
        query = AuditQuery(event_types=[AuditEventType.MCP_REQUEST, AuditEventType.MCP_ERROR])
        events = self.audit_manager.query_events(query)
        
        assert len(events) == 2
        
        # Check successful interaction
        success_event = next(e for e in events if e.event_id == success_id)
        assert success_event.mcp_server == "linkedin"
        assert success_event.context["success"] is True
        
        # Check failed interaction  
        failure_event = next(e for e in events if e.event_id == failure_id)
        assert failure_event.event_type == AuditEventType.MCP_ERROR
        assert failure_event.severity == AuditSeverity.HIGH
    
    def test_social_media_action_logging(self):
        """Test logging social media actions"""
        event_id = self.audit_manager.log_social_media_action(
            platform="linkedin",
            action_type="post",
            agent_id="marketing_agent",
            content="Excited to announce our new AI-powered business solution!",
            target_audience="technology_professionals",
            engagement_metrics={"likes": 50, "comments": 12, "shares": 8}
        )
        
        # Verify social media action was logged
        query = AuditQuery(event_types=[AuditEventType.SOCIAL_MEDIA_POST])
        events = self.audit_manager.query_events(query)
        
        assert len(events) == 1
        event = events[0]
        assert event.mcp_server == "linkedin"
        assert "social_media" in event.compliance_tags
        assert "content_preview" in event.context
    
    def test_business_action_logging(self):
        """Test logging business system actions"""
        event_id = self.audit_manager.log_business_action(
            system="erpnext",
            operation="create_invoice",
            agent_id="finance_agent", 
            business_entity="customer_123",
            transaction_data={
                "invoice_number": "INV-2024-001",
                "amount": 5000.00,
                "currency": "USD"
            }
        )
        
        # Verify business action was logged
        query = AuditQuery(event_types=[AuditEventType.BUSINESS_TRANSACTION])
        events = self.audit_manager.query_events(query)
        
        assert len(events) == 1
        event = events[0]
        assert event.severity == AuditSeverity.HIGH
        assert "sox" in event.compliance_tags
        assert "financial" in event.compliance_tags
    
    def test_audit_query_filtering(self):
        """Test audit log querying and filtering"""
        # Create multiple test events
        self.audit_manager.log_event(
            AuditEventType.ACCESS_GRANTED, "user1", "user", "Login successful"
        )
        self.audit_manager.log_event(
            AuditEventType.ACCESS_DENIED, "user2", "user", "Invalid credentials"
        )
        self.audit_manager.log_event(
            AuditEventType.MCP_REQUEST, "agent1", "agent", "Data query"
        )
        
        # Test filtering by event type
        access_query = AuditQuery(
            event_types=[AuditEventType.ACCESS_GRANTED, AuditEventType.ACCESS_DENIED]
        )
        access_events = self.audit_manager.query_events(access_query)
        assert len(access_events) == 2
        
        # Test filtering by subject type
        user_query = AuditQuery(subject_types=["user"])
        user_events = self.audit_manager.query_events(user_query)
        assert len(user_events) == 2
        
        # Test filtering by severity
        high_severity_query = AuditQuery(severities=[AuditSeverity.HIGH])
        high_events = self.audit_manager.query_events(high_severity_query)
        # Should have business transaction from previous test
        assert len(high_events) >= 1
    
    def test_audit_context_manager(self):
        """Test audit context manager for operation tracking"""
        with self.audit_manager.audit_context(
            operation="test_operation",
            subject_id="test_system",
            subject_type="system"
        ) as context_id:
            # Simulate some work
            pass
        
        # Should have logged start and completion
        query = AuditQuery(subject_ids=["test_system"])
        events = self.audit_manager.query_events(query)
        assert len(events) >= 2  # Start and completion events
    
    def test_audit_export(self):
        """Test audit trail export functionality"""
        # Create some test events
        self.audit_manager.log_event(
            AuditEventType.BOARDROOM_DECISION, "boardroom", "system", "Test decision"
        )
        
        # Export audit trail
        query = AuditQuery(limit=100)
        export_data = self.audit_manager.export_audit_trail(
            query=query,
            format="json",
            include_integrity_check=True
        )
        
        assert export_data is not None
        import json
        data = json.loads(export_data)
        
        assert "export_timestamp" in data
        assert "events" in data
        assert "integrity_check" in data
        assert len(data["events"]) >= 1
    
    def test_compliance_retention(self):
        """Test compliance-based retention policies"""
        # Create events with different compliance tags
        sox_event_id = self.audit_manager.log_event(
            AuditEventType.BUSINESS_TRANSACTION,
            "finance_agent", "agent", "Financial transaction",
            compliance_tags={"sox"}
        )
        
        gdpr_event_id = self.audit_manager.log_event(
            AuditEventType.BUSINESS_DATA_ACCESS,
            "user1", "user", "Data access",
            compliance_tags={"gdpr"}
        )
        
        # Query events and check retention periods
        query = AuditQuery(limit=10)
        events = self.audit_manager.query_events(query)
        
        for event in events:
            if "sox" in event.compliance_tags:
                # SOX retention should be ~7 years
                days_diff = (event.retention_until - event.timestamp).days
                assert days_diff >= 2500  # Approximately 7 years
            elif "gdpr" in event.compliance_tags:
                # GDPR retention should be up to 7 years
                days_diff = (event.retention_until - event.timestamp).days
                assert days_diff >= 300  # At least 1 year


class TestAuditTrailIntegration:
    """Test integration of audit trail with other systems"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock config for access control
        self.config_data = {
            "audit": {"log_denied_access": True, "log_all_access": True},
            "access_levels": {
                "read_only": {"permissions": ["read"]},
                "full_write": {"permissions": ["read", "create", "update"]}
            },
            "roles": {
                "Employee": {"default_access_level": "read_only"},
                "Manager": {"default_access_level": "full_write"}
            }
        }
        
        with patch.object(MCPAccessControlManager, '_load_config') as mock_load:
            mock_load.return_value = self.config_data
            self.access_manager = MCPAccessControlManager()
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_access_control_audit_integration(self):
        """Test that access control creates proper audit logs"""
        # Test successful access
        has_access, reason = self.access_manager.check_access(
            "user123", "Manager", "linkedin", "create"
        )
        
        assert has_access is True
        
        # Verify audit log was created for granted access
        audit_manager = get_audit_manager()
        query = AuditQuery(
            event_types=[AuditEventType.ACCESS_GRANTED],
            subject_ids=["user123"]
        )
        events = audit_manager.query_events(query)
        assert len(events) >= 1
        
        # Test denied access
        has_access, reason = self.access_manager.check_access(
            "user456", "Employee", "erpnext", "delete"
        )
        
        assert has_access is False
        
        # Verify audit log was created for denied access
        query = AuditQuery(
            event_types=[AuditEventType.ACCESS_DENIED],
            subject_ids=["user456"]
        )
        events = audit_manager.query_events(query)
        assert len(events) >= 1
    
    def test_boardroom_agent_access_audit(self):
        """Test that boardroom agent access is properly audited"""
        # Test agent access
        has_access, reason = self.access_manager.check_boardroom_agent_access(
            "CEO", "linkedin", "create"
        )
        
        # Should be denied since no agent profile exists
        assert has_access is False
        
        # Verify audit log for agent access denial
        audit_manager = get_audit_manager()
        query = AuditQuery(
            event_types=[AuditEventType.ACCESS_DENIED],
            subject_types=["agent"]
        )
        events = audit_manager.query_events(query)
        assert len(events) >= 1


if __name__ == "__main__":
    # Run basic functionality test
    temp_dir = tempfile.mkdtemp()
    try:
        audit_manager = AuditTrailManager(storage_path=temp_dir)
        
        # Test basic logging
        event_id = audit_manager.log_event(
            AuditEventType.SYSTEM_STARTUP,
            "test_system",
            "system", 
            "Test audit system"
        )
        print(f"Created audit event: {event_id}")
        
        # Test querying
        query = AuditQuery(limit=10)
        events = audit_manager.query_events(query)
        print(f"Found {len(events)} audit events")
        
        # Test export
        export_data = audit_manager.export_audit_trail(query)
        print(f"Exported {len(export_data)} bytes of audit data")
        
        print("Basic audit trail functionality test passed!")
        
    finally:
        shutil.rmtree(temp_dir)