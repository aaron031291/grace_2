"""
Layer 2 Watchdog - HTM, Trigger System, Event Policy, Scheduler
Explicit readiness checks and health monitoring for orchestration layer

Monitors:
- HTM queue depth and worker health
- Trigger mesh subscription health
- Event policy execution rate
- Scheduler task dispatch health
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Layer2ComponentHealth:
    """Health status for Layer 2 component"""
    component_name: str
    is_ready: bool
    is_healthy: bool
    last_check: datetime
    
    # Component-specific metrics
    queue_depth: Optional[int] = None
    worker_count: Optional[int] = None
    subscription_count: Optional[int] = None
    dispatch_rate: Optional[float] = None
    
    # Health indicators
    error_count: int = 0
    last_error: Optional[str] = None
    uptime_seconds: float = 0.0
    
    # SLO tracking
    slo_breaches: int = 0
    last_breach: Optional[datetime] = None


class Layer2Watchdog:
    """
    Watchdog for Layer 2 orchestration components
    Monitors HTM, trigger system, event policy, scheduler
    """
    
    def __init__(self):
        self.running = False
        self.health_status: Dict[str, Layer2ComponentHealth] = {}
        
        # Watchdog config
        self.check_interval_seconds = 15
        self.readiness_timeout_seconds = 30
        
        # Thresholds
        self.htm_queue_depth_warning = 1000
        self.htm_queue_depth_critical = 5000
        self.trigger_subscription_min = 5
        self.scheduler_dispatch_rate_min = 1.0  # Tasks/second
        
        # Components to monitor
        self.components = [
            'htm_orchestrator',
            'trigger_mesh',
            'event_policy_engine',
            'scheduler'
        ]
    
    async def start(self):
        """Start Layer 2 watchdog"""
        if self.running:
            return
        
        self.running = True
        
        # Initialize health tracking
        for component in self.components:
            self.health_status[component] = Layer2ComponentHealth(
                component_name=component,
                is_ready=False,
                is_healthy=False,
                last_check=datetime.utcnow()
            )
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
        
        logger.info("[LAYER2-WATCHDOG] Started monitoring orchestration layer")
        logger.info(f"[LAYER2-WATCHDOG] Components: {', '.join(self.components)}")
    
    async def stop(self):
        """Stop watchdog"""
        self.running = False
        logger.info("[LAYER2-WATCHDOG] Stopped")
    
    async def _monitoring_loop(self):
        """Continuous health monitoring"""
        
        while self.running:
            try:
                # Check all components
                await self._check_htm_health()
                await self._check_trigger_mesh_health()
                await self._check_event_policy_health()
                await self._check_scheduler_health()
                
                # Publish telemetry
                await self._publish_telemetry()
                
                # Check for SLO breaches
                await self._check_slo_breaches()
            
            except Exception as e:
                logger.error(f"[LAYER2-WATCHDOG] Monitoring error: {e}")
            
            await asyncio.sleep(self.check_interval_seconds)
    
    async def _check_htm_health(self):
        """Check HTM orchestrator health"""
        component = 'htm_orchestrator'
        health = self.health_status[component]
        health.last_check = datetime.utcnow()
        
        try:
            # Check if HTM is loaded
            try:
                from backend.core.enhanced_htm import htm_orchestrator
                health.is_ready = True
            except ImportError:
                health.is_ready = False
                health.is_healthy = False
                return
            
            # Check queue depth
            if hasattr(htm_orchestrator, 'intent_queue'):
                health.queue_depth = len(htm_orchestrator.intent_queue)
                
                # Check thresholds
                if health.queue_depth > self.htm_queue_depth_critical:
                    health.is_healthy = False
                    health.slo_breaches += 1
                    health.last_breach = datetime.utcnow()
                    
                    # Trigger alert
                    await self._trigger_alert(
                        component=component,
                        severity='critical',
                        reason=f'Queue depth critical: {health.queue_depth}'
                    )
                
                elif health.queue_depth > self.htm_queue_depth_warning:
                    logger.warning(f"[LAYER2-WATCHDOG] HTM queue depth warning: {health.queue_depth}")
            
            # Check worker count
            if hasattr(htm_orchestrator, 'active_workers'):
                health.worker_count = len(htm_orchestrator.active_workers)
                
                if health.worker_count == 0:
                    health.is_healthy = False
                    health.error_count += 1
                    health.last_error = "No active workers"
                else:
                    health.is_healthy = True
            else:
                health.is_healthy = True  # Assume healthy if no queue
        
        except Exception as e:
            health.is_healthy = False
            health.error_count += 1
            health.last_error = str(e)
    
    async def _check_trigger_mesh_health(self):
        """Check trigger mesh health"""
        component = 'trigger_mesh'
        health = self.health_status[component]
        health.last_check = datetime.utcnow()
        
        try:
            from backend.misc.trigger_mesh import trigger_mesh
            
            health.is_ready = True
            
            # Check subscription count
            health.subscription_count = len(trigger_mesh.subscribers)
            
            if health.subscription_count < self.trigger_subscription_min:
                health.is_healthy = False
                health.last_error = f"Low subscription count: {health.subscription_count}"
            else:
                health.is_healthy = True
        
        except Exception as e:
            health.is_ready = False
            health.is_healthy = False
            health.last_error = str(e)
    
    async def _check_event_policy_health(self):
        """Check event policy engine health"""
        component = 'event_policy_engine'
        health = self.health_status[component]
        health.last_check = datetime.utcnow()
        
        try:
            # Check if event policy loaded
            try:
                from backend.workflow_engines.event_policy import event_policy_engine
                health.is_ready = True
                health.is_healthy = True
            except ImportError:
                health.is_ready = False
                health.is_healthy = False
        
        except Exception as e:
            health.is_ready = False
            health.is_healthy = False
            health.last_error = str(e)
    
    async def _check_scheduler_health(self):
        """Check scheduler health"""
        component = 'scheduler'
        health = self.health_status[component]
        health.last_check = datetime.utcnow()
        
        try:
            from backend.core import control_plane
            
            # Check if scheduler kernel is running
            scheduler_kernel = control_plane.kernels.get('scheduler')
            
            if scheduler_kernel and scheduler_kernel.state.value == 'running':
                health.is_ready = True
                health.is_healthy = True
            else:
                health.is_ready = False
                health.is_healthy = False
                health.last_error = "Scheduler kernel not running"
        
        except Exception as e:
            health.is_ready = False
            health.is_healthy = False
            health.last_error = str(e)
    
    async def _publish_telemetry(self):
        """Publish Layer 2 telemetry to Clarity and Unified Logic"""
        
        try:
            from backend.logging.unified_logic_hub import unified_logic_hub
            from backend.core.clarity_framework import clarity_framework
            
            # Prepare telemetry payload
            telemetry = {
                'timestamp': datetime.utcnow().isoformat(),
                'layer': 'layer2_orchestration',
                'components': {}
            }
            
            for component_name, health in self.health_status.items():
                telemetry['components'][component_name] = {
                    'ready': health.is_ready,
                    'healthy': health.is_healthy,
                    'queue_depth': health.queue_depth,
                    'worker_count': health.worker_count,
                    'subscriptions': health.subscription_count,
                    'error_count': health.error_count,
                    'slo_breaches': health.slo_breaches
                }
            
            # Publish to unified logic
            await unified_logic_hub.submit_proposal(
                proposal_id=f"layer2_telemetry_{int(datetime.utcnow().timestamp())}",
                proposal_type="telemetry_update",
                actor="layer2_watchdog",
                target_component="unified_logic_hub",
                payload=telemetry,
                requires_vote=False
            )
            
            # Log to Clarity if issues detected
            unhealthy = [c for c, h in self.health_status.items() if not h.is_healthy]
            if unhealthy:
                await clarity_framework.record_decision(
                    actor="layer2_watchdog",
                    action_type="health_alert",
                    resource="layer2_orchestration",
                    decision={
                        'type': 'alert',
                        'unhealthy_components': unhealthy,
                        'severity': 'medium'
                    },
                    reasoning_chain=[
                        f"Detected {len(unhealthy)} unhealthy Layer 2 components",
                        f"Components: {', '.join(unhealthy)}",
                        "Publishing telemetry to unified logic for correlation",
                        "Watchdog will continue monitoring"
                    ]
                )
        
        except Exception as e:
            logger.error(f"[LAYER2-WATCHDOG] Telemetry publish failed: {e}")
    
    async def _check_slo_breaches(self):
        """Check for SLO breaches and trigger alerts"""
        
        for component_name, health in self.health_status.items():
            # Check for critical conditions
            if health.slo_breaches > 0 and health.last_breach:
                time_since_breach = (datetime.utcnow() - health.last_breach).total_seconds()
                
                if time_since_breach < 60:  # Breach within last minute
                    await self._trigger_alert(
                        component=component_name,
                        severity='high',
                        reason=f'SLO breach: {health.last_error or "Unknown"}'
                    )
    
    async def _trigger_alert(self, component: str, severity: str, reason: str):
        """Trigger alert for component issue"""
        
        logger.error(f"[LAYER2-WATCHDOG] ALERT [{severity.upper()}] {component}: {reason}")
        
        try:
            from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
            
            await trigger_mesh.publish(TriggerEvent(
                source="layer2_watchdog",
                event_type=f"layer2.{severity}_alert",
                actor="layer2_watchdog",
                resource=component,
                payload={
                    'component': component,
                    'severity': severity,
                    'reason': reason,
                    'health': self.health_status[component].__dict__,
                    'timestamp': datetime.utcnow().isoformat()
                }
            ))
        
        except Exception as e:
            logger.error(f"[LAYER2-WATCHDOG] Alert trigger failed: {e}")
    
    async def check_readiness(self, timeout_seconds: int = 30) -> Dict[str, bool]:
        """
        Check if all Layer 2 components are ready
        Used during boot to ensure orchestration layer is operational
        """
        
        logger.info("[LAYER2-WATCHDOG] Checking Layer 2 readiness...")
        
        start_time = datetime.utcnow()
        deadline = start_time + timedelta(seconds=timeout_seconds)
        
        while datetime.utcnow() < deadline:
            # Force health check
            await self._check_htm_health()
            await self._check_trigger_mesh_health()
            await self._check_event_policy_health()
            await self._check_scheduler_health()
            
            # Check if all ready
            all_ready = all(h.is_ready for h in self.health_status.values())
            
            if all_ready:
                logger.info("[LAYER2-WATCHDOG] All Layer 2 components ready!")
                return {c: True for c in self.components}
            
            await asyncio.sleep(2)
        
        # Timeout - report which aren't ready
        readiness = {c: h.is_ready for c, h in self.health_status.items()}
        not_ready = [c for c, ready in readiness.items() if not ready]
        
        logger.warning(f"[LAYER2-WATCHDOG] Timeout - Not ready: {', '.join(not_ready)}")
        
        return readiness
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report"""
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'components': {
                name: {
                    'ready': health.is_ready,
                    'healthy': health.is_healthy,
                    'queue_depth': health.queue_depth,
                    'workers': health.worker_count,
                    'subscriptions': health.subscription_count,
                    'errors': health.error_count,
                    'slo_breaches': health.slo_breaches,
                    'last_error': health.last_error
                }
                for name, health in self.health_status.items()
            },
            'overall_health': all(h.is_healthy for h in self.health_status.values()),
            'all_ready': all(h.is_ready for h in self.health_status.values())
        }


# Global instance
layer2_watchdog = Layer2Watchdog()
