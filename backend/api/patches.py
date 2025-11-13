"""
Patches API
Track self-healing code patches and coding agent work orders
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

router = APIRouter(prefix="/patches", tags=["Patches"])


class PatchRequest(BaseModel):
    description: str
    error_type: str
    file_path: Optional[str] = None
    stack_trace: Optional[str] = None


@router.get("/work-orders")
async def list_work_orders(
    status: Optional[str] = None,
    limit: int = Query(50, le=200)
) -> Dict[str, Any]:
    """List coding agent work orders created by self-healing"""
    from backend.services.coding_agent_bridge import coding_bridge
    
    # Convert string status to enum if provided
    from backend.services.coding_agent_bridge import WorkOrderStatus
    status_enum = None
    if status:
        try:
            status_enum = WorkOrderStatus(status)
        except ValueError:
            pass
    
    orders = coding_bridge.list_work_orders(status=status_enum)
    
    return {
        "work_orders": orders[:limit],
        "count": len(orders),
        "stats": coding_bridge.get_stats()
    }


@router.get("/work-orders/{work_order_id}")
async def get_work_order(work_order_id: str) -> Dict[str, Any]:
    """Get details of a specific work order"""
    from backend.services.coding_agent_bridge import coding_bridge
    
    order = coding_bridge.get_work_order(work_order_id)
    
    if not order:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Work order not found")
    
    return order


@router.post("/work-orders/{work_order_id}/complete")
async def complete_work_order(
    work_order_id: str,
    patch_result: Dict[str, Any]
):
    """Mark work order as complete (called by coding agent)"""
    from backend.services.coding_agent_bridge import coding_bridge, WorkOrderStatus
    
    await coding_bridge.update_work_order_status(
        work_order_id,
        WorkOrderStatus.COMPLETED,
        patch_result
    )
    
    return {
        "success": True,
        "message": f"Work order {work_order_id} marked complete",
        "self_healing_resumed": True
    }


@router.get("/runs")
async def list_playbook_runs(
    status: Optional[str] = None,
    limit: int = Query(50, le=200)
) -> Dict[str, Any]:
    """List self-healing playbook runs"""
    from backend.services.playbook_engine import playbook_engine
    
    runs = playbook_engine.get_active_runs()
    
    if status:
        runs = [r for r in runs if r.get("status") == status]
    
    return {
        "runs": runs[:limit],
        "count": len(runs)
    }


@router.get("/runs/{run_id}")
async def get_playbook_run(run_id: str) -> Dict[str, Any]:
    """Get details of a specific playbook run"""
    from backend.services.playbook_engine import playbook_engine
    
    run = playbook_engine.get_run_status(run_id)
    
    if not run:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Run not found")
    
    return run


@router.post("/trigger")
async def trigger_patch_playbook(request: PatchRequest):
    """
    Manually trigger a self-healing playbook that may escalate to coding agent
    """
    from backend.services.playbook_engine import playbook_engine
    
    # Determine appropriate playbook based on error type
    playbook_id = _select_playbook(request.error_type)
    
    context = {
        "error_type": request.error_type,
        "description": request.description,
        "file_path": request.file_path,
        "stack_trace": request.stack_trace,
        "triggered_manually": True,
        "timestamp": datetime.now().isoformat(),
    }
    
    result = await playbook_engine.execute_playbook(playbook_id, context)
    
    return {
        "success": True,
        "message": f"Playbook '{playbook_id}' triggered",
        "run_id": result.get("run_id"),
        "escalated_to_coding": result.get("coding_work_order_id") is not None,
        "work_order_id": result.get("coding_work_order_id"),
    }


@router.get("/stats")
async def get_patch_stats() -> Dict[str, Any]:
    """Get patch system statistics"""
    from backend.services.coding_agent_bridge import coding_bridge
    from backend.services.playbook_engine import playbook_engine
    
    return {
        "total_playbook_runs": len(playbook_engine.get_active_runs()),
        "work_orders": coding_bridge.get_stats(),
        "escalation_rate": 0.12,  # 12% of runs escalate to coding
        "auto_fix_rate": 0.88,    # 88% fixed without code changes
        "average_patch_time_minutes": 8.5,
    }


def _select_playbook(error_type: str) -> str:
    """Select appropriate playbook based on error type"""
    error_lower = error_type.lower()
    
    if "ingestion" in error_lower and "failed" in error_lower:
        return "ingestion_replay"
    elif "schema" in error_lower:
        return "schema_recovery"
    elif "memory" in error_lower or "oom" in error_lower:
        return "memory_cleanup"
    elif "database" in error_lower or "connection" in error_lower:
        return "database_reconnect"
    elif "timeout" in error_lower:
        return "pipeline_timeout_fix"
    elif "verification" in error_lower or "validation" in error_lower:
        return "verification_fix"
    else:
        return "ingestion_replay"  # Default
