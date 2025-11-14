### Self-Healing → Coding Agent Integration - COMPLETE ✅

## 🎯 System Overview

Successfully implemented a **complete self-healing to coding agent workflow** that automatically:
1. Detects errors via log watchers
2. Triggers appropriate playbooks
3. Escalates to coding agent when code patches are needed
4. Tracks work orders and synchronizes status
5. Resumes self-healing after patches applied
6. Updates trust and notifies users

## 🔄 Complete Workflow

```
Error Detected (Log Watcher/Event)
    ↓
Event Bus Publishes (ingestion.failed, schema.invalid, etc.)
    ↓
Self-Healing Kernel Receives Event
    ↓
Selects Appropriate Playbook
    ↓
┌──────────────┐
│ Playbook Type│
└──────────────┘
    ├─→ Data Fix → Execute Steps → Verify → Trust Restored ✓
    ├─→ Cache Clear → Clear Memory → Verify → Trust Restored ✓
    ├─→ Retry → Backoff → Retry → Verify → Trust Restored ✓
    └─→ Code Patch Required
            ↓
        Escalate to Coding Agent
            ↓
        Create Work Order
            ↓
        Coding Agent Analyzes
            ↓
        Generate Patch
            ↓
        Run Tests
            ↓
        Apply Patch
            ↓
        Notify Self-Healing: Patch Complete
            ↓
        Resume Playbook
            ↓
        Rerun Pipeline/Verification
            ↓
        Update Trust Score
            ↓
        Trust Restored ✓
```

## 📋 Playbook Types

### 1. **Data Fix** (No code changes)
- Schema corrections
- Configuration updates
- Data migrations

**Example:** `schema_recovery`
```python
Steps:
  1. Validate current schema
  2. Backup schema
  3. Apply fix
  4. Verify integrity
```

### 2. **Cache Clear** (Memory/cache operations)
- Clear caches
- Free memory
- Stop low-priority tasks

**Example:** `memory_cleanup`
```python
Steps:
  1. Identify large caches
  2. Clear non-critical caches
  3. Stop background tasks
  4. Verify memory freed
```

### 3. **Retry** (Simple retry logic)
- Exponential backoff
- Connection retry
- Pipeline retry

**Example:** `database_reconnect`
```python
Steps:
  1. Close stale connections
  2. Exponential backoff
  3. Reconnect
  4. Verify connection
```

### 4. **Code Patch** (Requires coding agent)
- Validation logic fixes
- Performance optimizations
- Bug fixes

**Example:** `verification_fix`
```python
Steps:
  1. Analyze failure reason
  2. Check if data vs logic issue
  3. **Escalate to coding agent**
     └─→ Creates work order
     └─→ Waits for patch
     └─→ Resumes after completion
```

### 5. **Hybrid** (May need code patch)
- Analyzes root cause first
- Conditionally escalates

**Example:** `pipeline_timeout_fix`
```python
Steps:
  1. Analyze timeout cause
  2. Check if code issue
  3. If code → escalate to coding agent
  4. If config → increase timeout
```

## 🔧 API Endpoints

### Patches API (/patches)

#### List Work Orders
```bash
GET /patches/work-orders?status=queued&limit=20
```

Response:
```json
{
  "work_orders": [
    {
      "work_order_id": "wo_20251113_0001",
      "type": "self_healing_patch",
      "description": "Code patch required for: pipeline_timeout",
      "status": "queued",
      "self_healing_run_id": "run_20251113_163334",
      "estimated_complexity": "medium",
      "created_at": "2025-11-13T16:33:35"
    }
  ],
  "count": 1,
  "stats": {
    "total_work_orders": 5,
    "queued": 1,
    "in_progress": 2,
    "completed": 2
  }
}
```

#### Get Work Order Details
```bash
GET /patches/work-orders/wo_20251113_0001
```

#### Complete Work Order (Called by Coding Agent)
```bash
POST /patches/work-orders/wo_20251113_0001/complete
Content-Type: application/json

{
  "tests_passed": true,
  "files_changed": 2,
  "diff_url": "/patches/diffs/wo_20251113_0001.diff"
}
```

#### List Playbook Runs
```bash
GET /patches/runs?status=awaiting_patch
```

#### Get Run Status
```bash
GET /patches/runs/run_20251113_163334
```

#### Trigger Manual Patch
```bash
POST /patches/trigger
Content-Type: application/json

{
  "description": "Pipeline validation timeout",
  "error_type": "pipeline_timeout",
  "file_path": "/backend/ingestion_pipeline.py"
}
```

Response:
```json
{
  "success": true,
  "message": "Playbook 'pipeline_timeout_fix' triggered",
  "run_id": "run_20251113_163334",
  "escalated_to_coding": true,
  "work_order_id": "wo_20251113_0001"
}
```

