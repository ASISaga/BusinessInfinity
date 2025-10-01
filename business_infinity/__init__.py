"""
BusinessInfinity Package

Modern business intelligence and autonomous agent management system
built on the Agent Operating System (AOS) infrastructure.
"""

from .core.business_manager import create_business_manager, BusinessManager
from .agents.agent_coordinator import AgentCoordinator
from .tools.audit_viewer import BusinessAuditViewer

__all__ = [
    "create_business_manager",
    "BusinessManager", 
    "AgentCoordinator",
    "BusinessAuditViewer"
]

__version__ = "2.0.0"