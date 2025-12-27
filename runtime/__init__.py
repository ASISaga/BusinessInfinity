"""
Generic Agent Operating System Runtime

This package provides a generic, reusable runtime environment for building
applications on top of AgentOperatingSystem. It includes:

- Azure Functions integration and lifecycle management
- Microsoft Agent Framework integration
- Generic route registration and handling
- Configuration loading and management
- Observability and monitoring
- Reliability patterns (circuit breaker, retry, etc.)

This runtime can be used to build multiple applications (not just BusinessInfinity)
that run on AgentOperatingSystem with Azure Functions and Microsoft Agent Framework.
"""

from .azure_functions_runtime import AzureFunctionsRuntime, create_runtime
from .config_loader import RuntimeConfig, load_runtime_config
from .routes_registry import RouteRegistry, Route, RouteHandler, HttpMethod, AuthLevel, route
from .agent_framework_runtime import AgentFrameworkRuntime, create_agent_framework_runtime

__all__ = [
    'AzureFunctionsRuntime',
    'create_runtime',
    'RuntimeConfig',
    'load_runtime_config',
    'RouteRegistry',
    'Route',
    'RouteHandler',
    'HttpMethod',
    'AuthLevel',
    'route',
    'AgentFrameworkRuntime',
    'create_agent_framework_runtime',
]
