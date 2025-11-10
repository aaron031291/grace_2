# Update Mission Tracking
## Integration with Grace Mission System

Logic updates are now tracked as missions with stability verification and learning retrospectives.

---

## Overview

Every logic update becomes a **mission** that Grace tracks through:
1. Deployment phase
2. Observation window
3. Stability verification
4. Learning retrospective

**Mission Status:** `proposed` → `deployed` → `observing` → `stable`/`unstable` → `learned`

---

## Mission Lifecycle

### Phase 1: Proposed
```python
# Update submitted
update_id = await unified_logic_hub.submit_update(
    update_type="schema",
    component_targets=["memory_api"],
    content={...}
)

# Mission automatically created
mission_id = f"mission_update_{update_id}"
```

**Mission Data:**
```json
{
  "mission_id": "mission_update_abc123",
  "type": "logic_update",
  "update_id": "update_abc123",
  "status": "proposed",
  "created_at": "2025-11-09T12:00:00Z",
  "metadata": {
    "update_type": "schema",
    "components": ["memory_api"],
    "risk_level": "medium"
  }
}
```

### Phase 2: Deployed
```
Update passes through hub pipeline →
Distribution complete →
Mission status: "deployed"
```

**Mission Update:**
```json
{
  "status": "deployed",
  "deployed_at": "2025-11-09T12:05:00Z",
  "distribution": {
    "trigger_event_id": "event_xyz789",
    "crypto_signature": "sha3_...",
    "audit_ref": 12345
  }
}
```

### Phase 3: Observing
```
Observation window starts →
Health checks run periodically →
Mission status: "observing"
```

**Mission Data:**
```json
{
  "status": "observing",
  "observation": {
    "start_time": "2025-11-09T12:05:00Z",
    "end_time": "2025-11-09T18:05:00Z",
    "duration_hours": 6,
    "checks_completed": 25,
    "anomalies_detected": 0,
    "current_stability_score": 1.0
  }
}
```

### Phase 4: Stable/Unstable
```
Observation window completes →
Stability verdict calculated →
Mission status: "stable" or "unstable"
```

**Stable Mission:**
```json
{
  "status": "stable",
  "observation_completed_at": "2025-11-09T18:05:00Z",
  "stability_verdict": "stable",
  "final_stability_score": 0.98,
  "metrics_within_thresholds": true,
  "anomalies_total": 0
}
```

**Unstable Mission (Rollback):**
```json
{
  "status": "unstable",
  "observation_completed_at": "2025-11-09T14:30:00Z",
  "stability_verdict": "unstable",
  "final_stability_score": 0.65,
  "anomalies_total": 8,
  "rollback": {
    "triggered_at": "2025-11-09T14:30:00Z",
    "reason": "critical_anomaly_detected",
    "rollback_id": "rollback_abc123"
  }
}
```

### Phase 5: Learned
```
Retrospective analysis →
Learning data fed to proactive intelligence →
Mission status: "learned"
```

**Mission Learning:**
```json
{
  "status": "learned",
  "learned_at": "2025-11-09T19:00:00Z",
  "retrospective": {
    "outcome": "success",
    "duration_to_stable": "6h",
    "lessons": [
      "schema_changes_well_tolerated",
      "no_breaking_changes_detected",
      "governance_policies_effective"
    ],
    "recommendations": [
      "similar_updates_low_risk",
      "observation_window_can_be_shorter"
    ]
  }
}
```

---

## Mission Tracking API

### Create Update Mission
```python
from backend.logic_update_awareness import logic_update_awareness

# Automatic on update submission
mission_id = f"mission_update_{update_id}"

# Mission tracked in awareness system
mission_data = {
    "mission_id": mission_id,
    "update_id": update_id,
    "status": "proposed",
    "phases": []
}
```

### Check Mission Status
```python
# Get current observation status
observation = await logic_update_awareness.get_observation_status(update_id)

mission_status = {
    "mission_id": f"mission_update_{update_id}",
    "update_id": update_id,
    "status": observation["status"],  # active, completed, rolled_back
    "stability_score": observation.get("stability_score", 0.0),
    "verdict": observation.get("stability_verdict", "unknown")
}
```

