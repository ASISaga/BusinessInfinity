# Knowledge Management System

## Overview

The Knowledge Management System provides centralized document storage, versioning, search, and knowledge graph capabilities for Business Infinity. It serves as the organizational memory, capturing decisions, policies, procedures, and lessons learned.

## Key Features

### Document Management
- Create and manage knowledge documents with rich metadata
- Support for multiple document types (Decisions, Policies, Procedures, Templates, etc.)
- Full versioning with change tracking
- Status workflow (Draft → Review → Approved → Published)

### Search and Discovery
- Full-text search across all documents
- Tag-based filtering and categorization
- Document type filtering
- Relevance-based ranking

### Knowledge Relationships
- Link related documents
- Track document dependencies
- Build knowledge graphs
- Relationship strength scoring

### Auto-Generation
- Automatically create knowledge from decisions
- Extract insights from workflows
- Generate documentation from business processes
- Maintain living documentation

### Version Control
- Complete version history
- Track who made changes and when
- Describe what changed in each version
- Revert to previous versions

## Architecture

### Core Classes

#### `KnowledgeDocument`
Represents a knowledge document:
```python
@dataclass
class KnowledgeDocument:
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
```

#### `DocumentVersion`
Tracks document versions:
```python
@dataclass
class DocumentVersion:
    version: str
    created_date: datetime
    created_by: str
    changes: str
    content: Dict[str, Any]
```

#### `KnowledgeBase`
Main interface for knowledge management operations.

### Enumerations

#### `DocumentType`
- `DECISION`: Strategic and operational decisions
- `POLICY`: Organizational policies and standards
- `PROCEDURE`: Standard operating procedures
- `TEMPLATE`: Reusable document templates
- `MEMO`: Memos and communications
- `REPORT`: Analysis and reports
- `ANALYSIS`: Business analysis documents
- `LESSON`: Lessons learned and retrospectives
- `REFERENCE`: Reference materials

#### `DocumentStatus`
- `DRAFT`: Initial creation, not ready for review
- `REVIEW`: Under review by stakeholders
- `APPROVED`: Approved but not yet published
- `PUBLISHED`: Live and accessible
- `ARCHIVED`: Archived for historical reference
- `DEPRECATED`: No longer valid or superseded

## Usage

### Create a Document

```python
from knowledge import KnowledgeBase, DocumentType

# Initialize knowledge base
knowledge_base = KnowledgeBase(storage_manager, config)

# Create a new document
document = await knowledge_base.create_document(
    title='Data Retention Policy',
    document_type=DocumentType.POLICY,
    content={
        'summary': 'Organization-wide data retention and deletion policy',
        'sections': {
            'purpose': 'Define data retention requirements for compliance',
            'scope': 'All organizational data and systems',
            'retention_periods': {
                'customer_data': '7 years',
                'transaction_records': '10 years',
                'audit_logs': '5 years'
            },
            'deletion_process': 'Automated deletion after retention period...'
        }
    },
    created_by='compliance@company.com',
    tags=['policy', 'compliance', 'data', 'gdpr'],
    metadata={'compliance_framework': 'GDPR', 'review_cycle': 'annual'}
)

print(f"Document created: {document.id} - Version {document.current_version}")
```

### Update a Document

```python
# Update document content
updated_content = document.content.copy()
updated_content['sections']['retention_periods']['email'] = '3 years'

document = await knowledge_base.update_document(
    doc_id=document.id,
    content=updated_content,
    modified_by='compliance@company.com',
    changes='Added email retention policy',
    bump_version=True  # Increment version to 1.1
)

print(f"Document updated to version {document.current_version}")
```

### Publish a Document

```python
# Publish document to make it accessible
document = await knowledge_base.publish_document(
    doc_id=document.id,
    published_by='ceo@company.com'
)

print(f"Document published: {document.status.value}")
```

### Search Documents

```python
# Search for documents
results = await knowledge_base.search_documents(
    query='data retention compliance',
    document_type=DocumentType.POLICY,
    limit=10
)

for doc in results:
    print(f"Found: {doc.title} (v{doc.current_version})")
```

### Auto-Generate from Decisions

```python
# Automatically create knowledge from a decision
decision_data = {
    'id': 'decision_123',
    'title': 'Adopt new authentication system',
    'context': 'Need to improve security posture',
    'rationale': 'Current system has known vulnerabilities',
    'outcome': 'Approved with Q2 implementation timeline',
    'stakeholders': ['CISO', 'CTO', 'CEO'],
    'created_date': '2024-01-15T10:00:00Z'
}

document = await knowledge_base.auto_generate_from_decision(
    decision_data=decision_data,
    created_by='system'
)

print(f"Auto-generated document: {document.id}")
```

