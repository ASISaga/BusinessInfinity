# In the Azure Function, create an endpoint to provide the LinkedIn login URL
import requests

class LinkedInAuth:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id  # string The API Key value generated when you registered your application.
        self.client_secret = client_secret

        self.redirect_uri = "https://YOUR_STATIC_WEB_APP_NAME.azurestaticapps.net/api/linkedin-auth"  # url The URI your users are sent back to after authorization.

        self.oauth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.access_token_url = "https://www.linkedin.com/oauth/v2/accessToken"

        self.response_type = "code"  # string The value of this field should always be: code
        self.scope = "r_liteprofile"  # string URL-encoded, space-delimited list of member permissions your application is requesting on behalf of the user.
        self.grant_type = "authorization_code"

    def generateSignInUrl(self) -> str:
        # Step 1: Generate LinkedIn login URL
        login_url = (
            self.oauth_url +
            "?response_type=" + self.response_type +
            "&client_id=" + self.client_id +
            "&redirect_uri=" + self.redirect_uri +
            "&scope=" + self.scope
        )
        return login_url
    
    # Add URL for callback function in LinkedIn redirect URL settings. https://<your-static-web-app>.azurestaticapps.net/api/linkedin-auth
    # LinkedIn redirects the user to callback endpoint URL with an authorization code
    # Exchange this code for an access token

    def handleOAuthCallback(self, req) -> dict:
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
            access_token_response = self.getAccessToken(code)
            
            return {
                "status": 200,
                "body": access_token_response
            }

        else:
            if access_token_response.status_code == 401:
                # Extract the error message from the response (if available)
                error_message = access_token_response.json().get("error", "Unknown error")

                # Handle specific 401 errors
                if error_message == "Redirect_uri doesn’t match":
                    return "Error: Redirect URI passed in the request does not match the one registered in the developer application. Please ensure the redirect URI matches exactly."
                
                elif error_message == "Client_id doesn’t match":
                    return "Error: Client ID in the request does not match the one registered in the developer application. Please verify the Client ID used."

                elif error_message == "Invalid scope":
                    return "Error: Permissions (scope) passed in the request are invalid. Please ensure the permissions are correctly assigned in the developer application."

                else:
                    return f"Error: {error_message} (Additional debugging needed)."
        
            error = req.params.get("error")
            if error:
                if error == "user_cancelled_login":
                    return {
                        "status": 400,
                        "body": "The member declined to log in to their LinkedIn account."
                    }
                elif error == "user_cancelled_authorize":
                    return {
                        "status": 400,
                        "body": "The member refused to authorize the permissions request from your application."
                    }
                else:
                    return {
                    "status": 400,
                    "body": f"Error: {error}"
                }

            return {
                "status": 400,
                "body": "Unexpected response from LinkedIn."
            }
        
    def getAccessToken(self, code: str) -> dict:
        """
        Exchange authorization code for access token.
        Args:
            code: The authorization code received from LinkedIn.
        Returns:
            dict: A dictionary containing the access token.
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}  # Set the content type for the request

        data = {
            "grant_type": self.grant_type,
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri
        }

        # Send a POST request to LinkedIn to fetch the access token
        response = requests.post(self.access_token_url, data=data, headers=headers)
        
        if response.status_code == 401:
            # Extract the error message from the response
            error_message = response.json().get("error", "Unknown error")

            # Handle specific 401 errors
            if "authorization code not found" in error_message:
                return "Error: The authorization code sent is invalid or not found. Check whether the sent authorization code is valid."
            else:
                return f"Error: {error_message} (Additional debugging needed)."

        elif response.status_code == 400:
            # Extract the error message from the response
            error_message = response.json().get("error_description", "Unknown error")

            # Handle specific 400 errors
            if "redirect_uri" in error_message:
                return "Error: Redirect URI is missing in the request. It is mandatory. Pass the 'redirect_uri' to route the user back to the correct landing page."
            elif "code" in error_message:
                return "Error: Authorization code is missing in the request. It is mandatory. Pass the authorization code received as part of the authorization API call."
            elif "grant_type" in error_message:
                return "Error: Grant type is missing in the request. Add 'grant_type' as 'authorization_code' in the request."
            elif "client_id" in error_message:
                return "Error: Client ID is missing in the request. Pass the client ID of the app in the request."
            elif "client_secret" in error_message:
                return "Error: Client Secret is missing in the request. Pass the client secret of the app in the request."
            elif "appid/redirect uri/code verifier does not match authorization code" in error_message:
                return "Error: The redirect URI or authorization code is invalid, expired, or mismatched. Ensure you pass the correct redirect URI and a valid, non-expired authorization code."
            else:
                return f"Error: {error_message} (Additional debugging needed)."
        
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return {"error": "Invalid JSON response from LinkedIn."}