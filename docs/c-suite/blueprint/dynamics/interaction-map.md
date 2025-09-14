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
[Event Source]
    ├── Internal systems (ERP, CRM, HRIS, analytics)
    ├── External feeds (market data, news, regulatory updates)
    └── Cross‑org partners (SharedForecast, JointPerformanceReport)

        │
        ▼

[Event Ingestion via MCP]
    • Normalise event into structured format
    • Tag with:
        - Scope: local | inter_org | value_chain
        - Urgency: low | medium | high | critical
        - Domains: finance, ops, marketing, HR, tech, etc.

        │
        ▼

[Context Assembly by Role Agent]
    • Filter events by relevance to role
    • Pull fresh context slices from Organizational Data MCP
    • Retrieve related shared artifacts (DecisionTree, SharedForecast, PartnershipAgreement)

        │
        ▼

[Decision Loop Activation]
    ├── Re‑score existing DecisionTree.v1
    └── Create new DecisionTree.v1

        │
        ▼

[DecisionScore Generation]
    • Score each branch for:
        - Vision Alignment
        - Purpose Alignment
        - Legendary Lens
        - (Federated) Ecosystem Vision Alignment

        │
        ▼

[Aggregation & Governance]
    ├── Local: Aggregate into GovernanceDecision.v1 per DecisionPolicy.v1
    └── Federated: Aggregate into JointGovernanceDecision.v1 per InterOrgDecisionPolicy.v1 or MultiPartyDecisionPolicy.v1
    • Enforce guardrails; trigger human‑in‑loop if thresholds breached

        │
        ▼

[Execution]
    • Execute approved actions via:
        - Community Engagement MCP (external comms, campaigns)
        - Organizational Data MCP (internal ops, system updates)
    • Create ProvenanceReceipt.v1 linking decision → action → source data

        │
        ▼

[Outcome Tracking]
    • Generate PerformanceReport.v1 (local) or JointPerformanceReport.v1 (federated)
    • Create DecisionOutcome.v1 comparing expected vs actual metrics

        │
        ▼

[Learning & Evolution]
    • Draft ImprovementPlan.v1 for gaps
    • Update AlignmentMatrix.v1 if vision/purpose interpretations shift
    • Schedule domain LLM fine‑tuning if systemic drift detected 

---

## 3. Dynamic Features

- **Event Priority Routing:** Critical events bypass periodic loops for immediate attention.
- **Context Freshness Bias:** Preference for most recent, high‑confidence data slices.
- **Adaptive Weighting:** Influence shifts based on decision type and agent reputation.
- **Simulation Mode:** Optional pre‑execution scenario testing.
- **Feedback Loop:** Outcomes directly influence future decision weights and guardrails.

---

## 4. Governance Touchpoints

- **At Event Ingestion:** Scope and urgency classification.
- **At Aggregation:** Policy enforcement (DecisionPolicy, InterOrgDecisionPolicy).
- **At Execution:** Guardrail checks, human approval if required.
- **At Learning:** Policy and model updates logged for audit.

---

## 5. Observability

- **Dashboards:** Real‑time view of active decisions, event backlog, guardrail status.
- **Metrics:** Consensus time, override frequency, decision accuracy, outcome variance.
- **Alerts:** Governance breaches, KPI anomalies, stalled decisions.

---