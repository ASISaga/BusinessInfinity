import json
import azure.functions as func

async def main(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({"ok": True}),
        mimetype="application/json",
        status_code=200
    )