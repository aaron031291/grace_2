"""
Unified Logic Hub API
Routes for submitting and tracking logic updates
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

router = APIRouter(prefix="/api/logic-hub", tags=["Unified Logic Hub"])


# Request/Response Models

class SchemaUpdateRequest(BaseModel):
    """Request to update a schema"""
    endpoint: str
    current_schema: Optional[Dict[str, Any]] = None
    proposed_schema: Dict[str, Any]
    created_by: str = "api_user"
    risk_level: Literal["low", "medium", "high", "critical"] = "medium"


class CodeModuleUpdateRequest(BaseModel):
    """Request to update code modules"""
    modules: Dict[str, str] = Field(..., description="Map of module_path to code content")
    component_targets: List[str]
    created_by: str = "api_user"
    risk_level: Literal["low", "medium", "high", "critical"] = "high"


class PlaybookUpdateRequest(BaseModel):
    """Request to update a playbook"""
    playbook_name: str
    playbook_content: Dict[str, Any]
    component_targets: List[str]
    created_by: str = "api_user"
    risk_level: Literal["low", "medium", "high", "critical"] = "medium"


class GenericUpdateRequest(BaseModel):
    """Generic update request for any type"""
    update_type: Literal["schema", "code_module", "playbook", "config", "metric_definition"]
    component_targets: List[str]
    content: Dict[str, Any]
    created_by: str = "api_user"
    risk_level: Literal["low", "medium", "high", "critical"] = "medium"
    context: Optional[Dict[str, Any]] = None


class UpdateResponse(BaseModel):
    """Response after submitting update"""
    update_id: str
    status: str
    message: str


class UpdateStatusResponse(BaseModel):
    """Detailed status of an update"""
    update_id: str
    update_type: str
    component_targets: List[str]
    version: str
    status: str
    status_history: List[Dict[str, Any]]
    validation_results: Dict[str, Any]
    diagnostics: List[str]
    created_by: str
    created_at: str
    checksum: Optional[str]
    crypto_id: Optional[str]


class UpdateListItem(BaseModel):
    """Summary item in update list"""
    update_id: str
    update_type: str
    status: str
    component_targets: List[str]
    created_at: str
    created_by: str


class HubStatsResponse(BaseModel):
    """Hub statistics"""
    total_updates: int
    successful_updates: int
    failed_updates: int
    rollbacks: int
    active_updates: int
    registry_size: int
    success_rate: float


# Routes

@router.post("/updates/schema", response_model=UpdateResponse)
async def submit_schema_update(request: SchemaUpdateRequest):
    """
    Submit a schema update to the Unified Logic Hub
    
    Flow:
    1. Governance check
    2. Crypto signature
    3. Validation (breaking change detection)
    4. Distribution to API layer
    5. Watchdog monitoring
    """
    
    try:
        from backend.unified_logic_hub import submit_schema_update
        
        update_id = await submit_schema_update(
            endpoint=request.endpoint,
            current_schema=request.current_schema,
            proposed_schema=request.proposed_schema,
            created_by=request.created_by,
            risk_level=request.risk_level
        )
        
        return UpdateResponse(
            update_id=update_id,
            status="submitted",
            message=f"Schema update submitted for {request.endpoint}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit schema update: {e}")


@router.post("/updates/code-module", response_model=UpdateResponse)
async def submit_code_module_update(request: CodeModuleUpdateRequest):
    """
    Submit a code module update to the Unified Logic Hub
    
    Flow:
    1. Governance check (high risk)
    2. Crypto signature
    3. Sandbox validation (lint, tests)
    4. Distribution to target components
    5. Watchdog monitoring
    """
    
    try:
        from backend.unified_logic_hub import submit_code_module_update
        
        update_id = await submit_code_module_update(
            modules=request.modules,
            component_targets=request.component_targets,
            created_by=request.created_by,
            risk_level=request.risk_level
        )
        
        return UpdateResponse(
            update_id=update_id,
            status="submitted",
            message=f"Code module update submitted for {len(request.modules)} modules"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit code module update: {e}")


@router.post("/updates/playbook", response_model=UpdateResponse)
async def submit_playbook_update(request: PlaybookUpdateRequest):
    """
    Submit a playbook update to the Unified Logic Hub
    
    Flow:
    1. Governance check
    2. Crypto signature
    3. Playbook validation
    4. Distribution to self-heal components
    5. Watchdog monitoring
    """
    
    try:
        from backend.unified_logic_hub import submit_playbook_update
        
        update_id = await submit_playbook_update(
            playbook_name=request.playbook_name,
            playbook_content=request.playbook_content,
            component_targets=request.component_targets,
            created_by=request.created_by,
            risk_level=request.risk_level
        )
        
        return UpdateResponse(
            update_id=update_id,
            status="submitted",
            message=f"Playbook update submitted: {request.playbook_name}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit playbook update: {e}")


@router.post("/updates/generic", response_model=UpdateResponse)
async def submit_generic_update(request: GenericUpdateRequest):
    """
    Submit any type of update to the Unified Logic Hub
    
    Supports: schema, code_module, playbook, config, metric_definition
    """
    
    try:
        from backend.unified_logic_hub import unified_logic_hub
        
        update_id = await unified_logic_hub.submit_update(
            update_type=request.update_type,
            component_targets=request.component_targets,
            content=request.content,
            created_by=request.created_by,
            risk_level=request.risk_level,
            context=request.context
        )
        
        return UpdateResponse(
            update_id=update_id,
            status="submitted",
            message=f"{request.update_type} update submitted"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit update: {e}")


@router.get("/updates/{update_id}", response_model=UpdateStatusResponse)
async def get_update_status(update_id: str):
    """
    Get detailed status of a specific update
    
    Returns:
    - Current status
    - Status history (pipeline stages)
    - Validation results
    - Diagnostics
    - Crypto signatures
    """
    
    try:
        from backend.unified_logic_hub import unified_logic_hub
        
        status = await unified_logic_hub.get_update_status(update_id)
        
        if not status:
            raise HTTPException(status_code=404, detail=f"Update {update_id} not found")
        
        return UpdateStatusResponse(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get update status: {e}")


@router.get("/updates", response_model=List[UpdateListItem])
async def list_updates(limit: int = 20):
    """
    List recent updates
    
    Returns summary of recent updates with basic status info
    """
    
    try:
        from backend.unified_logic_hub import unified_logic_hub
        
        updates = await unified_logic_hub.list_recent_updates(limit=limit)
        
        return [UpdateListItem(**u) for u in updates]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list updates: {e}")


@router.get("/stats", response_model=HubStatsResponse)
async def get_hub_stats():
    """
    Get Unified Logic Hub statistics
    
    Returns:
    - Total updates processed
    - Success/failure counts
    - Rollback count
    - Success rate
    """
    
    try:
        from backend.unified_logic_hub import unified_logic_hub
        
        stats = unified_logic_hub.get_stats()
        
        return HubStatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get hub stats: {e}")


@router.post("/updates/{update_id}/rollback", response_model=UpdateResponse)
async def trigger_rollback(update_id: str):
    """
    Manually trigger rollback of an update
    
    This will revert the changes made by the update
    and distribute rollback instructions via trigger mesh
    """
    
    try:
        from backend.unified_logic_hub import unified_logic_hub
        
        # Get the update
        status = await unified_logic_hub.get_update_status(update_id)
        
        if not status:
            raise HTTPException(status_code=404, detail=f"Update {update_id} not found")
        
        if status["status"] in ["failed", "rolled_back"]:
            raise HTTPException(
                status_code=400,
                detail=f"Update already in status: {status['status']}"
            )
        
        # Find package and rollback
        package = unified_logic_hub.active_updates.get(update_id)
        if not package:
            # Try registry
            package = next(
                (p for p in unified_logic_hub.update_registry if p.update_id == update_id),
                None
            )
        
        if not package:
            raise HTTPException(status_code=404, detail="Package not found for rollback")
        
        await unified_logic_hub._rollback_update(package)
        
        return UpdateResponse(
            update_id=update_id,
            status="rolled_back",
            message=f"Rollback initiated for update {update_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger rollback: {e}")
