"""
Memory Learning Pipeline API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..memory_learning_pipeline import memory_learning_pipeline, MemoryClassification
from ..auth import get_current_user

router = APIRouter(prefix="/api/learning", tags=["learning"])


class CaptureMemoryRequest(BaseModel):
    content: str
    content_type: str  # "conversation", "code", "error", "decision", "outcome", "feedback"
    metadata: dict = {}
    domain: str = "general"


class ApproveMemoryRequest(BaseModel):
    memory_id: str


@router.post("/capture")
async def capture_memory(request: CaptureMemoryRequest, user=Depends(get_current_user)):
    """Capture a memory for learning"""
    
    try:
        content_type = MemoryClassification(request.content_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid content_type")
    
    memory_id = await memory_learning_pipeline.capture_interaction(
        user=user["username"],
        content=request.content,
        content_type=content_type,
        metadata=request.metadata,
        domain=request.domain
    )
    
    memory = memory_learning_pipeline.memory_store.get(memory_id)
    
    return {
        "memory_id": memory_id,
        "sensitivity": memory.sensitivity.value,
        "approved_for_training": memory.approved_for_training,
        "training_value": memory.training_value
    }


@router.get("/memories")
async def list_memories(
    limit: int = 50,
    sensitivity: Optional[str] = None,
    approved_only: bool = False,
    user=Depends(get_current_user)
):
    """List captured memories"""
    
    memories = list(memory_learning_pipeline.memory_store.values())
    
    # Filter by sensitivity
    if sensitivity:
        memories = [m for m in memories if m.sensitivity.value == sensitivity]
    
    # Filter by approval
    if approved_only:
        memories = [m for m in memories if m.approved_for_training]
    
    # Sort by timestamp desc
    memories.sort(key=lambda m: m.timestamp, reverse=True)
    
    return [
        {
            "memory_id": m.memory_id,
            "timestamp": m.timestamp.isoformat(),
            "user": m.user,
            "content_type": m.content_type.value,
            "sensitivity": m.sensitivity.value,
            "approved_for_training": m.approved_for_training,
            "training_value": m.training_value,
            "domain": m.domain,
            "content_preview": m.redacted_content[:100]
        }
        for m in memories[:limit]
    ]


@router.get("/memories/{memory_id}")
async def get_memory(memory_id: str, user=Depends(get_current_user)):
    """Get a specific memory"""
    
    memory = memory_learning_pipeline.memory_store.get(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return {
        "memory_id": memory.memory_id,
        "timestamp": memory.timestamp.isoformat(),
        "user": memory.user,
        "content_type": memory.content_type.value,
        "redacted_content": memory.redacted_content,
        "sensitivity": memory.sensitivity.value,
        "approved_for_training": memory.approved_for_training,
        "training_value": memory.training_value,
        "metadata": memory.metadata,
        "domain": memory.domain
    }


@router.post("/approve")
async def approve_memory(request: ApproveMemoryRequest, user=Depends(get_current_user)):
    """Approve a memory for training"""
    
    try:
        await memory_learning_pipeline.approve_for_training(
            request.memory_id,
            user["username"]
        )
        return {"status": "approved", "memory_id": request.memory_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/request-curation/{memory_id}")
async def request_curation(memory_id: str, user=Depends(get_current_user)):
    """Request human curation for a yellow memory"""
    
    try:
        curation_id = await memory_learning_pipeline.request_human_curation(memory_id)
        return {"curation_id": curation_id, "memory_id": memory_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/provenance/{memory_id}")
async def get_provenance(memory_id: str, user=Depends(get_current_user)):
    """Get full provenance chain of a memory"""
    
    provenance = memory_learning_pipeline.get_provenance(memory_id)
    if not provenance:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return provenance


@router.get("/batches")
async def list_learning_batches(user=Depends(get_current_user)):
    """List all learning batches"""
    
    batches = list(memory_learning_pipeline.learning_batches.values())
    batches.sort(key=lambda b: b.created_at, reverse=True)
    
    return [
        {
            "batch_id": b.batch_id,
            "created_at": b.created_at.isoformat(),
            "memory_count": len(b.memories),
            "training_type": b.training_type,
            "status": b.status
        }
        for b in batches
    ]


@router.post("/run-nightly-learning")
async def run_nightly_learning(user=Depends(get_current_user)):
    """Manually trigger nightly learning job"""
    
    await memory_learning_pipeline.run_nightly_learning()
    return {"status": "completed"}


@router.get("/stats")
async def get_learning_stats(user=Depends(get_current_user)):
    """Get learning pipeline statistics"""
    
    memories = list(memory_learning_pipeline.memory_store.values())
    
    return {
        "total_memories": len(memories),
        "green_memories": len([m for m in memories if m.sensitivity.value == "green"]),
        "yellow_memories": len([m for m in memories if m.sensitivity.value == "yellow"]),
        "red_memories": len([m for m in memories if m.sensitivity.value == "red"]),
        "approved_for_training": len([m for m in memories if m.approved_for_training]),
        "total_batches": len(memory_learning_pipeline.learning_batches),
        "batches_completed": len([
            b for b in memory_learning_pipeline.learning_batches.values()
            if b.status == "completed"
        ])
    }
