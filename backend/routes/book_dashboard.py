"""
Book Dashboard API - Monitoring and metrics for book ingestion
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime

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

    # Get books sorted by last_synced_at descending
    books = table_registry.query_rows('memory_documents', filters={'source_type': 'book'}, limit=1000)

    # Sort by last_synced_at in descending order and limit
    sorted_books = sorted(
        books,
        key=lambda x: getattr(x, 'last_synced_at', datetime.min),
        reverse=True
    )[:limit]

    return [
        {
            "document_id": getattr(book, 'id', None),
            "title": getattr(book, 'title', 'Unknown'),
            "author": getattr(book, 'authors', 'Unknown') or "Unknown",
            "trust_score": getattr(book, 'trust_score', 0.0),
            "created_at": getattr(book, 'last_synced_at', None),
            "metadata": {"notes": getattr(book, 'notes', None)} if getattr(book, 'notes', None) else {}
        }
        for book in sorted_books
    ]


@router.get("/flagged")
async def get_flagged_books() -> List[Dict[str, Any]]:
    """Get books flagged for manual review (trust score < 0.7)"""

    # Get all books
    all_books = table_registry.query_rows('memory_documents', filters={'source_type': 'book'})

    # Filter books with trust_score < 0.7
    flagged = [book for book in all_books if getattr(book, 'trust_score', 0) < 0.7]

    # Sort by trust_score ascending
    flagged_sorted = sorted(flagged, key=lambda x: getattr(x, 'trust_score', 0))

    return [
        {
            "document_id": getattr(book, 'id', None),
            "title": getattr(book, 'title', 'Unknown'),
            "author": getattr(book, 'authors', 'Unknown') or "Unknown",
            "trust_score": getattr(book, 'trust_score', 0.0),
            "verification_results": {"risk_level": getattr(book, 'risk_level', None)} if getattr(book, 'risk_level', None) else {}
        }
        for book in flagged_sorted
    ]


@router.get("/{document_id}")
async def get_book_details(document_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific book"""

    # Get the specific book
    books = table_registry.query_rows('memory_documents', filters={'id': document_id})

    if not books:
        raise HTTPException(status_code=404, detail="Book not found")

    book = books[0]

    # Get chunks - check if table exists
    try:
        chunks = table_registry.query_rows('memory_document_chunks', filters={'document_id': document_id})
    except:
        chunks = []

    # Get insights
    try:
        insights = table_registry.query_rows('memory_insights', filters={'document_id': document_id})
    except:
        insights = []

    # Get verification results
    try:
        verifications = table_registry.query_rows('memory_verification_suites', filters={'document_id': document_id})
        # Sort by timestamp descending
        verifications_sorted = sorted(verifications, key=lambda x: getattr(x, 'timestamp', datetime.min), reverse=True)
    except:
        verifications_sorted = []

    return {
        "document_id": getattr(book, 'id', None),
        "title": getattr(book, 'title', 'Unknown'),
        "author": getattr(book, 'authors', 'Unknown') or "Unknown",
        "source_type": getattr(book, 'source_type', 'unknown'),
        "file_path": getattr(book, 'file_path', ''),
        "trust_score": getattr(book, 'trust_score', 0.0),
        "created_at": getattr(book, 'last_synced_at', None),
        "updated_at": getattr(book, 'last_synced_at', None),
        "metadata": {
            "summary": getattr(book, 'summary', None),
            "notes": getattr(book, 'notes', None)
        } if getattr(book, 'summary', None) or getattr(book, 'notes', None) else {},
        "verification_results": {"risk_level": getattr(book, 'risk_level', None)} if getattr(book, 'risk_level', None) else {},
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
        ],
        "verification_history": [
            {
                "type": getattr(v, 'verification_type', 'unknown'),
                "trust_score": getattr(v, 'trust_score', 0.0),
                "timestamp": getattr(v, 'timestamp', None),
                "results": getattr(v, 'results', {}) if getattr(v, 'results', None) else {}
            }
            for v in verifications_sorted
        ]
    }


