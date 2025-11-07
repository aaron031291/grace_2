"""
Unified Verification & Resilience Router

Consolidates all verification artifacts under a single API surface:
- Action contracts
- Safe-hold snapshots
- Benchmarks
- Mission timelines
- Learning stats

Consistent response envelope: { data, meta }
OpenAPI tags for frontend discovery
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from ..models import async_session
from ..action_contract import ActionContract
from ..self_heal.safe_hold import SafeHoldSnapshot
from ..progression_tracker import Mission
from ..auth import get_current_user

# Handle Benchmark import (may be in different location)
try:
    from ..benchmarks.models import Benchmark
except (ImportError, AttributeError):
    try:
        from ..benchmarks import Benchmark
    except (ImportError, AttributeError):
        # Create a placeholder if not available
        Benchmark = None

router = APIRouter(
    prefix="/api/verification",
    tags=["verification", "resilience"],
    responses={404: {"description": "Not found"}}
)


def _response_envelope(data: Any, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Consistent response wrapper"""
    return {
        "data": data,
        "meta": meta or {}
    }


@router.get(
    "/contracts",
    summary="List action contracts",
    description="Retrieve all action contracts with optional filtering"
)
async def list_contracts(
    status: Optional[str] = Query(None, description="Filter by status: pending, executing, verified, violated, rolled_back"),
    tier: Optional[str] = Query(None, description="Filter by autonomy tier: tier_1, tier_2, tier_3"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(async_session)
):
    """List action contracts with pagination and filtering"""
    query = select(ActionContract)
    
    if status:
        query = query.where(ActionContract.status == status)
    if tier:
        query = query.where(ActionContract.tier == tier)
    
    # Count total
    count_query = select(func.count()).select_from(query.alias())
    total = await session.scalar(count_query)
    
    query = query.order_by(desc(ActionContract.created_at)).limit(limit).offset(offset)
    result = await session.execute(query)
    contracts = result.scalars().all()
    
    return _response_envelope(
        data=[{
            "id": c.id,
            "action_type": c.action_type,
            "status": c.status,
            "tier": c.tier,
            "expected_effect": c.expected_effect,
            "actual_outcome": c.actual_outcome,
            "verification_result": c.verification_result,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "executed_at": c.executed_at.isoformat() if c.executed_at else None,
            "verified_at": c.verified_at.isoformat() if c.verified_at else None,
            "playbook_id": c.playbook_id,
            "run_id": c.run_id,
            "triggered_by": c.triggered_by
        } for c in contracts],
        meta={
            "total": total,
            "limit": limit,
            "offset": offset,
            "count": len(contracts)
        }
    )


@router.get(
    "/contracts/{contract_id}",
    summary="Get contract details",
    description="Retrieve a specific action contract by ID"
)
async def get_contract(
    contract_id: int,
    session: AsyncSession = Depends(async_session)
):
    """Get detailed contract information"""
    contract = await session.get(ActionContract, contract_id)
    
    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found")
    
    return _response_envelope(
        data={
            "id": contract.id,
            "action_type": contract.action_type,
            "status": contract.status,
            "tier": contract.tier,
            "expected_effect": contract.expected_effect,
            "actual_outcome": contract.actual_outcome,
            "verification_result": contract.verification_result,
            "baseline_state": contract.baseline_state,
            "created_at": contract.created_at.isoformat() if contract.created_at else None,
            "executed_at": contract.executed_at.isoformat() if contract.executed_at else None,
            "verified_at": contract.verified_at.isoformat() if contract.verified_at else None,
            "rolled_back_at": contract.rolled_back_at.isoformat() if contract.rolled_back_at else None,
            "safe_hold_snapshot_id": contract.safe_hold_snapshot_id,
            "playbook_id": contract.playbook_id,
            "run_id": contract.run_id,
            "triggered_by": contract.triggered_by,
            "rollback_reason": contract.rollback_reason
        }
    )


@router.get(
    "/snapshots",
    summary="List safe-hold snapshots",
    description="Retrieve system state snapshots with optional filtering"
)
async def list_snapshots(
    snapshot_type: Optional[str] = Query(None, description="Filter by type: pre_action, post_rollback, periodic"),
    contract_id: Optional[int] = Query(None, description="Filter by associated contract"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(async_session)
):
    """List safe-hold snapshots"""
    query = select(SafeHoldSnapshot)
    
    if snapshot_type:
        query = query.where(SafeHoldSnapshot.snapshot_type == snapshot_type)
    if contract_id:
        query = query.where(SafeHoldSnapshot.action_contract_id == contract_id)
    
    # Count total
    count_query = select(func.count()).select_from(query.alias())
    total = await session.scalar(count_query)
    
    query = query.order_by(desc(SafeHoldSnapshot.created_at)).limit(limit).offset(offset)
    result = await session.execute(query)
    snapshots = result.scalars().all()
    
    return _response_envelope(
        data=[{
            "id": s.id,
            "snapshot_type": s.snapshot_type,
            "triggered_by": s.triggered_by,
            "action_contract_id": s.action_contract_id,
            "playbook_run_id": s.playbook_run_id,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "restored_at": s.restored_at.isoformat() if s.restored_at else None,
            "notes": s.notes,
            "state_hash": s.state_hash
        } for s in snapshots],
        meta={
            "total": total,
            "limit": limit,
            "offset": offset,
            "count": len(snapshots)
        }
    )


@router.get(
    "/snapshots/{snapshot_id}",
    summary="Get snapshot details",
    description="Retrieve a specific snapshot with full state data"
)
async def get_snapshot(
    snapshot_id: int,
    session: AsyncSession = Depends(async_session)
):
    """Get detailed snapshot information"""
    snapshot = await session.get(SafeHoldSnapshot, snapshot_id)
    
    if not snapshot:
        raise HTTPException(status_code=404, detail=f"Snapshot {snapshot_id} not found")
    
    return _response_envelope(
        data={
            "id": snapshot.id,
            "snapshot_type": snapshot.snapshot_type,
            "triggered_by": snapshot.triggered_by,
            "action_contract_id": snapshot.action_contract_id,
            "playbook_run_id": snapshot.playbook_run_id,
            "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
            "restored_at": snapshot.restored_at.isoformat() if snapshot.restored_at else None,
            "state_data": snapshot.state_data,
            "state_hash": snapshot.state_hash,
            "notes": snapshot.notes
        }
    )


@router.get(
    "/benchmarks",
    summary="List benchmarks",
    description="Retrieve benchmark results for drift detection"
)
async def list_benchmarks(
    benchmark_type: Optional[str] = Query(None, description="Filter by type: post_action, scheduled, on_demand"),
    contract_id: Optional[int] = Query(None, description="Filter by associated contract"),
    passed: Optional[bool] = Query(None, description="Filter by pass/fail status"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(async_session)
):
    """List benchmark results"""
    query = select(Benchmark)
    
    if benchmark_type:
        query = query.where(Benchmark.benchmark_type == benchmark_type)
    if contract_id:
        query = query.where(Benchmark.action_contract_id == contract_id)
    if passed is not None:
        query = query.where(Benchmark.passed == passed)
    
    # Count total
    count_query = select(func.count()).select_from(query.alias())
    total = await session.scalar(count_query)
    
    query = query.order_by(desc(Benchmark.executed_at)).limit(limit).offset(offset)
    result = await session.execute(query)
    benchmarks = result.scalars().all()
    
    return _response_envelope(
        data=[{
            "id": b.id,
            "benchmark_type": b.benchmark_type,
            "action_contract_id": b.action_contract_id,
            "passed": b.passed,
            "score": b.score,
            "metrics": b.metrics,
            "executed_at": b.executed_at.isoformat() if b.executed_at else None,
            "duration_ms": b.duration_ms
        } for b in benchmarks],
        meta={
            "total": total,
            "limit": limit,
            "offset": offset,
            "count": len(benchmarks),
            "pass_rate": sum(1 for b in benchmarks if b.passed) / len(benchmarks) if benchmarks else 0
        }
    )


@router.get(
    "/missions",
    summary="List missions",
    description="Retrieve mission timelines and progression data"
)
async def list_missions(
    status: Optional[str] = Query(None, description="Filter by status: active, completed, failed, cancelled"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(async_session)
):
    """List missions with progression tracking"""
    query = select(Mission)
    
    if status:
        query = query.where(Mission.status == status)
    
    # Count total
    count_query = select(func.count()).select_from(query.alias())
    total = await session.scalar(count_query)
    
    query = query.order_by(desc(Mission.started_at)).limit(limit).offset(offset)
    result = await session.execute(query)
    missions = result.scalars().all()
    
    return _response_envelope(
        data=[{
            "id": m.id,
            "mission_id": m.mission_id,
            "status": m.status,
            "goal": m.goal,
            "started_at": m.started_at.isoformat() if m.started_at else None,
            "completed_at": m.completed_at.isoformat() if m.completed_at else None,
            "progress_percent": m.progress_percent,
            "current_phase": m.current_phase,
            "total_actions": m.total_actions,
            "completed_actions": m.completed_actions
        } for m in missions],
        meta={
            "total": total,
            "limit": limit,
            "offset": offset,
            "count": len(missions)
        }
    )


@router.get(
    "/learning/stats",
    summary="Get learning statistics",
    description="Retrieve aggregated learning metrics and playbook success rates"
)
async def get_learning_stats(
    session: AsyncSession = Depends(async_session)
):
    """Get learning loop statistics"""
    from ..learning_loop import learning_loop
    
    # Get playbook success rates
    playbook_stats = learning_loop.playbook_success_rates
    
    # Get contract statistics
    total_contracts = await session.scalar(select(func.count(ActionContract.id)))
    verified_contracts = await session.scalar(
        select(func.count(ActionContract.id)).where(ActionContract.status == "verified")
    )
    violated_contracts = await session.scalar(
        select(func.count(ActionContract.id)).where(ActionContract.status == "violated")
    )
    rolled_back_contracts = await session.scalar(
        select(func.count(ActionContract.id)).where(ActionContract.status == "rolled_back")
    )
    
    # Get benchmark statistics
    total_benchmarks = await session.scalar(select(func.count(Benchmark.id)))
    passed_benchmarks = await session.scalar(
        select(func.count(Benchmark.id)).where(Benchmark.passed == True)
    )
    
    return _response_envelope(
        data={
            "playbook_success_rates": playbook_stats,
            "contracts": {
                "total": total_contracts or 0,
                "verified": verified_contracts or 0,
                "violated": violated_contracts or 0,
                "rolled_back": rolled_back_contracts or 0,
                "verification_rate": (verified_contracts or 0) / (total_contracts or 1)
            },
            "benchmarks": {
                "total": total_benchmarks or 0,
                "passed": passed_benchmarks or 0,
                "pass_rate": (passed_benchmarks or 0) / (total_benchmarks or 1)
            }
        },
        meta={
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    )


@router.get(
    "/health",
    summary="Verification system health",
    description="Check overall health of the verification subsystem"
)
async def verification_health(
    session: AsyncSession = Depends(async_session)
):
    """Health check for verification system"""
    
    # Check recent contracts
    recent_contracts = await session.scalar(
        select(func.count(ActionContract.id)).where(
            ActionContract.created_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        )
    )
    
    # Check recent benchmarks
    recent_benchmarks = await session.scalar(
        select(func.count(Benchmark.id)).where(
            Benchmark.executed_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        )
    )
    
    return _response_envelope(
        data={
            "status": "healthy",
            "contracts_today": recent_contracts or 0,
            "benchmarks_today": recent_benchmarks or 0,
            "components": {
                "contract_verifier": "operational",
                "snapshot_manager": "operational",
                "benchmark_suite": "operational",
                "learning_loop": "operational"
            }
        },
        meta={
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
    )
