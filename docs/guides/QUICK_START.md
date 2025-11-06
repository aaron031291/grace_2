# GRACE Self-Healing - Quick Start Guide

## 🚀 Start GRACE Now

### 1. Start the Backend

```bash
cd c:/Users/aaron/grace_2
python backend/minimal_backend.py
```

**Expected Output:**
```
✓ Database initialized
✓ Grace API server starting...
  Visit: http://localhost:8000/health
  Docs: http://localhost:8000/docs

============================================================
GRACE AGENTIC SPINE - AUTONOMOUS ACTIVATION
============================================================

[1/9] Starting foundational systems...
[2/9] Starting multi-agent shard coordinator...
[3/9] Starting agentic observability...
[4/9] Starting proactive intelligence...
[5/9] Activating autonomous decision core...
[6/9] Starting learning integration...
[7/9] Enabling human collaboration...
[8/9] Activating resource stewardship...
[9/9] Starting ethics & compliance sentinel...

[FINAL] Starting meta loop supervisor...

[MEMORY] Starting agentic memory broker...
  ✓ Agentic memory broker started

[INTELLIGENCE] Starting intelligent systems...
  ✓ Immutable log analyzer started
  ✓ Intelligent trigger manager started (8 event types)
  ✓ Meta-coordinated healing started

[DOMAINS] Registering domain adapters...
  -> Registering domain: self_heal
     Telemetry schemas: 6
     Health nodes: 4
     Playbooks: 6
  ✓ Domain self_heal integrated with agent core
  ✓ Self-healing predictor started
  
  -> Registering domain: core
  ✓ Registered 2 domain(s) with agent core

============================================================
GRACE AGENTIC SPINE FULLY OPERATIONAL
============================================================

GRACE is now autonomous and can:
  - Predict incidents before they occur (proactive)
  - Enrich events with intent and context
  - Make decisions with trust core partnership
  - Plan and execute recovery actions
  - Learn from outcomes and self-improve
  - Collaborate with humans proactively
  - Manage her own resources
  - Monitor ethics and compliance
  - Supervise her own behavior cross-domain

  🧠 Agentic Memory:
    • Intelligent Broker → All domains request through broker
    • Policy-Aware → Trust/governance on every access
    • Context Ranking → Semantic search & relevance
    • Domain Isolation → Cross-domain with approval only

  🤖 Meta-Coordinated Self-Healing:
    • Meta Loop → Orchestrates focus & guardrails
    • ML/DL Advisors → Embedded scoring & ranking
    • Agentic Planner → Executes with verification
    • Immutable Log → Single source of truth (signed)

  📡 Intelligent Triggers:
    • Proactive ML → Forecasts & predictions
    • Cross-Domain → Health graph monitoring
    • Pattern Detection → Recurring issue analysis

============================================================
```

### 2. Test Basic Functionality

```bash
# Health check
curl http://localhost:8000/health

# Should return:
# {"status":"ok","message":"Grace API is running"}
```

### 3. Monitor Meta Loop (Watch Logs)

In the backend logs, every 2 minutes you'll see:

```
🔄 Meta Loop Cycle 1 - 14:30:00
  📋 Focus: routine_maintenance
  🛡️ Guardrails: maintain
  🤖 ML Root Causes: []
  📊 Top Playbook: none
```

### 4. Trigger Proactive Prediction

The self-healing predictor analyzes trends every 30 seconds. If it detects rising latency:

```
  🔮 Prediction: api_service - Latency Spike Predicted (confidence: 0.85)
  🔮 Proactive playbook proposed for api_service: Ml Anomaly Forecast (status=proposed)
```

---

## 🧪 Test Agentic Memory

### From Python

```python
# In backend code or Python REPL
from backend.agentic_memory import agentic_memory
from backend.agent_core import DomainAdapter, DomainType

# Create test domain
class TestDomain(DomainAdapter):
    def __init__(self):
        super().__init__(DomainType.CORE)
        self.domain_id = "test"

domain = TestDomain()

# Store memory
await domain.store_memory(
    memory_type="episodic",
    content={"event": "test_healing", "result": "success"},
    tags=["test", "healing", "success"]
)

# Request memory
response = await domain.request_memory(
    memory_type="episodic",
    query="successful healing",
    context={"result": "success"},
    limit=5
)

print(f"Found {len(response['memories'])} memories")
print(f"Access level: {response['access_level']}")
print(f"Explanation: {response['explanation']}")
```

