
import azure.functions as func
import logging
from http_router import HttpRouter, route
from api.extract_name import extract_name
from api.AuthHandler import AuthHandler

class HttpMainHandler:
    @route(methods=["GET", "POST"], path="/http_trigger")
    def handle(self, req: func.HttpRequest) -> func.HttpResponse:
        logging.info('Python HTTP trigger function processed a request.')
        resp_str, status_code = extract_name(req)
        return func.HttpResponse(resp_str, status_code=status_code)

    @route(methods=["POST"], path="/auth/login")
    def login_route(self, req: func.HttpRequest) -> func.HttpResponse:
        return self.auth_handler.login(req)

    @route(methods=["POST"], path="/auth/refresh")
    def refresh_route(self, req: func.HttpRequest) -> func.HttpResponse:
        return self.auth_handler.refresh(req)


router = HttpRouter()

http_main_handler = HttpMainHandler()
router.add_routes_from(http_main_handler)

auth_handler = AuthHandler()
router.add_routes_from(auth_handler)

def main(req: func.HttpRequest) -> func.HttpResponse:
    return router.handle(req)