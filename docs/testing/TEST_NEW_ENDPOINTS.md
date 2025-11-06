# Testing New Observability Endpoints

## Quick Test Guide

### Prerequisites
```bash
# Start GRACE
cd c:/Users/aaron/grace_2
python backend/minimal_backend.py
```

Wait for:
```
✓ Agentic memory broker started
✓ Meta-coordinated healing started
✓ Self-healing predictor started
```

---

## Test 1: Learning Aggregates

### All Time Statistics
```bash
curl -X GET "http://localhost:8000/api/self_heal/learning?time_bucket=all" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "bucket": "All Time",
  "time_range": "all",
  "total_runs": 0,
  "overall_success_rate": 0.0,
  "by_playbook": {},
  "by_service": {},
  "by_status": {},
  "playbook_rankings": [],
  "recent_trends": []
}
```

### Last 24 Hours
```bash
curl -X GET "http://localhost:8000/api/self_heal/learning?time_bucket=24h" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Last 7 Days
```bash
curl -X GET "http://localhost:8000/api/self_heal/learning?time_bucket=7d" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Service
```bash
curl -X GET "http://localhost:8000/api/self_heal/learning?time_bucket=24h&service=api_cluster" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Playbook
```bash
curl -X GET "http://localhost:8000/api/self_heal/learning?time_bucket=7d&playbook=scale_up_instances" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Test 2: Scheduler Counters

### Get Scheduler State
```bash
curl -X GET "http://localhost:8000/api/self_heal/scheduler_counters" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "scheduler_state": {
    "poll_interval_seconds": 30,
    "running": true
  },
  "backoff": {
    "active_count": 0,
    "services": []
  },
  "rate_limiting": {
    "active_count": 0,
    "services": []
  },
  "statistics": {
    "total_backoff_entries": 0,
    "total_rate_tracked_services": 0
  },
  "metadata": {
    "timestamp": "2025-01-15T14:30:00Z",
    "observe_only": true,
    "execute_enabled": false
  }
}
```

### Scheduler Health Check
```bash
curl -X GET "http://localhost:8000/api/self_heal/scheduler_health" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected:**
```json
{
  "status": "running",
  "poll_interval_seconds": 30,
  "backoff_entries": 0,
  "rate_tracked_services": 0,
  "healthy": true
}
```

---

## Test 3: Meta Focus

### Get Current Focus
```bash
curl -X GET "http://localhost:8000/api/meta/focus" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "current_cycle": {
    "cycle_id": "cycle_20250115_143000_42",
    "focus_area": "routine_maintenance",
    "confidence": 0.85,
    "guardrail_adjustment": "maintain",
    "reasoning": ["System stable", "Routine checks"],
    "extra_probes": [],
    "playbook_priorities": ["increase_logging"],
    "time_budget_seconds": 120
  },
  "health_distress": {
    "score": 15.5,
    "critical_count": 0,
    "degraded_count": 1,
    "healthy_count": 3,
    "open_incidents": 0
  },
  "critical_services": [],
  "degraded_services": [
    {
      "service": "reflection_service",
      "status": "degraded",
      "confidence": 0.75,
      "top_symptoms": ["stale_reflections"],
      "last_updated": "2025-01-15T14:25:00Z"
    }
  ],
  "open_incidents": [],
  "recommendations": {
    "focus_area": "preventive_maintenance",
    "guardrail_adjustment": "maintain",
    "reasoning": [
      "No critical services",
      "1 degraded service",
      "No open incidents",
      "Distress score: 15.5/100"
    ]
  },
  "metadata": {
    "timestamp": "2025-01-15T14:30:00Z",
    "guardrail_state": "maintain",
    "total_cycles": 42
  }
}
```

### Get Meta Loop Cycles
```bash
curl -X GET "http://localhost:8000/api/meta/cycles?limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Test 4: Learning Outcomes

### Get Recent Outcomes
```bash
curl -X GET "http://localhost:8000/api/self_heal/learning/outcomes?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Service
```bash
curl -X GET "http://localhost:8000/api/self_heal/learning/outcomes?service=api_cluster&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Test 5: Integration Test

### Simulate a Full Cycle

**Watch backend logs for:**
```
🔄 Meta Loop Cycle 1 - 14:30:00
  📋 Focus: routine_maintenance
  🛡️ Guardrails: maintain
```

Then check:
```bash
# 1. Check meta focus changed
curl http://localhost:8000/api/meta/focus

# 2. Check scheduler is processing
curl http://localhost:8000/api/self_heal/scheduler_health

# 3. Check learning data accumulating
curl http://localhost:8000/api/self_heal/learning?time_bucket=24h
```

---

## Expected Results Summary

### Fresh Install (No Data Yet)
```
✅ /api/self_heal/learning → total_runs: 0
✅ /api/self_heal/scheduler_counters → running: true, backoff: 0
✅ /api/meta/focus → current_cycle exists, distress: low
✅ /api/self_heal/scheduler_health → healthy: true
```

### After Running (With Data)
```
✅ /api/self_heal/learning → Shows playbook success rates
✅ /api/self_heal/scheduler_counters → Shows backoff/rate limits if active
✅ /api/meta/focus → Shows actual focus area, distress score
✅ /api/self_heal/learning/outcomes → Shows learning log entries
```

---

## Troubleshooting

### 404 Error
**Cause:** Feature flags not enabled  
**Fix:** Set `SELF_HEAL_OBSERVE_ONLY=True` or `LEARNING_AGGREGATION_ENABLED=True`

### 503 Error  
**Cause:** Models not imported  
**Fix:** Check database migrations, ensure models loaded

### Empty Data
**Cause:** No playbook runs yet (normal on fresh install)
**Action:** Wait for scheduler to create proposals, or manually create test data

### 401 Unauthorized
**Cause:** No auth token  
**Fix:** Login first or use test user credentials

---

## Success Criteria

✅ All endpoints return 200 OK  
✅ Learning endpoint shows structure (even if empty)  
✅ Scheduler counters show running state  
✅ Meta focus shows current cycle  
✅ No errors in backend logs  
✅ Feature flags work (404 when disabled)  

---

## Next: Generate Test Data

To see the endpoints with actual data, trigger some playbook proposals:

```python
# In Python or via API
from backend.self_heal_models import PlaybookRun
from backend.models import async_session

async with async_session() as session:
    run = PlaybookRun(
        service="test_service",
        status="proposed",
        requested_by="test",
        diagnosis='{"code": "test", "title": "Test Run"}'
    )
    session.add(run)
    await session.commit()
```

Then recheck `/api/self_heal/learning?time_bucket=24h` to see the data.

---

**All 3 observability endpoints are ready for production use!** 🎉
