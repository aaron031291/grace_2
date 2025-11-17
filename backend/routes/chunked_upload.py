"""
Chunked File Upload - For Large Files (PDFs, Books, Datasets)
Natural language controlled
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import hashlib
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/files", tags=["chunked_upload"])

# In-memory upload tracking
upload_sessions: Dict[str, dict] = {}

UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class UploadInitRequest(BaseModel):
    filename: str
    total_size_bytes: int
    content_type: str
    chunk_size_mb: int = 5  # Default 5MB chunks

class UploadCompleteRequest(BaseModel):
    upload_id: str
    expected_sha256: Optional[str] = None
    ingest_to_namespace: Optional[str] = "general"
    tags: list[str] = []

@router.post("/init")
async def init_chunked_upload(request: UploadInitRequest):
    """
    Initialize chunked upload
    
    Natural language: "I want to upload a 500MB PDF"
    Grace calls this internally
    """
    import uuid
    
    upload_id = str(uuid.uuid4())
    chunk_size_bytes = request.chunk_size_mb * 1024 * 1024
    total_chunks = (request.total_size_bytes + chunk_size_bytes - 1) // chunk_size_bytes
    
    upload_sessions[upload_id] = {
        "upload_id": upload_id,
        "filename": request.filename,
        "total_size_bytes": request.total_size_bytes,
        "content_type": request.content_type,
        "chunk_size_bytes": chunk_size_bytes,
        "total_chunks": total_chunks,
        "received_chunks": set(),
        "created_at": str(Path(UPLOAD_DIR / upload_id).absolute())
    }
    
    # Create upload directory
    upload_path = UPLOAD_DIR / upload_id
    upload_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"[UPLOAD] Initialized {upload_id} for {request.filename} ({request.total_size_bytes} bytes, {total_chunks} chunks)")
    
    return {
        "upload_id": upload_id,
        "chunk_size_bytes": chunk_size_bytes,
        "total_chunks": total_chunks,
        "upload_url": f"/api/files/chunk?upload_id={upload_id}"
    }

@router.put("/chunk")
async def upload_chunk(upload_id: str, chunk_number: int, chunk: UploadFile = File(...)):
    """
    Upload a single chunk
    
    Grace streams large files in chunks automatically
    """
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    session = upload_sessions[upload_id]
    
    # Save chunk
    upload_path = UPLOAD_DIR / upload_id
    chunk_path = upload_path / f"chunk_{chunk_number}"
    
    content = await chunk.read()
    chunk_path.write_bytes(content)
    
    session["received_chunks"].add(chunk_number)
    
    progress = len(session["received_chunks"]) / session["total_chunks"] * 100
    
    logger.info(f"[UPLOAD] {upload_id} chunk {chunk_number}/{session['total_chunks']} ({progress:.1f}%)")
    
    return {
        "upload_id": upload_id,
        "chunk_number": chunk_number,
        "progress_percent": round(progress, 1),
        "chunks_remaining": session["total_chunks"] - len(session["received_chunks"])
    }

@router.post("/complete")
async def complete_upload(request: UploadCompleteRequest):
    """
    Complete upload and assemble file
    
    Natural language: "Finished uploading, please ingest it"
    Grace calls this and triggers ingestion
    """
    if request.upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    session = upload_sessions[request.upload_id]
    
    # Check all chunks received
    if len(session["received_chunks"]) != session["total_chunks"]:
        raise HTTPException(
            status_code=400,
            detail=f"Missing chunks: {session['total_chunks'] - len(session['received_chunks'])} remaining"
        )
    
    # Assemble file
    upload_path = UPLOAD_DIR / request.upload_id
    final_path = UPLOAD_DIR / session["filename"]
    
    with open(final_path, 'wb') as outfile:
        for i in range(session["total_chunks"]):
            chunk_path = upload_path / f"chunk_{i}"
            outfile.write(chunk_path.read_bytes())
    
    # Verify SHA-256 if provided
    actual_sha256 = hashlib.sha256(final_path.read_bytes()).hexdigest()
    
    if request.expected_sha256 and actual_sha256 != request.expected_sha256:
        final_path.unlink()  # Delete corrupted file
        raise HTTPException(status_code=400, detail="SHA-256 mismatch - file corrupted")
    
    # Cleanup chunks
    for chunk_file in upload_path.glob("chunk_*"):
        chunk_file.unlink()
    upload_path.rmdir()
    
    logger.info(f"[UPLOAD] Completed {request.upload_id}: {session['filename']} ({session['total_size_bytes']} bytes)")
    
    # Trigger ingestion if requested
    artifact_id = None
    if request.ingest_to_namespace:
        from ..enhanced_ingestion import enhanced_ingestion_service
        artifact_id = await enhanced_ingestion_service.ingest_file(
            file_path=str(final_path),
            namespace=request.ingest_to_namespace,
            tags=request.tags
        )
    
    # Cleanup from session tracking
    del upload_sessions[request.upload_id]
    
    return {
        "success": True,
        "filename": session["filename"],
        "size_bytes": session["total_size_bytes"],
        "sha256": actual_sha256,
        "file_path": str(final_path),
        "artifact_id": artifact_id,
        "message": "Upload complete and ingested" if artifact_id else "Upload complete"
    }

@router.get("/uploads/active")
async def list_active_uploads():
    """List active upload sessions"""
    return {
        "active_uploads": len(upload_sessions),
        "sessions": [
            {
                "upload_id": uid,
                "filename": session["filename"],
                "progress": len(session["received_chunks"]) / session["total_chunks"] * 100
            }
            for uid, session in upload_sessions.items()
        ]
    }
