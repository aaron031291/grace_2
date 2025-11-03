# Grace Cognition System - Quick Start

Get Grace's 10-domain cognition system running in 5 minutes.

---

## 1. Start the Backend

```bash
cd grace_rebuild
python -m uvicorn backend.main:app --reload
```

Backend will be available at: http://localhost:8000

---

## 2. View Live Cognition Dashboard

```bash
cd cli
python grace_unified.py cognition
```

You'll see:
- Overall health, trust, confidence (0-100%)
- 10-domain grid with real-time KPIs
- 🚀 SaaS Ready indicator (when benchmarks hit 90%)

---

## 3. Check SaaS Readiness

```bash
python grace_unified.py readiness
```

Shows:
- Current vs. target benchmarks
- Sustained status over 7-day window
- Next steps to commercialization
- Grace's self-assessment

---

## 4. Test Domain Commands

### Core - Platform Operations
```bash
python grace_unified.py core heartbeat
python grace_unified.py core governance
python grace_unified.py core self-heal
```

### Transcendence - Agentic Development
```bash
python grace_unified.py transcendence plan "build authentication system"
python grace_unified.py transcendence memory "jwt patterns"
```

### Security - Hunter Protection
```bash
python grace_unified.py security scan ./backend
python grace_unified.py security alerts
python grace_unified.py security rules
```

---

## 5. Test API Directly

### Get Cognition Status
```bash
curl http://localhost:8000/api/cognition/status
```

### Get Readiness Report
```bash
curl http://localhost:8000/api/cognition/readiness
```

### Core Heartbeat
```bash
curl http://localhost:8000/api/core/heartbeat
```

### Transcendence Plan
```bash
curl -X POST http://localhost:8000/api/transcendence/plan \
  -H "Content-Type: application/json" \
  -d '{"task_description": "build auth system", "context": {}}'
```

### Security Scan
```bash
curl -X POST http://localhost:8000/api/security/scan \
  -H "Content-Type: application/json" \
  -d '{"path": "./backend", "deep": false}'
```

---

## 6. Publish Metrics from Your Code

Add to any backend service:

```python
from backend.metrics_service import publish_metric

# After completing a task
await publish_metric("transcendence", "task_success", 1.0, {
    "task_id": "123",
    "duration": 5.2
})

# After generating code
await publish_metric("transcendence", "code_quality", 0.92, {
    "lines": 150,
    "language": "python"
})

# After security scan
await publish_metric("security", "threats_detected", 3.0)
await publish_metric("security", "scan_coverage", 0.94)
```

Batch publishing:
```python
from backend.metrics_service import publish_batch

await publish_batch("ml", {
    "model_accuracy": 0.94,
    "deployment_success": 1.0,
    "inference_latency": 0.032
})
```

---

## 7. Watch Benchmarks Climb to 90%

As you use Grace, metrics accumulate:
1. Each operation publishes KPIs
2. Rolling 7-day windows track trends
3. Health/trust/confidence aggregate across domains
4. When all three sustain ≥90% for 7 days → **SaaS Ready!**

### Monitor Progress
```bash
# Live dashboard (updates every 2 seconds)
python grace_unified.py cognition

# Detailed benchmark status
curl http://localhost:8000/api/cognition/benchmark/overall_health
curl http://localhost:8000/api/cognition/benchmark/overall_trust
curl http://localhost:8000/api/cognition/benchmark/overall_confidence
```

---

## 8. When Grace Hits 90%

The CLI will show:
```
Grace Overall Cognition ● READY FOR COMMERCIALIZATION
┌────────────┬───────┬────────────────────┐
│ Metric     │ Value │ Bar                │
├────────────┼───────┼────────────────────┤
│ Health     │ 92%   │ ████████████████░░ │
│ Trust      │ 91%   │ ████████████████░░ │
│ Confidence │ 90%   │ ████████████████░░ │
│ Status     │ 🚀 SaaS Ready            │
└────────────┴───────┴────────────────────┘
```

Grace will tell you it's time to commercialize with:
- Auto-generated readiness report
- Next steps checklist
- Usage stats and proof points
- Go-to-market recommendations

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    CLI (Downloadable)                    │
│  grace cognition | grace core | grace transcendence     │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│  /api/cognition/* | /api/core/* | /api/transcendence/* │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────┐
│   Metrics    │  │    Cognition     │  │   10 Domains │
│  Collector   │  │     Engine       │  │              │
│              │  │                  │  │ Core         │
│ - Publishes  │  │ - Aggregates     │  │ Transcend    │
│ - Windows    │  │ - Benchmarks     │  │ Knowledge    │
│ - Subscribers│  │ - 90% Trigger    │  │ Security     │
│              │  │                  │  │ ML           │
└──────────────┘  └──────────────────┘  │ Temporal     │
                                        │ Parliament   │
                                        │ Federation   │
                                        │ Cognition    │
                                        │ Speech       │
                                        └──────────────┘
```

---

## 10 Domains at a Glance

| Domain | Icon | Purpose | CLI Command |
|--------|------|---------|-------------|
| Core | 💓 | Platform operations | `grace core heartbeat` |
| Transcendence | 🧠 | Agentic dev partner | `grace transcendence plan` |
| Knowledge | 📚 | Ingestion & BI | `grace knowledge search` |
| Security | 🛡️ | Hunter protection | `grace security scan` |
| ML | 🤖 | Learning & deployment | `grace ml deploy` |
| Temporal | ⏰ | Causal & forecasting | `grace temporal simulate` |
| Parliament | 🏛️ | Governance & meta | `grace parliament vote` |
| Federation | 🌐 | External integration | `grace federation connectors` |
| Cognition | 🧠📊 | Real-time intelligence | `grace cognition` |
| Speech | 🎤 | Voice interface | `grace speech listen` |

---

## Troubleshooting

### Backend won't start
```bash
# Install dependencies
pip install -r requirements.txt

# Check database
python reset_db.py
```

### CLI not found
```bash
# Run directly
python grace_unified.py cognition

# Or install
pip install -e .
grace cognition
```

### Metrics not appearing
```bash
# Check backend logs
# Ensure operations are publishing metrics
# Verify /api/cognition/status returns data
```

### Can't connect to backend
```bash
# Specify backend URL
python grace_unified.py cognition --backend http://localhost:8000
```

---

## What's Next?

1. Use Grace for your daily development
2. Watch metrics accumulate
3. Wait for 90% sustained benchmarks
4. Grace will signal when ready for SaaS
5. Follow the commercialization checklist

**Grace is your personal R&D platform until she tells you it's time to scale!**
