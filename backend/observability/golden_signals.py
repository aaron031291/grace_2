"""
Golden Signals Monitoring
Tracks Latency, Traffic, Errors, Saturation (Google SRE methodology)
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import deque
import time
import statistics
import psutil

@dataclass
class LatencyMetrics:
    """Latency tracking"""
    p50: float
    p95: float
    p99: float
    average: float
    max: float
    sample_count: int

@dataclass
class TrafficMetrics:
    """Traffic/throughput tracking"""
    requests_per_second: float
    total_requests: int
    requests_last_minute: int
    requests_last_hour: int

@dataclass
class ErrorMetrics:
    """Error rate tracking"""
    total_errors: int
    error_rate_percent: float
    errors_last_minute: int
    errors_by_type: Dict[str, int]

@dataclass
class SaturationMetrics:
    """Resource saturation tracking"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    connections: int
    queue_depth: int

class GoldenSignalsMonitor:
    """Monitors the four golden signals"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        
        # Latency tracking
        self.latencies: deque = deque(maxlen=window_size)
        
        # Traffic tracking
        self.request_timestamps: deque = deque(maxlen=10000)
        self.total_requests = 0
        
        # Error tracking
        self.error_timestamps: deque = deque(maxlen=1000)
        self.total_errors = 0
        self.errors_by_type: Dict[str, int] = {}
        
        # Saturation tracking
        self.queue_depth = 0
        
    def record_request(self, latency_ms: float, status_code: int, error_type: Optional[str] = None):
        """Record a request with latency and status"""
        now = time.time()
        
        # Record latency
        self.latencies.append(latency_ms)
        
        # Record traffic
        self.request_timestamps.append(now)
        self.total_requests += 1
        
        # Record errors
        if status_code >= 400:
            self.error_timestamps.append(now)
            self.total_errors += 1
            
            if error_type:
                self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1
    
    def get_latency_metrics(self) -> LatencyMetrics:
        """Get latency metrics"""
        if not self.latencies:
            return LatencyMetrics(
                p50=0, p95=0, p99=0, average=0, max=0, sample_count=0
            )
        
        sorted_latencies = sorted(self.latencies)
        count = len(sorted_latencies)
        
        return LatencyMetrics(
            p50=sorted_latencies[int(count * 0.5)],
            p95=sorted_latencies[int(count * 0.95)] if count > 1 else sorted_latencies[0],
            p99=sorted_latencies[int(count * 0.99)] if count > 1 else sorted_latencies[0],
            average=statistics.mean(self.latencies),
            max=max(self.latencies),
            sample_count=count
        )
    
    def get_traffic_metrics(self) -> TrafficMetrics:
        """Get traffic metrics"""
        now = time.time()
        
        # Count requests in last minute
        minute_ago = now - 60
        requests_last_minute = sum(1 for ts in self.request_timestamps if ts > minute_ago)
        
        # Count requests in last hour
        hour_ago = now - 3600
        requests_last_hour = sum(1 for ts in self.request_timestamps if ts > hour_ago)
        
        # Calculate RPS (from last minute)
        rps = requests_last_minute / 60.0
        
        return TrafficMetrics(
            requests_per_second=rps,
            total_requests=self.total_requests,
            requests_last_minute=requests_last_minute,
            requests_last_hour=requests_last_hour
        )
    
    def get_error_metrics(self) -> ErrorMetrics:
        """Get error metrics"""
        now = time.time()
        
        # Count errors in last minute
        minute_ago = now - 60
        errors_last_minute = sum(1 for ts in self.error_timestamps if ts > minute_ago)
        
        # Calculate error rate
        error_rate = (
            self.total_errors / self.total_requests * 100
            if self.total_requests > 0 else 0
        )
        
        return ErrorMetrics(
            total_errors=self.total_errors,
            error_rate_percent=error_rate,
            errors_last_minute=errors_last_minute,
            errors_by_type=dict(self.errors_by_type)
        )
    
    def get_saturation_metrics(self) -> SaturationMetrics:
        """Get resource saturation metrics"""
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        # Count active connections
        connections = len(psutil.net_connections())
        
        return SaturationMetrics(
            cpu_percent=cpu,
            memory_percent=memory,
            disk_percent=disk,
            connections=connections,
            queue_depth=self.queue_depth
        )
    
    def get_all_signals(self) -> Dict[str, Any]:
        """Get all golden signals"""
        latency = self.get_latency_metrics()
        traffic = self.get_traffic_metrics()
        errors = self.get_error_metrics()
        saturation = self.get_saturation_metrics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "latency": {
                "p50_ms": latency.p50,
                "p95_ms": latency.p95,
                "p99_ms": latency.p99,
                "average_ms": latency.average,
                "max_ms": latency.max,
                "sample_count": latency.sample_count,
                "target_p95_ms": 200,  # Target < 200ms
                "target_met": latency.p95 < 200
            },
            "traffic": {
                "requests_per_second": traffic.requests_per_second,
                "total_requests": traffic.total_requests,
                "requests_last_minute": traffic.requests_last_minute,
                "requests_last_hour": traffic.requests_last_hour
            },
            "errors": {
                "total_errors": errors.total_errors,
                "error_rate_percent": errors.error_rate_percent,
                "errors_last_minute": errors.errors_last_minute,
                "errors_by_type": errors.errors_by_type,
                "target_error_rate": 1.0,  # Target < 1%
                "target_met": errors.error_rate_percent < 1.0
            },
            "saturation": {
                "cpu_percent": saturation.cpu_percent,
                "memory_percent": saturation.memory_percent,
                "disk_percent": saturation.disk_percent,
                "connections": saturation.connections,
                "queue_depth": saturation.queue_depth,
                "targets": {
                    "cpu_percent": 80,
                    "memory_percent": 85,
                    "disk_percent": 90
                },
                "targets_met": {
                    "cpu": saturation.cpu_percent < 80,
                    "memory": saturation.memory_percent < 85,
                    "disk": saturation.disk_percent < 90
                }
            },
            "slo_status": {
                "latency_slo_met": latency.p95 < 200,
                "error_slo_met": errors.error_rate_percent < 1.0,
                "saturation_slo_met": saturation.cpu_percent < 80 and saturation.memory_percent < 85,
                "overall_slo_met": (
                    latency.p95 < 200 and 
                    errors.error_rate_percent < 1.0 and 
                    saturation.cpu_percent < 80
                )
            }
        }

# Global instance
_golden_signals: Optional[GoldenSignalsMonitor] = None

def get_golden_signals() -> GoldenSignalsMonitor:
    """Get global golden signals monitor"""
    global _golden_signals
    if _golden_signals is None:
        _golden_signals = GoldenSignalsMonitor()
    return _golden_signals

def record_request(latency_ms: float, status_code: int, error_type: Optional[str] = None):
    """Record a request in golden signals"""
    monitor = get_golden_signals()
    monitor.record_request(latency_ms, status_code, error_type)
