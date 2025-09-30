"""
Business Infinity Source Package

Enterprise Business Application built on Agent Operating System (AOS).
Provides business-specific functionality with C-Suite agents, workflow
orchestration, analytics, and governance capabilities.
"""

# Import from new business_infinity package
from .business_infinity import (
    # Core Application
    BusinessInfinity,
    BusinessInfinityConfig,
    create_business_infinity,
    get_business_infinity,
    create_default_business_infinity,
    
    # Configuration
    create_default_config,
    create_production_config,
    create_development_config,
    
    # Business Agents
    BusinessAgent,
    ChiefExecutiveOfficer,
    ChiefTechnologyOfficer,
    FounderAgent,
    
    # Workflow Management
    BusinessWorkflowManager,
    WorkflowStatus,
    
    # Analytics
    BusinessAnalyticsManager,
    BusinessMetric,
    MetricType,
    
    # Convenience Functions
    create_default_business_app,
    create_production_business_app,
    create_development_business_app,
    
    # Metadata
    __version__,
    __author__,
    __description__
)

# Backward compatibility imports for existing code
# These maintain compatibility with the old structure
from .business_infinity.core.application import BusinessInfinity as BusinessInfinity_Legacy
from .business_infinity.core.config import BusinessInfinityConfig as BusinessInfinityConfig_Legacy

# Export everything for backward compatibility
__all__ = [
    # Core Application
    "BusinessInfinity",
    "BusinessInfinityConfig", 
    "create_business_infinity",
    "get_business_infinity",
    "create_default_business_infinity",
    
    # Configuration
    "create_default_config",
    "create_production_config",
    "create_development_config",
    
    # Business Agents
    "BusinessAgent",
    "ChiefExecutiveOfficer",
    "ChiefTechnologyOfficer",
    "FounderAgent",
    
    # Workflow Management
    "BusinessWorkflowManager",
    "WorkflowStatus",
    
    # Analytics
    "BusinessAnalyticsManager",
    "BusinessMetric",
    "MetricType",
    
    # Convenience Functions
    "create_default_business_app",
    "create_production_business_app",
    "create_development_business_app",
    
    # Legacy compatibility
    "BusinessInfinity_Legacy",
    "BusinessInfinityConfig_Legacy",
    
    # Metadata
    "__version__",
    "__author__",
    "__description__"
]

# Package metadata
__version__ = __version__
__author__ = __author__
__description__ = __description__