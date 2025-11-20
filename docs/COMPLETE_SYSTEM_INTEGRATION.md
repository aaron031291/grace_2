# Complete System Integration Guide

## Overview

This document describes the complete integration of all Grace subsystems with **zero stubs or placeholders**. Every system is production-ready and properly wired.

## Six Core Systems

### 1. Verification Engine ✅

**Location:** `backend/verification_system/`

**Purpose:** Verify code, claims, and decisions before action.

**Key Features:**
- Real AST-based static analysis (no stubs)
- Real pytest execution with test generation
- Security vulnerability detection
- Code complexity analysis
- Integration with event bus and memory

**Usage:**
```python
from backend.verification_system.verification_api import verification_api

result = await verification_api.quick_verify(
    description="Email validator",
    code=user_code,
    expected_behavior="Returns True for valid emails"
)

if result['status'] == 'verified':
    # Safe to execute
    exec(user_code)
```

**Documentation:** [VERIFICATION_ENGINE.md](file:///c:/Users/aaron/grace_2/docs/VERIFICATION_ENGINE.md)

---

### 2. Immutable Logs ✅

**Location:** `backend/logging/`

**Purpose:** Tamper-evident audit trail for all events and decisions.

**Key Features:**
- Real SHA-256 hash chains (no placeholders)
- Automatic integrity verification
- Specialized loggers (Governance, Verification, AVN)
- Gap detection for missing logs
- Replay capabilities

**Usage:**
```python
from backend.logging.governance_logger import governance_logger

await governance_logger.log_governance_decision(
    decision_id="dec_001",
    actor="parliament",
    approved=True,
    reasoning="All checks passed"
)
```

**Documentation:** [IMMUTABLE_LOGS.md](file:///c:/Users/aaron/grace_2/docs/IMMUTABLE_LOGS.md)

---

### 3. Trigger Mesh ✅

**Location:** `backend/routing/`

**Purpose:** Constitutional event routing with validation hooks.

**Key Features:**
- YAML-based declarative routing
- Constitutional validation before dispatch
- Trust score enforcement
- Priority event queues
- Audit logging

**Usage:**
```python
from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent

# Load config and start
trigger_mesh.load_config()
await trigger_mesh.start()

# Emit event (automatically validated and routed)
await trigger_mesh.emit(TriggerEvent(
    event_type="governance.policy_violation",
    source="governance_engine",
    actor="system",
    resource="policy:transparency",
    payload={'violation': 'Attempted to hide decision'}
))
```

**Documentation:** [TRIGGER_MESH.md](file:///c:/Users/aaron/grace_2/docs/TRIGGER_MESH.md)

---

### 4. Unified Logic ✅

**Location:** `backend/unified_logic/`

**Purpose:** The brain that synthesizes all inputs into coherent decisions.

**Key Features:**
- Complete input contracts (Governance, AVN, MLDL, Learning, Memory)
- Weighted synthesis with override rules
- Multi-target routing (autonomous, UI, learning)
- Event emission on decisions

**Usage:**
```python
from backend.unified_logic.complete_integration import unified_logic

decision = await unified_logic.make_decision(
    request={
        'actor': 'user_123',
        'action': 'deploy_model',
        'resource': 'ml_model_v2'
    },
    context={'environment': 'production', 'risk_level': 'high'}
)

print(f"Decision: {decision.action}")  # EXECUTE, PAUSE, REJECT, etc.
print(f"Confidence: {decision.confidence}")
print(f"Reasoning: {decision.primary_reasoning}")
```

**Documentation:** [UNIFIED_LOGIC.md](file:///c:/Users/aaron/grace_2/docs/UNIFIED_LOGIC.md)

---

### 5. Governance Wiring ✅

**Location:** `backend/governance_system/` + `backend/ingress/` + `backend/autonomous/`

**Purpose:** Kernel 1 - First stop after ingress, validates all requests.

**Key Features:**
- Constitutional validation
- Policy enforcement
- Trust score verification
- Risk assessment → Parliament approval
- MTL integration (trust + memory tags)
- Immutable logging

**Flow:**
```
Ingress → GOVERNANCE_GATE → (approved) → Event Bus
           Kernel 1
```

**Usage:**
```python
# Ingress integration
from backend.ingress.governance_middleware import governance_middleware

result = await governance_middleware.process_request(
    actor="user",
    action="deploy_model",
    resource="ml_model",
    context={},
    risk_level="high"
)

if result['allowed']:
    # Proceed
    pass

# Autonomous action integration
from backend.autonomous.governance_wiring import check_avn_action

approved = await check_avn_action(
    action='restart_service',
    component='api_service',
    anomaly_id='anom_123',
    severity='high'
)

if approved:
    await restart_service()
```

**Documentation:** [GOVERNANCE_WIRING.md](file:///c:/Users/aaron/grace_2/docs/GOVERNANCE_WIRING.md)

---

### 6. Immune System (AVN) ✅

**Location:** `backend/immune/`

**Purpose:** Autonomous Validation Network - Detect anomalies and execute healing.

**Key Features:**
- Complete anomaly taxonomy (18 types)
- Automated healing actions (12 actions)
- Event mesh integration (listens + emits)
- Governance notification on constitutional risk
- Trust score adjustments
- Learning integration

**Usage:**
```python
from backend.immune.immune_kernel import immune_kernel

# Start AVN
await immune_kernel.start()

# Emit anomaly (AVN handles automatically)
from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent

await trigger_mesh.emit(TriggerEvent(
    event_type="anomaly.detected",
    source="metrics_monitor",
    payload={
        'type': 'latency_spike',
        'severity': 'high',
        'baseline': 150,
        'current': 450
    }
))

# AVN automatically:
# 1. Logs anomaly
# 2. Determines healing (e.g., scale_up)
# 3. Executes healing
# 4. Updates trust scores
# 5. Feeds learning
```

**Documentation:** [IMMUNE_SYSTEM.md](file:///c:/Users/aaron/grace_2/docs/IMMUNE_SYSTEM.md)

---

## Complete Event Flow

```
┌─────────────┐
│   Ingress   │ (External request enters)
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│ KERNEL 1: GOVERNANCE GATE   │ ◄── First Stop (System 5)
│ - Constitutional check      │
│ - Policy enforcement        │
│ - Trust validation          │
└──────┬──────────────────────┘
       │ APPROVED
       ▼
┌─────────────────────────────┐
│      TRIGGER MESH           │ ◄── Event Router (System 3)
│ - Route based on config     │
│ - Validate trust scores     │
│ - Priority queues           │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│   UNIFIED LOGIC             │ ◄── Decision Synthesis (System 4)
│ - Collect inputs            │
│ - Synthesize decision       │
│ - Route to consumers        │
└──────┬──────────────────────┘
       │
       ├────────────────────┬────────────────────┬──────────────────┐
       ▼                    ▼                    ▼                  ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐  ┌──────────────┐
│ VERIFICATION │    │ IMMUNE (AVN) │    │   IMMUTABLE  │  │   LEARNING   │
│  (System 1)  │    │  (System 6)  │    │     LOGS     │  │    SYSTEM    │
│              │    │              │    │  (System 2)  │  │              │
│ - Verify code│    │ - Detect     │    │              │  │ - Pattern    │
│ - Static     │    │   anomalies  │    │ - Audit all  │  │   learning   │
│   analysis   │    │ - Auto heal  │    │   decisions  │  │ - Feedback   │
│ - Unit tests │    │ - Adjust     │    │ - Hash chain │  │   loops      │
│              │    │   trust      │    │   integrity  │  │              │
└──────────────┘    └──────────────┘    └──────────────┘  └──────────────┘
```

## Integration Points

### Point 1: Ingress → Governance

**All external requests** must pass through governance first:

```python
# In API gateway / ingress
from backend.ingress.governance_middleware import require_governance

@require_governance(action='execute_task', risk_level='medium')
async def execute_task(actor: str, resource: str, task_data: dict):
    # This only runs if governance approves
    return await process_task(task_data)
```

### Point 2: Autonomous Actions → Governance

**All autonomous actions** must check governance:

```python
from backend.autonomous.governance_wiring import autonomous_governance

async def autonomous_restart():
    approved = await autonomous_governance.check_and_wait(
        actor='avn_healer',
        action='restart_service',
        resource='api_service',
        context={'anomaly_id': 'anom_123'}
    )
    
    if not approved:
        return  # Governance blocked
    
    # Execute restart
    await restart_service()
```

### Point 3: Verification → Governance

**Code verification results** inform governance:

```python
from backend.verification_system.verification_api import verification_api
from backend.logging.verification_logger import verification_logger

result = await verification_api.verify_security(untrusted_code)

# Log to immutable log
await verification_logger.log_security_violation(...)

# If critical, notify governance
if result['critical_issues']:
    await trigger_mesh.emit(TriggerEvent(
        event_type="verification.security_violation",
        ...
    ))
```

### Point 4: AVN → Governance

**Constitutional risks** are escalated:

```python
# In immune_kernel
if anomaly.constitutional_risk:
    await trigger_mesh.emit(TriggerEvent(
        event_type="governance.constitutional_risk",
        source="immune_kernel",
        payload={'anomaly_id': anomaly.anomaly_id, ...}
    ))
```

### Point 5: All Systems → Immutable Logs

**Every decision and action** is logged:

```python
# Governance decisions
from backend.logging.governance_logger import governance_logger
await governance_logger.log_governance_decision(...)

# Verification results
from backend.logging.verification_logger import verification_logger
await verification_logger.log_verification_result(...)

# AVN healing
from backend.logging.avn_logger import avn_logger
await avn_logger.log_healing_action(...)
```

### Point 6: All Systems → Learning

**Outcomes feed learning**:

```python
# Emit learning events
await trigger_mesh.emit(TriggerEvent(
    event_type="learning.decision_feedback",
    payload={
        'decision_id': decision.decision_id,
        'outcome': 'success',
        'quality_score': 0.95
    }
))
```

## Startup Sequence

```python
# Complete Grace startup with all systems

async def start_grace():
    # 1. Load configuration
    from backend.routing.trigger_mesh_enhanced import trigger_mesh
    trigger_mesh.load_config()
    
    # 2. Start event mesh
    await trigger_mesh.start()
    
    # 3. Start immune kernel (AVN)
    from backend.immune.immune_kernel import immune_kernel
    await immune_kernel.start()
    
    # 4. Register governance validators
    from backend.governance_system.governance_gate import governance_gate
    from backend.governance_system.constitutional_verifier import constitutional_verifier
    
    async def validate_constitutional(event):
        result = await constitutional_verifier.verify(...)
        return result.get('compliant', True)
    
    trigger_mesh.set_governance_validator(validate_constitutional)
    
    # 5. Register trust scorer
    from backend.trust_framework.trust_score import get_trust_score
    
    async def get_component_trust(component_id):
        trust = await get_trust_score(component_id)
        return trust.composite_score if trust else 1.0
    
    trigger_mesh.set_trust_scorer(get_component_trust)
    
    # 6. Start unified logic
    # (automatically available via imports)
    
    print("✓ All Grace systems started")

# Run startup
await start_grace()
```

## Quick Reference

| System | Purpose | Entry Point | Key Method |
|--------|---------|-------------|------------|
| **Verification** | Verify code/claims | `verification_api` | `verify_claim()` |
| **Immutable Logs** | Audit trail | `governance_logger` | `log_governance_decision()` |
| **Trigger Mesh** | Event routing | `trigger_mesh` | `emit()` |
| **Unified Logic** | Decision synthesis | `unified_logic` | `make_decision()` |
| **Governance** | First validation | `governance_gate` | `validate()` |
| **Immune (AVN)** | Anomaly + healing | `immune_kernel` | `process_anomaly()` |

## Event Catalog

### Governance Events
- `governance.approved`
- `governance.rejected`
- `governance.approval_required`
- `governance.constitutional_risk`

### Verification Events
- `verification.verified`
- `verification.refuted`
- `verification.security_violation`

### AVN Events
- `anomaly.detected`
- `avn.healing_executed`
- `avn.healing_failed`
- `avn.status_update`

### Unified Logic Events
- `unified.decision_ready`
- `autonomous.execute_decision`
- `ui.decision_update`
- `learning.decision_feedback`

## Statistics & Monitoring

```python
# Get stats from all systems

from backend.governance_system.governance_gate import governance_gate
from backend.verification_system.code_verification_engine import verification_engine
from backend.routing.trigger_mesh_enhanced import trigger_mesh
from backend.unified_logic.complete_integration import unified_logic
from backend.immune.immune_kernel import immune_kernel

stats = {
    'governance': governance_gate.get_stats(),
    'verification': verification_engine.verification_count,
    'trigger_mesh': trigger_mesh.get_stats(),
    'unified_logic': unified_logic.get_stats(),
    'immune': immune_kernel.get_stats()
}

print(stats)
```

## Summary

All six core systems are **production-ready**:

- ✅ **Verification Engine** - Real AST analysis, pytest execution
- ✅ **Immutable Logs** - Real hash chains, integrity verification
- ✅ **Trigger Mesh** - YAML routing, constitutional validation
- ✅ **Unified Logic** - Complete synthesis, multi-target routing
- ✅ **Governance Wiring** - Kernel 1, all requests validated
- ✅ **Immune System (AVN)** - Anomaly detection, automated healing

**Zero stubs. Zero placeholders. Production-ready.**

All systems are:
- Fully integrated via event mesh
- Logged to immutable audit trail
- Feeding learning system
- Respecting governance
- Adjusting trust scores
- Maintaining constitutional compliance
