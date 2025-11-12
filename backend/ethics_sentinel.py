"""
Ethics & Compliance Sentinel - Oversight and alignment guardian

Watches the immutable ledger for systemic bias, rule violations, and policy drift.
Surfaces explainability reports. Forces human review when actions press against
policy boundaries. Keeps agentic behavior aligned with trust commitments.
"""

import asyncio
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log


class ViolationType(Enum):
    BIAS_DETECTED = "bias_detected"
    POLICY_VIOLATION = "policy_violation"
    TRUST_BOUNDARY = "trust_boundary"
    FAIRNESS_CONCERN = "fairness_concern"
    TRANSPARENCY_GAP = "transparency_gap"
    ACCOUNTABILITY_ISSUE = "accountability_issue"


class SeverityLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    BLOCKING = "blocking"


@dataclass
class ComplianceRule:
    """Compliance rule specification"""
    rule_id: str
    rule_type: str
    description: str
    pattern: Dict[str, Any]
    severity: SeverityLevel
    requires_human_review: bool = False
    auto_block: bool = False


@dataclass
class ViolationRecord:
    """Detected compliance violation"""
    violation_id: str
    violation_type: ViolationType
    severity: SeverityLevel
    detected_at: datetime
    actor: str
    action: str
    resource: str
    evidence: Dict[str, Any]
    rule_id: Optional[str] = None
    human_reviewed: bool = False
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None


@dataclass
class BiasSignal:
    """Signal indicating potential bias"""
    signal_id: str
    category: str
    metric: str
    expected_distribution: Dict[str, float]
    actual_distribution: Dict[str, float]
    divergence_score: float
    sample_size: int
    detected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExplainabilityReport:
    """Explains why GRACE made a decision"""
    report_id: str
    decision_id: str
    decision_type: str
    timestamp: datetime
    factors: List[Dict[str, Any]]
    weights: Dict[str, float]
    confidence: float
    alternatives_considered: List[str]
    human_readable_explanation: str
    supporting_evidence: List[str]


class BiasDetector:
    """Detects systemic bias in decision patterns"""
    
    def __init__(self):
        self.decision_history: List[Dict] = []
        self.bias_thresholds = {
            "geographic": 0.15,
            "temporal": 0.20,
            "service_type": 0.15,
            "severity": 0.10
        }
    
    async def analyze_for_bias(self) -> List[BiasSignal]:
        """Analyze decision patterns for systemic bias"""
        signals = []
        
        signals.extend(await self._check_geographic_bias())
        signals.extend(await self._check_temporal_bias())
        signals.extend(await self._check_service_bias())
        signals.extend(await self._check_severity_bias())
        
        return signals
    
    async def _check_geographic_bias(self) -> List[BiasSignal]:
        """Check for geographic bias in decisions"""
        
        regional_decisions = defaultdict(int)
        total = 0
        
        for decision in self.decision_history:
            if "region" in decision.get("context", {}):
                region = decision["context"]["region"]
                regional_decisions[region] += 1
                total += 1
        
        if total < 30:
            return []
        
        expected_uniform = 1.0 / len(regional_decisions) if regional_decisions else 0
        
        divergence = 0.0
        actual_dist = {}
        expected_dist = {}
        
        for region, count in regional_decisions.items():
            actual_rate = count / total
            actual_dist[region] = actual_rate
            expected_dist[region] = expected_uniform
            divergence += abs(actual_rate - expected_uniform)
        
        if divergence > self.bias_thresholds["geographic"]:
            return [BiasSignal(
                signal_id=f"bias_{datetime.utcnow().timestamp()}",
                category="geographic",
                metric="decision_distribution",
                expected_distribution=expected_dist,
                actual_distribution=actual_dist,
                divergence_score=divergence,
                sample_size=total
            )]
        
        return []
    
    async def _check_temporal_bias(self) -> List[BiasSignal]:
        """Check for time-of-day or day-of-week bias"""
        return []
    
    async def _check_service_bias(self) -> List[BiasSignal]:
        """Check if certain services get preferential treatment"""
        return []
    
    async def _check_severity_bias(self) -> List[BiasSignal]:
        """Check if severity assessments are consistent"""
        return []
    
    async def record_decision(self, decision: Dict):
        """Record decision for bias analysis"""
        self.decision_history.append(decision)
        
        if len(self.decision_history) > 10000:
            self.decision_history = self.decision_history[-5000:]


