"""
Generic Azure Functions Runtime

Provides a generic runtime for Azure Functions that can be used by any
application built on AgentOperatingSystem.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

try:
    import azure.functions as func
    AZURE_FUNCTIONS_AVAILABLE = True
except ImportError:
    AZURE_FUNCTIONS_AVAILABLE = False
    func = None

from .config_loader import RuntimeConfig
from .routes_registry import RouteRegistry, Route, HttpMethod, AuthLevel


class AzureFunctionsRuntime:
    """
    Generic Azure Functions runtime for AgentOperatingSystem applications.
    
    This runtime provides:
    - Automatic route registration from RouteRegistry
    - Application lifecycle management
    - Health check endpoints
    - Service bus integration
    - Observability and monitoring
    
    Any application can use this runtime by providing:
    - RuntimeConfig with application-specific settings
    - RouteRegistry with application routes
    - Optional initialization and shutdown hooks
    """
    
    def __init__(
        self,
        config: RuntimeConfig,
        route_registry: Optional[RouteRegistry] = None,
        app_initializer: Optional[Callable[[], Any]] = None,
        app_shutdown: Optional[Callable[[], Any]] = None
    ):
        """
        Initialize the Azure Functions runtime.
        
        Args:
            config: Runtime configuration
            route_registry: Optional pre-configured route registry
            app_initializer: Optional async function to initialize the application
            app_shutdown: Optional async function to shutdown the application
        """
        self.config = config
        self.route_registry = route_registry or RouteRegistry()
        self.app_initializer = app_initializer
        self.app_shutdown = app_shutdown
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, config.log_level.upper(), logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Application state
        self.app_instance: Optional[Any] = None
        self.initialized = False
        
        # Azure Functions app (created lazily)
        self._func_app: Optional[Any] = None
        
        self.logger.info(f"Initialized {config.app_name} runtime v{config.app_version}")
    
    def get_func_app(self) -> Any:
        """
        Get or create the Azure Functions app instance.
        
        Returns:
            Azure Functions FunctionApp instance
        """
        if self._func_app is None:
            if not AZURE_FUNCTIONS_AVAILABLE:
                raise RuntimeError("azure-functions package is not installed")
            
            # Map config auth level to Azure Functions auth level
            auth_level_map = {
                "ANONYMOUS": func.AuthLevel.ANONYMOUS,
                "FUNCTION": func.AuthLevel.FUNCTION,
                "ADMIN": func.AuthLevel.ADMIN,
            }
            auth_level = auth_level_map.get(self.config.auth_level, func.AuthLevel.FUNCTION)
            
            self._func_app = func.FunctionApp(http_auth_level=auth_level)
            self.logger.info("Created Azure Functions app instance")
        
        return self._func_app
    
    async def initialize_application(self) -> Any:
        """
        Initialize the application.
        
        Returns:
            The initialized application instance
        """
        if self.initialized:
            return self.app_instance
        
        try:
            self.logger.info(f"Initializing {self.config.app_name}...")
            
            if self.app_initializer:
                self.app_instance = await self.app_initializer()
            
            self.initialized = True
            self.logger.info(f"{self.config.app_name} initialized successfully")
            return self.app_instance
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.config.app_name}: {e}")
            raise
    
    async def shutdown_application(self):
        """Shutdown the application."""
        if not self.initialized:
            return
        
        try:
            self.logger.info(f"Shutting down {self.config.app_name}...")
            
            if self.app_shutdown:
                await self.app_shutdown()
            
            self.initialized = False
            self.app_instance = None
            self.logger.info(f"{self.config.app_name} shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def register_default_routes(self):
        """Register default routes (health, status)."""
        
        # Health check route
        async def health_check(req) -> func.HttpResponse:
            try:
                health_status = {
                    "service": self.config.app_name,
                    "version": self.config.app_version,
                    "status": "healthy" if self.initialized else "initializing",
                    "timestamp": datetime.utcnow().isoformat(),
                }
                
                status_code = 200 if self.initialized else 503
                return func.HttpResponse(
                    body=str(health_status),
                    status_code=status_code,
                    headers={"Content-Type": "application/json"}
                )
            except Exception as e:
                return func.HttpResponse(
                    body=str({"status": "error", "error": str(e)}),
                    status_code=500,
                    headers={"Content-Type": "application/json"}
                )
        
        self.route_registry.register(
            path="health",
            handler=health_check,
            methods=[HttpMethod.GET],
            auth_level=AuthLevel.ANONYMOUS,
            description="Health check endpoint"
        )
    
    def register_routes_to_azure_functions(self):
        """
        Register all routes from the registry to Azure Functions.
        
        This method converts framework-agnostic routes to Azure Functions routes.
        """
        func_app = self.get_func_app()
        
        for route in self.route_registry.get_all_routes():
            # Convert HttpMethod enum to strings
            methods = [m.value for m in route.methods]
            
            # Convert AuthLevel enum to Azure Functions AuthLevel
            auth_level_map = {
                AuthLevel.ANONYMOUS: func.AuthLevel.ANONYMOUS,
                AuthLevel.FUNCTION: func.AuthLevel.FUNCTION,
                AuthLevel.ADMIN: func.AuthLevel.ADMIN,
            }
            auth_level = auth_level_map.get(route.auth_level, func.AuthLevel.FUNCTION)
            
            # Create Azure Functions route decorator
            # Note: We need to use a factory function to capture the handler correctly
            def create_handler(handler):
                async def azure_handler(req: func.HttpRequest) -> func.HttpResponse:
                    return await handler(req)
                return azure_handler
            
            # Register with Azure Functions
            func_app.route(
                route=route.path,
                auth_level=auth_level,
                methods=methods
            )(create_handler(route.handler))
            
            self.logger.info(f"Registered Azure Functions route: {route}")
    
    def create_startup_function(self):
        """
        Create a startup timer function that initializes the application.
        
        This runs once when the Azure Functions host starts.
        """
        func_app = self.get_func_app()
        
        @func_app.function_name("startup")
        @func_app.timer_trigger(schedule="0 0 0 1 1 *", arg_name="timer", run_on_startup=True)
        async def startup_function(timer: func.TimerRequest) -> None:
            """Initialize application on startup"""
            await self.initialize_application()


def create_runtime(
    config: RuntimeConfig,
    route_registry: Optional[RouteRegistry] = None,
    app_initializer: Optional[Callable[[], Any]] = None,
    app_shutdown: Optional[Callable[[], Any]] = None,
    register_default_routes: bool = True
) -> AzureFunctionsRuntime:
    """
    Factory function to create and configure an Azure Functions runtime.
    
    Args:
        config: Runtime configuration
        route_registry: Optional pre-configured route registry
        app_initializer: Optional async function to initialize the application
        app_shutdown: Optional async function to shutdown the application
        register_default_routes: Whether to register default routes (health, etc.)
        
    Returns:
        Configured AzureFunctionsRuntime instance
    """
    runtime = AzureFunctionsRuntime(
        config=config,
        route_registry=route_registry,
        app_initializer=app_initializer,
        app_shutdown=app_shutdown
    )
    
    if register_default_routes:
        runtime.register_default_routes()
    
    return runtime
