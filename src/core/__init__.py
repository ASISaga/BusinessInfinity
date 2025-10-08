"""
Core Business Infinity System
Consolidated core functionality for all features

Core components for Business Infinity application including
configuration, application orchestration, and supporting managers.

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

from .application import BusinessInfinity, create_business_infinity, get_business_infinity, create_default_business_infinity
from .config import BusinessInfinityConfig, create_default_config, create_production_config, create_development_config
from .covenant_manager import BusinessCovenantManager
from .conversation_manager import BusinessConversationManager


# Remove broken imports for missing modules
# from .server import unified_server, app as server_app
from .agents import UnifiedAgentManager, get_unified_manager, initialize_unified_manager, ask_agent, get_agent_profiles_json, get_agent_by_name
# from .mcp import mcp_handler, handle_mcp
# from .BusinessInfinityOrchestrator import BusinessInfinityOrchestrator, process_decision, coordinate_agents
# from .auth import auth_handler, UnifiedAuthHandler
# from .triggers import triggers_manager, UnifiedTriggersManager
from .utils import utils_manager, UnifiedUtilsManager, validate_request, get_ui_schema
# from .azure_functions import consolidated_functions, register_consolidated_functions

# Import feature modules correctly
from .features import storage_manager, env_manager, api_orchestrator

# Export all major components
__all__ = [
    # Main Application
    "BusinessInfinity",
    "create_business_infinity",
    "get_business_infinity", 
    "create_default_business_infinity",
    
    # Configuration
    "BusinessInfinityConfig",
    "create_default_config",
    "create_production_config",
    "create_development_config",
    
    # Core Managers
    "BusinessCovenantManager",
    "BusinessConversationManager",

    # Audit trail system
    'audit_trail',
    'mcp_access_control',
    'businessinfinity_config_mcp_stub',

    # Agent components
    'UnifiedAgentManager',
    'get_unified_manager',
    'initialize_unified_manager',
    'ask_agent',
    'get_agent_profiles_json',
    'get_agent_by_name',
    
    # Utilities and governance
    'utils_manager',
    'UnifiedUtilsManager',
    'validate_request',
    'get_ui_schema',
    
    # Feature modules
    'storage_manager',
    'env_manager',
    'api_orchestrator'
]