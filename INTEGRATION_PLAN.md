# Integration Plan: Wiring Six Systems Into Grace

## Current State Analysis

Your Grace system has:
- ✅ **Guardian boot orchestrator** - Chunked boot sequence with validation
- ✅ **Existing event bus** - `backend/event_bus.py` and `backend/core/message_bus.py`
- ✅ **Existing immutable log** - `backend/logging/immutable_log.py` (already has hash chains)
- ✅ **Existing governance** - `backend/governance_system/` (but needs wiring)
- ✅ **Existing trigger mesh** - `backend/misc/trigger_mesh.py` (basic version)
- ✅ **Boot chunks** - Guardian validates each chunk before proceeding

## What We Built (Six New Systems)

1. **Verification Engine** - `backend/verification_system/code_verification_engine.py`
2. **Immutable Log Extensions** - `backend/logging/{governance,verification,avn}_logger.py`
3. **Enhanced Trigger Mesh** - `backend/routing/trigger_mesh_enhanced.py`
4. **Unified Logic** - `backend/unified_logic/unified_decision_engine.py`
5. **Governance Gate** - `backend/governance_system/governance_gate.py`
6. **Immune Kernel** - `backend/immune/immune_kernel.py`

---

## Integration Strategy

### Phase 1: Wire Core Infrastructure (Boot Chunks 0-2)

**Goal:** Add new systems to boot sequence without breaking existing chunks.

**Steps:**

1. **Add to Chunk 1-2** (after Guardian, before Kernels):
   ```python
   # In server.py, add new chunk:
   
   async def chunk_1_5_production_systems():
       print("[CHUNK 1.5] Production Systems (Verification, Governance, AVN)...")
       
       # Start trigger mesh (enhanced version)
       from backend.routing.trigger_mesh_enhanced import trigger_mesh
       trigger_mesh.load_config()
       await trigger_mesh.start()
       print("  [OK] Trigger Mesh: Loaded config, routing active")
       
       # Start immune kernel (AVN)
       from backend.immune.immune_kernel import immune_kernel
       await immune_kernel.start()
       print("  [OK] Immune Kernel (AVN): Listening for anomalies")
       
       # Governance gate is passive (validates on-demand)
       from backend.governance_system.governance_gate import governance_gate
       print("  [OK] Governance Gate: Ready (Kernel 1)")
       
       return {"status": "online"}
   
   boot_orchestrator.register_chunk(BootChunk(
       chunk_id="production_systems",
       name="Production Systems (Verification, Governance, AVN)",
       priority=1.5,
       boot_function=chunk_1_5_production_systems,
       can_fail=False,  # Critical for safety
       guardian_validates=True
   ))
   ```

**Why this works:** 
- Slots between core systems (chunk 1-2) and kernels (chunk 3+)
- Guardian validates the chunk
- Doesn't break existing boot flow

---

### Phase 2: Wire Trigger Mesh Validators

**Goal:** Connect constitutional and trust validators to the enhanced trigger mesh.

**Steps:**

2. **Add after Chunk 1.5** (in same boot sequence):
   ```python
   async def chunk_1_6_mesh_validators():
       print("[CHUNK 1.6] Trigger Mesh Validators...")
       
       from backend.routing.trigger_mesh_enhanced import trigger_mesh
       from backend.governance_system.constitutional_verifier import constitutional_verifier
       from backend.trust_framework.trust_score import get_trust_score
       
       # Set constitutional validator
       async def validate_constitutional(event):
           result = await constitutional_verifier.verify(
               actor=event.actor,
               action=event.event_type,
               resource=event.resource,
               context=event.payload
           )
           return result.get('compliant', True)
       
       trigger_mesh.set_governance_validator(validate_constitutional)
       print("  [OK] Constitutional validator: Registered")
       
       # Set trust scorer
       async def get_component_trust(component_id):
           trust = await get_trust_score(component_id)
           return trust.composite_score if trust else 1.0
       
       trigger_mesh.set_trust_scorer(get_component_trust)
       print("  [OK] Trust scorer: Registered")
       
       return {"status": "configured"}
   
   boot_orchestrator.register_chunk(BootChunk(
       chunk_id="mesh_validators",
       name="Trigger Mesh Validators",
       priority=1.6,
       boot_function=chunk_1_6_mesh_validators,
       can_fail=True,  # Can degrade gracefully
       guardian_validates=True
   ))
   ```

**Why this works:**
- Separates validator setup from mesh startup
- Fails gracefully if validators unavailable
- Guardian can validate this chunk

---

### Phase 3: Intercept API Routes (Ingress Wiring)

**Goal:** Make governance the first stop for API requests.

**Option A: Middleware Approach** (Recommended)

