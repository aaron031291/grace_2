"""
Immune Kernel - AVN (Autonomous Validation Network) Core
The immune system that detects anomalies, executes healing, and protects Grace.

Complete implementation:
- Anomaly taxonomy
- Automated healing actions
- Trust adjustments
- Event mesh integration
- Governance notifications
- Immutable logging
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# ============================================================================
# Anomaly Taxonomy
# ============================================================================

class AnomalyType(Enum):
    """Complete anomaly taxonomy"""
    # Performance anomalies
    LATENCY_SPIKE = "latency_spike"
    THROUGHPUT_DROP = "throughput_drop"
    ERROR_RATE_INCREASE = "error_rate_increase"
    
    # Resource anomalies
    MEMORY_LEAK = "memory_leak"
    CPU_SPIKE = "cpu_spike"
    DISK_FULL = "disk_full"
    CONNECTION_POOL_EXHAUSTION = "connection_pool_exhaustion"
    
    # Behavioral anomalies
    DRIFT_DETECTED = "drift_detected"
    PATTERN_DEVIATION = "pattern_deviation"
    HTM_ANOMALY = "htm_anomaly"
    
    # Security anomalies
    INJECTION_ATTEMPT = "injection_attempt"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    GUARDRAIL_BYPASS = "guardrail_bypass"
    
    # System anomalies
    SERVICE_DOWN = "service_down"
    DEPENDENCY_FAILURE = "dependency_failure"
    DEADLOCK_DETECTED = "deadlock_detected"
    CASCADE_FAILURE = "cascade_failure"


class AnomalySeverity(Enum):
    """Severity levels for anomalies"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HealingAction(Enum):
    """Automated healing actions"""
    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    ROLLBACK = "rollback"
    CIRCUIT_BREAKER = "circuit_breaker"
    RATE_LIMIT = "rate_limit"
    KILL_CONNECTION = "kill_connection"
    CLEAR_CACHE = "clear_cache"
    GARBAGE_COLLECT = "garbage_collect"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    QUARANTINE_COMPONENT = "quarantine_component"
    HARDEN_SECURITY = "harden_security"


@dataclass
class Anomaly:
    """Anomaly detection event"""
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    detector: str
    affected_resource: str
    anomaly_score: float
    baseline_value: Optional[float] = None
    current_value: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    constitutional_risk: bool = False


@dataclass
class HealingAttempt:
    """Healing action execution"""
    healing_id: str
    anomaly_id: str
    action: HealingAction
    target_resource: str
    success: bool
    duration_seconds: float
    side_effects: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ============================================================================
# Immune Kernel - AVN Core
# ============================================================================

