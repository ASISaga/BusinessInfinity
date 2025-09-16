# Business Infinity — IXL Mode Integration Map

## Purpose
To define how the three primary MCP‑UI modes interconnect, share context, and integrate with the static (architecture, artifacts, governance) and dynamic (events, decision loops, learning) layers of Business Infinity.

---

## 1. Modes Overview

1. **Governance Dashboard**
   - Monitoring, oversight, and policy control.
   - Anchored in MCP‑UI’s Artifact Browser, Decision Workspace, Execution Console, and Governance Panel.

2. **Mentor Mode**
   - Safe environment for fine‑tuning and testing domain‑specific LLMs.
   - Anchored in Mentor Console, Scenario Library, Lexicon Manager, and Version Tracker.

3. **Boardroom**
   - Conversational space for one‑to‑one and group agent interactions.
   - Anchored in Boardroom View, Chat Interface, Live Decision Panel, and Consensus Tracker.

---

## 2. Integration Principles

- **Context Persistence:**  
  Moving between modes retains the current decision/event context and relevant artifacts.
  
- **Role‑Aware Access:**  
  Mode features adapt to the user’s role, scope, and governance permissions.

- **Artifact Continuity:**  
  Artifacts created or updated in one mode are immediately available in others, with provenance intact.

- **Governance Everywhere:**  
  Guardrail status, autonomy phase indicators, and policy links are visible in all modes.

---

## 3. Mode‑to‑Mode Flows

### A. Governance Dashboard → Boardroom
- **Use Case:** CEO spots a guardrail breach in Dashboard → opens Boardroom session with COO and CFO agents to discuss.
- **Shared Context:** DecisionTree, DecisionScores, guardrail trigger details.
- **Outcome:** Consensus reached → GovernanceDecision updated in Dashboard.

### B. Boardroom → Governance Dashboard
- **Use Case:** Agents in Boardroom finalise a decision → push GovernanceDecision to Dashboard for approval.
- **Shared Context:** Conversation log linked to decision provenance.
- **Outcome:** Approved decision triggers Execution Console actions.

### C. Governance Dashboard → Mentor Mode
- **Use Case:** CFO notes repeated misalignment in AI scoring → sends case to Mentor Mode for model review.
- **Shared Context:** DecisionTree, DecisionScores, DecisionOutcome.
- **Outcome:** Model fine‑tuned; updated version deployed back to production.

### D. Mentor Mode → Governance Dashboard
- **Use Case:** Mentor Mode produces improved model → Governance Dashboard shows promotion readiness.
- **Shared Context:** Version comparison metrics, mentor feedback logs.
- **Outcome:** Governance owner approves model deployment.

### E. Boardroom → Mentor Mode
- **Use Case:** Agents disagree on scoring rationale → export scenario to Mentor Mode for LLM reasoning test.
- **Shared Context:** DecisionTree, contested branches, rationale notes.
- **Outcome:** Model adjustments proposed; results fed back to Boardroom.

---

## 4. Integration with Static Layer

- **Artifacts:**  
  - Governance Dashboard: consumes/updates DecisionTree, DecisionScore, GovernanceDecision, PerformanceReport.  
  - Mentor Mode: consumes/updates Lexicon, Scenario, ModelVersion artifacts.  
  - Boardroom: consumes/updates DecisionTree, DecisionScore, ProvenanceReceipt, ImprovementPlan.

- **Governance Specs:**  
  All modes enforce DecisionPolicy, InterOrgDecisionPolicy, MultiPartyDecisionPolicy as defined in static specs.

---

## 5. Integration with Dynamic Layer

- **Event Flow:**  
  - Governance Dashboard: primary entry point for event alerts.  
  - Boardroom: real‑time deliberation on event‑triggered decisions.  
  - Mentor Mode: post‑event analysis and model refinement.

- **Decision Loops:**  
  - Dashboard: oversight and approval stages.  
  - Boardroom: scoring and consensus stages.  
  - Mentor Mode: learning and model evolution stages.

---

## 6. Observability Across Modes

- **Shared Metrics:**  
  - Decision throughput, consensus time, override frequency, model accuracy trends.
- **Cross‑Mode Analytics:**  
  - Track how often decisions move between modes.
  - Identify bottlenecks (e.g., long Boardroom deliberations, slow model updates).

---

## 7. Example End‑to‑End Flow

**Scenario:** Supply Chain Disruption
1. **Governance Dashboard:** COO sees critical event alert → opens Decision Workspace.
2. **Boardroom:** COO invites CFO and CEO agents to deliberate options.
3. **Governance Dashboard:** Consensus decision pushed back for approval.
4. **Mentor Mode:** Post‑event, scenario exported to test model’s crisis reasoning.
5. **Governance Dashboard:** Updated model deployed; future disruptions handled faster.

---