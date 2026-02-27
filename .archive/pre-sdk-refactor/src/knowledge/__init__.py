"""
Knowledge Management Module

Centralized knowledge management for Business Infinity.
"""

from .knowledge_base import (
    KnowledgeBase,
    KnowledgeDocument,
    DocumentType,
    DocumentStatus,
    DocumentVersion
)

__all__ = [
    'KnowledgeBase',
    'KnowledgeDocument',
    'DocumentType',
    'DocumentStatus',
    'DocumentVersion'
]
