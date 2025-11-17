#!/usr/bin/env python3
"""
Auto-Ingestion API Routes
Manage automatic file ingestion and approval workflows
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auto-ingest", tags=["auto-ingestion"])


# Pydantic models
class StartAutoIngestRequest(BaseModel):
    folders: Optional[List[str]] = None
    auto_approve_low_risk: bool = True


class ApprovalDecision(BaseModel):
    approval_id: str
    approved: bool
    reason: Optional[str] = None


# Routes
@router.post("/start")
async def start_auto_ingestion(request: StartAutoIngestRequest):
    """Start the auto-ingestion service"""
    try:
        from backend.memory_tables.auto_ingestion import auto_ingestion_service
        from backend.memory_tables.registry import table_registry
        
        # Ensure registry is loaded
        if not table_registry.schemas:
            table_registry.load_all_schemas()
        
        # Start service
        await auto_ingestion_service.start(folders=request.folders)
        
        return {
            'success': True,
            'message': 'Auto-ingestion started',
            'stats': auto_ingestion_service.get_stats()
        }
        
    except Exception as e:
        logger.error(f"Failed to start auto-ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_auto_ingestion():
    """Stop the auto-ingestion service"""
    try:
        from backend.memory_tables.auto_ingestion import auto_ingestion_service
        
        await auto_ingestion_service.stop()
        
        return {
            'success': True,
            'message': 'Auto-ingestion stopped'
        }
        
    except Exception as e:
        logger.error(f"Failed to stop auto-ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_auto_ingestion_status():
    """Get status of auto-ingestion service"""
    try:
        from backend.memory_tables.auto_ingestion import auto_ingestion_service
        
        stats = auto_ingestion_service.get_stats()
        
        return {
            'success': True,
            'status': 'running' if stats['running'] else 'stopped',
            'stats': stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending")
async def get_pending_approvals():
    """Get all pending approval requests"""
    try:
        from backend.memory_tables.auto_ingestion import auto_ingestion_service
        
        pending = auto_ingestion_service.get_pending_approvals()
        
        return {
            'success': True,
            'count': len(pending),
            'pending_approvals': pending
        }
        
    except Exception as e:
        logger.error(f"Failed to get pending approvals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve")
async def approve_ingestion(decision: ApprovalDecision):
    """Approve or reject a pending ingestion"""
    try:
        from backend.memory_tables.auto_ingestion import auto_ingestion_service
        
        if decision.approved:
            success = await auto_ingestion_service.approve_pending(decision.approval_id)
            message = 'Ingestion approved and processed'
        else:
            success = await auto_ingestion_service.reject_pending(decision.approval_id)
            message = 'Ingestion rejected'
        
        if not success:
            raise HTTPException(status_code=404, detail='Approval ID not found')
        
        return {
            'success': True,
            'message': message,
            'approval_id': decision.approval_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process approval: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-file")
async def process_single_file(file_path: str, background_tasks: BackgroundTasks):
    """Manually trigger processing of a single file"""
    try:
        from backend.memory_tables.auto_ingestion import auto_ingestion_service
        
        path = Path(file_path)
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        # Process in background
        background_tasks.add_task(auto_ingestion_service._process_file, path)
        
        return {
            'success': True,
            'message': f'Processing {file_path}',
            'file_path': file_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/failed")
async def get_failed_ingestions(limit: int = 50):
    """Get recent failed ingestion attempts"""
    try:
        from backend.memory_tables.registry import table_registry
        
        # Query insights table for failed ingestions
        rows = table_registry.query_rows(
            'memory_insights',
            filters={'insight_type': 'alert'},
            limit=limit
        )
        
        # Filter for failed ingestions
        failed = [
            {
                'file_path': row.file_path,
                'error': row.content,
                'timestamp': str(row.created_at) if hasattr(row, 'created_at') else None
            }
            for row in rows
            if 'failed to ingest' in row.content.lower()
        ]
        
        return {
            'success': True,
            'count': len(failed),
            'failed_ingestions': failed
        }
        
    except Exception as e:
        logger.error(f"Failed to get failed ingestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
