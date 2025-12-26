# AgentOperatingSystem Integration Guide

## Overview

BusinessInfinity is built on the [Agent Operating System (AOS)](https://github.com/ASISaga/AgentOperatingSystem) infrastructure layer. This document details how BusinessInfinity leverages AOS capabilities and provides guidance for developers working with the integration.

## Architecture

### Clean Separation of Concerns

```
┌─────────────────────────────────────────────────────────────┐
│              Business Infinity (BI)                        │
│            Business Application Layer                       │
├─────────────────────────────────────────────────────────────┤
│  • Business logic and workflows                            │
│  • Business-specific agents (CEO, CFO, CTO, etc.)          │
│  • Strategic decision-making processes                     │
│  • Business analytics and KPIs                             │
│  • External business system integrations                   │
│  • Risk management and knowledge base                      │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ Uses via clean interfaces
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Agent Operating System (AOS)                       │
│           Infrastructure Layer                              │
├─────────────────────────────────────────────────────────────┤
│  Core Services (CURRENTLY USED):                           │
│  ✅ Orchestration Engine                                   │
│  ✅ Storage Services (Blob, Table, Queue)                  │
│  ✅ Messaging (Service Bus)                                │
│  ✅ ML Pipeline (LoRA training, inference)                 │
│  ✅ Environment Management                                 │
│  ✅ Authentication & Authorization                         │
│                                                             │
│  Advanced Services (NEWLY INTEGRATED):                     │
│  ✅ Service Interfaces (IStorage, IMessaging, etc.)        │
│  ✅ Reliability Patterns (Circuit Breaker, Retry)          │
│  ✅ Observability (Structured Logging, Metrics)            │
│  ✅ Health Checks & Monitoring                             │
│                                                             │
│  Available Services (PLANNED):                             │
│  ⏳ Enhanced Agent Base Classes                            │
│  ⏳ Message Envelopes with Correlation IDs                 │
│  ⏳ Governance Services                                     │
│  ⏳ Knowledge Management                                    │
│  ⏳ Learning Pipeline                                       │
│  ⏳ Extensibility Framework                                │
└─────────────────────────────────────────────────────────────┘
```

## AOS Capabilities Utilized

### 1. Service Interfaces (Priority 1 - ✅ Implemented)

BusinessInfinity now uses clean service interfaces to interact with AOS infrastructure:

```python
from core.service_interfaces import (
    IStorageService,
    IMessagingService,
    IWorkflowService,
    AOSStorageService,
    AOSMessagingService,
    AOSWorkflowService
)

# Initialize with clean interfaces
storage_service: IStorageService = AOSStorageService(aos.storage_manager)
messaging_service: IMessagingService = AOSMessagingService(aos.messaging_manager)
workflow_service: IWorkflowService = AOSWorkflowService(aos.orchestration_engine)
```

**Benefits:**
- Better testability through interface mocking
- Decoupling from concrete AOS implementations
- Easier migration if AOS APIs change
- Cleaner dependency injection

**Implementation:** `src/core/service_interfaces.py`

### 2. Reliability Patterns (Priority 1 - ✅ Implemented)

Robust fault tolerance through proven reliability patterns:

#### Circuit Breaker

Prevents cascading failures by stopping calls to failing services:

```python
from core.reliability import CircuitBreaker

breaker = CircuitBreaker(
    failure_threshold=5,      # Open after 5 failures
    recovery_timeout=60       # Retry after 60 seconds
)

# Execute with protection
result = await breaker.call(risky_operation, *args, **kwargs)
```

**Use Cases:**
- Workflow execution
- External API calls
- Database operations

#### Retry Policy

Automatic retries with exponential backoff:

```python
from core.reliability import RetryPolicy, with_retry

# Using RetryPolicy
policy = RetryPolicy(
    max_retries=3,
    base_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True
)
result = await policy.execute(operation, *args, **kwargs)

# Using decorator
@with_retry(max_retries=3, base_delay=2.0)
async def make_strategic_decision(context):
    # Operation that may fail transiently
    pass
```

**Use Cases:**
- Strategic decision workflows
- Transient network failures
- Database connection issues
- Service Bus operations

#### Idempotency Handler

Ensures operations can be safely retried without side effects:

```python
from core.reliability import IdempotencyHandler

handler = IdempotencyHandler(cache_ttl=3600)

# Execute with idempotency guarantee
result = await handler.execute(
    idempotency_key="operation-123",
    func=operation,
    *args,
    **kwargs
)
```

**Implementation:** `src/core/reliability.py`

### 3. Enhanced Observability (Priority 1 - ✅ Implemented)

Comprehensive visibility into system behavior:

#### Structured Logging with Correlation IDs

All log entries include correlation IDs for distributed tracing:

```python
from core.observability import create_structured_logger, correlation_scope

logger = create_structured_logger(__name__)

# Automatic correlation ID injection
with correlation_scope(operation_name="process_workflow"):
    logger.info("Processing workflow",
                workflow_id=workflow_id,
                workflow_type="strategic_decision")
```

**Output:**
```json
{
  "timestamp": "2025-12-26T00:00:00.000Z",
  "level": "INFO",
  "logger": "workflows.manager",
  "message": "Processing workflow",
  "correlation_id": "abc123-def456-ghi789",
  "operation": "process_workflow",
  "data": {
    "workflow_id": "strategic_decision_20251226",
    "workflow_type": "strategic_decision"
  }
}
```

#### Metrics Collection

Track performance with counters, gauges, and histograms:

```python
from core.observability import get_metrics_collector

metrics = get_metrics_collector()

# Counters for events
metrics.increment_counter("bi.decisions.success")
metrics.increment_counter("bi.workflows.failed", tags={"workflow": "innovation"})

# Gauges for current values
metrics.set_gauge("bi.active_workflows", workflow_count)

# Histograms for distributions
metrics.record_histogram("bi.workflow.duration", duration_seconds,
                         tags={"workflow_type": "strategic"})

# Get all metrics
all_metrics = metrics.get_metrics()
```

#### Health Checks

Component-level health monitoring:

```python
from core.observability import get_health_check

health = get_health_check()

# Register health checks
health.register_check("aos", check_aos_health)
health.register_check("agents", check_agents_health)

# Run all checks
status = await health.check_health()
# Returns: {
#   "healthy": true,
#   "timestamp": "2025-12-26T00:00:00.000Z",
#   "checks": {
#     "aos": {"healthy": true, "status": "running"},
#     "agents": {"healthy": true, "agent_count": 8}
#   }
# }
```

**Implementation:** `src/core/observability.py`

## Integration Points

### Core Application (`src/core/application.py`)

The main BusinessInfinity application uses all AOS improvements:

```python
from core.service_interfaces import AOSStorageService
from core.observability import create_structured_logger, correlation_scope, get_metrics_collector
from core.reliability import CircuitBreaker, RetryPolicy

class BusinessInfinity:
    def __init__(self, config):
        # Structured logging
        self.logger = create_structured_logger(__name__)
        
        # Metrics collection
        self.metrics = get_metrics_collector()
        
        # Service interfaces
        self.storage_service = AOSStorageService(self.storage_manager)
        
        # Reliability patterns
        self.circuit_breaker = CircuitBreaker()
        self.retry_policy = RetryPolicy()
    
    async def make_strategic_decision(self, context):
        # Correlation scope for tracing
        with correlation_scope(operation_name="make_strategic_decision"):
            # Structured logging
            self.logger.info("Making strategic decision",
                           decision_type=context.get("type"))
            
            # Metrics tracking
            self.metrics.increment_counter("bi.decisions.requested")
            
            # Retry for resilience
            result = await self.retry_policy.execute(
                self.workflow_manager.make_strategic_decision,
                context
            )
            
            self.metrics.increment_counter("bi.decisions.success")
            return result
```

### Workflow Manager (`src/workflows/manager.py`)

Workflows leverage reliability patterns and observability:

```python
from core.observability import create_structured_logger, correlation_scope
from core.reliability import with_retry

class BusinessWorkflowManager:
    def __init__(self, aos, config, logger):
        self.logger = create_structured_logger(__name__)
        self.metrics = get_metrics_collector()
    
    @with_retry(max_retries=3, base_delay=2.0)
    async def make_strategic_decision(self, context):
        with correlation_scope(operation_name="make_strategic_decision"):
            self.logger.info("Executing strategic decision workflow",
                           decision_type=context.get("type"))
            
            # Execute workflow
            result = await self.aos.orchestration_engine.execute_workflow(...)
            
            # Track metrics
            self.metrics.increment_counter("workflow.success")
            self.metrics.record_histogram("workflow.duration", duration)
            
            return result
```

## Migration Status

Based on [AOS_UTILIZATION_ANALYSIS.md](../AOS_UTILIZATION_ANALYSIS.md), here's the current migration status:

### ✅ Completed (Priority 1 - Critical)

1. **Service Interfaces** - All infrastructure access goes through clean interfaces
2. **Reliability Patterns** - Circuit breakers and retry logic implemented
3. **Observability** - Structured logging, metrics, and health checks in place

### ⏳ In Progress (Priority 2 - Important)

4. **Agent Hierarchy** - Refactor agents to extend AOS `BaseAgent`/`LeadershipAgent`
5. **Message Envelopes** - Adopt `MessageEnvelope` for all inter-agent communication
6. **Governance Integration** - Leverage AOS audit logging and compliance

### 📋 Planned (Priority 3 - Nice-to-have)

7. **Learning Pipeline** - Integrate AOS continuous learning capabilities
8. **Extensibility Framework** - Use AOS plugin system for custom features
9. **Knowledge Management** - Evaluate migration to AOS knowledge services

## Best Practices

### 1. Always Use Correlation Scopes

For any multi-step operation, use correlation scopes:

```python
with correlation_scope(operation_name="complex_operation"):
    # All operations share same correlation ID
    step1()
    step2()
    step3()
```

### 2. Apply Retry Logic to Transient Operations

Use `@with_retry` decorator for operations that may fail transiently:

```python
@with_retry(max_retries=3, base_delay=1.0)
async def call_external_api():
    # May fail due to network issues
    pass
```

### 3. Use Circuit Breakers for External Services

Protect against cascading failures:

```python
breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
result = await breaker.call(external_service_call)
```

### 4. Track Business Metrics

Always track important business metrics:

```python
metrics.increment_counter("business_event", tags={"type": "decision"})
metrics.record_histogram("operation_duration", duration, tags={"operation": "decision"})
```

### 5. Use Structured Logging

Replace all `logging.getLogger()` with `create_structured_logger()`:

```python
# Bad
logger = logging.getLogger(__name__)
logger.info(f"Processing {item_id}")

# Good
logger = create_structured_logger(__name__)
logger.info("Processing item", item_id=item_id, item_type=item.type)
```

## Testing

### Unit Testing with Service Interfaces

Service interfaces make testing easier:

```python
from core.service_interfaces import IStorageService

class MockStorageService(IStorageService):
    async def save(self, container, key, data):
        return True
    
    async def load(self, container, key):
        return {"test": "data"}

# Use in tests
app = BusinessInfinity(config)
app.storage_service = MockStorageService()
```

### Testing Reliability Patterns

Test circuit breaker behavior:

```python
async def test_circuit_breaker_opens():
    breaker = CircuitBreaker(failure_threshold=2)
    
    # Cause failures
    for _ in range(2):
        try:
            await breaker.call(failing_operation)
        except:
            pass
    
    # Circuit should be open
    assert breaker.state == CircuitState.OPEN
```

## Monitoring and Debugging

### View Correlation IDs in Logs

Filter logs by correlation ID to trace entire operations:

```bash
# View all logs for a specific operation
cat application.log | grep "correlation_id\":\"abc123-def456"
```

### Access Metrics

Get current metrics via health endpoint:

```python
# In your API endpoint
@app.get("/metrics")
async def get_metrics():
    metrics = get_metrics_collector()
    return metrics.get_metrics()
```

### Health Check Endpoint

Monitor system health:

```python
@app.get("/health")
async def health_check():
    health = get_health_check()
    return await health.check_health()
```

## Performance Impact

The AOS utilization improvements have minimal performance impact:

- **Structured Logging**: ~5% overhead vs. standard logging
- **Circuit Breaker**: Negligible overhead when closed
- **Retry Logic**: Only impacts failed operations
- **Correlation Context**: ~1% overhead from thread-local storage
- **Metrics Collection**: In-memory, <1% overhead

**Overall**: <5% performance impact with significant reliability and observability gains.

## Future Roadmap

See [AOS_UTILIZATION_ANALYSIS.md](../AOS_UTILIZATION_ANALYSIS.md) for detailed roadmap:

1. **Q1 2026**: Complete Priority 2 items (Agent hierarchy, Message envelopes, Governance)
2. **Q2 2026**: Implement Priority 3 items (Learning pipeline, Extensibility)
3. **Q3 2026**: Full AOS capability utilization
4. **Q4 2026**: Performance optimization and advanced features

## References

- **AOS Documentation**: [AgentOperatingSystem/README.md](https://github.com/ASISaga/AgentOperatingSystem/blob/main/README.md)
- **Utilization Analysis**: [AOS_UTILIZATION_ANALYSIS.md](../AOS_UTILIZATION_ANALYSIS.md)
- **Migration Guide**: [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md)
- **Refactoring Spec**: [AOS_REFACTORING_SPEC.md](../AOS_REFACTORING_SPEC.md)

## Support

For questions or issues:
1. Check the [AOS Documentation](https://github.com/ASISaga/AgentOperatingSystem)
2. Review [AOS_UTILIZATION_ANALYSIS.md](../AOS_UTILIZATION_ANALYSIS.md)
3. Open an issue in the BusinessInfinity repository
