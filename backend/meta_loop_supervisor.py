"""
Meta Loop Supervisor - Systemic oversight and governance layer

Sits atop the agentic spine, analyzing cross-domain performance and
issuing directives to optimize how the spine itself behaves. This is
the "supervisor watching the autonomous agent" - ensuring GRACE
continuously improves her own decision-making across all domains.
"""

import asyncio
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import json

from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log
from .unified_logger import unified_logger


class DirectiveType(Enum):
    ADJUST_THRESHOLD = "adjust_threshold"
    ENABLE_PLAYBOOK = "enable_playbook"
    DISABLE_PLAYBOOK = "disable_playbook"
    ADJUST_CONFIDENCE = "adjust_confidence"
    SCHEDULE_EXPERIMENT = "schedule_experiment"
    REQUEST_REVIEW = "request_review"
    ENABLE_PROBE = "enable_probe"
    ROLLBACK_CHANGE = "rollback_change"


class ChangeImpact(Enum):
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DomainSnapshot:
    """Snapshot of a single domain's state"""
    domain_id: str
    timestamp: datetime
    health_state: Dict[str, Any]
    kpis: Dict[str, float]
    active_playbooks: List[str]
    success_rates: Dict[str, float]
    drift_trends: Dict[str, float]
    trust_exceptions: List[Dict]
    recent_outcomes: List[Dict]
    baseline_comparison: Dict[str, float]


@dataclass
class CrossDomainSnapshot:
    """Unified snapshot across all domains"""
    snapshot_id: str
    timestamp: datetime
    domain_snapshots: Dict[str, DomainSnapshot]
    global_kpis: Dict[str, float]
    cross_domain_correlations: Dict[str, Any]
    strategic_goals: Dict[str, float]
    goal_gaps: Dict[str, float]
    systemic_patterns: List[Dict]
    focus_recommendation: str = "routine_maintenance"
    guardrails_recommendation: str = "maintain"
    ml_root_causes: List[str] = None


@dataclass
class MetaDirective:
    """Directive from meta loop to spine"""
    directive_id: str
    directive_type: DirectiveType
    target_domain: str
    target_subsystem: str
    action: str
    parameters: Dict[str, Any]
    justification: str
    expected_impact: str
    change_impact: ChangeImpact
    requires_approval: bool
    created_at: datetime = field(default_factory=datetime.utcnow)
    approved: bool = False
    executed: bool = False
    verified: bool = False
    outcome: Optional[str] = None


@dataclass
class MetaPolicy:
    """Policy for meta-loop decision making"""
    policy_id: str
    name: str
    description: str
    condition: Dict[str, Any]
    directive_template: Dict[str, Any]
    confidence_threshold: float = 0.7
    human_approval_threshold: ChangeImpact = ChangeImpact.MODERATE
    enabled: bool = True


@dataclass
class MetaDecision:
    """Record of meta loop decision"""
    decision_id: str
    snapshot_id: str
    policy_id: Optional[str]
    analysis: Dict[str, Any]
    directives_issued: List[str]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    outcome: Optional[Dict] = None