3. **Add FastAPI middleware** (in your existing FastAPI app setup):
   ```python
   # In server.py or wherever you create the FastAPI app
   
   from fastapi import FastAPI, Request, Response
   from backend.ingress.governance_middleware import governance_middleware
   
   app = FastAPI()
   
   @app.middleware("http")
   async def governance_middleware_handler(request: Request, call_next):
       """Intercept all requests for governance check"""
       
       # Skip governance for health checks and static files
       if request.url.path in ['/health', '/metrics', '/favicon.ico']:
           return await call_next(request)
       
       # Extract request details
       actor = request.headers.get('X-Actor', 'anonymous')
       action = f"{request.method}:{request.url.path}"
       resource = request.url.path
       
       # Check governance
       result = await governance_middleware.process_request(
           actor=actor,
           action=action,
           resource=resource,
           context={'method': request.method, 'path': str(request.url)},
           risk_level='medium'  # Default, can be customized per route
       )
       
       if not result['allowed']:
           return Response(
               status_code=result['status_code'],
               content=json.dumps(result['response'])
           )
       
       # Governance approved - continue
       return await call_next(request)
   ```

**Option B: Decorator Approach** (More Granular)

3. **Add decorators to specific routes:**
   ```python
   from backend.ingress.governance_middleware import require_governance
   
   # Protect high-risk endpoints
   @app.post("/api/deploy")
   @require_governance(action='deploy_model', risk_level='high')
   async def deploy_model(actor: str, resource: str, model_data: dict):
       # Only executes if governance approves
       return await deploy(model_data)
   
   # Protect autonomous actions
   @app.post("/api/autonomous/execute")
   @require_governance(action='autonomous_execute', risk_level='high', is_autonomous=True)
   async def autonomous_execute(actor: str, task: dict):
       return await execute_autonomous_task(task)
   ```

**Why Option A is better:**
- Catches all requests automatically
- Can't accidentally bypass governance
- Single point of enforcement

**Why Option B is better:**
- More granular control
- Can customize risk per endpoint
- Easier to debug

**Recommendation:** Use **both** - Middleware for blanket coverage, decorators for explicit risk levels.

---

### Phase 4: Wire Autonomous Actions

**Goal:** Ensure AVN healing, business ops, and system changes go through governance.

**Where to wire:**

4. **In existing autonomous action code:**

   **A. AVN Self-Healing** (e.g., `backend/self_heal/runner.py`):
   ```python
   # Before executing healing action:
   from backend.autonomous.governance_wiring import check_avn_action
   
   async def execute_healing(issue):
       # Check governance first
       approved = await check_avn_action(
           action='restart_service',
           component=issue.component,
           anomaly_id=issue.id,
           severity=issue.severity
       )
       
       if not approved:
           logger.warning(f"Governance blocked healing for {issue.component}")
           # Escalate or skip
           return
       
       # Execute healing
       await restart_service(issue.component)
   ```

   **B. Business Operations** (e.g., `backend/transcendence/business/payment_processor.py`):
   ```python
   from backend.autonomous.governance_wiring import check_business_operation
   
   async def process_payment(order_id, amount, customer):
       # Check governance
       approved = await check_business_operation(
           operation='process_payment',
           actor=customer.id,
           resource=f"order:{order_id}",
           context={'amount': amount}
       )
       
       if not approved:
           return {'error': 'Governance rejected payment'}
       
       # Process payment
       ...
   ```

   **C. System Changes** (e.g., auto-scaling):
   ```python
   from backend.autonomous.governance_wiring import check_system_change
   
   async def auto_scale(service, target_replicas):
       approved = await check_system_change(
           change_type='scale',
           target_system=service,
           actor='auto_scaler',
           details={'target_replicas': target_replicas}
       )
       
       if approved:
           await scale_service(service, target_replicas)
   ```

**Key locations to wire:**
- `backend/self_heal/runner.py` - Self-healing agent
- `backend/agents_core/elite_coding_agent.py` - Code generation/deployment
- `backend/transcendence/business/*.py` - Business operations
- `backend/misc/elite_self_healing.py` - Elite healing actions
- Any function that modifies system state

---

### Phase 5: Emit Events to Immune Kernel

**Goal:** Feed anomalies to AVN for automated detection and healing.

**Where to emit:**

5. **In monitoring/metrics code:**

   **A. Health Monitor** (e.g., `backend/production_readiness/health_monitor.py`):
   ```python
   from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent
   
   async def check_health():
       health = await get_system_health()
       
       if health['status'] == 'degraded':
           # Emit anomaly event
           await trigger_mesh.emit(TriggerEvent(
               event_type="anomaly.detected",
               source="health_monitor",
               actor="system",
               resource=health['degraded_component'],
               payload={
                   'type': 'service_degraded',
                   'severity': 'medium',
                   'score': 0.6
               }
           ))
   ```

   **B. Metrics Monitor** (wherever you track latency/errors):
   ```python
   # When latency spikes
   if current_latency > baseline * 3:
       await trigger_mesh.emit(TriggerEvent(
           event_type="anomaly.detected",
           source="metrics_monitor",
           payload={
               'type': 'latency_spike',
               'severity': 'high',
               'baseline': baseline,
               'current': current_latency
           }
       ))
   ```

