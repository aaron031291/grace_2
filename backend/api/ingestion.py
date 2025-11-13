"""
Ingestion API
Book and document ingestion pipeline
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


class IngestionRequest(BaseModel):
    file_path: str
    document_type: str
    options: Optional[Dict[str, Any]] = None


@router.get("/status")
async def get_ingestion_status() -> Dict[str, Any]:
    """Get ingestion pipeline status"""
    return {
        "status": "active",
        "queue_size": 3,
        "active_jobs": 2,
        "completed_today": 12,
        "failed_today": 1,
        "average_time_seconds": 145,
        "stats": {
            "total_books_ingested": 23,
            "total_chunks_processed": 12847,
            "total_embeddings_created": 12847
        }
    }


@router.get("/jobs")
async def list_ingestion_jobs(
    status: Optional[str] = None,
    limit: int = Query(20, le=100)
) -> Dict[str, Any]:
    """List ingestion jobs"""
    jobs = []
    
    statuses = ["pending", "processing", "completed", "failed"] if not status else [status]
    
    for i in range(min(limit, 10)):
        job_status = random.choice(statuses)
        jobs.append({
            "id": i + 1,
            "file_name": f"book_{i}.pdf",
            "document_type": random.choice(["pdf", "epub", "txt", "md"]),
            "status": job_status,
            "progress": 1.0 if job_status == "completed" else random.uniform(0.1, 0.9),
            "chunks_processed": random.randint(0, 500) if job_status != "pending" else 0,
            "started_at": (datetime.now() - timedelta(minutes=i * 15)).isoformat() if job_status != "pending" else None,
            "completed_at": (datetime.now() - timedelta(minutes=i * 10)).isoformat() if job_status == "completed" else None
        })
    
    return {
        "jobs": jobs,
        "count": len(jobs),
        "total": 150
    }


@router.get("/jobs/{job_id}")
async def get_job_details(job_id: int) -> Dict[str, Any]:
    """Get detailed information about an ingestion job"""
    return {
        "id": job_id,
        "file_name": "lean_startup.pdf",
        "document_type": "pdf",
        "status": "completed",
        "progress": 1.0,
        "stats": {
            "total_pages": 200,
            "total_chunks": 450,
            "embeddings_created": 450,
            "duration_seconds": 135
        },
        "started_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        "completed_at": (datetime.now() - timedelta(hours=1, minutes=45)).isoformat(),
        "metadata": {
            "title": "The Lean Startup",
            "author": "Eric Ries",
            "language": "en"
        }
    }


@router.post("/jobs")
async def create_ingestion_job(request: IngestionRequest):
    """Create a new ingestion job"""
    job_id = random.randint(100, 999)
    
    return {
        "success": True,
        "message": f"Ingestion job created for {request.file_path}",
        "job_id": job_id,
        "estimated_time_seconds": 120
    }


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: int):
    """Cancel an ingestion job"""
    return {
        "success": True,
        "message": f"Job {job_id} cancelled"
    }


@router.post("/jobs/{job_id}/retry")
async def retry_job(job_id: int):
    """Retry a failed ingestion job"""
    new_job_id = random.randint(100, 999)
    
    return {
        "success": True,
        "message": f"Job {job_id} retry initiated",
        "new_job_id": new_job_id
    }


@router.get("/metrics")
async def get_ingestion_metrics() -> Dict[str, Any]:
    """Get ingestion pipeline metrics"""
    return {
        "total_ingested": 23,
        "chunks_processed": 12847,
        "average_chunk_time_ms": 125,
        "success_rate": 0.98,
        "daily_stats": [
            {
                "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "ingested": random.randint(1, 5),
                "failed": random.randint(0, 1)
            }
            for i in range(7)
        ]
    }


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for ingestion"""
    return {
        "success": True,
        "message": f"File {file.filename} uploaded successfully",
        "job_id": random.randint(100, 999),
        "file_size": 1024 * 512  # Mock size
    }