class SnapshotBuilder:
    """Builds unified cross-domain snapshots"""
    
    def __init__(self):
        self.domain_data: Dict[str, List[Dict]] = defaultdict(list)
        self.baselines: Dict[str, Dict[str, float]] = {}
        self.strategic_goals: Dict[str, float] = {
            "overall_success_rate": 0.95,
            "mean_recovery_time_seconds": 30,
            "autonomy_rate": 0.80,
            "compliance_score": 95.0,
            "human_intervention_rate": 0.15
        }
    
    async def build_snapshot(self) -> CrossDomainSnapshot:
        """Build unified cross-domain snapshot"""
        
        domain_snapshots = {}
        
        for domain_id in await self._get_active_domains():
            domain_snapshots[domain_id] = await self._build_domain_snapshot(domain_id)
        
        global_kpis = await self._aggregate_global_kpis(domain_snapshots)
        correlations = await self._find_cross_domain_correlations(domain_snapshots)
        goal_gaps = await self._calculate_goal_gaps(global_kpis)
        patterns = await self._detect_systemic_patterns(domain_snapshots)
        
        snapshot = CrossDomainSnapshot(
            snapshot_id=f"snapshot_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            domain_snapshots=domain_snapshots,
            global_kpis=global_kpis,
            cross_domain_correlations=correlations,
            strategic_goals=self.strategic_goals,
            goal_gaps=goal_gaps,
            systemic_patterns=patterns
        )
        
        await self._store_snapshot(snapshot)
        return snapshot
    
    async def _get_active_domains(self) -> List[str]:
        """Get list of active domains"""
        from .agent_core import agent_core
        
        # Return actual registered domains
        return list(agent_core.domains.keys()) if agent_core.domains else ["core"]
    
    async def _build_domain_snapshot(self, domain_id: str) -> DomainSnapshot:
        """Build snapshot for a single domain"""
        
        from .agent_core import agent_core
        
        # Get metrics from domain adapter if registered
        if domain_id in agent_core.domains:
            domain_metrics = await agent_core.domains[domain_id].collect_metrics()
            kpis = {
                "health_score": domain_metrics.health_score,
                "active_tasks": float(domain_metrics.active_tasks),
                "success_rate": (
                    domain_metrics.completed_tasks_24h / 
                    (domain_metrics.completed_tasks_24h + domain_metrics.failed_tasks_24h)
                ) if (domain_metrics.completed_tasks_24h + domain_metrics.failed_tasks_24h) > 0 else 1.0,
                "error_rate": domain_metrics.error_rate,
                **domain_metrics.custom_metrics
            }
        else:
            kpis = await self._get_domain_kpis(domain_id)
        
        health_state = await self._get_health_state(domain_id)
        playbooks = await self._get_active_playbooks(domain_id)
        success_rates = await self._get_success_rates(domain_id)
        drift = await self._calculate_drift_trends(domain_id, kpis)
        exceptions = await self._get_trust_exceptions(domain_id)
        outcomes = await self._get_recent_outcomes(domain_id)
        baseline_comp = await self._compare_to_baseline(domain_id, kpis)
        
        return DomainSnapshot(
            domain_id=domain_id,
            timestamp=datetime.utcnow(),
            health_state=health_state,
            kpis=kpis,
            active_playbooks=playbooks,
            success_rates=success_rates,
            drift_trends=drift,
            trust_exceptions=exceptions,
            recent_outcomes=outcomes,
            baseline_comparison=baseline_comp
        )
    
    async def _get_health_state(self, domain_id: str) -> Dict:
        """Get health state from health graph"""
        return {"status": "operational", "degraded_nodes": []}
    
    async def _get_domain_kpis(self, domain_id: str) -> Dict[str, float]:
        """Get KPIs for domain"""
        return {
            "recovery_latency_p95": 25.0,
            "success_rate": 0.92,
            "autonomy_rate": 0.75,
            "alert_volume": 45.0
        }
    
    async def _get_active_playbooks(self, domain_id: str) -> List[str]:
        """Get active playbooks"""
        return []
    
    async def _get_success_rates(self, domain_id: str) -> Dict[str, float]:
        """Get playbook success rates"""
        return {}
    
    async def _calculate_drift_trends(self, domain_id: str, kpis: Dict) -> Dict[str, float]:
        """Calculate drift from baseline"""
        baseline = self.baselines.get(domain_id, {})
        drift = {}
        
        for key, value in kpis.items():
            if key in baseline:
                drift[key] = (value - baseline[key]) / baseline[key] if baseline[key] != 0 else 0.0
        
        return drift
    
    async def _get_trust_exceptions(self, domain_id: str) -> List[Dict]:
        """Get trust core exceptions"""
        return []
    
    async def _get_recent_outcomes(self, domain_id: str) -> List[Dict]:
        """Get recent decision outcomes"""
        return []
    
    async def _compare_to_baseline(self, domain_id: str, kpis: Dict) -> Dict[str, float]:
        """Compare current to baseline"""
        baseline = self.baselines.get(domain_id, {})
        comparison = {}
        
        for key, value in kpis.items():
            if key in baseline:
                comparison[key] = ((value - baseline[key]) / baseline[key]) * 100 if baseline[key] != 0 else 0.0
        
        return comparison
    
    async def _aggregate_global_kpis(self, snapshots: Dict[str, DomainSnapshot]) -> Dict[str, float]:
        """Aggregate KPIs across all domains"""
        
        global_kpis = {
            "overall_success_rate": 0.0,
            "mean_recovery_time_seconds": 0.0,
            "autonomy_rate": 0.0,
            "total_interventions": 0.0
        }
        
        if not snapshots:
            return global_kpis
        
        success_rates = [s.kpis.get("success_rate", 0.0) for s in snapshots.values()]
        global_kpis["overall_success_rate"] = sum(success_rates) / len(success_rates)
        
        recovery_times = [s.kpis.get("recovery_latency_p95", 0.0) for s in snapshots.values()]
        global_kpis["mean_recovery_time_seconds"] = sum(recovery_times) / len(recovery_times)
        
        autonomy_rates = [s.kpis.get("autonomy_rate", 0.0) for s in snapshots.values()]
        global_kpis["autonomy_rate"] = sum(autonomy_rates) / len(autonomy_rates)
        
        return global_kpis
    
    async def _find_cross_domain_correlations(self, snapshots: Dict[str, DomainSnapshot]) -> Dict:
        """Find correlations between domains"""
        return {}
    
    async def _calculate_goal_gaps(self, global_kpis: Dict[str, float]) -> Dict[str, float]:
        """Calculate gaps between current and strategic goals"""
        gaps = {}
        
        for goal, target in self.strategic_goals.items():
            current = global_kpis.get(goal, 0.0)
            gaps[goal] = target - current
        
        return gaps
    
    async def _detect_systemic_patterns(self, snapshots: Dict[str, DomainSnapshot]) -> List[Dict]:
        """Detect systemic patterns across domains"""
        patterns = []
        
        high_drift_domains = [
            s.domain_id for s in snapshots.values()
            if any(abs(d) > 0.2 for d in s.drift_trends.values())
        ]
        
        if len(high_drift_domains) >= 2:
            patterns.append({
                "pattern": "multi_domain_drift",
                "domains": high_drift_domains,
                "severity": "moderate"
            })
        
        return patterns
    
    async def _store_snapshot(self, snapshot: CrossDomainSnapshot):
        """Store snapshot for historical analysis"""
        await immutable_log.append(
            actor="meta_loop_supervisor",
            action="snapshot_created",
            resource=snapshot.snapshot_id,
            subsystem="snapshot_builder",
            payload={
                "domains": list(snapshot.domain_snapshots.keys()),
                "global_kpis": snapshot.global_kpis,
                "goal_gaps": snapshot.goal_gaps
            },
            result="stored"
        )


