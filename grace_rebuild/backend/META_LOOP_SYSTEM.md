# Meta-Loop Recommendation Application System

## Overview

The Meta-Loop system is a **self-optimizing framework** that analyzes GRACE's operational performance and automatically generates, approves, and applies recommendations to improve system effectiveness.

### Three Levels of Meta-Analysis

1. **Level 1: Meta-Loop** - Analyzes operational effectiveness and generates recommendations
2. **Level 2: Meta-Meta Loop** - Evaluates whether meta-loop changes actually improved performance
3. **Level 3: Meta-Meta-Meta** - (Future) Optimizes the meta-optimization process itself

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OPERATIONAL LOOPS                        │
│  (Reflection, Learning, Task Generation, etc.)             │
└─────────────────────┬───────────────────────────────────────┘
                      │ monitors
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 LEVEL 1: META-LOOP                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Analyze     │→ │  Generate    │→ │  Submit for  │     │
│  │  Performance │  │  Recomm.     │  │  Approval    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│               APPROVAL & APPLICATION                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Validate    │→ │  Governance  │→ │  Apply &     │     │
│  │  Safety      │  │  Check       │  │  Measure     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│            LEVEL 2: META-META EVALUATION                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Measure     │→ │  Evaluate    │→ │  Rollback if │     │
│  │  Before/After│  │  Improvement │  │  Worse       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Meta-Loop Engine (`meta_loop.py`)

**Purpose**: Analyzes operational effectiveness and generates recommendations

**Key Functions**:
- `analyze_and_optimize()` - Main analysis loop
- `_analyze_task_completion_rate()` - Checks if auto-tasks are being completed
- `_analyze_reflection_utility()` - Checks if reflections lead to actions
- `_submit_actionable_recommendation()` - Converts analysis to actionable recommendation

**Recommendations Generated**:
- Threshold changes (e.g., task creation threshold)
- Interval changes (e.g., reflection loop speed)
- Priority changes (e.g., task importance)

### 2. Recommendation Applicator (`meta_loop_engine.py`)

**Purpose**: Applies recommendations with safety checks and metrics

**Key Methods**:
- `validate_recommendation()` - Safety checks before applying
- `apply_threshold_change()` - Modify operational thresholds
- `apply_interval_change()` - Adjust loop intervals
- `apply_priority_change()` - Change task priorities
- `measure_before_metrics()` - Capture baseline performance
- `measure_after_metrics()` - Evaluate effectiveness
- `rollback_change()` - Revert if performance degrades

**Safety Limits**:
```python
{
    "task_threshold": {"min": 1, "max": 10},
    "reflection_interval": {"min": 10, "max": 3600},
    "task_priority": {"min": 1, "max": 10},
    "completion_threshold": {"min": 0.1, "max": 1.0}
}
```

### 3. Approval Queue (`meta_loop_approval.py`)

**Purpose**: Manages approval workflow for recommendations

**Key Features**:
- **Risk Assessment**: Categorizes changes as low/medium/high risk
- **Auto-Approval**: Low-risk, high-confidence changes auto-approved
- **Manual Review**: Risky changes require human approval
- **Governance Integration**: Enforces policies on meta-changes
- **Verification**: All applied changes are cryptographically signed

**Workflow**:
1. Recommendation submitted to queue
2. Risk level assessed
3. If low-risk & high-confidence → auto-approved
4. If medium/high-risk → awaits manual approval
5. On approval → governance check → apply → verify → sign

### 4. Meta-Meta Evaluation (`meta_loop.py`)

**Purpose**: Evaluates whether meta-loop changes actually helped

**Key Method**:
- `evaluate_improvement()` - Compares before/after metrics

**Conclusions**:
- `Improvement` - Metric improved by >10%
- `No significant change` - Within ±10%
- `Regression` - Degraded by >10% (triggers rollback)

## API Endpoints

### GET /api/meta/recommendations/pending
List all recommendations awaiting approval

**Response**:
```json
[
  {
    "id": 1,
    "type": "threshold_change",
    "target": "task_threshold",
    "current": "3",
    "proposed": "5",
    "text": "Increase threshold to reduce noise",
    "confidence": 0.75,
    "risk_level": "medium",
    "submitted_at": "2025-11-02T10:30:00Z"
  }
]
```

### POST /api/meta/recommendations/{id}/approve
Approve and apply a recommendation

**Body**:
```json
{
  "reason": "Approved after review"
}
```

**Response**:
```json
{
  "success": true,
  "applied_id": 42,
  "old_value": "3",
  "new_value": "5",
  "before_metrics": {
    "total_tasks_24h": 50,
    "completed_tasks_24h": 15,
    "completion_rate": 0.30
  }
}
```

### POST /api/meta/recommendations/{id}/reject
Reject a recommendation

**Body**:
```json
{
  "reason": "Risk too high, requires further analysis"
}
```

### GET /api/meta/recommendations/applied
View history of applied recommendations with effectiveness

