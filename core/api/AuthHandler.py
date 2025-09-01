# Constant for unauthorized message
UNAUTHORIZED_MSG = "Unauthorized"

# auth.py – Login, Refresh & JWT Validation

import os, json, requests
import azure.functions as func
import jwt
from msal import ConfidentialClientApplication
from jwt.algorithms import RSAAlgorithm

class AuthHandler:
    def __init__(self):
        self.TENANT = os.getenv("B2C_TENANT")
        self.POLICY = os.getenv("B2C_POLICY")
        self.CLIENTID = os.getenv("B2CCLIENT_ID")
        from .EnvManager import EnvManager
        env = EnvManager()
        self.CLIENTSECRET = env.get_required("B2CCLIENT_SECRET")
        self.SCOPE = [os.getenv("B2CAPISCOPE")]
        self.ISSUER = os.getenv("B2C_ISSUER")
        self.AUTHORITY = f"https://{self.TENANT}/{self.POLICY}"
        self._jwks = None

    def login(self, req: func.HttpRequest) -> func.HttpResponse:
        creds = req.get_json()
        username, password = creds.get("username"), creds.get("password")
        if not username or not password:
            return func.HttpResponse("username & password required", status_code=400)

        app = ConfidentialClientApplication(
            self.CLIENTID, authority=self.AUTHORITY, client_credential=self.CLIENTSECRET
        )
        result = app.acquire_token_by_username_password(
            username=username, password=password, scopes=self.SCOPE
        )
        if "access_token" in result:
            return func.HttpResponse(json.dumps({
                "accesstoken": result["access_token"],
                "refreshtoken": result.get("refresh_token"),
                "expiresin": result["expires_in"]
            }), mimetype="application/json")
        return func.HttpResponse(json.dumps(result), status_code=400)

    def refresh(self, req: func.HttpRequest) -> func.HttpResponse:
        body = req.get_json()
        rtoken = body.get("refresh_token")
        if not rtoken:
            return func.HttpResponse("refreshtoken required", status_code=400)

        app = ConfidentialClientApplication(
            self.CLIENTID, authority=self.AUTHORITY, client_credential=self.CLIENTSECRET
        )
        result = app.acquire_token_by_refresh_token(rtoken, scopes=self.SCOPE)
        if "access_token" in result:
            return func.HttpResponse(json.dumps({
                "accesstoken": result["access_token"],
                "refreshtoken": result.get("refresh_token"),
                "expiresin": result["expires_in"]
            }), mimetype="application/json")
        return func.HttpResponse(json.dumps(result), status_code=400)

    def load_jwks(self):
        if not self._jwks:
            url = f"https://{self.TENANT}/discovery/v2.0/keys?p={self.POLICY}"
            self._jwks = requests.get(url).json()
        return self._jwks

    def validate_jwt(self, token: str):
        try:
            header = jwt.get_unverified_header(token)
            jwks = self.load_jwks()["keys"]
            key = next(k for k in jwks if k["kid"] == header["kid"])
            pub = RSAAlgorithm.from_jwk(json.dumps(key))
            claims = jwt.decode(
                token, pub,
                algorithms=[header["alg"]],
                audience=self.CLIENTID,
                issuer=self.ISSUER
            )
            return claims
        except Exception:
            return None