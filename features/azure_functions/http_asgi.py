import azure.functions as func
from azure.functions import AsgiFunctionHandler
from ..app.app import app

handler = AsgiFunctionHandler(app)

async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return await handler.handle_async(req, context)