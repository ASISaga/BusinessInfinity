"""
Test the refactored storage manager to ensure it properly uses AOS services
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest.mock import Mock, AsyncMock, patch


class TestStorageRefactor:
    """Test suite for the refactored storage manager"""

    def test_storage_manager_initialization(self):
        """Test that UnifiedStorageManager can initialize without errors"""
        with patch('src.core.features.storage.StorageManager') as mock_storage, \
             patch('src.core.features.storage.ServiceBusManager') as mock_servicebus:
            
            # Setup mocks
            mock_storage.return_value = Mock()
            mock_servicebus.return_value = Mock()
            
            # Create storage manager
            storage_manager = UnifiedStorageManager()
            
            # Verify initialization
            assert storage_manager is not None
            assert hasattr(storage_manager, 'storage_manager')
            assert hasattr(storage_manager, 'servicebus_manager')
            assert hasattr(storage_manager, 'boardroom_table')
            assert hasattr(storage_manager, 'metrics_table')

    @pytest.mark.asyncio
    async def test_store_boardroom_decision(self):
        """Test storing a boardroom decision using AOS services"""
        with patch('src.core.features.storage.StorageManager') as mock_storage, \
             patch('src.core.features.storage.ServiceBusManager') as mock_servicebus:
            
            # Setup mocks
            mock_storage_instance = AsyncMock()
            mock_storage_instance.store_table_entity = AsyncMock(return_value={"success": True})
            mock_storage.return_value = mock_storage_instance
            
            mock_servicebus.return_value = Mock()
            
            # Create storage manager
            storage_manager = UnifiedStorageManager()
            storage_manager.storage_manager = mock_storage_instance
            
            # Test data
            decision_data = {
                "PartitionKey": "BoardroomDecisions",
                "RowKey": "test_decision_1",
                "decision": "Approve new product launch",
                "decision_maker": "CEO",
                "status": "approved"
            }
            
            # Call method
            result = await storage_manager.store_boardroom_decision(decision_data)
            
            # Verify
            assert result is True
            mock_storage_instance.store_table_entity.assert_called_once()

    @pytest.mark.asyncio
    async def test_enqueue_request(self):
        """Test enqueuing a request using AOS ServiceBus manager"""
        with patch('src.core.features.storage.StorageManager') as mock_storage, \
             patch('src.core.features.storage.ServiceBusManager') as mock_servicebus:
            
            # Setup mocks
            mock_servicebus_instance = AsyncMock()
            mock_servicebus_instance.send_message = AsyncMock(return_value={"success": True})
            mock_servicebus.return_value = mock_servicebus_instance
            
            mock_storage.return_value = Mock()
            
            # Create storage manager
            storage_manager = UnifiedStorageManager()
            storage_manager.servicebus_manager = mock_servicebus_instance
            
            # Test data
            request_msg = {
                "agent": "CEO",
                "action": "analyze_market",
                "parameters": {"market": "tech", "region": "US"}
            }
            
            # Call method
            await storage_manager.enqueue_request(request_msg)
            
            # Verify
            mock_servicebus_instance.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_boardroom_history(self):
        """Test retrieving boardroom history using AOS services"""
        with patch('src.core.features.storage.StorageManager') as mock_storage, \
             patch('src.core.features.storage.ServiceBusManager') as mock_servicebus:
            
            # Setup mocks
            mock_storage_instance = AsyncMock()
            mock_decisions = [
                {"decision": "Approve budget", "decision_maker": "CEO"},
                {"decision": "Launch product", "decision_maker": "COO"}
            ]
            mock_storage_instance.query_table_entities = AsyncMock(
                return_value={"success": True, "entities": mock_decisions}
            )
            mock_storage.return_value = mock_storage_instance
            
            mock_servicebus.return_value = Mock()
            
            # Create storage manager
            storage_manager = UnifiedStorageManager()
            storage_manager.storage_manager = mock_storage_instance
            
            # Call method
            result = await storage_manager.get_boardroom_history(limit=10)
            
            # Verify
            assert len(result) == 2
            assert result[0]["decision"] == "Approve budget"
            mock_storage_instance.query_table_entities.assert_called_once()

    def test_legacy_methods_raise_errors(self):
        """Test that legacy direct Azure SDK methods raise appropriate errors"""
        storage_manager = UnifiedStorageManager()
        
        # Test legacy methods
        with pytest.raises(NotImplementedError):
            storage_manager.get_table_client()
        
        with pytest.raises(NotImplementedError):
            storage_manager.get_cosmos_table_client()
        
        with pytest.raises(NotImplementedError):
            storage_manager.get_queue_client("test-queue")
        
        with pytest.raises(NotImplementedError):
            storage_manager.get_blob_client("test-container", "test-blob")


if __name__ == "__main__":
    # Run a simple test
    print("Testing UnifiedStorageManager initialization...")
    
    with patch('src.core.features.storage.StorageManager') as mock_storage, \
         patch('src.core.features.storage.ServiceBusManager') as mock_servicebus:
        
        mock_storage.return_value = Mock()
        mock_servicebus.return_value = Mock()
        
        try:
            storage_manager = UnifiedStorageManager()
            print("✅ UnifiedStorageManager initialized successfully!")
            print(f"📋 Boardroom table: {storage_manager.boardroom_table}")
            print(f"📊 Metrics table: {storage_manager.metrics_table}")
            print(f"🤝 Collaboration table: {storage_manager.collaboration_table}")
            print(f"📥 Request queue: {storage_manager.request_queue}")
            print(f"📤 Event queue: {storage_manager.event_queue}")
        except Exception as e:
            print(f"❌ Initialization failed: {e}")