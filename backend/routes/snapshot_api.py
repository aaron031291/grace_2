"""
Snapshot Management API
Control boot snapshots and rollback capability
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter(
    prefix="/api/snapshots",
    tags=["Boot Snapshots"]
)


@router.get("/list")
async def list_snapshots():
    """List all available boot snapshots"""
    from backend.boot.snapshot_manager import boot_snapshot_manager
    
    snapshots = boot_snapshot_manager.list_snapshots()
    
    return {
        "snapshots": snapshots,
        "total": len(snapshots),
        "max_retention": boot_snapshot_manager.max_snapshots
    }


@router.get("/stats")
async def get_snapshot_stats():
    """Get snapshot manager statistics"""
    from backend.boot.snapshot_manager import boot_snapshot_manager
    
    return boot_snapshot_manager.get_stats()


@router.post("/restore/{snapshot_id}")
async def restore_snapshot(snapshot_id: str):
    """
    Restore system from a snapshot
    
    WARNING: This will overwrite current state
    Server must be restarted after restore
    """
    from backend.boot.snapshot_manager import boot_snapshot_manager
    
    result = await boot_snapshot_manager.restore_snapshot(snapshot_id)
    
    if not result.get("restored"):
        raise HTTPException(status_code=400, detail=result.get("error", "Restore failed"))
    
    return result


@router.delete("/{snapshot_id}")
async def delete_snapshot(snapshot_id: str):
    """Delete a specific snapshot"""
    from backend.boot.snapshot_manager import boot_snapshot_manager
    import shutil
    
    snapshot_dir = boot_snapshot_manager.snapshot_root / snapshot_id
    
    if not snapshot_dir.exists():
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    try:
        shutil.rmtree(snapshot_dir)
        return {
            "deleted": True,
            "snapshot_id": snapshot_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {e}")
