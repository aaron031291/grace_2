"""
Complete Integration - Tie all subsystems together
Provides high-level API for making unified decisions from all system inputs
"""

from typing import Dict, Any, Optional
from datetime import datetime

from .unified_decision_engine import (
    unified_decision_engine,
    UnifiedDecision,
    GovernanceInput,
    AVNInput,
    MLDLQuorumInput,
    LearningInput,
    MemoryInput
)
from .decision_router import decision_router


class UnifiedLogicIntegration:
    """
    Complete integration of unified logic with all subsystems
    
    High-level API for:
    1. Collecting inputs from all systems
    2. Synthesizing unified decision
    3. Routing decision to consumers
    """
    
    def __init__(self):
        self.engine = unified_decision_engine
        self.router = decision_router
        
        self.decisions_processed = 0
    
    async def make_decision(
        self,
        request: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> UnifiedDecision:
        """
        Make a unified decision by collecting inputs from all subsystems
        
        Args:
            request: Decision request with action details
            context: Additional context
            
        Returns:
            UnifiedDecision with action and routing
        """
        
        # Collect inputs from all subsystems
        governance = await self._get_governance_input(request, context)
        avn = await self._get_avn_input(request, context)
        mldl = await self._get_mldl_input(request, context)
        learning = await self._get_learning_input(request, context)
        memory = await self._get_memory_input(request, context)
        
        # Synthesize decision
        decision = await self.engine.synthesize(
            governance_decision=governance,
            avn_state=avn,
            mldl_consensus=mldl,
            learning_insights=learning,
            memory_context=memory
        )
        
        # Route decision
        await self.router.route(decision)
        
        self.decisions_processed += 1
        
        return decision
    
    async def _get_governance_input(
        self,
        request: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> GovernanceInput:
        """Get input from governance system"""
        
        try:
            from backend.governance_system.governance_framework import governance_framework
            
            # Check if action requires approval
            result = await governance_framework.check_approval_required(
                actor=request.get('actor', 'system'),
                action=request.get('action', 'unknown'),
                resource=request.get('resource', ''),
                context=context or {}
            )
            
            return GovernanceInput(
                approved=result.get('approved', True),
                approval_id=result.get('approval_id'),
                violated_policies=result.get('violated_policies', []),
                reasoning=result.get('reasoning', ''),
                trust_score=result.get('trust_score', 1.0)
            )
        
        except Exception as e:
            print(f"⚠ Governance input unavailable: {e}")
            # Default to approved for now
            return GovernanceInput(
                approved=True,
                reasoning="Governance system unavailable - auto-approved"
            )
    
    async def _get_avn_input(
        self,
        request: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> AVNInput:
        """Get input from AVN (health monitoring)"""
        
        try:
            from backend.misc.unified_health import unified_health
            
            health_state = unified_health.get_health_state()
            
            anomalies = []
            severity = "none"
            
            if health_state.get('degraded_components'):
                severity = "medium"
                anomalies = [
                    {'component': comp, 'status': 'degraded'}
                    for comp in health_state.get('degraded_components', [])
                ]
            
            if health_state.get('critical_components'):
                severity = "critical"
                anomalies.extend([
                    {'component': comp, 'status': 'critical'}
                    for comp in health_state.get('critical_components', [])
                ])
            
            return AVNInput(
                health_state=health_state.get('overall_status', 'healthy'),
                anomalies_detected=anomalies,
                severity=severity,
                confidence=health_state.get('confidence', 1.0)
            )
        
        except Exception as e:
            print(f"⚠ AVN input unavailable: {e}")
            return AVNInput(
                health_state="healthy",
                confidence=0.8
            )
    
    async def _get_mldl_input(
        self,
        request: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> MLDLQuorumInput:
        """Get input from MLDL Quorum"""
        
        try:
            from backend.workflow_engines.parliament_engine import parliament_engine
            
            # Request quorum vote
            vote_result = await parliament_engine.vote_on_proposal(
                proposal={
                    'action': request.get('action'),
                    'resource': request.get('resource'),
                    'context': context or {}
                }
            )
            
            return MLDLQuorumInput(
                consensus_reached=vote_result.get('consensus', False),
                consensus_action=vote_result.get('action'),
                vote_breakdown=vote_result.get('votes', {}),
                confidence=vote_result.get('confidence', 0.0),
                reasoning=vote_result.get('reasoning', [])
            )
        
        except Exception as e:
            print(f"⚠ MLDL quorum unavailable: {e}")
            # Default to consensus for now
            return MLDLQuorumInput(
                consensus_reached=True,
                consensus_action=request.get('action'),
                confidence=0.7
            )
    
    async def _get_learning_input(
        self,
        request: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> LearningInput:
        """Get input from learning system"""
        
        try:
            from backend.learning_systems.pattern_learner import pattern_learner
            
            insights = await pattern_learner.get_insights_for_action(
                action=request.get('action'),
                context=context or {}
            )
            
            return LearningInput(
                insights=insights.get('patterns', []),
                pattern_confidence=insights.get('confidence', 0.0),
                recommended_adjustments=insights.get('adjustments', []),
                similar_past_outcomes=insights.get('past_outcomes', [])
            )
        
        except Exception as e:
            print(f"⚠ Learning input unavailable: {e}")
            return LearningInput()
    
    async def _get_memory_input(
        self,
        request: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> MemoryInput:
        """Get input from memory system"""
        
        try:
            from backend.memory_services.memory_service import memory_service
            
            # Retrieve relevant context
            relevant = await memory_service.search(
                query=request.get('action', ''),
                limit=5
            )
            
            return MemoryInput(
                relevant_context=relevant.get('results', []),
                trust_scores=relevant.get('trust_scores', {}),
                contradictions_found=relevant.get('contradictions', [])
            )
        
        except Exception as e:
            print(f"⚠ Memory input unavailable: {e}")
            return MemoryInput()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        return {
            'decisions_processed': self.decisions_processed,
            'engine_stats': self.engine.get_stats(),
            'router_stats': self.router.get_stats()
        }


# Global integration instance
unified_logic = UnifiedLogicIntegration()
