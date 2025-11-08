"""
Meta-Coordinated Self-Healing Architecture

PROPER HIERARCHY:
1. Meta Loop -> Decides WHEN and WHAT to focus on
2. ML/DL Models -> Embedded advisors (scoring, ranking, root-cause)
3. Agentic Layer -> Execution engine (planner + trust + verification)
4. Immutable Log -> Single source of truth (signed, auditable)

Flow:
  Meta Loop observes system -> Decides "focus on latency drift this cycle"
  -> ML/DL scores anomalies, suggests root causes, ranks playbooks
  -> Meta Loop issues directive to agentic planner
  -> Agentic layer: plan -> trust check -> execute -> verify
  -> Results signed to immutable log
  -> Meta loop learns from outcome, adjusts next cycle
"""

from __future__ import annotations
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

from ..trigger_mesh import trigger_mesh, TriggerEvent
from ..immutable_log import immutable_log


class FocusArea(Enum):
    """What the meta loop decides to focus on this cycle"""
    LATENCY_DRIFT = "latency_drift"
    ERROR_SPIKE = "error_spike"
    CAPACITY_STRAIN = "capacity_strain"
    DEPENDENCY_HEALTH = "dependency_health"
    TRUST_VIOLATIONS = "trust_violations"
    ROUTINE_MAINTENANCE = "routine_maintenance"


class GuardrailAdjustment(Enum):
    """How meta loop adjusts guardrails"""
    TIGHTEN = "tighten"  # More conservative approvals
    LOOSEN = "loosen"    # Allow more autonomy
    MAINTAIN = "maintain"


@dataclass
class CycleFocus:
    """Meta loop's decision about this healing cycle"""
    cycle_id: str
    focus_area: FocusArea
    reasoning: List[str]
    confidence: float
    guardrail_adjustment: GuardrailAdjustment
    extra_probes: List[str]  # Additional monitoring to enable
    playbook_priorities: List[str]  # Preferred playbooks this cycle
    time_budget_seconds: int
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MLAdvice:
    """ML/DL model recommendations (embedded, not autonomous)"""
    advice_id: str
    model_type: str  # "anomaly_scorer", "root_cause", "playbook_ranker"
    focus_area: FocusArea
    recommendations: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    root_cause_candidates: List[str]
    ranked_playbooks: List[Tuple[str, float]]  # (playbook_id, score)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgenticPlan:
    """Plan from agentic layer (planner output)"""
    plan_id: str
    service: str
    diagnosis: Dict[str, Any]
    selected_playbook: str
    steps: List[Dict]
    verifications: List[Dict]
    rollback_plan: List[Dict]
    trust_approval_required: bool
    estimated_duration: int
    risk_assessment: Dict[str, Any]


