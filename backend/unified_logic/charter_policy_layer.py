"""
Charter Policy Layer - Unified Logic Integration
Encodes Grace's immutable mission charter into the policy evaluation system

Every intent, plan, and action is evaluated against the charter.
Only Aaron Shipton can modify the charter.
Action sequencing remains flexible but guided by immutable pillars.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from backend.constitutional.grace_charter import get_grace_charter, MissionPillar

logger = logging.getLogger(__name__)


@dataclass
class CharterEvaluation:
    """Result of evaluating an action against the charter"""
    action_id: str
    evaluation_timestamp: str
    
    # Charter compliance
    compliant: bool
    
    # Mission alignment
    aligned_pillars: List[str]
    enabled_pillars: List[str]
    contributes_to_mission: bool
    
    # Authorization
    principal_authorized: bool
    principal_name: Optional[str] = None
    
    # Violations
    violations: List[str] = None
    
    # Recommendations
    suggested_sequence: Optional[str] = None
    blocked_until: Optional[str] = None
    
    def __post_init__(self):
        if self.violations is None:
            self.violations = []
        if self.evaluation_timestamp is None:
            self.evaluation_timestamp = datetime.utcnow().isoformat()


class CharterPolicyLayer:
    """
    Charter policy layer for Unified Logic
    
    Integrates Grace's immutable mission charter into the policy evaluation system.
    
    Features:
    - Evaluates every intent/plan against charter pillars
    - Enforces principal-based charter modification rights
    - Checks mission alignment for all high-level actions
    - Recommends action sequencing based on pillar priorities
    - Blocks actions that violate charter constraints
    """
    
    def __init__(self):
        self.charter = get_grace_charter()
        self.mission_planner = None
        
        # Policy enforcement
        self.enforcement_level = "strict"  # strict, advisory, disabled
        
        # Statistics
        self.stats = {
            "total_evaluations": 0,
            "compliant_actions": 0,
            "violations_blocked": 0,
            "charter_modification_attempts": 0,
            "unauthorized_modification_attempts": 0
        }
    
    async def initialize(self):
        """Initialize the charter policy layer"""
        
        from backend.constitutional.mission_planner import get_mission_planner
        self.mission_planner = await get_mission_planner()
        
        logger.info("[CHARTER POLICY] Charter policy layer initialized")
        logger.info(f"[CHARTER POLICY] Phase: {self.charter.phase}, Version: {self.charter.version}")
        logger.info(f"[CHARTER POLICY] Immutable: {self.charter.immutable}")
        logger.info(f"[CHARTER POLICY] Owner: {self.charter.charter_owner}")
    
    async def evaluate_intent(
        self,
        intent_description: str,
        intent_type: str,
        actor: str,
        context: Optional[Dict[str, Any]] = None
    ) -> CharterEvaluation:
        """
        Evaluate an intent against the charter
        
        Returns charter evaluation with compliance status and recommendations
        """
        
        self.stats["total_evaluations"] += 1
        
        action_id = f"eval_{self.stats['total_evaluations']}"
        
        evaluation = CharterEvaluation(
            action_id=action_id,
            evaluation_timestamp=datetime.utcnow().isoformat(),
            compliant=True,
            aligned_pillars=[],
            enabled_pillars=[],
            contributes_to_mission=False,
            principal_authorized=True
        )
        
        # 1. Check if this is a charter modification attempt
        if "charter" in intent_description.lower() or "mission" in intent_description.lower():
            if "modify" in intent_description.lower() or "change" in intent_description.lower():
                self.stats["charter_modification_attempts"] += 1
                
                # Check principal authorization
                principal = self.charter.recognize_principal(actor)
                
                if principal:
                    evaluation.principal_name = principal.name
                    
                    if not principal.can_modify_charter:
                        evaluation.compliant = False
                        evaluation.principal_authorized = False
                        evaluation.violations.append(
                            f"Charter modification requires authorization from {self.charter.charter_owner}. "
                            f"Actor '{actor}' is not authorized."
                        )
                        
                        self.stats["unauthorized_modification_attempts"] += 1
                        
                        logger.warning(f"[CHARTER POLICY] Unauthorized charter modification attempt by {actor}")
                        
                        return evaluation
                else:
                    # Unknown actor trying to modify charter
                    evaluation.compliant = False
                    evaluation.principal_authorized = False
                    evaluation.violations.append(
                        f"Unknown actor '{actor}' cannot modify charter. "
                        f"Only {self.charter.charter_owner} can modify Phase {self.charter.phase}."
                    )
                    
                    self.stats["unauthorized_modification_attempts"] += 1
                    
                    logger.error(f"[CHARTER POLICY] Unknown actor '{actor}' attempted charter modification")
                    
                    return evaluation
        
        # 2. Check mission alignment
        alignment = self.charter.check_mission_alignment(intent_description, intent_type)
        
        evaluation.aligned_pillars = alignment.get("pillars", [])
        evaluation.enabled_pillars = alignment.get("enabled_pillars", [])
        evaluation.contributes_to_mission = alignment.get("mission_contribution", False)
        
        # 3. Check if action targets disabled pillars
        disabled_pillars = [p for p in evaluation.aligned_pillars if p not in evaluation.enabled_pillars]
        
        if disabled_pillars:
            # Action aligns with locked pillars
            for pillar_name in disabled_pillars:
                pillar = MissionPillar(pillar_name)
                pillar_status = self.charter.get_pillar_status(pillar)
                
                # Find blocking clauses
                blocking_clauses = [
                    c for c in self.charter.clauses.values()
                    if c.blocking and not c.satisfied and self.charter.pillars[c.pillar]["priority"] < pillar_status["priority"]
                ]
                
                if blocking_clauses:
                    clause = blocking_clauses[0]
                    
                    evaluation.violations.append(
                        f"Pillar '{pillar_status['name']}' is locked. "
                        f"Must satisfy clause '{clause.clause_id}': {clause.description}"
                    )
                    
                    evaluation.blocked_until = clause.clause_id
                    
                    # Advisory, not blocking (flexible sequencing)
                    logger.warning(f"[CHARTER POLICY] Intent aligns with locked pillar {pillar_name}")
        
        # 4. Generate sequencing recommendation
        if evaluation.contributes_to_mission and evaluation.enabled_pillars:
            # Find lowest priority enabled pillar this contributes to
            pillar_priorities = {
                p: self.charter.pillars[MissionPillar(p)]["priority"]
                for p in evaluation.enabled_pillars
            }
            
            recommended_pillar = min(pillar_priorities, key=pillar_priorities.get)
            
            evaluation.suggested_sequence = (
                f"Prioritize this action as it advances '{recommended_pillar}' "
                f"(Priority {pillar_priorities[recommended_pillar]})"
            )
        
        # 5. Final compliance check
        if self.enforcement_level == "strict" and evaluation.violations:
            evaluation.compliant = False
        
        if evaluation.compliant:
            self.stats["compliant_actions"] += 1
        else:
            self.stats["violations_blocked"] += 1
        
        logger.info(
            f"[CHARTER POLICY] Evaluated intent: compliant={evaluation.compliant}, "
            f"mission_contribution={evaluation.contributes_to_mission}, "
            f"pillars={evaluation.aligned_pillars}"
        )
        
        return evaluation
    
    async def evaluate_plan(
        self,
        plan: Dict[str, Any],
        actor: str
    ) -> Dict[str, Any]:
        """
        Evaluate a complete action plan against the charter
        
        Returns evaluation with step-by-step charter alignment
        """
        
        plan_id = plan.get("plan_id", "unknown")
        steps = plan.get("steps", [])
        
        logger.info(f"[CHARTER POLICY] Evaluating plan {plan_id} with {len(steps)} steps")
        
        step_evaluations = []
        overall_compliant = True
        total_mission_contribution = 0
        
        for i, step in enumerate(steps):
            step_description = step.get("description", "")
            step_type = step.get("type", "unknown")
            
            eval_result = await self.evaluate_intent(
                intent_description=step_description,
                intent_type=step_type,
                actor=actor
            )
            
            step_evaluations.append({
                "step_index": i,
                "step_description": step_description,
                "evaluation": asdict(eval_result)
            })
            
            if not eval_result.compliant:
                overall_compliant = False
            
            if eval_result.contributes_to_mission:
                total_mission_contribution += 1
        
        mission_alignment_score = total_mission_contribution / len(steps) if steps else 0.0
        
        return {
            "plan_id": plan_id,
            "overall_compliant": overall_compliant,
            "mission_alignment_score": mission_alignment_score,
            "total_steps": len(steps),
            "mission_contributing_steps": total_mission_contribution,
            "step_evaluations": step_evaluations,
            "recommendation": self._generate_plan_recommendation(
                overall_compliant, mission_alignment_score, step_evaluations
            )
        }
    
    def _generate_plan_recommendation(
        self,
        compliant: bool,
        mission_score: float,
        step_evaluations: List[Dict[str, Any]]
    ) -> str:
        """Generate recommendation for a plan"""
        
        if not compliant:
            violations = []
            for step_eval in step_evaluations:
                if not step_eval["evaluation"]["compliant"]:
                    violations.extend(step_eval["evaluation"]["violations"])
            
            return (
                f"Plan NOT COMPLIANT with charter. Violations: {'; '.join(violations)}. "
                f"Requires authorization or pillar unlock."
            )
        
        if mission_score == 0.0:
            return (
                "Plan is compliant but does not contribute to any mission pillar. "
                "Consider aligning plan with Knowledge, Business, Energy, Quantum, "
                "Atlantis/Wakanda, Co-habitation, or Science pillars."
            )
        
        if mission_score < 0.5:
            return (
                f"Plan is compliant with {mission_score:.0%} mission alignment. "
                f"Consider increasing mission contribution for higher priority."
            )
        
        return (
            f"Plan is charter-compliant with {mission_score:.0%} mission alignment. "
            f"Recommended for execution."
        )
    
    async def get_recommended_actions(self, actor: str = "grace") -> List[Dict[str, Any]]:
        """
        Get recommended actions based on charter priorities
        
        Returns prioritized list of actions that advance mission pillars
        """
        
        if not self.mission_planner:
            await self.initialize()
        
        recommendations = []
        
        # Get active mission tasks
        active_tasks = self.mission_planner.get_active_tasks()
        
        for task in active_tasks[:10]:  # Top 10
            recommendations.append({
                "task_id": task.task_id,
                "title": task.title,
                "pillar": task.pillar.value,
                "priority": task.priority,
                "layer3_intent": task.layer3_intent,
                "reason": f"Advances {task.pillar.value} mission pillar (Priority {task.priority})"
            })
        
        # Sort by priority
        recommendations.sort(key=lambda x: x["priority"])
        
        return recommendations
    
    def get_charter_status(self) -> Dict[str, Any]:
        """Get current charter status"""
        
        return {
            "phase": self.charter.phase,
            "version": self.charter.version,
            "immutable": self.charter.immutable,
            "owner": self.charter.charter_owner,
            "enforcement_level": self.enforcement_level,
            "pillars": {
                pillar.value: {
                    "enabled": self.charter.pillars[pillar]["enabled"],
                    "priority": self.charter.pillars[pillar]["priority"],
                    "name": self.charter.pillars[pillar]["name"]
                }
                for pillar in MissionPillar
            },
            "statistics": self.stats,
            "principals": list(self.charter.principals.keys())
        }
    
    async def enforce_charter_compliance(
        self,
        action_description: str,
        actor: str
    ) -> Dict[str, Any]:
        """
        Enforce charter compliance for an action
        
        Returns decision: allow, deny, or advisory
        """
        
        evaluation = await self.evaluate_intent(
            intent_description=action_description,
            intent_type="action",
            actor=actor
        )
        
        if not evaluation.compliant:
            return {
                "decision": "deny",
                "reason": "; ".join(evaluation.violations),
                "evaluation": asdict(evaluation)
            }
        
        if evaluation.violations and self.enforcement_level == "advisory":
            return {
                "decision": "advisory",
                "reason": "Action may target locked pillars. Proceed with caution.",
                "warnings": evaluation.violations,
                "evaluation": asdict(evaluation)
            }
        
        return {
            "decision": "allow",
            "mission_contribution": evaluation.contributes_to_mission,
            "aligned_pillars": evaluation.aligned_pillars,
            "suggested_sequence": evaluation.suggested_sequence,
            "evaluation": asdict(evaluation)
        }


# Global charter policy layer
_charter_policy_layer: Optional[CharterPolicyLayer] = None


async def get_charter_policy_layer() -> CharterPolicyLayer:
    """Get or create the global charter policy layer"""
    global _charter_policy_layer
    
    if _charter_policy_layer is None:
        _charter_policy_layer = CharterPolicyLayer()
        await _charter_policy_layer.initialize()
    
    return _charter_policy_layer


async def evaluate_against_charter(
    intent: str,
    actor: str,
    context: Optional[Dict[str, Any]] = None
) -> CharterEvaluation:
    """
    Convenience function to evaluate an intent against the charter
    
    Usage:
        evaluation = await evaluate_against_charter(
            intent="Build a quantum computer",
            actor="grace"
        )
        
        if not evaluation.compliant:
            print(f"Charter violation: {evaluation.violations}")
    """
    
    policy_layer = await get_charter_policy_layer()
    
    return await policy_layer.evaluate_intent(
        intent_description=intent,
        intent_type="intent",
        actor=actor,
        context=context
    )
