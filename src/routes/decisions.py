import json
import azure.functions as func

class DecisionsEndpoint:
    def __init__(self, business_infinity=None, logger=None):
        self.business_infinity = business_infinity
        self.logger = logger

    async def make_decision(self, req: func.HttpRequest) -> func.HttpResponse:
        try:
            # Parse request body
            try:
                decision_context = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    mimetype="application/json",
                    status_code=400
                )
            if self.business_infinity:
                result = await self.business_infinity.make_strategic_decision(decision_context)
                return func.HttpResponse(
                    json.dumps(result),
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
            if self.logger:
                self.logger.error(f"Error making decision: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

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
