# 🧪 Grace Stress Test Guide

## Purpose

Validate the complete **real telemetry → playbook → execution** chain under realistic failure scenarios.

Now that Grace has:
- ✅ Real metrics collection (CPU/memory/disk/DB)
- ✅ Real playbook execution (scale/restart/throttle)
- ✅ Real proactive intelligence (metric-driven decisions)

We stress test to ensure autonomy works under load.

---

## 📋 The 6 Stress Test Scenarios

### 1. Metric Flood + Planner Overload
**Citation:** [docs/METRICS_CATALOG.md:55-95](file:///c:/Users/aaron/grace_2/docs/METRICS_CATALOG.md#L55-L95)

**What:** Drive API latency, request rate, and queue depth into critical simultaneously

**Validates:**
- trigger.mesh_queue_depth rises
- telemetry.publish_latency increases
- Grace sequences multiple playbooks
- Governance doesn't bottleneck

**Expected Playbooks:** scale-api-shard, spawn-workers, shed-load

---

### 2. Collector Blackout Drill
**Citation:** [docs/METRICS_CATALOG.md:45-95](file:///c:/Users/aaron/grace_2/docs/METRICS_CATALOG.md#L45-L95)

**What:** Kill GitHub collector mid-run

**Validates:**
- learning.collector_health goes critical
- Grace throttles learning orchestrator
- Governance alerts raised
- Config change proposals logged

**Expected Playbooks:** restart-collector, fail-ingestion-cycle

---

### 3. Trigger Mesh Backpressure
**Citation:** [docs/METRICS_CATALOG.md:82-90](file:///c:/Users/aaron/grace_2/docs/METRICS_CATALOG.md#L82-L90)

**What:** Flood mesh with 100+ events

**Validates:**
- trigger.mesh_queue_depth spikes
- Grace prioritizes critical handlers
- Non-critical events shed
- Handler errors tracked

**Expected Playbooks:** scale-router, shed-non-critical-events

---

### 4. Learning Misinformation Injection
**Citation:** [docs/METRICS_CATALOG.md:45-76](file:///c:/Users/aaron/grace_2/docs/METRICS_CATALOG.md#L45-L76)

**What:** Feed duplicate/stale sources

**Validates:**
- learning.source_freshness_ratio drops
- Sources quarantined
- Trust scores updated
- Policies tightened

**Expected Playbooks:** run-trust-analysis, stop-ingestion-cycle

---

### 5. Trust-Core Bias Spike
**Citation:** [docs/METRICS_CATALOG.md:60-76](file:///c:/Users/aaron/grace_2/docs/METRICS_CATALOG.md#L60-L76)

**What:** Ethics sentinel detects rising bias

**Validates:**
- trust.bias_index goes critical
- Grace auto-tightens guardrails
- Autonomy ratio reduced
- Human oversight escalated

**Expected Actions:** tighten-guardrails, downgrade-autonomy-tier

---

### 6. Approval Queue Jam
**Citation:** [docs/METRICS_CATALOG.md:55-76](file:///c:/Users/aaron/grace_2/docs/METRICS_CATALOG.md#L55-L76)

**What:** Queue 10+ high-risk actions, delay approvals

**Validates:**
- trust.governance_latency increases
- autonomy.approvals_pending rises
- Plans reassigned or paused
- State logged immutably

**Expected Actions:** pause-high-risk-plans, notify-reviewers

---

## 🚀 Running Stress Tests

### Prerequisites:
```powershell
# 1. Boot Grace
.\BOOT_GRACE_REAL.ps1

# 2. Wait for startup complete
# Look for: [METRICS] ✅ Real telemetry system started
```

### Run Full Suite:
```powershell
# In new window
cd tests
pytest stress_test_suite.py -v -s
```

Or run directly:
```powershell
python tests/stress_test_suite.py
```

---

## 📊 Methodical Testing Approach

### 1. Define Scenarios
Per [docs/METRICS_CATALOG.md:197-217](file:///c:/Users/aaron/grace_2/docs/METRICS_CATALOG.md#L197-L217):
- Pick realistic failure modes
- Log as structured experiments
- Compare against healthy baseline

### 2. Instrument the Run
Per [docs/METRICS_CATALOG.md:118-151](file:///c:/Users/aaron/grace_2/docs/METRICS_CATALOG.md#L118-L151):
- Tag each scenario in immutable log
- Correlate metric spikes with playbook activations
- Create reusable training data

### 3. Validate Responses
Per [docs/METRICS_CATALOG.md:45-95](file:///c:/Users/aaron/grace_2/docs/METRICS_CATALOG.md#L45-L95):
- Confirm playbooks execute
- Verify metrics tracked
- Capture post-mortems

### 4. Feed Learning Loop
- Archive stress test snapshots
- Store outcomes in provenance
- Enable regression detection

---

## 📈 What to Monitor

During tests, watch:
```powershell
# Metrics snapshots
curl http://localhost:8000/api/metrics

# Approval queue
curl http://localhost:8000/api/governance/approvals

# Immutable log (test scenarios)
curl http://localhost:8000/api/immutable/audit | findstr "scenario"

# System health
curl http://localhost:8000/health
```

---

## ✅ Success Criteria

Each scenario should:
1. ✅ Publish to immutable log (scenario_start/scenario_end)
2. ✅ Trigger appropriate playbook recommendations
3. ✅ Execute or request approval based on risk
4. ✅ Log all actions to immutable log
5. ✅ Return system to stable state

---

## 📝 Post-Test Analysis

After running:
```powershell
# View all stress test entries
python -c "from backend.immutable_log import immutable_log; import asyncio; asyncio.run(immutable_log.query({'action_pattern': 'scenario_%'}))"

# Check metrics snapshots during test windows
# Review playbook execution logs
# Archive for future baseline comparison
```

---

**Stress tests validate Grace can handle real-world failure modes autonomously!** 🎯