**Key locations:**
- `backend/production_readiness/health_monitor.py`
- `backend/monitoring/*.py`
- `backend/metrics_service.py`
- `backend/misc/anomaly_watchdog.py` (already exists - just emit events)

---

### Phase 6: Connect to Existing Event Bus

**Goal:** Bridge enhanced trigger mesh with existing event bus.

**Strategy:**

6. **Dual-mode operation** (transition period):
   ```python
   # In trigger_mesh_enhanced.py, add bridge:
   
   async def emit(self, event: TriggerEvent):
       # Route through enhanced mesh
       await self._route_event(event)
       
       # Also publish to legacy event bus for compatibility
       try:
           from backend.event_bus import event_bus
           await event_bus.publish(
               event_type=event.event_type,
               payload=event.payload
           )
       except:
           pass  # Enhanced mesh is primary
   ```

   **OR better: Replace legacy with enhanced:**
   ```python
   # In backend/event_bus.py, delegate to enhanced:
   
   from backend.routing.trigger_mesh_enhanced import trigger_mesh as enhanced_mesh
   
   class EventBus:
       async def publish(self, event_type, payload):
           # Delegate to enhanced mesh
           await enhanced_mesh.emit(TriggerEvent(
               event_type=event_type,
               payload=payload,
               source='legacy',
               actor='system',
               resource=''
           ))
   ```

**Why this works:**
- Backward compatible
- Gradual migration
- Both buses work during transition

---

### Phase 7: Integration Testing

**Goal:** Verify all systems work together.

**Test sequence:**

7. **Create integration test:**
   ```python
   # tests/test_production_integration.py
   
   async def test_complete_flow():
       """Test request → governance → verification → decision → heal"""
       
       # 1. Start all systems
       from backend.routing.trigger_mesh_enhanced import trigger_mesh
       from backend.immune.immune_kernel import immune_kernel
       
       trigger_mesh.load_config()
       await trigger_mesh.start()
       await immune_kernel.start()
       
       # 2. Make request through governance
       from backend.ingress.governance_middleware import governance_middleware
       
       result = await governance_middleware.process_request(
           actor='test_user',
           action='test_action',
           resource='test_resource',
           context={},
           risk_level='low'
       )
       
       assert result['allowed'] == True
       print("✓ Governance passed")
       
       # 3. Emit anomaly, verify AVN heals
       from backend.routing.trigger_mesh_enhanced import TriggerEvent
       
       await trigger_mesh.emit(TriggerEvent(
           event_type="anomaly.detected",
           source="test",
           actor="system",
           resource="test_service",
           payload={'type': 'latency_spike', 'severity': 'medium'}
       ))
       
       await asyncio.sleep(1)  # Let AVN process
       
       stats = immune_kernel.get_stats()
       assert stats['anomalies_detected'] > 0
       print("✓ AVN processed anomaly")
       
       # 4. Verify immutable log integrity
       from backend.logging.immutable_log import immutable_log
       
       integrity = await immutable_log.verify_integrity()
       assert integrity['valid'] == True
       print("✓ Immutable log chain valid")
       
       print("\n✅ Complete integration test passed")
   
   # Run test
   asyncio.run(test_complete_flow())
   ```

---

## Step-by-Step Integration Plan

### Step 1: Prepare (No code changes yet)

**Tasks:**
- ✅ Review current boot sequence in `server.py`
- ✅ Identify where each system fits
- ✅ Map existing event bus to enhanced trigger mesh
- ✅ Identify all autonomous action points

**Questions for you:**
1. Should we add as new boot chunks, or wire into existing chunks?
2. Do you want to keep legacy event bus during transition, or replace immediately?
3. Which autonomous actions are most critical to protect first? (AVN healing, business ops, code deployment?)

---

### Step 2: Add Boot Chunks (Minimal risk)

**Tasks:**
- Add Chunk 1.5: Production Systems (Trigger Mesh, AVN, Governance Gate)
- Add Chunk 1.6: Mesh Validators (Constitutional, Trust)
- Test boot sequence still works

**Risk:** Low - New chunks are isolated, can fail without breaking existing system.

---

### Step 3: Add Middleware (Medium risk)

**Tasks:**
- Add governance middleware to FastAPI
- Test that health checks still work
- Test that existing endpoints still respond

**Risk:** Medium - Affects all API requests, but can be toggled on/off easily.

---

### Step 4: Wire Autonomous Actions (Targeted)

