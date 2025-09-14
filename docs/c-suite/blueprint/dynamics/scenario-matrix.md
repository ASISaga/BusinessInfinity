# Business Infinity — Scenario Traceability Matrix

## Purpose
To map each dynamic scenario to:
- The artifacts created, updated, or consumed.
- The MCP‑UI modules where those artifacts are surfaced.
- The governance policies or guardrails applied.

---

## Legend
- **A:** Artifact
- **UI:** MCP‑UI Module
- **G:** Governance / Policy Reference

---

## Scenario 1 — Supply Chain Disruption (Value Chain)

| Step | Affected Artifacts | MCP‑UI Modules | Governance Touchpoints |
|------|--------------------|----------------|------------------------|
| Event Ingestion | SharedEvent.v1 | Ecosystem Dashboard | Scope=`value_chain`, urgency=`critical` |
| Context Assembly | SharedForecast.v1, PartnershipAgreement.v1 | Artifact Browser, Multi‑Company Artifact Library | Access control: tier‑scoped |
| Decision Loop | DecisionTree.v1 | Decision Workspace (Value Chain) | MultiPartyDecisionPolicy.v1 |
| Scoring | DecisionScore.v1 | Decision Workspace (Value Chain) | Weighting: COO↑, CFO↑ |
| Aggregation | JointGovernanceDecision.v1 | Joint Decision Room | Guardrail: human‑in‑loop for contract changes |
| Execution | ProvenanceReceipt.v1 | Execution Console | Policy: Supplier‑Supplier Collaboration archetype |
| Outcome Tracking | JointPerformanceReport.v1 | Ecosystem Dashboard | KPI review cadence |
| Learning | ImprovementPlan.v1 | Governance & Policy Panel | Update risk mitigation playbook |

---

## Scenario 2 — Joint Product Launch (Customer–Seller)

| Step | Affected Artifacts | MCP‑UI Modules | Governance Touchpoints |
|------|--------------------|----------------|------------------------|
| Event Ingestion | SharedEvent.v1 | Ecosystem Dashboard | Scope=`inter_org` |
| Context Assembly | CampaignCalendar.v1, PartnershipAgreement.v1 | Artifact Browser, Multi‑Company Artifact Library | Access: marketing‑role scoped |
| Decision Loop | DecisionTree.v1 | Decision Workspace (Value Chain) | InterOrgDecisionPolicy.v1 |
| Scoring | DecisionScore.v1 | Decision Workspace | Weighting: CMO↑, COO↑ |
| Aggregation | GovernanceDecision.v1 | Joint Decision Room | No guardrail breach |
| Execution | ProvenanceReceipt.v1 | Execution Console | Policy: Customer‑Seller Collaboration archetype |
| Outcome Tracking | JointPerformanceReport.v1 | Ecosystem Dashboard | KPI: sales lift, engagement |
| Learning | ImprovementPlan.v1 | Governance & Policy Panel | Creative alignment recommendation |

---

## Scenario 3 — Regulatory Change (Regulator–Industry)

| Step | Affected Artifacts | MCP‑UI Modules | Governance Touchpoints |
|------|--------------------|----------------|------------------------|
| Event Ingestion | SharedEvent.v1 | Ecosystem Dashboard | Scope=`value_chain` |
| Context Assembly | RegulatorySchema.v1, ComplianceReport.v1 | Artifact Browser | Access: compliance‑role scoped |
| Decision Loop | DecisionTree.v1 | Decision Workspace | MultiPartyDecisionPolicy.v1 |
| Scoring | DecisionScore.v1 | Decision Workspace | Weighting: Legal↑, CFO↑ |
| Aggregation | JointGovernanceDecision.v1 | Joint Decision Room | Guardrail: regulator consultation |
| Execution | ProvenanceReceipt.v1 | Execution Console | Policy: Regulator–Industry Collaboration archetype |
| Outcome Tracking | JointPerformanceReport.v1 | Ecosystem Dashboard | Compliance rate tracking |
| Learning | ImprovementPlan.v1 | Governance & Policy Panel | Add regulatory sandbox participation |

---

## Scenario 4 — Internal Innovation Sprint (Single Company)

| Step | Affected Artifacts | MCP‑UI Modules | Governance Touchpoints |
|------|--------------------|----------------|------------------------|
| Event Ingestion | EventArtifact.v1 | Local Dashboard | Scope=`local` |
| Context Assembly | CustomerFeedback.v1, ProductRoadmap.v1 | Artifact Browser | Access: innovation‑role scoped |
| Decision Loop | DecisionTree.v1 | Decision Workspace (Single Company) | DecisionPolicy.v1 |
| Scoring | DecisionScore.v1 | Decision Workspace | Weighting: CTO↑, CFO↑ |
| Aggregation | GovernanceDecision.v1 | Decision Workspace | No guardrail breach |
| Execution | ProvenanceReceipt.v1 | Execution Console | Policy: Founder‑led innovation |
| Outcome Tracking | PerformanceReport.v1 | Metrics Dashboard | MVP delivery KPIs |
| Learning | ImprovementPlan.v1 | Governance & Policy Panel | Add customer co‑design step |

---

## Scenario 5 — Crisis Response Drill (Value Chain)

| Step | Affected Artifacts | MCP‑UI Modules | Governance Touchpoints |
|------|--------------------|----------------|------------------------|
| Event Ingestion | SharedEvent.v1 | Ecosystem Dashboard | Scope=`value_chain`, urgency=`critical` |
| Context Assembly | LogisticsData.v1, CostExposure.v1 | Artifact Browser | Access: ops & finance roles |
| Decision Loop | CrisisCoordinationBrief.v1, DecisionTree.v1 | Decision Workspace (Value Chain) | MultiPartyDecisionPolicy.v1 |
| Scoring | DecisionScore.v1 | Decision Workspace | Weighting: COO↑, CFO↑ |
| Aggregation | JointGovernanceDecision.v1 | Joint Decision Room | No guardrail breach |
| Execution | ProvenanceReceipt.v1 | Execution Console | Policy: Value Chain Collaboration archetype |
| Outcome Tracking | JointPerformanceReport.v1 | Ecosystem Dashboard | Simulated delivery KPIs |
| Learning | ImprovementPlan.v1 | Governance & Policy Panel | Update real crisis playbook |

---

## Notes
- **Artifacts** are linked to their definitions in `Artifacts.md`.
- **MCP‑UI Modules** are defined in `MCP-UI-SingleCompany.md` and `MCP-UI-ValueChain.md`.
- **Governance Policies** are defined in `Progressive-Autonomy-Deployment.md` and relevant archetype specs.