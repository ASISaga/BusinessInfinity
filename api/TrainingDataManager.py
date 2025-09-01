"""
DEPRECATED: This module has been consolidated into core/storage.py
Use: from core.storage import storage_manager instead
"""
import warnings
from core.storage import UnifiedStorageManager as TrainingDataManager

warnings.warn(
    "api.TrainingDataManager is deprecated. Use core.storage.storage_manager instead.",
    DeprecationWarning,
    stacklevel=2
)
