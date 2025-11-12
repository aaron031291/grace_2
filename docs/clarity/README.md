# Grace Clarity Framework Documentation

## Overview

The Clarity Framework provides standardized patterns for component lifecycle, event routing, loop tracking, and trust management across the entire Grace AI system.

**Version:** 1.0  
**Status:** Production Ready  
**Location:** `backend/clarity/`

## Quick Start

### 1. Creating a Clarity-Compatible Component

```python
from backend.clarity import (
    BaseComponent,
    ComponentStatus,
    get_event_bus,
    Event,
    get_manifest,
    TrustLevel
)

class MyComponent(BaseComponent):
    def __init__(self):
        super().__init__()
        self.component_type = "my_component"
        self.event_bus = get_event_bus()
    
    async def activate(self) -> bool:
        """Start the component"""
        self.set_status(ComponentStatus.ACTIVATING)
        
        # Register with manifest
        manifest = get_manifest()
        manifest.register(
            self,
            trust_level=TrustLevel.MEDIUM,
            role_tags=["my_role", "optional_tag"]
        )
        
        # Initialize your component
        # ...
        
        self.set_status(ComponentStatus.ACTIVE)
        
        # Publish activation event
        await self.event_bus.publish(Event(
            event_type="component.activated",
            source=self.component_id,
            payload={"component_type": self.component_type}
        ))
        
        return True
    
    async def deactivate(self) -> bool:
        """Stop the component"""
        self.set_status(ComponentStatus.DEACTIVATING)
        
        # Cleanup
        # ...
        
        # Unregister
        get_manifest().unregister(self.component_id)
        
        self.set_status(ComponentStatus.STOPPED)
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Return component status"""
        return {
            "status": self.status.value,
            "component_id": self.component_id,
            "component_type": self.component_type
        }
```

### 2. Publishing and Subscribing to Events

```python
from backend.clarity import get_event_bus, Event

bus = get_event_bus()

# Subscribe
async def my_handler(event: Event):
    print(f"Received: {event.event_type}")
    print(f"Payload: {event.payload}")

bus.subscribe("system.boot.completed", my_handler)

# Publish
await bus.publish(Event(
    event_type="system.boot.completed",
    source="orchestrator",
    payload={"duration_ms": 1234}
))
```

### 3. Using GraceLoopOutput for Cognitive Loops

```python
from backend.clarity import GraceLoopOutput

# Create loop output
output = GraceLoopOutput(
    loop_type="reasoning",
    component_id=self.component_id
)

# Track execution
try:
    result = await perform_reasoning()
    output.mark_completed(
        results=result,
        confidence=0.95
    )
except Exception as e:
    output.mark_failed(str(e))

# Publish as event
await bus.publish(Event(
    event_type="loop.completed",
    source=self.component_id,
    payload={"loop_output": output.to_dict()}
))
```

## Core Concepts

### 1. BaseComponent

All Grace components should inherit from `BaseComponent` to ensure:
- Consistent lifecycle management (`activate`, `deactivate`)
- Standardized status reporting (`get_status`)
- UUID-based identity
- Configuration and metadata tracking

**Status States:**
- `CREATED` - Component instantiated
- `ACTIVATING` - Starting up
- `ACTIVE` - Running normally
- `PAUSED` - Temporarily suspended
- `DEACTIVATING` - Shutting down
- `STOPPED` - Fully stopped
- `ERROR` - Error state

### 2. EventBus

Pub/sub messaging system for decoupled communication:
- Async handler support
- Event history tracking (last 1000 events)
- Type-safe event structure
- Global singleton via `get_event_bus()`

### 3. GraceLoopOutput

Standardized output for all cognitive loops:
- Unique loop ID and reasoning chain tracking
- Parent/child loop relationships
- Confidence scoring
- Duration tracking
- Serializable to dict

### 4. ComponentManifest

