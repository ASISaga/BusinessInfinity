"""
Shared pytest fixtures for BusinessInfinity tests

Based on the testing specifications in docs/testing/specifications.md
"""
import os
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

# Set environment to testing mode
os.environ['TESTING'] = 'true'


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    env_vars = {
        'AZURE_SERVICE_BUS_CONNECTION_STRING': 'Endpoint=sb://test.servicebus.windows.net/;SharedAccessKeyName=test;SharedAccessKey=test',
        'AZURE_STORAGE_CONNECTION_STRING': 'DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test==;EndpointSuffix=core.windows.net',
        'BUSINESS_DECISIONS_QUEUE': 'test-decisions',
        'BUSINESS_EVENTS_TOPIC': 'test-events',
        'BOARDROOM_TABLE_NAME': 'TestBoardroomDecisions',
        'METRICS_TABLE_NAME': 'TestBusinessMetrics',
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def sample_business_decision():
    """Sample business decision data for testing"""
    return {
        "decision_id": "test-decision-001",
        "type": "strategic",
        "title": "Test Strategic Decision",
        "context": {
            "initiative": "Test Initiative",
            "budget": 100000,
            "timeline": "Q1 2024"
        },
        "champion": "founder",
        "required_votes": 3,
        "status": "pending"
    }


@pytest.fixture
def sample_service_bus_message():
    """Sample Service Bus message for testing"""
    message = MagicMock()
    message.get_body.return_value = b'{"type": "test", "data": "test_data"}'
    message.message_id = "test-message-id"
    message.enqueued_time_utc = "2024-01-01T00:00:00Z"
    return message


@pytest.fixture
def mock_table_client():
    """Mock Azure Table client"""
    client = MagicMock()
    client.create_entity = MagicMock()
    client.upsert_entity = MagicMock()
    client.get_entity = MagicMock(return_value={
        'PartitionKey': 'test',
        'RowKey': 'test-001',
        'Data': 'test data'
    })
    client.query_entities = MagicMock(return_value=[])
    return client


@pytest.fixture
def mock_service_bus_client():
    """Mock Service Bus client for unit tests"""
    client = MagicMock()
    
    # Mock sender
    sender = MagicMock()
    sender.send_messages = AsyncMock()
    client.get_queue_sender.return_value.__aenter__.return_value = sender
    
    # Mock receiver
    receiver = MagicMock()
    receiver.receive_messages = AsyncMock(return_value=[])
    receiver.complete_message = AsyncMock()
    client.get_queue_receiver.return_value.__aenter__.return_value = receiver
    
    return client


@pytest.fixture
def mock_table_storage():
    """Mock Table Storage for unit tests"""
    class MockTableClient:
        def __init__(self):
            self.entities = {}
        
        def create_entity(self, entity):
            key = f"{entity['PartitionKey']}|{entity['RowKey']}"
            self.entities[key] = dict(entity)
        
        def upsert_entity(self, entity):
            key = f"{entity['PartitionKey']}|{entity['RowKey']}"
            self.entities[key] = dict(entity)
        
        def get_entity(self, partition_key, row_key):
            key = f"{partition_key}|{row_key}"
            return self.entities.get(key)
        
        def query_entities(self, query_filter=None):
            if not query_filter:
                return list(self.entities.values())
            
            results = []
            for entity in self.entities.values():
                # Simple filter parsing
                if "PartitionKey eq" in query_filter:
                    pk = query_filter.split("'")[1]
                    if entity.get('PartitionKey') == pk:
                        results.append(entity)
            return results
        
        def list_entities(self):
            return list(self.entities.values())
    
    return MockTableClient()
