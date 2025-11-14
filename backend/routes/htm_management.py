"""
HTM Management API - MVP
Simple endpoints for HTM queue control, priority management, and auto-scaling rules
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api/htm", tags=["htm_management"])


class PriorityWeights(BaseModel):
    critical_weight: float
    high_weight: float
    normal_weight: float
    low_weight: float


class HTMRule(BaseModel):
    rule_type: str
    condition: Dict[str, Any]
    action: str


# In-memory storage (replace with database in production)
current_priorities = {
    "critical_weight": 1.0,
    "high_weight": 0.8,
    "normal_weight": 0.5,
    "low_weight": 0.2
}

htm_rules = []


@router.post("/priorities")
async def set_htm_priorities(priorities: PriorityWeights):
    """
    Set HTM queue priority weights
    Used by Layer 2 priority sliders
    """
    global current_priorities
    current_priorities = priorities.dict()
    
    return {
        "status": "updated",
        "priorities": current_priorities,
        "message": "Priority weights updated successfully"
    }


@router.get("/priorities")
async def get_htm_priorities():
    """Get current HTM priority weights"""
    return {
        "priorities": current_priorities
    }


@router.post("/pause")
async def pause_htm_queue():
    """
    Pause HTM queue (stop accepting new tasks)
    Used by Layer 2 HTM console quick action
    """
    # In production: Update HTM queue state in database
    return {
        "status": "paused",
        "message": "HTM queue paused. No new tasks will be accepted.",
        "timestamp": "2025-11-14T10:40:00Z"
    }


@router.post("/resume")
async def resume_htm_queue():
    """Resume HTM queue"""
    return {
        "status": "resumed",
        "message": "HTM queue resumed. Accepting new tasks.",
        "timestamp": "2025-11-14T10:41:00Z"
    }


@router.post("/flush")
async def flush_completed_tasks():
    """
    Flush completed tasks from HTM queue
    Used by Layer 2 HTM console quick action
    """
    # In production: Delete completed tasks from database
    flushed_count = 45  # Mock count
    
    return {
        "status": "flushed",
        "count": flushed_count,
        "message": f"Flushed {flushed_count} completed tasks from queue"
    }


@router.post("/spawn_agent")
async def spawn_htm_agent(
    agent_type: Optional[str] = "general",
    capacity: Optional[int] = 10
):
    """
    Spawn a new HTM processing agent
    Used by Layer 2 agent spawner and co-pilot quick actions
    """
    # In production: Actually spawn agent, add to agent pool
    agent_id = f"agent-{hash(agent_type + str(capacity))}"
    
    return {
        "status": "spawned",
        "agent_id": agent_id,
        "agent_type": agent_type,
        "capacity": capacity,
        "message": f"Spawned {agent_type} agent with capacity {capacity}"
    }


@router.post("/rules")
async def create_htm_rule(rule: HTMRule):
    """
    Create HTM auto-scaling rule
    Used by Layer 2 low-code rule builder
    
    Example rule:
    {
      "rule_type": "auto_scale",
      "condition": {
        "metric": "queue_depth",
        "operator": "greater_than",
        "threshold": 50
      },
      "action": "spawn_agent"
    }
    """
    rule_dict = rule.dict()
    rule_dict["rule_id"] = f"rule-{len(htm_rules) + 1}"
    rule_dict["created_at"] = "2025-11-14T10:40:00Z"
    rule_dict["enabled"] = True
    
    htm_rules.append(rule_dict)
    
    return {
        "status": "created",
        "rule": rule_dict,
        "message": "HTM rule created and enabled"
    }


@router.get("/rules")
async def get_htm_rules():
    """Get all HTM auto-scaling rules"""
    return {
        "rules": htm_rules,
        "total": len(htm_rules)
    }


@router.delete("/rules/{rule_id}")
async def delete_htm_rule(rule_id: str):
    """Delete HTM rule"""
    global htm_rules
    htm_rules = [r for r in htm_rules if r.get("rule_id") != rule_id]
    
    return {
        "status": "deleted",
        "rule_id": rule_id
    }
