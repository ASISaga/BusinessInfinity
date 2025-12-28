"""
BusinessInfinity Azure Functions Application

This is the main entry point for the BusinessInfinity Azure Functions application.
It uses the generic AgentOperatingSystem runtime for all infrastructure.

Architecture:
    ┌─────────────────────────────────────────────┐
    │         BusinessInfinity Application        │
    │  • Business-specific configuration          │
    │  • Business routes and handlers             │
    │  • Business agents and workflows            │
    └─────────────────────────────────────────────┘
                         ▼
    ┌─────────────────────────────────────────────┐
    │         Generic Runtime Layer               │
    │  • AzureFunctionsRuntime                    │
    │  • RouteRegistry                            │
    │  • RuntimeConfig                            │
    └─────────────────────────────────────────────┘
                         ▼
    ┌─────────────────────────────────────────────┐
    │       AgentOperatingSystem (AOS)            │
    │  • Storage, Messaging, ML Pipeline          │
    │  • Observability, Reliability, Security     │
    └─────────────────────────────────────────────┘
"""

import logging
from typing import Optional

# Import generic runtime
from runtime import RouteRegistry, create_runtime

# Import BusinessInfinity-specific modules
from src.app import BusinessInfinity, create_business_infinity, set_business_infinity
from src.config import BusinessInfinityConfig, load_bi_config
from src.handlers import register_routes

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global application instance
bi_app: Optional[BusinessInfinity] = None


async def initialize_application() -> BusinessInfinity:
    """Initialize the BusinessInfinity application."""
    global bi_app

    try:
        logger.info("Initializing BusinessInfinity application...")

        # Load configuration
        config = load_bi_config()

        # Create and initialize BusinessInfinity
        bi_app = await create_business_infinity(config)

        # Set global instance for handlers
        set_business_infinity(bi_app)

        logger.info("BusinessInfinity initialized successfully")
        return bi_app

    except Exception as e:
        logger.error(f"Failed to initialize BusinessInfinity: {e}")
        raise


async def shutdown_application() -> None:
    """Shutdown the BusinessInfinity application."""
    global bi_app

    if bi_app:
        await bi_app.shutdown()
        bi_app = None


# Load configuration
config = load_bi_config()
runtime_config = config.to_runtime_config()

# Create route registry
route_registry = RouteRegistry()

# Create runtime
runtime = create_runtime(
    config=runtime_config,
    route_registry=route_registry,
    app_initializer=initialize_application,
    app_shutdown=shutdown_application,
    register_default_routes=False,  # We register our own health endpoint
)

# Register BusinessInfinity routes
# The handlers use the global instance via get_business_infinity()
register_routes(route_registry)

# Get Azure Functions app
app = runtime.get_func_app()

# Register routes to Azure Functions
runtime.register_routes_to_azure_functions()

# Create startup function
runtime.create_startup_function()

logger.info("BusinessInfinity Azure Functions app configured")
