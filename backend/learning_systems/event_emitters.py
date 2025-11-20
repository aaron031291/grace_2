"""
Event Emitters for Learning Triage System

Helper functions to emit structured events from various Grace components
to the learning triage agent via message bus
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EventEmitter:
    """Base event emitter"""
    
    def __init__(self):
        self.message_bus = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize message bus connection"""
        if self._initialized:
            return
        
        try:
            from backend.core.message_bus import message_bus
            self.message_bus = message_bus
            self._initialized = True
        except ImportError:
            logger.warning("[EVENT-EMITTER] Message bus not available")
    
    async def emit(self, event_type: str, data: Dict[str, Any], severity: str = 'medium'):
        """Emit an event"""
        if not self._initialized:
            await self.initialize()
        
        if not self.message_bus:
            return
        
        event = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'severity': severity,
            **data
        }
        
        await self.message_bus.publish(event_type, event)


class GuardianEventEmitter(EventEmitter):
    """Emit Guardian-related events"""
    
    async def emit_mission_created(self, mission_id: str, mission_type: str, description: str):
        """Emit mission created event"""
        await self.emit('mission.created', {
            'mission_id': mission_id,
            'mission_type': mission_type,
            'description': description
        }, severity='medium')
    
    async def emit_mission_resolved(self, mission_id: str, resolution: str):
        """Emit mission resolved event"""
        await self.emit('mission.resolved', {
            'mission_id': mission_id,
            'resolution': resolution
        }, severity='low')
    
    async def emit_mission_failed(self, mission_id: str, error: str):
        """Emit mission failed event"""
        await self.emit('mission.failed', {
            'mission_id': mission_id,
            'error': error
        }, severity='high')
    
    async def emit_guardian_error(self, error_type: str, details: str):
        """Emit Guardian error"""
        await self.emit('guardian.error', {
            'error_type': error_type,
            'details': details
        }, severity='high')
    
    async def emit_guardian_warning(self, warning_type: str, details: str):
        """Emit Guardian warning"""
        await self.emit('guardian.warning', {
            'warning_type': warning_type,
            'details': details
        }, severity='medium')


class HTMEventEmitter(EventEmitter):
    """Emit HTM anomaly detection events"""
    
    async def emit_anomaly_detected(
        self,
        detector_id: str,
        metric_name: str,
        anomaly_score: float,
        value: float
    ):
        """Emit HTM anomaly detected"""
        severity = 'critical' if anomaly_score > 0.9 else 'high' if anomaly_score > 0.7 else 'medium'
        
        await self.emit('htm.anomaly.detected', {
            'detector_id': detector_id,
            'metric_name': metric_name,
            'anomaly_score': anomaly_score,
            'value': value
        }, severity=severity)
    
    async def emit_pattern_unusual(self, pattern_type: str, details: str):
        """Emit unusual pattern detected"""
        await self.emit('htm.pattern.unusual', {
            'pattern_type': pattern_type,
            'details': details
        }, severity='medium')
    
    async def emit_degradation(self, component: str, metric: str, threshold: float, actual: float):
        """Emit performance degradation"""
        await self.emit('htm.degradation', {
            'component': component,
            'metric': metric,
            'threshold': threshold,
            'actual': actual
        }, severity='medium')


class RAGEventEmitter(EventEmitter):
    """Emit RAG system events"""
    
    async def emit_health_degraded(self, subsystem: str, health_score: float):
        """Emit RAG health degraded"""
        severity = 'high' if health_score < 0.5 else 'medium'
        
        await self.emit('rag.health.degraded', {
            'subsystem': subsystem,
            'health_score': health_score
        }, severity=severity)
    
    async def emit_retrieval_failed(self, query: str, error: str):
        """Emit retrieval failure"""
        await self.emit('rag.retrieval.failed', {
            'query': query,
            'error': error
        }, severity='medium')
    
    async def emit_confidence_low(self, query: str, confidence: float, threshold: float):
        """Emit low confidence warning"""
        await self.emit('rag.confidence.low', {
            'query': query,
            'confidence': confidence,
            'threshold': threshold
        }, severity='medium')


class RemoteAccessEventEmitter(EventEmitter):
    """Emit remote access events"""
    
    async def emit_action_failed(self, action: str, error: str):
        """Emit remote action failed"""
        await self.emit('remote_access.action.failed', {
            'action': action,
            'error': error
        }, severity='medium')
    
    async def emit_governance_blocked(self, action: str, reason: str):
        """Emit governance block"""
        await self.emit('remote_access.governance.blocked', {
            'action': action,
            'reason': reason
        }, severity='low')
    
    async def emit_firefox_browse_failed(self, url: str, error: str):
        """Emit Firefox browse failure"""
        await self.emit('firefox.browse.failed', {
            'url': url,
            'error': error
        }, severity='medium')
    
    async def emit_github_rate_limit(self, remaining: int, reset_time: str):
        """Emit GitHub rate limit warning"""
        severity = 'high' if remaining < 10 else 'medium' if remaining < 100 else 'low'
        
        await self.emit('github.rate_limit', {
            'remaining': remaining,
            'reset_time': reset_time
        }, severity=severity)


class AgentEventEmitter(EventEmitter):
    """Emit autonomous agent events"""
    
    async def emit_task_failed(self, agent: str, task: str, error: str):
        """Emit agent task failure"""
        await self.emit('agent.task.failed', {
            'agent': agent,
            'task': task,
            'error': error
        }, severity='medium')
    
    async def emit_agent_error(self, agent: str, error_type: str, details: str):
        """Emit agent error"""
        await self.emit('agent.error', {
            'agent': agent,
            'error_type': error_type,
            'details': details
        }, severity='high')
    
    async def emit_coding_build_failed(self, project: str, errors: int):
        """Emit coding agent build failure"""
        severity = 'high' if errors > 10 else 'medium'
        
        await self.emit('coding_agent.build.failed', {
            'project': project,
            'errors': errors
        }, severity=severity)
    
    async def emit_healing_remediation_failed(self, issue: str, playbook: str, error: str):
        """Emit self-healing remediation failure"""
        await self.emit('self_healing.remediation.failed', {
            'issue': issue,
            'playbook': playbook,
            'error': error
        }, severity='high')


class SystemEventEmitter(EventEmitter):
    """Emit system-level events"""
    
    async def emit_kernel_boot_failed(self, kernel: str, error: str):
        """Emit kernel boot failure"""
        await self.emit('kernel.boot.failed', {
            'kernel': kernel,
            'error': error
        }, severity='critical')
    
    async def emit_service_degraded(self, service: str, health_score: float):
        """Emit service degradation"""
        severity = 'high' if health_score < 0.5 else 'medium'
        
        await self.emit('service.degraded', {
            'service': service,
            'health_score': health_score
        }, severity=severity)
    
    async def emit_unhandled_error(self, component: str, error: str, traceback: str):
        """Emit unhandled error"""
        await self.emit('error.unhandled', {
            'component': component,
            'error': error,
            'traceback': traceback
        }, severity='high')


# Global emitter instances
guardian_events = GuardianEventEmitter()
htm_events = HTMEventEmitter()
rag_events = RAGEventEmitter()
remote_access_events = RemoteAccessEventEmitter()
agent_events = AgentEventEmitter()
system_events = SystemEventEmitter()


# Convenience function to emit from anywhere
async def emit_learning_event(
    event_type: str,
    data: Dict[str, Any],
    severity: str = 'medium'
):
    """
    Emit a learning event from anywhere in Grace
    
    Usage:
        from backend.learning_systems.event_emitters import emit_learning_event
        
        await emit_learning_event(
            'custom.event.type',
            {'key': 'value'},
            severity='high'
        )
    """
    emitter = EventEmitter()
    await emitter.emit(event_type, data, severity)
