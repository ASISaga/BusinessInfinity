"""
Unit tests for Storage Manager

Based on specifications in docs/testing/specifications.md
Tests the UnifiedStorageManager class with mocked dependencies.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime


@pytest.mark.unit
class TestStorageManager:
    """Unit tests for Storage Manager"""
    
    @pytest.fixture
    def mock_env_manager(self):
        """Mock environment manager"""
        env_mgr = MagicMock()
        env_mgr.get = MagicMock(side_effect=lambda key, default: default)
        return env_mgr
    
    @pytest.fixture
    def storage_manager(self, mock_table_client, mock_env_manager):
        """Create StorageManager with mocked table client"""
        with patch('src.core.features.storage.UnifiedEnvManager', return_value=mock_env_manager):
            from src.core.features.storage import UnifiedStorageManager
            
            # Create instance
            with patch.object(UnifiedStorageManager, '__init__', lambda self, env=None: None):
                manager = UnifiedStorageManager()
                manager.boardroom_table = "TestBoardroomDecisions"
                manager.metrics_table = "TestBusinessMetrics"
                manager.collaboration_table = "TestAgentCollaboration"
                manager.logger = MagicMock()
                manager.get_table_client = MagicMock(return_value=mock_table_client)
                manager.store_entity = AsyncMock(return_value=True)
                manager.get_entities = AsyncMock(return_value=[])
                
                return manager
    
    @pytest.mark.asyncio
    async def test_store_boardroom_decision(self, storage_manager, sample_business_decision):
        """Test storing a boardroom decision"""
        # Act
        result = await storage_manager.store_boardroom_decision(sample_business_decision)
        
        # Assert
        assert result is True
        storage_manager.store_entity.assert_called_once()
        
        # Verify the entity has required fields
        call_args = storage_manager.store_entity.call_args[0]
        assert call_args[0] == "TestBoardroomDecisions"
        stored_data = call_args[1]
        assert 'timestamp' in stored_data
        assert 'source' in stored_data
        assert stored_data['source'] == 'business_infinity_boardroom'
    
    @pytest.mark.asyncio
    async def test_store_boardroom_decision_error_handling(self, storage_manager, sample_business_decision):
        """Test error handling when storing decision fails"""
        # Arrange
        storage_manager.store_entity = AsyncMock(side_effect=Exception("Storage error"))
        
        # Act
        result = await storage_manager.store_boardroom_decision(sample_business_decision)
        
        # Assert
        assert result is False
        storage_manager.logger.error.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_store_business_metrics(self, storage_manager):
        """Test storing business metrics"""
        # Arrange
        metrics = {
            "revenue": 100000,
            "users": 5000,
            "conversion_rate": 0.15
        }
        agent_id = "ceo-001"
        
        # Act
        result = await storage_manager.store_business_metrics(metrics, agent_id)
        
        # Assert
        assert result is True
        storage_manager.store_entity.assert_called_once()
        
        # Verify the metrics data structure
        call_args = storage_manager.store_entity.call_args[0]
        assert call_args[0] == "TestBusinessMetrics"
        stored_data = call_args[1]
        assert stored_data['agent_id'] == agent_id
        assert stored_data['metrics'] == metrics
        assert 'timestamp' in stored_data
        assert stored_data['source'] == 'business_infinity'
    
    @pytest.mark.asyncio
    async def test_get_boardroom_history(self, storage_manager):
        """Test retrieving boardroom history"""
        # Arrange
        expected_history = [
            {"decision_id": "001", "title": "Decision 1"},
            {"decision_id": "002", "title": "Decision 2"}
        ]
        storage_manager.get_entities = AsyncMock(return_value=expected_history)
        
        # Act
        history = await storage_manager.get_boardroom_history(limit=10)
        
        # Assert
        assert len(history) == 2
        assert history == expected_history
        storage_manager.get_entities.assert_called_once_with("TestBoardroomDecisions", limit=10)
    
    @pytest.mark.asyncio
    async def test_get_boardroom_history_default_limit(self, storage_manager):
        """Test retrieving boardroom history with default limit"""
        # Arrange
        storage_manager.get_entities = AsyncMock(return_value=[])
        
        # Act
        history = await storage_manager.get_boardroom_history()
        
        # Assert
        storage_manager.get_entities.assert_called_once_with("TestBoardroomDecisions", limit=100)
    
    @pytest.mark.asyncio
    async def test_get_boardroom_history_error_handling(self, storage_manager):
        """Test error handling when retrieving history fails"""
        # Arrange
        storage_manager.get_entities = AsyncMock(side_effect=Exception("Query error"))
        
        # Act
        history = await storage_manager.get_boardroom_history()
        
        # Assert
        assert history == []
        storage_manager.logger.error.assert_called_once()


@pytest.mark.unit
class TestTableStorageMock:
    """Test the mock table storage implementation"""
    
    def test_mock_table_create_entity(self, mock_table_storage):
        """Test creating an entity in mock table storage"""
        # Arrange
        entity = {
            'PartitionKey': 'decisions',
            'RowKey': 'decision-001',
            'Title': 'Test Decision',
            'Status': 'pending'
        }
        
        # Act
        mock_table_storage.create_entity(entity)
        
        # Assert
        retrieved = mock_table_storage.get_entity('decisions', 'decision-001')
        assert retrieved is not None
        assert retrieved['Title'] == 'Test Decision'
    
    def test_mock_table_upsert_entity(self, mock_table_storage):
        """Test upserting an entity in mock table storage"""
        # Arrange
        entity1 = {
            'PartitionKey': 'decisions',
            'RowKey': 'decision-001',
            'Status': 'pending'
        }
        entity2 = {
            'PartitionKey': 'decisions',
            'RowKey': 'decision-001',
            'Status': 'approved'
        }
        
        # Act
        mock_table_storage.create_entity(entity1)
        mock_table_storage.upsert_entity(entity2)
        
        # Assert
        retrieved = mock_table_storage.get_entity('decisions', 'decision-001')
        assert retrieved['Status'] == 'approved'
    
    def test_mock_table_query_entities(self, mock_table_storage):
        """Test querying entities in mock table storage"""
        # Arrange
        entities = [
            {'PartitionKey': 'decisions', 'RowKey': f'decision-{i:03d}', 'Status': 'pending'}
            for i in range(5)
        ]
        for entity in entities:
            mock_table_storage.create_entity(entity)
        
        # Act
        results = mock_table_storage.query_entities("PartitionKey eq 'decisions'")
        
        # Assert
        assert len(results) == 5
    
    def test_mock_table_list_entities(self, mock_table_storage):
        """Test listing all entities in mock table storage"""
        # Arrange
        for i in range(3):
            mock_table_storage.create_entity({
                'PartitionKey': f'partition-{i}',
                'RowKey': f'row-{i}',
                'Data': f'data-{i}'
            })
        
        # Act
        all_entities = mock_table_storage.list_entities()
        
        # Assert
        assert len(all_entities) == 3
