# Add URL for callback function in LinkedIn redirect URL settings. https://<your-static-web-app>.azurestaticapps.net/api/linkedin-auth
# LinkedIn redirects the user to callback endpoint URL with an authorization code
# Exchange this code for an access token

import requests
import os

token_url = "https://www.linkedin.com/oauth/v2/accessToken"
grant_type = "authorization_code"
client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
client_id = os.getenv("LINKEDIN_CLIENT_ID")
redirect_uri = "https://<your-static-web-app>.azurestaticapps.net/api/linkedin-auth"

def main(req):
    """
    Main function to handle LinkedIn OAuth callback.

    Args:
        req: The request object containing query parameters.

    Returns:
        dict: A dictionary with status code and response body.
    """
    # Fetch authorization code from the query parameters
    code = req.params.get("code")

    if code:
        # Exchange code for access token
        payload = {
            "grant_type": grant_type,
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret
        }

        # Send a POST request to LinkedIn to fetch the access token
        response = requests.post(token_url, data=payload)
        try:
            return {
                "status": 200,
                "body": response.json()  # Return token or additional data
            }
        except requests.exceptions.JSONDecodeError:
            return {
                "status": 500,
                "body": "Invalid JSON response from LinkedIn."
            }
    else:
        return {
            "status": 400,
            "body": "Authorization code missing."
        }
