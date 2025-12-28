# BusinessInfinity

Enterprise Business Application built on the **AgentOperatingSystem Runtime**.

## Architecture

BusinessInfinity uses a clean three-layer architecture:

```
┌─────────────────────────────────────────────────┐
│         BusinessInfinity Application            │
│  • src/config.py - Configuration                │
│  • src/app.py - Core business logic             │
│  • src/handlers.py - HTTP route handlers        │
└─────────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│         Generic Runtime Layer                   │
│  • runtime/azure_functions_runtime.py           │
│  • runtime/routes_registry.py                   │
│  • runtime/config_loader.py                     │
│  • runtime/storage.py & messaging.py            │
└─────────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│       AgentOperatingSystem (AOS)                │
│  • Storage, Messaging, ML Pipeline              │
│  • Observability, Reliability, Security         │
└─────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.8+
- Azure Functions Core Tools
- Azure subscription (for deployment)

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -e .
   ```

2. **Configure environment:**
   ```bash
   cp local.settings.json.example local.settings.json
   # Edit local.settings.json with your settings
   ```

3. **Run locally:**
   ```bash
   func start
   ```

### Configuration

BusinessInfinity is **configuration-driven**. All settings are in `src/config.py` and loaded from environment variables or JSON files.

Key configuration options:

| Setting | Default | Description |
|---------|---------|-------------|
| `COMPANY_NAME` | "Business Infinity" | Company name |
| `BOARDROOM_ENABLED` | true | Enable boardroom features |
| `WORKFLOWS_ENABLED` | true | Enable workflow engine |
| `ANALYTICS_ENABLED` | true | Enable analytics |
| `MENTOR_MODE_ENABLED` | true | Enable mentor mode |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/status` | GET | Detailed status |
| `/agents` | GET | List all agents |
| `/agents/{role}/ask` | POST | Ask an agent |
| `/workflows/{name}` | POST | Execute workflow |
| `/mcp/servers` | GET | List MCP servers |

## Project Structure

```
BusinessInfinity/
├── function_app.py          # Azure Functions entry point
├── pyproject.toml           # Package configuration
├── runtime/                  # Generic runtime (reusable)
│   ├── __init__.py          # Runtime exports (v2.0.0)
│   ├── azure_functions_runtime.py
│   ├── routes_registry.py
│   ├── config_loader.py
│   ├── storage.py
│   └── messaging.py
├── src/                      # BusinessInfinity source
│   ├── __init__.py          # Package exports (v2.0.0)
│   ├── app.py               # Main BusinessInfinity class
│   ├── config.py            # BusinessInfinityConfig
│   ├── handlers.py          # HTTP route handlers
│   ├── agents/              # C-Suite agents
│   │   ├── base.py          # BusinessAgent base class
│   │   ├── ceo.py           # ChiefExecutiveOfficer
│   │   ├── cto.py           # ChiefTechnologyOfficer
│   │   ├── founder.py       # FounderAgent
│   │   └── agent_coordinator.py
│   ├── orchestration/       # Workflow orchestration
│   │   ├── BusinessBoardroomOrchestrator.py
│   │   ├── DecisionIntegrator.py
│   │   └── DecisionLedger.py
│   ├── executors/           # MCP executors
│   │   ├── ERPExecutor.py
│   │   ├── CRMExecutor.py
│   │   └── LinkedInExecutor.py
│   └── core/                # Supporting utilities
├── .archive/                 # Archived legacy files
└── docs/                     # Documentation
```

## Key Concepts

### Runtime Layer

The `runtime/` package provides generic infrastructure that can be reused by any application:

- **RouteRegistry**: Framework-agnostic route registration
- **RuntimeConfig**: Configuration loading from env/JSON
- **AzureFunctionsRuntime**: Azure Functions integration
- **ServiceBusRuntime**: Message handling
- **Storage/Messaging**: Abstractions over AOS

### Application Layer

The `src/` package contains BusinessInfinity-specific code:

- **BusinessInfinity**: Main application orchestrator
- **BusinessInfinityConfig**: Business configuration
- **Handlers**: HTTP route handlers
- **Agents**: C-Suite agent implementations

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Format code
black .

# Type checking
mypy src/
```

### Adding New Routes

1. Create a handler in `src/handlers.py`
2. Register in `register_routes()` function
3. Routes are automatically registered with Azure Functions

### Adding New Agents

1. Add agent configuration to `BusinessInfinityConfig`
2. Add agent initialization in `BusinessInfinity._initialize_agents()`
3. Implement agent-specific logic

## Deployment

### Azure Functions

```bash
func azure functionapp publish <app-name>
```

### Environment Variables

Set these in Azure Functions Application Settings:

- `APP_ENVIRONMENT`: production/development
- `STORAGE_CONNECTION_STRING`: Azure Storage connection
- `MESSAGING_CONNECTION_STRING`: Service Bus connection
- `APPLICATIONINSIGHTS_CONNECTION_STRING`: App Insights

## License

See [LICENSE](LICENSE) for details.

## Related Projects

- [AgentOperatingSystem](../AgentOperatingSystem/) - Core infrastructure
- [Boardroom](../Boardroom/) - C-Suite agent implementations
- [MCP](../MCP/) - Model Context Protocol servers
