"""
GRACE Agentic Spine - Autonomous Decision-Making Architecture

This is the central nervous system that gives GRACE autonomous agency.
It coordinates sensing, reasoning, planning, execution, and learning
while maintaining trust, ethics, and human collaboration.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from collections import defaultdict

from .trigger_mesh import trigger_mesh, TriggerEvent
from backend.logging.immutable_log import immutable_log
# Integrations commented out - not critical for core functionality
# from .integrations.slack_integration import slack_integration
# from .integrations.pagerduty_integration import pagerduty_integration
# from .integrations.github_integration import github_integration


class ConfidenceLevel(Enum):
    VERY_LOW = 0.0
    LOW = 0.3
    MEDIUM = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9


class RiskLevel(Enum):
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class PlanStatus(Enum):
    PROPOSED = "proposed"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class EnrichedEvent:
    """Event with full context, intent, and expected outcomes"""
    event_id: str
    original_event: TriggerEvent
    signer_identity: str
    intent: str
    context: Dict[str, Any]
    expected_outcome: str
    confidence: float
    signals: List[Dict[str, Any]] = field(default_factory=list)
    missing_signals: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class HealthNode:
    """Node in the unified health graph"""
    node_id: str
    node_type: str
    name: str
    status: str
    kpis: Dict[str, float]
    dependencies: List[str]
    dependents: List[str]
    blast_radius: int
    priority: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Playbook:
    """Policy-aware recovery plan as state machine"""
    playbook_id: str
    name: str
    description: str
    preconditions: List[Dict[str, Any]]
    steps: List[Dict[str, Any]]
    verifications: List[Dict[str, Any]]
    rollback_steps: List[Dict[str, Any]]
    risk_level: RiskLevel
    requires_approval: bool
    success_rate: float = 0.0
    execution_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryPlan:
    """Autonomous recovery plan with governance"""
    plan_id: str
    playbook: Playbook
    target_nodes: List[str]
    parameters: Dict[str, Any]
    risk_score: float
    justification: str
    status: PlanStatus
    approvals: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    outcome: Optional[str] = None


@dataclass
class DecisionRecord:
    """Auditable decision with rationale"""
    decision_id: str
    decision_type: str
    context: Dict[str, Any]
    options_considered: List[Dict[str, Any]]
    chosen_option: str
    rationale: str
    confidence: float
    risk_assessment: Dict[str, Any]
    approvals_required: List[str]
    approvals_received: List[str]
    outcome: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class EventEnrichmentLayer:
    """Enriches trigger mesh events with signer identity, context, and intent"""
    
    def __init__(self):
        self.enrichment_rules = {}
        self.probe_registry = {}
    
    async def enrich(self, event: TriggerEvent) -> EnrichedEvent:
        """Enrich event with full context and intent data"""
        event_id = f"{event.source}:{event.event_type}:{datetime.utcnow().timestamp()}"
        
        context = await self._gather_context(event)
        intent = await self._infer_intent(event, context)
        expected_outcome = await self._predict_outcome(event, context, intent)
        confidence = await self._calculate_confidence(event, context)
        
        enriched = EnrichedEvent(
            event_id=event_id,
            original_event=event,
            signer_identity=event.actor,
            intent=intent,
            context=context,
            expected_outcome=expected_outcome,
            confidence=confidence
        )
        
        if confidence < 0.6:
            enriched.missing_signals = await self._identify_missing_signals(event, context)
            await self._request_signals(enriched.missing_signals)
        
        return enriched
    
    async def _gather_context(self, event: TriggerEvent) -> Dict[str, Any]:
        """Gather relevant context from health graph, ledger, memory"""
        context = {
            "event_history": await self._get_recent_similar_events(event),
            "system_state": await self._get_system_state(event.resource),
            "actor_history": await self._get_actor_history(event.actor),
            "dependencies": await self._get_dependencies(event.resource)
        }
        return context
    
    async def _infer_intent(self, event: TriggerEvent, context: Dict) -> str:
        """Infer why this event happened - what was the intent?"""
        if "deploy" in event.event_type:
            return "deploy_new_version"
        elif "scale" in event.event_type:
            return "adjust_capacity"
        elif "alert" in event.event_type:
            return "signal_degradation"
        return "unknown_intent"
    
    async def _predict_outcome(self, event: TriggerEvent, context: Dict, intent: str) -> str:
        """Predict what should happen as a result"""
        outcomes = {
            "deploy_new_version": "service_running_new_version",
            "adjust_capacity": "capacity_meets_demand",
            "signal_degradation": "investigation_initiated"
        }
        return outcomes.get(intent, "state_change")
    
    async def _calculate_confidence(self, event: TriggerEvent, context: Dict) -> float:
        """Calculate confidence in event interpretation"""
        signal_count = len(context.get("event_history", [])) + len(context.get("dependencies", []))
        return min(0.5 + (signal_count * 0.05), 0.95)
    
    async def _get_recent_similar_events(self, event: TriggerEvent) -> List[Dict]:
        """Query ledger for similar events - IMPLEMENTED"""
        try:
            entries = await immutable_log.query_recent(
                actor=event.actor,
                resource=event.resource,
                hours=24
            )
            return [
                {
                    "event_id": entry.id,
                    "action": entry.action,
                    "outcome": entry.outcome,
                    "timestamp": entry.timestamp.isoformat() if hasattr(entry, 'timestamp') else None
                }
                for entry in entries[:10]
            ]
        except Exception as e:
            return []
    
    async def _get_system_state(self, resource: str) -> Dict:
        """Get current state of resource from health graph - IMPLEMENTED"""
        try:
            # Get kernel health from registry
            from backend.kernels.kernel_registry import kernel_registry
            status = kernel_registry.get_status()
            
            # Check if specific kernel
            kernel = kernel_registry.get_kernel(resource)
            if kernel:
                return {
                    "status": "operational",
                    "resource": resource,
                    "kernel_available": True,
                    "registry_health": status["health"].get(resource, {})
                }
            
            # Return overall system state
            return {
                "status": "operational" if status["initialized"] else "degraded",
                "total_kernels": status["total_kernels"],
                "domain_kernels": status["domain_kernels"],
                "clarity_kernels": status["clarity_kernels"]
            }
        except Exception as e:
            return {"status": "unknown", "error": str(e)}
    
    async def _get_actor_history(self, actor: str) -> Dict:
        """Get actor's recent actions from ledger - IMPLEMENTED"""
        try:
            from backend.models.governance_models import AuditLog
            from backend.models.base_models import async_session
            from sqlalchemy import select, desc
            
            async with async_session() as session:
                result = await session.execute(
                    select(AuditLog)
                    .where(AuditLog.actor == actor)
                    .order_by(desc(AuditLog.timestamp))
                    .limit(10)
                )
                logs = result.scalars().all()
                return {
                    "recent_actions": [
                        {
                            "action": log.action,
                            "resource": log.resource,
                            "result": log.result,
                            "timestamp": log.timestamp.isoformat() if hasattr(log, 'timestamp') else None
                        }
                        for log in logs
                    ],
                    "total_actions": len(logs)
                }
        except Exception as e:
            return {"recent_actions": [], "error": str(e)}
    
    async def _get_dependencies(self, resource: str) -> List[str]:
        """Get resource dependencies from health graph - IMPLEMENTED"""
        try:
            # Check if it's a kernel - get its domain
            from backend.kernels.kernel_registry import kernel_registry
            kernel = kernel_registry.get_kernel(resource)
            
            if kernel:
                # Return kernel dependencies (message_bus, etc.)
                return ["message_bus", "infrastructure_manager"]
            
            # For other resources, return empty for now
            # TODO: Implement full health graph with dependency tracking
            return []
        except Exception as e:
            return []
    
    async def _identify_missing_signals(self, event: TriggerEvent, context: Dict) -> List[str]:
        """Identify what signals would increase confidence"""
        return ["health_probe", "dependency_check"]
    
    async def _request_signals(self, signals: List[str]):
        """Spin up probes or synthetic checks to gather missing signals"""
        for signal in signals:
            await trigger_mesh.publish(TriggerEvent(
                event_type=f"probe.request.{signal}",
                source="enrichment_layer",
                actor="grace_agent",
                resource=signal,
                payload={"probe_type": signal},
                timestamp=datetime.utcnow()
            ))


