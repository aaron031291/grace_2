# Next Steps: Complete Layer 3 Agentic Integration

**Status:** Layer 1 Complete ✅ | Layer 2 Partial 🟡 | Layer 3 Stubbed 🔴

---

## 🎯 **THE ANSWER TO YOUR QUESTION**

> "Once we're up to Layer 3 improvement, is it just UI and ingestion to complete?"

**NO - there's significant integration work needed first:**

### What Must Be Done BEFORE UI/Ingestion:

1. **Wire enrichment routines** (agentic_spine.py) → 1-2 days
2. **Create Intent API** (Layer 3 → Layer 2 bridge) → 1 day
3. **Close learning loop** (outcomes → brain feedback) → 1 day
4. **Wire agentic memory** (kernels → memory broker) → 1 day
5. **Real telemetry collection** (all layers → brain) → 1 day
6. **HTM hardening** (SLA, priority, completion events) → 1-2 days
7. **Cross-layer stress testing** → 1 day

**Total: ~7-10 days of core integration work**

THEN you can do UI + ingestion polish.

---

## 🚀 **IMMEDIATE NEXT STEPS (Start Here)**

### **Step 1: Wire Enrichment Routines** (Start Now - 4 hours)

**File:** `backend/misc/agentic_spine.py`

**What to fix:**
```python
# Lines 198-212 - Currently stubbed:
async def _get_recent_similar_events(self, event: TriggerEvent) -> List[Dict]:
    return []  # ❌ FIX THIS

async def _get_system_state(self, resource: str) -> Dict:
    return {"status": "operational"}  # ❌ FIX THIS

async def _get_actor_history(self, actor: str) -> Dict:
    return {"recent_actions": []}  # ❌ FIX THIS

async def _get_dependencies(self, resource: str) -> List[str]:
    return []  # ❌ FIX THIS
```

**How to fix:**
```python
async def _get_recent_similar_events(self, event: TriggerEvent) -> List[Dict]:
    # Query immutable log for similar event types
    from backend.logging.immutable_log import ImmutableLog
    log = ImmutableLog()
    entries = await log.query_recent(
        actor=event.actor,
        resource=event.resource,
        hours=24
    )
    return [{"event_id": e.id, "action": e.action} for e in entries]

async def _get_system_state(self, resource: str) -> Dict:
    # Get real kernel health from registry
    from backend.kernels.kernel_registry import kernel_registry
    status = kernel_registry.get_status()
    return {
        "status": "operational" if status["initialized"] else "degraded",
        "total_kernels": status["total_kernels"],
        "health": status["health"]
    }

async def _get_actor_history(self, actor: str) -> Dict:
    # Query audit log for actor history
    from backend.models.governance_models import AuditLog
    from backend.models.base_models import async_session
    from sqlalchemy import select, desc
    
    async with async_session() as session:
        result = await session.execute(
            select(AuditLog)
            .where(AuditLog.actor == actor)
            .order_by(desc(AuditLog.timestamp))
            .limit(10)
        )
        logs = result.scalars().all()
        return {
            "recent_actions": [
                {"action": log.action, "resource": log.resource, "result": log.result}
                for log in logs
            ]
        }

async def _get_dependencies(self, resource: str) -> List[str]:
    # Get from health graph or kernel dependencies
    # For now, use kernel registry to infer dependencies
    return []  # TODO: Implement health graph
```

---

### **Step 2: Create Intent API** (4 hours)

**Create:** `backend/core/intent_api.py`

