"""
Business Infinity Agents

Business-specific agent implementations that extend the BusinessAgent base class
with specialized C-Suite capabilities.

Architecture:
    ┌───────────────────────────────────┐
    │      BusinessInfinity Agents      │
    │  CEO, CTO, Founder (specialized)  │
    └───────────────────────────────────┘
                    ▼
    ┌───────────────────────────────────┐
    │         BusinessAgent             │
    │  (external package - Boardroom)   │
    └───────────────────────────────────┘
                    ▼
    ┌───────────────────────────────────┐
    │      AgentOperatingSystem         │
    │  (core infrastructure)            │
    └───────────────────────────────────┘
"""

# Agent coordinator (local module)
from .agent_coordinator import AgentCoordinator, AgentQuery, AgentResponse

# Specialized C-Suite agents (local implementations)
from .ceo import ChiefExecutiveOfficer
from .cto import ChiefTechnologyOfficer
from .founder import FounderAgent

# Try importing external BusinessAgent package
try:
    from BusinessAgent import BusinessAgent
    BUSINESS_AGENT_AVAILABLE = True
except ImportError:
    BusinessAgent = None
    BUSINESS_AGENT_AVAILABLE = False


__all__ = [
    # Coordination
    "AgentCoordinator",
    "AgentQuery",
    "AgentResponse",
    # C-Suite agents
    "ChiefExecutiveOfficer",
    "ChiefTechnologyOfficer",
    "FounderAgent",
    # External package (optional)
    "BusinessAgent",
    "BUSINESS_AGENT_AVAILABLE",
]