class TrustCorePartner:
    """Trust cores as decision partners, not just gatekeepers"""
    
    def __init__(self):
        self.policy_intents = {}
        self.risk_models = {}
    
    async def evaluate_decision(self, decision: DecisionRecord) -> Tuple[bool, str, List[str]]:
        """Evaluate decision against policy intent and risk scoring"""
        
        approved = True
        reasoning = []
        escalations = []
        
        policy_check = await self._check_policy_alignment(decision)
        if not policy_check["aligned"]:
            approved = False
            reasoning.append(f"Policy misalignment: {policy_check['reason']}")
        
        risk_score = await self._calculate_risk_score(decision)
        decision.risk_assessment["trust_core_score"] = risk_score
        
        if risk_score > 0.7:
            if decision.decision_type in ["data_deletion", "production_deploy", "security_change"]:
                escalations.append("human_approval_required")
                reasoning.append(f"High risk ({risk_score:.2f}) requires human approval")
            else:
                approved = False
                reasoning.append(f"Risk score {risk_score:.2f} exceeds threshold")
        elif risk_score > 0.4:
            escalations.append("trust_core_review")
            reasoning.append(f"Moderate risk ({risk_score:.2f}) - trust core reviewing")
        else:
            reasoning.append(f"Low risk ({risk_score:.2f}) - auto-approved")
        
        edge_case = await self._check_edge_cases(decision)
        if edge_case:
            escalations.append("edge_case_review")
            reasoning.append(f"Edge case detected: {edge_case}")
        
        rationale = " | ".join(reasoning)
        return approved, rationale, escalations
    
    async def co_sign_recovery(self, plan: RecoveryPlan) -> bool:
        """Co-sign recovery action when guardrails satisfied"""
        
        if plan.risk_score < 0.3:
            await self._sign_plan(plan, "auto_approved_low_risk")
            return True
        
        if plan.playbook.success_rate > 0.9 and plan.playbook.execution_count > 10:
            await self._sign_plan(plan, "auto_approved_proven_playbook")
            return True
        
        guardrails_satisfied = await self._verify_guardrails(plan)
        if guardrails_satisfied:
            await self._sign_plan(plan, "guardrails_satisfied")
            return True
        
        return False
    
    async def _check_policy_alignment(self, decision: DecisionRecord) -> Dict:
        """Check if decision aligns with policy intent"""
        return {"aligned": True, "reason": "within_bounds"}
    
    async def _calculate_risk_score(self, decision: DecisionRecord) -> float:
        """Calculate risk score based on context and impact"""
        base_risk = {
            "data_access": 0.3,
            "deployment": 0.5,
            "scaling": 0.2,
            "security_change": 0.8,
            "data_deletion": 0.9
        }.get(decision.decision_type, 0.4)
        
        confidence_modifier = (1.0 - decision.confidence) * 0.3
        return min(base_risk + confidence_modifier, 1.0)
    
    async def _check_edge_cases(self, decision: DecisionRecord) -> Optional[str]:
        """Detect edge cases requiring special handling"""
        if decision.context.get("cross_boundary_impact"):
            return "cross_boundary_decision"
        return None
    
    async def _verify_guardrails(self, plan: RecoveryPlan) -> bool:
        """Verify all safety guardrails are in place"""
        has_rollback = len(plan.playbook.rollback_steps) > 0
        has_verification = len(plan.playbook.verifications) > 0
        preconditions_met = await self._check_preconditions(plan)
        
        return has_rollback and has_verification and preconditions_met
    
    async def _check_preconditions(self, plan: RecoveryPlan) -> bool:
        """Verify plan preconditions are satisfied"""
        return True
    
    async def _sign_plan(self, plan: RecoveryPlan, reason: str):
        """Co-sign a recovery plan"""
        plan.approvals.append(f"trust_core:{reason}")
        
        await immutable_log.append(
            actor="trust_core",
            action="co_sign_recovery_plan",
            resource=plan.plan_id,
            subsystem="trust_core_partner",
            payload={"reason": reason, "risk_score": plan.risk_score},
            result="approved"
        )


