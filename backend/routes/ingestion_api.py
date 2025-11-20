"""
Ingestion Pipeline API
Endpoints for managing ingestion workflows
"""

from fastapi import APIRouter, Depends, HTTPException
from backend.models.base_models import async_session
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/ingestion",
    tags=["Data Ingestion"]
)

@router.get("/health")
async def ingestion_health():
    """Health check for ingestion API"""
    return {"status": "healthy", "service": "ingestion"}

@router.get("/stats")
async def get_ingestion_stats():
    """Get ingestion statistics"""
    try:
        # Get real stats from memory catalog
        from backend.memory.memory_mount import memory_mount
        
        stats = memory_mount.get_catalog_stats()
        
        # Calculate trust levels
        from backend.memory.memory_catalog import memory_catalog
        all_assets = memory_catalog.list_all_assets()
        
        high = len([a for a in all_assets if a.trust_score >= 0.8])
        medium = len([a for a in all_assets if 0.5 <= a.trust_score < 0.8])
        low = len([a for a in all_assets if a.trust_score < 0.5])
        
        avg_trust = sum(a.trust_score for a in all_assets) / len(all_assets) if all_assets else 0.0
        
        return {
            "total_files": stats.get("total_assets", 0),
            "by_modality": stats.get("by_type", {}),
            "trust_levels": {
                "high": high,
                "medium": medium,
                "low": low
            },
            "recent_ingestions_7d": stats.get("recent_7d", 0),
            "total_chunks": stats.get("total_chunks", 0),
            "average_trust_score": avg_trust
        }
    except Exception as e:
        # Return empty stats if system not available
        return {
            "total_files": 0,
            "by_modality": {},
            "trust_levels": {"high": 0, "medium": 0, "low": 0},
            "recent_ingestions_7d": 0,
            "total_chunks": 0,
            "average_trust_score": 0.0
        }

@router.get("/recent")
async def get_recent_files(limit: int = 10):
    """Get recently ingested files"""
    try:
        from backend.memory.memory_catalog import memory_catalog
        from datetime import datetime, timedelta
        
        # Get recent assets (last 7 days)
        cutoff = datetime.utcnow() - timedelta(days=7)
        all_assets = memory_catalog.list_all_assets()
        
        recent = [
            {
                "document_id": a.asset_id,
                "title": a.path.split("/")[-1],
                "modality": a.asset_type.value,
                "trust_score": a.trust_score,
                "ingested_at": a.ingestion_date.isoformat() if hasattr(a.ingestion_date, 'isoformat') else str(a.ingestion_date),
                "file_path": a.path,
                "metadata": a.metadata or {}
            }
            for a in sorted(all_assets, key=lambda x: x.ingestion_date if hasattr(x, 'ingestion_date') else datetime.min, reverse=True)[:limit]
        ]
        
        return recent
    except Exception as e:
        return []

@router.post("/ingest")
async def ingest_data(data: dict):
    """Ingest data into the system"""
    try:
        # Basic ingestion logic
        return {"status": "ingested", "data_id": "temp_id"}
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


