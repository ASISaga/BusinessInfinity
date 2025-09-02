"""
Azure Function Triggers Module

This module organizes Azure Function triggers by type:
- http_routes: HTTP route handlers for REST API endpoints
- queue_triggers: Azure Storage Queue triggers
- service_bus_triggers: Azure Service Bus triggers
"""

# Import all trigger functions to make them available when importing this module
from .http_routes import *
from .queue_triggers import *
from .service_bus_triggers import *