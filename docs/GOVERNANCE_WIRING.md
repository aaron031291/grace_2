# Governance Wiring - Complete Implementation

## Overview

Governance is **Kernel 1** - the first stop after ingress. All requests must pass through governance validation before autonomous action.

**This is a production-ready implementation with all stubs removed.**

## Architecture

```
┌─────────────┐
│   Ingress   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│  KERNEL 1: GOVERNANCE GATE      │  ◄── First Stop
│  - Constitutional validation    │
│  - Policy enforcement           │
│  - Trust score check            │
│  - Risk assessment              │
└───────┬──────────────┬──────────┘
        │ APPROVED     │ REJECTED/PENDING
        ▼              ▼
┌──────────────┐   ┌────────────┐
│  Event Bus   │   │  403/202   │
└──────┬───────┘   └────────────┘
       │
       ▼
┌──────────────┐
│  Processing  │
└──────────────┘
```

## Core Components

### 1. Governance Gate ([governance_gate.py](file:///c:/Users/aaron/grace_2/backend/governance_system/governance_gate.py))

**Kernel 1** - The first stop after ingress that validates all requests.

```python
from backend.governance_system.governance_gate import governance_gate, GovernanceRequest

# Validate request
response = await governance_gate.validate(GovernanceRequest(
    request_id="req_001",
    actor="user_123",
    action="deploy_model",
    resource="ml_model_v2",
    context={'environment': 'production'},
    risk_level=ActionRiskLevel.HIGH
))

if response.decision == GovernanceDecision.APPROVED:
    # Proceed with action
    pass
```

**Validation Steps:**
1. **Constitutional Validation** - Check against constitutional principles
2. **Policy Enforcement** - Enforce domain policies
3. **Trust Score Validation** - Verify actor trust score ≥ 0.5
4. **Risk Assessment** - High/critical risk → Parliament approval
5. **Autonomous Action Check** - Additional validation for autonomous actions

### 2. Governance Middleware ([governance_middleware.py](file:///c:/Users/aaron/grace_2/backend/ingress/governance_middleware.py))

Integrates governance into ingress - every request goes through Kernel 1.

```python
from backend.ingress.governance_middleware import governance_middleware

# Process request through governance
result = await governance_middleware.process_request(
    actor="user_123",
    action="deploy_model",
    resource="ml_model_v2",
    context={'environment': 'production'},
    risk_level="high"
)

if result['allowed']:
    # Continue processing
    pass
else:
    # Return error
    return {'error': result['error'], 'status_code': result['status_code']}
```

**Decorator for API Endpoints:**

```python
from backend.ingress.governance_middleware import require_governance

@require_governance(action='deploy_model', risk_level='high')
async def deploy_model(actor: str, resource: str, **kwargs):
    """This only executes if governance approves"""
    # Deploy model...
    return {'success': True}
```

### 3. Autonomous Governance Wiring ([governance_wiring.py](file:///c:/Users/aaron/grace_2/backend/autonomous/governance_wiring.py))

Ensures ALL autonomous actions go through governance before execution.

```python
from backend.autonomous.governance_wiring import autonomous_governance

# Check governance before autonomous action
approved = await autonomous_governance.check_and_wait(
    actor='avn_healer',
    action='restart_service',
    resource='api_service',
    context={'anomaly_id': 'anom_123'}
)

if approved:
    # Execute autonomous action
    await restart_service()
```

## Wiring Points

### 1. Ingress → Governance Gate

**ALL external requests:**

```python
# In API gateway / ingress layer
from backend.ingress.governance_middleware import governance_middleware

@app.post("/api/action")
async def handle_action(request: Request):
    # Extract request details
    actor = request.headers.get('X-Actor')
    action = request.json.get('action')
    resource = request.json.get('resource')
    
    # GOVERNANCE CHECK (Kernel 1)
    result = await governance_middleware.process_request(
        actor=actor,
        action=action,
        resource=resource,
        context=request.json,
        risk_level=request.json.get('risk_level', 'medium')
    )
    
    if not result['allowed']:
        return JSONResponse(
            status_code=result['status_code'],
            content=result['response']
        )
    
    # Proceed to event bus
    await event_bus.publish(...)
```

### 2. Autonomous Actions → Governance

**Business Operations:**

```python
from backend.autonomous.governance_wiring import check_business_operation

async def process_marketplace_order(order_id: str, actor: str):
    # GOVERNANCE CHECK before processing
    approved = await check_business_operation(
        operation='process_order',
        actor=actor,
        resource=f"order:{order_id}",
        context={'order_id': order_id, 'amount': 99.99}
    )
    
    if not approved:
        return {'error': 'Governance rejected order processing'}
    
    # Process order
    ...
```

