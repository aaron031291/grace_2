"""
Self-Healing Trigger System
Proactive monitoring that hooks into self-healing playbooks

Trigger Types:
1. Heartbeat failures      - Kernel stops responding
2. API/Endpoint timeouts   - Repeated 500s, timeouts
3. KPI thresholds          - Latency, error rate, trust score drops
4. Resource spikes         - CPU/RAM/disk high watermarks
5. Sandbox failures        - Experiment fatal errors
6. Event anomalies         - Unusual log/metric patterns
7. Schedule checks         - Daily health, key rotation

Each trigger publishes:
- event.incident (for immediate response)
- task.enqueue (for scheduled playbook execution)
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from enum import Enum
from collections import deque
import psutil

from backend.core.message_bus import message_bus, MessagePriority


class TriggerType(str, Enum):
    """Types of self-healing triggers"""
    HEARTBEAT_FAILURE = "heartbeat_failure"
    API_TIMEOUT = "api_timeout"
    API_ERROR_RATE = "api_error_rate"
    KPI_THRESHOLD = "kpi_threshold"
    RESOURCE_SPIKE = "resource_spike"
    SANDBOX_FAILURE = "sandbox_failure"
    EVENT_ANOMALY = "event_anomaly"
    SCHEDULED_CHECK = "scheduled_check"


class IncidentSeverity(str, Enum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SelfHealingTrigger:
    """Base class for self-healing triggers"""
    
    def __init__(
        self,
        trigger_id: str,
        trigger_type: TriggerType,
        playbook_name: str,
        severity: IncidentSeverity = IncidentSeverity.MEDIUM
    ):
        self.trigger_id = trigger_id
        self.trigger_type = trigger_type
        self.playbook_name = playbook_name
        self.severity = severity
        self.enabled = True
        self.fire_count = 0
        self.last_fired = None
    
    async def check(self) -> bool:
        """Check if trigger condition is met - override in subclass"""
        return False
    
    async def fire(self, context: Dict[str, Any]):
        """Fire the trigger - publish incident event"""
        
        if not self.enabled:
            return
        
        self.fire_count += 1
        self.last_fired = datetime.utcnow()
        
        incident = {
            "trigger_id": self.trigger_id,
            "trigger_type": self.trigger_type.value,
            "playbook": self.playbook_name,
            "severity": self.severity.value,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context,
            "fire_count": self.fire_count
        }
        
        # Publish incident event (immediate response)
        await message_bus.publish(
            source="trigger_system",
            topic="event.incident",
            payload=incident,
            priority=MessagePriority.HIGH if self.severity == IncidentSeverity.CRITICAL else MessagePriority.NORMAL
        )
        
        # Enqueue playbook task
        await message_bus.publish(
            source="trigger_system",
            topic="task.enqueue",
            payload={
                "task_type": "self_healing",
                "playbook": self.playbook_name,
                "incident_id": f"incident_{self.trigger_id}_{self.fire_count}",
                "context": context,
                "priority": self.severity.value
            },
            priority=MessagePriority.HIGH if self.severity == IncidentSeverity.CRITICAL else MessagePriority.NORMAL
        )
        
        print(f"[TRIGGER] 🔥 {self.trigger_type.value}: {self.playbook_name} (severity: {self.severity.value})")


class HeartbeatFailureTrigger(SelfHealingTrigger):
    """Triggers when kernel stops sending heartbeats"""
    
    def __init__(self, kernel_name: str, timeout_seconds: int = 60):
        super().__init__(
            trigger_id=f"heartbeat_{kernel_name}",
            trigger_type=TriggerType.HEARTBEAT_FAILURE,
            playbook_name="restart_kernel",
            severity=IncidentSeverity.HIGH
        )
        self.kernel_name = kernel_name
        self.timeout_seconds = timeout_seconds
        self.last_heartbeat = datetime.utcnow()
    
    def record_heartbeat(self):
        """Record a heartbeat received"""
        self.last_heartbeat = datetime.utcnow()
    
    async def check(self) -> bool:
        """Check if heartbeat is stale"""
        age = (datetime.utcnow() - self.last_heartbeat).total_seconds()
        
        if age > self.timeout_seconds:
            await self.fire({
                "kernel_name": self.kernel_name,
                "heartbeat_age_seconds": age,
                "timeout_threshold": self.timeout_seconds
            })
            return True
        
        return False


class APITimeoutTrigger(SelfHealingTrigger):
    """Triggers on repeated API timeouts or 500 errors"""
    
    def __init__(self, endpoint: str, threshold: int = 5, window_seconds: int = 300):
        super().__init__(
            trigger_id=f"api_timeout_{endpoint.replace('/', '_')}",
            trigger_type=TriggerType.API_TIMEOUT,
            playbook_name="restart_service",
            severity=IncidentSeverity.MEDIUM
        )
        self.endpoint = endpoint
        self.threshold = threshold
        self.window_seconds = window_seconds
        self.error_log = deque(maxlen=100)  # Last 100 errors
    
    def record_error(self, status_code: int, error_type: str):
        """Record an API error"""
        self.error_log.append({
            "timestamp": datetime.utcnow(),
            "status_code": status_code,
            "error_type": error_type
        })
    
    async def check(self) -> bool:
        """Check if error rate exceeds threshold"""
        cutoff = datetime.utcnow() - timedelta(seconds=self.window_seconds)
        
        # Count errors in window
        recent_errors = [
            err for err in self.error_log 
            if err["timestamp"] > cutoff
        ]
        
        if len(recent_errors) >= self.threshold:
            await self.fire({
                "endpoint": self.endpoint,
                "error_count": len(recent_errors),
                "threshold": self.threshold,
                "window_seconds": self.window_seconds,
                "recent_errors": recent_errors[-5:]  # Last 5
            })
            
            # Clear log to prevent repeat firing
            self.error_log.clear()
            return True
        
        return False


class KPIThresholdTrigger(SelfHealingTrigger):
    """Triggers when KPI crosses threshold"""
    
    def __init__(
        self,
        kpi_name: str,
        threshold: float,
        comparison: str = "greater_than",  # or "less_than"
        playbook: str = "performance_optimization"
    ):
        super().__init__(
            trigger_id=f"kpi_{kpi_name}",
            trigger_type=TriggerType.KPI_THRESHOLD,
            playbook_name=playbook,
            severity=IncidentSeverity.MEDIUM
        )
        self.kpi_name = kpi_name
        self.threshold = threshold
        self.comparison = comparison
        self.current_value = None
    
    def update_value(self, value: float):
        """Update current KPI value"""
        self.current_value = value
    
    async def check(self) -> bool:
        """Check if KPI exceeds threshold"""
        if self.current_value is None:
            return False
        
        triggered = False
        
        if self.comparison == "greater_than" and self.current_value > self.threshold:
            triggered = True
        elif self.comparison == "less_than" and self.current_value < self.threshold:
            triggered = True
        
        if triggered:
            await self.fire({
                "kpi_name": self.kpi_name,
                "current_value": self.current_value,
                "threshold": self.threshold,
                "comparison": self.comparison
            })
            return True
        
        return False


class ResourceSpikeTrigger(SelfHealingTrigger):
    """Triggers on CPU/RAM/disk spikes"""
    
    def __init__(
        self,
        resource_type: str,  # "cpu", "memory", "disk"
        threshold_percent: float = 85.0,
        sustained_seconds: int = 60
    ):
        super().__init__(
            trigger_id=f"resource_{resource_type}",
            trigger_type=TriggerType.RESOURCE_SPIKE,
            playbook_name="resource_cleanup" if resource_type == "disk" else "restart_service",
            severity=IncidentSeverity.HIGH
        )
        self.resource_type = resource_type
        self.threshold_percent = threshold_percent
        self.sustained_seconds = sustained_seconds
        self.spike_start = None
    
    async def check(self) -> bool:
        """Check if resource usage is high"""
        
        # Get current usage
        if self.resource_type == "cpu":
            usage = psutil.cpu_percent(interval=1)
        elif self.resource_type == "memory":
            usage = psutil.virtual_memory().percent
        elif self.resource_type == "disk":
            usage = psutil.disk_usage('/').percent
        else:
            return False
        
        # Check if above threshold
        if usage > self.threshold_percent:
            if not self.spike_start:
                self.spike_start = datetime.utcnow()
            
            # Check if sustained
            duration = (datetime.utcnow() - self.spike_start).total_seconds()
            
            if duration >= self.sustained_seconds:
                await self.fire({
                    "resource_type": self.resource_type,
                    "usage_percent": usage,
                    "threshold": self.threshold_percent,
                    "duration_seconds": duration
                })
                
                self.spike_start = None  # Reset
                return True
        else:
            # Below threshold, reset
            self.spike_start = None
        
        return False


class SandboxFailureTrigger(SelfHealingTrigger):
    """Triggers on sandbox/experiment failures"""
    
    def __init__(self):
        super().__init__(
            trigger_id="sandbox_failure",
            trigger_type=TriggerType.SANDBOX_FAILURE,
            playbook_name="quarantine_artifacts",
            severity=IncidentSeverity.MEDIUM
        )
        self.failure_count = 0
    
    async def on_sandbox_failure(self, sandbox_id: str, error: str):
        """Called when a sandbox fails"""
        self.failure_count += 1
        
        await self.fire({
            "sandbox_id": sandbox_id,
            "error": error,
            "failure_count": self.failure_count
        })


class EventAnomalyTrigger(SelfHealingTrigger):
    """Triggers on unusual patterns in logs/metrics"""
    
    def __init__(self, anomaly_type: str = "error_burst"):
        super().__init__(
            trigger_id=f"anomaly_{anomaly_type}",
            trigger_type=TriggerType.EVENT_ANOMALY,
            playbook_name="run_diagnostics",
            severity=IncidentSeverity.MEDIUM
        )
        self.anomaly_type = anomaly_type
        self.event_window = deque(maxlen=100)
        self.baseline_rate = None
    
    def record_event(self, event_type: str):
        """Record an event occurrence"""
        self.event_window.append({
            "type": event_type,
            "timestamp": datetime.utcnow()
        })
    
    async def check(self) -> bool:
        """Detect anomalies in event patterns"""
        
        if len(self.event_window) < 10:
            return False
        
        # Count events in last minute
        cutoff = datetime.utcnow() - timedelta(seconds=60)
        recent = [e for e in self.event_window if e["timestamp"] > cutoff]
        
        # Error burst detection
        if self.anomaly_type == "error_burst":
            error_count = len([e for e in recent if "error" in e["type"].lower()])
            
            if error_count > 10:  # More than 10 errors per minute
                await self.fire({
                    "anomaly_type": self.anomaly_type,
                    "error_count": error_count,
                    "window_seconds": 60
                })
                return True
        
        return False


class ScheduledHealthCheckTrigger(SelfHealingTrigger):
    """Triggers scheduled health checks (cron-like)"""
    
    def __init__(
        self,
        check_name: str,
        interval_hours: int = 24,
        playbook: str = "daily_health_check"
    ):
        super().__init__(
            trigger_id=f"scheduled_{check_name}",
            trigger_type=TriggerType.SCHEDULED_CHECK,
            playbook_name=playbook,
            severity=IncidentSeverity.LOW
        )
        self.check_name = check_name
        self.interval_hours = interval_hours
        self.last_run = None
    
    async def check(self) -> bool:
        """Check if it's time to run"""
        
        now = datetime.utcnow()
        
        if self.last_run is None:
            # First run
            await self.fire({"check_name": self.check_name, "type": "initial_run"})
            self.last_run = now
            return True
        
        elapsed_hours = (now - self.last_run).total_seconds() / 3600
        
        if elapsed_hours >= self.interval_hours:
            await self.fire({
                "check_name": self.check_name,
                "hours_since_last": elapsed_hours
            })
            self.last_run = now
            return True
        
        return False


