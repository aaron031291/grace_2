"""
Intent Governance Router
Routes all Layer 3 intents through Unified Logic with autonomy tier checks

Integrates with Phase 1 Charter to enforce mission priorities
"""

from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AutonomyTier(Enum):
    """Autonomy tiers from Phase 1 Charter"""
    TIER_0_HUMAN_REQUIRED = 0  # Human must approve
    TIER_1_REVIEW_REQUIRED = 1  # Auto-execute but log for review
    TIER_2_AUTONOMOUS_LOW_RISK = 2  # Fully autonomous, low impact
    TIER_3_AUTONOMOUS_HIGH_IMPACT = 3  # Autonomous but high impact, extra logging
    TIER_4_EMERGENCY = 4  # Emergency override, log heavily


class IntentGovernanceRouter:
    """
    Routes Layer 3 intents through unified logic
    Enforces autonomy tiers and mission alignment
    """
    
    def __init__(self):
        # Autonomy tier mapping based on intent type
        self.autonomy_tiers = {
            # Low risk - fully autonomous
            'query_knowledge': AutonomyTier.TIER_2_AUTONOMOUS_LOW_RISK,
            'generate_summary': AutonomyTier.TIER_2_AUTONOMOUS_LOW_RISK,
            'schedule_task': AutonomyTier.TIER_2_AUTONOMOUS_LOW_RISK,
            
            # Medium risk - autonomous with logging
            'execute_sandbox': AutonomyTier.TIER_1_REVIEW_REQUIRED,
            'deploy_model': AutonomyTier.TIER_1_REVIEW_REQUIRED,
            'modify_config': AutonomyTier.TIER_1_REVIEW_REQUIRED,
            
            # High impact - autonomous but extra scrutiny
            'self_improve': AutonomyTier.TIER_3_AUTONOMOUS_HIGH_IMPACT,
            'extend_grace': AutonomyTier.TIER_3_AUTONOMOUS_HIGH_IMPACT,
            'optimize_system': AutonomyTier.TIER_3_AUTONOMOUS_HIGH_IMPACT,
            
            # Critical - human approval required
            'modify_governance': AutonomyTier.TIER_0_HUMAN_REQUIRED,
            'change_charter': AutonomyTier.TIER_0_HUMAN_REQUIRED,
            'grant_permissions': AutonomyTier.TIER_0_HUMAN_REQUIRED,
            
            # Emergency - override normal flow
            'emergency_recovery': AutonomyTier.TIER_4_EMERGENCY,
            'critical_incident': AutonomyTier.TIER_4_EMERGENCY
        }
        
        logger.info("[INTENT-GOVERNANCE] Router initialized")
    
    async def route_intent(
        self,
        intent_id: str,
        intent_type: str,
        actor: str,
        payload: Dict[str, Any],
        mission_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Route intent through unified logic with governance checks
        
        Returns:
            - approved: bool
            - autonomy_tier: int
            - requires_vote: bool
            - reasoning: List[str]
            - routed_to: str
        """
        
        logger.info(f"[INTENT-GOVERNANCE] Routing intent: {intent_type} from {actor}")
        
        # Determine autonomy tier
        tier = self.autonomy_tiers.get(intent_type, AutonomyTier.TIER_1_REVIEW_REQUIRED)
        
        # Build routing decision
        routing = {
            'intent_id': intent_id,
            'intent_type': intent_type,
            'actor': actor,
            'autonomy_tier': tier.value,
            'tier_name': tier.name,
            'approved': False,
            'requires_vote': False,
            'requires_human': False,
            'reasoning': [],
            'routed_to': None,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Apply tier-based routing
        if tier == AutonomyTier.TIER_0_HUMAN_REQUIRED:
            routing['requires_human'] = True
            routing['approved'] = False
            routing['reasoning'].append("Tier 0: Human approval required")
            routing['routed_to'] = 'human_review_queue'
        
        elif tier == AutonomyTier.TIER_1_REVIEW_REQUIRED:
            routing['approved'] = True
            routing['requires_vote'] = False
            routing['reasoning'].append("Tier 1: Auto-approved with review logging")
            routing['routed_to'] = 'unified_logic_hub'
            
            # Log for post-execution review
            await self._log_for_review(intent_id, intent_type, actor, payload)
        
        elif tier == AutonomyTier.TIER_2_AUTONOMOUS_LOW_RISK:
            routing['approved'] = True
            routing['requires_vote'] = False
            routing['reasoning'].append("Tier 2: Fully autonomous, low risk")
            routing['routed_to'] = 'direct_execution'
        
        elif tier == AutonomyTier.TIER_3_AUTONOMOUS_HIGH_IMPACT:
            routing['approved'] = True
            routing['requires_vote'] = True  # Submit to unified logic for voting
            routing['reasoning'].append("Tier 3: High impact, requires unified logic vote")
            routing['routed_to'] = 'unified_logic_hub'
        
        elif tier == AutonomyTier.TIER_4_EMERGENCY:
            routing['approved'] = True
            routing['requires_vote'] = False
            routing['reasoning'].append("Tier 4: Emergency override, heavy logging")
            routing['routed_to'] = 'emergency_handler'
            
            # Log emergency to all systems
            await self._log_emergency(intent_id, intent_type, actor, payload)
        
        # Submit to unified logic if needed
        if routing['routed_to'] == 'unified_logic_hub':
            await self._submit_to_unified_logic(routing, payload, mission_context)
        
        # Log routing decision with 5W1H
        await self._log_routing_decision(routing, mission_context)
        
        logger.info(f"[INTENT-GOVERNANCE] Routed to: {routing['routed_to']}, Approved: {routing['approved']}")
        
        return routing
    
    async def _submit_to_unified_logic(
        self,
        routing: Dict,
        payload: Dict,
        mission_context: Optional[Dict]
    ):
        """Submit intent to unified logic for governance decision"""
        
        try:
            from backend.logging.unified_logic_hub import unified_logic_hub
            
            # Map mission context to charter priorities
            mission_priority = self._get_mission_priority(routing['intent_type'], mission_context)
            
            # Submit proposal
            await unified_logic_hub.submit_proposal(
                proposal_id=routing['intent_id'],
                proposal_type=routing['intent_type'],
                actor=routing['actor'],
                target_component="intent_executor",
                payload=payload,
                requires_vote=routing['requires_vote'],
                mission_alignment=mission_priority
            )
            
            logger.info(f"[INTENT-GOVERNANCE] Submitted to unified logic: {routing['intent_id']}")
        
        except Exception as e:
            logger.error(f"[INTENT-GOVERNANCE] Unified logic submission failed: {e}")
    
    def _get_mission_priority(self, intent_type: str, mission_context: Optional[Dict]) -> float:
        """
        Calculate mission alignment priority from Phase 1 Charter
        
        Returns: 0.0 - 1.0 (alignment score)
        """
        
        # Charter priorities (from Phase 1):
        # 1. Unbreakable resilience
        # 2. Revenue generation
        # 3. Autonomous operation
        # 4. Continuous learning
        
        priority_map = {
            # Resilience-aligned (highest priority)
            'emergency_recovery': 1.0,
            'critical_incident': 1.0,
            'self_improve': 0.9,
            
            # Revenue-aligned
            'deploy_model': 0.8,
            'optimize_system': 0.8,
            
            # Autonomy-aligned
            'extend_grace': 0.7,
            'schedule_task': 0.7,
            
            # Learning-aligned
            'query_knowledge': 0.6,
            'generate_summary': 0.6,
            
            # Administrative (lower priority)
            'modify_config': 0.4,
            'grant_permissions': 0.3
        }
        
        base_priority = priority_map.get(intent_type, 0.5)
        
        # Adjust based on mission context
        if mission_context:
            if mission_context.get('revenue_impact'):
                base_priority += 0.1
            if mission_context.get('user_facing'):
                base_priority += 0.1
            if mission_context.get('emergency'):
                base_priority = 1.0
        
        return min(base_priority, 1.0)
    
    async def _log_routing_decision(self, routing: Dict, mission_context: Optional[Dict]):
        """Log routing decision with 5W1H narrative"""
        
        # Build narrative
        why_narrative = [
            f"Intent type: {routing['intent_type']}",
            f"Autonomy tier: {routing['tier_name']}",
            *routing['reasoning']
        ]
        
        if mission_context:
            mission_priority = self._get_mission_priority(routing['intent_type'], mission_context)
            why_narrative.append(f"Mission alignment: {mission_priority:.0%}")
        
        # Log with 5W1H
        narrative = {
            'who': 'intent_governance_router',
            'what': 'route_intent',
            'when': routing['timestamp'],
            'where': routing['routed_to'],
            'why': why_narrative,
            'how': f"tier_{routing['autonomy_tier']}_routing",
            'context': {
                'intent_id': routing['intent_id'],
                'actor': routing['actor'],
                'approved': routing['approved'],
                'mission_context': mission_context
            }
        }
        
        self.narrative_log.append(narrative)
        
        logger.info(f"[INTENT-GOVERNANCE] Routing decision logged")
    
    async def _log_for_review(self, intent_id: str, intent_type: str, actor: str, payload: Dict):
        """Log intent for post-execution review"""
        
        from backend.core import immutable_log
        
        await immutable_log.append(
            actor=actor,
            action=f"intent_executed_{intent_type}",
            resource=intent_id,
            result="pending_review",
            metadata={
                'intent_type': intent_type,
                'payload_summary': str(payload)[:200],
                'tier': 'TIER_1_REVIEW_REQUIRED',
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    async def _log_emergency(self, intent_id: str, intent_type: str, actor: str, payload: Dict):
        """Heavy logging for emergency intents"""
        
        from backend.core import immutable_log
        from backend.core.clarity_framework import clarity_framework
        
        # Immutable log
        await immutable_log.append(
            actor=actor,
            action=f"EMERGENCY_{intent_type}",
            resource=intent_id,
            result="executed_emergency_override",
            metadata={
                'intent_type': intent_type,
                'payload': payload,
                'tier': 'TIER_4_EMERGENCY',
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        # Clarity framework
        await clarity_framework.record_decision(
            actor=actor,
            action_type=f"EMERGENCY_{intent_type}",
            resource=intent_id,
            decision={'emergency': True, 'payload': payload},
            reasoning_chain=[
                "Emergency tier 4 intent received",
                "Bypassing normal governance flow",
                "Heavy audit logging activated",
                f"Intent: {intent_type}",
                "Execution proceeded immediately"
            ]
        )
        
        logger.critical(f"[INTENT-GOVERNANCE] EMERGENCY intent logged: {intent_type}")


# Global instance
intent_governance_router = IntentGovernanceRouter()
