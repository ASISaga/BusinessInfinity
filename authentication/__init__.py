"""
Authentication Feature
Consolidated into core system - this module provides backward compatibility.
Use core.auth_handler instead.
"""

# Backward compatibility - redirect to core system
try:
    from core.auth import auth_handler, UnifiedAuthHandler
    
    # Create aliases for backward compatibility
    AuthHandler = UnifiedAuthHandler
    handler = auth_handler
    
    # For legacy imports
    UNAUTHORIZED_MSG = auth_handler.UNAUTHORIZED_MSG
    validate_jwt = auth_handler.validate_jwt
    
    __all__ = ['auth_handler', 'UnifiedAuthHandler', 'AuthHandler', 'handler', 'UNAUTHORIZED_MSG', 'validate_jwt']
except ImportError:
    # If core system not available, provide fallback
    UNAUTHORIZED_MSG = "Unauthorized"
    
    def validate_jwt(token):
        return None
    
    class AuthHandler:
        UNAUTHORIZED_MSG = UNAUTHORIZED_MSG
        def __init__(self):
            pass
    
    class UnifiedAuthHandler:
        UNAUTHORIZED_MSG = UNAUTHORIZED_MSG
        def __init__(self):
            pass
    
    handler = AuthHandler()
    auth_handler = handler
    
    __all__ = ['auth_handler', 'UnifiedAuthHandler', 'AuthHandler', 'handler', 'UNAUTHORIZED_MSG', 'validate_jwt']