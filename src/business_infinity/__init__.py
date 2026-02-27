"""BusinessInfinity — lean Azure Functions client application.

BusinessInfinity demonstrates how a client application uses the Agent Operating
System as an infrastructure service.  It contains only business logic — agent
lifecycle, orchestration, messaging, and storage are handled by AOS.

The ``aos-client-sdk`` provides the ``AOSApp`` framework that handles all
Azure Functions scaffolding, Service Bus communication, authentication,
and deployment.  BusinessInfinity just defines workflows.

Enterprise capabilities (v4.0.0):

- Knowledge base search via SDK
- Risk registry (register, assess) via SDK
- Audit trail / decision logging via SDK
- Covenant creation via SDK
- Direct agent interaction via SDK
- MCP tool integration via SDK
- Observability (structured logging, correlation tracking)
- Workflow templates for code reuse

Usage::

    from business_infinity.workflows import app

    # function_app.py:
    functions = app.get_functions()
"""

__version__ = "4.0.0"
