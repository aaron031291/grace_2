# ML Integration & Handshake Protocol - Complete ✓

## Overview

Two final integrations complete the unified logic system:

1. **ML Update Integration** - Logic update metadata flows into ML models for learning and prediction
2. **Component Handshake Protocol** - Secure onboarding for new services/versions

---

## Part 1: ML Update Integration

### What It Does

Feeds logic update signals into ML models so they can:
- **Correlate regressions** with specific rollouts
- **Predict risks** based on past update outcomes
- **Learn patterns** from observation windows
- **Improve trust scores** using crypto/governance context

### Data Flow

```
Logic Update Deployed
  ↓
Observation Window Runs
  ↓
Observation Completes
  ↓
ML Update Integration Triggered
  ↓
├─→ Proactive Intelligence (correlates with metrics)
├─→ Causal Analyzer (adds intervention node)
├─→ Temporal Forecaster (records timeline event)
└─→ Training Pipeline (stores labeled example)
```

### Signals Fed to ML Models

```python
signals = {
    # Update characteristics
    "update_type": "schema" | "code_module" | "playbook",
    "risk_level": 0.25 | 0.50 | 0.75 | 1.0,
    "components_count": 3,
    "components_touched": ["memory_api", "fusion_memory"],
    
    # Capabilities
    "new_capabilities_count": 2,
    "new_metrics_count": 5,
    "schema_changes_count": 1,
    
    # Governance & crypto
    "governance_approved": true,
    "crypto_signed": true,
    "validation_passed": true,
    
    # Observation results
    "stability_score": 0.98,
    "anomalies_count": 0,
    "health_checks_passed": 25,
    "stability_verdict": "stable"
}
```

### Training Labels Created

**Binary Classification:**
```python
{
    "success": true  # stable vs unstable
}
```

**Regression:**
```python
{
    "stability_score": 0.98  # 0.0 - 1.0
}
```

**Multi-class:**
```python
{
    "verdict": 2  # 0=unstable, 1=acceptable, 2=stable
}
```

### Crypto/Governance Context Enrichment

Models now receive crypto/audit context for better trust prediction:

```python
enriched_features = {
    # Base features
    ...base_features,
    
    # Crypto context
    "has_crypto_signature": true,
    "crypto_age_minutes": 15.2,
    
    # Governance context
    "has_governance_approval": true,
    "governance_decision_time": 10.5,
    
    # Audit context
    "has_audit_trail": true,
    "audit_sequence": 12345,
    "audit_integrity_verified": true,
    
    # Composite trust score
    "composite_trust_score": 0.9
}
```

**Trust Score Calculation:**
- Crypto signature present: +0.4
- Recent signature (<1h): +0.1
- Governance approval: +0.3
- Audit integrity verified: +0.2
- **Max score:** 1.0

### Regression Correlation

When regression detected, ML correlates with recent updates:

```python
correlation = {
    "update_id": "update_abc123",
    "correlation_score": 0.85,
    "components_overlap": 2,
    "temporal_proximity_hours": 0.5
}
```

**Scoring:**
- Component overlap: 0-0.5
- Metric overlap: 0-0.3
- Temporal proximity: 0-0.2
- **Threshold:** 0.5 for likely cause

### Usage Example

```python
from backend.ml_update_integration import ml_update_integration

# After observation completes
await ml_update_integration.feed_update_to_models(
    update_id="update_abc123",
    update_summary=summary,
    observation_data=observation
)

# Creates training example
training_example = await ml_update_integration.create_training_labels_from_observation(
    update_id="update_abc123",
    observation=observation
)

# Stores for future training
await ml_update_integration.store_training_example(training_example)

# Later: Correlate regression
correlation = await ml_update_integration.correlate_regression_with_rollout(
    regression_data={
        "detected_at": "2025-11-09T14:00:00Z",
        "components": ["memory_api"],
        "metrics": ["error_rate"]
    },
    time_window_hours=24
)

if correlation:
    print(f"Likely caused by {correlation['update_id']}")
```

---

## Part 2: Component Handshake Protocol

### What It Does

Secure onboarding protocol for new services/versions:
1. Component submits handshake request
2. Hub validates governance + crypto
3. Hub announces to all subsystems
4. Subsystems acknowledge (quorum tracking)
5. Hub marks as integrated
6. Validation window starts

### Protocol Flow

