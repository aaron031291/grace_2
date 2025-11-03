# 🧠 Cognition System - Quick Start Guide

## Installation

Already installed in `grace_rebuild/backend/cognition/`

## Import

```python
from cognition import (
    QuorumEngine,
    GraceCognitionLinter,
    DecisionTask,
    DecisionStrategy,
    RiskLevel,
    ViolationSeverity
)
```

## Basic Usage

### 1. Quorum Consensus

```python
# Initialize
engine = QuorumEngine()

# Create task
task = DecisionTask(
    task_id="my_decision",
    description="Should we proceed?",
    context={},
    strategy=DecisionStrategy.SOFTMAX_WEIGHTED
)

# Add specialist proposals
task.specialist_proposals = [
    reflection_proposal,
    hunter_proposal,
    meta_proposal
]

# Reach consensus
decision = engine.deliberate(task)

print(f"Winner: {decision.chosen_proposal.component}")
print(f"Confidence: {decision.confidence:.2f}")
print(f"Rationale: {decision.rationale}")
```

### 2. Linting

```python
# Initialize
linter = GraceCognitionLinter()

# Lint output
report = linter.lint(output)

if report.passed:
    print("✓ Passed linting")
else:
    print(f"✗ Found {len(report.violations)} violations")
    for v in report.violations:
        print(f"  - {v.violation_type}: {v.description}")
    
    if report.auto_remediable:
        linter.auto_remediate(report)
```

### 3. Full Pipeline

```python
from cognition.integration_example import CognitionPipeline

# Initialize pipeline
pipeline = CognitionPipeline()

# Process decision
result = pipeline.process_decision(
    task_description="Deploy model?",
    specialist_outputs={
        'reflection': reflection_output,
        'hunter': hunter_output,
        'meta': meta_output
    },
    strategy=DecisionStrategy.MIN_RISK,
    risk_level=RiskLevel.HIGH
)

if result['success']:
    # Execute decision
    execute(result['decision']['chosen_proposal'])
    
    # Update trust
    pipeline.update_trust_from_outcome(
        result['task_id'],
        outcome_success=True
    )
```

## Decision Strategies

- **MAJORITY**: Fastest, simple vote
- **SOFTMAX_WEIGHTED**: Balanced probabilistic blend
- **MIN_RISK**: Safest under constraints (use for HIGH/CRITICAL)
- **UNANIMOUS**: All must agree or escalate

## Risk Levels

- **LOW**: Reversible, low impact
- **MEDIUM**: Standard operations
- **HIGH**: Important decisions, use MIN_RISK
- **CRITICAL**: Irreversible, requires UNANIMOUS or MIN_RISK

## Violation Severities

- **INFO**: Informational only
- **WARNING**: Log and monitor
- **ERROR**: Review before execution
- **CRITICAL**: Block immediately

## Configuration

```python
# Set causal dependencies
linter.set_causal_dependencies({
    'meta': ['reflection', 'hunter']
})

# Set governance anchors
linter.set_governance_anchors({
    'safety_policy': config
})

# Add knowledge artifacts
linter.add_knowledge_artifact('source_1', {
    'trust_score': 0.85,
    'verified': True
})
```

## Metrics

```python
# Get pipeline metrics
metrics = pipeline.get_pipeline_metrics()

print(f"Total decisions: {metrics['total_decisions']}")
print(f"Escalation rate: {metrics['escalation_rate']:.2%}")
print(f"Average confidence: {metrics['average_confidence']:.2f}")
```

## Testing

```bash
cd grace_rebuild/backend
pytest tests/test_quorum_engine.py -v
pytest tests/test_cognition_linter.py -v
```

## Documentation

- [QUORUM_CONSENSUS.md](QUORUM_CONSENSUS.md) - QuorumEngine details
- [COGNITION_LINTING.md](COGNITION_LINTING.md) - Linting details
- [COGNITION_CLASSES_8_10_COMPLETE.md](COGNITION_CLASSES_8_10_COMPLETE.md) - Complete status

## Example: Critical Decision

```python
# High-stakes decision with safety constraints
engine = QuorumEngine()
linter = GraceCognitionLinter()

# Lint all proposals first
valid_proposals = []
for name, output in specialist_outputs.items():
    report = linter.lint(output)
    if report.passed or report.auto_remediable:
        if report.auto_remediable:
            linter.auto_remediate(report)
        valid_proposals.append(create_proposal(name, output))

# Critical decision with constraints
task = DecisionTask(
    task_id="critical_deploy",
    description="Deploy to production",
    specialist_proposals=valid_proposals,
    strategy=DecisionStrategy.MIN_RISK,
    risk_level=RiskLevel.CRITICAL,
    constraints=['safety_policy', 'reversibility', 'data_privacy']
)

# Deliberate
decision = engine.deliberate(task)

# Final lint
final_report = linter.lint(decision.chosen_proposal)

if decision.governance_validated and final_report.passed:
    execute(decision.chosen_proposal)
else:
    escalate_to_parliament(decision)
```

---

**Ready to use!** ✅
