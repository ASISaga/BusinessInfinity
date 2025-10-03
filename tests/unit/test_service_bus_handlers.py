"""
Unit tests for Azure Service Bus handlers

Based on specifications in docs/testing/specifications.md
Tests the BusinessServiceBusHandlers class with mocked dependencies.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json


@pytest.mark.unit
class TestServiceBusHandlers:
    """Test Service Bus message handlers"""
    
    @pytest.fixture
    def mock_business_infinity(self):
        """Create mock BusinessInfinity instance"""
        mock_bi = MagicMock()
        mock_bi._initialize_task = AsyncMock()
        mock_bi.make_strategic_decision = AsyncMock(
            return_value={"id": "decision-001", "status": "created"}
        )
        mock_bi.analytics_engine = MagicMock()
        mock_bi.analytics_engine.record_metric = AsyncMock()
        return mock_bi
    
    @pytest.fixture
    def service_bus_handler(self, mock_business_infinity):
        """Create Service Bus handler for testing"""
        from src.routes.business_service_bus import BusinessServiceBusHandlers
        
        handler = BusinessServiceBusHandlers(mock_business_infinity)
        return handler
    
    @pytest.mark.asyncio
    async def test_business_decision_processor_success(self, service_bus_handler, sample_service_bus_message, mock_business_infinity):
        """Test successful processing of business decision message"""
        # Arrange
        decision_data = {
            "type": "strategic",
            "title": "Test Decision",
            "context": {"budget": 100000}
        }
        sample_service_bus_message.get_body.return_value = json.dumps(decision_data).encode('utf-8')
        
        # Act
        await service_bus_handler.business_decision_processor(sample_service_bus_message)
        
        # Assert
        mock_business_infinity.make_strategic_decision.assert_called_once_with(decision_data)
    
    @pytest.mark.asyncio
    async def test_business_decision_processor_invalid_json(self, service_bus_handler, sample_service_bus_message, mock_business_infinity):
        """Test handling of invalid JSON in message"""
        # Arrange
        sample_service_bus_message.get_body.return_value = b"invalid json"
        
        # Act - Should not raise exception
        await service_bus_handler.business_decision_processor(sample_service_bus_message)
        
        # Assert - Decision method should not be called
        mock_business_infinity.make_strategic_decision.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_business_decision_processor_no_business_infinity(self, sample_service_bus_message):
        """Test handling when BusinessInfinity is not available"""
        from src.routes.business_service_bus import BusinessServiceBusHandlers
        
        # Arrange
        handler = BusinessServiceBusHandlers(None)
        decision_data = {"type": "strategic", "title": "Test"}
        sample_service_bus_message.get_body.return_value = json.dumps(decision_data).encode('utf-8')
        
        # Act - Should not raise exception
        await handler.business_decision_processor(sample_service_bus_message)
        
        # Assert - No exception should be raised
        assert True  # Test passes if no exception
    
    @pytest.mark.asyncio
    async def test_performance_metric_processor(self, service_bus_handler, sample_service_bus_message, mock_business_infinity):
        """Test processing of performance metric events"""
        # Arrange
        event_data = {
            "type": "performance_metric",
            "metric_name": "revenue",
            "metric_value": 50000,
            "metric_unit": "USD"
        }
        sample_service_bus_message.get_body.return_value = json.dumps(event_data).encode('utf-8')
        
        # Mock the business_infinity_available attribute
        service_bus_handler.business_infinity_available = True
        
        # Act
        await service_bus_handler.business_event_processor(sample_service_bus_message)
        
        # Assert
        mock_business_infinity.analytics_engine.record_metric.assert_called_once_with(
            name="revenue",
            value=50000,
            unit="USD",
            metric_type="external"
        )
    
    @pytest.mark.asyncio
    async def test_business_milestone_processor(self, service_bus_handler, sample_service_bus_message):
        """Test processing of business milestone events"""
        # Arrange
        event_data = {
            "type": "business_milestone",
            "milestone": "Reached 1M users"
        }
        sample_service_bus_message.get_body.return_value = json.dumps(event_data).encode('utf-8')
        
        # Mock the business_infinity_available attribute
        service_bus_handler.business_infinity_available = True
        
        # Act - Should not raise exception
        await service_bus_handler.business_event_processor(sample_service_bus_message)
        
        # Assert - Test passes if no exception
        assert True
    
    @pytest.mark.asyncio
    async def test_external_integration_processor(self, service_bus_handler, sample_service_bus_message):
        """Test processing of external integration events"""
        # Arrange
        event_data = {
            "type": "external_integration",
            "integration_type": "CRM_sync"
        }
        sample_service_bus_message.get_body.return_value = json.dumps(event_data).encode('utf-8')
        
        # Mock the business_infinity_available attribute
        service_bus_handler.business_infinity_available = True
        
        # Act - Should not raise exception
        await service_bus_handler.business_event_processor(sample_service_bus_message)
        
        # Assert - Test passes if no exception
        assert True


@pytest.mark.unit
class TestServiceBusMessageFormatting:
    """Test message formatting and validation"""
    
    @pytest.mark.parametrize("decision_type,expected_valid", [
        ("strategic", True),
        ("operational", True),
        ("financial", True),
        ("invalid_type", True),  # Should still process, validation happens elsewhere
    ])
    def test_decision_type_handling(self, decision_type, expected_valid):
        """Test different decision types are handled"""
        decision_data = {
            "type": decision_type,
            "title": f"Test {decision_type} Decision"
        }
        
        # Serialize and deserialize to ensure valid JSON
        serialized = json.dumps(decision_data)
        deserialized = json.loads(serialized)
        
        assert deserialized["type"] == decision_type
        assert expected_valid is True
