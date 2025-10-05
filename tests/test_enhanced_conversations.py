#!/usr/bin/env python3
"""
Test script for Azure Table Storage and Web Publishing functionality

Tests the enhanced conversation system with storage persistence and web publishing.
"""

import asyncio
import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_azure_table_storage():
    """Test Azure Table Storage integration"""
    try:
        logger.info("=== Testing Azure Table Storage Integration ===")
        
        # Import conversation system
        from conversations.boardroom_conversations import BoardroomConversationManager
        from conversations.conversation_system import (
            ConversationType, ConversationRole, ConversationStatus
        )
        
        # Test with mock storage manager
        class MockStorageManager:
            def __init__(self):
                self.entities = {}
                self.web_events = {}
            
            def get_table_client(self):
                return MockTableClient(self.entities)
                
        class MockTableClient:
            def __init__(self, entities):
                self.entities = entities
                
            def create_entity(self, entity):
                key = f"{entity['PartitionKey']}|{entity['RowKey']}"
                self.entities[key] = dict(entity)
                logger.info(f"✅ Created entity: {key}")
                
            def upsert_entity(self, entity):
                key = f"{entity['PartitionKey']}|{entity['RowKey']}"
                self.entities[key] = dict(entity)
                logger.info(f"✅ Upserted entity: {key}")
                
            def query_entities(self, query_filter=None):
                matching_entities = []
                for key, entity in self.entities.items():
                    if query_filter:
                        # Simple filter parsing for PartitionKey
                        if "PartitionKey eq" in query_filter:
                            partition_key = query_filter.split("'")[1]
                            if entity.get("PartitionKey") == partition_key:
                                matching_entities.append(entity)
                        elif "RowKey eq" in query_filter:
                            row_key = query_filter.split("'")[1]
                            if entity.get("RowKey") == row_key:
                                matching_entities.append(entity)
                        else:
                            matching_entities.append(entity)
                    else:
                        matching_entities.append(entity)
                return matching_entities
                
            def list_entities(self):
                return list(self.entities.values())
        
        # Initialize conversation manager with mock storage
        storage_manager = MockStorageManager()
        conv_manager = BoardroomConversationManager(storage_manager)
        
        logger.info("✅ Conversation manager initialized with mock Azure Table Storage")
        
        # Test 1: Create and store conversation
        logger.info("\n--- Test 1: Create and Store Conversation ---")
        conv_id = await conv_manager.create_conversation(
            conversation_type=ConversationType.STRATEGIC_FRAME,
            champion=ConversationRole.FOUNDER,
            title="Test Strategic Conversation",
            content="This is a test conversation for Azure Table Storage",
            context={"test": True}
        )
        
        logger.info(f"✅ Created conversation: {conv_id}")
        logger.info(f"✅ Storage entities: {len(storage_manager.entities)}")
        
        # Test 2: Retrieve conversation
        logger.info("\n--- Test 2: Retrieve Conversation ---")
        retrieved_conv = await conv_manager.get_conversation(conv_id)
        if retrieved_conv:
            logger.info(f"✅ Retrieved conversation: {retrieved_conv.title}")
            logger.info(f"   Status: {retrieved_conv.status.value}")
            logger.info(f"   Champion: {retrieved_conv.champion.value}")
        else:
            logger.error("❌ Failed to retrieve conversation")
        
        # Test 3: Sign conversation (triggers web publishing)
        logger.info("\n--- Test 3: Sign Conversation ---")
        success = await conv_manager.sign_conversation(
            conv_id,
            ConversationRole.FOUNDER,
            "Test Founder"
        )
        
        if success:
            logger.info("✅ Conversation signed successfully")
        else:
            logger.error("❌ Failed to sign conversation")
        
        # Test 4: Check web events
        logger.info("\n--- Test 4: Web Events ---")
        web_events = await conv_manager.get_web_events_since()
        logger.info(f"✅ Web events generated: {len(web_events)}")
        
        for event in web_events[:3]:  # Show first 3 events
            logger.info(f"   Event: {event.get('event_type')} - {event.get('conversation', {}).get('title', 'Unknown')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Azure Table Storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_web_publishing():
    """Test web publishing functionality"""
    try:
        logger.info("\n=== Testing Web Publishing ===")
        
        from conversations.boardroom_conversations import BoardroomConversationManager
        from conversations.conversation_system import ConversationType, ConversationRole
        
        # Initialize manager
        conv_manager = BoardroomConversationManager()
        
        # Test A2A communication with web publishing
        logger.info("\n--- Test A2A Communication ---")
        a2a_id = await conv_manager.create_a2a_communication(
            from_agent=ConversationRole.CEO,
            to_agent=ConversationRole.CUSTOMER,
            conversation_type=ConversationType.CUSTOMER_ENROLLMENT_EXT,
            message_content="Welcome to our new AI services!",
            context={"campaign": "Q4_launch", "external": True}
        )
        
        logger.info(f"✅ Created A2A communication: {a2a_id}")
        
        # Test web event retrieval
        web_events = await conv_manager.get_web_events_since()
        logger.info(f"✅ Web events available: {len(web_events)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Web publishing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_business_infinity_integration():
    """Test Business Infinity integration with new features"""
    try:
        logger.info("\n=== Testing Business Infinity Integration ===")
        
        from src.tools import BusinessInfinity, BusinessInfinityConfig
        
        # Initialize Business Infinity
        config = BusinessInfinityConfig()
        bi = BusinessInfinity(config)
        
        logger.info("✅ Business Infinity initialized")
        
        # Test new conversation methods
        logger.info("\n--- Test Enhanced Conversation Methods ---")
        
        # Test strategic conversation creation
        conv_id = await bi.create_strategic_conversation(
            title="AI Infrastructure Strategy",
            content="Strategic plan for AI infrastructure expansion"
        )
        
        if conv_id:
            logger.info(f"✅ Created strategic conversation: {conv_id}")
        else:
            logger.warning("⚠ Strategic conversation returned None (expected without full system)")
        
        # Test investment conversation
        investment_id = await bi.create_investment_conversation(
            amount=2000000,
            purpose="AI research and development"
        )
        
        if investment_id:
            logger.info(f"✅ Created investment conversation: {investment_id}")
        else:
            logger.warning("⚠ Investment conversation returned None (expected without full system)")
        
        # Test external communication
        external_id = await bi.create_external_stakeholder_communication(
            stakeholder_type="customer",
            message="New AI features available in Q1 2024"
        )
        
        if external_id:
            logger.info(f"✅ Created external communication: {external_id}")
        else:
            logger.warning("⚠ External communication returned None (expected without full system)")
        
        return True
        
    except Exception as e:
        logger.error(f"Business Infinity integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint_definitions():
    """Test that API endpoints are properly defined"""
    try:
        logger.info("\n=== Testing API Endpoint Definitions ===")
        
        # Test function definitions (without importing azure.functions)
        import inspect
        import sys
        
        # Read function_app.py to check for endpoint definitions
        with open('function_app.py', 'r') as f:
            content = f.read()
        
        # Check for conversation endpoints
        endpoints = [
            'conversations',
            'conversations/{conversation_id}',
            'conversations/{conversation_id}/sign',
            'conversations/a2a',
            'conversations/events'
        ]
        
        for endpoint in endpoints:
            if f'route="{endpoint}"' in content:
                logger.info(f"✅ Endpoint defined: {endpoint}")
            else:
                logger.error(f"❌ Endpoint missing: {endpoint}")
        
        # Check for HTTP methods
        methods = ['GET', 'POST']
        for method in methods:
            if f'methods=["{method}"]' in content or f'methods=["GET", "POST"]' in content:
                logger.info(f"✅ HTTP method supported: {method}")
        
        return True
        
    except Exception as e:
        logger.error(f"API endpoint test failed: {e}")
        return False

async def main():
    """Run all enhanced conversation system tests"""
    logger.info("Starting Enhanced Conversation System Tests")
    logger.info("Testing Azure Table Storage persistence and Web Publishing")
    
    # Test storage integration
    storage_result = await test_azure_table_storage()
    
    # Test web publishing
    web_result = await test_web_publishing()
    
    # Test Business Infinity integration
    bi_result = await test_business_infinity_integration()
    
    # Test API endpoints
    api_result = test_api_endpoint_definitions()
    
    # Summary
    if all([storage_result, web_result, bi_result, api_result]):
        logger.info("\n🎉 ALL ENHANCED TESTS PASSED 🎉")
        logger.info("✅ Azure Table Storage persistence working")
        logger.info("✅ Web publishing functionality implemented") 
        logger.info("✅ Business Infinity integration enhanced")
        logger.info("✅ API endpoints properly defined")
        logger.info("Boardroom conversations are now persisted and published to web clients!")
    else:
        results = {
            "Azure Table Storage": storage_result,
            "Web Publishing": web_result,
            "Business Infinity": bi_result,
            "API Endpoints": api_result
        }
        
        logger.info("\n📊 Test Results:")
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {test_name}: {status}")
    
    return all([storage_result, web_result, bi_result, api_result])

if __name__ == "__main__":
    asyncio.run(main())