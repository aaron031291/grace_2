"""
Metrics Collection - Golden signals and custom metrics
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
from threading import Lock
import statistics


@dataclass
class GoldenSignals:
    """The four golden signals of monitoring"""
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0
    
    requests_per_second: float = 0.0
    requests_total: int = 0
    
    error_rate: float = 0.0
    errors_total: int = 0
    
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_percent: float = 0.0
    active_connections: int = 0


class MetricsCollector:
    """Collect and aggregate metrics"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.latencies: deque = deque(maxlen=window_size)
        self.requests_by_endpoint: Dict[str, int] = defaultdict(int)
        self.errors_by_endpoint: Dict[str, int] = defaultdict(int)
        self.requests_by_tenant: Dict[str, int] = defaultdict(int)
        self.errors_by_tenant: Dict[str, int] = defaultdict(int)
        
        self.total_requests = 0
        self.total_errors = 0
        self.start_time = time.time()
        
        self.lock = Lock()
    
    def record_request(
        self,
        endpoint: str,
        duration_ms: float,
        status_code: int,
        tenant_id: Optional[str] = None
    ):
        """Record a request with its metrics"""
        with self.lock:
            self.latencies.append(duration_ms)
            self.requests_by_endpoint[endpoint] += 1
            self.total_requests += 1
            
            if tenant_id:
                self.requests_by_tenant[tenant_id] += 1
            
            if status_code >= 500:
                self.errors_by_endpoint[endpoint] += 1
                self.total_errors += 1
                if tenant_id:
                    self.errors_by_tenant[tenant_id] += 1
    
    def get_golden_signals(self) -> GoldenSignals:
        """Calculate golden signals from collected metrics"""
        with self.lock:
            if self.latencies:
                sorted_latencies = sorted(self.latencies)
                p50 = self._percentile(sorted_latencies, 50)
                p95 = self._percentile(sorted_latencies, 95)
                p99 = self._percentile(sorted_latencies, 99)
            else:
                p50 = p95 = p99 = 0.0
            
            elapsed = time.time() - self.start_time
            rps = self.total_requests / elapsed if elapsed > 0 else 0.0
            
            error_rate = (
                self.total_errors / self.total_requests
                if self.total_requests > 0
                else 0.0
            )
            
            return GoldenSignals(
                latency_p50_ms=p50,
                latency_p95_ms=p95,
                latency_p99_ms=p99,
                requests_per_second=rps,
                requests_total=self.total_requests,
                error_rate=error_rate,
                errors_total=self.total_errors
            )
    
    def get_endpoint_stats(self) -> Dict[str, dict]:
        """Get per-endpoint statistics"""
        with self.lock:
            stats = {}
            for endpoint, count in self.requests_by_endpoint.items():
                errors = self.errors_by_endpoint.get(endpoint, 0)
                stats[endpoint] = {
                    "requests": count,
                    "errors": errors,
                    "error_rate": errors / count if count > 0 else 0.0
                }
            return stats
    
    def get_tenant_stats(self, tenant_id: str) -> dict:
        """Get statistics for a specific tenant"""
        with self.lock:
            requests = self.requests_by_tenant.get(tenant_id, 0)
            errors = self.errors_by_tenant.get(tenant_id, 0)
            return {
                "requests": requests,
                "errors": errors,
                "error_rate": errors / requests if requests > 0 else 0.0
            }
    
    def reset(self):
        """Reset all metrics"""
        with self.lock:
            self.latencies.clear()
            self.requests_by_endpoint.clear()
            self.errors_by_endpoint.clear()
            self.requests_by_tenant.clear()
            self.errors_by_tenant.clear()
            self.total_requests = 0
            self.total_errors = 0
            self.start_time = time.time()
    
    @staticmethod
    def _percentile(sorted_data: List[float], percentile: int) -> float:
        """Calculate percentile from sorted data"""
        if not sorted_data:
            return 0.0
        
        index = (percentile / 100) * (len(sorted_data) - 1)
        lower = int(index)
        upper = lower + 1
        
        if upper >= len(sorted_data):
            return sorted_data[-1]
        
        weight = index - lower
        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight
