"""
Immutable Log Integration - Universal Subsystem Logging

Ensures every subsystem in GRACE properly logs to the immutable ledger.
Provides:
- Standardized logging patterns
- Automatic context enrichment
- Pattern detection triggers
- Compliance enforcement
"""

from __future__ import annotations
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from collections import defaultdict, deque
import json

from .immutable_log import immutable_log
from .trigger_mesh import trigger_mesh, TriggerEvent


class SubsystemLogger:
    """
    Wrapper for subsystem logging to immutable log.
    
    Ensures consistent logging patterns and automatically enriches context.
    """
    
    def __init__(self, subsystem_name: str):
        self.subsystem = subsystem_name
        self.event_counts = defaultdict(int)
        self.last_logged: Optional[datetime] = None
    
    async def log_action(
        self,
        actor: str,
        action: str,
        resource: str,
        result: str,
        payload: Optional[Dict] = None,
        **kwargs
    ):
        """Log an action with automatic context enrichment"""
        
        enriched_payload = {
            **(payload or {}),
            "subsystem": self.subsystem,
            "event_count": self.event_counts[action],
            **kwargs
        }
        
        await immutable_log.append(
            actor=actor,
            action=action,
            resource=resource,
            subsystem=self.subsystem,
            payload=enriched_payload,
            result=result
        )
        
        self.event_counts[action] += 1
        self.last_logged = datetime.now(timezone.utc)
    
    async def log_start(self, actor: str = "system"):
        """Log subsystem startup"""
        await self.log_action(
            actor=actor,
            action=f"{self.subsystem}_started",
            resource=self.subsystem,
            result="started"
        )
    
    async def log_stop(self, actor: str = "system"):
        """Log subsystem shutdown"""
        await self.log_action(
            actor=actor,
            action=f"{self.subsystem}_stopped",
            resource=self.subsystem,
            result="stopped",
            payload={"total_events": sum(self.event_counts.values())}
        )
    
    async def log_error(
        self,
        actor: str,
        action: str,
        resource: str,
        error: Exception,
        **kwargs
    ):
        """Log an error with exception details"""
        await self.log_action(
            actor=actor,
            action=action,
            resource=resource,
            result="error",
            payload={
                "error_type": type(error).__name__,
                "error_message": str(error),
                **kwargs
            }
        )
    
    async def log_decision(
        self,
        actor: str,
        decision_type: str,
        resource: str,
        decision: str,
        reasoning: List[str],
        confidence: float,
        **kwargs
    ):
        """Log a decision with reasoning"""
        await self.log_action(
            actor=actor,
            action=f"decision_{decision_type}",
            resource=resource,
            result=decision,
            payload={
                "decision_type": decision_type,
                "reasoning": reasoning,
                "confidence": confidence,
                **kwargs
            }
        )
    
    async def log_prediction(
        self,
        actor: str,
        prediction_type: str,
        resource: str,
        predicted_value: Any,
        confidence: float,
        **kwargs
    ):
        """Log a prediction"""
        await self.log_action(
            actor=actor,
            action=f"prediction_{prediction_type}",
            resource=resource,
            result="predicted",
            payload={
                "prediction_type": prediction_type,
                "predicted_value": predicted_value,
                "confidence": confidence,
                **kwargs
            }
        )


