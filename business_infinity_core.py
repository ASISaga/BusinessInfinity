"""
Business Infinity Core Module

This module provides the main entry points and coordination for the refactored
Business Infinity application built on AOS foundation.
"""

from .business_infinity_refactored import (
    BusinessInfinity,
    BusinessInfinityConfig,
    create_business_infinity,
    create_default_business_infinity
)

from .business_agents_refactored import (
    BusinessAgent,
    BusinessCEO,
    BusinessCFO, 
    BusinessCTO,
    BusinessFounder,
    BusinessInvestor
)

from .business_workflows import BusinessWorkflowEngine, WorkflowStatus
from .business_analytics import BusinessAnalyticsEngine, BusinessMetric, MetricType

# Export main classes and functions
__all__ = [
    # Core Business Application
    "BusinessInfinity",
    "BusinessInfinityConfig", 
    "create_business_infinity",
    "create_default_business_infinity",
    
    # Business Agents
    "BusinessAgent",
    "BusinessCEO",
    "BusinessCFO",
    "BusinessCTO", 
    "BusinessFounder",
    "BusinessInvestor",
    
    # Business Engines
    "BusinessWorkflowEngine",
    "BusinessAnalyticsEngine",
    
    # Supporting Classes
    "WorkflowStatus",
    "BusinessMetric", 
    "MetricType"
]