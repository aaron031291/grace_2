"""Governance Prime Directive - Constitutional Gate

Constitutional validation enforcer preventing violations before execution.
All GraceLoopOutput must pass through this gate.
"""

import uuid
from typing import Dict, Any, List

from .GraceLoopOutput import GraceLoopOutput
from .models import GovernanceVerdict, GovernanceDecision, RemediationAction

# Lazy import to avoid circular dependencies
constitutional_engine = None
immutable_logger = None

def _init_engines():
    """Initialize engines lazily"""
    global constitutional_engine, immutable_logger
    if constitutional_engine is None:
        try:
            from backend.constitutional_engine import constitutional_engine as ce
            from backend.immutable_log import immutable_logger as il
            constitutional_engine = ce
            immutable_logger = il
        except ImportError:
            # Standalone mode - create minimal mocks
            constitutional_engine = None
            immutable_logger = None

class GovernancePrimeDirective:
    """
    Constitutional gate enforcing non-negotiable principles
    
    Validates all GraceLoopOutput against constitutional principles
    and issues governance verdicts.
    """
    
    def __init__(self):
        # Initialize with simple logger that works standalone
        self.audit = None  # Will be initialized lazily with _init_engines()
        
        # Non-negotiable thresholds
        self.safety_threshold = 0.9  # Minimum compliance for safety-critical
        self.legal_threshold = 0.95  # Minimum compliance for legal operations
        self.high_risk_threshold = 0.85  # Threshold for high-risk tagging
        
    async def validate_against_constitution(
        self,
        output: GraceLoopOutput
    ) -> GovernanceVerdict:
        """
        Validate output against constitutional principles
        
        Args:
            output: GraceLoopOutput to validate
            
        Returns:
            GovernanceVerdict with decision and remediation actions
        """
        
        action_id = str(uuid.uuid4())
        
        # Check constitutional compliance
        _init_engines()
        
        if constitutional_engine:
            compliance_result = await constitutional_engine.check_constitutional_compliance(
                action_id=action_id,
                actor=output.component,
                action_type=output.output_type.value,
                resource=str(output.result)[:200],
                context={
                    'loop_id': output.loop_id,
                    'confidence': output.confidence,
                    'has_errors': len(output.errors) > 0,
                    'has_warnings': len(output.warnings) > 0,
                    'policy_tags': [p.policy_name for p in output.policy_tags]
                },
                confidence=output.confidence
            )
        else:
            # Standalone mode - basic compliance check
            compliance_result = {
                'principles_checked': [],
                'compliance_score': 1.0 if output.constitutional_compliance else 0.0,
                'violations': [],
                'needs_clarification': output.confidence < 0.7
            }
        
        # Extract principle IDs checked
        constitutional_checks = compliance_result.get('principles_checked', [])
        compliance_score = compliance_result.get('compliance_score', 1.0)
        
        # Determine decision and tags
        decision, tags = self._determine_decision(output, compliance_result)
        
        # Determine remediation actions
        remediation_actions = self._determine_remediation(output, compliance_result, decision)
        
        # Build reason
        reason = self._build_reason(output, compliance_result, decision)
        
        # Determine severity
        severity = self._determine_severity(compliance_result, decision)
        
        # Create verdict
        verdict = GovernanceVerdict(
            decision=decision,
            tags=tags,
            remediation_actions=remediation_actions,
            reason=reason,
            constitutional_checks=constitutional_checks,
            compliance_score=compliance_score,
            severity=severity,
            requires_approval=compliance_result.get('needs_clarification', False),
            safe_to_store=decision != GovernanceDecision.BLOCK
        )
        
        # Audit the verdict
        await self.audit.append(
            actor=output.component,
            action="governance_validation",
            resource=output.loop_id,
            subsystem="governance_prime_directive",
            payload={
                'decision': decision.value,
                'compliance_score': compliance_score,
                'tags': tags,
                'constitutional_checks': constitutional_checks
            },
            result=decision.value
        )
        
        return verdict
    
    def _determine_decision(
        self,
        output: GraceLoopOutput,
        compliance_result: Dict[str, Any]
    ) -> tuple[GovernanceDecision, List[str]]:
        """Determine governance decision and tags"""
        
        tags = []
        compliance_score = compliance_result.get('compliance_score', 1.0)
        violations = compliance_result.get('violations', [])
        needs_clarification = compliance_result.get('needs_clarification', False)
        
        # Check for critical violations
        critical_violations = [v for v in violations if v.get('severity') == 'critical']
        
        # BLOCK: Critical violations or already flagged non-compliant
        if critical_violations or not output.constitutional_compliance:
            tags.append('blocked')
            tags.append('constitutional_violation')
            return GovernanceDecision.BLOCK, tags
        
        # ESCALATE: Needs human review or approval
        if needs_clarification or output.requires_approval:
            tags.append('requires_human_review')
            if output.confidence < 0.5:
                tags.append('low_confidence')
            return GovernanceDecision.ESCALATE, tags
        
        # Check for high-risk indicators
        is_high_risk = (
            compliance_score < self.high_risk_threshold or
            output.confidence < 0.7 or
            len(output.errors) > 0
        )
        
        if is_high_risk:
            tags.append('high_risk')
        
        # Check for restricted context
        if self._has_sensitive_content(output):
            tags.append('restricted_context')
        
        # Check for export controls
        if self._requires_export_controls(output):
            tags.append('export_controls')
        
        # DEGRADE: Has issues but can proceed with reduced trust
        if violations or compliance_score < 0.9:
            tags.append('degraded_trust')
            return GovernanceDecision.DEGRADE, tags
        
        # GO: Full approval
        tags.append('approved')
        return GovernanceDecision.GO, tags
    
    def _determine_remediation(
        self,
        output: GraceLoopOutput,
        compliance_result: Dict[str, Any],
        decision: GovernanceDecision
    ) -> List[RemediationAction]:
        """Determine remediation actions"""
        
        actions = []
        
        if decision == GovernanceDecision.BLOCK:
            actions.append(RemediationAction.BLOCK)
            actions.append(RemediationAction.LOG)
            actions.append(RemediationAction.NOTIFY)
        
        if decision == GovernanceDecision.ESCALATE:
            actions.append(RemediationAction.ESCALATE)
            actions.append(RemediationAction.LOG)
        
        if decision == GovernanceDecision.DEGRADE:
            actions.append(RemediationAction.DOWNGRADE)
            actions.append(RemediationAction.LOG)
        
        # Check for sensitive content
        if self._has_sensitive_content(output):
            actions.append(RemediationAction.REDACT)
        
        # Always log
        if RemediationAction.LOG not in actions:
            actions.append(RemediationAction.LOG)
        
        return actions
    
    def _build_reason(
        self,
        output: GraceLoopOutput,
        compliance_result: Dict[str, Any],
        decision: GovernanceDecision
    ) -> str:
        """Build explanation for verdict"""
        
        reasons = []
        
        if decision == GovernanceDecision.BLOCK:
            violations = compliance_result.get('violations', [])
            if violations:
                reasons.append(f"Critical violations: {len(violations)}")
            if not output.constitutional_compliance:
                reasons.append("Pre-flagged as non-compliant")
        
        elif decision == GovernanceDecision.ESCALATE:
            if compliance_result.get('needs_clarification'):
                reasons.append(compliance_result.get('clarification_reason', 'Needs clarification'))
            if output.requires_approval:
                reasons.append("Requires human approval")
        
        elif decision == GovernanceDecision.DEGRADE:
            score = compliance_result.get('compliance_score', 1.0)
            reasons.append(f"Compliance score {score:.2f} below optimal")
        
        else:  # GO
            reasons.append("All constitutional checks passed")
        
        return "; ".join(reasons) if reasons else "Standard governance review"
    
    def _determine_severity(
        self,
        compliance_result: Dict[str, Any],
        decision: GovernanceDecision
    ) -> str:
        """Determine severity level"""
        
        if decision == GovernanceDecision.BLOCK:
            return "critical"
        elif decision == GovernanceDecision.ESCALATE:
            return "warning"
        elif decision == GovernanceDecision.DEGRADE:
            return "warning"
        else:
            return "info"
    
    def _has_sensitive_content(self, output: GraceLoopOutput) -> bool:
        """Check if output contains sensitive content"""
        
        # Check for sensitive policy tags
        sensitive_policies = ['privacy', 'security', 'credentials', 'pii']
        for tag in output.policy_tags:
            if any(s in tag.policy_name.lower() for s in sensitive_policies):
                return True
        
        # Check result content
        result_str = str(output.result).lower()
        sensitive_keywords = ['password', 'token', 'secret', 'key', 'credential']
        if any(kw in result_str for kw in sensitive_keywords):
            return True
        
        return False
    
    def _requires_export_controls(self, output: GraceLoopOutput) -> bool:
        """Check if output requires export controls"""
        
        # Check for code generation or model outputs
        if output.output_type.value in ['generation', 'action']:
            result_str = str(output.result).lower()
            if 'encryption' in result_str or 'crypto' in result_str:
                return True
        
        return False
    
    def explain(self, verdict: GovernanceVerdict) -> str:
        """
        Generate human-readable explanation of verdict
        
        Args:
            verdict: GovernanceVerdict to explain
            
        Returns:
            Audit-ready explanation
        """
        
        explanation_parts = [
            f"**Governance Decision**: {verdict.decision.value.upper()}",
            f"**Compliance Score**: {verdict.compliance_score:.2%}",
            f"**Severity**: {verdict.severity}",
            f"**Reason**: {verdict.reason}",
            "",
            f"**Tags**: {', '.join(verdict.tags) if verdict.tags else 'none'}",
            f"**Remediation Actions**: {', '.join(a.value for a in verdict.remediation_actions)}",
            f"**Constitutional Checks**: {len(verdict.constitutional_checks)} principles verified",
            "",
            f"**Approved**: {verdict.is_approved()}",
            f"**Needs Escalation**: {verdict.needs_escalation()}",
            f"**Safe to Store**: {verdict.safe_to_store}"
        ]
        
        return "\n".join(explanation_parts)

# Singleton instance (will initialize audit lazily)
try:
    governance_prime_directive = GovernancePrimeDirective()
except:
    governance_prime_directive = None  # Will be initialized on first use
