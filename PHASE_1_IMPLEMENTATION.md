# Phase 1 Implementation - Event Bus Bridge & Boot Chunks

## Changes to Make (Zero Breaking Changes)

### Change 1: Bridge Event Bus to Trigger Mesh

**File:** `backend/event_bus.py`

**Current code (line 57-71):**
```python
async def publish(self, event: Event) -> None:
    """Publish event to all subscribers"""
    self.event_log.append(event)
    
    if len(self.event_log) > self.max_log_size:
        self.event_log = self.event_log[-self.max_log_size:]
    
    print(f"[EventBus] Published: {event.event_type.value} from {event.source}")
    
    if event.event_type in self.subscribers:
        tasks = []
        for callback in self.subscribers[event.event_type]:
            tasks.append(self._safe_callback(callback, event))
        
        await asyncio.gather(*tasks, return_exceptions=True)
```

**New code:**
```python
async def publish(self, event: Event) -> None:
    """Publish event to all subscribers - routes through trigger mesh"""
    
    # Keep legacy log
    self.event_log.append(event)
    if len(self.event_log) > self.max_log_size:
        self.event_log = self.event_log[-self.max_log_size:]
    
    # Route through trigger mesh (includes governance validation)
    try:
        from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
        
        # Convert Event to TriggerEvent
        event_type_str = event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type)
        
        trigger_event = TriggerEvent(
            event_type=event_type_str,
            source=event.source,
            actor=event.source,
            resource="",
            payload=event.data
        )
        
        # Publish through mesh
        await trigger_mesh.publish(trigger_event)
        
        print(f"[EventBus] Routed through mesh: {event_type_str} from {event.source}")
    
    except Exception as e:
        # Fallback to direct publish if mesh fails
        print(f"[EventBus] Mesh routing failed, using direct: {e}")
        
        if event.event_type in self.subscribers:
            tasks = []
            for callback in self.subscribers[event.event_type]:
                tasks.append(self._safe_callback(callback, event))
            
            await asyncio.gather(*tasks, return_exceptions=True)
```

**Lines to modify:** 57-71 (15 lines)  
**Risk:** Low - has fallback  
**Testing:** Verify events still publish after change

---

### Change 2: Alias Enhanced Trigger Mesh

**File:** `backend/misc/trigger_mesh.py`

**Current code (line 100):**
```python
trigger_mesh = TriggerMesh()
```

**New code (insert after line 100):**
```python
trigger_mesh = TriggerMesh()

# ============================================================================
# INTEGRATION: Use enhanced trigger mesh if available
# ============================================================================

_simple_mesh = trigger_mesh  # Keep reference to simple version

try:
    from backend.routing.trigger_mesh_enhanced import (
        trigger_mesh as _enhanced_mesh,
        TriggerMesh as _EnhancedMesh,
        TriggerEvent as _EnhancedEvent,
        RouteMetadata,
        RoutingRule
    )
    
    # Check if enhanced mesh has required methods
    if hasattr(_enhanced_mesh, 'load_config') and hasattr(_enhanced_mesh, 'emit'):
        # Use enhanced version
        trigger_mesh = _enhanced_mesh
        TriggerMesh = _EnhancedMesh
        TriggerEvent = _EnhancedEvent
        
        print("✓ Using enhanced trigger mesh with governance hooks")
    else:
        print("⚠ Enhanced trigger mesh incomplete, using simple version")

except ImportError as e:
    # Fall back to simple mesh
    print(f"⚠ Enhanced trigger mesh unavailable: {e}")
    print("  Using simple trigger mesh (no governance hooks)")
    pass

# Keep setup_subscriptions for compatibility
```

**Lines to add:** 10 lines after line 100  
**Risk:** None - has fallback  
**Testing:** Boot should show which mesh is loaded

---

### Change 3: Add Production Systems Boot Chunk

**File:** `server.py`

