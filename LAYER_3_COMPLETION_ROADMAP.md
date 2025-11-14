# Layer 3 Agentic Layer - Completion Roadmap

**Date:** November 14, 2025  
**Current Status:** Layer 1 (18 kernels) ✅ | Layer 2 (HTM) 🟡 | Layer 3 (Agentic Brain) 🔴  
**Goal:** Complete autonomous decision-making with full telemetry integration

---

## 🎯 Current State Assessment

### ✅ **What's Working (Layer 1 + Partial Layer 2)**

**Layer 1 - Execution Layer (COMPLETE)**
- ✅ 18 kernels operational
- ✅ Kernel Registry with Clarity Framework
- ✅ Request routing functional
- ✅ Memory persistence working
- ✅ Structured logging in place

**Layer 2 - Orchestration Layer (PARTIAL)**
- 🟡 HTM exists but not integrated with Layer 3 intents
- 🟡 Trigger Mesh exists but enrichment is stubbed
- 🟡 Playbook execution framework exists
- 🟡 Priority queues exist but SLA enforcement incomplete

**Layer 3 - Agentic Brain (STUBBED)**
- 🔴 Agentic Spine exists with stubbed enrichment
- 🔴 Agentic Memory exists but not wired to kernels
- 🔴 Learning Loop exists but outcomes not flowing back
- 🔴 Agentic Brain exists but telemetry inputs stubbed
- 🔴 No Intent API connecting Layer 3 → Layer 2

---

## 🚧 Critical Gaps (What Blocks Full Autonomy)

### **Gap #1: Stubbed Enrichment Routines** 🔴 CRITICAL

**Location:** `backend/misc/agentic_spine.py` lines 198-212

**Current State:**
```python
async def _get_recent_similar_events(self, event: TriggerEvent) -> List[Dict]:
    return []  # ❌ Stubbed!

async def _get_system_state(self, resource: str) -> Dict:
    return {"status": "operational"}  # ❌ Stubbed!

async def _get_actor_history(self, actor: str) -> Dict:
    return {"recent_actions": []}  # ❌ Stubbed!
```

**Impact:** Event enrichment always returns empty context → confidence scores artificially low → brain can't make informed decisions.

**Fix Required:** Wire to:
- Immutable log for `_get_recent_similar_events()`
- Health graph for `_get_system_state()`
- Ledger/audit tables for `_get_actor_history()`

---

### **Gap #2: No Intent API (Layer 3 → Layer 2)** 🔴 CRITICAL

**Problem:** Layer 3 (agentic brain) has no formal way to send goals/intents to Layer 2 (HTM). HTM doesn't know "why" it's scheduling tasks.

**Missing:**
- Intent schema (intent_id, goal, SLA, expected_outcome)
- Intent → HTM task conversion
- Completion feedback (HTM → Brain)

**Fix Required:** Create `backend/core/intent_api.py`:
```python
class Intent:
    intent_id: str
    goal: str
    expected_outcome: str
    sla_ms: int
    priority: str
    context: Dict[str, Any]

class IntentAPI:
    async def submit_intent(intent: Intent) -> str
    async def get_intent_status(intent_id: str) -> Dict
    async def complete_intent(intent_id: str, outcome: Dict)
```

---

### **Gap #3: Learning Loop Not Closed** 🔴 CRITICAL

**Location:** `backend/learning_systems/learning_loop.py`

**Current State:**
- ✅ `record_outcome()` writes to database
- ❌ Outcomes never flow back to brain
- ❌ Playbook success rates not updated
- ❌ HTM doesn't see failure patterns

**Fix Required:**
- Wire learning_loop → agentic_brain feedback
- Auto-update playbook success_rate in database
- Emit `agentic.learning.insight` events
- HTM subscribes to learning events for priority adjustments

---

### **Gap #4: Agentic Memory Not Wired to Kernels** 🔴 HIGH