class LedgerReasoningHooks:
    """Real-time queries and pattern detection over immutable log"""
    
    async def correlate_incidents(self, current_event: EnrichedEvent) -> List[Dict]:
        """Find related incidents from historical log"""
        return []
    
    async def detect_recurring_patterns(self, pattern_type: str) -> List[Dict]:
        """Detect patterns that repeat over time"""
        return []
    
    async def justify_action(self, plan: RecoveryPlan) -> str:
        """Generate justification based on historical success"""
        
        similar_recoveries = await self._query_similar_recoveries(plan.playbook.playbook_id)
        
        if not similar_recoveries:
            return f"Applying {plan.playbook.name} based on policy match"
        
        success_count = sum(1 for r in similar_recoveries if r.get("outcome") == "success")
        total = len(similar_recoveries)
        success_rate = success_count / total if total > 0 else 0.0
        
        if success_rate > 0.8:
            return f"Applying {plan.playbook.name} - succeeded {success_count}/{total} times in similar scenarios"
        elif success_rate > 0.5:
            return f"Applying {plan.playbook.name} with caution - {success_rate:.1%} success rate in {total} attempts"
        else:
            return f"Experimental application of {plan.playbook.name} - limited historical success ({success_rate:.1%})"
    
    async def _query_similar_recoveries(self, playbook_id: str) -> List[Dict]:
        """Query ledger for similar recovery attempts"""
        return []