**Tasks:**
- Start with lowest-risk actions (read-only)
- Add governance checks to AVN healing
- Add checks to business operations
- Add checks to code deployment

**Risk:** Low - Can add checks incrementally, one action at a time.

---

### Step 5: Replace Event Bus (Optional)

**Tasks:**
- Create adapter/bridge between legacy and enhanced
- Gradually migrate event emissions
- Eventually deprecate legacy bus

**Risk:** Medium-High - Only do this after everything else is stable.

---

## Migration Approaches

### Approach A: Conservative (Recommended)

1. **Week 1:** Add boot chunks only (Phase 2, Step 2)
2. **Week 2:** Add middleware to 1-2 critical endpoints (Step 3)
3. **Week 3:** Wire 5-10 autonomous actions (Step 4)
4. **Week 4:** Test thoroughly, measure stats
5. **Week 5:** Expand to all endpoints and actions

**Pros:** Safe, reversible at each step, can validate thoroughly  
**Cons:** Takes longer

### Approach B: Aggressive

1. **Day 1:** Add all boot chunks + middleware
2. **Day 2:** Wire all autonomous actions
3. **Day 3:** Replace event bus
4. **Day 4:** Fix issues

**Pros:** Fast integration  
**Cons:** Higher risk of breaking existing functionality

### Approach C: Feature Flag

1. Add all systems but behind feature flags:
   ```python
   ENABLE_GOVERNANCE_GATE = os.getenv('ENABLE_GOVERNANCE_GATE', 'false') == 'true'
   ENABLE_AVN_IMMUNE = os.getenv('ENABLE_AVN_IMMUNE', 'false') == 'true'
   
   if ENABLE_GOVERNANCE_GATE:
       # Use governance middleware
   else:
       # Bypass governance (legacy behavior)
   ```

**Pros:** Can toggle on/off easily, test in production with subset of traffic  
**Cons:** More complex code, need to maintain both paths

---

## Key Decision Points

### Decision 1: Boot Chunk Placement

**Question:** Where to add new chunks?

**Options:**
- **A.** Chunk 1.5 (before kernels) - Recommended
- **B.** Chunk 0.9 (right after Guardian) - Earlier validation
- **C.** Chunk 3+ (with kernels) - Later in boot

**Recommendation:** **Chunk 1.5** - After core systems, before domain kernels.

### Decision 2: Event Bus Strategy

**Question:** Keep legacy bus or replace?

**Options:**
- **A.** Bridge both (legacy delegates to enhanced) - Safe transition
- **B.** Replace immediately - Clean but risky
- **C.** Gradual migration - Both run in parallel

**Recommendation:** **Option A (Bridge)** - Legacy delegates to enhanced, zero downtime.

### Decision 3: Governance Enforcement Level

**Question:** How strict should governance be initially?

**Options:**
- **A.** Log-only mode (governance checks but doesn't block) - Safe learning period
- **B.** Enforce on critical endpoints only - Gradual rollout
- **C.** Enforce everywhere immediately - Full security

**Recommendation:** **Option A → B → C** - Start with logging, measure impact, then enforce.

---

## What I Need From You

Before I start wiring, please tell me:

1. **Boot chunk placement:** Should I add new chunks at priority 1.5, or somewhere else?

2. **Middleware approach:** Should I add FastAPI middleware for all requests, or use decorators on specific endpoints first?

3. **Enforcement mode:** Should governance:
   - **Log only** (check but don't block) initially?
   - **Enforce on critical endpoints** only?
   - **Enforce everywhere** from day 1?

4. **Autonomous actions:** Which autonomous actions are most critical to protect?
   - AVN self-healing?
   - Business operations (payments, marketplace)?
   - Code generation/deployment?
   - System changes (scaling, restarts)?

5. **Event bus strategy:** Should I:
   - Bridge legacy to enhanced (safe)?
   - Replace legacy entirely (clean)?
   - Run both in parallel (gradual)?

6. **Testing approach:** Conservative (weekly) or Aggressive (daily)?

---

## My Recommendation

**Phase 1 (Week 1):** Boot chunks + log-only governance
- Add Chunks 1.5 and 1.6 to boot sequence
- Add middleware in log-only mode
- Monitor what would be blocked
- **Risk: Minimal** - Just observing

**Phase 2 (Week 2):** Enforce critical endpoints
- Enable enforcement on 3-5 critical endpoints
- Keep logging for others
- Measure impact
- **Risk: Low** - Limited scope

**Phase 3 (Week 3):** Wire autonomous actions
- Add governance checks to AVN healing
- Add checks to business ops
- Test thoroughly
- **Risk: Medium** - But well-tested

**Phase 4 (Week 4+):** Full rollout
- Enable enforcement everywhere
- Replace event bus
- Full production mode
- **Risk: Low** - After proving in previous phases

What do you think? Which approach do you prefer?