**Response**:
```json
[
  {
    "id": 42,
    "type": "threshold_change",
    "target": "learning.task_threshold",
    "old_value": "3",
    "new_value": "5",
    "applied_by": "admin",
    "applied_at": "2025-11-02T10:35:00Z",
    "effectiveness": 25.5,
    "rolled_back": false,
    "before_metrics": {...},
    "after_metrics": {...}
  }
]
```

### POST /api/meta/recommendations/{applied_id}/rollback
Manually rollback an applied recommendation

### POST /api/meta/recommendations/{applied_id}/measure
Manually trigger effectiveness measurement

### GET /api/meta/recommendations/stats
Get system statistics

**Response**:
```json
{
  "pending": 3,
  "approved": 12,
  "rejected": 2,
  "applied": 12,
  "rolled_back": 1,
  "average_effectiveness": 18.3
}
```

## Usage Examples

### 1. Manual Test Workflow

```python
# Run the test
python grace_rebuild/backend/test_meta_loop_workflow.py
```

This demonstrates:
- Meta-loop generating recommendations
- Recommendations queued for approval
- Auto-approval of safe changes
- Manual approval workflow
- Before/after metrics
- Effectiveness evaluation
- Rollback capability

### 2. API Usage

```bash
# View pending recommendations
curl http://localhost:8000/api/meta/recommendations/pending

# Approve a recommendation
curl -X POST http://localhost:8000/api/meta/recommendations/1/approve \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"reason": "Looks good"}'

# Check effectiveness
curl http://localhost:8000/api/meta/recommendations/applied

# Rollback if needed
curl -X POST http://localhost:8000/api/meta/recommendations/42/rollback \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"reason": "Performance degraded"}'
```

### 3. Programmatic Integration

```python
from meta_loop_approval import approval_queue
from meta_loop_engine import recommendation_applicator

# Submit custom recommendation
rec_id = await approval_queue.submit_for_approval(
    meta_analysis_id=1,
    recommendation_type="threshold_change",
    target="task_threshold",
    current_value=3,
    proposed_value=5,
    recommendation_text="Manual optimization",
    confidence=0.8,
    risk_level="low",
    payload={"component": "learning"}
)

# Approve and apply
result = await approval_queue.approve_recommendation(
    rec_id, 
    approver="admin",
    reason="Manual override"
)

# Measure effectiveness after 24 hours
metrics = await recommendation_applicator.measure_after_metrics(
    result['applied_id']
)
```

## Integration with Other Systems

### Governance

All meta-loop changes go through governance checks:
- High-risk changes require review
- Very short intervals (< 30s) are blocked
- All changes are logged

See: `seed_meta_governance.py`

### Verification

All applied recommendations are cryptographically signed:
- Immutable audit trail
- Tamper-proof record
- Non-repudiation

### Trigger Mesh

Meta-meta regressions trigger events:
```python
# On >20% performance degradation
trigger_mesh.publish(TriggerEvent(
    event_type="meta.regression_detected",
    ...
))
```

## Best Practices

### 1. Safety First
- Always validate recommendations before applying
- Start with conservative thresholds
- Monitor effectiveness closely
- Use rollback if performance degrades

### 2. Gradual Rollout
- Test on low-risk changes first
- Increase confidence thresholds gradually
- Monitor meta-meta evaluations
- Adjust auto-approval criteria over time

### 3. Human Oversight
- Review high-risk recommendations manually
- Check governance audit logs regularly
- Monitor rollback frequency
- Investigate repeated failures

### 4. Metrics-Driven
- Always capture before/after metrics
- Wait sufficient time before evaluating
- Use meta-meta evaluations for decisions
- Track long-term trends

## Database Tables

### `meta_analyses`
Stores Level 1 meta-loop analyses

### `recommendation_queue`
Pending recommendations awaiting approval

### `applied_recommendations`
History of applied changes with metrics

### `meta_meta_evaluations`
Level 2 evaluations of meta-loop effectiveness

### `meta_loop_configs`
Current configuration values

## Future Enhancements

1. **Machine Learning**: Train models to predict recommendation effectiveness
2. **A/B Testing**: Run parallel configurations and compare
3. **Multi-Agent**: Multiple meta-loops optimizing different aspects
4. **Causal Analysis**: Understand why changes helped/hurt
5. **Automated Rollback**: Trigger based on real-time metrics
6. **Meta-Meta-Meta**: Optimize the optimization of the optimization 🤯

## Troubleshooting

### Recommendation Not Auto-Approved
- Check confidence level (must be ≥0.8 for low-risk)
- Check risk level (must be "low")
- Check interval (must be ≥60s for auto-approval)

### Governance Blocking Changes
- Review governance policies in database
- Check audit logs for denial reasons
- Adjust policies if too restrictive

### Effectiveness Not Measured
- Ensure sufficient time has passed (default: 24h)
- Check that metrics are being collected
- Verify recommendation was actually applied

### Rollback Not Working
- Check if already rolled back
- Verify old_value exists
- Check configuration table for current state
