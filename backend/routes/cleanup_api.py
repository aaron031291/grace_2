"""
Cleanup Management API

Endpoints for triggering and monitoring snapshot/cache cleanup.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import logging

from backend.utils.snapshot_cleanup import SnapshotCleanupManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cleanup", tags=["Cleanup"])


class CleanupRequest(BaseModel):
    dry_run: bool = False


class CleanupResponse(BaseModel):
    success: bool
    items_deleted: int
    bytes_freed: int
    mb_freed: float
    errors: int


@router.post("/run", response_model=CleanupResponse)
async def run_cleanup(request: CleanupRequest = CleanupRequest()):
    """
    Trigger snapshot and cache cleanup
    
    - **dry_run**: If true, shows what would be deleted without actually deleting
    """
    try:
        manager = SnapshotCleanupManager()
        stats = manager.cleanup_all(dry_run=request.dry_run)
        
        return CleanupResponse(
            success=True,
            items_deleted=stats["items_deleted"],
            bytes_freed=stats["bytes_freed"],
            mb_freed=stats["bytes_freed"] / 1024 / 1024,
            errors=stats["errors"],
        )
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_cleanup_stats() -> Dict[str, Any]:
    """
    Get current disk usage statistics for snapshots and caches
    """
    try:
        manager = SnapshotCleanupManager()
        stats = manager.get_disk_usage_stats()
        return {
            "success": True,
            "stats": stats,
        }
    except Exception as e:
        logger.error(f"Failed to get cleanup stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
