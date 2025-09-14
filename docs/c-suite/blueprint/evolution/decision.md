# Business Infinity — Layer Evolution Decision Framework

## Purpose
Provide a governed, repeatable process for deciding **which layer** of Business Infinity to evolve — Agent, LLM, MCP, Governance, or Interaction — based on operational triggers, root cause analysis, and LLM scoring.  
The goal is to ensure that every evolution accelerates fulfilment of the company’s possibility (vision).

---

## 1. Step 1 — Detect a Trigger
From the defined evolution triggers (specification variation, operational pressure, performance differentiation, contextual divergence, scheduled iteration review, step‑change event), log the event in `ProvenanceReceipt.v1`.

---

## 2. Step 2 — Localise the Impact
Identify where the misalignment or opportunity originates.

| **Layer** | **Primary Signals** | **Typical Root Causes** |
|-----------|--------------------|-------------------------|
| **Agent Layer** | - Vision Alignment scores vary widely between agents in similar contexts<br>- Frequent overrides of a specific role’s decisions<br>- Slow consensus in Boardroom for that role’s domain | Role definition gaps, mis‑weighted scoring profiles, unclear authority, ineffective reasoning style |
| **LLM Layer** | - Low Vision Alignment across multiple agents using the same domain model<br>- Consistent misinterpretation of domain terms<br>- Poor performance in Mentor Mode scenario tests | Outdated fine‑tuning data, incomplete domain lexicon, suboptimal reasoning chain |
| **MCP Layer** | - Context drift between agents<br>- Decisions made on stale or incomplete context<br>- Cross‑org misalignment despite strong local scores | Context window too narrow, refresh cadence too slow, missing context sources, poor federation rules |
| **Governance / Policy Layer** | - High Vision Alignment but poor KPI outcomes<br>- Frequent guardrail breaches in certain decision types | Policy thresholds mis‑set, escalation rules too strict/loose |
| **Interaction Layer (IXL)** | - Delays or confusion in decision loops despite strong scores<br>- Users bypassing intended workflows | UI not surfacing right context, poor mode hand‑off, missing transparency cues |

---

## 3. Step 3 — Score the Evolution Options
Treat each possible layer change as an **option** in a *Blueprint DecisionTree*.

Example options:
- Adjust Agent blueprint
- Update LLM fine‑tuning
- Redesign MCP context rules

**LLM scoring** (vision + domain‑tuned) evaluates each option for:
1. Vision Alignment — Will this change accelerate the possibility?
2. Domain Fit — Will it solve the operational gap?
3. Resilience Potential — Will it hold under varied future conditions?

---

## 4. Step 4 — Simulate Before Committing
Run the top‑scoring option(s) in **Mentor Mode**:
- Replay relevant historical scenarios
- Inject synthetic stress‑tests
- Compare `DecisionScore.v1` patterns before/after

---

## 5. Step 5 — Governance Approval
Present:
- Trigger & root cause analysis
- LLM scorecard for each option
- Simulation results

Approval per relevant policy (local, inter‑org, multi‑party).

---

## 6. Step 6 — Deploy & Monitor
- Deploy the evolved blueprint for the chosen layer
- Monitor both **LLM scoring patterns** and **KPI trends**
- If improvement is not observed, revisit Step 3 with alternate layer options

---

## Quick Heuristics
- **If the *what* of decisions is wrong** → Evolve the **LLM** (knowledge & reasoning).  
- **If the *who* or *how* of decision authority is wrong** → Evolve the **Agent** (role, scope, scoring weights).  
- **If the *information they act on* is wrong or incomplete** → Evolve the **MCP** (context framing & exchange).  
- **If decisions are sound but outcomes still fail** → Evolve **Governance** (policies, thresholds) or **IXL** (interaction flow).

---