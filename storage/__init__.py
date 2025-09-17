"""
Storage Feature
Consolidated into core system - this module provides backward compatibility.
Use core.storage_manager instead.
"""

# Backward compatibility - redirect to core system
try:
    from core.features.storage import storage_manager, UnifiedStorageManager
    
    # Create aliases for backward compatibility
    StorageManager = UnifiedStorageManager
    manager = storage_manager
    
    __all__ = ['storage_manager', 'UnifiedStorageManager', 'StorageManager', 'manager']
except ImportError:
    # If core system not available, provide fallback
    class StorageManager:
        def __init__(self):
            pass
    
    class UnifiedStorageManager:
        def __init__(self):
            pass
    
    manager = StorageManager()
    storage_manager = manager
    
    __all__ = ['storage_manager', 'UnifiedStorageManager', 'StorageManager', 'manager']