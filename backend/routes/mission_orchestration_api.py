"""
Mission Orchestration API - Complete Mission Execution Pipeline

Provides endpoints for submitting missions and managing sandbox execution.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from backend.kernels.mission_orchestrator import get_mission_orchestrator

router = APIRouter()


class MissionSubmission(BaseModel):
    mission_id: Optional[str] = None
    brief: str
    constraints: Optional[Dict[str, Any]] = None
    auto_implement: bool = False


@router.post("/submit")
async def submit_mission(submission: MissionSubmission) -> Dict[str, Any]:
    """
    Submit a new mission for orchestrated execution
    
    Example:
        POST /api/missions/orchestrate/submit
        {
            "brief": "Build iOS/Android mobile app with offline sync, chat, and media upload",
            "constraints": {
                "platforms": ["iOS", "Android"],
                "frameworks": ["React Native", "Flutter"],
                "deadline": "2 weeks"
            },
            "auto_implement": false
        }
    
    Workflow:
        1. Stores brief in Learning Memory
        2. Consults local mentor models
        3. Generates implementation plan
        4. Creates sandbox workspace
        5. (If auto_implement=true) Generates code, runs tests, notifies
    """
    
    orchestrator = get_mission_orchestrator()
    await orchestrator.activate()
    
    try:
        # Generate mission ID if not provided
        mission_id = submission.mission_id or f"mission_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Execute mission pipeline
        result = await orchestrator.execute_mission(
            mission_id=mission_id,
            brief=submission.brief,
            constraints=submission.constraints,
            auto_implement=submission.auto_implement
        )
        
        return {
            "status": "success",
            "mission_id": mission_id,
            "execution_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{mission_id}")
async def get_mission_status(mission_id: str) -> Dict[str, Any]:
    """Get status of an orchestrated mission"""
    
    from backend.learning_memory import query_category
    
    try:
        # Query Learning Memory for mission artifacts
        files = await query_category("mission_briefs", mission_id)
        
        if not files:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        # Load execution log
        import json
        execution_log = None
        
        for file_path in files:
            if "execution_log" in file_path:
                with open(file_path) as f:
                    execution_log = json.load(f)
                break
        
        return {
            "mission_id": mission_id,
            "files_found": len(files),
            "execution_log": execution_log,
            "artifacts": files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/promote/{mission_id}")
async def promote_mission(mission_id: str) -> Dict[str, Any]:
    """
    Promote mission sandbox to mainline after user approval
    
    Example:
        POST /api/missions/orchestrate/promote/mobile-app-001
    """
    
    orchestrator = get_mission_orchestrator()
    
    try:
        result = await orchestrator.promote_sandbox(mission_id)
        
        return {
            "status": "success",
            "mission_id": mission_id,
            "promotion_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active")
async def list_active_missions() -> Dict[str, Any]:
    """List all active sandbox missions"""
    
    orchestrator = get_mission_orchestrator()
    await orchestrator.activate()
    
    status = await orchestrator.get_status()
    
    return {
        "active_sandboxes": list(orchestrator.active_sandboxes.keys()),
        "total": status["active_sandboxes"]
    }


# Import datetime for mission_id generation
from datetime import datetime
