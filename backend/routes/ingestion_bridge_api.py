#!/usr/bin/env python3
"""
Ingestion Bridge API
Routes for managing ingestion jobs that populate Memory Tables
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ingestion-bridge", tags=["ingestion-bridge"])


class CreateJobRequest(BaseModel):
    file_path: str
    table_name: str
    job_type: str = "auto"


class UpdateMetadataRequest(BaseModel):
    metadata: Dict[str, Any]


@router.post("/jobs")
async def create_ingestion_job(request: CreateJobRequest, background_tasks: BackgroundTasks):
    """Create a new ingestion job"""
    try:
        from backend.memory_tables.ingestion_engine_bridge import ingestion_bridge
        
        # Validate file exists
        file_path = Path(request.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
        
        # Create job
        job = await ingestion_bridge.create_ingestion_job(
            file_path,
            request.table_name,
            request.job_type
        )
        
        if 'error' in job:
            raise HTTPException(status_code=500, detail=job['error'])
        
        # Execute in background
        background_tasks.add_task(
            ingestion_bridge.execute_ingestion_job,
            job['job_id']
        )
        
        return {
            'success': True,
            'job': job
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
async def list_ingestion_jobs():
    """List all active ingestion jobs"""
    try:
        from backend.memory_tables.ingestion_engine_bridge import ingestion_bridge
        
        jobs = ingestion_bridge.list_active_jobs()
        
        return {
            'success': True,
            'jobs': jobs,
            'count': len(jobs)
        }
        
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a specific job"""
    try:
        from backend.memory_tables.ingestion_engine_bridge import ingestion_bridge
        
        job = ingestion_bridge.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        
        return {
            'success': True,
            'job': job
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_ingestion_stats():
    """Get ingestion statistics"""
    try:
        from backend.memory_tables.ingestion_engine_bridge import ingestion_bridge
        
        stats = ingestion_bridge.get_stats()
        
        return {
            'success': True,
            'stats': stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/{table_name}")
async def query_table_for_ingestion(
    table_name: str,
    filters: Optional[Dict[str, Any]] = None
):
    """Query a table for ingestion/learning"""
    try:
        from backend.memory_tables.ingestion_engine_bridge import ingestion_bridge
        
        data = await ingestion_bridge.query_table_for_ingestion(table_name, filters)
        
        return {
            'success': True,
            'table': table_name,
            'data': data,
            'count': len(data)
        }
        
    except Exception as e:
        logger.error(f"Failed to query table: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/metadata/{table_name}/{row_id}")
async def update_ingestion_metadata(
    table_name: str,
    row_id: str,
    request: UpdateMetadataRequest
):
    """Update ingestion metadata for a row"""
    try:
        from backend.memory_tables.ingestion_engine_bridge import ingestion_bridge
        
        success = await ingestion_bridge.update_ingestion_metadata(
            table_name,
            row_id,
            request.metadata
        )
        
        return {
            'success': success,
            'table': table_name,
            'row_id': row_id
        }
        
    except Exception as e:
        logger.error(f"Failed to update metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))
