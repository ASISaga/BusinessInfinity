"""
Core Framework package - provides framework components

This package contains framework-level components including:
- Adapters for training and inference
- MCP (Model Context Protocol) components  
- Server components
- Function handlers
"""

# Import key framework components
try:
    from .server import governance, decision_engine, azure_ml
except ImportError:
    pass

try:
    from .mcp import protocol
except ImportError:
    pass

__all__ = [
    'governance',
    'decision_engine', 
    'azure_ml',
    'protocol'
]