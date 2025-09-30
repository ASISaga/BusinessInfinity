import azure.functions as func
import json
from datetime import datetime

class BusinessHealthEndpoint:
    def __init__(self, business_infinity, business_infinity_available):
        self.business_infinity = business_infinity
        self.business_infinity_available = business_infinity_available

    async def handle(self, req: func.HttpRequest) -> func.HttpResponse:
        health_status = {
            "service": "Business Infinity",
            "status": "healthy" if self.business_infinity_available else "degraded",
            "aos_available": self.business_infinity_available,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0-refactored"
        }
        if self.business_infinity:
            health_status["business_context"] = self.business_infinity.business_context
        status_code = 200 if self.business_infinity_available else 503
        return func.HttpResponse(
            json.dumps(health_status),
            status_code=status_code,
            headers={"Content-Type": "application/json"}
        )
