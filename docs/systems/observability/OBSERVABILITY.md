# Grace Observability System

Complete observability stack with structured logging, correlation IDs, and timeline tracking.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  OBSERVABILITY STACK                                         │
├──────────────────────────────────────────────────────────────┤
│  1. Structured Logging   → JSON logs with correlation IDs   │
│  2. Timeline API         → Track autonomous runs & steps     │
│  3. Correlation System   → Link logs to runs/playbooks      │
│  4. Metrics Integration  → Tie logs to performance data      │
│  5. Immutable Audit Log  → Tamper-proof action history      │
└──────────────────────────────────────────────────────────────┘
```

## 1. Structured Logging

### Enable Structured Logging

Add to `.env`:
```
STRUCTURED_LOGGING=true
```

### Log Format

All logs output as JSON:

```json
{
  "timestamp": "2025-11-09T18:30:00.123456Z",
  "level": "INFO",
  "logger": "backend.boot_pipeline",
  "subsystem": "boot_pipeline",
  "event_type": "stage_complete",
  "message": "Stage completed: Preflight Gate",
  "run_id": "boot_20251109_183000",
  "playbook_id": "pb_fix_unicode",
  "request_id": "req_abc123",
  "details": {...}
}
```

### Tail Logs with jq

#### All logs with nice formatting:
```powershell
.\scripts\tail_logs.ps1
```

#### Filter by subsystem:
```powershell
.\scripts\tail_logs.ps1 -Subsystem "agentic_spine"
.\scripts\tail_logs.ps1 -Subsystem "playbook_executor"
.\scripts\tail_logs.ps1 -Subsystem "boot_pipeline"
```

#### Filter by run ID:
```powershell
.\scripts\tail_logs.ps1 -RunId "run_abc123"
```

#### Errors only:
```powershell
.\scripts\tail_logs.ps1 -Errors
```

#### Combine filters:
```powershell
.\scripts\tail_logs.ps1 -Subsystem "playbook_executor" -RunId "run_abc123"
```

### Manual jq Queries

```powershell
# Get all playbook executions
Get-Content logs\backend.log | jq 'select(.event_type=="playbook_execution")'

# Get failures
Get-Content logs\backend.log | jq 'select(.level=="ERROR" or .level=="CRITICAL")'

# Get specific run
Get-Content logs\backend.log | jq 'select(.run_id=="run_abc123")'

# Pretty print last 10
Get-Content logs\backend.log -Tail 10 | jq .
```

---

## 2. Timeline API

Track autonomous agent runs with detailed step-by-step timelines.

### Get Active Runs

```powershell
Invoke-RestMethod http://localhost:8000/api/agent/runs/active
```

Response:
```json
[
  {
    "run_id": "run_startup_001",
    "started_at": "2025-11-09T18:30:00Z",
    "status": "active",
    "trigger": "scheduled",
    "subsystem": "boot_pipeline",
    "playbooks_executed": 3,
    "verifications_passed": 3,
    "verifications_failed": 0
  }
]
```

### Get Run Timeline

```powershell
Invoke-RestMethod http://localhost:8000/api/agent/runs/run_startup_001/timeline
```

Response shows:
- Run metadata
- All steps with timestamps
- Step types: kernel_selection, plan_creation, playbook_execution, verification
- Duration in milliseconds
- Correlated log entry count

### Check Correlations

```powershell
.\scripts\check_correlations.ps1 -RunId "run_startup_001"
```

Shows:
1. Timeline from API
2. Log entries matching run_id
3. All timeline steps with status

---

## 3. Correlation IDs

Every log entry can have up to 4 correlation IDs:

| ID | Purpose | Example |
|----|---------|---------|
| `run_id` | Autonomous agent run | run_20251109_183000 |
| `playbook_id` | Playbook execution | pb_fix_unicode_001 |
| `verification_id` | Verification check | verify_schema_001 |
| `request_id` | HTTP request | req_abc123def456 |

### Set Correlation Context in Code

```python
from backend.structured_logger import (
    set_run_context,
    set_playbook_context,
    set_verification_context,
    clear_context
)

# Set run context
set_run_context("run_abc123")

# All logs now include run_id
logger.info("Starting playbook execution")

# Add playbook context
set_playbook_context("pb_fix_unicode")

# Now logs have both run_id and playbook_id
logger.info("Executing step 1")

# Clear when done
clear_context()
```

### Query by Correlation

```powershell
# All logs for a specific run
jq 'select(.run_id=="run_abc123")' logs\backend.log

# All logs for a playbook
jq 'select(.playbook_id=="pb_fix_unicode")' logs\backend.log

# All logs for a request
jq 'select(.request_id=="req_abc123")' logs\backend.log
```

---

## 4. Metrics Integration

### Tie Logs to Metrics

Check metrics snapshots alongside logs:

```powershell
# Latest metrics
sqlite3 databases\metrics.db "SELECT metric_id, latest_band FROM metrics_snapshots ORDER BY window_end DESC LIMIT 10"

