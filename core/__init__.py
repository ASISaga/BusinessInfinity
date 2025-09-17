"""
Core Business Infinity System
Consolidated core functionality for all features

This module consolidates:
- Server functionality (FastAPI + WebSocket MCP + Static files)
- Agent management (Operational, AML, Semantic agents)
- MCP communication (Multi-Agent Communication Protocol)
- Orchestration (Workflows, coordination, decision engine)
- Authentication and authorization
- Triggers and event processing
- Azure Functions integration
- Utilities and governance
- Feature modules (Storage, ML, Environment, API)
"""

# Import main components
from .server import unified_server, app as server_app
from .agents import agent_manager, UnifiedAgentManager
from .mcp import mcp_handler, handle_mcp
from .orchestrator import orchestrator, process_decision, coordinate_agents

# Import consolidated modules
from .auth import auth_handler, UnifiedAuthHandler
from .triggers import triggers_manager, UnifiedTriggersManager
from .utils import utils_manager, UnifiedUtilsManager, validate_request, get_ui_schema
from .azure_functions import consolidated_functions, register_consolidated_functions

# Import feature modules
from .features import storage_manager, ml_manager, env_manager, api_orchestrator

# Export all major components
__all__ = [
    # Server components
    'unified_server',
    'server_app', 
    
    # Agent components
    'agent_manager',
    'UnifiedAgentManager',
    
    # MCP components  
    'mcp_handler',
    'handle_mcp',
    
    # Orchestration components
    'orchestrator',
    'process_decision',
    'coordinate_agents',
    
    # Authentication components
    'auth_handler',
    'UnifiedAuthHandler',
    
    # Triggers and event processing
    'triggers_manager',
    'UnifiedTriggersManager',
    
    # Azure Functions integration
    'consolidated_functions',
    'register_consolidated_functions',
    
    # Utilities and governance
    'utils_manager',
    'UnifiedUtilsManager',
    'validate_request',
    'get_ui_schema',
    
    # Feature modules
    'storage_manager',
    'ml_manager', 
    'env_manager',
    'api_orchestrator'
]