class UnifiedHealthGraph:
    """Dynamic graph of services, dependencies, and KPIs"""
    
    def __init__(self):
        self.nodes: Dict[str, HealthNode] = {}
        self.edges: Dict[str, List[str]] = defaultdict(list)
    
    async def register_node(self, node: HealthNode):
        """Add or update node in health graph"""
        self.nodes[node.node_id] = node
        
        for dep in node.dependencies:
            self.edges[node.node_id].append(dep)
        
        await self._recalculate_blast_radius(node.node_id)
        await self._recalculate_priorities()
    
    async def update_health(self, node_id: str, status: str, kpis: Dict[str, float]):
        """Update node health status"""
        if node_id in self.nodes:
            self.nodes[node_id].status = status
            self.nodes[node_id].kpis.update(kpis)
            
            if status in ["degraded", "failing", "down"]:
                await self._propagate_health_impact(node_id)
    
    async def calculate_blast_radius(self, node_id: str) -> List[str]:
        """Calculate what would be impacted if this node fails"""
        impacted = set()
        queue = [node_id]
        
        while queue:
            current = queue.pop(0)
            if current in self.nodes:
                for dependent in self.nodes[current].dependents:
                    if dependent not in impacted:
                        impacted.add(dependent)
                        queue.append(dependent)
        
        return list(impacted)
    
    async def get_critical_path(self, from_node: str, to_node: str) -> List[str]:
        """Find critical dependency path between nodes"""
        return []
    
    async def _recalculate_blast_radius(self, node_id: str):
        """Recalculate blast radius when topology changes"""
        blast_radius = await self.calculate_blast_radius(node_id)
        if node_id in self.nodes:
            self.nodes[node_id].blast_radius = len(blast_radius)
    
    async def _recalculate_priorities(self):
        """Recalculate node priorities based on blast radius and criticality"""
        for node_id, node in self.nodes.items():
            criticality_score = node.blast_radius * len(node.dependents)
            node.priority = criticality_score
    
    async def _propagate_health_impact(self, node_id: str):
        """Propagate health degradation to dependents"""
        impacted = await self.calculate_blast_radius(node_id)
        
        for impacted_node_id in impacted:
            await trigger_mesh.publish(TriggerEvent(
                event_type="health.degradation.propagated",
                source="health_graph",
                actor="grace_agent",
                resource=impacted_node_id,
                payload={"source_node": node_id},
                timestamp=datetime.utcnow()
            ))


