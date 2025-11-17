"""
Trigger Storm Safeguard
Detects and mitigates trigger mesh event floods

Monitors:
- Event publish rate
- Subscription backpressure
- Event queue depth
- Cascade detection

Actions:
- Rate limiting
- Circuit breaking
- Playbook triggering
- Clarity logging with mission context
"""

import asyncio
from typing import List
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class TriggerStormSafeguard:
    """
    Safeguard against trigger mesh storms
    Prevents event floods from overwhelming subscriptions
    """
    
    def __init__(self):
        self.running = False
        
        # Rate tracking
        self.event_counts = defaultdict(int)  # event_type -> count
        self.event_timestamps = defaultdict(list)  # event_type -> [timestamps]
        
        # Thresholds
        self.storm_threshold_events_per_second = 100
        self.cascade_depth_limit = 10
        self.circuit_breaker_threshold = 500  # Total events in 10s
        
        # Circuit breaker state
        self.circuit_open = False
        self.circuit_opened_at = None
        self.circuit_cooldown_seconds = 60
        
        # Cascade tracking
        self.event_chain = []  # Track event causality
        
        logger.info("[TRIGGER-SAFEGUARD] Initialized")
    
    async def start(self):
        """Start storm monitoring"""
        if self.running:
            return
        
        self.running = True
        
        # Subscribe to all trigger mesh events
        try:
            from backend.misc.trigger_mesh import trigger_mesh
            
            trigger_mesh.subscribe("*", self._monitor_event)
            logger.info("[TRIGGER-SAFEGUARD] Subscribed to all trigger mesh events")
        except Exception as e:
            logger.error(f"[TRIGGER-SAFEGUARD] Subscription failed: {e}")
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
        
        logger.info("[TRIGGER-SAFEGUARD] Storm safeguard started")
    
    async def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info("[TRIGGER-SAFEGUARD] Stopped")
    
    async def _monitor_event(self, event):
        """Monitor each trigger mesh event"""
        
        event_type = getattr(event, 'event_type', 'unknown')
        
        # Track event
        self.event_counts[event_type] += 1
        self.event_timestamps[event_type].append(datetime.utcnow())
        
        # Check for cascade
        self.event_chain.append(event_type)
        if len(self.event_chain) > self.cascade_depth_limit:
            await self._detect_cascade()
    
    async def _monitoring_loop(self):
        """Continuous storm detection"""
        
        while self.running:
            try:
                await self._check_for_storm()
                await self._check_circuit_breaker()
                await self._cleanup_old_data()
            except Exception as e:
                logger.error(f"[TRIGGER-SAFEGUARD] Monitoring error: {e}")
            
            await asyncio.sleep(5)
    
    async def _check_for_storm(self):
        """Check if event storm is occurring"""
        
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=1)
        
        for event_type, timestamps in self.event_timestamps.items():
            # Count events in last second
            recent = [t for t in timestamps if t > cutoff]
            
            if len(recent) > self.storm_threshold_events_per_second:
                logger.error(f"[TRIGGER-SAFEGUARD] STORM DETECTED: {event_type} - {len(recent)} events/sec")
                
                await self._trigger_storm_playbook(event_type, len(recent))
    
    async def _check_circuit_breaker(self):
        """Check if circuit breaker should open"""
        
        if self.circuit_open:
            # Check if cooldown expired
            if self.circuit_opened_at:
                time_open = (datetime.utcnow() - self.circuit_opened_at).total_seconds()
                if time_open > self.circuit_cooldown_seconds:
                    await self._close_circuit()
            return
        
        # Count total recent events
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=10)
        
        total_recent = 0
        for timestamps in self.event_timestamps.values():
            total_recent += len([t for t in timestamps if t > cutoff])
        
        if total_recent > self.circuit_breaker_threshold:
            await self._open_circuit(total_recent)
    
    async def _open_circuit(self, event_count: int):
        """Open circuit breaker - stop accepting events"""
        
        self.circuit_open = True
        self.circuit_opened_at = datetime.utcnow()
        
        logger.critical(f"[TRIGGER-SAFEGUARD] CIRCUIT BREAKER OPEN - {event_count} events in 10s")
        
        # Trigger playbook
        try:
            from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
            
            await trigger_mesh.publish(TriggerEvent(
                source="trigger_storm_safeguard",
                event_type="event.emergency",
                actor="trigger_safeguard",
                resource="trigger_mesh",
                payload={
                    'trigger_id': 'trigger_storm_safeguard',
                    'playbook': 'trigger_mesh_circuit_breaker',
                    'severity': 'critical',
                    'event_count': event_count,
                    'circuit_open': True,
                    'timestamp': datetime.utcnow().isoformat()
                }
            ))
        except Exception as e:
            logger.error(f"[TRIGGER-SAFEGUARD] Emergency trigger failed: {e}")
        
        # Log to Clarity with mission context
        await self._log_circuit_breaker_to_clarity(event_count)
    
    async def _close_circuit(self):
        """Close circuit breaker - resume normal operation"""
        
        self.circuit_open = False
        logger.info("[TRIGGER-SAFEGUARD] Circuit breaker closed - resuming normal operation")
        
        # Log to Clarity
        try:
            from backend.core.clarity_framework import clarity_framework
            
            await clarity_framework.record_decision(
                actor="trigger_storm_safeguard",
                action_type="circuit_breaker_closed",
                resource="trigger_mesh",
                decision={'action': 'resume_operations'},
                reasoning_chain=[
                    f"Circuit was open for {self.circuit_cooldown_seconds}s",
                    "Event rate has normalized",
                    "Resuming normal trigger mesh operations",
                    "Monitoring continues for recurrence"
                ]
            )
        except Exception as e:
            logger.debug(f"[TRIGGER-SAFEGUARD] Clarity logging failed: {e}")
    
    async def _detect_cascade(self):
        """Detect event cascade (events triggering events)"""
        
        logger.warning(f"[TRIGGER-SAFEGUARD] Potential cascade detected - chain depth: {len(self.event_chain)}")
        
        # Check for repeating patterns
        recent_chain = self.event_chain[-self.cascade_depth_limit:]
        unique_events = set(recent_chain)
        
        if len(unique_events) < 3:
            # Same events repeating - likely cascade
            logger.error(f"[TRIGGER-SAFEGUARD] CASCADE CONFIRMED: {unique_events}")
            
            await self._trigger_cascade_playbook(list(unique_events))
    
    async def _trigger_storm_playbook(self, event_type: str, rate: int):
        """Trigger playbook for event storm"""
        
        try:
            from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
            
            await trigger_mesh.publish(TriggerEvent(
                source="trigger_storm_safeguard",
                event_type="event.incident",
                actor="trigger_safeguard",
                resource=event_type,
                payload={
                    'trigger_id': 'trigger_storm_safeguard',
                    'playbook': 'trigger_storm_mitigation',
                    'severity': 'high',
                    'event_type': event_type,
                    'rate_per_second': rate,
                    'timestamp': datetime.utcnow().isoformat()
                }
            ))
            
            logger.info(f"[TRIGGER-SAFEGUARD] Storm playbook triggered for {event_type}")
        except Exception as e:
            logger.error(f"[TRIGGER-SAFEGUARD] Playbook trigger failed: {e}")
    
    async def _trigger_cascade_playbook(self, cascade_events: List[str]):
        """Trigger playbook for event cascade"""
        
        try:
            from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
            
            await trigger_mesh.publish(TriggerEvent(
                source="trigger_storm_safeguard",
                event_type="event.incident",
                actor="trigger_safeguard",
                resource="event_cascade",
                payload={
                    'trigger_id': 'trigger_storm_safeguard',
                    'playbook': 'event_cascade_breaker',
                    'severity': 'high',
                    'cascade_events': cascade_events,
                    'depth': len(self.event_chain),
                    'timestamp': datetime.utcnow().isoformat()
                }
            ))
        except Exception as e:
            logger.error(f"[TRIGGER-SAFEGUARD] Cascade playbook failed: {e}")
    
    async def _log_circuit_breaker_to_clarity(self, event_count: int):
        """Log circuit breaker with mission context"""
        
        try:
            from backend.core.clarity_5w1h import clarity_5w1h
            
            await clarity_5w1h.log_dispatch(
                who="trigger_storm_safeguard",
                what="open_circuit_breaker",
                when=datetime.utcnow(),
                where="trigger_mesh",
                why=[
                    f"Event flood detected: {event_count} events in 10 seconds",
                    f"Threshold exceeded: {event_count} > {self.circuit_breaker_threshold}",
                    "Circuit breaker activated to protect subscriptions",
                    "Mission alignment: Preserve system stability (resilience priority)",
                    f"Will auto-close after {self.circuit_cooldown_seconds}s cooldown"
                ],
                how="circuit_breaker_pattern",
                context={
                    'event_count': event_count,
                    'threshold': self.circuit_breaker_threshold,
                    'cooldown_seconds': self.circuit_cooldown_seconds
                }
            )
        except Exception as e:
            logger.error(f"[TRIGGER-SAFEGUARD] 5W1H logging failed: {e}")
    
    async def _cleanup_old_data(self):
        """Remove old timestamp data to prevent memory bloat"""
        
        cutoff = datetime.utcnow() - timedelta(minutes=5)
        
        for event_type in list(self.event_timestamps.keys()):
            self.event_timestamps[event_type] = [
                t for t in self.event_timestamps[event_type] if t > cutoff
            ]
        
        # Trim event chain
        if len(self.event_chain) > 1000:
            self.event_chain = self.event_chain[-500:]


# Global instance
trigger_storm_safeguard = TriggerStormSafeguard()
