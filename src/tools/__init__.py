"""
BusinessInfinity Package

Modern business intelligence and autonomous agent management system
built on the Agent Operating System (AOS) infrastructure.
"""

from .audit_viewer import BusinessAuditViewer
from ..orchestration.business_manager import create_business_manager, BusinessManager
from ..agents.agent_coordinator import AgentCoordinator

__all__ = [
    "BusinessAuditViewer",
    "create_business_manager",
    "BusinessManager", 
    "AgentCoordinator",
    "BusinessAuditViewer"
]

__version__ = "2.0.0"