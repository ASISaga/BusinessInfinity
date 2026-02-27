"""Shared application object and utilities for BusinessInfinity workflows.

This module defines the ``AOSApp`` singleton (:data:`app`) that all workflow
submodules import and decorate against, together with the beyond-SDK utilities
that are shared across multiple workflow domains:

- :class:`RateLimiter` / :data:`default_rate_limiter` — token-bucket throttle
- :func:`encrypt_sensitive_fields` / :func:`decrypt_sensitive_fields` — field-level encryption stub
- :data:`WORKFLOW_DEPENDENCIES` — upstream dependency metadata
- :data:`_ORCHESTRATION_GROUPS` — in-memory orchestration group registry
- :data:`_WEBHOOK_FILTERS` — per-webhook conditional filter rules
- :data:`_MIDDLEWARE` / :func:`use_middleware` — lightweight middleware list
- :data:`C_SUITE_TYPES` / :data:`C_SUITE_AGENT_IDS` — C-suite agent constants
- :func:`select_c_suite_agents` — catalog lookup helper
- :func:`c_suite_orchestration` — reusable orchestration template
"""

from __future__ import annotations

import asyncio
import base64
import hashlib  # noqa: F401 — re-exported for beyond_sdk.py audit hashing
import logging
import time
import uuid  # noqa: F401 — re-exported for submodules
from typing import Any, Callable, Dict, List, Optional

from aos_client import (
    AOSApp,
    AOSClient,
    AgentDescriptor,
    WorkflowRequest,
    workflow_template,
)
from aos_client.observability import ObservabilityConfig

logger = logging.getLogger(__name__)

app = AOSApp(
    name="business-infinity",
    observability=ObservabilityConfig(
        structured_logging=True,
        correlation_tracking=True,
        health_checks=["aos", "service-bus"],
    ),
)

# ── Beyond-SDK: Enhancement #2 — Rate Limiter ────────────────────────────────


