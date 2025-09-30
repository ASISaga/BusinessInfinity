import azure.functions as func
import json

class BusinessWorkflowsEndpoint:
    def __init__(self, business_infinity, business_infinity_available):
        self.business_infinity = business_infinity
        self.business_infinity_available = business_infinity_available

    async def execute_business_workflow(self, req: func.HttpRequest) -> func.HttpResponse:
        if not self.business_infinity_available or not self.business_infinity:
            return func.HttpResponse(
                json.dumps({"error": "Business Infinity not available"}),
                status_code=503,
                headers={"Content-Type": "application/json"}
            )
        workflow_name = req.route_params.get('workflow_name')
        if not workflow_name:
            return func.HttpResponse(
                json.dumps({"error": "Workflow name is required"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        await self.business_infinity._initialize_task
        try:
            request_json = req.get_json()
            parameters = request_json.get("parameters", {})
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        workflow_result = await self.business_infinity.execute_business_workflow(workflow_name, parameters)
        return func.HttpResponse(
            json.dumps(workflow_result),
            headers={"Content-Type": "application/json"}
        )