```
New Component
  ↓
1. Submit Handshake Request
  ├─ Component ID, type, capabilities
  ├─ Expected metrics
  ├─ Version
  └─ Crypto signature
  ↓
2. Hub Validates
  ├─ Governance approval
  └─ Crypto signature
  ↓
3. Hub Announces (Trigger Mesh)
  └─ Event: unified_logic.handshake_announce
  ↓
4. Subsystems Acknowledge
  ├─ Agentic Spine → Ack
  ├─ Memory Fusion → Ack + schema reload
  ├─ Metrics Collector → Ack + new metrics
  ├─ Anomaly Watchdog → Ack
  └─ Self-Heal → Ack
  ↓
5. Quorum Check
  └─ All required acks received?
  ↓
6. Integration
  ├─ Mark as integrated
  ├─ Register in component registry
  └─ Log to immutable log
  ↓
7. Validation Window (1 hour)
  └─ Observation with anomaly detection
```

### Required Acknowledgers (Quorum)

```python
required_acks = {
    "agentic_spine",
    "memory_fusion",
    "metrics_collector",
    "anomaly_watchdog",
    "self_heal_scheduler"
}
```

**Quorum met when:** All 5 subsystems acknowledge

### Handshake Request

```python
from backend.component_handshake import component_handshake

handshake_id = await component_handshake.submit_handshake_request(
    component_id="new_ml_model_v2",
    component_type="ml_model",
    capabilities=["prediction", "anomaly_detection"],
    expected_metrics=["model_latency_p95", "prediction_accuracy"],
    version="2.0.0",
    crypto_signature="sha3_..."  # Optional
)

print(f"Handshake ID: {handshake_id}")
```

### Subsystem Acknowledgment

Each subsystem subscribes to handshake announces:

```python
from backend.trigger_mesh import trigger_mesh

async def on_handshake_announce(event):
    """Handle new component handshake"""
    handshake_id = event.payload["handshake_id"]
    component_id = event.payload["component_id"]
    capabilities = event.payload["capabilities"]
    
    # Perform subsystem-specific adjustments
    if "schema_reload" in capabilities:
        await reload_schemas()
    
    if "new_metrics" in capabilities:
        await register_metrics(event.payload["expected_metrics"])
    
    # Send acknowledgment
    from backend.component_handshake import component_handshake
    
    await component_handshake.receive_acknowledgment(
        handshake_id=handshake_id,
        acknowledger="memory_fusion",
        adjustments={
            "schemas_reloaded": True,
            "acl_updated": True
        }
    )

trigger_mesh.subscribe("unified_logic.handshake_announce", on_handshake_announce)
```

### Handshake Status

```python
# Check handshake status
status = component_handshake.get_handshake_status(handshake_id)

print(f"Status: {status['status']}")
print(f"Quorum: {status['acks_received']}/{status['acks_required']}")
print(f"Adjustments: {status['subsystem_adjustments']}")
```

**Example Response:**
```json
{
  "handshake_id": "handshake_a1b2c3",
  "component_id": "new_ml_model_v2",
  "status": "integrated",
  "acks_received": 5,
  "acks_required": 5,
  "quorum_met": true,
  "subsystem_adjustments": {
    "agentic_spine": {"context_updated": true},
    "memory_fusion": {"schemas_reloaded": true},
    "metrics_collector": {"metrics_registered": 2},
    "anomaly_watchdog": {"monitoring_started": true},
    "self_heal_scheduler": {"playbooks_updated": false}
  }
}
```

### Component Registry

```python
# Get component info
component = component_handshake.get_component_info("new_ml_model_v2")

print(f"Type: {component['component_type']}")
print(f"Capabilities: {component['capabilities']}")
print(f"Version: {component['version']}")
print(f"Integrated: {component['integrated_at']}")
```

### Reusing for Logic Version Changes

Handshake protocol works for existing components changing versions:

```python
# Component upgraded to v2.1.0
handshake_id = await component_handshake.submit_handshake_request(
    component_id="memory_fusion",  # Existing component
    component_type="service",
    capabilities=["storage", "retrieval", "crypto_signing"],
    expected_metrics=["fetch_latency", "crypto_assign_rate"],
    version="2.1.0",  # New version
    crypto_signature="sha3_..."
)

# All subsystems get notified
# They acknowledge the version change
# Validation window runs to ensure compatibility
```

---

## Integration Points

### 1. Observation System → ML Models

In `logic_update_awareness.py`:

