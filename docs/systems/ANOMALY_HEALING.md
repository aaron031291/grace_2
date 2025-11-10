# Anomaly-Driven Self-Healing System

**Complete post-boot workflow: Stress Test → Baseline → Watchdog → Self-Heal → Verify → Escalate**

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  ANOMALY-DRIVEN HEALING LOOP                                     │
├──────────────────────────────────────────────────────────────────┤
│  1. Boot Pipeline Complete → "Baseline Healthy"                  │
│          ↓                                                        │
│  2. Stress Test Suite → Find issues before users                 │
│          ↓                                                        │
│  3. Establish Baseline → Define "healthy" metrics                │
│          ↓                                                        │
│  4. Start Watchdog → Continuous monitoring                       │
│          ↓                                                        │
│  5. Detect Anomaly → Drift from baseline                         │
│          ↓                                                        │
│  6. Take Snapshot → Before healing (rollback capability)         │
│          ↓                                                        │
│  7. Execute Playbook → Auto-fix the issue                        │
│          ↓                                                        │
│  8. Re-run Test → "Trust but verify"                             │
│          ↓                                                        │
│  9. Verified? → YES: Log success  /  NO: Try again               │
│          ↓                                                        │
│  10. Max Attempts? → Escalate to AMP API                         │
│          ↓                                                        │
│  11. Immutable Log → Full forensic trail                         │
└──────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Stress Test Suite (`backend/stress_test_suite.py`)

**Purpose**: Find issues before users encounter them

**8 Tests**:
1. **Health Endpoint Load** - 50 concurrent requests
2. **Database Connection Pool** - 20 parallel DB queries
3. **Concurrent API Requests** - 40 requests across 4 endpoints
4. **Multimodal Chat Stress** - 5 concurrent chat requests
5. **Metrics Collection Load** - Metrics endpoint under pressure
6. **Governance Latency** - Decision-making speed
7. **Self-Heal Trigger** - Event mesh response time
8. **Memory Leak Detection** - 100 requests, check growth

**Outputs**:
- Test results with pass/fail
- Performance metrics (latency, throughput)
- Anomalies detected
- Fresh telemetry for baseline

---

### 2. Anomaly Watchdog (`backend/anomaly_watchdog.py`)

**Purpose**: Runtime guardian monitoring for drift from baseline

**Monitors**:
- **Error Rate**: Immutable log errors in last 5 min
- **Latency**: API response times (p95)
- **Memory Growth**: Process memory over time
- **Failure Rate**: Playbook execution failures

**Thresholds**:
```python
{
    "error_rate": 0.05,        # 5% triggers alert
    "latency_p95": 2000,       # 2s max
    "memory_growth_mb": 100,   # 100MB/hour
    "failure_rate": 0.10       # 10% playbook failures
}
```

**Actions**:
- Detects anomaly
- Triggers healing workflow
- Tracks healing attempts
- Escalates after 3 failed attempts

---

### 3. Post-Boot Orchestrator (`backend/post_boot_orchestrator.py`)

**Purpose**: Coordinates complete healing workflow

**Workflow**:

#### Stage 1: Stress Test
```
Run full test suite → Generate fresh telemetry
```

#### Stage 2: Establish Baseline
```
Calculate metrics:
- Success rate: 95%
- Avg latency: 150ms
- Error count: 0

Save to storage/baseline.json
```

#### Stage 3: Start Watchdog
```
Begin continuous monitoring (every 60s)
Watch for drift from baseline
```

#### Stage 4: Immediate Healing
```
For each anomaly found in stress test:
  1. Take snapshot
  2. Select playbook
  3. Execute healing
  4. Re-run test
  5. Verify or escalate
  6. Log cycle
```

---

## Healing Workflow (Detailed)

### Example: High Error Rate Detected

#### 1. Anomaly Detection
```json
{
  "type": "error_rate_spike",
  "severity": "high",
  "current": 0.12,
  "threshold": 0.05,
  "details": "Error rate 12% exceeds threshold 5%"
}
```

#### 2. Snapshot Taken
```
storage/snapshots/pre_heal_error_rate_spike_20251109_190500/
  ├─ grace.db          (database backup)
  ├─ anomaly.json      (anomaly context)
  └─ metadata.json     (snapshot info)
```

#### 3. Playbook Selected
```
Anomaly: error_rate_spike
Playbook: investigate_error_spike
Risk: medium
Tier: tier_2
```

