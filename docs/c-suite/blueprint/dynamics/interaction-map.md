# Business Infinity — Dynamic Interaction Map

## Purpose
To visualise and describe the real-time flows between events, AI agents, artifacts, and governance layers in the Business Infinity ecosystem, covering both single-company and federated value chain contexts.

---

## 1. Core Interaction Flow

### Step 1 — Event Trigger
- **Sources:**
  - Internal systems (ERP, CRM, HRIS, analytics)
  - External feeds (market data, news, regulatory updates)
  - Cross-org partners (SharedForecast, JointPerformanceReport)
- **Event Types:** Operational, strategic, risk, opportunity, compliance.

### Step 2 — Event Ingestion
- MCP servers receive events and normalise them into **EventArtifact.v1** (internal) or **SharedEvent.v1** (cross-org).
- Events tagged with:
  - Scope (`local`, `inter_org`, `value_chain`)
  - Urgency (`low`, `medium`, `high`, `critical`)
  - Domains affected (finance, ops, marketing, etc.)

### Step 3 — Context Assembly
- Persistent AI Agent for each role:
  - Filters events by relevance.
  - Pulls fresh context slices from Organizational Data MCP.
  - Retrieves relevant shared artifacts (e.g., latest DecisionTree, SharedForecast).

### Step 4 — Decision Loop Activation
- Agent determines if:
  - An existing DecisionTree.v1 needs re-scoring.
  - A new DecisionTree.v1 should be created.
- Scoring performed via DecisionScore.v1:
  - Vision Alignment
  - Purpose Alignment
  - Legendary Lens
  - (Federated) Ecosystem Vision Alignment

### Step 5 — Aggregation & Governance
- **Single Company:** Scores aggregated into GovernanceDecision.v1 per DecisionPolicy.v1.
- **Federated:** Company positions aggregated into JointGovernanceDecision.v1 per InterOrgDecisionPolicy.v1 or MultiPartyDecisionPolicy.v1.
- Guardrails enforced; human-in-loop triggered if thresholds breached.

### Step 6 — Execution
- Approved actions executed via:
  - Community Engagement MCP (external comms, campaigns)
  - Organizational Data MCP (internal ops, system updates)
- ProvenanceReceipt.v1 created linking decision → action → source data.

### Step 7 — Outcome Tracking
- PerformanceReport.v1 (local) or JointPerformanceReport.v1 (federated) generated.
- DecisionOutcome.v1 created comparing expected vs actual metrics.

### Step 8 — Learning & Evolution
- ImprovementPlan.v1 drafted for gaps.
- AlignmentMatrix.v1 updated if vision/purpose interpretations shift.
- Domain LLM fine-tuning scheduled if systemic drift detected.

---

## 2. Interaction Map (Text Diagram)