#### Get Patch Statistics
```bash
GET /patches/stats
```

Response:
```json
{
  "total_playbook_runs": 23,
  "work_orders": {
    "total_work_orders": 5,
    "queued": 1,
    "in_progress": 2,
    "completed": 2,
    "failed": 0
  },
  "escalation_rate": 0.12,
  "auto_fix_rate": 0.88,
  "average_patch_time_minutes": 8.5
}
```

## 🎬 Example Workflow

### Scenario: Ingestion Pipeline Timeout

1. **Detection**
```python
# Log watcher detects pattern in serve.log:
"ERROR: Pipeline timeout after 300 seconds"

# Emits event:
event_bus.publish('log_pattern.critical', {
    'pattern': 'timeout',
    'line': 'ERROR: Pipeline timeout...',
    'source': 'serve.log'
})
```

2. **Self-Healing Triggered**
```python
# Event handler receives event
# Selects playbook: pipeline_timeout_fix
# Executes steps:
Step 1: Analyze timeout cause → Found: Large file processing
Step 2: Check if code issue → Yes, inefficient chunking
Step 3: Escalate to coding agent
```

3. **Work Order Created**
```python
work_order = {
    "work_order_id": "wo_20251113_0001",
    "description": "Optimize chunking logic for large files",
    "context": {
        "error_type": "pipeline_timeout",
        "file_size": "500MB",
        "current_chunk_size": "1MB",
        "timeout_threshold": "300s"
    },
    "status": "queued",
    "estimated_complexity": "medium"
}
```

4. **Coding Agent Processes**
```python
# Coding agent receives work order
# Analyzes code: backend/ingestion_pipeline.py
# Identifies issue: Fixed chunk size inefficient for large files
# Generates patch: Adaptive chunking based on file size
# Runs tests: All pass ✓
# Notifies: Work order complete
```

5. **Self-Healing Resumes**
```python
# Receives notification: Patch applied
# Reruns ingestion pipeline
# Verifies: Ingestion completes in 45 seconds (was timing out)
# Updates trust score: 0.95 → 0.98
# Marks run as completed
```

6. **User Notification**
```
Co-Pilot: "Self-healing escalated to coding agent for patch X
           (pipeline timeout fix). Patch applied successfully.
           Trust restored to 0.98 after verification."
```

## 🔌 Integration Points

### Self-Healing → Coding Agent
```python
# In playbook_engine.py
work_order_id = await coding_bridge.create_work_order(
    description="Fix pipeline timeout",
    context={"error_type": "timeout", ...},
    self_healing_run_id=run_id,
    playbook_id=playbook_id
)
```

### Coding Agent → Self-Healing
```python
# When patch completes
await coding_bridge.update_work_order_status(
    work_order_id,
    WorkOrderStatus.COMPLETED,
    patch_result={
        "tests_passed": True,
        "files_changed": 2,
        "diff_url": "/patches/diffs/..."
    }
)

# Automatically calls:
await playbook_engine.handle_coding_patch_completed(work_order_id, patch_result)
```

### Status Synchronization
```python
# Work order tracks self-healing run
work_order["self_healing_run_id"] = "run_20251113_163334"

# Self-healing run tracks work order
playbook_run["coding_work_order_id"] = "wo_20251113_0001"

# Bidirectional tracking for complete visibility
```

## 📊 Monitoring & Visibility

### API Endpoints for Tracking

1. **Get All Work Orders**
   ```bash
   GET /patches/work-orders
   ```

2. **Get Work Orders by Status**
   ```bash
   GET /patches/work-orders?status=in_progress
   ```

3. **Get Work Orders for Specific Run**
   ```bash
   GET /patches/work-orders?self_healing_run_id=run_20251113_163334
   ```

4. **Get Playbook Run Status**
   ```bash
   GET /patches/runs/run_20251113_163334
   ```

### Event Stream
```bash
GET /events/recent?event_type=self_healing.escalated
GET /events/recent?event_type=coding_agent.work_order_created
GET /events/recent?event_type=self_healing.patch_applied
```

### Real-Time Updates
The Co-Pilot dock shows live updates:
- "Self-healing detected ingestion failure"
- "Running playbook: ingestion_replay"
- "Escalated to coding agent (work order wo_xxx)"
- "Coding agent analyzing... (Est. 5 minutes)"
- "Patch applied! Running verification..."
- "Trust restored: 0.92 → 0.98"

## 🎯 Pre-Packaged Playbooks

### Current Playbooks (6 total)

1. **ingestion_replay** (Data Fix)
   - Clear cache → Reset state → Retry
   - Does NOT require code

