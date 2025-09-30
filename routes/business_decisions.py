import azure.functions as func
import json

class BusinessDecisionsEndpoint:
    def __init__(self, business_infinity, business_infinity_available):
        self.business_infinity = business_infinity
        self.business_infinity_available = business_infinity_available

    async def make_strategic_decision(self, req: func.HttpRequest) -> func.HttpResponse:
        if not self.business_infinity_available or not self.business_infinity:
            return func.HttpResponse(
                json.dumps({"error": "Business Infinity not available"}),
                status_code=503,
                headers={"Content-Type": "application/json"}
            )
        await self.business_infinity._initialize_task
        try:
            request_json = req.get_json()
            decision_context = request_json.get("decision_context", {})
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        decision_result = await self.business_infinity.make_strategic_decision(decision_context)
        return func.HttpResponse(
            json.dumps(decision_result),
            headers={"Content-Type": "application/json"}
        )
