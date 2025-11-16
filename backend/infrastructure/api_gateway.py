"""
API Gateway - Intelligent Request Router
Routes requests to best available service based on health, load, and capabilities

Integrates with:
- Service Discovery (finds services)
- Load Balancer (distributes load)
- Circuit Breaker (prevents cascade failures)
- Rate Limiting (protects services)
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from datetime import datetime, timedelta
from collections import deque
import httpx
import time

if TYPE_CHECKING:
    from .service_discovery import ServiceInstance

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Circuit breaker pattern for service calls
    Prevents cascade failures
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        half_open_attempts: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.half_open_attempts = half_open_attempts
        
        self.failure_count = 0
        self.state = "closed"  # closed, open, half_open
        self.last_failure_time = None
        self.half_open_successes = 0
    
    def record_success(self):
        """Record successful call"""
        if self.state == "half_open":
            self.half_open_successes += 1
            
            if self.half_open_successes >= self.half_open_attempts:
                # Reset to closed
                self.state = "closed"
                self.failure_count = 0
                self.half_open_successes = 0
                logger.info("[CIRCUIT-BREAKER] Circuit closed - service recovered")
        
        elif self.state == "closed":
            # Reset failure count on success
            self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            if self.state == "closed":
                self.state = "open"
                logger.warning(
                    f"[CIRCUIT-BREAKER] Circuit opened - "
                    f"service failing ({self.failure_count} failures)"
                )
    
    def can_attempt(self) -> bool:
        """Check if call attempt is allowed"""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            # Check if timeout expired
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                
                if elapsed >= self.timeout_seconds:
                    # Try half-open
                    self.state = "half_open"
                    self.half_open_successes = 0
                    logger.info("[CIRCUIT-BREAKER] Circuit half-open - trying recovery")
                    return True
            
            return False
        
        if self.state == "half_open":
            return True
        
        return False


class RateLimiter:
    """
    Rate limiter for protecting services
    Token bucket algorithm
    """
    
    def __init__(self, requests_per_second: float = 100.0):
        self.capacity = requests_per_second
        self.tokens = requests_per_second
        self.last_refill = time.time()
    
    def allow_request(self) -> bool:
        """Check if request is allowed"""
        self._refill()
        
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        
        return False
    
    def _refill(self):
        """Refill token bucket"""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add tokens based on elapsed time
        new_tokens = elapsed * self.capacity
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now


class APIGateway:
    """
    API Gateway - Intelligent Request Router
    
    Features:
    - Service discovery integration
    - Health-based routing
    - Load balancing
    - Circuit breakers
    - Rate limiting
    - Request retry
    - Failover
    - Metrics collection
    """
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self.request_history: deque = deque(maxlen=10000)
        
        # Metrics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.retried_requests = 0
        self.circuit_breaker_blocks = 0
        self.rate_limit_blocks = 0
    
    async def route_request(
        self,
        capability: str,
        path: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Route request to best available service
        
        Args:
            capability: Required capability (e.g., 'chat', 'search')
            path: Request path
            method: HTTP method
            data: Request body
            headers: Request headers
            max_retries: Maximum retry attempts
        
        Returns:
            Response from service
        """
        from backend.infrastructure.service_discovery import service_discovery
        
        self.total_requests += 1
        
        request_id = f"req_{int(time.time() * 1000)}"
        start_time = datetime.utcnow()
        
        for attempt in range(max_retries):
            try:
                # Find best service for capability
                service = service_discovery.find_service(
                    capability=capability,
                    health_status="healthy"
                )
                
                if not service:
                    # No healthy service found
                    logger.warning(
                        f"[API-GATEWAY] No healthy service for capability: {capability}"
                    )
                    
                    # Try degraded services
                    service = service_discovery.find_service(
                        capability=capability,
                        health_status="degraded"
                    )
                    
                    if not service:
                        self.failed_requests += 1
                        return {
                            'success': False,
                            'error': 'no_service_available',
                            'capability': capability
                        }
                
                # Check circuit breaker
                cb = self._get_circuit_breaker(service.service_id)
                
                if not cb.can_attempt():
                    logger.warning(
                        f"[API-GATEWAY] Circuit breaker open for {service.service_id}"
                    )
                    self.circuit_breaker_blocks += 1
                    
                    # Try next retry with different service
                    continue
                
                # Check rate limit
                rl = self._get_rate_limiter(service.service_id)
                
                if not rl.allow_request():
                    logger.warning(
                        f"[API-GATEWAY] Rate limit exceeded for {service.service_id}"
                    )
                    self.rate_limit_blocks += 1
                    
                    # Wait a bit and retry
                    await asyncio.sleep(0.1)
                    continue
                
                # Make request
                result = await self._make_request(
                    service=service,
                    path=path,
                    method=method,
                    data=data,
                    headers=headers
                )
                
                if result.get('success'):
                    # Success
                    cb.record_success()
                    self.successful_requests += 1
                    
                    # Record request
                    end_time = datetime.utcnow()
                    duration_ms = (end_time - start_time).total_seconds() * 1000
                    
                    self.request_history.append({
                        'request_id': request_id,
                        'capability': capability,
                        'service_id': service.service_id,
                        'path': path,
                        'method': method,
                        'success': True,
                        'duration_ms': duration_ms,
                        'attempts': attempt + 1,
                        'timestamp': start_time.isoformat()
                    })
                    
                    return result
                
                else:
                    # Failure
                    cb.record_failure()
                    
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"[API-GATEWAY] Request failed, retrying "
                            f"({attempt + 1}/{max_retries})"
                        )
                        self.retried_requests += 1
                        await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        self.failed_requests += 1
                        return result
            
            except Exception as e:
                logger.error(f"[API-GATEWAY] Request error: {e}")
                
                if attempt < max_retries - 1:
                    self.retried_requests += 1
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                else:
                    self.failed_requests += 1
                    return {
                        'success': False,
                        'error': str(e)
                    }
        
        self.failed_requests += 1
        return {
            'success': False,
            'error': 'max_retries_exceeded'
        }
    
    async def _make_request(
        self,
        service: Any,  # ServiceInstance
        path: str,
        method: str,
        data: Optional[Dict[str, Any]],
        headers: Optional[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Make HTTP request to service"""
        url = f"http://{service.host}:{service.port}{path}"
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers, timeout=30.0)
            elif method == "POST":
                response = await client.post(url, json=data, headers=headers, timeout=30.0)
            elif method == "PUT":
                response = await client.put(url, json=data, headers=headers, timeout=30.0)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers, timeout=30.0)
            else:
                return {'success': False, 'error': 'unsupported_method'}
            
            if response.status_code < 400:
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'data': response.json() if response.text else {}
                }
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text
                }
    
    def _get_circuit_breaker(self, service_id: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_id not in self.circuit_breakers:
            self.circuit_breakers[service_id] = CircuitBreaker()
        return self.circuit_breakers[service_id]
    
    def _get_rate_limiter(self, service_id: str) -> RateLimiter:
        """Get or create rate limiter for service"""
        if service_id not in self.rate_limiters:
            self.rate_limiters[service_id] = RateLimiter(requests_per_second=100.0)
        return self.rate_limiters[service_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get gateway statistics"""
        success_rate = (
            self.successful_requests / self.total_requests * 100
            if self.total_requests > 0 else 0
        )
        
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': success_rate,
            'retried_requests': self.retried_requests,
            'circuit_breaker_blocks': self.circuit_breaker_blocks,
            'rate_limit_blocks': self.rate_limit_blocks,
            'active_circuit_breakers': len([
                cb for cb in self.circuit_breakers.values()
                if cb.state != "closed"
            ])
        }
    
    def get_request_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent request history"""
        return list(self.request_history)[-limit:]


# Singleton instance
api_gateway = APIGateway()
