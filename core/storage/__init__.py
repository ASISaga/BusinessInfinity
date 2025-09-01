"""
Storage management package
"""
from .unified_storage_manager import UnifiedStorageManager

# Global instance
storage_manager = UnifiedStorageManager()

__all__ = ['UnifiedStorageManager', 'storage_manager']