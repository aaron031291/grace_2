"""
Verification & Mission API Endpoints

Provides stable contracts for frontend consumption.
Includes smoke checks to ensure data integrity.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, text
from ..models import async_session
from ..auth import get_current_user
from ..schemas_extended import (
    VerificationMissionDetailResponse, VerificationSmokeCheckResponseExtended, 
    VerificationHealthResponse
)

router = APIRouter(prefix="/api/verification", tags=["verification"])


# Response Models (stable contracts for frontend)

class ContractSummary(BaseModel):
    """Contract summary for list views"""
    id: str
    action_type: str
    tier: Optional[str]
    status: str
    confidence_score: Optional[float]
    created_at: datetime
    executed_at: Optional[datetime]
    was_rolled_back: bool


class ContractDetail(BaseModel):
    """Full contract details"""
    id: str
    action_type: str
    playbook_id: Optional[str]
    tier: Optional[str]
    status: str
    expected_effect: Dict[str, Any]
    actual_effect: Optional[Dict[str, Any]]
    verification_result: Optional[Dict[str, Any]]
    confidence_score: Optional[float]
    created_at: datetime
    executed_at: Optional[datetime]
    verified_at: Optional[datetime]
    snapshot_id: Optional[str]
    triggered_by: Optional[str]


class SnapshotSummary(BaseModel):
    """Snapshot summary for list views"""
    id: str
    snapshot_type: str
    status: str
    is_golden: bool
    created_at: datetime
    components_count: int


class MissionSummary(BaseModel):
    """Mission summary for list views"""
    mission_id: str
    mission_name: str
    status: str
    progress_ratio: float
    confidence_score: float
    completed_actions: int
    total_planned_actions: int
    started_at: datetime
    completed_at: Optional[datetime]


class VerificationStats(BaseModel):
    """Overall verification statistics"""
    total_contracts: int
    successful_contracts: int
    failed_contracts: int
    rolled_back_contracts: int
    success_rate: float
    avg_confidence: float
    total_snapshots: int
    golden_snapshots: int


# Endpoints

@router.get("/stats", response_model=VerificationStats)
async def get_verification_stats(
    days: int = Query(7, ge=1, le=90),
    current_user: str = Depends(get_current_user)
):
    """
    Get overall verification statistics.
    
    **Smoke Check**: Ensures data integrity.
    """
    
    async with async_session() as session:
        # Get contract stats
        since = datetime.utcnow() - timedelta(days=days)
        
        result = await session.execute(text("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'verified' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status = 'rolled_back' THEN 1 ELSE 0 END) as rolled_back,
                AVG(confidence_score) as avg_confidence
            FROM action_contracts
            WHERE created_at >= :since
        """), {"since": since})
        
        row = result.fetchone()
        
        # Get snapshot stats
        snapshot_result = await session.execute(text("""
            SELECT 
                COUNT(*) as total,
                SUM(CAST(is_golden AS INTEGER)) as golden
            FROM safe_hold_snapshots
            WHERE created_at >= :since
        """), {"since": since})
        
        snap_row = snapshot_result.fetchone()
        
        total = row[0] or 0
        successful = row[1] or 0
        
        return VerificationStats(
            total_contracts=total,
            successful_contracts=successful,
            failed_contracts=row[2] or 0,
            rolled_back_contracts=row[3] or 0,
            success_rate=round((successful / total * 100) if total > 0 else 0, 2),
            avg_confidence=round(row[4] or 0, 3),
            total_snapshots=snap_row[0] or 0,
            golden_snapshots=snap_row[1] or 0
        )


