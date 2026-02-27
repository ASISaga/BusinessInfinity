"""BusinessInfinity — lean Azure Functions client application.

BusinessInfinity demonstrates how a client application uses the Agent Operating
System as an infrastructure service.  It contains only business logic — agent
lifecycle, orchestration, messaging, and storage are handled by AOS.

The ``aos-client-sdk`` provides the ``AOSApp`` framework that handles all
Azure Functions scaffolding, Service Bus communication, authentication,
and deployment.  BusinessInfinity just defines workflows.

Enterprise capabilities (v5.0.0):

- Knowledge base search, batch operations, versioning via SDK
- Risk registry (register, assess, heatmaps, summaries, trends) via SDK
- Audit trail / decision logging, compliance reports via SDK
- Covenant creation, lifecycle events via SDK
- Direct agent interaction via SDK
- MCP tool integration, bidirectional MCP events via SDK
- Analytics with dashboards and threshold alerts via SDK
- Observability (structured logging, correlation tracking)
- Workflow templates for code reuse
- Orchestration status streaming via SDK
- Webhook support for external notifications via SDK

Beyond-SDK capabilities (implemented locally, not yet in the AOS SDK):

- :class:`~business_infinity.workflows.RateLimiter` — token-bucket rate limiter
- :func:`~business_infinity.workflows.encrypt_sensitive_fields` — field-level encryption
- :func:`~business_infinity.workflows.decrypt_sensitive_fields` — field-level decryption
- ``WORKFLOW_DEPENDENCIES`` — workflow dependency chain metadata
- ``find-agents`` workflow — capability-based agent matching
- ``start-orchestration-group`` / ``get-group-status`` / ``stop-orchestration-group``
  workflows — bulk orchestration group management
- ``checkpoint-orchestration`` / ``resume-orchestration`` workflows — checkpointing
- ``register-conditional-webhook`` workflow — webhooks with event filters
- :func:`~business_infinity.workflows.evaluate_webhook_filter` — filter evaluation
- ``verify-audit-integrity`` workflow — SHA-256 hash-chain tamper detection
- ``start-workflow-chain`` workflow — dependency-aware workflow launch
- ``generate-api-docs`` workflow — auto-generated workflow documentation
- :func:`~business_infinity.workflows.use_middleware` — lightweight middleware support

Restored route-layer capabilities (conversations, mentor mode, network management,
onboarding, health, and analytics — not provided by the SDK):

Conversations:

- ``list-conversations`` — list boardroom conversations from the knowledge base
- ``create-conversation`` — create a new boardroom conversation
- ``sign-conversation`` — sign a conversation
- ``create-a2a-message`` — agent-to-agent communication
- ``get-conversation-events`` — recent conversation events for web clients

Mentor Mode:

- ``mentor-list-agents`` — list agents with LoRA / fine-tuning metadata
- ``mentor-chat`` — direct chat with a specific agent in mentor mode
- ``mentor-fine-tune`` — start a LoRA fine-tuning job
- ``mentor-training-logs`` — retrieve training logs for a job
- ``mentor-deploy-adapter`` — deploy a trained LoRA adapter

Network Management:

- ``network-status`` — local node status and peer count
- ``join-network`` — join the Global Boardroom Network
- ``discover-boardrooms`` — find peer boardrooms
- ``create-negotiation`` — create a peer negotiation record
- ``sign-agreement`` — sign a network agreement / covenant

Onboarding:

- ``onboarding-parse-website`` — extract company profile from a public URL
- ``onboarding-connect-system`` — generate OAuth URL to connect an external system
- ``onboarding-voice-profile`` — generate a founder voice profile via CMO agent
- ``onboarding-export-data`` — GDPR data-portability export
- ``onboarding-delete-data`` — GDPR right-to-erasure request

Health & Analytics:

- ``system-health`` — service health check
- ``business-analytics`` — business KPIs and agent summary

Usage::

    from business_infinity.workflows import app

    # function_app.py:
    functions = app.get_functions()
"""

__version__ = "5.0.0"
