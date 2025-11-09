# Grace Verification & Rollback System

## Overview

The verification system ensures that agentic actions perform their intended effects and provides safe rollback when things go wrong. It answers the critical question: **"How do we know the action did what we wanted?"**

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Action Executor                        │
│  (Orchestrates verified execution with rollback)        │
└──────────┬──────────────────────────────────────────────┘
           │
           ├─► 1. Action Contract (Expected vs Actual)
           │
           ├─► 2. Safe-Hold Snapshot (Before execution)
           │
           ├─► 3. Execute via Self-Heal Adapter
           │
           ├─► 4. Benchmark Suite (Detect drift)
           │
           ├─► 5. Contract Verification (Compare results)
           │
           └─► 6. Rollback (If verification fails)
```

## Components

### 1. Action Contracts (`backend/action_contract.py`)

**Purpose**: Define what an action INTENDS to do before execution.

**Features**:
- Pre-execution: Captures expected state changes
- Post-execution: Verifies actual outcomes match intent
- Success criteria: Metrics/checks that must pass
- Confidence scoring: 0.0-1.0 based on how well actual matched expected

**Example**:
```python
expected_effect = ExpectedEffect(
    target_resource="service:grace_backend",
    target_state={"status": "running", "health_score": 100},
    success_criteria=[
        {"type": "metric_threshold", "metric": "error_rate", "operator": "lt", "value": 0.05},
        {"type": "health_check", "endpoint": "/health"}
    ],
    rollback_threshold=0.3
)

contract = await contract_verifier.create_contract(
    action_type="restart_service",
    expected_effect=expected_effect,
    baseline_state=current_state
)
```

### 2. Safe-Hold Snapshots (`backend/self_heal/safe_hold.py`)

**Purpose**: Atomic snapshots of system state for rollback.

**Features**:
- Database checkpoints (WAL + SHM files)
- Configuration exports
- Health baselines
- Signed manifests for integrity verification
- Golden baseline certification

**Snapshot Types**:
- `pre_action`: Before risky operations
- `golden`: Certified safe baseline (benchmark validated)
- `manual`: User-initiated snapshots

**Example**:
```python
# Take snapshot before action
snapshot = await snapshot_manager.create_snapshot(
    snapshot_type="pre_action",
    triggered_by="input_sentinel:error_123",
    notes="Before database migration"
)

# Restore if needed
result = await snapshot_manager.restore_snapshot(
    snapshot_id=snapshot.id,
    dry_run=False  # Set True to validate without restoring
)
```

### 3. Benchmark Suite (`backend/benchmarks/benchmark_suite.py`)

**Purpose**: Detect performance/stability regressions after actions.

**Test Types**:

**Smoke Tests** (fast, run after every action):
- Database connectivity
- API health
- Reflection service
- Task execution

**Regression Suite** (comprehensive, run after major changes):
- All smoke tests
- Query performance
- Concurrent task handling
- Memory usage
- Trigger mesh functionality
- Immutable log writes

**Golden Baselines**:
```python
# Run regression suite
result = await benchmark_suite.run_regression_suite(
    triggered_by="post_action:contract_123",
    compare_to_baseline=True
)

# If passed and stable, mark as golden
if result['passed'] and result['drift_detected'] == False:
    await benchmark_suite.set_golden_baseline(result['run_id'])
```

**Drift Detection**:
- Compares current metrics to golden baseline
- Flags if any metric changes by >20% (configurable)
- Triggers rollback recommendation

### 4. Progression Tracker (`backend/progression_tracker.py`)

**Purpose**: Track Grace's journey through missions - where she came from, where she is, how far to go.

**Mission Timeline**:
```python
# Start a mission
timeline = await progression_tracker.start_mission(
    mission_name="Database Migration",
    mission_goal="Migrate to WAL mode without downtime",
    planned_actions=5,
    initial_snapshot_id=snapshot.id
)

# Record action completion
await progression_tracker.record_action_completed(
    mission_id=timeline.mission_id,
    action_contract_id=contract.id,
    success=True,
    new_safe_point_id=new_snapshot.id
)

