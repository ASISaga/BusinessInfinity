# Migration Guide: BusinessInfinity Refactoring

## Overview

This guide documents the migration from the current mixed-concerns architecture to the clean separation between AgentOperatingSystem (infrastructure) and BusinessInfinity (business logic).

## Architecture Change Summary

### Before (Mixed Concerns)
```
BusinessInfinity
├── Business logic (agents, workflows, analytics)
├── Infrastructure code (lifecycle, storage, messaging)  ← Should be in AOS
├── Mixed imports and responsibilities
└── Duplicated infrastructure patterns
```

### After (Clean Separation)
```
AgentOperatingSystem (Infrastructure)
├── Agent lifecycle management
├── Message bus and communication
├── Storage and persistence
├── Base agent classes
├── Orchestration engine
├── Authentication and security
└── Monitoring and telemetry

BusinessInfinity (Business Logic)
├── Business agents (CEO, CFO, CTO, etc.)
├── Business workflows
├── Business analytics
├── Strategic decision-making
├── Business governance
└── External business integrations
```

## Breaking Changes

### 1. Agent Class Hierarchy

**Before:**
```python
# Mixed inheritance with unclear separation
from BusinessAgent import BusinessAgent

class ChiefExecutiveOfficer(BusinessAgent):
    # Mixed business and infrastructure concerns
    pass
```

**After:**
```python
# Clean inheritance from AOS base classes
from AgentOperatingSystem.agents import LeadershipAgent
from .business_agent_refactored import BusinessAgent

class ChiefExecutiveOfficerRefactored(BusinessAgent):
    # Pure business logic only
    # Infrastructure provided by LeadershipAgent (AOS)
    pass
```

**Migration Steps:**
1. Update agent classes to extend `BusinessAgent` (which extends AOS `LeadershipAgent`)
2. Remove infrastructure code from agent implementations
3. Use AOS services via dependency injection
4. Focus agent code on business logic only

### 2. BusinessInfinity Main Application

**Before:**
```python
# Mixed infrastructure and business logic
from AgentOperatingSystem import AgentOperatingSystem

class BusinessInfinity:
    def __init__(self):
        # Mixed initialization
        self.aos = AgentOperatingSystem()
        # Direct infrastructure manipulation
        pass
```

**After:**
```python
# Clean separation with dependency injection
from AgentOperatingSystem import AgentOperatingSystem
from AgentOperatingSystem.agents import UnifiedAgentManager
from AgentOperatingSystem.storage.manager import UnifiedStorageManager

class BusinessInfinityRefactored:
    def __init__(self, config: BusinessInfinityConfig = None):
        # Business config only
        self.config = config or BusinessInfinityConfig()
        
        # AOS services injected
        self.aos = None
        self.agent_manager = None
        self.storage = None
        
    async def initialize(self):
        # Initialize AOS infrastructure
        self.aos = AgentOperatingSystem()
        await self.aos.initialize()
        
        # Get AOS services
        self.agent_manager = self.aos.get_agent_manager()
        self.storage = self.aos.get_storage_manager()
        
        # Initialize business components
        await self._initialize_business_agents()
```

**Migration Steps:**
1. Separate business config from infrastructure config
2. Use dependency injection for AOS services
3. Remove direct infrastructure manipulation
4. Use AOS service interfaces

### 3. Import Structure

**Before:**
```python
# Scattered imports
from AgentOperatingSystem import AgentOperatingSystem
from AgentOperatingSystem.storage.manager import UnifiedStorageManager
from some_module import SomeClass
```

**After:**
```python
# Organized imports by layer
# AOS Infrastructure imports
from AgentOperatingSystem import AgentOperatingSystem
from AgentOperatingSystem.agents import BaseAgent, LeadershipAgent, UnifiedAgentManager
from AgentOperatingSystem.services.interfaces import IStorageService, IMessagingService
from AgentOperatingSystem.storage.manager import UnifiedStorageManager
from AgentOperatingSystem.messaging import MessageEnvelope, ServiceBusManager
from AgentOperatingSystem.orchestration import OrchestrationEngine

# Business layer imports
from .agents.business_agent_refactored import BusinessAgent
from .agents.ceo_refactored import ChiefExecutiveOfficerRefactored
```

### 4. Storage Operations

**Before:**
```python
# Direct storage manipulation
storage = UnifiedStorageManager()
await storage.save("decisions", key, data)
```

**After:**
```python
# Use injected AOS storage service
class BusinessInfinityRefactored:
    def __init__(self):
        self.storage = None  # Injected from AOS
    
    async def initialize(self):
        self.storage = self.aos.get_storage_manager()
    
    async def save_decision(self, decision):
        # Use injected service
        await self.storage.save(
            collection="strategic_decisions",
            key=decision["id"],
            data=decision
        )
```

### 5. Messaging Operations