#### 4. Playbook Executed
```python
async def investigate_error_spike():
    # Step 1: Query recent errors from immutable_log
    errors = get_recent_errors(last_5_min)
    
    # Step 2: Group by error type
    error_groups = group_by_pattern(errors)
    
    # Step 3: Apply specific fix
    if "database_locked" in error_groups:
        await unlock_database()
    elif "rate_limit" in error_groups:
        await increase_rate_limits()
    
    # Step 4: Restart affected services
    await restart_services(["metrics_collector"])
    
    return {"success": True, "fixes_applied": 2}
```

#### 5. Re-run Stress Test
```
Re-execute "Concurrent API Requests" test
Result: PASS ✅
Error rate: 0.02 (below threshold)
```

#### 6. Verification
```json
{
  "passed": true,
  "verification_method": "stress_test_rerun",
  "error_rate_after": 0.02,
  "improvement": "10% → 2%"
}
```

#### 7. Immutable Log Entry
```json
{
  "sequence": 12345,
  "actor": "post_boot_orchestrator",
  "action": "complete_healing_cycle",
  "resource": "Concurrent API Requests",
  "subsystem": "orchestrator",
  "payload": {
    "workflow_id": "heal_concurrent_api_190500",
    "anomaly": {...},
    "playbook": "investigate_error_spike",
    "execution": {"success": true, "steps": 4},
    "verification": {"passed": true},
    "outcome": "success"
  },
  "result": "success",
  "timestamp": "2025-11-09T19:05:15Z"
}
```

---

## Escalation to AMP API

### When It Happens

After **3 failed healing attempts** for same anomaly:

```
Attempt 1: investigate_error_spike → Failed
Attempt 2: investigate_error_spike → Failed  
Attempt 3: investigate_error_spike → Failed
→ ESCALATE TO AMP API
```

### Escalation Process

#### 1. Query AMP API
```python
await amp_client.ask_for_guidance(
    issue="error_rate_spike",
    context={
        "severity": "high",
        "healing_attempts": 3,
        "playbook_used": "investigate_error_spike",
        "baseline": {...},
        "recent_errors": [...]
    }
)
```

#### 2. AMP Response
```json
{
  "suggested_action": "increase_db_pool_size",
  "confidence": 0.85,
  "reasoning": "Error pattern indicates database connection exhaustion",
  "recommended_config": {
    "pool_size": 20,
    "pool_timeout": 30
  }
}
```

#### 3. Apply AMP Suggestion
```
Execute AMP's suggested playbook
Re-test
Verify
Log outcome
```

#### 4. Record AMP Guidance
```
grace_training/amp_guidance/error_rate_spike_20251109_190600.json

{
  "anomaly": {...},
  "amp_response": {...},
  "outcome": "success",
  "learned": true
}
```

### Final Fallback: Human Alert

If AMP also fails:

```
logs/ALERT_error_rate_spike_20251109_190700.txt

================================================================================
CRITICAL ALERT - HUMAN INTERVENTION REQUIRED
================================================================================
Timestamp: 2025-11-09T19:07:00
Anomaly: error_rate_spike
Severity: high
Details: Error rate 12% exceeds threshold 5%
Healing Attempts: 3
AMP Escalation: Failed

Self-healing exhausted. Manual intervention required.
================================================================================
```

---

## Immutable Audit Trail

Every healing cycle creates forensic record:

```sql
-- Query healing history
SELECT sequence, actor, action, result, timestamp
FROM immutable_log  
WHERE action = 'complete_healing_cycle'
ORDER BY sequence DESC
LIMIT 10;
```

**Each entry contains**:
- Anomaly details
- Playbook executed
- Before/after snapshots
- Verification result
- Escalation status
- Full context

**Benefits**:
- ✅ Tamper-proof audit trail
- ✅ Root cause analysis
- ✅ Compliance/governance
- ✅ Training data for ML
- ✅ Debugging complex issues

---

## Integration with Main App

### Automatic Execution

When Grace starts, after all systems initialize:

```python
# At end of startup in main.py:

print("\n[POST-BOOT] Starting anomaly-driven healing workflow...")

from backend.post_boot_orchestrator import post_boot_orchestrator

# Run in background
asyncio.create_task(post_boot_orchestrator.run_post_boot_workflow())

print("[OK] Post-boot workflow scheduled")
```

