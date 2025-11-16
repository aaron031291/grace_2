### Summary

All four Layer 2/3 integration tasks completed:

✅ **HTM Actionability** - SLA enforcement, auto-escalation, queue reprioritization, sub-agent spawning  
✅ **Layer 3↔Layer 2 Bridge** - Intent/task ID sharing, context propagation, completion events  
✅ **Secrets & Consent Flow** - Secure vault + UI consent prompts with governance  
✅ **Recording Capture** - Screen/video/voice pipeline with consent → transcription → learning (already completed)

---

## Implementation Details

### 1. HTM Actionability ([htm_sla_enforcer.py](file:///c:/Users/aaron/grace_2/backend/core/htm_sla_enforcer.py))

**Features:**
- Real-time SLA monitoring with deadline tracking
- Automatic escalation when SLAs violated (priority boost)
- Queue reprioritization based on urgency ratios
- Sub-agent spawning for critically overdue tasks (>200% SLA)
- Statistics feed to agentic brain dashboard

**Escalation Levels:**
1. **Warning (80% elapsed)** → Publish warning event
2. **Violation (100% elapsed)** → Escalate priority to HIGH
3. **Critical (200% elapsed)** → Spawn sub-agent rescue task

**Usage:**
```python
from backend.core.htm_sla_enforcer import htm_sla_enforcer

# Start enforcer
await htm_sla_enforcer.start()

# Get stats
stats = await htm_sla_enforcer.get_statistics()
# {
#   "total_violations": 5,
#   "warnings_issued": 12,
#   "escalations_triggered": 5,
#   "sub_agents_spawned": 2,
#   "sla_compliance_rate": 0.92
# }
```

**Message Bus Events:**
- `htm.sla.warning` - Task approaching deadline
- `htm.sla.violated` - SLA missed, priority escalated
- `htm.sla.critical` - Critical violation, sub-agent spawned
- `htm.sla.stats` - Periodic statistics

---

### 2. HTM Dashboard ([htm_dashboard_api.py](file:///c:/Users/aaron/grace_2/backend/routes/htm_dashboard_api.py))

**Endpoints:**

#### GET /api/htm/dashboard/stats
Real-time metrics for agentic brain:
- Task counts (total, active, queued, completed, failed)
- SLA compliance rate and violations
- Timing distributions (avg, p50, p95, p99)
- Queue depths by priority
- Worker utilization
- Escalation statistics

#### GET /api/htm/dashboard/violations
Active SLA violations with details

#### GET /api/htm/dashboard/tasks/slow
Slowest running tasks for bottleneck identification

#### GET /api/htm/dashboard/tasks/queued
Current queue state with wait times

#### GET /api/htm/dashboard/metrics/hourly
Historical trends (last 24 hours)

#### GET /api/htm/dashboard/health
Overall HTM health status with alerts

**Example Response:**
```json
{
  "total_tasks": 1247,
  "active_tasks": 15,
  "queued_tasks": 8,
  "sla_compliance_rate": 0.94,
  "active_violations": 2,
  "avg_execution_time_ms": 1250,
  "p95_execution_ms": 3400,
  "queue_depths": {
    "critical": 0,
    "high": 3,
    "normal": 5
  },
  "warnings_issued": 23,
  "escalations_triggered": 8,
  "sub_agents_spawned": 2
}
```

---

### 3. Layer 3↔Layer 2 Bridge ([intent_htm_bridge.py](file:///c:/Users/aaron/grace_2/backend/core/intent_htm_bridge.py))

**Features:**
- Bidirectional ID sharing (intent_id ↔ task_id)
- Context propagation from agentic brain to HTM
- Automatic status synchronization
- Completion event flow to learning loop
- Orphaned task detection and recovery

**Architecture:**
```
Layer 3 (Agentic Brain)
    ↓ submit_intent_as_task()
Intent API (records intent)
    ↓ creates HTM task with intent_id
HTM (Layer 2)
    ↓ execution updates
Intent-HTM Bridge (monitors)
    ↓ task completion event
Learning Loop (Layer 3)
```

**Usage:**
```python
from backend.core.intent_htm_bridge import intent_htm_bridge
from backend.core.intent_api import Intent, IntentPriority

# Start bridge
await intent_htm_bridge.start()

# Submit intent as task
intent = Intent(
    intent_id="int_ingest_docs_123",
    goal="Index new documents in uploads folder",
    expected_outcome="documents_indexed",
    sla_ms=30000,
    priority=IntentPriority.HIGH,
    domain="ingestion",
    context={"folder": "/uploads", "format": "pdf"}
)

task_id = await intent_htm_bridge.submit_intent_as_task(
    intent=intent,
    task_handler="ingestion_worker"
)

# Bridge automatically:
# 1. Stores bidirectional mapping (intent_id ↔ task_id)
# 2. Propagates full context to HTM task payload
# 3. Monitors task completion
# 4. Updates intent status
# 5. Feeds outcome to learning loop
```

