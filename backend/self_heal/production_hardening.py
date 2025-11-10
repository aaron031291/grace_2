"""
Production Hardening - Resilience patterns for real-world use

Implements:
- Retry logic with exponential backoff
- Circuit breakers for failing services
- Timeouts and deadlines
- Graceful degradation
- Error handling and recovery
"""

import asyncio
import time
from typing import Dict, Any, Callable, Optional
from datetime import datetime, timedelta
from functools import wraps
from enum import Enum


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, blocking requests
    HALF_OPEN = "half_open"  # Testing if recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    Prevents cascading failures by stopping requests to failing services.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout_seconds
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            # Check if timeout has elapsed
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception(f"Circuit breaker OPEN - service unavailable (retry after {self.timeout}s)")
        
        try:
            result = await func(*args, **kwargs)
            
            # Success - reset if in half-open
            if self.state == CircuitState.HALF_OPEN:
                self._reset()
            
            return result
            
        except self.expected_exception as e:
            self._record_failure()
            raise e
    
    def _record_failure(self):
        """Record a failure and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"  [WARN]  Circuit breaker OPENED after {self.failure_count} failures")
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try again"""
        if not self.last_failure_time:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.timeout
    
    def _reset(self):
        """Reset circuit breaker to closed state"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        print("  [OK] Circuit breaker CLOSED - service recovered")


class RetryPolicy:
    """
    Retry logic with exponential backoff and jitter.
    """
    
    @staticmethod
    async def retry_with_backoff(
        func: Callable,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        exceptions: tuple = (Exception,)
    ):
        """
        Retry function with exponential backoff.
        
        Args:
            func: Async function to retry
            max_attempts: Maximum number of attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Multiplier for exponential backoff
            jitter: Add random jitter to prevent thundering herd
            exceptions: Tuple of exceptions to catch and retry
        """
        
        for attempt in range(1, max_attempts + 1):
            try:
                return await func()
                
            except exceptions as e:
                if attempt == max_attempts:
                    print(f"  [FAIL] Failed after {max_attempts} attempts: {e}")
                    raise
                
                # Calculate delay with exponential backoff
                delay = min(base_delay * (exponential_base ** (attempt - 1)), max_delay)
                
                # Add jitter (random 0-100% of delay)
                if jitter:
                    import random
                    delay *= (0.5 + random.random() * 0.5)
                
                print(f"  [WARN]  Attempt {attempt}/{max_attempts} failed: {e}")
                print(f"  ⏳ Retrying in {delay:.1f}s...")
                
                await asyncio.sleep(delay)


class TimeoutManager:
    """
    Timeout management for operations.
    """
    
    @staticmethod
    async def with_timeout(
        func: Callable,
        timeout_seconds: float,
        operation_name: str = "operation"
    ):
        """
        Execute function with timeout.
        
        Args:
            func: Async function to execute
            timeout_seconds: Timeout in seconds
            operation_name: Name for error messages
        """
        
        try:
            return await asyncio.wait_for(func(), timeout=timeout_seconds)
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"{operation_name} timed out after {timeout_seconds}s")


def with_retry(max_attempts: int = 3, base_delay: float = 1.0):
    """Decorator to add retry logic to async functions"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await RetryPolicy.retry_with_backoff(
                lambda: func(*args, **kwargs),
                max_attempts=max_attempts,
                base_delay=base_delay
            )
        return wrapper
    return decorator


