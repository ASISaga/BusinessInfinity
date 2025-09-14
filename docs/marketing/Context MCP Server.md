# Marketing MCP Server

## Purpose
Serve as the persistent memory and analytics fabric for all marketing artifacts, events, and governance decisions.

## Core Responsibilities
- Store and version all marketing artifacts.
- Maintain campaign histories and narrative arcs.
- Provide historical context to AI CMO between sessions.
- Support analytics, cohort analysis, and experiment tracking.

## Inputs
- Artifacts from LinkedIn MCP (posts, comments, events).
- Governance decisions from AI CMO agent.
- Plans and strategies from LLM.

## Outputs
- Historical context bundles for LLM.
- Analytics reports for AI CMO.
- Saga ledger entries for governance and narrative tracking.

## Integration Contracts
- `put_artifact(artifact_id, payload)`
- `get_by_campaign(campaign_id, filters) → ArtifactList.v1`
- `append_event(stream, EngagementEvent.v1)`
- `report(time_window, cohort, metrics) → PerformanceReport.v1`

## Storage Principles
- Modular, format‑optimized artifacts for long‑term revival.
- Immutable historical records with versioning.
- Queryable by campaign, time, audience segment, or content type.