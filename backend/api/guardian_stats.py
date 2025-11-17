"""
Guardian Stats API - Phase 1
Expose Guardian healing statistics and metrics
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/guardian", tags=["guardian"])


class HealingRun(BaseModel):
    """Single healing run record"""
    run_id: str
    timestamp: str
    playbook_id: str
    playbook_name: str
    status: str
    duration_seconds: float
    actions_taken: List[str]
    success: bool
    error: Optional[str] = None


class GuardianStats(BaseModel):
    """Guardian healing statistics"""
    total_runs: int = Field(..., description="Total healing runs")
    successful_runs: int = Field(..., description="Successful healing runs")
    failed_runs: int = Field(..., description="Failed healing runs")
    success_rate: float = Field(..., description="Success rate percentage")
    mttr_seconds: float = Field(..., description="Mean Time To Recovery in seconds")
    mttr_minutes: float = Field(..., description="Mean Time To Recovery in minutes")
    last_5_runs: List[HealingRun] = Field(..., description="Last 5 healing runs")
    playbook_stats: Dict[str, Any] = Field(..., description="Per-playbook statistics")
    layer_health: Optional[Dict[str, Any]] = Field(None, description="OSI layer health status")


class PlaybookInfo(BaseModel):
    """Playbook information"""
    playbook_id: str
    name: str
    description: str
    priority: int
    executions: int
    successes: int
    failures: int
    success_rate: float
    last_executed: Optional[str]


class PlaybookListResponse(BaseModel):
    """List of all playbooks"""
    total: int
    playbooks: List[PlaybookInfo]


@router.get("/healer/stats", response_model=GuardianStats)
async def get_guardian_stats():
    """
    Get Guardian healing statistics
    
    Returns:
    - Total healing runs
    - Success/failure counts
    - Success rate
    - MTTR (Mean Time To Recovery)
    - Last 5 healing runs
    - Per-playbook statistics
    """
    from backend.core.guardian_playbooks import GuardianPlaybookRegistry
    
    registry = GuardianPlaybookRegistry()
    playbooks = registry.playbooks
    
    # Calculate aggregate stats
    total_executions = sum(pb.executions for pb in playbooks.values())
    total_successes = sum(pb.successes for pb in playbooks.values())
    total_failures = sum(pb.failures for pb in playbooks.values())
    
    success_rate = (total_successes / total_executions * 100) if total_executions > 0 else 0
    
    # Mock MTTR calculation (would need real incident data)
    # For now, use a placeholder based on average remediation time
    mttr_seconds = 45.0  # Placeholder: 45 seconds average
    mttr_minutes = mttr_seconds / 60
    
    # Get last 5 runs (mock data for now - would come from incident log)
    last_5_runs = []
    for i, (playbook_id, playbook) in enumerate(list(playbooks.items())[:5]):
        if playbook.last_executed:
            last_5_runs.append(HealingRun(
                run_id=f"run_{i+1}",
                timestamp=playbook.last_executed,
                playbook_id=playbook_id,
                playbook_name=playbook.name,
                status="success" if playbook.successes > 0 else "pending",
                duration_seconds=mttr_seconds,
                actions_taken=["Executed remediation"],
                success=playbook.successes > 0,
                error=None
            ))
    
    # Per-playbook statistics
    playbook_stats = {}
    for playbook_id, playbook in playbooks.items():
        playbook_stats[playbook_id] = {
            "name": playbook.name,
            "executions": playbook.executions,
            "successes": playbook.successes,
            "failures": playbook.failures,
            "success_rate": (playbook.successes / playbook.executions * 100) if playbook.executions > 0 else 0,
            "last_executed": playbook.last_executed
        }
    
    # Get OSI layer health (if available)
    layer_health = None
    try:
        from backend.guardian.osi_canary_probes import osi_canary_probes
        layer_health = osi_canary_probes.get_health_summary()
    except Exception as e:
        layer_health = {"error": str(e)}
    
    return GuardianStats(
        total_runs=total_executions,
        successful_runs=total_successes,
        failed_runs=total_failures,
        success_rate=success_rate,
        mttr_seconds=mttr_seconds,
        mttr_minutes=mttr_minutes,
        last_5_runs=last_5_runs,
        playbook_stats=playbook_stats,
        layer_health=layer_health
    )


@router.get("/playbooks", response_model=PlaybookListResponse)
async def list_playbooks():
    """
    List all registered Guardian playbooks
    
    Returns:
    - Total playbook count
    - List of all playbooks with their statistics
    """
    from backend.core.guardian_playbooks import GuardianPlaybookRegistry
    
    registry = GuardianPlaybookRegistry()
    playbooks = registry.playbooks
    
    playbook_list = []
    for playbook_id, playbook in playbooks.items():
        success_rate = (playbook.successes / playbook.executions * 100) if playbook.executions > 0 else 0
        
        playbook_list.append(PlaybookInfo(
            playbook_id=playbook_id,
            name=playbook.name,
            description=playbook.description,
            priority=playbook.priority,
            executions=playbook.executions,
            successes=playbook.successes,
            failures=playbook.failures,
            success_rate=success_rate,
            last_executed=playbook.last_executed
        ))
    
    # Sort by priority (highest first)
    playbook_list.sort(key=lambda x: x.priority, reverse=True)
    
    return PlaybookListResponse(
        total=len(playbook_list),
        playbooks=playbook_list
    )


@router.get("/osi/probe")
async def probe_osi_layers():
    """
    Probe all OSI network layers (2-7)
    
    Returns health status for each layer
    """
    from backend.guardian.osi_canary_probes import osi_canary_probes
    
    results = await osi_canary_probes.probe_all_layers()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "layers": {
            layer.name: result.to_dict()
            for layer, result in results.items()
        },
        "summary": osi_canary_probes.get_health_summary()
    }


@router.get("/health")
async def guardian_health():
    """
    Get overall Guardian health status
    
    Returns:
    - Playbook count
    - Active healing runs
    - Recent success rate
    - OSI layer health
    """
    from backend.core.guardian_playbooks import GuardianPlaybookRegistry
    from backend.guardian.osi_canary_probes import osi_canary_probes
    
    registry = GuardianPlaybookRegistry()
    playbooks = registry.playbooks
    
    total_executions = sum(pb.executions for pb in playbooks.values())
    total_successes = sum(pb.successes for pb in playbooks.values())
    
    success_rate = (total_successes / total_executions * 100) if total_executions > 0 else 0
    
    # Get OSI layer health
    layer_summary = osi_canary_probes.get_health_summary()
    
    return {
        "status": "healthy" if success_rate > 80 else "degraded",
        "playbook_count": len(playbooks),
        "total_healing_runs": total_executions,
        "success_rate": success_rate,
        "osi_layer_health": layer_summary,
        "timestamp": datetime.utcnow().isoformat()
    }
