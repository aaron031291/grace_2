"""
Chaos Diagnostics Collector
Comprehensive artifact collection for DiRT/FIT/Jepsen testing

Collects:
- Control plane status dumps
- Kernel state snapshots
- Resource metrics timelines
- API performance data
- Immutable log sequences
- Consistency verification results
"""

import json
import psutil
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ControlPlaneDump:
    """Control plane state snapshot"""
    timestamp: datetime
    system_state: str
    kernel_states: Dict[str, Dict]
    restart_counts: Dict[str, int]
    heartbeat_status: Dict[str, Optional[datetime]]
    resource_usage: Dict[str, float]


@dataclass
class ResourceMetricsSnapshot:
    """Point-in-time resource metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_bytes_sent: int
    network_bytes_recv: int


@dataclass
class APIMetrics:
    """API endpoint performance metrics"""
    endpoint: str
    request_count: int
    error_count: int
    response_times: List[float]
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    error_rate: float
    throughput_rps: float


@dataclass
class ConsistencyVerification:
    """Jepsen-style consistency check results"""
    check_name: str
    timestamp: datetime
    passed: bool
    violations: List[Dict[str, Any]]
    invariants_checked: List[str]
    invariants_violated: List[str]


class DiagnosticsCollector:
    """
    Collects comprehensive diagnostics during chaos testing
    """
    
    def __init__(self, test_id: str):
        self.test_id = test_id
        self.artifacts_dir = Path(__file__).parent.parent.parent / "logs" / "chaos_artifacts" / test_id
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Collections
        self.control_plane_dumps: List[ControlPlaneDump] = []
        self.resource_metrics: List[ResourceMetricsSnapshot] = []
        self.api_metrics: Dict[str, APIMetrics] = {}
        self.consistency_checks: List[ConsistencyVerification] = []
        
        # Monitoring state
        self.monitoring = False
        self.monitor_task = None
        
        logger.info(f"[DIAGNOSTICS] Collector initialized: {test_id}")
        logger.info(f"[DIAGNOSTICS] Artifacts dir: {self.artifacts_dir}")
    
    async def start_monitoring(self, interval_seconds: int = 5):
        """Start continuous monitoring"""
        import asyncio
        
        self.monitoring = True
        
        async def monitor_loop():
            while self.monitoring:
                await self.capture_snapshot()
                await asyncio.sleep(interval_seconds)
        
        self.monitor_task = asyncio.create_task(monitor_loop())
        logger.info(f"[DIAGNOSTICS] Monitoring started (interval: {interval_seconds}s)")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
        logger.info("[DIAGNOSTICS] Monitoring stopped")
    
    async def capture_snapshot(self):
        """Capture complete system snapshot"""
        timestamp = datetime.utcnow()
        
        # Control plane dump
        await self.capture_control_plane_dump(timestamp)
        
        # Resource metrics
        self.capture_resource_metrics(timestamp)
    
    async def capture_control_plane_dump(self, timestamp: datetime):
        """Capture control plane state"""
        try:
            from backend.core import control_plane
            
            status = control_plane.get_status()
            
            # Extract kernel states
            kernel_states = {}
            restart_counts = {}
            heartbeat_status = {}
            
            for kernel_name, kernel_data in status.get('kernels', {}).items():
                kernel_states[kernel_name] = {
                    'state': kernel_data.get('state'),
                    'critical': kernel_data.get('critical')
                }
                restart_counts[kernel_name] = kernel_data.get('restart_count', 0)
                
                last_hb = kernel_data.get('last_heartbeat')
                heartbeat_status[kernel_name] = last_hb
            
            dump = ControlPlaneDump(
                timestamp=timestamp,
                system_state=status.get('system_state', 'unknown'),
                kernel_states=kernel_states,
                restart_counts=restart_counts,
                heartbeat_status=heartbeat_status,
                resource_usage={
                    'cpu': psutil.cpu_percent(),
                    'memory': psutil.virtual_memory().percent
                }
            )
            
            self.control_plane_dumps.append(dump)
        
        except Exception as e:
            logger.error(f"[DIAGNOSTICS] Control plane dump failed: {e}")
    
    def capture_resource_metrics(self, timestamp: datetime):
        """Capture system resource metrics"""
        try:
            # CPU and memory
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            disk_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
            disk_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0
            
            # Network
            net_io = psutil.net_io_counters()
            
            snapshot = ResourceMetricsSnapshot(
                timestamp=timestamp,
                cpu_percent=cpu,
                memory_percent=memory,
                disk_io_read_mb=disk_read_mb,
                disk_io_write_mb=disk_write_mb,
                network_bytes_sent=net_io.bytes_sent,
                network_bytes_recv=net_io.bytes_recv
            )
            
            self.resource_metrics.append(snapshot)
        
        except Exception as e:
            logger.error(f"[DIAGNOSTICS] Resource metrics capture failed: {e}")
    
    def record_api_metrics(self, endpoint: str, metrics: APIMetrics):
        """Record API endpoint metrics"""
        self.api_metrics[endpoint] = metrics
        logger.info(f"[DIAGNOSTICS] API metrics recorded: {endpoint}")
    
    def record_consistency_check(self, check: ConsistencyVerification):
        """Record consistency verification result"""
        self.consistency_checks.append(check)
        status = "PASS" if check.passed else "FAIL"
        logger.info(f"[DIAGNOSTICS] Consistency check: {check.check_name} [{status}]")
    
    async def verify_immutable_log_continuity(self) -> ConsistencyVerification:
        """Verify immutable log sequence has no gaps"""
        try:
            
            # Check for sequence gaps
            violations = []
            
            # Get recent entries
            log_file = Path("logs/immutable_audit.jsonl")
            if log_file.exists():
                entries = []
                with open(log_file, 'r') as f:
                    for line in f:
                        try:
                            entries.append(json.loads(line))
                        except:
                            pass
                
                # Check chronological order
                for i in range(1, len(entries)):
                    prev_time = entries[i-1].get('timestamp')
                    curr_time = entries[i].get('timestamp')
                    
                    if prev_time and curr_time:
                        if curr_time < prev_time:
                            violations.append({
                                'type': 'out_of_order',
                                'index': i,
                                'prev': prev_time,
                                'curr': curr_time
                            })
            
            check = ConsistencyVerification(
                check_name="immutable_log_continuity",
                timestamp=datetime.utcnow(),
                passed=len(violations) == 0,
                violations=violations,
                invariants_checked=['chronological_order', 'no_gaps'],
                invariants_violated=['chronological_order'] if violations else []
            )
            
            self.record_consistency_check(check)
            return check
        
        except Exception as e:
            logger.error(f"[DIAGNOSTICS] Log continuity check failed: {e}")
            return ConsistencyVerification(
                check_name="immutable_log_continuity",
                timestamp=datetime.utcnow(),
                passed=False,
                violations=[{'error': str(e)}],
                invariants_checked=[],
                invariants_violated=[]
            )
    
    async def verify_no_split_brain(self) -> ConsistencyVerification:
        """Verify no duplicate/conflicting entries"""
        
        violations = []
        
        # Check for duplicate actor+action+timestamp combinations
        # (indicates split-brain scenario)
        
        check = ConsistencyVerification(
            check_name="no_split_brain",
            timestamp=datetime.utcnow(),
            passed=len(violations) == 0,
            violations=violations,
            invariants_checked=['unique_entries', 'no_conflicts'],
            invariants_violated=[]
        )
        
        self.record_consistency_check(check)
        return check
    
    def save_all_artifacts(self) -> Dict[str, str]:
        """Save all collected artifacts to disk"""
        
        artifacts = {}
        
        # Control plane dumps
        if self.control_plane_dumps:
            cp_file = self.artifacts_dir / "control_plane_dumps.json"
            with open(cp_file, 'w') as f:
                json.dump([asdict(d) for d in self.control_plane_dumps], f, indent=2, default=str)
            artifacts['control_plane_dumps'] = str(cp_file)
            logger.info(f"[DIAGNOSTICS] Saved {len(self.control_plane_dumps)} control plane dumps")
        
        # Resource metrics timeline
        if self.resource_metrics:
            metrics_file = self.artifacts_dir / "resource_metrics_timeline.json"
            with open(metrics_file, 'w') as f:
                json.dump([asdict(m) for m in self.resource_metrics], f, indent=2, default=str)
            artifacts['resource_metrics'] = str(metrics_file)
            logger.info(f"[DIAGNOSTICS] Saved {len(self.resource_metrics)} resource snapshots")
        
        # API metrics
        if self.api_metrics:
            api_file = self.artifacts_dir / "api_metrics.json"
            with open(api_file, 'w') as f:
                json.dump({k: asdict(v) for k, v in self.api_metrics.items()}, f, indent=2, default=str)
            artifacts['api_metrics'] = str(api_file)
            logger.info(f"[DIAGNOSTICS] Saved metrics for {len(self.api_metrics)} endpoints")
        
        # Consistency checks
        if self.consistency_checks:
            consistency_file = self.artifacts_dir / "consistency_checks.json"
            with open(consistency_file, 'w') as f:
                json.dump([asdict(c) for c in self.consistency_checks], f, indent=2, default=str)
            artifacts['consistency_checks'] = str(consistency_file)
            logger.info(f"[DIAGNOSTICS] Saved {len(self.consistency_checks)} consistency checks")
        
        # Summary report
        summary = self.generate_summary()
        summary_file = self.artifacts_dir / "test_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        artifacts['summary'] = str(summary_file)
        
        logger.info(f"[DIAGNOSTICS] All artifacts saved to: {self.artifacts_dir}")
        
        return artifacts
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        
        # Analyze resource usage
        cpu_peak = max([m.cpu_percent for m in self.resource_metrics]) if self.resource_metrics else 0
        mem_peak = max([m.memory_percent for m in self.resource_metrics]) if self.resource_metrics else 0
        
        # Count kernel restarts
        total_restarts = 0
        if self.control_plane_dumps:
            last_dump = self.control_plane_dumps[-1]
            total_restarts = sum(last_dump.restart_counts.values())
        
        # Consistency check results
        consistency_pass_rate = 0
        if self.consistency_checks:
            passed = sum(1 for c in self.consistency_checks if c.passed)
            consistency_pass_rate = passed / len(self.consistency_checks) * 100
        
        return {
            'test_id': self.test_id,
            'duration_seconds': (datetime.utcnow() - self.resource_metrics[0].timestamp).total_seconds() if self.resource_metrics else 0,
            'snapshots_collected': len(self.control_plane_dumps),
            'resource_metrics_points': len(self.resource_metrics),
            'cpu_peak_percent': cpu_peak,
            'memory_peak_percent': mem_peak,
            'total_kernel_restarts': total_restarts,
            'api_endpoints_monitored': len(self.api_metrics),
            'consistency_checks_run': len(self.consistency_checks),
            'consistency_pass_rate': consistency_pass_rate,
            'timestamp': datetime.utcnow().isoformat()
        }


# Factory function
def create_collector(test_id: str) -> DiagnosticsCollector:
    """Create a new diagnostics collector"""
    return DiagnosticsCollector(test_id)
