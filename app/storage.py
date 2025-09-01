"""
DEPRECATED: This module has been consolidated into core/storage.py  
Use: from core.storage import storage_manager instead
"""
import warnings
from core.storage import storage_manager

warnings.warn(
    "app.storage is deprecated. Use core.storage.storage_manager instead.",
    DeprecationWarning,
    stacklevel=2
)

# Backwards compatibility aliases
table = storage_manager.get_table_client
queue = storage_manager.get_queue_client
to_row = storage_manager.to_row
from_row = storage_manager.from_row
enqueue_request = storage_manager.enqueue_request
enqueue_event = storage_manager.enqueue_event
query_messages = storage_manager.query_messages