"""
Tests for AOS Utilization Improvements

Tests the Priority 1 implementations:
- Service Interfaces
- Reliability Patterns
- Observability
"""

import asyncio
import pytest
from datetime import datetime

# Import the new modules
from src.core.service_interfaces import (
    IStorageService,
    AOSStorageService,
)
from src.core.reliability import (
    CircuitBreaker,
    CircuitState,
    RetryPolicy,
    IdempotencyHandler,
    with_circuit_breaker,
    with_retry,
)
from src.core.observability import (
    CorrelationContext,
    get_correlation_context,
    set_correlation_context,
    correlation_scope,
    StructuredLogger,
    MetricsCollector,
    HealthCheck,
    create_structured_logger,
    get_metrics_collector,
    get_health_check,
)


class TestServiceInterfaces:
    """Test service interface abstractions."""
    
    def test_istorage_service_protocol(self):
        """Test IStorageService protocol definition."""
        # Protocol should allow checking
        assert hasattr(IStorageService, 'save')
        assert hasattr(IStorageService, 'load')
        assert hasattr(IStorageService, 'delete')
        assert hasattr(IStorageService, 'list_keys')
        assert hasattr(IStorageService, 'exists')


class TestReliabilityPatterns:
    """Test reliability patterns."""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures."""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
        
        # Define a failing operation
        async def failing_operation():
            raise Exception("Simulated failure")
        
        # Cause failures
        for _ in range(3):
            try:
                await breaker.call(failing_operation)
            except Exception:
                pass
        
        # Circuit should be open
        assert breaker.state == CircuitState.OPEN
        assert breaker.failure_count == 3
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_allows_success(self):
        """Test circuit breaker allows successful operations."""
        breaker = CircuitBreaker()
        
        async def success_operation():
            return "success"
        
        result = await breaker.call(success_operation)
        assert result == "success"
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_retry_policy_retries_on_failure(self):
        """Test retry policy retries failed operations."""
        policy = RetryPolicy(max_retries=3, base_delay=0.1, jitter=False)
        
        attempt_count = 0
        
        async def flaky_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Transient failure")
            return "success"
        
        result = await policy.execute(flaky_operation)
        assert result == "success"
        assert attempt_count == 3  # Failed twice, succeeded on 3rd attempt
    
    @pytest.mark.asyncio
    async def test_retry_policy_exhausts_retries(self):
        """Test retry policy exhausts all retries on persistent failure."""
        policy = RetryPolicy(max_retries=2, base_delay=0.1)
        
        async def always_fails():
            raise ValueError("Persistent failure")
        
        with pytest.raises(ValueError):
            await policy.execute(always_fails)
    
    @pytest.mark.asyncio
    async def test_idempotency_handler_caches_result(self):
        """Test idempotency handler caches results."""
        handler = IdempotencyHandler(cache_ttl=10)
        
        call_count = 0
        
        async def operation():
            nonlocal call_count
            call_count += 1
            return f"result_{call_count}"
        
        # First call
        result1 = await handler.execute("key1", operation)
        assert result1 == "result_1"
        assert call_count == 1
        
        # Second call with same key should return cached result
        result2 = await handler.execute("key1", operation)
        assert result2 == "result_1"  # Same cached result
        assert call_count == 1  # Operation not called again
        
        # Different key should execute operation
        result3 = await handler.execute("key2", operation)
        assert result3 == "result_2"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_with_retry_decorator(self):
        """Test @with_retry decorator."""
        attempt_count = 0
        
        @with_retry(max_retries=2, base_delay=0.1)
        async def decorated_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise Exception("Retry me")
            return "success"
        
        result = await decorated_operation()
        assert result == "success"
        assert attempt_count == 2


class TestObservability:
    """Test observability features."""
    
    def test_correlation_context_creation(self):
        """Test correlation context creation."""
        context = CorrelationContext(
            correlation_id="test-123",
            operation_name="test_operation"
        )
        
        assert context.correlation_id == "test-123"
        assert context.operation_name == "test_operation"
        assert isinstance(context.metadata, dict)
    
    def test_correlation_context_auto_id(self):
        """Test correlation context auto-generates ID."""
        context = CorrelationContext()
        
        assert context.correlation_id is not None
        assert len(context.correlation_id) > 0
    
    def test_correlation_scope_context_manager(self):
        """Test correlation scope context manager."""
        # Set initial context
        set_correlation_context(None)
        
        with correlation_scope(operation_name="outer_op") as ctx:
            assert ctx.operation_name == "outer_op"
            assert get_correlation_context() == ctx
            
            # Nested scope should inherit correlation_id
            with correlation_scope(operation_name="inner_op") as inner_ctx:
                assert inner_ctx.correlation_id == ctx.correlation_id
                assert inner_ctx.causation_id == ctx.correlation_id
                assert inner_ctx.operation_name == "inner_op"
        
        # Context should be cleared after exiting
        assert get_correlation_context() is None
    
    def test_structured_logger_creates_entry(self):
        """Test structured logger creates properly formatted entries."""
        logger = create_structured_logger("test_logger")
        
        assert logger.name == "test_logger"
        assert isinstance(logger, StructuredLogger)
    
    def test_metrics_collector_counters(self):
        """Test metrics collector counter functionality."""
        metrics = MetricsCollector()
        
        metrics.increment_counter("test.counter", 1)
        metrics.increment_counter("test.counter", 2)
        
        collected = metrics.get_metrics()
        assert collected["counters"]["test.counter"] == 3
    
    def test_metrics_collector_gauges(self):
        """Test metrics collector gauge functionality."""
        metrics = MetricsCollector()
        
        metrics.set_gauge("test.gauge", 42.5)
        metrics.set_gauge("test.gauge", 100.0)
        
        collected = metrics.get_metrics()
        assert collected["gauges"]["test.gauge"] == 100.0
    
    def test_metrics_collector_histograms(self):
        """Test metrics collector histogram functionality."""
        metrics = MetricsCollector()
        
        metrics.record_histogram("test.duration", 10.0)
        metrics.record_histogram("test.duration", 20.0)
        metrics.record_histogram("test.duration", 30.0)
        
        collected = metrics.get_metrics()
        histogram = collected["histograms"]["test.duration"]
        
        assert histogram["count"] == 3
        assert histogram["min"] == 10.0
        assert histogram["max"] == 30.0
        assert histogram["avg"] == 20.0
    
    def test_metrics_collector_with_tags(self):
        """Test metrics collector with tags."""
        metrics = MetricsCollector()
        
        metrics.increment_counter("requests", tags={"status": "200"})
        metrics.increment_counter("requests", tags={"status": "404"})
        
        collected = metrics.get_metrics()
        assert "requests[status=200]" in collected["counters"]
        assert "requests[status=404]" in collected["counters"]
    
    @pytest.mark.asyncio
    async def test_health_check_registration(self):
        """Test health check registration."""
        health = HealthCheck()
        
        async def mock_check():
            return {"healthy": True, "status": "ok"}
        
        health.register_check("test_check", mock_check)
        
        result = await health.check_health()
        assert result["healthy"] is True
        assert "test_check" in result["checks"]
        assert result["checks"]["test_check"]["healthy"] is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure_detection(self):
        """Test health check detects failures."""
        health = HealthCheck()
        
        async def failing_check():
            raise Exception("Check failed")
        
        async def passing_check():
            return True
        
        health.register_check("failing", failing_check)
        health.register_check("passing", passing_check)
        
        result = await health.check_health()
        
        # Overall health should be False if any check fails
        assert result["healthy"] is False
        assert result["checks"]["failing"]["healthy"] is False
        assert "error" in result["checks"]["failing"]
        assert result["checks"]["passing"]["healthy"] is True


class TestIntegration:
    """Integration tests combining multiple features."""
    
    @pytest.mark.asyncio
    async def test_correlation_with_retry(self):
        """Test correlation IDs persist across retries."""
        attempt_count = 0
        observed_correlation_ids = []
        
        with correlation_scope(operation_name="retry_test") as ctx:
            original_correlation_id = ctx.correlation_id
            
            @with_retry(max_retries=2, base_delay=0.1)
            async def operation_with_correlation():
                nonlocal attempt_count
                attempt_count += 1
                
                # Get current correlation context
                current_ctx = get_correlation_context()
                if current_ctx:
                    observed_correlation_ids.append(current_ctx.correlation_id)
                
                if attempt_count < 2:
                    raise Exception("Retry needed")
                return "success"
            
            result = await operation_with_correlation()
            
            assert result == "success"
            assert attempt_count == 2
            # All observed correlation IDs should match the original
            assert all(cid == original_correlation_id for cid in observed_correlation_ids)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
