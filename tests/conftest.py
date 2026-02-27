"""Pytest configuration and AOS SDK mock for BusinessInfinity tests.

The ``aos-client-sdk`` is not available on PyPI; this conftest provides a
minimal in-process stub so that ``business_infinity.workflows`` can be
imported and all decorator-based registrations can be verified without a
live AOS installation.
"""

import sys
import types
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import MagicMock


# ── Minimal AOS SDK stub ─────────────────────────────────────────────────────


class ObservabilityConfig:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class AgentDescriptor:
    def __init__(self, agent_id: str, agent_type: str = "", capabilities: Optional[List[str]] = None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities or []

    def model_dump(self, **kwargs):
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities,
        }


class WorkflowRequest:
    def __init__(self, body: Dict[str, Any] = None, client=None):
        self.body = body or {}
        self.client = client or MagicMock()


class AOSApp:
    """Minimal AOSApp stub that collects decorator registrations."""

    def __init__(self, name: str, observability=None):
        self.name = name
        self.observability = observability
        self._workflows: Dict[str, Callable] = {}
        self._update_handlers: Dict[str, Callable] = {}
        self._mcp_tools: Dict[str, Callable] = {}
        self._covenant_event_handlers: Dict[str, Callable] = {}
        self._mcp_event_handlers: Dict[str, Callable] = {}
        self._webhooks: Dict[str, Callable] = {}

    # ── Decorator factories ──────────────────────────────────────────────────

    def workflow(self, name: str):
        def decorator(fn: Callable) -> Callable:
            self._workflows[name] = fn
            return fn
        return decorator

    def on_orchestration_update(self, workflow_name: str):
        def decorator(fn: Callable) -> Callable:
            self._update_handlers[workflow_name] = fn
            return fn
        return decorator

    def mcp_tool(self, tool_name: str):
        def decorator(fn: Callable) -> Callable:
            self._mcp_tools[tool_name] = fn
            return fn
        return decorator

    def on_covenant_event(self, event_type: str):
        def decorator(fn: Callable) -> Callable:
            self._covenant_event_handlers[event_type] = fn
            return fn
        return decorator

    def on_mcp_event(self, server: str, event_type: str):
        def decorator(fn: Callable) -> Callable:
            key = f"{server}:{event_type}"
            self._mcp_event_handlers[key] = fn
            return fn
        return decorator

    def webhook(self, name: str):
        def decorator(fn: Callable) -> Callable:
            self._webhooks[name] = fn
            return fn
        return decorator

    # ── Introspection helpers ────────────────────────────────────────────────

    def get_workflow_names(self) -> List[str]:
        return list(self._workflows.keys())

    def get_update_handler_names(self) -> List[str]:
        return list(self._update_handlers.keys())

    def get_mcp_tool_names(self) -> List[str]:
        return list(self._mcp_tools.keys())

    def get_covenant_event_handler_names(self) -> List[str]:
        return list(self._covenant_event_handlers.keys())

    def get_mcp_event_handler_names(self) -> List[str]:
        return list(self._mcp_event_handlers.keys())

    def get_webhook_names(self) -> List[str]:
        return list(self._webhooks.keys())

    def get_functions(self):
        return list(self._workflows.values())


class AOSClient:
    pass


def workflow_template(fn: Callable) -> Callable:
    """Identity decorator stub for @workflow_template."""
    return fn


# ── Stub module assembly ─────────────────────────────────────────────────────

_aos_client_module = types.ModuleType("aos_client")
_aos_client_module.AOSApp = AOSApp
_aos_client_module.AOSClient = AOSClient
_aos_client_module.AgentDescriptor = AgentDescriptor
_aos_client_module.WorkflowRequest = WorkflowRequest
_aos_client_module.workflow_template = workflow_template

_obs_module = types.ModuleType("aos_client.observability")
_obs_module.ObservabilityConfig = ObservabilityConfig

sys.modules["aos_client"] = _aos_client_module
sys.modules["aos_client.observability"] = _obs_module
