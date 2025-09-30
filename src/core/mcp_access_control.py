"""
MCP Access Control Manager

Manages role-based access control for MCP servers, including progressive onboarding
and configurable permissions. Integrates with the existing BusinessInfinity role system.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Import audit trail system
from .audit_trail import (
    AuditTrailManager, AuditEventType, AuditSeverity, 
    audit_log, get_audit_manager
)


class AccessLevel(Enum):
    """MCP access levels"""
    NONE = "none"
    READ_ONLY = "read_only"
    LIMITED_WRITE = "limited_write"
    FULL_WRITE = "full_write"
    ADMIN = "admin"


class OnboardingStage(Enum):
    """Progressive onboarding stages"""
    OBSERVER = "observer"
    PARTICIPANT = "participant"
    TRUSTED = "trusted"


@dataclass
class AccessControlViolation:
    """Represents an access control violation"""
    user_role: str
    mcp_server: str
    operation: str
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)
    severity: str = "medium"


@dataclass
class BoardroomAgentProfile:
    """Represents a Boardroom Agent's access profile and onboarding status"""
    agent_id: str
    role: str
    enabled: bool
    onboarding_stage: str
    stage_started: Optional[datetime]
    mcp_access: Dict[str, str] = field(default_factory=dict)
    legendary_profile: str = ""
    domain: str = ""
    assigned_purpose: str = ""
    restrictions: Dict[str, Any] = field(default_factory=dict)
    decision_history: List[Dict[str, Any]] = field(default_factory=list)
    last_activity: Optional[datetime] = None


@dataclass
class UserAccessProfile:
    """Represents a user's access profile and permissions"""
    role: str
    onboarding_stage: str
    stage_started: datetime
    mcp_access: Dict[str, str] = field(default_factory=dict)
    restrictions: Dict[str, Any] = field(default_factory=dict)
    usage_stats: Dict[str, int] = field(default_factory=dict)
    last_activity: Optional[datetime] = None


