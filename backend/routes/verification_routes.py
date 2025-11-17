"""
Verification & Progression API Routes

Exposes endpoints for:
- Action contracts and verification status
- Safe-hold snapshots and rollback capability
- Benchmark results and drift detection
- Mission progression tracking

Provides UI visibility into Grace's autonomy and safety mechanisms.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime, timezone

from ..self_heal.safe_hold import snapshot_manager, SafeHoldSnapshot
from ..benchmarks import benchmark_suite
from ..progression_tracker import progression_tracker
from ..models import async_session
from ..schemas import (
    ContractListResponse, ContractDetailResponse, SnapshotListResponse, SnapshotDetailResponse,
    SnapshotRestoreResponse, GoldenSnapshotResponse, BenchmarkRunListResponse, BenchmarkRunDetailResponse,
    BenchmarkGoldenResponse, MissionStartResponse, MissionCompleteResponse, MissionHistoryResponse,
    VerificationSmokeTestResponse, VerificationRegressionResponse
)
from ..schemas_extended import (
    VerificationCurrentMissionResponse, VerificationStatusResponseExtended
)

router = APIRouter(prefix="/api/verification", tags=["verification"])


# ============= Action Contracts =============

@router.get("/contracts", response_model=ContractListResponse)
async def list_contracts(
    limit: int = 20,
    status: Optional[str] = None
):
    """List recent action contracts"""
    
    from ..action_contract import ActionContract
    from sqlalchemy import select
    
    async with async_session() as session:
        query = select(ActionContract).order_by(ActionContract.created_at.desc()).limit(limit)
        
        if status:
            query = query.where(ActionContract.status == status)
        
        result = await session.execute(query)
        contracts = result.scalars().all()
        
        return {
            "contracts": [
                {
                    "id": c.id,
                    "action_type": c.action_type,
                    "playbook_id": c.playbook_id,
                    "status": c.status,
                    "tier": c.tier,
                    "confidence_score": c.confidence_score,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "verified_at": c.verified_at.isoformat() if c.verified_at else None,
                    "requires_approval": c.requires_approval
                }
                for c in contracts
            ]
        }


@router.get("/contracts/{contract_id}", response_model=ContractDetailResponse)
async def get_contract(contract_id: str):
    """Get detailed contract information"""
    
    from ..action_contract import ActionContract
    
    async with async_session() as session:
        contract = await session.get(ActionContract, contract_id)
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        return {
            "id": contract.id,
            "action_type": contract.action_type,
            "playbook_id": contract.playbook_id,
            "run_id": contract.run_id,
            "status": contract.status,
            "tier": contract.tier,
            "expected_effect": contract.expected_effect,
            "baseline_state": contract.baseline_state,
            "actual_effect": contract.actual_effect,
            "verification_result": contract.verification_result,
            "confidence_score": contract.confidence_score,
            "safe_hold_snapshot_id": contract.safe_hold_snapshot_id,
            "created_at": contract.created_at.isoformat() if contract.created_at else None,
            "executed_at": contract.executed_at.isoformat() if contract.executed_at else None,
            "verified_at": contract.verified_at.isoformat() if contract.verified_at else None,
            "triggered_by": contract.triggered_by
        }


# ============= Safe-Hold Snapshots =============

@router.get("/snapshots", response_model=SnapshotListResponse)
async def list_snapshots(
    limit: int = 20,
    snapshot_type: Optional[str] = None,
    is_golden: Optional[bool] = None
):
    """List safe-hold snapshots"""
    
    from sqlalchemy import select
    
    async with async_session() as session:
        query = select(SafeHoldSnapshot).order_by(SafeHoldSnapshot.created_at.desc()).limit(limit)
        
        if snapshot_type:
            query = query.where(SafeHoldSnapshot.snapshot_type == snapshot_type)
        if is_golden is not None:
            query = query.where(SafeHoldSnapshot.is_golden == is_golden)
        
        result = await session.execute(query)
        snapshots = result.scalars().all()
        
        return {
            "snapshots": [
                {
                    "id": s.id,
                    "snapshot_type": s.snapshot_type,
                    "status": s.status,
                    "is_golden": s.is_golden,
                    "is_validated": s.is_validated,
                    "system_health_score": s.system_health_score,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                    "triggered_by": s.triggered_by,
                    "action_contract_id": s.action_contract_id,
                    "notes": s.notes
                }
                for s in snapshots
            ]
        }


@router.get("/snapshots/{snapshot_id}", response_model=SnapshotDetailResponse)
async def get_snapshot(snapshot_id: str):
    """Get detailed snapshot information"""
    
    async with async_session() as session:
        snapshot = await session.get(SafeHoldSnapshot, snapshot_id)
        
        if not snapshot:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        
        return {
            "id": snapshot.id,
            "snapshot_type": snapshot.snapshot_type,
            "status": snapshot.status,
            "is_golden": snapshot.is_golden,
            "is_validated": snapshot.is_validated,
            "manifest": snapshot.manifest,
            "manifest_hash": snapshot.manifest_hash,
            "storage_uri": snapshot.storage_uri,
            "baseline_metrics": snapshot.baseline_metrics,
            "system_health_score": snapshot.system_health_score,
            "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
            "validated_at": snapshot.validated_at.isoformat() if snapshot.validated_at else None,
            "restored_at": snapshot.restored_at.isoformat() if snapshot.restored_at else None,
            "triggered_by": snapshot.triggered_by,
            "action_contract_id": snapshot.action_contract_id,
            "playbook_run_id": snapshot.playbook_run_id,
            "notes": snapshot.notes
        }


@router.post("/snapshots/{snapshot_id}/restore", response_model=SnapshotRestoreResponse)
async def restore_snapshot(snapshot_id: str, dry_run: bool = False):
    """Restore system to a snapshot (or dry-run to validate)"""
    
    result = await snapshot_manager.restore_snapshot(
        snapshot_id=snapshot_id,
        dry_run=dry_run
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Restore failed"))
    
    return result


@router.get("/snapshots/golden/latest", response_model=GoldenSnapshotResponse)
async def get_latest_golden():
    """Get the most recent golden baseline snapshot"""
    
    snapshot = await snapshot_manager.get_latest_golden()
    
    if not snapshot:
        raise HTTPException(status_code=404, detail="No golden snapshot found")
    
    return {
        "id": snapshot.id,
        "snapshot_type": snapshot.snapshot_type,
        "system_health_score": snapshot.system_health_score,
        "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
        "validated_at": snapshot.validated_at.isoformat() if snapshot.validated_at else None,
        "manifest": snapshot.manifest
    }


# ============= Benchmarks =============

@router.post("/benchmarks/smoke", response_model=VerificationSmokeTestResponse)
async def run_smoke_tests(triggered_by: Optional[str] = None):
    """Run smoke tests"""
    
    result = await benchmark_suite.run_smoke_tests(triggered_by=triggered_by)
    return result


@router.post("/benchmarks/regression", response_model=VerificationRegressionResponse)
async def run_regression_suite(
    triggered_by: Optional[str] = None,
    compare_to_baseline: bool = True
):
    """Run full regression suite"""
    
    result = await benchmark_suite.run_regression_suite(
        triggered_by=triggered_by,
        compare_to_baseline=compare_to_baseline
    )
    return result


@router.get("/benchmarks", response_model=BenchmarkRunListResponse)
async def list_benchmark_runs(limit: int = 20):
    """List recent benchmark runs"""
    
    from ..benchmarks.benchmark_suite import BenchmarkRun
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(BenchmarkRun)
            .order_by(BenchmarkRun.created_at.desc())
            .limit(limit)
        )
        runs = result.scalars().all()
        
        return {
            "runs": [
                {
                    "run_id": r.run_id,
                    "benchmark_type": r.benchmark_type,
                    "passed": r.passed,
                    "drift_detected": r.drift_detected,
                    "is_golden": r.is_golden,
                    "duration_seconds": r.duration_seconds,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "triggered_by": r.triggered_by
                }
                for r in runs
            ]
        }


@router.get("/benchmarks/{run_id}", response_model=BenchmarkRunDetailResponse)
async def get_benchmark_run(run_id: str):
    """Get detailed benchmark run results"""
    
    from ..benchmarks.benchmark_suite import BenchmarkRun
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(BenchmarkRun).where(BenchmarkRun.run_id == run_id)
        )
        run = result.scalar_one_or_none()
        
        if not run:
            raise HTTPException(status_code=404, detail="Benchmark run not found")
        
        return {
            "run_id": run.run_id,
            "benchmark_type": run.benchmark_type,
            "passed": run.passed,
            "drift_detected": run.drift_detected,
            "is_golden": run.is_golden,
            "results": run.results,
            "metrics": run.metrics,
            "baseline_id": run.baseline_id,
            "delta_from_baseline": run.delta_from_baseline,
            "duration_seconds": run.duration_seconds,
            "created_at": run.created_at.isoformat() if run.created_at else None,
            "triggered_by": run.triggered_by
        }


@router.post("/benchmarks/{run_id}/set_golden", response_model=BenchmarkGoldenResponse)
async def set_golden_baseline(run_id: str):
    """Mark a benchmark run as the golden baseline"""
    
    success = await benchmark_suite.set_golden_baseline(run_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Benchmark run not found")
    
    return {"success": True, "run_id": run_id, "status": "golden"}


# ============= Mission Progression =============

@router.post("/missions", response_model=MissionStartResponse)
async def start_mission(
    mission_name: str,
    mission_goal: Optional[str] = None,
    planned_actions: int = 0,
    initial_snapshot_id: Optional[str] = None
):
    """Start tracking a new mission"""
    
    timeline = await progression_tracker.start_mission(
        mission_name=mission_name,
        mission_goal=mission_goal,
        planned_actions=planned_actions,
        initial_snapshot_id=initial_snapshot_id
    )
    
    return {
        "mission_id": timeline.mission_id,
        "mission_name": timeline.mission_name,
        "started_at": timeline.started_at.isoformat() if timeline.started_at else None,
        "planned_actions": timeline.total_planned_actions
    }


@router.get("/missions/current", response_model=VerificationCurrentMissionResponse)
async def get_current_mission():
    """Get current mission status"""
    
    status = await progression_tracker.get_current_status()
    
    if not status:
        raise HTTPException(status_code=404, detail="No active mission")
    
    from dataclasses import asdict
    return asdict(status)


@router.get("/missions/{mission_id}", response_model=VerificationCurrentMissionResponse)
async def get_mission_status(mission_id: str):
    """Get specific mission status"""
    
    status = await progression_tracker.get_current_status(mission_id=mission_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    from dataclasses import asdict
    return asdict(status)


@router.post("/missions/{mission_id}/complete", response_model=MissionCompleteResponse)
async def complete_mission(mission_id: str, success: bool = True):
    """Mark a mission as completed"""
    
    await progression_tracker.complete_mission(mission_id=mission_id, success=success)
    
    return {"mission_id": mission_id, "status": "completed" if success else "failed"}


@router.get("/missions/history", response_model=MissionHistoryResponse)
async def get_mission_history(limit: int = 10):
    """Get recent mission history"""
    
    history = await progression_tracker.get_mission_history(limit=limit)
    return {"missions": history}


# ============= Combined Status =============

@router.get("/status", response_model=VerificationStatusResponseExtended)
async def get_verification_status():
    """
    Get overall verification and progression status.
    Shows Grace where she is, where she came from, and how far to go.
    """
    
    # Get current mission
    mission_status = await progression_tracker.get_current_status()
    
    # Get latest golden snapshot
    golden_snapshot = await snapshot_manager.get_latest_golden()
    
    # Get recent contracts
    from ..action_contract import ActionContract
    from sqlalchemy import select, func
    
    async with async_session() as session:
        # Count contracts by status
        total_contracts = await session.execute(
            select(func.count()).select_from(ActionContract)
        )
        total = total_contracts.scalar() or 0
        
        verified_contracts = await session.execute(
            select(func.count())
            .select_from(ActionContract)
            .where(ActionContract.status == "verified")
        )
        verified = verified_contracts.scalar() or 0
        
        failed_contracts = await session.execute(
            select(func.count())
            .select_from(ActionContract)
            .where(ActionContract.status == "failed")
        )
        failed = failed_contracts.scalar() or 0
    
    return {
        "mission": asdict(mission_status) if mission_status else None,
        "golden_snapshot": {
            "id": golden_snapshot.id,
            "created_at": golden_snapshot.created_at.isoformat() if golden_snapshot.created_at else None,
            "health_score": golden_snapshot.system_health_score
        } if golden_snapshot else None,
        "contracts": {
            "total": total,
            "verified": verified,
            "failed": failed,
            "success_rate": (verified / total * 100) if total > 0 else 0
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
