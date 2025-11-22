"""
Learning Visibility API
REST endpoints for monitoring Grace's learning activities
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.remote_access.learning_tracker import (
    get_learning_tracker,
    LearningSource,
    LearningStatus
)


router = APIRouter(prefix="/api/learning", tags=["Learning Visibility"])


# Request/Response Models
class StartSessionRequest(BaseModel):
    target_domain: str = Field(..., description="Domain or topic to learn about")
    goals: List[str] = Field(..., description="Learning goals for this session")


class RecordActivityRequest(BaseModel):
    source_type: str = Field(..., description="Type of learning source")
    source_url: str = Field(..., description="URL or identifier of the source")
    data_content: str = Field(..., description="Base64 encoded content or text content")
    content_type: str = Field(..., description="MIME type of content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UpdateActivityRequest(BaseModel):
    status: str = Field(..., description="New status")
    validation_score: Optional[float] = None
    integration_status: Optional[str] = None
    error: Optional[str] = None


# Endpoints
@router.get("/status")
async def get_learning_status():
    """
    Get real-time learning status
    Shows active sessions, recent activities, and current metrics
    """
    tracker = get_learning_tracker()
    status = tracker.get_realtime_status()
    return {
        "success": True,
        "data": status
    }


@router.get("/analytics")
async def get_learning_analytics():
    """
    Get comprehensive learning analytics
    Includes success rates, data volumes, source performance, etc.
    """
    tracker = get_learning_tracker()
    analytics = tracker.get_learning_analytics()
    return {
        "success": True,
        "data": analytics
    }


@router.post("/session/start")
async def start_learning_session(request: StartSessionRequest):
    """
    Start a new learning session
    """
    try:
        tracker = get_learning_tracker()
        session_id = tracker.start_session(
            target_domain=request.target_domain,
            goals=request.goals
        )
        return {
            "success": True,
            "session_id": session_id,
            "message": f"Learning session started for domain: {request.target_domain}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/end")
async def end_learning_session():
    """
    End the current learning session
    Returns session report
    """
    try:
        tracker = get_learning_tracker()
        report = tracker.end_session()
        return {
            "success": True,
            "data": report
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/activity/record")
async def record_learning_activity(request: RecordActivityRequest):
    """
    Record a new learning activity
    """
    try:
        # Validate source type
        try:
            source_type = LearningSource(request.source_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source_type. Must be one of: {[s.value for s in LearningSource]}"
            )
        
        # Convert content to bytes
        import base64
        try:
            data_bytes = base64.b64decode(request.data_content)
        except:
            # If not base64, treat as UTF-8 string
            data_bytes = request.data_content.encode('utf-8')
        
        tracker = get_learning_tracker()
        activity_id = tracker.record_activity(
            source_type=source_type,
            source_url=request.source_url,
            data_content=data_bytes,
            content_type=request.content_type,
            metadata=request.metadata
        )
        
        return {
            "success": True,
            "activity_id": activity_id,
            "message": "Learning activity recorded"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activity/{activity_id}")
async def get_activity(activity_id: str):
    """
    Get details of a specific learning activity
    """
    tracker = get_learning_tracker()
    activity = tracker.get_activity(activity_id)
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    return {
        "success": True,
        "data": activity
    }


@router.put("/activity/{activity_id}/status")
async def update_activity_status(activity_id: str, request: UpdateActivityRequest):
    """
    Update the status of a learning activity
    """
    try:
        # Validate status
        try:
            status = LearningStatus(request.status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {[s.value for s in LearningStatus]}"
            )
        
        tracker = get_learning_tracker()
        tracker.update_activity_status(
            activity_id=activity_id,
            status=status,
            validation_score=request.validation_score,
            integration_status=request.integration_status,
            error=request.error
        )
        
        return {
            "success": True,
            "message": f"Activity {activity_id} status updated to {request.status}"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/activity/{activity_id}/validate")
async def validate_activity(activity_id: str):
    """
    Validate that a learning activity was properly absorbed
    Returns validation report with score
    """
    try:
        tracker = get_learning_tracker()
        validation_report = tracker.validate_learning(activity_id)
        
        return {
            "success": True,
            "data": validation_report
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """
    Get details of a specific learning session
    """
    tracker = get_learning_tracker()
    session = tracker.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "success": True,
        "data": session
    }


@router.get("/dashboard/realtime")
async def get_realtime_dashboard():
    """
    Get real-time dashboard data for monitoring
    Optimized for frequent polling
    """
    tracker = get_learning_tracker()
    status = tracker.get_realtime_status()
    
    # Add additional dashboard-specific data
    dashboard_data = {
        **status,
        "health": {
            "tracker_active": True,
            "last_activity": status["recent_activities"][0]["timestamp"] if status["recent_activities"] else None,
            "validation_health": "good" if status["validation_rate"] > 0.8 else "warning" if status["validation_rate"] > 0.5 else "poor"
        },
        "alerts": []
    }
    
    # Generate alerts
    if status["active_session"] and status["current_learning_rate"]["last_5_min"] == 0:
        dashboard_data["alerts"].append({
            "severity": "warning",
            "message": "No learning activity in the last 5 minutes"
        })
    
    if status["validation_rate"] < 0.5:
        dashboard_data["alerts"].append({
            "severity": "error",
            "message": f"Low validation rate: {status['validation_rate']:.1%}"
        })
    
    return {
        "success": True,
        "timestamp": datetime.utcnow().isoformat(),
        "data": dashboard_data
    }


@router.get("/report/validation")
async def get_validation_report(
    hours: int = Query(default=24, ge=1, le=168, description="Hours to look back")
):
    """
    Get validation report for specified time period
    """
    tracker = get_learning_tracker()
    analytics = tracker.get_learning_analytics()
    
    # Filter for time period would go here
    # For now, return full analytics as validation report
    
    report = {
        "period_hours": hours,
        "generated_at": datetime.utcnow().isoformat(),
        "summary": {
            "total_activities": analytics.get("activities", {}).get("total", 0),
            "validated_activities": analytics.get("activities", {}).get("validated", 0),
            "failed_activities": analytics.get("activities", {}).get("failed", 0),
            "success_rate": analytics.get("activities", {}).get("success_rate", 0),
            "avg_validation_score": analytics.get("average_validation_score", 0)
        },
        "data_volume": analytics.get("data_volume", {}),
        "source_performance": analytics.get("source_performance", {}),
        "learning_velocity": analytics.get("learning_velocity", {})
    }
    
    return {
        "success": True,
        "data": report
    }


@router.get("/sources/supported")
async def get_supported_sources():
    """
    Get list of supported learning sources
    """
    return {
        "success": True,
        "sources": [
            {
                "type": source.value,
                "name": source.name.replace("_", " ").title(),
                "description": f"Learning from {source.name.lower().replace('_', ' ')}"
            }
            for source in LearningSource
        ]
    }


@router.get("/health")
async def learning_health_check():
    """
    Health check endpoint for learning system
    """
    try:
        tracker = get_learning_tracker()
        status = tracker.get_realtime_status()
        
        return {
            "success": True,
            "status": "healthy",
            "tracker_initialized": True,
            "total_activities": status["total_activities"],
            "validation_rate": status["validation_rate"],
            "active_session": bool(status["active_session"])
        }
    except Exception as e:
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e)
        }
