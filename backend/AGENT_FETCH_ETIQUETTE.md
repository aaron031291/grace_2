# Agent Fetch Etiquette
## Training Guide for Autonomous Agents

All autonomous agents in Grace must follow these protocols when fetching memories or data.

---

## Core Principle

**NEVER access storage directly. ALWAYS use the signed gateway.**

### Why?
- Governance enforcement (constitutional compliance)
- Crypto auditability (full traceability)
- Immutable logging (compliance & debugging)
- Logic versioning (know which update produced the data)

---

## Correct Fetch Pattern

### ✅ ALWAYS Use Gateway
```python
from backend.memory_fusion_service import memory_fusion_service

# Correct: Gated fetch with governance + crypto
result = await memory_fusion_service.fetch_with_gateway(
    user=agent_id,
    query=semantic_query,
    domain=target_domain,
    limit=10,
    context={
        "agent_type": "agentic_spine",
        "task_id": current_task_id,
        "logic_update_id": logic_update_id  # CRITICAL: Include this!
    }
)

# Extract data and metadata
memories = result["data"]
crypto_id = result["crypto_id"]
logic_update_id = result["logic_update_id"]
audit_ref = result["audit_ref"]
```

### ❌ NEVER Do This
```python
# WRONG: Direct storage access (bypasses governance + crypto)
from backend.memory import memory_service
memories = await memory_service.retrieve(user, domain)  # NO!

# WRONG: Direct DB query
from backend.models import async_session, Memory
async with async_session() as session:
    memories = await session.query(Memory).all()  # NO!
```

---

## Critical: Include logic_update_id in Context

Every agent operation must include the current logic_update_id so audit trails stay intact.

### How to Get logic_update_id

```python
from backend.logic_update_awareness import logic_update_awareness

# Option 1: Get from current update summary
summary = await logic_update_awareness.get_update_summary(current_update_id)
logic_update_id = summary.get("update_id") if summary else None

# Option 2: Get from memory fetch result
result = await memory_fusion_service.fetch_with_gateway(...)
logic_update_id = result["logic_update_id"]

# Option 3: Get from agent's internal state
logic_update_id = agent_state.get("current_logic_update_id")
```

### Include in All Operations

```python
# Fetch with logic_update_id
result = await memory_fusion_service.fetch_with_gateway(
    user=agent_id,
    query=query,
    context={
        "logic_update_id": logic_update_id,  # ← Critical!
        "agent_task": task_description
    }
)

# Store with logic_update_id
result = await memory_fusion_service.store_memory_with_crypto(
    user=agent_id,
    content=content,
    domain=domain,
    metadata={
        "logic_update_id": logic_update_id,  # ← Critical!
        "task_id": task_id
    }
)

# Execute actions with logic_update_id
from backend.action_executor import action_executor

result = await action_executor.execute(
    action=action_spec,
    context={
        "logic_update_id": logic_update_id,  # ← Critical!
        "agent_id": agent_id
    }
)
```

---

## Agent-Specific Guidelines

### AgenticSpine

**Before acting on new capabilities:**

```python
# 1. Request update summary FIRST
from backend.logic_update_awareness import logic_update_awareness

summary = await logic_update_awareness.get_update_summary(update_id)

# 2. Understand what changed
new_capabilities = summary.get("new_capabilities", [])
new_guardrails = summary.get("guardrails", [])
rollback_plan = summary.get("rollback_plan", {})

# 3. Update internal context
agent_context["current_update"] = {
    "update_id": update_id,
    "capabilities": new_capabilities,
    "guardrails": new_guardrails
}

# 4. Now use new capabilities with context
result = await memory_fusion_service.fetch_with_gateway(
    user="agentic_spine",
    query=query,
    context={
        "logic_update_id": update_id,
        "new_capability": "schema_v2_support"
    }
)
```

### Autonomous Improver

**When proposing improvements:**

