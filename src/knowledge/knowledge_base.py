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
    
    async def get_document(self, doc_id: str) -> Optional[KnowledgeDocument]:
        """Get a document by ID"""
        return self.documents.get(doc_id)
    
    async def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get summary statistics of knowledge base"""
        total_docs = len(self.documents)
        
        # Count by type
        by_type = {}
        for doc_type in DocumentType:
            by_type[doc_type.value] = len([
                d for d in self.documents.values()
                if d.document_type == doc_type
            ])
        
        # Count by status
        by_status = {}
        for status in DocumentStatus:
            by_status[status.value] = len([
                d for d in self.documents.values()
                if d.status == status
            ])
        
        return {
            'total_documents': total_docs,
            'by_type': by_type,
            'by_status': by_status,
            'indexed_terms': len(self.search_index)
        }
    
    async def auto_generate_from_decision(
        self,
        decision_data: Dict[str, Any],
        created_by: str
    ) -> KnowledgeDocument:
        """Auto-generate knowledge document from a decision"""
        title = f"Decision: {decision_data.get('title', 'Untitled')}"
        
        content = {
            'decision_id': decision_data.get('id'),
            'context': decision_data.get('context'),
            'rationale': decision_data.get('rationale'),
            'outcome': decision_data.get('outcome'),
            'stakeholders': decision_data.get('stakeholders'),
            'created_date': decision_data.get('created_date')
        }
        
        tags = ['decision', 'auto-generated']
        
        document = await self.create_document(
            title=title,
            document_type=DocumentType.DECISION,
            content=content,
            created_by=created_by,
            tags=tags,
            metadata={'source': 'decision', 'decision_id': decision_data.get('id')}
        )
        
        # Auto-publish
        document.status = DocumentStatus.PUBLISHED
        return document
    
    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a relationship between documents"""
        # Simple implementation - just add to related_documents
        if source_id in self.documents:
            if target_id not in self.documents[source_id].related_documents:
                self.documents[source_id].related_documents.append(target_id)
        
        self.logger.info(f"Relationship added: {source_id} -> {target_id} ({relationship_type})")
    
    async def get_related_documents(
        self,
        doc_id: str,
        relationship_type: Optional[str] = None
    ) -> List[KnowledgeDocument]:
        """Get documents related to a specific document"""
        if doc_id not in self.documents:
            return []
        
        related_ids = self.documents[doc_id].related_documents
        return [self.documents[rid] for rid in related_ids if rid in self.documents]
    
    async def _index_document(self, document: KnowledgeDocument):
        """Index document for search"""
        terms = set()
        terms.update(document.title.lower().split())
        terms.update(t.lower() for t in document.tags)
        
        for term in terms:
            if term not in self.search_index:
                self.search_index[term] = set()
            self.search_index[term].add(document.id)
