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

Usage::

    from business_infinity.workflows import app

    # function_app.py:
    functions = app.get_functions()
"""

__version__ = "5.0.0"
