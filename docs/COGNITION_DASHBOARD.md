# Grace Cognition Dashboard

**Real-time cognitive health monitoring and SaaS readiness tracking**

---

## Overview

The Cognition Dashboard provides comprehensive, real-time visibility into Grace's cognitive health across all 10 domains. It tracks Key Performance Indicators (KPIs), evaluates 90% benchmarks, and automatically signals when Grace is ready for SaaS commercialization.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Cognition Dashboard                       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  CLI Watch   │  │ API Endpoint │  │  Web Dashboard│     │
│  │   Commands   │  │    /status   │  │   (Future)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────┬───────────────┬────────────────┬────────────────┘
           │               │                │
           └───────────────┼────────────────┘
                           │
              ┌────────────▼────────────┐
              │  Cognition Metrics      │
              │      Engine             │
              │  - Health tracking      │
              │  - Benchmark windows    │
              │  - SaaS readiness       │
              └────────────┬────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
    │   Metrics   │ │ Benchmark │ │  Metric     │
    │  Collector  │ │ Scheduler │ │ Publishers  │
    │             │ │  (Hourly) │ │  (Domains)  │
    └─────────────┘ └───────────┘ └─────────────┘
```

## Domain Metrics

### 1. Core Domain
**Platform operations and governance**

| KPI | Description | Target |
|-----|-------------|--------|
| `uptime` | Platform availability | ≥ 0.95 |
| `governance_score` | Policy compliance | ≥ 0.90 |
| `healing_actions` | Self-healing triggers | Count |
| `verification_failures` | Verification issues | Count |
| `event_bus_latency` | Event system speed | ≥ 0.90 |

### 2. Transcendence Domain
**Agentic coding and task execution**

| KPI | Description | Target |
|-----|-------------|--------|
| `task_success` | Task completion rate | ≥ 0.90 |
| `code_quality` | Generated code quality | ≥ 0.85 |
| `memory_recall` | Context retrieval accuracy | ≥ 0.90 |
| `planning_accuracy` | Plan effectiveness | ≥ 0.85 |
| `architecture_score` | Design quality | ≥ 0.90 |

### 3. Knowledge Domain
**Information ingestion and retrieval**

| KPI | Description | Target |
|-----|-------------|--------|
| `trust_score` | Source trustworthiness | ≥ 0.90 |
| `ingestion_rate` | Items ingested | Count |
| `recall_accuracy` | Search precision | ≥ 0.90 |
| `source_diversity` | Source variety | ≥ 0.80 |
| `knowledge_freshness` | Information currency | ≥ 0.85 |

### 4. Security Domain (Hunter)
**Threat detection and mitigation**

| KPI | Description | Target |
|-----|-------------|--------|
| `threats_detected` | Security issues found | Count |
| `scan_coverage` | Code coverage | ≥ 0.95 |
| `response_time` | Detection speed | ≤ 0.020 |
| `false_positive_rate` | Accuracy | ≤ 0.05 |
| `auto_fix_success` | Auto-remediation | ≥ 0.85 |

### 5. ML Domain
**Model training and deployment**

| KPI | Description | Target |
|-----|-------------|--------|
| `model_accuracy` | Prediction accuracy | ≥ 0.90 |
| `deployment_success` | Deployment rate | ≥ 0.95 |
| `inference_latency` | Prediction speed | ≤ 0.050 |
| `training_efficiency` | Training speed | ≥ 0.80 |
| `auto_retrain_triggers` | Drift detection | Count |

### 6. Temporal Domain
**Causal reasoning and forecasting**

| KPI | Description | Target |
|-----|-------------|--------|
| `prediction_accuracy` | Forecast quality | ≥ 0.85 |
| `graph_completeness` | Causal graph coverage | ≥ 0.90 |
| `sim_quality` | Simulation accuracy | ≥ 0.85 |
| `event_latency` | Processing speed | ≤ 0.030 |
| `impact_precision` | Impact analysis | ≥ 0.85 |

### 7. Parliament Domain
**Governance and meta-learning**

| KPI | Description | Target |
|-----|-------------|--------|
| `vote_participation` | Voting engagement | ≥ 0.90 |
| `recommendation_adoption` | Meta-loop adoption | ≥ 0.80 |
| `compliance_score` | Policy adherence | ≥ 0.95 |
| `reflection_quality` | Learning quality | ≥ 0.85 |
| `meta_convergence` | Consensus rate | ≥ 0.85 |

### 8. Federation Domain
**External integrations**

| KPI | Description | Target |
|-----|-------------|--------|
| `connector_health` | Connector status | ≥ 0.90 |
| `api_success` | API call success | ≥ 0.95 |
| `secret_rotation` | Security compliance | ≥ 0.99 |
| `plugin_uptime` | Plugin availability | ≥ 0.95 |
| `sandbox_isolation` | Sandbox security | ≥ 0.99 |

### 9. Cognition Domain
**Overall system intelligence**

| KPI | Description | Target |
|-----|-------------|--------|
| `overall_health` | System-wide health | ≥ 0.90 |
| `overall_trust` | System trustworthiness | ≥ 0.90 |
| `overall_confidence` | Prediction confidence | ≥ 0.90 |
| `benchmark_progress` | Progress to 90% | Progress |
| `saas_readiness` | Commercialization ready | Boolean |

### 10. Speech Domain
**Voice interaction**

| KPI | Description | Target |
|-----|-------------|--------|
| `recognition_accuracy` | Speech-to-text accuracy | ≥ 0.90 |
| `synthesis_quality` | Text-to-speech quality | ≥ 0.85 |
| `command_success` | Voice command success | ≥ 0.90 |
| `latency` | Response time | ≤ 2.0s |
| `multi_modal_integration` | Integration quality | ≥ 0.85 |

## API Endpoints

### GET `/api/cognition/status`
Get real-time cognition status across all domains.

**Response:**
```json
{
  "timestamp": "2025-11-03T10:30:00",
  "overall_health": 0.88,
  "overall_trust": 0.84,
  "overall_confidence": 0.82,
  "saas_ready": false,
  "domains": {
    "core": {
      "domain_id": "core",
      "health": 0.91,
      "trust": 0.86,
      "confidence": 0.84,
      "kpis": {
        "uptime": 0.95,
        "governance_score": 0.87
      },
      "last_updated": "2025-11-03T10:30:00"
    }
  }
}
```

### GET `/api/cognition/readiness`
Get detailed SaaS readiness report.

**Response:**
```json
{
  "ready": false,
  "overall_health": 0.88,
  "overall_trust": 0.84,
  "overall_confidence": 0.82,
  "benchmarks": {
    "overall_health": {
      "sustained": false,
      "average": 0.88,
      "threshold": 0.90,
      "window_days": 7,
      "sample_count": 168
    }
  },
  "domains": {...},
  "next_steps": [
    "Improve overall_health by 2.0% to reach 90% threshold",
    "Strengthen temporal domain (currently 84%)"
  ]
}
```

### POST `/api/cognition/domain/{domain_id}/update`
Update KPIs for a specific domain.

**Request:**
```json
{
  "task_success": 0.92,
  "code_quality": 0.88
}
```

### GET `/api/cognition/benchmark/{metric_name}`
Get detailed benchmark status.

### POST `/api/cognition/report/generate`
Generate and save readiness report.

### GET `/api/cognition/report/latest`
View latest readiness report content.

## CLI Commands

### `grace cognition status`
Display current cognition status.

```bash
$ grace cognition status

