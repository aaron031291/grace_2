"""
Health Checker - System health monitoring
"""

import psutil
import time
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum


class HealthStatus(str, Enum):
    """Health check status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheck:
    """Individual health check result"""
    name: str
    status: HealthStatus
    message: str
    duration_ms: float
    timestamp: float


class HealthChecker:
    """Monitor system health"""
    
    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.last_results: Dict[str, HealthCheck] = {}
    
    def register_check(self, name: str, check_fn: Callable[[], tuple[HealthStatus, str]]):
        """Register a health check"""
        self.checks[name] = check_fn
    
    def run_checks(self) -> Dict[str, HealthCheck]:
        """Run all health checks"""
        results = {}
        
        for name, check_fn in self.checks.items():
            start_time = time.time()
            try:
                status, message = check_fn()
                duration_ms = (time.time() - start_time) * 1000
                
                result = HealthCheck(
                    name=name,
                    status=status,
                    message=message,
                    duration_ms=duration_ms,
                    timestamp=time.time()
                )
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                result = HealthCheck(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed: {str(e)}",
                    duration_ms=duration_ms,
                    timestamp=time.time()
                )
            
            results[name] = result
            self.last_results[name] = result
        
        return results
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status"""
        if not self.last_results:
            return HealthStatus.HEALTHY
        
        statuses = [check.status for check in self.last_results.values()]
        
        if any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    def get_system_metrics(self) -> dict:
        """Get system resource metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "active_connections": len(psutil.net_connections()),
            "process_count": len(psutil.pids())
        }
    
    @staticmethod
    def create_default_checks() -> 'HealthChecker':
        """Create health checker with default checks"""
        checker = HealthChecker()
        
        def check_cpu():
            cpu = psutil.cpu_percent(interval=0.1)
            if cpu > 90:
                return HealthStatus.UNHEALTHY, f"CPU usage critical: {cpu}%"
            elif cpu > 70:
                return HealthStatus.DEGRADED, f"CPU usage high: {cpu}%"
            else:
                return HealthStatus.HEALTHY, f"CPU usage normal: {cpu}%"
        
        def check_memory():
            memory = psutil.virtual_memory().percent
            if memory > 90:
                return HealthStatus.UNHEALTHY, f"Memory usage critical: {memory}%"
            elif memory > 70:
                return HealthStatus.DEGRADED, f"Memory usage high: {memory}%"
            else:
                return HealthStatus.HEALTHY, f"Memory usage normal: {memory}%"
        
        def check_disk():
            disk = psutil.disk_usage('/').percent
            if disk > 90:
                return HealthStatus.UNHEALTHY, f"Disk usage critical: {disk}%"
            elif disk > 80:
                return HealthStatus.DEGRADED, f"Disk usage high: {disk}%"
            else:
                return HealthStatus.HEALTHY, f"Disk usage normal: {disk}%"
        
        checker.register_check("cpu", check_cpu)
        checker.register_check("memory", check_memory)
        checker.register_check("disk", check_disk)
        
        return checker