@router.get("/search")
async def search_books(q: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search books by title, author, or content"""

    # Get all books
    all_books = table_registry.query_rows('memory_documents', filters={'source_type': 'book'})

    # Filter books that match search term
    search_term_lower = q.lower()
    matching_books = []
    for book in all_books:
        title = getattr(book, 'title', '').lower()
        authors = getattr(book, 'authors', '').lower()
        summary = getattr(book, 'summary', '').lower()
        notes = getattr(book, 'notes', '').lower()

        if (search_term_lower in title or
            search_term_lower in authors or
            search_term_lower in summary or
            search_term_lower in notes):
            matching_books.append(book)

    # Sort by trust_score descending and limit
    sorted_books = sorted(
        matching_books,
        key=lambda x: getattr(x, 'trust_score', 0),
        reverse=True
    )[:limit]

    return [
        {
            "document_id": getattr(book, 'id', None),
            "title": getattr(book, 'title', 'Unknown'),
            "author": getattr(book, 'authors', 'Unknown') or "Unknown",
            "trust_score": getattr(book, 'trust_score', 0.0),
            "metadata": {
                "summary": getattr(book, 'summary', None),
                "notes": getattr(book, 'notes', None)
            } if getattr(book, 'summary', None) or getattr(book, 'notes', None) else {}
        }
        for book in sorted_books
    ]


@router.get("/activity")
async def get_recent_activity(limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent book-related activity from execution logs"""

    # Get execution logs related to books
    activity = table_registry.query_rows('memory_execution_logs', limit=1000)

    # Filter for book-related activity
    book_activity = [
        log for log in activity
        if ('book' in getattr(log, 'agent_type', '').lower() or
            'book' in getattr(log, 'task_type', '').lower())
    ]

    # Sort by executed_at descending and limit
    sorted_activity = sorted(
        book_activity,
        key=lambda x: getattr(x, 'executed_at', datetime.min),
        reverse=True
    )[:limit]

    return [
        {
            "action": getattr(log, 'task_type', 'unknown'),
            "target": f"{getattr(log, 'agent_type', 'unknown')}:{getattr(log, 'status', 'unknown')}",
            "details": getattr(log, 'result', {}) if getattr(log, 'result', None) else {},
            "timestamp": getattr(log, 'executed_at', None)
        }
        for log in sorted_activity
    ]


@router.get("/metrics/daily")
async def get_daily_metrics(days: int = 30) -> List[Dict[str, Any]]:
    """Get daily ingestion metrics"""

    # Get all books
    all_books = table_registry.query_rows('memory_documents', filters={'source_type': 'book'})

    # Calculate date range
    from datetime import datetime, timedelta
    cutoff_date = datetime.now() - timedelta(days=days)

    # Group by date
    date_groups = {}
    for book in all_books:
        synced_at = getattr(book, 'last_synced_at', None)
        if synced_at and synced_at >= cutoff_date:
            date_str = synced_at.date().isoformat()
            if date_str not in date_groups:
                date_groups[date_str] = []
            date_groups[date_str].append(book)

    # Calculate metrics per date
    metrics = []
    for date_str, books in date_groups.items():
        trust_scores = [getattr(book, 'trust_score', 0) for book in books if getattr(book, 'trust_score', None) is not None]
        avg_trust = sum(trust_scores) / len(trust_scores) if trust_scores else 0.0

        metrics.append({
            "date": date_str,
            "books_added": len(books),
            "avg_trust_score": round(avg_trust, 3)
        })

    # Sort by date descending
    metrics_sorted = sorted(metrics, key=lambda x: x["date"], reverse=True)

    return metrics_sorted


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

    # Delete verifications
    try:
        verifications = table_registry.query_rows('memory_verification_suites', filters={'document_id': document_id})
        for v in verifications:
            table_registry.update_row('memory_verification_suites', getattr(v, 'id', None), {'deleted': True})
    except:
        pass

    # Delete insights
    try:
        insights = table_registry.query_rows('memory_insights', filters={'document_id': document_id})
        for i in insights:
            table_registry.update_row('memory_insights', getattr(i, 'id', None), {'deleted': True})
    except:
        pass

    # Delete chunks if table exists
    try:
        chunks = table_registry.query_rows('memory_document_chunks', filters={'document_id': document_id})
        for c in chunks:
            table_registry.update_row('memory_document_chunks', getattr(c, 'id', None), {'deleted': True})
    except:
        pass  # Table might not exist

    # Mark document as deleted (soft delete)
    table_registry.update_row('memory_documents', document_id, {'deleted': True})

    return {
        "status": "deleted",
        "document_id": document_id,
        "message": "Book and all associated data deleted"
    }
