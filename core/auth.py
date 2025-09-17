"""
Unified Authentication System
Consolidates functionality from authentication/ directory
"""

import os
import json
import requests
import jwt
from typing import Dict, Any, Optional
from msal import ConfidentialClientApplication
from jwt.algorithms import RSAAlgorithm

try:
    import azure.functions as func
    AZURE_FUNCTIONS_AVAILABLE = True
except ImportError:
    AZURE_FUNCTIONS_AVAILABLE = False


class UnifiedAuthHandler:
    """
    Unified authentication handler that consolidates:
    - Azure B2C authentication
    - LinkedIn OAuth integration
    - JWT validation and token management
    - Multi-provider authentication support
    """
    
    # Constant for unauthorized message
    UNAUTHORIZED_MSG = "Unauthorized"
    
    def __init__(self):
        # Azure B2C Configuration
        self.TENANT = os.getenv("B2C_TENANT")
        self.POLICY = os.getenv("B2C_POLICY") 
        self.CLIENTID = os.getenv("B2CCLIENT_ID")
        self.CLIENTSECRET = os.getenv("B2CCLIENT_SECRET")
        self.SCOPE = [os.getenv("B2CAPISCOPE")] if os.getenv("B2CAPISCOPE") else []
        self.ISSUER = os.getenv("B2C_ISSUER")
        self.AUTHORITY = f"https://{self.TENANT}/{self.POLICY}" if self.TENANT and self.POLICY else None
        
        # LinkedIn OAuth Configuration
        self.LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
        self.LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI")
        
        # JWT Configuration
        self._jwks = None
        
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user with username/password via Azure B2C"""
        if not username or not password:
            return {"error": "username & password required", "status": 400}
        
        if not self.AUTHORITY or not self.CLIENTID or not self.CLIENTSECRET:
            return {"error": "B2C configuration missing", "status": 500}
        
        try:
            app = ConfidentialClientApplication(
                self.CLIENTID, 
                authority=self.AUTHORITY, 
                client_credential=self.CLIENTSECRET
            )
            result = app.acquire_token_by_username_password(
                username=username, 
                password=password, 
                scopes=self.SCOPE
            )
            
            if "access_token" in result:
                return {
                    "accesstoken": result["access_token"],
                    "refreshtoken": result.get("refresh_token"),
                    "expiresin": result["expires_in"],
                    "status": 200
                }
            return {"error": result, "status": 400}
            
        except Exception as e:
            return {"error": f"Authentication failed: {str(e)}", "status": 500}
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        if not refresh_token:
            return {"error": "refreshtoken required", "status": 400}
        
        if not self.AUTHORITY or not self.CLIENTID or not self.CLIENTSECRET:
            return {"error": "B2C configuration missing", "status": 500}
        
        try:
            app = ConfidentialClientApplication(
                self.CLIENTID, 
                authority=self.AUTHORITY, 
                client_credential=self.CLIENTSECRET
            )
            result = app.acquire_token_by_refresh_token(refresh_token, scopes=self.SCOPE)
            
            if "access_token" in result:
                return {
                    "accesstoken": result["access_token"],
                    "refreshtoken": result.get("refresh_token"),
                    "expiresin": result["expires_in"],
                    "status": 200
                }
            return {"error": result, "status": 400}
            
        except Exception as e:
            return {"error": f"Token refresh failed: {str(e)}", "status": 500}
    
    def load_jwks(self) -> Dict[str, Any]:
        """Load JSON Web Key Set for JWT validation"""
        if not self._jwks and self.TENANT and self.POLICY:
            try:
                url = f"https://{self.TENANT}/discovery/v2.0/keys?p={self.POLICY}"
                response = requests.get(url)
                response.raise_for_status()
                self._jwks = response.json()
            except Exception as e:
                print(f"Warning: Failed to load JWKS: {e}")
                return {"keys": []}
        return self._jwks or {"keys": []}
    
    def validate_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return claims"""
        try:
            header = jwt.get_unverified_header(token)
            jwks = self.load_jwks()["keys"]
            
            # Find the key that matches the token's kid
            key = next((k for k in jwks if k["kid"] == header["kid"]), None)
            if not key:
                return None
            
            pub = RSAAlgorithm.from_jwk(json.dumps(key))
            claims = jwt.decode(
                token, 
                pub,
                algorithms=[header["alg"]],
                audience=self.CLIENTID,
                issuer=self.ISSUER
            )
            return claims
            
        except Exception as e:
            print(f"JWT validation failed: {e}")
            return None
    
    def linkedin_auth_url(self, state: str = None) -> str:
        """Generate LinkedIn OAuth authorization URL"""
        if not self.LINKEDIN_CLIENT_ID or not self.LINKEDIN_REDIRECT_URI:
            raise ValueError("LinkedIn configuration missing")
        
        base_url = "https://www.linkedin.com/oauth/v2/authorization"
        params = {
            "response_type": "code",
            "client_id": self.LINKEDIN_CLIENT_ID,
            "redirect_uri": self.LINKEDIN_REDIRECT_URI,
            "scope": "openid profile email"
        }
        
        if state:
            params["state"] = state
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    def linkedin_exchange_code(self, code: str) -> Dict[str, Any]:
        """Exchange LinkedIn authorization code for access token"""
        if not self.LINKEDIN_CLIENT_ID or not self.LINKEDIN_CLIENT_SECRET:
            return {"error": "LinkedIn configuration missing", "status": 500}
        
        try:
            token_url = "https://www.linkedin.com/oauth/v2/accessToken"
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self.LINKEDIN_CLIENT_ID,
                "client_secret": self.LINKEDIN_CLIENT_SECRET,
                "redirect_uri": self.LINKEDIN_REDIRECT_URI
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Get user profile
            profile_url = "https://api.linkedin.com/v2/userinfo"
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            profile_response = requests.get(profile_url, headers=headers)
            profile_response.raise_for_status()
            
            profile_data = profile_response.json()
            
            return {
                "access_token": token_data["access_token"],
                "profile": profile_data,
                "email": profile_data.get("email"),
                "status": 200
            }
            
        except Exception as e:
            return {"error": f"LinkedIn authentication failed: {str(e)}", "status": 500}
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate authentication configuration"""
        issues = []
        
        # Check B2C configuration
        if not self.TENANT:
            issues.append("Missing B2C_TENANT")
        if not self.POLICY:
            issues.append("Missing B2C_POLICY")
        if not self.CLIENTID:
            issues.append("Missing B2CCLIENT_ID")
        if not self.CLIENTSECRET:
            issues.append("Missing B2CCLIENT_SECRET")
        
        # Check LinkedIn configuration (optional)
        linkedin_configured = bool(
            self.LINKEDIN_CLIENT_ID and 
            self.LINKEDIN_CLIENT_SECRET and 
            self.LINKEDIN_REDIRECT_URI
        )
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "b2c_configured": bool(self.TENANT and self.POLICY and self.CLIENTID and self.CLIENTSECRET),
            "linkedin_configured": linkedin_configured,
            "jwks_loaded": bool(self._jwks)
        }
    
    # Azure Functions compatibility methods
    def azure_login(self, req) -> Any:
        """Azure Functions compatibility wrapper for login"""
        if not AZURE_FUNCTIONS_AVAILABLE:
            raise ImportError("Azure Functions not available")
        
        try:
            creds = req.get_json()
            username = creds.get("username")
            password = creds.get("password")
            
            result = self.login(username, password)
            
            if result.get("status") == 200:
                return func.HttpResponse(
                    json.dumps({
                        "accesstoken": result["accesstoken"],
                        "refreshtoken": result["refreshtoken"],
                        "expiresin": result["expiresin"]
                    }),
                    mimetype="application/json"
                )
            else:
                return func.HttpResponse(
                    json.dumps({"error": result.get("error")}),
                    status_code=result.get("status", 400)
                )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                status_code=500
            )
    
    def azure_refresh(self, req) -> Any:
        """Azure Functions compatibility wrapper for token refresh"""
        if not AZURE_FUNCTIONS_AVAILABLE:
            raise ImportError("Azure Functions not available")
        
        try:
            body = req.get_json()
            refresh_token = body.get("refresh_token")
            
            result = self.refresh_token(refresh_token)
            
            if result.get("status") == 200:
                return func.HttpResponse(
                    json.dumps({
                        "accesstoken": result["accesstoken"],
                        "refreshtoken": result["refreshtoken"],
                        "expiresin": result["expiresin"]
                    }),
                    mimetype="application/json"
                )
            else:
                return func.HttpResponse(
                    json.dumps({"error": result.get("error")}),
                    status_code=result.get("status", 400)
                )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                status_code=500
            )


# Create singleton instance
auth_handler = UnifiedAuthHandler()

# Export for backward compatibility
__all__ = ['auth_handler', 'UnifiedAuthHandler']