"""
Concurrent Execution API - Multi-threading and Background Tasks

Exposes concurrent executor capabilities:
- Submit tasks for parallel execution
- Check task status
- View queue statistics
- Spawn domain-specific subagents
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from ..concurrent_executor import concurrent_executor
from ..auth import get_current_user

router = APIRouter(prefix="/api/concurrent", tags=["concurrent"])


# ============= Request Models =============

class TaskSubmitRequest(BaseModel):
    domain: str
    action: str
    parameters: Dict[str, Any] = {}
    priority: int = 5
    background: bool = True


class BatchTaskRequest(BaseModel):
    tasks: List[Dict[str, Any]]
    wait_for_all: bool = False


# ============= Task Submission =============

@router.post("/tasks/submit")
async def submit_task(
    req: TaskSubmitRequest,
    user=Depends(get_current_user)
):
    """
    Submit task for concurrent execution.
    
    Enables multi-threading for long-running operations.
    """
    
    task_id = await concurrent_executor.submit_task(
        domain=req.domain,
        action=req.action,
        parameters=req.parameters,
        priority=req.priority,
        background=req.background
    )
    
    return {
        "task_id": task_id,
        "domain": req.domain,
        "action": req.action,
        "background": req.background,
        "queued": True
    }


@router.post("/tasks/batch")
async def submit_batch(
    req: BatchTaskRequest,
    user=Depends(get_current_user)
):
    """
    Submit multiple tasks for parallel execution.
    
    All tasks execute concurrently across worker pool.
    """
    
    task_ids = await concurrent_executor.submit_batch(
        tasks=req.tasks,
        wait_for_all=req.wait_for_all
    )
    
    return {
        "task_ids": task_ids,
        "count": len(task_ids),
        "parallel": True,
        "wait_for_all": req.wait_for_all
    }


# ============= Task Status =============

@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    user=Depends(get_current_user)
):
    """Get status of a concurrent task"""
    
    status = await concurrent_executor.get_task_status(task_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return status


@router.get("/queue/status")
async def get_queue_status(user=Depends(get_current_user)):
    """Get concurrent executor queue statistics"""
    
    return await concurrent_executor.get_queue_status()


# ============= Domain Operations =============

@router.get("/domains")
async def list_domains():
    """List all registered domain adapters"""
    
    adapters = domain_registry.get_all_adapters()
    
    return {
        "domains": [
            {
                "domain_id": a.domain_id,
                "domain_type": a.domain_type.value
            }
            for a in adapters
        ],
        "count": len(adapters)
    }


@router.get("/domains/{domain}/metrics")
async def get_domain_metrics(domain: str):
    """Get metrics from specific domain"""
    
    adapter = domain_registry.get_adapter(domain)
    
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Domain not found: {domain}")
    
    from dataclasses import asdict
    metrics = await adapter.collect_metrics()
    
    return asdict(metrics)


@router.get("/domains/metrics/all")
async def get_all_domain_metrics():
    """Get metrics from all domains"""
    
    from dataclasses import asdict
    metrics = await domain_registry.collect_all_metrics()
    
    return {
        domain: asdict(m) for domain, m in metrics.items()
    }
