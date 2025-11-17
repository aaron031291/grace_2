"""
Memory Learning Pipeline API Routes - Fixed Import

NOTE: This is a stub router that will be enhanced once backend.routes.learning exists.
For now, provides basic learning endpoints without conflicts.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..auth import get_current_user
from ..schemas_extended import LearningStatsResponse, LearningStatusResponse

router = APIRouter(prefix="/api/learning-pipeline", tags=["learning_pipeline"])


class CaptureMemoryRequest(BaseModel):
    content: str
    content_type: str
    metadata: dict = {}
    domain: str = "general"


@router.get("/stats", response_model=LearningStatsResponse)
async def get_learning_stats(user=Depends(get_current_user)):
    """Get learning pipeline statistics"""
    
    # TODO(FUTURE): Wire to memory_learning_pipeline once imports resolved
    return LearningStatsResponse(
        total_memories=0,
        green_memories=0,
        yellow_memories=0,
        red_memories=0,
        approved_for_training=0,
        total_batches=0,
        batches_completed=0,
        status="ready",
        execution_trace=None,
        data_provenance=[]
    )


@router.get("/status", response_model=LearningStatusResponse)
async def get_pipeline_status():
    """Get learning pipeline status"""
    return LearningStatusResponse(
        status="active",
        message="Memory learning pipeline ready",
        execution_trace=None,
        data_provenance=[]
    )
