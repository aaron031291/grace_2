# Meta-Loop Quick Reference Card

## 🚀 What Is It?

**Self-optimizing system** that analyzes GRACE's performance, generates recommendations, and applies changes to improve effectiveness.

## 📊 Three-Level Architecture

```
Level 1: Meta-Loop       → Analyzes operations, generates recommendations
Level 2: Meta-Meta       → Evaluates if meta-changes helped
Level 3: Meta-Meta-Meta  → (Future) Optimizes the optimization
```

## 🔄 Workflow (30 seconds)

```
1. Meta-loop detects issue (e.g., low task completion)
2. Generates recommendation (e.g., "increase threshold")
3. Submits to approval queue
4. Auto-approves if low-risk OR waits for admin
5. Applies change with governance/verification
6. Measures effectiveness after 24h
7. Rolls back if performance degrades
```

## 🌐 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/meta/recommendations/pending` | View pending recommendations |
| POST | `/api/meta/recommendations/{id}/approve` | Approve & apply |
| POST | `/api/meta/recommendations/{id}/reject` | Reject with reason |
| GET | `/api/meta/recommendations/applied` | View history with metrics |
| POST | `/api/meta/recommendations/{id}/rollback` | Undo a change |
| GET | `/api/meta/recommendations/stats` | System statistics |

## 📝 Example: Approve a Recommendation

```bash
# 1. View pending
curl http://localhost:8000/api/meta/recommendations/pending

# 2. Approve #1
curl -X POST http://localhost:8000/api/meta/recommendations/1/approve \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"reason": "Looks good"}'

# 3. Check results
curl http://localhost:8000/api/meta/recommendations/applied
```

## 🔒 Safety Features

| Feature | Description |
|---------|-------------|
| **Validation** | All changes checked against safety limits |
| **Risk Assessment** | Low/medium/high risk classification |
| **Auto-Approval** | Only for low-risk + high-confidence |
| **Governance** | Policies enforce review/deny rules |
| **Before/After Metrics** | Captures performance data |
| **Auto-Rollback** | Reverts if effectiveness < -20% |
| **Verification** | Cryptographic signing of all changes |

## 📐 Safety Limits

| Parameter | Min | Max |
|-----------|-----|-----|
| Task threshold | 1 | 10 |
| Reflection interval | 10s | 3600s |
| Task priority | 1 | 10 |
| Completion threshold | 0.1 | 1.0 |

## 🎯 Recommendation Types

1. **threshold_change** - Adjust operational thresholds
2. **interval_change** - Modify loop intervals (reflection, meta-loop)
3. **priority_change** - Change default task priorities

## 🤖 Auto-Approval Criteria

Change is auto-approved if:
- Risk level = "low" AND confidence ≥ 0.8
- OR interval change ≥ 60s

## 📊 Key Metrics

| Metric | What It Means |
|--------|---------------|
| Effectiveness Score | % improvement in completion rate |
| Confidence | How sure meta-loop is (0-1) |
| Risk Level | low/medium/high |
| Rollback Rate | % of changes that needed reverting |

## 🔍 Monitoring

Check these regularly:
- Pending queue: `/api/meta/recommendations/pending`
- Stats: `/api/meta/recommendations/stats`
- Applied history: `/api/meta/recommendations/applied`
- Meta-loop logs (every 300s)

## ⚡ Quick Actions

### View Stats
```python
from grace_rebuild.backend.meta_loop_approval import approval_queue
stats = await approval_queue.get_pending_recommendations()
```

### Submit Custom Recommendation
```python
rec_id = await approval_queue.submit_for_approval(
    meta_analysis_id=1,
    recommendation_type="threshold_change",
    target="task_threshold",
    current_value=3,
    proposed_value=5,
    recommendation_text="Reduce noise",
    confidence=0.8,
    risk_level="low",
    payload={"component": "learning"}
)
```

### Rollback
```python
from grace_rebuild.backend.meta_loop_engine import recommendation_applicator
await recommendation_applicator.rollback_change(
    applied_id=5,
    reason="Performance degraded"
)
```

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| Nothing auto-approved | Check confidence ≥ 0.8 and risk = "low" |
| Governance blocking | Review governance policies, check audit logs |
| No effectiveness data | Wait 24h after application |
| Unexpected rollback | Check meta-meta evaluations, investigate regression |

## 📁 Files

| File | Purpose |
|------|---------|
| `meta_loop.py` | Level 1 meta-loop engine |
| `meta_loop_engine.py` | Recommendation applicator |
| `meta_loop_approval.py` | Approval queue & workflow |
| `routes/meta_api.py` | REST API endpoints |
| `seed_meta_governance.py` | Governance policies |
| `META_LOOP_SYSTEM.md` | Full documentation |

## 🎓 Learn More

- Full docs: `grace_rebuild/backend/META_LOOP_SYSTEM.md`
- Activation summary: `grace_rebuild/META_LOOP_ACTIVATION_SUMMARY.md`
- Test workflow: `grace_rebuild/backend/test_meta_loop_workflow.py`

## ✨ Status

🟢 **FULLY ACTIVATED AND OPERATIONAL**

Meta-loop runs every 300s, analyzing performance and generating recommendations automatically.