class MCPAccessControlManager:
    """
    Manages MCP access control with role-based permissions and progressive onboarding
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or str(Path(__file__).parent.parent / "config" / "mcp_access_control.json")
        self.config = self._load_config()
        self.user_profiles: Dict[str, UserAccessProfile] = {}
        self.boardroom_agent_profiles: Dict[str, BoardroomAgentProfile] = {}
        self.violations: List[AccessControlViolation] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize audit trail manager
        self.audit_manager = get_audit_manager()
        
        # Log system initialization
        self.audit_manager.log_event(
            event_type=AuditEventType.SYSTEM_STARTUP,
            subject_id="mcp_access_control",
            subject_type="system",
            action="MCP Access Control Manager initialized",
            context={"config_path": self.config_path},
            compliance_tags={"access_control", "system_lifecycle"}
        )
        
        # Initialize boardroom agent profiles from config
        self._initialize_boardroom_agents()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load access control configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Access control config not found: {self.config_path}")
            return self._default_config()
        except Exception as e:
            self.logger.error(f"Error loading access control config: {e}")
            return self._default_config()
    
    def _initialize_boardroom_agents(self):
        """Initialize boardroom agent profiles from configuration"""
        try:
            boardroom_config = self.config.get("boardroom_agents", {})
            if not boardroom_config.get("enabled", False):
                self.logger.info("Boardroom agent onboarding is disabled")
                return
            
            agents_config = boardroom_config.get("agents", {})
            
            for agent_role, agent_config in agents_config.items():
                stage_started = None
                if agent_config.get("stage_started"):
                    stage_started_str = agent_config["stage_started"].replace('Z', '+00:00')
                    stage_started = datetime.fromisoformat(stage_started_str).replace(tzinfo=None)
                
                # Get stage restrictions
                stage_config = self._get_boardroom_agent_stage_config(agent_config.get("onboarding_stage", "observer"))
                restrictions = stage_config.get("restrictions", {}) if stage_config else {}
                
                profile = BoardroomAgentProfile(
                    agent_id=f"boardroom_{agent_role.lower()}",
                    role=agent_role,
                    enabled=agent_config.get("enabled", False),
                    onboarding_stage=agent_config.get("onboarding_stage", "observer"),
                    stage_started=stage_started,
                    mcp_access=agent_config.get("mcp_access", {}).copy(),
                    legendary_profile=agent_config.get("legendary_profile", ""),
                    domain=agent_config.get("domain", ""),
                    assigned_purpose=agent_config.get("assigned_purpose", ""),
                    restrictions=restrictions.copy()
                )
                
                self.boardroom_agent_profiles[agent_role] = profile
                self.logger.info(f"Initialized boardroom agent profile: {agent_role} (enabled: {profile.enabled})")
                
        except Exception as e:
            self.logger.error(f"Error initializing boardroom agents: {e}")
    
    def _get_boardroom_agent_stage_config(self, stage_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for boardroom agent onboarding stage"""
        stages = self.config.get("boardroom_agents", {}).get("progressive_stages", {})
        return stages.get(stage_name)
    
    def get_boardroom_agent_profile(self, agent_role: str) -> Optional[BoardroomAgentProfile]:
        """Get boardroom agent profile by role"""
        return self.boardroom_agent_profiles.get(agent_role)
    
    def check_boardroom_agent_access(self, agent_role: str, mcp_server: str, operation: str) -> Tuple[bool, str]:
        """
        Check if boardroom agent has access to perform operation on MCP server
        
        Returns:
            Tuple[bool, str]: (has_access, reason)
        """
        profile = self.get_boardroom_agent_profile(agent_role)
        
        if not profile:
            reason = f"Boardroom agent {agent_role} not found"
            self._log_agent_violation(agent_role, mcp_server, operation, reason)
            
            # Log agent access denied event
            self.audit_manager.log_event(
                event_type=AuditEventType.ACCESS_DENIED,
                subject_id=agent_role,
                subject_type="agent",
                subject_role=agent_role,
                action=f"Agent not found for {mcp_server}.{operation}",
                mcp_server=mcp_server,
                severity=AuditSeverity.HIGH,
                context={
                    "operation": operation,
                    "reason": reason
                },
                compliance_tags={"access_control", "agent_security"}
            )
            return False, reason
        
        if not profile.enabled:
            reason = f"Boardroom agent {agent_role} is not enabled"
            self._log_agent_violation(agent_role, mcp_server, operation, reason)
            
            # Log disabled agent access attempt
            self.audit_manager.log_event(
                event_type=AuditEventType.ACCESS_DENIED,
                subject_id=profile.agent_id,
                subject_type="agent",
                subject_role=agent_role,
                action=f"Disabled agent attempted {mcp_server}.{operation}",
                mcp_server=mcp_server,
                severity=AuditSeverity.HIGH,
                context={
                    "operation": operation,
                    "reason": reason,
                    "onboarding_stage": profile.onboarding_stage
                },
                compliance_tags={"access_control", "agent_security"}
            )
            return False, reason
        
        # Update usage statistics
        self._update_agent_activity(profile, mcp_server, operation)
        
        # Check if agent has access to MCP server
        if not self._has_agent_mcp_server_access(profile, mcp_server):
            reason = f"Agent {agent_role} does not have access to MCP server {mcp_server}"
            self._log_agent_violation(agent_role, mcp_server, operation, reason)
            
            # Log agent MCP access denied
            self.audit_manager.log_event(
                event_type=AuditEventType.MCP_ACCESS_DENIED,
                subject_id=profile.agent_id,
                subject_type="agent",
                subject_role=agent_role,
                action=f"No MCP server access for {mcp_server}.{operation}",
                mcp_server=mcp_server,
                severity=AuditSeverity.MEDIUM,
                context={
                    "operation": operation,
                    "reason": reason,
                    "assigned_purpose": profile.assigned_purpose
                },
                compliance_tags={"access_control", "mcp_security"}
            )
            return False, reason
        
        # Get agent's access level for this MCP server
        access_level = self._get_agent_access_level(profile, mcp_server)
        
        # Check if operation is allowed for this access level
        if not self._is_operation_allowed(access_level, operation):
            reason = f"Access level {access_level} does not permit operation {operation}"
            self._log_agent_violation(agent_role, mcp_server, operation, reason)
            
            # Log insufficient agent permissions
            self.audit_manager.log_event(
                event_type=AuditEventType.ACCESS_DENIED,
                subject_id=profile.agent_id,
                subject_type="agent",
                subject_role=agent_role,
                action=f"Insufficient permissions for {mcp_server}.{operation}",
                mcp_server=mcp_server,
                severity=AuditSeverity.MEDIUM,
                context={
                    "operation": operation,
                    "access_level": access_level,
                    "reason": reason
                },
                compliance_tags={"access_control", "agent_permissions"}
            )
            return False, reason
        
        # Check boardroom-specific restrictions
        if not self._check_agent_restrictions(profile, mcp_server, operation):
            reason = "Operation blocked by agent restrictions or decision limits"
            self._log_agent_violation(agent_role, mcp_server, operation, reason)
            
            # Log agent restriction violation
            self.audit_manager.log_event(
                event_type=AuditEventType.ACCESS_DENIED,
                subject_id=profile.agent_id,
                subject_type="agent",
                subject_role=agent_role,
                action=f"Blocked by restrictions for {mcp_server}.{operation}",
                mcp_server=mcp_server,
                severity=AuditSeverity.HIGH,
                context={
                    "operation": operation,
                    "reason": reason,
                    "restrictions": profile.restrictions
                },
                compliance_tags={"access_control", "agent_restrictions"}
            )
            return False, reason
        
        # Check if onboarding stage progression is needed
        self._check_agent_onboarding_progression(profile)
        
        # Log successful agent access grant
        self.audit_manager.log_event(
            event_type=AuditEventType.ACCESS_GRANTED,
            subject_id=profile.agent_id,
            subject_type="agent",
            subject_role=agent_role,
            action=f"Granted agent access to {mcp_server}.{operation}",
            mcp_server=mcp_server,
            severity=AuditSeverity.LOW,
            context={
                "operation": operation,
                "access_level": access_level,
                "onboarding_stage": profile.onboarding_stage,
                "assigned_purpose": profile.assigned_purpose
            },
            compliance_tags={"access_control", "agent_access"}
        )
        
        if self.config.get("audit", {}).get("log_all_access", False):
            self.logger.info(f"Agent access granted: {agent_role} -> {mcp_server}.{operation}")
        
        return True, "Access granted"
    
    def _has_agent_mcp_server_access(self, profile: BoardroomAgentProfile, mcp_server: str) -> bool:
        """Check if agent has any access to MCP server"""
        # Check explicit access
        if mcp_server in profile.mcp_access:
            return profile.mcp_access[mcp_server] != AccessLevel.NONE.value
        
        # Check stage-based access
        stage_config = self._get_boardroom_agent_stage_config(profile.onboarding_stage)
        if stage_config:
            allowed_mcps = stage_config.get("allowed_mcps", [])
            return mcp_server in allowed_mcps
        
        return False
    
    def _get_agent_access_level(self, profile: BoardroomAgentProfile, mcp_server: str) -> str:
        """Get agent's access level for specific MCP server"""
        # Check explicit access first
        if mcp_server in profile.mcp_access:
            return profile.mcp_access[mcp_server]
        
        # Fall back to stage default access
        stage_config = self._get_boardroom_agent_stage_config(profile.onboarding_stage)
        if stage_config:
            return stage_config.get("default_access", "read_only")
        
        return "none"
    
    def _check_agent_restrictions(self, profile: BoardroomAgentProfile, mcp_server: str, operation: str) -> bool:
        """Check agent-specific restrictions"""
        # Check daily decision limits
        max_decisions = profile.restrictions.get("max_decisions_per_day", -1)
        if max_decisions > 0:
            today = datetime.now().date()
            decisions_today = sum(
                1 for decision in profile.decision_history 
                if decision.get("date") == today.isoformat()
            )
            if decisions_today >= max_decisions:
                return False
        
        # Check allowed decision types for strategic operations
        if operation in ["create", "update", "admin"]:
            allowed_types = profile.restrictions.get("allowed_decision_types", [])
            if allowed_types and "strategic" not in allowed_types:
                # For now, assume these are strategic operations
                # In real implementation, this would be context-aware
                pass
        
        return True
    
    def _update_agent_activity(self, profile: BoardroomAgentProfile, mcp_server: str, operation: str):
        """Update agent activity tracking"""
        profile.last_activity = datetime.now()
        
        # Log decision if it's a significant operation
        if operation in ["create", "update", "delete", "admin"]:
            today = datetime.now().date()
            profile.decision_history.append({
                "date": today.isoformat(),
                "mcp_server": mcp_server,
                "operation": operation,
                "timestamp": datetime.now().isoformat()
            })
            
            # Clean up old decision history (keep only last 30 days)
            cutoff_date = (datetime.now() - timedelta(days=30)).date()
            profile.decision_history = [
                d for d in profile.decision_history
                if datetime.fromisoformat(d["date"]).date() >= cutoff_date
            ]
    
    def _check_agent_onboarding_progression(self, profile: BoardroomAgentProfile):
        """Check if agent should progress to next onboarding stage"""
        if not profile.stage_started:
            return
        
        current_stage_config = self._get_boardroom_agent_stage_config(profile.onboarding_stage)
        if not current_stage_config:
            return
        
        duration_days = current_stage_config.get("duration_days", -1)
        if duration_days <= 0:  # Permanent stage
            return
        
        days_in_stage = (datetime.now() - profile.stage_started).days
        if days_in_stage >= duration_days:
            self._progress_agent_to_next_stage(profile)
    
    def _progress_agent_to_next_stage(self, profile: BoardroomAgentProfile):
        """Progress agent to next onboarding stage"""
        stages = ["observer", "participant", "trusted"]
        current_idx = stages.index(profile.onboarding_stage) if profile.onboarding_stage in stages else -1
        
        if current_idx >= 0 and current_idx < len(stages) - 1:
            next_stage = stages[current_idx + 1]
            profile.onboarding_stage = next_stage
            profile.stage_started = datetime.now()
            
            # Update restrictions
            stage_config = self._get_boardroom_agent_stage_config(next_stage)
            if stage_config:
                profile.restrictions = stage_config.get("restrictions", {}).copy()
            
            self.logger.info(f"Boardroom agent {profile.role} progressed to stage: {next_stage}")
            
            # Update config file
            self._update_agent_stage_in_config(profile.role, next_stage)
    
    def _update_agent_stage_in_config(self, agent_role: str, new_stage: str):
        """Update agent's stage in configuration file"""
        try:
            if "boardroom_agents" in self.config and "agents" in self.config["boardroom_agents"]:
                if agent_role in self.config["boardroom_agents"]["agents"]:
                    self.config["boardroom_agents"]["agents"][agent_role]["onboarding_stage"] = new_stage
                    self.config["boardroom_agents"]["agents"][agent_role]["stage_started"] = datetime.now().isoformat()
        except Exception as e:
            self.logger.error(f"Error updating agent stage in config: {e}")
    
    def _log_agent_violation(self, agent_role: str, mcp_server: str, operation: str, reason: str):
        """Log access control violation for boardroom agent"""
        violation = AccessControlViolation(
            user_role=f"BoardroomAgent:{agent_role}",
            mcp_server=mcp_server,
            operation=operation,
            reason=reason,
            severity="high"  # Agent violations are more serious
        )
        self.violations.append(violation)
        
        if self.config.get("audit", {}).get("log_denied_access", True):
            self.logger.warning(f"Agent access denied: {agent_role} -> {mcp_server}.{operation} - {reason}")
    
    def enable_boardroom_agent(self, agent_role: str) -> bool:
        """Enable a boardroom agent for onboarding"""
        profile = self.get_boardroom_agent_profile(agent_role)
        if not profile:
            return False
        
        if not profile.enabled:
            profile.enabled = True
            profile.stage_started = datetime.now()
            self.logger.info(f"Enabled boardroom agent: {agent_role}")
            
            # Update config
            try:
                if "boardroom_agents" in self.config and "agents" in self.config["boardroom_agents"]:
                    if agent_role in self.config["boardroom_agents"]["agents"]:
                        self.config["boardroom_agents"]["agents"][agent_role]["enabled"] = True
                        self.config["boardroom_agents"]["agents"][agent_role]["stage_started"] = datetime.now().isoformat()
            except Exception as e:
                self.logger.error(f"Error updating agent config: {e}")
        
        return True
    
    def disable_boardroom_agent(self, agent_role: str) -> bool:
        """Disable a boardroom agent"""
        profile = self.get_boardroom_agent_profile(agent_role)
        if not profile:
            return False
        
        profile.enabled = False
        self.logger.info(f"Disabled boardroom agent: {agent_role}")
        
        # Update config
        try:
            if "boardroom_agents" in self.config and "agents" in self.config["boardroom_agents"]:
                if agent_role in self.config["boardroom_agents"]["agents"]:
                    self.config["boardroom_agents"]["agents"][agent_role]["enabled"] = False
        except Exception as e:
            self.logger.error(f"Error updating agent config: {e}")
        
        return True
    
    def get_boardroom_agents_summary(self) -> Dict[str, Any]:
        """Get summary of all boardroom agents and their status"""
        summary = {
            "enabled": self.config.get("boardroom_agents", {}).get("enabled", False),
            "agents": {}
        }
        
        for agent_role, profile in self.boardroom_agent_profiles.items():
            days_in_stage = 0
            if profile.stage_started:
                days_in_stage = (datetime.now() - profile.stage_started).days
            
            summary["agents"][agent_role] = {
                "enabled": profile.enabled,
                "onboarding_stage": profile.onboarding_stage,
                "days_in_stage": days_in_stage,
                "legendary_profile": profile.legendary_profile,
                "domain": profile.domain,
                "mcp_access": profile.mcp_access,
                "restrictions": profile.restrictions,
                "recent_decisions": len([
                    d for d in profile.decision_history 
                    if (datetime.now() - datetime.fromisoformat(d["timestamp"])).days <= 7
                ]),
                "last_activity": profile.last_activity.isoformat() if profile.last_activity else None
            }
        
        return summary
        """Return default configuration if config file is not available"""
        return {
            "access_levels": {
                "none": {"permissions": []},
                "read_only": {"permissions": ["read", "list", "query"]},
                "limited_write": {"permissions": ["read", "list", "query", "create", "update_own"]},
                "full_write": {"permissions": ["read", "list", "query", "create", "update", "delete"]},
                "admin": {"permissions": ["read", "list", "query", "create", "update", "delete", "admin", "configure"]}
            },
            "roles": {
                "Founder": {"default_stage": "trusted", "mcp_access": {}, "override_restrictions": True},
                "Employee": {"default_stage": "observer", "mcp_access": {}, "progressive_onboarding": True}
            },
            "progressive_onboarding": {"stages": []},
            "mcp_servers": {},
            "audit": {"enabled": True, "log_all_access": True}
        }
    
    def get_user_profile(self, user_id: str, role: str) -> UserAccessProfile:
        """Get or create user access profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = self._create_user_profile(user_id, role)
        
        # Update role if changed
        if self.user_profiles[user_id].role != role:
            self.user_profiles[user_id] = self._update_user_role(user_id, role)
        
        return self.user_profiles[user_id]
    
    def _create_user_profile(self, user_id: str, role: str) -> UserAccessProfile:
        """Create new user access profile based on role"""
        role_config = self.config.get("roles", {}).get(role, {})
        default_stage = role_config.get("default_stage", "observer")
        
        # Get stage configuration
        stage_config = self._get_stage_config(default_stage)
        
        profile = UserAccessProfile(
            role=role,
            onboarding_stage=default_stage,
            stage_started=datetime.now(),
            mcp_access=role_config.get("mcp_access", {}).copy(),
            restrictions=stage_config.get("restrictions", {}).copy() if stage_config else {}
        )
        
        self.logger.info(f"Created access profile for user {user_id} with role {role}, stage {default_stage}")
        return profile
    
    def _update_user_role(self, user_id: str, new_role: str) -> UserAccessProfile:
        """Update user's role and access profile"""
        existing_profile = self.user_profiles[user_id]
        role_config = self.config.get("roles", {}).get(new_role, {})
        
        # Preserve onboarding progress if applicable
        if not role_config.get("progressive_onboarding", False):
            default_stage = role_config.get("default_stage", "trusted")
            stage_started = datetime.now()
        else:
            default_stage = existing_profile.onboarding_stage
            stage_started = existing_profile.stage_started
        
        existing_profile.role = new_role
        existing_profile.onboarding_stage = default_stage
        existing_profile.stage_started = stage_started
        existing_profile.mcp_access = role_config.get("mcp_access", {}).copy()
        
        stage_config = self._get_stage_config(default_stage)
        existing_profile.restrictions = stage_config.get("restrictions", {}).copy() if stage_config else {}
        
        self.logger.info(f"Updated role for user {user_id} to {new_role}")
        return existing_profile
    
    def _get_stage_config(self, stage_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for onboarding stage"""
        stages = self.config.get("progressive_onboarding", {}).get("stages", [])
        return next((s for s in stages if s.get("name") == stage_name), None)
    
    def check_access(self, user_id: str, role: str, mcp_server: str, operation: str) -> Tuple[bool, str]:
        """
        Check if user has access to perform operation on MCP server
        
        Returns:
            Tuple[bool, str]: (has_access, reason)
        """
        profile = self.get_user_profile(user_id, role)
        
        # Update usage statistics
        self._update_usage_stats(profile, mcp_server, operation)
        
        # Check if user has access to MCP server
        if not self._has_mcp_server_access(profile, mcp_server):
            reason = f"Role {role} does not have access to MCP server {mcp_server}"
            self._log_violation(role, mcp_server, operation, reason)
            
            # Log access denied event
            self.audit_manager.log_event(
                event_type=AuditEventType.ACCESS_DENIED,
                subject_id=user_id,
                subject_type="user",
                subject_role=role,
                action=f"Access denied to {mcp_server}.{operation}",
                mcp_server=mcp_server,
                severity=AuditSeverity.MEDIUM,
                context={
                    "operation": operation,
                    "reason": reason,
                    "onboarding_stage": profile.onboarding_stage
                },
                compliance_tags={"access_control", "security"}
            )
            return False, reason
        
        # Get user's access level for this MCP server
        access_level = self._get_user_access_level(profile, mcp_server)
        
        # Check if operation is allowed for this access level
        if not self._is_operation_allowed(access_level, operation):
            reason = f"Access level {access_level} does not permit operation {operation}"
            self._log_violation(role, mcp_server, operation, reason)
            
            # Log access denied event
            self.audit_manager.log_event(
                event_type=AuditEventType.ACCESS_DENIED,
                subject_id=user_id,
                subject_type="user",
                subject_role=role,
                action=f"Insufficient permissions for {mcp_server}.{operation}",
                mcp_server=mcp_server,
                severity=AuditSeverity.MEDIUM,
                context={
                    "operation": operation,
                    "access_level": access_level,
                    "reason": reason
                },
                compliance_tags={"access_control", "security"}
            )
            return False, reason
        
        # Check rate limiting and restrictions
        if not self._check_restrictions(profile, mcp_server, operation):
            reason = "Operation blocked by usage restrictions or rate limiting"
            self._log_violation(role, mcp_server, operation, reason)
            
            # Log access denied event
            self.audit_manager.log_event(
                event_type=AuditEventType.ACCESS_DENIED,
                subject_id=user_id,
                subject_type="user",
                subject_role=role,
                action=f"Rate limited access to {mcp_server}.{operation}",
                mcp_server=mcp_server,
                severity=AuditSeverity.HIGH,
                context={
                    "operation": operation,
                    "reason": reason,
                    "usage_stats": profile.usage_stats
                },
                compliance_tags={"access_control", "rate_limiting"}
            )
            return False, reason
        
        # Check if onboarding stage progression is needed
        self._check_onboarding_progression(profile)
        
        # Log successful access grant
        self.audit_manager.log_event(
            event_type=AuditEventType.ACCESS_GRANTED,
            subject_id=user_id,
            subject_type="user",
            subject_role=role,
            action=f"Granted access to {mcp_server}.{operation}",
            mcp_server=mcp_server,
            severity=AuditSeverity.LOW,
            context={
                "operation": operation,
                "access_level": access_level,
                "onboarding_stage": profile.onboarding_stage
            },
            compliance_tags={"access_control", "data_access"}
        )
        
        if self.config.get("audit", {}).get("log_all_access", False):
            self.logger.info(f"Access granted: user {user_id} ({role}) -> {mcp_server}.{operation}")
        
        return True, "Access granted"
    
    def _has_mcp_server_access(self, profile: UserAccessProfile, mcp_server: str) -> bool:
        """Check if user has any access to MCP server"""
        # Check explicit role-based access
        if mcp_server in profile.mcp_access:
            return profile.mcp_access[mcp_server] != AccessLevel.NONE.value
        
        # Check stage-based access
        stage_config = self._get_stage_config(profile.onboarding_stage)
        if stage_config:
            allowed_mcps = stage_config.get("allowed_mcps", [])
            return mcp_server in allowed_mcps
        
        return False
    
    def _get_user_access_level(self, profile: UserAccessProfile, mcp_server: str) -> str:
        """Get user's access level for specific MCP server"""
        # Check explicit role-based access first
        if mcp_server in profile.mcp_access:
            return profile.mcp_access[mcp_server]
        
        # Fall back to stage default access
        stage_config = self._get_stage_config(profile.onboarding_stage)
        if stage_config:
            return stage_config.get("default_access", "read_only")
        
        return "none"
    
    def _is_operation_allowed(self, access_level: str, operation: str) -> bool:
        """Check if operation is allowed for access level"""
        level_config = self.config.get("access_levels", {}).get(access_level, {})
        allowed_permissions = level_config.get("permissions", [])
        return operation in allowed_permissions
    
    def _check_restrictions(self, profile: UserAccessProfile, mcp_server: str, operation: str) -> bool:
        """Check usage restrictions and rate limiting"""
        role_config = self.config.get("roles", {}).get(profile.role, {})
        
        # Check if user can override restrictions
        if role_config.get("override_restrictions", False):
            return True
        
        # Check hourly rate limits
        max_queries = profile.restrictions.get("max_queries_per_hour", float('inf'))
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        hour_key = f"{mcp_server}:{current_hour.isoformat()}"
        
        current_usage = profile.usage_stats.get(hour_key, 0)
        if current_usage >= max_queries:
            return False
        
        # Check allowed operations
        allowed_ops = profile.restrictions.get("allowed_operations", [])
        if allowed_ops and operation not in allowed_ops:
            return False
        
        return True
    
    def _update_usage_stats(self, profile: UserAccessProfile, mcp_server: str, operation: str):
        """Update usage statistics for rate limiting"""
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        hour_key = f"{mcp_server}:{current_hour.isoformat()}"
        
        profile.usage_stats[hour_key] = profile.usage_stats.get(hour_key, 0) + 1
        profile.last_activity = datetime.now()
        
        # Clean up old usage stats (keep only last 24 hours)
        cutoff_time = current_hour - timedelta(hours=24)
        profile.usage_stats = {
            k: v for k, v in profile.usage_stats.items()
            if datetime.fromisoformat(k.split(":", 1)[1]) >= cutoff_time
        }
    
    def _check_onboarding_progression(self, profile: UserAccessProfile):
        """Check if user should progress to next onboarding stage"""
        role_config = self.config.get("roles", {}).get(profile.role, {})
        if not role_config.get("progressive_onboarding", False):
            return
        
        current_stage_config = self._get_stage_config(profile.onboarding_stage)
        if not current_stage_config:
            return
        
        duration_days = current_stage_config.get("duration_days", -1)
        if duration_days <= 0:  # Permanent stage
            return
        
        days_in_stage = (datetime.now() - profile.stage_started).days
        if days_in_stage >= duration_days:
            self._progress_to_next_stage(profile)
    
    def _progress_to_next_stage(self, profile: UserAccessProfile):
        """Progress user to next onboarding stage"""
        stages = self.config.get("progressive_onboarding", {}).get("stages", [])
        current_idx = next((i for i, s in enumerate(stages) if s.get("name") == profile.onboarding_stage), -1)
        
        if current_idx >= 0 and current_idx < len(stages) - 1:
            next_stage = stages[current_idx + 1]
            profile.onboarding_stage = next_stage["name"]
            profile.stage_started = datetime.now()
            profile.restrictions = next_stage.get("restrictions", {}).copy()
            
            self.logger.info(f"User {profile.role} progressed to onboarding stage: {next_stage['name']}")
    
    def _log_violation(self, role: str, mcp_server: str, operation: str, reason: str):
        """Log access control violation"""
        violation = AccessControlViolation(
            user_role=role,
            mcp_server=mcp_server,
            operation=operation,
            reason=reason
        )
        self.violations.append(violation)
        
        if self.config.get("audit", {}).get("log_denied_access", True):
            self.logger.warning(f"Access denied: {role} -> {mcp_server}.{operation} - {reason}")
    
    def get_user_permissions_summary(self, user_id: str, role: str) -> Dict[str, Any]:
        """Get summary of user's current permissions"""
        profile = self.get_user_profile(user_id, role)
        
        return {
            "user_id": user_id,
            "role": role,
            "onboarding_stage": profile.onboarding_stage,
            "stage_started": profile.stage_started.isoformat(),
            "days_in_stage": (datetime.now() - profile.stage_started).days,
            "mcp_access": profile.mcp_access,
            "restrictions": profile.restrictions,
            "recent_usage": {
                k: v for k, v in profile.usage_stats.items()
                if datetime.fromisoformat(k.split(":", 1)[1]) >= datetime.now() - timedelta(hours=24)
            },
            "last_activity": profile.last_activity.isoformat() if profile.last_activity else None
        }
    
    def get_access_violations(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent access violations"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_violations = [v for v in self.violations if v.timestamp >= cutoff]
        
        return [
            {
                "user_role": v.user_role,
                "mcp_server": v.mcp_server,
                "operation": v.operation,
                "reason": v.reason,
                "timestamp": v.timestamp.isoformat(),
                "severity": v.severity
            }
            for v in recent_violations
        ]
    
    def update_user_access(self, user_id: str, mcp_server: str, access_level: str) -> bool:
        """Update user's access level for specific MCP server"""
        if user_id not in self.user_profiles:
            self.logger.error(f"User profile not found: {user_id}")
            return False
        
        if access_level not in self.config.get("access_levels", {}):
            self.logger.error(f"Invalid access level: {access_level}")
            return False
        
        profile = self.user_profiles[user_id]
        profile.mcp_access[mcp_server] = access_level
        
        self.logger.info(f"Updated access for user {user_id}: {mcp_server} -> {access_level}")
        return True
    
    def bulk_update_role_access(self, role: str, mcp_access: Dict[str, str]) -> bool:
        """Update MCP access for all users with specific role"""
        try:
            # Update configuration
            if "roles" not in self.config:
                self.config["roles"] = {}
            if role not in self.config["roles"]:
                self.config["roles"][role] = {}
            
            self.config["roles"][role]["mcp_access"] = mcp_access.copy()
            
            # Update existing user profiles with this role
            updated_count = 0
            for profile in self.user_profiles.values():
                if profile.role == role:
                    profile.mcp_access.update(mcp_access)
                    updated_count += 1
            
            self.logger.info(f"Updated MCP access for role {role}, affected {updated_count} users")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating role access: {e}")
            return False


# Create singleton instance
mcp_access_manager = MCPAccessControlManager()


# Backward compatibility functions
def check_mcp_access(user_id: str, role: str, mcp_server: str, operation: str) -> Tuple[bool, str]:
    """Check MCP access - backward compatibility wrapper"""
    return mcp_access_manager.check_access(user_id, role, mcp_server, operation)


def get_user_mcp_permissions(user_id: str, role: str) -> Dict[str, Any]:
    """Get user MCP permissions - backward compatibility wrapper"""
    return mcp_access_manager.get_user_permissions_summary(user_id, role)