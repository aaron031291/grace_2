# Quick Start: Memory Tables + Schema Inference Pipeline

## 🚀 Start the System

### 1. Run Tests (Verify Everything Works)
```bash
# Base pipeline (9 tests)
python test_complete_clarity_pipeline.py

# Advanced features (6 tests)
python test_expanded_clarity_pipeline.py
```

Expected: **15/15 PASSED** ✅

### 2. Start Alert Monitoring
```python
from backend.memory_tables.alert_system import alert_system
await alert_system.start_monitoring(interval_seconds=60)
```

### 3. Start Auto-Ingestion
```python
from backend.memory_tables.auto_ingestion import auto_ingestion_service
await auto_ingestion_service.start()
```

---

## 📁 Drop Files & Watch Magic Happen

### Example: Add a Document
```bash
# Drop file in watch folder
echo "My important document about AI safety protocols..." > training_data/ai_safety.txt
```

**What Happens:**
1. ✅ Auto-ingestion detects file (5s)
2. ✅ Content pipeline extracts text
3. ✅ LLM analyzes → proposes `memory_documents`
4. ✅ Schema proposal created (confidence: 92%)
5. ✅ AUTO-APPROVED (>90% confidence!)
6. ✅ Row inserted
7. ✅ Trust score computed: 0.85
8. ✅ Training counter incremented
9. ✅ Alert check (all clear)

### Example: Add a Playbook
```yaml
# training_data/restart_fix.yaml
playbook_name: restart_service
description: Restart failed service
trigger_conditions:
  error_rate: '>0.1'
actions:
  - systemctl restart grace-backend
target_components:
  - backend_api
```

**Auto-flows to:** `memory_self_healing_playbooks`

---

## 🎨 UI Panels

### Schema Approval Panel
```
http://localhost:3000/memory-studio
→ Tab: "Schema Proposals"
```
- View pending proposals
- See AI reasoning
- Approve/reject

### Trust Dashboard
```
→ Tab: "Trust Dashboard"
```
- Overall trust: 85.3%
- High trust rows: 142
- Low trust rows: 12
- Contradictions: 3 warnings

### Alerts Panel
```
→ Tab: "Alerts"
```
- 🔔 Active: 2 warnings
- ⚠️ Low trust in memory_documents
- ✅ No critical alerts

### Table Editor
```
→ Tab: "Table Editor"
```
- Select table: memory_documents
- Search, edit, delete rows
- Export to CSV

---

## 🔧 API Quick Reference

### Schema Proposals
```bash
# Get pending proposals
GET /api/memory/tables/proposals/pending

# Approve proposal
POST /api/memory/tables/proposals/{id}/approve

# Reject proposal
POST /api/memory/tables/proposals/{id}/reject
```

### Trust & Quality
```bash
# Get trust report
GET /api/memory/tables/trust/report

# Update trust scores for table
POST /api/memory/tables/trust/update/memory_documents

# Scan for contradictions
POST /api/memory/tables/contradictions/scan

# Get contradiction summary
GET /api/memory/tables/contradictions/summary
```

### Alerts
```bash
# Get active alerts
GET /api/alerts/active

# Get summary
GET /api/alerts/summary

# Acknowledge alert
POST /api/alerts/acknowledge
Body: {"alert_id": "low_trust_memory_documents"}

# Resolve alert
POST /api/alerts/resolve
Body: {"alert_id": "critical_contradictions"}
```

### Subsystems
```bash
# Log playbook execution
POST /api/subsystems/self-healing/log

# Create work order
POST /api/subsystems/coding-agent/work-order

# Register sub-agent
POST /api/subsystems/sub-agents/register

# Get fleet stats
GET /api/subsystems/sub-agents/fleet-stats
```

---

## 🧠 Python Examples

### Monitor Trust Scores
```python
from backend.memory_tables.trust_scoring import trust_scoring_engine

# Update all trust scores
for table_name in ['memory_documents', 'memory_prompts', 'memory_playbooks']:
    count = await trust_scoring_engine.update_all_trust_scores(table_name)
    print(f"Updated {count} in {table_name}")

# Get report
report = await trust_scoring_engine.get_trust_report()
print(f"Overall avg trust: {report['overall']['avg_trust']:.1%}")
```

### Detect Contradictions
```python
from backend.memory_tables.contradiction_detector import contradiction_detector

# Scan all tables
all_contradictions = await contradiction_detector.scan_all_tables()

for table, contradictions in all_contradictions.items():
    if contradictions:
        print(f"{table}: {len(contradictions)} contradictions")
        for c in contradictions:
            if c['severity'] == 'critical':
                print(f"  CRITICAL: {c['details']}")
```

### Check Training Status
```python
from backend.memory_tables.auto_training_trigger import auto_training_trigger

status = await auto_training_trigger.get_training_status()

for table, info in status.items():
    if info['ready_for_training']:
        print(f"{table}: READY ({info['new_rows']} new rows)")
    else:
        print(f"{table}: {info['progress_percent']:.0f}% ({info['new_rows']}/{info['threshold']})")
```