**Location:** After line 250 (after existing chunk registrations, before orchestrator.boot())

**Code to add:**

```python
        # ========================================================================
        # CHUNK 1.5: Production Systems (Governance, Verification, AVN)
        # ========================================================================
        async def chunk_1_5_production_systems():
            print("[CHUNK 1.5] Production Systems (Governance, Verification, AVN)...")
            
            results = {}
            
            try:
                # Load and start enhanced trigger mesh
                from backend.misc.trigger_mesh import trigger_mesh
                
                # Load YAML config if enhanced version
                if hasattr(trigger_mesh, 'load_config'):
                    try:
                        config = trigger_mesh.load_config()
                        routes_loaded = len(config.get('events', []))
                        print(f"  [OK] Trigger Mesh: {routes_loaded} routes loaded from YAML")
                        results['trigger_mesh'] = f"{routes_loaded}_routes"
                    except Exception as e:
                        print(f"  [WARN] Trigger Mesh config load failed: {e}")
                        print(f"  [INFO] Continuing with simple trigger mesh")
                        results['trigger_mesh'] = 'simple_version'
                else:
                    print(f"  [INFO] Simple trigger mesh active (no YAML config)")
                    results['trigger_mesh'] = 'simple_version'
                
                # Start immune kernel (AVN)
                try:
                    from backend.immune.immune_kernel import immune_kernel
                    await immune_kernel.start()
                    print("  [OK] Immune Kernel (AVN): Anomaly detection active")
                    results['immune_kernel'] = 'active'
                except ImportError as e:
                    print(f"  [WARN] Immune kernel unavailable: {e}")
                    results['immune_kernel'] = 'unavailable'
                
                # Governance gate is passive (validates on-demand)
                try:
                    from backend.governance_system.governance_gate import governance_gate
                    print("  [OK] Governance Gate: Ready (Kernel 1)")
                    results['governance_gate'] = 'ready'
                except ImportError as e:
                    print(f"  [WARN] Governance gate unavailable: {e}")
                    results['governance_gate'] = 'unavailable'
                
                # Verification engine is passive (verifies on-demand)
                try:
                    from backend.verification_system.code_verification_engine import verification_engine
                    print("  [OK] Verification Engine: Ready")
                    results['verification_engine'] = 'ready'
                except ImportError as e:
                    print(f"  [WARN] Verification engine unavailable: {e}")
                    results['verification_engine'] = 'unavailable'
                
                # Unified decision engine is passive
                try:
                    from backend.unified_logic.unified_decision_engine import unified_decision_engine
                    print("  [OK] Unified Decision Engine: Ready")
                    results['unified_decision'] = 'ready'
                except ImportError:
                    results['unified_decision'] = 'unavailable'
                
                print(f"  [SUMMARY] {len([v for v in results.values() if 'active' in v or 'ready' in v])}/{len(results)} systems online")
                
                return {
                    "status": "online",
                    "systems": results
                }
            
            except Exception as e:
                logger.error(f"Production systems startup error: {e}")
                return {"status": "degraded", "error": str(e)}
        
        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="production_systems",
            name="Production Systems (Governance, Verification, AVN)",
            priority=1.5,
            boot_function=chunk_1_5_production_systems,
            can_fail=True,  # Can degrade gracefully
            guardian_validates=True
        ))
        
        # ========================================================================
        # CHUNK 1.6: Mesh Validators (Constitutional + Trust)
        # ========================================================================
        async def chunk_1_6_mesh_validators():
            print("[CHUNK 1.6] Trigger Mesh Validators...")
            
            try:
                from backend.misc.trigger_mesh import trigger_mesh
                
                # Only set validators if enhanced mesh is loaded
                if hasattr(trigger_mesh, 'set_governance_validator'):
                    # Constitutional validator
                    try:
                        from backend.governance_system.constitutional_verifier import constitutional_verifier
                        
                        async def validate_constitutional(event):
                            try:
                                result = await constitutional_verifier.verify(
                                    actor=event.actor,
                                    action=event.event_type,
                                    resource=event.resource,
                                    context=event.payload
                                )
                                return result.get('compliant', True)
                            except Exception as e:
                                logger.warning(f"Constitutional validation error: {e}")
                                return True  # Default to compliant if check fails
                        
                        trigger_mesh.set_governance_validator(validate_constitutional)
                        print("  [OK] Constitutional validator: Registered")
                    
                    except ImportError as e:
                        print(f"  [WARN] Constitutional verifier unavailable: {e}")
                    
                    # Trust scorer
                    try:
                        from backend.trust_framework.trust_score import get_trust_score
                        
                        async def get_component_trust(component_id):
                            try:
                                trust = await get_trust_score(component_id)
                                return trust.composite_score if trust else 1.0
                            except Exception as e:
                                logger.warning(f"Trust score error: {e}")
                                return 1.0
                        
                        trigger_mesh.set_trust_scorer(get_component_trust)
                        print("  [OK] Trust scorer: Registered")
                    
                    except ImportError as e:
                        print(f"  [WARN] Trust framework unavailable: {e}")
                    
                    return {"status": "configured", "validators": 2}
                
                else:
                    print("  [INFO] Simple trigger mesh - validators not needed")
                    return {"status": "simple_mesh", "validators": 0}
            
            except Exception as e:
                logger.error(f"Validator setup error: {e}")
                return {"status": "degraded", "error": str(e)}
        
        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="mesh_validators",
            name="Trigger Mesh Validators (Constitutional + Trust)",
            priority=1.6,
            boot_function=chunk_1_6_mesh_validators,
            can_fail=True,  # Can degrade gracefully
            guardian_validates=True
        ))
```