**Database Schema:**
- `intent_records.htm_task_id` - Links intent to task
- `htm_tasks.intent_id` - Links task to intent
- Shared context in `htm_tasks.payload`

**Message Bus Events:**
- `agentic.intent.created` - New intent submitted
- `htm.task.created` - Task created from intent
- `htm.task.update` - Task progress updates
- `agentic.intent.completed` - Intent fulfilled
- `agentic.intent.failed` - Intent failed
- `agentic.intent.timeout` - Intent timed out

**Learning Loop Integration:**
```python
# Automatically feeds to learning loop on completion
await learning_loop.record_outcome(
    action_type=f"intent_{domain}",
    success=task.success,
    confidence_score=intent.confidence,
    execution_time=task.total_time_ms / 1000,
    context={
        "intent_id": intent_id,
        "goal": intent.goal,
        "sla_met": task.sla_met,
        "metrics": {...}
    }
)
```

---

### 4. Secrets & Consent Flow ([secrets_consent_flow.py](file:///c:/Users/aaron/grace_2/backend/security/secrets_consent_flow.py))

**Features:**
- User consent required before credential redemption
- UI prompts via message bus
- Governance checks for high-risk operations
- Single-use vs persistent consent
- Auto-approval for low-risk actions
- Revocable consent per secret/action
- Complete audit trail

**Consent Flow:**
```
1. Component requests secret access
   ↓
2. Check existing valid consent
   ↓ (if none)
3. Send UI prompt to user
   ↓
4. Wait for user approval/denial
   ↓
5. Check governance (if high/critical risk)
   ↓
6. Log access attempt
   ↓
7. Return access decision
```

**Risk Levels:**
- **Low**: Auto-approved, read-only actions
- **Medium**: UI consent required
- **High**: UI consent + governance approval
- **Critical**: Single-use consent + governance + audit

**Usage:**
```python
from backend.security.secrets_consent_flow import secrets_consent_flow

# Start consent flow
await secrets_consent_flow.start()

# Request consent before accessing secret
approved = await secrets_consent_flow.request_consent(
    secret_key="github_api_token",
    secret_type="api_key",
    service="github",
    requested_by="code_agent",
    requested_for="push code to repository",
    requested_action="git_push",
    user_id="aaron",
    risk_level="high",
    context={"repo": "grace_2", "branch": "main"},
    timeout_seconds=300  # 5 min to respond
)

if approved:
    # Proceed with credential use
    token = await secrets_vault.retrieve_secret("github_api_token")
else:
    # User denied or timeout
    print("Consent denied or expired")
```

**Database Schema:**
```sql
CREATE TABLE secret_consent_records (
    consent_id VARCHAR(128) PRIMARY KEY,
    secret_key VARCHAR(128) NOT NULL,
    secret_type VARCHAR(64),
    service VARCHAR(128),
    requested_by VARCHAR(128),
    requested_for VARCHAR(256),
    requested_action VARCHAR(128),
    user_id VARCHAR(128),
    consent_status VARCHAR(32),  -- pending, approved, denied, revoked
    risk_level VARCHAR(32),
    single_use BOOLEAN,
    used_count INTEGER,
    governance_approval_required BOOLEAN,
    ...
)
```

**UI Integration:**
Subscribe to `secrets.consent.request` events:
```javascript
// Frontend subscribes to message bus
messageBus.subscribe('secrets.consent.request', (event) => {
    showConsentPrompt({
        message: `Grace wants to use your ${event.service} credentials to ${event.requested_for}. Allow?`,
        consentId: event.consent_id,
        riskLevel: event.risk_level,
        context: event.context,
        expiresIn: event.expires_in_seconds
    });
});

// User responds
async function respondToConsent(consentId, approved, denialReason = null) {
    await fetch('/api/secrets/consent/respond', {
        method: 'POST',
        body: JSON.stringify({
            consent_id: consentId,
            approved: approved,
            user_id: currentUser.id,
            denial_reason: denialReason
        })
    });
}
```

**API Endpoints ([secrets_consent_api.py](file:///c:/Users/aaron/grace_2/backend/routes/secrets_consent_api.py)):**

- `POST /api/secrets/consent/respond` - User approves/denies
- `POST /api/secrets/consent/revoke` - Revoke existing consent
- `GET /api/secrets/consent/history` - View consent history
- `GET /api/secrets/consent/pending` - Get pending requests
- `GET /api/secrets/consent/stats` - Aggregate statistics

---

## Integration Points

### HTM → Agentic Brain
```python
# HTM publishes timing data
await message_bus.publish(
    topic="htm.sla.stats",
    payload={
        "sla_compliance_rate": 0.94,
        "avg_execution_time_ms": 1250,
        "p95_execution_ms": 3400,
        "active_violations": 2
    }
)

# Brain subscribes and adapts
# - Spawn more workers if queues deep
# - Adjust SLAs based on actual runtimes
# - Learn patterns (time of day, task type)
```

### Intent → HTM → Learning
```python
# Complete flow with IDs and context
intent = await intent_api.submit_intent(...)
    ↓ (intent_id: "int_123")
task = await htm.create_task(intent_id="int_123", ...)
    ↓ (task_id: "task_456")
outcome = await htm.complete_task("task_456")
    ↓
await intent_api.update_intent("int_123", outcome)
    ↓
await learning_loop.record_outcome(intent_id="int_123", ...)
```

### Secrets → Governance → User
```python
# Consent request flow
request = secrets_consent_flow.request_consent(...)
    ↓
if risk_level in ["high", "critical"]:
    governance_check = await governance_engine.check(...)
    ↓
ui_prompt = await message_bus.publish("secrets.consent.request")
    ↓
user_response = await wait_for_response(timeout=300)
    ↓
if approved and governance_ok:
    credential = await secrets_vault.retrieve_secret(...)
```

---

## Startup Integration

Add to main application startup:

```python
# backend/main.py or similar

from backend.core.htm_sla_enforcer import htm_sla_enforcer
from backend.core.intent_htm_bridge import intent_htm_bridge
from backend.security.secrets_consent_flow import secrets_consent_flow

async def startup():
    """Start all Layer 2/3 integration services"""
    
    # HTM SLA enforcement
    await htm_sla_enforcer.start()
    
    # Intent-HTM bridge
    await intent_htm_bridge.start()
    
    # Secrets consent flow
    await secrets_consent_flow.start()
    
    print("[LAYER 2/3] All integration services started")

# Add to FastAPI lifespan or startup event
```

---

## Testing

### HTM SLA Enforcer Test:
```python
# Create task with short SLA
task = HTMTask(
    task_id="test_123",
    sla_ms=1000,  # 1 second
    status="running"
)

# Wait for escalation
await asyncio.sleep(1.5)

# Check for violation event
assert task.priority == "high"
assert sla_enforcer.stats["escalations_triggered"] > 0
```

### Intent-HTM Bridge Test:
```python
# Submit intent
intent = Intent(intent_id="int_test", ...)
task_id = await bridge.submit_intent_as_task(intent, "test_handler")

# Verify linkage
assert bridge.active_mappings["int_test"] == task_id
assert bridge.task_to_intent[task_id] == "int_test"

# Complete task
await message_bus.publish("htm.task.completed", {"task_id": task_id})

# Verify intent updated
intent_record = await get_intent_record("int_test")
assert intent_record.status == "completed"
assert intent_record.learned_from == True
```

### Secrets Consent Test:
```python
# Request consent
consent_task = asyncio.create_task(
    secrets_consent_flow.request_consent(
        secret_key="test_api_key",
        service="test",
        requested_action="test_action",
        user_id="test_user",
        timeout_seconds=5
    )
)

# Simulate user approval
await message_bus.publish("secrets.consent.response", {
    "consent_id": consent_id,
    "approved": True,
    "user_id": "test_user"
})

# Verify approval
approved = await consent_task
assert approved == True
```

---

## Files Created/Modified

### HTM Actionability:
- ✅ `backend/core/htm_sla_enforcer.py` (new) - SLA enforcement with auto-escalation
- ✅ `backend/routes/htm_dashboard_api.py` (new) - Dashboard API with runtime stats

### Layer 3↔Layer 2 Bridge:
- ✅ `backend/core/intent_htm_bridge.py` (new) - Complete intent/task integration
- ✅ `backend/models/htm_models.py` (existing, verified) - Contains `intent_id` field
- ✅ `backend/core/intent_api.py` (existing, verified) - Contains `htm_task_id` field

### Secrets & Consent:
- ✅ `backend/security/secrets_consent_flow.py` (new) - Consent management
- ✅ `backend/routes/secrets_consent_api.py` (new) - Consent API endpoints
- ✅ `backend/security/secrets_vault.py` (existing) - Secure credential storage

### Documentation:
- ✅ `docs/LAYER_2_3_INTEGRATION_COMPLETE.md` (this file)
- ✅ `docs/RECORDING_PIPELINE_COMPLETE.md` (from previous task)

---

## Next Steps (Optional Enhancements)

1. **HTM Worker Pool Management**: Auto-scale workers based on queue depth
2. **Predictive SLA Adjustment**: ML model to predict task duration, adjust SLAs
3. **Consent Templates**: Pre-approved consent patterns for common workflows
4. **Multi-User Consent**: Require approval from multiple stakeholders
5. **Secrets Rotation Automation**: Auto-rotate credentials on schedule
6. **Intent Templating**: Common intent patterns (ingest, analyze, export)
7. **Dashboard UI**: React/Svelte components for real-time HTM monitoring
8. **Alert Integration**: Slack/email notifications for SLA violations

---

**Status**: ✅ Complete  
**Date**: 2025-11-14  
**Components**: HTM SLA, Dashboard, Intent Bridge, Secrets Consent  
**Integration**: Message bus, governance, learning loop  
**Quality**: Full event flow, audit logging, error handling
