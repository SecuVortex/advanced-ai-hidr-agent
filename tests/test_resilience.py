"""Tests for resilience layer"""
import pytest
import time
from core.resilience import ResilienceLayer, CircuitBreaker

class TestCircuitBreaker:
    """Test circuit breaker functionality"""
    
    def test_init(self):
        """Test circuit breaker initialization"""
        cb = CircuitBreaker(failure_threshold=3, timeout=30)
        assert cb.failure_threshold == 3
        assert cb.timeout == 30
        assert cb.state == 'closed'
    
    def test_successful_call(self):
        """Test successful function call"""
        cb = CircuitBreaker()
        
        def success_func():
            return "success"
        
        result = cb.call(success_func)
        assert result == "success"
        assert cb.state == 'closed'
    
    def test_circuit_opens_on_failures(self):
        """Test circuit opens after threshold failures"""
        cb = CircuitBreaker(failure_threshold=3)
        
        def failing_func():
            raise Exception("Test failure")
        
        # Trigger failures
        for i in range(3):
            with pytest.raises(Exception):
                cb.call(failing_func)
        
        assert cb.state == 'open'
        assert cb.failures == 3
    
    def test_circuit_blocks_when_open(self):
        """Test circuit blocks calls when open"""
        cb = CircuitBreaker(failure_threshold=2)
        
        def failing_func():
            raise Exception("Test failure")
        
        # Open the circuit
        for i in range(2):
            with pytest.raises(Exception):
                cb.call(failing_func)
        
        # Should block now
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            cb.call(failing_func)
    
    def test_reset(self):
        """Test circuit breaker reset"""
        cb = CircuitBreaker()
        cb.failures = 5
        cb.state = 'open'
        
        cb.reset()
        
        assert cb.failures == 0
        assert cb.state == 'closed'

class TestResilienceLayer:
    """Test resilience layer functionality"""
    
    def test_init(self):
        """Test resilience layer initialization"""
        rl = ResilienceLayer()
        assert rl is not None
        assert isinstance(rl.circuit_breakers, dict)
    
    def test_get_circuit_breaker(self):
        """Test getting circuit breaker"""
        rl = ResilienceLayer()
        cb = rl.get_circuit_breaker('test_service')
        
        assert isinstance(cb, CircuitBreaker)
        assert 'test_service' in rl.circuit_breakers
    
    def test_retry_decorator(self):
        """Test retry decorator"""
        rl = ResilienceLayer()
        attempts = []
        
        @rl.retry(max_attempts=3, backoff=0.1)
        def flaky_func():
            attempts.append(1)
            if len(attempts) < 2:
                raise Exception("Temporary failure")
            return "success"
        
        result = flaky_func()
        assert result == "success"
        assert len(attempts) == 2
    
    def test_retry_exhausted(self):
        """Test retry exhaustion"""
        rl = ResilienceLayer()
        
        @rl.retry(max_attempts=2, backoff=0.1)
        def always_fails():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            always_fails()
    
    def test_call_with_resilience(self):
        """Test full resilience call"""
        rl = ResilienceLayer()
        
        def test_func(x, y):
            return x + y
        
        result = rl.call_with_resilience(test_func, 2, 3, max_attempts=2)
        assert result == 5
    
    def test_call_with_resilience_and_circuit_breaker(self):
        """Test resilience with circuit breaker"""
        rl = ResilienceLayer()
        
        def test_func():
            return "ok"
        
        result = rl.call_with_resilience(
            test_func,
            max_attempts=2,
            circuit_breaker_name='test'
        )
        assert result == "ok"