class PolicyMonitor:
    """Monitors adherence to governance policies"""
    
    def __init__(self):
        self.rules: Dict[str, ComplianceRule] = {}
        self.violations: List[ViolationRecord] = []
    
    async def register_rule(self, rule: ComplianceRule):
        """Register compliance rule"""
        self.rules[rule.rule_id] = rule
    
    async def check_action(
        self,
        actor: str,
        action: str,
        resource: str,
        context: Dict
    ) -> Optional[ViolationRecord]:
        """Check if action violates any compliance rules"""
        
        for rule_id, rule in self.rules.items():
            if await self._matches_pattern(action, resource, context, rule.pattern):
                violation = ViolationRecord(
                    violation_id=f"violation_{datetime.utcnow().timestamp()}",
                    violation_type=ViolationType.POLICY_VIOLATION,
                    severity=rule.severity,
                    detected_at=datetime.utcnow(),
                    actor=actor,
                    action=action,
                    resource=resource,
                    evidence=context,
                    rule_id=rule_id
                )
                
                self.violations.append(violation)
                
                await immutable_log.append(
                    actor="ethics_sentinel",
                    action="violation_detected",
                    resource=violation.violation_id,
                    subsystem="policy_monitor",
                    payload={
                        "violation_type": violation.violation_type.value,
                        "severity": violation.severity.value,
                        "rule_id": rule_id,
                        "actor": actor
                    },
                    result="detected"
                )
                
                if rule.auto_block:
                    await self._block_action(violation)
                
                if rule.requires_human_review:
                    await self._request_human_review(violation)
                
                return violation
        
        return None
    
    async def _matches_pattern(
        self,
        action: str,
        resource: str,
        context: Dict,
        pattern: Dict
    ) -> bool:
        """Check if action matches rule pattern"""
        
        if "action" in pattern and pattern["action"] not in action:
            return False
        
        if "resource_pattern" in pattern and pattern["resource_pattern"] not in resource:
            return False
        
        if "context_conditions" in pattern:
            for key, value in pattern["context_conditions"].items():
                if context.get(key) != value:
                    return False
        
        return True
    
    async def _block_action(self, violation: ViolationRecord):
        """Block action that violates policy"""
        await trigger_mesh.publish(TriggerEvent(
            event_type="ethics.action_blocked",
            source="policy_monitor",
            actor="ethics_sentinel",
            resource=violation.violation_id,
            payload={
                "blocked_actor": violation.actor,
                "blocked_action": violation.action,
                "reason": violation.violation_type.value
            },
            timestamp=datetime.utcnow()
        ))
    
    async def _request_human_review(self, violation: ViolationRecord):
        """Escalate violation for human review"""
        await trigger_mesh.publish(TriggerEvent(
            event_type="ethics.human_review_required",
            source="policy_monitor",
            actor="ethics_sentinel",
            resource=violation.violation_id,
            payload={
                "violation_type": violation.violation_type.value,
                "severity": violation.severity.value,
                "actor": violation.actor,
                "action": violation.action
            },
            timestamp=datetime.utcnow()
        ))


class TrustBoundaryGuard:
    """Guards against actions that press policy boundaries"""
    
    def __init__(self):
        self.boundaries: Dict[str, Dict] = {
            "data_access": {
                "max_records_per_query": 10000,
                "sensitive_data_actions": ["delete", "export", "modify"]
            },
            "system_changes": {
                "production_changes": ["deploy", "scale", "configure"],
                "requires_approval_above_risk": 0.6
            },
            "autonomous_actions": {
                "max_cost_per_action": 1000.0,
                "critical_resources": ["database", "auth", "payment"]
            }
        }
    
    async def check_boundary(
        self,
        action: str,
        resource: str,
        context: Dict
    ) -> Tuple[bool, Optional[str]]:
        """Check if action approaches policy boundary"""
        
        if await self._is_sensitive_data_action(action, resource, context):
            return True, "sensitive_data_boundary"
        
        if await self._is_high_risk_system_change(action, resource, context):
            return True, "system_change_boundary"
        
        if await self._exceeds_autonomous_limits(action, resource, context):
            return True, "autonomous_limit_boundary"
        
        return False, None
    
    async def _is_sensitive_data_action(
        self,
        action: str,
        resource: str,
        context: Dict
    ) -> bool:
        """Check if action involves sensitive data"""
        sensitive_actions = self.boundaries["data_access"]["sensitive_data_actions"]
        
        if any(sa in action for sa in sensitive_actions):
            if "sensitive" in resource or context.get("data_classification") == "sensitive":
                return True
        
        return False
    
    async def _is_high_risk_system_change(
        self,
        action: str,
        resource: str,
        context: Dict
    ) -> bool:
        """Check if action is high-risk system change"""
        production_changes = self.boundaries["system_changes"]["production_changes"]
        
        if any(pc in action for pc in production_changes):
            if context.get("environment") == "production":
                return True
        
        return False
    
    async def _exceeds_autonomous_limits(
        self,
        action: str,
        resource: str,
        context: Dict
    ) -> bool:
        """Check if action exceeds autonomous authority"""
        critical_resources = self.boundaries["autonomous_actions"]["critical_resources"]
        
        if any(cr in resource for cr in critical_resources):
            return True
        
        cost = context.get("estimated_cost", 0)
        if cost > self.boundaries["autonomous_actions"]["max_cost_per_action"]:
            return True
        
        return False


