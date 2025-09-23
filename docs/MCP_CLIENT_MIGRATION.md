# MCP Client Refactor & Azure Service Bus Integration

## Overview
BusinessInfinity now uses a generic MCP client implemented in the AgentOperatingSystem (AOS) for all communication with external MCP services (ERPNext-MCP, linkedin-mcp-server, mcp-reddit) via Azure Service Bus.

## Key Changes
- **MCP client code moved to AOS**: The reusable client is in `RealmOfAgents/AgentOperatingSystem/mcp_servicebus_client.py`.
- **Service Bus management utilities**: Topic/subscription management is in `RealmOfAgents/AgentOperatingSystem/servicebus_manager.py`.
- **Orchestrator refactored**: `BusinessInfinityOrchestrator` now uses the AOS MCP client for all external MCP calls.
- **All direct MCP handler code removed**: Only the new client is used for communication.

## Configuration
See `AZURE_SERVICE_BUS.md` for required environment variables and example `.env`.

## Deployment
- Ensure all required environment variables are set.
- Deploy as usual to Azure Functions or your preferred environment.

## Further Reading
- `core/BusinessInfinityOrchestrator.py`
- `RealmOfAgents/AgentOperatingSystem/mcp_servicebus_client.py`
- `RealmOfAgents/AgentOperatingSystem/servicebus_manager.py`

---

For questions or issues, see the code comments or contact the maintainers.