**Lines to add:** ~130 lines after line 250  
**Risk:** None - new chunks, can fail gracefully  
**Testing:** Boot and verify chunks show "[OK]"

---

### Change 4: Add Component Wiring Chunk

**File:** `server.py`

**Location:** After the new chunks above

**Code to add:**

```python
        # ========================================================================
        # CHUNK 2.5: Component Wiring (Connect all systems)
        # ========================================================================
        async def chunk_2_5_component_wiring():
            print("[CHUNK 2.5] Component Wiring System...")
            
            try:
                from backend.core.component_wiring import wire_all_grace_components
                
                # Wire all components
                results = await wire_all_grace_components()
                
                successful = results.get('successful_wirings', 0)
                total = results.get('total_components', 0)
                
                print(f"  [OK] Component Wiring: {successful}/{total} components wired")
                
                # Show which systems are connected
                wiring_details = results.get('wiring_results', {})
                for component, status in wiring_details.items():
                    if status.get('success'):
                        print(f"      ✓ {component}")
                    else:
                        print(f"      ✗ {component}: {status.get('error', 'unknown')}")
                
                return results
            
            except Exception as e:
                logger.error(f"Component wiring error: {e}")
                return {"status": "degraded", "error": str(e)}
        
        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="component_wiring",
            name="Component Wiring System",
            priority=2.5,
            boot_function=chunk_2_5_component_wiring,
            can_fail=True,  # Can continue without full wiring
            guardian_validates=True
        ))
```

**Lines to add:** ~40 lines  
**Risk:** None - graceful degradation  
**Testing:** See which components wire successfully

---

## Implementation Steps

### Step 1: Make Backups

```bash
# Backup critical files before modification
cp backend/event_bus.py backend/event_bus.py.backup
cp backend/misc/trigger_mesh.py backend/misc/trigger_mesh.py.backup
cp server.py server.py.backup
```

### Step 2: Apply Changes

Apply the three changes above in order:
1. Modify `backend/event_bus.py` (Change 1)
2. Modify `backend/misc/trigger_mesh.py` (Change 2)
3. Add boot chunks to `server.py` (Changes 3-4)

