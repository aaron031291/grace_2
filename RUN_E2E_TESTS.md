# Running End-to-End Production Scenarios

Complete guide to validating Grace under production-like conditions.

---

## 🎯 Quick Start

### 1. Health Check First
```bash
# Validate system is ready
python scripts/validate_system_health.py
```

### 2. Bootstrap (if needed)
```bash
# One-time setup for fresh environment
python scripts/bootstrap_verification.py
```

### 3. Run Production Scenario
```bash
# Basic run
python scripts/run_production_scenario.py

# With monitoring
python scripts/run_production_scenario.py --monitor

# Chaos mode (random failures)
python scripts/run_production_scenario.py --chaos

# Stress test (multiple iterations)
python scripts/run_production_scenario.py --iterations 5
```

### 4. Run via Pytest
```bash
# Normal mode
pytest tests/test_e2e_production_scenario.py::test_production_scenario_normal_mode -v

# Chaos mode
pytest tests/test_e2e_production_scenario.py::test_production_scenario_chaos_mode -v

# Stress test
pytest tests/test_e2e_production_scenario.py::test_production_scenario_stress -v

# All E2E tests
pytest tests/ -m e2e -v
```

---

## 📋 What Gets Tested

### Phase 1: Mission Setup ✅
- Creates synthetic mission with known ID
- Provides timeline anchor for all actions
- Validates mission tracking initialization

### Phase 2: Diverse Error Injection ⚡
- **Tier 1 (Auto-execute)**: database_locked, validation_error, timeout
- **Tier 2 (Approval required)**: permission_denied, resource_exhausted
- **Tier 3 (Governance)**: dependency_unavailable
- Tests high/medium/low confidence paths

### Phase 3: Approval Workflows ✋
- Approves 2/3 of requests
- Rejects 1/3 to test graceful fallback
- Validates auto-execution on approval
- Confirms stored contracts are used (no rebuild)

### Phase 4: Forced Rollback 🔄
- Sabotages verification metrics
- Forces contract violation
- Validates snapshot restore
- Checks mission rollback counters
- Verifies immutable log captures rollback

### Phase 5: Concurrent Load 🔥
- 50+ concurrent background requests
- Simulates: chat calls, task submissions, metric queries
- Stresses DB, Trigger Mesh, event listeners
- Measures latency and throughput

### Phase 6: Monitor Telemetry 📊
- Tracks action rates
- Monitors rollback frequency
- Measures confidence trends
- Asserts latency < 500ms avg, < 2000ms max
- Asserts error rate < 10% (normal mode)

### Phase 7: Validate Persistence 🔍
- **Events**: All agentic.action_* events persisted
- **Contracts**: Created and linked to actions
- **Benchmarks**: Run for tier 2+ actions
- **Snapshots**: Created for tier 2+ actions
- **Missions**: Progress updated correctly
- **Approvals**: Requests and decisions logged
- **Immutable Log**: Full audit trail
- **Orphan Check**: No orphaned foreign key rows

### Phase 8: Final Report 📈
- Aggregated metrics
- Success/failure counts
- Latency percentiles
- Throughput calculations
- Saved to JSON for regression tracking

---

## 🎨 Test Scenarios

### Normal Mode (Default)
```bash
python scripts/run_production_scenario.py
```
- No random failures
- Expected behavior under normal conditions
- Error rate should be < 10%
- All data should persist correctly

### Chaos Mode 🌪️
```bash
python scripts/run_production_scenario.py --chaos
```
- 10% random failure injection
- Tests retry logic
- Validates circuit breakers
- Confirms rollback behavior
- Error rate may exceed 10% (expected)

### Stress Mode 💪
```bash
python scripts/run_production_scenario.py --iterations 10 --monitor
```
- Runs scenario 10 times back-to-back
- Checks for resource leaks
- Validates DB doesn't lock up
- Monitors memory/CPU trends

### Monitored Mode 📺
```bash
python scripts/run_production_scenario.py --monitor
```
- Real-time stats printed every 2 seconds
- Shows: event count, contract count, latest status
- Useful for debugging slow phases

---

## 📊 Metrics Collected

### Action Metrics
- `actions_triggered`: Total errors injected
- `actions_completed`: Successfully completed
- `actions_failed`: Failed executions

### Approval Metrics
- `approvals_requested`: Total approval requests
- `approvals_granted`: Approved actions
- `approvals_rejected`: Rejected actions

### Verification Metrics
- `contracts_created`: Action contracts
- `benchmarks_run`: Benchmark executions
- `snapshots_created`: Safe-hold snapshots
- `rollbacks`: Rollback operations

### Performance Metrics
- `avg_latency_ms`: Average response time
- `max_latency_ms`: Worst-case latency
- `events_persisted`: Database writes

