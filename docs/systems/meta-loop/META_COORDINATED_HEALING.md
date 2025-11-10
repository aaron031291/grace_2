# Meta-Coordinated Self-Healing Architecture

## Proper Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│                   META LOOP                              │
│              (Orchestrator & Decision Maker)             │
│                                                           │
│  Decides: WHEN, WHAT, and HOW AGGRESSIVELY              │
│  • Focus area this cycle (latency vs errors vs capacity)│
│  • Guardrail adjustments (tighten/loosen autonomy)       │
│  • Extra probes to enable                                │
│  • Time budget for actions                               │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌──────────────────┐    ┌──────────────────┐
│   ML/DL MODELS   │    │  AGENTIC LAYER   │
│   (Advisors)     │───▶│  (Executor)      │
│                  │    │                  │
│ • Anomaly scores │    │ • Planner        │
│ • Root causes    │    │ • Trust check    │
│ • Playbook ranks │    │ • Execution      │
│ (NOT autonomous) │    │ • Verification   │
└──────────────────┘    │ • Rollback       │
                        └─────────┬────────┘
                                  │
                                  ▼
                        ┌──────────────────┐
                        │  IMMUTABLE LOG   │
                        │  (Source of Truth)│
                        │                  │
                        │ • Signed entries │
                        │ • Audit replay   │
                        │ • Learning data  │
                        └──────────────────┘
```

## Core Principle

**The meta loop orchestrates, ML/DL advises, agentic layer executes, immutable log records.**

## Architecture Components

### 1. Meta Loop (Orchestrator)

**Role:** Decides WHEN the self-healing system needs to act and WHAT to focus on.

**Responsibilities:**
- Observe cross-system performance every 2 minutes
- Decide focus area for this cycle:
  - `LATENCY_DRIFT` - Focus on response time issues
  - `ERROR_SPIKE` - Focus on error rate
  - `CAPACITY_STRAIN` - Focus on resource saturation
  - `DEPENDENCY_HEALTH` - Focus on upstream services
  - `TRUST_VIOLATIONS` - Focus on governance issues
  - `ROUTINE_MAINTENANCE` - Normal operations
- Adjust guardrails:
  - `TIGHTEN` - More conservative, require more approvals
  - `LOOSEN` - Allow more autonomy, faster execution
  - `MAINTAIN` - Keep current settings
- Spin up extra probes (additional monitoring)
- Set time budget for actions
- Learn from outcomes and adjust future cycles

**Example Decision:**
```python
CycleFocus(
    cycle_id="cycle_20250115_143000_42",
    focus_area=FocusArea.LATENCY_DRIFT,
    reasoning=[
        "Latency drift: 150ms → 245ms",
        "Traffic patterns indicate sustained load"
    ],
    confidence=0.85,
    guardrail_adjustment=GuardrailAdjustment.LOOSEN,  # Allow proactive scaling
    extra_probes=["latency_histograms"],
    playbook_priorities=["scale_up_instances", "warm_cache"],
    time_budget_seconds=120
)
```

### 2. ML/DL Models (Embedded Advisors)

**Role:** Provide recommendations, NOT act autonomously.

**ML Advisors:**

#### Anomaly Scorer
- Scores incoming signals for anomaly likelihood
- Feeds trigger mesh with scored events
- Does NOT trigger actions directly

#### Root Cause Suggester
- Analyzes patterns to suggest probable root causes
- Maps symptoms to likely causes
- Provides ranked list of candidates

#### Playbook Ranker
- Ranks playbooks based on:
  - Historical success rate for (service, diagnosis)
  - Recent performance trends
  - Context (time of day, load, dependencies)
- Returns sorted list with confidence scores

**Example ML Advice:**
```python
MLAdvice(
    advice_id="advice_cycle_20250115_143000_42",
    model_type="ensemble",
    focus_area=FocusArea.LATENCY_DRIFT,
    recommendations=[
        {"type": "anomaly", "severity": "medium", "description": "Latency trending upward"}
    ],
    confidence_scores={
        "anomaly_scorer": 0.82,
        "root_cause": 0.75,
        "playbook_ranker": 0.88
    },
    root_cause_candidates=[
        "database_slow_query",
        "cache_miss_rate_high",
        "cpu_saturation"
    ],
    ranked_playbooks=[
        ("scale_up_instances", 0.88),
        ("warm_cache", 0.75),
        ("restart_service", 0.62)
    ]
)
```

**Key Point:** ML models advise the meta loop, which then issues directives to the agentic layer. They do NOT execute playbooks themselves.

### 3. Agentic Layer (Execution Engine)

**Role:** Plan, validate, execute, and verify recovery actions.

**Pipeline:**
1. **Receive Directive** from meta loop
2. **Plan** - Create execution plan with steps
3. **Trust Check** - Validate against governance policies
4. **Execute** - Run playbook steps
5. **Verify** - Check expected outcome
6. **Rollback** - If verification fails
7. **Sign & Log** - Record outcome to immutable log

**Example Directive:**
```python
# Meta loop issues directive
{
    "cycle_id": "cycle_20250115_143000_42",
    "focus_area": "latency_drift",
    "guardrail_level": "loosen",
    "ml_advice": {
        "root_causes": ["database_slow_query", "cache_miss_rate_high"],
        "recommended_playbooks": ["scale_up_instances", "warm_cache"],
        "confidence_scores": {"playbook_ranker": 0.88}
    },
    "time_budget_seconds": 120,
    "requires_verification": True
}
```

**Agentic Response:**
```python
# 1. Plan
AgenticPlan(
    plan_id="plan_143000_001",
    service="api_cluster",
    diagnosis={"code": "latency_drift", "confidence": 0.85},
    selected_playbook="scale_up_instances",
    steps=[
        {"action": "check_current_capacity", "timeout": 10},
        {"action": "scale_instances", "params": {"delta": 2}, "timeout": 60},
        {"action": "wait_for_ready", "timeout": 30}
    ],
    verifications=[
        {"type": "health_check", "endpoint": "/health"},
        {"type": "latency_threshold", "max_ms": 200}
    ],
    rollback_plan=[
        {"action": "scale_instances", "params": {"delta": -2}}
    ],
    trust_approval_required=False,  # Guardrails loosened
    estimated_duration=100,
    risk_assessment={"blast_radius": 1, "impact": "low"}
)

