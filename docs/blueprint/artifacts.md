# Artifact Library — Core `.v1` Specifications

This document defines the core artifact types used across the AI C‑suite and federated collaboration framework.  
All artifacts are **self‑describing** and include **provenance metadata** for traceability.

---

## 1. Common Header (all artifacts)
Every artifact includes this header:

| Field | Type | Description |
|-------|------|-------------|
| `artifact_type` | string | Type name (e.g., `DecisionTree`, `PerformanceReport`). |
| `version` | string | Schema version (e.g., `v1`). |
| `artifact_id` | string (UUID) | Unique identifier for this artifact. |
| `created_at` | datetime | ISO‑8601 timestamp of creation. |
| `created_by` | string | Agent or system that created it. |
| `provenance` | object | `{ source_system, source_record_id, signatures[] }`. |
| `visibility` | enum | `public` \| `shared` \| `private`. |
| `scope` | string | Context scope (e.g., `local`, `federated`, `value_chain`). |

---

## 2. DecisionTree.v1
Structured representation of a decision and its options.

| Field | Type | Description |
|-------|------|-------------|
| `topic` | string | Decision subject. |
| `nodes` | array<object> | Decision points. |
| `nodes[].node_id` | string | Unique node identifier. |
| `nodes[].question` | string | Question at this node. |
| `nodes[].branches` | array<object> | Possible options. |
| `nodes[].branches[].branch_id` | string | Unique branch identifier. |
| `nodes[].branches[].description` | string | Option description. |
| `nodes[].branches[].dependencies` | array<string> | IDs of dependent nodes/branches. |
| `annotations` | object | Risks, dependencies, expected outcomes. |

---

## 3. DecisionScore.v1
Per‑agent scoring of a decision branch.

| Field | Type | Description |
|-------|------|-------------|
| `decision_tree_id` | string | Link to DecisionTree.v1. |
| `branch_id` | string | Branch being scored. |
| `agent_id` | string | Scoring agent. |
| `scores` | object | `{ vision_alignment, purpose_alignment, legendary_lens }` (0–1 floats). |
| `weights` | object | Weight applied to each score dimension. |
| `rationale` | string | Short explanation. |
| `uncertainty` | float | 0–1 confidence gap. |

---

## 4. GovernanceDecision.v1
Finalised decision record.

| Field | Type | Description |
|-------|------|-------------|
| `decision_tree_id` | string | Link to DecisionTree.v1. |
| `selected_branch_id` | string | Chosen option. |
| `score_matrix` | array<object> | Per‑agent DecisionScore.v1 summaries. |
| `consensus_mode` | enum | `unanimity` \| `weighted_majority` \| `veto`. |
| `dissent_notes` | array<object> | `{ agent_id, note }`. |
| `execution_plan` | object | Actions, owners, timelines. |

---

## 5. DecisionOutcome.v1
Post‑decision performance and learning.

| Field | Type | Description |
|-------|------|-------------|
| `governance_decision_id` | string | Link to GovernanceDecision.v1. |
| `expected_metrics` | object | KPIs predicted at decision time. |
| `actual_metrics` | object | KPIs observed after execution. |
| `variance_analysis` | string | Summary of differences. |
| `lessons_learned` | string | Key takeaways. |
| `improvement_plan_id` | string | Link to ImprovementPlan.v1 if created. |

---

## 6. PerformanceReport.v1
Performance metrics for a post, campaign, initiative, or joint effort.

| Field | Type | Description |
|-------|------|-------------|
| `entity_type` | string | e.g., `campaign`, `initiative`, `post`. |
| `entity_id` | string | ID of the entity measured. |
| `metrics` | object | `{ impressions, ctr, conversions, revenue, sentiment_score, ... }`. |
| `time_window` | object | `{ start, end }`. |
| `cohort` | string | Audience segment. |
| `source` | string | Data origin (platform/system). |

---

## 7. SharedForecast.v1
Forecast shared between partners.

| Field | Type | Description |
|-------|------|-------------|
| `forecast_type` | enum | `demand` \| `supply` \| `capacity`. |
| `granularity` | string | e.g., `SKU-region-week`. |
| `horizon` | string | Time horizon (e.g., `Q4-2025`). |
| `data_points` | array<object> | `{ key, value, confidence }`. |
| `assumptions` | string | Basis for forecast. |

---

## 8. PartnershipAgreement.v1
Formalised collaboration terms.

| Field | Type | Description |
|-------|------|-------------|
| `parties` | array<string> | Company/agent IDs. |
| `scope` | string | Collaboration scope. |
| `objectives` | array<string> | Goals. |
| `kpis` | array<string> | Success measures. |
| `terms` | string | Contractual terms. |
| `effective_dates` | object | `{ start, end }`. |

---

## 9. JointPerformanceReport.v1
Aggregated KPIs across multiple entities.

| Field | Type | Description |
|-------|------|-------------|
| `participants` | array<string> | Company IDs. |
| `metrics` | object | Aggregated KPIs. |
| `time_window` | object | `{ start, end }`. |
| `source_systems` | array<string> | Data origins. |

---

## 10. ImprovementPlan.v1
Agreed actions to address performance gaps.

| Field | Type | Description |
|-------|------|-------------|
| `issues` | array<string> | Problems identified. |
| `actions` | array<object> | `{ action, owner, due_date }`. |
| `expected_outcomes` | array<string> | Target improvements. |
| `review_date` | datetime | Scheduled review. |

---

## 11. CrisisCoordinationBrief.v1
Shared situational awareness during disruptions.

| Field | Type | Description |
|-------|------|-------------|
| `incident_id` | string | Unique incident reference. |
| `situation_summary` | string | Current state. |
| `roles_responsibilities` | array<object> | `{ role, company, responsibility }`. |
| `actions` | array<object> | `{ action, owner, status }`. |
| `cadence` | string | Update frequency. |

---

## 12. AlignmentMatrix.v1
Mapping of local visions/purposes to a shared vision.

| Field | Type | Description |
|-------|------|-------------|
| `shared_vision_id` | string | Reference to ValueChainVision.v1 or EcosystemVision.v1. |
| `mappings` | array<object> | `{ company_id, local_vision, alignment_score }`. |

---

## 13. ProvenanceReceipt.v1
Record of linking artifacts/entities.

| Field | Type | Description |
|-------|------|-------------|
| `links` | array<object> | `{ from_id, to_id, relationship_type }`. |
| `timestamp` | datetime | Link creation time. |
| `created_by` | string | Agent/system. |

---

## Notes
- All `.v1` artifacts are **immutable** once published; updates create a new version.
- Provenance is **mandatory** for cross‑org sharing.
- Visibility and scope fields control **access** in MCP‑UI.

---