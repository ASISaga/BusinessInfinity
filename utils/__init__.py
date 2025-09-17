"""
Utilities Feature
Consolidated into core system - this module provides backward compatibility.
Use core.utils_manager instead.
"""

# Backward compatibility - redirect to core system
try:
    from core.utils import utils_manager, UnifiedUtilsManager, validate_request, get_ui_schema, GovernanceError
    
    # Create aliases for backward compatibility
    UtilsManager = UnifiedUtilsManager
    manager = utils_manager
    
    # Legacy function imports
    def governance_validate_request(context, payload):
        """Backward compatibility wrapper"""
        return validate_request(context, payload)
    
    __all__ = [
        'utils_manager', 'UnifiedUtilsManager', 'UtilsManager', 'manager',
        'validate_request', 'get_ui_schema', 'governance_validate_request', 'GovernanceError'
    ]
except ImportError:
    # If core system not available, fallback to legacy imports
    try:
        from .governance import validate_request, GovernanceError
    except ImportError:
        class GovernanceError(Exception):
            pass
        def validate_request(context, payload):
            pass
    
    def get_ui_schema(role=None, scope="local"):
        return {"error": "UI schema not available"}
    
    def governance_validate_request(context, payload):
        return validate_request(context, payload)
    
    class UtilsManager:
        def __init__(self):
            pass
    
    class UnifiedUtilsManager:
        def __init__(self):
            pass
    
    manager = UtilsManager()
    utils_manager = manager
    
    __all__ = [
        'utils_manager', 'UnifiedUtilsManager', 'UtilsManager', 'manager',
        'validate_request', 'get_ui_schema', 'governance_validate_request', 'GovernanceError'
    ]