class StrategyEngine:
    """Analyzes snapshots and produces directives"""
    
    def __init__(self):
        self.policies: Dict[str, MetaPolicy] = {}
        self.decisions: List[MetaDecision] = []
    
    async def register_policy(self, policy: MetaPolicy):
        """Register a meta policy"""
        self.policies[policy.policy_id] = policy
    
    async def analyze_and_decide(self, snapshot: CrossDomainSnapshot) -> List[MetaDirective]:
        """Analyze snapshot and produce directives"""
        
        directives = []
        analysis = await self._analyze_snapshot(snapshot)
        
        for policy_id, policy in self.policies.items():
            if not policy.enabled:
                continue
            
            if await self._policy_matches(policy, snapshot, analysis):
                directive = await self._create_directive_from_policy(policy, snapshot, analysis)
                directives.append(directive)
        
        decision = MetaDecision(
            decision_id=f"decision_{datetime.utcnow().timestamp()}",
            snapshot_id=snapshot.snapshot_id,
            policy_id=None,
            analysis=analysis,
            directives_issued=[d.directive_id for d in directives],
            confidence=await self._calculate_decision_confidence(snapshot, directives)
        )
        
        self.decisions.append(decision)
        
        await immutable_log.append(
            actor="meta_loop_supervisor",
            action="meta_decision",
            resource=decision.decision_id,
            subsystem="strategy_engine",
            payload={
                "snapshot_id": snapshot.snapshot_id,
                "directives_count": len(directives),
                "confidence": decision.confidence
            },
            result="decided"
        )
        
        return directives
    
    async def _analyze_snapshot(self, snapshot: CrossDomainSnapshot) -> Dict[str, Any]:
        """Analyze snapshot for issues and opportunities"""
        
        analysis = {
            "goal_gaps": snapshot.goal_gaps,
            "systemic_patterns": snapshot.systemic_patterns,
            "underperforming_domains": [],
            "overperforming_domains": [],
            "recommendations": []
        }
        
        for domain_id, domain_snap in snapshot.domain_snapshots.items():
            success_rate = domain_snap.kpis.get("success_rate", 0.0)
            
            if success_rate < 0.85:
                analysis["underperforming_domains"].append({
                    "domain": domain_id,
                    "success_rate": success_rate,
                    "issue": "below_target"
                })
            elif success_rate > 0.95:
                analysis["overperforming_domains"].append({
                    "domain": domain_id,
                    "success_rate": success_rate
                })
        
        if snapshot.goal_gaps.get("overall_success_rate", 0) > 0.05:
            analysis["recommendations"].append({
                "action": "tighten_playbook_criteria",
                "reason": "success_rate_below_target"
            })
        
        return analysis
    
    async def _policy_matches(
        self,
        policy: MetaPolicy,
        snapshot: CrossDomainSnapshot,
        analysis: Dict
    ) -> bool:
        """Check if policy conditions are met"""
        
        condition = policy.condition
        
        if "goal_gap_threshold" in condition:
            gap_metric = condition["goal_gap_metric"]
            threshold = condition["goal_gap_threshold"]
            
            actual_gap = snapshot.goal_gaps.get(gap_metric, 0.0)
            if actual_gap < threshold:
                return False
        
        if "min_underperforming_domains" in condition:
            min_domains = condition["min_underperforming_domains"]
            if len(analysis["underperforming_domains"]) < min_domains:
                return False
        
        return True
    
    async def _create_directive_from_policy(
        self,
        policy: MetaPolicy,
        snapshot: CrossDomainSnapshot,
        analysis: Dict
    ) -> MetaDirective:
        """Create directive from policy template"""
        
        template = policy.directive_template
        
        directive = MetaDirective(
            directive_id=f"directive_{datetime.utcnow().timestamp()}",
            directive_type=DirectiveType[template["type"]],
            target_domain=template.get("target_domain", "all"),
            target_subsystem=template.get("target_subsystem", "planner"),
            action=template["action"],
            parameters=template.get("parameters", {}),
            justification=f"{policy.description} - triggered by {policy.condition}",
            expected_impact=template.get("expected_impact", "improve performance"),
            change_impact=ChangeImpact[template.get("impact_level", "LOW")],
            requires_approval=policy.human_approval_threshold.value <= template.get("impact_level", "LOW")
        )
        
        return directive
    
    async def _calculate_decision_confidence(
        self,
        snapshot: CrossDomainSnapshot,
        directives: List[MetaDirective]
    ) -> float:
        """Calculate confidence in meta decision"""
        
        if not directives:
            return 1.0
        
        data_completeness = len(snapshot.domain_snapshots) / 4.0
        pattern_clarity = 1.0 if snapshot.systemic_patterns else 0.7
        
        return min(data_completeness * pattern_clarity, 0.95)


