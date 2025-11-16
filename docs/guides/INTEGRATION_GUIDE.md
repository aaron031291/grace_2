# Domain System Integration Guide

## Current State vs New Architecture

### What You Have NOW (Running on 8017)
```
Grace (Port 8017)
├── All routes together
├── All services in one process
├── Guardian monitoring
├── Port watchdog
├── Network healing playbooks ✓
├── Kernel port manager ✓
└── Working perfectly!
```

### What We Just Built (NEW)
```
Domain System (NEW modules)
├── Domain Registry
├── Event Bus
├── Shared Memory
├── Domain Orchestrator
└── 30+ API endpoints
```

---

## Integration Strategy: INCREMENTAL

**Don't replace anything! Just ADD the domain system.**

### Phase 1: Add Domain System to Existing Grace (Week 1)

**Step 1: Register domain system in main API**

```python
# File: backend/main.py
# Add these imports at the top

from backend.routes.domain_system_api import router as domain_system_router
from backend.domains import initialize_domain_system

# Add the router
app.include_router(domain_system_router)

# In startup event, add initialization
@app.on_event("startup")
async def startup():
    # ... existing startup code ...
    
    # NEW: Initialize domain system
    await initialize_domain_system()
    print("[OK] Domain system initialized")
```

**That's it!** Domain system is now available at:
- `http://localhost:8017/domains/*`

---

### Phase 2: Register Current Components as "Domains" (Week 2)

**Make existing kernels/services discoverable**

```python
# File: backend/core/guardian.py
# In Guardian's boot() method, add:

async def boot(self):
    # ... existing guardian boot code ...
    
    # NEW: Register Guardian as a domain
    from backend.domains import domain_registry
    
    await domain_registry.register_domain({
        'domain_id': 'guardian_domain',
        'port': self.port,  # Port Guardian is on
        'capabilities': [
            'network_healing',
            'port_monitoring', 
            'auto_remediation',
            'health_checking'
        ]
    })
    
    # ... rest of boot code ...
```

**Do this for each major component:**

```python
# Register existing systems as domains
components_to_register = [
    {
        'domain_id': 'core_api',
        'port': 8017,
        'capabilities': ['all_routes', 'main_api']
    },
    {
        'domain_id': 'guardian',
        'port': guardian_port,
        'capabilities': ['healing', 'monitoring']
    },
    {
        'domain_id': 'librarian',
        'port': 8130,  # When we move it to dedicated port
        'capabilities': ['search', 'indexing', 'knowledge']
    }
    # ... etc
]
```

**Result:** Existing components now appear in domain registry!

---

### Phase 3: Use Event Bus for Existing Communication (Week 3)

**Replace direct calls with events**

**Before (direct call):**
```python
# In some API route
from backend.self_heal.network_healing_playbooks import network_playbook_registry

# Direct call
result = await network_playbook_registry.heal(issue)
```

**After (event-driven):**
```python
# In some API route
from backend.domains import domain_event_bus, DomainEvent

# Publish event
await domain_event_bus.publish(DomainEvent(
    event_type='healing.needed',
    source_domain='core_api',
    data={'issue': issue},
    timestamp=datetime.utcnow().isoformat(),
    event_id='...'
))

# Guardian (subscribed to 'healing.*') automatically receives it
# and triggers healing!
```

**Guardian subscribes on startup:**
```python
# In Guardian boot
from backend.domains import domain_event_bus

# Subscribe to healing events
domain_event_bus.subscribe('guardian', 'healing.*')
domain_event_bus.subscribe('guardian', 'port.*')
domain_event_bus.subscribe('guardian', 'error.critical')
```

---

### Phase 4: Use Shared Memory for Learnings (Week 4)

**Guardian contributes healing outcomes**

```python
# In network_healer_integration.py
# After successful healing

from backend.domains import shared_domain_memory

await shared_domain_memory.contribute(
    domain_id='guardian',
    contribution_type='optimization',
    content={
        'issue_type': 'port_timeout',
        'playbook_used': 'restart_component',
        'success': True,
        'time_to_resolve': 5.2
    },
    tags=['healing', 'network', 'success']
)
```

**Now ANY component can learn from Guardian's experience:**