### Link Related Documents

```python
# Add relationships between documents
await knowledge_base.add_relationship(
    source_id=policy_doc.id,
    target_id=procedure_doc.id,
    relationship_type='implements',
    strength=1.0,
    metadata={'created_date': datetime.utcnow().isoformat()}
)

# Get related documents
related = await knowledge_base.get_related_documents(
    doc_id=policy_doc.id,
    relationship_type='implements'
)
```

### Get Knowledge Summary

```python
# Get summary statistics
summary = await knowledge_base.get_knowledge_summary()

print(f"Total documents: {summary['total_documents']}")
print(f"Published: {summary['by_status']['published']}")
print(f"Policies: {summary['by_type']['policy']}")
```

## Document Types and Use Cases

### DECISION
**Purpose**: Capture strategic and operational decisions  
**Content Structure**:
```python
{
    'context': 'Why the decision was needed',
    'options_considered': ['Option A', 'Option B'],
    'rationale': 'Why this option was chosen',
    'outcome': 'The decision made',
    'stakeholders': ['Role1', 'Role2'],
    'impact': 'Expected impact',
    'next_steps': 'Follow-up actions'
}
```

### POLICY
**Purpose**: Define organizational standards and rules  
**Content Structure**:
```python
{
    'summary': 'Brief policy description',
    'sections': {
        'purpose': 'Why this policy exists',
        'scope': 'What it applies to',
        'requirements': 'What must be done',
        'exceptions': 'When exceptions are allowed'
    },
    'compliance_framework': 'Relevant regulations',
    'enforcement': 'How policy is enforced'
}
```

### PROCEDURE
**Purpose**: Document standard operating procedures  
**Content Structure**:
```python
{
    'summary': 'What this procedure does',
    'steps': [
        {'order': 1, 'action': 'First step', 'responsible': 'Role'},
        {'order': 2, 'action': 'Second step', 'responsible': 'Role'}
    ],
    'prerequisites': 'What must be true before starting',
    'expected_outcome': 'What should result',
    'troubleshooting': 'Common issues and solutions'
}
```

### LESSON
**Purpose**: Capture lessons learned and retrospectives  
**Content Structure**:
```python
{
    'situation': 'What happened',
    'what_went_well': ['Success 1', 'Success 2'],
    'what_to_improve': ['Improvement 1', 'Improvement 2'],
    'action_items': ['Action 1', 'Action 2'],
    'key_takeaways': ['Lesson 1', 'Lesson 2']
}
```

## Integration Points

### Decision Workflows
Knowledge is automatically generated from decision workflows:
- Decision rationale captured as knowledge
- Precedent tracking for similar decisions
- Link decisions to related policies

### Risk Registry
Documents can reference and be referenced by risks:
- Policy documents linked to compliance risks
- Procedure documents for risk mitigation
- Lessons learned from risk incidents

### Agent Collaboration
Agents can access knowledge base for context:
- Reference historical decisions
- Apply relevant policies
- Follow documented procedures
- Learn from past lessons

## Best Practices

### 1. Structured Content
- Use consistent content structure for each document type
- Include all relevant metadata
- Tag documents appropriately

### 2. Version Control
- Describe changes clearly in each version
- Use semantic versioning (major.minor)
- Major version for significant changes
- Minor version for updates and additions

### 3. Status Workflow
- Keep drafts until reviewed
- Get approval before publishing
- Archive when superseded
- Deprecate instead of deleting

### 4. Relationships
- Link related documents
- Create knowledge graphs
- Track document dependencies
- Show policy implementations

### 5. Search Optimization
- Use descriptive titles
- Add comprehensive tags
- Include keywords in content
- Maintain metadata

## Future Enhancements

- **AI-Powered Search**: Semantic search with embeddings
- **Auto-Tagging**: Automatic tag suggestions
- **Smart Recommendations**: Suggest related documents
- **Visual Knowledge Graph**: Interactive relationship visualization
- **Collaboration Features**: Comments, reviews, approvals
- **External Integration**: Import from external knowledge systems
- **Access Control**: Fine-grained permissions
- **Analytics**: Knowledge usage and gap analysis

## API Reference

See `src/knowledge/knowledge_base.py` for complete API documentation.

## Related Documentation

- [Risk Management](RISK_MANAGEMENT.md) - Risk tracking and mitigation
- [Decision Framework](DECISION_FRAMEWORK.md) - Decision-making processes
- [Workflow Orchestration](../workflows/README.md) - Business workflow management
