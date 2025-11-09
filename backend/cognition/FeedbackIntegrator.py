"""Feedback Integrator - Deterministic Write Path

Orchestrates the feedback loop: Governance -> Trust -> Memory -> Events
All specialist outputs flow through this single integration point.
"""

import uuid
from typing import Optional, Dict, Any
from datetime import datetime

from .GraceLoopOutput import GraceLoopOutput
from .GovernancePrimeDirective import governance_prime_directive
from .models import GovernanceDecision
from .events import (
    FeedbackRecorded, ConstitutionalViolation,
    TrustScoreUpdated, GovernanceEscalation
)

# Lazy imports to avoid circular dependencies
trigger_mesh = None
ImmutableLog = None

def _lazy_init():
    """Initialize dependencies lazily"""
    global trigger_mesh, ImmutableLog
    
    if trigger_mesh is None:
        try:
            from backend.trigger_mesh import trigger_mesh as tm, TriggerEvent
            from backend.immutable_log import ImmutableLog as IL
            
            trigger_mesh = tm
            ImmutableLog = IL
        except ImportError:
            # Standalone mode
            pass

class FeedbackIntegrator:
    """
    Deterministic write path for all GraceLoopOutput
    
    Flow:
    1. Receive GraceLoopOutput
    2. Constitutional validation (GovernancePrimeDirective)
    3. Trust scoring (MemoryScoreModel simulation)
    4. Memory storage (LoopMemoryBank)
    5. Event emission (trigger_mesh)
    """
    
    def __init__(self):
        # Initialize lazily
        _lazy_init()
        self.audit = ImmutableLog() if ImmutableLog else None
        self._retry_max = 3
        
    async def integrate(
        self,
        output: GraceLoopOutput
    ) -> Optional[str]:
        """
        Integrate output through governance -> trust -> memory pipeline
        
        Args:
            output: GraceLoopOutput to integrate
            
        Returns:
            Memory reference if stored, None if blocked
        """
        
        integration_id = str(uuid.uuid4())
        
        try:
            # STEP 1: Constitutional Validation
            verdict = await governance_prime_directive.validate_against_constitution(output)
            
            # Emit constitutional violation if blocked
            if verdict.decision == GovernanceDecision.BLOCK:
                await self._emit_constitutional_violation(output, verdict)
                await self.audit.append(
                    actor=output.component,
                    action="feedback_blocked",
                    resource=output.loop_id,
                    subsystem="feedback_integrator",
                    payload={
                        'integration_id': integration_id,
                        'reason': verdict.reason,
                        'compliance_score': verdict.compliance_score
                    },
                    result="blocked"
                )
                return None
            
            # Emit escalation event if needed
            if verdict.needs_escalation():
                await self._emit_escalation(output, verdict)
            
            # STEP 2: Compute Trust Score
            trust_score = await self._compute_trust_score(output, verdict)
            
            # Emit trust score event
            await self._emit_trust_score(output, trust_score)
            
            # STEP 3: Store in Memory (if approved)
            memory_ref = None
            if verdict.is_approved() and verdict.safe_to_store:
                memory_ref = await self._store_in_memory(output, trust_score, verdict)
            
            # STEP 4: Emit Feedback Recorded Event
            if memory_ref:
                await self._emit_feedback_recorded(
                    output, memory_ref, trust_score, verdict
                )
            
            # Audit successful integration
            await self.audit.append(
                actor=output.component,
                action="feedback_integrated",
                resource=output.loop_id,
                subsystem="feedback_integrator",
                payload={
                    'integration_id': integration_id,
                    'memory_ref': memory_ref,
                    'trust_score': trust_score,
                    'compliance_score': verdict.compliance_score,
                    'decision': verdict.decision.value
                },
                result="success"
            )
            
            return memory_ref
            
        except Exception as e:
            # Log error and retry
            await self.audit.append(
                actor=output.component,
                action="feedback_integration_error",
                resource=output.loop_id,
                subsystem="feedback_integrator",
                payload={
                    'integration_id': integration_id,
                    'error': str(e)
                },
                result="error"
            )
            
            # Could implement retry logic here
            return None
    
    async def _compute_trust_score(
        self,
        output: GraceLoopOutput,
        verdict
    ) -> float:
        """
        Compute trust score for output
        
        Simulates MemoryScoreModel scoring logic:
        - Base score from confidence
        - Adjusted by constitutional compliance
        - Penalized for errors/warnings
        - Boosted by evidence quality
        """
        
        # Base score from confidence
        base_score = output.confidence
        
        # Constitutional compliance factor
        compliance_factor = verdict.compliance_score
        
        # Evidence quality (based on citations)
        evidence_quality = 0.0
        if output.citations:
            citation_scores = [c.confidence for c in output.citations]
            evidence_quality = sum(citation_scores) / len(citation_scores)
        
        # Error penalty
        error_penalty = 0.0
        if output.errors:
            error_penalty = min(len(output.errors) * 0.1, 0.3)  # Max 30% penalty
        
        # Warning penalty
        warning_penalty = 0.0
        if output.warnings:
            warning_penalty = min(len(output.warnings) * 0.05, 0.15)  # Max 15% penalty
        
        # Compute final trust score
        trust_score = (
            base_score * 0.4 +  # 40% from confidence
            compliance_factor * 0.3 +  # 30% from compliance
            evidence_quality * 0.2 +  # 20% from evidence
            output.quality_score * 0.1 if output.quality_score else 0  # 10% from quality
        )
        
        # Apply penalties
        trust_score = max(0.0, trust_score - error_penalty - warning_penalty)
        
        # Degraded trust if verdict says so
        if verdict.decision == GovernanceDecision.DEGRADE:
            trust_score *= 0.8  # 20% trust reduction
        
        return min(1.0, max(0.0, trust_score))
    
    async def _store_in_memory(
        self,
        output: GraceLoopOutput,
        trust_score: float,
        verdict
    ) -> str:
        """
        Store output in LoopMemoryBank
        
        Returns memory reference
        """
        
        # TODO(FUTURE): Integrate with actual LoopMemoryBank when implemented
        # For now, simulate memory storage
        
        memory_ref = f"mem_{output.loop_id}_{str(uuid.uuid4())[:8]}"
        
        # Simulate storage
        await self.audit.append(
            actor=output.component,
            action="memory_stored",
            resource=memory_ref,
            subsystem="feedback_integrator",
            payload={
                'loop_id': output.loop_id,
                'component': output.component,
                'trust_score': trust_score,
                'importance': output.importance,
                'compliance_score': verdict.compliance_score
            },
            result="stored"
        )
        
        return memory_ref
    
    async def _emit_feedback_recorded(
        self,
        output: GraceLoopOutput,
        memory_ref: str,
        trust_score: float,
        verdict
    ):
        """Emit FeedbackRecorded event to trigger_mesh"""
        
        event = FeedbackRecorded(
            loop_id=output.loop_id,
            component=output.component,
            memory_ref=memory_ref,
            trust_score=trust_score,
            compliance_score=verdict.compliance_score,
            timestamp=datetime.utcnow(),
            metadata={
                'decision': verdict.decision.value,
                'tags': verdict.tags,
                'importance': output.importance
            }
        )
        
        await trigger_mesh.publish(TriggerEvent(
            event_type="cognition.feedback_recorded",
            source="feedback_integrator",
            actor=output.component,
            resource=memory_ref,
            payload=event.to_event_payload(),
            timestamp=datetime.utcnow()
        ))
    
    async def _emit_constitutional_violation(
        self,
        output: GraceLoopOutput,
        verdict
    ):
        """Emit ConstitutionalViolation event"""
        
        event = ConstitutionalViolation(
            loop_id=output.loop_id,
            component=output.component,
            violation_type="constitutional_block",
            principle_ids=verdict.constitutional_checks,
            severity=verdict.severity,
            reason=verdict.reason,
            timestamp=datetime.utcnow(),
            action_blocked=True
        )
        
        await trigger_mesh.publish(TriggerEvent(
            event_type="governance.constitutional_violation",
            source="feedback_integrator",
            actor=output.component,
            resource=output.loop_id,
            payload=event.to_event_payload(),
            timestamp=datetime.utcnow()
        ))
    
    async def _emit_trust_score(
        self,
        output: GraceLoopOutput,
        trust_score: float
    ):
        """Emit TrustScoreUpdated event"""
        
        evidence_quality = 0.0
        if output.citations:
            evidence_quality = sum(c.confidence for c in output.citations) / len(output.citations)
        
        event = TrustScoreUpdated(
            loop_id=output.loop_id,
            component=output.component,
            trust_score=trust_score,
            confidence=output.confidence,
            evidence_quality=evidence_quality,
            timestamp=datetime.utcnow()
        )
        
        await trigger_mesh.publish(TriggerEvent(
            event_type="cognition.trust_score_updated",
            source="feedback_integrator",
            actor=output.component,
            resource=output.loop_id,
            payload=event.to_event_payload(),
            timestamp=datetime.utcnow()
        ))
    
    async def _emit_escalation(
        self,
        output: GraceLoopOutput,
        verdict
    ):
        """Emit GovernanceEscalation event"""
        
        event = GovernanceEscalation(
            loop_id=output.loop_id,
            component=output.component,
            escalation_reason=verdict.reason,
            verdict=verdict.to_dict(),
            timestamp=datetime.utcnow()
        )
        
        await trigger_mesh.publish(TriggerEvent(
            event_type="governance.escalation_required",
            source="feedback_integrator",
            actor=output.component,
            resource=output.loop_id,
            payload=event.to_event_payload(),
            timestamp=datetime.utcnow()
        ))
    
    async def on_feedback_ack(
        self,
        memory_ref: str,
        metrics: Dict[str, Any]
    ):
        """
        Post-write hook after feedback is acknowledged
        
        Args:
            memory_ref: Reference to stored memory
            metrics: Performance metrics from storage
        """
        
        # Log acknowledgment
        await self.audit.append(
            actor="system",
            action="feedback_acknowledged",
            resource=memory_ref,
            subsystem="feedback_integrator",
            payload=metrics,
            result="acknowledged"
        )
        
        # Could trigger additional processing here
        # - Update learning statistics
        # - Trigger meta-analysis
        # - Update trust calibration

# Singleton instance
feedback_integrator = FeedbackIntegrator()
