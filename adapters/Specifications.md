---

📐 Developer Specification: Boardroom Agents with LoRA Adapters

1. Base Model
- Model: Llama-3.1-8B-Instruct
- Quantization: QLoRA (4‑bit NF4), FP16 for final layers if resources allow
- Why: Efficient for prototyping, strong instruction‑following, LoRA‑friendly

---

2. Adapter Architecture

2.1 Domain‑Specific LoRA Adapters
- Roles: CFO, CMO, COO, CTO, Founder, Investor
- Rank (r): 32–64 (Founder: 24–48; Investor: 32–48)
- Alpha: 16×–32× rank (Founder: 12×–24× rank)
- Target modules:  
  - Attention: qproj, kproj, vproj, oproj  
  - MLP: gateproj, upproj, down_proj
- Layer selection: Middle–upper layers (8–28 of 32)
- Purpose: Encodes role‑specific vocabulary, KPIs, reasoning style

2.2 Leadership LoRA Adapter
- Rank (r): 8–16
- Alpha: 8×–16× rank
- Target modules: oproj, downproj
- Layer selection: Upper layers only (24–32)
- Purpose: Governs tone, synthesis, decision framing

2.3 Orchestration Rules
- Always load exactly one domain adapter + leadership adapter
- Adapter order: Domain first → Leadership second
- Fusion weights (defaults):
  - CFO: 0.78 / 0.22
  - CMO: 0.68 / 0.32
  - COO: 0.74 / 0.26
  - CTO: 0.72 / 0.28
  - Founder: 0.70 / 0.30
  - Investor: 0.76 / 0.24

---

3. Prompt Scaffolding

System Prompts
- Domain contract:  
  "You are the [ROLE]. Provide precise, evidence‑backed analysis with explicit assumptions and role‑specific KPIs. Avoid leadership rhetoric in the Analysis section."
- Leadership contract:  
  "Reframe the analysis into an executive decision narrative. Present options, risks, a single recommendation, and next actions with owner, time, and form."

Output Schema
- Analysis: Assumptions, KPIs, evidence  
- Scenarios: 2–3 options with trade‑offs  
- Recommendation: One call, rationale, success criteria  
- Actions: Owner, time, form

---

4. Guardrails

Founder Adapter
- Must link vision to roadmap, market structure, measurable milestones
- Reject pure rhetoric without grounding

Investor Adapter
- Must include valuation impact, capital efficiency, liquidity, exit horizon
- Reject fabricated figures; enforce numeric consistency

Shared Leadership Checks
- Ensure options, risks, single recommendation, and actions are present
- Highlight trade‑offs when roles are in tension

---

5. Self‑Learning Loop

Data Sources
- Situational prompts (synthetic or real)
- Mentor feedback (corrections, refinements)

Dataset Strategy
- Original dataset: Frozen baseline (golden set)
- Self‑learning dataset: Expanding with mentor‑guided examples
- Fine‑tuning blend: 60–80% original + 20–40% self‑learning
- Versioning: Maintain v1, v2, v3… with provenance metadata

---

6. Upgrade Path: 8B → 13B

When to Upgrade
- Reasoning depth capped (shallow trade‑offs, missing second‑order effects)
- Cross‑role simulations blur voices
- Leadership tone lacks gravitas
- Evaluation metrics plateau

How to Upgrade
1. Preserve original + self‑learning datasets
2. Optionally distill 8B outputs into synthetic transcripts for style continuity
3. Retrain domain + leadership LoRAs on 13B
4. Run parallel evaluation (8B vs. 13B) on same scenarios
5. Shift self‑learning loop to 13B once it consistently outperforms 8B

---

7. Developer Tasks

- [ ] Implement adapter loading pipeline (domain + leadership, ordered, weighted fusion)  
- [ ] Build prompt scaffolding with system + leadership contracts and schema  
- [ ] Implement segmented generation (Analysis → Scenarios → Recommendation → Actions)  
- [ ] Add guardrail validators (role‑specific KPI checks, numeric consistency, schema compliance)  
- [ ] Build dataset governance: frozen baseline + expanding self‑learning repo with versioning  
- [ ] Implement evaluation harness (role fidelity, leadership clarity, conflict index)  
- [ ] Prepare migration scripts for retraining LoRAs on 13B with blended datasets  

---

8. Deliverables

- Adapter configs (rank, alpha, target modules, fusion weights per role)  
- Prompt templates (domain + leadership contracts, schema)  
- Training pipeline (fine‑tuning with blended datasets, versioned)  
- Evaluation suite (synthetic boardroom scenarios, scoring metrics)  
- Migration plan (8B → 13B retraining, distillation optional, parallel evaluation)  

---

✅ This spec gives developers a clear blueprint: how to configure adapters, how to orchestrate them, how to expand datasets via self‑learning, and how to upgrade to 13B without losing accumulated learning.  

---