class RateLimiter:
    """Token-bucket rate limiter for AOS SDK calls.

    Provides rate limiting that the SDK itself does not implement (see
    docs/AOS_NEXT_ENHANCEMENTS.md #2).  Use :attr:`default_rate_limiter` for
    the shared application-level limiter.

    Args:
        requests_per_minute: Sustained request rate.
        burst_limit: Maximum burst token capacity.
    """

    def __init__(self, requests_per_minute: int = 100, burst_limit: int = 20) -> None:
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self._tokens: float = float(burst_limit)
        self._last_refill: float = time.monotonic()
        self._lock: asyncio.Lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire one token, waiting with exponential back-off when exhausted."""
        async with self._lock:
            await self._refill()
            wait = 0.1
            while self._tokens < 1:
                await asyncio.sleep(wait)
                wait = min(wait * 2, 60 / self.requests_per_minute)
                await self._refill()
            self._tokens -= 1

    async def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(
            float(self.burst_limit),
            self._tokens + elapsed * (self.requests_per_minute / 60.0),
        )
        self._last_refill = now

    def get_quota_usage(self) -> Dict[str, Any]:
        """Return current token usage information."""
        return {
            "tokens_remaining": int(self._tokens),
            "burst_limit": self.burst_limit,
            "requests_per_minute": self.requests_per_minute,
        }


#: Shared application-level rate limiter (configurable at start-up).
default_rate_limiter = RateLimiter()


# ── Beyond-SDK: Enhancement #1 — Field-Level Encryption ─────────────────────


def encrypt_sensitive_fields(
    data: Dict[str, Any],
    fields: List[str],
    key_id: str = "boardroom-key",
) -> Dict[str, Any]:
    """Return a copy of *data* with the specified *fields* base-64 encoded.

    This is a lightweight placeholder implementation.  For production use,
    replace the encoding step with Azure Key Vault encryption as described in
    docs/AOS_NEXT_ENHANCEMENTS.md #1.  The ``key_id`` parameter is reserved
    for the Key Vault key name.

    Args:
        data:    Source dict (not mutated).
        fields:  Keys whose values should be encrypted.
        key_id:  Reserved for Key Vault key name (not used in this stub).

    Returns:
        New dict with the nominated fields replaced by ``"enc:<b64>"`` values.
    """
    result = dict(data)
    for field in fields:
        if field in result:
            raw = str(result[field]).encode()
            result[field] = f"enc:{base64.b64encode(raw).decode()}"
    return result


def decrypt_sensitive_fields(
    data: Dict[str, Any],
    fields: List[str],
    key_id: str = "boardroom-key",
) -> Dict[str, Any]:
    """Reverse :func:`encrypt_sensitive_fields` for the specified *fields*.

    Args:
        data:    Source dict (not mutated).
        fields:  Keys whose ``"enc:<b64>"`` values should be decoded.
        key_id:  Reserved for Key Vault key name (not used in this stub).

    Returns:
        New dict with the nominated fields decoded back to their original values.
    """
    result = dict(data)
    for field in fields:
        value = result.get(field)
        if isinstance(value, str) and value.startswith("enc:"):
            result[field] = base64.b64decode(value[4:]).decode()
    return result


# ── Beyond-SDK: Enhancement #3 — Workflow Dependency Chains ─────────────────

#: Maps each workflow name to the list of upstream workflows it depends on.
#: Used by :func:`start_workflow_chain` to enforce ordering.
WORKFLOW_DEPENDENCIES: Dict[str, List[str]] = {
    "compliance-report": ["covenant-compliance"],
    "risk-summary": ["risk-assess"],
    "risk-heatmap": ["risk-register", "risk-assess"],
    "verify-audit-integrity": ["log-decision"],
}


# ── Beyond-SDK: Enhancement #4 — Bulk Orchestration Groups ──────────────────

#: In-memory registry of orchestration groups.  Maps group_id → group metadata.
_ORCHESTRATION_GROUPS: Dict[str, Dict[str, Any]] = {}


# ── Beyond-SDK: Enhancement #7 — Conditional Webhook Filters ────────────────

#: Maps webhook_id → filter rule dict for conditional webhook evaluation.
_WEBHOOK_FILTERS: Dict[str, Dict[str, Any]] = {}


# ── Beyond-SDK: Enhancement #9 — Middleware / Plugin Architecture ────────────

#: Ordered list of middleware callables registered via :func:`use_middleware`.
_MIDDLEWARE: List[Callable] = []


def use_middleware(middleware_fn: Callable) -> None:
    """Register an async middleware to be invoked around each workflow call.

    Provides a lightweight plugin architecture as requested in
    docs/AOS_NEXT_ENHANCEMENTS.md #9.  Middleware functions receive
    ``(workflow_name: str, request: WorkflowRequest)`` as positional arguments.

    Example::

        async def logging_middleware(workflow_name, request):
            logger.info("Before %s", workflow_name)

        use_middleware(logging_middleware)
    """
    _MIDDLEWARE.append(middleware_fn)


# ── C-Suite Agent Selection ──────────────────────────────────────────────────

#: Agent types considered part of the C-suite
C_SUITE_TYPES = {"LeadershipAgent", "CMOAgent"}

#: Preferred C-suite agent IDs for BusinessInfinity orchestrations
C_SUITE_AGENT_IDS = ["ceo", "cfo", "cmo", "coo", "cto", "cso", "chro"]


async def select_c_suite_agents(client: AOSClient) -> List[AgentDescriptor]:
    """Select C-suite agents from the RealmOfAgents catalog.

    Returns agents matching :data:`C_SUITE_AGENT_IDS` or, if not found,
    agents whose ``agent_type`` is in :data:`C_SUITE_TYPES`.
    """
    all_agents = await client.list_agents()

    # Prefer explicit IDs
    by_id = {a.agent_id: a for a in all_agents}
    selected = [by_id[aid] for aid in C_SUITE_AGENT_IDS if aid in by_id]

    if not selected:
        # Fall back to type-based selection
        selected = [a for a in all_agents if a.agent_type in C_SUITE_TYPES]

    logger.info("Selected %d C-suite agents: %s", len(selected), [a.agent_id for a in selected])
    return selected


# ── Workflow Template (Enhancement #11) ──────────────────────────────────────


@workflow_template
async def c_suite_orchestration(
    request: WorkflowRequest,
    agent_filter: Callable[[AgentDescriptor], bool],
    purpose: str,
    purpose_scope: str,
) -> Dict[str, Any]:
    """Reusable template for C-suite orchestrations."""
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents if agent_filter(a)]
    if not agent_ids:
        raise ValueError(f"No matching agents available for '{purpose}'")
    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose=purpose,
        purpose_scope=purpose_scope,
        context=request.body,
    )
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}