class ImmutableLogAnalyzer:
    """
    Analyzes immutable log for patterns and triggers self-healing.
    
    Detects:
    - Recurring error patterns
    - Anomalous action sequences
    - Performance degradation trends
    - Trust violations
    """
    
    def __init__(self):
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self.pattern_history: deque = deque(maxlen=100)
    
    async def start(self):
        """Start pattern analysis loop"""
        if self.running:
            return
        
        self.running = True
        self._task = asyncio.create_task(self._analysis_loop())
        print("  [OK] Immutable log analyzer started")
    
    async def stop(self):
        """Stop pattern analysis"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print("  [OK] Immutable log analyzer stopped")
    
    async def _analysis_loop(self):
        """Continuous pattern analysis"""
        try:
            while self.running:
                try:
                    await self._analyze_recent_events()
                    await asyncio.sleep(60)  # Analyze every minute
                except Exception as e:
                    print(f"  Warning: Log analysis error: {e}")
                    await asyncio.sleep(60)
        except asyncio.CancelledError:
            pass
    
    async def _analyze_recent_events(self):
        """Analyze recent events for patterns"""
        try:
            from .models import async_session
            from sqlalchemy import select, func
            from .base_models import ImmutableLogEntry as ImmutableEntry
            
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
            
            async with async_session() as session:
                # Get recent events
                result = await session.execute(
                    select(ImmutableEntry)
                    .where(ImmutableEntry.timestamp >= cutoff)
                    .order_by(ImmutableEntry.timestamp.desc())
                    .limit(500)
                )
                events = result.scalars().all()
                
                if not events:
                    return
                
                # Detect recurring errors
                await self._detect_recurring_errors(events)
                
                # Detect anomalous sequences
                await self._detect_anomalous_sequences(events)
                
                # Detect performance degradation
                await self._detect_performance_degradation(events)
        
        except Exception as e:
            print(f"  Warning: Event analysis error: {e}")
    
    async def _detect_recurring_errors(self, events):
        """Detect recurring error patterns"""
        error_events = [e for e in events if e.result in ["error", "failed", "blocked"]]
        
        if not error_events:
            return
        
        # Group by (actor, action, resource)
        error_groups = defaultdict(list)
        for event in error_events:
            key = (event.actor, event.action, event.resource)
            error_groups[key].append(event)
        
        # Find patterns with 3+ occurrences in 10 minutes
        for key, group in error_groups.items():
            if len(group) >= 3:
                actor, action, resource = key
                
                pattern = {
                    "pattern_id": f"error_{actor}_{action}_{int(datetime.now().timestamp())}",
                    "pattern_type": "recurring_error",
                    "pattern_description": f"Recurring {action} errors on {resource}",
                    "resource": resource,
                    "actor": actor,
                    "action": action,
                    "occurrence_count": len(group),
                    "timespan": "10 minutes",
                    "confidence": min(0.9, 0.6 + (len(group) * 0.1)),
                    "severity": "high" if len(group) >= 5 else "medium",
                    "recommended_actions": ["investigate_root_cause", "rollback_flag", "restart_service"]
                }
                
                # Emit pattern detection event
                await trigger_mesh.publish(TriggerEvent(
                    event_type="immutable_log.pattern_detected",
                    source="immutable_log_analyzer",
                    actor="analyzer",
                    resource=resource,
                    payload=pattern,
                    timestamp=datetime.now(timezone.utc)
                ))
                
                self.pattern_history.append(pattern)
                
                print(f"  📜 Pattern: Recurring {action} errors ({len(group)}x) on {resource}")
    
    async def _detect_anomalous_sequences(self, events):
        """Detect anomalous event sequences"""
        
        # Look for unusual sequences: error -> retry -> error -> retry pattern
        sequence_buffer = []
        
        for event in sorted(events, key=lambda e: e.timestamp):
            sequence_buffer.append(event)
            if len(sequence_buffer) > 5:
                sequence_buffer.pop(0)
            
            # Detect error cascade pattern
            if len(sequence_buffer) >= 4:
                errors_in_sequence = sum(1 for e in sequence_buffer if e.result in ["error", "failed"])
                
                if errors_in_sequence >= 3:
                    resources = list(set(e.resource for e in sequence_buffer))
                    
                    sequence = {
                        "sequence_id": f"seq_{int(datetime.now().timestamp())}",
                        "sequence_type": "error_cascade",
                        "resource": resources[0] if len(resources) == 1 else "multiple",
                        "sequence_events": [f"{e.actor}.{e.action}:{e.result}" for e in sequence_buffer],
                        "confidence": 0.8,
                        "severity": "critical" if len(resources) > 1 else "high",
                        "recommended_actions": ["immediate_investigation", "rollback_flag"]
                    }
                    
                    await trigger_mesh.publish(TriggerEvent(
                        event_type="immutable_log.anomaly_sequence",
                        source="immutable_log_analyzer",
                        actor="analyzer",
                        resource=sequence["resource"],
                        payload=sequence,
                        timestamp=datetime.now(timezone.utc)
                    ))
                    
                    self.pattern_history.append(sequence)
                    
                    print(f"  📜 Sequence: Error cascade detected across {len(resources)} resource(s)")
                    
                    # Clear buffer to avoid duplicates
                    sequence_buffer.clear()
    
    async def _detect_performance_degradation(self, events):
        """Detect performance degradation from action timing"""
        
        # Group events by action type
        action_groups = defaultdict(list)
        for event in events:
            if hasattr(event, 'payload') and event.payload:
                try:
                    payload = json.loads(event.payload) if isinstance(event.payload, str) else event.payload
                    duration = payload.get('duration_ms')
                    if duration:
                        action_groups[event.action].append(duration)
                except Exception:
                    pass
        
        # Detect increasing latencies
        for action, durations in action_groups.items():
            if len(durations) >= 5:
                recent_avg = sum(durations[-3:]) / 3
                older_avg = sum(durations[:3]) / 3
                
                if recent_avg > older_avg * 1.5 and recent_avg > 100:
                    degradation = {
                        "pattern_id": f"perf_{action}_{int(datetime.now().timestamp())}",
                        "pattern_type": "performance_degradation",
                        "pattern_description": f"Action '{action}' slowing down",
                        "resource": action,
                        "metrics": {
                            "older_avg_ms": older_avg,
                            "recent_avg_ms": recent_avg,
                            "increase_pct": ((recent_avg / older_avg) - 1) * 100
                        },
                        "confidence": 0.75,
                        "severity": "medium",
                        "recommended_actions": ["investigate_performance", "scale_up_instances"]
                    }
                    
                    await trigger_mesh.publish(TriggerEvent(
                        event_type="immutable_log.pattern_detected",
                        source="immutable_log_analyzer",
                        actor="analyzer",
                        resource=action,
                        payload=degradation,
                        timestamp=datetime.now(timezone.utc)
                    ))
                    
                    print(f"  📜 Performance: {action} degrading ({older_avg:.0f}ms -> {recent_avg:.0f}ms)")


class SubsystemLogRegistry:
    """
    Registry of all subsystems and their logging status.
    Ensures every subsystem logs to immutable log.
    """
    
    def __init__(self):
        self.registered_subsystems: Dict[str, SubsystemLogger] = {}
    
    def register(self, subsystem_name: str) -> SubsystemLogger:
        """Register a subsystem and get its logger"""
        if subsystem_name not in self.registered_subsystems:
            logger = SubsystemLogger(subsystem_name)
            self.registered_subsystems[subsystem_name] = logger
        
        return self.registered_subsystems[subsystem_name]
    
    def get_subsystem_stats(self) -> Dict[str, Any]:
        """Get logging statistics for all subsystems"""
        return {
            name: {
                "event_counts": dict(logger.event_counts),
                "total_events": sum(logger.event_counts.values()),
                "last_logged": logger.last_logged.isoformat() if logger.last_logged else None
            }
            for name, logger in self.registered_subsystems.items()
        }


# Singleton instances
subsystem_registry = SubsystemLogRegistry()
log_analyzer = ImmutableLogAnalyzer()


# Convenience function to get subsystem logger
def get_subsystem_logger(subsystem_name: str) -> SubsystemLogger:
    """Get or create a logger for a subsystem"""
    return subsystem_registry.register(subsystem_name)