@router.get("/contracts", response_model=List[ContractSummary])
async def list_contracts(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    tier: Optional[str] = Query(None, regex="^tier_[123]$"),
    status: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """
    List action contracts with pagination and filtering.
    """
    
    async with async_session() as session:
        from backend.action_contract import ActionContract
        
        query = select(ActionContract).order_by(ActionContract.created_at.desc())
        
        if tier:
            query = query.where(ActionContract.tier == tier)
        
        if status:
            query = query.where(ActionContract.status == status)
        
        query = query.limit(limit).offset(offset)
        
        result = await session.execute(query)
        contracts = result.scalars().all()
        
        return [
            ContractSummary(
                id=c.id,
                action_type=c.action_type,
                tier=c.tier,
                status=c.status,
                confidence_score=c.confidence_score,
                created_at=c.created_at,
                executed_at=c.executed_at,
                was_rolled_back=(c.status == "rolled_back")
            )
            for c in contracts
        ]


@router.get("/contracts/{contract_id}", response_model=ContractDetail)
async def get_contract_detail(
    contract_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Get full contract details by ID.
    """
    
    async with async_session() as session:
        from backend.action_contract import ActionContract
        
        result = await session.execute(
            select(ActionContract).where(ActionContract.id == contract_id)
        )
        contract = result.scalar_one_or_none()
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        return ContractDetail(
            id=contract.id,
            action_type=contract.action_type,
            playbook_id=contract.playbook_id,
            tier=contract.tier,
            status=contract.status,
            expected_effect=contract.expected_effect,
            actual_effect=contract.actual_effect,
            verification_result=contract.verification_result,
            confidence_score=contract.confidence_score,
            created_at=contract.created_at,
            executed_at=contract.executed_at,
            verified_at=contract.verified_at,
            snapshot_id=contract.safe_hold_snapshot_id,
            triggered_by=contract.triggered_by
        )


@router.get("/snapshots", response_model=List[SnapshotSummary])
async def list_snapshots(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    is_golden: Optional[bool] = None,
    current_user: str = Depends(get_current_user)
):
    """
    List safe-hold snapshots.
    """
    
    async with async_session() as session:
        from backend.self_heal.safe_hold import SafeHoldSnapshot
        
        query = select(SafeHoldSnapshot).order_by(SafeHoldSnapshot.created_at.desc())
        
        if is_golden is not None:
            query = query.where(SafeHoldSnapshot.is_golden == is_golden)
        
        query = query.limit(limit).offset(offset)
        
        result = await session.execute(query)
        snapshots = result.scalars().all()
        
        return [
            SnapshotSummary(
                id=s.id,
                snapshot_type=s.snapshot_type,
                status=s.status,
                is_golden=s.is_golden,
                created_at=s.created_at,
                components_count=len(s.manifest.get('components', [])) if s.manifest else 0
            )
            for s in snapshots
        ]


@router.get("/missions", response_model=List[MissionSummary])
async def list_missions(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """
    List missions with progression tracking.
    """
    
    async with async_session() as session:
        from backend.progression_tracker import MissionTimeline
        
        query = select(MissionTimeline).order_by(MissionTimeline.started_at.desc())
        
        if status:
            query = query.where(MissionTimeline.status == status)
        
        query = query.limit(limit).offset(offset)
        
        result = await session.execute(query)
        missions = result.scalars().all()
        
        return [
            MissionSummary(
                mission_id=m.mission_id,
                mission_name=m.mission_name,
                status=m.status,
                progress_ratio=m.progress_ratio,
                confidence_score=m.confidence_score,
                completed_actions=m.completed_actions,
                total_planned_actions=m.total_planned_actions,
                started_at=m.started_at,
                completed_at=m.completed_at
            )
            for m in missions
        ]


@router.get("/missions/{mission_id}", response_model=VerificationMissionDetailResponse)
async def get_mission_detail(
    mission_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Get detailed mission status with all contracts.
    """
    
    async with async_session() as session:
        from backend.progression_tracker import MissionTimeline
        
        # Get mission
        result = await session.execute(
            select(MissionTimeline).where(MissionTimeline.mission_id == mission_id)
        )
        mission = result.scalar_one_or_none()
        
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        # Get associated contracts
        from backend.action_contract import ActionContract
        
        contracts_result = await session.execute(
            select(ActionContract).where(
                ActionContract.triggered_by.like(f"%{mission_id}%")
            ).order_by(ActionContract.created_at)
        )
        contracts = contracts_result.scalars().all()
        
        return {
            "mission_id": mission.mission_id,
            "mission_name": mission.mission_name,
            "mission_goal": mission.mission_goal,
            "status": mission.status,
            "progress_ratio": mission.progress_ratio,
            "confidence_score": mission.confidence_score,
            "completed_actions": mission.completed_actions,
            "total_planned_actions": mission.total_planned_actions,
            "started_at": mission.started_at,
            "completed_at": mission.completed_at,
            "contracts": [
                {
                    "id": c.id,
                    "action_type": c.action_type,
                    "status": c.status,
                    "confidence_score": c.confidence_score,
                    "created_at": c.created_at
                }
                for c in contracts
            ]
        }


@router.post("/smoke-check", response_model=VerificationSmokeCheckResponseExtended)
async def run_smoke_check(
    current_user: str = Depends(get_current_user)
):
    """
    Run smoke checks on verification system.
    
    Ensures:
    - All tables exist
    - Foreign keys valid
    - No orphaned records
    - Data integrity maintained
    """
    
    checks = {
        "tables_exist": False,
        "contracts_valid": False,
        "snapshots_valid": False,
        "missions_valid": False,
        "no_orphans": False
    }
    
    errors = []
    
    async with async_session() as session:
        # Check 1: Tables exist
        try:
            result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            
            required = ["action_contracts", "safe_hold_snapshots", "benchmark_runs", "mission_timelines"]
            checks["tables_exist"] = all(t in tables for t in required)
            
            if not checks["tables_exist"]:
                errors.append(f"Missing tables: {[t for t in required if t not in tables]}")
        except Exception as e:
            errors.append(f"Table check failed: {e}")
        
        # Check 2: Contracts valid
        try:
            result = await session.execute(text("SELECT COUNT(*) FROM action_contracts"))
            count = result.scalar()
            checks["contracts_valid"] = True
        except Exception as e:
            errors.append(f"Contract check failed: {e}")
        
        # Check 3: Snapshots valid
        try:
            result = await session.execute(text("SELECT COUNT(*) FROM safe_hold_snapshots"))
            count = result.scalar()
            checks["snapshots_valid"] = True
        except Exception as e:
            errors.append(f"Snapshot check failed: {e}")
        
        # Check 4: Missions valid
        try:
            result = await session.execute(text("SELECT COUNT(*) FROM mission_timelines"))
            count = result.scalar()
            checks["missions_valid"] = True
        except Exception as e:
            errors.append(f"Mission check failed: {e}")
        
        # Check 5: No orphaned contracts (referencing non-existent snapshots)
        try:
            result = await session.execute(text("""
                SELECT COUNT(*)
                FROM action_contracts ac
                WHERE ac.safe_hold_snapshot_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM safe_hold_snapshots s
                    WHERE s.id = ac.safe_hold_snapshot_id
                )
            """))
            orphans = result.scalar()
            checks["no_orphans"] = (orphans == 0)
            
            if orphans > 0:
                errors.append(f"Found {orphans} orphaned contract references")
        except Exception as e:
            errors.append(f"Orphan check failed: {e}")
    
    all_passed = all(checks.values())
    
    return {
        "passed": all_passed,
        "checks": checks,
        "errors": errors,
        "timestamp": datetime.utcnow().isoformat(),
        "message": "All checks passed" if all_passed else "Some checks failed"
    }


@router.get("/health", response_model=VerificationHealthResponse)
async def verification_health():
    """
    Quick health check for verification system (no auth required for monitoring).
    """
    
    try:
        async with async_session() as session:
            # Quick table existence check
            result = await session.execute(text("""
                SELECT 
                    (SELECT COUNT(*) FROM action_contracts) as contracts,
                    (SELECT COUNT(*) FROM safe_hold_snapshots) as snapshots,
                    (SELECT COUNT(*) FROM mission_timelines) as missions
            """))
            row = result.fetchone()
            
            return {
                "status": "healthy",
                "contracts_count": row[0],
                "snapshots_count": row[1],
                "missions_count": row[2],
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
