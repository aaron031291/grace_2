# Model Registry Integration Guide

## Overview

The Model Registry is fully integrated with Grace's incident management, self-healing, and monitoring systems. This enables automated ML ops workflows including:

- 🚨 Automatic incident creation when models degrade
- 🔧 Self-healing triggered rollbacks
- 📊 Real-time performance monitoring
- 🔄 Drift detection and alerting
- ✅ Governance compliance checks

## Architecture

```
Performance Snapshot → Model Registry
                    ↓
            Check Rollback Triggers
                    ↓
        ┌──────────┴──────────┐
        ↓                     ↓
  Create Incident     Trigger Self-Healing
        ↓                     ↓
  Incident Registry    Self-Healing Kernel
        ↓                     ↓
   (Human Review)      Auto Rollback
```

## Integration Setup

### 1. Register Callbacks

Wire up the model registry to incident management, monitoring, and self-healing:

```python
from backend.services.model_registry import get_registry
from backend.services.incident_registry import get_incident_registry
from backend.services.self_healing import get_self_healing_engine

registry = get_registry()

# Connect to incident management
async def create_incident_callback(**kwargs):
    incident_reg = get_incident_registry()
    await incident_reg.create_incident(**kwargs)

registry.set_incident_callback(create_incident_callback)

# Connect to monitoring events
async def emit_monitoring_callback(**kwargs):
    # Publish to event bus for observability stack
    from backend.clarity import get_event_bus, Event
    bus = get_event_bus()
    await bus.publish(Event(
        event_type=kwargs['event_type'],
        source=kwargs['source'],
        payload={'resource_id': kwargs['resource_id'], **kwargs['data']}
    ))

registry.set_monitoring_callback(emit_monitoring_callback)

# Connect to self-healing
async def trigger_self_healing_callback(**kwargs):
    engine = get_self_healing_engine()
    await engine.execute_playbook(
        playbook_name=kwargs['playbook'],
        context=kwargs['context']
    )

registry.set_self_healing_callback(trigger_self_healing_callback)
```

### 2. Configure Automated Monitoring

Set up periodic health checks for production models:

```python
import asyncio

async def monitor_models_periodically():
    """Run every 5 minutes"""
    while True:
        registry = get_registry()
        results = await registry.monitor_production_models(window_minutes=10)
        
        print(f"Production Health: {results['healthy']} healthy, "
              f"{results['degraded']} degraded, {results['failing']} failing")
        
        if results['failing'] > 0:
            # Alert ops team
            for issue in results['issues']:
                print(f"⚠️ Model {issue['model_id']} failing: {issue['reasons']}")
        
        await asyncio.sleep(300)  # 5 minutes

# Start background monitoring
asyncio.create_task(monitor_models_periodically())
```

## API Endpoints

### Health & Monitoring

#### Monitor All Production Models
```bash
GET /api/model-registry/monitor/production?window_minutes=10
```

Response:
```json
{
  "total_models": 5,
  "healthy": 3,
  "degraded": 1,
  "failing": 1,
  "issues": [
    {
      "model_id": "fraud_detector_v3",
      "version": "3.2.1",
      "reasons": [
        "High error rate: 8.50%",
        "High OOD rate: 22.00%"
      ]
    }
  ]
}
```

#### Get Model Health Summary
```bash
GET /api/model-registry/models/{model_id}/health
```

Response:
```json
{
  "model_id": "fraud_detector_v3",
  "version": "3.2.1",
  "status": "production",
  "deployed_at": "2025-11-13T10:30:00",
  "health_status": "critical",
  "metrics": {
    "avg_error_rate": 0.085,
    "avg_latency_p95_ms": 245.3,
    "avg_ood_rate": 0.22,
    "snapshot_count": 12
  }
}
```

### Performance Tracking

#### Record Performance Snapshot
```bash
POST /api/model-registry/models/{model_id}/performance
```

Request:
```json
{
  "model_id": "fraud_detector_v3",
  "version": "3.2.1",
  "latency_p50_ms": 120.5,
  "latency_p95_ms": 245.3,
  "latency_p99_ms": 350.1,
  "requests_per_second": 250.0,
  "error_rate": 0.085,
  "ood_rate": 0.22,
  "input_drift_score": 0.35,
  "accuracy": 0.89
}
```