### Query Mission History
```python
# Get learning history (past missions)
history = logic_update_awareness.get_learning_history(limit=20)

for mission in history:
    print(f"Mission {mission['update_id']}: {mission['stability_verdict']}")
    print(f"  Stability: {mission['stability_score']:.2%}")
    print(f"  Anomalies: {mission['anomalies_count']}")
```

---

## Integration Points

### 1. Mission Creation Hook

In `unified_logic_hub.py`:

```python
async def submit_update(...):
    update_id = generate_update_id()
    
    # Create mission
    mission_id = f"mission_update_{update_id}"
    await mission_tracker.create_mission(
        mission_id=mission_id,
        mission_type="logic_update",
        metadata={
            "update_id": update_id,
            "update_type": update_type,
            "components": component_targets
        }
    )
    
    # Process update...
    await self._process_update_pipeline(package, context)
    
    return update_id
```

### 2. Phase Transition Events

Publish events on phase transitions:

```python
# On deployment complete
await trigger_mesh.publish(TriggerEvent(
    event_type="mission.phase_transition",
    payload={
        "mission_id": mission_id,
        "from_phase": "proposed",
        "to_phase": "deployed",
        "update_id": update_id
    }
))

# On observation start
await trigger_mesh.publish(TriggerEvent(
    event_type="mission.phase_transition",
    payload={
        "mission_id": mission_id,
        "from_phase": "deployed",
        "to_phase": "observing"
    }
))

# On stability verdict
await trigger_mesh.publish(TriggerEvent(
    event_type="mission.phase_transition",
    payload={
        "mission_id": mission_id,
        "from_phase": "observing",
        "to_phase": "stable",  # or "unstable"
        "stability_score": 0.98
    }
))
```

### 3. Mission Dashboard Integration

```python
# Get all active update missions
active_missions = await mission_tracker.get_missions(
    mission_type="logic_update",
    status=["deployed", "observing"]
)

for mission in active_missions:
    observation = await logic_update_awareness.get_observation_status(
        mission["metadata"]["update_id"]
    )
    
    mission["observation_progress"] = {
        "elapsed": observation.get("elapsed_time"),
        "remaining": observation.get("remaining_time"),
        "stability_score": observation.get("stability_score"),
        "health_checks": len(observation.get("health_checks", []))
    }
```

---

## Stability Criteria

Mission marked "stable" only when:

✅ **Observation window completes** (duration based on risk level)  
✅ **Stability score ≥ 0.95** (no major anomalies)  
✅ **Metrics within thresholds** (error rate, latency, etc.)  
✅ **No critical anomalies detected**  
✅ **All health checks pass**  

### Calculation

```python
stability_score = 1.0

# Penalty for each anomaly
for anomaly in anomalies:
    if anomaly["severity"] == "critical":
        stability_score *= 0.5  # 50% penalty
    elif anomaly["severity"] == "high":
        stability_score *= 0.8  # 20% penalty
    elif anomaly["severity"] == "medium":
        stability_score *= 0.9  # 10% penalty

# Penalty for failed health checks
failed_checks = [c for c in health_checks if not c["passed"]]
stability_score *= (1 - len(failed_checks) / len(health_checks))

# Verdict
if stability_score >= 0.95:
    verdict = "stable"
elif stability_score >= 0.80:
    verdict = "acceptable"
else:
    verdict = "unstable"
```

---

## Learning & Retrospectives

After observation completes, mission data feeds into learning:

### Successful Mission
```python
learning_data = {
    "update_id": update_id,
    "outcome": "success",
    "stability_score": 0.98,
    "duration_to_stable": "6h",
    "components": ["memory_api"],
    "update_type": "schema",
    "risk_level": "medium",
    
    "lessons": [
        "schema_changes_well_tolerated",
        "no_client_errors_detected",
        "backward_compatible_migration"
    ],
    
    "recommendations": [
        "similar_schema_updates_can_use_low_risk",
        "observation_window_can_be_4h_instead_of_6h",
        "validation_checks_were_sufficient"
    ]
}

await proactive_intelligence.learn_from_mission(learning_data)
```

