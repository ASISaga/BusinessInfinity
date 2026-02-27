"""
AgentOperatingSystem Runtime - Generic Infrastructure Layer

This package provides a generic, reusable runtime environment for building
applications on top of AgentOperatingSystem. It includes:

- Azure Functions integration and lifecycle management
- Microsoft Agent Framework integration
- Generic route registration and handling
- Configuration loading and management
- Service Bus integration
- Storage and messaging abstractions
- Observability and monitoring (via AOS)
- Reliability patterns (via AOS)

Usage:
    from runtime import (
        create_runtime,
        RuntimeConfig,
        RouteRegistry,
        HttpMethod,
        AuthLevel,
    )
    
    config = RuntimeConfig.from_env()
    registry = RouteRegistry()
    runtime = create_runtime(config, registry)
    app = runtime.get_func_app()
"""

from .config_loader import RuntimeConfig, load_runtime_config, merge_configs
from .routes_registry import (
    RouteRegistry,
    Route,
    RouteHandler,
    HttpMethod,
    AuthLevel,
    route,
)
from .azure_functions_runtime import AzureFunctionsRuntime, create_runtime
from .agent_framework_runtime import (
    AgentFrameworkRuntime,
    create_agent_framework_runtime,
)
from .servicebus_runtime import (
    ServiceBusRuntime,
    ServiceBusRegistry,
    MessageType,
    MessageHandler,
    MessageRoute,
    create_servicebus_runtime,
)
from .storage import (
    IStorageProvider,
    MemoryStorageProvider,
    AOSStorageProvider,
    create_storage_provider,
)
from .messaging import (
    IMessagingProvider,
    MemoryMessagingProvider,
    AOSMessagingProvider,
    Message,
    MessageCallback,
    create_messaging_provider,
)

__version__ = "2.0.0"

__all__ = [
    # Version
    "__version__",
    # Azure Functions Runtime
    "AzureFunctionsRuntime",
    "create_runtime",
    # Configuration
    "RuntimeConfig",
    "load_runtime_config",
    "merge_configs",
    # Route Registry
    "RouteRegistry",
    "Route",
    "RouteHandler",
    "HttpMethod",
    "AuthLevel",
    "route",
    # Agent Framework
    "AgentFrameworkRuntime",
    "create_agent_framework_runtime",
    # Service Bus
    "ServiceBusRuntime",
    "ServiceBusRegistry",
    "MessageType",
    "MessageHandler",
    "MessageRoute",
    "create_servicebus_runtime",
    # Storage
    "IStorageProvider",
    "MemoryStorageProvider",
    "AOSStorageProvider",
    "create_storage_provider",
    # Messaging
    "IMessagingProvider",
    "MemoryMessagingProvider",
    "AOSMessagingProvider",
    "Message",
    "MessageCallback",
    "create_messaging_provider",
]