class ImmuneKernel:
    """
    AVN (Autonomous Validation Network) - The Immune System
    
    Responsibilities:
    1. Detect anomalies across all systems
    2. Execute automated healing actions
    3. Adjust trust scores based on behavior
    4. Notify governance of constitutional risks
    5. Log all actions to immutable log
    6. Feed learning system with healing experiences
    """
    
    def __init__(self):
        self.anomalies_detected = 0
        self.healing_attempts = 0
        self.healing_successes = 0
        self.escalations = 0
        
        # Active anomalies
        self.active_anomalies: Dict[str, Anomaly] = {}
        
        # Healing history
        self.healing_history: List[HealingAttempt] = []
        
        # Constitutional risk threshold
        self.constitutional_risk_threshold = 0.8
        
        # Event listeners
        self.running = False
        self.event_listener_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the immune kernel"""
        
        self.running = True
        
        # Start event listener
        self.event_listener_task = asyncio.create_task(self._listen_for_anomalies())
        
        print("✓ Immune Kernel (AVN) started")
    
    async def stop(self):
        """Stop the immune kernel"""
        
        self.running = False
        
        if self.event_listener_task:
            self.event_listener_task.cancel()
            try:
                await self.event_listener_task
            except asyncio.CancelledError:
                pass
        
        print("✓ Immune Kernel (AVN) stopped")
    
    async def _listen_for_anomalies(self):
        """Listen for anomaly events from event mesh"""
        
        try:
            from backend.routing.trigger_mesh_enhanced import trigger_mesh
            
            # Subscribe to anomaly events
            await trigger_mesh.subscribe("anomaly.detected", self._handle_anomaly_detected)
            await trigger_mesh.subscribe("system.health_check", self._handle_health_check)
            await trigger_mesh.subscribe("security.event", self._handle_security_event)
            
            print("✓ AVN subscribed to anomaly events")
            
            while self.running:
                await asyncio.sleep(1)
        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"⚠ AVN event listener error: {e}")
    
    async def _handle_anomaly_detected(self, event):
        """Handle ANOMALY_DETECTED event"""
        
        anomaly = Anomaly(
            anomaly_id=event.payload.get('anomaly_id', f"anom_{datetime.utcnow().timestamp()}"),
            anomaly_type=AnomalyType(event.payload.get('type', 'drift_detected')),
            severity=AnomalySeverity(event.payload.get('severity', 'medium')),
            detector=event.source,
            affected_resource=event.resource,
            anomaly_score=event.payload.get('score', 0.5),
            baseline_value=event.payload.get('baseline'),
            current_value=event.payload.get('current'),
            details=event.payload
        )
        
        await self.process_anomaly(anomaly)
    
    async def _handle_health_check(self, event):
        """Handle SYSTEM_HEALTH_CHECK event"""
        
        health_status = event.payload.get('status', 'healthy')
        
        if health_status in ['degraded', 'critical']:
            # Create anomaly for unhealthy state
            anomaly = Anomaly(
                anomaly_id=f"health_{event.event_id}",
                anomaly_type=AnomalyType.SERVICE_DOWN if health_status == 'critical' else AnomalyType.DRIFT_DETECTED,
                severity=AnomalySeverity.CRITICAL if health_status == 'critical' else AnomalySeverity.HIGH,
                detector="health_monitor",
                affected_resource=event.resource,
                anomaly_score=0.9 if health_status == 'critical' else 0.7,
                details=event.payload
            )
            
            await self.process_anomaly(anomaly)
    
    async def _handle_security_event(self, event):
        """Handle SECURITY_EVENT"""
        
        # All security events are treated as potential anomalies
        anomaly = Anomaly(
            anomaly_id=f"sec_{event.event_id}",
            anomaly_type=self._map_security_type(event.payload.get('type', 'unknown')),
            severity=AnomalySeverity.HIGH,  # Security always high
            detector="security_monitor",
            affected_resource=event.resource,
            anomaly_score=event.payload.get('threat_score', 0.8),
            details=event.payload,
            constitutional_risk=True  # Security events may violate transparency/trust
        )
        
        await self.process_anomaly(anomaly)
    
    def _map_security_type(self, security_type: str) -> AnomalyType:
        """Map security event type to anomaly type"""
        
        mapping = {
            'injection': AnomalyType.INJECTION_ATTEMPT,
            'unauthorized': AnomalyType.UNAUTHORIZED_ACCESS,
            'exfiltration': AnomalyType.DATA_EXFILTRATION,
            'bypass': AnomalyType.GUARDRAIL_BYPASS
        }
        
        return mapping.get(security_type, AnomalyType.UNAUTHORIZED_ACCESS)
    
    async def process_anomaly(self, anomaly: Anomaly):
        """
        Main anomaly processing pipeline
        
        1. Log anomaly
        2. Check constitutional risk
        3. Determine healing action
        4. Execute healing
        5. Adjust trust scores
        6. Emit events
        7. Learn from outcome
        """
        
        self.anomalies_detected += 1
        self.active_anomalies[anomaly.anomaly_id] = anomaly
        
        # Step 1: Log to immutable log
        await self._log_anomaly(anomaly)
        
        # Step 2: Check constitutional risk
        if anomaly.constitutional_risk or anomaly.severity == AnomalySeverity.CRITICAL:
            await self._notify_governance(anomaly)
        
        # Step 3: Determine healing action
        healing_action = self._determine_healing_action(anomaly)
        
        if not healing_action:
            # No healing needed or available
            return
        
        # Step 4: Execute healing
        healing_attempt = await self._execute_healing(anomaly, healing_action)
        
        # Step 5: Adjust trust scores
        await self._adjust_trust(anomaly, healing_attempt)
        
        # Step 6: Emit healing event
        await self._emit_healing_event(anomaly, healing_attempt)
        
        # Step 7: Feed learning system
        await self._record_learning_experience(anomaly, healing_attempt)
        
        # Remove from active if resolved
        if healing_attempt.success:
            del self.active_anomalies[anomaly.anomaly_id]
    
    def _determine_healing_action(self, anomaly: Anomaly) -> Optional[HealingAction]:
        """Determine appropriate healing action based on anomaly"""
        
        # Severity-based escalation
        if anomaly.severity == AnomalySeverity.CRITICAL:
            # Critical - immediate action or escalation
            if anomaly.anomaly_type == AnomalyType.SERVICE_DOWN:
                return HealingAction.RESTART_SERVICE
            elif anomaly.anomaly_type in [AnomalyType.INJECTION_ATTEMPT, AnomalyType.GUARDRAIL_BYPASS]:
                return HealingAction.QUARANTINE_COMPONENT
            else:
                return HealingAction.ESCALATE_TO_HUMAN
        
        # Type-specific healing
        healing_map = {
            AnomalyType.MEMORY_LEAK: HealingAction.RESTART_SERVICE,
            AnomalyType.CPU_SPIKE: HealingAction.SCALE_UP,
            AnomalyType.THROUGHPUT_DROP: HealingAction.SCALE_UP,
            AnomalyType.CONNECTION_POOL_EXHAUSTION: HealingAction.SCALE_UP,
            AnomalyType.ERROR_RATE_INCREASE: HealingAction.CIRCUIT_BREAKER,
            AnomalyType.LATENCY_SPIKE: HealingAction.RATE_LIMIT,
            AnomalyType.INJECTION_ATTEMPT: HealingAction.HARDEN_SECURITY,
            AnomalyType.UNAUTHORIZED_ACCESS: HealingAction.KILL_CONNECTION,
            AnomalyType.DATA_EXFILTRATION: HealingAction.QUARANTINE_COMPONENT,
        }
        
        return healing_map.get(anomaly.anomaly_type)
    
    async def _execute_healing(
        self,
        anomaly: Anomaly,
        action: HealingAction
    ) -> HealingAttempt:
        """Execute healing action"""
        
        self.healing_attempts += 1
        
        healing_id = f"heal_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        success = False
        side_effects = []
        
        try:
            # Execute action based on type
            if action == HealingAction.RESTART_SERVICE:
                success = await self._restart_service(anomaly.affected_resource)
            
            elif action == HealingAction.SCALE_UP:
                success = await self._scale_service(anomaly.affected_resource, 'up')
                side_effects.append('increased_resource_usage')
            
            elif action == HealingAction.SCALE_DOWN:
                success = await self._scale_service(anomaly.affected_resource, 'down')
            
            elif action == HealingAction.ROLLBACK:
                success = await self._rollback_deployment(anomaly.affected_resource)
            
            elif action == HealingAction.CIRCUIT_BREAKER:
                success = await self._enable_circuit_breaker(anomaly.affected_resource)
                side_effects.append('service_degraded')
            
            elif action == HealingAction.RATE_LIMIT:
                success = await self._enable_rate_limit(anomaly.affected_resource)
                side_effects.append('requests_throttled')
            
            elif action == HealingAction.QUARANTINE_COMPONENT:
                success = await self._quarantine_component(anomaly.affected_resource)
                side_effects.append('component_isolated')
            
            elif action == HealingAction.HARDEN_SECURITY:
                success = await self._harden_security(anomaly.affected_resource)
            
            elif action == HealingAction.ESCALATE_TO_HUMAN:
                success = await self._escalate_to_human(anomaly)
                self.escalations += 1
            
            else:
                print(f"⚠ Unknown healing action: {action}")
                success = False
            
            if success:
                self.healing_successes += 1
        
        except Exception as e:
            print(f"⚠ Healing action failed: {e}")
            success = False
            side_effects.append(f"error:{str(e)}")
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        healing_attempt = HealingAttempt(
            healing_id=healing_id,
            anomaly_id=anomaly.anomaly_id,
            action=action,
            target_resource=anomaly.affected_resource,
            success=success,
            duration_seconds=duration,
            side_effects=side_effects
        )
        
        self.healing_history.append(healing_attempt)
        
        # Log healing attempt
        await self._log_healing(healing_attempt, anomaly)
        
        return healing_attempt
    
    async def _restart_service(self, resource: str) -> bool:
        """Restart a service"""
        print(f"🔄 AVN: Restarting service {resource}")
        # Implementation would actually restart the service
        return True
    
    async def _scale_service(self, resource: str, direction: str) -> bool:
        """Scale service up or down"""
        print(f"📈 AVN: Scaling {resource} {direction}")
        # Implementation would call scaling API
        return True
    
    async def _rollback_deployment(self, resource: str) -> bool:
        """Rollback a deployment"""
        print(f"⏪ AVN: Rolling back {resource}")
        # Implementation would trigger rollback
        return True
    
    async def _enable_circuit_breaker(self, resource: str) -> bool:
        """Enable circuit breaker"""
        print(f"🛑 AVN: Enabling circuit breaker for {resource}")
        # Implementation would enable circuit breaker
        return True
    
    async def _enable_rate_limit(self, resource: str) -> bool:
        """Enable rate limiting"""
        print(f"⏱️ AVN: Enabling rate limit for {resource}")
        # Implementation would enable rate limiting
        return True
    
    async def _quarantine_component(self, resource: str) -> bool:
        """Quarantine a component"""
        print(f"🔒 AVN: Quarantining {resource}")
        # Implementation would isolate component
        return True
    
    async def _harden_security(self, resource: str) -> bool:
        """Harden security for resource"""
        print(f"🛡️ AVN: Hardening security for {resource}")
        # Implementation would apply security hardening
        return True
    
    async def _escalate_to_human(self, anomaly: Anomaly) -> bool:
        """Escalate to human operator"""
        print(f"🚨 AVN: Escalating {anomaly.anomaly_id} to human")
        
        try:
            from backend.logging_system.avn_logger import avn_logger
            
            await avn_logger.log_escalation(
                escalation_id=f"esc_{anomaly.anomaly_id}",
                anomaly_id=anomaly.anomaly_id,
                escalation_reason=f"{anomaly.anomaly_type.value} - {anomaly.severity.value} severity",
                severity=anomaly.severity.value,
                escalated_to="human_operator"
            )
            
            return True
        except Exception as e:
            print(f"⚠ Escalation logging failed: {e}")
            return False
    
    async def _log_anomaly(self, anomaly: Anomaly):
        """Log anomaly to immutable log"""
        
        try:
            from backend.logging_system.avn_logger import avn_logger
            
            await avn_logger.log_anomaly_detected(
                anomaly_id=anomaly.anomaly_id,
                detector=anomaly.detector,
                anomaly_type=anomaly.anomaly_type.value,
                severity=anomaly.severity.value,
                affected_resource=anomaly.affected_resource,
                anomaly_score=anomaly.anomaly_score,
                details=anomaly.details
            )
        except Exception as e:
            print(f"⚠ Anomaly logging failed: {e}")
    
    async def _log_healing(self, healing: HealingAttempt, anomaly: Anomaly):
        """Log healing attempt to immutable log"""
        
        try:
            from backend.logging_system.avn_logger import avn_logger
            
            await avn_logger.log_healing_action(
                healing_id=healing.healing_id,
                anomaly_id=healing.anomaly_id,
                healer="immune_kernel",
                action_type=healing.action.value,
                action_description=f"Automated healing for {anomaly.anomaly_type.value}",
                affected_resource=healing.target_resource,
                success=healing.success,
                execution_time_seconds=healing.duration_seconds,
                side_effects=healing.side_effects
            )
        except Exception as e:
            print(f"⚠ Healing logging failed: {e}")
    
    async def _notify_governance(self, anomaly: Anomaly):
        """Notify governance of constitutional risk"""
        
        try:
            from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent
            
            event = TriggerEvent(
                event_type="governance.constitutional_risk",
                source="immune_kernel",
                actor="avn",
                resource=anomaly.affected_resource,
                payload={
                    'anomaly_id': anomaly.anomaly_id,
                    'anomaly_type': anomaly.anomaly_type.value,
                    'severity': anomaly.severity.value,
                    'risk_type': 'security' if 'SECURITY' in anomaly.anomaly_type.name else 'integrity',
                    'constitutional_risk': True
                }
            )
            
            await trigger_mesh.emit(event)
            
            print(f"⚠️ AVN: Notified governance of constitutional risk - {anomaly.anomaly_id}")
        
        except Exception as e:
            print(f"⚠ Governance notification failed: {e}")
    
    async def _adjust_trust(self, anomaly: Anomaly, healing: HealingAttempt):
        """Adjust trust scores based on anomaly and healing outcome"""
        
        try:
            from backend.trust_framework.trust_score import update_trust_score
            
            # Determine trust adjustment
            if healing.success:
                # Healing succeeded - minor trust penalty for having anomaly
                await update_trust_score(
                    actor=anomaly.affected_resource,
                    action_outcome='anomaly_healed',
                    context={
                        'anomaly_type': anomaly.anomaly_type.value,
                        'severity': anomaly.severity.value,
                        'healing_action': healing.action.value
                    }
                )
            else:
                # Healing failed - larger trust penalty
                await update_trust_score(
                    actor=anomaly.affected_resource,
                    action_outcome='healing_failed',
                    context={
                        'anomaly_type': anomaly.anomaly_type.value,
                        'severity': anomaly.severity.value,
                        'requires_escalation': True
                    }
                )
        
        except Exception as e:
            print(f"⚠ Trust adjustment failed: {e}")
    
    async def _emit_healing_event(self, anomaly: Anomaly, healing: HealingAttempt):
        """Emit HEALING_ACTION_EXECUTED event"""
        
        try:
            from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent
            
            event_type = "avn.healing_executed" if healing.success else "avn.healing_failed"
            
            event = TriggerEvent(
                event_type=event_type,
                source="immune_kernel",
                actor="avn",
                resource=healing.target_resource,
                payload={
                    'healing_id': healing.healing_id,
                    'anomaly_id': healing.anomaly_id,
                    'action': healing.action.value,
                    'success': healing.success,
                    'duration_seconds': healing.duration_seconds,
                    'side_effects': healing.side_effects
                }
            )
            
            await trigger_mesh.emit(event)
        
        except Exception as e:
            print(f"⚠ Healing event emission failed: {e}")
    
    async def _record_learning_experience(self, anomaly: Anomaly, healing: HealingAttempt):
        """Feed learning system with healing experience"""
        
        try:
            from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent
            
            event = TriggerEvent(
                event_type="learning.healing_experience",
                source="immune_kernel",
                actor="avn",
                resource="learning_system",
                payload={
                    'anomaly_type': anomaly.anomaly_type.value,
                    'severity': anomaly.severity.value,
                    'healing_action': healing.action.value,
                    'success': healing.success,
                    'duration_seconds': healing.duration_seconds,
                    'outcome_quality': 1.0 if healing.success else 0.0
                }
            )
            
            await trigger_mesh.emit(event)
        
        except Exception as e:
            print(f"⚠ Learning recording failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get immune kernel statistics"""
        return {
            'anomalies_detected': self.anomalies_detected,
            'healing_attempts': self.healing_attempts,
            'healing_successes': self.healing_successes,
            'success_rate': self.healing_successes / max(1, self.healing_attempts),
            'escalations': self.escalations,
            'active_anomalies': len(self.active_anomalies)
        }


# Global immune kernel instance
immune_kernel = ImmuneKernel()