class DirectivePipeline:
    """Routes directives back into spine for execution"""
    
    def __init__(self):
        self.pending_directives: Dict[str, MetaDirective] = {}
        self.executed_directives: List[MetaDirective] = []
    
    async def submit_directive(self, directive: MetaDirective):
        """Submit directive for execution"""
        
        self.pending_directives[directive.directive_id] = directive
        
        if directive.requires_approval:
            await self._request_approval(directive)
        else:
            await self._execute_directive(directive)
    
    async def _request_approval(self, directive: MetaDirective):
        """Request human approval for high-impact directive"""
        
        await trigger_mesh.publish(TriggerEvent(
            event_type="meta.directive_approval_required",
            source="meta_loop_supervisor",
            actor="meta_loop_supervisor",
            resource=directive.directive_id,
            payload={
                "directive_type": directive.directive_type.value,
                "target_domain": directive.target_domain,
                "action": directive.action,
                "justification": directive.justification,
                "impact": directive.change_impact.value
            },
            timestamp=datetime.utcnow()
        ))
    
    async def approve_directive(self, directive_id: str, approved_by: str):
        """Approve pending directive"""
        
        if directive_id in self.pending_directives:
            directive = self.pending_directives[directive_id]
            directive.approved = True
            
            await immutable_log.append(
                actor=approved_by,
                action="meta_directive_approved",
                resource=directive_id,
                subsystem="directive_pipeline",
                payload={
                    "directive_type": directive.directive_type.value,
                    "target": directive.target_domain
                },
                result="approved"
            )
            
            await self._execute_directive(directive)
    
    async def _execute_directive(self, directive: MetaDirective):
        """Execute approved directive"""
        
        await trigger_mesh.publish(TriggerEvent(
            event_type=f"meta.directive.{directive.directive_type.value}",
            source="meta_loop_supervisor",
            actor="meta_loop_supervisor",
            resource=directive.directive_id,
            payload={
                "target_domain": directive.target_domain,
                "target_subsystem": directive.target_subsystem,
                "action": directive.action,
                "parameters": directive.parameters
            },
            timestamp=datetime.utcnow()
        ))
        
        directive.executed = True
        self.executed_directives.append(directive)
        
        if directive.directive_id in self.pending_directives:
            del self.pending_directives[directive.directive_id]
        
        await immutable_log.append(
            actor="meta_loop_supervisor",
            action="directive_executed",
            resource=directive.directive_id,
            subsystem="directive_pipeline",
            payload={
                "directive_type": directive.directive_type.value,
                "parameters": directive.parameters
            },
            result="executed"
        )


