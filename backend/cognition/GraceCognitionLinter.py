"""GraceCognitionLinter - Contradiction and Drift Detection

Runs BEFORE governance to catch:
- Direct conflicts (opposing facts)
- Policy drift (violates anchored governance)
- Causal mismatches (contradicts dependencies)
- Temporal inconsistencies
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import hashlib

from .models import LintReport, Violation, Patch, ViolationSeverity
from .GraceLoopOutput import GraceLoopOutput

logger = logging.getLogger(__name__)

class GraceCognitionLinter:
    """
    Pre-governance linting for contradictions and drift.
    
    Runs static and dynamic checks on outputs before they
    enter the governance pipeline.
    """
    
    def __init__(self):
        self.recent_memory_cache: List[GraceLoopOutput] = []
        self.knowledge_artifacts: Dict[str, Any] = {}
        self.governance_anchors: Dict[str, Any] = {}
        self.causal_dependencies: Dict[str, List[str]] = {}
        self.max_cache_size = 100
    
    def lint(
        self, 
        output: GraceLoopOutput, 
        context: Optional[Dict[str, Any]] = None
    ) -> LintReport:
        """
        Main linting method - check output for contradictions.
        
        Args:
            output: GraceLoopOutput to lint
            context: Optional context including recent memory
            
        Returns:
            LintReport with violations and suggested fixes
        """
        logger.info(f"Linting output from {output.component}")
        
        violations: List[Violation] = []
        
        # Static checks
        violations.extend(self._check_direct_conflicts(output))
        violations.extend(self._check_policy_drift(output))
        violations.extend(self._check_causal_mismatches(output))
        violations.extend(self._check_temporal_inconsistencies(output))
        
        # Always check constitutional alignment
        violations.extend(self._check_constitutional_alignment(output))
        
        # Dynamic checks (requires context)
        if context:
            violations.extend(self._check_memory_conflicts(output, context))
        
        # Always check knowledge conflicts (uses self.knowledge_artifacts)
        violations.extend(self._check_knowledge_conflicts(output))
        
        # Determine overall severity
        severity = self._compute_severity(violations)
        
        # Generate fixes
        fixes = self._generate_fixes(output, violations)
        
        # Check if auto-remediable
        auto_remediable = all(p.safe_to_auto_apply for p in fixes)
        
        # Generate summary
        summary = self._generate_summary(violations, fixes)
        
        report = LintReport(
            output_id=output.loop_id,
            severity=severity,
            violations=violations,
            suggested_fixes=fixes,
            auto_remediable=auto_remediable,
            passed=len(violations) == 0,
            summary=summary
        )
        
        # Update cache with this output if it passed
        if report.passed:
            self._update_memory_cache(output)
        
        logger.info(f"Lint complete: {len(violations)} violations, severity={severity.value}")
        return report
    
    def _check_direct_conflicts(self, output: GraceLoopOutput) -> List[Violation]:
        """Check for direct contradictions within the same output"""
        violations = []
        
        # Check for contradictions in result
        result_str = str(output.result).lower()
        
        # Simple contradiction patterns
        contradiction_pairs = [
            ('is true', 'is false'),
            ('true', 'false'),
            ('should', 'should not'),
            ('must', 'must not'),
            ('allowed', 'forbidden'),
            ('valid', 'invalid')
        ]
        
        for pos, neg in contradiction_pairs:
            if pos in result_str and neg in result_str:
                violations.append(Violation(
                    violation_type='direct_conflict',
                    severity=ViolationSeverity.ERROR,
                    description=f"Output contains contradictory statements: '{pos}' and '{neg}'",
                    location=output.component,
                    conflicting_items=[pos, neg],
                    suggested_action='Remove or reconcile conflicting statements'
                ))
        
        return violations
    
    def _check_policy_drift(self, output: GraceLoopOutput) -> List[Violation]:
        """Check if output violates anchored governance policies"""
        violations = []
        
        # Check policy tags for violations
        for tag in output.policy_tags:
            if tag.status == 'violation':
                violations.append(Violation(
                    violation_type='policy_drift',
                    severity=ViolationSeverity.ERROR,
                    description=f"Policy violation: {tag.policy_name}",
                    location=output.component,
                    conflicting_items=[tag.policy_name],
                    suggested_action=tag.reason or 'Review policy compliance',
                    metadata={'policy': tag.policy_name, 'reason': tag.reason}
                ))
        
        # Check for missing required approvals
        if output.requires_approval and not output.constitutional_compliance:
            violations.append(Violation(
                violation_type='policy_drift',
                severity=ViolationSeverity.WARNING,
                description='Output requires approval but lacks constitutional compliance',
                location=output.component,
                suggested_action='Ensure constitutional review before execution'
            ))
        
        return violations
    
    def _check_causal_mismatches(self, output: GraceLoopOutput) -> List[Violation]:
        """Check if output contradicts causal dependencies"""
        violations = []
        
        # If this component has causal dependencies, check them
        component = output.component
        if component in self.causal_dependencies:
            dependencies = self.causal_dependencies[component]
            
            # Look for violations in context
            if 'causal_chain' in output.context:
                declared_deps = output.context.get('causal_chain', [])
                
                for required_dep in dependencies:
                    if required_dep not in declared_deps:
                        violations.append(Violation(
                            violation_type='causal_mismatch',
                            severity=ViolationSeverity.WARNING,
                            description=f"Missing causal dependency: {required_dep}",
                            location=output.component,
                            conflicting_items=[required_dep],
                            suggested_action=f"Verify {required_dep} was executed before {component}"
                        ))
        
        return violations
    
    def _check_temporal_inconsistencies(self, output: GraceLoopOutput) -> List[Violation]:
        """Check for temporal logic violations"""
        violations = []
        
        # Check for future timestamps in evidence
        now = datetime.utcnow()
        for citation in output.citations:
            if citation.timestamp and citation.timestamp > now:
                violations.append(Violation(
                    violation_type='temporal_inconsistency',
                    severity=ViolationSeverity.WARNING,
                    description=f"Citation has future timestamp: {citation.source}",
                    location=output.component,
                    conflicting_items=[citation.source],
                    suggested_action='Verify citation timestamp accuracy'
                ))
        
        # Check expiration
        if output.expires_at and output.expires_at < now:
            violations.append(Violation(
                violation_type='temporal_inconsistency',
                severity=ViolationSeverity.INFO,
                description='Output has already expired',
                location=output.component,
                suggested_action='Update or remove expired output'
            ))
        
        return violations
    
    def _check_memory_conflicts(
        self, 
        output: GraceLoopOutput, 
        context: Dict[str, Any]
    ) -> List[Violation]:
        """Compare with recent memory for conflicts"""
        violations = []
        
        # Get recent memory from context or cache
        recent_items = context.get('recent_memory', self.recent_memory_cache[-100:])
        
        if not recent_items:
            return violations
        
        # Compare with recent outputs from same component
        for recent in recent_items:
            if not isinstance(recent, GraceLoopOutput):
                continue
                
            if recent.component != output.component:
                continue
            
            # Check for contradictory results
            if self._results_contradict(output.result, recent.result):
                violations.append(Violation(
                    violation_type='memory_conflict',
                    severity=ViolationSeverity.WARNING,
                    description=f"Contradicts recent output from {recent.component}",
                    location=output.component,
                    conflicting_items=[recent.loop_id, output.loop_id],
                    suggested_action='Reconcile with recent memory or explain change',
                    metadata={
                        'recent_loop_id': recent.loop_id,
                        'recent_timestamp': recent.created_at.isoformat()
                    }
                ))
        
        return violations
    
    def _check_knowledge_conflicts(self, output: GraceLoopOutput) -> List[Violation]:
        """Check against knowledge artifacts"""
        violations = []
        
        # Check citations against known artifacts
        for citation in output.citations:
            if citation.source in self.knowledge_artifacts:
                artifact = self.knowledge_artifacts[citation.source]
                
                # Verify citation confidence matches artifact trust
                artifact_trust = artifact.get('trust_score', 1.0)
                if citation.confidence > artifact_trust + 0.2:
                    violations.append(Violation(
                        violation_type='knowledge_conflict',
                        severity=ViolationSeverity.WARNING,
                        description=f"Citation confidence exceeds source trust: {citation.source}",
                        location=output.component,
                        conflicting_items=[citation.source],
                        suggested_action='Lower citation confidence or verify source'
                    ))
        
        return violations
    
    def _check_constitutional_alignment(self, output: GraceLoopOutput) -> List[Violation]:
        """Verify constitutional AI alignment"""
        violations = []
        
        # Check for missing compliance flag
        if output.requires_approval and not output.constitutional_compliance:
            violations.append(Violation(
                violation_type='constitutional_misalignment',
                severity=ViolationSeverity.CRITICAL,
                description='Requires approval but not constitutionally compliant',
                location=output.component,
                suggested_action='Run constitutional verification before execution'
            ))
        
        # Check for errors without diagnostics
        if output.errors and not output.diagnostics:
            violations.append(Violation(
                violation_type='constitutional_misalignment',
                severity=ViolationSeverity.WARNING,
                description='Errors present but no diagnostic information',
                location=output.component,
                suggested_action='Add diagnostic info for transparency'
            ))
        
        return violations
    
    def _results_contradict(self, result1: Any, result2: Any) -> bool:
        """Check if two results contradict each other"""
        # Simple heuristic - can be enhanced
        if isinstance(result1, bool) and isinstance(result2, bool):
            return result1 != result2
        
        if isinstance(result1, str) and isinstance(result2, str):
            r1_lower = result1.lower()
            r2_lower = result2.lower()
            
            # Check for opposite meanings
            opposite_pairs = [
                ('yes', 'no'),
                ('true', 'false'),
                ('allow', 'deny'),
                ('accept', 'reject')
            ]
            
            for pos, neg in opposite_pairs:
                if (pos in r1_lower and neg in r2_lower) or (neg in r1_lower and pos in r2_lower):
                    return True
        
        return False
    
    def _compute_severity(self, violations: List[Violation]) -> ViolationSeverity:
        """Compute overall severity from violations"""
        if not violations:
            return ViolationSeverity.INFO
        
        # Take highest severity
        severities = [v.severity for v in violations]
        
        if ViolationSeverity.CRITICAL in severities:
            return ViolationSeverity.CRITICAL
        elif ViolationSeverity.ERROR in severities:
            return ViolationSeverity.ERROR
        elif ViolationSeverity.WARNING in severities:
            return ViolationSeverity.WARNING
        else:
            return ViolationSeverity.INFO
    
    def _generate_fixes(
        self, 
        output: GraceLoopOutput, 
        violations: List[Violation]
    ) -> List[Patch]:
        """Generate suggested fixes for violations"""
        fixes = []
        
        for i, violation in enumerate(violations):
            patch_id = f"patch_{output.loop_id}_{i}"
            
            if violation.violation_type == 'direct_conflict':
                # Suggest removing conflicting statements
                fixes.append(Patch(
                    patch_id=patch_id,
                    violation_type=violation.violation_type,
                    action='remove',
                    target=','.join(violation.conflicting_items),
                    confidence=0.6,
                    rationale='Remove one of the conflicting statements',
                    safe_to_auto_apply=False
                ))
            
            elif violation.violation_type == 'memory_conflict':
                # Suggest re-run or escalation
                fixes.append(Patch(
                    patch_id=patch_id,
                    violation_type=violation.violation_type,
                    action='escalate',
                    target=output.component,
                    confidence=0.8,
                    rationale='Escalate to specialist for reconciliation',
                    safe_to_auto_apply=False
                ))
            
            elif violation.violation_type == 'temporal_inconsistency':
                # Safe to auto-fix timestamps
                fixes.append(Patch(
                    patch_id=patch_id,
                    violation_type=violation.violation_type,
                    action='replace',
                    target='timestamp',
                    replacement=datetime.utcnow(),
                    confidence=0.9,
                    rationale='Correct timestamp to current time',
                    safe_to_auto_apply=True
                ))
            
            elif violation.severity == ViolationSeverity.CRITICAL:
                # Critical violations require manual review
                fixes.append(Patch(
                    patch_id=patch_id,
                    violation_type=violation.violation_type,
                    action='escalate',
                    target='parliament',
                    confidence=1.0,
                    rationale='Critical violation requires Parliament review',
                    safe_to_auto_apply=False
                ))
        
        return fixes
    
    def _generate_summary(
        self, 
        violations: List[Violation], 
        fixes: List[Patch]
    ) -> str:
        """Generate human-readable summary"""
        if not violations:
            return "No violations detected. Output passed all linting checks."
        
        summary_parts = [
            f"Found {len(violations)} violation(s):"
        ]
        
        # Group by type
        by_type: Dict[str, int] = {}
        for v in violations:
            by_type[v.violation_type] = by_type.get(v.violation_type, 0) + 1
        
        for vtype, count in by_type.items():
            summary_parts.append(f"  - {vtype}: {count}")
        
        # Add fix summary
        auto_fixes = sum(1 for f in fixes if f.safe_to_auto_apply)
        if auto_fixes > 0:
            summary_parts.append(f"{auto_fixes} violation(s) can be auto-remediated.")
        
        return '\n'.join(summary_parts)
    
    def _update_memory_cache(self, output: GraceLoopOutput):
        """Add output to recent memory cache"""
        self.recent_memory_cache.append(output)
        
        # Keep cache size limited
        if len(self.recent_memory_cache) > self.max_cache_size:
            self.recent_memory_cache.pop(0)
    
    def auto_remediate(self, report: LintReport) -> Optional[Dict[str, Any]]:
        """
        Attempt automatic remediation of violations.
        
        Returns:
            Patch application result or None if not auto-remediable
        """
        if not report.auto_remediable:
            logger.info("Report not auto-remediable, skipping")
            return None
        
        applied_patches = []
        
        for fix in report.suggested_fixes:
            if fix.safe_to_auto_apply:
                logger.info(f"Auto-applying patch: {fix.patch_id}")
                applied_patches.append({
                    'patch_id': fix.patch_id,
                    'action': fix.action,
                    'target': fix.target,
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        return {
            'remediated': True,
            'patches_applied': applied_patches,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def set_governance_anchors(self, anchors: Dict[str, Any]):
        """Set governance policy anchors for drift detection"""
        self.governance_anchors = anchors
    
    def set_causal_dependencies(self, dependencies: Dict[str, List[str]]):
        """Set causal dependency map"""
        self.causal_dependencies = dependencies
    
    def add_knowledge_artifact(self, artifact_id: str, artifact_data: Dict[str, Any]):
        """Add knowledge artifact for validation"""
        self.knowledge_artifacts[artifact_id] = artifact_data
