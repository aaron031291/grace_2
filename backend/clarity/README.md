# Grace Clarity Framework

Standardized component architecture for consistent lifecycle, events, and outputs across all Grace subsystems.

## Overview

The Clarity Framework provides 4 foundational scaffolds that solve ambiguity problems in complex AI systems:

### Class 1: Structural Clarity (`base_component.py`)
**Problem:** Inconsistent component definitions and unclear lifecycle methods  
**Solution:** All components inherit from `BaseComponent` with enforced methods:
- `activate()` - Start the component
- `deactivate()` - Clean shutdown
- `get_status()` - Health and metrics reporting

```python
from backend.clarity import BaseComponent, ComponentStatus

class MyGraceComponent(BaseComponent):
    def __init__(self):
        super().__init__()
        self.component_type = "my_component"
    
    async def activate(self) -> bool:
        self.set_status(ComponentStatus.ACTIVATING)
        # initialization logic
        self.set_status(ComponentStatus.ACTIVE)
        return True
    
    async def deactivate(self) -> bool:
        self.set_status(ComponentStatus.DEACTIVATING)
        # cleanup logic
        self.set_status(ComponentStatus.STOPPED)
        return True
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "component_id": self.component_id,
            "uptime": (datetime.utcnow() - self.created_at).total_seconds()
        }
```

### Class 2: Signal Routing Clarity (`event_bus.py`)
**Problem:** Unclear who listens/responds to events  
**Solution:** Pub/sub event bus with typed events

```python
from backend.clarity import EventBus, Event, get_event_bus

bus = get_event_bus()

# Subscribe to events
async def handle_config_change(event: Event):
    print(f"Config changed: {event.payload}")

bus.subscribe("config.changed", handle_config_change)

# Publish events
await bus.publish(Event(
    event_type="config.changed",
    source="my_component",
    payload={"setting": "debug", "value": True}
))
```

### Class 3: Loop Identity Clarity (`loop_output.py`)
**Problem:** No clarity on which loop executed or how to track results  
**Solution:** Standardized `GraceLoopOutput` for all cognitive loops

```python
from backend.clarity import GraceLoopOutput

# Create loop output
output = GraceLoopOutput(
    loop_type="reasoning",
    component_id="reasoning_engine_001"
)

# Track execution
output.mark_completed(
    results={"decision": "approve", "reasoning": ["fact1", "fact2"]},
    confidence=0.92
)

# Serialize for storage/API
loop_data = output.to_dict()
```

### Class 4: Subsystem Activation Clarity (`component_manifest.py`)
**Problem:** Components instantiated but not tracked or trusted  
**Solution:** Central registry with trust flags and lifecycle state

```python
from backend.clarity import GraceComponentManifest, TrustLevel, get_manifest

manifest = get_manifest()

# Register component
manifest.register(
    my_component,
    trust_level=TrustLevel.VERIFIED,
    role_tags=["memory", "core"]
)

# Query active components
active = manifest.get_active_components()
memory_components = manifest.get_components_by_role("memory")
trusted = manifest.get_components_by_trust(TrustLevel.HIGH)
```

## Integration Guidelines

### For New Components
1. Inherit from `BaseComponent`
2. Implement required lifecycle methods
3. Register with manifest on startup
4. Publish events via event bus
5. Return `GraceLoopOutput` for cognitive operations

### For Existing Components
1. Wrap existing classes (don't rewrite immediately)
2. Add clarity scaffolds alongside current patterns
3. Gradually migrate to full compliance
4. Use clarity for all new features

## Future Classes (5-10)

The framework will expand to include:
- **Class 5:** Memory scoring with trust + decay models
- **Class 6:** Constitutional governance enforcement
- **Class 7:** Loop feedback integration
- **Class 8:** Specialist consensus + quorum
- **Class 9:** Output standardization across interfaces
- **Class 10:** Contradiction detection + drift monitoring

## Usage in Orchestrator

```python
from backend.clarity import get_manifest, get_event_bus, BaseComponent

class GraceOrchestrator:
    def __init__(self):
        self.manifest = get_manifest()
        self.event_bus = get_event_bus()
    
    async def register_component(self, component: BaseComponent):
        # Register in manifest
        self.manifest.register(component, trust_level=TrustLevel.MEDIUM)
        
        # Activate component
        success = await component.activate()
        
        if success:
            self.manifest.update_status(component.component_id, active=True)
            
            # Publish activation event
            await self.event_bus.publish(Event(
                event_type="component.activated",
                source="orchestrator",
                payload={"component_id": component.component_id}
            ))
```

## Benefits

✅ **Uniformity** - Every component shares common interface  
✅ **Traceability** - Events and loops are traceable by ID  
✅ **Autonomy** - Required foundation for autonomous operation  
✅ **Meta-Learning** - Standard outputs enable trust scoring  
✅ **Developer Clarity** - Shared expectations across team  

## Next Steps

1. Use clarity scaffolds for all new Grace components
2. Test with existing orchestrator stages
3. Add clarity validation to boot pipeline
4. Expose clarity data in dashboards/APIs
5. Implement classes 5-10 when subsystems are stable
