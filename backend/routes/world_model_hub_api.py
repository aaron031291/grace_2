"""
World Model Hub API - Unified Orb Interface
Unified interface for World Model Hub frontend with Orb capabilities
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime

from backend.world_model import world_model_service
from backend.models.orb import (
    SessionCreateRequest, SessionInfoResponse,
    ScreenShareRequest, ScreenShareResponse,
    RecordingRequest, RecordingResponse,
    VoiceToggleResponse, TaskCreateRequest, TaskResponse,
    OrbStats, SandboxExperiment, ConsensusPersona,
    FeedbackItem, SovereigntyMetrics
)

router = APIRouter(prefix="/api/world_model_hub", tags=["world_model_hub"])


class ChatMessage(BaseModel):
    """Chat message to Grace"""
    message: str
    user_id: str = "user"
    context: Optional[Dict[str, Any]] = None


class ApprovalAction(BaseModel):
    """Approval or decline action"""
    trace_id: str
    action: str  # "approve" or "decline"
    reason: Optional[str] = None
    user_id: str = "user"


# ============================================================================
# ============================================================================

@router.get("/context")
async def get_context(
    query: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50)
) -> Dict[str, Any]:
    """
    Get current context for World Model Hub
    
    Returns:
        - Recent artifacts
        - Active missions
        - Pending approvals
        - Learning jobs
        - System health
        - Relevant knowledge (if query provided)
    """
    return await world_model_service.query_context(
        user_query=query,
        limit=limit
    )


@router.post("/chat")
async def chat_with_grace(message: ChatMessage) -> Dict[str, Any]:
    """
    Send a message to Grace and get a response
    
    Args:
        message: User message with optional context
    
    Returns:
        Grace's response with trace_id and relevant knowledge
    """
    return await world_model_service.chat_with_grace(
        message=message.message,
        user_id=message.user_id,
        context=message.context
    )


@router.get("/trace/{trace_id}")
async def get_trace(trace_id: str) -> Dict[str, Any]:
    """
    Get execution trace details
    
    Args:
        trace_id: Trace ID to retrieve
    
    Returns:
        Events, actions, and reflections for the trace
    """
    return await world_model_service.link_trace(
        message_id="",  # Not needed for retrieval
        trace_id=trace_id
    )


# ============================================================================
# ============================================================================

@router.get("/artifacts")
async def list_artifacts(
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None
) -> Dict[str, Any]:
    """
    List recent artifacts from world model
    
    Args:
        limit: Maximum number of artifacts
        category: Filter by category (self, system, user, domain, temporal)
    
    Returns:
        List of artifacts
    """
    artifacts = await world_model_service.list_recent_artifacts(
        limit=limit,
        category=category
    )
    
    return {
        "artifacts": artifacts,
        "count": len(artifacts)
    }


# ============================================================================
# ============================================================================

@router.get("/missions")
async def list_missions(
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    List missions
    
    Args:
        status: Filter by status (active, completed, failed)
    
    Returns:
        List of missions
    """
    missions = await world_model_service.list_active_missions()
    
    
    return {
        "missions": missions,
        "count": len(missions)
    }


# ============================================================================
# ============================================================================

@router.get("/approvals")
async def list_approvals(
    limit: int = Query(20, ge=1, le=100)
) -> Dict[str, Any]:
    """
    List pending approvals
    
    Args:
        limit: Maximum number of approvals
    
    Returns:
        List of pending approvals
    """
    approvals = await world_model_service.list_pending_approvals(limit=limit)
    
    return {
        "approvals": approvals,
        "count": len(approvals)
    }


@router.post("/approvals/action")
async def handle_approval(action: ApprovalAction) -> Dict[str, Any]:
    """
    Approve or decline an action
    
    Args:
        action: Approval action (approve or decline)
    
    Returns:
        Result of the action
    """
    if action.action == "approve":
        return await world_model_service.approve_action(
            trace_id=action.trace_id,
            approved_by=action.user_id
        )
    elif action.action == "decline":
        return await world_model_service.decline_action(
            trace_id=action.trace_id,
            reason=action.reason or "Declined by user",
            declined_by=action.user_id
        )
    else:
        return {
            "success": False,
            "error": f"Invalid action: {action.action}. Must be 'approve' or 'decline'"
        }


# ============================================================================
# ============================================================================

@router.get("/health")
async def get_health() -> Dict[str, Any]:
    """
    Get World Model Hub health status
    
    Returns:
        System health and statistics
    """
    stats = world_model_service.get_stats()
    
    return {
        "status": "operational" if stats["initialized"] else "initializing",
        "stats": stats
    }


@router.post("/initialize")
async def initialize() -> Dict[str, Any]:
    """
    Initialize World Model Hub service
    
    Returns:
        Initialization status
    """
    await world_model_service.initialize()
    
    return {
        "status": "initialized",
        "message": "World Model Hub service initialized successfully"
    }


# ============================================================================
# ============================================================================

@router.post("/session/create")
async def create_session(request: SessionCreateRequest) -> Dict[str, Any]:
    """
    Create a new Orb session
    
    Args:
        request: Session creation request with user_id
    
    Returns:
        Session ID and metadata
    """
    session_id = await world_model_service.create_orb_session(
        user_id=request.user_id,
        metadata=request.metadata
    )
    
    return {
        "session_id": session_id,
        "status": "active",
        "message": "Orb session created successfully"
    }


