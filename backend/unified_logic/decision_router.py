"""
Decision Router - Phase 3
Routes unified decisions to autonomous loop, UI, and learning engine with event emission
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from .unified_decision_engine import UnifiedDecision, DecisionAction


class DecisionRouter:
    """
    Phase 3: Route unified decisions to all consumers
    
    Routes to:
    1. Autonomous run loop - for execution
    2. UI - for transparency
    3. Learning engine - for feedback
    4. Immutable log - for audit
    5. Trigger mesh - for event propagation
    """
    
    def __init__(self):
        self.routed_decisions = 0
        self.routing_failures = 0
        
        # Consumer handlers (registered at runtime)
        self.autonomous_loop_handler: Optional[callable] = None
        self.ui_handler: Optional[callable] = None
        self.learning_handler: Optional[callable] = None
    
    async def route(self, decision: UnifiedDecision):
        """
        Phase 3: Route unified decision to all consumers
        
        Args:
            decision: UnifiedDecision to route
        """
        
        # Emit UNIFIED_DECISION_READY event
        await self._emit_decision_event(decision)
        
        # Route to consumers in parallel
        await asyncio.gather(
            self._route_to_autonomous_loop(decision),
            self._route_to_ui(decision),
            self._route_to_learning(decision),
            self._route_to_immutable_log(decision),
            return_exceptions=True
        )
        
        self.routed_decisions += 1
    
    async def _emit_decision_event(self, decision: UnifiedDecision):
        """Emit UNIFIED_DECISION_READY event to trigger mesh"""
        
        try:
            from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent
            
            event = TriggerEvent(
                event_type="unified.decision_ready",
                source="unified_decision_engine",
                actor="unified_logic",
                resource=decision.decision_id,
                payload={
                    'decision_id': decision.decision_id,
                    'action': decision.action.value,
                    'confidence': decision.confidence,
                    'trust_score': decision.trust_score,
                    'primary_reasoning': decision.primary_reasoning,
                    'warnings': decision.warnings,
                    'recommended_next_loops': decision.recommended_next_loops
                },
                trust_score=decision.trust_score
            )
            
            await trigger_mesh.emit(event)
            
        except Exception as e:
            print(f"✗ Failed to emit decision event: {e}")
    
    async def _route_to_autonomous_loop(self, decision: UnifiedDecision):
        """Route to autonomous run loop for execution"""
        
        if decision.action != DecisionAction.EXECUTE:
            # Only route executable decisions to autonomous loop
            return
        
        try:
            if self.autonomous_loop_handler:
                await self.autonomous_loop_handler(decision)
            else:
                # Fallback: publish to event bus
                from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent
                
                event = TriggerEvent(
                    event_type="autonomous.execute_decision",
                    source="unified_decision_engine",
                    actor="unified_logic",
                    resource=decision.decision_id,
                    payload={
                        'decision_id': decision.decision_id,
                        'action': decision.action.value,
                        'confidence': decision.confidence,
                        'reasoning': decision.primary_reasoning
                    }
                )
                
                await trigger_mesh.emit(event)
        
        except Exception as e:
            print(f"✗ Failed to route to autonomous loop: {e}")
            self.routing_failures += 1
    
    async def _route_to_ui(self, decision: UnifiedDecision):
        """Route to UI for transparency"""
        
        try:
            if self.ui_handler:
                await self.ui_handler(decision)
            else:
                # Fallback: publish UI update event
                from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent
                
                event = TriggerEvent(
                    event_type="ui.decision_update",
                    source="unified_decision_engine",
                    actor="unified_logic",
                    resource=f"ui:decision_panel",
                    payload={
                        'decision_id': decision.decision_id,
                        'action': decision.action.value,
                        'confidence': decision.confidence,
                        'trust_score': decision.trust_score,
                        'reasoning': decision.primary_reasoning,
                        'warnings': decision.warnings,
                        'contradictions': decision.contradictions,
                        'timestamp': decision.timestamp.isoformat()
                    }
                )
                
                await trigger_mesh.emit(event)
        
        except Exception as e:
            print(f"✗ Failed to route to UI: {e}")
            self.routing_failures += 1
    
    async def _route_to_learning(self, decision: UnifiedDecision):
        """Route to learning engine for feedback"""
        
        try:
            if self.learning_handler:
                await self.learning_handler(decision)
            else:
                # Fallback: publish learning feedback event
                from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent
                
                event = TriggerEvent(
                    event_type="learning.decision_feedback",
                    source="unified_decision_engine",
                    actor="unified_logic",
                    resource=decision.decision_id,
                    payload={
                        'decision_id': decision.decision_id,
                        'action': decision.action.value,
                        'confidence': decision.confidence,
                        'quality_score': decision.quality_score,
                        'reasoning_chain': decision.reasoning_chain_ids,
                        'component_weights': {
                            'governance': decision.governance_weight,
                            'avn': decision.avn_weight,
                            'mldl': decision.mldl_weight,
                            'learning': decision.learning_weight,
                            'memory': decision.memory_weight
                        },
                        'contradictions': decision.contradictions
                    }
                )
                
                await trigger_mesh.emit(event)
        
        except Exception as e:
            print(f"✗ Failed to route to learning: {e}")
            self.routing_failures += 1
    
    async def _route_to_immutable_log(self, decision: UnifiedDecision):
        """Route to immutable log for audit trail"""
        
        try:
            from backend.logging.immutable_log import immutable_log
            
            await immutable_log.append(
                actor="unified_decision_engine",
                action=f"UNIFIED_DECISION:{decision.action.value.upper()}",
                resource=decision.decision_id,
                subsystem="unified_logic",
                payload={
                    'decision_id': decision.decision_id,
                    'action': decision.action.value,
                    'confidence': decision.confidence,
                    'trust_score': decision.trust_score,
                    'quality_score': decision.quality_score,
                    'primary_reasoning': decision.primary_reasoning,
                    'warnings_count': len(decision.warnings),
                    'contradictions_count': len(decision.contradictions),
                    'recommended_loops': decision.recommended_next_loops,
                    'component_weights': {
                        'governance': decision.governance_weight,
                        'avn': decision.avn_weight,
                        'mldl': decision.mldl_weight,
                        'learning': decision.learning_weight,
                        'memory': decision.memory_weight
                    }
                },
                result=decision.action.value
            )
        
        except Exception as e:
            print(f"✗ Failed to log decision: {e}")
            self.routing_failures += 1
    
    def register_autonomous_handler(self, handler: callable):
        """Register handler for autonomous loop"""
        self.autonomous_loop_handler = handler
        print("✓ Autonomous loop handler registered")
    
    def register_ui_handler(self, handler: callable):
        """Register handler for UI updates"""
        self.ui_handler = handler
        print("✓ UI handler registered")
    
    def register_learning_handler(self, handler: callable):
        """Register handler for learning feedback"""
        self.learning_handler = handler
        print("✓ Learning handler registered")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        return {
            'routed_decisions': self.routed_decisions,
            'routing_failures': self.routing_failures,
            'handlers_registered': {
                'autonomous': self.autonomous_loop_handler is not None,
                'ui': self.ui_handler is not None,
                'learning': self.learning_handler is not None
            }
        }


# Global router instance
decision_router = DecisionRouter()