```python
# In AI domain or anywhere
from backend.domains import shared_domain_memory

# Query what worked for port timeouts
insights = await shared_domain_memory.query_collective(
    query='port timeout',
    contribution_type='optimization',
    min_confidence=0.8
)

# Use insights to avoid issues or fix faster!
```

---

## Concrete Integration Examples

### Example 1: Guardian + Event Bus

**File: `backend/core/guardian.py`**

```python
# Add at top
from backend.domains import domain_event_bus, domain_registry, DomainEvent
from datetime import datetime

class Guardian:
    async def boot(self):
        # ... existing boot code ...
        
        # NEW: Register as domain
        await domain_registry.register_domain({
            'domain_id': 'guardian',
            'port': self.port,
            'capabilities': ['healing', 'monitoring', 'port_watchdog']
        })
        
        # NEW: Subscribe to events
        domain_event_bus.subscribe('guardian', 'healing.*')
        domain_event_bus.subscribe('guardian', 'error.*')
        domain_event_bus.subscribe('guardian', 'port.*')
        
        # NEW: Add event handler
        domain_event_bus.add_local_handler(
            'healing.needed',
            self._handle_healing_event
        )
        
        # ... existing boot code continues ...
    
    async def _handle_healing_event(self, event: DomainEvent):
        """Handle healing events from event bus"""
        issue = event.data.get('issue')
        
        # Trigger existing healing logic
        from backend.core.network_healer_integration import network_healer
        
        result = await network_healer.heal_component(
            component_name=issue['component'],
            issue_type=issue['type']
        )
        
        # Publish result
        await domain_event_bus.publish(DomainEvent(
            event_type='healing.completed',
            source_domain='guardian',
            data={'result': result},
            timestamp=datetime.utcnow().isoformat(),
            event_id=''
        ))
```

---

### Example 2: Network Healer + Shared Memory

**File: `backend/core/network_healer_integration.py`**

```python
# Add at top
from backend.domains import shared_domain_memory

class NetworkHealerIntegration:
    async def heal_component(self, component_name: str, issue_type: str, severity: str):
        # ... existing healing code ...
        
        # After healing completes
        if result.get('success'):
            # NEW: Contribute to shared memory
            await shared_domain_memory.contribute(
                domain_id='network_healer',
                contribution_type='pattern_success',
                content={
                    'component': component_name,
                    'issue_type': issue_type,
                    'severity': severity,
                    'playbooks_used': result['healing_result']['playbooks_executed'],
                    'time_to_resolve': time_taken,
                    'success': True
                },
                tags=['healing', 'network', component_name],
                confidence=1.0
            )
        
        # ... existing code continues ...
```

---

### Example 3: Port Manager + Domain Registry

**File: `backend/core/kernel_port_manager.py`**

```python
# Add at top
from backend.domains import domain_registry

class KernelPortManager:
    async def initialize(self):
        """Initialize and register all kernel ports as domains"""
        
        # Register port manager itself
        await domain_registry.register_domain({
            'domain_id': 'port_manager',
            'port': 8000,
            'capabilities': ['port_allocation', 'health_monitoring']
        })
        
        # Register each kernel as a domain
        for kernel_name, assignment in self.port_assignments.items():
            await domain_registry.register_domain({
                'domain_id': kernel_name,
                'port': assignment.port,
                'capabilities': self._get_kernel_capabilities(kernel_name)
            })
        
        print(f"[PORT-MANAGER] Registered {len(self.port_assignments)} kernels as domains")
    
    def _get_kernel_capabilities(self, kernel_name: str) -> List[str]:
        """Map kernel to capabilities"""
        capability_map = {
            'librarian_kernel': ['search', 'indexing', 'knowledge'],
            'self_healing_kernel': ['auto_healing', 'diagnostics'],
            'coding_agent_kernel': ['code_analysis', 'code_generation'],
            # ... etc
        }
        return capability_map.get(kernel_name, [])
```

---

## Migration Path - NO Breaking Changes!

### Week 1: Foundation
✅ Add domain system to main.py
✅ Domain APIs available at `/domains/*`
✅ System works exactly as before
✅ **No changes to existing functionality**

### Week 2: Registration
✅ Register Guardian as domain
✅ Register Port Manager as domain
✅ Register Network Healer as domain
✅ **Still works exactly as before**
✅ **Bonus: Can now see all components in registry**

