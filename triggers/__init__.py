"""
Triggers Feature
Consolidated into core system - this module provides backward compatibility.
Use core.triggers_manager instead.
"""

# Backward compatibility - redirect to core system
try:
    from core.triggers import triggers_manager, UnifiedTriggersManager
    
    # Create aliases for backward compatibility
    TriggersManager = UnifiedTriggersManager
    manager = triggers_manager
    
    # Legacy function imports for Azure Functions compatibility
    def register_http_routes(app):
        """Backward compatibility wrapper - HTTP routes now handled by core system"""
        try:
            from .http_routes import register_http_routes as legacy_register_http_routes
            return legacy_register_http_routes(app)
        except ImportError:
            pass
    
    def register_service_bus_triggers(app):
        """Backward compatibility wrapper"""
        try:
            from .service_bus_triggers import register_service_bus_triggers as legacy_register_service_bus_triggers
            return legacy_register_service_bus_triggers(app)
        except ImportError:
            pass
    
    def register_queue_triggers(app):
        """Backward compatibility wrapper"""
        try:
            from .queue_triggers import register_queue_triggers as legacy_register_queue_triggers
            return legacy_register_queue_triggers(app)
        except ImportError:
            pass
    
    __all__ = [
        'triggers_manager', 'UnifiedTriggersManager', 'TriggersManager', 'manager',
        'register_http_routes', 'register_service_bus_triggers', 'register_queue_triggers'
    ]
except ImportError:
    # If core system not available, fallback to legacy imports
    try:
        from .http_routes import register_http_routes
        from .queue_triggers import register_queue_triggers
        from .service_bus_triggers import register_service_bus_triggers
    except ImportError:
        def register_http_routes(app):
            pass
        def register_service_bus_triggers(app):
            pass
        def register_queue_triggers(app):
            pass
    
    class TriggersManager:
        def __init__(self):
            pass
    
    class UnifiedTriggersManager:
        def __init__(self):
            pass
    
    manager = TriggersManager()
    triggers_manager = manager
    
    __all__ = [
        'triggers_manager', 'UnifiedTriggersManager', 'TriggersManager', 'manager',
        'register_http_routes', 'register_service_bus_triggers', 'register_queue_triggers'
    ]