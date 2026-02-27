"""BusinessInfinity workflows — boardroom-driven perpetual orchestrations.

The **boardroom session** is the primary perpetual orchestration that sits at
the heart of BusinessInfinity.  All C-suite agents collaborate in a continuous
autonomous boardroom on strategic decisions, operational reviews, and governance.
Specialised orchestrations (strategic review, market analysis, etc.) and
enterprise capability workflows are sub-concerns that support the boardroom.

Each workflow function is decorated with ``@app.workflow`` from the AOS Client
SDK.  The SDK handles all Azure Functions scaffolding (HTTP triggers,
Service Bus triggers, authentication, health endpoints).

**Package layout**

.. code-block:: text

    workflows/
      _app.py            — AOSApp singleton + shared utilities
      orchestrations.py  — primary boardroom + 7 specialised perpetual orchestrations
      enterprise.py      — enterprise SDK capabilities + event handlers
      beyond_sdk.py      — 10 beyond-SDK enhancement workflows
      conversations.py   — 5 boardroom conversation workflows
      mentor.py          — 5 mentor mode / LoRA workflows
      network.py         — 5 network management workflows
      onboarding.py      — 5 onboarding workflows
      health.py          — 2 health & analytics workflows

All public symbols from each submodule are re-exported here so that the
import path ``from business_infinity.workflows import app, ...`` continues to
work unchanged.
"""

from __future__ import annotations

# ── Shared infrastructure ────────────────────────────────────────────────────
# Import first so the `app` singleton exists before any submodule decorates it.

from ._app import (
    C_SUITE_AGENT_IDS,
    C_SUITE_TYPES,
    WORKFLOW_DEPENDENCIES,
    _MIDDLEWARE,
    _ORCHESTRATION_GROUPS,
    _WEBHOOK_FILTERS,
    app,
    c_suite_orchestration,
    decrypt_sensitive_fields,
    default_rate_limiter,
    encrypt_sensitive_fields,
    logger,
    select_c_suite_agents,
    use_middleware,
    RateLimiter,
)

# ── Workflow submodules ───────────────────────────────────────────────────────
# Importing each submodule executes its module-level @app.workflow decorators,
# registering every workflow with the `app` singleton defined in `_app`.

from . import (  # noqa: E402, F401
    orchestrations,
    enterprise,
    beyond_sdk,
    conversations,
    health,
    mentor,
    network,
    onboarding,
)

# ── Per-domain public symbols ────────────────────────────────────────────────
# Re-export constants that tests import directly from `business_infinity.workflows`.

from .beyond_sdk import evaluate_webhook_filter
from .conversations import _CONVERSATION_DOC_TYPE
from .mentor import _TRAINING_JOB_DOC_TYPE
from .network import _NEGOTIATION_DOC_TYPE
from .onboarding import _OAUTH_URLS, _ONBOARDING_CONSENT_DOC_TYPE

__all__ = [
    # app + observability
    "app",
    "logger",
    # C-suite helpers
    "C_SUITE_AGENT_IDS",
    "C_SUITE_TYPES",
    "select_c_suite_agents",
    "c_suite_orchestration",
    # Rate limiting
    "RateLimiter",
    "default_rate_limiter",
    # Encryption
    "encrypt_sensitive_fields",
    "decrypt_sensitive_fields",
    # Workflow dependency chains
    "WORKFLOW_DEPENDENCIES",
    # Bulk orchestration groups
    "_ORCHESTRATION_GROUPS",
    # Conditional webhooks
    "_WEBHOOK_FILTERS",
    "evaluate_webhook_filter",
    # Middleware
    "_MIDDLEWARE",
    "use_middleware",
    # Conversations
    "_CONVERSATION_DOC_TYPE",
    # Mentor mode
    "_TRAINING_JOB_DOC_TYPE",
    # Network management
    "_NEGOTIATION_DOC_TYPE",
    # Onboarding
    "_ONBOARDING_CONSENT_DOC_TYPE",
    "_OAUTH_URLS",
]
