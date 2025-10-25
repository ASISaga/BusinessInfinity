"""
Knowledge Management System

This module provides centralized knowledge management for Business Infinity:
- Document storage and versioning
- Full-text search and indexing
- Knowledge graph for relationships
- Auto-generation from workflows and decisions
- Evidence retrieval for decision-making
"""

import json
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict, field


class DocumentType(Enum):
    """Types of knowledge documents"""
    DECISION = "decision"
    POLICY = "policy"
    PROCEDURE = "procedure"
    TEMPLATE = "template"
    MEMO = "memo"
    REPORT = "report"
    ANALYSIS = "analysis"
    LESSON = "lesson"
    REFERENCE = "reference"


class DocumentStatus(Enum):
    """Document status"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


@dataclass
class DocumentVersion:
    """Document version information"""
    version: str
    created_date: datetime
    created_by: str
    changes: str
    content: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_date'] = self.created_date.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentVersion':
        """Create from dictionary"""
        data['created_date'] = datetime.fromisoformat(data['created_date'])
        return cls(**data)


@dataclass
class KnowledgeDocument:
    """Knowledge document structure"""
    id: str
    title: str
    document_type: DocumentType
    status: DocumentStatus
    content: Dict[str, Any]
    created_date: datetime
    created_by: str
    last_modified_date: datetime
    last_modified_by: str
    current_version: str = "1.0"
    versions: List[DocumentVersion] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    related_documents: List[str] = field(default_factory=list)
    related_decisions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['document_type'] = self.document_type.value
        data['status'] = self.status.value
        data['created_date'] = self.created_date.isoformat()
        data['last_modified_date'] = self.last_modified_date.isoformat()
        data['versions'] = [v.to_dict() for v in self.versions]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeDocument':
        """Create from dictionary"""
        data['document_type'] = DocumentType(data['document_type'])
        data['status'] = DocumentStatus(data['status'])
        data['created_date'] = datetime.fromisoformat(data['created_date'])
        data['last_modified_date'] = datetime.fromisoformat(data['last_modified_date'])
        data['versions'] = [DocumentVersion.from_dict(v) for v in data.get('versions', [])]
        return cls(**data)


class KnowledgeBase:
    """
    Knowledge Management System for Business Infinity
    
    Provides centralized document storage, versioning, search, and knowledge graphs.
    """
    
    def __init__(self, storage_manager=None, config=None):
        self.storage_manager = storage_manager
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.documents: Dict[str, KnowledgeDocument] = {}
        self.search_index: Dict[str, Set[str]] = {}
    
    async def create_document(
        self,
        title: str,
        document_type: DocumentType,
        content: Dict[str, Any],
        created_by: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> KnowledgeDocument:
        """Create a new knowledge document"""
        doc_id = f"doc_{datetime.utcnow().timestamp()}"
        now = datetime.utcnow()
        
        document = KnowledgeDocument(
            id=doc_id,
            title=title,
            document_type=document_type,
            status=DocumentStatus.DRAFT,
            content=content,
            created_date=now,
            created_by=created_by,
            last_modified_date=now,
            last_modified_by=created_by,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self.documents[doc_id] = document
        await self._index_document(document)
        
        self.logger.info(f"Document created: {doc_id} - {title}")
        return document
    
    async def search_documents(
        self,
        query: str,
        document_type: Optional[DocumentType] = None,
        limit: int = 10
    ) -> List[KnowledgeDocument]:
        """Search for documents"""
        query_terms = query.lower().split()
        matching_doc_ids = set()
        
        for term in query_terms:
            if term in self.search_index:
                if not matching_doc_ids:
                    matching_doc_ids = self.search_index[term].copy()
                else:
                    matching_doc_ids &= self.search_index[term]
        
        results = [self.documents[doc_id] for doc_id in matching_doc_ids if doc_id in self.documents]
        
        if document_type:
            results = [d for d in results if d.document_type == document_type]
        
        results.sort(key=lambda d: d.last_modified_date, reverse=True)
        return results[:limit]
    
    async def _index_document(self, document: KnowledgeDocument):
        """Index document for search"""
        terms = set()
        terms.update(document.title.lower().split())
        terms.update(t.lower() for t in document.tags)
        
        for term in terms:
            if term not in self.search_index:
                self.search_index[term] = set()
            self.search_index[term].add(document.id)
