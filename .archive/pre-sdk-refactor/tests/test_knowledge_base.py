"""
Tests for Knowledge Management System

Basic tests to validate Knowledge Base functionality.
"""
import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from knowledge import KnowledgeBase, DocumentType, DocumentStatus


async def test_knowledge_base():
    """Test Knowledge Base basic functionality"""
    print("Testing Knowledge Base...")
    
    # Initialize knowledge base
    kb = KnowledgeBase()
    
    # Test 1: Create a document
    print("\n1. Testing document creation...")
    doc = await kb.create_document(
        title='Test Policy Document',
        document_type=DocumentType.POLICY,
        content={
            'summary': 'Test policy for validation',
            'sections': {
                'purpose': 'Testing knowledge base',
                'scope': 'All test scenarios'
            }
        },
        created_by='test@company.com',
        tags=['test', 'policy', 'validation'],
        metadata={'test_metadata': 'value'}
    )
    
    assert doc is not None, "Document should be created"
    assert doc.title == 'Test Policy Document', "Title should match"
    assert doc.document_type == DocumentType.POLICY, "Type should be POLICY"
    assert doc.status == DocumentStatus.DRAFT, "Initial status should be DRAFT"
    assert doc.current_version == '1.0', "Initial version should be 1.0"
    print("✅ Document creation successful")
    print(f"   Document ID: {doc.id}")
    print(f"   Version: {doc.current_version}")
    
    # Test 2: Search documents
    print("\n2. Testing document search...")
    results = await kb.search_documents(
        query='test policy',
        document_type=DocumentType.POLICY,
        limit=10
    )
    
    assert len(results) > 0, "Should find at least one document"
    assert results[0].id == doc.id, "Should find the created document"
    print(f"✅ Search successful - Found {len(results)} document(s)")
    
    # Test 3: Get document
    print("\n3. Testing document retrieval...")
    retrieved = await kb.get_document(doc.id)
    assert retrieved is not None, "Document should be retrievable"
    assert retrieved.id == doc.id, "Retrieved document should match"
    print("✅ Document retrieval successful")
    
    # Test 4: Create multiple documents
    print("\n4. Testing multiple documents...")
    doc2 = await kb.create_document(
        title='Test Procedure Document',
        document_type=DocumentType.PROCEDURE,
        content={'steps': ['Step 1', 'Step 2']},
        created_by='test@company.com',
        tags=['test', 'procedure']
    )
    
    doc3 = await kb.create_document(
        title='Test Decision Document',
        document_type=DocumentType.DECISION,
        content={'decision': 'Test decision'},
        created_by='test@company.com',
        tags=['test', 'decision']
    )
    
    # Get summary
    summary = await kb.get_knowledge_summary()
    assert summary['total_documents'] == 3, "Should have 3 documents"
    print(f"✅ Multiple documents created - Total: {summary['total_documents']}")
    print(f"   By type: {summary['by_type']}")
    
    # Test 5: Search with filters
    print("\n5. Testing filtered search...")
    policy_results = await kb.search_documents(
        query='test',
        document_type=DocumentType.POLICY
    )
    assert len(policy_results) == 1, "Should find only policy documents"
    
    all_results = await kb.search_documents(query='test')
    assert len(all_results) == 3, "Should find all test documents"
    print(f"✅ Filtered search successful")
    print(f"   Policy documents: {len(policy_results)}")
    print(f"   All test documents: {len(all_results)}")
    
    # Test 6: Auto-generate from decision
    print("\n6. Testing auto-generation from decision...")
    decision_data = {
        'id': 'test_decision_123',
        'title': 'Test Strategic Decision',
        'context': 'Testing auto-generation',
        'rationale': 'To validate knowledge base',
        'outcome': 'Success',
        'stakeholders': ['CEO', 'CTO'],
        'created_date': datetime.utcnow().isoformat()
    }
    
    auto_doc = await kb.auto_generate_from_decision(
        decision_data=decision_data,
        created_by='system'
    )
    
    assert auto_doc is not None, "Document should be auto-generated"
    assert auto_doc.document_type == DocumentType.DECISION, "Should be DECISION type"
    assert auto_doc.status == DocumentStatus.PUBLISHED, "Should be auto-published"
    assert 'auto-generated' in auto_doc.tags, "Should have auto-generated tag"
    print("✅ Auto-generation successful")
    print(f"   Document ID: {auto_doc.id}")
    print(f"   Status: {auto_doc.status.value}")
    
    # Test 7: Add relationships
    print("\n7. Testing document relationships...")
    await kb.add_relationship(
        source_id=doc.id,
        target_id=doc2.id,
        relationship_type='implements',
        strength=1.0
    )
    
    related = await kb.get_related_documents(doc.id)
    assert len(related) > 0, "Should have related documents"
    print(f"✅ Relationships added - {len(related)} related document(s)")
    
    print("\n" + "="*60)
    print("All Knowledge Base tests passed! ✅")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(test_knowledge_base())
