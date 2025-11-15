"""
Charter Integration with Unified Logic
Hooks Grace's immutable charter into the unified logic flow

Every high-level decision passes through charter evaluation.
Flexible action sequencing guided by immutable pillars.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional

from .charter_policy_layer import get_charter_policy_layer, CharterEvaluation
from backend.constitutional.grace_charter import get_grace_charter
from backend.execution.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class UnifiedLogicWithCharter:
    """
    Unified Logic enhanced with charter policy layer
    
    Integration points:
    1. Intent evaluation - Check charter before processing any intent
    2. Plan generation - Ensure plans align with mission pillars
    3. Action sequencing - Prioritize based on pillar priorities
    4. Authorization - Enforce principal-based charter modification rights
    5. Progress tracking - Update charter metrics from executed actions
    """
    
    def __init__(self):
        self.charter_policy = None
        self.charter = None
        
        # Integration hooks
        self.pre_intent_hooks = []
        self.post_action_hooks = []
        
        # Statistics
        self.stats = {
            "intents_evaluated": 0,
            "charter_blocks": 0,
            "mission_contributions": 0
        }
    
    async def initialize(self):
        """Initialize unified logic with charter"""
        
        self.charter_policy = await get_charter_policy_layer()
        self.charter = get_grace_charter()
        
        logger.info("[UNIFIED LOGIC] Charter integration initialized")
    
    async def process_intent(
        self,
        intent: Dict[str, Any],
        actor: str = "grace"
    ) -> Dict[str, Any]:
        """
        Process an intent through unified logic with charter evaluation
        
        Workflow:
        1. Evaluate against charter (compliance, mission alignment)
        2. If non-compliant, reject with explanation
        3. If compliant, process through standard unified logic
        4. Track mission contribution
        5. Update charter metrics on completion
        """
        
        intent_description = intent.get("description", "")
        intent_type = intent.get("type", "unknown")
        
        logger.info(f"[UNIFIED LOGIC] Processing intent: {intent_description}")
        
        self.stats["intents_evaluated"] += 1
        
        # Step 1: Charter evaluation
        evaluation = await self.charter_policy.evaluate_intent(
            intent_description=intent_description,
            intent_type=intent_type,
            actor=actor,
            context=intent.get("context")
        )
        
        # Step 2: Check compliance
        if not evaluation.compliant:
            self.stats["charter_blocks"] += 1
            
            logger.warning(f"[UNIFIED LOGIC] Intent blocked by charter: {evaluation.violations}")
            
            # Log to immutable log
            await immutable_log.record(
                actor=actor,
                action="intent.charter_blocked",
                result={
                    "intent": intent_description,
                    "violations": evaluation.violations,
                    "evaluation": evaluation.__dict__
                },
                trust_score=0.0
            )
            
            return {
                "success": False,
                "blocked_by": "charter_policy",
                "violations": evaluation.violations,
                "blocked_until": evaluation.blocked_until,
                "recommendation": "Satisfy blocking clauses or request authorization from charter owner"
            }
        
        # Step 3: Track mission contribution
        if evaluation.contributes_to_mission:
            self.stats["mission_contributions"] += 1
            
            logger.info(f"[UNIFIED LOGIC] Intent contributes to mission pillars: {evaluation.aligned_pillars}")
        
        # Step 4: Process through unified logic (simulated)
        result = await self._execute_intent(intent, evaluation)
        
        # Step 5: Update charter metrics if action succeeded
        if result.get("success") and evaluation.contributes_to_mission:
            await self._update_charter_metrics(evaluation, result)
        
        # Step 6: Log to immutable log
        await immutable_log.record(
            actor=actor,
            action="intent.processed",
            result={
                "intent": intent_description,
                "success": result.get("success"),
                "mission_pillars": evaluation.aligned_pillars,
                "charter_evaluation": evaluation.__dict__
            },
            trust_score=1.0 if result.get("success") else 0.5
        )
        
        return result
    
    async def _execute_intent(
        self,
        intent: Dict[str, Any],
        charter_eval: CharterEvaluation
    ) -> Dict[str, Any]:
        """Execute the intent (simplified - in production, routes to appropriate subsystem)"""
        
        # Simulate execution
        return {
            "success": True,
            "intent_id": intent.get("intent_id", "unknown"),
            "charter_aligned": charter_eval.contributes_to_mission,
            "pillars_advanced": charter_eval.enabled_pillars,
            "suggested_next": charter_eval.suggested_sequence
        }
    
    async def _update_charter_metrics(
        self,
        evaluation: CharterEvaluation,
        result: Dict[str, Any]
    ):
        """Update charter metrics based on action results"""
        
        # Extract metrics from result
        metrics = result.get("metrics", {})
        
        # Update each aligned pillar
        for pillar_name in evaluation.enabled_pillars:
            from backend.constitutional.grace_charter import MissionPillar
            
            pillar = MissionPillar(pillar_name)
            
            # Update pillar metrics
            if metrics:
                self.charter.update_metrics(pillar=pillar, metrics=metrics)
                logger.info(f"[UNIFIED LOGIC] Updated {pillar_name} metrics: {metrics}")
    
    async def generate_mission_aligned_plan(
        self,
        goal: str,
        actor: str = "grace"
    ) -> Dict[str, Any]:
        """
        Generate a plan that aligns with mission pillars
        
        Returns plan with charter-aligned action sequence
        """
        
        logger.info(f"[UNIFIED LOGIC] Generating mission-aligned plan for: {goal}")
        
        # Get recommended actions from charter
        recommended = await self.charter_policy.get_recommended_actions(actor)
        
        # Build plan steps
        plan_steps = []
        
        for i, action in enumerate(recommended[:5]):  # Top 5
            plan_steps.append({
                "step": i + 1,
                "description": action["title"],
                "type": action["layer3_intent"],
                "pillar": action["pillar"],
                "priority": action["priority"],
                "reason": action["reason"]
            })
        
        plan = {
            "plan_id": f"mission_plan_{len(plan_steps)}",
            "goal": goal,
            "steps": plan_steps,
            "mission_aligned": True,
            "generated_by": "unified_logic_with_charter"
        }
        
        # Evaluate the plan
        evaluation = await self.charter_policy.evaluate_plan(plan, actor)
        
        plan["charter_evaluation"] = evaluation
        
        return plan
    
    async def check_authorization(
        self,
        action: str,
        actor: str
    ) -> Dict[str, Any]:
        """
        Check if actor is authorized for an action
        
        Handles charter modification authorization specially
        """
        
        # Check if this is charter modification
        if "charter" in action.lower() and "modify" in action.lower():
            can_modify = self.charter.can_modify_charter(actor)
            
            return {
                "authorized": can_modify,
                "actor": actor,
                "action": action,
                "reason": f"Charter owner: {self.charter.charter_owner}" if not can_modify else "Authorized",
                "charter_owner_only": True
            }
        
        # For other actions, check charter compliance
        compliance = await self.charter_policy.enforce_charter_compliance(action, actor)
        
        return {
            "authorized": compliance["decision"] in ["allow", "advisory"],
            "actor": actor,
            "action": action,
            "decision": compliance["decision"],
            "reason": compliance.get("reason", "Charter compliant")
        }
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of charter integration"""
        
        return {
            "charter_integrated": True,
            "charter_phase": self.charter.phase if self.charter else None,
            "charter_owner": self.charter.charter_owner if self.charter else None,
            "statistics": self.stats,
            "policy_layer_stats": self.charter_policy.stats if self.charter_policy else {},
            "enforcement_level": self.charter_policy.enforcement_level if self.charter_policy else None
        }


