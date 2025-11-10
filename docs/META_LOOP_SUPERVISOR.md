# Meta Loop Supervisor - Cross-Domain Oversight

## Overview

The **Meta Loop Supervisor** is the "supervisor watching the autonomous agent." It sits atop the agentic spine, analyzing cross-domain performance and issuing directives to optimize how GRACE behaves across all domains.

This is **systemic oversight** - not reacting to individual incidents, but monitoring patterns, detecting drift from strategic goals, and continuously tuning the spine's decision-making to improve overall performance.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              META LOOP SUPERVISOR                       │
│   (Supervisory layer above the autonomous spine)        │
└─────────────────────────────────────────────────────────┘
           │                    │                    │
    ┌──────▼──────┐      ┌─────▼──────┐     ┌──────▼──────┐
    │  Snapshot   │      │  Strategy  │     │ Directive   │
    │  Builder    │─────▶│  Engine    │────▶│  Pipeline   │
    └──────┬──────┘      └────────────┘     └──────┬──────┘
           │                                        │
           │                                        ▼
           │                                  ┌──────────────┐
           └─────────────────────────────────▶│ Verification │
                                              │    Layer     │
                                              └──────────────┘
                                                      │
                                                      ▼
           ┌──────────────────────────────────────────────────┐
           │            AGENTIC SPINE                         │
           │  (Enrichment → Planning → Execution → Learning)  │
           └──────────────────────────────────────────────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 ▼                ▼                ▼
          ┌──────────┐     ┌──────────┐    ┌──────────┐
          │Infra     │     │App       │    │Security  │
          │Domain    │     │Domain    │    │Domain    │
          └──────────┘     └──────────┘    └──────────┘
```

---

## Data Flow

### 1. Input Tap (Reading)
Meta loop subscribes to:
- **Trigger Mesh** - All signed events from domain adapters
- **Immutable Ledger** - KPI deltas, trust annotations, outcome logs
- **Health Graph** - Current system topology and health
- **Learning Integration** - Decision outcomes and success rates

### 2. Synthesis Layer
Builds cross-domain snapshot:
- Aggregates health states across all domains
- Calculates KPI drift from baselines
- Identifies policy exceptions and trust violations
- Tracks playbook success rates
- Compares current state to strategic goals
- Detects systemic patterns (e.g., multi-domain drift)

### 3. Decision Hooks (Writing)
Issues directives back to spine:
- **Adjust thresholds** - Tighten/loosen confidence bands
- **Enable/disable playbooks** - Activate proven playbooks, retire failing ones
- **Schedule experiments** - Test new recovery strategies
- **Request reviews** - Escalate to humans when uncertain
- **Adjust policies** - Update trust core rules

Directives flow through:
1. Strategy Engine → Directive Pipeline
2. Directive Pipeline → Autonomous Planner (via trigger mesh)
3. Planner → Trust Core (for approval if high-impact)
4. Planner → Execution

### 4. Feedback Actions
Meta loop can:
- Seed synthetic probes via sensing layer
- Request ledger queries for pattern analysis
- Push configuration updates to domain adapters
- Trigger human collaboration for high-impact changes

### 5. Learning Feed
Logs its own decisions:
- Every directive logged to immutable ledger
- Outcomes tracked for future meta cycles
- Summaries published to human channels
- Enables auditors to trace why guardrails shifted

---

## Operational Cycle

```
1. SPINE RUNS NORMAL OPS
   ├─ Sensing → Enrichment → Planning → Execution
   └─ All signals → Immutable Ledger + KPI stores

2. META LOOP PERIODICALLY ANALYZES
   ├─ Build cross-domain snapshot
   ├─ Compare to baselines & goals
   ├─ Detect patterns & gaps
   └─ Decide on systemic adjustments

3. META LOOP ISSUES DIRECTIVES
   ├─ Directives → Planner (via trigger mesh)
   ├─ Trust core approval (if needed)
   └─ Planner executes like any task

4. META LOOP VERIFIES OUTCOMES
   ├─ Wait for next cycle
   ├─ Compare pre/post snapshots
   ├─ Rollback if verification fails
   └─ Log outcome to ledger

5. HUMANS STAY INFORMED
   └─ Summaries published to channels
