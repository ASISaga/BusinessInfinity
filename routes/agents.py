import json
import azure.functions as func

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
