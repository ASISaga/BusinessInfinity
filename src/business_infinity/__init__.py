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

Usage::

    from business_infinity.workflows import app

    # function_app.py:
    functions = app.get_functions()
"""

__version__ = "5.0.0"