```

**Cycle Frequency:** Every 5 minutes (configurable)

---

## Components

### 1. Snapshot Builder

**Purpose:** Aggregates cross-domain data into unified snapshots.

**Data Sources:**
- Health graph states
- KPI time series
- Trust exceptions
- Playbook execution history
- Decision outcomes from learning integration

**Output:** `CrossDomainSnapshot` containing:
- Domain-specific snapshots
- Global aggregated KPIs
- Cross-domain correlations
- Strategic goal gaps
- Systemic patterns

**Example:**
```python
snapshot = await snapshot_builder.build_snapshot()
# snapshot.global_kpis = {
#   "overall_success_rate": 0.87,
#   "mean_recovery_time_seconds": 42.3,
#   "autonomy_rate": 0.73
# }
# snapshot.goal_gaps = {
#   "overall_success_rate": 0.08,  # 8% below target
#   "mean_recovery_time_seconds": -12.3  # 12s above target
# }
```

---

### 2. Strategy Engine

**Purpose:** Analyzes snapshots and decides on systemic adjustments.

**Policy Framework:**
- Registers meta policies (rules for when to intervene)
- Evaluates policy conditions against snapshots
- Generates directives from policy templates
- Calculates decision confidence

**Meta Policies:**
Each policy has:
- **Condition** - When to trigger (e.g., "success rate < 90%")
- **Directive Template** - What action to take
- **Confidence Threshold** - Minimum confidence required
- **Approval Threshold** - When to request human approval

**Example Policy:**
```python
policy = MetaPolicy(
    policy_id="improve_success_rate",
    condition={
        "goal_gap_metric": "overall_success_rate",
        "goal_gap_threshold": 0.05  # Trigger if 5% below goal
    },
    directive_template={
        "type": "ADJUST_THRESHOLD",
        "action": "increase_playbook_confidence_threshold",
        "parameters": {"adjustment": 0.05},
        "impact_level": "LOW"
    }
)
```

**Analysis Output:**
- Underperforming domains
- Overperforming domains
- Systemic patterns
- Recommendations

---

### 3. Directive Pipeline

**Purpose:** Routes directives back into spine for execution.

**Workflow:**
1. Receives directives from strategy engine
2. Checks if human approval required (based on impact level)
3. Publishes to trigger mesh
4. Planner receives via event subscription
5. Planner executes through trust core
6. Outcome logged to ledger

**Directive Types:**
- `ADJUST_THRESHOLD` - Tune confidence/risk thresholds
- `ENABLE_PLAYBOOK` - Activate a recovery playbook
- `DISABLE_PLAYBOOK` - Retire a playbook
- `ADJUST_CONFIDENCE` - Change confidence bands
- `SCHEDULE_EXPERIMENT` - Run controlled test
- `REQUEST_REVIEW` - Escalate to human
- `ENABLE_PROBE` - Add synthetic monitoring
- `ROLLBACK_CHANGE` - Undo previous directive

**Impact Levels:**
- `MINIMAL` - Auto-execute, no approval
- `LOW` - Auto-execute, notify humans
- `MODERATE` - Require approval for production
- `HIGH` - Always require approval
- `CRITICAL` - Block + force human review

---

### 4. Verification Layer

**Purpose:** Verifies directives achieved expected outcomes.

**Process:**
1. Capture pre-directive snapshot
2. Wait for directive execution
3. Capture post-directive snapshot
4. Compare KPIs (pre vs post)
5. Success if improvement detected
6. Rollback if verification fails

**Verification Criteria:**
- Target metric improved (for threshold adjustments)
- Overall success rate maintained or improved
- No unexpected degradation in other metrics

**Rollback:**
If verification fails:
1. Issue rollback directive
2. Restore previous configuration
3. Log failure to ledger
4. Notify humans

---

## Integration with Spine

### Event Subscription
```python
# Meta loop subscribes to spine events
await trigger_mesh.subscribe("*", meta_loop.capture_event)
await trigger_mesh.subscribe("decision.*", meta_loop.capture_decision)
await trigger_mesh.subscribe("recovery.*", meta_loop.capture_recovery)
```

### Directive Issuance
```python
# Meta loop issues directive to planner
await trigger_mesh.publish(TriggerEvent(
    event_type="meta.directive.adjust_threshold",
    source="meta_loop_supervisor",
    resource="directive_123",
    payload={
        "target_domain": "application",
        "target_subsystem": "planner",
        "action": "increase_playbook_confidence",
        "parameters": {"adjustment": 0.05}
    }
))

# Planner receives and executes
# (via existing event subscription in agentic_spine)
```

### Ledger Integration
```python
# All meta decisions logged immutably
await immutable_log.append(
    actor="meta_loop_supervisor",
    action="directive_issued",
    resource="directive_123",
    payload={
        "directive_type": "adjust_threshold",
        "justification": "Success rate 8% below target",
        "impact": "low"
    }
)
```

---

## Example: Improving Success Rate

### Cycle 1: Detection
```python
# Snapshot shows success rate below target
snapshot = await snapshot_builder.build_snapshot()
# global_kpis["overall_success_rate"] = 0.87  (target: 0.95)
# goal_gaps["overall_success_rate"] = 0.08

