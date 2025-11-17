"""
Storage Tracking API
Monitor Grace's learning data storage (MB, GB, TB)
"""

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/storage", tags=["Storage Tracking"])


@router.get("/report")
async def get_storage_report():
    """
    Get complete storage usage report
    Shows MB, GB, TB usage across all learning data
    """
    try:
        from backend.services.storage_tracker import storage_tracker
        
        report = await storage_tracker.get_storage_report()
        return report
    
    except Exception as e:
        logger.error(f"[STORAGE-API] Storage report failed: {e}")
        return {
            "error": str(e),
            "status": "degraded"
        }


@router.get("/learning-data")
async def get_learning_data_breakdown():
    """
    Breakdown of learning data storage by type
    Shows: docs, code, datasets, repos
    """
    try:
        from backend.services.storage_tracker import storage_tracker
        
        breakdown = await storage_tracker.get_learning_data_breakdown()
        return breakdown
    
    except Exception as e:
        logger.error(f"[STORAGE-API] Learning data breakdown failed: {e}")
        return {
            "error": str(e)
        }


@router.get("/capacity-check")
async def check_capacity():
    """
    Check if Grace has enough storage to continue learning
    Returns warnings if running low
    """
    try:
        from backend.services.storage_tracker import storage_tracker
        
        capacity = await storage_tracker.check_storage_capacity()
        return capacity
    
    except Exception as e:
        logger.error(f"[STORAGE-API] Capacity check failed: {e}")
        return {
            "error": str(e),
            "status": "unknown"
        }


@router.post("/optimize")
async def optimize_storage():
    """
    Optimize storage by cleaning cache, removing duplicates
    Frees up space for continued learning
    """
    try:
        from backend.services.storage_tracker import storage_tracker
        
        result = await storage_tracker.optimize_storage()
        return {
            "success": True,
            "optimization": result
        }
    
    except Exception as e:
        logger.error(f"[STORAGE-API] Storage optimization failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/metrics")
async def get_storage_metrics():
    """Get storage tracking metrics"""
    try:
        from backend.services.storage_tracker import storage_tracker
        
        metrics = await storage_tracker.get_metrics()
        return {
            **metrics,
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "status": "degraded"
        }
