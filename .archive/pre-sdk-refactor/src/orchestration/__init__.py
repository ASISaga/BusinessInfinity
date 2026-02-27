"""
BusinessInfinity Orchestration Module

Provides business workflow orchestration, decision integration, and boardroom
coordination capabilities.

Architecture:
    ┌───────────────────────────────────────────────┐
    │     BusinessBoardroomOrchestrator             │
    │  High-level C-Suite workflow coordination     │
    └───────────────────────────────────────────────┘
                         ▼
    ┌───────────────────────────────────────────────┐
    │         DecisionIntegrator                    │
    │  Governance, voting, consensus logic          │
    └───────────────────────────────────────────────┘
                         ▼
    ┌───────────────────────────────────────────────┐
    │         DecisionLedger                        │
    │  Persistent JSONL decision storage            │
    └───────────────────────────────────────────────┘
"""

# Decision logging (no external dependencies)
from .DecisionLedger import DecisionLedger

# Try importing components with external dependencies
try:
    from .BusinessBoardroomOrchestrator import BusinessBoardroomOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    BusinessBoardroomOrchestrator = None
    ORCHESTRATOR_AVAILABLE = False

try:
    from .DecisionIntegrator import DecisionIntegrator
    DECISION_INTEGRATOR_AVAILABLE = True
except ImportError:
    DecisionIntegrator = None
    DECISION_INTEGRATOR_AVAILABLE = False

try:
    from .business_manager import BusinessManager
    BUSINESS_MANAGER_AVAILABLE = True
except ImportError:
    BusinessManager = None
    BUSINESS_MANAGER_AVAILABLE = False


__all__ = [
    # Always available
    "DecisionLedger",
    # Optional - require external packages
    "BusinessBoardroomOrchestrator",
    "DecisionIntegrator",
    "BusinessManager",
    # Availability flags
    "ORCHESTRATOR_AVAILABLE",
    "DECISION_INTEGRATOR_AVAILABLE",
    "BUSINESS_MANAGER_AVAILABLE",
]
