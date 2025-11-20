# Immune System (AVN) - Complete Implementation

## Overview

The **Immune Kernel (AVN - Autonomous Validation Network)** is Grace's immune system that detects anomalies, executes healing, and protects system integrity.

**This is a production-ready implementation with complete event wiring.**

## Architecture

```
┌───────────────────────────────────────────────────────┐
│              IMMUNE KERNEL (AVN Core)                 │
│  - Anomaly Detection                                   │
│  - Automated Healing                                   │
│  - Trust Adjustments                                   │
│  - Constitutional Risk Monitoring                      │
└───────┬───────────────────────────────────┬───────────┘
        │                                   │
        ▼                                   ▼
┌────────────────┐                 ┌────────────────┐
│  EVENT MESH    │                 │  GOVERNANCE    │
│  Listens:      │                 │  Notify on:    │
│  - anomaly.*   │                 │  - const risk  │
│  - health.*    │                 │  - sec events  │
│  - security.*  │                 └────────────────┘
│                │
│  Emits:        │
│  - healing.*   │
│  - avn.status  │
└────────────────┘
        │
        ▼
┌────────────────┐                 ┌────────────────┐
│ IMMUTABLE LOG  │                 │  LEARNING SYS  │
│ All actions    │                 │  Experiences   │
└────────────────┘                 └────────────────┘
```

## Complete Anomaly Taxonomy

```python
class AnomalyType(Enum):
    # Performance
    LATENCY_SPIKE = "latency_spike"
    THROUGHPUT_DROP = "throughput_drop"
    ERROR_RATE_INCREASE = "error_rate_increase"
    
    # Resource
    MEMORY_LEAK = "memory_leak"
    CPU_SPIKE = "cpu_spike"
    DISK_FULL = "disk_full"
    CONNECTION_POOL_EXHAUSTION = "connection_pool_exhaustion"
    
    # Behavioral
    DRIFT_DETECTED = "drift_detected"
    PATTERN_DEVIATION = "pattern_deviation"
    HTM_ANOMALY = "htm_anomaly"
    
    # Security
    INJECTION_ATTEMPT = "injection_attempt"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    GUARDRAIL_BYPASS = "guardrail_bypass"
    
    # System
    SERVICE_DOWN = "service_down"
    DEPENDENCY_FAILURE = "dependency_failure"
    DEADLOCK_DETECTED = "deadlock_detected"
    CASCADE_FAILURE = "cascade_failure"
```

## Automated Healing Actions

```python
class HealingAction(Enum):
    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    ROLLBACK = "rollback"
    CIRCUIT_BREAKER = "circuit_breaker"
    RATE_LIMIT = "rate_limit"
    KILL_CONNECTION = "kill_connection"
    CLEAR_CACHE = "clear_cache"
    GARBAGE_COLLECT = "garbage_collect"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    QUARANTINE_COMPONENT = "quarantine_component"
    HARDEN_SECURITY = "harden_security"
```

## Event Mesh Integration

### Events Listened To

1. **anomaly.detected** - From testers, metrics, monitors
2. **system.health_check** - From health monitoring
3. **security.event** - From security monitoring

### Events Emitted

1. **avn.healing_executed** - Healing action succeeded
2. **avn.healing_failed** - Healing action failed
3. **avn.status_update** - AVN status changes
4. **governance.constitutional_risk** - Constitutional risk detected
5. **learning.healing_experience** - Healing outcome for learning

## Usage Examples

### Starting the Immune Kernel

```python
from backend.immune.immune_kernel import immune_kernel

# Start AVN
await immune_kernel.start()

# AVN now listens for anomaly events automatically
```

### Emitting Anomaly Events

```python
from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent

# Emit anomaly detection event
event = TriggerEvent(
    event_type="anomaly.detected",
    source="metrics_monitor",
    actor="system",
    resource="api_service",
    payload={
        'anomaly_id': 'anom_001',
        'type': 'latency_spike',
        'severity': 'high',
        'score': 0.85,
        'baseline': 150,  # ms
        'current': 450    # ms
    }
)

await trigger_mesh.emit(event)

# AVN will automatically:
# 1. Log anomaly
# 2. Determine healing action (e.g., scale_up)
# 3. Execute healing
# 4. Emit healing event
# 5. Update trust scores
# 6. Feed learning system
```

### Manual Anomaly Processing

```python
from backend.immune.immune_kernel import immune_kernel, Anomaly, AnomalyType, AnomalySeverity

# Create anomaly
anomaly = Anomaly(
    anomaly_id="manual_001",
    anomaly_type=AnomalyType.MEMORY_LEAK,
    severity=AnomalySeverity.HIGH,
    detector="manual_check",
    affected_resource="worker_pool",
    anomaly_score=0.9,
    baseline_value=512,  # MB
    current_value=2048   # MB
)

# Process through AVN
await immune_kernel.process_anomaly(anomaly)

# AVN will determine RESTART_SERVICE and execute it
```

## Governance Integration

### Constitutional Risk Notification

When anomalies indicate constitutional risk (security events, critical failures), AVN notifies governance:

```python
# In immune_kernel - _notify_governance()

if anomaly.constitutional_risk or anomaly.severity == AnomalySeverity.CRITICAL:
    # Emit governance event
    event = TriggerEvent(
        event_type="governance.constitutional_risk",
        source="immune_kernel",
        payload={
            'anomaly_id': anomaly.anomaly_id,
            'risk_type': 'security',
            'constitutional_risk': True
        }
    )
    await trigger_mesh.emit(event)
```

### Governance Can Block Healing

For high-risk healing actions, check governance first:

