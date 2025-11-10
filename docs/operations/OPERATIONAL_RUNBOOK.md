# Grace Operational Runbook
## Complete Guide for System Operations

**For:** Operators, SRE, DevOps, Junie (can follow at any pace)

---

## Quick Reference

| Task | Command | Time |
|------|---------|------|
| **Start Grace** | `.\GRACE.ps1` | 3-5 min |
| **Check Status** | `.\GRACE.ps1 -Status` | 5 sec |
| **View Logs** | `.\GRACE.ps1 -Logs` | Instant |
| **Stop Grace** | `.\GRACE.ps1 -Stop` | 5 sec |
| **Health Check** | `curl http://localhost:8000/health` | Instant |
| **Logic Hub Stats** | `curl http://localhost:8000/api/logic-hub/stats` | Instant |

---

## Starting Grace

### Standard Start
```powershell
cd C:\Users\aaron\grace_2
.\GRACE.ps1
```

**What Happens:**
1. ✅ Cleans up old jobs
2. ✅ Checks Python/venv
3. ✅ Installs dependencies (~2-5 min first time)
4. ✅ Runs database migrations (~5 sec)
5. ✅ Seeds governance policies (~10 sec)
6. ✅ Verifies unified logic systems (~5 sec)
7. ✅ Runs boot pipeline (~30 sec)
8. ✅ Starts backend server
9. ✅ Waits for health check (up to 30 sec)
10. ✅ Shows success message

**Total Time:** 3-5 minutes first time, 1-2 minutes subsequent

### Troubleshooting Boot Failures

#### Issue: Database Migration Fails
```powershell
# Check migration status
.venv\Scripts\python.exe -m alembic current

# Manually run migrations
.venv\Scripts\python.exe -m alembic upgrade head

# If still fails, check logs
.venv\Scripts\python.exe -m alembic history
```

#### Issue: Governance Policies Fail
```powershell
# Manually seed policies
.venv\Scripts\python.exe -m backend.seed_governance_policies

# Check policy count
.venv\Scripts\python.exe -c "import sqlite3; conn = sqlite3.connect('databases/grace.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM governance_policies'); print('Policies:', cursor.fetchone()[0]); conn.close()"
```

#### Issue: System Verification Fails
```powershell
# Test each system individually
.venv\Scripts\python.exe -c "from backend.unified_logic_hub import unified_logic_hub; print('Logic Hub OK')"

.venv\Scripts\python.exe -c "from backend.memory_fusion_service import memory_fusion_service; print('Memory Fusion OK')"

.venv\Scripts\python.exe -c "from backend.capa_system import capa_system; print('CAPA OK')"
```

#### Issue: Backend Won't Start
```powershell
# Check for port conflicts
netstat -ano | findstr :8000

# If port is in use, kill the process
taskkill /PID <PID> /F

# Try starting manually
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

---

## Verification Steps (Smoke Tests)

### After Successful Boot

#### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "checks": {
    "database": "healthy",
    "trigger_mesh": "healthy",
    ...
  }
}
```

#### 2. Logic Hub Stats
```bash
curl http://localhost:8000/api/logic-hub/stats
```

**Expected:**
```json
{
  "total_updates": 0,
  "successful_updates": 0,
  "failed_updates": 0,
  "rollbacks": 0,
  "success_rate": 0.0
}
```

#### 3. Memory Fusion Stats
```bash
curl http://localhost:8000/api/memory-fusion/stats
```

**Expected:**
```json
{
  "service": "memory_fusion",
  "crypto_enabled": true,
  "governance_enabled": true,
  "logic_hub_enabled": true
}
```

#### 4. CAPA Metrics
```bash
curl http://localhost:8000/api/capa/metrics/stats
```

**Expected:**
```json
{
  "total_capas": 0,
  "open_capas": 0,
  "closed_capas": 0
}
```

