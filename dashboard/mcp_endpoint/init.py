import json
import azure.functions as func
from mcp_handlers import handle_mcp

async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            mimetype="application/json",
            status_code=400
        )

    response = await handle_mcp(body)
    return func.HttpResponse(
        json.dumps(response),
        mimetype="application/json",
        status_code=200
    )