"""
Critical Kernel Heartbeat Trigger
Fires when message_bus, self_healing, or coding_agent stop responding

Trigger Criteria:
- Critical kernel missed heartbeat > 30s
- Multiple critical kernels down simultaneously
- Message bus completely unresponsive

Actions:
- Launch emergency recovery playbook
- Create coding-agent diagnostic task
- Escalate to emergency protocol if needed
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CriticalKernelHeartbeatTrigger:
    """
    Monitors critical kernel heartbeats
    Triggers emergency response before 180s recovery window expires
    """
    
    def __init__(self):
        self.critical_kernels = ['message_bus', 'self_healing', 'coding_agent']
        self.heartbeat_threshold_seconds = 30
        self.running = False
        self.last_check = {}
        
        # Thresholds
        self.single_kernel_threshold = 30  # Seconds without heartbeat
        self.multiple_kernel_threshold = 15  # Faster trigger if multiple down
    
    async def start(self):
        """Start monitoring critical kernels"""
        if self.running:
            return
        
        self.running = True
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
        
        logger.info("[CRITICAL-KERNEL-TRIGGER] Started monitoring critical kernels")
        logger.info(f"[CRITICAL-KERNEL-TRIGGER] Watching: {', '.join(self.critical_kernels)}")
    
    async def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info("[CRITICAL-KERNEL-TRIGGER] Stopped")
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.running:
            try:
                await self._check_critical_kernels()
            except Exception as e:
                logger.error(f"[CRITICAL-KERNEL-TRIGGER] Monitoring error: {e}")
            
            await asyncio.sleep(5)  # Check every 5 seconds
    
    async def _check_critical_kernels(self):
        """Check critical kernel heartbeats"""
        from backend.core import control_plane
        
        now = datetime.utcnow()
        status = control_plane.get_status()
        
        kernels_down = []
        kernels_degraded = []
        
        for kernel_name in self.critical_kernels:
            kernel = control_plane.kernels.get(kernel_name)
            if not kernel:
                continue
            
            # Check state
            if kernel.state.value == 'failed':
                kernels_down.append(kernel_name)
                continue
            
            # Check heartbeat
            if kernel.last_heartbeat:
                time_since_heartbeat = (now - kernel.last_heartbeat).total_seconds()
                
                if time_since_heartbeat > self.single_kernel_threshold:
                    kernels_degraded.append({
                        'kernel': kernel_name,
                        'seconds_since_heartbeat': time_since_heartbeat
                    })
        
        # Trigger based on severity
        if len(kernels_down) >= 2:
            # Multiple critical kernels down - EMERGENCY
            await self._trigger_emergency_protocol(kernels_down, kernels_degraded)
        
        elif len(kernels_down) == 1:
            # Single critical kernel down
            await self._trigger_critical_kernel_recovery(kernels_down[0])
        
        elif len(kernels_degraded) >= 2:
            # Multiple kernels not responding
            kernel_names = [k['kernel'] for k in kernels_degraded]
            await self._trigger_multi_kernel_degradation(kernel_names)
    
    async def _trigger_emergency_protocol(self, kernels_down: List[str], degraded: List[Dict]):
        """
        EMERGENCY: Multiple critical kernels down
        Bypass normal playbook flow - go straight to emergency recovery
        """
        
        logger.critical(f"[EMERGENCY] Multiple critical kernels down: {kernels_down}")
        
        from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
        
        # Publish emergency event
        await trigger_mesh.publish(TriggerEvent(
            source="critical_kernel_trigger",
            event_type="event.emergency",
            actor="critical_kernel_monitor",
            resource="control_plane",
            payload={
                "trigger_id": "critical_kernel_heartbeat",
                "playbook": "emergency_critical_kernel_recovery",
                "severity": "critical",
                "kernels_down": kernels_down,
                "kernels_degraded": [k['kernel'] for k in degraded],
                "timestamp": datetime.utcnow().isoformat(),
                "emergency_protocol": True
            }
        ))
        
        logger.critical(f"[EMERGENCY] Triggered emergency recovery playbook")
        
        # Create coding-agent diagnostic task
        await self._create_diagnostic_task(
            f"Emergency: {len(kernels_down)} critical kernels failed: {', '.join(kernels_down)}",
            {
                'kernels_down': kernels_down,
                'degraded': degraded,
                'emergency': True
            }
        )
    
    async def _trigger_critical_kernel_recovery(self, kernel_name: str):
        """
        Single critical kernel down
        Trigger standard recovery playbook
        """
        
        logger.error(f"[CRITICAL-KERNEL-TRIGGER] Critical kernel down: {kernel_name}")
        
        from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
        
        # Publish incident event
        await trigger_mesh.publish(TriggerEvent(
            source="critical_kernel_trigger",
            event_type="event.incident",
            actor="critical_kernel_monitor",
            resource=kernel_name,
            payload={
                "trigger_id": "critical_kernel_heartbeat",
                "playbook": "critical_kernel_restart",
                "severity": "high",
                "kernel": kernel_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        ))
        
        logger.info(f"[CRITICAL-KERNEL-TRIGGER] Triggered recovery playbook for {kernel_name}")
    
    async def _trigger_multi_kernel_degradation(self, kernel_names: List[str]):
        """
        Multiple kernels degraded (heartbeat delays)
        Proactive recovery before full failure
        """
        
        logger.warning(f"[CRITICAL-KERNEL-TRIGGER] Multiple kernels degraded: {kernel_names}")
        
        from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
        
        # Publish early warning
        await trigger_mesh.publish(TriggerEvent(
            source="critical_kernel_trigger",
            event_type="event.early_warning",
            actor="critical_kernel_monitor",
            resource="control_plane",
            payload={
                "trigger_id": "critical_kernel_heartbeat",
                "playbook": "proactive_kernel_health_check",
                "severity": "medium",
                "kernels": kernel_names,
                "timestamp": datetime.utcnow().isoformat()
            }
        ))
        
        logger.info(f"[CRITICAL-KERNEL-TRIGGER] Proactive health check triggered")
    
    async def _create_diagnostic_task(self, description: str, context: Dict[str, Any]):
        """Create coding-agent task to diagnose kernel failure"""
        
        try:
            from backend.agents_core.elite_coding_agent import elite_coding_agent, CodingTask, CodingTaskType, ExecutionMode
            
            task = CodingTask(
                task_id=f"diag_kernel_{int(datetime.utcnow().timestamp())}",
                task_type=CodingTaskType.FIX_BUG,
                description=description,
                requirements={
                    'task': 'analyze_kernel_failure',
                    'context': context,
                    'actions': [
                        'Check kernel logs for crash reason',
                        'Verify dependencies are loaded',
                        'Check for resource exhaustion',
                        'Identify root cause',
                        'Generate fix if code-related'
                    ]
                },
                execution_mode=ExecutionMode.AUTO,
                priority=10,  # Highest priority
                created_at=datetime.utcnow()
            )
            
            await elite_coding_agent.submit_task(task)
            
            logger.info(f"[CRITICAL-KERNEL-TRIGGER] Created diagnostic task: {task.task_id}")
        
        except Exception as e:
            logger.error(f"[CRITICAL-KERNEL-TRIGGER] Failed to create task: {e}")


# Global instance
critical_kernel_trigger = CriticalKernelHeartbeatTrigger()