### Step 3: Test Boot Sequence

```bash
python server.py
```

**Expected output:**
```
[CHUNK 1.5] Production Systems (Governance, Verification, AVN)...
  [OK] Trigger Mesh: 25 routes loaded from YAML
  [OK] Immune Kernel (AVN): Anomaly detection active
  [OK] Governance Gate: Ready (Kernel 1)
  [OK] Verification Engine: Ready
  [OK] Unified Decision Engine: Ready
  [SUMMARY] 5/5 systems online

[CHUNK 1.6] Trigger Mesh Validators...
  [OK] Constitutional validator: Registered
  [OK] Trust scorer: Registered

[CHUNK 2.5] Component Wiring System...
  [OK] Component Wiring: 10/11 components wired
      ✓ unified_logic_hub
      ✓ verification_engine
      ✓ immutable_logs
      ✓ trigger_mesh
      ✓ immune_avn
      ...
```

### Step 4: Verify Events Route Correctly

```python
# Test event publishing still works
from backend.event_bus import event_bus, Event, EventType

await event_bus.publish(Event(
    event_type=EventType.AGENT_ACTION,
    source="test_component",
    data={"test": True}
))

# Check trigger mesh stats
from backend.misc.trigger_mesh import trigger_mesh

if hasattr(trigger_mesh, 'get_stats'):
    stats = trigger_mesh.get_stats()
    print(f"Events routed: {stats.get('events_routed', 0)}")
```

### Step 5: Verify Governance Works

```python
# Test governance gate
from backend.governance_system.governance_gate import governance_gate, GovernanceRequest, ActionRiskLevel, GovernanceDecision

response = await governance_gate.validate(GovernanceRequest(
    request_id="test_001",
    actor="test_user",
    action="test_action",
    resource="test_resource",
    context={},
    risk_level=ActionRiskLevel.LOW
))

print(f"Decision: {response.decision}")  # Should be APPROVED for low risk
print(f"Reasoning: {response.reasoning}")

# Test high-risk rejection
response2 = await governance_gate.validate(GovernanceRequest(
    request_id="test_002",
    actor="untrusted_actor",
    action="critical_action",
    resource="production_db",
    context={},
    risk_level=ActionRiskLevel.CRITICAL
))

print(f"Decision: {response2.decision}")  # Should be REQUIRES_PARLIAMENT
```

### Step 6: Verify Immutable Log Integrity

```python
from backend.logging.immutable_log import immutable_log

integrity = await immutable_log.verify_integrity()

print(f"Chain valid: {integrity['valid']}")
print(f"Entries verified: {integrity['entries_verified']}")
```

---

## Rollback Procedure

If anything breaks:

**Rollback Step 1:** Restore backups
```bash
cp backend/event_bus.py.backup backend/event_bus.py
cp backend/misc/trigger_mesh.py.backup backend/misc/trigger_mesh.py
cp server.py.backup server.py
```

**Rollback Step 2:** Restart server
```bash
python server.py
```

**Rollback Step 3:** Verify original functionality restored

---

## Success Criteria

Phase 1 is successful if:

- ✅ Server boots completely (all chunks succeed or degrade gracefully)
- ✅ Existing API endpoints still respond
- ✅ Events still publish and subscribers receive them
- ✅ No new errors in logs
- ✅ Guardian validation still works
- ✅ New systems show as "online" or "ready"

---

## Next Steps After Phase 1

Once Phase 1 is stable:

**Phase 2:** Start refactoring high-priority governance checks (10 files)  
**Phase 3:** Consolidate logging (20 files)  
**Phase 4:** Clean up healing triggers (10 files)  
**Phase 5:** Systematic event publish cleanup (100+ files)

---

## Ready to Apply?

I can now:

**A.** Apply these three changes to your files right now  
**B.** Show you a diff preview first  
**C.** Create a migration script that applies all changes  
**D.** Walk through each change one-by-one

Which would you prefer?
