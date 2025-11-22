"""
Temporal Domain Router
Consolidates all time-based operations: schedules, timers, TTL, snapshots, rollbacks

Bounded Context: Time and temporal operations
- Schedules: cron jobs, recurring tasks, timed events
- Timers: one-time timers, timeouts, delays
- TTL: time-to-live management, expiration
- Snapshots: point-in-time captures, versioning
- Rollbacks: temporal reversion operations

Canonical Verbs: schedule, timer, expire, snapshot, rollback, rewind
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from ..auth import get_current_user
from ..temporal_reasoning import temporal_forecaster

router = APIRouter(prefix="/api/temporal", tags=["Temporal Domain"])


class ScheduleRequest(BaseModel):
    task_name: str
    cron_expression: str
    task_data: Dict[str, Any]
    enabled: bool = True


class TimerRequest(BaseModel):
    task_name: str
    delay_seconds: int
    task_data: Dict[str, Any]


class TTLRequest(BaseModel):
    resource_id: str
    resource_type: str
    ttl_seconds: int
    auto_cleanup: bool = True


class SnapshotRequest(BaseModel):
    resource_type: str
    resource_id: Optional[str] = None
    name: Optional[str] = None


class RollbackRequest(BaseModel):
    snapshot_id: str
    target_resource: Optional[str] = None


@router.post("/schedule")
async def create_schedule(
    request: ScheduleRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a scheduled task"""
    try:
        schedule = await temporal_forecaster.schedule_task(
            name=request.task_name,
            cron=request.cron_expression,
            task_data=request.task_data,
            enabled=request.enabled
        )

        return {
            "schedule_id": schedule.get("id"),
            "task_name": request.task_name,
            "cron": request.cron_expression,
            "status": "scheduled"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/timer")
async def create_timer(
    request: TimerRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a one-time timer"""
    try:
        timer = await temporal_forecaster.create_timer(
            name=request.task_name,
            delay=request.delay_seconds,
            task_data=request.task_data
        )

        return {
            "timer_id": timer.get("id"),
            "task_name": request.task_name,
            "delay_seconds": request.delay_seconds,
            "expires_at": timer.get("expires_at"),
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ttl")
async def set_ttl(
    request: TTLRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Set time-to-live for a resource"""
    try:
        ttl_record = await temporal_forecaster.set_ttl(
            resource_id=request.resource_id,
            resource_type=request.resource_type,
            ttl_seconds=request.ttl_seconds,
            auto_cleanup=request.auto_cleanup
        )

        return {
            "resource_id": request.resource_id,
            "resource_type": request.resource_type,
            "ttl_seconds": request.ttl_seconds,
            "expires_at": ttl_record.get("expires_at"),
            "status": "set"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/snapshot")
async def create_snapshot(
    request: SnapshotRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a point-in-time snapshot"""
    try:
        snapshot = await temporal_forecaster.create_snapshot(
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            name=request.name
        )

        return {
            "snapshot_id": snapshot.get("id"),
            "resource_type": request.resource_type,
            "resource_id": request.resource_id,
            "name": request.name,
            "timestamp": snapshot.get("timestamp"),
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rollback")
async def rollback_to_snapshot(
    request: RollbackRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Rollback to a snapshot"""
    try:
        rollback = await temporal_forecaster.rollback_to_snapshot(
            snapshot_id=request.snapshot_id,
            target_resource=request.target_resource
        )

        return {
            "snapshot_id": request.snapshot_id,
            "target_resource": request.target_resource,
            "status": "rolled_back",
            "changes_reverted": rollback.get("changes", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedules")
async def list_schedules(
    active_only: bool = True,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List scheduled tasks"""
    try:
        schedules = await temporal_forecaster.list_schedules(active_only=active_only)
        return {
            "schedules": schedules,
            "count": len(schedules),
            "filter": {"active_only": active_only}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timers")
async def list_timers(
    active_only: bool = True,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List active timers"""
    try:
        timers = await temporal_forecaster.list_timers(active_only=active_only)
        return {
            "timers": timers,
            "count": len(timers),
            "filter": {"active_only": active_only}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ttl")
async def list_expiring_resources(
    within_hours: int = 24,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List resources expiring soon"""
    try:
        expiring = await temporal_forecaster.list_expiring_resources(hours=within_hours)
        return {
            "expiring_resources": expiring,
            "count": len(expiring),
            "within_hours": within_hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/snapshots")
async def list_snapshots(
    resource_type: Optional[str] = None,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List available snapshots"""
    try:
        snapshots = await temporal_forecaster.list_snapshots(resource_type=resource_type)
        return {
            "snapshots": snapshots,
            "count": len(snapshots),
            "filter": {"resource_type": resource_type} if resource_type else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/schedule/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Delete a scheduled task"""
    try:
        result = await temporal_forecaster.delete_schedule(schedule_id)
        return {
            "schedule_id": schedule_id,
            "status": "deleted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/timer/{timer_id}")
async def cancel_timer(
    timer_id: str,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Cancel a timer"""
    try:
        result = await temporal_forecaster.cancel_timer(timer_id)
        return {
            "timer_id": timer_id,
            "status": "cancelled"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/{resource_type}")
async def forecast_temporal(
    resource_type: str,
    forecast_hours: int = 24,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Generate temporal forecast"""
    try:
        forecast = await temporal_forecaster.forecast_resource(
            resource_type=resource_type,
            hours_ahead=forecast_hours
        )

        return {
            "resource_type": resource_type,
            "forecast_hours": forecast_hours,
            "forecast": forecast
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
