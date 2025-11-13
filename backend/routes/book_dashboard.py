"""
Book Dashboard API - Monitoring and metrics for book ingestion
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

from backend.database import get_db
from backend.clarity import get_event_bus

router = APIRouter()


@router.get("/books/stats")
async def get_book_stats() -> Dict[str, Any]:
    """Get overall book ingestion statistics"""
    
    db = await get_db()
    
    # Total books
    total_books = await db.fetch_one(
        "SELECT COUNT(*) as count FROM memory_documents WHERE source_type = 'book'"
    )
    
    # Books by trust level
    high_trust = await db.fetch_one(
        "SELECT COUNT(*) as count FROM memory_documents WHERE source_type = 'book' AND trust_score >= 0.9"
    )
    medium_trust = await db.fetch_one(
        "SELECT COUNT(*) as count FROM memory_documents WHERE source_type = 'book' AND trust_score >= 0.7 AND trust_score < 0.9"
    )
    low_trust = await db.fetch_one(
        "SELECT COUNT(*) as count FROM memory_documents WHERE source_type = 'book' AND trust_score < 0.7"
    )
    
    # Recent ingestions (last 7 days)
    recent_books = await db.fetch_one(
        "SELECT COUNT(*) as count FROM memory_documents WHERE source_type = 'book' AND created_at >= datetime('now', '-7 days')"
    )
    
    # Total chunks
    total_chunks = await db.fetch_one(
        "SELECT COUNT(*) as count FROM memory_document_chunks"
    )
    
    # Total insights
    total_insights = await db.fetch_one(
        "SELECT COUNT(*) as count FROM memory_insights"
    )
    
    # Average trust score
    avg_trust = await db.fetch_one(
        "SELECT AVG(trust_score) as avg FROM memory_documents WHERE source_type = 'book'"
    )
    
    return {
        "total_books": total_books["count"] if total_books else 0,
        "trust_levels": {
            "high": high_trust["count"] if high_trust else 0,
            "medium": medium_trust["count"] if medium_trust else 0,
            "low": low_trust["count"] if low_trust else 0
        },
        "recent_ingestions_7d": recent_books["count"] if recent_books else 0,
        "total_chunks": total_chunks["count"] if total_chunks else 0,
        "total_insights": total_insights["count"] if total_insights else 0,
        "average_trust_score": round(avg_trust["avg"], 3) if avg_trust and avg_trust["avg"] else 0.0
    }


@router.get("/books/recent")
async def get_recent_books(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recently ingested books"""
    
    db = await get_db()
    
    books = await db.fetch_all(
        """SELECT document_id, title, author, trust_score, created_at, metadata
           FROM memory_documents
           WHERE source_type = 'book'
           ORDER BY created_at DESC
           LIMIT ?""",
        (limit,)
    )
    
    return [
        {
            "document_id": book["document_id"],
            "title": book["title"],
            "author": book["author"],
            "trust_score": book["trust_score"],
            "created_at": book["created_at"],
            "metadata": json.loads(book["metadata"]) if book["metadata"] else {}
        }
        for book in books
    ]


@router.get("/books/flagged")
async def get_flagged_books() -> List[Dict[str, Any]]:
    """Get books flagged for manual review (trust score < 0.7)"""
    
    db = await get_db()
    
    flagged = await db.fetch_all(
        """SELECT document_id, title, author, trust_score, verification_results
           FROM memory_documents
           WHERE source_type = 'book' AND trust_score < 0.7
           ORDER BY trust_score ASC"""
    )
    
    return [
        {
            "document_id": book["document_id"],
            "title": book["title"],
            "author": book["author"],
            "trust_score": book["trust_score"],
            "verification_results": json.loads(book["verification_results"]) if book["verification_results"] else {}
        }
        for book in flagged
    ]


