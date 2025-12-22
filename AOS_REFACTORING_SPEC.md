# AgentOperatingSystem Refactoring Specification

## Purpose

This document specifies the required changes to AgentOperatingSystem to establish it as a pure, generic infrastructure layer for agent-based systems. This refactoring enables clean separation between infrastructure (AOS) and business logic (BusinessInfinity).

## PR Description for AgentOperatingSystem Repository

**Title**: Refactor AOS as Generic Agent Infrastructure Layer

**Description**:
This PR refactors AgentOperatingSystem to be a pure, reusable infrastructure layer for agent-based systems, removing any business-specific code and providing clean, well-defined service interfaces.

**Breaking Changes**: Yes - BusinessInfinity is the only consumer and will be updated accordingly.

## Required Changes

### 1. Enhanced Base Agent Classes

**File**: `AgentOperatingSystem/agents/base_agent.py`

```python
"""
Base Agent - Generic agent with lifecycle, messaging, and state management.
Foundation for all specialized agents.
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import uuid

class BaseAgent(ABC):
    """
    Generic base agent providing:
    - Unique identity and metadata
    - Lifecycle management (initialize, start, stop, health)
    - Message handling and routing
    - State persistence
    - Event publishing
    - Health monitoring
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        config: Dict[str, Any] = None
    ):
        """
        Initialize base agent.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable agent name
            role: Agent role/type
            config: Optional configuration dictionary
        """
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.config = config or {}
        self.metadata = {
            "created_at": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
        self.state = "initialized"
        self.logger = logging.getLogger(f"aos.agent.{agent_id}")
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize agent resources and connections."""
        pass
    
    @abstractmethod
    async def start(self) -> bool:
        """Start agent operations."""
        pass
    
    @abstractmethod
    async def stop(self) -> bool:
        """Stop agent operations gracefully."""
        pass
    
    @abstractmethod
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming message.
        
        Args:
            message: Message payload with type, data, metadata
            
        Returns:
            Response dictionary
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Health status with state, metrics, issues
        """
        return {
            "agent_id": self.agent_id,
            "state": self.state,
            "healthy": self.state in ["initialized", "running"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "state": self.state,
            "metadata": self.metadata
        }
```

**File**: `AgentOperatingSystem/agents/leadership_agent.py`

```python
"""
Leadership Agent - Agent with decision-making and coordination capabilities.
Extends BaseAgent with collaborative decision-making patterns.
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent

class LeadershipAgent(BaseAgent):
    """
    Leadership agent providing:
    - Decision-making capabilities
    - Stakeholder coordination
    - Consensus building
    - Delegation patterns
    - Decision provenance
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        config: Dict[str, Any] = None
    ):
        super().__init__(agent_id, name, role, config)
        self.decisions_made = []
        self.stakeholders = []
        
    async def make_decision(
        self,
        context: Dict[str, Any],
        stakeholders: List[str] = None,
        mode: str = "autonomous"
    ) -> Dict[str, Any]:
        """
        Make a decision based on context.
        
        Args:
            context: Decision context and inputs
            stakeholders: Optional list of stakeholder agent IDs to consult
            mode: Decision mode ("autonomous", "consensus", "delegated")
            
        Returns:
            Decision with rationale, confidence, metadata
        """
        decision = {
            "id": str(uuid.uuid4()),
            "agent_id": self.agent_id,
            "context": context,
            "mode": mode,
            "stakeholders": stakeholders or [],
            "timestamp": datetime.utcnow().isoformat(),
            "decision": await self._evaluate_decision(context),
            "confidence": 0.0,
            "rationale": ""
        }
        
        self.decisions_made.append(decision)
        return decision
    
    async def _evaluate_decision(self, context: Dict[str, Any]) -> Any:
        """
        Evaluate and make decision. Override in subclasses.
        
        Args:
            context: Decision context
            
        Returns:
            Decision outcome
        """
        # Base implementation - override in subclasses
        return {"decision": "pending", "reason": "not_implemented"}
    
    async def consult_stakeholders(
        self,
        stakeholders: List[str],
        topic: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Consult stakeholder agents on a topic.
        
        Args:
            stakeholders: List of agent IDs to consult
            topic: Consultation topic
            context: Context for consultation
            
        Returns:
            List of stakeholder responses
        """
        # To be implemented with message bus integration
        return []
```

### 2. Unified Agent Manager

**File**: `AgentOperatingSystem/agents/manager.py`

