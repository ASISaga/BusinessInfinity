# Generic AgentOperatingSystem Runtime

A generic, reusable runtime environment for building applications on top of **AgentOperatingSystem**. This runtime provides Azure Functions integration, Microsoft Agent Framework support, and infrastructure patterns that can be used by **any** application, not just BusinessInfinity.

## Overview

This runtime layer separates **generic infrastructure** from **application-specific logic**. It provides:

- **Azure Functions Runtime**: Generic HTTP endpoint handling, lifecycle management, and route registration
- **Microsoft Agent Framework Integration**: Generic agent lifecycle and communication patterns
- **Configuration System**: Flexible, environment-aware configuration loading
- **Route Registry**: Framework-agnostic route definition and registration
- **Observability**: Structured logging, metrics, and health checks (delegated to AOS)
- **Reliability**: Circuit breakers, retry policies, idempotency (delegated to AOS)

## Architecture

```
┌─────────────────────────────────────────────────┐
│         Application Layer                      │
│  (BusinessInfinity, or any other app)          │
│                                                 │
│  • App-specific configuration                  │
│  • App-specific routes/handlers                │
│  • App-specific agents/workflows               │
│  • App-specific business logic                 │
└─────────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│         Generic Runtime Layer                   │
│  (runtime/ - reusable for any app)             │
│                                                 │
│  • AzureFunctionsRuntime                       │
│  • AgentFrameworkRuntime                       │
│  • RuntimeConfig                                │
│  • RouteRegistry                                │
└─────────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│    AgentOperatingSystem (AOS)                  │
│  (Infrastructure services)                      │
│                                                 │
│  • Storage, Messaging, ML Pipeline              │
│  • Observability, Reliability, Security        │
│  • Agent Lifecycle, State Management           │
└─────────────────────────────────────────────────┘
```

## Key Components

### 1. RuntimeConfig (`config_loader.py`)

Generic configuration system that can be extended by applications.

```python
from runtime import RuntimeConfig, load_runtime_config

# Load from environment variables
config = RuntimeConfig.from_env()

# Load from JSON file
config = RuntimeConfig.from_json("config.json")

# Create programmatically with custom settings
config = RuntimeConfig(
    app_name="MyApp",
    app_version="1.0.0",
    custom_config={
        "my_setting": "value",
        "another_setting": 123
    }
)
```

### 2. RouteRegistry (`routes_registry.py`)

Framework-agnostic route definition system.

```python
from runtime import RouteRegistry, HttpMethod, AuthLevel

registry = RouteRegistry()

# Register a route
async def my_handler(req):
    return {"message": "Hello, World!"}

registry.register(
    path="api/hello",
    handler=my_handler,
    methods=[HttpMethod.GET, HttpMethod.POST],
    auth_level=AuthLevel.ANONYMOUS,
    description="Simple hello endpoint"
)

# Or use decorator
@route(registry, "api/goodbye", methods=[HttpMethod.GET])
async def goodbye_handler(req):
    return {"message": "Goodbye!"}
```

### 3. AzureFunctionsRuntime (`azure_functions_runtime.py`)

Generic Azure Functions runtime that converts RouteRegistry routes to Azure Functions.

```python
from runtime import create_runtime, RuntimeConfig, RouteRegistry

# Setup
config = RuntimeConfig.from_env()
registry = RouteRegistry()

# Register application routes
async def health_handler(req):
    return {"status": "healthy"}

registry.register("health", health_handler)

# Create runtime
async def initialize_app():
    # Initialize your app here
    return MyApp()

runtime = create_runtime(
    config=config,
    route_registry=registry,
    app_initializer=initialize_app
)

# Get Azure Functions app
func_app = runtime.get_func_app()
```

### 4. AgentFrameworkRuntime (`agent_framework_runtime.py`)

Microsoft Agent Framework integration.

```python
from runtime import AgentFrameworkRuntime

af_runtime = AgentFrameworkRuntime(config)

# Create agents
agent = await af_runtime.create_agent("my-agent", config={...})

# Get agent
agent = af_runtime.get_agent("my-agent")
```

## Usage Examples

### Example 1: Simple Azure Functions App

```python
# my_app.py
from runtime import create_runtime, RuntimeConfig, RouteRegistry, HttpMethod
import azure.functions as func

# Configuration
config = RuntimeConfig(
    app_name="MySimpleApp",
    app_version="1.0.0",
    auth_level="FUNCTION"
)

# Route registry
registry = RouteRegistry()

# Define routes
@route(registry, "api/ping", methods=[HttpMethod.GET])
async def ping(req: func.HttpRequest):
    return func.HttpResponse('{"message": "pong"}', mimetype="application/json")

# Create runtime
runtime = create_runtime(config, registry)
runtime.register_routes_to_azure_functions()
runtime.create_startup_function()

# Export Azure Functions app
app = runtime.get_func_app()
```

