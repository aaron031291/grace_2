# Cognition Dashboard - Quick Start Guide

**Get up and running with Grace's Cognition Dashboard in 5 minutes**

---

## 1. Start Grace Backend

```bash
cd grace_rebuild
python -m backend.main
```

Wait for:
```
✓ Database initialized
✓ Grace API server starting...
✓ Benchmark scheduler started (evaluates every hour)
```

---

## 2. Check Status via CLI

```bash
# View current status
grace cognition status

# View SaaS readiness
grace cognition readiness

# Live dashboard (updates every 5s)
grace cognition watch
```

---

## 3. View in Browser

Open: http://localhost:8000/docs

Try these endpoints:
- `GET /api/cognition/status` - Current status
- `GET /api/cognition/readiness` - SaaS readiness report

---

## 4. Publish Test Metrics

Create `test_metrics.py`:

```python
import asyncio
from backend.metric_publishers import *

async def publish_test_metrics():
    # Transcendence domain
    await OrchestratorMetrics.publish_task_completed(True, 0.92)
    await OrchestratorMetrics.publish_plan_created(0.88)
    
    # Security domain
    await HunterMetrics.publish_scan_completed(2, 0.96, 0.015)
    
    # ML domain
    await MLMetrics.publish_training_completed(0.94, 1800)
    
    # Knowledge domain
    await KnowledgeMetrics.publish_ingestion_completed(0.91, 25)
    
    print("✓ Test metrics published!")

asyncio.run(publish_test_metrics())
```

Run it:
```bash
python test_metrics.py
```

---

## 5. View Updated Status

```bash
# Check status again
grace cognition status

# Generate readiness report
grace cognition readiness-report
```

---

## Integration into Your Code

### Option 1: Use Publisher Classes

```python
from backend.metric_publishers import OrchestratorMetrics

async def my_task_function():
    result = await execute_task()
    
    # Publish metrics
    await OrchestratorMetrics.publish_task_completed(
        success=result.success,
        quality=result.quality_score
    )
```

### Option 2: Direct Publishing

```python
from backend.metrics_service import publish_metric

async def my_function():
    await publish_metric("transcendence", "task_success", 1.0)
```

### Option 3: Batch Publishing

```python
from backend.metrics_service import publish_batch

async def my_function():
    await publish_batch("ml", {
        "model_accuracy": 0.94,
        "deployment_success": 1.0,
        "inference_latency": 0.028
    })
```

---

## Understanding the Output

### CLI Status Output

```
Grace Cognition Status
Timestamp: 2025-11-03T10:30:00

┏━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Metric      ┃ Value  ┃
┡━━━━━━━━━━━━━╇━━━━━━━━┩
│ Health      │ 88.0%  │  ← Overall system health
│ Trust       │ 84.0%  │  ← Trustworthiness score
│ Confidence  │ 82.0%  │  ← Confidence level
│ SaaS Ready  │ 🔧 No  │  ← Ready for commercialization?
└─────────────┴────────┘
```

### Domain Performance

Each domain shows:
- **Health** - Weighted average of KPIs
- **Trust** - Derived from health × 0.95
- **Confidence** - Derived from health × 0.92

---

## What Happens When Grace Hits 90%?

When **all three benchmarks** (Health, Trust, Confidence) sustain **≥ 90%** for **7 consecutive days**:

1. 🚀 **Event Emitted:** `product.elevation_ready` via trigger mesh
2. 📄 **Report Generated:** Comprehensive SaaS readiness report
3. 📧 **Alerts Sent:** Notifications logged (future: email/Slack)
4. ✅ **Status Updated:** `saas_ready: true` in API responses

---

## Monitoring Tips

### Watch Live
```bash
grace cognition watch
# Updates every 5 seconds
# Press Ctrl+C to stop
```

### Check Specific Domain
```bash
grace transcendence metrics
grace security metrics
grace ml metrics
```

### Generate Reports
```bash
# Generate and save
grace cognition readiness-report

# View without saving
grace cognition view-report
```

---

## Domain KPI Summary

| Domain | Key Metrics |
|--------|------------|
| **Core** | uptime, governance_score, healing_actions |
| **Transcendence** | task_success, code_quality, planning_accuracy |
| **Knowledge** | trust_score, recall_accuracy, ingestion_rate |
| **Security** | threats_detected, scan_coverage, auto_fix_success |
| **ML** | model_accuracy, deployment_success, inference_latency |
| **Temporal** | prediction_accuracy, graph_completeness, sim_quality |
| **Parliament** | vote_participation, compliance_score, reflection_quality |
| **Federation** | connector_health, api_success, plugin_uptime |
| **Cognition** | overall_health, overall_trust, saas_readiness |
| **Speech** | recognition_accuracy, synthesis_quality, command_success |

---

## Troubleshooting

### "Connection refused" error
```bash
# Make sure backend is running
curl http://localhost:8000/health
# Should return: {"status":"ok","message":"Grace API is running"}
```

### No metrics showing
```bash
# Publish some test metrics first
python test_metrics.py

# Then check status
grace cognition status
```

### CLI command not found
```bash
# Run from grace_rebuild directory
cd grace_rebuild

# Or set PYTHONPATH
export PYTHONPATH=/path/to/grace_rebuild:$PYTHONPATH
```

---

## Next Steps

1. **Integrate Publishers** - Add metric publishing to your domain code
2. **Monitor Progress** - Use `grace cognition watch` to track improvements
3. **Iterate** - Focus on domains below 90% health
4. **Wait for 90%** - Let the system accumulate 7 days of data
5. **Launch** - When `product.elevation_ready` fires, follow the roadmap!

---

## Full Documentation

See `docs/COGNITION_DASHBOARD.md` for:
- Complete API reference
- All KPI definitions
- Database schema
- Integration patterns
- Advanced features

---

## Quick Reference

```bash
# Status
grace cognition status

# Readiness
grace cognition readiness

# Live watch
grace cognition watch

# Domain metrics
grace <domain> metrics

# Generate report
grace cognition readiness-report

# View report
grace cognition view-report
```

---

**Ready to monitor Grace's cognitive health! 🧠✨**
