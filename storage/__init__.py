"""
Storage Feature
Consolidated into core system - this module provides backward compatibility.
Use core.storage_manager instead.
"""

# Backward compatibility - redirect to core system
try:
    from core.features.storage import storage_manager as core_storage_manager, UnifiedStorageManager
    
    # Create aliases for backward compatibility - ensure we use the core storage_manager
    storage_manager = core_storage_manager
    manager = core_storage_manager
    StorageManager = UnifiedStorageManager
    
    __all__ = ['storage_manager', 'UnifiedStorageManager', 'StorageManager', 'manager']
except ImportError:
    # If core system not available, provide fallback
    class StorageManager:
        def __init__(self):
            pass
        def validate_configuration(self):
            return {"valid": False, "issues": ["Core system not available"]}
    
    class UnifiedStorageManager:
        def __init__(self):
            pass
        def validate_configuration(self):
            return {"valid": False, "issues": ["Core system not available"]}
    
    manager = StorageManager()
    storage_manager = manager
    
    __all__ = ['storage_manager', 'UnifiedStorageManager', 'StorageManager', 'manager']