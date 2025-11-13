# GRACE Self-Healing Agent Lifecycle

## State Machine

The self-healing agent operates as a finite state machine with the following states and transitions:

```
IDLE → DETECTING → ANALYZING → DECIDING → EXECUTING → VERIFYING → RESOLVED
                 ↓             ↓           ↓            ↓             ↓
                 └─────────────┴───────────┴────────────┴─────────────→ FAILED
                                                                          ↓
                                                                       ROLLBACK
```

## States

### 1. IDLE
**Description**: Agent is monitoring metrics but no anomalies detected  
**Duration**: Continuous  
**Transitions**: → DETECTING (when anomaly threshold exceeded)

**Metrics Monitored**:
- CPU usage across all services
- Memory consumption
- Error rates
- Response times (p50, p95, p99)
- Queue depths
- Database connection pools

### 2. DETECTING
**Description**: Anomaly detected, collecting context  
**Duration**: 5-30 seconds  
**Transitions**: → ANALYZING (context collected) | → IDLE (false positive)

**Actions**:
- Collect recent metrics (last 15 minutes)
- Capture error logs
- Snapshot service health
- Identify affected services/hosts
- Calculate confidence score

**Exit Criteria**:
- Confidence score > 85%: Proceed to ANALYZING
- Confidence score < 85%: Return to IDLE (log for review)

### 3. ANALYZING
**Description**: Analyzing root cause of anomaly  
**Duration**: 10-60 seconds  
**Transitions**: → DECIDING (root cause identified) | → FAILED (cannot determine cause)

**Actions**:
- Pattern matching against known issues
- ML-based classification
- Correlation analysis (multiple metrics)
- Historical incident lookup
- Service dependency analysis

**Outputs**:
- Root cause hypothesis
- Affected components list
- Severity assessment
- Recommended actions

### 4. DECIDING
**Description**: Selecting remediation strategy  
**Duration**: 5-15 seconds  
**Transitions**: → EXECUTING (action selected) | → FAILED (no safe action available)

**Decision Tree**:
```yaml
if severity == "critical" and confidence > 0.95:
  action = immediate_mitigation
elif severity == "high" and confidence > 0.85:
  action = standard_remediation
elif severity == "medium":
  action = monitored_remediation
else:
  action = alert_only
```

**Safety Checks**:
- Not in change freeze window
- Not during business-critical hours (configurable)
- Action hasn't failed recently (cooldown period)
- Impacted user count acceptable
- Rollback plan available

### 5. EXECUTING
**Description**: Executing remediation action  
**Duration**: Variable (30 seconds - 10 minutes)  
**Transitions**: → VERIFYING (execution complete) | → FAILED (execution error)

**Common Actions**:
- Restart service (rolling restart)
- Scale resources (horizontal/vertical)
- Kill long-running queries
- Clear cache
- Rollback deployment
- Redirect traffic
- Enable circuit breaker

**Execution Patterns**:
- **Gradual**: Apply to one instance, verify, then proceed
- **Parallel**: Apply to multiple instances simultaneously
- **Phased**: Apply in waves (10%, 50%, 100%)

**Monitoring During Execution**:
- Watch for secondary failures
- Monitor error rates
- Track response times
- Verify expected metrics improvement

### 6. VERIFYING
**Description**: Verifying remediation was successful  
**Duration**: 2-5 minutes  
**Transitions**: → RESOLVED (success) | → ROLLBACK (verification failed)

**Verification Checks**:
- Anomaly metric returned to normal range
- No new errors introduced
- Service health checks passing
- User-facing metrics acceptable
- No cascading failures

**Success Criteria**:
```python
def verify_success(original_metric, current_metric, threshold):
    improvement = (original_metric - current_metric) / original_metric
    return improvement >= threshold  # e.g., 70% improvement

# Example:
# Original error rate: 10%
# Current error rate: 2%
# Improvement: 80% → SUCCESS
```

### 7. RESOLVED
**Description**: Issue successfully remediated  
**Duration**: N/A (terminal state)  
**Transitions**: → IDLE (monitoring resumes)

**Actions**:
- Log incident summary
- Update success metrics
- Send notification (Slack, PagerDuty resolution)
- Create incident report
- Update ML model (positive feedback)

### 8. FAILED
**Description**: Remediation failed or unsafe to proceed  
**Duration**: N/A (terminal state)  
**Transitions**: → ROLLBACK (if action was taken) | → IDLE (if no action taken)

**Failure Reasons**:
- Low confidence in diagnosis
- No safe remediation action available
- Execution error
- Safety checks failed
- Change freeze active

**Actions**:
- Log failure reason
- Alert on-call engineer
- Preserve context for debugging
- Update ML model (negative feedback)

### 9. ROLLBACK
**Description**: Rolling back remediation attempt  
**Duration**: 30 seconds - 5 minutes  
**Transitions**: → IDLE (rollback complete)

**Actions**:
- Revert configuration changes
- Restore previous deployment
- Scale back to original resources
- Re-enable disabled components
- Verify system returned to pre-action state

**Rollback Safety**:
- Automatic rollback if verification fails
- Manual rollback available via API
- Preserve original state before any action

---

## Lifecycle Timing

### Typical Timeline (Fast Path - Success)
```
00:00 - IDLE: Anomaly detected
00:05 - DETECTING: Context collected
00:15 - ANALYZING: Root cause identified (high CPU from slow query)
00:25 - DECIDING: Action selected (kill slow query)
00:30 - EXECUTING: Query terminated
00:35 - VERIFYING: Metrics improving
02:35 - RESOLVED: All metrics normal
```
**Total Time**: ~2.5 minutes