#### 5. Submit Test Update
```bash
curl -X POST http://localhost:8000/api/logic-hub/updates/schema \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "/api/test",
    "proposed_schema": {"type": "object", "properties": {"test": {"type": "string"}}},
    "created_by": "runbook_test",
    "risk_level": "low"
  }'
```

**Expected:**
```json
{
  "update_id": "update_...",
  "status": "submitted",
  "message": "Schema update submitted for /api/test"
}
```

#### 6. Verify Update Processed
```bash
# Get update ID from previous response
curl http://localhost:8000/api/logic-hub/updates/{update_id}
```

**Expected:**
```json
{
  "update_id": "update_...",
  "status": "distributed",
  "validation_results": {"passed": true}
}
```

**If all 6 tests pass:** ✅ Grace is fully operational

---

## Monitoring & Observability

### Real-Time Monitoring

#### Check System Status
```powershell
.\GRACE.ps1 -Status
```

**Shows:**
- Job status
- Backend health
- API availability

#### View Live Logs
```powershell
.\GRACE.ps1 -Logs
```

**Shows:**
- Last 30 log lines from each job
- Real-time system activity

### Metrics Queries

#### Get All Metrics
```bash
curl http://localhost:8000/api/metrics
```

#### Query Specific Metric
```bash
curl "http://localhost:8000/api/metrics?metric_id=logic_hub.update_latency_p95"
```

#### Check Immutable Log
```bash
curl http://localhost:8000/api/immutable-log/entries?subsystem=unified_logic_hub&limit=20
```

### Anomaly Detection

#### Check Anomalies
```bash
curl http://localhost:8000/api/anomalies
```

#### Get Active CAPAs
```bash
curl http://localhost:8000/api/capa/?severity=critical
```

---

## Rollback Procedures

### Automatic Rollback

**Triggers:**
- Critical anomaly during observation window
- Stability score < 0.5
- Repeated failures in health checks

**Process:**
1. Watchdog detects critical anomaly
2. Logic update awareness triggers rollback
3. Unified logic hub executes rollback
4. Trigger mesh notifies all subsystems
5. CAPA automatically created
6. Immutable log records all steps

**No action required** - automatic

### Manual Rollback

#### Find Update to Rollback
```bash
# List recent updates
curl http://localhost:8000/api/logic-hub/updates?limit=20

# Get specific update details
curl http://localhost:8000/api/logic-hub/updates/{update_id}
```

#### Trigger Rollback
```bash
curl -X POST http://localhost:8000/api/logic-hub/updates/{update_id}/rollback
```

#### Verify Rollback
```bash
# Check update status (should show "rolled_back")
curl http://localhost:8000/api/logic-hub/updates/{update_id}

# Check affected components health
curl http://localhost:8000/health
```

#### Review CAPA
```bash
# CAPAs auto-created for rollbacks
curl http://localhost:8000/api/capa/

# Get CAPA details
curl http://localhost:8000/api/capa/{capa_id}
```

---

## Common Issues & Fixes

### Issue: Port 8000 Already in Use
```powershell
# Find process using port
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F

# Restart Grace
.\GRACE.ps1
```

### Issue: Database Locked
```powershell
# Stop Grace
.\GRACE.ps1 -Stop

# Wait 10 seconds
Start-Sleep -Seconds 10

# Delete lock files
Remove-Item databases\grace.db-wal -ErrorAction SilentlyContinue
Remove-Item databases\grace.db-shm -ErrorAction SilentlyContinue

# Restart
.\GRACE.ps1
```

### Issue: Migration Out of Sync
```powershell
# Check current migration
.venv\Scripts\python.exe -m alembic current

# See all migrations
.venv\Scripts\python.exe -m alembic history

# Upgrade to latest
.venv\Scripts\python.exe -m alembic upgrade head
```

### Issue: Missing Dependencies
```powershell
# Reinstall all dependencies
.venv\Scripts\pip install -r backend\requirements.txt --force-reinstall
```

---

## Post-Boot Stress Test

### Mini Stress Test (5 minutes)

