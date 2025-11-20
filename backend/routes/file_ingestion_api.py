"""
File Ingestion API - Monitoring and metrics for all file types
Mirrors book_dashboard.py pattern for unified ingestion tracking
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from backend.memory_tables.registry import table_registry
from backend.clarity import get_event_bus, Event
from backend.kernels.agents.file_ingestion_agent import FileIngestionAgent

router = APIRouter()

# Initialize agent (singleton pattern)
_file_agent = None

def get_file_agent() -> FileIngestionAgent:
    global _file_agent
    if _file_agent is None:
        _file_agent = FileIngestionAgent()
    return _file_agent


@router.get("/stats")
async def get_ingestion_stats() -> Dict[str, Any]:
    """Get overall file ingestion statistics across all modalities"""
    
    # Get all documents
    all_docs = table_registry.query_rows('memory_documents', limit=10000)
    
    # Group by source_type (modality)
    modality_counts = {}
    for doc in all_docs:
        source_type = getattr(doc, 'source_type', 'unknown')
        modality_counts[source_type] = modality_counts.get(source_type, 0) + 1
    
    # Calculate statistics
    total_files = len(all_docs)
    
    # Trust score distribution
    high_trust = sum(1 for doc in all_docs if getattr(doc, 'trust_score', 0) >= 0.9)
    medium_trust = sum(1 for doc in all_docs if 0.7 <= getattr(doc, 'trust_score', 0) < 0.9)
    low_trust = sum(1 for doc in all_docs if getattr(doc, 'trust_score', 0) < 0.7)
    
    # Recent ingestions (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_files = sum(1 for doc in all_docs if getattr(doc, 'last_synced_at', None) and
                      getattr(doc, 'last_synced_at', None) >= seven_days_ago)
    
    # Total chunks
    try:
        all_chunks = table_registry.query_rows('memory_document_chunks')
        total_chunks = len(all_chunks)
    except:
        total_chunks = 0
    
    # Average trust score
    trust_scores = [getattr(doc, 'trust_score', 0) for doc in all_docs if getattr(doc, 'trust_score', None) is not None]
    avg_trust_score = sum(trust_scores) / len(trust_scores) if trust_scores else 0.0
    
    return {
        "total_files": total_files,
        "by_modality": modality_counts,
        "trust_levels": {
            "high": high_trust,
            "medium": medium_trust,
            "low": low_trust
        },
        "recent_ingestions_7d": recent_files,
        "total_chunks": total_chunks,
        "average_trust_score": round(avg_trust_score, 3)
    }


@router.get("/stats/{modality}")
async def get_modality_stats(modality: str) -> Dict[str, Any]:
    """Get statistics for a specific modality"""
    
    # Get documents for this modality
    docs = table_registry.query_rows('memory_documents', filters={'source_type': modality})
    
    if not docs:
        return {
            "modality": modality,
            "total_files": 0,
            "avg_trust_score": 0.0,
            "recent_7d": 0
        }
    
    # Calculate stats
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent = sum(1 for doc in docs if getattr(doc, 'last_synced_at', None) and
                getattr(doc, 'last_synced_at', None) >= seven_days_ago)
    
    trust_scores = [getattr(doc, 'trust_score', 0) for doc in docs if getattr(doc, 'trust_score', None) is not None]
    avg_trust = sum(trust_scores) / len(trust_scores) if trust_scores else 0.0
    
    return {
        "modality": modality,
        "total_files": len(docs),
        "avg_trust_score": round(avg_trust, 3),
        "recent_7d": recent,
        "trust_distribution": {
            "high": sum(1 for doc in docs if getattr(doc, 'trust_score', 0) >= 0.9),
            "medium": sum(1 for doc in docs if 0.7 <= getattr(doc, 'trust_score', 0) < 0.9),
            "low": sum(1 for doc in docs if getattr(doc, 'trust_score', 0) < 0.7)
        }
    }


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    modality: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    folder: Optional[str] = Form("upload")
) -> Dict[str, Any]:
    """
    Upload and ingest a file
    
    Args:
        file: The file to upload
        modality: Optional modality override (api, web, audio, video, code, xxl)
        title: Optional title for the file
        description: Optional description
        folder: Destination folder (e.g., 'learning', 'upload', 'api', 'web')
    
    Special behavior:
        - Files uploaded to 'learning/*' folders automatically trigger full ML/DL pipeline
        - These files are tagged as standard training corpus
    """
    
    # Determine upload directory based on folder parameter
    is_learning = folder.startswith('learning')
    
    if is_learning:
        upload_dir = Path("storage/memory/learning")
        auto_ingest = True
    else:
        upload_dir = Path("storage/memory/raw") / folder
        auto_ingest = True  # Always auto-ingest through new pipeline
    
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / file.filename
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Prepare metadata
    metadata = {
        "original_filename": file.filename,
        "content_type": file.content_type,
        "uploaded_at": datetime.utcnow().isoformat(),
        "destination_folder": folder
    }
    
    # Add learning-specific metadata
    if is_learning:
        metadata.update({
            "is_standard_training": True,
            "source_folder": "learning",
            "auto_ml_pipeline": True
        })
    
    if title:
        metadata["title"] = title
    if description:
        metadata["description"] = description
    
    # Process file through ingestion agent
    agent = get_file_agent()
    result = await agent.process_file(file_path, metadata, modality)
    
    # Publish special event for learning folder
    if is_learning:
        event_bus = get_event_bus()
        await event_bus.publish(Event(
            event_type="learning.corpus.file_added",
            source="file_ingestion_api",
            payload={
                "document_id": result.get("document_id"),
                "modality": result.get("modality"),
                "file_path": str(file_path),
                "auto_ml_enabled": True
            }
        ))
    
    return {
        "status": "success",
        "document_id": result.get("document_id"),
        "modality": result.get("modality"),
        "storage_path": result.get("storage_path"),
        "auto_ingested": auto_ingest,
        "is_learning_corpus": is_learning,
        "message": f"File '{file.filename}' {'added to learning corpus and' if is_learning else ''} ingested successfully",
        "processing_result": result
    }


@router.get("/recent")
async def get_recent_files(limit: int = 20, modality: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get recently ingested files, optionally filtered by modality"""
    
    filters = {'source_type': modality} if modality else {}
    docs = table_registry.query_rows('memory_documents', filters=filters, limit=10000)
    
    # Sort by last_synced_at descending and limit
    sorted_docs = sorted(
        docs,
        key=lambda x: getattr(x, 'last_synced_at', datetime.min),
        reverse=True
    )[:limit]
    
    return [
        {
            "document_id": getattr(doc, 'id', None),
            "title": getattr(doc, 'title', 'Unknown'),
            "modality": getattr(doc, 'source_type', 'unknown'),
            "trust_score": getattr(doc, 'trust_score', 0.0),
            "ingested_at": getattr(doc, 'last_synced_at', None),
            "file_path": getattr(doc, 'file_path', ''),
            "metadata": json.loads(getattr(doc, 'metadata', '{}')) if getattr(doc, 'metadata', None) else {}
        }
        for doc in sorted_docs
    ]