### Typical Timeline (Slow Path - Rollback)
```
00:00 - IDLE: Anomaly detected
00:10 - DETECTING: Context collected
00:30 - ANALYZING: Root cause unclear, hypothesis: memory leak
00:45 - DECIDING: Action selected (restart service)
01:00 - EXECUTING: Rolling restart initiated
03:00 - VERIFYING: Error rate increased (not improving)
03:10 - ROLLBACK: Reverting restart (cancel rolling restart)
04:00 - IDLE: Alert engineer for manual investigation
```
**Total Time**: ~4 minutes (unsuccessful, escalated)

---

## Context Preservation

At each state transition, context is preserved:

```json
{
  "run_id": "sh-run-20250114-142347",
  "states": [
    {
      "state": "IDLE",
      "timestamp": "2025-01-14T14:23:47Z",
      "duration_ms": 0
    },
    {
      "state": "DETECTING",
      "timestamp": "2025-01-14T14:23:47Z",
      "duration_ms": 5230,
      "context": {
        "trigger_metric": "cpu_usage",
        "trigger_value": 92.3,
        "threshold": 90.0,
        "affected_services": ["api-gateway", "auth-service"],
        "confidence": 0.94
      }
    },
    {
      "state": "ANALYZING",
      "timestamp": "2025-01-14T14:23:52Z",
      "duration_ms": 12450,
      "context": {
        "root_cause": "slow_database_query",
        "evidence": [
          "db_query_time_max: 127s",
          "db_connection_pool: 98/100",
          "similar_pattern_match: INC-2024-0156"
        ],
        "confidence": 0.91
      }
    },
    {
      "state": "DECIDING",
      "timestamp": "2025-01-14T14:24:05Z",
      "duration_ms": 3200,
      "context": {
        "selected_action": "kill_long_running_queries",
        "alternatives_considered": [
          "restart_database",
          "scale_database_nodes"
        ],
        "safety_checks_passed": true
      }
    }
  ]
}
```

---

## Playbook Integration

Each state can execute playbook steps:

```yaml
playbook: high_cpu_remediation
states:
  DETECTING:
    actions:
      - collect_metrics: ["cpu", "memory", "io"]
      - snapshot_processes: top 20
  
  ANALYZING:
    actions:
      - pattern_match: known_cpu_issues
      - ml_classify: anomaly_type
  
  DECIDING:
    rules:
      - if: "ml_classification == 'slow_query'"
        action: kill_queries
      - if: "ml_classification == 'infinite_loop'"
        action: restart_service
  
  EXECUTING:
    action: kill_queries
    parameters:
      query_time_threshold: 30s
      max_queries_to_kill: 10
  
  VERIFYING:
    checks:
      - metric: cpu_usage
        expected: "< 70%"
        duration: 2m
```

---

## Monitoring & Observability

### Metrics Tracked

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `self_healing_runs_total` | Total healing attempts | - |
| `self_healing_success_rate` | % successful remediations | < 80% |
| `self_healing_duration_seconds` | Time to resolve | p95 > 300s |
| `self_healing_rollback_rate` | % of rollbacks | > 15% |
| `state_transition_duration_ms` | Time in each state | - |

### Dashboards

**Self-Healing Overview**:
- Runs per hour (timeline)
- Success vs. Failed (pie chart)
- State transition flow (Sankey diagram)
- Average resolution time (gauge)

**State Durations**:
- DETECTING: p50, p95, p99
- ANALYZING: p50, p95, p99
- EXECUTING: p50, p95, p99
- VERIFYING: p50, p95, p99

---

## Failure Modes & Recovery

### Stuck in DETECTING
**Cause**: Context collection timeout  
**Recovery**: Auto-transition to IDLE after 60s

### Stuck in ANALYZING
**Cause**: ML model inference timeout  
**Recovery**: Fall back to rule-based analysis after 30s

### Stuck in EXECUTING
**Cause**: Action hanging (no response)  
**Recovery**: Timeout after action-specific duration, transition to ROLLBACK

### Stuck in VERIFYING
**Cause**: Metrics not improving but not worsening  
**Recovery**: After 5 minutes, transition to IDLE and alert engineer

---

## Testing the Lifecycle

### Unit Tests
```python
def test_state_transitions():
    agent = SelfHealingAgent()
    
    # Test IDLE → DETECTING
    agent.trigger_anomaly(metric="cpu_usage", value=95)
    assert agent.state == "DETECTING"
    
    # Test DETECTING → ANALYZING
    agent.collect_context()
    assert agent.state == "ANALYZING"
    assert agent.context.confidence > 0.85
```

### Integration Tests
```python
def test_full_lifecycle_success():
    agent = SelfHealingAgent()
    
    # Simulate high CPU anomaly
    inject_anomaly("cpu_spike")
    
    # Wait for resolution
    wait_for_state("RESOLVED", timeout=300)
    
    # Verify
    assert get_metric("cpu_usage") < 70
    assert agent.get_last_run().outcome == "SUCCESS"
```

### Chaos Tests
```bash
# Test rollback on failed verification
grace chaos inject --type failed_verification
grace self-healing verify --expect-rollback
```

---

**Document Owner**: Platform Team  
**Last Updated**: January 2025  
**References**: Self-Healing Playbook, Incident Runbooks
