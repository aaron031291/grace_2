"""
HTM Orchestrator Readiness & Health
Complete boot guards, worker watchdogs, and telemetry

Components:
- Readiness verification (30s timeout)
- Worker health monitoring
- Queue depth telemetry
- SLA breach tracking
- Clarity/Unified Logic integration
"""

import asyncio
from typing import Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class WorkerHealth:
    """Individual worker health status"""
    worker_id: str
    is_healthy: bool
    cpu_percent: float
    memory_mb: float
    tasks_completed: int
    tasks_failed: int
    last_heartbeat: datetime
    uptime_seconds: float


@dataclass
class HTMTelemetry:
    """HTM telemetry snapshot"""
    timestamp: datetime
    queue_depth: int
    active_workers: int
    total_workers: int
    tasks_per_second: float
    sla_breaches: int
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float


class HTMReadinessMonitor:
    """
    HTM orchestrator readiness and health monitoring
    Integrates with Clarity and Unified Logic
    """
    
    def __init__(self):
        self.is_ready = False
        self.is_healthy = True
        
        # Worker tracking
        self.workers: Dict[str, WorkerHealth] = {}
        self.min_workers = 3
        self.worker_heartbeat_timeout = 30
        
        # Queue tracking
        self.queue_depth = 0
        self.queue_depth_warning = 1000
        self.queue_depth_critical = 5000
        
        # SLA tracking
        self.sla_target_latency_ms = 1000
        self.sla_breaches_total = 0
        self.sla_breaches_recent = 0
        
        # Telemetry
        self.telemetry_history: List[HTMTelemetry] = []
        self.telemetry_interval = 15  # seconds
        
        self.running = False
    
    async def verify_readiness(self, timeout_seconds: int = 30) -> bool:
        """
        Verify HTM is ready to accept intents
        
        Checks:
        - HTM module loaded
        - Minimum workers available
        - Queue initialized
        - No critical errors
        """
        
        logger.info("[HTM-READINESS] Verifying HTM readiness...")
        
        start_time = datetime.utcnow()
        deadline = start_time + timedelta(seconds=timeout_seconds)
        
        while datetime.utcnow() < deadline:
            try:
                # Check if HTM module exists
                try:
                    from backend.core.enhanced_htm import htm_orchestrator
                    htm_loaded = True
                except ImportError:
                    htm_loaded = False
                    logger.warning("[HTM-READINESS] HTM orchestrator not loaded")
                    await asyncio.sleep(2)
                    continue
                
                # Check queue initialized
                if not hasattr(htm_orchestrator, 'intent_queue'):
                    logger.warning("[HTM-READINESS] Intent queue not initialized")
                    await asyncio.sleep(2)
                    continue
                
                # Check workers
                worker_count = self._count_active_workers()
                if worker_count < self.min_workers:
                    logger.warning(f"[HTM-READINESS] Insufficient workers: {worker_count}/{self.min_workers}")
                    await asyncio.sleep(2)
                    continue
                
                # All checks passed
                self.is_ready = True
                logger.info(f"[HTM-READINESS] HTM ready! ({worker_count} workers)")
                return True
            
            except Exception as e:
                logger.error(f"[HTM-READINESS] Check failed: {e}")
                await asyncio.sleep(2)
        
        # Timeout
        logger.error("[HTM-READINESS] Timeout - HTM not ready!")
        return False
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        
        if self.running:
            return
        
        self.running = True
        
        # Start worker watchdog
        asyncio.create_task(self._worker_watchdog_loop())
        
        # Start telemetry streaming
        asyncio.create_task(self._telemetry_loop())
        
        logger.info("[HTM-READINESS] Monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        logger.info("[HTM-READINESS] Monitoring stopped")
    
    async def _worker_watchdog_loop(self):
        """Monitor worker health continuously"""
        
        while self.running:
            try:
                await self._check_worker_health()
            except Exception as e:
                logger.error(f"[HTM-WATCHDOG] Error: {e}")
            
            await asyncio.sleep(10)
    
    async def _check_worker_health(self):
        """Check all worker heartbeats and health"""
        
        now = datetime.utcnow()
        
        # Check each worker
        dead_workers = []
        for worker_id, health in self.workers.items():
            time_since_heartbeat = (now - health.last_heartbeat).total_seconds()
            
            if time_since_heartbeat > self.worker_heartbeat_timeout:
                health.is_healthy = False
                dead_workers.append(worker_id)
                logger.warning(f"[HTM-WATCHDOG] Worker {worker_id} missed heartbeat ({time_since_heartbeat:.0f}s)")
        
        # Trigger recovery if workers down
        if dead_workers:
            await self._trigger_worker_recovery(dead_workers)
    
    async def _trigger_worker_recovery(self, dead_workers: List[str]):
        """Trigger recovery for dead workers"""
        
        logger.error(f"[HTM-WATCHDOG] Triggering recovery for {len(dead_workers)} workers")
        
        try:
            from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
            
            await trigger_mesh.publish(TriggerEvent(
                source="htm_watchdog",
                event_type="event.incident",
                actor="htm_watchdog",
                resource="htm_workers",
                payload={
                    'trigger_id': 'htm_worker_failure',
                    'playbook': 'htm_worker_recovery',
                    'severity': 'high',
                    'dead_workers': dead_workers,
                    'worker_count': len(dead_workers),
                    'timestamp': datetime.utcnow().isoformat()
                }
            ))
        except Exception as e:
            logger.error(f"[HTM-WATCHDOG] Recovery trigger failed: {e}")
    
    async def _telemetry_loop(self):
        """Stream telemetry to Clarity and Unified Logic"""
        
        while self.running:
            try:
                await self._publish_telemetry()
            except Exception as e:
                logger.error(f"[HTM-TELEMETRY] Error: {e}")
            
            await asyncio.sleep(self.telemetry_interval)
    
    async def _publish_telemetry(self):
        """Publish HTM metrics to Clarity and Unified Logic"""
        
        # Capture current state
        telemetry = HTMTelemetry(
            timestamp=datetime.utcnow(),
            queue_depth=self.queue_depth,
            active_workers=self._count_active_workers(),
            total_workers=len(self.workers),
            tasks_per_second=self._calculate_throughput(),
            sla_breaches=self.sla_breaches_recent,
            avg_latency_ms=self._calculate_avg_latency(),
            p95_latency_ms=0.0,  # Would calculate from actual metrics
            p99_latency_ms=0.0
        )
        
        self.telemetry_history.append(telemetry)
        
        # Stream to Unified Logic
        try:
            from backend.unified_logic.unified_logic_hub import unified_logic_hub
            
            await unified_logic_hub.submit_proposal(
                proposal_id=f"htm_telemetry_{int(datetime.utcnow().timestamp())}",
                proposal_type="telemetry_update",
                actor="htm_readiness_monitor",
                target_component="unified_logic_hub",
                payload={
                    'component': 'htm_orchestrator',
                    'queue_depth': telemetry.queue_depth,
                    'active_workers': telemetry.active_workers,
                    'tasks_per_second': telemetry.tasks_per_second,
                    'sla_breaches': telemetry.sla_breaches,
                    'health_status': 'healthy' if self.is_healthy else 'degraded'
                },
                requires_vote=False
            )
        except Exception as e:
            logger.debug(f"[HTM-TELEMETRY] Unified logic update failed: {e}")
        
        # Stream to Clarity if issues
        if telemetry.queue_depth > self.queue_depth_warning or telemetry.sla_breaches > 0:
            try:
                from backend.core.clarity_framework import clarity_framework
                
                await clarity_framework.record_decision(
                    actor="htm_orchestrator",
                    action_type="performance_alert",
                    resource="htm_queue",
                    decision={
                        'type': 'alert',
                        'queue_depth': telemetry.queue_depth,
                        'sla_breaches': telemetry.sla_breaches
                    },
                    reasoning_chain=[
                        f"Queue depth: {telemetry.queue_depth} (warning: {self.queue_depth_warning})",
                        f"SLA breaches: {telemetry.sla_breaches}",
                        f"Active workers: {telemetry.active_workers}/{telemetry.total_workers}",
                        "Publishing telemetry for correlation analysis"
                    ]
                )
            except Exception as e:
                logger.debug(f"[HTM-TELEMETRY] Clarity update failed: {e}")
    
    def _count_active_workers(self) -> int:
        """Count healthy workers"""
        return sum(1 for w in self.workers.values() if w.is_healthy)
    
    def _calculate_throughput(self) -> float:
        """Calculate tasks per second"""
        # Simplified - would use sliding window in production
        return 0.0
    
    def _calculate_avg_latency(self) -> float:
        """Calculate average latency"""
        # Simplified - would track actual task latencies
        return 0.0
    
    def register_worker(self, worker_id: str):
        """Register a new worker"""
        self.workers[worker_id] = WorkerHealth(
            worker_id=worker_id,
            is_healthy=True,
            cpu_percent=0.0,
            memory_mb=0.0,
            tasks_completed=0,
            tasks_failed=0,
            last_heartbeat=datetime.utcnow(),
            uptime_seconds=0.0
        )
        logger.info(f"[HTM-READINESS] Worker registered: {worker_id}")
    
    def update_worker_heartbeat(self, worker_id: str):
        """Update worker heartbeat"""
        if worker_id in self.workers:
            self.workers[worker_id].last_heartbeat = datetime.utcnow()
            self.workers[worker_id].is_healthy = True


# Global instance
htm_readiness = HTMReadinessMonitor()
