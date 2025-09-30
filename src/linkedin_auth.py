"""
LinkedIn OAuth endpoints for BusinessInfinity
Delegates all logic to the unified handler in AOS (RealmOfAgents/AgentOperatingSystem/aos_auth.py)
"""
from RealmOfAgents.AgentOperatingSystem.aos_auth import auth_handler

# Azure Functions/FastAPI compatible endpoint for LinkedIn login URL
def get_linkedin_login_url(req):
    """Return the LinkedIn OAuth login URL."""
    state = req.params.get("state") if hasattr(req, 'params') else None
    url = auth_handler.linkedin_auth_url(state)
    return {
        "status": 200,
        "login_url": url
    }

# Azure Functions/FastAPI compatible endpoint for LinkedIn OAuth callback
def handle_linkedin_callback(req):
    """Handle LinkedIn OAuth callback and exchange code for access token/profile."""
    code = req.params.get("code") if hasattr(req, 'params') else None
    if code:
        result = auth_handler.linkedin_exchange_code(code)
        return result
    error = req.params.get("error") if hasattr(req, 'params') else None
    if error == "user_cancelled_login":
        return {"status": 400, "body": "The member declined to log in to their LinkedIn account."}
    elif error == "user_cancelled_authorize":
        return {"status": 400, "body": "The member refused to authorize the permissions request from your application."}
    else:
        return {"status": 400, "body": f"Error: {error}" if error else "Unexpected response from LinkedIn."}