# Global unified logic instance
_unified_logic_with_charter: Optional[UnifiedLogicWithCharter] = None


async def get_unified_logic_with_charter() -> UnifiedLogicWithCharter:
    """Get or create the global unified logic with charter integration"""
    global _unified_logic_with_charter
    
    if _unified_logic_with_charter is None:
        _unified_logic_with_charter = UnifiedLogicWithCharter()
        await _unified_logic_with_charter.initialize()
    
    return _unified_logic_with_charter


# Convenience functions for unified logic + charter


async def process_intent_with_charter(
    intent_description: str,
    actor: str = "grace",
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process an intent through unified logic with charter evaluation
    
    Usage:
        result = await process_intent_with_charter(
            intent_description="Learn quantum physics",
            actor="grace"
        )
        
        if result["success"]:
            print(f"Intent advanced pillars: {result['pillars_advanced']}")
    """
    
    unified_logic = await get_unified_logic_with_charter()
    
    intent = {
        "description": intent_description,
        "type": "user_intent",
        "context": context or {}
    }
    
    return await unified_logic.process_intent(intent, actor)


async def check_charter_authorization(action: str, actor: str) -> bool:
    """
    Quick check if actor is authorized for an action
    
    Usage:
        if await check_charter_authorization("modify charter", "Aaron Shipton"):
            # Proceed with charter modification
        else:
            # Deny
    """
    
    unified_logic = await get_unified_logic_with_charter()
    
    auth_result = await unified_logic.check_authorization(action, actor)
    
    return auth_result["authorized"]
