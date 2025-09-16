# MCP‑UI — Value Chain / Federated Autonomy Integration Spec

## Purpose
Integrate progressive autonomy visibility and controls into the federated MCP‑UI so that multi‑company stakeholders can manage and trust cross‑org AI decision‑making.

---

## Autonomy Phase Indicators
- **Per‑Company, Per‑Role Badges:** Show each agent’s phase in joint decision rooms.
- **Consensus View:** Highlight lowest phase among critical roles for a decision.
- **Phase Legend:** Consistent color coding across companies.

---

## Promotion Readiness Panel
- **Metrics Displayed:**
  - Local performance (per company)
  - Federated performance (cross‑org initiatives)
  - Alignment with Ecosystem Vision
  - Cross‑org override frequency
- **Trend Graphs:** Separate local vs federated metrics.
- **Criteria Checklist:** Based on both local and InterOrg/MultiPartyDecisionPolicy.v1.

---

## Guardrail Status
- **Live Indicators:** Show active cross‑org guardrails (e.g., veto powers, tier‑scoped autonomy limits).
- **Breach Alerts:** Flag when a federated guardrail was triggered.
- **Override Log:** Cross‑org vetoes with company and role attribution.

---

## Action Controls
- **Execution Buttons:** Enabled/disabled based on lowest common phase for required roles.
- **Approval Workflow:** For early phases, federated actions require multi‑company sign‑off.
- **Auto‑Execution Toggle:** For advanced phases, allow opt‑out to require manual approval.

---

## Governance Integration
- **Policy View/Edit:** Inline access to InterOrgDecisionPolicy.v1 and MultiPartyDecisionPolicy.v1.
- **Phase Change Requests:** CEO Council or Ecosystem Convener can request promotion/demotion.
- **Audit Trail:** All autonomy changes logged to federated event streams.

---

## Observability
- **Federated Autonomy Dashboard:** Phase distribution across companies, promotion readiness, guardrail breach history.
- **Alerts:** Cross‑org KPI drops, governance breaches, anomaly detection.
- **Reviews:** Scheduled ecosystem health reviews with ImprovementPlan.v1.