```python
# Include current logic version in proposals
from backend.unified_logic_hub import submit_code_module_update

update_id = await submit_code_module_update(
    modules=improved_code,
    component_targets=affected_components,
    created_by="autonomous_improver",
    risk_level="high"
)

# Track the update you created
agent_state["pending_updates"][update_id] = {
    "proposed_at": datetime.now(),
    "type": "code_improvement",
    "based_on_logic_version": current_logic_update_id
}
```

### Self-Heal Agents

**When accessing playbooks:**

```python
# Always fetch through gateway
result = await memory_fusion_service.fetch_with_gateway(
    user="self_heal_agent",
    domain="playbooks",
    query=f"playbook for {issue_type}",
    context={
        "logic_update_id": current_logic_update_id,
        "issue_type": issue_type,
        "severity": severity
    }
)

playbooks = result["data"]

# Verify playbook is from current logic version
for playbook in playbooks:
    if playbook.get("logic_update_id") != current_logic_update_id:
        logger.warning(f"Playbook from old logic version: {playbook}")
```

### Proactive Intelligence

**When analyzing patterns:**

```python
# Fetch historical data with logic versioning
result = await memory_fusion_service.fetch_with_gateway(
    user="proactive_intelligence",
    domain="metrics",
    query="error_rate anomalies last 7 days",
    context={
        "logic_update_id": current_logic_update_id,
        "analysis_type": "pattern_detection",
        "time_window": "7d"
    }
)

# Correlate anomalies with logic updates
for anomaly in result["data"]:
    anomaly_logic_version = anomaly.get("logic_update_id")
    if anomaly_logic_version != current_logic_update_id:
        # Anomaly from different logic version - may not be relevant
        logger.info(f"Anomaly from logic version {anomaly_logic_version}")
```

---

## Governance Compliance

### Respect Governance Decisions

```python
try:
    result = await memory_fusion_service.fetch_with_gateway(
        user=agent_id,
        domain=target_domain,
        context=agent_context
    )
    
    # Check if governance approved
    if not result.get("governance_approved"):
        logger.error("Governance blocked fetch - aborting")
        return
    
    # Proceed with approved data
    process_data(result["data"])
    
except Exception as e:
    if "Governance blocked" in str(e):
        # Governance denied access
        logger.error(f"Governance denied: {e}")
        await escalate_to_human(reason=str(e))
    else:
        raise
```

### Rate Limiting

Agents should respect fetch rate limits:

```python
import asyncio
from datetime import datetime, timedelta

class AgentFetchLimiter:
    def __init__(self, max_fetches_per_minute=60):
        self.max_fetches = max_fetches_per_minute
        self.fetch_times = []
    
    async def check_rate_limit(self):
        """Enforce rate limiting"""
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        # Remove old fetch times
        self.fetch_times = [t for t in self.fetch_times if t > cutoff]
        
        # Check limit
        if len(self.fetch_times) >= self.max_fetches:
            # Wait until oldest fetch expires
            wait_time = (self.fetch_times[0] + timedelta(minutes=1) - now).total_seconds()
            logger.warning(f"Rate limit reached, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
        
        # Record this fetch
        self.fetch_times.append(now)

# Use in agent
limiter = AgentFetchLimiter(max_fetches_per_minute=60)

async def agent_fetch(query, domain):
    await limiter.check_rate_limit()
    return await memory_fusion_service.fetch_with_gateway(
        user="my_agent",
        query=query,
        domain=domain
    )
```

---

## Audit Trail Best Practices

### Verify Fetch Integrity

```python
# After critical fetch, verify integrity
result = await memory_fusion_service.fetch_with_gateway(...)

# Verify the fetch was legitimate
verification = await memory_fusion_service.verify_fetch_integrity(
    fetch_session_id=result["fetch_session_id"],
    signature=result["signature"]
)

if not verification["valid"]:
    logger.error("Fetch integrity check failed!")
    raise Exception("Invalid fetch signature")

# Proceed with verified data
process_verified_data(result["data"])
```

