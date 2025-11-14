"""
Stress Test Metrics Aggregator
Consumes stress test telemetry and provides dashboard-ready metrics

Feeds:
- Real-time stress test status
- Historical pass/fail trends
- Performance regression detection
- Anomaly tracking
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field

from backend.core.message_bus import message_bus


@dataclass
class StressTestRun:
    """Single stress test run summary"""
    test_id: str
    test_type: str  # boot, ingestion, htm, etc.
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "running"
    total_cycles: int = 0
    successful_cycles: int = 0
    failed_cycles: int = 0
    avg_duration_ms: float = 0.0
    anomalies: List[Dict] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class StressMetricsAggregator:
    """
    Aggregates stress test metrics for dashboards and alerting
    
    Provides:
    - Current test status
    - Historical trends (last 24h, 7d, 30d)
    - Regression detection
    - Anomaly summaries
    """
    
    def __init__(self):
        self.active_tests: Dict[str, StressTestRun] = {}
        self.completed_tests: deque = deque(maxlen=100)  # Keep last 100 tests
        
        # Metrics history
        self.boot_times: deque = deque(maxlen=1000)
        self.kernel_counts: deque = deque(maxlen=1000)
        self.failure_events: deque = deque(maxlen=500)
        self.failure_patterns: Dict[str, int] = {}  # Track failure patterns
        
        # Aggregated stats
        self.total_tests_run = 0
        self.total_tests_passed = 0
        self.total_tests_failed = 0
        
        self.running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start metrics aggregator"""
        if self.running:
            return
        
        self.running = True
        
        # Subscribe to all stress telemetry
        try:
            queue = await message_bus.subscribe(
                subscriber="stress_metrics",
                topic="telemetry.stress"
            )
            self._task = asyncio.create_task(self._process_telemetry(queue))
            
            print("[STRESS-METRICS] Aggregator started, subscribed to telemetry")
        except Exception as e:
            print(f"[STRESS-METRICS] Failed to start: {e}")
    
    async def stop(self):
        """Stop metrics aggregator"""
        self.running = False
        if self._task:
            self._task.cancel()
    
    async def _process_telemetry(self, queue):
        """Process stress test telemetry events"""
        while self.running:
            try:
                msg = await queue.get()
                event_type = msg.topic.split('.')[-1]  # Last part of topic
                payload = msg.payload
                
                test_id = payload.get("test_id")
                
                # Handle different event types
                if event_type == "stress.run.started":
                    await self._handle_test_started(test_id, payload)
                
                elif event_type == "boot.cycle.completed":
                    await self._handle_boot_cycle(test_id, payload)
                
                elif event_type == "stress.run.completed":
                    await self._handle_test_completed(test_id, payload)
                
                elif "failed" in event_type:
                    await self._handle_failure(test_id, event_type, payload)
                
            except Exception as e:
                print(f"[STRESS-METRICS] Error processing telemetry: {e}")
                await asyncio.sleep(1)
    
    async def _handle_test_started(self, test_id: str, payload: Dict):
        """Handle stress test start event"""
        test_run = StressTestRun(
            test_id=test_id,
            test_type="boot",  # Could extract from test_id
            started_at=datetime.now(timezone.utc),
            total_cycles=payload.get("cycles", 0)
        )
        
        self.active_tests[test_id] = test_run
        self.total_tests_run += 1
    
    async def _handle_boot_cycle(self, test_id: str, payload: Dict):
        """Handle boot cycle completion"""
        if test_id not in self.active_tests:
            return
        
        test_run = self.active_tests[test_id]
        
        # Track metrics
        duration_ms = payload.get("boot_duration_ms", 0)
        kernels = payload.get("kernels", 0)
        anomalies = payload.get("anomalies", [])
        
        self.boot_times.append({
            "timestamp": datetime.now(timezone.utc),
            "duration_ms": duration_ms,
            "test_id": test_id
        })
        
        self.kernel_counts.append({
            "timestamp": datetime.now(timezone.utc),
            "count": kernels,
            "test_id": test_id
        })
        
        # Update test run
        test_run.successful_cycles += 1
        test_run.anomalies.extend(anomalies)
        
        # Calculate running average
        cycle_num = test_run.successful_cycles
        test_run.avg_duration_ms = (
            (test_run.avg_duration_ms * (cycle_num - 1) + duration_ms) / cycle_num
        )
    
    async def _handle_test_completed(self, test_id: str, payload: Dict):
        """Handle stress test completion"""
        if test_id not in self.active_tests:
            return
        
        test_run = self.active_tests[test_id]
        test_run.completed_at = datetime.now(timezone.utc)
        test_run.status = "completed"
        
        # Determine success
        if test_run.failed_cycles == 0 and len(test_run.anomalies) == 0:
            test_run.status = "passed"
            self.total_tests_passed += 1
        else:
            test_run.status = "failed"
            self.total_tests_failed += 1
        
        # Move to completed
        self.completed_tests.append(test_run)
        del self.active_tests[test_id]
    
    async def _handle_failure(self, test_id: str, event_type: str, payload: Dict):
        """Handle failure event"""
        self.failure_events.append({
            "timestamp": datetime.now(timezone.utc),
            "test_id": test_id,
            "event_type": event_type,
            "error": payload.get("error"),
            "payload": payload
        })
        
        # Update test run if active
        if test_id in self.active_tests:
            self.active_tests[test_id].failed_cycles += 1
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get metrics for dashboard display"""
        
        # Recent boot times (last 50)
        recent_boots = list(self.boot_times)[-50:]
        avg_boot_time = sum(b["duration_ms"] for b in recent_boots) / len(recent_boots) if recent_boots else 0
        
        # Recent kernel counts
        recent_kernels = list(self.kernel_counts)[-50:]
        avg_kernels = sum(k["count"] for k in recent_kernels) / len(recent_kernels) if recent_kernels else 0
        
        # Recent failures
        recent_failures = [f for f in self.failure_events if 
                          (datetime.now(timezone.utc) - f["timestamp"]).total_seconds() < 3600]
        
        # Success rate
        total = self.total_tests_passed + self.total_tests_failed
        success_rate = self.total_tests_passed / total if total > 0 else 0.0
        
        return {
            "current_status": {
                "active_tests": len(self.active_tests),
                "active_test_ids": list(self.active_tests.keys())
            },
            "performance": {
                "avg_boot_time_ms": avg_boot_time,
                "avg_kernels_activated": avg_kernels,
                "boot_time_trend": [b["duration_ms"] for b in recent_boots[-10:]]
            },
            "reliability": {
                "total_tests": total,
                "passed": self.total_tests_passed,
                "failed": self.total_tests_failed,
                "success_rate": success_rate,
                "failures_last_hour": len(recent_failures)
            },
            "anomalies": {
                "recent_count": len(recent_failures),
                "failure_patterns": dict(list(self.failure_patterns.items())[:10])
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_trend_data(self, hours: int = 24) -> Dict[str, Any]:
        """Get trend data for charts"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Filter recent data
        recent_boots = [b for b in self.boot_times if b["timestamp"] > cutoff]
        recent_failures = [f for f in self.failure_events if f["timestamp"] > cutoff]
        
        # Group by hour
        hourly_stats = defaultdict(lambda: {"boots": 0, "failures": 0, "avg_duration": 0})
        
        for boot in recent_boots:
            hour_key = boot["timestamp"].strftime("%Y-%m-%d %H:00")
            hourly_stats[hour_key]["boots"] += 1
            hourly_stats[hour_key]["avg_duration"] += boot["duration_ms"]
        
        for failure in recent_failures:
            hour_key = failure["timestamp"].strftime("%Y-%m-%d %H:00")
            hourly_stats[hour_key]["failures"] += 1
        
        # Calculate averages
        for stats in hourly_stats.values():
            if stats["boots"] > 0:
                stats["avg_duration"] /= stats["boots"]
        
        return {
            "hours": hours,
            "hourly_stats": dict(hourly_stats),
            "total_boots": len(recent_boots),
            "total_failures": len(recent_failures),
            "failure_rate": len(recent_failures) / len(recent_boots) if recent_boots else 0
        }


# Global instance
stress_metrics_aggregator = StressMetricsAggregator()
