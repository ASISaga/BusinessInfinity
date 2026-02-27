🏛️ Boardroom Agents: LLM + LoRA Orchestration Specification

🎯 Purpose
The Boardroom Agents system simulates the decision‑making dynamics of a boardroom.  
It models not only the C‑suite executives (CFO, CMO, COO, CTO, etc.) but also the Founder and Investor voices, harmonized by a Leadership LoRA adapter.

The goal is to produce outputs that are:
- Analytically rigorous (grounded in KPIs, assumptions, trade‑offs)  
- Strategically framed (options, risks, recommendations, actions)  
- Boardroom‑ready (concise, authoritative, actionable)  

---

⚙️ Base Model
- Model: Llama‑3.1‑8B‑Instruct  
- Why:  
  - Efficient for prototyping and fine‑tuning  
  - Strong instruction‑following baseline  
  - Adapter‑friendly (LoRA/QLoRA well supported)  
- Quantization: QLoRA (4‑bit NF4) for efficiency; FP16 for final layers if resources allow  

---

🧩 LoRA Adapter Design

1. Domain‑Specific LoRAs
Each role has its own LoRA adapter:
- CFO: Financial discipline, runway, EBITDA, ROI, sensitivity analysis  
- CMO: Market opportunity, segmentation, brand positioning, ROI of spend  
- COO: Operational readiness, capacity, SLAs, cost per unit  
- CTO: Technical trade‑offs, architecture, latency, reliability, cost profile  
- Founder: Vision, mission, cultural continuity, long‑term arcs, existential risk  
- Investor: Capital efficiency, valuation multiples, liquidity, exit horizons, governance  

Design parameters (typical):
- Rank (r): 32–64 (Founder: 24–48; Investor: 32–48)  
- Alpha: 16×–32× rank (Founder: 12×–24× rank)  
- Target modules:  
  - Attention: qproj, kproj, vproj, oproj  
  - MLP: gateproj, upproj, down_proj  
- Layer selection: Middle‑to‑upper layers (e.g., 8–28 of 32)  
- Purpose: Encodes role‑specific vocabulary, KPIs, and reasoning style  

2. Leadership LoRA
- Single adapter across all roles  
- Rank (r): 8–16 (lightweight overlay)  
- Alpha: 8×–16× rank  
- Target modules: oproj, downproj  
- Layer selection: Upper layers only (24–32)  
- Purpose: Governs tone, synthesis, and decision framing  

3. Orchestration
- Always use exactly one domain LoRA + leadership LoRA together  
- Adapter order: Domain first → Leadership second  
- Fusion weights (default): Domain 0.72, Leadership 0.28  
- Role‑specific tuning:  
  - CFO: 0.78 / 0.22  
  - CMO: 0.68 / 0.32  
  - COO: 0.74 / 0.26  
  - CTO: 0.72 / 0.28  
  - Founder: 0.70 / 0.30  
  - Investor: 0.76 / 0.24  

---

🧭 Prompt Scaffolding

System (Domain Contract)
`
You are the [ROLE]. Provide precise, evidence‑backed analysis with explicit assumptions and role‑specific KPIs.
Avoid leadership rhetoric in the Analysis section.
`

System (Leadership Contract)
`
Reframe the analysis into an executive decision narrative.
Present options, risks, a single recommendation, and next actions with owner, time, and form.
`

Output Schema
- Analysis: Assumptions, KPIs/evidence (role‑specific)  
- Scenarios: 2–3 options with trade‑offs  
- Recommendation: One call, rationale, success criteria  
- Actions: Owner, time, form  

---

🛡️ Guardrails and Evaluation

Founder guardrails
- Must tie vision claims to product roadmap, market structure, and measurable milestones  
- Avoid pure rhetoric without grounding  
- Check for explicit link between mission and 12–24‑month actions  

Investor guardrails
- Must include valuation impact, capital efficiency, liquidity, exit horizon  
- Avoid fabricated figures or excessive short‑term bias  
- Check numeric consistency and governance implications  

Shared leadership checks
- Options, risks, single recommendation, actions  
- Explicit trade‑offs when roles are in tension (e.g., Founder vs. Investor)  

---

🔄 Self‑Learning Loop

How It Works
- Situations: Real or synthetic boardroom prompts  
- Mentors: Human reviewers provide corrections, refinements, or alternative framings  
- Loop: Each interaction becomes a new training example (prompt → output → correction → improved output)  

Dataset Expansion
- Original dataset: Curated, clean, role‑specific baseline (frozen as “golden set”)  
- Self‑learning dataset: Continuously expanding with mentor‑guided examples  
- Fine‑tuning blend:  
  - 60–80% original dataset (anchor)  
  - 20–40% self‑learning data (growth)  
- Versioning: Keep original datasets frozen; append loop data as v2/v3; track provenance  

---

🚦 When to Upgrade to 13B
Upgrade from Llama‑3.1‑8B‑Instruct → 13B when:
1. Reasoning depth feels capped (shallow trade‑offs, missing second‑order effects)  
2. Cross‑role simulations blur voices (Founder vs. Investor vs. CFO not clearly separated)  
3. Leadership tone lacks gravitas (recommendations feel thin or generic)  
4. Evaluation metrics plateau (role fidelity and leadership clarity scores stop improving despite more loop data)  

---

🔄 How to Upgrade to 13B

Step 1: Preserve Learning
- Keep the original dataset intact  
- Carry forward the self‑learning dataset (situations + mentor feedback)  
- Treat the 8B system as a teacher (generate synthetic transcripts for distillation)

Step 2: Train New 13B LoRAs
- Retrain domain + leadership adapters on 13B using:  
  - Original dataset  
  - Self‑learning dataset  
  - Distilled outputs from 8B (optional, for stylistic continuity)

Step 3: Parallel Evaluation
- Run 8B and 13B side‑by‑side on the same boardroom scenarios  
- Compare role fidelity, leadership clarity, and decision quality  

Step 4: Transition
- Gradually shift the self‑learning loop to 13B  
- Phase out 8B once 13B consistently outperforms it  

---

✨ Summary
- Start with Llama‑3.1‑8B‑Instruct: efficient, adapter‑friendly, perfect for prototyping  
- Use one domain LoRA + leadership LoRA at a time: preserves role fidelity while ensuring executive framing  
- Domain LoRAs include: CFO, CMO, COO, CTO, Founder, Investor  
- Expand dataset via self‑learning: every situation + mentor correction becomes new training data  
- Upgrade to 13B when 8B hits reasoning/tone limits: retrain adapters on 13B with original + loop data, optionally distill from 8B  
- Result: A living, evolving Boardroom Simulation Engine where each role — operational, visionary, or capital — speaks with specialist precision and unified leadership authority


---