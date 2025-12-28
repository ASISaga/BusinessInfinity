"""
BusinessInfinity MCP Executors

Executors that integrate with MCP (Model Context Protocol) servers
to provide enterprise system integration capabilities.

Available Executors:
- ERPExecutor: Enterprise Resource Planning integration
- CRMExecutor: Customer Relationship Management integration
- LinkedInExecutor: LinkedIn API integration
"""

from .ERPExecutor import ERPExecutor
from .CRMExecutor import CRMExecutor
from .LinkedInExecutor import LinkedInExecutor


__all__ = [
    "ERPExecutor",
    "CRMExecutor",
    "LinkedInExecutor",
]
