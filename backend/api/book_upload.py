"""
Book Upload API - REAL Implementation

Connects upload → BookIngestionAgent → Memory Fusion
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import shutil
import uuid

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("/upload")
async def upload_book(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    trust_level: str = Form("medium")
) -> Dict[str, Any]:
    """
    Upload and ingest a book (PDF/EPUB/TXT)
    
    This is the REAL implementation that:
    1. Saves the uploaded file
    2. Calls BookIngestionAgent
    3. Triggers full pipeline → Memory Fusion
    """
    
    # Validate file type
    allowed_extensions = ['.pdf', '.epub', '.txt', '.md']
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}"
        )
    
    # Generate job ID
    job_id = str(uuid.uuid4())[:8]
    
    # Save uploaded file
    upload_dir = Path("storage/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = upload_dir / safe_filename
    
    try:
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract metadata
        metadata = {
            "title": title or Path(file.filename).stem,
            "author": author or "Unknown",
            "trust_level": trust_level,
            "original_filename": file.filename,
            "upload_timestamp": datetime.now().isoformat(),
            "job_id": job_id
        }
        
        # Trigger automatic pipeline
        from backend.services.book_pipeline import get_pipeline
        
        pipeline = get_pipeline()
        
        # Process immediately (runs full pipeline automatically)
        import asyncio
        pipeline_result = await pipeline.process_upload(
            file_path=file_path,
            title=metadata["title"],
            author=metadata["author"],
            trust_level=trust_level
        )
        
        # Check if duplicate
        if pipeline_result.get("is_duplicate"):
            return {
                "success": False,
                "status": "duplicate",
                "message": f"Duplicate book detected: '{pipeline_result['duplicate_title']}'",
                "duplicate_id": pipeline_result["duplicate_id"],
                "match_type": "Already in library"
            }
        
        # Update response with pipeline results
        metadata["pipeline_result"] = pipeline_result
        
        return {
            "success": True,
            "status": pipeline_result["status"],
            "job_id": job_id,
            "document_id": pipeline_result["document_id"],
            "title": metadata["title"],
            "author": metadata["author"],
            "file_path": str(file_path),
            "message": "Book uploaded and processed successfully!",
            "pages_extracted": pipeline_result.get("pages", 0),
            "words_extracted": pipeline_result.get("words", 0),
            "chunks_created": pipeline_result.get("chunks_created", 0),
            "embeddings_created": pipeline_result.get("embeddings_created", 0),
            "steps_completed": pipeline_result.get("steps_completed", [])
        }
        
    except Exception as e:
        # Cleanup on failure
        if file_path.exists():
            file_path.unlink()
        
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


async def _process_book_async(agent, file_path: Path, metadata: Dict, job_id: str):
    """Process book asynchronously in background"""
    try:
        result = await agent.process_book(file_path, metadata)
        
        # Update job status (could store in database)
        print(f"✅ Book ingestion complete: {job_id}")
        print(f"   Document ID: {result.get('document_id')}")
        print(f"   Chunks: {result.get('chunks_created')}")
        print(f"   Insights: {result.get('insights_created')}")
        
    except Exception as e:
        print(f"❌ Book ingestion failed: {job_id}")
        print(f"   Error: {e}")


def _estimate_processing_time(file_path: Path) -> float:
    """Estimate processing time based on file size"""
    size_mb = file_path.stat().st_size / (1024 * 1024)
    
    # Rough estimate: 1MB = 2-3 minutes
    # Includes: extraction, chunking, embedding (with rate limits)
    base_time = size_mb * 2.5
    
    # Add overhead for PDF extraction
    if file_path.suffix.lower() == '.pdf':
        base_time *= 1.2
    
    return round(base_time, 1)


@router.get("/jobs/{job_id}")
async def get_upload_status(job_id: str) -> Dict[str, Any]:
    """Get upload/processing status for a job"""
    
    # TODO: Store job status in database and query it
    # For now, check if document exists in memory_tables
    
    from backend.memory_tables.registry import table_registry
    
    try:
        # Search for document with this job_id in metadata
        docs = table_registry.query_rows('memory_documents', limit=1000)
        
        for doc in docs:
            # Check if job_id is in governance_stamp or notes
            if hasattr(doc, 'notes') and doc.notes and job_id in str(doc.notes):
                return {
                    "job_id": job_id,
                    "status": "completed",
                    "document_id": doc.id,
                    "title": doc.title,
                    "created_at": str(doc.last_synced_at) if hasattr(doc, 'last_synced_at') else None
                }
        
        # Not found yet - still processing
        return {
            "job_id": job_id,
            "status": "processing",
            "message": "Book is being processed. Check back in a few minutes."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
