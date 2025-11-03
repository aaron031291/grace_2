# GraceCognitionLinter - Contradiction & Drift Detection

## Overview

The GraceCognitionLinter runs **BEFORE governance** to detect contradictions, policy drift, and inconsistencies. It acts as a pre-flight check ensuring outputs are internally coherent before entering the governance pipeline.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              GraceCognitionLinter                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────┐         │
│  │         Input: GraceLoopOutput             │         │
│  └────────────────┬───────────────────────────┘         │
│                   │                                     │
│         ┌─────────┴──────────┐                          │
│         │                    │                          │
│  ┌──────▼──────┐    ┌────────▼────────┐                │
│  │   Static    │    │    Dynamic      │                │
│  │   Checks    │    │    Checks       │                │
│  └──────┬──────┘    └────────┬────────┘                │
│         │                    │                          │
│         │  Direct Conflicts  │  Memory Conflicts        │
│         │  Policy Drift      │  Knowledge Conflicts     │
│         │  Causal Mismatches │  Constitutional Check    │
│         │  Temporal Issues   │                          │
│         │                    │                          │
│         └─────────┬──────────┘                          │
│                   │                                     │
│         ┌─────────▼──────────┐                          │
│         │   Violation List   │                          │
│         └─────────┬──────────┘                          │
│                   │                                     │
│         ┌─────────▼──────────┐                          │
│         │   Fix Generation   │                          │
│         │   - Auto-remediate │                          │
│         │   - Escalate       │                          │
│         │   - Suggest merge  │                          │
│         └─────────┬──────────┘                          │
│                   │                                     │
│         ┌─────────▼──────────┐                          │
│         │    LintReport      │                          │
│         │  - Violations      │                          │
│         │  - Fixes           │                          │
│         │  - Severity        │                          │
│         └────────────────────┘                          │
└─────────────────────────────────────────────────────────┘
```

## Violation Types

### 1. Direct Conflicts
**What**: Contradictory statements within the same output

**Examples**:
- "This is true" AND "This is false"
- "Action is allowed" AND "Action is forbidden"
- "Should execute" AND "Should not execute"

**Detection**: Pattern matching for opposing terms in result content

**Fix**: Remove one statement or escalate for reconciliation

### 2. Policy Drift
**What**: Violations of anchored governance policies

**Examples**:
- Policy tag marked as 'violation'
- Required approval missing constitutional compliance
- Governance constraints not met

**Detection**: Check policy_tags and constitutional_compliance fields

**Fix**: Add missing compliance or escalate to governance review

### 3. Causal Mismatches
**What**: Contradicts causal dependencies

**Examples**:
- Meta loop executing before required reflection
- Hunter running without causal chain
- Missing prerequisite components

**Detection**: Compare causal_chain in context against required dependencies

**Fix**: Re-run with proper causal ordering

### 4. Temporal Inconsistencies
**What**: Timestamp or temporal logic violations

**Examples**:
- Citation with future timestamp
- Output already expired
- Invalid time sequence

**Detection**: Validate all timestamps against current time

**Fix**: Auto-correct timestamps (safe to auto-apply)

### 5. Memory Conflicts
**What**: Contradicts recent memory or history

**Examples**:
- Same component returning opposite results
- Recent decision reversed without explanation
- Unexplained state change

**Detection**: Compare against recent_memory_cache (last 100 items)

**Fix**: Escalate for specialist reconciliation

### 6. Knowledge Conflicts
**What**: Citation confidence exceeds source trust

**Examples**:
- Citing low-trust source with high confidence
- Artifact trust mismatch
- Invalid source references

**Detection**: Validate citations against knowledge_artifacts

**Fix**: Adjust citation confidence to match source

### 7. Constitutional Misalignment
**What**: Constitutional AI violations

**Examples**:
- Requires approval but not compliant
- Errors without diagnostic info
- Missing transparency markers

**Detection**: Check constitutional_compliance and diagnostics

**Fix**: Run constitutional verification before execution

## Usage

### Basic Linting

```python
from cognition.GraceCognitionLinter import GraceCognitionLinter
from cognition.GraceLoopOutput import GraceLoopOutput

linter = GraceCognitionLinter()

# Lint output
output = create_grace_output()
report = linter.lint(output)

if report.passed:
    print("✅ Lint passed")
    proceed_to_governance(output)
else:
    print(f"❌ {len(report.violations)} violations found")
    print(report.summary)
    handle_violations(report)
```

### With Context

```python
# Include recent memory for conflict detection
context = {
    'recent_memory': get_recent_memory(limit=100),
    'knowledge_base': load_knowledge_artifacts()
}

report = linter.lint(output, context=context)
```

### Auto-Remediation

```python
report = linter.lint(output)

if report.auto_remediable:
    result = linter.auto_remediate(report)
    if result['remediated']:
        print(f"Auto-fixed {len(result['patches_applied'])} violations")
        # Re-lint to verify
        report = linter.lint(output)
```

### Configure Dependencies

```python
# Set causal dependencies
linter.set_causal_dependencies({
    'meta': ['reflection', 'hunter'],
    'parliament': ['governance', 'constitutional'],
    'execution': ['verification', 'governance']
})

