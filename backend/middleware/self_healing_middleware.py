"""
Self-Healing Middleware
Captures API errors, timeouts, and KPIs to feed trigger system

Monitors:
- Response times (latency)
- Error rates (5xx, timeouts)
- Request patterns
- Resource usage during requests

Feeds data to trigger system for proactive healing.
"""

import time
from datetime import datetime
from typing import Callable
from collections import deque

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class SelfHealingMiddleware(BaseHTTPMiddleware):
    """Middleware that captures metrics for self-healing triggers"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
        # Metrics storage
        self.request_latencies = deque(maxlen=1000)
        self.error_counts = deque(maxlen=100)
        self.endpoint_stats = {}
        
        # KPI tracking
        self.kpi_values = {
            "api_latency_p95": 0.0,
            "error_rate": 0.0,
            "requests_per_minute": 0.0
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and capture metrics"""
        
        start_time = time.time()
        endpoint = f"{request.method} {request.url.path}"
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Record metrics
            self.request_latencies.append(latency_ms)
            
            # Track per-endpoint stats
            if endpoint not in self.endpoint_stats:
                self.endpoint_stats[endpoint] = {
                    "count": 0,
                    "total_latency": 0.0,
                    "errors": 0
                }
            
            self.endpoint_stats[endpoint]["count"] += 1
            self.endpoint_stats[endpoint]["total_latency"] += latency_ms
            
            # Check for errors
            if response.status_code >= 500:
                self.error_counts.append({
                    "timestamp": datetime.utcnow(),
                    "endpoint": endpoint,
                    "status_code": response.status_code
                })
                
                self.endpoint_stats[endpoint]["errors"] += 1
                
                # Feed to trigger system
                await self._notify_trigger_system(
                    "api_error",
                    endpoint,
                    response.status_code
                )
            
            # Check for slow responses
            if latency_ms > 1000:  # > 1 second
                await self._notify_trigger_system(
                    "slow_response",
                    endpoint,
                    latency_ms
                )
            
            # Update KPIs
            await self._update_kpis()
            
            return response
        
        except Exception as e:
            # Request timeout or exception
            latency_ms = (time.time() - start_time) * 1000
            
            self.error_counts.append({
                "timestamp": datetime.utcnow(),
                "endpoint": endpoint,
                "error": str(e)
            })
            
            # Feed to trigger system
            await self._notify_trigger_system(
                "api_timeout",
                endpoint,
                500
            )
            
            raise
    
    async def _notify_trigger_system(self, error_type: str, endpoint: str, value: Any):
        """Notify trigger system of issue"""
        
        try:
            # Dynamically import to avoid circular dependency
            from backend.self_heal.trigger_system import trigger_manager
            
            if error_type in ["api_error", "api_timeout"]:
                await trigger_manager.record_api_error(
                    endpoint,
                    int(value) if isinstance(value, (int, float)) else 500,
                    error_type
                )
            
            # Record as event for anomaly detection
            await trigger_manager.record_event(f"{error_type}:{endpoint}")
        
        except Exception as e:
            print(f"[MIDDLEWARE] Failed to notify trigger system: {e}")
    
    async def _update_kpis(self):
        """Update KPI values for trigger system"""
        
        try:
            # Calculate P95 latency
            if self.request_latencies:
                sorted_latencies = sorted(self.request_latencies)
                p95_index = int(len(sorted_latencies) * 0.95)
                self.kpi_values["api_latency_p95"] = sorted_latencies[p95_index]
            
            # Calculate error rate
            if self.error_counts:
                recent_errors = [
                    e for e in self.error_counts 
                    if (datetime.utcnow() - e["timestamp"]).total_seconds() < 300
                ]
                total_requests = len(self.request_latencies)
                self.kpi_values["error_rate"] = (len(recent_errors) / max(total_requests, 1)) * 100
            
            # Update trigger system
            from backend.self_heal.trigger_system import trigger_manager
            
            for kpi_name, value in self.kpi_values.items():
                await trigger_manager.update_kpi(kpi_name, value)
        
        except Exception as e:
            print(f"[MIDDLEWARE] KPI update error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get middleware statistics"""
        return {
            "total_requests": len(self.request_latencies),
            "total_errors": len(self.error_counts),
            "kpis": self.kpi_values,
            "endpoint_stats": self.endpoint_stats
        }