class TrustScoreDropTrigger(SelfHealingTrigger):
    """Triggers when trust score drops significantly"""
    
    def __init__(self, component_name: str, threshold: float = 0.7):
        super().__init__(
            trigger_id=f"trust_drop_{component_name}",
            trigger_type=TriggerType.KPI_THRESHOLD,
            playbook_name="rollback_deployment",
            severity=IncidentSeverity.HIGH
        )
        self.component_name = component_name
        self.threshold = threshold
        self.current_trust = 1.0
    
    def update_trust_score(self, score: float):
        """Update current trust score"""
        self.current_trust = score
    
    async def check(self) -> bool:
        """Check if trust dropped below threshold"""
        if self.current_trust < self.threshold:
            await self.fire({
                "component": self.component_name,
                "trust_score": self.current_trust,
                "threshold": self.threshold,
                "drop_amount": self.threshold - self.current_trust
            })
            return True
        return False


class TriggerManager:
    """
    Manages all self-healing triggers
    
    Integrates with:
    - Self-Healing Kernel: Receives events, executes playbooks
    - Kernel Restart Manager: Heartbeat monitoring
    - Resource Manager: CPU/RAM/disk monitoring
    - Data Cube: Anomaly detection
    - Governance: Incident approval for critical playbooks
    """
    
    def __init__(self):
        self.triggers: Dict[str, SelfHealingTrigger] = {}
        self.incident_history = []
        
        # Monitoring tasks
        self._monitor_task: Optional[asyncio.Task] = None
        self._scheduled_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            "total_triggers": 0,
            "triggers_fired": 0,
            "playbooks_invoked": 0,
            "incidents_resolved": 0
        }
    
    async def start(self):
        """Start trigger monitoring"""
        
        # Register default triggers
        await self._register_default_triggers()
        
        # Start monitoring loops
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        self._scheduled_task = asyncio.create_task(self._scheduled_loop())
        
        # Subscribe to incident resolutions
        asyncio.create_task(self._monitor_resolutions())
        
        print(f"[TRIGGER-SYS] Started with {len(self.triggers)} triggers")
    
    async def _register_default_triggers(self):
        """Register standard triggers"""
        
        # Heartbeat triggers for critical kernels
        for kernel in ["core", "memory", "infrastructure_manager", "governance"]:
            trigger = HeartbeatFailureTrigger(kernel, timeout_seconds=60)
            self.register_trigger(trigger)
        
        # API timeout trigger
        api_trigger = APITimeoutTrigger("/api/health", threshold=5, window_seconds=300)
        self.register_trigger(api_trigger)
        
        # Resource spike triggers
        self.register_trigger(ResourceSpikeTrigger("cpu", threshold_percent=85.0))
        self.register_trigger(ResourceSpikeTrigger("memory", threshold_percent=80.0))
        self.register_trigger(ResourceSpikeTrigger("disk", threshold_percent=90.0))
        
        # KPI triggers
        latency_trigger = KPIThresholdTrigger(
            "api_latency_p95",
            threshold=1000.0,  # 1 second
            comparison="greater_than",
            playbook="performance_optimization"
        )
        self.register_trigger(latency_trigger)
        
        error_rate_trigger = KPIThresholdTrigger(
            "error_rate",
            threshold=5.0,  # 5% error rate
            comparison="greater_than",
            playbook="restart_service"
        )
        self.register_trigger(error_rate_trigger)
        
        # Trust score triggers
        for component in ["memory", "intelligence", "code"]:
            trust_trigger = TrustScoreDropTrigger(component, threshold=0.7)
            self.register_trigger(trust_trigger)
        
        # Sandbox failure
        self.register_trigger(SandboxFailureTrigger())
        
        # Event anomaly
        self.register_trigger(EventAnomalyTrigger("error_burst"))
        
        # Scheduled checks
        daily_health = ScheduledHealthCheckTrigger(
            "daily_health",
            interval_hours=24,
            playbook="daily_health_check"
        )
        self.register_trigger(daily_health)
        
        key_rotation = ScheduledHealthCheckTrigger(
            "key_rotation",
            interval_hours=168,  # Weekly
            playbook="rotate_secrets"
        )
        self.register_trigger(key_rotation)
        
        self.stats["total_triggers"] = len(self.triggers)
    
    def register_trigger(self, trigger: SelfHealingTrigger):
        """Register a new trigger"""
        self.triggers[trigger.trigger_id] = trigger
        print(f"[TRIGGER-SYS] Registered: {trigger.trigger_type.value} → {trigger.playbook_name}")
    
    async def _monitoring_loop(self):
        """Continuously check all triggers"""
        
        while True:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                for trigger_id, trigger in self.triggers.items():
                    try:
                        fired = await trigger.check()
                        if fired:
                            self.stats["triggers_fired"] += 1
                            self.stats["playbooks_invoked"] += 1
                    except Exception as e:
                        print(f"[TRIGGER-SYS] Error checking {trigger_id}: {e}")
            
            except Exception as e:
                print(f"[TRIGGER-SYS] Monitor loop error: {e}")
    
    async def _scheduled_loop(self):
        """Handle scheduled triggers separately"""
        
        while True:
            try:
                await asyncio.sleep(3600)  # Check hourly
                
                for trigger in self.triggers.values():
                    if trigger.trigger_type == TriggerType.SCHEDULED_CHECK:
                        await trigger.check()
            
            except Exception as e:
                print(f"[TRIGGER-SYS] Scheduled loop error: {e}")
    
    async def _monitor_resolutions(self):
        """Monitor for incident resolutions"""
        
        try:
            queue = await message_bus.subscribe(
                subscriber="trigger_system",
                topic="incident.resolved"
            )
            
            while True:
                msg = await queue.get()
                self.stats["incidents_resolved"] += 1
                
                incident_id = msg.payload.get("incident_id")
                print(f"[TRIGGER-SYS] ✅ Incident resolved: {incident_id}")
        
        except Exception as e:
            print(f"[TRIGGER-SYS] Resolution monitor error: {e}")
    
    # Public API for trigger updates
    
    async def record_heartbeat(self, kernel_name: str):
        """Record kernel heartbeat"""
        trigger_id = f"heartbeat_{kernel_name}"
        if trigger_id in self.triggers:
            self.triggers[trigger_id].record_heartbeat()
    
    async def record_api_error(self, endpoint: str, status_code: int, error_type: str):
        """Record API error"""
        trigger_id = f"api_timeout_{endpoint.replace('/', '_')}"
        if trigger_id in self.triggers:
            self.triggers[trigger_id].record_error(status_code, error_type)
            await self.triggers[trigger_id].check()
    
    async def update_kpi(self, kpi_name: str, value: float):
        """Update KPI value"""
        trigger_id = f"kpi_{kpi_name}"
        if trigger_id in self.triggers:
            self.triggers[trigger_id].update_value(value)
    
    async def update_trust_score(self, component: str, score: float):
        """Update trust score"""
        trigger_id = f"trust_drop_{component}"
        if trigger_id in self.triggers:
            self.triggers[trigger_id].update_trust_score(score)
    
    async def on_sandbox_failure(self, sandbox_id: str, error: str):
        """Handle sandbox failure"""
        if "sandbox_failure" in self.triggers:
            await self.triggers["sandbox_failure"].on_sandbox_failure(sandbox_id, error)
    
    async def record_event(self, event_type: str):
        """Record event for anomaly detection"""
        for trigger in self.triggers.values():
            if trigger.trigger_type == TriggerType.EVENT_ANOMALY:
                trigger.record_event(event_type)
    
    def get_status(self) -> Dict[str, Any]:
        """Get trigger system status"""
        return {
            "enabled_triggers": len([t for t in self.triggers.values() if t.enabled]),
            "total_triggers": len(self.triggers),
            "statistics": self.stats,
            "active_triggers": {
                tid: {
                    "type": t.trigger_type.value,
                    "playbook": t.playbook_name,
                    "fire_count": t.fire_count,
                    "last_fired": t.last_fired.isoformat() if t.last_fired else None
                }
                for tid, t in self.triggers.items()
            }
        }
    
    async def shutdown(self):
        """Stop trigger monitoring"""
        if self._monitor_task:
            self._monitor_task.cancel()
        if self._scheduled_task:
            self._scheduled_task.cancel()


# Global instance
trigger_manager = TriggerManager()
'    KERNEL_HANDSHAKE_FAILURE = "kernel_handshake_failure"' 
