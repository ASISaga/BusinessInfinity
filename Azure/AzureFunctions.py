from azure.functions import HttpRequest, HttpResponse
from LinkedInAuth import LinkedInAuth
import json
import os

class AzureFunctionsHandler:
    def __init__(self):
        # Initialize resources or shared variables

        # Create an instance of LinkedInAuth
        linkedin_client_id = os.getenv("LINKEDIN_CLIENT_ID")
        linkedin_client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")

        self.linkedin_auth = LinkedInAuth(linkedin_client_id, linkedin_client_secret)

        # Map function names to actual function references
        self.functions = {
            "generateSignInUrl": self.linkedin_auth.generateSignInUrl,
            "handleOAuthCallback": self.linkedin_auth.handleOAuthCallback
        }

        pass

    def httpTrigger(self, req: HttpRequest) -> HttpResponse:
        name = req.params.get("name")

        # Call the function dynamically if it exists
        if name in self.functions:
            result = self.functions[name](req)
            if isinstance(result, str):
                return HttpResponse(json.dumps({"loginUrl": result}), status_code=200, headers={"Content-Type": "application/json"})
            return result
        else:
            return HttpResponse(
                f"No function found with the name '{name}'.",
                status_code=404
            )
        return HttpResponse(f"Hello, {name}!")


# Instantiate the class
handler = AzureFunctionsHandler()

# Specify the class member method as the main Azure Function
def main(req: HttpRequest) -> HttpResponse:
    return handler.httpTrigger(req)