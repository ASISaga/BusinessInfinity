"""
BusinessInfinity - Enterprise Business Application

BusinessInfinity is an enterprise business application built on top of the
Agent Operating System (AOS). It provides business-specific functionality
including C-Suite agents, workflow orchestration, analytics, and governance.

This package uses the generic runtime layer for all infrastructure concerns
and focuses purely on business logic.

Key Components:
    - BusinessInfinity: Main application orchestrator
    - BusinessInfinityConfig: Application configuration
    - Handlers: HTTP route handlers
    - Agents: C-Suite agents with domain expertise
    - AOSServiceBusClient: Client for communicating with AOS via Service Bus
"""

from .app import (
    AgentInfo,
    BusinessInfinity,
    WorkflowInfo,
    create_business_infinity,
    get_business_infinity,
    set_business_infinity,
)
from .config import (
    BusinessInfinityConfig,
    create_default_config,
    create_development_config,
    create_production_config,
    load_bi_config,
)
from .handlers import (
    AgentsHandler,
    HealthHandler,
    MCPHandler,
    WorkflowsHandler,
    register_routes,
)

# AOS Service Bus Client (for distributed deployment)
try:
    from .aos_client import AOSServiceBusClient, AOS_CLIENT_AVAILABLE
except ImportError:
    AOS_CLIENT_AVAILABLE = False
    AOSServiceBusClient = None  # type: ignore

__version__ = "2.0.0"
__author__ = "ASISaga"
__description__ = "Enterprise Business Application on AgentOperatingSystem"

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__description__",
    # Core Application
    "BusinessInfinity",
    "AgentInfo",
    "WorkflowInfo",
    "create_business_infinity",
    "get_business_infinity",
    "set_business_infinity",
    # Configuration
    "BusinessInfinityConfig",
    "load_bi_config",
    "create_default_config",
    "create_production_config",
    "create_development_config",
    # Handlers
    "HealthHandler",
    "AgentsHandler",
    "WorkflowsHandler",
    "MCPHandler",
    "register_routes",
    # AOS Service Bus Client
    "AOSServiceBusClient",
    "AOS_CLIENT_AVAILABLE",
]