# Strategy engine triggers policy
directives = await strategy_engine.analyze_and_decide(snapshot)
# → Directive: Increase playbook confidence threshold by 5%
```

### Cycle 2: Execution
```python
# Directive submitted to pipeline
await directive_pipeline.submit_directive(directive)
# → Published to trigger mesh
# → Planner receives and executes
# → Trust core approves (low impact)
# → Threshold updated: 0.70 → 0.75
```

### Cycle 3: Verification
```python
# Verification layer checks outcome
new_snapshot = await snapshot_builder.build_snapshot()
# global_kpis["overall_success_rate"] = 0.91  ← Improved!

success = await verification_layer.verify_directive(directive, old_snapshot)
# success = True (improvement detected)
# → Directive marked as verified
# → Logged to ledger
```

### Cycle 4: Human Notification
```python
# Summary published to collaboration channels
"Meta Loop Update: Increased playbook confidence threshold from 70% to 75%. 
Success rate improved from 87% to 91% (target: 95%). 
Will continue monitoring."
```

---

## Strategic Goals

Meta loop optimizes for these system-wide goals:

| Goal | Target | Description |
|------|--------|-------------|
| Overall Success Rate | 95% | % of recovery actions that succeed |
| Mean Recovery Time | 30s | Average time to resolve incidents |
| Autonomy Rate | 80% | % of decisions made without human approval |
| Compliance Score | 95/100 | Ethics & policy compliance rating |
| Human Intervention Rate | 15% | % of times humans override |

When actual performance drifts from targets, meta loop issues corrective directives.

---

## Safety & Governance

### Multi-Layer Safety

1. **Policy-Driven** - Only acts when policies match
2. **Confidence Gating** - Minimum confidence threshold (default: 70%)
3. **Impact Assessment** - High-impact changes require approval
4. **Trust Core Review** - All directives pass through trust cores
5. **Verification** - Post-execution verification required
6. **Rollback** - Auto-rollback on verification failure
7. **Audit Trail** - Every decision logged immutably

### Approval Matrix

| Impact Level | Auto-Execute? | Human Approval? | Example |
|--------------|---------------|-----------------|---------|
| Minimal | ✅ Yes | ❌ No | Log level change |
| Low | ✅ Yes | 📢 Notify | Threshold +5% |
| Moderate | ⚠️ Conditional | ✅ Production only | Enable new playbook |
| High | ❌ No | ✅ Always | Change recovery strategy |
| Critical | 🛑 Block | ✅ Required + Review | Disable safety checks |

---

## Monitoring

### Health Metrics
- Cycle latency (how long each cycle takes)
- Directive success rate (% verified successfully)
- Rollback rate (% of directives rolled back)
- Policy match rate (% of cycles triggering policies)

### Logging
Every meta cycle logs:
- Snapshot ID and timestamp
- Global KPIs and goal gaps
- Directives issued
- Verification results
- Rollbacks (if any)

### Alerts
Meta loop alerts when:
- Multiple verification failures
- Unable to close goal gaps after 5 cycles
- Systemic patterns persist despite directives
- Compliance score drops below threshold

---

## Usage

### Starting Meta Loop
```python
from backend.grace_spine_integration import activate_grace_autonomy

# Meta loop starts automatically with spine
await activate_grace_autonomy()
# → Meta loop supervisor started
```

### Registering Custom Policy
```python
from backend.meta_loop_supervisor import meta_loop_supervisor, MetaPolicy

policy = MetaPolicy(
    policy_id="custom_policy",
    name="My Custom Policy",
    condition={"goal_gap_metric": "my_kpi", "goal_gap_threshold": 0.1},
    directive_template={
        "type": "ADJUST_THRESHOLD",
        "action": "custom_action",
        "parameters": {}
    }
)

await meta_loop_supervisor.strategy_engine.register_policy(policy)
```

### Manual Directive Approval
```python
# Approve pending high-impact directive
await meta_loop_supervisor.directive_pipeline.approve_directive(
    directive_id="directive_123",
    approved_by="ops_engineer"
)
```

---

## Files

- `backend/meta_loop_supervisor.py` - Main supervisor implementation
- `backend/grace_spine_integration.py` - Integration with spine
- `docs/META_LOOP_SUPERVISOR.md` - This documentation

---

## Summary

The Meta Loop Supervisor is GRACE's **self-optimization layer**:

✅ **Monitors** cross-domain performance continuously  
✅ **Detects** drift from strategic goals  
✅ **Decides** on systemic adjustments via policies  
✅ **Directs** spine to execute changes  
✅ **Verifies** outcomes and rolls back failures  
✅ **Learns** from meta-decisions to improve policies  
✅ **Reports** to humans with full transparency  

**GRACE now supervises her own autonomous behavior.**
