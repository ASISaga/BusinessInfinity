# BusinessInfinity Testing Specifications

## Overview

This document provides comprehensive testing specifications and best practices for the BusinessInfinity Azure Functions application. It covers unit testing, integration testing, and end-to-end testing patterns specifically designed for Azure Functions with Python, including Azure Service Bus, Azure Machine Learning, and Azure Table Storage integrations.

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Test Environment Setup](#test-environment-setup)
3. [Unit Testing Best Practices](#unit-testing-best-practices)
4. [Integration Testing Best Practices](#integration-testing-best-practices)
5. [Azure Service Bus Testing](#azure-service-bus-testing)
6. [Azure Table Storage Testing](#azure-table-storage-testing)
7. [Azure Machine Learning Testing](#azure-machine-learning-testing)
8. [Azure Functions Testing](#azure-functions-testing)
9. [Async Testing Patterns](#async-testing-patterns)
10. [Mocking and Fixtures](#mocking-and-fixtures)
11. [Test Organization](#test-organization)
12. [Continuous Integration](#continuous-integration)

---

## Testing Philosophy

### Core Principles

1. **Test Isolation**: Each test should be independent and not rely on external state
2. **Fast Feedback**: Unit tests should run quickly; integration tests can take longer
3. **Realistic Testing**: Integration tests should use Azure emulators or test instances
4. **Comprehensive Coverage**: Aim for >80% code coverage with meaningful tests
5. **Clear Test Names**: Test names should describe what they test and expected behavior
6. **Arrange-Act-Assert**: Follow the AAA pattern for test structure

### Test Categories

- **Unit Tests**: Test individual functions/methods in isolation
- **Integration Tests**: Test interactions between components and Azure services
- **End-to-End Tests**: Test complete workflows through the API
- **Performance Tests**: Validate performance requirements
- **Security Tests**: Verify authentication, authorization, and data protection

---

## Test Environment Setup

### Required Dependencies

Add the following to your `pyproject.toml` or `requirements-dev.txt`:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.0",
    "pytest-timeout>=2.1.0",
    "pytest-xdist>=3.3.0",  # Parallel test execution
    "faker>=19.0.0",  # Generate test data
    "freezegun>=1.2.0",  # Mock datetime
    "responses>=0.23.0",  # Mock HTTP requests
    "azure-devtools>=1.2.0",  # Azure testing utilities
]
```

### pytest Configuration

Create or update `pyproject.toml` with pytest configuration:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-ra",  # Show summary of all test results
    "--strict-markers",  # Strict marker checking
    "--cov=business_infinity",  # Coverage for business_infinity package
    "--cov=src",  # Coverage for src package
    "--cov-report=term-missing",  # Show missing lines in terminal
    "--cov-report=html:htmlcov",  # Generate HTML coverage report
    "--cov-report=xml",  # Generate XML for CI
    "--tb=short",  # Shorter traceback format
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow running tests",
    "azure: Tests that require Azure services",
    "service_bus: Azure Service Bus specific tests",
    "table_storage: Azure Table Storage specific tests",
    "ml: Azure Machine Learning specific tests",
]
```

### Environment Variables for Testing

Create a `.env.test` file for test environment variables:

```bash
# Azure Service Bus
AZURE_SERVICE_BUS_CONNECTION_STRING=Endpoint=sb://test.servicebus.windows.net/...
BUSINESS_DECISIONS_QUEUE=test-business-decisions
BUSINESS_EVENTS_TOPIC=test-business-events

# Azure Table Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=test...
BOARDROOM_TABLE_NAME=TestBoardroomDecisions
METRICS_TABLE_NAME=TestBusinessMetrics

# Azure Machine Learning (if applicable)
AZURE_ML_WORKSPACE_NAME=test-workspace
AZURE_ML_RESOURCE_GROUP=test-rg
AZURE_ML_SUBSCRIPTION_ID=test-sub-id

# Test-specific settings
TESTING=true
LOG_LEVEL=DEBUG
```

### Test Fixtures Setup

Create `tests/conftest.py` for shared fixtures:

```python
"""
Shared pytest fixtures for BusinessInfinity tests
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
        'AZURE_SERVICE_BUS_CONNECTION_STRING': 'test-connection-string',
        'AZURE_STORAGE_CONNECTION_STRING': 'test-storage-connection',
        'BUSINESS_DECISIONS_QUEUE': 'test-decisions',
        'BUSINESS_EVENTS_TOPIC': 'test-events',
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
```

---

## Unit Testing Best Practices

### Structure of a Good Unit Test

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestBusinessManager:
    """Test suite for BusinessManager class"""
    
    @pytest.fixture
    def business_manager(self, mock_env_vars):
        """Create BusinessManager instance for testing"""
        from business_infinity.core.business_manager import BusinessManager
        return BusinessManager()
    
    @pytest.mark.unit
    async def test_initialize_business_manager_success(self, business_manager):
        """Test successful initialization of business manager"""
        # Arrange
        expected_status = "initialized"
        
        # Act
        result = await business_manager.initialize()
        
        # Assert
        assert result.status == expected_status
        assert business_manager.is_initialized is True
    
    @pytest.mark.unit
    async def test_initialize_business_manager_failure(self, business_manager):
        """Test business manager initialization handles errors gracefully"""
        # Arrange
        with patch.object(business_manager, '_load_config', side_effect=Exception("Config error")):
            
            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await business_manager.initialize()
            
            assert "Config error" in str(exc_info.value)
```

### Testing Pure Functions

```python
@pytest.mark.unit
def test_calculate_business_metrics():
    """Test business metrics calculation"""
    # Arrange
    from business_infinity.utils.metrics import calculate_roi
    
    investment = 100000
    revenue = 150000
    
    # Act
    roi = calculate_roi(investment, revenue)
    
    # Assert
    assert roi == 0.5  # 50% return
    assert isinstance(roi, float)


@pytest.mark.unit
@pytest.mark.parametrize("investment,revenue,expected_roi", [
    (100000, 150000, 0.5),
    (50000, 75000, 0.5),
    (100000, 100000, 0.0),
    (100000, 50000, -0.5),
])
def test_calculate_roi_various_inputs(investment, revenue, expected_roi):
    """Test ROI calculation with various inputs"""
    from business_infinity.utils.metrics import calculate_roi
    
    roi = calculate_roi(investment, revenue)
    
    assert roi == expected_roi
```

### Testing Classes with Dependencies

```python
@pytest.mark.unit
class TestDecisionEngine:
    """Test DecisionEngine with mocked dependencies"""
    
    @pytest.fixture
    def mock_storage(self):
        """Mock storage manager"""
        storage = MagicMock()
        storage.store_decision = AsyncMock(return_value=True)
        storage.get_decision = AsyncMock(return_value={"id": "test"})
        return storage
    
    @pytest.fixture
    def mock_service_bus(self):
        """Mock service bus client"""
        service_bus = MagicMock()
        service_bus.send_message = AsyncMock()
        return service_bus
    
    @pytest.fixture
    def decision_engine(self, mock_storage, mock_service_bus):
        """Create DecisionEngine with mocked dependencies"""
        from business_infinity.core.decision_engine import DecisionEngine
        
        engine = DecisionEngine()
        engine.storage = mock_storage
        engine.service_bus = mock_service_bus
        return engine
    
    @pytest.mark.unit
    async def test_create_decision(self, decision_engine, mock_storage, sample_business_decision):
        """Test creating a new business decision"""
        # Act
        result = await decision_engine.create_decision(sample_business_decision)
        
        # Assert
        assert result is not None
        mock_storage.store_decision.assert_called_once()
        assert mock_storage.store_decision.call_args[0][0]['decision_id'] == sample_business_decision['decision_id']
```

---

## Integration Testing Best Practices

### Testing with Azure Storage Emulator

```python
import pytest
from azure.data.tables import TableServiceClient
import os


@pytest.mark.integration
@pytest.mark.azure
class TestTableStorageIntegration:
    """Integration tests for Azure Table Storage"""
    
    @pytest.fixture(scope="class")
    def table_service_client(self):
        """Create TableServiceClient for testing"""
        connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        
        if not connection_string:
            pytest.skip("Azure Storage connection string not configured")
        
        client = TableServiceClient.from_connection_string(connection_string)
        yield client
    
    @pytest.fixture
    def test_table(self, table_service_client):
        """Create and cleanup test table"""
        table_name = "TestBusinessDecisions"
        
        # Create table
        table_client = table_service_client.create_table_if_not_exists(table_name)
        
        yield table_client
        
        # Cleanup - delete table after test
        try:
            table_service_client.delete_table(table_name)
        except Exception as e:
            print(f"Cleanup warning: {e}")
    
    @pytest.mark.integration
    async def test_store_and_retrieve_decision(self, test_table, sample_business_decision):
        """Test storing and retrieving a decision from Table Storage"""
        # Arrange
        entity = {
            'PartitionKey': 'decisions',
            'RowKey': sample_business_decision['decision_id'],
            'Title': sample_business_decision['title'],
            'Status': sample_business_decision['status']
        }
        
        # Act - Store
        test_table.create_entity(entity)
        
        # Act - Retrieve
        retrieved = test_table.get_entity(
            partition_key='decisions',
            row_key=sample_business_decision['decision_id']
        )
        
        # Assert
        assert retrieved['RowKey'] == sample_business_decision['decision_id']
        assert retrieved['Title'] == sample_business_decision['title']
        assert retrieved['Status'] == sample_business_decision['status']
```

### End-to-End Workflow Testing

```python
@pytest.mark.integration
@pytest.mark.slow
class TestBusinessDecisionWorkflow:
    """End-to-end tests for business decision workflows"""
    
    @pytest.fixture
    async def business_infinity(self):
        """Initialize complete BusinessInfinity system"""
        from business_infinity import BusinessInfinity, BusinessInfinityConfig
        
        config = BusinessInfinityConfig()
        bi = BusinessInfinity(config)
        await bi.initialize()
        
        yield bi
        
        # Cleanup
        await bi.cleanup()
    
    @pytest.mark.integration
    async def test_complete_decision_workflow(self, business_infinity, sample_business_decision):
        """Test complete decision creation, voting, and execution workflow"""
        # Act - Create decision
        decision_id = await business_infinity.create_strategic_decision(
            title=sample_business_decision['title'],
            context=sample_business_decision['context']
        )
        
        assert decision_id is not None
        
        # Act - Get decision status
        decision = await business_infinity.get_decision(decision_id)
        assert decision['status'] == 'pending'
        
        # Act - Simulate votes from agents
        votes = ['ceo', 'cfo', 'cto']
        for agent in votes:
            vote_result = await business_infinity.cast_vote(
                decision_id=decision_id,
                agent_role=agent,
                vote='approve'
            )
            assert vote_result['success'] is True
        
        # Act - Check if decision is approved
        final_decision = await business_infinity.get_decision(decision_id)
        assert final_decision['status'] == 'approved'
```

---

## Azure Service Bus Testing

### Unit Testing Service Bus Handlers

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json


@pytest.mark.unit
class TestServiceBusHandlers:
    """Test Service Bus message handlers"""
    
    @pytest.fixture
    def service_bus_handler(self):
        """Create Service Bus handler for testing"""
        from src.routes.business_service_bus import BusinessServiceBusHandlers
        
        mock_business_infinity = MagicMock()
        mock_business_infinity._initialize_task = AsyncMock()
        mock_business_infinity.make_strategic_decision = AsyncMock(
            return_value={"id": "decision-001", "status": "created"}
        )
        
        handler = BusinessServiceBusHandlers(mock_business_infinity)
        return handler
    
    @pytest.mark.unit
    async def test_business_decision_processor_success(self, service_bus_handler, sample_service_bus_message):
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
        service_bus_handler.business_infinity.make_strategic_decision.assert_called_once_with(decision_data)
    
    @pytest.mark.unit
    async def test_business_decision_processor_invalid_json(self, service_bus_handler, sample_service_bus_message):
        """Test handling of invalid JSON in message"""
        # Arrange
        sample_service_bus_message.get_body.return_value = b"invalid json"
        
        # Act - Should not raise exception
        await service_bus_handler.business_decision_processor(sample_service_bus_message)
        
        # Assert - Decision method should not be called
        service_bus_handler.business_infinity.make_strategic_decision.assert_not_called()
```

### Integration Testing with Service Bus

```python
@pytest.mark.integration
@pytest.mark.service_bus
class TestServiceBusIntegration:
    """Integration tests for Azure Service Bus"""
    
    @pytest.fixture
    async def service_bus_client(self):
        """Create Service Bus client for testing"""
        from azure.servicebus.aio import ServiceBusClient
        
        connection_string = os.getenv('AZURE_SERVICE_BUS_CONNECTION_STRING')
        if not connection_string:
            pytest.skip("Service Bus connection string not configured")
        
        async with ServiceBusClient.from_connection_string(connection_string) as client:
            yield client
    
    @pytest.mark.integration
    async def test_send_and_receive_decision_message(self, service_bus_client):
        """Test sending and receiving messages from Service Bus queue"""
        queue_name = os.getenv('BUSINESS_DECISIONS_QUEUE', 'test-business-decisions')
        
        # Arrange
        test_message = {
            "type": "strategic",
            "title": "Integration Test Decision",
            "context": {"test": True}
        }
        
        # Act - Send message
        async with service_bus_client.get_queue_sender(queue_name) as sender:
            from azure.servicebus import ServiceBusMessage
            message = ServiceBusMessage(json.dumps(test_message))
            await sender.send_messages(message)
        
        # Act - Receive message
        async with service_bus_client.get_queue_receiver(queue_name) as receiver:
            messages = await receiver.receive_messages(max_wait_time=5)
            
            # Assert
            assert len(messages) > 0
            received_data = json.loads(str(messages[0]))
            assert received_data['title'] == test_message['title']
            
            # Complete message
            await receiver.complete_message(messages[0])
```

### Testing Service Bus Triggers in Azure Functions

```python
@pytest.mark.unit
class TestServiceBusTriggers:
    """Test Azure Functions Service Bus triggers"""
    
    @pytest.mark.unit
    async def test_business_decision_processor_trigger(self, sample_service_bus_message):
        """Test Service Bus queue trigger for business decisions"""
        # Arrange
        from src.function_app import business_service_bus_handlers
        
        decision_data = {
            "type": "strategic",
            "title": "Trigger Test",
            "context": {}
        }
        sample_service_bus_message.get_body.return_value = json.dumps(decision_data).encode('utf-8')
        
        # Mock the business infinity instance
        with patch.object(business_service_bus_handlers, 'business_infinity') as mock_bi:
            mock_bi._initialize_task = AsyncMock()
            mock_bi.make_strategic_decision = AsyncMock(return_value={"id": "test"})
            
            # Act
            await business_service_bus_handlers.business_decision_processor(sample_service_bus_message)
            
            # Assert
            mock_bi.make_strategic_decision.assert_called_once()
```

### Mock Service Bus Client

```python
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
```

---

## Azure Table Storage Testing

### Unit Testing Table Storage Operations

```python
@pytest.mark.unit
class TestStorageManager:
    """Unit tests for Storage Manager"""
    
    @pytest.fixture
    def mock_table_client(self):
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
    def storage_manager(self, mock_table_client):
        """Create StorageManager with mocked table client"""
        from src.core.features.storage import UnifiedStorageManager
        
        manager = UnifiedStorageManager()
        manager.get_table_client = MagicMock(return_value=mock_table_client)
        return manager
    
    @pytest.mark.unit
    async def test_store_boardroom_decision(self, storage_manager, mock_table_client, sample_business_decision):
        """Test storing a boardroom decision"""
        # Act
        result = await storage_manager.store_boardroom_decision(sample_business_decision)
        
        # Assert
        assert result is True
        mock_table_client.create_entity.assert_called_once()
        
        # Verify the entity has required fields
        call_args = mock_table_client.create_entity.call_args[0][0]
        assert 'timestamp' in call_args
        assert 'source' in call_args
        assert call_args['source'] == 'business_infinity_boardroom'
```

### Integration Testing with Real Table Storage

```python
@pytest.mark.integration
@pytest.mark.table_storage
class TestTableStorageOperations:
    """Integration tests for Table Storage operations"""
    
    @pytest.fixture
    async def storage_manager(self):
        """Create real storage manager for integration tests"""
        from src.core.features.storage import UnifiedStorageManager
        
        # Ensure we're using test connection string
        connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if not connection_string:
            pytest.skip("Azure Storage connection string not configured")
        
        manager = UnifiedStorageManager()
        yield manager
    
    @pytest.mark.integration
    async def test_store_and_retrieve_boardroom_decision(self, storage_manager, sample_business_decision):
        """Test complete workflow of storing and retrieving decision"""
        # Act - Store
        store_result = await storage_manager.store_boardroom_decision(sample_business_decision)
        assert store_result is True
        
        # Act - Retrieve
        history = await storage_manager.get_boardroom_history(limit=10)
        
        # Assert
        assert len(history) > 0
        found = any(d.get('decision_id') == sample_business_decision['decision_id'] for d in history)
        assert found is True
```

### Testing Batch Operations

```python
@pytest.mark.integration
@pytest.mark.table_storage
class TestBatchTableOperations:
    """Test batch operations with Table Storage"""
    
    @pytest.mark.integration
    async def test_batch_insert_decisions(self, test_table):
        """Test inserting multiple decisions in batch"""
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
        from azure.data.tables import TableTransactionError
        try:
            for decision in decisions:
                test_table.create_entity(decision)
            
            # Verify
            entities = list(test_table.query_entities("PartitionKey eq 'decisions'"))
            assert len(entities) >= 10
            
        except TableTransactionError as e:
            pytest.fail(f"Batch operation failed: {e}")
```

### Mock Table Storage Client

```python
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
```

---

## Azure Machine Learning Testing

### Unit Testing ML Model Integration

```python
@pytest.mark.unit
class TestMLModelIntegration:
    """Test Machine Learning model integration"""
    
    @pytest.fixture
    def mock_ml_client(self):
        """Mock Azure ML client"""
        client = MagicMock()
        client.models.get = MagicMock(return_value=MagicMock(name="test-model", version="1"))
        client.online_endpoints.invoke = MagicMock(return_value={"predictions": [0.85]})
        return client
    
    @pytest.fixture
    def ml_service(self, mock_ml_client):
        """Create ML service with mocked client"""
        from business_infinity.ml.predictor import MLPredictor
        
        predictor = MLPredictor()
        predictor.ml_client = mock_ml_client
        return predictor
    
    @pytest.mark.unit
    async def test_predict_decision_outcome(self, ml_service, sample_business_decision):
        """Test ML prediction for decision outcome"""
        # Act
        prediction = await ml_service.predict_outcome(sample_business_decision)
        
        # Assert
        assert prediction is not None
        assert 'confidence' in prediction
        assert 0 <= prediction['confidence'] <= 1
```

### Integration Testing with Azure ML

```python
@pytest.mark.integration
@pytest.mark.ml
@pytest.mark.slow
class TestAzureMLIntegration:
    """Integration tests for Azure Machine Learning"""
    
    @pytest.fixture
    def ml_workspace(self):
        """Connect to Azure ML workspace"""
        from azure.ai.ml import MLClient
        from azure.identity import DefaultAzureCredential
        
        subscription_id = os.getenv('AZURE_ML_SUBSCRIPTION_ID')
        resource_group = os.getenv('AZURE_ML_RESOURCE_GROUP')
        workspace_name = os.getenv('AZURE_ML_WORKSPACE_NAME')
        
        if not all([subscription_id, resource_group, workspace_name]):
            pytest.skip("Azure ML configuration not complete")
        
        client = MLClient(
            DefaultAzureCredential(),
            subscription_id,
            resource_group,
            workspace_name
        )
        yield client
    
    @pytest.mark.integration
    def test_list_ml_models(self, ml_workspace):
        """Test retrieving ML models from workspace"""
        # Act
        models = list(ml_workspace.models.list())
        
        # Assert
        assert models is not None
        # Verify expected model exists
        model_names = [m.name for m in models]
        assert any('decision' in name.lower() for name in model_names)
```

### Testing Model Inference

```python
@pytest.mark.integration
@pytest.mark.ml
class TestModelInference:
    """Test ML model inference"""
    
    @pytest.mark.integration
    async def test_model_endpoint_inference(self, ml_workspace):
        """Test calling ML endpoint for inference"""
        # Arrange
        endpoint_name = "business-decision-predictor"
        test_data = {
            "data": [{
                "budget": 100000,
                "timeline": 90,
                "risk_level": "medium",
                "department": "engineering"
            }]
        }
        
        # Act
        try:
            from azure.ai.ml.entities import OnlineEndpoint
            endpoint = ml_workspace.online_endpoints.get(endpoint_name)
            
            # Call endpoint
            response = ml_workspace.online_endpoints.invoke(
                endpoint_name=endpoint_name,
                request_file=None,
                request=test_data
            )
            
            # Assert
            assert response is not None
            assert 'predictions' in response or 'results' in response
            
        except Exception as e:
            pytest.skip(f"ML endpoint not available: {e}")
```

---

## Azure Functions Testing

### Unit Testing HTTP Triggers

```python
@pytest.mark.unit
class TestHTTPTriggers:
    """Test Azure Functions HTTP triggers"""
    
    @pytest.fixture
    def mock_http_request(self):
        """Create mock HTTP request"""
        import azure.functions as func
        
        request = MagicMock(spec=func.HttpRequest)
        request.method = "POST"
        request.url = "http://localhost:7071/api/business/decisions"
        request.params = {}
        request.headers = {"Content-Type": "application/json"}
        request.get_json.return_value = {
            "title": "Test Decision",
            "context": {"test": True}
        }
        return request
    
    @pytest.mark.unit
    async def test_health_endpoint(self):
        """Test health check endpoint"""
        from src.function_app import health
        import azure.functions as func
        
        # Arrange
        request = MagicMock(spec=func.HttpRequest)
        request.method = "GET"
        
        # Act
        response = await health(request)
        
        # Assert
        assert response.status_code == 200
        body = json.loads(response.get_body())
        assert body['status'] == 'healthy'
    
    @pytest.mark.unit
    async def test_create_decision_endpoint(self, mock_http_request):
        """Test decision creation endpoint"""
        from src.function_app import make_strategic_decision
        
        # Act
        response = await make_strategic_decision(mock_http_request)
        
        # Assert
        assert response.status_code in [200, 201, 202]
        body = json.loads(response.get_body())
        assert 'decision_id' in body or 'id' in body
```

### Testing HTTP Request Validation

```python
@pytest.mark.unit
class TestRequestValidation:
    """Test HTTP request validation"""
    
    @pytest.mark.unit
    async def test_missing_required_fields(self):
        """Test validation of required fields in request"""
        import azure.functions as func
        from src.function_app import make_strategic_decision
        
        # Arrange - Request missing required field
        request = MagicMock(spec=func.HttpRequest)
        request.get_json.return_value = {
            "context": {"test": True}
            # Missing 'title' field
        }
        
        # Act
        response = await make_strategic_decision(request)
        
        # Assert
        assert response.status_code == 400
        body = json.loads(response.get_body())
        assert 'error' in body
    
    @pytest.mark.unit
    @pytest.mark.parametrize("invalid_data", [
        {},  # Empty object
        {"title": ""},  # Empty title
        {"title": None},  # Null title
        {"title": "Test", "context": "not-a-dict"},  # Invalid context type
    ])
    async def test_invalid_request_data(self, invalid_data):
        """Test handling of various invalid request data"""
        import azure.functions as func
        from src.function_app import make_strategic_decision
        
        # Arrange
        request = MagicMock(spec=func.HttpRequest)
        request.get_json.return_value = invalid_data
        
        # Act
        response = await make_strategic_decision(request)
        
        # Assert
        assert response.status_code in [400, 422]
```

### Integration Testing HTTP Endpoints

```python
@pytest.mark.integration
class TestHTTPEndpointsIntegration:
    """Integration tests for HTTP endpoints"""
    
    @pytest.fixture
    def function_app_url(self):
        """Get Function App URL for testing"""
        url = os.getenv('FUNCTION_APP_URL', 'http://localhost:7071')
        return url
    
    @pytest.mark.integration
    async def test_end_to_end_decision_creation(self, function_app_url):
        """Test complete decision creation through HTTP endpoint"""
        import httpx
        
        # Arrange
        endpoint = f"{function_app_url}/api/business/decisions"
        payload = {
            "title": "Integration Test Decision",
            "context": {
                "department": "engineering",
                "budget": 50000,
                "timeline": "Q1 2024"
            }
        }
        
        # Act
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
        
        # Assert
        assert response.status_code in [200, 201, 202]
        data = response.json()
        assert 'decision_id' in data or 'id' in data
```

---

## Async Testing Patterns

### Basic Async Test Structure

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async function"""
    from business_infinity.core.async_operations import fetch_data
    
    # Act
    result = await fetch_data("test-id")
    
    # Assert
    assert result is not None


@pytest.mark.asyncio
async def test_async_with_timeout():
    """Test async function with timeout"""
    import asyncio
    from business_infinity.core.async_operations import long_running_task
    
    # Act & Assert
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(long_running_task(), timeout=1.0)
```

### Testing Concurrent Operations

```python
@pytest.mark.asyncio
async def test_concurrent_decision_processing():
    """Test processing multiple decisions concurrently"""
    import asyncio
    from business_infinity.core.decision_engine import DecisionEngine
    
    # Arrange
    engine = DecisionEngine()
    decisions = [
        {"title": f"Decision {i}", "context": {}}
        for i in range(5)
    ]
    
    # Act
    tasks = [engine.process_decision(d) for d in decisions]
    results = await asyncio.gather(*tasks)
    
    # Assert
    assert len(results) == 5
    assert all(r['status'] == 'processed' for r in results)
```

### Testing Async Context Managers

```python
@pytest.mark.asyncio
async def test_async_context_manager():
    """Test async context manager"""
    from business_infinity.core.connections import DatabaseConnection
    
    # Act
    async with DatabaseConnection() as conn:
        # Assert - Connection is open
        assert conn.is_connected is True
        
        # Perform operations
        result = await conn.query("SELECT * FROM decisions")
        assert result is not None
    
    # Assert - Connection is closed after context
    assert conn.is_connected is False
```

### Testing Async Generators

```python
@pytest.mark.asyncio
async def test_async_generator():
    """Test async generator"""
    from business_infinity.core.streams import stream_decisions
    
    # Act
    decisions = []
    async for decision in stream_decisions(limit=5):
        decisions.append(decision)
    
    # Assert
    assert len(decisions) == 5
```

### Mocking Async Functions

```python
@pytest.mark.asyncio
async def test_with_mocked_async_function():
    """Test with mocked async function"""
    from unittest.mock import AsyncMock
    from business_infinity.core.external_api import ExternalAPIClient
    
    # Arrange
    client = ExternalAPIClient()
    client.fetch_data = AsyncMock(return_value={"status": "success"})
    
    # Act
    result = await client.fetch_data("test-id")
    
    # Assert
    assert result['status'] == "success"
    client.fetch_data.assert_called_once_with("test-id")
```

---

## Mocking and Fixtures

### Common Fixture Patterns

```python
# tests/conftest.py

@pytest.fixture
def temp_directory():
    """Create temporary directory for tests"""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
async def initialized_business_infinity():
    """Fully initialized BusinessInfinity instance"""
    from business_infinity import BusinessInfinity, BusinessInfinityConfig
    
    config = BusinessInfinityConfig()
    bi = BusinessInfinity(config)
    await bi.initialize()
    
    yield bi
    
    # Cleanup
    await bi.cleanup()


@pytest.fixture(scope="session")
def test_data_loader():
    """Load test data from fixtures"""
    import json
    from pathlib import Path
    
    def load(filename):
        path = Path(__file__).parent / "fixtures" / filename
        with open(path) as f:
            return json.load(f)
    
    return load
```

### Mocking External Services

```python
@pytest.fixture
def mock_azure_services():
    """Mock all Azure service clients"""
    with patch('azure.servicebus.ServiceBusClient') as mock_sb, \
         patch('azure.data.tables.TableServiceClient') as mock_table, \
         patch('azure.storage.blob.BlobServiceClient') as mock_blob:
        
        # Configure Service Bus mock
        mock_sb_instance = MagicMock()
        mock_sb.from_connection_string.return_value = mock_sb_instance
        
        # Configure Table Storage mock
        mock_table_instance = MagicMock()
        mock_table.from_connection_string.return_value = mock_table_instance
        
        # Configure Blob Storage mock
        mock_blob_instance = MagicMock()
        mock_blob.from_connection_string.return_value = mock_blob_instance
        
        yield {
            'service_bus': mock_sb_instance,
            'table_storage': mock_table_instance,
            'blob_storage': mock_blob_instance
        }
```

### Parameterized Fixtures

```python
@pytest.fixture(params=['ceo', 'cfo', 'cto', 'cmo'])
def agent_role(request):
    """Parameterized fixture for different agent roles"""
    return request.param


@pytest.mark.unit
def test_agent_specific_logic(agent_role):
    """Test logic for each agent role"""
    from business_infinity.agents import get_agent
    
    agent = get_agent(agent_role)
    assert agent.role == agent_role
```

### Dynamic Fixture Creation

```python
def create_decision_fixture(decision_type):
    """Factory function to create decision fixtures"""
    @pytest.fixture
    def fixture():
        return {
            "type": decision_type,
            "title": f"Test {decision_type} Decision",
            "context": {"type": decision_type}
        }
    return fixture


# Create specific fixtures
strategic_decision = create_decision_fixture("strategic")
operational_decision = create_decision_fixture("operational")
financial_decision = create_decision_fixture("financial")
```

---

## Test Organization

### Directory Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── unit/                       # Unit tests
│   ├── test_business_manager.py
│   ├── test_decision_engine.py
│   ├── test_agents.py
│   └── test_utils.py
├── integration/                # Integration tests
│   ├── test_azure_services.py
│   ├── test_service_bus.py
│   ├── test_table_storage.py
│   └── test_workflows.py
├── e2e/                        # End-to-end tests
│   ├── test_decision_workflow.py
│   └── test_agent_collaboration.py
├── fixtures/                   # Test data fixtures
│   ├── decisions.json
│   ├── agents.json
│   └── metrics.json
└── performance/                # Performance tests
    └── test_load.py
```

### Test Naming Conventions

```python
# Good test names - descriptive and clear
def test_create_decision_with_valid_data_returns_decision_id()
def test_create_decision_with_missing_title_raises_validation_error()
def test_get_decision_with_invalid_id_returns_none()

# Test class organization
class TestDecisionEngine:
    """Tests for DecisionEngine class"""
    
    class TestDecisionCreation:
        """Tests for decision creation"""
        
        def test_valid_decision()
        def test_invalid_decision()
    
    class TestDecisionRetrieval:
        """Tests for decision retrieval"""
        
        def test_existing_decision()
        def test_nonexistent_decision()
```

### Test Markers

```python
# Mark tests by category
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.azure
@pytest.mark.service_bus
@pytest.mark.table_storage
@pytest.mark.ml

# Run specific test categories
# pytest -m unit          # Run only unit tests
# pytest -m "not slow"    # Skip slow tests
# pytest -m "azure and integration"  # Run Azure integration tests
```

---

## Continuous Integration

### GitHub Actions Workflow Example

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Run unit tests
      run: |
        pytest tests/unit -v --cov --cov-report=xml
    
    - name: Run integration tests
      env:
        AZURE_STORAGE_CONNECTION_STRING: ${{ secrets.TEST_STORAGE_CONNECTION }}
        AZURE_SERVICE_BUS_CONNECTION_STRING: ${{ secrets.TEST_SERVICEBUS_CONNECTION }}
      run: |
        pytest tests/integration -v -m "not slow"
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest tests/unit -v
        language: system
        pass_filenames: false
        always_run: true
```

---

## Best Practices Summary

### DO:

✅ Write tests before or alongside code (TDD)
✅ Keep tests simple and focused on one thing
✅ Use descriptive test names
✅ Mock external dependencies in unit tests
✅ Use real Azure services for integration tests (with cleanup)
✅ Test both success and failure cases
✅ Use fixtures for common test setup
✅ Test edge cases and boundary conditions
✅ Keep tests independent and isolated
✅ Use appropriate test markers for categorization

### DON'T:

❌ Test implementation details
❌ Share state between tests
❌ Use production Azure resources for testing
❌ Skip cleanup in integration tests
❌ Ignore slow or flaky tests
❌ Test third-party library functionality
❌ Write overly complex test logic
❌ Depend on test execution order
❌ Hardcode credentials in tests
❌ Mix unit and integration test concerns

---

## Example Test Suite

See the complete example test suite structure:

```python
# tests/test_business_infinity_complete.py
"""
Complete test suite demonstrating all testing patterns for BusinessInfinity
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import os


class TestBusinessInfinityComplete:
    """Comprehensive test suite for BusinessInfinity"""
    
    # Unit Tests
    @pytest.mark.unit
    async def test_initialization(self, mock_azure_services):
        """Test BusinessInfinity initialization"""
        from business_infinity import BusinessInfinity, BusinessInfinityConfig
        
        config = BusinessInfinityConfig()
        bi = BusinessInfinity(config)
        
        assert bi is not None
        assert bi.config == config
    
    # Integration Tests
    @pytest.mark.integration
    @pytest.mark.azure
    async def test_decision_workflow_integration(self, initialized_business_infinity):
        """Test complete decision workflow"""
        decision = await initialized_business_infinity.create_strategic_decision(
            title="Test Decision",
            context={"test": True}
        )
        
        assert decision is not None
        assert 'id' in decision
    
    # Service Bus Tests
    @pytest.mark.integration
    @pytest.mark.service_bus
    async def test_service_bus_integration(self, service_bus_client):
        """Test Service Bus message handling"""
        # Implementation here
        pass
    
    # Table Storage Tests
    @pytest.mark.integration
    @pytest.mark.table_storage
    async def test_table_storage_integration(self, test_table):
        """Test Table Storage operations"""
        # Implementation here
        pass
    
    # Async Tests
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent async operations"""
        import asyncio
        
        tasks = [self._dummy_async_task() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
    
    async def _dummy_async_task(self):
        """Dummy async task for testing"""
        await asyncio.sleep(0.1)
        return {"status": "completed"}
```

---

## Additional Resources

- [Azure Functions Python Developer Guide](https://docs.microsoft.com/azure/azure-functions/functions-reference-python)
- [pytest Documentation](https://docs.pytest.org/)
- [Azure SDK for Python Testing](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core#testing)
- [Async Testing with pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

---

*Last Updated: 2024-01-01*
*Version: 1.0*