---

## 📊 Check System Status

### View Stats via Python

```python
# Agentic memory stats
from backend.agentic_memory import agentic_memory
stats = agentic_memory.get_stats()
print(stats)

# Intelligent trigger stats
from backend.self_heal.intelligent_triggers import intelligent_trigger_manager
stats = intelligent_trigger_manager.get_stats()
print(stats)

# Meta loop current cycle
from backend.self_heal.meta_coordinated_healing import meta_coordinated_healing
if meta_coordinated_healing.current_cycle:
    print(f"Focus: {meta_coordinated_healing.current_cycle.focus_area.value}")
    print(f"Guardrails: {meta_coordinated_healing.current_cycle.guardrail_adjustment.value}")
```

---

## 🔧 Configuration

### Enable Autonomous Execution

```bash
# In .env or environment
SELF_HEAL_EXECUTE=true

# With safety settings
SELF_HEAL_RUN_TIMEOUT_MIN=10
SELF_HEAL_BASE_URL=http://localhost:8000
```

**⚠️ Warning:** Autonomous execution will:
- Auto-approve low-risk actions (impact ≤ medium, BR ≤ 2)
- Execute playbooks automatically
- Rollback on verification failure
- Create incidents on failures

Start with **observe-only mode** (default) to see proposals first!

---

## 📚 Documentation Map

**Architecture & Design:**
- `docs/AGENTIC_MEMORY.md` - Memory broker architecture
- `docs/META_COORDINATED_HEALING.md` - Orchestration hierarchy
- `docs/INTELLIGENT_TRIGGERS.md` - Multi-source triggers
- `docs/DOMAIN_INTEGRATION.md` - Domain adapter guide

**Operational:**
- `docs/IMPLEMENTATION_SUMMARY.md` - What was built
- `ROADMAP.md` - Strategic paths forward
- `TASK_STATUS.md` - Enhancement tasks
- `QUICK_START.md` - This guide!

**Legacy:**
- `README.md` - Project overview
- `SYSTEM_WIRED.md` - System integration status

---

## 🎯 What to Do Next

### **Today: Test & Explore**
1. Start backend → See GRACE activate
2. Watch meta loop cycles in logs
3. Observe predictor analyzing trends
4. Review documentation to understand architecture

### **Next Session: Choose Your Path**

Tell me one of:
- **"Let's do Option A"** → Learning aggregates + observability
- **"Let's build Knowledge domain"** → Domain expansion
- **"Let's add ML playbook ranking"** → Intelligence boost
- **"Let's write tests"** → Production hardening
- **"Let's integrate Kubernetes"** → External federation

I'll execute with focus. 🎯

---

## ❓ Common Questions

### Q: Is GRACE running autonomously?
**A:** By default, **observe-only mode**. She analyzes, predicts, and proposes - but waits for approval to execute. Set `SELF_HEAL_EXECUTE=true` for autonomous low-risk actions.

### Q: How do I approve actions?
**A:** Currently manual via DB. Next enhancement adds approval API endpoint. Slack integration in PATH 4.

### Q: Where are decisions logged?
**A:** Everything goes to immutable log with signatures. Query via `immutable_log.replay_cycle(cycle_id)`.

### Q: How does meta loop decide focus?
**A:** Analyzes recent immutable log entries - counts errors, checks latency trends, observes trust violations. Decides focus + guardrail adjustment each cycle.

### Q: Can domains access other domain memories?
**A:** Yes, with `include_cross_domain=True` and trust score ≥ 0.8. Agentic memory broker validates and filters.

### Q: What happens if playbook fails?
**A:** Runner verifies outcome. If verification fails → automatic rollback → create incident → signed to immutable log → meta loop learns.

---

**GRACE is ready to run. Start her up and watch her think!** 🧠✨
