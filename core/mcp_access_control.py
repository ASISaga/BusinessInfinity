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
        self.violations: List[AccessControlViolation] = []
        self.logger = logging.getLogger(__name__)
        
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
    
    def _default_config(self) -> Dict[str, Any]:
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
            return False, reason
        
        # Get user's access level for this MCP server
        access_level = self._get_user_access_level(profile, mcp_server)
        
        # Check if operation is allowed for this access level
        if not self._is_operation_allowed(access_level, operation):
            reason = f"Access level {access_level} does not permit operation {operation}"
            self._log_violation(role, mcp_server, operation, reason)
            return False, reason
        
        # Check rate limiting and restrictions
        if not self._check_restrictions(profile, mcp_server, operation):
            reason = "Operation blocked by usage restrictions or rate limiting"
            self._log_violation(role, mcp_server, operation, reason)
            return False, reason
        
        # Check if onboarding stage progression is needed
        self._check_onboarding_progression(profile)
        
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