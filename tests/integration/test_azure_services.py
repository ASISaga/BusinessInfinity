"""
Integration tests for Azure services

Based on specifications in docs/testing/specifications.md
These tests can be run against Azure emulators or test instances.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import os
import json


@pytest.mark.integration
@pytest.mark.azure
class TestAzureServicesIntegration:
    """Integration tests for Azure services"""
    
    def test_azure_connection_strings_configured(self, mock_env_vars):
        """Test that Azure connection strings are properly configured"""
        # Assert
        assert 'AZURE_SERVICE_BUS_CONNECTION_STRING' in mock_env_vars
        assert 'AZURE_STORAGE_CONNECTION_STRING' in mock_env_vars
        assert mock_env_vars['AZURE_SERVICE_BUS_CONNECTION_STRING'].startswith('Endpoint=sb://')
    
    def test_table_names_configured(self, mock_env_vars):
        """Test that table names are properly configured"""
        # Assert
        assert 'BOARDROOM_TABLE_NAME' in mock_env_vars
        assert 'METRICS_TABLE_NAME' in mock_env_vars
        assert mock_env_vars['BOARDROOM_TABLE_NAME'] == 'TestBoardroomDecisions'


@pytest.mark.integration
@pytest.mark.table_storage
class TestTableStorageIntegration:
    """Integration tests for Azure Table Storage"""
    
    @pytest.mark.asyncio
    async def test_table_storage_mock_workflow(self, mock_table_storage, sample_business_decision):
        """Test complete workflow with mock table storage"""
        # Arrange
        entity = {
            'PartitionKey': 'decisions',
            'RowKey': sample_business_decision['decision_id'],
            'Title': sample_business_decision['title'],
            'Status': sample_business_decision['status'],
            'Context': json.dumps(sample_business_decision['context'])
        }
        
        # Act - Store
        mock_table_storage.create_entity(entity)
        
        # Act - Retrieve
        retrieved = mock_table_storage.get_entity(
            partition_key='decisions',
            row_key=sample_business_decision['decision_id']
        )
        
        # Assert
        assert retrieved is not None
        assert retrieved['RowKey'] == sample_business_decision['decision_id']
        assert retrieved['Title'] == sample_business_decision['title']
        assert retrieved['Status'] == sample_business_decision['status']
    
    def test_batch_insert_decisions(self, mock_table_storage):
        """Test inserting multiple decisions"""
        # Arrange
        decisions = [
            {
                'PartitionKey': 'decisions',
                'RowKey': f'decision-{i:03d}',
                'Title': f'Decision {i}',
                'Status': 'pending'
            }
            for i in range(10)
        ]
        
        # Act
        for decision in decisions:
            mock_table_storage.create_entity(decision)
        
        # Verify
        entities = mock_table_storage.query_entities("PartitionKey eq 'decisions'")
        assert len(entities) == 10
    
    def test_query_with_filter(self, mock_table_storage):
        """Test querying entities with filter"""
        # Arrange
        for i in range(5):
            mock_table_storage.create_entity({
                'PartitionKey': 'metrics',
                'RowKey': f'metric-{i}',
                'Value': i * 100
            })
        
        # Act
        results = mock_table_storage.query_entities("PartitionKey eq 'metrics'")
        
        # Assert
        assert len(results) == 5
        assert all(e['PartitionKey'] == 'metrics' for e in results)


@pytest.mark.integration
@pytest.mark.service_bus
class TestServiceBusIntegration:
    """Integration tests for Azure Service Bus"""
    
    @pytest.mark.asyncio
    async def test_service_bus_message_structure(self, sample_service_bus_message):
        """Test Service Bus message structure"""
        # Assert
        assert hasattr(sample_service_bus_message, 'get_body')
        assert hasattr(sample_service_bus_message, 'message_id')
        
        # Verify message body can be decoded
        body = sample_service_bus_message.get_body()
        assert isinstance(body, bytes)
        
        # Verify it's valid JSON
        decoded = json.loads(body.decode('utf-8'))
        assert 'type' in decoded
    
    @pytest.mark.asyncio
    async def test_mock_service_bus_sender(self, mock_service_bus_client):
        """Test mock Service Bus sender"""
        # Arrange
        test_message = {"type": "test", "data": "test_data"}
        
        # Act
        async with mock_service_bus_client.get_queue_sender('test-queue') as sender:
            await sender.send_messages(test_message)
        
        # Assert
        sender.send_messages.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mock_service_bus_receiver(self, mock_service_bus_client):
        """Test mock Service Bus receiver"""
        # Act
        async with mock_service_bus_client.get_queue_receiver('test-queue') as receiver:
            messages = await receiver.receive_messages(max_wait_time=5)
        
        # Assert
        receiver.receive_messages.assert_called_once_with(max_wait_time=5)
        assert isinstance(messages, list)


@pytest.mark.integration
class TestEndToEndWorkflow:
    """End-to-end workflow tests"""
    
    @pytest.mark.asyncio
    async def test_decision_creation_workflow(self, sample_business_decision, mock_table_storage):
        """Test complete decision creation workflow"""
        # Arrange - Prepare decision data
        decision = sample_business_decision.copy()
        
        # Act - Create decision in storage
        entity = {
            'PartitionKey': 'decisions',
            'RowKey': decision['decision_id'],
            'Title': decision['title'],
            'Type': decision['type'],
            'Status': 'pending',
            'Champion': decision['champion'],
            'RequiredVotes': decision['required_votes']
        }
        mock_table_storage.create_entity(entity)
        
        # Act - Retrieve decision
        stored_decision = mock_table_storage.get_entity('decisions', decision['decision_id'])
        
        # Assert - Verify workflow
        assert stored_decision is not None
        assert stored_decision['Status'] == 'pending'
        assert stored_decision['Title'] == decision['title']
        
        # Act - Update decision status
        entity['Status'] = 'approved'
        mock_table_storage.upsert_entity(entity)
        
        # Assert - Verify update
        updated_decision = mock_table_storage.get_entity('decisions', decision['decision_id'])
        assert updated_decision['Status'] == 'approved'


@pytest.mark.integration
class TestAsyncConcurrency:
    """Test concurrent async operations"""
    
    @pytest.mark.asyncio
    async def test_concurrent_decision_processing(self):
        """Test processing multiple decisions concurrently"""
        import asyncio
        
        # Arrange
        async def process_decision(decision_id):
            await asyncio.sleep(0.01)  # Simulate async work
            return {"id": decision_id, "status": "processed"}
        
        decision_ids = [f"decision-{i:03d}" for i in range(5)]
        
        # Act
        tasks = [process_decision(did) for did in decision_ids]
        results = await asyncio.gather(*tasks)
        
        # Assert
        assert len(results) == 5
        assert all(r['status'] == 'processed' for r in results)
        assert [r['id'] for r in results] == decision_ids
    
    @pytest.mark.asyncio
    async def test_concurrent_with_error_handling(self):
        """Test concurrent operations with error handling"""
        import asyncio
        
        # Arrange
        async def process_with_error(item_id):
            if item_id == "error":
                raise ValueError("Simulated error")
            return {"id": item_id, "status": "success"}
        
        items = ["item-1", "error", "item-3"]
        
        # Act
        tasks = [process_with_error(item) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Assert
        assert len(results) == 3
        assert isinstance(results[1], ValueError)
        assert results[0]['status'] == 'success'
        assert results[2]['status'] == 'success'
