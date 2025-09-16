# Organizational Data MCP Server Blueprint

## Purpose
Integrate the agent with enterprise systems and maintain dual-horizon memory for operational and strategic data.

## Scope
- **Integrations:** ERP, CRM, HRIS, CMS/DAM, Analytics, Finance, Legal, Support, Events.
- **Custom DB:** Store domain-specific data not present in enterprise systems.

## Memory Horizons
- **Short-term operational context:** Active briefs, live metrics, transient states; TTL-based, overwritable.
- **Long-term organizational ledger:** Immutable, versioned history; analytics-ready.

## Core Functions
- **Data ingestion:** Normalize external system data into MCP artifacts.
- **Context retrieval:** Selective recall with freshness bias and diversity of signals.
- **Persistence:** Store artifacts/events with provenance.
- **Provenance graph:** Link artifacts to campaigns, decisions, external records.

## Interfaces
- `put_artifact(artifact, horizon) → ArtifactId`
- `append_event(stream, event, horizon) → Offset`
- `get_context(selectors, horizon, window, limits) → ContextSlice.v1`
- `fetch_from_system(system_id, query) → SystemData.v1`
- `link_provenance(edges) → ProvenanceReceipt.v1`
- `report(window, cohort, metrics) → PerformanceReport.v1`

## Design Principles
- **Integration-aware:** Live fetch when fresher than stored copy.
- **Security:** Scoped access, pseudonymization, retention policies.
- **Extensibility:** Support new artifact types and system connectors.