**AVN Self-Healing:**

```python
from backend.autonomous.governance_wiring import check_avn_action

async def avn_restart_service(component: str, anomaly_id: str):
    # GOVERNANCE CHECK before restart
    approved = await check_avn_action(
        action='restart_service',
        component=component,
        anomaly_id=anomaly_id,
        severity='high'
    )
    
    if not approved:
        print(f"⚠ Governance blocked restart of {component}")
        # Escalate to human
        return
    
    # Restart service
    ...
```

**System-Level Changes:**

```python
from backend.autonomous.governance_wiring import check_system_change

async def auto_scale_service(service_name: str, target_replicas: int):
    # GOVERNANCE CHECK before scaling
    approved = await check_system_change(
        change_type='scale',
        target_system=service_name,
        actor='auto_scaler',
        details={
            'current_replicas': 2,
            'target_replicas': target_replicas,
            'reason': 'high_load'
        }
    )
    
    if not approved:
        print(f"⚠ Governance blocked scaling of {service_name}")
        return
    
    # Scale service
    ...
```

**Code Generation & Deployment:**

```python
from backend.autonomous.governance_wiring import check_code_deployment
from backend.verification_system.verification_api import verification_api

async def deploy_generated_code(code: str, code_id: str, target: str):
    # Step 1: Verify code
    verification = await verification_api.verify_security(code)
    
    # Step 2: GOVERNANCE CHECK before deployment
    approved = await check_code_deployment(
        code_id=code_id,
        deployment_target=target,
        actor='code_generator',
        verification_passed=verification['safe_to_execute']
    )
    
    if not approved:
        print(f"⚠ Governance blocked deployment of {code_id}")
        return
    
    # Deploy code
    ...
```

### 3. Governance → Trust & Memory (MTL)

Governance writes to MTL kernel for trust updates and constitutional tags:

```python
# In governance_gate.py - _update_mtl()

# Update trust score based on outcome
from backend.trust_framework.trust_score import update_trust_score

if response.decision == GovernanceDecision.APPROVED:
    await update_trust_score(
        actor=request.actor,
        action_outcome='success',
        context={'governance_approved': True}
    )
elif response.decision == GovernanceDecision.REJECTED:
    await update_trust_score(
        actor=request.actor,
        action_outcome='violation',
        context={
            'governance_rejected': True,
            'violated_policies': response.violated_policies
        }
    )

# Tag memory with constitutional compliance
from backend.memory_services.memory_service import memory_service

await memory_service.tag_action(
    action_id=request.request_id,
    tags=[
        f"governance:{response.decision.value}",
        f"constitutional:{'compliant' if response.constitutional_compliant else 'violation'}",
        f"trust:{response.trust_score:.2f}"
    ]
)
```

### 4. Governance → Immutable Log

All governance decisions are logged:

```python
# In governance_gate.py - _log_decision()

from backend.logging.governance_logger import governance_logger

await governance_logger.log_governance_decision(
    decision_id=request.request_id,
    decision_type="governance_gate",
    actor=request.actor,
    resource=request.resource,
    approved=(response.decision == GovernanceDecision.APPROVED),
    reasoning=response.reasoning,
    vote_details={
        'trust_score': response.trust_score,
        'violated_policies': response.violated_policies,
        'constitutional_compliant': response.constitutional_compliant
    },
    metadata={
        'action': request.action,
        'risk_level': request.risk_level.value,
        'is_autonomous': request.is_autonomous
    }
)
```

## Decision Flow

### Approved Flow

```
Request → Governance Gate
  ├─ Constitutional: ✓
  ├─ Policy: ✓
  ├─ Trust: 0.85 ✓
  └─ Risk: medium
       ↓
   APPROVED
       ↓
   Event Bus → Processing
       ↓
   Update MTL (trust +0.1)
       ↓
   Log to immutable
```

### Rejected Flow

```
Request → Governance Gate
  ├─ Constitutional: ✗ (transparency violation)
  ↓
REJECTED
  ↓
403 Forbidden
  ↓
Update MTL (trust -0.2)
  ↓
Log to immutable
```

### Approval Required Flow

```
Request → Governance Gate
  ├─ Constitutional: ✓
  ├─ Policy: ✓
  ├─ Trust: 0.9 ✓
  └─ Risk: HIGH
       ↓
   REQUIRES_PARLIAMENT
       ↓
   Request Parliament Vote
       ↓
   202 Accepted (pending)
       ↓
   Wait for approval...
       ↓
   (Vote completes)
       ↓
   APPROVED / REJECTED
```