### Example 2: App with Custom Initialization

```python
# my_complex_app.py
from runtime import create_runtime, RuntimeConfig, RouteRegistry
from my_app_logic import MyApplication

# Configuration
config = RuntimeConfig.from_json("config/app_config.json")

# Application initialization
async def initialize():
    app = MyApplication(config)
    await app.start()
    return app

async def shutdown():
    # Cleanup logic
    pass

# Route registry
registry = RouteRegistry()

# Create runtime with lifecycle hooks
runtime = create_runtime(
    config=config,
    route_registry=registry,
    app_initializer=initialize,
    app_shutdown=shutdown
)

# Your app instance will be available at runtime.app_instance
```

### Example 3: BusinessInfinity Using Runtime

```python
# function_app.py (for BusinessInfinity)
from runtime import create_runtime, RuntimeConfig, RouteRegistry
from src.business_infinity import create_business_infinity
from src.bi_config import load_bi_config

# Load BusinessInfinity-specific config
bi_config = load_bi_config()

# Create runtime config from BI config
runtime_config = RuntimeConfig(
    app_name="BusinessInfinity",
    app_version="2.0.0",
    custom_config=bi_config
)

# Initialize BusinessInfinity
async def initialize_bi():
    return await create_business_infinity(bi_config)

# Create runtime
runtime = create_runtime(
    config=runtime_config,
    app_initializer=initialize_bi
)

# Register BusinessInfinity routes
from src.routes import register_bi_routes
register_bi_routes(runtime.route_registry, runtime.app_instance)

# Export
app = runtime.get_func_app()
```

## Benefits

### For Application Developers

1. **Less Boilerplate**: Don't rewrite Azure Functions setup for each app
2. **Consistent Patterns**: Same patterns across all AOS apps
3. **Framework Agnostic Routes**: Define routes once, use anywhere
4. **Easy Testing**: Routes can be tested without Azure Functions infrastructure

### For the Ecosystem

1. **Reusability**: Same runtime can power multiple apps (BI, CRM, ERP, etc.)
2. **Maintainability**: Fix/improve runtime once, all apps benefit
3. **Standardization**: Consistent runtime behavior across apps
4. **Interoperability**: Apps using same runtime can interoperate easily

## Configuration

Runtime configuration can be loaded from:

1. **Environment Variables**: `RuntimeConfig.from_env()`
2. **JSON Files**: `RuntimeConfig.from_json("path/to/config.json")`
3. **Python Dict**: `RuntimeConfig.from_dict({...})`
4. **Programmatic**: `RuntimeConfig(app_name="...", ...)`

### Configuration Schema

```json
{
  "app_name": "MyApp",
  "app_version": "1.0.0",
  "app_environment": "production",
  "azure_functions_enabled": true,
  "auth_level": "FUNCTION",
  "agent_framework_enabled": false,
  "aos_enabled": true,
  "storage_type": "blob",
  "messaging_type": "servicebus",
  "observability_enabled": true,
  "log_level": "INFO",
  "circuit_breaker_enabled": true,
  "retry_enabled": true,
  "max_retries": 3,
  "custom_config": {
    "your_custom_settings": "here"
  }
}
```

## Extending the Runtime

To add new capabilities to the runtime:

1. Add new configuration fields to `RuntimeConfig`
2. Create new runtime modules (e.g., `kafka_runtime.py`)
3. Extend `AzureFunctionsRuntime` or create new runtime classes
4. Keep it **generic** - avoid app-specific logic

## Migration Guide

### From Legacy Azure Functions Code

**Before (legacy):**
```python
# function_app.py
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="health")
async def health(req: func.HttpRequest):
    return func.HttpResponse("OK")
```

**After (using runtime):**
```python
from runtime import create_runtime, RuntimeConfig, RouteRegistry

config = RuntimeConfig.from_env()
registry = RouteRegistry()

async def health(req):
    return {"status": "ok"}

registry.register("health", health)
runtime = create_runtime(config, registry)
runtime.register_routes_to_azure_functions()

app = runtime.get_func_app()
```

## Testing

The runtime is designed to be testable:

```python
# test_my_app.py
from runtime import RouteRegistry, RuntimeConfig
import pytest

@pytest.fixture
def registry():
    return RouteRegistry()

@pytest.fixture
def config():
    return RuntimeConfig(app_name="TestApp")

async def test_route_registration(registry):
    async def test_handler(req):
        return {"test": "ok"}
    
    route = registry.register("test", test_handler)
    assert route.path == "test"
    assert registry.get_route("test") is not None
```

## License

Same as BusinessInfinity/AgentOperatingSystem.

## Contributing

When contributing to the runtime:

1. Keep it **generic** - no app-specific code
2. Maintain **backward compatibility** when possible
3. Add **tests** for new features
4. Update **documentation**
5. Follow existing **code style**
