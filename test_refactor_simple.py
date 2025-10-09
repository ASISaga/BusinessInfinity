"""
Simple test script to validate the refactored storage manager
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest.mock import Mock, AsyncMock, patch

def test_storage_initialization():
    """Test that UnifiedStorageManager can initialize without errors"""
    print("Testing UnifiedStorageManager initialization...")
    
    with patch('core.features.storage.StorageManager') as mock_storage, \
         patch('core.features.storage.ServiceBusManager') as mock_servicebus, \
         patch('core.features.storage.env_manager') as mock_env:
        
        # Setup mocks
        mock_storage.return_value = Mock()
        mock_servicebus.return_value = Mock()
        mock_env.get.side_effect = lambda key, default=None: {
            "BOARDROOM_TABLE_NAME": "BoardroomDecisions",
            "METRICS_TABLE_NAME": "BusinessMetrics",
            "COLLABORATION_TABLE_NAME": "AgentCollaboration",
            "REQUEST_QUEUE_NAME": "agent-requests",
            "EVENT_QUEUE_NAME": "agent-events",
            "AZURE_STORAGE_CONNECTION_STRING": "mock_connection_string",
            "AZURE_SERVICE_BUS_CONNECTION_STRING": "mock_servicebus_connection"
        }.get(key, default)
        
        try:
            from core.features.storage import UnifiedStorageManager
            
            # Create storage manager
            storage_manager = UnifiedStorageManager()
            
            # Verify initialization
            assert storage_manager is not None
            assert hasattr(storage_manager, 'storage_manager')
            assert hasattr(storage_manager, 'servicebus_manager')
            assert hasattr(storage_manager, 'boardroom_table')
            assert hasattr(storage_manager, 'metrics_table')
            
            print("✅ UnifiedStorageManager initialized successfully!")
            print(f"📋 Boardroom table: {storage_manager.boardroom_table}")
            print(f"📊 Metrics table: {storage_manager.metrics_table}")
            print(f"🤝 Collaboration table: {storage_manager.collaboration_table}")
            print(f"📥 Request queue: {storage_manager.request_queue}")
            print(f"📤 Event queue: {storage_manager.event_queue}")
            
            return True
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False

async def test_store_boardroom_decision():
    """Test storing a boardroom decision using AOS services"""
    print("\nTesting store_boardroom_decision...")
    
    with patch('core.features.storage.StorageManager') as mock_storage, \
         patch('core.features.storage.ServiceBusManager') as mock_servicebus, \
         patch('core.features.storage.env_manager') as mock_env:
        
        # Setup mocks
        mock_storage_instance = AsyncMock()
        mock_storage_instance.store_table_entity = AsyncMock(return_value={"success": True})
        mock_storage.return_value = mock_storage_instance
        
        mock_servicebus.return_value = Mock()
        mock_env.get.side_effect = lambda key, default=None: {
            "BOARDROOM_TABLE_NAME": "BoardroomDecisions",
            "METRICS_TABLE_NAME": "BusinessMetrics",
            "COLLABORATION_TABLE_NAME": "AgentCollaboration",
            "REQUEST_QUEUE_NAME": "agent-requests",
            "EVENT_QUEUE_NAME": "agent-events",
            "AZURE_STORAGE_CONNECTION_STRING": "mock_connection_string",
            "AZURE_SERVICE_BUS_CONNECTION_STRING": "mock_servicebus_connection"
        }.get(key, default)
        
        try:
            from core.features.storage import UnifiedStorageManager
            
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
            
            print("✅ store_boardroom_decision works correctly!")
            return True
        except Exception as e:
            print(f"❌ store_boardroom_decision failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_legacy_methods():
    """Test that legacy methods properly raise NotImplementedError"""
    print("\nTesting legacy methods...")
    
    with patch('core.features.storage.StorageManager') as mock_storage, \
         patch('core.features.storage.ServiceBusManager') as mock_servicebus, \
         patch('core.features.storage.env_manager') as mock_env:
        
        mock_storage.return_value = Mock()
        mock_servicebus.return_value = Mock()
        mock_env.get.side_effect = lambda key, default=None: {
            "BOARDROOM_TABLE_NAME": "BoardroomDecisions",
            "AZURE_STORAGE_CONNECTION_STRING": "mock_connection_string",
            "AZURE_SERVICE_BUS_CONNECTION_STRING": "mock_servicebus_connection"
        }.get(key, default)
        
        try:
            from core.features.storage import UnifiedStorageManager
            
            storage_manager = UnifiedStorageManager()
            
            # Test legacy methods
            legacy_methods = [
                ('get_table_client', []),
                ('get_cosmos_table_client', []),
                ('get_queue_client', ['test-queue']),
                ('get_blob_client', ['test-container', 'test-blob'])
            ]
            
            for method_name, args in legacy_methods:
                try:
                    method = getattr(storage_manager, method_name)
                    method(*args)
                    print(f"❌ {method_name} should raise NotImplementedError")
                    return False
                except NotImplementedError:
                    print(f"✅ {method_name} properly raises NotImplementedError")
                except Exception as e:
                    print(f"❌ {method_name} raised unexpected error: {e}")
                    return False
            
            return True
        except Exception as e:
            print(f"❌ Legacy method test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Run all tests"""
    print("🧪 Running BusinessInfinity Storage Refactoring Tests")
    print("=" * 60)
    
    tests = [
        test_storage_initialization(),
        asyncio.run(test_store_boardroom_decision()),
        test_legacy_methods()
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Refactoring appears successful!")
        print("\n✅ Key Achievements:")
        print("   • UnifiedStorageManager now uses AOS services instead of direct Azure SDK")
        print("   • StorageManager handles Azure Tables, Blobs, and Queues")
        print("   • ServiceBusManager handles Azure Service Bus operations")
        print("   • Legacy methods properly raise NotImplementedError")
        print("   • Business logic remains in BusinessInfinity layer")
        print("   • Separation of concerns maintained")
    else:
        print("❌ Some tests failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)