class VerificationLayer:
    """Verifies meta directives achieved expected outcomes"""
    
    def __init__(self, snapshot_builder: SnapshotBuilder):
        self.snapshot_builder = snapshot_builder
        self.verification_results: List[Dict] = []
    
    async def verify_directive(
        self,
        directive: MetaDirective,
        pre_snapshot: CrossDomainSnapshot
    ) -> bool:
        """Verify directive achieved expected outcome"""
        
        await asyncio.sleep(60)
        
        post_snapshot = await self.snapshot_builder.build_snapshot()
        
        success = await self._compare_snapshots(directive, pre_snapshot, post_snapshot)
        
        directive.verified = True
        directive.outcome = "success" if success else "failed"
        
        result = {
            "directive_id": directive.directive_id,
            "success": success,
            "pre_kpis": pre_snapshot.global_kpis,
            "post_kpis": post_snapshot.global_kpis,
            "timestamp": datetime.utcnow()
        }
        
        self.verification_results.append(result)
        
        await immutable_log.append(
            actor="meta_loop_supervisor",
            action="directive_verified",
            resource=directive.directive_id,
            subsystem="verification_layer",
            payload=result,
            result="success" if success else "failed"
        )
        
        if not success:
            await self._rollback_directive(directive)
        
        return success
    
    async def _compare_snapshots(
        self,
        directive: MetaDirective,
        pre: CrossDomainSnapshot,
        post: CrossDomainSnapshot
    ) -> bool:
        """Compare pre/post snapshots to verify improvement"""
        
        if directive.directive_type == DirectiveType.ADJUST_THRESHOLD:
            target_metric = directive.parameters.get("metric")
            if target_metric in post.global_kpis and target_metric in pre.global_kpis:
                return post.global_kpis[target_metric] > pre.global_kpis[target_metric]
        
        overall_success_pre = pre.global_kpis.get("overall_success_rate", 0.0)
        overall_success_post = post.global_kpis.get("overall_success_rate", 0.0)
        
        return overall_success_post >= overall_success_pre * 0.95
    
    async def _rollback_directive(self, directive: MetaDirective):
        """Rollback failed directive"""
        
        await trigger_mesh.publish(TriggerEvent(
            event_type="meta.directive_rollback",
            source="meta_loop_supervisor",
            actor="meta_loop_supervisor",
            resource=directive.directive_id,
            payload={
                "directive_type": directive.directive_type.value,
                "reason": "verification_failed"
            },
            timestamp=datetime.utcnow()
        ))


