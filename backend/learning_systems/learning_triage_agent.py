"""
Learning Triage Agent
Autonomous diagnosis and learning mission launcher

Consumes events from:
- Guardian missions (mission.created, mission.resolved, *.error)
- HTM anomalies
- RAG health metrics
- Remote access telemetry
- Autonomous agent outcomes

Decides when to launch learning missions based on:
- Event clustering (domain, severity, recurrence)
- Knowledge gaps
- Success/failure patterns
- System health trends
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


@dataclass
class EventCluster:
    """Clustered events requiring learning attention"""
    
    domain: str  # 'guardian', 'htm', 'rag', 'remote_access', 'agent'
    severity: str  # 'low', 'medium', 'high', 'critical'
    pattern_type: str  # 'error', 'anomaly', 'degradation', 'failure'
    event_count: int = 0
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    events: List[Dict[str, Any]] = field(default_factory=list)
    learning_mission_id: Optional[str] = None
    resolved: bool = False
    
    def recurrence_score(self) -> float:
        """Calculate recurrence score (0-1)"""
        time_span = (self.last_seen - self.first_seen).total_seconds()
        if time_span < 60:
            return 0.3  # Too recent to determine pattern
        
        # Events per hour
        rate = self.event_count / (time_span / 3600)
        
        if rate > 10:
            return 1.0  # Very high recurrence
        elif rate > 5:
            return 0.8
        elif rate > 2:
            return 0.6
        elif rate > 1:
            return 0.4
        else:
            return 0.2
    
    def urgency_score(self) -> float:
        """Calculate urgency score (0-1)"""
        severity_map = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.5,
            'low': 0.2
        }
        
        base_urgency = severity_map.get(self.severity, 0.3)
        recurrence = self.recurrence_score()
        
        # Urgency = severity + recurrence weight
        return min(1.0, base_urgency * 0.6 + recurrence * 0.4)
    
    def should_launch_mission(self) -> bool:
        """Determine if this cluster warrants a learning mission"""
        
        # Already has mission or resolved
        if self.learning_mission_id or self.resolved:
            return False
        
        # High urgency = immediate mission
        if self.urgency_score() >= 0.7:
            return True
        
        # Multiple events in same domain
        if self.event_count >= 5:
            return True
        
        # Critical severity = always launch
        if self.severity == 'critical':
            return True
        
        return False


class LearningTriageAgent:
    """
    Autonomous learning triage system
    
    Continuously monitors system events, clusters them,
    and autonomously launches learning missions
    
    Automation Cadence:
    - Boot phase (fast loop): 15s intervals, critical issues only
    - Steady state (slow loop): 3-5 min intervals, all issues
    """
    
    def __init__(self):
        self.running = False
        self.event_buffer: List[Dict[str, Any]] = []
        self.clusters: Dict[str, EventCluster] = {}
        self.subscriptions: Set[str] = set()
        
        # State management
        self.boot_phase = True  # Start in boot phase
        self.boot_complete_time: Optional[datetime] = None
        
        # Cadence configuration
        self.boot_interval = 15  # 15 seconds during boot
        self.steady_interval = 180  # 3 minutes during steady state (can vary 3-5 min)
        self.current_interval = self.boot_interval
        
        # Priority thresholds
        self.boot_priority_threshold = 0.7  # Only critical during boot
        self.steady_priority_threshold = 0.3  # Lower bar during steady state
        
        # Statistics
        self.stats = {
            'events_processed': 0,
            'clusters_created': 0,
            'missions_launched': 0,
            'missions_suspended': 0,
            'last_triage': None,
            'triage_count': 0,
            'boot_phase': True
        }
        
        # Dependencies (injected on start)
        self.message_bus = None
        self.immutable_log = None
        self.rag_system = None
        self.mission_launcher = None
        self.guardian = None
    
    async def start(self):
        """Start the learning triage agent"""
        if self.running:
            return
        
        logger.info("[LEARNING-TRIAGE] Starting autonomous learning triage agent...")
        
        # Initialize dependencies
        try:
            from backend.core.message_bus import message_bus
            self.message_bus = message_bus
        except ImportError:
            logger.warning("[LEARNING-TRIAGE] Message bus not available")
        
        try:
            from backend.core.immutable_log import immutable_log
            self.immutable_log = immutable_log
        except ImportError:
            logger.warning("[LEARNING-TRIAGE] Immutable log not available")
        
        try:
            from backend.learning_systems.learning_mission_launcher import learning_mission_launcher
            self.mission_launcher = learning_mission_launcher
        except ImportError:
            logger.warning("[LEARNING-TRIAGE] Mission launcher not available")
        
        try:
            from backend.core.guardian import guardian
            self.guardian = guardian
        except ImportError:
            logger.warning("[LEARNING-TRIAGE] Guardian not available")
        
        # Subscribe to events
        await self._setup_subscriptions()
        
        # Subscribe to boot completion
        if self.message_bus:
            await self.message_bus.subscribe('grace.boot.complete', self._handle_boot_complete)
        
        self.running = True
        
        # Start triage loop
        asyncio.create_task(self._triage_loop())
        
        logger.info("[LEARNING-TRIAGE] ✅ Started")
        logger.info(f"[LEARNING-TRIAGE] Subscriptions: {len(self.subscriptions)}")
        logger.info(f"[LEARNING-TRIAGE] Boot phase: {self.boot_interval}s interval")
        logger.info(f"[LEARNING-TRIAGE] Steady state: {self.steady_interval}s interval")
        logger.info("[LEARNING-TRIAGE] Autonomous diagnosis: Active")
    
    async def stop(self):
        """Stop the learning triage agent"""
        self.running = False
        logger.info("[LEARNING-TRIAGE] Stopped")
    
    async def _setup_subscriptions(self):
        """Subscribe to all relevant event streams"""
        
        # Guardian missions
        subscriptions = [
            'mission.created',
            'mission.resolved',
            'mission.failed',
            'guardian.error',
            'guardian.warning',
            
            # HTM anomalies
            'htm.anomaly.detected',
            'htm.pattern.unusual',
            'htm.degradation',
            
            # RAG health
            'rag.health.degraded',
            'rag.retrieval.failed',
            'rag.confidence.low',
            
            # Remote access
            'remote_access.action.failed',
            'remote_access.governance.blocked',
            'firefox.browse.failed',
            'github.rate_limit',
            
            # Autonomous agents
            'agent.task.failed',
            'agent.error',
            'coding_agent.build.failed',
            'self_healing.remediation.failed',
            
            # System events
            'kernel.boot.failed',
            'service.degraded',
            'error.unhandled'
        ]
        
        for event_type in subscriptions:
            if self.message_bus:
                await self.message_bus.subscribe(event_type, self._handle_event)
            self.subscriptions.add(event_type)
        
        logger.info(f"[LEARNING-TRIAGE] Subscribed to {len(subscriptions)} event types")
    
    async def _handle_event(self, event: Dict[str, Any]):
        """Handle incoming event"""
        
        # Add to buffer for processing
        self.event_buffer.append({
            **event,
            'received_at': datetime.utcnow().isoformat()
        })
        
        self.stats['events_processed'] += 1
        
        # Log to immutable log
        if self.immutable_log:
            await self.immutable_log.append_entry(
                category='learning_triage',
                subcategory='event_received',
                data=event,
                actor='learning_triage_agent',
                action='event_received',
                resource=event.get('event_type', 'unknown')
            )
    
    async def _triage_loop(self):
        """
        Continuous triage loop with adaptive cadence
        
        Boot phase: 15s intervals, critical issues only
        Steady state: 3-5 min intervals, all issues
        """
        
        logger.info(f"[LEARNING-TRIAGE] Triage loop started")
        logger.info(f"[LEARNING-TRIAGE] Boot phase: {self.boot_interval}s intervals")
        logger.info(f"[LEARNING-TRIAGE] Steady state: {self.steady_interval}s intervals")
        
        while self.running:
            try:
                # Adaptive sleep based on phase
                await asyncio.sleep(self.current_interval)
                
                self.stats['triage_count'] += 1
                
                # Check if we should transition to steady state
                await self._check_phase_transition()
                
                if not self.event_buffer:
                    continue
                
                phase_label = "BOOT" if self.boot_phase else "STEADY"
                logger.info(
                    f"[LEARNING-TRIAGE] [{phase_label}] Processing {len(self.event_buffer)} events "
                    f"(interval: {self.current_interval}s)..."
                )
                
                # Process buffered events
                await self._process_events()
                
                # Analyze clusters (phase-aware)
                await self._analyze_clusters()
                
                # Launch missions if needed (phase-aware)
                await self._launch_missions()
                
                # Vary interval in steady state (3-5 minutes)
                if not self.boot_phase:
                    import random
                    self.current_interval = random.randint(180, 300)  # 3-5 minutes
                
                self.stats['last_triage'] = datetime.utcnow().isoformat()
                
            except Exception as e:
                logger.error(f"[LEARNING-TRIAGE] Error in triage loop: {e}", exc_info=True)
    
    async def _process_events(self):
        """Process buffered events and cluster them"""
        
        events_to_process = self.event_buffer.copy()
        self.event_buffer.clear()
        
        for event in events_to_process:
            await self._cluster_event(event)
    
    async def _cluster_event(self, event: Dict[str, Any]):
        """Cluster event by domain, severity, and pattern"""
        
        # Extract clustering dimensions
        domain = self._extract_domain(event)
        severity = self._extract_severity(event)
        pattern_type = self._extract_pattern(event)
        
        # Create cluster key
        cluster_key = f"{domain}:{severity}:{pattern_type}"
        
        # Get or create cluster
        if cluster_key not in self.clusters:
            self.clusters[cluster_key] = EventCluster(
                domain=domain,
                severity=severity,
                pattern_type=pattern_type
            )
            self.stats['clusters_created'] += 1
            logger.info(f"[LEARNING-TRIAGE] New cluster: {cluster_key}")
        
        # Add event to cluster
        cluster = self.clusters[cluster_key]
        cluster.event_count += 1
        cluster.last_seen = datetime.utcnow()
        cluster.events.append(event)
        
        # Keep only last 100 events per cluster
        if len(cluster.events) > 100:
            cluster.events = cluster.events[-100:]
    
    def _extract_domain(self, event: Dict[str, Any]) -> str:
        """Extract domain from event"""
        event_type = event.get('event_type', '')
        
        if 'mission' in event_type or 'guardian' in event_type:
            return 'guardian'
        elif 'htm' in event_type:
            return 'htm'
        elif 'rag' in event_type:
            return 'rag'
        elif 'remote_access' in event_type or 'firefox' in event_type or 'github' in event_type:
            return 'remote_access'
        elif 'agent' in event_type or 'coding' in event_type or 'healing' in event_type:
            return 'agent'
        elif 'kernel' in event_type or 'service' in event_type:
            return 'system'
        else:
            return 'unknown'
    
    def _extract_severity(self, event: Dict[str, Any]) -> str:
        """Extract severity from event"""
        
        # Check explicit severity
        if 'severity' in event:
            return event['severity']
        
        # Infer from event type
        event_type = event.get('event_type', '')
        
        if 'critical' in event_type or 'failed' in event_type:
            return 'high'
        elif 'error' in event_type:
            return 'medium'
        elif 'warning' in event_type or 'degraded' in event_type:
            return 'medium'
        elif 'anomaly' in event_type:
            return 'medium'
        else:
            return 'low'
    
    def _extract_pattern(self, event: Dict[str, Any]) -> str:
        """Extract pattern type from event"""
        event_type = event.get('event_type', '')
        
        if 'error' in event_type or 'failed' in event_type:
            return 'error'
        elif 'anomaly' in event_type:
            return 'anomaly'
        elif 'degraded' in event_type or 'degradation' in event_type:
            return 'degradation'
        elif 'blocked' in event_type:
            return 'blocked'
        else:
            return 'general'
    
    async def _check_phase_transition(self):
        """Check if we should transition from boot to steady state"""
        
        if not self.boot_phase:
            return  # Already in steady state
        
        # Check Guardian boot status
        if self.guardian and hasattr(self.guardian, 'boot_complete'):
            if self.guardian.boot_complete:
                await self._transition_to_steady_state()
                return
        
        # Fallback: Check message bus for boot complete
        # (This would have been set by _handle_boot_complete)
        if self.boot_complete_time:
            await self._transition_to_steady_state()
    
    async def _handle_boot_complete(self, event: Dict[str, Any]):
        """Handle boot completion event"""
        self.boot_complete_time = datetime.utcnow()
        logger.info("[LEARNING-TRIAGE] Received boot completion signal")
    
    async def _transition_to_steady_state(self):
        """Transition from boot phase to steady state"""
        
        self.boot_phase = False
        self.current_interval = self.steady_interval
        self.stats['boot_phase'] = False
        
        logger.info("=" * 80)
        logger.info("[LEARNING-TRIAGE] ⚡ TRANSITION TO STEADY STATE")
        logger.info(f"[LEARNING-TRIAGE] Boot phase complete after {self.stats['triage_count']} triage cycles")
        logger.info(f"[LEARNING-TRIAGE] New interval: {self.steady_interval}s (3-5 min variable)")
        logger.info(f"[LEARNING-TRIAGE] Priority threshold: {self.steady_priority_threshold} (lower bar)")
        logger.info("=" * 80)
        
        # Log to immutable log
        if self.immutable_log:
            await self.immutable_log.append_entry(
                category='learning_triage',
                subcategory='phase_transition',
                data={
                    'from': 'boot',
                    'to': 'steady_state',
                    'boot_triages': self.stats['triage_count'],
                    'new_interval': self.steady_interval
                },
                actor='learning_triage_agent',
                action='phase_transition',
                resource='automation_cadence'
            )
    
    async def _analyze_clusters(self):
        """Analyze clusters to identify learning opportunities (phase-aware)"""
        
        now = datetime.utcnow()
        
        # Determine priority threshold based on phase
        threshold = self.boot_priority_threshold if self.boot_phase else self.steady_priority_threshold
        
        for cluster_key, cluster in list(self.clusters.items()):
            # Clean up old resolved clusters
            if cluster.resolved and (now - cluster.last_seen) > timedelta(hours=24):
                del self.clusters[cluster_key]
                continue
            
            # Calculate scores
            urgency = cluster.urgency_score()
            recurrence = cluster.recurrence_score()
            
            # During boot phase, only process critical infrastructure issues
            if self.boot_phase:
                # Check if cluster is infrastructure-related
                is_infrastructure = cluster.domain in ['guardian', 'system', 'kernel']
                
                if not is_infrastructure:
                    continue  # Skip non-infrastructure during boot
            
            if urgency >= threshold or recurrence >= 0.8:
                phase_label = "BOOT-CRITICAL" if self.boot_phase else "STEADY"
                logger.info(
                    f"[LEARNING-TRIAGE] [{phase_label}] High-priority cluster: {cluster_key} "
                    f"(urgency={urgency:.2f}, recurrence={recurrence:.2f}, "
                    f"events={cluster.event_count})"
                )
    
    async def _launch_missions(self):
        """Launch learning missions for clusters that need them"""
        
        if not self.mission_launcher:
            return
        
        for cluster_key, cluster in self.clusters.items():
            if cluster.should_launch_mission():
                await self._launch_mission_for_cluster(cluster_key, cluster)
    
    async def _launch_mission_for_cluster(self, cluster_key: str, cluster: EventCluster):
        """Launch a learning mission for a specific cluster"""
        
        logger.info(f"[LEARNING-TRIAGE] 🚀 Launching learning mission for: {cluster_key}")
        
        # Prepare mission context
        mission_context = {
            'cluster_key': cluster_key,
            'domain': cluster.domain,
            'severity': cluster.severity,
            'pattern_type': cluster.pattern_type,
            'event_count': cluster.event_count,
            'urgency_score': cluster.urgency_score(),
            'recurrence_score': cluster.recurrence_score(),
            'sample_events': cluster.events[-5:],  # Last 5 events
            'first_seen': cluster.first_seen.isoformat(),
            'last_seen': cluster.last_seen.isoformat()
        }
        
        # Generate mission description
        mission_description = self._generate_mission_description(cluster)
        
        # Launch mission
        try:
            mission_id = await self.mission_launcher.launch_mission(
                mission_type='autonomous_learning',
                description=mission_description,
                context=mission_context,
                priority=cluster.urgency_score(),
                launched_by='learning_triage_agent'
            )
            
            cluster.learning_mission_id = mission_id
            self.stats['missions_launched'] += 1
            
            logger.info(f"[LEARNING-TRIAGE] ✅ Mission launched: {mission_id}")
            
            # Log to immutable log
            if self.immutable_log:
                await self.immutable_log.append_entry(
                    category='learning_triage',
                    subcategory='mission_launched',
                    data={
                        'mission_id': mission_id,
                        'cluster_key': cluster_key,
                        'context': mission_context
                    },
                    actor='learning_triage_agent',
                    action='launch_mission',
                    resource=cluster_key
                )
        
        except Exception as e:
            logger.error(f"[LEARNING-TRIAGE] Failed to launch mission: {e}", exc_info=True)
    
    def _generate_mission_description(self, cluster: EventCluster) -> str:
        """Generate human-readable mission description"""
        
        return (
            f"Learn to resolve {cluster.pattern_type} in {cluster.domain} domain. "
            f"Observed {cluster.event_count} occurrences with {cluster.severity} severity. "
            f"Urgency: {cluster.urgency_score():.0%}, Recurrence: {cluster.recurrence_score():.0%}."
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get triage statistics"""
        
        active_clusters = [c for c in self.clusters.values() if not c.resolved]
        
        return {
            **self.stats,
            'running': self.running,
            'subscriptions': len(self.subscriptions),
            'active_clusters': len(active_clusters),
            'total_clusters': len(self.clusters),
            'events_buffered': len(self.event_buffer)
        }
    
    def get_clusters(self, include_resolved: bool = False) -> List[Dict[str, Any]]:
        """Get cluster information"""
        
        clusters = []
        
        for cluster_key, cluster in self.clusters.items():
            if not include_resolved and cluster.resolved:
                continue
            
            clusters.append({
                'cluster_key': cluster_key,
                'domain': cluster.domain,
                'severity': cluster.severity,
                'pattern_type': cluster.pattern_type,
                'event_count': cluster.event_count,
                'urgency_score': cluster.urgency_score(),
                'recurrence_score': cluster.recurrence_score(),
                'first_seen': cluster.first_seen.isoformat(),
                'last_seen': cluster.last_seen.isoformat(),
                'learning_mission_id': cluster.learning_mission_id,
                'resolved': cluster.resolved
            })
        
        # Sort by urgency
        clusters.sort(key=lambda c: c['urgency_score'], reverse=True)
        
        return clusters


# Global instance
learning_triage_agent = LearningTriageAgent()
