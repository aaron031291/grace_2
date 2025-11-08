"""
Meta Loop Focus API

Provides health distress summary and meta-loop insights:
- Critical health states across all services
- Open incidents summary
- Current meta loop focus
- Recommended actions
"""

from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from ..auth import get_current_user
from ..models import async_session
from ..settings import settings
from ..schemas_extended import MetaCyclesResponse

router = APIRouter(prefix="/api/meta", tags=["meta-loop"])


@router.get("/focus")
async def get_meta_focus(current_user: str = Depends(get_current_user)):
    """
    Get meta loop focus and health distress summary.
    
    Returns:
    - Current meta loop cycle focus
    - Critical and degraded health states
    - Open incidents count
    - Recommended focus areas
    - Guardrail state
    """
    
    try:
        from ..self_heal.meta_coordinated_healing import meta_coordinated_healing
        from ..health_models import Service, HealthState
        from ..self_heal_models import Incident
    except ImportError:
        raise HTTPException(status_code=503, detail="Meta-loop components not available")
    
    async with async_session() as session:
        now = datetime.now(timezone.utc)
        
        # Get current meta loop cycle
        current_cycle = meta_coordinated_healing.current_cycle
        
        cycle_info = None
        if current_cycle:
            cycle_info = {
                "cycle_id": current_cycle.cycle_id,
                "focus_area": current_cycle.focus_area.value,
                "confidence": current_cycle.confidence,
                "guardrail_adjustment": current_cycle.guardrail_adjustment.value,
                "reasoning": current_cycle.reasoning,
                "extra_probes": current_cycle.extra_probes,
                "playbook_priorities": current_cycle.playbook_priorities,
                "time_budget_seconds": current_cycle.time_budget_seconds
            }
        
        # Get critical and degraded health states
        health_states_result = await session.execute(
            select(HealthState).order_by(HealthState.updated_at.desc()).limit(100)
        )
        health_states = health_states_result.scalars().all()
        
        critical_services = []
        degraded_services = []
        healthy_services = []
        
        for state in health_states:
            # Get service name
            service_result = await session.execute(
                select(Service).where(Service.id == state.service_id)
            )
            service = service_result.scalar_one_or_none()
            
            if not service:
                continue
            
            service_info = {
                "service": service.name,
                "status": state.status,
                "confidence": state.confidence,
                "top_symptoms": state.top_symptoms,
                "last_updated": state.updated_at.isoformat() if state.updated_at else None
            }
            
            if state.status == "critical":
                critical_services.append(service_info)
            elif state.status in ["degraded", "warning"]:
                degraded_services.append(service_info)
            else:
                healthy_services.append(service_info)
        
        # Get open incidents
        incidents_result = await session.execute(
            select(Incident)
            .where(Incident.status == "open")
            .order_by(Incident.created_at.desc())
            .limit(50)
        )
        open_incidents = incidents_result.scalars().all()
        
        incident_summary = []
        for inc in open_incidents:
            incident_summary.append({
                "id": inc.id,
                "service": inc.service,
                "severity": inc.severity,
                "title": inc.title,
                "created_at": inc.created_at.isoformat() if inc.created_at else None
            })
        
        # Calculate health distress score (0-100, higher = worse)
        distress_score = 0.0
        
        if health_states:
            critical_weight = len(critical_services) * 30
            degraded_weight = len(degraded_services) * 10
            incident_weight = len(open_incidents) * 20
            
            distress_score = min(100, critical_weight + degraded_weight + incident_weight)
        
        # Determine recommended focus
        recommended_focus = "routine_maintenance"
        
        if len(critical_services) > 0:
            recommended_focus = "critical_response"
        elif len(open_incidents) > 5:
            recommended_focus = "incident_resolution"
        elif len(degraded_services) > 3:
            recommended_focus = "preventive_maintenance"
        elif distress_score > 30:
            recommended_focus = "health_investigation"
        
        # Guardrail recommendation
        guardrail_recommendation = "maintain"
        
        if distress_score > 60:
            guardrail_recommendation = "tighten"  # Be conservative when stressed
        elif distress_score < 10:
            guardrail_recommendation = "loosen"  # Allow autonomy when healthy
        
        return {
            "current_cycle": cycle_info,
            "health_distress": {
                "score": distress_score,
                "critical_count": len(critical_services),
                "degraded_count": len(degraded_services),
                "healthy_count": len(healthy_services),
                "open_incidents": len(open_incidents)
            },
            "critical_services": critical_services[:10],
            "degraded_services": degraded_services[:10],
            "open_incidents": incident_summary[:10],
            "recommendations": {
                "focus_area": recommended_focus,
                "guardrail_adjustment": guardrail_recommendation,
                "reasoning": [
                    f"{len(critical_services)} critical services" if critical_services else "No critical services",
                    f"{len(degraded_services)} degraded services" if degraded_services else "Services healthy",
                    f"{len(open_incidents)} open incidents" if open_incidents else "No open incidents",
                    f"Distress score: {distress_score:.1f}/100"
                ]
            },
            "metadata": {
                "timestamp": now.isoformat(),
                "guardrail_state": meta_coordinated_healing.guardrail_state.value if meta_coordinated_healing.running else "unknown",
                "total_cycles": len(meta_coordinated_healing.cycle_history)
            }
        }


@router.get("/cycles", response_model=MetaCyclesResponse)
async def get_meta_cycles(
    limit: int = 10,
    current_user: str = Depends(get_current_user)
):
    """Get recent meta loop cycles"""
    
    try:
        from ..self_heal.meta_coordinated_healing import meta_coordinated_healing
        
        recent_cycles = meta_coordinated_healing.cycle_history[-limit:] if meta_coordinated_healing.cycle_history else []
        
        cycles = []
        for cycle in reversed(recent_cycles):
            cycles.append({
                "cycle_id": cycle.cycle_id,
                "focus_area": cycle.focus_area.value,
                "confidence": cycle.confidence,
                "guardrail_adjustment": cycle.guardrail_adjustment.value,
                "reasoning": cycle.reasoning,
                "extra_probes": cycle.extra_probes,
                "playbook_priorities": cycle.playbook_priorities,
                "created_at": cycle.created_at.isoformat()
            })
        
        return MetaCyclesResponse(
            cycles=cycles,
            count=len(cycles),
            current_cycle=cycles[0] if cycles else None,
            execution_trace=None,
            data_provenance=[]
        )
    
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Meta-loop not available: {str(e)}")
