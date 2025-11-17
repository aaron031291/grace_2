"""
ACL Violation Monitor - Dedicated Safeguard for Message Bus Spam
Watches for ACL violations and triggers playbooks before system degrades

Fixes Gap: S02_acl_spam scenario had no watcher
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from collections import deque, defaultdict

from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent

logger = logging.getLogger(__name__)


class ACLViolationMonitor:
    """
    Monitors message bus ACL violations and triggers safeguards
    
    Detects:
    - Spam attacks (>10 violations/second)
    - Repeated violations from same actor
    - Control topic flooding
    - Privilege escalation attempts
    
    Actions:
    - Triggers ACL violation playbook
    - Routes to coding agent for persistent fixes
    - Blacklists abusive actors
    - Notifies security team
    """
    
    def __init__(self):
        # Violation tracking
        self.violation_log = deque(maxlen=1000)  # Last 1000 violations
        self.actor_violations = defaultdict(int)
        self.topic_violations = defaultdict(int)
        
        # Thresholds
        self.spam_threshold = 10  # violations per second
        self.actor_threshold = 20  # violations per actor before blacklist
        self.control_topic_threshold = 5  # violations on control topics
        
        # State
        self.running = False
        self.blacklist = set()
        
        # Statistics
        self.stats = {
            "total_violations": 0,
            "spam_incidents": 0,
            "playbooks_triggered": 0,
            "actors_blacklisted": 0
        }
    
    async def start(self):
        """Start ACL violation monitoring"""
        
        if self.running:
            return
        
        self.running = True
        
        # Subscribe to ACL violation events
        try:
            trigger_mesh.subscribe("message_bus.acl_violation", self._handle_acl_violation)
            logger.info("[ACL MONITOR] Subscribed to message_bus.acl_violation events")
        except Exception as e:
            logger.error(f"[ACL MONITOR] Failed to subscribe: {e}")
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
        
        logger.info("[ACL MONITOR] ACL violation monitor started")
    
    async def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info("[ACL MONITOR] ACL violation monitor stopped")
    
    async def _handle_acl_violation(self, event: TriggerEvent):
        """Handle ACL violation event"""
        
        payload = event.payload if hasattr(event, 'payload') else {}
        
        actor = payload.get("actor", "unknown")
        topic = payload.get("topic", "unknown")
        timestamp = datetime.utcnow()
        
        # Record violation
        violation = {
            "actor": actor,
            "topic": topic,
            "timestamp": timestamp,
            "event_id": getattr(event, 'event_id', None)
        }
        
        self.violation_log.append(violation)
        self.actor_violations[actor] += 1
        self.topic_violations[topic] += 1
        self.stats["total_violations"] += 1
        
        logger.warning(f"[ACL MONITOR] Violation: {actor} -> {topic}")
        
        # Check for spam attack
        await self._check_spam_attack()
        
        # Check actor threshold
        await self._check_actor_threshold(actor)
        
        # Check control topic flooding
        if "control" in topic.lower():
            await self._check_control_flooding(topic)
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        
        while self.running:
            try:
                # Check every 5 seconds
                await asyncio.sleep(5)
                
                # Clean old violations (>60s)
                await self._clean_old_violations()
                
            except Exception as e:
                logger.error(f"[ACL MONITOR] Monitoring loop error: {e}")
    
    async def _clean_old_violations(self):
        """Remove violations older than 60 seconds"""
        
        cutoff = datetime.utcnow() - timedelta(seconds=60)
        
        # Filter recent violations
        recent = [v for v in self.violation_log if v["timestamp"] > cutoff]
        
        # If significantly fewer, update
        if len(recent) < len(self.violation_log) * 0.8:
            self.violation_log.clear()
            self.violation_log.extend(recent)
    
    async def _check_spam_attack(self):
        """Check for spam attack (>10 violations/second)"""
        
        # Count violations in last second
        cutoff = datetime.utcnow() - timedelta(seconds=1)
        recent = [v for v in self.violation_log if v["timestamp"] > cutoff]
        
        if len(recent) >= self.spam_threshold:
            logger.error(f"[ACL MONITOR] SPAM ATTACK DETECTED: {len(recent)} violations/second")
            
            self.stats["spam_incidents"] += 1
            
            # Trigger playbook
            await self._trigger_acl_playbook(
                reason="spam_attack",
                details={
                    "violations_per_second": len(recent),
                    "threshold": self.spam_threshold
                }
            )
    
    async def _check_actor_threshold(self, actor: str):
        """Check if actor exceeded violation threshold"""
        
        if self.actor_violations[actor] >= self.actor_threshold:
            logger.error(f"[ACL MONITOR] ACTOR THRESHOLD EXCEEDED: {actor} ({self.actor_violations[actor]} violations)")
            
            # Blacklist actor
            if actor not in self.blacklist:
                self.blacklist.add(actor)
                self.stats["actors_blacklisted"] += 1
                
                # Trigger playbook
                await self._trigger_acl_playbook(
                    reason="actor_blacklist",
                    details={
                        "actor": actor,
                        "total_violations": self.actor_violations[actor]
                    }
                )
                
                # Notify security
                await self._notify_security_team(
                    alert_type="actor_blacklisted",
                    actor=actor,
                    violations=self.actor_violations[actor]
                )
    
    async def _check_control_flooding(self, topic: str):
        """Check for control topic flooding"""
        
        if self.topic_violations[topic] >= self.control_topic_threshold:
            logger.error(f"[ACL MONITOR] CONTROL TOPIC FLOODING: {topic} ({self.topic_violations[topic]} violations)")
            
            # Trigger playbook
            await self._trigger_acl_playbook(
                reason="control_topic_flood",
                details={
                    "topic": topic,
                    "violations": self.topic_violations[topic]
                }
            )
    
    async def _trigger_acl_playbook(self, reason: str, details: Dict[str, Any]):
        """Trigger ACL violation remediation playbook"""
        
        self.stats["playbooks_triggered"] += 1
        
        # Publish incident event
        await trigger_mesh.publish(TriggerEvent(
            source="acl_violation_monitor",
            event_type="event.incident",
            payload={
                "trigger_id": "acl_violation_monitor",
                "playbook": "message_bus_acl_violation_fix",
                "severity": "high",
                "reason": reason,
                "details": details,
                "timestamp": datetime.utcnow().isoformat()
            }
        ))
        
        logger.info(f"[ACL MONITOR] Triggered playbook: message_bus_acl_violation_fix (reason: {reason})")
    
    async def _notify_security_team(self, alert_type: str, actor: str, violations: int):
        """Notify security team of critical event"""
        
        await trigger_mesh.publish(TriggerEvent(
            source="acl_violation_monitor",
            event_type="security.alert",
            payload={
                "alert_type": alert_type,
                "actor": actor,
                "violations": violations,
                "blacklisted": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        ))
        
        logger.warning(f"[ACL MONITOR] Security alert: {alert_type} - actor: {actor}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get monitor statistics"""
        return {
            **self.stats,
            "recent_violations": len(self.violation_log),
            "blacklisted_actors": len(self.blacklist),
            "monitored_actors": len(self.actor_violations),
            "monitored_topics": len(self.topic_violations)
        }
    
    def is_blacklisted(self, actor: str) -> bool:
        """Check if actor is blacklisted"""
        return actor in self.blacklist


# Global monitor instance
acl_violation_monitor = ACLViolationMonitor()
