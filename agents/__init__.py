"""
Business Infinity Agents Module

This module contains all business-specific agents for Business Infinity,
inheriting from the generic LeadershipAgent in AOS (Agent Operating System).

All agents follow the one-class-per-file architecture and implement
business-specific functionality while leveraging the generic orchestration
capabilities provided by AOS.
"""

# Import all business-specific agents
from .ChiefExecutiveOfficer import ChiefExecutiveOfficer
from .ChiefFinancialOfficer import ChiefFinancialOfficer
from .ChiefMarketingOfficer import ChiefMarketingOfficer
from .ChiefOperatingOfficer import ChiefOperatingOfficer
from .ChiefTechnologyOfficer import ChiefTechnologyOfficer
from .ChiefHumanResourcesOfficer import ChiefHumanResourcesOfficer
from .FounderAgent import FounderAgent
from .InvestorAgent import InvestorAgent

# Define agent registry for easy access
AGENT_REGISTRY = {
    "CEO": ChiefExecutiveOfficer,
    "CFO": ChiefFinancialOfficer,
    "CMO": ChiefMarketingOfficer,
    "COO": ChiefOperatingOfficer,
    "CTO": ChiefTechnologyOfficer,
    "CHRO": ChiefHumanResourcesOfficer,
    "Founder": FounderAgent,
    "Investor": InvestorAgent
}

# Define all exports
__all__ = [
    'ChiefExecutiveOfficer',
    'ChiefFinancialOfficer', 
    'ChiefMarketingOfficer',
    'ChiefOperatingOfficer',
    'ChiefTechnologyOfficer',
    'ChiefHumanResourcesOfficer',
    'FounderAgent',
    'InvestorAgent',
    'AGENT_REGISTRY'
]