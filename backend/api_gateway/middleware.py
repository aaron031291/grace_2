"""
API Gateway Middleware - Rate limiting, auth, and logging
"""

import time
import json
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .rate_limiter import RateLimiter, TenantRateLimiter
from .auth import APIKeyAuth, JWTAuth


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(
        self,
        app: ASGIApp,
        rate_limiter: Optional[RateLimiter] = None,
        tenant_rate_limiter: Optional[TenantRateLimiter] = None
    ):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.tenant_rate_limiter = tenant_rate_limiter or TenantRateLimiter()
    
    async def dispatch(self, request: Request, call_next: Callable):
        client_id = self._get_client_id(request)
        
        tenant_id = request.state.__dict__.get("tenant_id")
        
        if tenant_id:
            allowed, retry_after = self.tenant_rate_limiter.check_rate_limit(
                tenant_id, client_id
            )
        else:
            allowed, retry_after = self.rate_limiter.check_rate_limit(client_id)
        
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(int(retry_after or 1))}
            )
        
        response = await call_next(request)
        
        if tenant_id:
            stats = self.tenant_rate_limiter.get_stats(tenant_id, client_id)
        else:
            stats = self.rate_limiter.get_stats(client_id)
        
        response.headers["X-RateLimit-Limit"] = str(stats["capacity"])
        response.headers["X-RateLimit-Remaining"] = str(stats["tokens_available"])
        
        return response
    
    @staticmethod
    def _get_client_id(request: Request) -> str:
        """Get client identifier from request"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        if request.client:
            return request.client.host
        
        return "unknown"


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware"""
    
    def __init__(
        self,
        app: ASGIApp,
        api_key_auth: Optional[APIKeyAuth] = None,
        jwt_auth: Optional[JWTAuth] = None,
        public_paths: Optional[list[str]] = None
    ):
        super().__init__(app)
        self.api_key_auth = api_key_auth or APIKeyAuth()
        self.jwt_auth = jwt_auth
        self.public_paths = public_paths or ["/docs", "/openapi.json", "/health"]
    
    async def dispatch(self, request: Request, call_next: Callable):
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)
        
        api_key = request.headers.get("X-API-Key")
        if api_key:
            key_data = self.api_key_auth.validate_key(api_key)
            if key_data:
                request.state.tenant_id = key_data.tenant_id
                request.state.auth_scopes = key_data.scopes
                request.state.auth_type = "api_key"
                return await call_next(request)
        
        if self.jwt_auth:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
                payload = self.jwt_auth.validate_token(token)
                if payload:
                    request.state.tenant_id = payload.get("tenant_id")
                    request.state.user_id = payload.get("user_id")
                    request.state.auth_scopes = payload.get("scopes", [])
                    request.state.auth_type = "jwt"
                    return await call_next(request)
        
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Authentication required"},
            headers={"WWW-Authenticate": "Bearer"}
        )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging middleware with structured JSON logs"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        request_log = {
            "timestamp": time.time(),
            "type": "request",
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("User-Agent"),
            "tenant_id": request.state.__dict__.get("tenant_id"),
            "auth_type": request.state.__dict__.get("auth_type")
        }
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            response_log = {
                "timestamp": time.time(),
                "type": "response",
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "tenant_id": request.state.__dict__.get("tenant_id"),
                "auth_type": request.state.__dict__.get("auth_type")
            }
            
            request_id = f"{int(start_time * 1000)}-{hash(request.url.path) % 10000}"
            response.headers["X-Request-ID"] = request_id
            response_log["request_id"] = request_id
            
            print(json.dumps(request_log))
            print(json.dumps(response_log))
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            error_log = {
                "timestamp": time.time(),
                "type": "error",
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
                "error_type": type(e).__name__,
                "duration_ms": round(duration * 1000, 2),
                "tenant_id": request.state.__dict__.get("tenant_id")
            }
            print(json.dumps(error_log))
            
            raise