@router.get("/flagged")
async def get_flagged_files() -> List[Dict[str, Any]]:
    """Get files flagged for manual review (trust score < 0.7)"""
    
    all_docs = table_registry.query_rows('memory_documents', limit=10000)
    
    # Filter low trust files
    flagged = [doc for doc in all_docs if getattr(doc, 'trust_score', 0) < 0.7]
    
    # Sort by trust_score ascending
    flagged_sorted = sorted(flagged, key=lambda x: getattr(doc, 'trust_score', 0))
    
    return [
        {
            "document_id": getattr(doc, 'id', None),
            "title": getattr(doc, 'title', 'Unknown'),
            "modality": getattr(doc, 'source_type', 'unknown'),
            "trust_score": getattr(doc, 'trust_score', 0.0),
            "file_path": getattr(doc, 'file_path', '')
        }
        for doc in flagged_sorted
    ]


@router.get("/{document_id}")
async def get_file_details(document_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific file"""
    
    docs = table_registry.query_rows('memory_documents', filters={'id': document_id})
    
    if not docs:
        raise HTTPException(status_code=404, detail="File not found")
    
    doc = docs[0]
    
    # Get chunks
    try:
        chunks = table_registry.query_rows('memory_document_chunks', filters={'document_id': document_id})
    except:
        chunks = []
    
    # Get insights
    try:
        insights = table_registry.query_rows('memory_insights', filters={'document_id': document_id})
    except:
        insights = []
    
    return {
        "document_id": getattr(doc, 'id', None),
        "title": getattr(doc, 'title', 'Unknown'),
        "modality": getattr(doc, 'source_type', 'unknown'),
        "file_path": getattr(doc, 'file_path', ''),
        "trust_score": getattr(doc, 'trust_score', 0.0),
        "ingested_at": getattr(doc, 'last_synced_at', None),
        "updated_at": getattr(doc, 'last_synced_at', None),
        "metadata": json.loads(getattr(doc, 'metadata', '{}')) if getattr(doc, 'metadata', None) else {},
        "chunks": {
            "total": len(chunks),
            "sample": [
                {"index": getattr(c, 'chunk_index', 0), "content": (getattr(c, 'content', '')[:200] + "...")}
                for c in chunks[:3]
            ]
        },
        "insights": [
            {
                "type": getattr(i, 'insight_type', 'unknown'),
                "content": getattr(i, 'content', ''),
                "confidence": getattr(i, 'confidence', 0.0)
            }
            for i in insights
        ]
    }


@router.get("/activity")
async def get_recent_activity(limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent file ingestion activity from execution logs"""
    
    activity = table_registry.query_rows('memory_execution_logs', limit=1000)
    
    # Filter for file-related activity
    file_activity = [
        log for log in activity
        if ('file' in getattr(log, 'agent_type', '').lower() or
            'ingest' in getattr(log, 'task_type', '').lower())
    ]
    
    # Sort by executed_at descending and limit
    sorted_activity = sorted(
        file_activity,
        key=lambda x: getattr(x, 'executed_at', datetime.min),
        reverse=True
    )[:limit]
    
    return [
        {
            "action": getattr(log, 'task_type', 'unknown'),
            "modality": getattr(log, 'agent_type', 'unknown'),
            "status": getattr(log, 'status', 'unknown'),
            "details": getattr(log, 'result', {}) if getattr(log, 'result', None) else {},
            "timestamp": getattr(log, 'executed_at', None)
        }
        for log in sorted_activity
    ]


@router.post("/{document_id}/reverify")
async def reverify_file(document_id: str) -> Dict[str, Any]:
    """Trigger re-verification for a file"""
    
    event_bus = get_event_bus()
    
    await event_bus.publish(Event(
        event_type="verification.document.requested",
        source="file_ingestion_api",
        payload={
            "document_id": document_id,
            "verification_type": "comprehensive",
            "triggered_by": "manual_dashboard"
        }
    ))
    
    return {
        "status": "queued",
        "document_id": document_id,
        "message": "Verification queued successfully"
    }


@router.delete("/{document_id}")
async def delete_file(document_id: str) -> Dict[str, Any]:
    """Delete a file and all associated data"""
    
    # Delete chunks
    try:
        chunks = table_registry.query_rows('memory_document_chunks', filters={'document_id': document_id})
        for c in chunks:
            table_registry.update_row('memory_document_chunks', getattr(c, 'id', None), {'deleted': True})
    except:
        pass
    
    # Delete insights
    try:
        insights = table_registry.query_rows('memory_insights', filters={'document_id': document_id})
        for i in insights:
            table_registry.update_row('memory_insights', getattr(i, 'id', None), {'deleted': True})
    except:
        pass
    
    # Mark document as deleted (soft delete)
    table_registry.update_row('memory_documents', document_id, {'deleted': True})
    
    return {
        "status": "deleted",
        "document_id": document_id,
        "message": "File and all associated data deleted"
    }


# Helper to import json properly
import json