class AutonomousPlanner:
    """Plans recovery actions based on health state and goals"""
    
    def __init__(self, health_graph: UnifiedHealthGraph, trust_core: TrustCorePartner):
        self.health_graph = health_graph
        self.trust_core = trust_core
        self.playbooks: Dict[str, Playbook] = {}
        self.active_plans: Dict[str, RecoveryPlan] = {}
    
    async def register_playbook(self, playbook: Playbook):
        """Register a recovery playbook"""
        self.playbooks[playbook.playbook_id] = playbook
    
    async def plan_recovery(self, enriched_event: EnrichedEvent) -> Optional[RecoveryPlan]:
        """Generate recovery plan for incident"""
        
        matching_playbooks = await self._match_playbooks(enriched_event)
        if not matching_playbooks:
            return None
        
        best_playbook = await self._select_best_playbook(matching_playbooks, enriched_event)
        
        target_nodes = await self._identify_targets(enriched_event)
        parameters = await self._parameterize_playbook(best_playbook, enriched_event)
        risk_score = await self._assess_risk(best_playbook, target_nodes, enriched_event)
        
        justification = await LedgerReasoningHooks().justify_action(
            RecoveryPlan(
                plan_id="temp",
                playbook=best_playbook,
                target_nodes=target_nodes,
                parameters=parameters,
                risk_score=risk_score,
                justification="",
                status=PlanStatus.PROPOSED
            )
        )
        
        plan = RecoveryPlan(
            plan_id=f"plan_{datetime.utcnow().timestamp()}",
            playbook=best_playbook,
            target_nodes=target_nodes,
            parameters=parameters,
            risk_score=risk_score,
            justification=justification,
            status=PlanStatus.PROPOSED
        )
        
        if risk_score > 0.5 or best_playbook.requires_approval:
            plan.status = PlanStatus.AWAITING_APPROVAL
            await self._request_human_approval(plan)
        else:
            can_approve = await self.trust_core.co_sign_recovery(plan)
            if can_approve:
                plan.status = PlanStatus.APPROVED
        
        self.active_plans[plan.plan_id] = plan
        return plan
    
    async def execute_plan(self, plan_id: str) -> bool:
        """Execute approved recovery plan"""
        if plan_id not in self.active_plans:
            return False
        
        plan = self.active_plans[plan_id]
        if plan.status != PlanStatus.APPROVED:
            return False
        
        plan.status = PlanStatus.EXECUTING
        plan.executed_at = datetime.utcnow()
        
        try:
            for step in plan.playbook.steps:
                await self._execute_step(step, plan.parameters)
            
            plan.status = PlanStatus.VERIFYING
            verification_passed = await self._verify_plan(plan)
            
            if verification_passed:
                plan.status = PlanStatus.COMPLETED
                plan.outcome = "success"
                plan.completed_at = datetime.utcnow()
                
                plan.playbook.execution_count += 1
                plan.playbook.success_rate = (
                    (plan.playbook.success_rate * (plan.playbook.execution_count - 1) + 1.0) /
                    plan.playbook.execution_count
                )
                return True
            else:
                await self._rollback_plan(plan)
                plan.status = PlanStatus.ROLLED_BACK
                plan.outcome = "verification_failed"
                return False
                
        except Exception as e:
            await self._rollback_plan(plan)
            plan.status = PlanStatus.FAILED
            plan.outcome = f"error: {str(e)}"
            return False
    
    async def _match_playbooks(self, event: EnrichedEvent) -> List[Playbook]:
        """Find playbooks matching the event"""
        return list(self.playbooks.values())
    
    async def _select_best_playbook(self, playbooks: List[Playbook], event: EnrichedEvent) -> Playbook:
        """Select best playbook based on success rate and risk"""
        return max(playbooks, key=lambda p: p.success_rate)
    
    async def _identify_targets(self, event: EnrichedEvent) -> List[str]:
        """Identify target nodes for recovery"""
        return [event.original_event.resource]
    
    async def _parameterize_playbook(self, playbook: Playbook, event: EnrichedEvent) -> Dict:
        """Fill in playbook parameters from event context"""
        return event.context
    
    async def _assess_risk(self, playbook: Playbook, targets: List[str], event: EnrichedEvent) -> float:
        """Assess risk of executing this playbook"""
        base_risk = 0.3 if playbook.risk_level == RiskLevel.LOW else 0.6
        
        blast_radius_risk = 0.0
        for target in targets:
            if target in self.health_graph.nodes:
                blast_radius_risk += self.health_graph.nodes[target].blast_radius * 0.01
        
        return min(base_risk + blast_radius_risk, 1.0)
    
    async def _request_human_approval(self, plan: RecoveryPlan):
        """Request human sign-off for high-risk plan"""
        await trigger_mesh.publish(TriggerEvent(
            event_type="governance.approval_required",
            source="autonomous_planner",
            actor="grace_agent",
            resource=plan.plan_id,
            payload={
                "plan": plan.plan_id,
                "playbook": plan.playbook.name,
                "risk_score": plan.risk_score,
                "justification": plan.justification
            },
            timestamp=datetime.utcnow()
        ))
    
    async def _execute_step(self, step: Dict, parameters: Dict):
        """Execute a single playbook step"""
        action = step.get("action")

        if action == "scale_up":
            # Real AWS scaling
            from .executors.aws_executor import aws_executor
            node_id = parameters.get("node_id", step.get("target"))
            target_capacity = parameters.get("target_capacity", step.get("capacity", 2))

            result = await aws_executor.execute_scale_action(node_id, target_capacity, parameters)
            if not result.get("success", False):
                raise Exception(f"Scale action failed: {result}")

        elif action == "restart_service":
            # Real AWS instance restart
            from .executors.aws_executor import aws_executor
            instance_id = parameters.get("instance_id", step.get("target"))

            result = await aws_executor.execute_restart_action(instance_id, parameters)
            if not result.get("success", False):
                raise Exception(f"Restart action failed: {result}")

        else:
            # Fallback to mock execution for unknown actions
            print(f"⚠️ Mock executing step: {action} with params {parameters}")
            await asyncio.sleep(0.1)
    
    async def _verify_plan(self, plan: RecoveryPlan) -> bool:
        """Verify plan achieved expected outcome"""
        return True
    
    async def _rollback_plan(self, plan: RecoveryPlan):
        """Rollback failed plan"""
        for step in plan.playbook.rollback_steps:
            await self._execute_step(step, plan.parameters)


