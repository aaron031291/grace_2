# Intelligent Multi-Source Self-Healing Triggers

## Overview

GRACE's self-healing system is triggered by **multiple intelligent subsystems**, creating a comprehensive, multi-layered detection and response system that operates proactively across all domains.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Intelligent Trigger Manager                     │
│                                                               │
│  Subscribes to 8 Event Types from 4 Intelligent Subsystems  │
└───────────────────┬─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  Meta Loop       │    │  Proactive ML/DL │
│  Supervisor      │    │  Intelligence    │
│                  │    │                  │
│ • Directives     │    │ • Forecasts      │
│ • Systemic       │    │ • Capacity       │
│   Issues         │    │ • Risk           │
│                  │    │ • Drift          │
└──────────────────┘    └──────────────────┘
        │                       │
        └───────────┬───────────┘
                    ▼
┌──────────────────┐    ┌──────────────────┐
│  Agentic Spine   │    │  Immutable Log   │
│                  │    │  Analyzer        │
│ • Cross-Domain   │    │                  │
│   Alerts         │    │ • Patterns       │
│ • Health         │    │ • Sequences      │
│   Degradation    │    │ • Performance    │
└──────────────────┘    └──────────────────┘
        │                       │
        └───────────┬───────────┘
                    ▼
        ┌───────────────────────┐
        │  Self-Healing System  │
        │  • Scheduler          │
        │  • Trust Core Check   │
        │  • Execution          │
        └───────────────────────┘