# 2. Trust Check (auto-approved due to loosened guardrails)

# 3. Execute (with verification)

# 4. Sign Outcome
SignedOutcome(
    outcome_id="outcome_143100_001",
    cycle_id="cycle_20250115_143000_42",
    plan_id="plan_143000_001",
    service="api_cluster",
    playbook="scale_up_instances",
    result="success",
    duration_seconds=85.3,
    verification_passed=True,
    trust_decision="auto_approved",
    actor_signature="a3f8b9c2...",
    rationale=[
        "Meta loop directive: focus on latency_drift",
        "ML advice: scale_up_instances (score: 0.88)",
        "Guardrails: loosened for proactive action",
        "Verification: latency reduced to 165ms"
    ],
    learned_insights=[
        "Scaling effective for this load pattern",
        "2 instances sufficient for 30% latency reduction",
        "No rollback needed - verification passed"
    ]
)
```

### 4. Immutable Log (Single Source of Truth)

**Role:** Permanent, auditable record of ALL decisions and actions.

**Signed Entries:**

Every critical action is signed and stored:

```python
# Meta loop decision
await immutable_log.append(
    actor="meta_loop",
    action="cycle_focus_decided",
    resource="self_heal",
    subsystem="meta_coordinated_healing",
    payload={
        "cycle_id": "cycle_20250115_143000_42",
        "focus_area": "latency_drift",
        "reasoning": ["Latency drift: 150ms → 245ms"],
        "guardrail_adjustment": "loosen"
    },
    result="decided",
    signature="f4a9c8e1..."  # Cryptographic signature
)

# ML advice
await immutable_log.append(
    actor="ml_advisors",
    action="advice_provided",
    resource="self_heal",
    subsystem="meta_coordinated_healing",
    payload={
        "root_causes": ["database_slow_query"],
        "top_playbooks": ["scale_up_instances"]
    },
    result="advised",
    signature="b2d7e5f3..."
)

