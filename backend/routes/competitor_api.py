"""
Competitor Tracking API
Monitor and analyze competitor marketing campaigns
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/competitors", tags=["Competitor Tracking"])


class TrackCompetitorRequest(BaseModel):
    competitor_name: str
    platforms: List[str] = ["meta", "tiktok", "google"]


@router.post("/track")
async def track_competitor(request: TrackCompetitorRequest):
    """
    Track a specific competitor across platforms
    Downloads their ads, campaigns, strategies
    """
    try:
        from backend.agents.competitor_tracker import competitor_tracker
        
        results = {}
        
        if "meta" in request.platforms:
            meta_result = await competitor_tracker.track_facebook_ads(
                competitor_name=request.competitor_name
            )
            results['meta'] = meta_result
        
        if "tiktok" in request.platforms:
            tiktok_result = await competitor_tracker.track_tiktok_campaigns(
                industry=request.competitor_name
            )
            results['tiktok'] = tiktok_result
        
        return {
            "success": True,
            "competitor": request.competitor_name,
            "platforms_tracked": request.platforms,
            "results": results
        }
    
    except Exception as e:
        logger.error(f"[COMPETITOR-API] Tracking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze-patterns")
async def analyze_patterns(platform: str = "all"):
    """
    Analyze all tracked campaigns to identify winning patterns
    Returns what works across competitors
    """
    try:
        from backend.agents.competitor_tracker import competitor_tracker
        
        patterns = await competitor_tracker.analyze_campaign_patterns(
            platform=platform
        )
        
        return {
            "success": True,
            "patterns": patterns,
            "platform": platform
        }
    
    except Exception as e:
        logger.error(f"[COMPETITOR-API] Pattern analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_tracking_metrics():
    """Get competitor tracking metrics"""
    try:
        from backend.agents.competitor_tracker import competitor_tracker
        
        metrics = await competitor_tracker.get_metrics()
        return {
            **metrics,
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "status": "degraded"
        }