```

## Trigger Sources

### 1. Meta Loop Supervisor

**Purpose:** Detects systemic issues through cross-domain oversight

**Event Types:**
- `meta_loop.directive` - Optimization directives
- `meta_loop.systemic_issue` - System-wide patterns

**Example Triggers:**

```python
# Meta loop detects repeated playbook failures
{
    "source": "meta_loop",
    "trigger_type": "systemic_issue",
    "diagnosis_code": "meta_loop_optimization",
    "confidence": 0.9,
    "impact": "moderate",
    "reasoning": [
        "Playbook 'restart_service' failing 60% of time",
        "Threshold adjustment needed",
        "Cross-domain correlation detected"
    ],
    "suggested_playbooks": ["adjust_threshold", "investigate_root_cause"]
}
```

**When It Triggers:**
- Success rates drop below baseline
- Cross-domain correlations indicate systemic issues
- Thresholds need adjustment
- Playbooks consistently fail

### 2. Proactive Intelligence (ML/DL)

**Purpose:** Predicts issues using machine learning before they occur

**Event Types:**
- `proactive.anomaly_forecast` - ML anomaly predictions
- `proactive.capacity_prediction` - Capacity shortage forecasts
- `proactive.risk_assessment` - Risk scoring
- `proactive.drift_detected` - Performance drift

**Example Triggers:**

```python
# ML forecasts latency spike in 15 minutes
{
    "source": "proactive_ml",
    "trigger_type": "ml_anomaly_forecast",
    "diagnosis_code": "latency_spike",
    "confidence": 0.87,
    "impact": "high",
    "reasoning": [
        "Latency trend increasing 45% over 10min",
        "Pattern matches historical spike signatures",
        "Traffic patterns indicate sustained load"
    ],
    "suggested_playbooks": ["scale_up_instances", "warm_cache"],
    "metadata": {
        "ml_model": "anomaly_forecaster",
        "predicted_time": "2025-01-15T14:45:00Z",
        "forecast_window": "15 minutes"
    }
}
```

```python
# ML predicts 30% capacity shortfall
{
    "source": "proactive_ml",
    "trigger_type": "ml_capacity_prediction",
    "diagnosis_code": "capacity_shortage_predicted",
    "confidence": 0.82,
    "impact": "medium",
    "reasoning": [
        "Predicted shortfall: 30.2%",
        "Current: 1000 req/s capacity",
        "Predicted demand: 1450 req/s",
        "Time: 2025-01-15T15:00:00Z"
    ],
    "suggested_playbooks": ["scale_up_instances"]
}
```

**When It Triggers:**
- Time-series analysis detects trend changes
- Anomaly forecaster predicts future issues
- Capacity models show shortfall > 10%
- Risk assessment scores > 0.75
- Performance drift exceeds baseline by 30%

### 3. Agentic Spine

**Purpose:** Cross-domain health awareness and coordination

**Event Types:**
- `agentic_spine.cross_domain_alert` - Multi-domain issues
- `agentic_spine.health_degradation` - Component health decline

**Example Triggers:**

```python
# Cross-domain dependency cascade
{
    "source": "agentic_spine",
    "trigger_type": "cross_domain_alert",
    "diagnosis_code": "cross_domain_cascade",
    "confidence": 0.85,
    "impact": "high",
    "reasoning": [
        "Knowledge domain degradation",
        "ML domain dependency affected",
        "Temporal domain at risk"
    ],
    "suggested_playbooks": ["restart_service", "rollback_flag"],
    "metadata": {
        "affected_domains": ["knowledge", "ml", "temporal"],
        "blast_radius": 3
    }
}
```

**When It Triggers:**
- Health graph shows cascade risks
- Multiple domains affected simultaneously
- Dependency chains show degradation
- Cross-domain correlations detected

### 4. Immutable Log Analyzer

**Purpose:** Pattern and sequence detection from audit trail

**Event Types:**
- `immutable_log.pattern_detected` - Recurring patterns
- `immutable_log.anomaly_sequence` - Unusual event sequences

**Example Triggers:**

```python
# Recurring error pattern detected
{
    "source": "immutable_log",
    "trigger_type": "pattern_detected",
    "diagnosis_code": "recurring_error",
    "confidence": 0.88,
    "impact": "high",
    "reasoning": [
        "Pattern: auth_validate errors",
        "Occurrences: 7 times in 10 minutes",
        "Timespan: 10 minutes",
        "Resources: auth_service"
    ],
    "suggested_playbooks": ["investigate_root_cause", "rollback_flag"]
}
```

```python
# Anomalous error cascade
{
    "source": "immutable_log",
    "trigger_type": "anomaly_sequence",
    "diagnosis_code": "error_cascade",
    "confidence": 0.85,
    "impact": "critical",
    "reasoning": [
        "database.query:error",
        "reflection.generate:error",
        "task_executor.execute:failed",
        "trigger_mesh.publish:blocked"
    ],
    "suggested_playbooks": ["immediate_investigation", "restart_service"]
}
```

**When It Triggers:**
- Same error occurs 3+ times in 10 minutes
- Error cascades across multiple components
- Performance degradation trend detected
- Unusual action sequences observed

## Unified Trigger Flow

### 1. Event Detection

Each subsystem publishes events to trigger mesh:

```python
# Meta Loop
await trigger_mesh.publish(TriggerEvent(
    event_type="meta_loop.systemic_issue",
    source="meta_loop_supervisor",
    resource="knowledge_domain",
    payload={...}
))

# ML/DL
await trigger_mesh.publish(TriggerEvent(
    event_type="proactive.anomaly_forecast",
    source="anomaly_forecaster",
    resource="api_service",
    payload={...}
))

# Agentic Spine
await trigger_mesh.publish(TriggerEvent(
    event_type="agentic_spine.cross_domain_alert",
    source="health_graph",
    resource="database",
    payload={...}
))

# Immutable Log
await trigger_mesh.publish(TriggerEvent(
    event_type="immutable_log.pattern_detected",
    source="log_analyzer",
    resource="auth_service",
    payload={...}
))
```

### 2. Trigger Manager Processing

Intelligent trigger manager processes and enriches:

```python
# Create unified trigger
trigger = IntelligentTrigger(
    trigger_id="ml_forecast_12345",
    source_subsystem="proactive_ml",
    trigger_type="ml_anomaly_forecast",
    service="api_service",
    diagnosis_code="latency_spike",
    confidence=0.87,
    impact="high",
    reasoning=[...],
    suggested_playbooks=["scale_up_instances"],
    metadata={...},
    created_at=datetime.now()
)