### Week 3: Events (Optional)
✅ Guardian subscribes to events
✅ Start publishing healing events
✅ **Old direct calls still work**
✅ **New event-driven calls also work**
✅ **Both coexist peacefully**

### Week 4: Shared Learning (Optional)
✅ Contribute healing outcomes
✅ Query collective knowledge
✅ **Gradual adoption**
✅ **Use where it makes sense**

---

## File Changes Required

### Minimal Integration (Just Add APIs)

**1. Edit: `backend/main.py`**
```python
# Add these 3 lines:
from backend.routes.domain_system_api import router as domain_system_router
app.include_router(domain_system_router)

# In startup event:
from backend.domains import initialize_domain_system
await initialize_domain_system()
```

**That's it!** Domain system is live at `/domains/*`

---

### Full Integration (Event-Driven)

**2. Edit: `backend/core/guardian.py`**
```python
# Add domain registration + event subscription (~10 lines)
```

**3. Edit: `backend/core/network_healer_integration.py`**
```python
# Add shared memory contributions (~5 lines)
```

**4. Edit: `backend/core/kernel_port_manager.py`**
```python
# Add domain registration for kernels (~15 lines)
```

**Total changes: ~30 lines across 4 files**

---

## What You Get Immediately

### After Week 1 (Minimal Integration)
```bash
# New endpoints available
curl http://localhost:8017/domains/list
curl http://localhost:8017/domains/system/overview
curl http://localhost:8017/domains/events/stats
curl http://localhost:8017/domains/memory/stats
```

### After Week 2 (Registration)
```bash
# See all your components
curl http://localhost:8017/domains/list

# Output:
{
  "domains": [
    {"domain_id": "guardian", "port": 8017, "health": "healthy"},
    {"domain_id": "port_manager", "port": 8000, "health": "healthy"},
    {"domain_id": "network_healer", "port": 8000, "health": "healthy"}
  ]
}
```

### After Week 3 (Events)
```bash
# See event flow
curl http://localhost:8017/domains/events/history

# Output:
{
  "events": [
    {"type": "healing.needed", "source": "guardian"},
    {"type": "healing.completed", "source": "network_healer"},
    {"type": "port.health_check", "source": "port_manager"}
  ]
}
```

### After Week 4 (Learning)
```bash
# Query collective knowledge
curl "http://localhost:8017/domains/memory/query?query=port+timeout"

# Output:
{
  "results": [
    {
      "from_domain": "guardian",
      "type": "optimization",
      "content": {
        "issue": "port_timeout",
        "solution": "restart_component",
        "success_rate": 0.95
      }
    }
  ]
}
```

---

## Backwards Compatibility

**100% backwards compatible!**

### Old way still works:
```python
# Direct call (existing code)
await network_healer.heal_component(...)
```

### New way also works:
```python
# Event-driven (new code)
await domain_event_bus.publish(DomainEvent(...))
```

**Both coexist!** Migrate gradually.

---

## Testing the Integration

### Step 1: Add domain system (5 minutes)
```python
# Edit backend/main.py
from backend.routes.domain_system_api import router as domain_system_router
app.include_router(domain_system_router)
```

### Step 2: Restart Grace
```bash
python serve.py
```

### Step 3: Test new endpoints
```bash
curl http://localhost:8017/domains/system/health
```

**If you see JSON response, it worked!**

---

## Summary

### What Changes
✅ **Add** domain system modules (new files)
✅ **Add** domain API routes (1 line in main.py)
✅ **Add** domain registration calls (optional, ~30 lines)

### What Stays the Same
✅ All existing routes work
✅ All existing functionality works
✅ Guardian still monitors
✅ Network healing still works
✅ Port manager still works
✅ **Nothing breaks!**

### What You Gain
✅ Domain registry (see all components)
✅ Event bus (event-driven communication)
✅ Shared memory (collective learning)
✅ Orchestrator (multi-component workflows)
✅ Full observability
✅ Future-ready architecture

---

## Recommended Approach

**Start simple, add gradually:**

1. **This week:** Add domain APIs (1 line change)
2. **Next week:** Register Guardian (10 lines)
3. **Following week:** Try event bus (where it makes sense)
4. **Ongoing:** Use shared memory (as you see value)

**No rush. No pressure. Incremental adoption.**

The domain system is **additive**, not **replacement**! 🎯
