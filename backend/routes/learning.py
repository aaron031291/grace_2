"""
Self-Healing Learning API

Provides aggregated learning data and analytics for:
- Playbook success rates by time bucket
- Diagnosis effectiveness
- Service-specific patterns
- Continuous improvement metrics
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..models import async_session
from ..settings import settings
from ..schemas import LearningAggregatesResponse, LearningOutcomesResponse

router = APIRouter(prefix="/api/self_heal", tags=["self-heal-learning"])


@router.get("/learning", response_model=LearningAggregatesResponse)
async def get_learning_aggregates(
    time_bucket: str = Query("24h", description="Time bucket: all, 24h, 7d"),
    service: Optional[str] = Query(None, description="Filter by service"),
    playbook: Optional[str] = Query(None, description="Filter by playbook"),
    current_user: str = Depends(get_current_user)
):
    """
    Get learning aggregates and success rate analytics.
    
    Returns:
    - Overall success rates by time bucket
    - Playbook effectiveness rankings
    - Service-specific patterns
    - Diagnosis correlation data
    """
    
    if not settings.LEARNING_AGGREGATION_ENABLED:
        raise HTTPException(status_code=404, detail="Learning aggregation endpoint disabled")
    
    try:
        from ..self_heal_models import PlaybookRun, LearningLog
    except ImportError:
        raise HTTPException(status_code=503, detail="Self-heal models not available")
    
    async with async_session() as session:
        now = datetime.now(timezone.utc)
        
        # Determine cutoff based on bucket
        if time_bucket == "24h":
            cutoff = now - timedelta(hours=24)
            bucket_label = "Last 24 Hours"
        elif time_bucket == "7d":
            cutoff = now - timedelta(days=7)
            bucket_label = "Last 7 Days"
        else:  # all
            cutoff = datetime(2020, 1, 1, tzinfo=timezone.utc)
            bucket_label = "All Time"
        
        # Build base query
        query = select(PlaybookRun).where(PlaybookRun.created_at >= cutoff)
        
        if service:
            query = query.where(PlaybookRun.service == service)
        
        if playbook:
            query = query.where(PlaybookRun.playbook_id == playbook)
        
        result = await session.execute(query.order_by(PlaybookRun.created_at.desc()))
        runs = result.scalars().all()
        
        # Aggregate statistics
        total_runs = len(runs)
        
        if total_runs == 0:
            return {
                "bucket": bucket_label,
                "time_range": time_bucket,
                "total_runs": 0,
                "overall_success_rate": 0.0,
                "by_playbook": {},
                "by_service": {},
                "by_status": {},
                "recent_trends": []
            }
        
        # Count by status
        by_status = {}
        succeeded = 0
        failed = 0
        
        for run in runs:
            status = run.status or "unknown"
            by_status[status] = by_status.get(status, 0) + 1
            
            if status == "succeeded":
                succeeded += 1
            elif status == "failed":
                failed += 1
        
        overall_success_rate = (succeeded / (succeeded + failed)) if (succeeded + failed) > 0 else 0.0
        
        # Aggregate by playbook
        by_playbook = {}
        for run in runs:
            pb_id = run.playbook_id or "unknown"
            if pb_id not in by_playbook:
                by_playbook[pb_id] = {
                    "total": 0,
                    "succeeded": 0,
                    "failed": 0,
                    "success_rate": 0.0,
                    "avg_duration_seconds": 0.0,
                    "durations": []
                }
            
            by_playbook[pb_id]["total"] += 1
            
            if run.status == "succeeded":
                by_playbook[pb_id]["succeeded"] += 1
            elif run.status == "failed":
                by_playbook[pb_id]["failed"] += 1
            
            # Calculate duration if available
            if run.started_at and run.ended_at:
                duration = (run.ended_at - run.started_at).total_seconds()
                by_playbook[pb_id]["durations"].append(duration)
        
        # Calculate success rates and avg durations
        for pb_id, stats in by_playbook.items():
            if stats["succeeded"] + stats["failed"] > 0:
                stats["success_rate"] = stats["succeeded"] / (stats["succeeded"] + stats["failed"])
            
            if stats["durations"]:
                stats["avg_duration_seconds"] = sum(stats["durations"]) / len(stats["durations"])
            
            del stats["durations"]  # Remove from response
        
        # Aggregate by service
        by_service = {}
        for run in runs:
            svc = run.service or "unknown"
            if svc not in by_service:
                by_service[svc] = {
                    "total": 0,
                    "succeeded": 0,
                    "failed": 0,
                    "success_rate": 0.0
                }
            
            by_service[svc]["total"] += 1
            if run.status == "succeeded":
                by_service[svc]["succeeded"] += 1
            elif run.status == "failed":
                by_service[svc]["failed"] += 1
        
        # Calculate service success rates
        for svc, stats in by_service.items():
            if stats["succeeded"] + stats["failed"] > 0:
                stats["success_rate"] = stats["succeeded"] / (stats["succeeded"] + stats["failed"])
        
        # Recent trends (last 10 runs)
        recent_trends = []
        for run in runs[:10]:
            recent_trends.append({
                "timestamp": run.created_at.isoformat() if run.created_at else None,
                "service": run.service,
                "playbook": run.playbook_id,
                "status": run.status,
                "requested_by": run.requested_by
            })
        
        # Top performers
        playbook_rankings = sorted(
            [
                {"playbook": pb_id, **stats}
                for pb_id, stats in by_playbook.items()
            ],
            key=lambda x: (x["success_rate"], x["total"]),
            reverse=True
        )
        
        return {
            "bucket": bucket_label,
            "time_range": time_bucket,
            "total_runs": total_runs,
            "overall_success_rate": overall_success_rate,
            "by_status": by_status,
            "by_playbook": by_playbook,
            "by_service": by_service,
            "playbook_rankings": playbook_rankings[:10],
            "recent_trends": recent_trends,
            "metadata": {
                "generated_at": now.isoformat(),
                "filter_service": service,
                "filter_playbook": playbook
            }
        }


@router.get("/learning/outcomes", response_model=LearningOutcomesResponse)
async def get_learning_outcomes(
    limit: int = Query(50, le=500),
    service: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Get recent learning log entries with outcomes"""
    
    if not settings.LEARNING_AGGREGATION_ENABLED:
        raise HTTPException(status_code=404, detail="Learning endpoint disabled")
    
    try:
        from ..self_heal_models import LearningLog
    except ImportError:
        raise HTTPException(status_code=503, detail="Learning models not available")
    
    async with async_session() as session:
        query = select(LearningLog).order_by(LearningLog.created_at.desc()).limit(limit)
        
        if service:
            query = query.where(LearningLog.service == service)
        
        result = await session.execute(query)
        logs = result.scalars().all()
        
        outcomes = []
        for log in logs:
            try:
                diagnosis = json.loads(log.diagnosis) if log.diagnosis else {}
                action = json.loads(log.action) if log.action else {}
                outcome = json.loads(log.outcome) if log.outcome else {}
            except:
                diagnosis = {}
                action = {}
                outcome = {}
            
            outcomes.append({
                "id": log.id,
                "service": log.service,
                "timestamp": log.created_at.isoformat() if log.created_at else None,
                "diagnosis": diagnosis,
                "action": action,
                "outcome": outcome,
                "learned": outcome.get("result") if outcome else None
            })
        
        return {
            "outcomes": outcomes,
            "count": len(outcomes),
            "service_filter": service
        }


import json