@router.get("/session/{session_id}/info")
async def get_session_info(session_id: str) -> SessionInfoResponse:
    """
    Get session information with duration and topics
    
    Args:
        session_id: Session identifier
    
    Returns:
        Session info with duration, topics, message count
    """
    info = await world_model_service.get_session_info(session_id)
    
    if not info:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    return SessionInfoResponse(**info)


@router.post("/session/{session_id}/close")
async def close_session(session_id: str) -> Dict[str, Any]:
    """
    Close an Orb session and save to vector store
    
    Args:
        session_id: Session identifier
    
    Returns:
        Session summary with duration and topics
    """
    summary = await world_model_service.close_orb_session(session_id)
    
    if not summary:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    return {
        "status": "closed",
        "summary": summary,
        "message": "Session closed and saved successfully"
    }


# ============================================================================
# ============================================================================

@router.post("/multimodal/screen-share/start")
async def start_screen_share(request: ScreenShareRequest) -> ScreenShareResponse:
    """
    Start screen sharing session (Phase 1: simulated)
    
    Args:
        request: Screen share request with quality settings
    
    Returns:
        Session ID and status
    """
    session_id = await world_model_service.start_screen_share(
        user_id=request.user_id,
        quality_settings=request.quality_settings
    )
    
    return ScreenShareResponse(
        session_id=session_id,
        status="active",
        message="Screen sharing started (simulated in Phase 1)"
    )


@router.post("/multimodal/screen-share/stop")
async def stop_screen_share(session_id: str) -> Dict[str, Any]:
    """
    Stop screen sharing session
    
    Args:
        session_id: Screen share session ID
    
    Returns:
        Status and summary
    """
    success = await world_model_service.stop_screen_share(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Screen share session {session_id} not found")
    
    return {
        "status": "stopped",
        "session_id": session_id,
        "message": "Screen sharing stopped"
    }


@router.post("/multimodal/recording/start")
async def start_recording(request: RecordingRequest) -> RecordingResponse:
    """
    Start recording session (Phase 1: simulated)
    
    Args:
        request: Recording request with media type
    
    Returns:
        Session ID and status
    """
    session_id = await world_model_service.start_recording(
        user_id=request.user_id,
        media_type=request.media_type,
        metadata=request.metadata
    )
    
    return RecordingResponse(
        session_id=session_id,
        status="recording",
        message=f"{request.media_type} recording started (simulated in Phase 1)"
    )


@router.post("/multimodal/recording/stop")
async def stop_recording(session_id: str) -> Dict[str, Any]:
    """
    Stop recording session
    
    Args:
        session_id: Recording session ID
    
    Returns:
        Recording details with file path and duration
    """
    result = await world_model_service.stop_recording(session_id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Recording session {session_id} not found")
    
    return {
        "status": "completed",
        "session_id": session_id,
        "file_path": result.get("file_path"),
        "duration": result.get("duration"),
        "message": "Recording stopped and saved"
    }


@router.post("/multimodal/voice/toggle")
async def toggle_voice(user_id: str, enable: bool) -> VoiceToggleResponse:
    """
    Toggle voice control for user
    
    Args:
        user_id: User identifier
        enable: Enable or disable voice
    
    Returns:
        Voice status
    """
    enabled = await world_model_service.toggle_voice(user_id, enable)
    
    return VoiceToggleResponse(
        voice_enabled=enabled,
        user_id=user_id,
        message=f"Voice {'enabled' if enabled else 'disabled'}"
    )


# ============================================================================
# ============================================================================

@router.get("/sandbox/experiments")
async def list_experiments() -> Dict[str, Any]:
    """
    List sandbox experiments
    
    Returns:
        List of experiments with status and metrics
    """
    experiments = await world_model_service.list_sandbox_experiments()
    
    return {
        "experiments": experiments,
        "count": len(experiments)
    }


@router.get("/sandbox/consensus")
async def get_consensus() -> Dict[str, Any]:
    """
    Get cross-persona consensus votes
    
    Returns:
        Consensus votes from different personas
    """
    consensus = await world_model_service.get_consensus_votes()
    
    return {
        "consensus": consensus,
        "count": len(consensus)
    }


@router.get("/sandbox/feedback")
async def get_feedback_queue() -> Dict[str, Any]:
    """
    Get human feedback queue
    
    Returns:
        Pending feedback items
    """
    feedback = await world_model_service.get_feedback_queue()
    
    return {
        "feedback": feedback,
        "count": len(feedback)
    }


@router.get("/sandbox/sovereignty")
async def get_sovereignty_metrics() -> SovereigntyMetrics:
    """
    Get Grace's sovereignty metrics
    
    Returns:
        Autonomy level, success rate, learning velocity, etc.
    """
    metrics = await world_model_service.get_sovereignty_metrics()
    
    return SovereigntyMetrics(**metrics)


# ============================================================================
# ============================================================================

@router.post("/tasks")
async def create_task(request: TaskCreateRequest) -> TaskResponse:
    """
    Create a background task
    
    Args:
        request: Task creation request
    
    Returns:
        Task ID and status
    """
    task_id = await world_model_service.create_background_task(
        task_type=request.task_type,
        metadata=request.metadata
    )
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="Background task created"
    )


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get background task status
    
    Args:
        task_id: Task identifier
    
    Returns:
        Task status and details
    """
    task = await world_model_service.get_task_status(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return task


# ============================================================================
# ============================================================================

@router.get("/stats")
async def get_orb_stats() -> OrbStats:
    """
    Get comprehensive Orb statistics
    
    Returns:
        Unified stats for sessions, memory, intelligence, governance, multimodal
    """
    stats = await world_model_service.get_orb_stats()
    
    return OrbStats(**stats)
