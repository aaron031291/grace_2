# Trigger Mesh - Complete Implementation

## Overview

The Trigger Mesh is Grace's constitutional "wiring harness" - a routing layer on top of the event bus that provides:
- YAML-based declarative event routing
- Constitutional validation hooks
- Trust score enforcement
- Priority event handling

**This is a production-ready implementation with zero stubs or placeholders.**

## Architecture

### Components

1. **TriggerMeshEnhanced** ([trigger_mesh_enhanced.py](file:///c:/Users/aaron/grace_2/backend/routing/trigger_mesh_enhanced.py))
   - Complete routing mesh with all three phases implemented
   - YAML configuration loader
   - Constitutional validation hooks
   - Trust score enforcement

2. **Configuration** ([trigger_mesh.yaml](file:///c:/Users/aaron/grace_2/config/trigger_mesh.yaml))
   - Declarative event definitions
   - Routing rules with metadata
   - Trust requirements
   - Priority classifications

3. **Legacy Support** ([trigger_mesh.py](file:///c:/Users/aaron/grace_2/backend/misc/trigger_mesh.py))
   - Backward compatible simple event bus
   - Pattern-based subscriptions

## Three-Phase Implementation

### Phase 1: Loader

The TriggerMesh loads `trigger_mesh.yaml` at startup and normalizes it into an in-memory routing map.

```python
from backend.routing.trigger_mesh_enhanced import trigger_mesh

# Load configuration
config = trigger_mesh.load_config()

# Routing map structure: (source, event_type) → [RoutingRule]
# Example: ('governance_engine', 'governance.policy_changed') → [RoutingRule(...)]
```

**Routing Map Structure:**

```python
routing_map = {
    ('governance_engine', 'governance.policy_violation'): [
        RoutingRule(
            source='governance_engine',
            event_type='governance.policy_violation',
            targets=['alert_system', 'immutable_log', 'governance_dashboard'],
            metadata=RouteMetadata(
                requires_constitutional_validation=True,
                min_trust_score=0.9,
                priority_level=10,
                audit_required=True,
                alert_on_failure=True
            )
        )
    ],
    ...
}
```

### Phase 2: Event Dispatch

Events are dispatched through the mesh with intelligent routing:

```python
from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent

# Create event
event = TriggerEvent(
    event_type="governance.policy_violation",
    source="governance_engine",
    actor="constitutional_engine",
    resource="policy:transparency",
    payload={
        "violation": "Attempted to hide decision",
        "severity": "high"
    },
    trust_score=0.95
)

# Emit through mesh
await trigger_mesh.emit(event)
```

**Event Flow:**

1. Event enters `emit()` method
2. Constitutional validation (if required)
3. Trust score validation
4. Route lookup: `(source, event_type)` → routing rules
5. Priority classification
6. Queue assignment (priority or normal)
7. Background router dispatches to all targets
8. Audit logging (if required)

### Phase 3: Constitutional & Trust Hooks

#### Constitutional Validation

```python
# Register constitutional validator
async def validate_constitutional(event: TriggerEvent) -> bool:
    """Validate event against constitutional principles"""
    
    # Check if event violates any constitutional principle
    from backend.governance_system.constitutional_engine import constitutional_engine
    
    result = await constitutional_engine.validate_event(event)
    
    return result.approved

trigger_mesh.set_governance_validator(validate_constitutional)
```

#### Trust Score Enforcement

```python
# Register trust scorer
async def get_component_trust_score(component_id: str) -> float:
    """Get trust score for a component"""
    
    from backend.trust_framework.trust_score import get_trust_score
    
    score = await get_trust_score(component_id)
    
    return score.composite_score

trigger_mesh.set_trust_scorer(get_component_trust_score)
```

## Configuration Format

### Event Definition

```yaml
- event_type: governance.policy_violation
  description: Policy violation detected
  publishers:
    - constitutional_engine
    - verification_kernel
    - governance_engine
  subscribers:
    - alert_system
    - immutable_log
    - governance_dashboard
    - parliament_engine
  requires_constitutional_validation: true
  min_trust_score: 0.9
```

### Routing Rules

```yaml
routing_rules:
  # High priority events
  priority_events:
    - health.critical
    - governance.policy_violation
    - verification.security_violation
  
  # Events requiring audit logging
  audit_events:
    - governance.policy_violation
    - governance.decision_made
    - avn.healing_action
  
  # Events triggering alerts
  alert_events:
    - health.critical
    - verification.security_violation
    - avn.healing_failed
```

### Subscriber Groups

```yaml
subscriber_groups:
  governance:
    - constitutional_engine
    - governance_engine
    - verification_kernel
    - parliament_engine
  
  healing:
    - self_heal_engine
    - alert_system
    - auto_fix_engine
```

## Usage Examples

### Basic Event Emission

```python
from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent
from datetime import datetime

# Start the mesh
await trigger_mesh.start()

# Emit an event
event = TriggerEvent(
    event_type="task.completed",
    source="task_executor",
    actor="user_123",
    resource="task_456",
    payload={
        "duration_seconds": 12.5,
        "result": "success"
    }
)

await trigger_mesh.emit(event)
```

### Registering Component Handlers

```python
# Define a handler for a specific component
async def handle_governance_events(event: TriggerEvent):
    """Handle events routed to governance_engine"""
    
    if event.event_type == "governance.approval_required":
        # Process approval request
        from backend.governance_system.governance_engine import governance_engine
        await governance_engine.process_approval_request(event)

# Register the handler
trigger_mesh.register_component_handler(
    component_id="governance_engine",
    handler=handle_governance_events
)
```

### Pattern-Based Subscriptions

```python
# Subscribe to all governance events
async def on_governance_event(event: TriggerEvent):
    print(f"Governance event: {event.event_type}")

await trigger_mesh.subscribe("governance.*", on_governance_event)

# Subscribe to all events
await trigger_mesh.subscribe("*", log_all_events)
```

### High-Trust Event Emission

```python
# Event requiring high trust score
event = TriggerEvent(
    event_type="governance.policy_changed",
    source="governance_engine",
    actor="admin",
    resource="policy:security",
    payload={
        "old_policy": {"min_approval": 2},
        "new_policy": {"min_approval": 3}
    },
    trust_score=0.95,  # High trust
    requires_validation=True  # Explicit validation request
)

await trigger_mesh.emit(event)
```

### Handling Validation Failures

Events that fail validation are:
1. Blocked from routing
2. Logged to immutable log with block reason
3. Not dispatched to targets
4. Counted in `events_blocked` statistic

```python
# This event will be blocked (trust score too low)
event = TriggerEvent(
    event_type="governance.policy_changed",  # Requires 0.95 trust
    source="untrusted_component",
    actor="unknown",
    resource="policy:security",
    payload={},
    trust_score=0.5  # Too low!
)

await trigger_mesh.emit(event)
# Output: ⚠ Event blocked by trust score check: governance.policy_changed (score: 0.5)
```

## Integration with Governance

### Complete Example

```python
from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent
from backend.governance_system.constitutional_engine import constitutional_engine
from backend.trust_framework.trust_score import get_trust_score

# Initialize trigger mesh
trigger_mesh.load_config()

# Set up constitutional validation
async def validate_against_constitution(event: TriggerEvent) -> bool:
    """Validate event against Grace's constitutional principles"""
    
    result = await constitutional_engine.validate_action(
        actor=event.actor,
        action=event.event_type,
        resource=event.resource,
        context=event.payload
    )
    
    if not result.approved:
        # Log constitutional violation
        from backend.logging.governance_logger import governance_logger
        
        await governance_logger.log_constitutional_violation(
            violation_id=event.event_id,
            actor=event.actor,
            violated_principle=result.violated_principle,
            violation_details=result.reasoning,
            action_taken="Event blocked by trigger mesh"
        )
    
    return result.approved

trigger_mesh.set_governance_validator(validate_against_constitution)

# Set up trust scoring
async def get_component_trust(component_id: str) -> float:
    """Get trust score for component"""
    
    trust_score = await get_trust_score(component_id)
    return trust_score.composite_score

trigger_mesh.set_trust_scorer(get_component_trust)

# Start routing
await trigger_mesh.start()
```

## Integration with Verification

```python
from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent
from backend.logging.verification_logger import verification_logger

# Register verification event handler
async def handle_verification_results(event: TriggerEvent):
    """Handle verification result events"""
    
    if event.event_type == "verification.refuted":
        # Log refutation
        await verification_logger.log_refutation(
            hypothesis_id=event.payload.get('hypothesis_id'),
            actor=event.actor,
            refutation_reason=event.payload.get('reason'),
            evidence=event.payload.get('evidence', []),
            severity=event.payload.get('severity', 'medium')
        )
    
    elif event.event_type == "verification.security_violation":
        # Log security violation
        await verification_logger.log_security_violation(
            code_id=event.payload.get('code_id'),
            actor=event.actor,
            violation_type=event.payload.get('violation_type'),
            violation_details=event.payload.get('details'),
            dangerous_patterns=event.payload.get('dangerous_patterns', []),
            action_taken="Code blocked by verification system"
        )

trigger_mesh.register_component_handler(
    component_id="verification_system",
    handler=handle_verification_results
)
```

## Integration with AVN

```python
from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent
from backend.logging.avn_logger import avn_logger

# Emit anomaly detection event
async def emit_anomaly(anomaly_id: str, anomaly_data: dict):
    """Emit anomaly detection event"""
    
    event = TriggerEvent(
        event_type="avn.anomaly_detected",
        source="htm_detector",
        actor="avn_system",
        resource=f"anomaly:{anomaly_id}",
        payload=anomaly_data,
        trust_score=0.85
    )
    
    await trigger_mesh.emit(event)
    
    # Also log to immutable log
    await avn_logger.log_anomaly_detected(
        anomaly_id=anomaly_id,
        detector="htm_detector",
        anomaly_type=anomaly_data.get('type'),
        severity=anomaly_data.get('severity'),
        affected_resource=anomaly_data.get('resource'),
        anomaly_score=anomaly_data.get('score'),
        details=anomaly_data
    )

# Emit healing action event
async def emit_healing_action(healing_id: str, healing_data: dict):
    """Emit self-healing action event"""
    
    # This requires constitutional validation (min_trust_score: 0.85)
    event = TriggerEvent(
        event_type="avn.healing_action",
        source="self_heal_engine",
        actor="avn_healer",
        resource=f"healing:{healing_id}",
        payload=healing_data,
        trust_score=0.9,
        requires_validation=True
    )
    
    await trigger_mesh.emit(event)
```

## Priority Event Handling

Priority events are processed before normal events:

```python
# Priority events (from config)
priority_events = [
    'health.critical',
    'system.boot.failed',
    'governance.policy_violation',
    'verification.security_violation',
    'avn.rollback_required'
]

# Priority event gets immediate attention
event = TriggerEvent(
    event_type="health.critical",  # Priority!
    source="health_monitor",
    actor="system",
    resource="component:database",
    payload={
        "error": "Connection pool exhausted",
        "severity": "critical"
    }
)

await trigger_mesh.emit(event)
# Routed through priority_queue for immediate processing
```

## Statistics & Monitoring

```python
# Get routing statistics
stats = trigger_mesh.get_stats()

# Example output:
{
    'events_routed': 1543,
    'events_blocked': 12,
    'events_validated': 87,
    'routing_rules': 45,
    'component_handlers': 8,
    'subscribers': 23
}
```

## Audit Trail

All events marked for audit are automatically logged to the immutable log:

```yaml
audit_events:
  - governance.policy_violation
  - governance.decision_made
  - verification.security_violation
  - avn.healing_action
```

Query audit trail:

```python
from backend.logging.immutable_log import immutable_log

# Get all governance events
entries = await immutable_log.get_entries(
    subsystem="governance_engine",
    limit=100
)

# Get specific action
entries = await immutable_log.get_entries(
    action="governance.policy_violation",
    limit=50
)
```

## Event Categories

### High-Security Events (Require Validation)
- `governance.*` - All governance decisions
- `verification.security_violation` - Security threats
- `avn.healing_action` - System modifications
- `avn.rollback_required` - Version control
- `health.critical` - Critical failures
- `learning.model_updated` - ML model changes

### High-Trust Events (min_trust_score ≥ 0.9)
- `governance.policy_changed` - Policy modifications
- `governance.decision_made` - Governance outcomes
- `avn.rollback_required` - Rollback decisions

### Priority Events (Immediate Processing)
- `health.critical` - Critical health issues
- `system.boot.failed` - Boot failures
- `governance.policy_violation` - Policy violations
- `verification.security_violation` - Security violations
- `avn.rollback_required` - Rollback requests

## Best Practices

### 1. Event Naming
Use hierarchical dot notation:
- `{domain}.{action}` (e.g., `governance.approval_required`)
- Domains: `governance`, `verification`, `avn`, `health`, `task`, `memory`

### 2. Trust Scores
- System components: 0.9+
- Governance components: 0.95+
- User-facing components: 0.7+
- External integrations: 0.5+

### 3. Validation
Only require constitutional validation for:
- Policy changes
- System modifications
- Security-critical actions
- Model updates

### 4. Payload Design
Keep payloads focused and JSON-serializable:
```python
# Good
payload = {
    "action": "approve",
    "reasoning": "All checks passed",
    "metadata": {"key": "value"}
}

# Avoid
payload = {
    "entire_state": {...},  # Too large
    "object": some_object    # Not JSON-serializable
}
```

## Migration from Legacy Mesh

The enhanced trigger mesh is backward compatible:

```python
# Old code (still works)
from backend.misc.trigger_mesh import trigger_mesh

await trigger_mesh.subscribe("governance.*", handler)
await trigger_mesh.publish(event)

# New code (recommended)
from backend.routing.trigger_mesh_enhanced import trigger_mesh

trigger_mesh.load_config()
trigger_mesh.register_component_handler("my_component", handler)
await trigger_mesh.emit(event)
```

## Summary

The Trigger Mesh provides:

1. **Phase 1: YAML-based routing** - Declarative configuration loaded into in-memory routing map
2. **Phase 2: Event dispatch** - Intelligent routing to target components with priority handling
3. **Phase 3: Constitutional hooks** - Validation and trust score enforcement before routing

All three phases are **fully implemented** with:
- ✅ Real YAML loading and parsing
- ✅ In-memory routing map normalization
- ✅ Constitutional validation hooks
- ✅ Trust score enforcement
- ✅ Priority event queues
- ✅ Audit logging integration
- ✅ Alert emission
- ✅ Complete configuration
- ✅ Zero stubs or placeholders

The system acts as Grace's constitutional "wiring harness", ensuring all events flow through proper validation channels before reaching their targets.