### Data Integrity
- `orphaned_events`: Foreign key violations (should be 0)
- `log_entries`: Immutable log audit trail

---

## 🔍 Interpreting Results

### ✅ Success Criteria

**All must be true:**
- [x] All phases complete without exceptions
- [x] `actions_triggered > 0`
- [x] `events_persisted > 0`
- [x] `contracts_created > 0`
- [x] Average latency < 500ms
- [x] Max latency < 2000ms
- [x] Error rate < 10% (normal mode)
- [x] No orphaned database rows
- [x] Mission progress updates correctly

### ⚠️ Warning Signs

**Investigate if you see:**
- Latency > 500ms average
- Error rate > 10% in normal mode
- Orphaned database records
- Missing events or contracts
- Rollbacks when not expected
- Memory leaks across iterations

### ❌ Failure Conditions

**Test fails if:**
- Database connection lost
- Trigger Mesh unresponsive
- Immutable log fails
- Referential integrity violated
- Latency exceeds 2000ms
- Approval workflow broken

---

## 📁 Output Files

### Metrics JSON
**File**: `e2e_metrics_<mission_id>.json`

Contains:
- All metrics collected
- Validation results
- Mission ID
- Chaos mode flag
- Timestamp

### Scenario Report
**File**: `scenario_report_<timestamp>.json`

Contains:
- Summary (success rate, totals)
- Per-iteration details
- Configuration used
- Aggregated metrics

### Example Output
```json
{
  "metrics": {
    "actions_triggered": 6,
    "actions_completed": 5,
    "actions_failed": 1,
    "avg_latency_ms": 142.5,
    "max_latency_ms": 487.3,
    "rollbacks": 1,
    "contracts_created": 6,
    "events_persisted": 18
  },
  "validation": {
    "events": 18,
    "contracts": 6,
    "benchmarks": 4,
    "snapshots": 2,
    "orphaned_events": 0
  }
}
```

---

## 🔧 Troubleshooting

### "Database is locked"
```bash
# Check WAL mode
sqlite3 grace.db "PRAGMA journal_mode"

# Should return: wal
# If not, run bootstrap again
python scripts/bootstrap_verification.py
```

### "Trigger Mesh not responding"
```bash
# Ensure backend is running
cd backend
uvicorn main:app --reload

# Or check if services started
# Look for: "✓ Trigger Mesh started"
```

### "High latency warnings"
```bash
# Check concurrent load in system
# Reduce iterations or disable monitoring

python scripts/run_production_scenario.py --iterations 1
```

### "Missing tables"
```bash
# Run full bootstrap
python scripts/bootstrap_verification.py

# Or create tables manually
python -c "from backend.base_models import Base, engine; import asyncio; asyncio.run(engine.begin()).__aenter__().run_sync(Base.metadata.create_all)"
```

---

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
name: E2E Production Tests

on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      
      - name: Bootstrap system
        run: python scripts/bootstrap_verification.py
      
      - name: Health check
        run: python scripts/validate_system_health.py
      
      - name: Run E2E tests
        run: python scripts/run_production_scenario.py --iterations 3
      
      - name: Upload metrics
        uses: actions/upload-artifact@v3
        with:
          name: e2e-metrics
          path: |
            e2e_metrics_*.json
            scenario_report_*.json
```

### Nightly Regression
```bash
#!/bin/bash
# nightly_e2e.sh

# Clean slate
rm -f grace.db
python scripts/bootstrap_verification.py

# Run comprehensive test
python scripts/run_production_scenario.py --iterations 10 > e2e_$(date +%Y%m%d).log

# Archive results
mkdir -p test_archive/$(date +%Y%m%d)
mv e2e_*.json scenario_*.json e2e_$(date +%Y%m%d).log test_archive/$(date +%Y%m%d)/

# Alert on failure
if [ $? -ne 0 ]; then
  echo "E2E test failed!" | mail -s "GRACE E2E Failure" ops@example.com
fi
```

---

## 📚 Next Steps

After successful E2E tests:

1. **Deploy to Staging**
   ```bash
   # Copy .env to staging
   # Run bootstrap on staging
   # Run E2E tests on staging
   ```

2. **Load Testing**
   ```bash
   # Use Locust or similar
   # Target: /api/verification endpoints
   # Measure: throughput, error rate
   ```

3. **Connect Dashboards**
   ```bash
   # Enable Prometheus
   echo "PROMETHEUS_ENABLED=true" >> .env
   
   # Point Grafana to metrics
   # Import Grace dashboard
   ```

4. **Production Deployment**
   - Run E2E tests on prod-like environment
   - Monitor first 24 hours closely
   - Set up alerts on key metrics

---

**Ready to validate production readiness? Start here:**
```bash
python scripts/validate_system_health.py && \
python scripts/run_production_scenario.py --monitor
```
