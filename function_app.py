"""
Business Infinity - Azure Functions App
Consolidated and refactored to use the unified core system
"""

import logging
import azure.functions as func

# Import consolidated core system
from core.azure_functions import register_consolidated_functions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Azure Functions app
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Register all consolidated functions
try:
    register_consolidated_functions(app)
    logger.info("Successfully registered all consolidated Azure Functions")
except Exception as e:
    logger.error(f"Failed to register consolidated functions: {e}")
    # Fallback to basic functionality
    
    @app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
    async def health_fallback(req: func.HttpRequest) -> func.HttpResponse:
        """Fallback health check if core registration fails"""
        return func.HttpResponse(
            '{"status": "fallback", "message": "Core system registration failed"}',
            mimetype="application/json",
            status_code=200
        )

# Export the app for Azure Functions runtime
if __name__ == "__main__":
    logger.info("Azure Functions app initialized with consolidated core system")