import logging
import azure.functions as func

# Import trigger registration functions
from triggers.http_routes import register_http_routes
from triggers.queue_triggers import register_queue_triggers  
from triggers.service_bus_triggers import register_service_bus_triggers

# Create the main function app instance  
app = func.FunctionApp()

# Register all triggers from the specialized modules
register_http_routes(app)
register_queue_triggers(app)
register_service_bus_triggers(app)