2. **schema_recovery** (Data Fix)
   - Validate → Backup → Fix → Verify
   - Does NOT require code

3. **memory_cleanup** (Cache Clear)
   - Identify caches → Clear → Stop tasks → Verify
   - Does NOT require code

4. **database_reconnect** (Retry)
   - Close connections → Backoff → Reconnect → Verify
   - Does NOT require code

5. **pipeline_timeout_fix** (Hybrid)
   - Analyze → Check cause → **May escalate** → Config fix
   - May require code

6. **verification_fix** (Code Patch)
   - Analyze failure → Check data vs logic → **Escalates**
   - REQUIRES code patch

## 📝 Files Created

### Backend Services (3 files)
1. `backend/services/playbook_engine.py` - Playbook orchestration with escalation
2. `backend/services/coding_agent_bridge.py` - Work order management
3. Updated `backend/services/event_bus.py` - Integrated playbook triggers

### Backend API (1 file)
1. `backend/api/patches.py` - Patch tracking API (8 endpoints)

### Frontend (1 file)
1. `frontend/src/components/PatchTrackingPanel.tsx` - Patch tracking UI

### Documentation (1 file)
1. `SELF_HEALING_CODE_PATCH_COMPLETE.md` (this file)

## 🧪 Testing the Workflow

### Test 1: Trigger Playbook That Doesn't Escalate
```bash
curl -X POST http://localhost:8000/patches/trigger \
  -H "Content-Type: application/json" \
  -d '{"description":"Database connection lost","error_type":"database_connection"}'
```

Expected: Playbook runs, completes without escalation

### Test 2: Trigger Playbook That Escalates
```bash
curl -X POST http://localhost:8000/patches/trigger \
  -H "Content-Type: application/json" \
  -d '{"description":"Pipeline validation timeout","error_type":"pipeline_timeout"}'
```

Expected: 
```json
{
  "escalated_to_coding": true,
  "work_order_id": "wo_20251113_0001"
}
```

### Test 3: Check Work Orders
```bash
curl http://localhost:8000/patches/work-orders
```

### Test 4: Complete Work Order (Simulate Coding Agent)
```bash
curl -X POST http://localhost:8000/patches/work-orders/wo_20251113_0001/complete \
  -H "Content-Type: application/json" \
  -d '{"tests_passed":true,"files_changed":2}'
```

## 📈 Statistics & Metrics

Access via `/patches/stats`:

- **Total Playbook Runs**: How many self-healing attempts
- **Work Orders**: Breakdown by status (queued/in-progress/completed/failed)
- **Escalation Rate**: % of runs that need coding patches
- **Auto-Fix Rate**: % of runs fixed without code changes
- **Average Patch Time**: How long coding patches take

Example:
```json
{
  "escalation_rate": 0.12,    // 12% need code patches
  "auto_fix_rate": 0.88,      // 88% fixed automatically
  "average_patch_time_minutes": 8.5
}
```

## 🎨 UI Components

### Patch Tracking Panel

**3 Tabs:**

1. **Workflow Tab** - Visual workflow diagram showing:
   - Error Detection
   - Playbook Execution  
   - Code Escalation
   - Trust Restoration
   - Recent escalations list

2. **Runs Tab** - All playbook runs:
   - Run ID
   - Playbook type
   - Status
   - Steps completed
   - Work order ID (if escalated)

3. **Patches Tab** - Code patch work orders:
   - Work order ID
   - Description
   - Priority & complexity
   - Status
   - Patch results (tests, files changed)

### Integration in Main UI

Add to GraceComprehensive.tsx:
```typescript
import { PatchTrackingPanel } from './components/PatchTrackingPanel';

// In tabs array:
{ id: 'patches', label: 'Code Patches', icon: GitBranch }

// In render:
case 'patches':
  return <PatchTrackingPanel />;
```

## 🔗 Event Types

### Published by Watchers
- `ingestion.failed`
- `ingestion.completed`
- `schema.invalid`
- `pipeline.timeout`
- `verification.failed`
- `log_pattern.error`
- `log_pattern.critical`

### Published by Self-Healing
- `self_healing.triggered`
- `self_healing.escalated` (when creating work order)
- `self_healing.completed`
- `self_healing.patch_applied` (after coding agent completes)

### Published by Coding Agent
- `coding_agent.work_order_created`
- `coding_agent.work_order_updated`
- `coding_agent.patch_generated`
- `coding_agent.tests_passed`

## 🎓 Design Principles

### 1. Conditional Escalation
Not every playbook needs code changes:
- Try data fixes first
- Escalate only when necessary
- Track escalation rate

### 2. Bidirectional Tracking
- Work order knows its self-healing run
- Playbook run knows its work order
- Complete visibility in UI

