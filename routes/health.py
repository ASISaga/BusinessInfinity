import json
import azure.functions as func

class HealthEndpoint:
    def __init__(self, business_infinity=None):
        self.business_infinity = business_infinity

    async def handle(self, req: func.HttpRequest) -> func.HttpResponse:
        """Health check endpoint (instance-based)"""
        try:
            if self.business_infinity:
                status = await self.business_infinity.get_business_status()
                return func.HttpResponse(
                    json.dumps({"status": "healthy", "system": "business_infinity", "details": status}),
                    mimetype="application/json",
                    status_code=200
                )
            else:
                return func.HttpResponse(
                    json.dumps({"status": "limited", "system": "fallback", "message": "Business Infinity not available"}),
                    mimetype="application/json", 
                    status_code=200
                )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"status": "error", "error": str(e)}),
                mimetype="application/json",
                status_code=500
            )

