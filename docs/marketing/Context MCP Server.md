# 4-Marketing-MCP-Server.md

## Purpose
- **Role:** Unified integration and persistence hub—bridging enterprise systems (ERP, CRM, CMS, Analytics) and a custom marketing database—to power on-the-fly context and durable organizational memory.
- **Goal:** Provide dual-horizon memory: short-term operational context and long-term saga ledger, with integration-aware retrieval.

---

## Integration layer

### Connected systems
- **ERP:** Product catalog, pricing, inventory, order history, supply events.  
- **CRM:** Customer profiles, segments, lifecycle stages, interaction history.  
- **CMS/DAM:** Brand assets, approved copy, media libraries.  
- **Analytics:** Web/app traffic, conversion funnels, attribution.  
- **Other:** Event management, support ticketing, partner portals.

### Principles
- **Read-through access:** Live queries to systems for freshest data when needed.  
- **Selective caching:** Short-term cache for slow or frequently accessed items.  
- **Normalization:** Map external records into Marketing MCP artifact formats.  
- **Provenance:** Tag each datum with source system, record ID, and retrieval timestamp.

---

## Dual-horizon memory

### Short-term operational context
- **Definition:** Volatile working set for active campaigns and real-time decisioning.  
- **Examples:** Active briefs, working drafts, live threads, temporary audience snapshots, live trend feeds.  
- **Characteristics:** High churn, short TTL, overwritable snapshots, low-latency retrieval.

### Long-term organizational memory
- **Definition:** Immutable, queryable history of marketing and organizational knowledge.  
- **Examples:** Published posts with outcomes, experiment results, governance decisions, brand covenant versions, engagement archetypes.  
- **Characteristics:** Content-addressed, versioned, analytics-ready, durable.

---

## Core data contracts
- **Artifacts (v1+):** PostDraft, CommentDraft, PublishedPost, EngagementPlan, ContentCalendar, GovernanceDecision, ToneComplianceReport, ThreadExport.  
- **Events (v1+):** EngagementEvent, PerformanceReport, ReviewAction, ExperimentOutcome.  
- **Linkage:** CampaignId, ArtifactId, PostId, ThreadId, ExperimentId, ExternalRecordId (ERP/CRM/etc.), Provenance edges.

> Contracts evolve additively; older versions remain readable. Each object carries a minimal self-describing header with type, version, and content hash.

---

## Interfaces

### Artifact storage
- **put_artifact(artifact, horizon) → ArtifactId**  
  - **horizon:** short_term | long_term  
  - **Behavior:** Short-term is overwritable with TTL; long-term is immutable and versioned.

### Event logging
- **append_event(stream, event, horizon) → Offset**  
  - **Streams:** engagements, governance, analytics, experiments.

### Context retrieval
- **get_context(selectors, horizon, window, limits) → ContextSlice.v1**  
  - **Selectors:** campaign, audience segment, topic, format, recency, quality thresholds.  
  - **Horizon:** short_term | long_term | both.  
  - **Integration-aware:** May perform live fetches from ERP/CRM and merge with stored context.

### External data access
- **fetch_from_system(system_id, query) → SystemData.v1**  
  - **system_id:** ERP | CRM | CMS | Analytics | Other.  
  - **Output:** Normalized artifact with provenance and freshness metadata.

### Provenance management
- **link_provenance(edges[]) → ProvenanceReceipt.v1**  
  - **Edges:** ArtifactId ↔ PostId, PostId ↔ ThreadId, ArtifactId ↔ ExperimentId, ArtifactId ↔ ExternalRecordId.

### Reporting and insights
- **report(window, cohort, metrics) → PerformanceReport.v1**  
  - **Metrics:** Impressions, CTR, saves, comments, reshares, dwell (if available), conversation health, tribe growth quality.  
- **resonance_map(dimensions) → ResonanceMap.v1**  
  - **Dimensions:** topic × format × cohort × time.

---

## Retrieval principles for on-the-fly context
- **Relevance first:** Supply only what the agent needs for the current task.  
- **Signal diversity:** Include successes, failures, and neutral baselines to reduce bias.  
- **Freshness bias:** Prefer recent data unless canonical exemplars requested.  
- **Size caps:** Enforce token budgets; support paging and “ask for more.”  
- **Source transparency:** Indicate whether data came from ERP/CRM or custom DB; include freshness timestamps.

---

## Caching and TTL policy
- **Short-term caches:** Live trends, segment snapshots, slow ERP queries; TTL 15m–48h based on type.  
- **Promotion rules:** Agent may promote cached items to long-term if strategic value is demonstrated (e.g., archetype discovery).  
- **Invalidation:** Source change events trigger cache bust or delta refresh.

---

## Analytics and learning
- **Conversation health:** Depth, breadth, unique contributors, sustained exchange.  
- **Experiment tracking:** Branch allocations, outcome deltas, confidence intervals; auto postmortems.  
- **Cross-system joins:** Merge CRM segments and ERP launches with social performance to explain outcomes.  
- **Exports:** Curated, de-identified snapshots for model refresh; versioned and auditable.

---

## Observability and compliance
- **Metrics:** Query latency, cache hit rate, external call latency, schema version mix.  
- **Logs:** Structured, correlation-ID based; sensitive fields redacted.  
- **Access control:** Scoped service identities; row/field-level guards for external data.  
- **Privacy:** Pseudonymize user identifiers; retain only necessary fields; apply retention policies.

---

## Versioning and evolution
- **Schema evolution:** Backward-compatible changes favored; deprecation with migration shims.  
- **Data migrations:** Blue/green compatible; provenance preserved across versions.  
- **Extensibility:** New artifact types can be registered with type metadata and validation hooks.