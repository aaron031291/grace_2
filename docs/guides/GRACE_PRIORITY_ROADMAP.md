# Grace Priority Roadmap - Next Phase

**Current Status:** Clarity Framework Deployed, 9 Kernels + UI Ready  
**Date:** 2025-11-12

---

## 🎯 Immediate Actions (Do After Restart)

### 1. UI Validation ✅
**Goal:** Verify all 13 dashboards work end-to-end

```bash
# After restarting both services:
# Visit http://localhost:5173 and test each tab:

- 🔍 Clarity → Check event bus, components, mesh
- 🧠 LLM → Verify status display
- 💡 Intel → Check kernel status
- 📥 Ingest → Try starting a GitHub task
- 🎓 Learn → Verify learning status
- 📊 Dash → Confirm metrics load
- 📁 Memory → Test memory browser
- 🛡️ Hunter → Check security dashboard
```

**Acceptance:** All tabs load without errors, clarity shows live data

### 2. Regression Test Suite ✅
**Goal:** Protect all new integrations in CI

**Create:** `tests/test_api_regression.py`
```python
# Test all new endpoints
- /api/llm/status
- /api/intelligence/status  
- /api/ingestion/status
- /api/learning/status
- /api/kernels
- /api/clarity/* (4 endpoints)
```

**Add to CI:** `.github/workflows/basic_ci.yml`
```yaml
- name: API Regression Tests
  run: python -m pytest tests/test_api_regression.py -v
```

### 3. Monitoring Integration ✅
**Goal:** Clarity events flow into logs and alerts

**Wire:**
- Clarity event bus → structured logs
- Component health → alert system
- Ingestion progress → metrics
- Kernel errors → notifications

**Create:** `backend/clarity/monitoring_bridge.py`

---

## 🚀 Phase 2: Advanced Clarity (Classes 5-10)

### Class 5: Memory Trust Scoring
**When:** After memory systems are live  
**What:** Trust + decay models for memory entries

```python
# backend/clarity/memory_trust.py
class MemoryTrustScorer:
    - Score memory by source, age, validation
    - Apply decay curves
    - Update trust in real-time
```

### Class 6: Constitutional Governance
**When:** After governance policies are defined  
**What:** Enforce Prime Directive at every decision point

```python
# backend/clarity/constitutional_enforcer.py
def validate_against_constitution(action):
    - Check action against policies
    - Require approval for violations
    - Log governance decisions
```

### Class 7: Loop Feedback Integration
**When:** After loops generate outputs  
**What:** Pipe loop results into memory automatically

```python
# backend/clarity/loop_feedback.py
async def loop_output_to_memory(loop_output: GraceLoopOutput):
    - Extract learnings from loop
    - Store in memory with trust tags
    - Link to reasoning chains
```

### Class 8: Specialist Consensus
**When:** After MLDL specialists are active  
**What:** Trust-weighted quorum for decisions

```python
# backend/clarity/quorum_engine.py
class QuorumEngine:
    - Evaluate(specialists, question)
    - Weight by trust
    - Resolve conflicts
    - Log dissent
```

### Class 9: Output Standardization
**When:** After APIs are stable  
**What:** GraceLoopOutput for ALL interfaces

**Enforce:**
- Every API returns GraceLoopOutput
- Every CLI command uses it
- Every UI panel expects it

### Class 10: Contradiction Detection
**When:** After data flows  
**What:** Scan for conflicting knowledge/policy drift

```python
# backend/clarity/cognition_linter.py
class GraceCognitionLinter:
    - Detect conflicting conclusions
    - Find policy drift
    - Trigger AVN fallback
    - Auto-remediate
```

---

## 📋 Documentation Priorities

### 1. Universal Boot Guide
**File:** `docs/UNIVERSAL_BOOT.md`

**Content:**
- One-command start for any platform
- Environment detection
- Troubleshooting by stage
- Health verification

### 2. Kernel Developer Guide  
**File:** `docs/KERNEL_DEVELOPMENT.md`

**Content:**
- How to create a new kernel
- Clarity BaseComponent patterns
- Event publishing
- Trust level management

### 3. Dashboard Integration Guide
**File:** `docs/UI_DASHBOARD_GUIDE.md`

**Content:**
- How to add new dashboards
- API client patterns
- Real-time updates
- Error handling

### 4. Troubleshooting Playbook
**File:** `docs/TROUBLESHOOTING.md`

**Content:**
- Common errors and fixes
- Log locations
- Clarity component inspection
- Kernel restart procedures

---

## 🔧 Technical Debt / Cleanup

### Priority 1: Replace Stubs
**Current:** 9 kernels, LLM, memory systems are stubs  
**Target:** Replace with real implementations

**Order:**
1. Memory Kernel → PersistentMemory integration
2. LLM System → OpenAI/local model integration
3. Intelligence Kernel → Reasoning engine
4. Code Kernel → Coding agent integration

### Priority 2: Event Mesh Expansion
**Current:** 23 events defined  
**Target:** 50+ events covering all operations

**Add:**
- Kernel-to-kernel events
- Trust update events
- Learning pattern events
- Governance decision events

### Priority 3: Real-time Event Stream
**Current:** Event history via API  
**Target:** WebSocket event streaming to UI

**Create:** `backend/websocket_events.py`
```python
@app.websocket("/ws/events")
async def event_stream(websocket):
    # Stream clarity events to frontend
```

---

## 📊 Success Metrics

### Phase 1 (Complete) ✅
- [x] Clarity Framework (Classes 1-4) implemented
- [x] 21/21 tests passing
- [x] 9 kernels with BaseComponent
- [x] UI dashboards for all systems
- [x] Clean import tracking

### Phase 2 (Next 2 Weeks)
- [ ] All endpoints tested in CI
- [ ] 50+ events in trigger mesh
- [ ] 3+ kernels with real implementations
- [ ] Real-time event streaming to UI
- [ ] Monitoring/alerting wired up

### Phase 3 (Next Month)
- [ ] Classes 5-10 implemented
- [ ] Trust scoring operational
- [ ] Constitutional governance active
- [ ] Loop feedback flowing
- [ ] Contradiction detection working

---

## 🎯 Immediate Next Steps (Priority Order)

1. **Restart services** - See new UI in action
2. **Test ingestion** - Start a task from dashboard
3. **Add regression tests** - Protect new endpoints
4. **Wire monitoring** - Events → logs → alerts
5. **Document boot** - Universal start guide
6. **Plan Class 5** - Memory trust scoring design

---

## 💡 Strategic Vision

**Where Grace is heading:**

### Short-term (This Month)
- Clarity-based architecture across all systems
- Real kernels replacing stubs
- Full observability via dashboards
- Event-driven self-healing

### Mid-term (Next Quarter)
- Trust-based decision making
- Constitutional governance enforcement
- Autonomous learning loops
- Cross-kernel collaboration

### Long-term (Next 6 Months)
- Self-aware, self-improving AI
- Zero-touch deployment and healing
- Policy-driven autonomy
- Multi-agent consensus

---

**Grace is transforming from a collection of services into a unified, self-aware, autonomous AI platform powered by the Clarity Framework.** 🚀

---

**Next Session: Test the UI, add regression coverage, then tackle Class 5 (Memory Trust Scoring).**