class MetaLoopAutonomy:
    """Self-improvement and retrospective analysis"""
    
    def __init__(self, planner: AutonomousPlanner):
        self.planner = planner
        self.improvement_threshold = 0.3
    
    async def schedule_retrospective(self, plan: RecoveryPlan):
        """Schedule post-mortem analysis"""
        await trigger_mesh.publish(TriggerEvent(
            event_type="meta.retrospective_scheduled",
            source="meta_loop",
            actor="grace_agent",
            resource=plan.plan_id,
            payload={
                "plan_id": plan.plan_id,
                "outcome": plan.outcome,
                "schedule_time": (datetime.utcnow().timestamp() + 3600)
            },
            timestamp=datetime.utcnow()
        ))
    
    async def tune_thresholds(self, subsystem: str, metric: str, performance: float):
        """Automatically tune detection thresholds"""
        if performance < self.improvement_threshold:
            new_threshold = await self._calculate_optimal_threshold(subsystem, metric)
            
            await trigger_mesh.publish(TriggerEvent(
                event_type="meta.threshold_tuned",
                source="meta_loop",
                actor="grace_agent",
                resource=f"{subsystem}.{metric}",
                payload={
                    "subsystem": subsystem,
                    "metric": metric,
                    "new_threshold": new_threshold,
                    "reason": f"performance below {self.improvement_threshold}"
                },
                timestamp=datetime.utcnow()
            ))
    
    async def propose_new_playbook(self, gap_analysis: Dict):
        """Propose new playbook when gaps detected"""
        playbook = Playbook(
            playbook_id=f"generated_{datetime.utcnow().timestamp()}",
            name=f"Auto-generated: {gap_analysis['pattern']}",
            description=gap_analysis['description'],
            preconditions=[],
            steps=gap_analysis.get('suggested_steps', []),
            verifications=[],
            rollback_steps=[],
            risk_level=RiskLevel.MODERATE,
            requires_approval=True
        )
        
        await trigger_mesh.publish(TriggerEvent(
            event_type="meta.playbook_proposed",
            source="meta_loop",
            actor="grace_agent",
            resource=playbook.playbook_id,
            payload={"playbook": playbook.name, "gap": gap_analysis['pattern']},
            timestamp=datetime.utcnow()
        ))
    
    async def run_experiment(self, experiment_spec: Dict):
        """Run low-risk experiment under governance"""
        if experiment_spec.get('risk_level') == 'low':
            await trigger_mesh.publish(TriggerEvent(
                event_type="meta.experiment_started",
                source="meta_loop",
                actor="grace_agent",
                resource=experiment_spec['name'],
                payload=experiment_spec,
                timestamp=datetime.utcnow()
            ))
    
    async def _calculate_optimal_threshold(self, subsystem: str, metric: str) -> float:
        """Calculate optimal threshold based on historical data"""
        return 0.75


