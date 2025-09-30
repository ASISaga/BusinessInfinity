import azure.functions as func
import json

class BusinessAgentsEndpoint:
    def __init__(self, business_infinity, business_infinity_available):
        self.business_infinity = business_infinity
        self.business_infinity_available = business_infinity_available

    async def list_business_agents(self, req: func.HttpRequest) -> func.HttpResponse:
        if not self.business_infinity_available or not self.business_infinity:
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
        if not self.business_infinity_available or not self.business_infinity:
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
