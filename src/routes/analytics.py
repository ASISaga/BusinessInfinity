import azure.functions as func
import json

class AnalyticsEndpoint:
    def __init__(self, business_infinity, business_infinity_available):
        self.business_infinity = business_infinity
        self.business_infinity_available = business_infinity_available

    async def get_business_analytics(self, req: func.HttpRequest) -> func.HttpResponse:
        if not self.business_infinity_available or not self.business_infinity:
            return func.HttpResponse(
                json.dumps({"error": "Business Infinity not available"}),
                status_code=503,
                headers={"Content-Type": "application/json"}
            )
        await self.business_infinity._initialize_task
        analytics = await self.business_infinity.get_business_analytics()
        return func.HttpResponse(
            json.dumps(analytics),
            headers={"Content-Type": "application/json"}
        )

    async def get_performance_report(self, req: func.HttpRequest) -> func.HttpResponse:
        if not self.business_infinity_available or not self.business_infinity:
            return func.HttpResponse(
                json.dumps({"error": "Business Infinity not available"}),
                status_code=503,
                headers={"Content-Type": "application/json"}
            )
        await self.business_infinity._initialize_task
        if self.business_infinity.analytics_engine:
            performance_report = await self.business_infinity.analytics_engine.generate_performance_report()
        else:
            performance_report = {"error": "Analytics engine not available"}
        return func.HttpResponse(
            json.dumps(performance_report),
            headers={"Content-Type": "application/json"}
        )