```python
"""
Intent API - Bridge Between Layer 3 (Brain) and Layer 2 (HTM)
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class IntentStatus(Enum):
    CREATED = "created"
    DISPATCHED = "dispatched"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Intent:
    """Structured intent from agentic brain"""
    intent_id: str
    goal: str
    expected_outcome: str
    sla_ms: int
    priority: str  # high, medium, low
    domain: str
    context: Dict[str, Any]
    created_at: datetime
    created_by: str = "agentic_brain"


class IntentAPI:
    """API for brain to submit intents to HTM"""
    
    def __init__(self):
        self.intents: Dict[str, Intent] = {}
        self.intent_status: Dict[str, IntentStatus] = {}
    
    async def submit_intent(self, intent: Intent) -> str:
        """Submit intent and get task_id from HTM"""
        self.intents[intent.intent_id] = intent
        self.intent_status[intent.intent_id] = IntentStatus.CREATED
        
        # TODO: Convert to HTM task
        # from backend.orchestrators.htm import htm_orchestrator
        # task_id = await htm_orchestrator.create_task_from_intent(intent)
        
        return intent.intent_id
    
    async def get_intent_status(self, intent_id: str) -> Dict[str, Any]:
        """Get current status of intent"""
        if intent_id not in self.intents:
            return {"error": "Intent not found"}
        
        return {
            "intent_id": intent_id,
            "status": self.intent_status[intent_id].value,
            "intent": self.intents[intent_id]
        }
    
    async def complete_intent(
        self, 
        intent_id: str, 
        outcome: Dict[str, Any]
    ):
        """Mark intent as completed with outcome"""
        if intent_id in self.intents:
            self.intent_status[intent_id] = IntentStatus.COMPLETED
            
            # TODO: Feed back to learning loop
            # from backend.learning_systems.learning_loop import learning_loop
            # await learning_loop.record_outcome(intent_id, outcome)


# Global instance
intent_api = IntentAPI()
```

---

### **Step 3: Close Learning Loop** (4 hours)

**File:** `backend/learning_systems/learning_loop.py`

**Add at bottom:**
```python
class LearningFeedback:
    """Feeds learning outcomes back to agentic brain"""
    
    async def notify_brain_of_insights(self, playbook_id: str):
        """Send learning insights to brain"""
        async with async_session() as session:
            result = await session.execute(
                select(PlaybookStatistics)
                .where(PlaybookStatistics.playbook_id == playbook_id)
            )
            stats = result.scalar_one_or_none()
            
            if stats and stats.success_rate < 0.6:
                # Emit low success rate event
                from backend.core.message_bus import message_bus
                await message_bus.publish(
                    topic="agentic.learning.insight",
                    message={
                        "playbook_id": playbook_id,
                        "success_rate": stats.success_rate,
                        "recommendation": "consider_alternative",
                        "reason": "success_rate_below_threshold"
                    }
                )


# Global instance
learning_feedback = LearningFeedback()
```

**Then in `record_outcome()` method, add:**
```python
# After updating stats, notify brain
await learning_feedback.notify_brain_of_insights(playbook_id)
```

---

## 📊 **AFTER These 3 Steps (3 Days Work)**

You'll have:
- ✅ **Real enrichment** - Brain sees actual event history, system state, actor patterns
- ✅ **Intent flow** - Brain → Intent API → HTM → Kernels
- ✅ **Closed loop** - Execution → Learning → Brain adjusts strategy

Then remaining work:
1. Wire agentic memory to kernels (1 day)
2. Real telemetry collection (1 day)
3. HTM hardening (2 days)
4. Cross-layer testing (1 day)
5. **THEN** UI + ingestion polish (3-5 days)

---

## 🎯 **Recommended Priority**

### **Option A: Complete Autonomy First (My Recommendation)**
Week 1: Layer 3 enrichment + Intent API + learning loop  
Week 2: Memory wiring + telemetry + HTM hardening  
Week 3: UI + ingestion optimization  

**Outcome:** Fully autonomous system that makes smart decisions, then add pretty UI

### **Option B: Visibility First**
Week 1: Basic UI showing Layer 1 kernel status  
Week 2: Layer 3 enrichment + Intent API  
Week 3: Complete integration  

**Outcome:** Can demo early, but system isn't truly autonomous yet

---

## ✅ **What Do You Want to Tackle First?**

1. **Start with enrichment routines** (wire real data into brain)?
2. **Create Intent API** (connect brain to HTM)?
3. **Build UI first** (get visibility before integration)?

Let me know and I'll implement it! 🚀
