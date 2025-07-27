import azure.functions as func
from azure.functions.decorators import FunctionApp, route
import logging
import json

app = FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="trigger-agent", methods=["POST"])
@app.function_name(name="TriggerAgentFunction")
def trigger_agent(req: func.HttpRequest) -> func.HttpResponse:
    try:
        payload = req.get_json()
        logging.info(f"Agent Triggered with payload: {payload}")

        # Replace this with your MCP orchestration logic
        result = {
            "status": "success",
            "agent_response": payload   # Echo or transformed
        }

        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=400,
            mimetype="application/json"
        )