Central registry for all active components:
- Trust level management (UNTRUSTED → VERIFIED)
- Role-based queries
- Active component tracking
- Heartbeat monitoring

**Trust Levels:**
- `UNTRUSTED` (0) - New/unknown
- `LOW` (1) - Basic validation
- `MEDIUM` (2) - Tested, limited scope
- `HIGH` (3) - Well-tested, important functions
- `VERIFIED` (4) - Critical, fully audited

## Trigger Mesh Configuration

Event routing is defined in `backend/clarity/trigger_mesh.yaml`:

```yaml
events:
  - event_type: component.activated
    description: A component has been activated
    publishers:
      - any_component
    subscribers:
      - component_manifest
      - metrics_collector
      - health_monitor
```

**23 Event Types Defined:**
- System lifecycle
- Component lifecycle
- Cognitive loops
- Memory operations
- Task execution
- Governance
- Health monitoring
- Learning
- Configuration

## API Endpoints

### GET /api/clarity/status
Get clarity framework statistics:
```json
{
  "event_bus": {
    "total_events": 42,
    "subscriber_count": 15,
    "event_types": [...]
  },
  "manifest": {
    "total_components": 8,
    "active_components": 6,
    "trust_distribution": {...}
  }
}
```

### GET /api/clarity/components
Get all registered components from manifest

### GET /api/clarity/events?limit=100
Get recent event history

### GET /api/clarity/mesh
Get trigger mesh configuration

## Testing

### Run Smoke Test
```bash
python scripts/test_clarity_smoke.py
```

### Run Full Test Suite
```bash
python -m pytest tests/test_clarity_framework.py -v
```

### Test Example Component
```bash
python -m backend.clarity.example_component
```

## Examples

### Health Monitor
See `backend/health/clarity_health_monitor.py` for a production example showing:
- BaseComponent inheritance
- Event publishing
- Manifest registration
- GraceLoopOutput usage
- Periodic health checks

### Run Health Monitor Demo
```bash
python -m backend.health.clarity_health_monitor
```

## Integration Checklist

When creating a new Grace component:

- [ ] Inherit from `BaseComponent`
- [ ] Implement required methods (`activate`, `deactivate`, `get_status`)
- [ ] Register with manifest on activation
- [ ] Publish lifecycle events
- [ ] Use `GraceLoopOutput` for cognitive operations
- [ ] Subscribe to relevant events
- [ ] Add to trigger mesh configuration if needed

## Best Practices

1. **Always use async/await** for lifecycle methods
2. **Handle exceptions gracefully** - set ERROR status and publish events
3. **Clean up resources** in deactivate()
4. **Use trust levels appropriately** - start low, earn high
5. **Publish meaningful events** - include useful payload data
6. **Track reasoning chains** - use parent_loop_id for nested operations
7. **Keep event history lean** - EventBus stores last 1000 only

## Troubleshooting

### Component not appearing in manifest
- Check if `register()` was called during activation
- Verify manifest wasn't cleared
- Ensure component status is ACTIVE

### Events not being received
- Verify subscription before publishing
- Check event_type spelling matches exactly
- Confirm handler is async if event handling requires it

### Import errors
```python
# Wrong
from backend.clarity.base_component import BaseComponent

# Right  
from backend.clarity import BaseComponent
```

## Future Enhancements (Classes 5-10)

Planned additions when subsystems are stable:
- **Class 5:** Memory trust scoring with decay models
- **Class 6:** Constitutional governance enforcement
- **Class 7:** Loop feedback integration to memory
- **Class 8:** Specialist consensus and quorum logic
- **Class 9:** Output format standardization across interfaces
- **Class 10:** Contradiction detection and drift monitoring

## Support

- Framework source: `backend/clarity/`
- Tests: `tests/test_clarity_framework.py`
- Examples: `backend/clarity/example_component.py`
- Health Monitor: `backend/health/clarity_health_monitor.py`

For questions or issues, consult the code comments or run the smoke test for validation.
