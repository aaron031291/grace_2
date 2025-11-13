"""
Book Dashboard API - Monitoring and metrics for book ingestion
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

from backend.memory_tables.registry import table_registry
from backend.clarity import get_event_bus

router = APIRouter()


@router.get("/stats")
async def get_book_stats() -> Dict[str, Any]:
    """Get overall book ingestion statistics"""

    # Get all documents with source_type = 'book'
    all_books = table_registry.query_rows('memory_documents', filters={'source_type': 'book'})

    # Calculate statistics
    total_books = len(all_books)

    high_trust = sum(1 for book in all_books if getattr(book, 'trust_score', 0) >= 0.9)
    medium_trust = sum(1 for book in all_books if 0.7 <= getattr(book, 'trust_score', 0) < 0.9)
    low_trust = sum(1 for book in all_books if getattr(book, 'trust_score', 0) < 0.7)

    # Recent ingestions (last 7 days) - use last_synced_at
    from datetime import datetime, timedelta
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_books = sum(1 for book in all_books if getattr(book, 'last_synced_at', None) and
                      getattr(book, 'last_synced_at', None) >= seven_days_ago)

    # Total chunks - check if table exists
    try:
        all_chunks = table_registry.query_rows('memory_document_chunks')
        total_chunks = len(all_chunks)
    except:
        total_chunks = 0

    # Total insights
    try:
        all_insights = table_registry.query_rows('memory_insights')
        total_insights = len(all_insights)
    except:
        total_insights = 0

    # Average trust score
    trust_scores = [getattr(book, 'trust_score', 0) for book in all_books if getattr(book, 'trust_score', None) is not None]
    avg_trust_score = sum(trust_scores) / len(trust_scores) if trust_scores else 0.0

    return {
        "total_books": total_books,
        "trust_levels": {
            "high": high_trust,
            "medium": medium_trust,
            "low": low_trust
        },
        "recent_ingestions_7d": recent_books,
        "total_chunks": total_chunks,
        "total_insights": total_insights,
        "average_trust_score": round(avg_trust_score, 3)
    }


@router.get("/recent")
async def get_recent_books(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recently ingested books"""

    db = await get_db()

    books = await db.fetch_all(
        """SELECT id, title, authors, trust_score, last_synced_at, notes
           FROM memory_documents
           WHERE source_type = 'book'
           ORDER BY last_synced_at DESC
           LIMIT ?""",
        (limit,)
    )

    return [
        {
            "document_id": book["id"],
            "title": book["title"],
            "author": book["authors"] if book["authors"] else "Unknown",
            "trust_score": book["trust_score"],
            "created_at": book["last_synced_at"],
            "metadata": {"notes": book["notes"]} if book["notes"] else {}
        }
        for book in books
    ]


@router.get("/flagged")
async def get_flagged_books() -> List[Dict[str, Any]]:
    """Get books flagged for manual review (trust score < 0.7)"""

    db = await get_db()

    flagged = await db.fetch_all(
        """SELECT id, title, authors, trust_score, risk_level
           FROM memory_documents
           WHERE source_type = 'book' AND trust_score < 0.7
           ORDER BY trust_score ASC"""
    )

    return [
        {
            "document_id": book["id"],
            "title": book["title"],
            "author": book["authors"] if book["authors"] else "Unknown",
            "trust_score": book["trust_score"],
            "verification_results": {"risk_level": book["risk_level"]} if book["risk_level"] else {}
        }
        for book in flagged
    ]


@router.get("/{document_id}")
async def get_book_details(document_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific book"""

    db = await get_db()

    # Get document
    book = await db.fetch_one(
        "SELECT * FROM memory_documents WHERE id = ?",
        (document_id,)
    )

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Get chunks - check if table exists
    try:
        chunks = await db.fetch_all(
            "SELECT chunk_index, content FROM memory_document_chunks WHERE document_id = ? ORDER BY chunk_index",
            (document_id,)
        )
    except:
        chunks = []

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
        "document_id": book["id"],
        "title": book["title"],
        "author": book["authors"] if book["authors"] else "Unknown",
        "source_type": book["source_type"],
        "file_path": book["file_path"],
        "trust_score": book["trust_score"],
        "created_at": book["last_synced_at"],
        "updated_at": book["last_synced_at"],
        "metadata": {"summary": book["summary"], "notes": book["notes"]} if book["summary"] or book["notes"] else {},
        "verification_results": {"risk_level": book["risk_level"]} if book["risk_level"] else {},
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


@router.get("/search")
async def search_books(q: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search books by title, author, or content"""

    db = await get_db()

    search_term = f"%{q}%"

    books = await db.fetch_all(
        """SELECT id, title, authors, trust_score, summary, notes
           FROM memory_documents
           WHERE source_type = 'book'
           AND (title LIKE ? OR authors LIKE ? OR summary LIKE ? OR notes LIKE ?)
           ORDER BY trust_score DESC
           LIMIT ?""",
        (search_term, search_term, search_term, search_term, limit)
    )

    return [
        {
            "document_id": book["id"],
            "title": book["title"],
            "author": book["authors"] if book["authors"] else "Unknown",
            "trust_score": book["trust_score"],
            "metadata": {"summary": book["summary"], "notes": book["notes"]} if book["summary"] or book["notes"] else {}
        }
        for book in books
    ]


@router.get("/activity")
async def get_recent_activity(limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent book-related activity from execution logs"""

    db = await get_db()

    # Use execution logs instead of librarian_log
    activity = await db.fetch_all(
        """SELECT agent_type, task_type, status, executed_at, result
           FROM memory_execution_logs
           WHERE agent_type LIKE '%book%' OR task_type LIKE '%book%'
           ORDER BY executed_at DESC
           LIMIT ?""",
        (limit,)
    )

    return [
        {
            "action": a["task_type"],
            "target": f"{a['agent_type']}:{a['status']}",
            "details": json.loads(a["result"]) if a["result"] else {},
            "timestamp": a["executed_at"]
        }
        for a in activity
    ]


@router.get("/metrics/daily")
async def get_daily_metrics(days: int = 30) -> List[Dict[str, Any]]:
    """Get daily ingestion metrics"""

    db = await get_db()

    metrics = await db.fetch_all(
        """SELECT
               DATE(last_synced_at) as date,
               COUNT(*) as books_added,
               AVG(trust_score) as avg_trust
           FROM memory_documents
           WHERE source_type = 'book' AND last_synced_at >= datetime('now', ? || ' days')
           GROUP BY DATE(last_synced_at)
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


@router.post("/{document_id}/reverify")
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


@router.delete("/{document_id}")
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

    # Check if chunks table exists before deleting
    try:
        await db.execute(
            "DELETE FROM memory_document_chunks WHERE document_id = ?",
            (document_id,)
        )
    except:
        pass  # Table might not exist

    await db.execute(
        "DELETE FROM memory_documents WHERE id = ?",
        (document_id,)
    )

    await db.commit()

    return {
        "status": "deleted",
        "document_id": document_id,
        "message": "Book and all associated data deleted"
    }