## Risk Levels

### Action Risk Assessment

```python
# CRITICAL - Always requires human approval
critical_actions = [
    'delete_database',
    'shutdown_system',
    'deploy_to_production',
    'modify_governance_policy'
]

# HIGH - Requires parliament approval
high_risk_actions = [
    'restart_service',
    'rollback_deployment',
    'scale_down',
    'deploy_model',
    'execute_code'
]

# MEDIUM - Auto-approved if policies pass
medium_risk_actions = [
    'generate_code',
    'create_task',
    'send_email',
    'process_payment'
]

# LOW - Auto-approved
low_risk_actions = [
    'read_data',
    'query_database',
    'get_status'
]
```

## Event Integration

### Governance Events

Add to [trigger_mesh.yaml](file:///c:/Users/aaron/grace_2/config/trigger_mesh.yaml):

```yaml
- event_type: governance.approved
  description: Governance approved a request
  publishers:
    - governance_gate
  subscribers:
    - event_bus
    - immutable_log
    - metrics_collector
  requires_constitutional_validation: false
  min_trust_score: 0.9

- event_type: governance.rejected
  description: Governance rejected a request
  publishers:
    - governance_gate
  subscribers:
    - alert_system
    - immutable_log
    - notification_service
  requires_constitutional_validation: false
  min_trust_score: 0.5

- event_type: governance.approval_required
  description: Request requires approval
  publishers:
    - governance_gate
  subscribers:
    - parliament_engine
    - notification_service
    - immutable_log
  requires_constitutional_validation: false
  min_trust_score: 0.7
```

## Statistics & Monitoring

```python
from backend.governance_system.governance_gate import governance_gate
from backend.ingress.governance_middleware import governance_middleware
from backend.autonomous.governance_wiring import autonomous_governance

# Governance gate stats
gate_stats = governance_gate.get_stats()
# {
#     'requests_processed': 1543,
#     'approved': 1420,
#     'rejected': 95,
#     'pending_approvals': 28,
#     'approval_rate': 0.92
# }

# Middleware stats
middleware_stats = governance_middleware.get_stats()
# {
#     'total_requests': 1543,
#     'passed': 1420,
#     'blocked': 123,
#     'pass_rate': 0.92
# }

# Autonomous wiring stats
autonomous_stats = autonomous_governance.get_stats()
# {
#     'actions_checked': 342,
#     'actions_blocked': 18,
#     'block_rate': 0.05
# }
```

## Best Practices

### 1. Always Check Governance for Autonomous Actions

```python
# ✅ GOOD - Checks governance
async def autonomous_action():
    approved = await autonomous_governance.check_and_wait(...)
    if approved:
        execute_action()

# ❌ BAD - Bypasses governance
async def autonomous_action():
    execute_action()  # NEVER DO THIS
```

### 2. Use Appropriate Risk Levels

```python
# ✅ GOOD - High risk for production deployment
await governance_middleware.process_request(
    action='deploy',
    resource='production',
    risk_level='high'  # Correct
)

# ❌ BAD - Low risk for critical action
await governance_middleware.process_request(
    action='delete_database',
    risk_level='low'  # Wrong!
)
```

### 3. Log All Governance Decisions

The system automatically logs to:
- Immutable log (audit trail)
- MTL kernel (trust updates)
- Trigger mesh (event propagation)

### 4. Handle Rejections Gracefully

```python
result = await governance_middleware.process_request(...)

if not result['allowed']:
    # Don't just fail silently
    logger.warning(f"Governance rejected: {result['response']}")
    
    # Notify user
    await send_notification(
        user=actor,
        message=f"Action rejected: {result['response']['reasoning']}"
    )
    
    # Escalate if needed
    if result['response']['requires_human_approval']:
        await escalate_to_human(request)
```

## Summary

Governance is now properly wired as **Kernel 1**:

- ✅ **Ingress Integration** - All requests go through governance gate first
- ✅ **Autonomous Wiring** - All autonomous actions checked before execution
- ✅ **MTL Integration** - Trust scores updated, constitutional tags written
- ✅ **Immutable Logging** - All decisions logged to audit trail
- ✅ **Event Emission** - Governance events published to trigger mesh
- ✅ **No Stubs** - All placeholder code removed
- ✅ **Complete Implementation** - Real constitutional validation, policy enforcement, trust scoring

The system ensures **no autonomous action bypasses governance**, providing complete transparency, auditability, and constitutional compliance.