class MetaLoopSupervisor:
    """
    Main meta loop supervisor coordinating cross-domain oversight.
    
    This is the "supervisor watching the autonomous agent" - it analyzes
    how GRACE performs across all domains and adjusts her behavior to
    optimize for strategic goals while maintaining governance.
    """
    
    def __init__(self):
        self.snapshot_builder = SnapshotBuilder()
        self.strategy_engine = StrategyEngine()
        self.directive_pipeline = DirectivePipeline()
        self.verification_layer = VerificationLayer(self.snapshot_builder)
        self.running = False
        self.cycle_interval_seconds = 300
    
    async def start(self):
        """Start meta loop supervisor"""
        
        await self._register_default_policies()
        
        trigger_mesh.subscribe("meta.*", self._handle_meta_event)
        
        self.running = True
        asyncio.create_task(self._supervisor_loop())
        
        print("[OK] Meta Loop Supervisor started - Watching spine behavior")
    
    async def stop(self):
        """Stop meta loop supervisor"""
        self.running = False
    
    async def _register_default_policies(self):
        """Register default meta policies"""
        
        success_rate_policy = MetaPolicy(
            policy_id="improve_success_rate",
            name="Improve Success Rate",
            description="Tighten playbook criteria when success rate below target",
            condition={
                "goal_gap_metric": "overall_success_rate",
                "goal_gap_threshold": 0.05
            },
            directive_template={
                "type": "ADJUST_THRESHOLD",
                "target_domain": "all",
                "target_subsystem": "planner",
                "action": "increase_playbook_confidence_threshold",
                "parameters": {"adjustment": 0.05},
                "impact_level": "LOW",
                "expected_impact": "increase_success_rate"
            },
            confidence_threshold=0.75
        )
        await self.strategy_engine.register_policy(success_rate_policy)
        
        recovery_latency_policy = MetaPolicy(
            policy_id="reduce_recovery_latency",
            name="Reduce Recovery Latency",
            description="Enable faster playbooks when latency exceeds target",
            condition={
                "goal_gap_metric": "mean_recovery_time_seconds",
                "goal_gap_threshold": -10.0
            },
            directive_template={
                "type": "ENABLE_PLAYBOOK",
                "target_domain": "all",
                "target_subsystem": "planner",
                "action": "enable_fast_recovery_playbooks",
                "parameters": {},
                "impact_level": "MODERATE",
                "expected_impact": "reduce_recovery_time"
            },
            confidence_threshold=0.70,
            human_approval_threshold=ChangeImpact.MODERATE
        )
        await self.strategy_engine.register_policy(recovery_latency_policy)
    
    async def _supervisor_loop(self):
        """Main supervisory cycle"""
        
        cycle_number = 0
        
        while self.running:
            try:
                cycle_number += 1
                cycle_start = datetime.utcnow()
                
                print(f"\n[Meta Loop] Starting supervisory cycle at {cycle_start.strftime('%H:%M:%S')}")
                
                snapshot = await self.snapshot_builder.build_snapshot()
                print(f"  -> Built cross-domain snapshot: {len(snapshot.domain_snapshots)} domains")
                
                directives = await self.strategy_engine.analyze_and_decide(snapshot)
                print(f"  -> Strategy engine issued {len(directives)} directives")
                
                directives_executed = 0
                directives_successful = 0
                
                for directive in directives:
                    await self.directive_pipeline.submit_directive(directive)
                    print(f"    * {directive.directive_type.value}: {directive.justification}")
                    
                    if directive.executed:
                        directives_executed += 1
                        if not directive.requires_approval:
                            directives_successful += 1
                            asyncio.create_task(
                                self.verification_layer.verify_directive(directive, snapshot)
                            )
                
                cycle_end = datetime.utcnow()
                duration = (cycle_end - cycle_start).total_seconds()
                
                # Log to unified logger
                await unified_logger.log_meta_loop_cycle(
                    cycle_number=cycle_number,
                    focus_area=snapshot.focus_recommendation,
                    guardrails_mode=snapshot.guardrails_recommendation,
                    ml_root_causes=snapshot.ml_root_causes,
                    directives_issued=[d.directive_type.value for d in directives],
                    directives_executed=directives_executed,
                    directives_successful=directives_successful,
                    duration=duration,
                    domains_analyzed=len(snapshot.domain_snapshots),
                    outcome='success',
                    completed_at=cycle_end
                )
                
                await self._publish_summary(snapshot, directives)
                
            except Exception as e:
                print(f"[FAIL] Meta loop cycle error: {e}")
            
            await asyncio.sleep(self.cycle_interval_seconds)
    
    async def _handle_meta_event(self, event: TriggerEvent):
        """Handle meta-related events"""
        
        if event.event_type == "meta.directive_approval_required":
            pass
        elif event.event_type == "meta.directive_rollback":
            pass
    
    async def _publish_summary(
        self,
        snapshot: CrossDomainSnapshot,
        directives: List[MetaDirective]
    ):
        """Publish summary to human collaboration channels"""
        
        await trigger_mesh.publish(TriggerEvent(
            event_type="meta.cycle_complete",
            source="meta_loop_supervisor",
            actor="meta_loop_supervisor",
            resource=snapshot.snapshot_id,
            payload={
                "global_kpis": snapshot.global_kpis,
                "goal_gaps": snapshot.goal_gaps,
                "directives_issued": len(directives),
                "systemic_patterns": len(snapshot.systemic_patterns)
            },
            timestamp=datetime.utcnow()
        ))


meta_loop_supervisor = MetaLoopSupervisor()
