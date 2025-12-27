"""
Complete Example: Building an App with the Generic Runtime

This example shows how to build a complete application using all the
runtime features:
- Configuration
- Routes (HTTP endpoints)
- Service Bus messaging
- Storage
- Agent Framework

This is NOT BusinessInfinity - it's a generic example that could be
any application (CRM, ERP, custom business app, etc.)
"""

import asyncio
import logging
from datetime import datetime

# Import generic runtime
from runtime import (
    # Configuration
    RuntimeConfig,
    
    # HTTP routes
    RouteRegistry, HttpMethod, AuthLevel,
    
    # Service Bus
    ServiceBusRegistry,
    
    # Storage and Messaging
    create_storage_provider,
    create_messaging_provider,
    Message,
    
    # Azure Functions runtime
    create_runtime,
    create_servicebus_runtime,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========================================
# 1. Application Class
# ========================================

class MyApplication:
    """
    Example application built on the generic runtime.
    
    This could be a CRM, ERP, or any business application.
    """
    
    def __init__(self, config: RuntimeConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Create storage and messaging providers
        self.storage = create_storage_provider(
            config.custom_config.get('storage_type', 'memory')
        )
        self.messaging = create_messaging_provider(
            config.custom_config.get('messaging_type', 'memory')
        )
        
        # Application state
        self.users = {}
        self.orders = {}
    
    async def start(self):
        """Initialize the application."""
        self.logger.info(f"Starting {self.config.app_name}...")
        
        # Load data from storage
        users_data = await self.storage.get('users')
        if users_data:
            self.users = users_data
        
        # Subscribe to messaging topics
        await self.messaging.subscribe(
            topic='user_events',
            callback=self.handle_user_event
        )
        
        self.logger.info(f"{self.config.app_name} started successfully")
    
    async def handle_user_event(self, message: Message):
        """Handle user events from messaging system."""
        self.logger.info(f"Received user event: {message.type}")
        
        if message.type == 'user_created':
            user_data = message.body
            self.users[user_data['id']] = user_data
            await self.storage.set('users', self.users)
    
    async def shutdown(self):
        """Shutdown the application."""
        self.logger.info(f"Shutting down {self.config.app_name}...")
        
        # Save data to storage
        await self.storage.set('users', self.users)
        await self.storage.set('orders', self.orders)
        
        self.logger.info(f"{self.config.app_name} shutdown complete")


# ========================================
# 2. Configuration
# ========================================

# Create configuration
config = RuntimeConfig(
    app_name="MyApp",
    app_version="1.0.0",
    app_environment="development",
    azure_functions_enabled=True,
    auth_level="FUNCTION",
    aos_enabled=False,  # Using memory storage/messaging for this example
    storage_type="memory",
    messaging_type="memory",
    custom_config={
        "max_users": 1000,
        "enable_analytics": True,
    }
)


# ========================================
# 3. Application Lifecycle
# ========================================

# Global app instance
app = None


async def initialize_app():
    """Initialize the application."""
    global app
    app = MyApplication(config)
    await app.start()
    return app


async def shutdown_app():
    """Shutdown the application."""
    global app
    if app:
        await app.shutdown()


# ========================================
# 4. HTTP Routes
# ========================================

# Create route registry
route_registry = RouteRegistry()


# Health check
async def health_check(req):
    """Health check endpoint."""
    return {
        "service": config.app_name,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


route_registry.register(
    path="health",
    handler=health_check,
    methods=[HttpMethod.GET],
    auth_level=AuthLevel.ANONYMOUS,
    description="Health check endpoint",
    tags=["health"]
)


# List users
async def list_users(req):
    """List all users."""
    global app
    
    if not app:
        return {"error": "Application not initialized"}, 503
    
    return {
        "users": list(app.users.values()),
        "total": len(app.users)
    }


route_registry.register(
    path="api/users",
    handler=list_users,
    methods=[HttpMethod.GET],
    auth_level=AuthLevel.FUNCTION,
    description="List all users",
    tags=["users"]
)


# Create user
async def create_user(req):
    """Create a new user."""
    global app
    
    if not app:
        return {"error": "Application not initialized"}, 503
    
    try:
        # In a real app, would parse request body
        import json
        user_data = json.loads(req.get_body().decode('utf-8'))
        
        user_id = user_data.get('id')
        app.users[user_id] = user_data
        
        # Publish event
        await app.messaging.publish(
            Message(
                id=user_id,
                type='user_created',
                body=user_data,
                timestamp=datetime.utcnow()
            ),
            topic='user_events'
        )
        
        return {"status": "created", "user": user_data}
        
    except Exception as e:
        return {"error": str(e)}, 400


route_registry.register(
    path="api/users",
    handler=create_user,
    methods=[HttpMethod.POST],
    auth_level=AuthLevel.FUNCTION,
    description="Create a new user",
    tags=["users"]
)


# ========================================
# 5. Service Bus Message Handlers
# ========================================

# Create service bus registry
servicebus_registry = ServiceBusRegistry()


async def handle_order_event(message: dict):
    """Handle order events from service bus."""
    global app
    
    logger.info(f"Processing order event: {message.get('type')}")
    
    if message.get('type') == 'order_created':
        order_data = message.get('order', {})
        app.orders[order_data['id']] = order_data
        return True
    
    return False


servicebus_registry.register(
    message_type="order_event",
    handler=handle_order_event,
    description="Handle order events",
    tags=["orders"]
)


async def handle_user_event_sb(message: dict):
    """Handle user events from service bus."""
    logger.info(f"Processing user event from service bus: {message.get('type')}")
    return True


servicebus_registry.register(
    message_type="user_event",
    handler=handle_user_event_sb,
    description="Handle user events from service bus",
    tags=["users"]
)


# ========================================
# 6. Create Azure Functions Runtime
# ========================================

# Create the runtime
runtime = create_runtime(
    config=config,
    route_registry=route_registry,
    app_initializer=initialize_app,
    app_shutdown=shutdown_app,
    register_default_routes=False  # We registered health check manually
)

# Register routes to Azure Functions
runtime.register_routes_to_azure_functions()

# Create startup function
runtime.create_startup_function()

# Get Azure Functions app
app_func = runtime.get_func_app()


# ========================================
# 7. Service Bus Integration
# ========================================

# Create service bus runtime
servicebus = create_servicebus_runtime(
    message_registry=servicebus_registry,
    connection_string_env_var="MyAppServiceBusConnection"
)

# Register service bus handlers
# Note: Uncomment these when you have actual queues/topics
# servicebus.register_to_azure_functions(
#     func_app=app_func,
#     queue_name="orders-queue"
# )

# servicebus.register_to_azure_functions(
#     func_app=app_func,
#     topic_name="events-topic",
#     subscription_name="myapp-subscription"
# )


# ========================================
# 8. Summary
# ========================================

logger.info(f"""
===========================================
{config.app_name} v{config.app_version}
===========================================

Runtime Features Enabled:
- HTTP Routes: {len(route_registry.get_all_routes())} routes registered
- Service Bus: {len(servicebus_registry.get_all_handlers())} message handlers
- Storage: {config.storage_type}
- Messaging: {config.messaging_type}
- Environment: {config.app_environment}

Ready to deploy to Azure Functions!
===========================================
""")


# ========================================
# How to Use This Example:
# ========================================
"""
1. Save this as your function_app.py

2. Install dependencies:
   pip install azure-functions

3. Configure environment variables:
   - MyAppServiceBusConnection (if using service bus)
   - Any other app-specific settings

4. Deploy to Azure Functions:
   func azure functionapp publish <your-function-app-name>

5. Test endpoints:
   - GET /health - Health check
   - GET /api/users - List users
   - POST /api/users - Create user

This example demonstrates ALL runtime features:
- Configuration loading
- HTTP route registration
- Service bus message handling
- Storage abstraction
- Messaging pub/sub
- Application lifecycle
- Azure Functions integration

You can build ANY application this way:
- CRM (customers, contacts, deals)
- ERP (inventory, orders, suppliers)
- Custom business apps
- Etc.

The runtime handles all the infrastructure!
"""