# Log to immutable ledger
await immutable_log.append(
    actor="proactive_ml",
    action="intelligent_trigger",
    resource="api_service",
    subsystem="intelligent_triggers",
    payload={...},
    result="emitted"
)
```

### 3. Self-Healing Activation

Trigger converted to self-heal prediction event:

```python
# Emit as self_heal.prediction
await trigger_mesh.publish(TriggerEvent(
    event_type="self_heal.prediction",
    source="proactive_ml",
    actor="intelligent_triggers",
    resource="api_service",
    payload={
        "code": "latency_spike",
        "title": "ML Anomaly Forecast",
        "likelihood": 0.87,
        "impact": "high",
        "suggested_playbooks": ["scale_up_instances"],
        "reasons": [...],
        "source": "proactive_ml"
    }
))
```

### 4. Scheduler Processing

Self-healing scheduler receives and processes:

```python
# Scheduler handles prediction
async def _handle_prediction(self, event):
    # Rate limit check
    ok = self._should_propose(service, diagnosis_code)
    
    if ok:
        # Create PlaybookRun
        run = PlaybookRun(
            service=service,
            status="proposed",
            diagnosis=json.dumps({...}),
            requested_by="intelligent_triggers"
        )
        
        # Check for autonomous approval
        blast_radius = await self._estimate_blast_radius(service)
        
        if can_auto_approve:
            decision = await governance_engine.check(...)
            if decision["decision"] == "allow":
                run.status = "approved"
```

## Subsystem Logging Standards

All subsystems **must** log to immutable ledger using the integration helper:

```python
from backend.immutable_log_integration import get_subsystem_logger

# Get logger for your subsystem
logger = get_subsystem_logger("my_subsystem")

# Log actions
await logger.log_action(
    actor="system",
    action="process_data",
    resource="data_pipeline",
    result="success",
    payload={"records": 1000, "duration_ms": 245}
)

# Log errors
await logger.log_error(
    actor="worker_3",
    action="transform_data",
    resource="dataset_123",
    error=exception
)

# Log decisions
await logger.log_decision(
    actor="policy_engine",
    decision_type="approval",
    resource="deployment_456",
    decision="approved",
    reasoning=["low risk", "within window", "trust score > 0.8"],
    confidence=0.92
)

# Log predictions
await logger.log_prediction(
    actor="ml_model",
    prediction_type="capacity",
    resource="api_cluster",
    predicted_value=1500,
    confidence=0.85,
    current_value=1000
)
```

## Benefits of Multi-Source Triggers

### 1. **Comprehensive Coverage**

- **Meta Loop:** Catches systemic, cross-domain issues
- **ML/DL:** Predicts before symptoms appear
- **Agentic Spine:** Detects cross-domain cascades
- **Immutable Log:** Catches recurring patterns

### 2. **Proactive Prevention**

- ML forecasts trigger preventive actions
- Meta loop optimizations prevent future issues
- Pattern detection stops recurring problems
- Cross-domain awareness prevents cascades

### 3. **Increased Confidence**

- Multiple sources validate each other
- Higher confidence when sources agree
- Lower false positives through correlation
- Trust core has richer context for decisions

### 4. **Continuous Learning**

- Each trigger recorded in immutable log
- Success/failure tracked per source
- Subsystems learn which triggers are accurate
- Meta loop optimizes trigger thresholds

## Statistics & Monitoring

### View Trigger Statistics

```python
from backend.self_heal.intelligent_triggers import intelligent_trigger_manager

