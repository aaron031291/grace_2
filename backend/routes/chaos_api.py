"""
Chaos Engineering API
Control and monitor chaos campaigns
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/chaos",
    tags=["Chaos Engineering"]
)


class ChaosRequest(BaseModel):
    """Request to run chaos campaign"""
    target_components: Optional[List[str]] = None
    environment: str = 'staging'
    approved_by: str


@router.get("/status")
async def get_chaos_status():
    """Get chaos agent status"""
    try:
        from backend.chaos.chaos_agent import chaos_agent
        
        stats = chaos_agent.get_stats()
        
        return {
            "status": stats.get('status'),
            "statistics": stats
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Chaos agent not initialized: {e}")


@router.get("/components")
async def list_components():
    """List all component profiles"""
    try:
        from backend.chaos.component_profiles import component_registry
        
        profiles = component_registry.list_profiles()
        
        return {
            "components": [p.to_dict() for p in profiles],
            "total": len(profiles)
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Component registry not initialized: {e}")


@router.get("/components/{component_id}")
async def get_component_profile(component_id: str):
    """Get component profile details"""
    try:
        from backend.chaos.component_profiles import component_registry
        
        profile = component_registry.get_profile(component_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail=f"Component not found: {component_id}")
        
        return profile.to_dict()
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Component registry not initialized: {e}")


@router.post("/run")
async def run_chaos_campaign(request: ChaosRequest):
    """
    Run a chaos engineering campaign
    
    Requires governance approval for production
    """
    try:
        from backend.chaos.chaos_agent import chaos_agent
        
        # Validate environment
        if request.environment not in ['staging', 'shadow', 'production']:
            raise HTTPException(status_code=400, detail=f"Invalid environment: {request.environment}")
        
        # Production requires explicit approval
        if request.environment == 'production' and not request.approved_by:
            raise HTTPException(status_code=403, detail="Production chaos requires approval")
        
        # Run campaign
        campaign_id = await chaos_agent.run_campaign(
            target_components=request.target_components,
            environment=request.environment,
            approved_by=request.approved_by
        )
        
        return {
            "campaign_id": campaign_id,
            "status": "started",
            "environment": request.environment
        }
    except Exception as e:
        if 'denied by governance' in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns")
async def list_campaigns():
    """List all chaos campaigns"""
    try:
        from backend.chaos.chaos_agent import chaos_agent
        
        campaigns = [c.to_dict() for c in chaos_agent.campaigns.values()]
        
        # Sort by started time (newest first)
        campaigns.sort(key=lambda c: c.get('started_at', ''), reverse=True)
        
        return {
            "campaigns": campaigns,
            "total": len(campaigns)
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Chaos agent not initialized: {e}")


@router.get("/campaigns/{campaign_id}")
async def get_campaign_details(campaign_id: str):
    """Get campaign details with results"""
    try:
        from backend.chaos.chaos_agent import chaos_agent
        
        campaign = chaos_agent.get_campaign(campaign_id)
        
        if not campaign:
            raise HTTPException(status_code=404, detail=f"Campaign not found: {campaign_id}")
        
        return campaign
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Chaos agent not initialized: {e}")


@router.post("/halt")
async def halt_chaos():
    """Emergency halt - Guardian override"""
    try:
        from backend.core.message_bus import message_bus
        
        await message_bus.publish('guardian.halt_chaos', {
            'timestamp': datetime.utcnow().isoformat(),
            'reason': 'Manual halt requested'
        })
        
        return {
            "status": "halted",
            "message": "Chaos agent halted by Guardian"
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Message bus not available: {e}")


@router.get("/resilience")
async def get_resilience_rankings():
    """Get components ranked by resilience"""
    try:
        from backend.chaos.component_profiles import component_registry
        
        # Lowest resilience first (need most improvement)
        profiles = component_registry.get_by_resilience(ascending=True)
        
        rankings = []
        for i, profile in enumerate(profiles, 1):
            rankings.append({
                'rank': i,
                'component_id': profile.component_id,
                'component_name': profile.component_name,
                'resilience_score': profile.resilience_score,
                'last_tested': profile.last_tested,
                'test_count': len(profile.test_history)
            })
        
        return {
            "rankings": rankings,
            "total": len(rankings)
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Component registry not initialized: {e}")