# Agentic execution
await immutable_log.append(
    actor="agentic_planner",
    action="execution_outcome",
    resource="api_cluster",
    subsystem="meta_coordinated_healing",
    payload={
        "playbook": "scale_up_instances",
        "result": "success",
        "verification_passed": True,
        "learned_insights": [...]
    },
    result="success",
    signature="c8f1a4b9..."
)
```

**Replay Capability:**

Audit any cycle by replaying all signed entries:

```python
# Replay entire healing cycle
replay = await immutable_log.replay_cycle("cycle_20250115_143000_42")

# Returns chronological list:
[
    {
        "sequence": 1042,
        "timestamp": "2025-01-15T14:30:00Z",
        "actor": "meta_loop",
        "action": "cycle_focus_decided",
        "signature": "f4a9c8e1...",
        "payload": {...}
    },
    {
        "sequence": 1043,
        "timestamp": "2025-01-15T14:30:05Z",
        "actor": "ml_advisors",
        "action": "advice_provided",
        "signature": "b2d7e5f3...",
        "payload": {...}
    },
    {
        "sequence": 1044,
        "timestamp": "2025-01-15T14:31:30Z",
        "actor": "agentic_planner",
        "action": "execution_outcome",
        "signature": "c8f1a4b9...",
        "payload": {...}
    }
]
```

## Flow Examples

### Example 1: Latency Drift - Proactive Scaling

```
14:30:00 - Meta Loop Cycle 42 starts
14:30:01 - Meta loop observes: Latency 150ms → 245ms
14:30:02 - Meta loop decides: Focus on LATENCY_DRIFT
14:30:02 - Guardrails: LOOSEN (allow proactive action)
14:30:03 - Extra probes enabled: latency_histograms
14:30:04 - ML anomaly scorer: 0.82 confidence
14:30:05 - ML root cause: database_slow_query (0.75)
14:30:06 - ML playbook ranker: scale_up_instances (0.88)
14:30:07 - Meta loop issues directive to agentic planner
14:30:08 - Agentic planner creates plan
14:30:09 - Trust check: AUTO-APPROVED (guardrails loosened)
14:30:10 - Execution starts: scale +2 instances
14:31:20 - Instances ready
14:31:25 - Verification: latency now 165ms ✓
14:31:26 - Outcome signed to immutable log
14:31:27 - Meta loop learns: "Scaling effective for this pattern"
```

### Example 2: Error Spike - Tighten Guardrails

```
09:15:00 - Meta Loop Cycle 18 starts
09:15:01 - Meta loop observes: 15 errors in 5min
09:15:02 - Meta loop decides: Focus on ERROR_SPIKE
09:15:02 - Guardrails: TIGHTEN (require more approvals)
09:15:03 - Extra probes: error_tracking, stack_traces
09:15:04 - ML anomaly scorer: 0.90 confidence (high)
09:15:05 - ML root cause: bad_deployment (0.85)
09:15:06 - ML playbook ranker: rollback_flag (0.92)
09:15:07 - Meta loop issues directive
09:15:08 - Agentic planner creates rollback plan
09:15:09 - Trust check: REQUIRES APPROVAL (guardrails tight)
09:15:10 - Approval request created
09:18:00 - Human approves rollback
09:18:01 - Execution: disable feature flag
09:18:05 - Verification: errors dropped to 0 ✓
09:18:06 - Outcome signed
09:18:07 - Meta loop learns: "Rollback effective, keep tight guardrails"
```

### Example 3: Routine Maintenance

```
22:00:00 - Meta Loop Cycle 95 starts
22:00:01 - Meta loop observes: System stable
22:00:02 - Meta loop decides: ROUTINE_MAINTENANCE
22:00:02 - Guardrails: MAINTAIN
22:00:03 - No extra probes needed
22:00:04 - ML advisors: No anomalies detected
22:00:05 - Meta loop: No directive needed
22:00:06 - Cycle complete, no action taken
```

## Benefits of This Architecture

### 1. Clear Separation of Concerns

- **Meta loop** = Strategy (what to focus on)
- **ML/DL** = Advice (what might work best)
- **Agentic layer** = Tactics (how to execute safely)
- **Immutable log** = Truth (what actually happened)

### 2. Auditability & Compliance

Every decision has a signature and rationale:
- Who decided what
- Why they decided it
- What advice they received
- What happened
- What was learned

### 3. Continuous Learning

Meta loop learns from signed outcomes:
- Which focus areas are most common
- When to tighten/loosen guardrails
- Which ML advice is most accurate
- Which playbooks succeed/fail

### 4. Adaptive Guardrails

System adjusts autonomy based on performance:
- Success rate > 85% → Loosen (more autonomy)
- Success rate < 50% → Tighten (more oversight)
- Error spikes → Tighten immediately
- Stable periods → Loosen gradually

### 5. Explainable Decisions

Every action has clear provenance:
```
Action: scale_up_instances
├─ Meta loop: "Latency drift detected"
├─ ML root cause: "database_slow_query (0.75)"
├─ ML recommendation: "scale_up_instances (0.88)"
├─ Trust decision: "auto_approved (guardrails loosened)"
├─ Outcome: "success (verification passed)"
└─ Signature: "c8f1a4b9..." (auditable)
```

## Configuration

### Cycle Frequency
```python
# Meta loop coordination cycle
COORDINATION_CYCLE_SECONDS = 120  # 2 minutes