stats = intelligent_trigger_manager.get_stats()
# {
#     "total_triggers": 145,
#     "by_source": {
#         "meta_loop": 23,
#         "proactive_ml": 67,
#         "agentic_spine": 31,
#         "immutable_log": 24
#     },
#     "by_type": {
#         "ml_anomaly_forecast": 35,
#         "pattern_detected": 18,
#         "systemic_issue": 12,
#         ...
#     },
#     "avg_confidence": 0.82
# }
```

### View Subsystem Logging Status

```python
from backend.immutable_log_integration import subsystem_registry

stats = subsystem_registry.get_subsystem_stats()
# {
#     "self_heal": {
#         "event_counts": {"proposal": 45, "execution": 38},
#         "total_events": 83,
#         "last_logged": "2025-01-15T14:30:22Z"
#     },
#     "meta_loop": {...},
#     "proactive_ml": {...}
# }
```

## Example Scenarios

### Scenario 1: ML Predicts + Meta Loop Confirms

```
14:00 - ML forecasts latency spike (conf: 0.87)
14:01 - Trigger manager emits healing trigger
14:01 - Scheduler proposes "scale_up_instances"
14:02 - Trust core checks: low risk, BR=1
14:02 - AUTO-APPROVED and executed
14:03 - Verification passes
14:05 - Meta loop observes: "ML prediction prevented incident"
14:10 - Meta loop increases ML trigger weight
```

### Scenario 2: Log Pattern + Agentic Spine Alert

```
09:15 - Log analyzer detects recurring auth errors (7x)
09:15 - Agentic spine detects auth domain degradation
09:16 - Both trigger healing (high confidence: 0.92)
09:16 - Scheduler proposes "rollback_flag" (impact: high)
09:17 - Trust core blocks (BR=3, requires approval)
09:18 - Human approves rollback
09:20 - Flag disabled, errors stop
09:21 - Both subsystems record success
```

### Scenario 3: Capacity Prediction + Proactive Scaling

```
11:00 - ML predicts 30% capacity shortfall at 11:15
11:01 - Proactive trigger: "scale_up_instances"
11:02 - Trust core: low risk, preventive action
11:02 - AUTO-APPROVED
11:03 - Instances scaled +2
11:05 - Load arrives, no saturation
11:15 - Meta loop: "Proactive scaling prevented incident"
11:20 - Meta loop adjusts capacity thresholds
```

## Configuration

### Enable/Disable Trigger Sources

```python
# In settings.py or environment
INTELLIGENT_TRIGGERS_ENABLED = True
META_LOOP_TRIGGERS_ENABLED = True
ML_TRIGGERS_ENABLED = True
AGENTIC_TRIGGERS_ENABLED = True
LOG_PATTERN_TRIGGERS_ENABLED = True

# Minimum confidence per source
META_LOOP_MIN_CONFIDENCE = 0.85
ML_MIN_CONFIDENCE = 0.70
AGENTIC_MIN_CONFIDENCE = 0.75
LOG_PATTERN_MIN_CONFIDENCE = 0.80
```

### Trigger Rate Limits

```python
# Maximum triggers per source per hour
MAX_META_LOOP_TRIGGERS_PER_HOUR = 10
MAX_ML_TRIGGERS_PER_HOUR = 20
MAX_AGENTIC_TRIGGERS_PER_HOUR = 15
MAX_LOG_TRIGGERS_PER_HOUR = 25
```

## Future Enhancements

### Phase 2
- [ ] Trigger correlation engine (detect when multiple sources agree)
- [ ] Confidence boosting (increase confidence when sources correlate)
- [ ] False positive tracking per source
- [ ] Adaptive source weighting based on accuracy

### Phase 3
- [ ] Federated learning across trigger sources
- [ ] Causal inference (which trigger sources are root cause vs symptom)
- [ ] Trigger deduplication (merge similar triggers from different sources)
- [ ] Explainable AI for trigger reasoning

---

**GRACE now has 4 intelligent subsystems continuously monitoring, predicting, and preventing issues before they impact users.**
