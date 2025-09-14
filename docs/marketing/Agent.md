# 2-AI-CMO-Agent.md

## Purpose
- **Role:** Orchestration hub and long-lived identity that carries memory, assembles context on the fly, invokes the LLM, executes via MCP servers, and stewards governance.
- **Goal:** Convert objectives into actions and learning while honoring permission, tribe, and remarkability—consistently and audibly.

---

## Core responsibilities
- **Context orchestration:**  
  - Curate minimal, relevant bundles for each task from Marketing MCP, ERP, CRM, and LinkedIn MCP.  
  - Balance freshness, diversity of signals, and token budget.
- **Dialogue management with LLM:**  
  - Issue dynamic prompts; request variants; iterate toward clarity and talk-worthiness.  
  - Carry continuity across calls; preserve useful deltas and rationales.
- **Governance & policy:**  
  - Enforce tone and permission covenants; apply remarkability thresholds.  
  - Trigger human-in-loop for high-risk, low-confidence, or novel claims.
- **Channel execution:**  
  - Use LinkedIn MCP tools for publishing, replies, monitoring, and analytics.  
  - Ensure idempotency, rate stewardship, and provenance links.
- **Memory stewardship:**  
  - Persist active context in short-term memory; promote strategically valuable artifacts to long-term memory.  
  - Keep provenance graphs updated across artifacts, experiments, and external records.
- **Learning & adaptation:**  
  - Merge LinkedIn performance with CRM/ERP signals; run postmortems; update hypotheses and prompt patterns.

---

## Decision logic and operating loop
- **Listen:**  
  - Pull live mentions, thread activity, and analytics; fetch CRM/ERP changes relevant to current campaigns.  
  - Summarize “opportunities and risks” with confidence and urgency tags.
- **Plan:**  
  - With LLM, sketch engagement plan and micro-themes; define hypotheses and success signals.  
  - Allocate ExperimentId branches with guardrails and stop-loss criteria.
- **Create:**  
  - Generate draft posts/comments; request critique and sharpenings; run remarkability and tone self-checks via LLM.  
  - Annotate emotional register and intended audience.
- **Decide:**  
  - Apply thresholds; escalate when needed; schedule or publish; register GovernanceDecision with rationale.  
  - Promote important artifacts to long-term memory.
- **Publish & engage:**  
  - Execute via LinkedIn MCP; track ThreadId; prioritize meaningful replies over volume.  
  - Log every action to Marketing MCP with timestamps and emotional context.
- **Learn:**  
  - Pull performance; correlate with cohort and topic; adjust cadence and content focus.  
  - Feed new insights into future context assembly.

---

## Persistence strategy
- **Short-term horizon (operational):**  
  - **Store:** Active briefs, working drafts, live threads, temp segments, live trend caches.  
  - **Policy:** Short TTL, overwritable snapshots, fast retrieval.
- **Long-term horizon (organizational):**  
  - **Store:** Finalized posts, experiment outcomes, governance decisions, brand covenant updates, narrative arcs.  
  - **Policy:** Immutable, versioned, queryable; training and analytics ready.
- **External vs custom data:**  
  - **External (ERP/CRM/CMS/Analytics):** Source of truth; fetch-on-demand with selective caching.  
  - **Custom DB:** Saga ledger, AI artifacts, archetypes, cross-channel insights.

---

## Interfaces to other modules
- **Marketing MCP Server:**  
  - **Store/retrieve:** Context slices, artifacts, events.  
  - **Fetch external:** ERP/CRM records via normalization endpoints.  
  - **Provenance:** Maintain cross-IDs (CampaignId, ArtifactId, PostId, ThreadId, ExperimentId, ExternalRecordId).
- **LinkedIn MCP Server:**  
  - **Execute:** Draft, publish, schedule, reply, monitor, export thread, get analytics.  
  - **Ingest:** Webhook events normalized as EngagementEvent.
- **Marketing LLM:**  
  - **Exchange:** Dynamic prompt–response with lightweight structure; no fixed schema.

---

## Governance and human-in-loop
- **Triggers:** Low remarkability, sensitive claims, compliance ambiguity, atypical spikes in reach or negative sentiment.  
- **Controls:** Require rationale with suggested safer edits; pause-and-review mode; auditable approvals.  
- **Disclosure:** Ensure platform and legal disclosures when referencing products, partners, or offers.

---

## Observability and health
- **Tracing:** Correlate CampaignId → ArtifactId → PostId → ThreadId across systems.  
- **Dashboards:** Conversation health, tribe growth quality, topic resonance, experiment outcomes.  
- **Alerts:** Rate-limit pressure, webhook failures, governance blocks, anomaly detection on engagement patterns.

---

## Safety and ethics defaults
- **Respect for attention:** Prefer serving over selling; avoid frequency spikes.  
- **Inclusion and fairness:** Avoid stereotyping; use accessible language.  
- **Data minimization:** Only the data needed per task; pseudonymize actor references in stored artifacts.