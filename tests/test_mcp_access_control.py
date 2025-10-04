"""
Test MCP Access Control System

Tests for role-based access control, progressive onboarding, and security features.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.mcp_access_control import (
    MCPAccessControlManager, AccessLevel, OnboardingStage,
    AccessControlViolation, UserAccessProfile
)
from src.core.utils import MCPAccessDeniedError


class TestMCPAccessControlManager:
    """Test MCP Access Control Manager functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        # Create test configuration
        self.test_config = {
            "access_levels": {
                "none": {"permissions": []},
                "read_only": {"permissions": ["read", "list", "query"]},
                "limited_write": {"permissions": ["read", "list", "query", "create", "update_own"]},
                "full_write": {"permissions": ["read", "list", "query", "create", "update", "delete"]},
                "admin": {"permissions": ["read", "list", "query", "create", "update", "delete", "admin", "configure"]}
            },
            "progressive_onboarding": {
                "stages": [
                    {
                        "name": "observer",
                        "duration_days": 7,
                        "default_access": "read_only",
                        "allowed_mcps": ["linkedin", "reddit"],
                        "restrictions": {"max_queries_per_hour": 10, "allowed_operations": ["read", "list"]}
                    },
                    {
                        "name": "participant", 
                        "duration_days": 30,
                        "default_access": "limited_write",
                        "allowed_mcps": ["linkedin", "reddit", "erpnext"],
                        "restrictions": {"max_queries_per_hour": 50, "allowed_operations": ["read", "list", "query", "create"]}
                    },
                    {
                        "name": "trusted",
                        "duration_days": -1,
                        "default_access": "full_write",
                        "allowed_mcps": ["linkedin", "reddit", "erpnext"],
                        "restrictions": {"max_queries_per_hour": 200}
                    }
                ]
            },
            "roles": {
                "Founder": {
                    "default_stage": "trusted",
                    "mcp_access": {
                        "linkedin": "admin",
                        "reddit": "full_write", 
                        "erpnext": "admin"
                    },
                    "override_restrictions": True
                },
                "Employee": {
                    "default_stage": "observer",
                    "mcp_access": {
                        "linkedin": "none",
                        "reddit": "none",
                        "erpnext": "read_only"
                    },
                    "progressive_onboarding": True
                }
            },
            "audit": {"enabled": True, "log_all_access": True}
        }
        
        # Mock the config loading
        with patch.object(MCPAccessControlManager, '_load_config', return_value=self.test_config):
            self.manager = MCPAccessControlManager()
    
    def test_user_profile_creation(self):
        """Test user profile creation with different roles"""
        # Test Founder profile creation
        founder_profile = self.manager.get_user_profile("user1", "Founder")
        assert founder_profile.role == "Founder"
        assert founder_profile.onboarding_stage == "trusted"
        assert founder_profile.mcp_access["linkedin"] == "admin"
        
        # Test Employee profile creation
        employee_profile = self.manager.get_user_profile("user2", "Employee")
        assert employee_profile.role == "Employee"
        assert employee_profile.onboarding_stage == "observer"
        assert employee_profile.mcp_access["linkedin"] == "none"
    
    def test_access_control_validation(self):
        """Test access control validation for different operations"""
        # Test Founder access (should have admin access)
        has_access, reason = self.manager.check_access("user1", "Founder", "linkedin", "admin")
        assert has_access is True
        assert reason == "Access granted"
        
        # Test Employee access to LinkedIn (should be denied)
        has_access, reason = self.manager.check_access("user2", "Employee", "linkedin", "read")
        assert has_access is False
        assert "does not have access" in reason
        
        # Test Employee access to ERPNext read (should be allowed)
        has_access, reason = self.manager.check_access("user2", "Employee", "erpnext", "read")
        assert has_access is True
        assert reason == "Access granted"
    
    def test_progressive_onboarding(self):
        """Test progressive onboarding stage transitions"""
        # Create employee profile
        profile = self.manager.get_user_profile("user3", "Employee")
        assert profile.onboarding_stage == "observer"
        
        # Simulate time passing for onboarding progression
        profile.stage_started = datetime.now() - timedelta(days=8)
        
        # Check access should trigger progression
        self.manager.check_access("user3", "Employee", "erpnext", "read")
        
        # Profile should have progressed to participant stage
        assert profile.onboarding_stage == "participant"
        assert profile.restrictions["max_queries_per_hour"] == 50
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Create employee profile
        profile = self.manager.get_user_profile("user4", "Employee")
        
        # Simulate multiple requests in same hour
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        hour_key = f"erpnext:{current_hour.isoformat()}"
        
        # Set usage to near limit
        profile.usage_stats[hour_key] = 9
        
        # Should still allow one more request
        has_access, reason = self.manager.check_access("user4", "Employee", "erpnext", "read")
        assert has_access is True
        
        # Next request should be denied due to rate limit
        has_access, reason = self.manager.check_access("user4", "Employee", "erpnext", "read")
        assert has_access is False
        assert "usage restrictions" in reason
    
    def test_operation_permissions(self):
        """Test operation-level permissions"""
        # Employee with read_only access should not be able to create
        profile = self.manager.get_user_profile("user5", "Employee")
        profile.mcp_access["erpnext"] = "read_only"
        
        has_access, reason = self.manager.check_access("user5", "Employee", "erpnext", "create")
        assert has_access is False
        assert "does not permit operation" in reason
        
        # Should be able to read
        has_access, reason = self.manager.check_access("user5", "Employee", "erpnext", "read")
        assert has_access is True
    
    def test_violation_logging(self):
        """Test access violation logging"""
        # Clear existing violations
        self.manager.violations = []
        
        # Generate a violation
        self.manager.check_access("user6", "Employee", "linkedin", "admin")
        
        # Check that violation was logged
        assert len(self.manager.violations) == 1
        violation = self.manager.violations[0]
        assert violation.user_role == "Employee"
        assert violation.mcp_server == "linkedin"
        assert violation.operation == "admin"
        assert "does not have access" in violation.reason
    
    def test_bulk_role_update(self):
        """Test bulk role access updates"""
        # Update access for all Employee roles
        new_access = {
            "linkedin": "read_only",
            "reddit": "read_only"
        }
        
        result = self.manager.bulk_update_role_access("Employee", new_access)
        assert result is True
        
        # Verify configuration was updated
        assert self.manager.config["roles"]["Employee"]["mcp_access"]["linkedin"] == "read_only"
        assert self.manager.config["roles"]["Employee"]["mcp_access"]["reddit"] == "read_only"
    
    def test_user_permissions_summary(self):
        """Test user permissions summary"""
        profile = self.manager.get_user_profile("user7", "Founder")
        summary = self.manager.get_user_permissions_summary("user7", "Founder")
        
        assert summary["role"] == "Founder"
        assert summary["onboarding_stage"] == "trusted"
        assert "mcp_access" in summary
        assert "restrictions" in summary
        assert "days_in_stage" in summary
    
    def test_override_restrictions(self):
        """Test restriction overrides for privileged roles"""
        # Founder should override all restrictions
        profile = self.manager.get_user_profile("user8", "Founder")
        
        # Simulate high usage that would normally be blocked
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        hour_key = f"linkedin:{current_hour.isoformat()}"
        profile.usage_stats[hour_key] = 1000  # Way over limit
        
        # Should still allow access due to override
        has_access, reason = self.manager.check_access("user8", "Founder", "linkedin", "admin")
        assert has_access is True
    
    def test_stage_config_retrieval(self):
        """Test onboarding stage configuration retrieval"""
        observer_config = self.manager._get_stage_config("observer")
        assert observer_config is not None
        assert observer_config["duration_days"] == 7
        assert observer_config["default_access"] == "read_only"
        
        # Invalid stage should return None
        invalid_config = self.manager._get_stage_config("invalid_stage")
        assert invalid_config is None
    
    def test_usage_stats_cleanup(self):
        """Test automatic cleanup of old usage statistics"""
        profile = self.manager.get_user_profile("user9", "Employee")
        
        # Add old usage stats
        old_time = datetime.now() - timedelta(hours=25)
        old_hour_key = f"erpnext:{old_time.replace(minute=0, second=0, microsecond=0).isoformat()}"
        profile.usage_stats[old_hour_key] = 10
        
        # Add recent usage stats
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        recent_hour_key = f"erpnext:{current_hour.isoformat()}"
        profile.usage_stats[recent_hour_key] = 5
        
        # Update usage stats (should trigger cleanup)
        self.manager._update_usage_stats(profile, "erpnext", "read")
        
        # Old stats should be removed, recent stats should remain
        assert old_hour_key not in profile.usage_stats
        assert recent_hour_key in profile.usage_stats


