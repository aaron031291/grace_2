# Unified Logic Hub

**One secure, observable path for all Grace logic updates**

## Overview

The Unified Logic Hub is Grace's central orchestrator for managing all system changes—schema revisions, code modules, playbooks, configs, and metric definitions. Every update flows through a single pipeline that ensures:

- **Governance compliance** via constitutional checks
- **Cryptographic auditability** via Lightning signatures
- **Validation** via sandbox testing and schema analysis
- **Safe distribution** via trigger mesh events
- **Rollback capability** with automated recovery
- **Complete traceability** via immutable logs

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     UNIFIED LOGIC HUB                            │
│                                                                   │
│  1. Ingestion Gate                                              │
│     ↓ Governance Check (constitutional approval)                │
│     ↓ Crypto Assignment (Lightning signature)                   │
│     ↓ Immutable Log (proposal recorded)                         │
│                                                                   │
│  2. Validation & Rollback Prep                                  │
│     ↓ Schema Diff Analysis (breaking change detection)          │
│     ↓ Sandbox Testing (lint, unit tests)                        │
│     ↓ Rollback Snapshot (revert instructions)                   │
│                                                                   │
│  3. Distribution Orchestrator                                   │
│     ↓ Package Build (signed, checksummed)                       │
│     ↓ Trigger Mesh Event (unified_logic.update)                 │
│     ↓ Immutable Log (distribution complete)                     │
│                                                                   │
│  4. Feedback & Learning                                         │
│     ↓ Watchdog Monitoring (regression detection)                │
│     ↓ Healing Analytics (outcome tracking)                      │
│     ↓ Learning Loop (pattern improvement)                       │
└─────────────────────────────────────────────────────────────────┘

               ↓ Downstream Consumers ↓

    AgenticMemory  Fusion  Lightning  Self-Heal  Metrics
```

## Pipeline Stages

### Stage 1: Governance Check
- Calls `governance_engine.check_action()` with update metadata
- Blocks if constitutional principles violated
- Records approval ID for audit trail

### Stage 2: Crypto Assignment
- Generates Lightning cryptographic identity via `crypto_engine`
- Creates tamper-proof signature for the update
- Links to constitutional validation

### Stage 3: Immutable Log (Proposal)
- Records `logic_update_proposed` in append-only log
- Includes governance approval, crypto signature, update metadata
- Provides audit trail sequence number

### Stage 4: Validation
- **Schema updates**: Breaking change detection via `schema_evolution`
- **Code modules**: Sandbox execution (lint, compile, unit tests)
- **Playbooks**: Structure validation against executor schema
- Captures diagnostics for any failures

### Stage 5: Package Build
- Generates SHA3-256 checksum of update content
- Creates rollback instructions (previous version, revert steps)
- Bundles all metadata into signed package

### Stage 6: Distribution
- Publishes `TriggerEvent(event_type="unified_logic.update")` to mesh
- Contains: update_id, version, checksum, crypto_signature, package_url
- All subscribers (AgenticMemory, Fusion, Lightning, etc.) react

### Stage 7: Immutable Log (Completion)
- Records `logic_update_distributed` with final status
- Links to trigger mesh event ID for full traceability

### Stage 8: Watchdog Setup
- Registers update with `anomaly_watchdog` for regression monitoring
- Tracks metrics tied to this update_id
- Auto-triggers rollback if downstream failures detected

## Update Types

### 1. Schema Updates
```python
from backend.unified_logic_hub import submit_schema_update

update_id = await submit_schema_update(
    endpoint="/api/memory/store",
    current_schema={...},
    proposed_schema={...},
    created_by="schema_evolution",
    risk_level="medium"
)
```

**Flow:**
- Breaking change detection
- API route schema refresh
- AgenticMemory schema cache reload

### 2. Code Module Updates
```python
from backend.unified_logic_hub import submit_code_module_update

update_id = await submit_code_module_update(
    modules={
        "backend/new_feature.py": code_content,
        "backend/helper.py": helper_code
    },
    component_targets=["agentic_spine", "ml_pipeline"],
    created_by="autonomous_improver",
    risk_level="high"
)
```

**Flow:**
- Sandbox lint/compile checks
- Hot-reload of affected components
- Watchdog monitoring for regressions

### 3. Playbook Updates
```python
from backend.unified_logic_hub import submit_playbook_update

