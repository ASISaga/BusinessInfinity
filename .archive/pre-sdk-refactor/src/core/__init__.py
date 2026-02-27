"""
Core Business Infinity System

Core supporting components for Business Infinity application.

NOTE: Main application classes (BusinessInfinity, BusinessInfinityConfig) are now 
defined in src/app.py and src/config.py respectively. This module provides 
additional supporting functionality.

This module provides:
- Covenant management (compliance and governance)
- Conversation management
- Agent management utilities
- MCP access control
- Observability and reliability patterns
- Service interfaces
"""

# Core supporting managers
from .covenant_manager import BusinessCovenantManager
from .conversation_manager import BusinessConversationManager

# Try importing agent utilities
try:
    from .agents import UnifiedAgentManager, get_unified_manager, initialize_unified_manager
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    UnifiedAgentManager = None
    get_unified_manager = None
    initialize_unified_manager = None

# Try importing utilities
try:
    from .utils import utils_manager, UnifiedUtilsManager, validate_request, get_ui_schema
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    utils_manager = None
    UnifiedUtilsManager = None
    validate_request = None
    get_ui_schema = None

# Try importing feature modules
try:
    from .features import storage_manager, env_manager, api_orchestrator
    FEATURES_AVAILABLE = True
except ImportError:
    FEATURES_AVAILABLE = False
    storage_manager = None
    env_manager = None
    api_orchestrator = None


# Export all major components
__all__ = [
    # Core Managers
    "BusinessCovenantManager",
    "BusinessConversationManager",
    
    # Agent components (optional)
    "UnifiedAgentManager",
    "get_unified_manager",
    "initialize_unified_manager",
    
    # Utilities (optional)
    "utils_manager",
    "UnifiedUtilsManager",
    "validate_request",
    "get_ui_schema",
    
    # Feature modules (optional)
    "storage_manager",
    "env_manager",
    "api_orchestrator",
    
    # Availability flags
    "AGENTS_AVAILABLE",
    "UTILS_AVAILABLE",
    "FEATURES_AVAILABLE",
]