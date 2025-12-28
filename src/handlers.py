"""
BusinessInfinity Route Handlers

This module provides all HTTP route handlers for BusinessInfinity,
designed to work with the generic runtime route registry.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    import azure.functions as func

try:
    import azure.functions as func

    AZURE_FUNCTIONS_AVAILABLE = True
except ImportError:
    AZURE_FUNCTIONS_AVAILABLE = False
    func = None  # type: ignore

from runtime import AuthLevel, HttpMethod, RouteRegistry

from .app import get_business_infinity


class HealthHandler:
    """Health check endpoint handler."""

    async def health(self, req: Any) -> Any:
        """Health check endpoint."""
        try:
            app = get_business_infinity()
            status = "healthy" if app and app._initialized else "initializing"
            health_data = {
                "service": "BusinessInfinity",
                "status": status,
                "version": "2.0.0",
                "timestamp": datetime.utcnow().isoformat(),
            }

            if app:
                health_data["aos_available"] = app.aos is not None

            status_code = 200 if status == "healthy" else 503
            return func.HttpResponse(
                body=json.dumps(health_data),
                status_code=status_code,
                headers={"Content-Type": "application/json"},
            )
        except Exception as e:
            return func.HttpResponse(
                body=json.dumps({"status": "error", "error": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"},
            )

    async def status(self, req) -> Any:
        """Detailed status endpoint."""
        try:
            app = get_business_infinity()
            if not app:
                return func.HttpResponse(
                    body=json.dumps({"error": "Application not initialized"}),
                    status_code=503,
                    headers={"Content-Type": "application/json"},
                )

            status_data = await app.get_business_status()
            return func.HttpResponse(
                body=json.dumps(status_data, default=str),
                status_code=200,
                headers={"Content-Type": "application/json"},
            )
        except Exception as e:
            return func.HttpResponse(
                body=json.dumps({"error": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"},
            )


class AgentsHandler:
    """Agent management endpoint handlers."""

    async def list_agents(self, req) -> Any:
        """List all available agents."""
        try:
            app = get_business_infinity()
            if not app:
                return func.HttpResponse(
                    body=json.dumps({"agents": [], "error": "Application not initialized"}),
                    status_code=503,
                    headers={"Content-Type": "application/json"},
                )

            agents = app.list_agents()
            return func.HttpResponse(
                body=json.dumps({"agents": agents}),
                status_code=200,
                headers={"Content-Type": "application/json"},
            )
        except Exception as e:
            return func.HttpResponse(
                body=json.dumps({"error": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"},
            )

    async def ask_agent(self, req) -> Any:
        """Ask an agent a question."""
        try:
            app = get_business_infinity()
            if not app:
                return func.HttpResponse(
                    body=json.dumps({"error": "Application not initialized"}),
                    status_code=503,
                    headers={"Content-Type": "application/json"},
                )

            agent_role = req.route_params.get("agent_role")
            if not agent_role:
                return func.HttpResponse(
                    body=json.dumps({"error": "Agent role required"}),
                    status_code=400,
                    headers={"Content-Type": "application/json"},
                )

            try:
                body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    body=json.dumps({"error": "Invalid JSON"}),
                    status_code=400,
                    headers={"Content-Type": "application/json"},
                )

            message = body.get("message", "")
            context = body.get("context", {})

            if not message:
                return func.HttpResponse(
                    body=json.dumps({"error": "Message is required"}),
                    status_code=400,
                    headers={"Content-Type": "application/json"},
                )

            response = await app.ask_agent(agent_role, message, context)
            return func.HttpResponse(
                body=json.dumps(response, default=str),
                status_code=200,
                headers={"Content-Type": "application/json"},
            )
        except Exception as e:
            return func.HttpResponse(
                body=json.dumps({"error": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"},
            )


class WorkflowsHandler:
    """Workflow management endpoint handlers."""

    async def execute_workflow(self, req) -> Any:
        """Execute a workflow."""
        try:
            app = get_business_infinity()
            if not app:
                return func.HttpResponse(
                    body=json.dumps({"error": "Application not initialized"}),
                    status_code=503,
                    headers={"Content-Type": "application/json"},
                )

            workflow_name = req.route_params.get("workflow_name")
            if not workflow_name:
                return func.HttpResponse(
                    body=json.dumps({"error": "Workflow name required"}),
                    status_code=400,
                    headers={"Content-Type": "application/json"},
                )

            try:
                params = req.get_json() if req.get_body() else {}
            except ValueError:
                params = {}

            result = await app.execute_workflow(workflow_name, params)
            return func.HttpResponse(
                body=json.dumps(result, default=str),
                status_code=200,
                headers={"Content-Type": "application/json"},
            )
        except Exception as e:
            return func.HttpResponse(
                body=json.dumps({"error": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"},
            )


class MCPHandler:
    """MCP server management endpoint handlers."""

    async def list_mcp_servers(self, req) -> Any:
        """List registered MCP servers."""
        try:
            app = get_business_infinity()
            if not app:
                return func.HttpResponse(
                    body=json.dumps({"servers": {}}),
                    status_code=200,
                    headers={"Content-Type": "application/json"},
                )

            servers = app.list_mcp_servers()
            return func.HttpResponse(
                body=json.dumps({"servers": servers}),
                status_code=200,
                headers={"Content-Type": "application/json"},
            )
        except Exception as e:
            return func.HttpResponse(
                body=json.dumps({"error": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"},
            )


def register_routes(registry: RouteRegistry) -> None:
    """
    Register all BusinessInfinity routes to the route registry.

    Args:
        registry: The route registry to register routes to
    """
    # Create handlers
    health = HealthHandler()
    agents = AgentsHandler()
    workflows = WorkflowsHandler()
    mcp = MCPHandler()

    # Health & Status
    registry.register(
        path="health",
        handler=health.health,
        methods=[HttpMethod.GET],
        auth_level=AuthLevel.ANONYMOUS,
        description="Health check endpoint",
        tags=["health", "monitoring"],
    )

    registry.register(
        path="status",
        handler=health.status,
        methods=[HttpMethod.GET],
        auth_level=AuthLevel.FUNCTION,
        description="Detailed status endpoint",
        tags=["health", "monitoring"],
    )

    # Agents
    registry.register(
        path="agents",
        handler=agents.list_agents,
        methods=[HttpMethod.GET],
        auth_level=AuthLevel.FUNCTION,
        description="List all agents",
        tags=["agents"],
    )

    registry.register(
        path="agents/{agent_role}/ask",
        handler=agents.ask_agent,
        methods=[HttpMethod.POST],
        auth_level=AuthLevel.FUNCTION,
        description="Ask an agent a question",
        tags=["agents"],
    )

    # Workflows
    registry.register(
        path="workflows/{workflow_name}",
        handler=workflows.execute_workflow,
        methods=[HttpMethod.POST],
        auth_level=AuthLevel.FUNCTION,
        description="Execute a workflow",
        tags=["workflows"],
    )

    # MCP
    registry.register(
        path="mcp/servers",
        handler=mcp.list_mcp_servers,
        methods=[HttpMethod.GET],
        auth_level=AuthLevel.FUNCTION,
        description="List MCP servers",
        tags=["mcp"],
    )