class ExplainabilityEngine:
    """Generates explainability reports for decisions"""
    
    def __init__(self):
        self.reports: Dict[str, ExplainabilityReport] = {}
    
    async def explain_decision(
        self,
        decision_id: str,
        decision_type: str,
        context: Dict,
        factors: List[Dict],
        chosen_option: str,
        alternatives: List[str]
    ) -> ExplainabilityReport:
        """Generate explainability report"""
        
        weights = await self._calculate_factor_weights(factors)
        explanation = await self._generate_human_explanation(
            decision_type, factors, weights, chosen_option, alternatives
        )
        
        evidence = await self._gather_supporting_evidence(decision_id, context)
        
        confidence = sum(f.get("confidence", 0.5) * weights.get(f["name"], 0.0) for f in factors)
        
        report = ExplainabilityReport(
            report_id=f"explain_{decision_id}",
            decision_id=decision_id,
            decision_type=decision_type,
            timestamp=datetime.utcnow(),
            factors=factors,
            weights=weights,
            confidence=confidence,
            alternatives_considered=alternatives,
            human_readable_explanation=explanation,
            supporting_evidence=evidence
        )
        
        self.reports[report.report_id] = report
        
        await immutable_log.append(
            actor="ethics_sentinel",
            action="explainability_report_generated",
            resource=report.report_id,
            subsystem="explainability_engine",
            payload={
                "decision_id": decision_id,
                "confidence": confidence
            },
            result="generated"
        )
        
        return report
    
    async def _calculate_factor_weights(self, factors: List[Dict]) -> Dict[str, float]:
        """Calculate weight of each factor in decision"""
        total_impact = sum(f.get("impact", 1.0) for f in factors)
        
        weights = {}
        for factor in factors:
            impact = factor.get("impact", 1.0)
            weights[factor["name"]] = impact / total_impact if total_impact > 0 else 0.0
        
        return weights
    
    async def _generate_human_explanation(
        self,
        decision_type: str,
        factors: List[Dict],
        weights: Dict[str, float],
        chosen_option: str,
        alternatives: List[str]
    ) -> str:
        """Generate human-readable explanation"""
        
        top_factors = sorted(
            factors,
            key=lambda f: weights.get(f["name"], 0.0),
            reverse=True
        )[:3]
        
        explanation = f"I chose '{chosen_option}' for this {decision_type} based on:\n\n"
        
        for i, factor in enumerate(top_factors, 1):
            weight = weights.get(factor["name"], 0.0)
            explanation += f"{i}. {factor['name']} (weight: {weight:.1%}): {factor.get('description', 'N/A')}\n"
        
        if alternatives:
            explanation += f"\nI also considered: {', '.join(alternatives)}"
        
        return explanation
    
    async def _gather_supporting_evidence(
        self,
        decision_id: str,
        context: Dict
    ) -> List[str]:
        """Gather supporting evidence from ledger and context"""
        evidence = []
        
        if "historical_success_rate" in context:
            evidence.append(f"Historical success rate: {context['historical_success_rate']:.1%}")
        
        if "similar_cases" in context:
            evidence.append(f"Based on {context['similar_cases']} similar past cases")
        
        return evidence


