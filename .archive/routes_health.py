
import json
import azure.functions as func
from datetime import datetime

class HealthEndpoint:
    def __init__(self, business_infinity, business_manager=None, agents_api=None, audit_viewer=None):
        self.business_infinity = business_infinity
        self.business_manager = business_manager
        self.agents_api = agents_api
        self.audit_viewer = audit_viewer

    async def handle(self, req: func.HttpRequest) -> func.HttpResponse:
        """Unified health check endpoint (instance-based)"""
        try:
            health_status = {
                "service": "Business Infinity",
                "status": "healthy" if self.business_infinity else "degraded",
                "aos_available": bool(self.business_infinity),
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
            status_code = 200 if self.business_infinity else 503
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

    async def system_status(self, req: func.HttpRequest) -> func.HttpResponse:
        """Detailed system status endpoint (moved from function_app.py)"""
        import azure.functions as func
        import json
        try:
            status = {
                "legacy_available": hasattr(self, 'LEGACY_AVAILABLE') and self.LEGACY_AVAILABLE,
                "components_initialized": {
                    "business_manager": self.business_manager is not None,
                    "agents_api": self.agents_api is not None,
                    "audit_viewer": self.audit_viewer is not None
                }
            }
            if self.business_manager:
                business_metrics = await self.business_manager.get_business_metrics()
                status["business_metrics"] = business_metrics
            return func.HttpResponse(
                json.dumps(status, default=str),
                mimetype="application/json",
                status_code=200
            )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )
