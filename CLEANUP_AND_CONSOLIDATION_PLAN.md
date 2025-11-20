# Cleanup & Consolidation Plan - Remove Redundancies

## Executive Summary

After integrating the six new systems, we need to **remove 500+ redundant calls** across your codebase.

**Found:**
- **504 direct `.publish()` calls** that should route through trigger mesh
- **55+ `governance_engine.check()` calls** that should use governance gate
- **40+ direct file logging** that should use immutable log
- **Multiple audit trails** that should consolidate to one

---

## 1. Event Publishing Consolidation

### Current State: 504 Direct Publish Calls

**Problem:** Components bypass trigger mesh and call event bus directly.

**Found in:**
- `backend/world_model/*.py` - 10 calls to `event_bus.publish()`
- `backend/services/*.py` - 25 calls to `message_bus.publish()` and `event_bus.publish()`
- `backend/workflow_engines/*.py` - 15 calls to `trigger_mesh.publish()`
- `backend/routes/*.py` - 10 calls to `event_bus.publish()`
- And 444 more across the codebase

### Solution: Bridge Event Bus (Already Planned)

**Step 1:** Modify `backend/event_bus.py` to route through trigger mesh:

```python
# backend/event_bus.py - Line 57
async def publish(self, event: Event) -> None:
    """Publish event through trigger mesh (mandatory routing)"""
    
    from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
    
    # Convert to TriggerEvent and route through mesh
    trigger_event = TriggerEvent(
        event_type=event.event_type.value,
        source=event.source,
        actor=event.source,
        resource="",
        payload=event.data
    )
    
    # Route through mesh (includes governance validation)
    await trigger_mesh.publish(trigger_event)
    
    # Keep legacy log for compatibility
    self.event_log.append(event)
```

**Impact:** All 504 calls now automatically route through trigger mesh  
**Code to remove:** None yet - this makes existing calls compliant  
**Risk:** Low - Backward compatible

### Audit & Remove Direct Helpers

**Step 2:** After bridge is confirmed working, remove redundant helpers:

**Files to clean:**

```python
# backend/services/coding_agent_bridge.py - Lines 81, 135
# REMOVE these direct publishes:
await event_bus.publish("coding_agent.work_order_created", {...})
await event_bus.publish("coding_agent.work_order_updated", {...})

# REPLACE with trigger mesh events (define in trigger_mesh.yaml):
# Events already route through mesh via event_bus bridge - no change needed
# But can clean up to use trigger mesh directly for clarity:
await trigger_mesh.emit(TriggerEvent(
    event_type="coding_agent.work_order_created",
    source="coding_agent_bridge",
    actor="system",
    resource=f"work_order:{work_order_id}",
    payload={...}
))
```

**Systematic cleanup:**
```bash
# Search for all direct publishes
grep -r "event_bus.publish(" backend/ | wc -l  # 80+ files

# After bridge works, refactor in batches:
# Week 1: services/ (25 files)
# Week 2: routes/ (10 files)
# Week 3: workflow_engines/ (15 files)
# Week 4: everything else
```

**Files to audit (high priority):**
1. `backend/services/playbook_engine.py` - 3 direct publishes
2. `backend/services/coding_agent_bridge.py` - 2 direct publishes
3. `backend/world_model/world_model_service.py` - 10 direct publishes
4. `backend/watchers/mission_watcher.py` - 5 direct publishes
5. `backend/routes/chat_api.py` - 3 direct publishes

**Cleanup action:** Convert to `trigger_mesh.emit()` or keep as-is (bridge handles it)

---

## 2. Governance + Verification Stubs

### Current State: 55 Direct Governance Checks

**Problem:** Components call `governance_engine.check()` directly, bypassing governance gate.

**Found in:**
- `backend/ui_handlers/ide_websocket_handler.py` - 6 calls
- `backend/routes/*.py` - 5 calls
- `backend/transcendence/*.py` - 3 calls
- `backend/ml_training/*.py` - 4 calls
- `backend/misc/elite_self_healing.py` - 1 call
- And 36 more

### Solution: Replace with Governance Gate

**Current pattern:**
```python
# OLD - Direct governance check
from backend.governance_system.governance import governance_engine

decision = await governance_engine.check(
    actor=user,
    action="deploy",
    resource="model"
)

if decision.get('approved'):
    await deploy_model()
```

**New pattern:**
```python
# NEW - Through governance gate
from backend.governance_system.governance_gate import governance_gate, GovernanceRequest, ActionRiskLevel

response = await governance_gate.validate(GovernanceRequest(
    request_id=f"req_{uuid.uuid4().hex[:8]}",
    actor=user,
    action="deploy",
    resource="model",
    context={},
    risk_level=ActionRiskLevel.HIGH
))

if response.decision == GovernanceDecision.APPROVED:
    await deploy_model()
```

**Even Better - Use decorator:**
```python
# BEST - Decorator handles it
from backend.ingress.governance_middleware import require_governance

@require_governance(action='deploy_model', risk_level='high')
async def deploy_model(actor: str, resource: str):
    # Governance check automatic
    await actually_deploy()
```

### Files to Refactor

**High Priority (API endpoints):**

1. **backend/routes/execution.py** - Line 136
   ```python
   # REMOVE
   governance_result = await governance_engine.check(...)
   
   # REPLACE with decorator
   @require_governance(action='execute_code', risk_level='high')
   async def execute_code(...):
   ```

2. **backend/routes/sandbox.py** - Line 57
   ```python
   # REMOVE
   decision = await governance_engine.check(...)
   
   # REPLACE
   @require_governance(action='sandbox_execute', risk_level='medium')
   async def run_sandbox(...):
   ```

3. **backend/ui_handlers/ide_websocket_handler.py** - Lines 77, 133, 178, 234, 323, 511
   ```python
   # REMOVE all 6 governance_engine.check() calls
   
   # REPLACE with governance gate validation at connection level
   # Or use decorator on each WebSocket handler
   ```

**Medium Priority (Internal services):**

4. **backend/ml_training/training_pipeline.py** - Lines 76, 171, 252
5. **backend/misc/elite_self_healing.py** - Line 494
6. **backend/core/healing_orchestrator.py** - Lines 407, 695

**Cleanup strategy:**
```python
# Create helper function for migration
async def check_governance_compat(actor, action, resource, context, risk_level='medium'):
    """Backward-compatible governance check - USE GOVERNANCE GATE"""
    from backend.governance_system.governance_gate import governance_gate, GovernanceRequest, ActionRiskLevel
    
    risk_map = {'low': ActionRiskLevel.LOW, 'medium': ActionRiskLevel.MEDIUM, 
                'high': ActionRiskLevel.HIGH, 'critical': ActionRiskLevel.CRITICAL}
    
    response = await governance_gate.validate(GovernanceRequest(
        request_id=f"compat_{datetime.utcnow().timestamp()}",
        actor=actor,
        action=action,
        resource=resource,
        context=context,
        risk_level=risk_map[risk_level]
    ))
    
    # Return in old format for compatibility
    return {
        'approved': response.decision == GovernanceDecision.APPROVED,
        'requires_approval': response.requires_human_approval,
        'reason': response.reasoning
    }

# Then replace all governance_engine.check() calls:
# decision = await governance_engine.check(...)
decision = await check_governance_compat(actor, action, resource, context)
```

**Total to refactor:** 55 files

---

## 3. Learning Direct Writes

### Current State: No Direct Memory Writes Found ✅

**Good news:** Your learning system already uses proper interfaces.

**Verification needed:**
- Check if any components write directly to `memory_tables/` databases
- Check if any scripts update trust scores without using trust framework

**Action:** Verify no direct writes:
```bash
grep -r "INSERT INTO memory" backend/ | grep -v "memory_service"
grep -r "UPDATE.*trust_score" backend/ | grep -v "trust_framework"
```

---

## 4. Duplicate Audit/Logging

### Current State: 40+ Direct File Logging

**Problem:** Components write audit logs to files instead of immutable log.

**Found:**
- `backend/guardian/incident_log.py` - Lines 95, 115 (file-based incident log)
- `backend/core/guardian_healer.py` - Lines 633, 646 (file-based healing log)
- `backend/core/advanced_network_healer.py` - Lines 964, 979 (file-based network log)
- `backend/trust_framework/chaos_drills.py` - Line 317 (file-based drill log)
- `backend/services/log_service.py` - Multiple file reads for different log types

**Also found:** Multiple `audit.append()` calls:
- `backend/workflow_engines/constitutional_engine.py` - 3 calls
- `backend/cognition/FeedbackIntegrator.py` - 5 calls
- `backend/learning/governed_learning.py` - 2 calls

### Solution: Consolidate to Immutable Log

**Keep file logs for:**
- Guardian incident tracking (operational, not audit)
- Boot logs (pre-immutable log availability)
- Performance logs (high-volume, not audit-critical)

**Replace with immutable log:**

```python
# backend/core/guardian_healer.py - Line 633
# REMOVE file logging:
with open(log_file, 'a') as f:
    json.dump(healing_event, f)

# REPLACE with immutable log:
from backend.logging.avn_logger import avn_logger

await avn_logger.log_healing_action(
    healing_id=healing_id,
    anomaly_id=anomaly_id,
    healer="guardian",
    action_type=action,
    action_description=description,
    affected_resource=resource,
    success=success,
    execution_time_seconds=duration
)
```

**Files to refactor:**
1. `backend/core/guardian_healer.py` - Replace file logging with `avn_logger`
2. `backend/workflow_engines/constitutional_engine.py` - Replace `audit.append()` with `governance_logger`
3. `backend/cognition/FeedbackIntegrator.py` - Replace `audit.append()` with immutable log

**Can keep:**
- `backend/guardian/incident_log.py` - Operational log (not audit)
- `backend/services/log_service.py` - Log aggregation service (reads, doesn't write audit)

---

## 5. Duplicate Healing Triggers

### Current State: Multiple Healing Entry Points

**Problem:** Healing triggered from multiple places instead of through AVN.

**Found:**
- `backend/misc/log_based_healer.py` - Watches log files, triggers healing directly
- `backend/self_heal/trigger_system.py` - Multiple trigger classes (HeartbeatFailureTrigger, etc.)
- `backend/services/playbook_engine.py` - Direct playbook execution

### Solution: Consolidate Through AVN

**Current flow:**
```
Log Watcher → Detect issue → Call healing directly
Trigger System → Detect failure → Call playbook directly
```

**New flow:**
```
Log Watcher → Detect issue → Emit anomaly.detected event → AVN handles it
Trigger System → Detect failure → Emit anomaly.detected event → AVN handles it
```

**Refactor:**

```python
# backend/misc/log_based_healer.py - When error detected:
# REMOVE direct healing:
await healing_orchestrator.execute_playbook(playbook)

# REPLACE with event emission:
from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent

await trigger_mesh.emit(TriggerEvent(
    event_type="anomaly.detected",
    source="log_watcher",
    actor="system",
    resource=component_name,
    payload={
        'type': 'error_rate_increase',
        'severity': 'medium',
        'details': error_details
    }
))

# AVN will automatically determine and execute healing
```

**Files to refactor:**
1. `backend/misc/log_based_healer.py` - Emit events instead of direct healing
2. `backend/self_heal/trigger_system.py` - Triggers emit events, don't execute directly
3. `backend/services/playbook_engine.py` - Keep playbooks, but invoke via AVN

**Can keep:**
- Playbook implementations (called by AVN)
- Healing orchestrator (called by AVN)
- Trigger definitions (but change actions to event emission)

---

## 6. Sandbox/Deployment Helper Scripts

### Current State: Scattered Deployment Scripts

**Look for:**
- Shell scripts in `scripts/` that restart services
- Python helpers that deploy without governance
- Direct subprocess calls to restart/deploy

**Action:** Audit and consolidate

```bash
# Find shell scripts that restart/deploy
find scripts/ -name "*.sh" -o -name "*.bat" | grep -i "restart\|deploy\|start"

# Find Python subprocess calls
grep -r "subprocess.*restart\|subprocess.*deploy" backend/
```

### Solution: Route Through Multi-OS Kernel (Future)

**For now:** Keep scripts but call through governance:

```python
# scripts/restart_service.py
# BEFORE:
subprocess.run(['systemctl', 'restart', service_name])

# AFTER:
from backend.autonomous.governance_wiring import check_system_change

approved = await check_system_change(
    change_type='restart',
    target_system=service_name,
    actor='admin_script',
    details={'manual_restart': True}
)

if approved:
    subprocess.run(['systemctl', 'restart', service_name])
    
    # Log to immutable
    from backend.logging.avn_logger import avn_logger
    await avn_logger.log_healing_action(...)
```

---

## 7. Business Ops Direct API Calls

### Current State: Components Hit External APIs Directly

**Need to find:**
- HTTP clients calling external services without governance
- Payment processors without approval workflows
- Email senders without validation

**Action: Audit external calls**

```bash
# Find httpx/requests calls
grep -r "httpx\.|requests\." backend/transcendence/business/
grep -r "stripe\.|paypal\.|twilio\." backend/
```

### Solution: Route Through Business Ops Kernel

**Future:** All external calls go through business ops with governance

```python
# backend/transcendence/business/payment_processor.py
# BEFORE:
async def process_payment(amount, customer):
    stripe_result = await stripe_client.charge(...)
    return stripe_result

# AFTER:
async def process_payment(amount, customer):
    # Check governance first
    from backend.autonomous.governance_wiring import check_business_operation
    
    approved = await check_business_operation(
        operation='process_payment',
        actor=customer.id,
        resource=f"payment:{amount}",
        context={'amount': amount, 'customer': customer.id}
    )
    
    if not approved:
        return {'error': 'Governance rejected payment'}
    
    # Process payment
    stripe_result = await stripe_client.charge(...)
    
    # Log to immutable
    # Emit result event for learning
    
    return stripe_result
```

---

## 8. Per-Component Mode Flags

### Current State: Unknown (Need to Search)

**Look for:**
```bash
# Find local mode variables
grep -r "learning_mode\s*=" backend/
grep -r "self\.mode\s*=" backend/
grep -r "stabilize\|explore\|build" backend/ | grep -i mode
```

### Solution: Subscribe to Consciousness Events

**Pattern to replace:**
```python
# REMOVE local mode
class MyComponent:
    def __init__(self):
        self.mode = "normal"  # Local mode - REMOVE
    
    async def should_explore(self):
        return self.mode == "explore"  # Local check - REMOVE

# REPLACE with consciousness subscription
class MyComponent:
    def __init__(self):
        self.consciousness_mode = "stabilize"  # From consciousness
        
        # Subscribe to consciousness updates
        from backend.misc.trigger_mesh import trigger_mesh
        trigger_mesh.subscribe("consciousness.state_updated", self._update_mode)
    
    async def _update_mode(self, event):
        self.consciousness_mode = event.payload.get('mode', 'stabilize')
    
    async def should_explore(self):
        return self.consciousness_mode == "explore"
```

---

## Cleanup Priority Matrix

| Priority | Category | Files Affected | Effort | Risk | Impact |
|----------|----------|----------------|--------|------|--------|
| **P0** | Event Bus Bridge | 1 file | 30 min | Low | Enables all other cleanup |
| **P1** | Governance Gate Refactor | 55 files | 2-3 days | Medium | Critical security |
| **P2** | Immutable Log Consolidation | 40 files | 2 days | Low | Audit compliance |
| **P3** | Healing Trigger Consolidation | 10 files | 1 day | Medium | AVN effectiveness |
| **P4** | Direct Publish Cleanup | 504 files | 1-2 weeks | Low | Code clarity |
| **P5** | Mode Flag Removal | TBD | TBD | Low | Consciousness integration |

---

## Phased Cleanup Plan

### Phase 1: Foundation (Week 1)

**Goal:** Enable routing without breaking anything

**Actions:**
1. ✅ Modify `event_bus.py` to bridge to trigger mesh
2. ✅ Test all existing functionality still works
3. ✅ Monitor trigger mesh stats to see events flowing

**Files modified:** 1  
**Code removed:** 0 (only adding)  
**Risk:** Minimal

---

### Phase 2: High-Value Cleanup (Week 2)

**Goal:** Remove critical redundancies

**Actions:**
1. Refactor 10 highest-traffic governance checks to use governance gate
2. Replace 5 critical file logs with immutable log
3. Convert 3 healing triggers to emit events

**Files modified:** ~18  
**Code removed:** ~500 lines  
**Risk:** Low (well-tested patterns)

**Specific files:**
- `backend/routes/execution.py` - Add `@require_governance`
- `backend/routes/sandbox.py` - Add `@require_governance`  
- `backend/ui_handlers/ide_websocket_handler.py` - Use governance gate
- `backend/core/guardian_healer.py` - Use `avn_logger`
- `backend/misc/log_based_healer.py` - Emit events, don't heal directly

---

### Phase 3: Systematic Consolidation (Weeks 3-4)

**Goal:** Remove all redundancies systematically

**Actions:**
1. Refactor remaining 45 governance checks
2. Convert all direct publishes to use trigger mesh explicitly
3. Remove duplicate audit logs
4. Consolidate healing triggers

**Files modified:** ~100  
**Code removed:** ~2000 lines  
**Risk:** Medium (large scope)

---

### Phase 4: Deep Cleanup (Week 5+)

**Goal:** Remove obsolete helpers and scripts

**Actions:**
1. Remove redundant helper functions
2. Delete obsolete shell scripts
3. Remove duplicate audit tables
4. Clean up mode flags

**Files removed:** ~20  
**Code removed:** ~1000 lines  
**Risk:** Low (deprecated code)

---

## Automated Cleanup Script

I can create a script to help identify candidates:

```python
# cleanup_audit.py
import os
import re
from pathlib import Path

def find_redundancies():
    """Find all redundant patterns to clean up"""
    
    backend = Path('backend/')
    
    redundancies = {
        'direct_event_publish': [],
        'direct_governance': [],
        'file_logging': [],
        'direct_healing': []
    }
    
    for py_file in backend.rglob('*.py'):
        content = py_file.read_text()
        
        # Find direct event publishes
        if 'event_bus.publish(' in content and 'event_bus.py' not in str(py_file):
            redundancies['direct_event_publish'].append(str(py_file))
        
        # Find direct governance
        if 'governance_engine.check(' in content:
            redundancies['direct_governance'].append(str(py_file))
        
        # Find file logging
        if re.search(r"with open\(.*log.*'a'", content):
            redundancies['file_logging'].append(str(py_file))
        
        # Find direct healing calls
        if 'healing_orchestrator.execute_playbook(' in content:
            redundancies['direct_healing'].append(str(py_file))
    
    # Print report
    print("REDUNDANCY AUDIT REPORT")
    print("=" * 60)
    
    for category, files in redundancies.items():
        print(f"\n{category}: {len(files)} files")
        for f in files[:10]:  # Show first 10
            print(f"  - {f}")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more")
    
    return redundancies

if __name__ == '__main__':
    find_redundancies()
```

---

## Verification Strategy

After each cleanup phase, run:

**1. Smoke Tests**
```bash
# Test boot sequence
python server.py

# Should see all chunks boot successfully
```

**2. Integration Tests**
```bash
# Test governance blocks unauthorized
# Test AVN heals anomalies
# Test events route correctly
```

**3. Statistics Check**
```python
from backend.routing.trigger_mesh_enhanced import trigger_mesh
from backend.governance_system.governance_gate import governance_gate
from backend.immune.immune_kernel import immune_kernel

print("Trigger Mesh:", trigger_mesh.get_stats())
print("Governance:", governance_gate.get_stats())
print("AVN:", immune_kernel.get_stats())

# Should show non-zero activity
```

**4. Immutable Log Integrity**
```python
from backend.logging.immutable_log import immutable_log

integrity = await immutable_log.verify_integrity()
assert integrity['valid'] == True
```

---

## What To Do Next

**I can help you with:**

**Option A: Create the automated audit script** (find all redundancies systematically)

**Option B: Start Phase 1 cleanup** (event bus bridge + 10 high-priority refactors)

**Option C: Create file-by-file refactoring guide** (show exact changes for each file)

**Option D: Generate search queries** (so you can audit specific categories yourself)

Which would you like me to do first?