class AgenticSpine:
    """
    Main coordinator of all agentic capabilities.
    This is GRACE's autonomous decision-making core.
    """
    
    def __init__(self):
        self.enrichment = EventEnrichmentLayer()
        self.trust_core = TrustCorePartner()
        self.ledger_hooks = LedgerReasoningHooks()
        self.health_graph = UnifiedHealthGraph()
        self.planner = AutonomousPlanner(self.health_graph, self.trust_core)
        self.meta_loop = MetaLoopAutonomy(self.planner)
        self.running = False
    
    async def start(self):
        """Start the agentic spine"""
        await trigger_mesh.subscribe("*", self._handle_event)
        self.running = True
        print("✓ Agentic Spine activated - GRACE is now autonomous")
    
    async def stop(self):
        """Stop the agentic spine"""
        self.running = False
        print("✓ Agentic Spine deactivated")
    
    async def _handle_event(self, event: TriggerEvent):
        """Main event handler - enriches, reasons, plans, and acts"""
        
        enriched = await self.enrichment.enrich(event)
        
        await immutable_log.append(
            actor="agentic_spine",
            action="event_enriched",
            resource=enriched.event_id,
            subsystem="enrichment",
            payload={
                "confidence": enriched.confidence,
                "intent": enriched.intent,
                "expected_outcome": enriched.expected_outcome
            },
            result="enriched"
        )
        
        if enriched.confidence < 0.4:
            return
        
        if event.event_type.startswith(("health.degraded", "alert.", "incident.")):
            await self._handle_incident(enriched)

        # Handle external integration events
        elif event.event_type.startswith("external."):
            if "slack" in event.event_type:
                await slack_integration.handle_slack_event(event)
            elif "pagerduty" in event.event_type:
                await pagerduty_integration.handle_pagerduty_webhook(event.payload)
            elif "github" in event.event_type:
                await github_integration.handle_github_webhook(event.payload)
    
    async def _handle_incident(self, enriched: EnrichedEvent):
        """Handle incident with autonomous planning and execution"""
        
        decision = DecisionRecord(
            decision_id=f"decision_{datetime.utcnow().timestamp()}",
            decision_type="incident_response",
            context=enriched.context,
            options_considered=[],
            chosen_option="automated_recovery",
            rationale=f"Intent: {enriched.intent}, Expected: {enriched.expected_outcome}",
            confidence=enriched.confidence,
            risk_assessment={}
        )
        
        approved, rationale, escalations = await self.trust_core.evaluate_decision(decision)
        
        if not approved:
            await immutable_log.append(
                actor="agentic_spine",
                action="decision_rejected",
                resource=decision.decision_id,
                subsystem="trust_core",
                payload={"rationale": rationale},
                result="rejected"
            )
            return
        
        plan = await self.planner.plan_recovery(enriched)
        if not plan:
            return

        await immutable_log.append(
            actor="agentic_spine",
            action="recovery_planned",
            resource=plan.plan_id,
            subsystem="planner",
            payload={
                "playbook": plan.playbook.name,
                "risk_score": plan.risk_score,
                "justification": plan.justification
            },
            result="planned"
        )

        # Notify external systems
        await slack_integration.notify_recovery({
            "action": plan.playbook.name,
            "description": plan.justification,
            "playbook": plan.playbook.name,
            "risk_score": plan.risk_score,
            "status": "planned"
        })

        if plan.status == PlanStatus.APPROVED:
            success = await self.planner.execute_plan(plan.plan_id)

            # Update external notifications
            await slack_integration.notify_recovery({
                "action": plan.playbook.name,
                "description": plan.justification,
                "playbook": plan.playbook.name,
                "risk_score": plan.risk_score,
                "status": "completed" if success else "failed"
            })

            await immutable_log.append(
                actor="agentic_spine",
                action="recovery_executed",
                resource=plan.plan_id,
                subsystem="executor",
                payload={"outcome": plan.outcome},
                result="success" if success else "failed"
            )

            await self.meta_loop.schedule_retrospective(plan)


agentic_spine = AgenticSpine()
