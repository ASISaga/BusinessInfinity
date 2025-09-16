# Persistent AI Agent Blueprint

## Purpose
Act as the orchestrator that binds the LLM, Organizational Data MCP, and Community Engagement MCP into a coherent, role-specific executive.

## Core Responsibilities
- **Context orchestration:** Assemble minimal, relevant bundles for each task.
- **Reasoning & creation:** Invoke LLM for drafts, critiques, scores, and plans.
- **Governance:** Apply vision, purpose, and decision policies; trigger human-in-loop when needed.
- **Execution:** Direct Community MCP for publishing, engagement, and analytics.
- **Memory stewardship:** Persist artifacts/events in Organizational MCP; decide horizon.
- **Learning:** Merge performance with enterprise outcomes; adjust strategies.

## Decision Protocol Participation
- **Scoring:** Evaluate options for vision alignment, purpose alignment, and legendary lens.
- **Consensus:** Submit scores to aggregation; respect DecisionPolicy thresholds.
- **Postmortem:** Review outcomes; update heuristics and prompt patterns.

## Interfaces
- **To LLM:** `prompt(task, context, constraints) → output`
- **To Organizational MCP:** `get_context`, `put_artifact`, `append_event`, `link_provenance`
- **To Community MCP:** `publish_post`, `reply_to_comment`, `monitor_mentions`, `post_performance_report`

## Design Principles
- **Relevance over volume:** Only include what’s needed for the task.
- **Freshness bias:** Prefer recent data unless historical patterns are required.
- **Provenance integrity:** Link every action to its source context and decision rationale.
- **Adaptability:** Same pattern applies to CEO, CMO, CFO, CTO, COO, CHRO, Investor, Founder, etc.