**Location:** `backend/misc/agentic_memory.py`

**Current State:**
- ✅ Full architecture defined
- ❌ Not used by any kernels
- ❌ Kernels access memory directly (bypassing governance)

**Fix Required:**
- Update all 18 kernels to use agentic_memory broker
- Implement trust checks and domain isolation
- Add memory access logging to immutable log

---

### **Gap #5: Telemetry Not Feeding Brain** 🟡 MEDIUM

**Location:** `backend/core/agentic_brain.py`

**Current State:**
- ✅ TelemetrySnapshot class defined
- ❌ Actual telemetry collection stubbed
- ❌ Brain decisions not based on real metrics

**Fix Required:**
- Collect real metrics from:
  - HTM queue depths
  - Kernel health from registry
  - Hunter alerts
  - Ingestion pipeline stats
- Feed into brain's decision logic

---

## 📋 Completion Roadmap

### **Phase 1: Core Integration (HIGH PRIORITY)** 

**Estimated: 2-3 days**

1. ✅ **Fix Layer 1 Kernels** (DONE)
   - [x] Restore 7 empty kernel files
   - [x] Fix import chains
   - [x] Implement abstract methods
   - [x] Verify all 18 kernels boot

2. 🔄 **Implement Enrichment Routines** (IN PROGRESS)
   - [ ] Wire `_get_recent_similar_events()` to immutable log
   - [ ] Wire `_get_system_state()` to health graph/kernel registry
   - [ ] Wire `_get_actor_history()` to audit log
   - [ ] Wire `_get_dependencies()` to health graph

3. 🔄 **Create Intent API**
   - [ ] Define Intent schema
   - [ ] Create IntentAPI service
   - [ ] Wire agentic_brain → IntentAPI → HTM
   - [ ] Add intent tracking to database

4. 🔄 **Close Learning Loop**
   - [ ] Add LearningLoop → AgenticBrain feedback
   - [ ] Auto-update playbook stats from outcomes
   - [ ] Emit learning insight events
   - [ ] Wire HTM to consume learning events

---

### **Phase 2: Memory & Observability (MEDIUM PRIORITY)**

**Estimated: 1-2 days**

5. 🔄 **Wire Agentic Memory**
   - [ ] Update kernels to use agentic_memory broker
   - [ ] Implement trust checks
   - [ ] Add memory access logging
   - [ ] Test cross-domain memory requests

6. 🔄 **Real Telemetry Collection**
   - [ ] Collect HTM queue metrics
   - [ ] Collect kernel health from registry
   - [ ] Collect Hunter alerts
   - [ ] Collect ingestion stats
   - [ ] Feed all into TelemetrySnapshot

---

### **Phase 3: Orchestration Hardening (MEDIUM PRIORITY)**

**Estimated: 2 days**

7. 🔄 **HTM Improvements**
   - [ ] SLA enforcement (timeout detection)
   - [ ] Priority math based on intent + learning
   - [ ] Better failure handling
   - [ ] Completion events back to brain

8. 🔄 **Governance Integration**
   - [ ] Policy checks for all agentic actions
   - [ ] Approval workflows for high-risk intents
   - [ ] Trust score validation

---

### **Phase 4: Testing & Verification (HIGH PRIORITY)**

**Estimated: 1-2 days**

9. 🔄 **Cross-Layer Stress Tests**
   - [ ] Layer 3 intent → Layer 2 HTM → Layer 1 kernel flow
   - [ ] Learning loop feedback verification
   - [ ] Enrichment quality testing
   - [ ] Full autonomy cycle test

10. 🔄 **E2E Autonomy Validation**
    - [ ] Submit intent to brain
    - [ ] Track through HTM
    - [ ] Verify kernel execution
    - [ ] Confirm learning recorded
    - [ ] Validate brain adjusted strategy

---

### **Phase 5: UI & Polish (LOWER PRIORITY)**

**Estimated: 3-4 days**

