"""
Business Infinity - Enterprise Business Application

Business Infinity is an enterprise business application built on top of the
Agent Operating System (AOS). It provides business-specific functionality
including C-Suite agents, workflow orchestration, analytics, and governance.

Key Components:
- BusinessInfinity: Main application orchestrator
- Business Agents: C-Suite agents with domain expertise
- Workflow Management: Strategic decision-making processes
- Analytics Engine: KPIs, metrics, and business intelligence
- Covenant Management: Governance and compliance
"""

from ...src.orchestration.business_manager import create_business_manager, BusinessManager, BusinessAgent, BusinessTask

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

# Convenience functions for quick setup (from 1.py)
def create_default_business_app():
    """Create a Business Infinity application with default configuration."""
    config = create_default_config()
    return create_business_infinity(config)

def create_production_business_app():
    """Create a Business Infinity application with production configuration."""
    config = create_production_config()
    return create_business_infinity(config)

def create_development_business_app():
    """Create a Business Infinity application with development configuration."""
    config = create_development_config()
    return create_business_infinity(config)

# Backward compatibility imports for existing code
# These maintain compatibility with the old structure
from .business_infinity.core.application import BusinessInfinity as BusinessInfinity_Legacy
from .business_infinity.core.config import BusinessInfinityConfig as BusinessInfinityConfig_Legacy

# Export everything for backward compatibility and public API (merged from 1.py and previous __all__)
__all__ = [
    "create_business_manager",
    "BusinessManager",
    "BusinessAgent", 
    "BusinessTask",
    
    # Core Application
    "BusinessInfinity",
    "BusinessInfinityConfig",
    "create_business_infinity",
    "get_business_infinity",
    "create_default_business_infinity",

    # Configuration Factory Functions
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

# Package metadata (already imported from .business_infinity)