# Set governance anchors
linter.set_governance_anchors({
    'safety_policy': {...},
    'data_privacy': {...},
    'reversibility': {...}
})

# Add knowledge artifacts
linter.add_knowledge_artifact('source_1', {
    'trust_score': 0.85,
    'verified': True
})
```

## LintReport Model

```python
@dataclass
class LintReport:
    output_id: str
    severity: ViolationSeverity  # INFO, WARNING, ERROR, CRITICAL
    violations: List[Violation]
    suggested_fixes: List[Patch]
    auto_remediable: bool
    passed: bool
    summary: str
    created_at: datetime
```

## Violation Model

```python
@dataclass
class Violation:
    violation_type: str
    severity: ViolationSeverity
    description: str
    location: str
    conflicting_items: List[str]
    suggested_action: Optional[str]
    metadata: Dict[str, Any]
```

## Patch Model

```python
@dataclass
class Patch:
    patch_id: str
    violation_type: str
    action: str  # remove, replace, merge, escalate
    target: str
    replacement: Optional[Any]
    confidence: float
    rationale: str
    safe_to_auto_apply: bool
```

## Integration Pipeline

### Before Governance

```python
def process_output(output: GraceLoopOutput):
    # 1. LINT FIRST
    lint_report = linter.lint(output, context=get_context())
    
    if not lint_report.passed:
        if lint_report.severity == ViolationSeverity.CRITICAL:
            # Block immediately
            raise CriticalViolationError(lint_report)
        elif lint_report.auto_remediable:
            # Auto-fix minor issues
            linter.auto_remediate(lint_report)
        else:
            # Log and continue with warnings
            log_violations(lint_report)
    
    # 2. GOVERNANCE
    governance_result = governance.verify(output)
    
    # 3. PARLIAMENT (if needed)
    if governance_result.requires_vote:
        parliament.vote(output)
    
    # 4. EXECUTE
    execute(output)
```

### With QuorumEngine

```python
# Lint all proposals before consensus
task = DecisionTask(...)
for proposal in task.specialist_proposals:
    report = linter.lint(proposal.output)
    if not report.passed:
        # Penalize in quorum scoring
        proposal.trust_score *= 0.8

decision = quorum_engine.deliberate(task)
```

### With FeedbackIntegrator

```python
# Lint before integrating feedback
feedback_output = reflection.generate_feedback()
lint_report = linter.lint(feedback_output)

if lint_report.passed:
    feedback_integrator.integrate(feedback_output)
else:
    # Flag for review
    flag_for_manual_review(feedback_output, lint_report)
```

## Severity Levels

### INFO
- Minor issues
- No blocking required
- Informational only

### WARNING
- Potential problems
- Log and continue
- Monitor for patterns

### ERROR
- Serious violations
- Should block non-critical flows
- Require manual review

### CRITICAL
- Immediate blocking
- Constitutional violations
- Safety concerns
- Escalate to Parliament

## Remediation Strategies

### Auto-Remediate (Safe)
- Timestamp corrections
- Format normalization
- Minor metadata fixes

### Escalate (Requires Review)
- Direct conflicts
- Memory contradictions
- Policy violations
- Constitutional issues

### Merge (Complex)
- Reconcile opposing views
- Combine partial truths
- Generate consensus statement

### Remove (Destructive)
- Remove conflicting statement
- Requires confidence > 0.8
- Only for clear contradictions

## Best Practices

1. **Always Lint Before Governance**
   - Catches internal issues early
   - Reduces governance overhead
   - Improves audit quality

2. **Configure Dependencies**
   - Set causal dependencies for components
   - Update governance anchors regularly
   - Maintain knowledge artifacts

3. **Handle Violations Appropriately**
   - CRITICAL: Block immediately
   - ERROR: Review before execution
   - WARNING: Log and monitor
   - INFO: Track metrics

4. **Use Auto-Remediation Carefully**
   - Only for safe_to_auto_apply patches
   - Re-lint after remediation
   - Log all auto-fixes

5. **Track Patterns**
   - Monitor violation types over time
   - Identify systematic issues
   - Improve component quality

## Testing

```bash
cd grace_rebuild/backend
pytest tests/test_cognition_linter.py -v
```

## Metrics

Track these for system health:

- **Lint Pass Rate**: % of outputs passing lint
- **Violation Distribution**: Which types occur most
- **Auto-Remediation Rate**: % fixed automatically
- **Severity Breakdown**: CRITICAL vs ERROR vs WARNING
- **Component Quality**: Violations per component

## Example Reports

### Clean Output
```
✅ No violations detected. Output passed all linting checks.
```

### With Violations
```
❌ Found 3 violation(s):
  - direct_conflict: 1
  - policy_drift: 1
  - temporal_inconsistency: 1

1 violation(s) can be auto-remediated.
```

### Critical Violation
```
🚨 CRITICAL: Requires approval but not constitutionally compliant
   Location: hunter
   Action: Run constitutional verification before execution
```

## Future Enhancements

- [ ] Machine learning for conflict detection
- [ ] Natural language understanding for contradictions
- [ ] Semantic similarity for memory conflicts
- [ ] Auto-reconciliation with confidence thresholds
- [ ] Pattern-based violation prediction