# Get current status
status = await progression_tracker.get_current_status()
# Returns:
# {
#   "progress_percent": 60.0,
#   "completed_actions": 3,
#   "total_actions": 5,
#   "confidence_score": 0.85,
#   "last_safe_point": "snapshot-20251107-...",
#   "can_rollback": True,
#   "rollback_points_available": 3
# }
```

### 5. Action Executor (`backend/action_executor.py`)

**Purpose**: Orchestrates verified execution with full rollback capability.

**Execution Flow**:
```python
result = await action_executor.execute_verified_action(
    action_type="restart_service",
    playbook_id="restart_service",
    run_id=123,
    expected_effect=expected_effect,
    baseline_state=current_state,
    tier="tier_2",  # tier_1, tier_2, or tier_3
    triggered_by="input_sentinel:error_456",
    mission_id="mission-..."
)

# Returns:
# {
#   "success": True,
#   "contract_id": "contract-abc123",
#   "snapshot_id": "snapshot-20251107-...",
#   "verification": {
#     "confidence": 0.95,
#     "passed_checks": [...],
#     "failed_checks": []
#   },
#   "benchmark": {
#     "passed": True,
#     "drift_detected": False
#   },
#   "rolled_back": False
# }
```

## Integration Points

### InputSentinel Integration

Update `backend/input_sentinel.py` to use verified execution:

```python
from .action_executor import action_executor
from .action_contract import ExpectedEffect

async def _run_playbook_action(self, action: str, error_id: str) -> Dict:
    # Define expected effect
    expected_effect = ExpectedEffect(
        target_resource="grace_backend",
        target_state={"action": action, "status": "completed"},
        success_criteria=[
            {"type": "metric_threshold", "metric": "error_rate", "operator": "lt", "value": 0.05}
        ]
    )
    
    # Execute with verification
    result = await action_executor.execute_verified_action(
        action_type=action,
        playbook_id=playbook_code,
        run_id=run_id,
        expected_effect=expected_effect,
        baseline_state={"parameters": params},
        tier="tier_1",
        triggered_by=f"input_sentinel:{error_id}"
    )
    
    return result