### Manual Execution

```powershell
.\.venv\Scripts\python.exe scripts\run_post_boot_workflow.py
```

---

## Usage Examples

### Run Stress Test Only

```python
from backend.stress_test_suite import stress_tester

results = await stress_tester.run_full_suite()

print(f"Passed: {results['tests_passed']}/{results['tests_run']}")
print(f"Anomalies: {len(results['anomalies'])}")
```

### Check Watchdog Status

```python
from backend.anomaly_watchdog import anomaly_watchdog

# Check if baseline exists
if anomaly_watchdog.baseline:
    print(f"Baseline success rate: {anomaly_watchdog.baseline['metrics']['success_rate']:.1%}")
    print(f"Watchdog: {'ACTIVE' if anomaly_watchdog.running else 'STOPPED'}")
```

### View Healing Attempts

```python
print(anomaly_watchdog.healing_attempts)
# {'error_rate_spike': 2, 'memory_growth': 1}
```

### Query Immutable Log

```powershell
# View all healing cycles
sqlite3 backend\grace.db "SELECT * FROM immutable_log WHERE action='complete_healing_cycle' ORDER BY sequence DESC LIMIT 5"

# Count successful healings
sqlite3 backend\grace.db "SELECT COUNT(*) FROM immutable_log WHERE action='complete_healing_cycle' AND result='success'"
```

---

## Baseline Example

```json
{
  "timestamp": "2025-11-09T19:00:00Z",
  "metrics": {
    "success_rate": 1.0,
    "avg_latency_ms": 145,
    "error_count": 0
  },
  "thresholds": {
    "error_rate": 0.05,
    "latency_p95": 2000,
    "memory_growth_mb": 100,
    "failure_rate": 0.10
  },
  "test_results": {
    "tests_run": 8,
    "tests_passed": 8,
    "anomalies": []
  }
}
```

---

## Monitoring

### View Stress Test Results

```powershell
# After boot
Get-Content logs\backend.log | jq 'select(.subsystem=="stress_test")'
```

### Watch Watchdog Activity

```powershell
# Real-time watchdog monitoring
.\scripts\tail_logs.ps1 -Subsystem "watchdog"
```

### Check Healing Cycles

```powershell
# All healing attempts
Get-Content logs\backend.log | jq 'select(.event_type=="healing_cycle_complete")'
```

---

## Benefits

### Before Anomaly-Driven Healing:
- ❌ Issues discovered by users
- ❌ Reactive firefighting
- ❌ No proactive detection
- ❌ Manual investigation each time
- ❌ No learning between incidents

### After Anomaly-Driven Healing:
- ✅ Issues found in stress test
- ✅ Proactive auto-healing
- ✅ Continuous monitoring
- ✅ Automatic retry with verification
- ✅ AMP API escalation
- ✅ Human alerts as last resort
- ✅ Full audit trail
- ✅ Learns and improves

---

## Workflow Example

### Scenario: Memory Leak Detected

```
[19:00:00] Boot pipeline completes (7/7 stages)
[19:00:05] Stress test starts
[19:00:15] Memory leak test: +55MB growth [FAIL]
[19:00:15] Anomaly detected: memory_growth
[19:00:16] Baseline established (with anomaly noted)
[19:00:17] Watchdog started
[19:00:18] Immediate healing triggered

[HEALING WORKFLOW]
  [1/6] Taking snapshot... [OK]
  [2/6] Selecting playbook... [OK] restart_memory_heavy_services
  [3/6] Executing playbook... [OK]
  [4/6] Re-running memory leak test... [PASS]
  [5/6] Verification: [PASS] Memory growth: +5MB
  [6/6] Logging to immutable ledger... [OK]

  [SUCCESS] Anomaly resolved permanently

[19:00:25] Watchdog monitoring active (60s interval)
[19:01:25] Watchdog check: No anomalies
[19:02:25] Watchdog check: No anomalies
...
```

### Scenario: Persistent Failure → AMP Escalation

