"""
Grace Memory API
Endpoints for Grace to autonomously manage her memory
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from ..auth import get_current_user
from ..grace_memory_agent import get_grace_memory_agent

router = APIRouter(prefix="/api/grace/memory", tags=["grace-memory"])


class CreateFileRequest(BaseModel):
    category: str
    subcategory: Optional[str] = None
    filename: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    auto_sync: bool = True


class SaveResearchRequest(BaseModel):
    title: str
    content: str
    domain: str = "general"
    tags: List[str] = []
    auto_sync: bool = True


class SaveInsightRequest(BaseModel):
    insight: str
    category_type: str = "observations"
    confidence: float = 0.8
    auto_sync: bool = True


class SaveConversationRequest(BaseModel):
    conversation_id: str
    messages: List[Dict]
    metadata: Optional[Dict] = None
    auto_sync: bool = False


class UpdateFileRequest(BaseModel):
    file_path: str
    new_content: str
    reason: str = ""
    auto_sync: bool = True


class OrganizeFileRequest(BaseModel):
    file_path: str
    suggested_category: str
    suggested_subcategory: str
    auto_move: bool = False


@router.get("/categories")
async def list_categories(current_user: str = Depends(get_current_user)):
    """List all memory categories Grace can use"""
    agent = await get_grace_memory_agent()
    return {
        "categories": agent.list_categories(),
        "count": len(agent.categories)
    }


@router.get("/categories/{category}")
async def get_category_info(
    category: str,
    current_user: str = Depends(get_current_user)
):
    """Get detailed info about a category"""
    agent = await get_grace_memory_agent()
    info = agent.get_category_info(category)
    
    if not info:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    return info


@router.post("/create")
async def create_file(
    req: CreateFileRequest,
    current_user: str = Depends(get_current_user)
):
    """Grace creates a new file in her memory"""
    agent = await get_grace_memory_agent()
    
    result = await agent.create_file(
        category=req.category,
        subcategory=req.subcategory,
        filename=req.filename,
        content=req.content,
        metadata=req.metadata,
        auto_sync=req.auto_sync
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=403, detail=result.get("error"))
    
    return result


@router.post("/research")
async def save_research(
    req: SaveResearchRequest,
    current_user: str = Depends(get_current_user)
):
    """Grace saves research findings"""
    agent = await get_grace_memory_agent()
    
    result = await agent.save_research(
        title=req.title,
        content=req.content,
        domain=req.domain,
        tags=req.tags,
        auto_sync=req.auto_sync
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=403, detail=result.get("error"))
    
    return result


@router.post("/insight")
async def save_insight(
    req: SaveInsightRequest,
    current_user: str = Depends(get_current_user)
):
    """Grace saves her own insights"""
    agent = await get_grace_memory_agent()
    
    result = await agent.save_insight(
        insight=req.insight,
        category_type=req.category_type,
        confidence=req.confidence,
        auto_sync=req.auto_sync
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=403, detail=result.get("error"))
    
    return result


@router.post("/conversation")
async def save_conversation(
    req: SaveConversationRequest,
    current_user: str = Depends(get_current_user)
):
    """Grace saves conversation for learning"""
    agent = await get_grace_memory_agent()
    
    result = await agent.save_conversation(
        conversation_id=req.conversation_id,
        messages=req.messages,
        metadata=req.metadata,
        auto_sync=req.auto_sync
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=403, detail=result.get("error"))
    
    return result


@router.post("/training")
async def save_training_data(
    dataset_name: str,
    data: Any,
    data_type: str = "embeddings",
    auto_sync: bool = True,
    current_user: str = Depends(get_current_user)
):
    """Grace saves training data"""
    agent = await get_grace_memory_agent()
    
    result = await agent.save_training_data(
        dataset_name=dataset_name,
        data=data,
        data_type=data_type,
        auto_sync=auto_sync
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=403, detail=result.get("error"))
    
    return result


@router.post("/immutable-log")
async def log_immutable_event(
    event_type: str,
    event_data: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """Log immutable event"""
    agent = await get_grace_memory_agent()
    
    result = await agent.log_immutable_event(
        event_type=event_type,
        event_data=event_data
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=403, detail=result.get("error"))
    
    return result


@router.put("/update")
async def update_file(
    req: UpdateFileRequest,
    current_user: str = Depends(get_current_user)
):
    """Update existing file"""
    agent = await get_grace_memory_agent()
    
    result = await agent.update_file(
        file_path=req.file_path,
        new_content=req.new_content,
        reason=req.reason,
        auto_sync=req.auto_sync
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=403, detail=result.get("error"))
    
    return result


@router.delete("/delete")
async def delete_file(
    file_path: str,
    reason: str = "",
    force: bool = False,
    current_user: str = Depends(get_current_user)
):
    """Delete file (with permission check)"""
    agent = await get_grace_memory_agent()
    
    result = await agent.delete_file(
        file_path=file_path,
        reason=reason,
        force=force
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=403, detail=result.get("error"))
    
    return result


@router.post("/organize")
async def organize_file(
    req: OrganizeFileRequest,
    current_user: str = Depends(get_current_user)
):
    """Grace organizes/categorizes a file"""
    agent = await get_grace_memory_agent()
    
    result = await agent.organize_file(
        file_path=req.file_path,
        suggested_category=req.suggested_category,
        suggested_subcategory=req.suggested_subcategory,
        auto_move=req.auto_move
    )
    
    return result


@router.get("/actions")
async def get_action_log(
    limit: int = 100,
    action_type: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Get Grace's action history"""
    agent = await get_grace_memory_agent()
    
    actions = agent.get_action_log(limit=limit, action_type=action_type)
    
    return {
        "actions": actions,
        "count": len(actions)
    }


@router.get("/status")
async def get_agent_status(current_user: str = Depends(get_current_user)):
    """Get Grace memory agent status"""
    agent = await get_grace_memory_agent()
    
    return {
        "status": agent.status.value,
        "component_id": agent.component_id,
        "activated_at": agent.activated_at.isoformat() if agent.activated_at else None,
        "categories_count": len(agent.categories),
        "actions_logged": len(agent.action_log)
    }
