"""
Example test updates for the new AOS-based storage architecture

This shows how to update tests to work with the refactored BusinessInfinity
that now uses AgentOperatingSystem Azure services.
"""
import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch
import json


@pytest.mark.asyncio
@pytest.mark.integration
class TestBusinessInfinityAOSIntegration:
    """Tests for BusinessInfinity using AOS Azure services"""
    
    @patch('AgentOperatingSystem.orchestration.business_azure_services.BusinessAzureServices')
    async def test_store_boardroom_decision(self, mock_azure_services):
        """Test storing boardroom decision via AOS"""
        # Arrange
        from core.features.storage import UnifiedStorageManager
        
        mock_services_instance = AsyncMock()
        mock_azure_services.return_value = mock_services_instance
        mock_services_instance.store_boardroom_decision.return_value = {"success": True}
        
        storage_manager = UnifiedStorageManager()
        
        decision_data = {
            "decision_id": "test-001",
            "type": "strategic", 
            "title": "Test Decision"
        }
        
        # Act
        result = await storage_manager.store_boardroom_decision(decision_data)
        
        # Assert
        assert result is True
        mock_services_instance.store_boardroom_decision.assert_called_once_with(decision_data)
    
    @patch('AgentOperatingSystem.orchestration.business_azure_services.BusinessAzureServices')
    async def test_enqueue_request(self, mock_azure_services):
        """Test enqueuing request via AOS"""
        # Arrange  
        from core.features.storage import UnifiedStorageManager
        
        mock_services_instance = AsyncMock()
        mock_azure_services.return_value = mock_services_instance
        mock_services_instance.enqueue_request.return_value = {"success": True}
        
        storage_manager = UnifiedStorageManager()
        
        message = {"agent_id": "test", "action": "process"}
        
        # Act
        await storage_manager.enqueue_request(message)
        
        # Assert
        mock_services_instance.enqueue_request.assert_called_once_with(message)
    
    @patch('AgentOperatingSystem.orchestration.business_azure_services.BusinessAzureServices')
    async def test_get_boardroom_history(self, mock_azure_services):
        """Test getting boardroom history via AOS"""
        # Arrange
        from core.features.storage import UnifiedStorageManager
        
        mock_services_instance = AsyncMock()
        mock_azure_services.return_value = mock_services_instance
        mock_services_instance.get_boardroom_history.return_value = {
            "success": True,
            "decisions": [{"decision_id": "test-001", "title": "Test"}]
        }
        
        storage_manager = UnifiedStorageManager()
        
        # Act
        result = await storage_manager.get_boardroom_history(limit=50)
        
        # Assert
        assert len(result) == 1
        assert result[0]["decision_id"] == "test-001"
        mock_services_instance.get_boardroom_history.assert_called_once_with(50)
    
    @patch('AgentOperatingSystem.orchestration.business_azure_services.BusinessAzureServices')
    async def test_storage_validation(self, mock_azure_services):
        """Test storage configuration validation via AOS"""
        # Arrange
        from core.features.storage import UnifiedStorageManager
        
        mock_services_instance = AsyncMock()
        mock_azure_services.return_value = mock_services_instance
        mock_services_instance.validate_configuration.return_value = {
            "success": True,
            "azure_status": {"overall_health": "healthy"},
            "business_requirements": []
        }
        
        storage_manager = UnifiedStorageManager()
        
        # Act
        result = await storage_manager.validate_configuration()
        
        # Assert
        assert result["success"] is True
        assert result["azure_status"]["overall_health"] == "healthy"
        mock_services_instance.validate_configuration.assert_called_once()


@pytest.mark.asyncio  
@pytest.mark.unit
class TestAzureServicesMocking:
    """Examples of how to mock AOS Azure services for unit tests"""
    
    async def test_aos_azure_integration_mock(self):
        """Test mocking the core AOS Azure integration"""
        with patch('AgentOperatingSystem.orchestration.azure_integration.AzureIntegration') as mock_integration:
            mock_instance = AsyncMock()
            mock_integration.return_value = mock_instance
            
            # Configure mock responses
            mock_instance.upsert_entity.return_value = {"success": True}
            mock_instance.send_message.return_value = {"success": True}
            mock_instance.store_data.return_value = {"success": True}
            
            from AgentOperatingSystem.orchestration.business_azure_services import BusinessAzureServices
            
            # Test the business services wrapper
            business_services = BusinessAzureServices()
            
            decision_data = {"decision_id": "test", "title": "Test Decision"}
            result = await business_services.store_boardroom_decision(decision_data)
            
            assert result["success"] is True
            mock_instance.upsert_entity.assert_called()
    
    async def test_environment_configuration_mock(self):
        """Test mocking environment configuration for AOS"""
        env_vars = {
            'AZURE_STORAGE_CONNECTION_STRING': 'DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test;',
            'AZURE_SERVICE_BUS_CONNECTION_STRING': 'Endpoint=sb://test.servicebus.windows.net/;',
            'BOARDROOM_TABLE_NAME': 'TestBoardroomDecisions',
            'METRICS_TABLE_NAME': 'TestBusinessMetrics'
        }
        
        with patch.dict('os.environ', env_vars):
            with patch('AgentOperatingSystem.orchestration.azure_integration.AzureIntegration') as mock_integration:
                mock_instance = AsyncMock()
                mock_integration.return_value = mock_instance
                
                from AgentOperatingSystem.orchestration.business_azure_services import BusinessAzureServices
                
                business_services = BusinessAzureServices()
                
                # Verify configuration is picked up
                assert business_services.boardroom_table == "TestBoardroomDecisions"
                assert business_services.metrics_table == "TestBusinessMetrics"


# Integration test helper for real Azure services
@pytest.mark.integration
@pytest.mark.azure
class TestRealAzureIntegration:
    """Integration tests that can run against real Azure services"""
    
    @pytest.mark.skipif(
        not all([
            os.getenv('AZURE_STORAGE_CONNECTION_STRING'),
            os.getenv('AZURE_SERVICE_BUS_CONNECTION_STRING')
        ]),
        reason="Azure connection strings not configured"
    )
    async def test_real_azure_connection(self):
        """Test actual connection to Azure services (requires real config)"""
        from AgentOperatingSystem.orchestration.business_azure_services import BusinessAzureServices
        
        business_services = BusinessAzureServices()
        
        # Test health check
        health = await business_services.health_check()
        
        # Should connect successfully with real credentials
        assert "overall_health" in health
        print(f"Azure health check result: {health}")
    
    @pytest.mark.skipif(
        not os.getenv('AZURE_STORAGE_CONNECTION_STRING'),
        reason="Azure storage connection string not configured"  
    )
    async def test_real_table_operations(self):
        """Test actual table operations (requires real config)"""
        from AgentOperatingSystem.orchestration.business_azure_services import BusinessAzureServices
        
        business_services = BusinessAzureServices()
        
        # Use test table name
        business_services.configure_business_settings(
            boardroom_table="TestBoardroomDecisions"
        )
        
        # Test storing and retrieving decision
        test_decision = {
            "decision_id": f"integration-test-{os.urandom(4).hex()}",
            "type": "test",
            "title": "Integration Test Decision"
        }
        
        # Store decision
        store_result = await business_services.store_boardroom_decision(test_decision)
        assert store_result.get("success") is True
        
        # Retrieve decisions
        history_result = await business_services.get_boardroom_history(limit=10)
        assert history_result.get("success") is True
        
        decisions = history_result.get("decisions", [])
        test_decision_found = any(
            d.get("RowKey") == test_decision["decision_id"] 
            for d in decisions
        )
        assert test_decision_found, "Test decision should be found in history"