```
[19:00:00] Anomaly: error_rate_spike detected
[19:00:05] Healing attempt 1: investigate_error_spike [FAIL]
[19:01:05] Anomaly persists
[19:01:10] Healing attempt 2: investigate_error_spike [FAIL]
[19:02:10] Anomaly still present
[19:02:15] Healing attempt 3: investigate_error_spike [FAIL]
[19:02:20] Max attempts reached - ESCALATING TO AMP

[AMP ESCALATION]
  Query: "error_rate_spike" with full context
  Response: "Try increasing rate limits and worker count"
  Suggested Playbook: scale_up_resources
  
[19:02:25] Executing AMP suggestion...
[19:02:30] Re-test: [PASS] Error rate normalized
[19:02:31] AMP guidance recorded in grace_training/amp_guidance/
[19:02:32] Immutable log updated with AMP-assisted resolution

[SUCCESS] Issue resolved with AMP assistance
```

---

## Configuration

### Enable/Disable Features

Add to `.env`:

```bash
# Post-boot orchestration
RUN_POST_BOOT_STRESS_TEST=true
ESTABLISH_WATCHDOG_BASELINE=true
ENABLE_ANOMALY_WATCHDOG=true

# Watchdog thresholds
WATCHDOG_ERROR_RATE_THRESHOLD=0.05
WATCHDOG_LATENCY_P95_MS=2000
WATCHDOG_MEMORY_GROWTH_MB=100
WATCHDOG_FAILURE_RATE=0.10

# Healing configuration
MAX_HEALING_ATTEMPTS=3
ENABLE_AMP_ESCALATION=true

# AMP API (for escalation)
AMP_API_KEY=your_key_here
```

---

## Commands

### Run Post-Boot Workflow Manually

```powershell
.\.venv\Scripts\python.exe scripts\run_post_boot_workflow.py
```

### Run Stress Test Only

```powershell
.\.venv\Scripts\python.exe -c "import asyncio; from backend.stress_test_suite import stress_tester; asyncio.run(stress_tester.run_full_suite())"
```

### Check Baseline

```powershell
Get-Content storage\baseline.json | ConvertFrom-Json
```

### View Watchdog Status

```powershell
# Watchdog logs
Get-Content logs\backend.log | jq 'select(.subsystem=="watchdog")'
```

### View Healing History

```powershell
# All healing cycles
Get-Content logs\backend.log | jq 'select(.action=="complete_healing_cycle")'

# Successful healings
Get-Content logs\backend.log | jq 'select(.action=="complete_healing_cycle" and .result=="success")'

# Failed healings (escalated)
Get-Content logs\backend.log | jq 'select(.action=="complete_healing_cycle" and .result=="failed")'
```

### View AMP Escalations

```powershell
# AMP guidance records
dir grace_training\amp_guidance\

# View specific guidance
Get-Content grace_training\amp_guidance\error_rate_spike_20251109_190600.json
```

---

## Files Created

### Core System
- `backend/stress_test_suite.py` - 8 stress tests
- `backend/anomaly_watchdog.py` - Runtime monitoring
- `backend/post_boot_orchestrator.py` - Workflow coordination
- `scripts/run_post_boot_workflow.py` - Manual execution

### Storage
- `storage/baseline.json` - Healthy baseline metrics
- `storage/snapshots/pre_heal_*/` - Healing snapshots
- `storage/snapshots/workflow_*/` - Workflow snapshots

### Training Data
- `grace_training/amp_guidance/` - AMP API responses
- Immutable log entries for all healing cycles

### Alerts
- `logs/ALERT_*.txt` - Human intervention alerts

---

## Success Metrics

After system is running:

**Week 1**:
- Stress tests find 5 anomalies
- 4 auto-healed successfully
- 1 escalated to AMP
- Baseline established

**Week 2**:
- Stress tests find 2 anomalies (previous fixes working)
- 2 auto-healed
- 0 escalations
- Watchdog prevented 3 runtime issues

**Month 1**:
- Stress tests: 100% pass rate
- Watchdog: 15 anomalies detected & fixed
- AMP escalations: 0
- Human alerts: 0
- System stability: Excellent

---

## See Also

- [BOOT_PIPELINE.md](file:///c:/Users/aaron/grace_2/BOOT_PIPELINE.md) - Pre-boot validation
- [BOOT_LEARNING.md](file:///c:/Users/aaron/grace_2/BOOT_LEARNING.md) - Pattern learning
- [OBSERVABILITY.md](file:///c:/Users/aaron/grace_2/OBSERVABILITY.md) - Logging & monitoring
- [COMPLETE_SYSTEM.md](file:///c:/Users/aaron/grace_2/COMPLETE_SYSTEM.md) - Full system overview