Grace Cognition Status
Timestamp: 2025-11-03T10:30:00

┏━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Metric      ┃ Value  ┃
┡━━━━━━━━━━━━━╇━━━━━━━━┩
│ Health      │ 88.0%  │
│ Trust       │ 84.0%  │
│ Confidence  │ 82.0%  │
│ SaaS Ready  │ 🔧 No  │
└─────────────┴────────┘
```

### `grace cognition readiness`
View detailed SaaS readiness report.

### `grace cognition watch`
Live dashboard with auto-refresh (default: 5s).

```bash
$ grace cognition watch
Grace Cognition Live Dashboard
Updating every 5 seconds. Press Ctrl+C to stop.
```

### `grace <domain> metrics`
View metrics for a specific domain.

```bash
$ grace transcendence metrics
$ grace security metrics
$ grace ml metrics
```

### `grace cognition readiness-report`
Generate and save SaaS readiness report.

## Metric Publishing

### Publishing from Your Code

```python
from backend.metric_publishers import TranscendenceMetrics

# After completing a task
await TranscendenceMetrics.publish_task_completed(
    success=True, 
    quality=0.92
)

# After creating a plan
await TranscendenceMetrics.publish_plan_created(
    plan_quality=0.88
)
```

### Available Publishers

- `CoreMetrics` - Platform operations
- `OrchestratorMetrics` / `TranscendenceMetrics` - Agentic coding
- `KnowledgeMetrics` - Information systems
- `HunterMetrics` - Security scanning
- `MLMetrics` - Machine learning
- `TemporalMetrics` - Causal reasoning
- `ParliamentMetrics` - Governance
- `FederationMetrics` - External systems
- `SpeechMetrics` - Voice interaction

### Direct Publishing

```python
from backend.metrics_service import publish_metric, publish_batch

# Single metric
await publish_metric("transcendence", "task_success", 1.0)

