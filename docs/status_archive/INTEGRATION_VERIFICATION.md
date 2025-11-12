# Integration Verification Guide

## 🎯 Complete System Integration - Verification Steps

This guide verifies that all pipeline components work together:
- Memory Tables
- Auto-Ingestion
- Schema Inference
- Unified Logic Hub
- Clarity Framework
- Ingestion Engine
- Learning Systems

---

## ✅ Pre-Flight Checks

### 1. Dependencies Installed

```bash
pip install sqlmodel>=0.0.14 sqlalchemy>=2.0.0 pyyaml>=6.0
```

### 2. Directories Created

```bash
mkdir -p databases logs training_data storage/uploads grace_training
```

### 3. Grace Started

```bash
python backend/unified_grace_orchestrator.py
```

**Expected logs:**
```
🗄️ Initializing Memory Tables system...
✅ Loaded 5 table schemas
✅ Database initialized
✅ Memory Tables system started
```

---

## 🧪 Test 1: Basic Pipeline

### Run Complete Pipeline Test

```bash
python test_complete_pipeline.py
```

**Expected output:**
```
✅ ALL TESTS PASSED

Complete pipeline verified:
  • Schema registry ✓
  • Content analysis ✓
  • Schema inference ✓
  • Table operations ✓
  • Learning integration ✓
  • Auto-ingestion ✓
```

---

## 🧪 Test 2: Clarity Integration

### Run Clarity Smoke Tests

```bash
python test_clarity_integration.py
```

**Expected output:**
```
✅ CLARITY INTEGRATION TESTS PASSED

Verified:
  • Clarity manifest registration ✓
  • Event publishing ✓
  • Trust score updates ✓
  • Logic Hub integration ✓
  • Learning reports ✓
  • Cross-domain queries ✓
```

**Note:** Some warnings are OK if optional components (Clarity, Logic Hub) aren't running.

---

## 🧪 Test 3: Auto-Ingestion Flow

### Start Auto-Ingestion

```bash
curl -X POST http://localhost:8001/api/auto-ingest/start \
  -H "Content-Type: application/json" \
  -d '{"folders": ["training_data"], "auto_approve_low_risk": true}'
```

**Expected response:**
```json
{
  "success": true,
  "message": "Auto-ingestion started",
  "stats": {
    "running": true,
    "watch_folders": ["training_data"]
  }
}
```

### Upload Test File

```bash
echo "# Test Document

This tests Grace's complete learning pipeline.

Topics: testing, automation, intelligence" > training_data/pipeline_test.md
```

### Verify Processing (wait 10 seconds)

```bash
sleep 10

# Check ingestion status
curl http://localhost:8001/api/auto-ingest/status
```

**Expected:**
```json
{
  "stats": {
    "running": true,
    "processed_files_count": 1  // Should increase
  }
}
```

### Query Table

```bash
curl "http://localhost:8001/api/memory/tables/memory_documents/rows?limit=5"
```

**Expected:** Row with `file_path: "training_data/pipeline_test.md"`

---

## 🧪 Test 4: Ingestion Bridge

### Create Ingestion Job

```bash
curl -X POST http://localhost:8001/api/ingestion-bridge/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "README.md",
    "table_name": "memory_documents",
    "job_type": "manual"
  }'
```

**Expected response:**
```json
{
  "success": true,
  "job": {
    "job_id": "ingest_20250112_...",
    "file_path": "README.md",
    "status": "pending",
    "stages": {
      "extraction": "pending",
      "validation": "pending",
      "population": "pending",
      "sync": "pending"
    }
  }
}
```

### Check Job Status (wait 5 seconds)

```bash
sleep 5

curl http://localhost:8001/api/ingestion-bridge/jobs/ingest_20250112_...
```

**Expected:**
```json
{
  "job": {
    "status": "complete",
    "stages": {
      "extraction": "complete",
      "validation": "complete",
      "population": "complete",
      "sync": "complete"
    },
    "row_id": "..."
  }
}
```

### Check Ingestion Stats

```bash
curl http://localhost:8001/api/ingestion-bridge/stats
```

---

## 🧪 Test 5: Learning Integration

### Get Learning Report

```bash
curl http://localhost:8001/api/memory/tables/learning-report
```

**Expected:**
```json
{
  "report": {
    "tables": {
      "memory_documents": {
        "total_rows": 2,
        "synced_rows": 2,
        "avg_trust_score": 0.6,
        "sync_percentage": 100
      }
    },
    "summary": {
      "total_tables": 5,
      "total_rows": 2,
      "overall_avg_trust": 0.6
    }
  }
}
```

### Cross-Domain Query

```bash
curl -X POST http://localhost:8001/api/memory/tables/cross-domain-query \
  -H "Content-Type: application/json" \
  -d '{
    "documents": {},
    "codebases": {},
    "datasets": {}
  }'
```

