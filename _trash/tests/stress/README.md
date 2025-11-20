# Stress Test Suite

## Multi-Layer Stress Testing for Grace

### Test Components

#### 1. Layer 1 Boot Stress (`layer1_boot_runner.py`)
Tests kernel boot, failures, and recovery

```bash
python -m tests.stress.layer1_boot_runner --cycles 5
```

**Tests:**
- Repeated boot cycles
- Process kill recovery
- Config corruption handling
- Watchdog reactions
- Self-healing responses

**Logs:** `logs/stress/boot/<timestamp>.jsonl`

#### 2. Ingestion Chunking Stress (`ingestion_chunking.py`)
Tests pipeline performance under load

```bash
python -m tests.stress.ingestion_chunking --docs 10
```

**Tests:**
- Varying document sizes
- Stage latencies (extract, chunk)
- Quality score consistency
- Drift detection

**Logs:** `logs/stress/ingestion/<test_id>.json`

#### 3. HTM Trigger Stress (`htm_trigger_stress.py`)
Tests orchestration under load

```bash
python -m tests.stress.htm_trigger_stress --tasks 100
```

**Tests:**
- Random task bursts
- SLA enforcement
- Preemption
- Workload perception
- Trigger deduplication

**Logs:** `logs/stress/htm/<timestamp>.jsonl`

---

## Automated Execution

### Run All Stress Tests
```bash
python tests/stress/run_all_stress_tests.py
```

### Scheduled Runs
Configured to run:
- Hourly during low load
- On-demand when Hunter detects anomalies
- Before deployments

### Integration
- Results feed HTM for task creation
- Failures trigger watchdog escalation
- Metrics stream to telemetry hub
- Anomalies alert Hunter

---

## Logs & Diagnostics

All tests produce:
- Structured JSONL logs
- Summary JSON files
- Metrics for telemetry hub
- Events on message bus

**Log Schema:**
```json
{
  "test_id": "boot_stress_20251114_120000",
  "timestamp": "2025-11-14T12:00:00Z",
  "event_type": "stress.run.started",
  "message": "Boot stress test started",
  "cycles": 5
}
```

---

**All stress tests validate Grace's resilience under real-world conditions!**