# Focus area confidence threshold
FOCUS_DECISION_MIN_CONFIDENCE = 0.70

# Guardrail adjustment thresholds
LOOSEN_SUCCESS_RATE_THRESHOLD = 0.85
TIGHTEN_SUCCESS_RATE_THRESHOLD = 0.50
```

### ML Advisor Weights
```python
# Weight ML advice in decision making
ML_ANOMALY_WEIGHT = 0.30
ML_ROOT_CAUSE_WEIGHT = 0.25
ML_PLAYBOOK_WEIGHT = 0.45

# Minimum confidence to accept ML advice
ML_MIN_CONFIDENCE = 0.65
```

### Guardrail Levels
```python
# TIGHT: Conservative, require approvals
TIGHT_AUTO_APPROVE_THRESHOLD = 0.95  # Almost never
TIGHT_BLAST_RADIUS_MAX = 1
TIGHT_IMPACT_MAX = "low"

# MAINTAIN: Balanced approach
MAINTAIN_AUTO_APPROVE_THRESHOLD = 0.80
MAINTAIN_BLAST_RADIUS_MAX = 2
MAINTAIN_IMPACT_MAX = "medium"

# LOOSE: Aggressive autonomy
LOOSE_AUTO_APPROVE_THRESHOLD = 0.65
LOOSE_BLAST_RADIUS_MAX = 3
LOOSE_IMPACT_MAX = "medium"
```

## API Usage

### Replay a Healing Cycle
```python
from backend.immutable_log import immutable_log

# Get all signed entries for a cycle
replay = await immutable_log.replay_cycle("cycle_20250115_143000_42")

# Audit: Who decided what and why?
for entry in replay:
    print(f"{entry['timestamp']} - {entry['actor']}: {entry['action']}")
    print(f"  Signature: {entry['signature']}")
    print(f"  Result: {entry['result']}")
```

### Get Learning Data
```python
# Get signed outcomes for ML training
outcomes = await immutable_log.get_signed_outcomes(
    subsystem="meta_coordinated_healing",
    hours_back=24,
    limit=100
)

# Analyze success rates
success_count = sum(1 for o in outcomes if o['result'] == 'success')
success_rate = success_count / len(outcomes) if outcomes else 0

# Train playbook ranking model
training_data = [
    {
        "playbook": o['playbook'],
        "context": o['cycle_id'],
        "success": o['verification_passed']
    }
    for o in outcomes
]
```

### Monitor Current Cycle
```python
from backend.self_heal.meta_coordinated_healing import meta_coordinated_healing

# Current focus
current = meta_coordinated_healing.current_cycle
print(f"Focus: {current.focus_area.value}")
print(f"Guardrails: {current.guardrail_adjustment.value}")

# Recent outcomes
recent = meta_coordinated_healing.outcome_history[-10:]
for outcome in recent:
    print(f"{outcome.playbook}: {outcome.result}")
```

---

**GRACE now has a properly hierarchical self-healing system where the meta loop orchestrates, ML/DL advises, the agentic layer executes, and the immutable log provides a permanent, auditable record of everything that happens.**
