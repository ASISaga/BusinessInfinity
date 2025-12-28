import json
import azure.functions as func

class WorkflowsEndpoint:
    def __init__(self, business_infinity=None, logger=None):
        self.business_infinity = business_infinity
        self.logger = logger

    async def execute_workflow(self, req: func.HttpRequest) -> func.HttpResponse:
        """Execute a business workflow"""
        try:
            workflow_name = req.route_params.get('workflow_name')
            if not workflow_name:
                return func.HttpResponse(
                    json.dumps({"error": "Workflow name required"}),
                    mimetype="application/json",
                    status_code=400
                )

            # Parse request body
            try:
                workflow_params = req.get_json()
            except ValueError:
                workflow_params = {}

            if self.business_infinity:
                workflow_id = await self.business_infinity.execute_business_workflow(workflow_name, workflow_params)
                return func.HttpResponse(
                    json.dumps({
                        "workflow_id": workflow_id,
                        "workflow_name": workflow_name,
                        "status": "started"
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
            if self.logger:
                self.logger.error(f"Error executing workflow {workflow_name}: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )
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
