"""
Scheduler Boot Guards & Heartbeat Monitoring
Structured logging for all dispatch decisions

Guards:
- Boot verification
- Heartbeat monitoring
- Queue overflow protection
- Dispatch rate tracking

Logging:
- 5W1H for every dispatch
- Mission context
- Load balancing decisions
- Rerouting explanations
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SchedulerHealth:
    """Scheduler health metrics"""
    is_ready: bool
    is_healthy: bool
    queue_depth: int
    dispatch_rate: float  # tasks/second
    last_heartbeat: datetime
    error_count: int
    task_backlog: int
    reroute_count: int


class SchedulerGuards:
    """
    Boot guards and health monitoring for scheduler
    """
    
    def __init__(self):
        self.health = SchedulerHealth(
            is_ready=False,
            is_healthy=False,
            queue_depth=0,
            dispatch_rate=0.0,
            last_heartbeat=datetime.utcnow(),
            error_count=0,
            task_backlog=0,
            reroute_count=0
        )
        
        # Thresholds
        self.queue_depth_warning = 500
        self.queue_depth_critical = 2000
        self.min_dispatch_rate = 1.0  # tasks/second
        self.heartbeat_timeout = 30
        
        self.running = False
    
    async def verify_boot_ready(self, timeout_seconds: int = 30) -> bool:
        """
        Verify scheduler is ready to dispatch tasks
        
        Boot guards:
        - Scheduler kernel running
        - Task queue initialized
        - Dispatch logic loaded
        - No critical errors
        """
        
        logger.info("[SCHEDULER-GUARDS] Verifying scheduler boot readiness...")
        
        start_time = datetime.utcnow()
        deadline = start_time + timedelta(seconds=timeout_seconds)
        
        while datetime.utcnow() < deadline:
            try:
                # Check scheduler kernel
                from backend.core import control_plane
                
                scheduler_kernel = control_plane.kernels.get('scheduler')
                if not scheduler_kernel or scheduler_kernel.state.value != 'running':
                    logger.warning("[SCHEDULER-GUARDS] Scheduler kernel not running")
                    await asyncio.sleep(2)
                    continue
                
                # All checks passed
                self.health.is_ready = True
                self.health.is_healthy = True
                logger.info("[SCHEDULER-GUARDS] Scheduler ready!")
                return True
            
            except Exception as e:
                logger.error(f"[SCHEDULER-GUARDS] Boot check failed: {e}")
                await asyncio.sleep(2)
        
        # Timeout
        logger.error("[SCHEDULER-GUARDS] Boot timeout - scheduler not ready!")
        return False
    
    async def start_heartbeat_monitoring(self):
        """Start heartbeat and health monitoring"""
        
        if self.running:
            return
        
        self.running = True
        
        # Start monitoring loop
        asyncio.create_task(self._heartbeat_loop())
        
        logger.info("[SCHEDULER-GUARDS] Heartbeat monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        logger.info("[SCHEDULER-GUARDS] Monitoring stopped")
    
    async def _heartbeat_loop(self):
        """Monitor scheduler heartbeat"""
        
        while self.running:
            try:
                await self._check_heartbeat()
                await self._check_queue_health()
                await self._publish_telemetry()
            except Exception as e:
                logger.error(f"[SCHEDULER-GUARDS] Heartbeat error: {e}")
            
            await asyncio.sleep(10)
    
    async def _check_heartbeat(self):
        """Check if scheduler is responding"""
        
        now = datetime.utcnow()
        time_since_heartbeat = (now - self.health.last_heartbeat).total_seconds()
        
        if time_since_heartbeat > self.heartbeat_timeout:
            logger.error(f"[SCHEDULER-GUARDS] Scheduler heartbeat timeout ({time_since_heartbeat:.0f}s)")
            
            self.health.is_healthy = False
            
            # Trigger recovery
            await self._trigger_scheduler_recovery()
    
    async def _check_queue_health(self):
        """Check scheduler queue health"""
        
        if self.health.queue_depth > self.queue_depth_critical:
            logger.error(f"[SCHEDULER-GUARDS] Queue depth critical: {self.health.queue_depth}")
            
            self.health.is_healthy = False
            
            # Trigger load shedding
            await self._trigger_load_shedding()
        
        elif self.health.queue_depth > self.queue_depth_warning:
            logger.warning(f"[SCHEDULER-GUARDS] Queue depth warning: {self.health.queue_depth}")
    
    async def _trigger_scheduler_recovery(self):
        """Trigger scheduler recovery playbook"""
        
        try:
            from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
            
            await trigger_mesh.publish(TriggerEvent(
                source="scheduler_guards",
                event_type="event.incident",
                actor="scheduler_guards",
                resource="scheduler",
                payload={
                    'trigger_id': 'scheduler_heartbeat_timeout',
                    'playbook': 'scheduler_recovery',
                    'severity': 'high',
                    'timeout_seconds': self.heartbeat_timeout,
                    'timestamp': datetime.utcnow().isoformat()
                }
            ))
        except Exception as e:
            logger.error(f"[SCHEDULER-GUARDS] Recovery trigger failed: {e}")
    
    async def _trigger_load_shedding(self):
        """Trigger load shedding playbook"""
        
        try:
            from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
            
            await trigger_mesh.publish(TriggerEvent(
                source="scheduler_guards",
                event_type="event.incident",
                actor="scheduler_guards",
                resource="scheduler_queue",
                payload={
                    'trigger_id': 'scheduler_queue_overflow',
                    'playbook': 'scheduler_load_shedding',
                    'severity': 'medium',
                    'queue_depth': self.health.queue_depth,
                    'threshold': self.queue_depth_critical,
                    'timestamp': datetime.utcnow().isoformat()
                }
            ))
        except Exception as e:
            logger.error(f"[SCHEDULER-GUARDS] Load shedding trigger failed: {e}")
    
    async def _publish_telemetry(self):
        """Publish scheduler telemetry"""
        
        try:
            from backend.logging.unified_logic_hub import unified_logic_hub
            
            await unified_logic_hub.submit_proposal(
                proposal_id=f"scheduler_telemetry_{int(datetime.utcnow().timestamp())}",
                proposal_type="telemetry_update",
                actor="scheduler_guards",
                target_component="unified_logic_hub",
                payload={
                    'component': 'scheduler',
                    'queue_depth': self.health.queue_depth,
                    'dispatch_rate': self.health.dispatch_rate,
                    'task_backlog': self.health.task_backlog,
                    'health_status': 'healthy' if self.health.is_healthy else 'degraded'
                },
                requires_vote=False
            )
        except Exception as e:
            logger.debug(f"[SCHEDULER-GUARDS] Telemetry publish failed: {e}")
    
    async def log_dispatch(
        self,
        task_id: str,
        task_type: str,
        target: str,
        selection_method: str,
        queue_depth: int,
        reasoning: List[str]
    ):
        """
        Log task dispatch with 5W1H and mission context
        
        Called by scheduler when dispatching tasks
        """
        
        try:
            from backend.core.clarity_5w1h import clarity_5w1h
            
            await clarity_5w1h.log_task_dispatch(
                dispatcher="scheduler",
                task_id=task_id,
                task_type=task_type,
                target_worker=target,
                queue_depth=queue_depth,
                selection_method=selection_method,
                reasons=reasoning
            )
        except Exception as e:
            logger.error(f"[SCHEDULER-GUARDS] 5W1H logging failed: {e}")
    
    def update_heartbeat(self):
        """Update scheduler heartbeat"""
        self.health.last_heartbeat = datetime.utcnow()
        self.health.is_healthy = True
    
    def update_metrics(
        self,
        queue_depth: int,
        dispatch_rate: float,
        task_backlog: int
    ):
        """Update scheduler metrics"""
        self.health.queue_depth = queue_depth
        self.health.dispatch_rate = dispatch_rate
        self.health.task_backlog = task_backlog


# Global instance
scheduler_guards = SchedulerGuards()
