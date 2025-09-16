# 4-Organizational-Memory-and-Learning-Fabric.md

## Purpose
- **Role:** Unified, integration-aware memory fabric that powers on-the-fly context and preserves long-term organizational history.
- **Goal:** Serve dynamic agent needs while ensuring durable provenance and auditability—without storing domain lexicons.

---

## Dual-Horizon Memory
- **Short-Term (Operational):**  
  - **Store:** Active briefs, drafts, live threads, temp segments, trend caches.  
  - **Policy:** High-churn, TTL-based, overwritable, low-latency retrieval.
- **Long-Term (Organizational):**  
  - **Store:** Final posts, decisions, outcomes, experiments, covenant versions, cross-domain provenance.  
  - **Policy:** Immutable, versioned, analytics-ready.

---

## Integration Layer
- **Enterprise Systems:** ERP, CRM, HRIS, CMS/DAM, Analytics, Support, Events.  
- **Custom DB:** Saga ledger, AI artifacts, engagement archetypes, decision trees/scores, performance joins.
- **Principles:** Read-through for freshness, selective caching, normalization with source and timestamp provenance.

---

## Core Data Contracts
- **Artifacts:** PostDraft, CommentDraft, PublishedPost, EngagementPlan, ContentCalendar, DecisionTree, DecisionScore, GovernanceDecision, DecisionOutcome, ToneComplianceReport, PerformanceReport.  
- **Events:** EngagementEvent, ReviewAction, ExperimentOutcome, AnalyticsIngest.  
- **Linkage:** CampaignId, ArtifactId, PostId, ThreadId, DecisionId, ExperimentId, ExternalRecordId, with explicit provenance edges.

> No DomainLexicon or Legends objects are persisted. The “lexicon” lives in LLM weights; the memory fabric stores decisions, outcomes, and context—not language models.

---

## Retrieval & Context Assembly
- **Selective Recall:**  
  - **get_context(selectors, horizon, window, limits) → ContextSlice.v1**  
  - **Selectors:** campaign, persona, topic, format, recency, performance, risk profile.
- **Freshness & Diversity:** Prefer recent, mix outcomes (win/neutral/miss) to reduce bias.
- **Size Discipline:** Enforce token budgets; support paging/“ask for more” patterns.

---

## Analytics & Learning
- **Conversation Health:** Depth, breadth, sustained exchange, unique contributors.  
- **Resonance Maps:** Topic × format × cohort × time matrices.  
- **Cross-System Joins:** Merge CRM value, ERP availability, and social performance for causal signals.  
- **Model Refresh Pipeline:** Curated, de-identified snapshots for periodic fine-tune evaluation or updates.

---

## Observability & Compliance
- **Metrics:** Retrieval latency, cache hit rate, schema version mix, data freshness.  
- **Security:** Scoped access, row/field-level controls, pseudonymization of user identifiers.  
- **Audit:** End-to-end provenance, reproducible decision trails, human-in-loop logs.

---

## Interfaces
- **put_artifact(artifact, horizon) → ArtifactId**
- **append_event(stream, event, horizon) → Offset**
- **get_context(selectors, horizon, window, limits) → ContextSlice.v1**
- **fetch_from_system(system_id, query) → SystemData.v1**
- **link_provenance(edges) → ProvenanceReceipt.v1**
- **report(window, cohort, metrics) → PerformanceReport.v1**