```bash
# 1. Submit 10 updates rapidly
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/logic-hub/updates/schema \
    -H "Content-Type: application/json" \
    -d "{\"endpoint\": \"/test_$i\", \"proposed_schema\": {\"type\": \"object\"}, \"created_by\": \"stress_test\", \"risk_level\": \"low\"}"
done

# 2. Fetch memories 50 times
for i in {1..50}; do
  curl -X POST http://localhost:8000/api/memory-fusion/fetch \
    -H "Content-Type: application/json" \
    -d "{\"user\": \"stress_test\", \"domain\": \"test\", \"limit\": 10}"
done

# 3. Check for errors
curl http://localhost:8000/api/capa/?severity=critical

# 4. Verify metrics
curl http://localhost:8000/api/logic-hub/stats
curl http://localhost:8000/api/memory-fusion/stats

# 5. Check health
curl http://localhost:8000/health
```

**Success Criteria:**
- ✅ All updates processed
- ✅ No critical CAPAs created
- ✅ Health status = healthy
- ✅ Success rate > 95%

---

## Maintenance Tasks

### Daily
- [ ] Check health endpoint
- [ ] Review critical CAPAs
- [ ] Monitor logic hub success rate

### Weekly
- [ ] Review observation window outcomes
- [ ] Check rollback rate (<5%)
- [ ] Review immutable log integrity
- [ ] Run stress test

### Monthly
- [ ] Database backup
- [ ] Review compliance metrics
- [ ] Audit CAPA closures
- [ ] Governance policy review

---

## Emergency Procedures

### Complete System Failure

1. **Stop Grace**
   ```powershell
   .\GRACE.ps1 -Stop
   ```

2. **Backup Database**
   ```powershell
   Copy-Item databases\grace.db databases\grace.db.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')
   ```

3. **Check Logs**
   ```powershell
   Get-Content logs\*.log | Select-Object -Last 100
   ```

4. **Restore from Backup** (if needed)
   ```powershell
   Copy-Item databases\grace.db.backup_YYYYMMDD_HHMMSS databases\grace.db -Force
   ```

5. **Restart**
   ```powershell
   .\GRACE.ps1
   ```

### Data Corruption Detected

1. **Verify Immutable Log Integrity**
   ```bash
   curl http://localhost:8000/api/immutable-log/verify-integrity
   ```

2. **If Corrupted:**
   - Stop Grace
   - Restore from last known good backup
   - Run migrations
   - Restart

3. **Create Critical CAPA**
   ```bash
   curl -X POST http://localhost:8000/api/capa/create \
     -d '{"title": "Data corruption detected", "severity": "critical", ...}'
   ```

---

## Success Criteria

### Boot Success
✅ All subsystems show "[OK]"  
✅ Backend responds within 30 seconds  
✅ Health check returns "healthy"  
✅ All 6 smoke tests pass  

### Operational Health
✅ Logic hub success rate > 95%  
✅ CAPA open count < 10  
✅ Rollback rate < 5%  
✅ No critical anomalies  

### Compliance
✅ Immutable log integrity verified  
✅ All updates have crypto signatures  
✅ Governance policies active  
✅ Audit trail complete  

---

## Contact & Escalation

### Auto-Escalation Triggers
- Playbook fails twice (same playbook)
- Critical anomaly repeats
- Rollback rate > 10%
- CAPA open > 30 days

### Manual Escalation
```bash
# Create high-priority CAPA
curl -X POST http://localhost:8000/api/capa/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Manual escalation needed",
    "description": "Issue description",
    "capa_type": "corrective",
    "severity": "high",
    "source": "manual",
    "detected_by": "operator_name"
  }'
```

---

## Summary

**This runbook provides:**
- ✅ Step-by-step boot procedure
- ✅ Smoke test checklist
- ✅ Troubleshooting guide
- ✅ Rollback procedures
- ✅ Emergency protocols
- ✅ Monitoring commands
- ✅ Maintenance schedule

**Follow this for safe, repeatable Grace operations.**
