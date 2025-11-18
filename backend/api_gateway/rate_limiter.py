"""
Rate Limiter - Token bucket algorithm with per-tenant limits
"""

import time
from typing import Dict, Optional
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class TokenBucket:
    """Token bucket for rate limiting"""
    capacity: int
    refill_rate: float  # tokens per second
    tokens: float = field(init=False)
    last_refill: float = field(init=False)
    lock: Lock = field(default_factory=Lock, init=False)
    
    def __post_init__(self):
        self.tokens = float(self.capacity)
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens. Returns True if successful."""
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def _refill(self):
        """Refill tokens based on time elapsed"""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + (elapsed * self.refill_rate)
        )
        self.last_refill = now
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """Get time to wait before tokens are available"""
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                return 0.0
            deficit = tokens - self.tokens
            return deficit / self.refill_rate


class RateLimiter:
    """Global rate limiter with per-IP limits"""
    
    def __init__(
        self,
        requests_per_second: int = 100,
        burst_size: int = 200
    ):
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.buckets: Dict[str, TokenBucket] = {}
        self.lock = Lock()
    
    def check_rate_limit(self, client_id: str) -> tuple[bool, Optional[float]]:
        """
        Check if request is allowed for client.
        Returns (allowed, retry_after_seconds)
        """
        bucket = self._get_bucket(client_id)
        if bucket.consume():
            return True, None
        else:
            wait_time = bucket.get_wait_time()
            return False, wait_time
    
    def _get_bucket(self, client_id: str) -> TokenBucket:
        """Get or create bucket for client"""
        if client_id not in self.buckets:
            with self.lock:
                if client_id not in self.buckets:
                    self.buckets[client_id] = TokenBucket(
                        capacity=self.burst_size,
                        refill_rate=self.requests_per_second
                    )
        return self.buckets[client_id]
    
    def get_stats(self, client_id: str) -> dict:
        """Get rate limit stats for client"""
        if client_id not in self.buckets:
            return {
                "tokens_available": self.burst_size,
                "capacity": self.burst_size,
                "refill_rate": self.requests_per_second
            }
        
        bucket = self.buckets[client_id]
        with bucket.lock:
            bucket._refill()
            return {
                "tokens_available": int(bucket.tokens),
                "capacity": bucket.capacity,
                "refill_rate": bucket.refill_rate
            }


class TenantRateLimiter:
    """Per-tenant rate limiter with configurable limits"""
    
    def __init__(self):
        self.tenant_limits: Dict[str, tuple[int, int]] = {}  # tenant_id -> (rps, burst)
        self.limiters: Dict[str, RateLimiter] = {}
        self.lock = Lock()
        
        self.default_rps = 100
        self.default_burst = 200
    
    def set_tenant_limits(
        self,
        tenant_id: str,
        requests_per_second: int,
        burst_size: int
    ):
        """Configure custom limits for a tenant"""
        with self.lock:
            self.tenant_limits[tenant_id] = (requests_per_second, burst_size)
            if tenant_id in self.limiters:
                del self.limiters[tenant_id]
    
    def check_rate_limit(
        self,
        tenant_id: str,
        client_id: str
    ) -> tuple[bool, Optional[float]]:
        """Check rate limit for tenant + client combination"""
        limiter = self._get_limiter(tenant_id)
        return limiter.check_rate_limit(f"{tenant_id}:{client_id}")
    
    def _get_limiter(self, tenant_id: str) -> RateLimiter:
        """Get or create rate limiter for tenant"""
        if tenant_id not in self.limiters:
            with self.lock:
                if tenant_id not in self.limiters:
                    rps, burst = self.tenant_limits.get(
                        tenant_id,
                        (self.default_rps, self.default_burst)
                    )
                    self.limiters[tenant_id] = RateLimiter(rps, burst)
        return self.limiters[tenant_id]
    
    def get_stats(self, tenant_id: str, client_id: str) -> dict:
        """Get rate limit stats for tenant + client"""
        limiter = self._get_limiter(tenant_id)
        return limiter.get_stats(f"{tenant_id}:{client_id}")