### Get Full Audit Trail

```python
# For debugging or compliance, get full audit trail
import requests

audit_trail = requests.get(
    f"http://localhost:8000/api/memory-fusion/audit-trail/{fetch_session_id}"
).json()

logger.info(f"Audit trail: {len(audit_trail['audit_entries'])} entries")
for entry in audit_trail["audit_entries"]:
    logger.info(f"  {entry['action']} by {entry['actor']} at {entry['timestamp']}")
```

---

## Error Handling

### Handle Governance Blocks

```python
try:
    result = await memory_fusion_service.fetch_with_gateway(...)
except Exception as e:
    if "Governance blocked" in str(e):
        # Request is blocked by governance
        logger.warning(f"Governance blocked fetch: {e}")
        
        # Option 1: Request approval
        await request_human_approval(
            action="fetch_memory",
            reason=str(e),
            agent_id=agent_id
        )
        
        # Option 2: Use alternative approach
        result = await use_alternative_data_source()
        
        # Option 3: Abort gracefully
        return None
    else:
        raise
```

### Handle Crypto Failures

```python
try:
    result = await memory_fusion_service.fetch_with_gateway(...)
except Exception as e:
    if "crypto" in str(e).lower():
        # Crypto engine failure
        logger.error(f"Crypto failure: {e}")
        
        # Fall back to direct fetch (emergency only)
        logger.warning("EMERGENCY: Using direct fetch (governance bypassed)")
        result = await emergency_direct_fetch()
        
        # Log the bypass
        await log_governance_bypass(
            reason="crypto_engine_failure",
            agent_id=agent_id,
            timestamp=datetime.now()
        )
    else:
        raise
```

---

## Summary Checklist

Before deploying an agent, verify:

✅ Uses `memory_fusion_service.fetch_with_gateway()` (not direct storage)  
✅ Includes `logic_update_id` in all fetch contexts  
✅ Requests update summary before using new capabilities  
✅ Respects governance decisions (doesn't bypass blocks)  
✅ Implements rate limiting  
✅ Verifies fetch integrity for critical operations  
✅ Handles governance blocks gracefully  
✅ Logs all operations with crypto metadata  

---

## Training Examples

### Example: Agentic Spine Task Execution

```python
class AgenticSpineTask:
    async def execute(self, task_spec):
        # 1. Get current logic update summary
        summary = await logic_update_awareness.get_update_summary(
            self.current_update_id
        )
        
        # 2. Understand new guardrails
        guardrails = summary.get("guardrails", [])
        
        # 3. Fetch relevant memories through gateway
        context = {
            "logic_update_id": self.current_update_id,
            "task_type": task_spec["type"],
            "guardrails": guardrails
        }
        
        memories = await memory_fusion_service.fetch_with_gateway(
            user="agentic_spine",
            query=task_spec["context"],
            domain=task_spec["domain"],
            context=context
        )
        
        # 4. Execute with full context
        result = await self.execute_with_memories(
            task=task_spec,
            memories=memories["data"],
            logic_version=self.current_update_id
        )
        
        return result
```

### Example: Self-Heal Playbook Selection

```python
class SelfHealAgent:
    async def select_playbook(self, issue):
        # Fetch playbooks through gateway
        result = await memory_fusion_service.fetch_with_gateway(
            user="self_heal_agent",
            query=f"playbook for {issue.type}",
            domain="playbooks",
            context={
                "logic_update_id": self.current_logic_update_id,
                "issue_severity": issue.severity,
                "component": issue.component
            }
        )
        
        # Filter to current logic version only
        current_playbooks = [
            pb for pb in result["data"]
            if pb.get("logic_update_id") == self.current_logic_update_id
        ]
        
        return self.rank_playbooks(current_playbooks, issue)
```

---

**Remember:** The gateway is your friend. It adds ~50ms latency but gives you governance, crypto, and auditability. Always worth it.
