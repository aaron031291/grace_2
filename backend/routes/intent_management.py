"""
Intent Management API - MVP
Simple endpoints for intent creation and management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/intent", tags=["intent_management"])


class IntentCreate(BaseModel):
    goal: str
    data_source: str
    priority: str = "normal"


# In-memory storage (replace with database in production)
active_intents = []


@router.post("/create")
async def create_intent(intent: IntentCreate):
    """
    Create new intent
    Used by Layer 3 simple intent creation form
    """
    intent_id = f"int-{len(active_intents) + 1:03d}"
    
    new_intent = {
        "intent_id": intent_id,
        "goal": intent.goal,
        "data_source": intent.data_source,
        "priority": intent.priority,
        "status": "pending",
        "completion_percent": 0,
        "created_at": datetime.utcnow().isoformat(),
        "htm_tasks_generated": 0,
        "estimated_completion": None
    }
    
    active_intents.append(new_intent)
    
    # Estimate HTM tasks based on goal complexity (simple heuristic)
    estimated_tasks = len(intent.goal.split()) // 5 + 5  # Rough estimate
    
    return {
        "status": "created",
        "intent_id": intent_id,
        "estimated_tasks": estimated_tasks,
        "message": f"Intent created: {intent.goal[:50]}..."
    }


@router.get("/list")
async def list_intents(status: Optional[str] = None):
    """Get all intents, optionally filtered by status"""
    if status:
        filtered = [i for i in active_intents if i["status"] == status]
        return {"intents": filtered, "total": len(filtered)}
    
    return {"intents": active_intents, "total": len(active_intents)}


@router.delete("/{intent_id}")
async def cancel_intent(intent_id: str):
    """Cancel an intent"""
    global active_intents
    active_intents = [i for i in active_intents if i["intent_id"] != intent_id]
    
    return {
        "status": "cancelled",
        "intent_id": intent_id,
        "message": "Intent cancelled"
    }