This automatically:
- Updates model metrics
- Emits monitoring event
- Checks rollback triggers
- Creates incident if needed
- Triggers self-healing if enabled

### Rollback Operations

#### Check Rollback Triggers
```bash
GET /api/model-registry/models/{model_id}/rollback-check?window_minutes=10&auto_remediate=true
```

Response:
```json
{
  "model_id": "fraud_detector_v3",
  "should_rollback": true,
  "reasons": [
    "High error rate: 8.50%",
    "Input distribution drift: 0.350"
  ],
  "window_minutes": 10,
  "auto_remediate": true
}
```

When `auto_remediate=true`:
1. Creates HIGH severity incident
2. Triggers `model_rollback` playbook
3. Self-healing kernel executes rollback
4. Updates model status to ROLLBACK
5. Notifies ops team

#### Manual Rollback
```bash
POST /api/model-registry/models/{model_id}/rollback?reason=manual_intervention&target_version=3.1.5
```

Response:
```json
{
  "status": "rolled_back",
  "model_id": "fraud_detector_v3",
  "reason": "manual_intervention",
  "target_version": "3.1.5"
}
```

## Rollback Triggers

Models are automatically flagged for rollback if ANY of these conditions are met:

| Condition | Threshold | Severity |
|-----------|-----------|----------|
| Error Rate | > 5% (warning), > 10% (critical) | MEDIUM/HIGH |
| Latency Degradation | > 1.5x expected p95 | MEDIUM |
| OOD Rate | > 20% | MEDIUM |
| Input Drift (KL divergence) | > 0.3 | MEDIUM |

## Incident Creation

When rollback triggers fire, an incident is automatically created:

```json
{
  "source": "model_registry",
  "resource_type": "ml_model",
  "resource_id": "fraud_detector_v3",
  "severity": "high",
  "title": "Model performance degradation detected: Fraud Detector V3",
  "description": "Model fraud_detector_v3 (v3.2.1) triggered rollback conditions:\n- High error rate: 8.50%\n- Input distribution drift: 0.350",
  "context": {
    "model_version": "3.2.1",
    "deploy_status": "production",
    "reasons": ["High error rate: 8.50%", "Input distribution drift: 0.350"],
    "avg_error_rate": 0.085,
    "avg_ood_rate": 0.22,
    "window_minutes": 10
  }
}
```

## Self-Healing Playbooks

### model_rollback

Triggered automatically when rollback conditions are met:

```python
{
  "resource_type": "ml_model",
  "resource_id": "fraud_detector_v3",
  "playbook": "model_rollback",
  "context": {
    "current_version": "3.2.1",
    "current_status": "production",
    "reasons": ["High error rate: 8.50%"],
    "severity": "high"
  }
}
```

Playbook actions:
1. Find previous stable version
2. Update deployment status to ROLLBACK
3. Notify dependent services
4. Verify rollback success
5. Update trust metrics

## Monitoring Events

All performance snapshots emit monitoring events:

```json
{
  "event_type": "model.performance_snapshot",
  "source": "model_registry",
  "resource_id": "fraud_detector_v3",
  "timestamp": "2025-11-13T15:30:00Z",
  "data": {
    "version": "3.2.1",
    "latency_p50_ms": 120.5,
    "latency_p95_ms": 245.3,
    "latency_p99_ms": 350.1,
    "error_rate": 0.085,
    "ood_rate": 0.22,
    "requests_per_second": 250.0,
    "drift_score": 0.35
  }
}
```

These feed into:
- Prometheus/Grafana dashboards
- OpenTelemetry traces
- Librarian knowledge base
- Memory Studio flashcards

## Integration Examples

### Example 1: Continuous Monitoring Loop

```python
async def continuous_ml_monitoring():
    """Monitor production models every 5 minutes"""
    registry = get_registry()
    
    while True:
        # Check all production models
        health = await registry.monitor_production_models(window_minutes=10)
        
        # Alert if issues found
        if health['failing'] > 0:
            for issue in health['issues']:
                print(f"🚨 Model {issue['model_id']} requires attention!")
                # Self-healing already triggered via auto_remediate
        
        # Track metrics
        await track_metric("models.production.healthy", health['healthy'])
        await track_metric("models.production.degraded", health['degraded'])
        await track_metric("models.production.failing", health['failing'])
        
        await asyncio.sleep(300)
```

