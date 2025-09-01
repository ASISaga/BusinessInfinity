import json
import azure.functions as func
from pathlib import Path

manifest_path = Path(__file__).parent.parent / "manifest.json"
manifest = json.loads(manifest_path.read_text())

async def main(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps(manifest),
        mimetype="application/json",
        status_code=200
    )