```python
"""
Unified Agent Manager - Generic agent lifecycle and orchestration.
Manages agent registration, discovery, health monitoring, and coordination.
"""

from typing import Dict, Any, List, Optional
import logging
from .base_agent import BaseAgent

class UnifiedAgentManager:
    """
    Manages agent lifecycle:
    - Agent registration and deregistration
    - Agent discovery and lookup
    - Health monitoring
    - Fallback and degradation patterns
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("aos.agent_manager")
        
    async def register_agent(self, agent: BaseAgent) -> bool:
        """
        Register an agent.
        
        Args:
            agent: Agent instance to register
            
        Returns:
            True if successful
        """
        try:
            await agent.initialize()
            self.agents[agent.agent_id] = agent
            self.logger.info(f"Registered agent: {agent.agent_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent.agent_id}: {e}")
            return False
    
    async def deregister_agent(self, agent_id: str) -> bool:
        """
        Deregister an agent.
        
        Args:
            agent_id: Agent ID to deregister
            
        Returns:
            True if successful
        """
        if agent_id in self.agents:
            try:
                await self.agents[agent_id].stop()
                del self.agents[agent_id]
                self.logger.info(f"Deregistered agent: {agent_id}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to deregister agent {agent_id}: {e}")
                return False
        return False
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents."""
        return [agent.get_metadata() for agent in self.agents.values()]
    
    async def health_check_all(self) -> Dict[str, Any]:
        """
        Perform health check on all agents.
        
        Returns:
            Health status for each agent
        """
        health_status = {}
        for agent_id, agent in self.agents.items():
            health_status[agent_id] = await agent.health_check()
        return health_status
```

### 3. Service Interfaces

**File**: `AgentOperatingSystem/services/interfaces.py`

```python
"""
Service Interfaces - Clean contracts for AOS services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class IStorageService(ABC):
    """Interface for storage operations."""
    
    @abstractmethod
    async def save(self, collection: str, key: str, data: Dict[str, Any]) -> bool:
        """Save data to storage."""
        pass
    
    @abstractmethod
    async def load(self, collection: str, key: str) -> Optional[Dict[str, Any]]:
        """Load data from storage."""
        pass
    
    @abstractmethod
    async def query(self, collection: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query data with filters."""
        pass
    
    @abstractmethod
    async def delete(self, collection: str, key: str) -> bool:
        """Delete data from storage."""
        pass

class IMessagingService(ABC):
    """Interface for messaging operations."""
    
    @abstractmethod
    async def publish(self, topic: str, message: Dict[str, Any]) -> bool:
        """Publish message to topic."""
        pass
    
    @abstractmethod
    async def subscribe(self, topic: str, handler: callable) -> bool:
        """Subscribe to topic with handler."""
        pass
    
    @abstractmethod
    async def send_to_agent(self, agent_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message directly to agent."""
        pass

class IWorkflowService(ABC):
    """Interface for workflow orchestration."""
    
    @abstractmethod
    async def execute_workflow(
        self,
        workflow_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a workflow."""
        pass
    
    @abstractmethod
    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get workflow execution status."""
        pass

class IAuthService(ABC):
    """Interface for authentication and authorization."""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Authenticate user/agent."""
        pass
    
    @abstractmethod
    async def authorize(self, user_id: str, resource: str, action: str) -> bool:
        """Check authorization."""
        pass
```

### 4. Event Model & Reliability

**File**: `AgentOperatingSystem/messaging/envelope.py`

```python
"""
Message Envelope - Standardized message format with correlation.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class MessageEnvelope:
    """
    Standardized message envelope with:
    - Message type and version
    - Correlation and causation IDs for tracing
    - Timestamp and actor information
    - Payload with schema validation
    """
    
    def __init__(
        self,
        message_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        actor: Optional[str] = None,
        version: str = "1.0",
        attributes: Optional[Dict[str, Any]] = None
    ):
        self.message_id = str(uuid.uuid4())
        self.message_type = message_type
        self.version = version
        self.timestamp = datetime.utcnow().isoformat()
        self.correlation_id = correlation_id or self.message_id
        self.causation_id = causation_id or self.message_id
        self.actor = actor
        self.attributes = attributes or {}
        self.payload = payload
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert envelope to dictionary."""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type,
            "version": self.version,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "actor": self.actor,
            "attributes": self.attributes,
            "payload": self.payload
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageEnvelope':
        """Create envelope from dictionary."""
        envelope = cls(
            message_type=data["message_type"],
            payload=data["payload"],
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id"),
            actor=data.get("actor"),
            version=data.get("version", "1.0"),
            attributes=data.get("attributes", {})
        )
        envelope.message_id = data["message_id"]
        envelope.timestamp = data["timestamp"]
        return envelope
```

**File**: `AgentOperatingSystem/messaging/reliability.py`

```python
"""
Reliability Patterns - Retry, circuit breaker, idempotency.
"""

import asyncio
import time
from typing import Callable, Any, Optional
from functools import wraps

class RetryPolicy:
    """Exponential backoff retry with jitter."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry policy."""
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_attempts - 1:
                    delay = min(
                        self.initial_delay * (self.exponential_base ** attempt),
                        self.max_delay
                    )
                    if self.jitter:
                        delay *= (0.5 + random.random())
                    await asyncio.sleep(delay)
        
        raise last_exception

class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.failure_count = 0
        self.success_count = 0
        self.state = "closed"  # closed, open, half_open
        self.opened_at = None
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker."""
        if self.state == "open":
            if time.time() - self.opened_at >= self.recovery_timeout:
                self.state = "half_open"
                self.success_count = 0
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful execution."""
        self.failure_count = 0
        if self.state == "half_open":
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = "closed"
    
    def _on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            self.opened_at = time.time()
```