```

## API Endpoints

All endpoints available at `/api/verification/*`:

**Contracts**:
- `GET /api/verification/contracts` - List contracts
- `GET /api/verification/contracts/{contract_id}` - Contract details

**Snapshots**:
- `GET /api/verification/snapshots` - List snapshots
- `GET /api/verification/snapshots/{snapshot_id}` - Snapshot details
- `POST /api/verification/snapshots/{snapshot_id}/restore` - Restore snapshot
- `GET /api/verification/snapshots/golden/latest` - Get latest golden baseline

**Benchmarks**:
- `POST /api/verification/benchmarks/smoke` - Run smoke tests
- `POST /api/verification/benchmarks/regression` - Run full regression
- `GET /api/verification/benchmarks` - List benchmark runs
- `GET /api/verification/benchmarks/{run_id}` - Benchmark details
- `POST /api/verification/benchmarks/{run_id}/set_golden` - Mark as golden

**Missions**:
- `POST /api/verification/missions` - Start mission
- `GET /api/verification/missions/current` - Current mission status
- `GET /api/verification/missions/{mission_id}` - Mission details
- `POST /api/verification/missions/{mission_id}/complete` - Complete mission
- `GET /api/verification/missions/history` - Mission history

**Status**:
- `GET /api/verification/status` - Overall verification status

## UI Integration

The verification system exposes all data needed for a comprehensive UI:

### Mission Dashboard
Shows Grace's current mission:
- Progress bar (0-100%)
- Completed vs total actions
- Confidence score
- Last safe point timestamp
- Rollback capability indicator

### Action Contract Viewer
Lists all contracts with:
- Expected vs actual outcomes
- Verification confidence scores
- Pass/fail status
- Rollback recommendations

### Snapshot Timeline
Visual timeline of snapshots:
- Pre-action snapshots
- Golden baselines
- Restore points
- Health scores at snapshot time

### Benchmark Trends
Charts showing:
- Metric trends over time
- Drift detection alerts
- Comparison to golden baseline
- Performance regressions

## Database Schema

### ActionContract Table
```sql
CREATE TABLE action_contracts (
    id TEXT PRIMARY KEY,
    action_type TEXT NOT NULL,
    playbook_id TEXT,
    run_id INTEGER,
    expected_effect_hash TEXT NOT NULL,
    expected_effect JSON NOT NULL,
    baseline_state JSON NOT NULL,
    status TEXT DEFAULT 'pending',
    actual_effect JSON,
    verification_result JSON,
    confidence_score REAL,
    created_at TIMESTAMP NOT NULL,
    executed_at TIMESTAMP,
    verified_at TIMESTAMP,
    safe_hold_snapshot_id TEXT,
    triggered_by TEXT,
    tier TEXT,
    requires_approval BOOLEAN DEFAULT 0
);
```

### SafeHoldSnapshot Table
```sql
CREATE TABLE safe_hold_snapshots (
    id TEXT PRIMARY KEY,
    snapshot_type TEXT NOT NULL,
    triggered_by TEXT,
    action_contract_id TEXT,
    playbook_run_id INTEGER,
    manifest JSON NOT NULL,
    manifest_hash TEXT NOT NULL,
    storage_uri TEXT,
    baseline_metrics JSON,
    system_health_score INTEGER,
    status TEXT DEFAULT 'active',
    is_golden BOOLEAN DEFAULT 0,
    is_validated BOOLEAN DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    validated_at TIMESTAMP,
    restored_at TIMESTAMP,
    notes TEXT
);
```

### BenchmarkRun Table
```sql
CREATE TABLE benchmark_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT UNIQUE NOT NULL,
    triggered_by TEXT,
    benchmark_type TEXT NOT NULL,
    results JSON NOT NULL,
    metrics JSON NOT NULL,
    passed BOOLEAN NOT NULL,
    baseline_id TEXT,
    delta_from_baseline JSON,
    drift_detected BOOLEAN DEFAULT 0,
    duration_seconds REAL NOT NULL,
    created_at TIMESTAMP NOT NULL,
    is_golden BOOLEAN DEFAULT 0
);
```

### MissionTimeline Table
```sql
CREATE TABLE mission_timelines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id TEXT UNIQUE NOT NULL,
    mission_name TEXT NOT NULL,
    mission_goal TEXT,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    initial_snapshot_id TEXT,
    current_safe_point_id TEXT,
    current_state_hash TEXT,
    current_health_score INTEGER,
    total_planned_actions INTEGER DEFAULT 0,
    completed_actions INTEGER DEFAULT 0,
    failed_actions INTEGER DEFAULT 0,
    rolled_back_actions INTEGER DEFAULT 0,
    progress_ratio REAL DEFAULT 0.0,
    confidence_score REAL DEFAULT 1.0,
    status TEXT DEFAULT 'in_progress',
    can_rollback BOOLEAN DEFAULT 1,
    rollback_available_count INTEGER DEFAULT 0,
    metadata JSON
);
```

## Example Workflow

### Complete Verified Action Flow

```python
# 1. Start mission
mission = await progression_tracker.start_mission(
    mission_name="Fix Database Lock Issue",
    planned_actions=3
)

# 2. Take initial snapshot
snapshot = await snapshot_manager.create_snapshot(
    snapshot_type="pre_action",
    notes="Before lock fix"
)

# 3. Update mission with snapshot
# (handled automatically by action_executor)

# 4. Execute action with verification
result = await action_executor.execute_verified_action(
    action_type="restart_service",
    playbook_id="restart_service",
    expected_effect=ExpectedEffect(...),
    baseline_state=current_state,
    tier="tier_2",
    mission_id=mission.mission_id
)

# 5. Check result
if result['success']:
    print(f"✅ Action succeeded (confidence: {result['confidence']})")
    if result['snapshot_id']:
        print(f"📸 Snapshot available: {result['snapshot_id']}")
else:
    print(f"❌ Action failed")
    if result['rolled_back']:
        print(f"🔙 Rolled back to: {result['snapshot_id']}")

# 6. Complete mission
await progression_tracker.complete_mission(
    mission_id=mission.mission_id,
    success=result['success']
)
```

## Next Steps

1. **Database Migration**: Add new tables to Alembic migrations
2. **InputSentinel Integration**: Update `_run_playbook_action` to use `action_executor`
3. **UI Development**: Build dashboards for contracts, snapshots, benchmarks, missions
4. **Testing**: Add integration tests for verification flows
5. **Observability**: Integrate with existing observability endpoints
6. **Documentation**: User guide for interpreting verification results

## Benefits

✅ **Trust**: Know that actions did what they intended  
✅ **Safety**: Automatic rollback when verification fails  
✅ **Visibility**: Track progression and confidence  
✅ **Auditability**: Complete immutable log of all actions  
✅ **Recovery**: One-click restore to last known-good state  
✅ **Confidence**: Benchmark-validated golden baselines  
✅ **Learning**: Historical data for improving autonomy