**Before:**
```python
# Direct Service Bus usage
from AgentOperatingSystem.messaging.servicebus_manager import ServiceBusManager

bus = ServiceBusManager()
await bus.publish("topic", message)
```

**After:**
```python
# Use injected AOS messaging service
class BusinessInfinityRefactored:
    def __init__(self):
        self.messaging = None  # Injected from AOS
    
    async def initialize(self):
        self.messaging = self.aos.get_messaging_service()
    
    async def publish_decision(self, decision):
        # Use injected service
        await self.messaging.publish(
            topic="business_decisions",
            message={
                "type": "strategic_decision_made",
                "decision_id": decision["id"]
            }
        )
```

## File Migration Map

### Files to Keep (Business Logic)

These files stay in BusinessInfinity, refactored to use AOS services:

- `src/agents/ceo.py` → `src/agents/ceo_refactored.py`
- `src/agents/cfo.py` → `src/agents/cfo_refactored.py`
- `src/agents/cto.py` → `src/agents/cto_refactored.py`
- `src/agents/founder.py` → `src/agents/founder_refactored.py`
- `src/agents/investor_agent.py` → `src/agents/investor_refactored.py`
- `src/business_infinity.py` → `src/business_infinity_refactored.py`
- `src/workflows/business_workflows.py` (refactor to use AOS orchestration)
- `src/analytics/business_analytics.py` (refactor to use AOS storage)
- `src/network/*` (business-specific Global Boardroom Network)
- `src/risk/*` (business risk management)
- `src/knowledge/*` (business knowledge management)
- `src/routes/*` (business API endpoints)

### Files to Remove (Duplicated Infrastructure)

These represent infrastructure concerns that should be in AOS:

- Generic agent lifecycle code in `src/core/agents.py` → Move to AOS
- Generic utilities in `src/core/utils.py` → Move to AOS
- Base patterns that aren't business-specific

### Files That Need Refactoring

- `src/function_app.py`: Update to use refactored BusinessInfinity and AOS services
- `src/core/config.py`: Separate business config from infrastructure config
- `src/agents/manager.py`: Refactor to use AOS UnifiedAgentManager
- `src/workflows/manager.py`: Refactor to use AOS OrchestrationEngine

## Step-by-Step Migration Process

### Phase 1: Prepare AOS (External PR)

1. **Create PR in AgentOperatingSystem** with:
   - Enhanced base agent classes (`BaseAgent`, `LeadershipAgent`)
   - `UnifiedAgentManager` for generic agent lifecycle
   - Clean service interfaces (`IStorageService`, `IMessagingService`, etc.)
   - Reliability patterns (`RetryPolicy`, `CircuitBreaker`)
   - Observability foundation (`StructuredLogger`, `MetricsCollector`)

2. **Review and merge AOS PR**

3. **Publish new AOS version** with refactored structure

### Phase 2: Update BusinessInfinity Dependencies

1. **Update `pyproject.toml`**:
   ```toml
   dependencies = [
       # Update to new AOS version
       "AgentOperatingSystem[azure] @ git+https://github.com/ASISaga/AgentOperatingSystem.git@refactored",
       # Other dependencies...
   ]
   ```

2. **Install updated dependencies**:
   ```bash
   pip install -e .
   ```

### Phase 3: Refactor Business Agents

1. **Create new base class** (`src/agents/business_agent_refactored.py`):
   - Extend AOS `LeadershipAgent`
   - Add business-specific capabilities (KPIs, analytics, domain expertise)
   - Remove infrastructure concerns

2. **Refactor each business agent**:
   - CEO: `src/agents/ceo_refactored.py`
   - CFO: `src/agents/cfo_refactored.py`
   - CTO: `src/agents/cto_refactored.py`
   - Founder: `src/agents/founder_refactored.py`
   - Investor: `src/agents/investor_refactored.py`

3. **Update agent implementations**:
   - Extend `BusinessAgent`
   - Implement business-specific methods only
   - Use AOS services for infrastructure needs

### Phase 4: Refactor Main Application

1. **Create refactored BusinessInfinity** (`src/business_infinity_refactored.py`):
   - Separate business config
   - Inject AOS services
   - Remove infrastructure code
   - Focus on business orchestration

2. **Update initialization**:
   - Initialize AOS first
   - Get AOS service instances
   - Initialize business components
   - Register business agents with AOS

### Phase 5: Update API Layer

1. **Refactor Azure Functions** (`src/function_app.py`):
   - Use refactored BusinessInfinity
   - Use AOS authentication middleware
   - Delegate to business services
   - Thin request/response handlers

2. **Update route handlers**:
   - Use injected services
   - Remove direct infrastructure access
   - Focus on business routing

### Phase 6: Update Workflows and Analytics

1. **Refactor workflows** to use AOS `OrchestrationEngine`
2. **Refactor analytics** to use AOS storage services
3. **Update business logic** to use clean interfaces

### Phase 7: Testing and Validation