@router.get("/books/{document_id}")
async def get_book_details(document_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific book"""
    
    db = await get_db()
    
    # Get document
    book = await db.fetch_one(
        "SELECT * FROM memory_documents WHERE document_id = ?",
        (document_id,)
    )
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Get chunks
    chunks = await db.fetch_all(
        "SELECT chunk_index, content FROM memory_document_chunks WHERE document_id = ? ORDER BY chunk_index",
        (document_id,)
    )
    
    # Get insights
    insights = await db.fetch_all(
        "SELECT insight_type, content, confidence FROM memory_insights WHERE document_id = ?",
        (document_id,)
    )
    
    # Get verification results
    verifications = await db.fetch_all(
        "SELECT verification_type, results, trust_score, timestamp FROM memory_verification_suites WHERE document_id = ? ORDER BY timestamp DESC",
        (document_id,)
    )
    
    return {
        "document_id": book["document_id"],
        "title": book["title"],
        "author": book["author"],
        "source_type": book["source_type"],
        "file_path": book["file_path"],
        "trust_score": book["trust_score"],
        "created_at": book["created_at"],
        "updated_at": book["updated_at"],
        "metadata": json.loads(book["metadata"]) if book["metadata"] else {},
        "verification_results": json.loads(book["verification_results"]) if book["verification_results"] else {},
        "chunks": {
            "total": len(chunks),
            "sample": [
                {"index": c["chunk_index"], "content": c["content"][:200] + "..."}
                for c in chunks[:3]
            ]
        },
        "insights": [
            {
                "type": i["insight_type"],
                "content": i["content"],
                "confidence": i["confidence"]
            }
            for i in insights
        ],
        "verification_history": [
            {
                "type": v["verification_type"],
                "trust_score": v["trust_score"],
                "timestamp": v["timestamp"],
                "results": json.loads(v["results"]) if v["results"] else {}
            }
            for v in verifications
        ]
    }


@router.get("/books/search")
async def search_books(q: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search books by title, author, or content"""
    
    db = await get_db()
    
    search_term = f"%{q}%"
    
    books = await db.fetch_all(
        """SELECT document_id, title, author, trust_score, metadata
           FROM memory_documents
           WHERE source_type = 'book' 
           AND (title LIKE ? OR author LIKE ? OR metadata LIKE ?)
           ORDER BY trust_score DESC
           LIMIT ?""",
        (search_term, search_term, search_term, limit)
    )
    
    return [
        {
            "document_id": book["document_id"],
            "title": book["title"],
            "author": book["author"],
            "trust_score": book["trust_score"],
            "metadata": json.loads(book["metadata"]) if book["metadata"] else {}
        }
        for book in books
    ]


@router.get("/books/activity")
async def get_recent_activity(limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent book-related activity from Librarian logs"""
    
    db = await get_db()
    
    activity = await db.fetch_all(
        """SELECT action_type, target_path, details, timestamp
           FROM memory_librarian_log
           WHERE action_type IN ('schema_proposal', 'ingestion_launch', 'trust_update', 'automation_rule_executed')
           ORDER BY timestamp DESC
           LIMIT ?""",
        (limit,)
    )
    
    return [
        {
            "action": a["action_type"],
            "target": a["target_path"],
            "details": json.loads(a["details"]) if a["details"] else {},
            "timestamp": a["timestamp"]
        }
        for a in activity
    ]


@router.get("/books/metrics/daily")
async def get_daily_metrics(days: int = 30) -> List[Dict[str, Any]]:
    """Get daily ingestion metrics"""
    
    db = await get_db()
    
    metrics = await db.fetch_all(
        """SELECT 
               DATE(created_at) as date,
               COUNT(*) as books_added,
               AVG(trust_score) as avg_trust
           FROM memory_documents
           WHERE source_type = 'book' AND created_at >= datetime('now', ? || ' days')
           GROUP BY DATE(created_at)
           ORDER BY date DESC""",
        (f"-{days}",)
    )
    
    return [
        {
            "date": m["date"],
            "books_added": m["books_added"],
            "avg_trust_score": round(m["avg_trust"], 3) if m["avg_trust"] else 0.0
        }
        for m in metrics
    ]


@router.post("/books/{document_id}/reverify")
async def reverify_book(document_id: str) -> Dict[str, Any]:
    """Trigger re-verification for a book"""
    
    event_bus = get_event_bus()
    
    from backend.clarity import Event
    
    await event_bus.publish(Event(
        event_type="verification.book.requested",
        source="book_dashboard",
        payload={
            "document_id": document_id,
            "verification_type": "book_comprehensive",
            "triggered_by": "manual_dashboard"
        }
    ))
    
    return {
        "status": "queued",
        "document_id": document_id,
        "message": "Verification queued successfully"
    }


@router.delete("/books/{document_id}")
async def delete_book(document_id: str) -> Dict[str, Any]:
    """Delete a book and all associated data"""
    
    db = await get_db()
    
    # Delete in order: verifications, insights, chunks, document
    await db.execute(
        "DELETE FROM memory_verification_suites WHERE document_id = ?",
        (document_id,)
    )
    
    await db.execute(
        "DELETE FROM memory_insights WHERE document_id = ?",
        (document_id,)
    )
    
    await db.execute(
        "DELETE FROM memory_document_chunks WHERE document_id = ?",
        (document_id,)
    )
    
    await db.execute(
        "DELETE FROM memory_documents WHERE document_id = ?",
        (document_id,)
    )
    
    await db.commit()
    
    return {
        "status": "deleted",
        "document_id": document_id,
        "message": "Book and all associated data deleted"
    }