# Multiple metrics at once
await publish_batch("ml", {
    "model_accuracy": 0.94,
    "deployment_success": 1.0,
    "inference_latency": 0.028
})
```

## Benchmark System

### 90% Sustained Performance
Grace tracks three key benchmarks over a 7-day rolling window:

1. **Overall Health** ≥ 90%
2. **Overall Trust** ≥ 90%
3. **Overall Confidence** ≥ 90%

### Evaluation Schedule
- **Hourly:** Background evaluator checks benchmarks
- **Events:** Emits `product.elevation_ready` when all benchmarks sustained
- **Persistence:** Stores history in database for trend analysis

### State Transitions

```
Development Mode (< 90%)
         ↓
    [Crosses 90%]
         ↓
  Threshold Crossed
         ↓
  [Sustained 7 days]
         ↓
🚀 SaaS Ready!
```

## SaaS Readiness Trigger

When Grace sustains 90%+ across all benchmarks for 7 consecutive days:

1. **Event Emitted:** `product.elevation_ready` via trigger mesh
2. **Report Generated:** Markdown readiness report saved
3. **Notifications:** Alerts sent (CLI, logs, future: email/Slack)
4. **Next Steps:** Action items provided for commercialization

### Readiness Report Contents

- Executive summary with current metrics
- Benchmark performance table
- Domain-by-domain breakdown
- Technical readiness checklist
- SaaS product roadmap
- Infrastructure requirements
- Next steps for launch

## Database Schema

### MetricEvent
Raw metric data points
```sql
id, domain, kpi, value, timestamp, metadata
```

### MetricsRollup
Aggregated metrics (hourly/daily/weekly)
```sql
id, domain, kpi, period, period_start, period_end,
avg_value, min_value, max_value, count, sum_value
```

### BenchmarkHistory
Benchmark evaluation history
```sql
id, metric_name, value, threshold, sustained,
window_days, sample_count, timestamp, metadata
```

### SaaSReadinessEvent
SaaS readiness trigger events
```sql
id, event_type, overall_health, overall_trust,
overall_confidence, saas_ready, message, 
triggered_at, metadata, notified
```

### DomainMetrics
Current domain snapshot
```sql
id, domain, health, trust, confidence, kpis,
last_updated, health_trend, performance_score,
has_alerts, alert_count
```

## Testing

### Manual Testing

```bash
# 1. Start Grace backend
cd grace_rebuild
python -m backend.main

# 2. Check cognition status
grace cognition status

# 3. Watch live dashboard
grace cognition watch

# 4. Generate report
grace cognition readiness-report
```

### Publishing Test Metrics

```python
# test_cognition.py
import asyncio
from backend.metric_publishers import *

async def test_metrics():
    # Publish some test metrics
    await OrchestratorMetrics.publish_task_completed(True, 0.92)
    await HunterMetrics.publish_scan_completed(2, 0.96, 0.015)
    await MLMetrics.publish_training_completed(0.94, 1800)
    await KnowledgeMetrics.publish_ingestion_completed(0.91, 25)
    
    print("✓ Test metrics published")

asyncio.run(test_metrics())
```

## Next Steps

### Immediate (In Place)
- ✅ Metrics backbone
- ✅ Background evaluator
- ✅ API endpoints
- ✅ CLI commands
- ✅ Metric publishers
- ✅ Documentation

### Phase 2
- [ ] Frontend React dashboard
- [ ] Real-time WebSocket updates
- [ ] Historical trend charts
- [ ] Alert management UI
- [ ] Custom benchmark configuration

### Phase 3
- [ ] Email/Slack notifications
- [ ] Custom metric definitions
- [ ] Multi-user access control
- [ ] Export to Prometheus/Grafana
- [ ] Mobile dashboard app

## Troubleshooting

### No metrics showing
1. Verify backend is running: `http://localhost:8000/health`
2. Check metric publishers are integrated
3. Review logs: `tail -f grace.log`

### Benchmarks not updating
1. Check benchmark scheduler: logs should show hourly evaluations
2. Verify metrics are being published
3. Check 7-day window has enough samples

### CLI connection errors
1. Ensure backend API is accessible
2. Check port 8000 is not blocked
3. Verify CORS settings in `main.py`

## References

- [Metrics Service](../backend/metrics_service.py)
- [Cognition Metrics Engine](../backend/cognition_metrics.py)
- [Benchmark Scheduler](../backend/benchmark_scheduler.py)
- [Metric Publishers](../backend/metric_publishers.py)
- [Cognition API Router](../backend/routers/cognition.py)
- [CLI Commands](../backend/cli/commands/cognition_command.py)

---

**Last Updated:** November 3, 2025  
**Status:** Production Ready ✅  
**Version:** 1.0.0
