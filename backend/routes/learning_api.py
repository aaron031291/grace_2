"""
Learning API - Knowledge gap detection and autonomous learning
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime

router = APIRouter(prefix="/api/learning", tags=["learning"])

@router.get("/gaps")
async def get_knowledge_gaps() -> Dict[str, Any]:
    """
    Get detected knowledge gaps prioritized by severity
    
    Returns gaps that need learning with suggested sources
    """
    try:
        from backend.learning.knowledge_gap_detector import get_gap_detector
        
        detector = get_gap_detector()
        gaps = detector.get_prioritized_gaps()
        
        return {
            "total_gaps": len(gaps),
            "gaps": [asdict(g) for g in gaps],
            "stats": detector.get_stats()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get gaps: {str(e)}")

@router.post("/gaps/detect")
async def detect_gaps(lookback_hours: int = 24) -> Dict[str, Any]:
    """Trigger gap detection on recent queries"""
    try:
        from backend.learning.knowledge_gap_detector import get_gap_detector
        
        detector = get_gap_detector()
        new_gaps = detector.detect_gaps(lookback_hours)
        
        return {
            "new_gaps_detected": len(new_gaps),
            "gaps": [asdict(g) for g in new_gaps]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect gaps: {str(e)}")

@router.post("/record-query")
async def record_query(
    query: str,
    domain: str,
    confidence: float,
    retrieved_docs: int
) -> Dict[str, Any]:
    """Record a query for gap analysis"""
    try:
        from backend.learning.knowledge_gap_detector import get_gap_detector
        
        detector = get_gap_detector()
        detector.record_query(query, domain, confidence, retrieved_docs)
        
        return {
            "recorded": True,
            "query": query,
            "domain": domain,
            "confidence": confidence
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record query: {str(e)}")

@router.get("/stats")
async def get_learning_stats() -> Dict[str, Any]:
    """Get learning system statistics"""
    try:
        from backend.learning.knowledge_gap_detector import get_gap_detector
        
        detector = get_gap_detector()
        stats = detector.get_stats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "gap_detection": stats,
            "learning_status": {
                "active_learning_jobs": 0,
                "completed_today": 0,
                "success_rate": 0
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
