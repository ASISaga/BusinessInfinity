# Artifact Relationships & Governance Spec

## Purpose
To define how core `.v1` artifacts relate to each other across the AI C‑suite and federated collaboration framework, and to set governance rules for their creation, sharing, and lifecycle.

---

## 1. Functional Grouping

### Decision‑Making Layer
- **DecisionTree.v1** — Defines the structure of a decision.
- **DecisionScore.v1** — Per‑agent evaluation of decision branches.
- **GovernanceDecision.v1** — Aggregated, finalised decision record.
- **DecisionOutcome.v1** — Post‑decision performance and learning.
- **AlignmentMatrix.v1** — Maps local visions/purposes to a shared vision.

### Performance & Learning Layer
- **PerformanceReport.v1** — Metrics for a specific entity (campaign, initiative, etc.).
- **JointPerformanceReport.v1** — Aggregated KPIs across multiple entities.
- **ImprovementPlan.v1** — Agreed actions to address performance gaps.

### Collaboration & Agreement Layer
- **PartnershipAgreement.v1** — Formalised collaboration terms.
- **SharedForecast.v1** — Demand/supply/capacity projections.
- **CrisisCoordinationBrief.v1** — Shared situational awareness during disruptions.

### Provenance & Linking Layer
- **ProvenanceReceipt.v1** — Records of linking artifacts/entities.

---

## 2. Relationship Map

### Core Flow
1. **Decision Initiation**
   - `DecisionTree.v1` created for a topic.
2. **Scoring**
   - Each agent produces `DecisionScore.v1` for relevant branches.
3. **Aggregation**
   - Scores combined into `GovernanceDecision.v1`.
4. **Execution**
   - Actions from GovernanceDecision executed; provenance recorded.
5. **Outcome Tracking**
   - Results captured in `DecisionOutcome.v1`.
6. **Learning**
   - Gaps addressed via `ImprovementPlan.v1`.

### Supporting Flows
- **Forecast‑Driven Decisions**
  - `SharedForecast.v1` feeds into `DecisionTree.v1` for supply/demand planning.
- **Partnership‑Driven Decisions**
  - `PartnershipAgreement.v1` informs decision constraints and opportunities.
- **Crisis Response**
  - `CrisisCoordinationBrief.v1` triggers rapid decision cycles.
- **Performance Feedback**
  - `PerformanceReport.v1` → `JointPerformanceReport.v1` → informs new decisions.
- **Alignment in Federated Contexts**
  - `AlignmentMatrix.v1` influences scoring in cross‑org decisions.
- **Provenance**
  - `ProvenanceReceipt.v1` links all artifacts to their source data and related decisions.

---

## 3. Governance Metadata

Every artifact must include:
- **Governance Scope**
  - `local` — Single company use.
  - `inter_org` — Between two companies.
  - `value_chain` — Multi‑tier, chain‑wide.
- **Review Cadence**
  - How often the artifact is revisited (e.g., quarterly, annually, ad‑hoc).
- **Retention Policy**
  - Short‑term (operational) vs long‑term (strategic) storage.
- **Access Level**
  - `public` — Visible to all participants.
  - `shared` — Visible to defined partners.
  - `private` — Internal only.

---

## 4. Lifecycle States

### Common States
- **Draft** — In creation; editable.
- **Under Review** — Awaiting approval.
- **Approved** — Locked for execution.
- **Executed** — Actions completed.
- **Archived** — Retained for reference; no further edits.

### Performance Artifacts
- **In Progress** — Metrics being collected.
- **Completed** — Data collection finished.
- **Reviewed** — Analysis and lessons learned captured.

---

## 5. MCP‑UI Surfacing

### Single Company UI
- **Artifact Browser** — All artifact types.
- **Decision Workspace** — DecisionTree, DecisionScore, GovernanceDecision.
- **Metrics Dashboards** — PerformanceReport, JointPerformanceReport.
- **Governance Panel** — PartnershipAgreement, AlignmentMatrix, ProvenanceReceipt.

### Value Chain UI
- **Multi‑Company Artifact Library** — SharedForecast, JointPerformanceReport, CrisisCoordinationBrief.
- **Joint Decision Room** — InterOrgDecisionTree, CompanyPosition, GovernanceDecision.
- **Ecosystem Dashboards** — Aggregated KPIs, alignment scores.

---

## 6. Governance Rules

- **Provenance is Mandatory** — No artifact is valid without source metadata.
- **Immutable Once Approved** — Approved artifacts cannot be altered; changes require a new version.
- **Access Control Enforced at Source** — MCP servers enforce visibility and scope before sharing.
- **Reciprocity in Data Sharing** — Access to shared artifacts contingent on contributing equivalent data.
- **Audit Trails** — All artifact creation, modification, and access events logged.

---

## 7. Review & Evolution

- **Periodic Review** — Governance owners review artifact usage and compliance.
- **Schema Evolution** — Backward‑compatible changes preferred; deprecation windows for breaking changes.
- **Feedback Loop** — Lessons from DecisionOutcome and ImprovementPlan feed into artifact design updates.

---