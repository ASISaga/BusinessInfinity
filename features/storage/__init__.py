"""
Storage and Data Management Feature
Consolidates all storage, conversation, and data management functionality
"""
from .manager import UnifiedStorageManager

# Create singleton instance
storage_manager = UnifiedStorageManager()

__all__ = ['storage_manager', 'UnifiedStorageManager']