### 5. Observability Foundation

**File**: `AgentOperatingSystem/monitoring/observability.py`

```python
"""
Observability - Structured logging, metrics, tracing.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

class StructuredLogger:
    """Structured logger with context and correlation."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context = {}
    
    def with_context(self, **kwargs) -> 'StructuredLogger':
        """Create logger with additional context."""
        new_logger = StructuredLogger(self.logger.name)
        new_logger.context = {**self.context, **kwargs}
        return new_logger
    
    def _log(self, level: int, message: str, **kwargs):
        """Log with structured context."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "context": {**self.context, **kwargs}
        }
        self.logger.log(level, log_data)
    
    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)

class MetricsCollector:
    """Metrics collection for observability."""
    
    def __init__(self):
        self.metrics = {}
    
    def record_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Record counter metric."""
        key = f"counter_{name}"
        if key not in self.metrics:
            self.metrics[key] = 0
        self.metrics[key] += value
    
    def record_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record gauge metric."""
        key = f"gauge_{name}"
        self.metrics[key] = value
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record histogram metric."""
        key = f"histogram_{name}"
        if key not in self.metrics:
            self.metrics[key] = []
        self.metrics[key].append(value)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return self.metrics
```

## Module Structure for AOS

```
AgentOperatingSystem/
├── __init__.py
├── agents/
│   ├── __init__.py
│   ├── base_agent.py              # BaseAgent class
│   ├── leadership_agent.py        # LeadershipAgent class
│   └── manager.py                 # UnifiedAgentManager
├── services/
│   ├── __init__.py
│   └── interfaces.py              # IStorageService, IMessagingService, etc.
├── storage/
│   ├── __init__.py
│   ├── manager.py                 # UnifiedStorageManager (existing)
│   └── implementations/           # Azure, local, etc.
├── messaging/
│   ├── __init__.py
│   ├── envelope.py                # MessageEnvelope
│   ├── reliability.py             # RetryPolicy, CircuitBreaker
│   └── servicebus_manager.py     # ServiceBusManager (existing)
├── orchestration/
│   ├── __init__.py
│   ├── engine.py                  # OrchestrationEngine (existing)
│   └── workflow.py                # Workflow patterns
├── monitoring/
│   ├── __init__.py
│   ├── observability.py           # StructuredLogger, MetricsCollector
│   ├── audit_trail.py             # Audit logging (existing)
│   └── health.py                  # Health check patterns
├── environment/
│   ├── __init__.py
│   └── manager.py                 # UnifiedEnvManager (existing)
├── auth/
│   ├── __init__.py
│   └── auth_handler.py            # auth_handler (existing)
└── executor/
    ├── __init__.py
    └── base_executor.py           # BaseExecutor (existing)
```

## Breaking Changes

### Import Changes
**Before**:
```python
# Various imports from different modules
```

**After**:
```python
# Clean, organized imports
from AgentOperatingSystem.agents import BaseAgent, LeadershipAgent, UnifiedAgentManager
from AgentOperatingSystem.services.interfaces import IStorageService, IMessagingService
from AgentOperatingSystem.messaging import MessageEnvelope, RetryPolicy, CircuitBreaker
from AgentOperatingSystem.monitoring import StructuredLogger, MetricsCollector
```

### Agent Class Changes
**Before**: Various agent patterns

**After**: Must extend `BaseAgent` or `LeadershipAgent`

### Service Access Changes
**Before**: Direct imports and instantiation

**After**: Use service interfaces with dependency injection

## Testing Requirements

### Unit Tests
- Test all base agent functionality
- Test agent manager lifecycle
- Test reliability patterns
- Test message envelope serialization

### Integration Tests
- Test agent registration and discovery
- Test message routing
- Test storage operations
- Test workflow execution

### Contract Tests
- Verify service interfaces
- Test backwards compatibility where needed

## Documentation Requirements

- [ ] API reference for all public classes and methods
- [ ] Architecture documentation for AOS design
- [ ] Migration guide for upgrading from previous versions
- [ ] Examples for common patterns
- [ ] Service interface contracts

## Acceptance Criteria

- [ ] All base classes and interfaces implemented
- [ ] Agent manager with lifecycle management
- [ ] Clean service interfaces defined
- [ ] Reliability patterns (retry, circuit breaker)
- [ ] Observability foundation (logging, metrics)
- [ ] All tests passing
- [ ] Documentation complete
- [ ] No business-specific code in AOS
- [ ] Breaking changes documented
- [ ] Migration guide provided

## Timeline

This is a significant refactoring that will:
1. Establish AOS as pure infrastructure
2. Enable BusinessInfinity to focus on business logic
3. Make AOS reusable for other domains
4. Improve maintainability and testability

Estimated effort: 2-3 weeks for implementation and testing.