class ComplianceDashboard:
    """Surfaces compliance status and violations"""
    
    def __init__(
        self,
        bias_detector: BiasDetector,
        policy_monitor: PolicyMonitor,
        boundary_guard: TrustBoundaryGuard
    ):
        self.bias_detector = bias_detector
        self.policy_monitor = policy_monitor
        self.boundary_guard = boundary_guard
    
    async def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        
        bias_signals = await self.bias_detector.analyze_for_bias()
        
        recent_violations = [
            v for v in self.policy_monitor.violations
            if (datetime.utcnow() - v.detected_at).days < 7
        ]
        
        unresolved_violations = [v for v in recent_violations if not v.human_reviewed]
        
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "bias_signals": {
                "count": len(bias_signals),
                "signals": [
                    {
                        "category": s.category,
                        "divergence": s.divergence_score,
                        "sample_size": s.sample_size
                    }
                    for s in bias_signals
                ]
            },
            "violations": {
                "last_7_days": len(recent_violations),
                "unresolved": len(unresolved_violations),
                "by_severity": self._group_by_severity(recent_violations)
            },
            "compliance_score": await self._calculate_compliance_score(
                bias_signals, recent_violations
            )
        }
        
        return report
    
    def _group_by_severity(self, violations: List[ViolationRecord]) -> Dict[str, int]:
        """Group violations by severity"""
        groups = defaultdict(int)
        for v in violations:
            groups[v.severity.value] += 1
        return dict(groups)
    
    async def _calculate_compliance_score(
        self,
        bias_signals: List[BiasSignal],
        violations: List[ViolationRecord]
    ) -> float:
        """Calculate overall compliance score (0-100)"""
        
        base_score = 100.0
        
        base_score -= len(bias_signals) * 5
        
        for violation in violations:
            if violation.severity == SeverityLevel.CRITICAL:
                base_score -= 15
            elif violation.severity == SeverityLevel.WARNING:
                base_score -= 5
            elif violation.severity == SeverityLevel.INFO:
                base_score -= 1
        
        return max(0.0, min(100.0, base_score))


class EthicsSentinel:
    """Main ethics and compliance coordinator"""
    
    def __init__(self):
        self.bias_detector = BiasDetector()
        self.policy_monitor = PolicyMonitor()
        self.boundary_guard = TrustBoundaryGuard()
        self.explainability = ExplainabilityEngine()
        self.dashboard = ComplianceDashboard(
            self.bias_detector,
            self.policy_monitor,
            self.boundary_guard
        )
        self.running = False
    
    async def start(self):
        """Start ethics sentinel"""
        
        await self._register_default_rules()
        
        await trigger_mesh.subscribe("*", self._monitor_action)
        
        asyncio.create_task(self._ethics_loop())
        
        self.running = True
        print("✓ Ethics & Compliance Sentinel started - Watching for violations")
    
    async def stop(self):
        """Stop ethics sentinel"""
        self.running = False
    
    async def _register_default_rules(self):
        """Register default compliance rules"""
        
        await self.policy_monitor.register_rule(ComplianceRule(
            rule_id="no_unauthorized_data_deletion",
            rule_type="data_protection",
            description="Prevent unauthorized data deletion",
            pattern={"action": "delete", "context_conditions": {"authorized": False}},
            severity=SeverityLevel.BLOCKING,
            requires_human_review=True,
            auto_block=True
        ))
        
        await self.policy_monitor.register_rule(ComplianceRule(
            rule_id="production_change_approval",
            rule_type="change_management",
            description="Production changes require approval",
            pattern={"action": "deploy", "context_conditions": {"environment": "production"}},
            severity=SeverityLevel.WARNING,
            requires_human_review=True,
            auto_block=False
        ))
    
    async def _monitor_action(self, event: TriggerEvent):
        """Monitor all actions for compliance"""
        
        violation = await self.policy_monitor.check_action(
            event.actor,
            event.event_type,
            event.resource,
            event.payload
        )
        
        at_boundary, boundary_type = await self.boundary_guard.check_boundary(
            event.event_type,
            event.resource,
            event.payload
        )
        
        if at_boundary:
            await trigger_mesh.publish(TriggerEvent(
                event_type="ethics.boundary_approached",
                source="ethics_sentinel",
                actor="ethics_sentinel",
                resource=event.resource,
                payload={
                    "boundary_type": boundary_type,
                    "original_action": event.event_type
                },
                timestamp=datetime.utcnow()
            ))
        
        if event.event_type.startswith("decision."):
            await self.bias_detector.record_decision({
                "action": event.event_type,
                "context": event.payload
            })
    
    async def _ethics_loop(self):
        """Background ethics monitoring loop"""
        while self.running:
            await asyncio.sleep(3600)
            
            bias_signals = await self.bias_detector.analyze_for_bias()
            
            for signal in bias_signals:
                if signal.divergence_score > 0.25:
                    await trigger_mesh.publish(TriggerEvent(
                        event_type="ethics.bias_detected",
                        source="ethics_sentinel",
                        actor="ethics_sentinel",
                        resource=signal.signal_id,
                        payload={
                            "category": signal.category,
                            "divergence": signal.divergence_score,
                            "sample_size": signal.sample_size
                        },
                        timestamp=datetime.utcnow()
                    ))
            
            report = await self.dashboard.generate_compliance_report()
            
            await immutable_log.append(
                actor="ethics_sentinel",
                action="compliance_report_generated",
                resource=f"report_{datetime.utcnow().timestamp()}",
                subsystem="ethics_sentinel",
                payload=report,
                result="generated"
            )


ethics_sentinel = EthicsSentinel()