### Failed Mission (Rollback)
```python
learning_data = {
    "update_id": update_id,
    "outcome": "failure",
    "stability_score": 0.65,
    "duration_to_rollback": "2h",
    "components": ["memory_api"],
    "update_type": "schema",
    "risk_level": "medium",
    
    "failure_reasons": [
        "breaking_change_not_detected_in_validation",
        "client_compatibility_issue",
        "error_rate_spike_in_production"
    ],
    
    "lessons": [
        "validation_insufficient_for_this_change_type",
        "need_client_compatibility_testing",
        "should_have_been_marked_high_risk"
    ],
    
    "improvements": [
        "add_client_compatibility_check_to_validation",
        "increase_observation_window_for_schema_changes",
        "improve_breaking_change_detection"
    ]
}

await proactive_intelligence.learn_from_mission(learning_data)
```

### Pattern Recognition

Proactive intelligence analyzes mission history to:
- Predict update risk levels
- Suggest observation durations
- Recommend validation improvements
- Identify recurring failure patterns

```python
# Query past similar missions
similar_missions = await proactive_intelligence.find_similar_missions(
    update_type="schema",
    components=["memory_api"],
    limit=10
)

# Calculate success rate
success_rate = len([m for m in similar_missions if m["outcome"] == "success"]) / len(similar_missions)

# Adjust risk level recommendation
if success_rate >= 0.95:
    recommended_risk = "low"
elif success_rate >= 0.80:
    recommended_risk = "medium"
else:
    recommended_risk = "high"
```

---

## Mission Metrics

Track mission metrics for observability:

```yaml
# metrics_catalog.yaml
metrics:
  - metric_id: mission.update_success_rate
    category: mission
    description: "Percentage of update missions that reach stable"
    unit: ratio
    aggregation: avg
    thresholds:
      good: { lower: 0.95 }
      warning: { lower: 0.90, upper: 0.95 }
      critical: { upper: 0.90 }
  
  - metric_id: mission.average_observation_duration
    category: mission
    description: "Average observation window duration by risk level"
    unit: hours
    aggregation: avg
  
  - metric_id: mission.rollback_rate
    category: mission
    description: "Percentage of missions requiring rollback"
    unit: ratio
    aggregation: avg
    thresholds:
      good: { upper: 0.05 }
      warning: { lower: 0.05, upper: 0.10 }
      critical: { lower: 0.10 }
```

---

## API Endpoints

### Get Mission Status
```bash
GET /api/missions/mission_update_{update_id}
```

**Response:**
```json
{
  "mission_id": "mission_update_abc123",
  "update_id": "update_abc123",
  "status": "observing",
  "phases": [
    {"phase": "proposed", "timestamp": "2025-11-09T12:00:00Z"},
    {"phase": "deployed", "timestamp": "2025-11-09T12:05:00Z"},
    {"phase": "observing", "timestamp": "2025-11-09T12:05:00Z"}
  ],
  "observation": {
    "progress": 0.42,
    "elapsed_hours": 2.5,
    "remaining_hours": 3.5,
    "stability_score": 0.98,
    "anomalies": 0,
    "health_checks_passed": 15
  }
}
```

### List Active Missions
```bash
GET /api/missions?type=logic_update&status=observing
```

### Get Mission Learning
```bash
GET /api/missions/mission_update_{update_id}/retrospective
```

---

## Summary

✅ **Mission tracking** integrated with logic updates  
✅ **Phase transitions** tracked (proposed → deployed → observing → stable)  
✅ **Stability verification** with observation windows  
✅ **Learning retrospectives** feed proactive intelligence  
✅ **Metrics & observability** for mission success rates  
✅ **API endpoints** for mission status queries  

**Result:** Grace treats every logic update as a mission with clear success criteria, observation periods, and learning outcomes.
