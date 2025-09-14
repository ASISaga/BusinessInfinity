# 3-Decision-Orchestration-and-Scoring-Protocol.md

## Purpose
- **Role:** Provide a consistent, multi-agent process for C-suite discussions where each member scores options for alignment.
- **Goal:** Decisions reflect the shared vision and each agent’s purpose, with domain scoring produced by fine-tuned LLMs.

---

## Process Overview
- **Initiate Discussion:**  
  - **Define:** Topic, goals, constraints, and candidate options.  
  - **Assemble:** Cross-domain context slices relevant to the decision.
- **Decision Tree Construction:**  
  - **Artifact:** DecisionTree.v1 with nodes (questions), branches (options), and leaves (final actions).  
  - **Annotations:** Risks, dependencies, required capabilities, expected outcomes.
- **Agent Scoring (per branch):**  
  - **Vision Alignment:** Fit with Vision.v1 in the agent’s domain interpretation.  
  - **Purpose Alignment:** Degree to which the branch advances the agent’s mission.  
  - **Legendary Lens:** Heuristic fit as internalized by the fine-tuned LLM (no external legend objects).  
  - **Output:** DecisionScore.v1 { scores, weights, rationale, uncertainties }.

> Each agent’s LLM generates scores and short rationales using its internalized domain lexicon (weights), optionally guided by an AlignmentRubric.v1 if present.

---

## Aggregation & Consensus
- **Normalization:** Scale scores to a common range; document weights per agent (policy-driven).
- **Consensus Modes:**  
  - **Unanimity:** All agents above threshold.  
  - **Weighted Majority:** Sum(weights × scores) ≥ threshold.  
  - **Veto:** Specific roles can block under defined conditions.
- **Finalization:**  
  - **Artifact:** GovernanceDecision.v1 with selected branch, score matrix, dissent notes, and provenance.

---

## Feedback & Learning
- **Outcome Tracking:**  
  - **Artifact:** DecisionOutcome.v1 linking expected vs actual metrics; confidence updates.  
  - **Postmortems:** LLM-assisted summaries with counterfactuals and lessons.
- **Continuous Calibration:**  
  - **Adjust:** Agent weights, thresholds, and rubrics; consider LLM refresh if systemic drift is detected.

---

## Interfaces
- **create_decision_tree(topic, options, context) → DecisionTree.v1**
- **score_branch(agent_id, branch_id, context) → DecisionScore.v1**
- **aggregate_scores(tree_id, policy) → GovernanceDecision.v1**
- **record_outcome(decision_id, metrics) → DecisionOutcome.v1**