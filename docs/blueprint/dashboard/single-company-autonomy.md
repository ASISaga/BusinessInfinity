# MCP‑UI — Single Company Autonomy Integration Spec

## Purpose
Embed progressive autonomy controls, indicators, and guardrails into the single‑company MCP‑UI so stakeholders can see, manage, and trust the AI C‑suite’s evolving authority.

---

## Autonomy Phase Indicators
- **Phase Badge:** Prominent label on each agent’s profile (Phase 0–4).
- **Color Coding:** 
  - Grey = Observer
  - Blue = Co‑Pilot
  - Green = Shared Control
  - Amber = Conditional Autonomy
  - Gold = Strategic Autonomy
- **Tooltip:** Short description of current phase, capabilities, and limits.

---

## Promotion Readiness Panel
- **Metrics Displayed:**
  - Forecast accuracy
  - Recommendation acceptance rate
  - Alignment score average
  - Override frequency
- **Trend Graphs:** Show performance over last N review cycles.
- **Promotion Criteria Checklist:** Auto‑populated from Progressive Autonomy Deployment Spec.

---

## Guardrail Status
- **Live Indicators:** Show which guardrails are active (e.g., human‑in‑loop triggers, risk thresholds).
- **Breach Alerts:** Highlight when a guardrail was triggered and why.
- **Override Log:** List of human vetoes with rationale.

---

## Action Controls
- **Execution Buttons:** Enabled/disabled based on current phase.
- **Approval Workflow:** For phases 0–2, all actions route to human approvers.
- **Auto‑Execution Toggle:** For phases 3–4, per‑action opt‑out to require manual approval.

---

## Governance Integration
- **Policy View/Edit:** Inline access to DecisionPolicy.v1.
- **Phase Change Requests:** CEO or governance owner can request promotion/demotion with rationale.
- **Audit Trail:** All autonomy changes logged to Organizational Data MCP.

---

## Observability
- **Autonomy Dashboard:** Phase distribution across agents, promotion readiness, guardrail breach history.
- **Alerts:** KPI drops, governance breaches, anomaly detection.