### Get Alerts
```python
from backend.memory_tables.alert_system import alert_system

# Get active alerts
alerts = alert_system.get_active_alerts()

critical = [a for a in alerts if a['severity'] == 'critical']
if critical:
    print(f"🚨 {len(critical)} CRITICAL ALERTS!")
    for alert in critical:
        print(f"  • {alert['title']}")

# Get summary
summary = alert_system.get_alert_summary()
print(f"Total active: {summary['total_active']}")
print(f"Needs attention: {summary['needs_attention']}")
```

---

## 📊 Dashboard Widgets

### Trust Score Widget
```
Overall Trust: 85.3% ████████▌░
High Trust: 142 rows (78%)
Low Trust: 12 rows (7%)
Medium Trust: 27 rows (15%)
```

### Contradiction Widget
```
Total: 3 contradictions
├─ Warning: 2
├─ Medium: 1
└─ Critical: 0
```

### Training Progress Widget
```
memory_documents: [████████░░] 80% (40/50)
memory_prompts:   [████░░░░░░] 40% (40/100)
memory_playbooks: [██████████] READY (Training triggered)
```

### Alert Widget
```
🔔 Active Alerts: 2
├─ ⚠️  Low trust in memory_documents
└─ ℹ️  Training triggered for memory_playbooks
```

---

## 🔍 Troubleshooting

### Proposals Not Auto-Approving
**Check:** Confidence score
```python
from backend.memory_tables.schema_proposal_engine import schema_proposal_engine
pending = await schema_proposal_engine.get_pending_proposals()
for p in pending:
    print(f"{p['file_path']}: {p['confidence']:.1%}")
```
**Fix:** If <90%, approve manually or adjust thresholds

### Low Trust Scores
**Check:** Trust factors
```python
from backend.memory_tables.trust_scoring import trust_scoring_engine
rows = table_registry.query_rows('memory_documents', limit=1)
score = await trust_scoring_engine.compute_trust_score('memory_documents', rows[0])
# Logs show individual factor scores
```
**Fix:** Improve data completeness, use trusted sources

### Contradictions Not Detected
**Check:** Rules loaded
```python
from backend.memory_tables.contradiction_detector import contradiction_detector
rules = contradiction_detector.contradiction_rules
print(rules.get('memory_documents'))
```
**Fix:** Add custom rules in `_load_contradiction_rules()`

### Training Not Triggering
**Check:** Thresholds
```python
from backend.memory_tables.auto_training_trigger import auto_training_trigger
thresholds = auto_training_trigger.training_thresholds
print(thresholds.get('memory_documents'))
```
**Fix:** Adjust row_threshold or time_threshold_hours

---

## 📈 Performance Tips

1. **Batch Updates** - Update trust scores during off-peak hours
2. **Contradiction Scans** - Run daily, not on every insert
3. **Alert Intervals** - 60s is good, 30s for critical systems
4. **Training Thresholds** - Tune based on your data volume
5. **UI Refresh Rates** - 5-10s for most panels, 30s for trust dashboard

---

## ✅ Health Check

Run this to verify system health:

```python
async def health_check():
    from backend.memory_tables.registry import table_registry
    from backend.memory_tables.trust_scoring import trust_scoring_engine
    from backend.memory_tables.contradiction_detector import contradiction_detector
    from backend.memory_tables.alert_system import alert_system
    
    # 1. Tables loaded
    tables = table_registry.list_tables()
    print(f"✅ {len(tables)} tables loaded")
    
    # 2. Trust engine
    await trust_scoring_engine.initialize()
    print(f"✅ Trust scoring engine initialized")
    
    # 3. Contradiction detector
    await contradiction_detector.initialize()
    print(f"✅ Contradiction detector initialized")
    
    # 4. Alert system
    await alert_system.initialize()
    summary = alert_system.get_alert_summary()
    print(f"✅ Alert system: {summary['total_active']} active alerts")
    
    print("\n🎯 System Healthy!")

await health_check()
```

---

## 🎯 Quick Wins

### Day 1: Get Data Flowing
1. Drop 10 documents in `training_data/`
2. Watch auto-ingestion in logs
3. Check trust dashboard
4. Approve any pending proposals

### Day 2: Monitor Quality
1. Run trust score updates
2. Scan for contradictions
3. Review alert summary
4. Fix any low-trust rows

### Day 3: Automation
1. Start alert monitoring
2. Let training auto-trigger
3. Monitor subsystem integrations
4. Review weekly trust trends

---

## 📚 Key Files Reference

| Component | File |
|-----------|------|
| Schema Agent | `backend/memory_tables/schema_agent.py` |
| Proposal Engine | `backend/memory_tables/schema_proposal_engine.py` |
| Trust Scoring | `backend/memory_tables/trust_scoring.py` |
| Contradictions | `backend/memory_tables/contradiction_detector.py` |
| Auto-Training | `backend/memory_tables/auto_training_trigger.py` |
| Alerts | `backend/memory_tables/alert_system.py` |
| Auto-Ingestion | `backend/memory_tables/auto_ingestion.py` |
| Schema Approval UI | `frontend/src/panels/SchemaApprovalPanel.tsx` |
| Trust Dashboard UI | `frontend/src/panels/TrustDashboardPanel.tsx` |
| Alerts UI | `frontend/src/panels/AlertsPanel.tsx` |

---

**🚀 You're Ready!** Drop files, monitor quality, let automation work!