def with_timeout(timeout_seconds: float):
    """Decorator to add timeout to async functions"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await TimeoutManager.with_timeout(
                lambda: func(*args, **kwargs),
                timeout_seconds=timeout_seconds,
                operation_name=func.__name__
            )
        return wrapper
    return decorator


def with_circuit_breaker(failure_threshold: int = 5, timeout_seconds: int = 60):
    """Decorator to add circuit breaker to async functions"""
    
    # Create circuit breaker instance for this function
    breaker = CircuitBreaker(
        failure_threshold=failure_threshold,
        timeout_seconds=timeout_seconds
    )
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator


class GracefulDegradation:
    """
    Graceful degradation patterns.
    Provides fallback behavior when primary operations fail.
    """
    
    @staticmethod
    async def with_fallback(
        primary_func: Callable,
        fallback_func: Callable,
        exceptions: tuple = (Exception,)
    ):
        """
        Try primary function, fall back to secondary on failure.
        
        Args:
            primary_func: Primary async function to try
            fallback_func: Fallback async function
            exceptions: Exceptions to catch
        """
        
        try:
            return await primary_func()
        except exceptions as e:
            print(f"  [WARN]  Primary operation failed: {e}")
            print(f"  🔄 Falling back to secondary operation...")
            return await fallback_func()
    
    @staticmethod
    async def with_default(
        func: Callable,
        default_value: Any,
        exceptions: tuple = (Exception,)
    ):
        """
        Try function, return default value on failure.
        
        Args:
            func: Async function to try
            default_value: Value to return on failure
            exceptions: Exceptions to catch
        """
        
        try:
            return await func()
        except exceptions as e:
            print(f"  [WARN]  Operation failed: {e}")
            print(f"  ↩️  Returning default value")
            return default_value


class ErrorHandler:
    """
    Centralized error handling with logging and recovery.
    """
    
    @staticmethod
    async def handle_error(
        error: Exception,
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle error with logging and structured response.
        
        Args:
            error: The exception that occurred
            operation: Name of the operation that failed
            context: Additional context for debugging
        """
        
        error_info = {
            "ok": False,
            "error": str(error),
            "error_type": type(error).__name__,
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        }
        
        if context:
            error_info["context"] = context
        
        # Log error (in production, would use proper logging)
        print(f"  [FAIL] ERROR in {operation}: {error}")
        if context:
            print(f"    Context: {context}")
        
        return error_info
    
    @staticmethod
    def is_retryable(error: Exception) -> bool:
        """Determine if an error is retryable"""
        
        retryable_errors = (
            TimeoutError,
            ConnectionError,
            OSError,
            asyncio.TimeoutError
        )
        
        return isinstance(error, retryable_errors)


class RateLimiter:
    """
    Rate limiting to prevent overwhelming services.
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
    
    async def acquire(self):
        """Acquire permission to make a request"""
        
        now = time.time()
        
        # Remove old requests outside window
        self.requests = [
            req_time for req_time in self.requests
            if now - req_time < self.window_seconds
        ]
        
        # Check if at limit
        if len(self.requests) >= self.max_requests:
            # Wait until oldest request expires
            wait_time = self.window_seconds - (now - self.requests[0]) + 0.1
            print(f"  ⏳ Rate limit reached, waiting {wait_time:.1f}s...")
            await asyncio.sleep(wait_time)
            self.requests.pop(0)
        
        # Record this request
        self.requests.append(now)


# ============= Production-Ready Executor Wrapper =============

class ProductionExecutor:
    """
    Wraps executors with production hardening patterns.
    """
    
    def __init__(self):
        self.circuit_breakers = {}
        self.rate_limiters = {}
    
    async def execute_with_resilience(
        self,
        func: Callable,
        operation_name: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        use_circuit_breaker: bool = True,
        rate_limit: Optional[tuple] = None  # (max_requests, window_seconds)
    ) -> Dict[str, Any]:
        """
        Execute function with full production hardening.
        
        Includes:
        - Timeout protection
        - Retry logic
        - Circuit breaker
        - Rate limiting
        - Error handling
        """
        
        # Rate limiting
        if rate_limit:
            limiter = self._get_rate_limiter(operation_name, *rate_limit)
            await limiter.acquire()
        
        # Circuit breaker
        if use_circuit_breaker:
            breaker = self._get_circuit_breaker(operation_name)
            
            try:
                # Execute with timeout and retry
                result = await breaker.call(
                    TimeoutManager.with_timeout,
                    lambda: RetryPolicy.retry_with_backoff(
                        func,
                        max_attempts=max_retries
                    ),
                    timeout,
                    operation_name
                )
                return result
                
            except Exception as e:
                return await ErrorHandler.handle_error(
                    e,
                    operation_name,
                    {"timeout": timeout, "max_retries": max_retries}
                )
        else:
            # Without circuit breaker
            try:
                result = await TimeoutManager.with_timeout(
                    lambda: RetryPolicy.retry_with_backoff(
                        func,
                        max_attempts=max_retries
                    ),
                    timeout,
                    operation_name
                )
                return result
                
            except Exception as e:
                return await ErrorHandler.handle_error(
                    e,
                    operation_name,
                    {"timeout": timeout, "max_retries": max_retries}
                )
    
    def _get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """Get or create circuit breaker for operation"""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker()
        return self.circuit_breakers[name]
    
    def _get_rate_limiter(self, name: str, max_requests: int, window_seconds: int) -> RateLimiter:
        """Get or create rate limiter for operation"""
        if name not in self.rate_limiters:
            self.rate_limiters[name] = RateLimiter(max_requests, window_seconds)
        return self.rate_limiters[name]


# Singleton instance
production_executor = ProductionExecutor()
