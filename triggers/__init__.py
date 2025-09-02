"""
Azure Function Triggers Module

This module organizes Azure Function triggers by type:
- http_routes: HTTP route handlers for REST API endpoints
- queue_triggers: Azure Storage Queue triggers
- service_bus_triggers: Azure Service Bus triggers

To use these triggers, import the registration functions and call them with your FunctionApp instance:

    from triggers.http_routes import register_http_routes
    from triggers.queue_triggers import register_queue_triggers  
    from triggers.service_bus_triggers import register_service_bus_triggers
    
    app = func.FunctionApp()
    register_http_routes(app)
    register_queue_triggers(app)
    register_service_bus_triggers(app)
"""

# Make registration functions available at package level
from .http_routes import register_http_routes
from .queue_triggers import register_queue_triggers
from .service_bus_triggers import register_service_bus_triggers

__all__ = ['register_http_routes', 'register_queue_triggers', 'register_service_bus_triggers']