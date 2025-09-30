"""
Business Infinity Core

Core components for Business Infinity application including
configuration, application orchestration, and supporting managers.
"""

from .application import BusinessInfinity, create_business_infinity, get_business_infinity, create_default_business_infinity
from .config import BusinessInfinityConfig, create_default_config, create_production_config, create_development_config
from .covenant_manager import BusinessCovenantManager
from .conversation_manager import BusinessConversationManager

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
    "BusinessConversationManager"
]