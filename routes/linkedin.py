import json
import azure.functions as func

class LinkedInEndpoint:
    def __init__(self, business_infinity=None, logger=None):
        self.business_infinity = business_infinity
        self.logger = logger

    async def linkedin_auth_endpoint(self, req: func.HttpRequest) -> func.HttpResponse:
        try:
            from linkedin_auth import get_linkedin_login_url
            result = get_linkedin_login_url(req)
            return func.HttpResponse(
                json.dumps(result),
                mimetype="application/json",
                status_code=result.get("status", 200)
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error initiating LinkedIn auth: {e}")
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )
