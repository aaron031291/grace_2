# Agentic Observability

**Transparent View Into Autonomous Decisions**

## Overview

**Agentic Observability** provides a clean, focused view into what GRACE's autonomous agent is doing—without exposing every internal detail. It surfaces:

✅ **What the agent sensed** - The signal that triggered action  
✅ **What it diagnosed** - Root cause analysis  
✅ **What it planned** - Recovery strategy chosen  
✅ **What guardrails it checked** - Trust & policy validation  
✅ **What it executed** - Actions taken  
✅ **What the outcome was** - Success or failure  

This is **decision transparency** for ops teams, auditors, and stakeholders.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│          AGENTIC OBSERVABILITY LAYER                    │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼────────┐
│ Insight        │  │ Read        │  │ Dashboard       │
│ Capture        │  │ Models      │  │ Data            │
│                │  │             │  │                 │
│ • Captures     │  │ • Active    │  │ • Summary       │
│   decisions    │  │   runs      │  │ • Timeline      │
│ • Privacy      │  │ • Details   │  │ • Statistics    │
│   filters      │  │ • Approvals │  │                 │
│ • Verbosity    │  │ • Stats     │  │                 │
└───────┬────────┘  └──────┬──────┘  └────────┬────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                ┌───────────▼───────────┐
                │  Agentic Insights DB  │
                │  (Compact ledger)     │
                └───────────┬───────────┘
                            │
                ┌───────────▼───────────┐
                │   HTTP API            │
                │   /agent/...          │
                └───────────┬───────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼────────┐
│ Ops Dashboard  │  │ CLI Tools   │  │ Audit Reports   │
└────────────────┘  └─────────────┘  └─────────────────┘
```

---

## Decision Flow Tracking

### Example: Autonomo Recovery

```
1. SENSING
   📡 Detected signal
   ├─ What: "latency_degraded" from monitoring
   ├─ Resource: api-service
   └─ Confidence: 95%

2. DIAGNOSIS
   🔍 Diagnosed issue
   ├─ What: High CPU utilization causing latency
   ├─ Root cause: Traffic spike
   └─ Confidence: 82%

3. PLANNING
   📋 Planned response
   ├─ Options considered:
   │  • Scale up capacity
   │  • Restart service
   │  • Enable rate limiting
   ├─ Chosen: Scale up capacity
   └─ Rationale: "Proven playbook with 92% success rate"

4. GUARDRAIL CHECK
   🛡️ Checked guardrails
   ├─ Guardrails:
   │  • Within budget limits ✓
   │  • No recent deployments ✓
   │  • Trust core approval ✓
   ├─ Risk score: 0.3 (low)
   └─ Approval required: No

5. EXECUTION
   ⚡ Executing plan
   ├─ Action: Scale from 10 → 15 instances
   └─ Duration: 45 seconds

6. VERIFICATION
   ✅ Verifying outcome
   ├─ Latency: 450ms → 180ms ✓
   ├─ CPU: 85% → 62% ✓
   └─ Status: Success

7. COMPLETION
   🎯 Completed
   ├─ Outcome: Success
   ├─ Duration: 52 seconds
   └─ Human notified: Yes
```

**This entire trace is captured, queryable, and auditable.**

---

## Data Model

### AgenticInsight (Database)

Compact ledger storing agentic decisions:

```sql
CREATE TABLE agentic_insights (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(64) NOT NULL,
    phase VARCHAR(32) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE,
    
    -- What agent perceived
    signal_type VARCHAR(64),
    signal_summary VARCHAR(256),
    
    -- What agent diagnosed
    diagnosis VARCHAR(256),
    root_cause VARCHAR(256),
    
    -- What agent planned
    plan_type VARCHAR(64),
    plan_summary VARCHAR(512),
    rationale TEXT,
    options_considered TEXT,
    chosen_option VARCHAR(256),
    
    -- Guardrails
    guardrails_checked TEXT,
    guardrails_passed BOOLEAN,
    risk_score FLOAT,
    confidence FLOAT,
    
    -- Approval
    approval_required BOOLEAN,
    approved_by VARCHAR(64),
    approved_at TIMESTAMP,
    
    -- Outcome
    outcome VARCHAR(64),
    outcome_detail TEXT,
    verified BOOLEAN,
    
    -- Privacy
    sensitive_data_redacted BOOLEAN,
    metadata TEXT
);

CREATE INDEX idx_run_id ON agentic_insights(run_id);
CREATE INDEX idx_timestamp ON agentic_insights(timestamp);
```

---

## API Endpoints

### GET /agent/status

Get current agentic status (active runs, pending approvals)

**Response:**
```json
{
  "status": "active",
  "active_runs": 2,
  "pending_approvals": 0,
  "highest_risk": 0.45
}
```

### GET /agent/runs/active

Get all currently active agentic runs

**Response:**
```json
[
  {
    "run_id": "run_1730901234",
    "started_at": "2025-11-06T14:30:00Z",
    "current_phase": "execution",
    "signal": "monitoring: latency_degraded",
    "plan": "Scale api-service capacity",
    "risk_score": 0.3,
    "approval_required": false
  }
]
```

### GET /agent/runs/{run_id}

Get detailed trace of a specific run

**Response:**
```json
{
  "run_id": "run_1730901234",
  "started_at": "2025-11-06T14:30:00Z",
  "phases": [
    {
      "phase": "sensing",
      "timestamp": "2025-11-06T14:30:00Z",
      "what": "monitoring: latency_degraded",
      "why": null,
      "confidence": 0.95,
      "risk_score": null
    },
    {
      "phase": "diagnosis",
      "timestamp": "2025-11-06T14:30:02Z",
      "what": "High CPU utilization",
      "why": "Traffic spike",
      "confidence": 0.82,
      "risk_score": null
    },
    {
      "phase": "planning",
      "timestamp": "2025-11-06T14:30:04Z",
      "what": "Scale up capacity",
      "why": "Proven playbook with 92% success rate",
      "confidence": null,
      "risk_score": 0.3
    }
  ],
  "outcome": "success",
  "verified": true
}
```

### GET /agent/runs/{run_id}/timeline

Get visual timeline for dashboards

**Response:**
```json
{
  "run_id": "run_1730901234",
  "timeline": [
    {
      "time": "2025-11-06T14:30:00Z",
      "phase": "sensing",
      "label": "📡 Detected signal",
      "status": "success",
      "details": {
        "what": "monitoring: latency_degraded",
        "confidence": 0.95
      }
    }
  ],
  "outcome": "success",
  "duration_seconds": 52
}
```

### GET /agent/decisions/recent

Get recent agentic decisions

**Query params:**
- `hours` - Lookback period (default: 24)
- `limit` - Max results (default: 50)

**Response:**
```json
[
  {
    "run_id": "run_1730901234",
    "timestamp": "2025-11-06T14:30:00Z",
    "signal": "latency_degraded",
    "plan": "Scale up capacity",
    "outcome": "success",
    "success": true,
    "risk_score": 0.3
  }
]
```

### GET /agent/approvals/pending

Get runs awaiting human approval

**Response:**
```json
[
  {
    "run_id": "run_1730901500",
    "timestamp": "2025-11-06T14:35:00Z",
    "plan": "Failover to database replica",
    "risk_score": 0.75,
    "rationale": "Primary DB showing signs of failure"
  }
]
```

### GET /agent/statistics

Get performance statistics

**Query params:**
- `hours` - Lookback period (default: 24)

**Response:**
```json
{
  "total_runs": 142,
  "successful_runs": 134,
  "success_rate": 0.944,
  "average_risk_score": 0.28,
  "autonomous_decisions": 128,
  "autonomy_rate": 0.901,
  "pending_approvals": 1
}
```

### GET /agent/dashboard

Get complete dashboard summary

**Response:**
```json
{
  "current_state": {
    "status": "active",
    "active_run_count": 2,
    "pending_approval_count": 1,
    "highest_risk_run": 0.75
  },
  "active_runs": [...],
  "pending_approvals": [...],
  "recent_decisions": [...],
  "statistics_24h": {...},
  "statistics_7d": {...}
}
```

### POST /agent/verbosity

Set observability verbosity level

**Body:**
```json
{
  "level": "summary"
}
```

**Levels:**
- `minimal` - Only outcomes
- `summary` - Key decisions (default)
- `detailed` - Full decision trail
- `debug` - Everything

---

## Verbosity Levels

### Minimal
Captures only completion phase:
- What was the final outcome?
- Success or failure?

**Use case:** Production, minimal storage

### Summary (Default)
Captures key decision points:
- What triggered action?
- What plan was chosen?
- What were guardrails?
- What was outcome?

**Use case:** Ops teams, daily monitoring

### Detailed
Captures full decision trail:
- All phases (sensing → completion)
- All options considered
- All guardrail checks
- Complete rationale

**Use case:** Incident review, audits

### Debug
Captures everything:
- Full metadata
- Complete payloads
- Internal state

**Use case:** Development, debugging

---

## Privacy Guardrails

### Automatic Redaction

Sensitive fields automatically redacted:
- `password`, `token`, `secret`, `key`, `credential`
- Marked with `sensitive_data_redacted=true`

**Example:**
```json
{
  "context": {
    "database": "prod-db",
    "password": "[REDACTED]",
    "connection_string": "[REDACTED]"
  },
  "sensitive_data_redacted": true
}
```

### Configurable Filters

Add custom privacy filters:
```python
agentic_observability.capture.privacy_filters.extend([
    "ssn", "credit_card", "api_key"
])
```

---

## Dashboard Integration

### Ops Dashboard Widgets

**Active Runs Widget:**
```
┌─────────────────────────────────────┐
│ Active Agentic Runs (2)             │
├─────────────────────────────────────┤
│ run_1730901234                      │
│ ⚡ Executing: Scale api-service     │
│ Risk: 0.3 (Low) | Started: 2min ago │
│                                     │
│ run_1730901500                      │
│ ✋ Awaiting approval                │
│ Risk: 0.75 (High) | Started: 5min  │
└─────────────────────────────────────┘
```

**Statistics Widget:**
```
┌─────────────────────────────────────┐
│ Agentic Performance (24h)           │
├─────────────────────────────────────┤
│ Total Runs:         142             │
│ Success Rate:       94.4%           │
│ Autonomy Rate:      90.1%           │
│ Avg Risk Score:     0.28            │
│ Pending Approvals:  1               │
└─────────────────────────────────────┘
```

**Recent Decisions:**
```
┌─────────────────────────────────────┐
│ Recent Decisions                    │
├─────────────────────────────────────┤
│ 14:30 ✓ Scale api-service           │
│ 14:22 ✓ Restart cache cluster       │
│ 14:15 ✓ Update health check         │
│ 14:08 ✗ Failover attempt failed     │
│ 14:01 ✓ Enable rate limiting        │
└─────────────────────────────────────┘
```

---

## Usage

### Starting Observability

```python
from backend.grace_spine_integration import activate_grace_autonomy

# Starts automatically with spine
await activate_grace_autonomy()
# → Agentic Observability started - Transparent decision tracking
```

### Capturing Decisions (Internal)

The agentic spine automatically captures decisions:

```python
from backend.agentic_observability import agentic_observability

# Start tracking a run
await agentic_observability.capture.start_run(
    run_id="run_123",
    trigger_event=event,
    context={"resource": "api-service"}
)

# Record diagnosis
await agentic_observability.capture.record_diagnosis(
    run_id="run_123",
    diagnosis="High CPU utilization",
    root_cause="Traffic spike",
    confidence=0.82
)

# Record plan
await agentic_observability.capture.record_plan(
    run_id="run_123",
    plan_type="scale_up",
    plan_summary="Scale from 10 → 15 instances",
    options_considered=["Scale up", "Restart", "Rate limit"],
    chosen_option="Scale up",
    rationale="Proven 92% success rate"
)

# Complete run
await agentic_observability.capture.complete_run(
    run_id="run_123",
    final_outcome="Latency normalized",
    success=True
)
```

### Querying (External)

Ops teams query via API:

```bash
# Get current status
curl http://localhost:8000/agent/status

# Get active runs
curl http://localhost:8000/agent/runs/active

# Get run details
curl http://localhost:8000/agent/runs/run_123

# Get recent decisions
curl http://localhost:8000/agent/decisions/recent?hours=6

# Get statistics
curl http://localhost:8000/agent/statistics?hours=24

# Set verbosity
curl -X POST http://localhost:8000/agent/verbosity \
  -H "Content-Type: application/json" \
  -d '{"level": "detailed"}'
```

---

## Benefits

### For Ops Teams
- **Real-time visibility** into what GRACE is doing
- **Understand decisions** without reading code
- **Intervene when needed** (approve/reject)
- **Monitor performance** (success rate, autonomy rate)

### For Auditors
- **Complete audit trail** of all autonomous actions
- **Decision rationale** for every action
- **Guardrail verification** logged
- **Privacy compliance** (sensitive data redacted)

### For Stakeholders
- **Trust through transparency** - See what the agent does
- **Performance metrics** - Is it working?
- **Risk visibility** - What's the risk exposure?

---

## Files

- `backend/agentic_observability.py` - Core observability system
- `backend/routes/agentic_insights.py` - HTTP API
- `docs/AGENTIC_OBSERVABILITY.md` - This documentation

---

## Summary

Agentic Observability provides **clean transparency** into GRACE's autonomous decisions:

✅ **Captures** sensing, diagnosis, planning, guardrails, execution, verification  
✅ **Stores** in compact agentic insights ledger  
✅ **Exposes** via HTTP API for dashboards, tools, audits  
✅ **Protects** privacy with automatic redaction  
✅ **Controls** verbosity (minimal → debug)  

**Humans understand what the agent is doing and why—without internal implementation details.**
