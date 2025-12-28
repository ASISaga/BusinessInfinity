# BusinessInfinity Refactoring Plan - Post AOS Migration

## Overview

This document outlines the refactoring plan for BusinessInfinity after the infrastructure components have been moved to AgentOperatingSystem (AOS). The goal is to update BusinessInfinity to import and use these components from AOS rather than maintaining local copies.

## Assumption

**The files in `/temp/aos_migration` have been successfully merged into the AgentOperatingSystem repository** and are available via the AOS package.

## Files to Refactor in BusinessInfinity

### 1. Update `src/core/reliability.py`

**Current State**: Contains full implementation of reliability patterns

**Refactored State**: Should be a thin wrapper/re-export from AOS

**Action**:
```python
"""
Reliability patterns for BusinessInfinity - imported from AOS
"""
# Import everything from AOS reliability module
from AgentOperatingSystem.reliability import (
    CircuitBreaker,
    RetryPolicy,
    IdempotencyHandler,
    CircuitState,
    with_circuit_breaker,
    with_retry,
    with_idempotency
)

# Re-export for backward compatibility
__all__ = [
    'CircuitBreaker',
    'RetryPolicy',
    'IdempotencyHandler',
    'CircuitState',
    'with_circuit_breaker',
    'with_retry',
    'with_idempotency'
]
```

**Files that import from this module**: No changes needed if they import from `src.core.reliability`

### 2. Update `src/core/observability.py`

**Current State**: Contains full implementation of observability infrastructure

**Refactored State**: Should be a thin wrapper/re-export from AOS

**Action**:
```python
"""
Observability for BusinessInfinity - imported from AOS
"""
# Import everything from AOS observability module
from AgentOperatingSystem.observability import (
    CorrelationContext,
    get_correlation_context,
    set_correlation_context,
    correlation_scope,
    StructuredLogger,
    MetricsCollector,
    HealthCheck,
    get_metrics_collector,
    get_health_check,
    create_structured_logger
)

# Re-export for backward compatibility
__all__ = [
    'CorrelationContext',
    'get_correlation_context',
    'set_correlation_context',
    'correlation_scope',
    'StructuredLogger',
    'MetricsCollector',
    'HealthCheck',
    'get_metrics_collector',
    'get_health_check',
    'create_structured_logger'
]
```

**Files that import from this module**: No changes needed if they import from `src.core.observability`

### 3. Update `src/core/service_interfaces.py`

**Current State**: Contains interface definitions and AOS wrapper implementations

**Refactored State**: Should import interfaces from AOS, keep concrete implementations if they're business-specific

**Action**:
```python
"""
Service Interfaces for BusinessInfinity - imported from AOS
"""
# Import generic interfaces from AOS
from AgentOperatingSystem.service_interfaces import (
    IStorageService,
    IMessagingService,
    IWorkflowService,
    IAuthService
)

# Keep concrete implementations that wrap AOS services
# (AOSStorageService, AOSMessagingService, etc. if they exist)
# OR import them from AOS if they're generic enough

from typing import Dict, Any, List, Optional

class AOSStorageService(IStorageService):
    """Storage service implementation using AOS UnifiedStorageManager."""
    
    def __init__(self, storage_manager):
        """Initialize with AOS storage manager."""
        self.storage = storage_manager
    
    async def save(self, container: str, key: str, data: Any) -> bool:
        """Save data to storage."""
        try:
            await self.storage.save(container, key, data)
            return True
        except Exception:
            return False
    
    # ... rest of implementation

# Re-export interfaces
__all__ = [
    'IStorageService',
    'IMessagingService',
    'IWorkflowService',
    'IAuthService',
    'AOSStorageService',
    'AOSMessagingService',
    'AOSWorkflowService'
]
```

**Files that import from this module**: No changes needed if they import from `src.core.service_interfaces`

### 4. Update `src/core/audit_trail.py`

**Current State**: Contains both generic infrastructure and business-specific logic

**Refactored State**: Should extend AOS base classes with business-specific functionality