11. 🔄 **Multi-Layer UI**
    - [ ] Layer 1: Kernel health & execution view
    - [ ] Layer 2: HTM orchestration dashboard
    - [ ] Layer 3: Intent & learning view
    - [ ] Layer 4: OS/dev control panel

12. 🔄 **Ingestion Optimization**
    - [ ] Chunk quality improvements
    - [ ] Pipeline performance tuning
    - [ ] Trust score calibration

---

## 🎯 What Remains After Layer 3

**After completing Phase 1-3 above, the system will have:**
- ✅ Fully autonomous decision-making
- ✅ Complete telemetry integration
- ✅ Closed learning loops
- ✅ Intent-driven orchestration

**Then remaining work is:**
1. **UI/Frontend** - Multi-layer dashboards (Phase 5.11)
2. **Ingestion Polish** - Performance tuning (Phase 5.12)
3. **Documentation** - User/operator guides
4. **Deployment** - Production hardening, monitoring setup
5. **Integration Testing** - Full system validation

**So NO, it's not just UI and ingestion.** The orchestration hardening (Phase 3) and cross-layer integration (Phase 1-2) are substantial work that must happen before UI/ingestion polish makes sense.

---

## 🏆 Recommended Order

### **Critical Path (Must Do First)**

1. **Phase 1.2:** Implement enrichment routines (2 days)
   - This unblocks meaningful brain decisions

2. **Phase 1.3:** Create Intent API (1 day)
   - This connects brain → HTM

3. **Phase 1.4:** Close learning loop (1 day)
   - This enables continuous improvement

4. **Phase 2.6:** Real telemetry (1 day)
   - This gives brain real data

5. **Phase 4.9-10:** Cross-layer testing (2 days)
   - This validates autonomy works

**Total Critical Path: ~7 days**

After that, UI and ingestion can proceed in parallel.

---

## 📊 Completion Percentage

### Current Status
```
Layer 1 (Kernels):        [████████████████████] 100% ✅
Layer 2 (HTM):            [████████░░░░░░░░░░░░]  40% 🟡
Layer 3 (Agentic Brain):  [████░░░░░░░░░░░░░░░░]  20% 🔴
Integration:              [██░░░░░░░░░░░░░░░░░░]  10% 🔴
UI:                       [░░░░░░░░░░░░░░░░░░░░]   0% 🔴
Ingestion:                [██████░░░░░░░░░░░░░░]  30% 🟡

Overall System:           [█████░░░░░░░░░░░░░░░]  25%
```

### To Reach 100%
- Complete Phases 1-3 (orchestration + brain): +50%
- Complete Phase 4 (testing): +10%
- Complete Phase 5 (UI + polish): +15%

**Estimated Total: 10-15 days of focused work**

---

## 🚀 Quick Wins (Start Here)

If you want immediate progress on Layer 3:

**Day 1:** Implement enrichment in agentic_spine.py
- Wire `_get_recent_similar_events()` to query immutable log
- Wire `_get_system_state()` to kernel_registry.get_status()
- Test that enriched events have real context

**Day 2:** Create Intent API + wire to HTM
- Define Intent schema
- Create intent submission endpoint
- Wire HTM to consume intents as tasks

**Day 3:** Close learning loop
- Add feedback from learning_loop to brain
- Update playbook success rates
- Test that brain learns from outcomes

After these 3 days, you'll have a functional autonomous decision loop!

---

## 📝 Decision Point

**Question:** Do you want to proceed with Layer 3 improvements now, or focus on UI/ingestion first?

**My Recommendation:** Complete Phase 1 (items 2-4) first. Without the enrichment + intent API + learning loop, the brain is "flying blind" and UI dashboards would just show stubbed data.

**Alternative:** If you need UI for demos/visibility, we can build a basic dashboard showing Layer 1 kernel status (already working) while completing Layer 3 integration in parallel.

**Your call!** 🎯
