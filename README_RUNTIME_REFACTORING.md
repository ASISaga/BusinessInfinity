# BusinessInfinity Runtime Refactoring

## Overview

BusinessInfinity has been refactored to separate **generic runtime infrastructure** from **BusinessInfinity-specific configuration and business logic**. This enables:

1. **Reusable Runtime**: The `runtime/` package can be used to build **any** application on AgentOperatingSystem, not just BusinessInfinity
2. **Configuration-Driven**: BusinessInfinity is now primarily configuration-driven with minimal custom code
3. **Clear Separation**: Generic infrastructure vs. business logic is clearly separated
4. **Easier Maintenance**: Runtime improvements benefit all applications using it

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 BusinessInfinity Application               │
│  (src/ - Business-specific code and configuration)         │
├─────────────────────────────────────────────────────────────┤
│  • bi_config.py - BI-specific configuration                │
│  • business_infinity.py - BI application logic             │
│  • agents/ - C-Suite agents (CEO, CFO, CTO, etc.)          │
│  • routes/ - HTTP endpoint handlers                        │
│  • workflows/ - Business workflows                         │
│  • analytics/ - Business analytics and KPIs                │
│  • network/ - Covenant and network management              │
└─────────────────────────────────────────────────────────────┘
                          ▼ uses
┌─────────────────────────────────────────────────────────────┐
│           Generic Runtime (runtime/)                       │
│  (Reusable for ANY app on AgentOperatingSystem)            │
├─────────────────────────────────────────────────────────────┤
│  • config_loader.py - Generic configuration system         │
│  • routes_registry.py - Framework-agnostic route registry  │
│  • azure_functions_runtime.py - Azure Functions wrapper    │
│  • agent_framework_runtime.py - Agent Framework wrapper    │
└─────────────────────────────────────────────────────────────┘
                          ▼ uses
┌─────────────────────────────────────────────────────────────┐
│        AgentOperatingSystem (External Dependency)          │
│  (Infrastructure services - storage, messaging, etc.)       │
└─────────────────────────────────────────────────────────────┘
```

## What's New

### 1. Generic Runtime Package (`runtime/`)

A new **reusable runtime environment** that provides:

- **RuntimeConfig**: Generic configuration loading from env vars, JSON, or code
- **RouteRegistry**: Framework-agnostic route registration system
- **AzureFunctionsRuntime**: Generic Azure Functions app wrapper
- **AgentFrameworkRuntime**: Microsoft Agent Framework integration

**Key Point**: This runtime can be used by **any** application, not just BusinessInfinity. Examples:
- A CRM application built on AOS
- An ERP application built on AOS
- A custom business application

See `runtime/README.md` for detailed documentation.

### 2. BusinessInfinity Configuration (`src/bi_config.py`)

BusinessInfinity-specific configuration that extends `RuntimeConfig`:

```python
from runtime import RuntimeConfig
from src.bi_config import load_bi_config

# Load BI config
bi_config = load_bi_config()

# Convert to runtime config
runtime_config = bi_config.to_runtime_config()
```

Configuration includes:
- Company identity (name, domain, industry)
- Enabled C-Suite agents
- Boardroom settings
- Covenant and compliance settings
- Feature flags (mentor mode, onboarding, etc.)

### 3. Runtime-Based Function App (`function_app_runtime.py`)

New Azure Functions app that uses the generic runtime:

```python
from runtime import create_runtime
from src.bi_config import load_bi_config

# Load config
config = load_bi_config()

# Create runtime
runtime = create_runtime(
    config=config.to_runtime_config(),
    app_initializer=initialize_business_infinity,
    app_shutdown=shutdown_business_infinity
)

# Register routes
register_bi_routes(runtime.route_registry, bi_app)

# Get Azure Functions app
app = runtime.get_func_app()
```

## Migration Guide

### For BusinessInfinity Developers

**No immediate changes required**. The existing `function_app.py` still works. However, you can:

1. **Use the new runtime** by switching to `function_app_runtime.py`
2. **Configure via environment** instead of code
3. **Add new routes** using the route registry instead of decorators

### For New Applications

To build a new application on the runtime:

1. **Install dependencies**:
   ```bash
   pip install azure-functions agent-framework
   ```

2. **Create your config**:
   ```python
   # my_app_config.py
   from runtime import RuntimeConfig
   
   config = RuntimeConfig(
       app_name="MyApp",
       app_version="1.0.0",
       custom_config={
           "my_setting": "value"
       }
   )
   ```

3. **Create your app**:
   ```python
   # my_app.py
   class MyApp:
       def __init__(self, config):
           self.config = config
       
       async def start(self):
           print("MyApp started!")
   ```

4. **Create function app**:
   ```python
   # function_app.py
   from runtime import create_runtime, RouteRegistry
   from my_app import MyApp
   from my_app_config import config
   
   async def init_app():
       app = MyApp(config)
       await app.start()
       return app
   
   registry = RouteRegistry()
   
   # Register routes
   async def health(req):
       return {"status": "healthy"}
   
   registry.register("health", health)
   
   # Create runtime
   runtime = create_runtime(
       config=config,
       route_registry=registry,
       app_initializer=init_app
   )
   
   runtime.register_routes_to_azure_functions()
   runtime.create_startup_function()
   
   app = runtime.get_func_app()
   ```

## Key Benefits

### 1. Reusability

The runtime can power multiple applications:
- BusinessInfinity (C-Suite agents, boardroom)
- CRM application (customer agents, sales workflows)
- ERP application (inventory agents, procurement workflows)
- Custom business apps

### 2. Maintainability

- **One Runtime**: Fix bugs once, all apps benefit
- **Consistent Patterns**: Same patterns across all AOS apps
- **Clear Boundaries**: Generic vs. specific code is clearly separated

### 3. Testability

- **Framework-Agnostic Routes**: Test routes without Azure Functions
- **Mockable Configuration**: Easy to test with different configs
- **Isolated Components**: Runtime, config, and business logic are separate

### 4. Flexibility

- **Configuration-Driven**: Change behavior via config, not code
- **Feature Flags**: Enable/disable features easily
- **Multiple Environments**: Dev, staging, prod configs

## File Structure

```
BusinessInfinity/
├── runtime/                          # NEW: Generic runtime package
│   ├── __init__.py
│   ├── README.md                     # Runtime documentation
│   ├── config_loader.py              # Generic configuration
│   ├── routes_registry.py            # Generic route system
│   ├── azure_functions_runtime.py    # Azure Functions wrapper
│   └── agent_framework_runtime.py    # Agent Framework wrapper
│
├── src/
│   ├── bi_config.py                  # NEW: BI-specific configuration
│   ├── business_infinity.py          # Updated to use runtime patterns
│   ├── agents/                       # C-Suite agents
│   ├── routes/                       # Route handlers
│   ├── workflows/                    # Business workflows
│   ├── analytics/                    # Business analytics
│   ├── network/                      # Covenant management
│   └── ...
│
├── function_app.py                   # Existing function app (still works)
├── function_app_runtime.py           # NEW: Runtime-based function app
├── pyproject.toml                    # Dependencies
└── README_RUNTIME_REFACTORING.md     # This file
```

## Configuration Examples

### Environment Variables

```bash
# Runtime Configuration
APP_NAME=BusinessInfinity
APP_VERSION=2.0.0
APP_ENVIRONMENT=production
AUTH_LEVEL=FUNCTION
AOS_ENABLED=true

