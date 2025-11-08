from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from datetime import datetime
from ..governance_models import HealthCheck, HealingAction
from ..models import async_session
from ..auth import get_current_user
from ..self_healing import health_monitor, system_state
from ..schemas import HealthStatusResponse, HealthRestartResponse, HealthModeResponse, HealthModeSetResponse

router = APIRouter(prefix="/api/health", tags=["health"])

class RestartRequest(BaseModel):
    component: str

@router.get("/status", response_model=HealthStatusResponse)
async def status(limit: int = 10):
    """Get health check status and recent healing actions"""
    async with async_session() as session:
        checks = await session.execute(
            select(HealthCheck).order_by(HealthCheck.created_at.desc()).limit(limit)
        )
        actions = await session.execute(
            select(HealingAction).order_by(HealingAction.created_at.desc()).limit(limit)
        )
    
    return {
        "system_mode": system_state.mode,
        "mode_reason": system_state.reason,
        "mode_changed": system_state.last_changed,
        "checks": [
            {
                "component": c.component,
                "status": c.status,
                "latency_ms": c.latency_ms,
                "error": c.error,
                "at": c.created_at
            }
            for c in checks.scalars().all()
        ],
        "actions": [
            {
                "component": a.component,
                "action": a.action,
                "result": a.result,
                "detail": a.detail,
                "at": a.created_at
            }
            for a in actions.scalars().all()
        ],
    }

@router.post("/restart", response_model=HealthRestartResponse)
async def manual_restart(
    req: RestartRequest,
    current_user: str = Depends(get_current_user)
):
    """Manually restart a component (governed)"""
    result = await health_monitor.manual_restart(req.component, current_user)
    return result

@router.get("/mode", response_model=HealthModeResponse)
async def get_system_mode():
    """Get current system operational mode"""
    return {
        "mode": system_state.mode,
        "reason": system_state.reason,
        "changed_at": system_state.last_changed
    }

@router.post("/mode", response_model=HealthModeSetResponse)
async def set_system_mode(
    mode: str,
    reason: str = "",
    current_user: str = Depends(get_current_user)
):
    """Change system mode (governed)"""
    from ..governance import governance_engine
    
    decision = await governance_engine.check(
        actor=current_user,
        action="change_system_mode",
        resource=mode,
        payload={"from": system_state.mode, "to": mode, "reason": reason}
    )
    
    if decision["decision"] != "allow":
        return {"status": "denied", "decision": decision["decision"]}
    
    system_state.mode = mode
    system_state.reason = reason
    system_state.last_changed = datetime.utcnow()
    
    print(f"🔧 System mode changed to: {mode} (by {current_user})")
    
    return {
        "status": "success",
        "mode": system_state.mode,
        "reason": system_state.reason
    }
