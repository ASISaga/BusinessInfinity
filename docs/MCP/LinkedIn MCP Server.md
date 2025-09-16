# 3-LinkedIn-MCP-Server.md

## Purpose
- **Role:** Protocol-native execution adapter for LinkedIn, built on the official API and exposed as strict, safe MCP tools.
- **Goal:** Execute publishing and engagement reliably, surface normalized events and analytics, and preserve provenance for persistence and audit.

---

## Tool contracts (strict)
- **draft_post(content, metadata) → PostDraft.v1**  
  - **Metadata:** CampaignId, intended_audience, hashtags, assets[], tone hints.
- **publish_post(draft_id, schedule?) → PublishedPost.v1**  
  - **Idempotency:** Client token derived from draft ArtifactId.
- **schedule_post(draft_id, datetime) → ScheduledPost.v1**
- **reply_to_comment(comment_id, content, metadata?) → CommentReply.v1**  
  - **De-duplication:** Hash(parent CommentId + content digest).
- **start_conversation(post_url, content, metadata?) → CommentReply.v1**
- **monitor_mentions(keywords, frequency, window) → MentionFeed.v1**
- **subscribe_webhooks(callback_url, events[]) → SubscriptionReceipt.v1**
- **post_performance_report(post_id, window) → PerformanceReport.v1**
- **export_thread(post_id) → ThreadExport.v1**
- **list_company_posts(window, filters?) → PostList.v1**

> All outputs include provenance fields needed by the Marketing MCP (e.g., LinkedIn IDs, timestamps, source, latency).

---

## Event normalization
- **EngagementEvent.v1:**  
  - **Type:** like, comment, share, mention, follow.  
  - **Context:** PostId/CommentId, ThreadId, actor_profile_hash, language (if available), detected_intent (optional), sentiment (optional).  
  - **Timing:** source_timestamp, received_at, processing_latency.
- **Provenance links:**  
  - **Edges:** ArtifactId ↔ LinkedIn PostId, PostId ↔ ThreadId, ArtifactId ↔ ExperimentId.

---

## Guarantees and stewardship
- **Idempotency & retries:** Deterministic client tokens; exponential backoff with jitter; exactly-once publish intent where possible.  
- **Rate limits:** Central scheduler smooths bursts; exposes remaining budget to the agent; safe degradation rules.  
- **Safety flags:** Platform policy warnings (e.g., content length, restricted topics) surfaced before execution.  
- **Time integrity:** Record platform vs processing times; maintain monotonic sequence per thread.  
- **Privacy:** Avoid storing raw PII; hash actor references before emitting artifacts.

---

## Error surfaces
- **Operational:** Rate-limit exceeded, network failure, expired tokens, permission scopes.  
- **Semantic:** Invalid asset references, content too long, invalid post URL, unsupported media types.  
- **Policy:** Platform violations, blocked categories, missing disclosures.

---

## Observability
- **Metrics:** Success rates by operation, latency distributions, retry counts, rate-limit headroom.  
- **Logs:** Structured logs per request with correlation IDs; redaction of sensitive fields.  
- **Alerts:** Webhook delivery failures, persistent retries, anomaly in engagement mix (spam spikes).

---

## Security and compliance
- **Auth:** Scoped tokens; least-privilege; rotation policy.  
- **Transport:** TLS for all callbacks; signature verification for webhooks.  
- **Isolation:** No long-term PII storage; ephemeral caches only for operation flow.

---

## Versioning and evolution
- **Contract versioning:** vN on artifact types and tool contracts; additive fields first; deprecation windows.  
- **Compatibility:** Backward-compatible parsers; explicit feature flags for new LinkedIn API capabilities.