**Expected:**
```json
{
  "success": true,
  "results": {
    "documents": [/* rows */],
    "codebases": [],
    "datasets": []
  },
  "total_rows": 2
}
```

### Update Trust Scores

```bash
curl -X POST http://localhost:8001/api/memory/tables/update-trust-scores/memory_documents
```

**Expected:**
```json
{
  "success": true,
  "table": "memory_documents",
  "updated_count": 2
}
```

---

## 🧪 Test 6: Approval Workflow

### Create File Requiring Approval

```bash
# Create a file that will trigger medium-risk approval
echo "Contract Agreement 2025" > training_data/new_schema_type.contract
```

### Check Pending Approvals (wait 10 seconds)

```bash
sleep 10

curl http://localhost:8001/api/auto-ingest/pending
```

**Expected:** If Grace proposes a new table schema:
```json
{
  "pending_approvals": {
    "upd_abc123": {
      "file_path": "training_data/new_schema_type.contract",
      "proposal": {
        "action": "create_new",
        "table_name": "memory_contracts",
        "confidence": 0.75
      }
    }
  }
}
```

### Approve or Reject

```bash
# Approve
curl -X POST http://localhost:8001/api/auto-ingest/approve \
  -H "Content-Type: application/json" \
  -d '{
    "approval_id": "upd_abc123",
    "approved": true
  }'

# Or reject
curl -X POST http://localhost:8001/api/auto-ingest/approve \
  -d '{
    "approval_id": "upd_abc123",
    "approved": false,
    "reason": "Not needed"
  }'
```

---

## 📊 Monitoring Endpoints

### System Health

```bash
# Overall health
curl http://localhost:8001/health

# Grace status
curl http://localhost:8001/api/status

# Memory tables stats
curl http://localhost:8001/api/memory/tables/stats
```

### Auto-Ingestion

```bash
# Status
curl http://localhost:8001/api/auto-ingest/status

# Pending approvals
curl http://localhost:8001/api/auto-ingest/pending

# Failed ingestions
curl http://localhost:8001/api/auto-ingest/insights/failed
```

### Ingestion Bridge

```bash
# All jobs
curl http://localhost:8001/api/ingestion-bridge/jobs

# Specific job
curl http://localhost:8001/api/ingestion-bridge/jobs/{job_id}

# Stats
curl http://localhost:8001/api/ingestion-bridge/stats
```

---

## ✅ Success Criteria

### All Tests Pass

- [x] Complete pipeline test passes
- [x] Clarity integration test passes (or warnings only)
- [x] Auto-ingestion detects and processes files
- [x] Ingestion bridge creates and executes jobs
- [x] Learning reports generate successfully
- [x] Cross-domain queries work
- [x] Trust scores update
- [x] Approval workflows function

### Logs Show Expected Messages

```bash
tail -f logs/orchestrator.log

# Should see:
# ✅ Memory Tables system started
# 🔍 Auto-ingestion started
# 📄 Processing new file: ...
# ✅ Successfully ingested: ...
# ✅ Synced to learning pipeline
```

### Tables Populated

```bash
# Check database
sqlite3 databases/memory_tables.db

sqlite> SELECT COUNT(*) FROM memory_documents;
-- Should return > 0

sqlite> SELECT file_path, title FROM memory_documents LIMIT 5;
-- Should show uploaded files
```

---

## 🚨 Troubleshooting

### Issue: Auto-ingestion not detecting files

**Fix:**
```bash
# Restart auto-ingestion
curl -X POST http://localhost:8001/api/auto-ingest/stop
curl -X POST http://localhost:8001/api/auto-ingest/start
```

### Issue: Files not inserting

**Check:**
```bash
# Pending approvals
curl http://localhost:8001/api/auto-ingest/pending

# Failed ingestions
curl http://localhost:8001/api/auto-ingest/insights/failed
```

### Issue: Trust scores not updating

**Fix:**
```bash
# Manually trigger update
curl -X POST http://localhost:8001/api/memory/tables/update-trust-scores/memory_documents
```

### Issue: Ingestion jobs stuck

**Check:**
```bash
# Job status
curl http://localhost:8001/api/ingestion-bridge/jobs

# Look for jobs with status "running" for too long
```

---

## 🎉 Verification Complete

If all tests pass, you have verified:

✅ **Upload → Learn pipeline fully operational**
- Files upload and are detected
- Content is analyzed and structured
- Schemas are inferred automatically
- Approvals work (auto and manual)
- Tables are populated correctly
- Learning systems integrate
- Trust scores compute
- Cross-domain queries function

✅ **Integration complete**
- Memory Tables ↔ Clarity Framework
- Memory Tables ↔ Unified Logic Hub
- Memory Tables ↔ Ingestion Engine
- Memory Tables ↔ Learning Systems

✅ **Production ready**
- All components working
- APIs functional
- Monitoring in place
- Error handling robust

**Grace can now learn autonomously from real-world data!** 🚀
