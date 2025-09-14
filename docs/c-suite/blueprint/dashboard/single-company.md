# MCP‑UI — Single Company Spec

## Purpose
Provide a unified, role‑aware interface for a company’s AI C‑suite agents and human stakeholders to interact with local MCP servers, visualise artifacts, participate in decision protocols, and monitor performance.

---

## Core Modules

### 1. Artifact Browser
- **Functions:**
  - Search, filter, and preview artifacts from Organizational Data MCP and Community Engagement MCP.
  - Inline provenance view (source system, timestamps, signatures).
- **Supported Types:** PostDraft, DecisionTree, PerformanceReport, GovernanceDecision, ImprovementPlan, etc.

### 2. Decision Workspace
- **Functions:**
  - Visualise DecisionTree.v1 as an interactive graph.
  - Display per‑agent DecisionScore.v1 with rationale.
  - Simulate “what‑if” changes to weights or thresholds.
- **Integration:** Pulls live scoring data from Persistent AI Agents.

### 3. Execution Console
- **Functions:**
  - Trigger MCP tool actions (publish_post, fetch_from_system, link_provenance).
  - Schedule or approve actions with governance checks.
- **Safety:** Enforce DecisionPolicy.v1 before execution.

### 4. Metrics & Dashboards
- **Functions:**
  - Live KPIs from PerformanceReport.v1.
  - Role‑specific dashboards (CEO: portfolio map; CFO: budget vs actual; COO: capacity utilisation).
- **Data Sources:** Organizational Data MCP, Community Engagement MCP.

### 5. Governance & Policy Panel
- **Functions:**
  - View/edit DecisionPolicy.v1 and Purpose.v1 per agent.
  - Manage role‑based access and data visibility scopes.
- **Audit:** All changes logged to MCP event streams.

---

## Role‑Aware Views
- **CEO:** Strategic dashboards, consensus status, vision evolution tracker.
- **CFO:** Financial KPIs, ROI scoring panels, budget allocation tools.
- **COO:** Supply chain maps, capacity planning boards.
- **CTO:** Architecture diagrams, tech debt registers, release calendars.
- **CMO:** Campaign calendars, engagement heatmaps.
- **CHRO:** Talent pipeline charts, engagement survey dashboards.
- **Founder:** Innovation pipeline boards, cultural initiatives tracker.
- **Investor:** Capital flow charts, market sentiment feeds.

---

## Integration Points
- **Organizational Data MCP:** Artifact/Context views, performance data.
- **Community Engagement MCP:** Channel activity streams, engagement metrics.
- **Persistent AI Agents:** Push alerts, scoring updates, governance checks.

---

## Governance & Security
- **Authentication:** Role‑based, scoped to company and archetype.
- **Audit Trails:** Every UI action logs to MCP event streams.
- **Data Masking:** Enforce visibility scopes in UI layer.
- **Signatures:** Actions and approvals cryptographically signed.

---

## Observability
- **Metrics:** UI usage, decision throughput, approval latency.
- **Alerts:** Governance blocks, SLA breaches, anomaly detection.