### 3. Event-Driven
- Loose coupling via event bus
- Easy to add new handlers
- No direct dependencies

### 4. Status Synchronization
- Self-healing waits in `awaiting_patch` state
- Coding agent updates work order status
- Callback resumes self-healing
- Trust updated after verification

## 📊 Sample Data Flow

### 1. Error Detected
```python
# Log watcher sees:
"ERROR: Ingestion failed for book_123.pdf: Schema mismatch"

# Emits:
event_bus.publish('ingestion.failed', {
    'file_path': 'book_123.pdf',
    'error': 'Schema mismatch'
})
```

### 2. Playbook Executes
```python
# Event handler triggers playbook
await playbook_engine.execute_playbook('ingestion_replay', context)

# Playbook checks if code patch needed
if error_type == "schema_mismatch":
    # Yes, needs schema validation logic fix
    work_order_id = await escalate_to_coding_agent(context)
```

### 3. Work Order Created
```python
{
    "work_order_id": "wo_20251113_0001",
    "description": "Fix schema validation logic",
    "self_healing_run_id": "run_20251113_163334",
    "status": "queued"
}
```

### 4. Coding Agent Works
```python
# Analyzes backend/schema_validator.py
# Finds bug in validation logic
# Generates patch
# Tests pass
# Calls: POST /patches/work-orders/wo_20251113_0001/complete
```

### 5. Self-Healing Resumes
```python
# Receives callback
await playbook_engine.handle_coding_patch_completed(
    work_order_id,
    {'tests_passed': True, 'files_changed': 1}
)

# Reruns ingestion
# Verification passes
# Trust updated: 0.75 → 0.92
```

### 6. User Sees in UI
```
Timeline:
  [16:33:34] Error detected: Ingestion failed
  [16:33:35] Playbook triggered: ingestion_replay
  [16:33:36] Escalated to coding agent (wo_20251113_0001)
  [16:41:12] Code patch applied (2 files changed)
  [16:41:15] Verification passed
  [16:41:16] Trust restored: 0.75 → 0.92 ✓
```

## ✅ What's Working Now

### Backend
- ✅ Playbook engine with 6 pre-packaged playbooks
- ✅ Coding agent bridge for work order management
- ✅ Event-driven trigger system
- ✅ Status synchronization
- ✅ API endpoints for tracking (8 endpoints)

### Integration
- ✅ Log watcher → Event bus → Playbook
- ✅ Playbook → Coding bridge → Work order
- ✅ Work order complete → Self-healing resume
- ✅ Trust/verification update after patch

### Frontend
- ✅ PatchTrackingPanel with 3 tabs
- ✅ Workflow visualization
- ✅ Work order list
- ✅ Playbook run tracking

## 🚀 Usage Examples

### From Frontend
```typescript
import { api } from './api/factory';

// Trigger a patch manually
const result = await fetch('http://localhost:8000/patches/trigger', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    description: 'Fix validation bug',
    error_type: 'verification_failed'
  })
});

// Check if escalated
if (result.escalated_to_coding) {
  console.log(`Escalated to coding agent: ${result.work_order_id}`);
}

// Track work order
const order = await fetch(`http://localhost:8000/patches/work-orders/${result.work_order_id}`);
```

### From Backend Services
```python
from backend.services.playbook_engine import playbook_engine
from backend.services.event_bus import event_bus

# Trigger playbook
result = await playbook_engine.execute_playbook(
    'verification_fix',
    context={'error_type': 'validation_failed', 'file': 'test.py'}
)

# Or publish event (playbook auto-triggers)
await event_bus.publish('ingestion.failed', {
    'file_path': 'book.pdf',
    'error': 'Timeout'
})
```

## 🎉 Complete Feature Set

✅ **Detection**: Log watcher monitors 6 critical patterns  
✅ **Pre-packaged Playbooks**: 6 playbooks covering all common issues  
✅ **Coding Agent Handoff**: Seamless escalation with work orders  
✅ **Status Updates**: Bidirectional tracking and synchronization  
✅ **Event-Driven**: Pub/sub architecture for loose coupling  
✅ **UI Visibility**: Complete tracking panel with workflow diagram  
✅ **Real-Time Updates**: Event bus broadcasts all status changes  
✅ **Trust Restoration**: Automatic trust update after successful fix  

## 🌟 Summary

The self-healing → coding agent integration is **production-ready**:

- Automatically detects errors via log monitoring
- Triggers appropriate playbooks based on error type
- Escalates to coding agent only when code changes needed
- Tracks entire workflow with bidirectional references
- Updates trust scores after successful remediation
- Provides complete visibility in UI

**Grace can now heal itself, escalate to code patches when needed, and keep you informed every step of the way!** 🚀🎊