```python
from backend.autonomous.governance_wiring import check_avn_action

async def execute_healing_with_governance(anomaly, action):
    # Check governance before healing
    approved = await check_avn_action(
        action=action.value,
        component=anomaly.affected_resource,
        anomaly_id=anomaly.anomaly_id,
        severity=anomaly.severity.value
    )
    
    if not approved:
        print(f"⚠ Governance blocked healing: {action}")
        return None
    
    # Execute healing
    healing = await immune_kernel._execute_healing(anomaly, action)
    return healing
```

## Trust Score Adjustments

AVN automatically adjusts trust scores based on anomalies and healing outcomes:

```python
# Anomaly detected → minor trust penalty
if healing.success:
    await update_trust_score(
        actor=anomaly.affected_resource,
        action_outcome='anomaly_healed',
        context={'anomaly_type': anomaly.anomaly_type.value}
    )

# Healing failed → larger trust penalty
else:
    await update_trust_score(
        actor=anomaly.affected_resource,
        action_outcome='healing_failed',
        context={'requires_escalation': True}
    )
```

## Immutable Logging

All AVN actions are logged:

```python
from backend.logging.avn_logger import avn_logger

# Anomaly logged
await avn_logger.log_anomaly_detected(...)

# Healing logged
await avn_logger.log_healing_action(...)

# Escalations logged
await avn_logger.log_escalation(...)
```

## Learning Integration

Healing experiences feed the learning system:

```python
# Emit learning event after healing
event = TriggerEvent(
    event_type="learning.healing_experience",
    source="immune_kernel",
    payload={
        'anomaly_type': 'memory_leak',
        'healing_action': 'restart_service',
        'success': True,
        'outcome_quality': 1.0
    }
)

await trigger_mesh.emit(event)

# Learning system uses this to:
# - Improve anomaly detection
# - Optimize healing strategies
# - Predict failure patterns
```

## Statistics & Monitoring

```python
stats = immune_kernel.get_stats()

# {
#     'anomalies_detected': 342,
#     'healing_attempts': 315,
#     'healing_successes': 298,
#     'success_rate': 0.946,
#     'escalations': 17,
#     'active_anomalies': 3
# }
```

## Complete Event Wiring

Add to [trigger_mesh.yaml](file:///c:/Users/aaron/grace_2/config/trigger_mesh.yaml):

```yaml
# AVN Events
- event_type: anomaly.detected
  description: Anomaly detected by monitoring systems
  publishers:
    - metrics_monitor
    - health_monitor
    - security_monitor
    - adversarial_tester
  subscribers:
    - immune_kernel
    - immutable_log
    - metrics_collector
  requires_constitutional_validation: false
  min_trust_score: 0.6

- event_type: avn.healing_executed
  description: AVN executed healing action
  publishers:
    - immune_kernel
  subscribers:
    - immutable_log
    - metrics_collector
    - learning_system
  requires_constitutional_validation: false
  min_trust_score: 0.8

- event_type: avn.healing_failed
  description: AVN healing action failed
  publishers:
    - immune_kernel
  subscribers:
    - alert_system
    - immutable_log
    - escalation_engine
  requires_constitutional_validation: false
  min_trust_score: 0.7

- event_type: governance.constitutional_risk
  description: AVN detected constitutional risk
  publishers:
    - immune_kernel
  subscribers:
    - governance_gate
    - parliament_engine
    - alert_system
    - immutable_log
  requires_constitutional_validation: true
  min_trust_score: 0.9

- event_type: learning.healing_experience
  description: Healing outcome for learning
  publishers:
    - immune_kernel
  subscribers:
    - learning_engine
    - pattern_learner
  requires_constitutional_validation: false
  min_trust_score: 0.7
```

## Healing Decision Matrix

| Anomaly Type | Severity | Healing Action | Governance Check |
|---|---|---|---|
| MEMORY_LEAK | HIGH | RESTART_SERVICE | Yes |
| CPU_SPIKE | MEDIUM | SCALE_UP | No |
| SERVICE_DOWN | CRITICAL | RESTART_SERVICE | Yes |
| INJECTION_ATTEMPT | HIGH | HARDEN_SECURITY | Yes |
| ERROR_RATE_INCREASE | MEDIUM | CIRCUIT_BREAKER | No |
| UNAUTHORIZED_ACCESS | HIGH | KILL_CONNECTION | Yes |
| DATA_EXFILTRATION | CRITICAL | QUARANTINE_COMPONENT | Yes |

## Best Practices

### 1. Always Emit Anomaly Events

```python
# ✅ GOOD - Emit event for AVN
await trigger_mesh.emit(TriggerEvent(
    event_type="anomaly.detected",
    ...
))

# ❌ BAD - Handle anomaly locally without AVN
handle_anomaly_myself(...)
```

### 2. Use Appropriate Severity Levels

```python
# ✅ GOOD - Critical for security
Anomaly(severity=AnomalySeverity.CRITICAL, anomaly_type=INJECTION_ATTEMPT)

# ❌ BAD - Low for critical issue
Anomaly(severity=AnomalySeverity.LOW, anomaly_type=SERVICE_DOWN)
```

### 3. Log All Healing Actions

All healing is automatically logged, but ensure custom healing logs too:

```python
await avn_logger.log_healing_action(...)
```

## Summary

The Immune Kernel provides:

- ✅ **Complete anomaly taxonomy** - 18 anomaly types across 5 categories
- ✅ **Automated healing** - 12 healing actions with auto-execution
- ✅ **Event mesh integration** - Listens and emits events
- ✅ **Governance notification** - Constitutional risk alerting
- ✅ **Trust adjustments** - Automatic trust score updates
- ✅ **Immutable logging** - All actions logged
- ✅ **Learning integration** - Healing experiences feed ML
- ✅ **No stubs** - Production-ready implementation

The system acts as Grace's **immune system**, automatically detecting and healing anomalies while maintaining full transparency and accountability.
