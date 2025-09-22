# Azure Service Bus Configuration for BusinessInfinity

BusinessInfinity now uses Azure Service Bus for all MCP (Model Context Protocol) communication with external systems (ERPNext-MCP, linkedin-mcp-server, mcp-reddit) via the AOS MCP client.

## Required Environment Variables

- `SERVICE_BUS_CONNECTION_STRING`: Azure Service Bus connection string (with Manage/Send/Listen rights)
- `ERP_MCP_TOPIC`: Topic name for ERPNext-MCP (default: `erpnext-mcp-topic`)
- `LINKEDIN_MCP_TOPIC`: Topic name for linkedin-mcp-server (default: `linkedin-mcp-topic`)
- `REDDIT_MCP_TOPIC`: Topic name for mcp-reddit (default: `mcp-reddit-topic`)
- `AOS_SUBSCRIPTION`: Subscription name for this orchestrator (default: `bi-orchestrator`)

## Usage
- The orchestrator uses the AOS MCP client to send/receive MCP messages to each system via the configured topics and subscription.
- All direct MCP handler code has been removed from BusinessInfinity; only the AOS MCP client is used for external MCP calls.

## Example .env
```
SERVICE_BUS_CONNECTION_STRING=Endpoint=sb://<your-servicebus>.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=...
ERP_MCP_TOPIC=erpnext-mcp-topic
LINKEDIN_MCP_TOPIC=linkedin-mcp-topic
REDDIT_MCP_TOPIC=mcp-reddit-topic
AOS_SUBSCRIPTION=bi-orchestrator
```

## Architecture
- MCP client and Service Bus management utilities are implemented in `RealmOfAgents/AgentOperatingSystem`.
- BusinessInfinity orchestrator imports and uses these clients for all external MCP communication.

---

For more details, see the code in `core/BusinessInfinityOrchestrator.py` and `RealmOfAgents/AgentOperatingSystem/mcp_servicebus_client.py`.
