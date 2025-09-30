
import json
import azure.functions as func
from datetime import datetime

class HealthEndpoint:
    def __init__(self, business_infinity, business_infinity_available):
        self.business_infinity = business_infinity
        self.business_infinity_available = business_infinity_available

    async def handle(self, req: func.HttpRequest) -> func.HttpResponse:
        """Unified health check endpoint (instance-based)"""
        try:
            health_status = {
                "service": "Business Infinity",
                "status": "healthy" if self.business_infinity_available else "degraded",
                "aos_available": self.business_infinity_available,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "2.0.0-refactored"
            }
            if self.business_infinity:
                # Optionally include more details if available
                if hasattr(self.business_infinity, 'business_context'):
                    health_status["business_context"] = self.business_infinity.business_context
                if hasattr(self.business_infinity, 'get_business_status'):
                    try:
                        status = await self.business_infinity.get_business_status()
                        health_status["details"] = status
                    except Exception as e:
                        health_status["details_error"] = str(e)
            status_code = 200 if self.business_infinity_available else 503
            return func.HttpResponse(
                json.dumps(health_status),
                status_code=status_code,
                headers={"Content-Type": "application/json"}
            )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"status": "error", "error": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )
