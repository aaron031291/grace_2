# Librarian as Data Orchestrator - Integration Guide

## Overview

The Librarian Kernel is now a separate **Data Orchestrator** component that sits alongside other kernels in the orchestrator's stage list. This clean architecture keeps the boot flow stable while giving Librarian full orchestration power over memory, intake, schemas, and sub-agents.

---

## Architecture: Librarian in the Orchestrator

```
┌─────────────────────────────────────────────────────────┐
│              Grace Orchestrator                         │
│                                                          │
│  Stage List:                                            │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 1. Core Services                                │   │
│  │ 2. Clarity Event Mesh                           │   │
│  │ 3. Unified Logic Hub                            │   │
│  │ 4. Memory Tables Registry                       │   │
│  │ 5. Librarian Data Orchestrator ← NEW           │   │
│  │ 6. ML/DL Federation                             │   │
│  │ 7. Self-Healing Engine                          │   │
│  │ 8. Verification Suite                           │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Integration Points

### 1. Clarity Framework Integration

The Librarian implements **clarity contracts** through `LibrarianClarityAdapter`:

#### BaseComponent Registration
```python
# Registers in GraceComponentManifest
manifest_entry = {
    'component_id': 'librarian_data_orchestrator',
    'component_type': 'data_orchestrator',
    'name': 'Librarian',
    'trust_score': 1.0,
    'health': {...},
    'capabilities': [...]
}
```

#### Event Mesh Integration
**Publishes**:
- `librarian.schema_proposal`
- `librarian.ingestion_launch`
- `librarian.trust_update`
- `librarian.agent_spawn/terminate`
- `librarian.ml_run_trigger`
- `librarian.verification_run`

**Subscribes To**:
- `governance.decision` - Handles approval/rejection
- `alert.triggered` - Triggers trust audits
- `verification.completed` - Pauses on failures
- `self_healing.playbook_executed` - Logs results

#### GraceLoopOutput Storage
Every action creates auditable `GraceLoopOutput` entries:
```python
{
    'component_id': 'librarian_data_orchestrator',
    'action_type': 'schema_proposal',
    'inputs': {...},
    'reasoning': "File detected as dataset...",
    'outputs': {...},
    'confidence': 0.9
}
```

---

### 2. Unified Logic Hub Integration

All governance flows through Unified Logic:

```python
# Submit for approval
decision = await adapter.submit_to_governance(
    update_type='schema_proposal',
    data={'table_name': 'memory_documents', ...},
    risk_level='low',
    context='New PDF file uploaded'
)

# Auto-approve if confidence >= 0.8
if decision['approved']:
    # Execute
    await execute_schema(data)
else:
    # Queue for human review
    await queue_for_review(decision)
```

**Decision Logging**:
```python
# Every decision logged to memory_governance_decisions
{
    'component_id': 'librarian_data_orchestrator',
    'update_type': 'schema_proposal',
    'decision': 'approved',
    'auto_approved': True,
    'reason': 'Confidence 0.9 exceeds threshold'
}
```

---

### 3. Orchestrator Stage Registration

The Librarian registers as an orchestrator stage with full lifecycle management:

```python
from backend.kernels.orchestrator_integration import register_librarian_in_orchestrator

# In orchestrator setup (e.g., serve.py or boot sequence)
await register_librarian_in_orchestrator(
    orchestrator,
    registry=table_registry,
    event_mesh=clarity_event_mesh,
    unified_logic=unified_logic_hub
)
```

**Stage Configuration**:
```python
{
    'stage_id': 'data_orchestrator',
    'auto_start': True,
    'critical': False,  # System can run without it
    'health_check_interval': 30,
    'restart_on_failure': True,
    'max_restart_attempts': 3
}
```

**Lifecycle Methods**:
- `initialize()` - Setup and kernel start
- `start()` - Start orchestration
- `stop()` - Graceful shutdown
- `pause()` / `resume()` - Temporary suspension
- `health_check()` - Heartbeat monitoring
- `restart()` - Auto-recovery on failure

---

## Subsystem Contracts

### Memory Tables
**Reads**:
- `memory_documents` - Files needing ingestion
- `memory_trusted_sources` - Whitelist validation
- `memory_discovery_targets` - External sources to monitor

**Writes**:
- `memory_librarian_log` - All actions
- `memory_schema_proposals` - Inferred schemas
- `memory_insights` - Flashcards/summaries
- `memory_execution_logs` - Agent activity

**Updates**:
- Ingestion status (`pending` → `completed`)
- Trust scores after audits
- Quality metrics after ingestion

---

### Ingestion Pipelines

**Launches**:
```python
await kernel.queue_ingestion(
    file_path='/path/to/file.pdf',
    metadata={
        'source_id': 'uuid',
        'trust_score': 0.9,
        'domains': ['finance']
    }
)
```

**Monitors**:
- Chunk processing progress
- Embedding generation status
- Memory Fusion sync

**Retries**:
- Failed chunks
- Timeout handling
- Malware scan failures

---

### ML/DL Federation

**Triggers**:
```python
# After large dataset ingestion
if dataset_size >= threshold:
    await trigger_ml_run({
        'run_type': 'fine_tune',
        'dataset_id': 'uuid',
        'model': 'grace-embeddings-v2'
    })
