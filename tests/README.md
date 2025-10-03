# BusinessInfinity Test Suite

This directory contains the test suite for BusinessInfinity, following the comprehensive testing specifications documented in `docs/testing/specifications.md`.

## Test Organization

```
tests/
├── conftest.py                          # Shared fixtures and test configuration
├── unit/                                # Unit tests (fast, isolated)
│   ├── test_service_bus_handlers.py    # Service Bus handler unit tests
│   ├── test_storage_manager.py         # Storage Manager unit tests
│   └── test_azure_functions.py         # Azure Functions HTTP trigger tests
├── integration/                         # Integration tests (slower, require services)
│   └── test_azure_services.py          # Azure services integration tests
└── README.md                            # This file
```

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run Azure-specific tests
pytest -m azure

# Run Service Bus tests
pytest -m service_bus

# Run Table Storage tests
pytest -m table_storage
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=src --cov=business_infinity --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run Specific Test Files

```bash
# Run Service Bus handler tests
pytest tests/unit/test_service_bus_handlers.py -v

# Run Storage Manager tests
pytest tests/unit/test_storage_manager.py -v

# Run integration tests
pytest tests/integration/test_azure_services.py -v
```

### Run Tests in Parallel

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

## Test Markers

The test suite uses the following pytest markers:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (require services)
- `@pytest.mark.azure` - Tests that interact with Azure services
- `@pytest.mark.service_bus` - Azure Service Bus specific tests
- `@pytest.mark.table_storage` - Azure Table Storage specific tests
- `@pytest.mark.asyncio` - Async tests (automatically handled)
- `@pytest.mark.slow` - Slow-running tests

## Environment Variables

For integration tests, set the following environment variables:

```bash
# Azure Service Bus
export AZURE_SERVICE_BUS_CONNECTION_STRING="Endpoint=sb://..."
export BUSINESS_DECISIONS_QUEUE="test-business-decisions"
export BUSINESS_EVENTS_TOPIC="test-business-events"

# Azure Table Storage
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;..."
export BOARDROOM_TABLE_NAME="TestBoardroomDecisions"
export METRICS_TABLE_NAME="TestBusinessMetrics"

# Test mode
export TESTING=true
```

Or create a `.env.test` file with these variables.

## Test Files Description

### `conftest.py`
Shared fixtures used across all tests:
- `mock_env_vars` - Mock environment variables
- `sample_business_decision` - Sample decision data
- `sample_service_bus_message` - Mock Service Bus message
- `mock_table_client` - Mock Azure Table client
- `mock_service_bus_client` - Mock Service Bus client
- `mock_table_storage` - Complete mock table storage implementation

### `unit/test_service_bus_handlers.py`
Unit tests for Azure Service Bus message handlers:
- Business decision processor tests
- Event processor tests (performance metrics, milestones, integrations)
- Error handling tests
- Message formatting tests

### `unit/test_storage_manager.py`
Unit tests for Storage Manager:
- Boardroom decision storage tests
- Business metrics storage tests
- History retrieval tests
- Error handling tests
- Mock table storage implementation tests

### `unit/test_azure_functions.py`
Unit tests for Azure Functions HTTP endpoints:
- Health endpoint tests
- Request validation tests
- Response formatting tests
- Async pattern tests

### `integration/test_azure_services.py`
Integration tests for Azure services:
- Table Storage workflow tests
- Service Bus message structure tests
- End-to-end workflow tests
- Concurrent operation tests

## Writing New Tests

When adding new tests, follow these guidelines:

1. **Use appropriate markers**: Mark tests with `@pytest.mark.unit` or `@pytest.mark.integration`
2. **Follow naming conventions**: Test functions should start with `test_`
3. **Use fixtures**: Leverage shared fixtures from `conftest.py`
4. **Document tests**: Add clear docstrings explaining what is being tested
5. **Follow AAA pattern**: Arrange-Act-Assert structure
6. **Test edge cases**: Include tests for error conditions and boundary cases

Example:

```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_my_feature(mock_dependency, sample_data):
    """Test that my feature works correctly"""
    # Arrange
    expected_result = "success"
    
    # Act
    result = await my_feature(sample_data)
    
    # Assert
    assert result == expected_result
    mock_dependency.method.assert_called_once()
```

## CI/CD Integration

Tests are automatically run in CI/CD pipelines. See `.github/workflows/test.yml` for configuration.

## Resources

- [Testing Specifications](../docs/testing/specifications.md) - Comprehensive testing guide
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [Azure SDK Testing Guide](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core#testing)

## Troubleshooting

### Tests fail with import errors

Make sure you have installed the package in development mode:
```bash
pip install -e .
```

### Async tests don't run

Ensure `pytest-asyncio` is installed:
```bash
pip install pytest-asyncio
```

### Coverage reports are not generated

Install pytest-cov:
```bash
pip install pytest-cov
```

### Azure service tests fail

Check that:
1. Environment variables are set correctly
2. Azure emulators are running (if using local emulation)
3. Test connection strings are valid
