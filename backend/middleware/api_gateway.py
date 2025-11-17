"""
API Gateway Middleware
Rate limiting, quotas, authentication, and request logging
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import time

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_size: int = 10
    ):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.buckets: Dict[str, Dict[str, Any]] = defaultdict(self._new_bucket)
        
    def _new_bucket(self) -> Dict[str, Any]:
        """Create a new token bucket"""
        return {
            "tokens": self.burst_size,
            "last_refill": time.time()
        }
    
    def _refill_bucket(self, bucket: Dict[str, Any]):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - bucket["last_refill"]
        
        # Add tokens based on rate (requests per second)
        tokens_to_add = elapsed * (self.requests_per_minute / 60.0)
        
        bucket["tokens"] = min(
            self.burst_size,
            bucket["tokens"] + tokens_to_add
        )
        bucket["last_refill"] = now
    
    def check_rate_limit(self, key: str) -> bool:
        """Check if request is allowed under rate limit"""
        bucket = self.buckets[key]
        self._refill_bucket(bucket)
        
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        else:
            return False
    
    def get_bucket_status(self, key: str) -> Dict[str, Any]:
        """Get current bucket status"""
        bucket = self.buckets[key]
        self._refill_bucket(bucket)
        
        return {
            "tokens_available": bucket["tokens"],
            "max_tokens": self.burst_size,
            "refill_rate_per_min": self.requests_per_minute
        }

class APIGatewayMiddleware(BaseHTTPMiddleware):
    """API Gateway with rate limiting and request logging"""
    
    def __init__(
        self,
        app,
        rate_limit_per_minute: int = 60,
        rate_limit_burst: int = 10,
        enable_logging: bool = True
    ):
        super().__init__(app)
        self.rate_limiter = RateLimiter(rate_limit_per_minute, rate_limit_burst)
        self.enable_logging = enable_logging
        self.request_count = 0
        self.error_count = 0
        
    async def dispatch(self, request: Request, call_next):
        """Process request through gateway"""
        start_time = time.time()
        
        # Extract client identifier (IP or API key)
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not self.rate_limiter.check_rate_limit(client_id):
            return HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        
        # Log request
        self.request_count += 1
        
        if self.enable_logging:
            print(f"[API-GATEWAY] {request.method} {request.url.path} from {client_id}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Track errors
            if response.status_code >= 400:
                self.error_count += 1
            
            # Add rate limit headers
            bucket_status = self.rate_limiter.get_bucket_status(client_id)
            response.headers["X-RateLimit-Remaining"] = str(int(bucket_status["tokens_available"]))
            response.headers["X-RateLimit-Limit"] = str(bucket_status["max_tokens"])
            
            # Add latency header
            latency_ms = (time.time() - start_time) * 1000
            response.headers["X-Response-Time"] = f"{latency_ms:.2f}ms"
            
            return response
            
        except Exception as e:
            self.error_count += 1
            raise
    
    def _get_client_id(self, request: Request) -> str:
        """Extract client identifier from request"""
        # Try API key first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"key_{api_key[:8]}"
        
        # Fall back to IP
        client_ip = request.client.host if request.client else "unknown"
        return f"ip_{client_ip}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get gateway statistics"""
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": (
                self.error_count / self.request_count * 100
                if self.request_count > 0 else 0
            ),
            "active_clients": len(self.rate_limiter.buckets)
        }

class QuotaManager:
    """Manage per-tenant quotas"""
    
    def __init__(self):
        self.quotas: Dict[str, Dict[str, Any]] = {}
        
    def set_quota(
        self,
        tenant_id: str,
        quota_type: str,
        limit: int,
        period: str = "daily"
    ):
        """Set quota for tenant"""
        if tenant_id not in self.quotas:
            self.quotas[tenant_id] = {}
        
        self.quotas[tenant_id][quota_type] = {
            "limit": limit,
            "used": 0,
            "period": period,
            "reset_at": self._calculate_reset_time(period)
        }
    
    def _calculate_reset_time(self, period: str) -> datetime:
        """Calculate when quota resets"""
        now = datetime.now()
        
        if period == "hourly":
            return now + timedelta(hours=1)
        elif period == "daily":
            return now + timedelta(days=1)
        elif period == "monthly":
            return now + timedelta(days=30)
        else:
            return now + timedelta(days=1)
    
    def check_quota(self, tenant_id: str, quota_type: str) -> bool:
        """Check if tenant is within quota"""
        if tenant_id not in self.quotas:
            return True  # No quota = unlimited
        
        quota = self.quotas[tenant_id].get(quota_type)
        
        if not quota:
            return True
        
        # Check if quota needs reset
        if datetime.now() > quota["reset_at"]:
            quota["used"] = 0
            quota["reset_at"] = self._calculate_reset_time(quota["period"])
        
        # Check limit
        return quota["used"] < quota["limit"]
    
    def increment_usage(self, tenant_id: str, quota_type: str, amount: int = 1):
        """Increment usage counter"""
        if tenant_id in self.quotas and quota_type in self.quotas[tenant_id]:
            self.quotas[tenant_id][quota_type]["used"] += amount
    
    def get_quota_status(self, tenant_id: str) -> Dict[str, Any]:
        """Get quota status for tenant"""
        if tenant_id not in self.quotas:
            return {}
        
        return {
            quota_type: {
                "limit": quota["limit"],
                "used": quota["used"],
                "remaining": quota["limit"] - quota["used"],
                "reset_at": quota["reset_at"].isoformat()
            }
            for quota_type, quota in self.quotas[tenant_id].items()
        }

# Global instances
_rate_limiter: Optional[RateLimiter] = None
_quota_manager: Optional[QuotaManager] = None

def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter

def get_quota_manager() -> QuotaManager:
    """Get global quota manager"""
    global _quota_manager
    if _quota_manager is None:
        _quota_manager = QuotaManager()
    return _quota_manager
