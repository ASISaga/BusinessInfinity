# In the Azure Function, create an endpoint to provide the LinkedIn login URL

from azure.functions import HttpRequest, HttpResponse
import json
import os

linkedin_oauth_url = "https://www.linkedin.com/oauth/v2/authorization"
response_type = "code"	# string The value of this field should always be: code
client_id = os.getenv("LINKEDIN_CLIENT_ID") #	string	The API Key value generated when you registered your application.
redirect_uri = "https://YOUR_STATIC_WEB_APP_NAME.azurestaticapps.net/api/linkedin-auth" #	url	The URI your users are sent back to after authorization.
scope =	"r_liteprofile" # string	URL-encoded, space-delimited list of member permissions your application is requesting on behalf of the user.

def main(req: HttpRequest) -> HttpResponse:
    # Step 1: Generate LinkedIn login URL
    login_url = generateSignInUrl()
    return HttpResponse(json.dumps({"loginUrl": login_url}), status_code=200, headers={"Content-Type": "application/json"})

def generateSignInUrl():

    login_url = (
        linkedin_oauth_url +
        "?response_type=" + response_type +
        "&client_id=" + client_id + 
        "&redirect_uri=" + redirect_uri +
        "&scope=" + scope
    )
    return login_url