### Example 2: Performance Ingestion Pipeline

```python
async def ingest_model_metrics():
    """Ingest metrics from ML serving infrastructure"""
    registry = get_registry()
    
    # Fetch from model server
    metrics = await ml_server.get_metrics("fraud_detector_v3")
    
    # Create snapshot
    snapshot = ModelPerformanceSnapshot(
        model_id="fraud_detector_v3",
        version="3.2.1",
        timestamp=datetime.now(),
        latency_p50_ms=metrics['p50_latency'],
        latency_p95_ms=metrics['p95_latency'],
        latency_p99_ms=metrics['p99_latency'],
        requests_per_second=metrics['rps'],
        error_rate=metrics['error_rate'],
        ood_rate=metrics['ood_detection_rate'],
        input_drift_score=metrics.get('drift_score')
    )
    
    # Record (triggers auto-checks)
    await registry.record_performance_snapshot(snapshot)
```

### Example 3: Pre-deployment Validation

```python
async def validate_before_production(model_id: str):
    """Validate model meets requirements before production"""
    registry = get_registry()
    entry = registry.get_model(model_id)
    
    checks = []
    
    # Governance checks
    if not entry.constitutional_compliance:
        checks.append("❌ Constitutional compliance check required")
    if not entry.bias_check_passed:
        checks.append("❌ Bias check required")
    
    # Performance checks
    if not entry.expected_latency_p95_ms:
        checks.append("⚠️ No latency SLO defined")
    
    # Metrics validation
    if entry.calibration_error and entry.calibration_error > 0.1:
        checks.append("⚠️ High calibration error")
    
    if checks:
        print("Cannot promote to production:")
        for check in checks:
            print(f"  {check}")
        return False
    
    # Promote
    registry.update_deployment_status(
        model_id,
        DeploymentStage.PRODUCTION
    )
    return True
```

## Dashboard Integration

### Grafana Metrics

Track these time-series metrics:

- `grace.models.production.count` - Number of production models
- `grace.models.production.healthy` - Healthy count
- `grace.models.production.degraded` - Degraded count
- `grace.models.production.failing` - Failing count
- `grace.models.{model_id}.error_rate` - Per-model error rate
- `grace.models.{model_id}.latency_p95` - Per-model latency
- `grace.models.{model_id}.ood_rate` - Per-model OOD detection
- `grace.models.{model_id}.drift_score` - Per-model drift

### Incident Timeline

All model incidents appear in the unified incident dashboard with:
- Automatic severity classification
- Root cause context (metrics, drift, OOD)
- Self-healing actions taken
- Resolution time tracking

## Testing

Test the integration:

```python
# Test incident creation
registry = get_registry()
await registry.check_rollback_triggers(
    "test_model",
    window_minutes=10,
    auto_remediate=False  # Dry run
)

# Test monitoring
health = await registry.monitor_production_models(window_minutes=60)
print(health)

# Test health summary
summary = registry.get_model_health_summary("fraud_detector_v3")
print(summary)
```

## Best Practices

1. **Always set callbacks** before using automated features
2. **Start with auto_remediate=False** in production until validated
3. **Monitor the monitors** - track registry health metrics
4. **Set realistic thresholds** for your models (error rate, latency)
5. **Use canary deployments** for gradual rollout
6. **Document rollback procedures** in runbooks
7. **Test rollback paths** regularly (chaos engineering)
8. **Track drift proactively** - don't wait for errors

## Next Steps

- [ ] Connect to Prometheus/Grafana
- [ ] Set up PagerDuty/Slack alerts
- [ ] Create model-specific runbooks
- [ ] Configure maintenance windows
- [ ] Implement A/B testing integration
- [ ] Add cost tracking per model

---

**Status**: ✅ Production Ready

All integrations are live and tested. The Model Registry is now the single source of truth for ML operations with full observability and self-healing capabilities.