**Action**:
```python
"""
Business-specific Audit Trail for BusinessInfinity

Extends AOS generic audit trail with business-specific event types and methods.
"""
from AgentOperatingSystem.audit_trail import (
    AuditTrailManager as BaseAuditTrailManager,
    AuditEvent,
    AuditSeverity,
    AuditQuery
)
from typing import Dict, Any, List, Optional
from enum import Enum


class BusinessEventType(Enum):
    """Business-specific event types for BusinessInfinity"""
    # Boardroom events
    BOARDROOM_DECISION = "boardroom_decision"
    AGENT_VOTE = "agent_vote"
    AGENT_PROPOSAL = "agent_proposal"
    AGENT_EVIDENCE = "agent_evidence"
    LORA_ADAPTER_SWAP = "lora_adapter_swap"
    
    # MCP interactions
    MCP_REQUEST = "mcp_request"
    MCP_RESPONSE = "mcp_response"
    MCP_ERROR = "mcp_error"
    MCP_ACCESS_DENIED = "mcp_access_denied"
    
    # Social media actions
    SOCIAL_MEDIA_POST = "social_media_post"
    SOCIAL_MEDIA_COMMENT = "social_media_comment"
    SOCIAL_MEDIA_ENGAGEMENT = "social_media_engagement"
    
    # Business system actions
    BUSINESS_TRANSACTION = "business_transaction"
    BUSINESS_DATA_ACCESS = "business_data_access"
    BUSINESS_CONFIGURATION = "business_configuration"
    
    # Conversation events
    CONVERSATION_CREATED = "conversation_created"
    CONVERSATION_SIGNED = "conversation_signed"
    A2A_COMMUNICATION = "a2a_communication"
    CONVERSATION_FLAGGED = "conversation_flagged"
    HUMAN_GATE_REQUIRED = "human_gate_required"


class BusinessInfinityAuditTrailManager(BaseAuditTrailManager):
    """
    Business-specific audit trail manager extending AOS base.
    
    Adds business-specific methods for logging boardroom decisions,
    agent votes, MCP interactions, etc.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize with business-specific storage path"""
        super().__init__(storage_path or "audit_logs")
    
    def log_boardroom_decision(self, 
                              decision_id: str,
                              decision_type: str,
                              proposed_by: str,
                              final_decision: str,
                              rationale: str,
                              votes: List[Dict[str, Any]],
                              confidence_score: float,
                              consensus_score: float) -> str:
        """Log a boardroom decision with comprehensive details"""
        return self.log_event(
            event_type=BusinessEventType.BOARDROOM_DECISION.value,
            subject_id=decision_id,
            subject_type="boardroom",
            action=f"Made decision: {decision_type}",
            severity=AuditSeverity.HIGH,
            context={
                "decision_type": decision_type,
                "proposed_by": proposed_by,
                "final_decision": final_decision,
                "votes": votes,
                "vote_count": len(votes)
            },
            rationale=rationale,
            metrics={
                "confidence_score": confidence_score,
                "consensus_score": consensus_score
            },
            compliance_tags={"sox", "business_governance"}
        )
    
    def log_agent_vote(self,
                       voter_id: str,
                       voter_role: str,
                       decision_id: str,
                       vote_value: float,
                       rationale: str,
                       evidence: List[str],
                       confidence: float) -> str:
        """Log an individual agent vote"""
        return self.log_event(
            event_type=BusinessEventType.AGENT_VOTE.value,
            subject_id=voter_id,
            subject_type="agent",
            subject_role=voter_role,
            action=f"Voted on decision {decision_id}",
            target=decision_id,
            context={
                "decision_id": decision_id,
                "vote_value": vote_value
            },
            rationale=rationale,
            evidence=evidence,
            metrics={
                "vote_value": vote_value,
                "confidence": confidence
            },
            compliance_tags={"business_governance"}
        )
    
    def log_mcp_interaction(self,
                           mcp_server: str,
                           operation: str,
                           agent_id: str,
                           success: bool,
                           details: Dict[str, Any]) -> str:
        """Log an MCP server interaction"""
        event_type = BusinessEventType.MCP_REQUEST if success else BusinessEventType.MCP_ERROR
        severity = AuditSeverity.LOW if success else AuditSeverity.MEDIUM
        
        return self.log_event(
            event_type=event_type.value,
            subject_id=agent_id,
            subject_type="agent",
            action=f"MCP {operation} on {mcp_server}",
            severity=severity,
            context={
                "mcp_server": mcp_server,
                "operation": operation,
                "success": success,
                "details": details
            },
            compliance_tags={"mcp_audit"}
        )
    
    # Add other business-specific methods as needed


# For backward compatibility, also export AOS base classes
__all__ = [
    'BusinessInfinityAuditTrailManager',
    'BusinessEventType',
    'AuditEvent',
    'AuditSeverity',
    'AuditQuery'
]
```

