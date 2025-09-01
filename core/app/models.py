"""
Backward compatibility module for models
This module re-exports models from the new models package structure.
"""
from .models import Envelope, UiAction, MessagesQuery, MessageType

__all__ = [
    'Envelope',
    'MessageType',
    'UiAction', 
    'MessagesQuery'
]