```

**Logs**:
```python
# To memory_model_training_logs
{
    'run_id': 'uuid',
    'triggered_by': 'librarian_data_orchestrator',
    'dataset_size': 1000000,
    'hyperparameters': {...},
    'status': 'queued'
}
```

---

### Self-Healing & Automation

**Spawns**:
```python
# On ingestion failure
if ingestion_failed:
    await spawn_self_healing_agent({
        'playbook': 'ingestion_retry',
        'target': file_path,
        'max_attempts': 3
    })
```

**Maintains**:
- `memory_self_healing_playbooks`
- `automation/rules` - Future failure patterns

---

### Verification Suite

**Runs**:
```python
# After ingestion or model update
await trigger_verification({
    'suite_type': 'bias_check',
    'target': 'ingested_dataset_uuid',
    'tests': ['contradiction', 'freshness', 'bias']
})
```

**Reacts**:
```python
# If verification fails
if verification.status == 'failed':
    await pause_ingestion()
    await emit_event('verification.failed', {...})
```

---

### Immutable Log & Trust Engine

**Records**:
- Every schema change
- Every ingestion action
- Every trust adjustment
- Every governance decision

**Computes**:
```python
# Periodic trust reports
await compute_trust_reports({
    'sources': all_active_sources,
    'metrics': ['success_rate', 'freshness', 'contradictions'],
    'output': 'memory_trust_reports'
})
```

---

## Dashboard Integration

### Orchestrator Dashboard

Shows Librarian alongside other stages:

```typescript
{
  stage_id: 'data_orchestrator',
  stage_name: 'Librarian Data Orchestrator',
  status: 'running',
  health: 'healthy',
  trust_score: 1.0,
  active_agents: 3,
  queue_depths: {
    schema_queue: 5,
    ingestion_queue: 12,
    trust_audit_queue: 0
  }
}
```

### LibrarianPanel Tab

Add to Memory Studio:
```typescript
<Tab label="Data Orchestrator">
  <LibrarianPanel />
</Tab>
```

Shows:
- Kernel status & controls
- Work queue depths
- Active sub-agents
- Recent actions (from memory_librarian_log)
- Trust metrics

---

## Boot Sequence Integration

### Option 1: Automatic Start

Add to `serve.py` or main boot script:

```python
from backend.kernels.orchestrator_integration import register_librarian_in_orchestrator

@app.on_event("startup")
async def startup_event():
    # ... existing orchestrator setup ...
    
    # Register Librarian
    librarian_stage = await register_librarian_in_orchestrator(
        orchestrator=grace_orchestrator,
        registry=table_registry,
        event_mesh=clarity_event_mesh,
        unified_logic=unified_logic_hub
    )
    
    # Auto-start if configured
    if librarian_stage.config['auto_start']:
        await librarian_stage.initialize()
    
    logger.info("✅ Librarian Data Orchestrator registered")
```

### Option 2: Manual Control

Control via orchestrator API:

```bash
# Start Data Orchestrator stage
curl -X POST /api/orchestrator/stages/data_orchestrator/start

# Check health
curl /api/orchestrator/stages/data_orchestrator/health

# Pause
curl -X POST /api/orchestrator/stages/data_orchestrator/pause
```

---

## Testing Integration

### 1. Verify Registration

```python
# Check orchestrator stages
stages = orchestrator.get_stages()
assert 'data_orchestrator' in [s.stage_id for s in stages]

# Check manifest
manifest = table_registry.query_rows(
    'grace_component_manifest',
    filters={'component_id': 'librarian_data_orchestrator'}
)
assert len(manifest) == 1
```

### 2. Test Governance Flow

```python
# Submit schema proposal
decision = await adapter.submit_to_governance(
    update_type='schema_proposal',
    data={'table_name': 'test_table', ...},
    risk_level='low'
)

# Verify auto-approval
assert decision['approved'] == True
assert decision['auto_approved'] == True

# Check log
logs = table_registry.query_rows(
    'memory_librarian_log',
    filters={'action_type': 'governance_request'}
)
assert len(logs) > 0
```

### 3. Test Event Integration

```python
# Subscribe to event
received_events = []

async def handler(event):
    received_events.append(event)

event_mesh.subscribe('librarian.schema_proposal', handler)

# Trigger action
await adapter.log_action(
    action_type='schema_proposal',
    action_detail='Test proposal'
)

# Verify emission
await asyncio.sleep(0.1)
assert len(received_events) == 1
```

### 4. Test Health Monitoring

```python
# Get health status
health = await librarian_stage.health_check()

assert health['healthy'] == True
assert health['status'] == 'running'
assert 'active_agents' in health['details']
```

---

## Configuration

### Environment Variables

```bash
# Librarian config
LIBRARIAN_AUTO_START=true
LIBRARIAN_MAX_AGENTS=5
LIBRARIAN_AUTO_APPROVE_THRESHOLD=0.8

# Orchestrator integration
ORCHESTRATOR_ENABLE_LIBRARIAN=true
ORCHESTRATOR_HEALTH_CHECK_INTERVAL=30
```

### Runtime Configuration

```python
# In orchestrator setup
librarian_stage.config.update({
    'max_concurrent_agents': 10,
    'health_check_interval': 15,
    'restart_on_failure': True
})
```

---

## Benefits of This Architecture

### ✅ Clean Separation
- Librarian is **self-contained** as a stage
- Doesn't interfere with existing boot flow
- Can be disabled/enabled independently

### ✅ Full Integration
- **Governance** through Unified Logic
- **Events** via clarity mesh
- **Monitoring** in orchestrator dashboard
- **Trust** in clarity framework

### ✅ Stability
- Isolated failures (non-critical stage)
- Auto-restart on errors
- Health monitoring
- Graceful degradation

### ✅ Observability
- All actions logged to `memory_librarian_log`
- Events emitted to clarity mesh
- GraceLoopOutput for audit trail
- Dashboard visibility

---

## Files Created

1. `config/policies/memory_librarian_log.yaml` - Action log schema
2. `backend/kernels/librarian_clarity_adapter.py` - Clarity integration
3. `backend/kernels/orchestrator_integration.py` - Stage registration
4. `LIBRARIAN_ORCHESTRATOR_INTEGRATION.md` - This guide

---

## Next Steps

1. **Run Schema Loader**: `python backend/memory_tables/schema_loader.py`
2. **Register in Orchestrator**: Add registration call to boot sequence
3. **Test Registration**: Verify stage appears in orchestrator
4. **Start Librarian**: Auto-start or manual via API
5. **Monitor Dashboard**: Check health and activity
6. **Test Workflows**: Upload file → schema → ingestion → verify logs

---

## Example: Complete Boot Integration

```python
# In serve.py

from backend.kernels.orchestrator_integration import register_librarian_in_orchestrator
from backend.orchestrator import GraceOrchestrator
from backend.clarity.event_mesh import ClarityEventMesh
from backend.unified_logic.hub import UnifiedLogicHub
from backend.memory_tables.registry import table_registry

# Create orchestrator
orchestrator = GraceOrchestrator()

# Create subsystems
event_mesh = ClarityEventMesh(registry=table_registry)
unified_logic = UnifiedLogicHub(registry=table_registry)

# Register stages
await orchestrator.add_stage(CoreServicesStage())
await orchestrator.add_stage(ClarityEventMeshStage(event_mesh))
await orchestrator.add_stage(UnifiedLogicStage(unified_logic))
await orchestrator.add_stage(MemoryTablesStage(table_registry))

# Register Librarian
librarian = await register_librarian_in_orchestrator(
    orchestrator,
    registry=table_registry,
    event_mesh=event_mesh,
    unified_logic=unified_logic
)

# Start orchestrator (starts all auto_start stages)
await orchestrator.start_all()

logger.info("✅ Grace Orchestrator running with Librarian Data Orchestrator")
```

---

**Status**: ✅ Librarian ready for orchestrator integration!