**Files that import from this module**: Need to update to use `BusinessInfinityAuditTrailManager` instead of `AuditTrailManager`

### 5. Update `pyproject.toml`

**Current State**: Depends on AOS from main branch

**Refactored State**: Should depend on AOS with the new version that includes infrastructure components

**Action**:
```toml
dependencies = [
    # ... other dependencies
    "AgentOperatingSystem[azure] @ git+https://github.com/ASISaga/AgentOperatingSystem.git@v1.1.0",
    # ... rest of dependencies
]
```

*Note: Replace `v1.1.0` with the actual version tag created after merging AOS changes*

## Import Update Strategy

### Option 1: Gradual Migration (Recommended for Production)

Keep the wrapper files in `src/core/` that re-export from AOS. This provides:
- **Backward compatibility**: Existing code doesn't need immediate updates
- **Gradual transition**: Can update imports module by module
- **Safety**: Can revert easily if issues arise

### Option 2: Direct Migration (Cleaner but Riskier)

Update all imports throughout the codebase to import directly from AOS:

**Before:**
```python
from src.core.reliability import CircuitBreaker, with_retry
from src.core.observability import StructuredLogger
```

**After:**
```python
from AgentOperatingSystem.reliability import CircuitBreaker, with_retry
from AgentOperatingSystem.observability import StructuredLogger
```

**Affected Files** (to be determined by searching codebase):
- All files importing from `src.core.reliability`
- All files importing from `src.core.observability`
- All files importing from `src.core.service_interfaces`
- All files importing from `src.core.audit_trail`

## Testing Strategy

### Unit Tests
1. Test that wrapper modules correctly re-export AOS components
2. Test business-specific audit trail extensions
3. Verify all business logic still works with AOS infrastructure

### Integration Tests
1. Test reliability patterns with actual business workflows
2. Test observability features in business context
3. Test audit trail with boardroom decisions and agent votes
4. Verify service interfaces work with AOS implementations

### Regression Testing
1. Run full existing test suite
2. Verify no functionality is broken
3. Check performance is not degraded

## Deployment Strategy

### Phase 1: Preparation
1. Wait for AOS changes to be merged and released
2. Update `pyproject.toml` to use new AOS version
3. Create wrapper files as shown above
4. Run tests locally

### Phase 2: Staged Rollout
1. Deploy to development environment
2. Run integration tests
3. Monitor for issues
4. Deploy to staging environment
5. Perform UAT (User Acceptance Testing)

### Phase 3: Production
1. Deploy to production
2. Monitor observability metrics
3. Check audit trail integrity
4. Verify all business workflows function correctly

## Rollback Plan

If issues arise:

1. **Immediate**: Revert to previous AOS version in `pyproject.toml`
2. **Short-term**: Fix issues in wrapper files without touching AOS
3. **Long-term**: Submit fixes to AOS if infrastructure issues found

## Benefits Verification

After refactoring, verify:

- [ ] No code duplication between AOS and BusinessInfinity
- [ ] Clean separation of infrastructure vs business logic
- [ ] All tests passing
- [ ] Observability features working correctly
- [ ] Audit trail properly recording business events
- [ ] Reliability patterns functioning in production

## Documentation Updates

Update the following documentation:

1. **ARCHITECTURE.md**: Reflect new AOS dependency structure
2. **REFACTORING_ARCHITECTURE.md**: Document completion of refactoring
3. **Developer Guide**: Update import examples
4. **Deployment Guide**: Note new AOS version requirement

## Success Criteria

The refactoring is successful when:

1. ✅ All BusinessInfinity code imports infrastructure from AOS
2. ✅ No infrastructure code duplicated in BusinessInfinity
3. ✅ All existing tests pass
4. ✅ Business-specific logic clearly separated in extended classes
5. ✅ Documentation updated and accurate
6. ✅ Production deployment successful with no regressions

## Next Steps

1. Wait for AOS migration files to be reviewed and merged
2. Once AOS is updated, execute this refactoring plan
3. Test thoroughly
4. Deploy gradually
5. Monitor and iterate as needed
