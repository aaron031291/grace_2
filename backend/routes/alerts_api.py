"""
Alerts API Routes
Endpoints for alert monitoring and management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


class AcknowledgeRequest(BaseModel):
    alert_id: str


@router.get("/active")
async def get_active_alerts(severity: Optional[str] = None):
    """Get all active alerts"""
    try:
        from backend.memory_tables.alert_system import alert_system, AlertSeverity
        
        if not alert_system._initialized:
            await alert_system.initialize()
        
        severity_filter = None
        if severity:
            try:
                severity_filter = AlertSeverity(severity.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
        
        alerts = alert_system.get_active_alerts(severity_filter)
        
        return {
            'success': True,
            'alerts': alerts,
            'count': len(alerts)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_alert_summary():
    """Get summary of current alerts"""
    try:
        from backend.memory_tables.alert_system import alert_system
        
        if not alert_system._initialized:
            await alert_system.initialize()
        
        summary = alert_system.get_alert_summary()
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/acknowledge")
async def acknowledge_alert(request: AcknowledgeRequest):
    """Acknowledge an alert"""
    try:
        from backend.memory_tables.alert_system import alert_system
        
        if not alert_system._initialized:
            await alert_system.initialize()
        
        success = alert_system.acknowledge_alert(request.alert_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {'success': True, 'alert_id': request.alert_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resolve")
async def resolve_alert(request: AcknowledgeRequest):
    """Resolve an alert"""
    try:
        from backend.memory_tables.alert_system import alert_system
        
        if not alert_system._initialized:
            await alert_system.initialize()
        
        success = alert_system.resolve_alert(request.alert_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {'success': True, 'alert_id': request.alert_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/start")
async def start_monitoring(interval_seconds: int = 60):
    """Start alert monitoring"""
    try:
        from backend.memory_tables.alert_system import alert_system
        
        await alert_system.start_monitoring(interval_seconds)
        
        return {
            'success': True,
            'message': f'Alert monitoring started (interval: {interval_seconds}s)'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/stop")
async def stop_monitoring():
    """Stop alert monitoring"""
    try:
        from backend.memory_tables.alert_system import alert_system
        
        await alert_system.stop_monitoring()
        
        return {
            'success': True,
            'message': 'Alert monitoring stopped'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-now")
async def check_conditions_now():
    """Manually trigger alert condition checks"""
    try:
        from backend.memory_tables.alert_system import alert_system
        
        if not alert_system._initialized:
            await alert_system.initialize()
        
        await alert_system._check_all_conditions()
        
        summary = alert_system.get_alert_summary()
        
        return {
            'success': True,
            'message': 'Alert check complete',
            'summary': summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