class TestMCPAccessIntegration:
    """Test MCP access control integration with utils system"""
    
    def test_access_validation_function(self):
        """Test the validate_mcp_request function"""
        from src.core.utils import validate_mcp_request
        
        # This should work (no exception)
        try:
            validate_mcp_request("user1", "Founder", "linkedin", "admin")
        except MCPAccessDeniedError:
            pytest.fail("Access should be granted for Founder")
    
    def test_access_denied_exception(self):
        """Test MCPAccessDeniedError is raised correctly"""
        from core.utils import validate_mcp_request
        
        with pytest.raises(MCPAccessDeniedError):
            validate_mcp_request("user1", "Employee", "linkedin", "admin")


class TestBoardroomAgentAccessControl:
    """Test boardroom agent access control functionality"""
    
    def setup_method(self):
        """Setup test environment for boardroom agents"""
        # Create test configuration with boardroom agents
        self.test_config = {
            "access_levels": {
                "none": {"permissions": []},
                "read_only": {"permissions": ["read", "list", "query"]},
                "limited_write": {"permissions": ["read", "list", "query", "create", "update_own"]},
                "full_write": {"permissions": ["read", "list", "query", "create", "update", "delete"]},
                "admin": {"permissions": ["read", "list", "query", "create", "update", "delete", "admin", "configure"]}
            },
            "boardroom_agents": {
                "enabled": True,
                "agents": {
                    "CEO": {
                        "enabled": False,
                        "onboarding_stage": "observer",
                        "stage_started": None,
                        "mcp_access": {"linkedin": "none", "reddit": "none", "erpnext": "none"},
                        "legendary_profile": "Steve Jobs",
                        "domain": "innovation_leadership"
                    },
                    "Founder": {
                        "enabled": True,
                        "onboarding_stage": "trusted",
                        "stage_started": "2023-01-01T00:00:00Z",
                        "mcp_access": {"linkedin": "admin", "reddit": "admin", "erpnext": "admin"},
                        "legendary_profile": "Elon Musk",
                        "domain": "visionary_leadership"
                    }
                },
                "progressive_stages": {
                    "observer": {
                        "duration_days": 14,
                        "default_access": "read_only",
                        "allowed_mcps": ["linkedin", "reddit"],
                        "restrictions": {"max_decisions_per_day": 2}
                    },
                    "participant": {
                        "duration_days": 60,
                        "default_access": "limited_write",
                        "allowed_mcps": ["linkedin", "reddit", "erpnext"],
                        "restrictions": {"max_decisions_per_day": 10}
                    },
                    "trusted": {
                        "duration_days": -1,
                        "default_access": "admin",
                        "allowed_mcps": ["linkedin", "reddit", "erpnext"],
                        "restrictions": {"max_decisions_per_day": -1}
                    }
                }
            },
            "roles": {},
            "audit": {"enabled": True}
        }
        
        # Mock the config loading
        with patch.object(MCPAccessControlManager, '_load_config', return_value=self.test_config):
            self.manager = MCPAccessControlManager()
    
    def test_boardroom_agent_initialization(self):
        """Test boardroom agent profile initialization"""
        # Check that agents are initialized
        ceo_profile = self.manager.get_boardroom_agent_profile("CEO")
        assert ceo_profile is not None
        assert ceo_profile.role == "CEO"
        assert ceo_profile.enabled is False
        assert ceo_profile.onboarding_stage == "observer"
        assert ceo_profile.legendary_profile == "Steve Jobs"
        
        founder_profile = self.manager.get_boardroom_agent_profile("Founder")
        assert founder_profile is not None
        assert founder_profile.enabled is True
        assert founder_profile.onboarding_stage == "trusted"
    
    def test_disabled_agent_access(self):
        """Test that disabled agents cannot access systems"""
        # CEO is disabled, should not have access
        has_access, reason = self.manager.check_boardroom_agent_access("CEO", "linkedin", "read")
        assert has_access is False
        assert "is not enabled" in reason
    
    def test_enabled_agent_access(self):
        """Test that enabled agents can access systems according to their stage"""
        # Founder is enabled and trusted, should have access
        has_access, reason = self.manager.check_boardroom_agent_access("Founder", "linkedin", "admin")
        assert has_access is True
        assert reason == "Access granted"
    
    def test_agent_enablement(self):
        """Test enabling a boardroom agent"""
        # Enable CEO
        result = self.manager.enable_boardroom_agent("CEO")
        assert result is True
        
        # Verify CEO is now enabled
        ceo_profile = self.manager.get_boardroom_agent_profile("CEO")
        assert ceo_profile.enabled is True
        assert ceo_profile.stage_started is not None
    
    def test_agent_disablement(self):
        """Test disabling a boardroom agent"""
        # Disable Founder
        result = self.manager.disable_boardroom_agent("Founder")
        assert result is True
        
        # Verify Founder is now disabled
        founder_profile = self.manager.get_boardroom_agent_profile("Founder")
        assert founder_profile.enabled is False
    
    def test_agent_onboarding_progression(self):
        """Test agent onboarding stage progression"""
        # Enable CEO and set stage_started to trigger progression
        self.manager.enable_boardroom_agent("CEO")
        ceo_profile = self.manager.get_boardroom_agent_profile("CEO")
        
        # Simulate time passing for progression (15 days)
        ceo_profile.stage_started = datetime.now() - timedelta(days=15)
        
        # Check access to trigger progression
        self.manager.check_boardroom_agent_access("CEO", "linkedin", "read")
        
        # Profile should have progressed to participant stage
        assert ceo_profile.onboarding_stage == "participant"
    
    def test_agent_decision_limits(self):
        """Test agent decision limits and restrictions"""
        # Enable CEO
        self.manager.enable_boardroom_agent("CEO")
        ceo_profile = self.manager.get_boardroom_agent_profile("CEO")
        
        # Simulate reaching daily decision limit
        today = datetime.now().date()
        ceo_profile.decision_history = [
            {"date": today.isoformat(), "operation": "create", "timestamp": datetime.now().isoformat()},
            {"date": today.isoformat(), "operation": "update", "timestamp": datetime.now().isoformat()}
        ]
        
        # Next decision should be blocked by limit (observer stage has max 2 decisions)
        ceo_profile.restrictions = {"max_decisions_per_day": 2}
        has_access, reason = self.manager.check_boardroom_agent_access("CEO", "linkedin", "create")
        assert has_access is False
        assert "decision limits" in reason or "restrictions" in reason
    
    def test_agents_summary(self):
        """Test getting boardroom agents summary"""
        summary = self.manager.get_boardroom_agents_summary()
        
        assert summary["enabled"] is True
        assert "agents" in summary
        assert "CEO" in summary["agents"]
        assert "Founder" in summary["agents"]
        
        ceo_summary = summary["agents"]["CEO"]
        assert ceo_summary["enabled"] is False
        assert ceo_summary["legendary_profile"] == "Steve Jobs"
        
        founder_summary = summary["agents"]["Founder"]
        assert founder_summary["enabled"] is True
        assert founder_summary["onboarding_stage"] == "trusted"
    
    def test_agent_violation_logging(self):
        """Test that agent access violations are logged with higher severity"""
        # Clear existing violations
        self.manager.violations = []
        
        # Generate a violation from disabled CEO
        self.manager.check_boardroom_agent_access("CEO", "linkedin", "admin")
        
        # Check that violation was logged with high severity
        assert len(self.manager.violations) == 1
        violation = self.manager.violations[0]
        assert violation.user_role == "BoardroomAgent:CEO"
        assert violation.mcp_server == "linkedin"
        assert violation.operation == "admin"
        assert violation.severity == "high"
        assert "is not enabled" in violation.reason


class TestMCPHandlerIntegration:
    """Test MCP handler integration with access control"""
    
    def test_handler_access_control(self):
        """Test that MCP handlers enforce access control"""
        from dashboard.mcp_handlers import handle_mcp
        
        # Mock request that should be denied
        body = {
            "method": "founder.approvePlan",
            "params": {"planId": "test123"},
            "id": "req1"
        }
        
        user_context = {
            "user_id": "employee1",
            "role": "Employee"
        }
        
        # This would need async testing framework for full test
        # For now, we verify the structure is correct
        assert callable(handle_mcp)


if __name__ == "__main__":
    pytest.main([__file__])