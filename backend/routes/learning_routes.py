"""
Memory Learning Pipeline API Routes - Fixed Import

NOTE: This is a stub router that will be enhanced once backend.routes.learning exists.
For now, provides basic learning endpoints without conflicts.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..auth import get_current_user

router = APIRouter(prefix="/api/learning-pipeline", tags=["learning_pipeline"])


class CaptureMemoryRequest(BaseModel):
    content: str
    content_type: str
    metadata: dict = {}
    domain: str = "general"


@router.get("/stats")
async def get_learning_stats(user=Depends(get_current_user)):
    """Get learning pipeline statistics"""
    
    # TODO: Wire to memory_learning_pipeline once imports resolved
    return {
        "total_memories": 0,
        "green_memories": 0,
        "yellow_memories": 0,
        "red_memories": 0,
        "approved_for_training": 0,
        "total_batches": 0,
        "batches_completed": 0,
        "status": "ready"
    }


@router.get("/status")
async def get_pipeline_status():
    """Get learning pipeline status"""
    return {
        "status": "active",
        "message": "Memory learning pipeline ready"
    }
