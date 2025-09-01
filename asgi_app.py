import azure.functions as func

# This will handle the FastAPI ASGI app if FastAPI is available
try:
    from app.app import app as fastapi_app
    asgi_app = func.AsgiFunctionApp(app=fastapi_app, http_auth_level=func.AuthLevel.ANONYMOUS)
except ImportError:
    # If FastAPI is not available, create a minimal placeholder
    from fastapi import FastAPI
    placeholder_app = FastAPI()
    
    @placeholder_app.get("/")
    def read_root():
        return {"message": "FastAPI dependencies not available"}
    
    asgi_app = func.AsgiFunctionApp(app=placeholder_app, http_auth_level=func.AuthLevel.ANONYMOUS)