update_id = await submit_playbook_update(
    playbook_name="database_connection_fix",
    playbook_content={
        "steps": [...],
        "rollback_steps": [...],
        "triggers": [...]
    },
    component_targets=["self_heal_scheduler", "playbook_executor"],
    created_by="self_heal",
    risk_level="medium"
)
```

**Flow:**
- Playbook schema validation
- Distribution to self-heal components
- Integration with causal graph

### 4. Config Updates
```python
from backend.unified_logic_hub import unified_logic_hub

update_id = await unified_logic_hub.submit_update(
    update_type="config",
    component_targets=["metrics_collector", "data_cube"],
    content={
        "config_changes": {
            "aggregation_interval": 60,
            "retention_days": 90
        }
    },
    created_by="performance_optimizer",
    risk_level="low"
)
```

### 5. Metric Definition Updates
```python
update_id = await unified_logic_hub.submit_update(
    update_type="metric_definition",
    component_targets=["metrics_catalog", "lightning_diagnostics"],
    content={
        "metric_definitions": [
            {
                "name": "fusion_query_latency_p99",
                "type": "histogram",
                "unit": "milliseconds",
                "aggregation": "percentile"
            }
        ]
    },
    created_by="proactive_intelligence",
    risk_level="low"
)
```

## API Routes

### Submit Updates
```bash
# Schema update
POST /api/logic-hub/updates/schema
{
  "endpoint": "/api/memory/store",
  "current_schema": {...},
  "proposed_schema": {...},
  "created_by": "api_user",
  "risk_level": "medium"
}

# Code module update
POST /api/logic-hub/updates/code-module
{
  "modules": {
    "path/to/module.py": "code content"
  },
  "component_targets": ["agentic_spine"],
  "created_by": "developer",
  "risk_level": "high"
}

# Playbook update
POST /api/logic-hub/updates/playbook
{
  "playbook_name": "memory_leak_fix",
  "playbook_content": {...},
  "component_targets": ["self_heal_scheduler"],
  "created_by": "self_heal",
  "risk_level": "medium"
}

# Generic update (any type)
POST /api/logic-hub/updates/generic
{
  "update_type": "config",
  "component_targets": ["metrics_collector"],
  "content": {...},
  "created_by": "api_user",
  "risk_level": "low"
}
```

### Track Updates
```bash
# Get update status
GET /api/logic-hub/updates/{update_id}

# List recent updates
GET /api/logic-hub/updates?limit=20

# Get hub statistics
GET /api/logic-hub/stats
```

### Rollback
```bash
# Trigger manual rollback
POST /api/logic-hub/updates/{update_id}/rollback
```

## Downstream Consumers

### AgenticMemory
Subscribes to `unified_logic.update` events:
- Reloads memory schema definitions
- Clears caches for affected memory domains
- Updates vector embedding configs

### Fusion/Lightning
Subscribes to `unified_logic.update` events:
- Refreshes memory pipeline configs
- Reloads query optimization rules
- Updates metric collection points

### Self-Heal
Subscribes to `unified_logic.update` events:
- Reloads playbooks from registry
- Updates healing strategies
- Refreshes causal graph nodes

### Metrics Collector
Subscribes to `unified_logic.update` events:
- Reloads metric definitions from catalog
- Updates aggregation rules
- Refreshes DataCube schemas

### Watchdog
Subscribes to `unified_logic.update` events:
- Registers new update for monitoring
- Tracks metrics tied to update_id
- Escalates anomalies linked to update

## Rollback Flow

When an update fails or causes regressions:

1. **Detection**
   - Watchdog detects anomaly tied to update_id
   - Manual rollback triggered via API
   - Self-healing detects persistent failures

2. **Rollback Execution**
   - Retrieves rollback instructions from package
   - Creates rollback update package
   - Publishes `unified_logic.rollback` event

3. **Distribution**
   - All affected components revert to previous version
   - Immutable log records rollback
   - Metrics tagged with rollback_id

4. **Learning**
   - Rollback reason fed to learning loop
   - Failure patterns added to causal graph
   - Governance policies updated

## Observability

### Immutable Log Queries
```python
from backend.immutable_log import immutable_log

# Get all updates from unified logic hub
entries = await immutable_log.get_entries(
    subsystem="unified_logic_hub",
    limit=100
)

# Verify integrity of update trail
integrity = await immutable_log.verify_integrity()
```

### Trigger Mesh Events
```python
from backend.trigger_mesh import trigger_mesh

# Subscribe to all logic updates
async def on_logic_update(event):
    print(f"Logic update: {event.payload['update_id']}")

trigger_mesh.subscribe("unified_logic.*", on_logic_update)
```

### Crypto Tracing
```python
from backend.crypto_assignment_engine import crypto_engine

# Trace update by crypto_id
trace = await crypto_engine.trace_entity_real_time(crypto_id)
```

## Security

### Governance Integration
- Every update requires constitutional approval
- High-risk updates require Parliament review
- Blocked updates logged for audit

### Cryptographic Signatures
- All updates signed with Lightning crypto
- Tamper detection via checksum validation
- Constitutional validation recorded

### Audit Trail
- Complete update history in immutable log
- Cryptographic chain prevents tampering
- Replay capability for compliance

## Performance

### Sub-millisecond Crypto
- Crypto assignment: <0.1ms target
- Signature validation: <1ms target
- Lightning-fast entity tracing

### Async Pipeline
- Non-blocking update submission
- Parallel validation stages where safe
- Background distribution to consumers

### Metrics
- Track success rate, rollback rate
- Monitor pipeline stage durations
- Alert on validation failures

## Integration Points

### Existing Components Used
- `governance.py` - Constitutional approval
- `crypto_assignment_engine.py` - Lightning signatures
- `immutable_log.py` - Audit trail
- `trigger_mesh.py` - Event distribution
- `sandbox_manager.py` - Code validation
- `schema_evolution.py` - Breaking change detection
- `anomaly_watchdog.py` - Regression monitoring
- `learning_loop.py` - Outcome learning

### New Components
- `unified_logic_hub.py` - Central orchestrator
- `routes/unified_logic_hub_api.py` - HTTP API
- `base_models.LogicUpdateRecord` - Persistent registry

## Example: End-to-End Update

```python
# 1. Schema evolution detects need for improvement
from backend.schema_evolution import schema_evolution

# 2. Propose schema change
from backend.unified_logic_hub import submit_schema_update

update_id = await submit_schema_update(
    endpoint="/api/memory/store",
    current_schema=current,
    proposed_schema=improved,
    created_by="schema_evolution",
    risk_level="medium"
)

# 3. Hub processes through pipeline
# - Governance checks ✓
# - Crypto signs ✓
# - Logs proposal ✓
# - Validates schema ✓
# - Builds package ✓
# - Distributes via trigger mesh ✓
# - Logs completion ✓
# - Starts watchdog ✓

# 4. AgenticMemory receives event and reloads
# 5. Watchdog monitors for 24 hours
# 6. Learning loop captures outcome

# Track progress
status = await unified_logic_hub.get_update_status(update_id)
print(f"Status: {status['status']}")
print(f"Validation: {status['validation_results']}")
```

## Future Enhancements

- [ ] A/B testing framework for updates
- [ ] Canary deployments (gradual rollout)
- [ ] Automated rollback triggers
- [ ] Machine learning-based validation
- [ ] Cross-instance update synchronization
- [ ] Real-time update dashboard
- [ ] Update approval workflow UI

## Summary

The Unified Logic Hub provides:

✅ **Single source of truth** for all logic updates  
✅ **Governance-first** approach ensuring constitutional compliance  
✅ **Cryptographic auditability** with Lightning signatures  
✅ **Safe validation** via sandbox and schema analysis  
✅ **Observable distribution** via trigger mesh events  
✅ **Automatic rollback** capability with recovery instructions  
✅ **Complete traceability** through immutable logs  
✅ **Learning integration** for continuous improvement  

**Result:** Grace evolves quickly without losing traceability or stability.
