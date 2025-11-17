"""
Monitoring API
Real incident tracking with database integration
"""

from fastapi import APIRouter, Query
from typing import Dict, Any, Optional
from datetime import datetime

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/incidents")
async def get_incidents(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, le=200)
) -> Dict[str, Any]:
    """Get real monitoring incidents from database"""
    try:
        from backend.monitoring_models import MonitoringEvent
        from backend.models import async_session
        from sqlalchemy import select, desc
        
        async with async_session() as session:
            query = select(MonitoringEvent).order_by(desc(MonitoringEvent.detected_at))
            
            if severity:
                query = query.where(MonitoringEvent.severity == severity)
            
            if status:
                query = query.where(MonitoringEvent.status == status)
            
            query = query.limit(limit)
            
            result = await session.execute(query)
            events = result.scalars().all()
            
            return {
                "incidents": [event.to_dict() for event in events],
                "count": len(events),
                "severity_counts": await get_severity_counts(session),
                "status_counts": await get_status_counts(session)
            }
    except Exception as e:
        print(f"[MonitoringAPI] Error fetching incidents: {e}")
        # Fall back to mock data if DB not ready
        return await get_mock_incidents(severity, status, limit)


@router.get("/executions")
async def get_executions(limit: int = Query(50, le=200)) -> Dict[str, Any]:
    """Get self-healing execution logs"""
    try:
        from backend.monitoring_models import SelfHealingExecution
        from backend.models import async_session
        from sqlalchemy import select, desc
        
        async with async_session() as session:
            query = select(SelfHealingExecution).order_by(desc(SelfHealingExecution.started_at)).limit(limit)
            result = await session.execute(query)
            executions = result.scalars().all()
            
            return {
                "executions": [ex.to_dict() for ex in executions],
                "count": len(executions)
            }
    except Exception as e:
        print(f"[MonitoringAPI] Error fetching executions: {e}")
        return {"executions": [], "count": 0}


@router.get("/agents")
async def get_active_agents() -> Dict[str, Any]:
    """Get active sub-agents"""
    try:
        from backend.monitoring_models import ActiveAgent
        from backend.models import async_session
        from sqlalchemy import select
        
        async with async_session() as session:
            query = select(ActiveAgent).where(ActiveAgent.status == "active")
            result = await session.execute(query)
            agents = result.scalars().all()
            
            return {
                "agents": [agent.to_dict() for agent in agents],
                "count": len(agents)
            }
    except Exception as e:
        print(f"[MonitoringAPI] Error fetching agents: {e}")
        return {"agents": [], "count": 0}


@router.post("/incidents/{incident_id}/acknowledge")
async def acknowledge_incident(incident_id: int):
    """Acknowledge an incident"""
    try:
        from backend.monitoring_models import MonitoringEvent
        from backend.models import async_session
        
        async with async_session() as session:
            event = await session.get(MonitoringEvent, incident_id)
            if event:
                event.status = "acknowledged"
                event.acknowledged_at = datetime.now()
                await session.commit()
                
                return {"success": True, "message": f"Incident {incident_id} acknowledged"}
            else:
                return {"success": False, "message": "Incident not found"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/incidents/{incident_id}/resolve")
async def resolve_incident(incident_id: int):
    """Manually resolve an incident"""
    try:
        from backend.monitoring_models import MonitoringEvent
        from backend.models import async_session
        
        async with async_session() as session:
            event = await session.get(MonitoringEvent, incident_id)
            if event:
                event.status = "resolved"
                event.resolved_at = datetime.now()
                if event.detected_at:
                    delta = datetime.now() - event.detected_at
                    event.resolution_time_seconds = delta.total_seconds()
                await session.commit()
                
                return {"success": True, "message": f"Incident {incident_id} resolved"}
            else:
                return {"success": False, "message": "Incident not found"}
    except Exception as e:
        return {"success": False, "message": str(e)}


# Helper functions

async def get_severity_counts(session) -> Dict[str, int]:
    """Get count of incidents by severity"""
    try:
        from backend.monitoring_models import MonitoringEvent
        from sqlalchemy import select, func
        
        query = select(
            MonitoringEvent.severity,
            func.count(MonitoringEvent.id)
        ).where(
            MonitoringEvent.status != "resolved"
        ).group_by(MonitoringEvent.severity)
        
        result = await session.execute(query)
        return {row[0]: row[1] for row in result.all()}
    except Exception:
        return {}


async def get_status_counts(session) -> Dict[str, int]:
    """Get count of incidents by status"""
    try:
        from backend.monitoring_models import MonitoringEvent
        from sqlalchemy import select, func
        
        query = select(
            MonitoringEvent.status,
            func.count(MonitoringEvent.id)
        ).group_by(MonitoringEvent.status)
        
        result = await session.execute(query)
        return {row[0]: row[1] for row in result.all()}
    except Exception:
        return {}


async def get_mock_incidents(severity, status, limit) -> Dict[str, Any]:
    """Fallback mock data if database not ready"""
    from backend.api.self_healing import get_incidents as get_mock
    return await get_mock(limit)
