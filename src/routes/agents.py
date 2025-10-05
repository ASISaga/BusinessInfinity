
"""
BusinessInfinity API Routes - Agents

Provides HTTP API endpoints for interacting with business agents
through the BusinessInfinity system.
"""

import json
import azure.functions as func
from datetime import datetime
from typing import Optional, Dict, Any

# Import business infinity core
try:
    from src.orchestration.business_manager import BusinessManager
    from src.agents.agent_coordinator import AgentCoordinator
    BUSINESS_INFINITY_AVAILABLE = True
except ImportError:
    BUSINESS_INFINITY_AVAILABLE = False
    print("Warning: BusinessInfinity core not available")


class AgentsEndpoint:

    async def list_business_agents(self, req: func.HttpRequest) -> func.HttpResponse:
        """List detailed info for all business agents (legacy endpoint)."""

        import json
        import azure.functions as func
        from datetime import datetime

        class AgentsEndpoint:
            def __init__(self, business_infinity=None):
                self.business_infinity = business_infinity

            async def list_agents(self, req: func.HttpRequest) -> func.HttpResponse:
                """List all available business agents"""
                try:
                    if self.business_infinity:
                        agents = self.business_infinity.list_agents()
                        return func.HttpResponse(
                            json.dumps({"agents": agents}),
                            mimetype="application/json",
                            status_code=200
                        )
                    else:
                        return func.HttpResponse(
                            json.dumps({"agents": [], "error": "Business Infinity not available"}),
                            mimetype="application/json",
                            status_code=503
                        )
                except Exception as e:
                    return func.HttpResponse(
                        json.dumps({"error": str(e)}),
                        mimetype="application/json",
                        status_code=500
                    )

            async def ask_agent(self, req: func.HttpRequest) -> func.HttpResponse:
                """Ask a specific agent a question"""
                try:
                    agent_role = req.route_params.get('agent_role')
                    if not agent_role:
                        return func.HttpResponse(
                            json.dumps({"error": "Agent role required"}),
                            mimetype="application/json",
                            status_code=400
                        )

                    # Parse request body
                    try:
                        req_body = req.get_json()
                    except ValueError:
                        return func.HttpResponse(
                            json.dumps({"error": "Invalid JSON in request body"}),
                            mimetype="application/json",
                            status_code=400
                        )

                    message = req_body.get('message', '')
                    context = req_body.get('context', {})

                    if not message:
                        return func.HttpResponse(
                            json.dumps({"error": "Message is required"}),
                            mimetype="application/json",
                            status_code=400
                        )

                    if self.business_infinity:
                        response = await self.business_infinity.ask_agent(agent_role, message, context)
                        return func.HttpResponse(
                            json.dumps({
                                "agent": agent_role,
                                "response": response,
                                "system": "business_infinity"
                            }),
                            mimetype="application/json",
                            status_code=200
                        )
                    else:
                        return func.HttpResponse(
                            json.dumps({"error": "Business Infinity not available"}),
                            mimetype="application/json",
                            status_code=503
                        )
                except Exception as e:
                    return func.HttpResponse(
                        json.dumps({"error": str(e)}),
                        mimetype="application/json",
                        status_code=500
                    )

            async def list_business_agents(self, req: func.HttpRequest) -> func.HttpResponse:
                if not getattr(self, 'business_infinity', None):
                    return func.HttpResponse(
                        json.dumps({"error": "Business Infinity not available"}),
                        status_code=503,
                        headers={"Content-Type": "application/json"}
                    )
                await self.business_infinity._initialize_task
                agents_info = {}
                for agent_id, agent in self.business_infinity.business_agents.items():
                    agents_info[agent_id] = {
                        "id": agent_id,
                        "role": agent.role,
                        "domain": agent.domain,
                        "expertise": agent.domain_expertise,
                        "kpis": list(agent.business_kpis.keys()),
                        "status": "active"
                    }
                return func.HttpResponse(
                    json.dumps({
                        "agents": agents_info,
                        "total_agents": len(agents_info),
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    headers={"Content-Type": "application/json"}
                )

            async def analyze_with_agent(self, req: func.HttpRequest) -> func.HttpResponse:
                if not getattr(self, 'business_infinity', None):
                    return func.HttpResponse(
                        json.dumps({"error": "Business Infinity not available"}),
                        status_code=503,
                        headers={"Content-Type": "application/json"}
                    )
                agent_role = req.route_params.get('agent_role')
                if not agent_role:
                    return func.HttpResponse(
                        json.dumps({"error": "Agent role is required"}),
                        status_code=400,
                        headers={"Content-Type": "application/json"}
                    )
                await self.business_infinity._initialize_task
                try:
                    request_json = req.get_json()
                    context = request_json.get("context", {})
                except ValueError:
                    return func.HttpResponse(
                        json.dumps({"error": "Invalid JSON in request body"}),
                        status_code=400,
                        headers={"Content-Type": "application/json"}
                    )
                agent = self.business_infinity.business_agents.get(agent_role.lower())
                if not agent:
                    return func.HttpResponse(
                        json.dumps({"error": f"Agent '{agent_role}' not found"}),
                        status_code=404,
                        headers={"Content-Type": "application/json"}
                    )
                analysis = await agent.analyze_business_context(context)
                return func.HttpResponse(
                    json.dumps(analysis),
                    headers={"Content-Type": "application/json"}
                )


        # Factory function must be defined before handlers
        def create_agents_api(business_manager: Optional['BusinessManager'] = None) -> AgentsEndpoint:
            """Create and configure the Agents API"""
            api = AgentsEndpoint(business_manager)
            # Optionally attach agent_coordinator if needed for new endpoints
            if BUSINESS_INFINITY_AVAILABLE:
                api.agent_coordinator = AgentCoordinator()
            else:
                api.agent_coordinator = None
            return api

        async def get_agent_handler(req: func.HttpRequest) -> func.HttpResponse:
            api = create_agents_api()
            if hasattr(api, 'get_agent_details'):
                return await api.get_agent_details(req)
            return func.HttpResponse(json.dumps({"error": "Not implemented"}), status_code=501)

        async def ask_agent_handler(req: func.HttpRequest) -> func.HttpResponse:
            """Azure Function handler for asking agent questions"""
            api = create_agents_api()
            return await api.ask_agent(req)


        async def assign_task_handler(req: func.HttpRequest) -> func.HttpResponse:
            """Azure Function handler for assigning tasks"""
            api = create_agents_api()
            return await api.assign_task(req)

        async def get_tasks_handler(req: func.HttpRequest) -> func.HttpResponse:
            """Azure Function handler for getting agent tasks"""
            api = create_agents_api()
            return await api.get_agent_tasks(req)
