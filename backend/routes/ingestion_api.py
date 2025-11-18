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

@router.post("/ingest")
async def ingest_data(data: dict):
    """Ingest data into the system"""
    try:
        # Basic ingestion logic
        return {"status": "ingested", "data_id": "temp_id"}
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


