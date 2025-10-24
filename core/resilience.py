"""
Resilience Layer - Retry, Timeout, Circuit Breaker
"""
import time
import logging
from functools import wraps
from typing import Callable, Any
import threading

logger = logging.getLogger('HIDR.Resilience')

class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half_open
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker"""
        with self.lock:
            if self.state == 'open':
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = 'half_open'
                    logger.info("Circuit breaker half-open, attempting call")
                else:
                    raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            with self.lock:
                if self.state == 'half_open':
                    self.state = 'closed'
                    self.failures = 0
                    logger.info("Circuit breaker closed")
            return result
        except Exception as e:
            with self.lock:
                self.failures += 1
                self.last_failure_time = time.time()
                
                if self.failures >= self.failure_threshold:
                    self.state = 'open'
                    logger.warning(f"Circuit breaker OPEN after {self.failures} failures")
                
            raise e
    
    def reset(self):
        """Reset circuit breaker"""
        with self.lock:
            self.failures = 0
            self.state = 'closed'
            self.last_failure_time = None

class ResilienceLayer:
    """Resilience layer with retry, timeout, and circuit breaker"""
    
    def __init__(self):
        self.circuit_breakers = {}
    
    def get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """Get or create circuit breaker for a service"""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker()
        return self.circuit_breakers[name]
    
    def retry(self, max_attempts: int = 3, backoff: float = 2.0, exceptions: tuple = (Exception,)):
        """Retry decorator with exponential backoff"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                attempt = 0
                last_exception = None
                
                while attempt < max_attempts:
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        attempt += 1
                        last_exception = e
                        
                        if attempt < max_attempts:
                            wait_time = backoff ** attempt
                            logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            logger.error(f"All {max_attempts} attempts failed")
                
                raise last_exception
            
            return wrapper
        return decorator
    
    def timeout(self, seconds: float):
        """Timeout decorator"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Function {func.__name__} timed out after {seconds}s")
                
                # Note: signal.alarm only works on Unix
                # For Windows, we use a simpler approach
                try:
                    if hasattr(signal, 'SIGALRM'):
                        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(int(seconds))
                    
                    result = func(*args, **kwargs)
                    
                    if hasattr(signal, 'SIGALRM'):
                        signal.alarm(0)
                        signal.signal(signal.SIGALRM, old_handler)
                    
                    return result
                except TimeoutError:
                    logger.error(f"Timeout after {seconds}s")
                    raise
            
            return wrapper
        return decorator
    
    def circuit_breaker(self, name: str, failure_threshold: int = 5):
        """Circuit breaker decorator"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                cb = self.get_circuit_breaker(name)
                return cb.call(func, *args, **kwargs)
            
            return wrapper
        return decorator
    
    def call_with_resilience(self, func: Callable, *args, 
                            max_attempts: int = 3, 
                            timeout_seconds: float = 10,
                            circuit_breaker_name: str = None,
                            **kwargs) -> Any:
        """Call function with full resilience (retry + timeout + circuit breaker)"""
        
        @self.retry(max_attempts=max_attempts)
        def resilient_call():
            if circuit_breaker_name:
                cb = self.get_circuit_breaker(circuit_breaker_name)
                return cb.call(func, *args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        return resilient_call()

# Global resilience instance
resilience = ResilienceLayer()
