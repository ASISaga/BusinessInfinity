# LinkedIn MCP Server

## Purpose
Provide protocol‑native access to LinkedIn for the AI CMO agent, built on top of the official LinkedIn API.

## Core Responsibilities
- Execute publishing, commenting, and engagement actions.
- Monitor mentions, hashtags, and network signals.
- Retrieve analytics and engagement events.
- Normalize all outputs into MCP artifacts for persistence.

## Inputs
- Publishing intents from AI CMO agent.
- Engagement strategies and reply drafts from LLM.
- Monitoring parameters (keywords, hashtags, accounts).

## Outputs
- `PublishedPost.v1`
- `EngagementEvent.v1`
- `PerformanceReport.v1`
- `MentionFeed.v1`

## Integration Contracts
- `draft_post(content, metadata) → PostDraft.v1`
- `publish_post(draft_id, schedule) → PublishedPost.v1`
- `reply_to_comment(comment_id, content) → CommentReply.v1`
- `monitor_mentions(keywords, frequency) → MentionFeed.v1`
- `post_performance_report(post_id) → PerformanceReport.v1`
- `engagement_mapper(post_id) → EngagementNode.v1`

## Guarantees
- Idempotent operations keyed by ArtifactId.
- Rate‑limit stewardship and safe retries.
- All events normalized before persistence.