# Metrics during a specific run
sqlite3 databases\metrics.db "SELECT * FROM metrics_snapshots WHERE timestamp >= '2025-11-09 18:30:00' AND timestamp <= '2025-11-09 18:35:00'"
```

### Startup Metrics

Boot pipeline publishes:

- `startup.preflight_status` → pass/fail
- `startup.validation_errors` → count
- `startup.schema_mismatches` → count
- `startup.boot_pipeline_stage` → 1-7
- `startup.tests_passed` → count
- `startup.console_encoding` → utf-8/cp1252

---

## 5. Immutable Audit Log

Tamper-proof record of all actions:

```powershell
# Last 10 actions
sqlite3 backend\grace.db "SELECT sequence, actor, action, subsystem FROM immutable_log ORDER BY sequence DESC LIMIT 10"

# Actions by subsystem
sqlite3 backend\grace.db "SELECT action, COUNT(*) FROM immutable_log WHERE subsystem='boot_pipeline' GROUP BY action"

# Actions during boot
sqlite3 backend\grace.db "SELECT * FROM immutable_log WHERE timestamp >= '2025-11-09 18:30:00' ORDER BY sequence"
```

---

## Complete Observability Workflow

### 1. Start Grace with Structured Logging

```powershell
# In .env
STRUCTURED_LOGGING=true

# Start Grace
.\GRACE.ps1
```

### 2. Tail Logs in Real-Time

```powershell
# New PowerShell window
.\scripts\tail_logs.ps1 -Subsystem "boot_pipeline"
```

### 3. Check Active Runs

```powershell
Invoke-RestMethod http://localhost:8000/api/agent/runs/active
```

### 4. Get Run Timeline

```powershell
$runId = "run_abc123"
Invoke-RestMethod http://localhost:8000/api/agent/runs/$runId/timeline
```

### 5. Check Correlations

```powershell
.\scripts\check_correlations.ps1 -RunId $runId
```

### 6. Query Specific Events

```powershell
# Get all playbook executions
Get-Content logs\backend.log | jq 'select(.event_type=="playbook_execution")'

# Get all for this run
Get-Content logs\backend.log | jq "select(.run_id==\"$runId\")"
```

### 7. Check Metrics Impact

```powershell
# Check if metrics improved after fixes
sqlite3 databases\metrics.db "SELECT metric_id, latest_band FROM metrics_snapshots WHERE timestamp >= '2025-11-09 18:30:00' ORDER BY window_end DESC"
```

### 8. Verify Immutable Log

```powershell
# Audit trail for the run
sqlite3 backend\grace.db "SELECT sequence, actor, action, result FROM immutable_log WHERE payload LIKE '%run_abc123%' ORDER BY sequence"
```

---

## Troubleshooting

### Logs Not JSON Formatted

**Check**:
```powershell
Get-Content logs\backend.log -Tail 1
```

If not JSON:
1. Check `.env` has `STRUCTURED_LOGGING=true`
2. Restart Grace
3. Verify environment variable: `$env:STRUCTURED_LOGGING`

### jq Command Not Found

**Install jq**:
1. Download from https://stedolan.github.io/jq/
2. Add to PATH
3. Or use Chocolatey: `choco install jq`

**Alternative**: Use built-in PowerShell:
```powershell
Get-Content logs\backend.log -Tail 20 | ForEach-Object { $_ | ConvertFrom-Json }
```

### No Correlation IDs in Logs

**Ensure context is set**:
```python
from backend.structured_logger import set_run_context

# At start of autonomous run
run_id = "run_abc123"
set_run_context(run_id)

# Now all logs include run_id
logger.info("Starting execution")
```

### Timeline API Returns 404

**Check**:
1. Grace is running: `Invoke-RestMethod http://localhost:8000/health`
2. Run ID exists: `Invoke-RestMethod http://localhost:8000/api/agent/runs/active`
3. Correct format: `run_abc123` not `abc123`

---

## Advanced Queries

### Find All Failed Playbooks

```powershell
Get-Content logs\backend.log | jq 'select(.event_type=="playbook_execution" and .details.status=="failed")'
```

### Get Timeline for All Runs Today

```powershell
$today = (Get-Date).ToString("yyyy-MM-dd")
Get-Content logs\backend.log | jq "select(.run_id and .timestamp | startswith(\"$today\"))"
```

### Find Long-Running Steps

```powershell
# Steps > 5 seconds
Get-Content logs\backend.log | jq 'select(.duration_ms > 5000)'
```

### Correlate Errors to Metrics

```powershell
# Get error timestamp
$errorTime = (Get-Content logs\backend.log | jq -r 'select(.level=="ERROR") | .timestamp' | Select-Object -First 1)

# Check metrics around that time
sqlite3 databases\metrics.db "SELECT * FROM metrics_snapshots WHERE timestamp BETWEEN datetime('$errorTime', '-5 minutes') AND datetime('$errorTime', '+5 minutes')"
```

---

## See Also

- [BOOT_PIPELINE.md](file:///c:/Users/aaron/grace_2/BOOT_PIPELINE.md) - Boot pipeline system
- [STARTUP_HEALING.md](file:///c:/Users/aaron/grace_2/STARTUP_HEALING.md) - Self-healing details
- Backend API docs: http://localhost:8000/docs