@dataclass
class SignedOutcome:
    """Signed execution outcome for immutable log"""
    outcome_id: str
    cycle_id: str
    plan_id: str
    service: str
    playbook: str
    result: str  # "success", "failed", "rolled_back"
    duration_seconds: float
    verification_passed: bool
    trust_decision: str
    actor_signature: str
    rationale: List[str]
    learned_insights: List[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MetaCoordinatedHealing:
    """
    Meta loop-coordinated self-healing.
    
    The meta loop is the orchestrator that:
    - Observes cross-system performance each cycle
    - Decides what to focus on (latency, errors, capacity, etc.)
    - Adjusts guardrails (tighten/loosen autonomy)
    - Requests ML/DL advice
    - Issues directives to agentic planner
    - Records signed outcomes to immutable log
    - Learns and adjusts for next cycle
    """
    
    def __init__(self):
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self.current_cycle: Optional[CycleFocus] = None
        self.cycle_history: List[CycleFocus] = []
        self.outcome_history: List[SignedOutcome] = []
        self.guardrail_state = GuardrailAdjustment.MAINTAIN
        
        # ML/DL advisors (embedded)
        self.ml_advisors = {
            "anomaly_scorer": self._ml_anomaly_advisor,
            "root_cause": self._ml_root_cause_advisor,
            "playbook_ranker": self._ml_playbook_advisor
        }
    
    async def start(self):
        """Start meta-coordinated healing cycles"""
        if self.running:
            return
        
        self.running = True
        self._task = asyncio.create_task(self._coordination_loop())
        
        await immutable_log.append(
            actor="meta_coordinator",
            action="healing_coordination_started",
            resource="self_heal",
            subsystem="meta_coordinated_healing",
            payload={"mode": "meta_orchestrated"},
            result="started",
            signature=await self._sign_action("coordination_started")
        )
        
        print("  [OK] Meta-coordinated healing started")
    
    async def stop(self):
        """Stop coordination"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        await immutable_log.append(
            actor="meta_coordinator",
            action="healing_coordination_stopped",
            resource="self_heal",
            subsystem="meta_coordinated_healing",
            payload={
                "total_cycles": len(self.cycle_history),
                "total_outcomes": len(self.outcome_history)
            },
            result="stopped",
            signature=await self._sign_action("coordination_stopped")
        )
        
        print("  [OK] Meta-coordinated healing stopped")
    
    async def _coordination_loop(self):
        """
        Main coordination loop (runs every 2 minutes).
        
        Each cycle:
        1. Meta loop observes system state
        2. Decides focus area and guardrail adjustments
        3. Requests ML/DL advice
        4. Issues directive to agentic planner
        5. Monitors execution
        6. Records signed outcome
        7. Learns and adjusts
        """
        cycle_count = 0
        
        try:
            while self.running:
                cycle_count += 1
                cycle_id = f"cycle_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{cycle_count}"
                
                try:
                    print(f"\n[META] Meta Loop Cycle {cycle_count} - {datetime.now(timezone.utc).strftime('%H:%M:%S')}")
                    
                    # STEP 1: Meta loop observes and decides
                    focus = await self._meta_decide_focus(cycle_id)
                    self.current_cycle = focus
                    self.cycle_history.append(focus)
                    
                    print(f"  [FOCUS] Focus: {focus.focus_area.value}")
                    print(f"  [GUARD] Guardrails: {focus.guardrail_adjustment.value}")
                    
                    # Sign decision to immutable log
                    await immutable_log.append(
                        actor="meta_loop",
                        action="cycle_focus_decided",
                        resource="self_heal",
                        subsystem="meta_coordinated_healing",
                        payload={
                            "cycle_id": cycle_id,
                            "focus_area": focus.focus_area.value,
                            "reasoning": focus.reasoning,
                            "confidence": focus.confidence,
                            "guardrail_adjustment": focus.guardrail_adjustment.value,
                            "extra_probes": focus.extra_probes
                        },
                        result="decided",
                        signature=await self._sign_action(f"focus_{cycle_id}")
                    )
                    
                    # STEP 2: Enable extra probes if requested
                    if focus.extra_probes:
                        await self._enable_probes(focus.extra_probes)
                    
                    # STEP 3: Request ML/DL advice (embedded models)
                    ml_advice = await self._request_ml_advice(focus)
                    
                    print(f"  [AI] ML Root Causes: {ml_advice.root_cause_candidates[:2]}")
                    print(f"  [STATS] Top Playbook: {ml_advice.ranked_playbooks[0] if ml_advice.ranked_playbooks else 'none'}")
                    
                    # STEP 4: Issue directive to agentic planner
                    if ml_advice.recommendations:
                        directive_issued = await self._issue_agentic_directive(focus, ml_advice)
                        
                        if directive_issued:
                            print(f"  ✅ Directive issued to agentic planner")
                    
                    # STEP 5: Learn from recent outcomes
                    await self._learn_from_outcomes()
                
                except Exception as e:
                    print(f"  [WARN] Cycle error: {e}")
                    await immutable_log.append(
                        actor="meta_coordinator",
                        action="cycle_error",
                        resource="self_heal",
                        subsystem="meta_coordinated_healing",
                        payload={"cycle_id": cycle_id, "error": str(e)},
                        result="error",
                        signature=await self._sign_action(f"error_{cycle_id}")
                    )
                
                # Run cycle every 2 minutes
                await asyncio.sleep(120)
        
        except asyncio.CancelledError:
            pass
    
    async def _meta_decide_focus(self, cycle_id: str) -> CycleFocus:
        """
        Meta loop decides what to focus on this cycle.
        
        Observes:
        - Recent immutable log entries
        - System metrics trends
        - Previous cycle outcomes
        - Current guardrail effectiveness
        """
        try:
            from ..models import async_session
            from sqlalchemy import select, func
            from ..base_models import ImmutableLogEntry as ImmutableEntry
            
            # Analyze recent system behavior (last 5 minutes)
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=5)
            
            async with async_session() as session:
                # Get recent events
                result = await session.execute(
                    select(ImmutableEntry)
                    .where(ImmutableEntry.timestamp >= cutoff)
                    .order_by(ImmutableEntry.timestamp.desc())
                    .limit(200)
                )
                recent_events = result.scalars().all()
                
                # Count error types
                error_count = sum(1 for e in recent_events if e.result in ["error", "failed"])
                trust_violations = sum(1 for e in recent_events if "blocked" in e.result)
                
                # Determine focus area
                if error_count > 10:
                    focus_area = FocusArea.ERROR_SPIKE
                    reasoning = [f"{error_count} errors in last 5min", "High error rate detected"]
                    guardrail = GuardrailAdjustment.MAINTAIN
                    extra_probes = ["error_tracking", "stack_traces"]
                    playbook_priorities = ["rollback_flag", "restart_service"]
                    
                elif trust_violations > 5:
                    focus_area = FocusArea.TRUST_VIOLATIONS
                    reasoning = [f"{trust_violations} blocked actions", "Tighten guardrails"]
                    guardrail = GuardrailAdjustment.TIGHTEN
                    extra_probes = ["governance_audit"]
                    playbook_priorities = ["increase_logging"]
                    
                else:
                    # Check for latency drift from health signals
                    try:
                        from ..health_models import HealthSignal
                        signals = await session.execute(
                            select(HealthSignal)
                            .where(HealthSignal.metric_key == "latency_ms")
                            .where(HealthSignal.created_at >= cutoff)
                            .order_by(HealthSignal.created_at.desc())
                            .limit(20)
                        )
                        latency_signals = signals.scalars().all()
                        
                        if latency_signals and len(latency_signals) >= 5:
                            recent_latencies = [float(s.value) for s in latency_signals[:5] if s.value]
                            older_latencies = [float(s.value) for s in latency_signals[-5:] if s.value]
                            
                            if recent_latencies and older_latencies:
                                recent_avg = sum(recent_latencies) / len(recent_latencies)
                                older_avg = sum(older_latencies) / len(older_latencies)
                                
                                if recent_avg > older_avg * 1.3:
                                    focus_area = FocusArea.LATENCY_DRIFT
                                    reasoning = [f"Latency drift: {older_avg:.0f}ms -> {recent_avg:.0f}ms"]
                                    guardrail = GuardrailAdjustment.LOOSEN  # Allow proactive scaling
                                    extra_probes = ["latency_histograms"]
                                    playbook_priorities = ["scale_up_instances", "warm_cache"]
                                else:
                                    focus_area = FocusArea.ROUTINE_MAINTENANCE
                                    reasoning = ["System stable", "Routine checks"]
                                    guardrail = GuardrailAdjustment.MAINTAIN
                                    extra_probes = []
                                    playbook_priorities = ["increase_logging"]
                        else:
                            focus_area = FocusArea.ROUTINE_MAINTENANCE
                            reasoning = ["System stable", "Routine checks"]
                            guardrail = GuardrailAdjustment.MAINTAIN
                            extra_probes = []
                            playbook_priorities = ["increase_logging"]
                    
                    except Exception:
                        focus_area = FocusArea.ROUTINE_MAINTENANCE
                        reasoning = ["Default focus"]
                        guardrail = GuardrailAdjustment.MAINTAIN
                        extra_probes = []
                        playbook_priorities = []
                
                # Update guardrail state
                self.guardrail_state = guardrail
                
                return CycleFocus(
                    cycle_id=cycle_id,
                    focus_area=focus_area,
                    reasoning=reasoning,
                    confidence=0.85 if len(reasoning) > 1 else 0.70,
                    guardrail_adjustment=guardrail,
                    extra_probes=extra_probes,
                    playbook_priorities=playbook_priorities,
                    time_budget_seconds=120
                )
        
        except Exception as e:
            # Default safe focus
            return CycleFocus(
                cycle_id=cycle_id,
                focus_area=FocusArea.ROUTINE_MAINTENANCE,
                reasoning=[f"Error in decision: {str(e)}"],
                confidence=0.5,
                guardrail_adjustment=GuardrailAdjustment.MAINTAIN,
                extra_probes=[],
                playbook_priorities=[],
                time_budget_seconds=120
            )
    
    async def _enable_probes(self, probes: List[str]):
        """Enable additional monitoring probes"""
        for probe in probes:
            await trigger_mesh.publish(TriggerEvent(
                event_type="monitoring.enable_probe",
                source="meta_coordinator",
                actor="meta_loop",
                resource=probe,
                payload={"probe_type": probe, "duration_seconds": 300},
                timestamp=datetime.now(timezone.utc)
            ))
    
    async def _request_ml_advice(self, focus: CycleFocus) -> MLAdvice:
        """
        Request advice from embedded ML/DL models.
        
        Models are advisors, not autonomous actors.
        They score, rank, and suggest - meta loop decides.
        """
        advice_id = f"advice_{focus.cycle_id}"
        
        # Aggregate recommendations from all ML advisors
        all_recommendations = []
        confidence_scores = {}
        root_causes = []
        ranked_playbooks = []
        
        for model_name, advisor_func in self.ml_advisors.items():
            try:
                advice = await advisor_func(focus)
                all_recommendations.extend(advice.get("recommendations", []))
                confidence_scores[model_name] = advice.get("confidence", 0.0)
                root_causes.extend(advice.get("root_causes", []))
                
                # Merge playbook rankings
                for playbook, score in advice.get("playbook_rankings", []):
                    ranked_playbooks.append((playbook, score))
            except Exception as e:
                print(f"    Warning: ML advisor {model_name} error: {e}")
        
        # Deduplicate and sort
        root_causes = list(set(root_causes))[:5]
        ranked_playbooks = sorted(set(ranked_playbooks), key=lambda x: x[1], reverse=True)[:5]
        
        # Sign ML advice to immutable log
        await immutable_log.append(
            actor="ml_advisors",
            action="advice_provided",
            resource="self_heal",
            subsystem="meta_coordinated_healing",
            payload={
                "advice_id": advice_id,
                "cycle_id": focus.cycle_id,
                "focus_area": focus.focus_area.value,
                "root_causes": root_causes,
                "top_playbooks": [p[0] for p in ranked_playbooks[:3]],
                "confidence_scores": confidence_scores
            },
            result="advised",
            signature=await self._sign_action(f"ml_advice_{advice_id}")
        )
        
        return MLAdvice(
            advice_id=advice_id,
            model_type="ensemble",
            focus_area=focus.focus_area,
            recommendations=all_recommendations,
            confidence_scores=confidence_scores,
            root_cause_candidates=root_causes,
            ranked_playbooks=ranked_playbooks
        )
    
    # ========== ML/DL ADVISORS (Embedded) ==========
    
    async def _ml_anomaly_advisor(self, focus: CycleFocus) -> Dict:
        """ML anomaly scoring advisor"""
        # Simplified: score anomalies based on trigger mesh events
        recommendations = []
        
        if focus.focus_area == FocusArea.LATENCY_DRIFT:
            recommendations.append({
                "type": "anomaly",
                "severity": "medium",
                "description": "Latency trending upward"
            })
        
        return {
            "recommendations": recommendations,
            "confidence": 0.75,
            "root_causes": ["increased_load", "cache_cold"],
            "playbook_rankings": [("scale_up_instances", 0.85), ("warm_cache", 0.72)]
        }
    
    async def _ml_root_cause_advisor(self, focus: CycleFocus) -> Dict:
        """ML root cause suggestion advisor"""
        root_causes = []
        
        if focus.focus_area == FocusArea.ERROR_SPIKE:
            root_causes = ["dependency_failure", "bad_deployment", "circuit_breaker_open"]
        elif focus.focus_area == FocusArea.LATENCY_DRIFT:
            root_causes = ["database_slow_query", "cache_miss_rate_high", "cpu_saturation"]
        
        return {
            "recommendations": [],
            "confidence": 0.80,
            "root_causes": root_causes,
            "playbook_rankings": []
        }
    
    async def _ml_playbook_advisor(self, focus: CycleFocus) -> Dict:
        """ML playbook ranking advisor"""
        # Use focus area priorities + historical success rates
        rankings = []
        
        for playbook in focus.playbook_priorities:
            # Simplified scoring: prioritize based on focus
            score = 0.80 if playbook in focus.playbook_priorities[:2] else 0.65
            rankings.append((playbook, score))
        
        return {
            "recommendations": [],
            "confidence": 0.70,
            "root_causes": [],
            "playbook_rankings": rankings
        }
    
    # ========== AGENTIC LAYER DIRECTIVE ==========
    
    async def _issue_agentic_directive(self, focus: CycleFocus, ml_advice: MLAdvice) -> bool:
        """
        Issue directive to agentic planner.
        
        The agentic layer (planner + trust + verification) will:
        1. Create execution plan
        2. Check trust/governance
        3. Execute if approved
        4. Verify outcome
        5. Rollback if needed
        6. Sign results to immutable log
        """
        try:
            # Publish directive for agentic planner
            await trigger_mesh.publish(TriggerEvent(
                event_type="meta_loop.healing_directive",
                source="meta_coordinator",
                actor="meta_loop",
                resource="agentic_planner",
                payload={
                    "cycle_id": focus.cycle_id,
                    "focus_area": focus.focus_area.value,
                    "guardrail_level": focus.guardrail_adjustment.value,
                    "ml_advice": {
                        "root_causes": ml_advice.root_cause_candidates,
                        "recommended_playbooks": [p[0] for p in ml_advice.ranked_playbooks],
                        "confidence_scores": ml_advice.confidence_scores
                    },
                    "time_budget_seconds": focus.time_budget_seconds,
                    "requires_verification": True
                },
                timestamp=datetime.now(timezone.utc)
            ))
            
            # Log directive to immutable log
            await immutable_log.append(
                actor="meta_loop",
                action="agentic_directive_issued",
                resource="agentic_planner",
                subsystem="meta_coordinated_healing",
                payload={
                    "cycle_id": focus.cycle_id,
                    "directive_type": "healing_action",
                    "focus": focus.focus_area.value
                },
                result="directive_issued",
                signature=await self._sign_action(f"directive_{focus.cycle_id}")
            )
            
            return True
        
        except Exception as e:
            print(f"    Error issuing directive: {e}")
            return False
    
    async def _learn_from_outcomes(self):
        """Learn from recent signed outcomes to adjust future cycles"""
        # Analyze last 10 outcomes
        recent_outcomes = self.outcome_history[-10:] if len(self.outcome_history) >= 10 else self.outcome_history
        
        if not recent_outcomes:
            return
        
        success_rate = sum(1 for o in recent_outcomes if o.result == "success") / len(recent_outcomes)
        
        # Adjust guardrails based on success rate
        if success_rate < 0.5 and self.guardrail_state != GuardrailAdjustment.TIGHTEN:
            print(f"  📉 Low success rate ({success_rate:.1%}) -> Tightening guardrails")
            self.guardrail_state = GuardrailAdjustment.TIGHTEN
        
        elif success_rate > 0.85 and self.guardrail_state != GuardrailAdjustment.LOOSEN:
            print(f"  📈 High success rate ({success_rate:.1%}) -> Loosening guardrails")
            self.guardrail_state = GuardrailAdjustment.LOOSEN
    
    async def record_outcome(self, outcome: SignedOutcome):
        """Record a signed execution outcome from agentic layer"""
        self.outcome_history.append(outcome)
        
        # Store in immutable log
        await immutable_log.append(
            actor="agentic_planner",
            action="execution_outcome",
            resource=outcome.service,
            subsystem="meta_coordinated_healing",
            payload={
                "outcome_id": outcome.outcome_id,
                "cycle_id": outcome.cycle_id,
                "plan_id": outcome.plan_id,
                "playbook": outcome.playbook,
                "result": outcome.result,
                "duration_seconds": outcome.duration_seconds,
                "verification_passed": outcome.verification_passed,
                "trust_decision": outcome.trust_decision,
                "rationale": outcome.rationale,
                "learned_insights": outcome.learned_insights
            },
            result=outcome.result,
            signature=outcome.actor_signature
        )
        
        print(f"  📝 Outcome recorded: {outcome.playbook} -> {outcome.result}")
    
    async def _sign_action(self, action_id: str) -> str:
        """Generate signature for immutable log entry"""
        # Simplified signature (in production: use cryptographic signing)
        import hashlib
        data = f"{action_id}:{datetime.now(timezone.utc).isoformat()}:meta_coordinator"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


# Singleton instance
meta_coordinated_healing = MetaCoordinatedHealing()
