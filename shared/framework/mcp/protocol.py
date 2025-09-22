"""
Backward compatibility module for MCP protocol
This module re-exports protocol classes from the new protocol package structure.
"""
from .protocol import MCPRequest, MCPResponse
__all__ = [
    'MCPRequest',
    'MCPResponse'
]