1. **Update tests**:
   - Mock AOS services in unit tests
   - Update integration tests for new structure
   - Add contract tests for service interfaces

2. **Run test suite**:
   ```bash
   pytest
   ```

3. **Verify all functionality**:
   - Agent operations
   - Decision-making
   - Workflows
   - Analytics
   - API endpoints

### Phase 8: Documentation and Cleanup

1. **Update documentation**:
   - README.md with new architecture
   - API documentation
   - Developer guides

2. **Clean up old files**:
   - Remove deprecated files
   - Update imports throughout codebase
   - Remove infrastructure duplicates

3. **Update manifest.json** with correct dependency relationships

## Rollback Plan

If issues arise during migration:

1. **Keep old files** alongside new refactored versions
2. **Feature flag** to switch between old and new implementations
3. **Gradual migration** - migrate one component at a time
4. **Comprehensive testing** at each step

## Testing Strategy

### Unit Tests

```python
# Test business agents with mocked AOS services
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_ceo_decision_making():
    # Mock AOS services
    mock_storage = AsyncMock()
    mock_messaging = AsyncMock()
    
    # Create CEO with mocked services
    ceo = create_ceo()
    ceo.storage = mock_storage
    ceo.messaging = mock_messaging
    
    # Test business decision
    decision = await ceo.make_business_decision({
        "type": "strategic",
        "context": "Market expansion"
    })
    
    assert decision is not None
    assert "decision" in decision
```

### Integration Tests

```python
# Test with real AOS instance
@pytest.mark.asyncio
async def test_business_infinity_integration():
    # Create BusinessInfinity with real AOS
    bi = await create_business_infinity()
    
    # Test full workflow
    decision = await bi.make_strategic_decision({
        "type": "strategic",
        "context": "New market entry"
    })
    
    assert decision is not None
    
    # Verify storage
    stored = await bi.storage.load("strategic_decisions", decision["id"])
    assert stored == decision
```

## Common Pitfalls and Solutions

### Pitfall 1: Direct Infrastructure Access

**Problem**: Code directly accesses infrastructure instead of using services
```python
# Bad
from AgentOperatingSystem.storage import some_storage_method
data = await some_storage_method()
```

**Solution**: Use injected services
```python
# Good
class BusinessComponent:
    def __init__(self):
        self.storage = None  # Will be injected
    
    async def load_data(self):
        return await self.storage.load(...)
```

### Pitfall 2: Mixed Configuration

**Problem**: Business and infrastructure config mixed together

**Solution**: Separate configs
```python
# Business config (stays in BusinessInfinity)
class BusinessInfinityConfig:
    business_name = "..."
    industry = "..."

# Infrastructure config (in AOS)
class AOSConfig:
    storage_backend = "..."
    messaging_provider = "..."
```

### Pitfall 3: Tight Coupling

**Problem**: Business code tightly coupled to specific AOS implementation

**Solution**: Use service interfaces
```python
# Use interfaces, not concrete implementations
from AgentOperatingSystem.services.interfaces import IStorageService

class BusinessComponent:
    def __init__(self, storage: IStorageService):
        self.storage = storage  # Works with any implementation
```

## Success Criteria

### For AgentOperatingSystem
- [ ] Generic, reusable infrastructure only
- [ ] No business-specific code
- [ ] Clean service interfaces
- [ ] Comprehensive base agent classes
- [ ] Well-documented contracts

### For BusinessInfinity
- [ ] Business logic and orchestration only
- [ ] Clean dependency on AOS services
- [ ] No infrastructure code duplication
- [ ] Proper extension of AOS base classes
- [ ] Business-focused configuration

### Integration
- [ ] All tests pass
- [ ] All API endpoints functional
- [ ] All workflows execute correctly
- [ ] All agents operational
- [ ] Documentation updated
- [ ] Clean import structure
- [ ] No circular dependencies

## Support and Resources

- **AOS Refactoring Spec**: `AOS_REFACTORING_SPEC.md`
- **Refactoring Analysis**: `REFACTORING_ANALYSIS.md`
- **Architecture Docs**: `docs/REFACTORING_ARCHITECTURE.md`
- **Example Code**: 
  - `src/agents/business_agent_refactored.py`
  - `src/agents/ceo_refactored.py`
  - `src/business_infinity_refactored.py`

## Timeline

- **Week 1**: AOS refactoring PR and review
- **Week 2**: AOS PR merge and new version release
- **Week 3-4**: BusinessInfinity refactoring
- **Week 5**: Testing and validation
- **Week 6**: Documentation and cleanup
- **Week 7**: Production deployment

## Conclusion

This migration establishes clean architectural boundaries:
- **AOS**: Generic, reusable agent infrastructure
- **BusinessInfinity**: Business-specific orchestration and logic

The result is:
- Better maintainability
- Clearer responsibilities
- Reusable infrastructure
- Testable components
- Scalable architecture
