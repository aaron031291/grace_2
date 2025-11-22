"""
Intelligent Model Router API
Routes tasks to optimal AI models based on intelligent analysis
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import json
from datetime import datetime

from backend.services.intelligent_model_router import intelligent_model_router

router = APIRouter()


class RouteTaskRequest(BaseModel):
    """Request to route a task to optimal model"""
    task: str = Field(..., description="Task description or query")
    user_id: Optional[str] = Field("anonymous", description="User identifier")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    task_id: Optional[str] = Field(None, description="Optional task identifier")


class RouteTaskResponse(BaseModel):
    """Response from task routing"""
    task_id: str
    selected_model: str
    result: Dict[str, Any]
    analysis: Dict[str, Any]
    performance: Optional[Dict[str, Any]]
    timestamp: str
    fallback_used: Optional[bool] = False
    original_model: Optional[str] = None
    error: Optional[str] = None


class RoutingStatsResponse(BaseModel):
    """Routing statistics response"""
    total_routed: int
    model_performance: Dict[str, Any]
    user_profiles: Dict[str, Any]
    recent_decisions: List[Dict[str, Any]]


@router.post("/route", response_model=RouteTaskResponse)
async def route_task(request: RouteTaskRequest) -> RouteTaskResponse:
    """
    Route a task to the optimal AI model based on intelligent analysis

    Analyzes task complexity, content type, and user context to select
    the best specialized model (BuilderAgent, SelfReflectionLoop, etc.)
    """
    try:
        result = await intelligent_model_router.route_task(
            task=request.task,
            user_id=request.user_id,
            context=request.context,
            task_id=request.task_id
        )

        return RouteTaskResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing failed: {str(e)}")


@router.post("/route/visual", response_model=RouteTaskResponse)
async def route_visual_task(
    task: str = Form(...),
    user_id: str = Form("anonymous"),
    context: Optional[str] = Form(None),  # JSON string
    image: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None)
) -> RouteTaskResponse:
    """
    Route a visual task (image/video) to vision models

    Accepts image or video files along with task description
    """
    try:
        # Parse context if provided
        parsed_context = json.loads(context) if context else {}

        # Handle file uploads
        if image:
            image_data = await image.read()
            parsed_context["image_data"] = image_data
            parsed_context["filename"] = image.filename
        elif video:
            # For video, we'd need to save to temp file and provide path
            # This is simplified for the example
            video_data = await video.read()
            parsed_context["video_data"] = video_data
            parsed_context["filename"] = video.filename
        else:
            raise HTTPException(status_code=400, detail="Either image or video file required")

        result = await intelligent_model_router.route_task(
            task=task,
            user_id=user_id,
            context=parsed_context
        )

        return RouteTaskResponse(**result)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid context JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visual routing failed: {str(e)}")


@router.post("/route/code", response_model=RouteTaskResponse)
async def route_code_task(
    task: str = Form(...),
    user_id: str = Form("anonymous"),
    context: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
) -> RouteTaskResponse:
    """
    Route a coding task to BuilderAgent

    Accepts code files and project requirements
    """
    try:
        parsed_context = json.loads(context) if context else {}

        # Handle multiple file uploads
        if files:
            file_contents = {}
            for file in files:
                content = await file.read()
                file_contents[file.filename] = content.decode('utf-8')
            parsed_context["files"] = file_contents

        result = await intelligent_model_router.route_task(
            task=task,
            user_id=user_id,
            context=parsed_context
        )

        return RouteTaskResponse(**result)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid context JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code routing failed: {str(e)}")


@router.post("/route/research", response_model=RouteTaskResponse)
async def route_research_task(
    task: str = Form(...),
    user_id: str = Form("anonymous"),
    context: Optional[str] = Form(None),
    paper: Optional[UploadFile] = File(None)
) -> RouteTaskResponse:
    """
    Route a research task to ResearchApplicationPipeline

    Accepts research papers and analysis requirements
    """
    try:
        parsed_context = json.loads(context) if context else {}

        # Handle paper upload
        if paper:
            paper_data = await paper.read()
            # In production, save to temp file and provide path
            parsed_context["paper_data"] = paper_data
            parsed_context["paper_filename"] = paper.filename
            # For now, assume paper_path is provided in context
            parsed_context["paper_path"] = f"/tmp/{paper.filename}"

        result = await intelligent_model_router.route_task(
            task=task,
            user_id=user_id,
            context=parsed_context
        )

        return RouteTaskResponse(**result)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid context JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research routing failed: {str(e)}")


@router.get("/stats", response_model=RoutingStatsResponse)
async def get_routing_stats() -> RoutingStatsResponse:
    """
    Get routing performance statistics and analytics

    Returns model performance metrics, user profiles, and recent decisions
    """
    try:
        stats = intelligent_model_router.get_routing_stats()
        return RoutingStatsResponse(**stats)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.post("/optimize")
async def optimize_routing(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Trigger routing optimization based on historical performance

    Runs in background and updates routing strategies
    """
    try:
        # Run optimization in background
        background_tasks.add_task(intelligent_model_router.optimize_routing)

        return {
            "message": "Routing optimization started",
            "status": "running",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.get("/models")
async def list_available_models() -> Dict[str, Any]:
    """
    List all available specialized models and their capabilities
    """
    from backend.services.intelligent_model_router import ModelType, ContentType, TaskComplexity

    models_info = {
        "models": {
            "builder_agent": {
                "description": "Full-stack software engineer for building applications",
                "capabilities": ["project_scaffolding", "dependency_management", "testing", "deployment"],
                "content_types": ["code"],
                "complexity_levels": ["simple", "medium", "complex"]
            },
            "self_reflection_loop": {
                "description": "Continuous learning and improvement through reflection",
                "capabilities": ["performance_analysis", "strategy_optimization", "trust_scoring"],
                "content_types": ["general", "learning"],
                "complexity_levels": ["simple", "medium", "complex"]
            },
            "research_pipeline": {
                "description": "Complete research-to-application pipeline",
                "capabilities": ["document_analysis", "experiment_design", "validation", "application"],
                "content_types": ["research"],
                "complexity_levels": ["medium", "complex"]
            },
            "vision_models": {
                "description": "Visual content analysis and understanding",
                "capabilities": ["image_analysis", "ocr", "object_detection", "video_analysis"],
                "content_types": ["visual"],
                "complexity_levels": ["simple", "medium"]
            }
        },
        "content_types": [ct.value for ct in ContentType],
        "complexity_levels": [tc.value for tc in TaskComplexity]
    }

    return models_info


@router.get("/health")
async def router_health_check() -> Dict[str, Any]:
    """
    Health check for the intelligent router service
    """
    try:
        stats = intelligent_model_router.get_routing_stats()

        return {
            "status": "healthy",
            "service": "intelligent_model_router",
            "total_routed": stats["total_routed"],
            "active_models": len(stats["model_performance"]),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "intelligent_model_router",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
