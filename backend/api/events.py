"""
Events API
Real-time event streaming and history
"""

from fastapi import APIRouter, Query
from typing import Dict, Any, Optional

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/recent")
async def get_recent_events(
    limit: int = Query(50, le=200),
    event_type: Optional[str] = None
) -> Dict[str, Any]:
    """Get recent events from the event bus"""
    from backend.services.event_bus import event_bus
    
    events = event_bus.get_recent_events(limit, event_type)
    
    return {
        "events": events,
        "count": len(events)
    }


@router.get("/stats")
async def get_event_stats() -> Dict[str, Any]:
    """Get event bus statistics"""
    from backend.services.event_bus import event_bus
    
    return event_bus.get_stats()


@router.post("/publish")
async def publish_event(event_type: str, payload: Dict[str, Any]):
    """Manually publish an event (for testing)"""
    from backend.services.event_bus import event_bus
    
    await event_bus.publish(event_type, payload)
    
    return {
        "success": True,
        "message": f"Event '{event_type}' published"
    }


@router.get("/types")
async def list_event_types() -> Dict[str, Any]:
    """List all available event types"""
    return {
        "event_types": [
            "librarian.file.created",
            "librarian.file.modified",
            "librarian.file.deleted",
            "ingestion.started",
            "ingestion.completed",
            "ingestion.failed",
            "self_healing.triggered",
            "self_healing.completed",
            "schema.proposed",
            "schema.approved",
            "schema.rejected",
            "log_pattern.error",
            "log_pattern.warning",
            "log_pattern.critical",
        ]
    }
