"""
Ingestion Pipeline API
Endpoints for managing ingestion workflows
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..auth import get_current_user
from ..ingestion_pipeline import get_ingestion_pipeline, IngestionMetrics

router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])


class StartPipelineRequest(BaseModel):
    pipeline_id: str
    file_path: str
    config: Optional[Dict[str, Any]] = None


@router.get("/pipelines")
async def list_pipelines(current_user: str = Depends(get_current_user)):
    """List all available ingestion pipelines"""
    pipeline = await get_ingestion_pipeline()
    return {"pipelines": pipeline.list_pipelines()}


@router.post("/start")
async def start_pipeline(
    req: StartPipelineRequest,
    current_user: str = Depends(get_current_user)
):
    """Start an ingestion pipeline for a file"""
    pipeline = await get_ingestion_pipeline()
    
    try:
        job_id = await pipeline.start_pipeline(
            req.pipeline_id,
            req.file_path,
            req.config
        )
        
        return {
            "job_id": job_id,
            "status": "started",
            "pipeline": req.pipeline_id,
            "file": req.file_path
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/jobs")
async def list_jobs(
    status: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """List all ingestion jobs"""
    pipeline = await get_ingestion_pipeline()
    jobs = pipeline.list_jobs(status)
    return {"jobs": jobs, "count": len(jobs)}


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get status of a specific job"""
    pipeline = await get_ingestion_pipeline()
    job = pipeline.get_job_status(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    current_user: str = Depends(get_current_user)
):
    """Cancel a running job"""
    pipeline = await get_ingestion_pipeline()
    success = await pipeline.cancel_job(job_id)
    
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Job not found or cannot be cancelled"
        )
    
    return {"status": "cancelled", "job_id": job_id}


@router.get("/metrics")
async def get_metrics(current_user: str = Depends(get_current_user)):
    """Get ingestion pipeline metrics"""
    pipeline = await get_ingestion_pipeline()
    metrics = await IngestionMetrics.get_metrics(pipeline)
    return metrics


@router.get("/recommend/{file_path:path}")
async def recommend_pipeline(
    file_path: str,
    current_user: str = Depends(get_current_user)
):
    """Recommend best pipeline for a file based on extension"""
    import os
    
    ext = os.path.splitext(file_path)[1].lower()
    
    pipeline = await get_ingestion_pipeline()
    pipelines = pipeline.list_pipelines()
    
    # Find matching pipelines
    matches = []
    for p in pipelines:
        if ext in p["file_types"] or "*" in p["file_types"]:
            matches.append(p)
    
    if not matches:
        return {
            "recommended": None,
            "message": f"No pipeline found for {ext} files"
        }
    
    # Return first match as recommendation
    return {
        "recommended": matches[0],
        "alternatives": matches[1:] if len(matches) > 1 else [],
        "file_type": ext
    }


@router.post("/analyze")
async def analyze_content(
    file_path: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    current_user: str = Depends(get_current_user)
):
    """Analyze file content for quality, duplicates, recommendations"""
    from ..content_intelligence import get_content_intelligence
    
    intelligence = await get_content_intelligence()
    analysis = await intelligence.analyze_file(file_path, content, metadata)
    
    return analysis


@router.get("/insights")
async def get_insights(current_user: str = Depends(get_current_user)):
    """Get overall content intelligence insights"""
    from ..content_intelligence import get_content_intelligence
    
    intelligence = await get_content_intelligence()
    insights = await intelligence.get_insights()
    
    return insights


@router.get("/schedules")
async def list_schedules(
    enabled_only: bool = False,
    current_user: str = Depends(get_current_user)
):
    """List all automation schedules"""
    from ..automation_scheduler import get_automation_scheduler
    
    scheduler = await get_automation_scheduler()
    schedules = scheduler.list_schedules(enabled_only)
    
    return {"schedules": schedules, "count": len(schedules)}


@router.post("/schedules")
async def create_schedule(
    schedule_id: str,
    pipeline_id: str,
    file_pattern: str,
    schedule_type: str,
    schedule_config: Dict[str, Any],
    enabled: bool = True,
    current_user: str = Depends(get_current_user)
):
    """Create a new automation schedule"""
    from ..automation_scheduler import get_automation_scheduler, ScheduleType
    
    scheduler = await get_automation_scheduler()
    
    try:
        schedule_type_enum = ScheduleType(schedule_type)
        schedule = scheduler.create_schedule(
            schedule_id, pipeline_id, file_pattern,
            schedule_type_enum, schedule_config, enabled
        )
        return schedule
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid schedule type: {schedule_type}")


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete an automation schedule"""
    from ..automation_scheduler import get_automation_scheduler
    
    scheduler = await get_automation_scheduler()
    success = scheduler.delete_schedule(schedule_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return {"status": "deleted", "schedule_id": schedule_id}


@router.get("/templates")
async def list_templates(current_user: str = Depends(get_current_user)):
    """List automation templates"""
    from ..automation_scheduler import AUTOMATION_TEMPLATES
    
    return {"templates": AUTOMATION_TEMPLATES}