```python
async def _store_learning_data(...):
    # ... existing code ...
    
    # Feed to ML models
    from backend.ml_update_integration import ml_update_integration
    
    await ml_update_integration.feed_update_to_models(
        update_id=update_id,
        update_summary=summary,
        observation_data=observation
    )
    
    training_example = await ml_update_integration.create_training_labels_from_observation(
        update_id=update_id,
        observation=observation
    )
    
    await ml_update_integration.store_training_example(training_example)
```

### 2. Handshake → Validation Window

In `component_handshake.py`:

```python
async def _integrate_component(...):
    # ... mark as integrated ...
    
    # Start validation window
    from backend.logic_update_awareness import logic_update_awareness
    
    await logic_update_awareness.start_observation_window(
        update_id=handshake_id,
        summary={
            "update_type": "component_onboarding",
            "components_touched": [component_id],
            "observation_window_duration": 3600
        }
    )
```

### 3. Trigger Mesh Events

**Handshake Announce:**
```python
TriggerEvent(
    event_type="unified_logic.handshake_announce",
    payload={
        "handshake_id": "handshake_a1b2c3",
        "component_id": "new_service",
        "capabilities": [...],
        "requires_ack": true
    }
)
```

**Handshake Complete:**
```python
TriggerEvent(
    event_type="unified_logic.handshake_complete",
    payload={
        "handshake_id": "handshake_a1b2c3",
        "component_id": "new_service",
        "quorum_size": 5,
        "validation_window_started": true
    }
)
```

---

## File Summary

| File | Lines | Purpose |
|------|-------|---------|
| `backend/ml_update_integration.py` | 500+ | ML model integration |
| `backend/component_handshake.py` | 600+ | Handshake protocol |
| `backend/logic_update_awareness.py` | +30 | ML hooks added |
| `ML_AND_HANDSHAKE_COMPLETE.md` | This doc | Documentation |
| **TOTAL** | **~1,130 lines** | **Complete system** |

---

## Usage Examples

### Example 1: New ML Model Onboarding

```python
# New model submits handshake
handshake_id = await component_handshake.submit_handshake_request(
    component_id="trust_predictor_v3",
    component_type="ml_model",
    capabilities=["trust_prediction", "risk_assessment"],
    expected_metrics=["prediction_latency", "accuracy"],
    version="3.0.0"
)

# Hub validates and announces
# Subsystems acknowledge:
# - Memory Fusion: reloads ACLs
# - Metrics Collector: registers new metrics
# - Agentic Spine: updates context

# Quorum reached → Integrated
# Validation window: 1 hour observation
# Anomalies detected → Watchdog alerts
# No issues → Marked stable
```

### Example 2: Regression Correlation

```python
# Regression detected
regression = {
    "detected_at": "2025-11-09T15:00:00Z",
    "components": ["memory_api", "fusion_memory"],
    "metrics": ["error_rate", "latency_p95"],
    "severity": "high"
}

# ML correlates with recent updates
correlation = await ml_update_integration.correlate_regression_with_rollout(
    regression_data=regression,
    time_window_hours=6
)

if correlation and correlation["correlation_score"] > 0.7:
    # High correlation found
    print(f"Likely caused by update {correlation['update_id']}")
    print(f"Component overlap: {correlation['components_overlap']}")
    print(f"Time proximity: {correlation['temporal_proximity_hours']}h")
    
    # Trigger automatic rollback
    from backend.unified_logic_hub import unified_logic_hub
    await unified_logic_hub._rollback_update(...)
```

### Example 3: ML Model Training with Update Data

```python
from backend.training_pipeline import training_pipeline

# Get all logic update training examples
examples = await training_pipeline.get_training_examples(
    example_type="logic_update_observation",
    limit=1000
)

# Train causal RL model
features = [ex["features"] for ex in examples]
labels = [ex["labels"]["stability_score"] for ex in examples]

model.fit(features, labels)

# Model now predicts update stability based on:
# - Update characteristics
# - Governance approval
# - Crypto signatures
# - Historical outcomes
```

---

## Summary

✅ **ML Integration Complete**
- Update metadata flows into proactive intelligence, causal analyzer, temporal forecaster
- Observation windows become labeled training data
- Crypto/governance context enriches model inputs
- Regression correlation with specific rollouts

✅ **Handshake Protocol Complete**
- Secure component onboarding
- Governance + crypto validation
- Quorum-based acknowledgment
- Validation windows for new components
- Reusable for version changes

**Result:** Grace's ML models now learn from every logic update, and new components/versions integrate through a secure, observable handshake protocol.