# Storage and Messaging
STORAGE_TYPE=blob
MESSAGING_TYPE=servicebus
STORAGE_CONNECTION_STRING=...
MESSAGING_CONNECTION_STRING=...

# BusinessInfinity Configuration
COMPANY_NAME="Acme Corp"
COMPANY_DOMAIN=acme.com
BOARDROOM_ENABLED=true
COVENANT_ENABLED=true
MENTOR_MODE_ENABLED=true
```

### JSON Configuration

```json
{
  "runtime_config": {
    "app_name": "BusinessInfinity",
    "app_version": "2.0.0",
    "app_environment": "production",
    "azure_functions_enabled": true,
    "auth_level": "FUNCTION",
    "aos_enabled": true,
    "storage_type": "blob",
    "messaging_type": "servicebus",
    "observability_enabled": true,
    "circuit_breaker_enabled": true
  },
  "company_name": "Acme Corp",
  "company_domain": "acme.com",
  "enabled_agents": ["ceo", "cfo", "cto"],
  "boardroom_enabled": true,
  "covenant_enabled": true,
  "mentor_mode_enabled": true
}
```

## Testing

### Testing Routes

```python
# test_routes.py
from runtime import RouteRegistry
import pytest

@pytest.fixture
def registry():
    return RouteRegistry()

async def test_health_route(registry):
    async def health(req):
        return {"status": "healthy"}
    
    route = registry.register("health", health)
    assert route.path == "health"
    
    # Test handler
    result = await health(None)
    assert result["status"] == "healthy"
```

### Testing Configuration

```python
# test_config.py
from src.bi_config import BusinessInfinityConfig

def test_bi_config_defaults():
    config = BusinessInfinityConfig()
    assert config.company_name == "Business Infinity"
    assert config.boardroom_enabled == True

def test_bi_config_from_dict():
    config = BusinessInfinityConfig.from_dict({
        "company_name": "Test Corp",
        "boardroom_enabled": False
    })
    assert config.company_name == "Test Corp"
    assert config.boardroom_enabled == False
```

## Performance Considerations

The runtime introduces minimal overhead:

- **Route Registry**: O(1) lookup by path
- **Configuration**: Loaded once at startup
- **Azure Functions Wrapping**: Thin wrapper, negligible overhead

## Security

The runtime maintains all security features:

- **Authentication Levels**: ANONYMOUS, FUNCTION, ADMIN
- **Environment-Based Secrets**: Secrets loaded from env vars
- **MCP Access Control**: Unchanged, still enforced
- **Audit Logging**: Delegated to AOS

## Future Enhancements

Potential future improvements to the runtime:

1. **FastAPI Support**: Add FastAPI runtime alongside Azure Functions
2. **Kubernetes Runtime**: Deploy as K8s services
3. **OpenAPI Generation**: Auto-generate OpenAPI specs from routes
4. **Hot Reload**: Reload routes without restart (dev mode)
5. **Middleware System**: Generic middleware for auth, logging, etc.

## FAQ

### Q: Do I need to migrate to the new runtime?

**A**: No, the existing `function_app.py` still works. The runtime is optional but recommended for new code.

### Q: Can I use the runtime for non-Azure applications?

**A**: Yes! The `RouteRegistry` and `RuntimeConfig` are framework-agnostic. You can create a FastAPI runtime, Flask runtime, etc.

### Q: Will the runtime work with existing AOS versions?

**A**: Yes, the runtime depends on AOS but doesn't require specific AOS changes.

### Q: How do I add a new route?

**A**: Register it in the route registry:
```python
registry.register("my/route", my_handler, methods=[HttpMethod.GET])
```

### Q: Can I still use Azure Functions decorators?

**A**: Yes, but we recommend using the route registry for consistency.

## Contributing

When contributing to the runtime:

1. **Keep it generic** - No BusinessInfinity-specific code in `runtime/`
2. **Add tests** - Test new runtime features
3. **Update docs** - Keep `runtime/README.md` current
4. **Backward compatible** - Don't break existing apps

## License

Same as BusinessInfinity and AgentOperatingSystem.
