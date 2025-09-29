"""
Business Infinity Network Module

Implements the Global Network of Autonomous Boardrooms as specified in /network/specification.md

This module provides:
- Inter-boardroom communication protocols
- LinkedIn-verified enterprise authentication  
- Network discovery and directory services
- Covenant ledger for inter-boardroom agreements
- Network monitoring and analytics

Based on the A2A (Agent-to-Agent) protocol foundation, extended for 
boardroom-to-boardroom federation and planetary governance.
"""

from .network_protocol import NetworkProtocol, BoardroomNode, InterBoardroomMessage
from .verification import LinkedInVerificationService, EnterpriseIdentity
from .discovery import NetworkDiscovery, BoardroomDirectory
from .covenant_ledger import CovenantLedger, InterBoardroomAgreement

__all__ = [
    'NetworkProtocol',
    'BoardroomNode', 
    'InterBoardroomMessage',
    'LinkedInVerificationService',
    'EnterpriseIdentity',
    'NetworkDiscovery',
    'BoardroomDirectory',
    'CovenantLedger',
    'InterBoardroomAgreement'
]