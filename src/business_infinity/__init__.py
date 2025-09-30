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

# Core Application
from .core import (
    BusinessInfinity,
    BusinessInfinityConfig,
    create_business_infinity,
    get_business_infinity,
    create_default_business_infinity,
    create_default_config,
    create_production_config,
    create_development_config
)

# Business Agents
from .agents import (
    BusinessAgent,
    ChiefExecutiveOfficer,
    ChiefTechnologyOfficer, 
    FounderAgent
)

# Workflow Management
from .workflows import (
    BusinessWorkflowManager,
    WorkflowStatus
)

# Analytics
from .analytics import (
    BusinessAnalyticsManager,
    BusinessMetric,
    MetricType
)

# Version information
__version__ = "2.0.0"
__author__ = "Business Infinity Team"
__description__ = "Enterprise Business Application built on AOS"

# Public API
__all__ = [
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
    
    # Metadata
    "__version__",
    "__author__",
    "__description__"
]

# Convenience functions for quick setup
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

# Add convenience functions to __all__
__all__.extend([
    "create_default_business_app",
    "create_production_business_app", 
    "create_development_business_app"
])