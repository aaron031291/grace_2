"""
Learning Feedback Loop API
Monitor and control Grace's self-driving learning system
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/learning-feedback",
    tags=["Learning Feedback Loop"]
)


class EventClusterResponse(BaseModel):
    """Response for event cluster"""
    cluster_key: str
    domain: str
    severity: str
    pattern_type: str
    event_count: int
    urgency_score: float
    recurrence_score: float
    first_seen: str
    last_seen: str
    learning_mission_id: Optional[str]
    resolved: bool


class LearningMissionResponse(BaseModel):
    """Response for learning mission"""
    mission_id: str
    mission_type: str
    description: str
    priority: float
    status: str
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]


@router.get("/status")
async def get_feedback_loop_status():
    """
    Get status of the learning feedback loop
    
    Returns:
        Status of triage agent, mission launcher, and event emitters
    """
    try:
        from backend.learning_systems.learning_triage_agent import learning_triage_agent
        from backend.learning_systems.learning_mission_launcher import learning_mission_launcher
        
        triage_stats = learning_triage_agent.get_stats()
        launcher_stats = learning_mission_launcher.get_stats()
        
        return {
            "status": "active" if learning_triage_agent.running else "inactive",
            "triage_agent": triage_stats,
            "mission_launcher": launcher_stats,
            "overall_health": {
                "events_processed": triage_stats.get('events_processed', 0),
                "clusters_active": triage_stats.get('active_clusters', 0),
                "missions_launched": launcher_stats.get('missions_launched', 0),
                "missions_active": launcher_stats.get('active_missions', 0)
            }
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Learning feedback loop not initialized: {e}")


@router.get("/clusters", response_model=List[EventClusterResponse])
async def get_event_clusters(include_resolved: bool = False):
    """
    Get all event clusters
    
    Args:
        include_resolved: Include resolved clusters
        
    Returns:
        List of event clusters
    """
    try:
        from backend.learning_systems.learning_triage_agent import learning_triage_agent
        
        clusters = learning_triage_agent.get_clusters(include_resolved=include_resolved)
        
        return clusters
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Triage agent not initialized: {e}")


@router.get("/clusters/{cluster_key}")
async def get_cluster_details(cluster_key: str):
    """
    Get detailed information about a specific cluster
    
    Args:
        cluster_key: Cluster key (format: domain:severity:pattern)
        
    Returns:
        Cluster details including events
    """
    try:
        from backend.learning_systems.learning_triage_agent import learning_triage_agent
        
        if cluster_key not in learning_triage_agent.clusters:
            raise HTTPException(status_code=404, detail=f"Cluster not found: {cluster_key}")
        
        cluster = learning_triage_agent.clusters[cluster_key]
        
        return {
            "cluster_key": cluster_key,
            "domain": cluster.domain,
            "severity": cluster.severity,
            "pattern_type": cluster.pattern_type,
            "event_count": cluster.event_count,
            "urgency_score": cluster.urgency_score(),
            "recurrence_score": cluster.recurrence_score(),
            "first_seen": cluster.first_seen.isoformat(),
            "last_seen": cluster.last_seen.isoformat(),
            "learning_mission_id": cluster.learning_mission_id,
            "resolved": cluster.resolved,
            "recent_events": cluster.events[-10:]  # Last 10 events
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Triage agent not initialized: {e}")


@router.get("/missions", response_model=List[LearningMissionResponse])
async def get_learning_missions(status: Optional[str] = None):
    """
    Get learning missions
    
    Args:
        status: Filter by status (pending, running, completed, failed)
        
    Returns:
        List of learning missions
    """
    try:
        from backend.learning_systems.learning_mission_launcher import learning_mission_launcher
        
        missions = learning_mission_launcher.get_missions(status=status)
        
        return missions
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Mission launcher not initialized: {e}")


@router.get("/missions/{mission_id}")
async def get_mission_details(mission_id: str):
    """
    Get detailed information about a specific mission
    
    Args:
        mission_id: Mission ID
        
    Returns:
        Mission details
    """
    try:
        from backend.learning_systems.learning_mission_launcher import learning_mission_launcher
        
        if mission_id not in learning_mission_launcher.missions:
            raise HTTPException(status_code=404, detail=f"Mission not found: {mission_id}")
        
        mission = learning_mission_launcher.missions[mission_id]
        
        return mission.to_dict()
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Mission launcher not initialized: {e}")


@router.get("/dashboard")
async def get_learning_dashboard():
    """
    Get comprehensive dashboard of learning feedback loop
    
    Returns:
        Dashboard with stats, top clusters, active missions
    """
    try:
        from backend.learning_systems.learning_triage_agent import learning_triage_agent
        from backend.learning_systems.learning_mission_launcher import learning_mission_launcher
        
        # Get stats
        triage_stats = learning_triage_agent.get_stats()
        launcher_stats = learning_mission_launcher.get_stats()
        
        # Get top clusters by urgency
        all_clusters = learning_triage_agent.get_clusters(include_resolved=False)
        top_clusters = sorted(
            all_clusters,
            key=lambda c: c['urgency_score'],
            reverse=True
        )[:10]
        
        # Get active missions
        active_missions = learning_mission_launcher.get_missions(status='running')
        pending_missions = learning_mission_launcher.get_missions(status='pending')
        
        # Calculate health metrics
        total_events = triage_stats.get('events_processed', 0)
        total_clusters = triage_stats.get('total_clusters', 0)
        active_clusters = triage_stats.get('active_clusters', 0)
        
        cluster_rate = (active_clusters / total_clusters * 100) if total_clusters > 0 else 0
        
        return {
            "overview": {
                "status": "active" if learning_triage_agent.running else "inactive",
                "uptime": "running" if learning_triage_agent.running else "stopped",
                "health_score": 100 - min(100, cluster_rate)  # Lower clusters = better health
            },
            "statistics": {
                "events_processed": total_events,
                "clusters_created": triage_stats.get('clusters_created', 0),
                "active_clusters": active_clusters,
                "missions_launched": launcher_stats.get('missions_launched', 0),
                "missions_completed": launcher_stats.get('missions_completed', 0),
                "missions_failed": launcher_stats.get('missions_failed', 0)
            },
            "current_state": {
                "top_clusters": top_clusters,
                "active_missions": active_missions,
                "pending_missions": pending_missions,
                "subscriptions": len(learning_triage_agent.subscriptions)
            },
            "performance": {
                "events_per_cluster": round(total_events / total_clusters, 2) if total_clusters > 0 else 0,
                "mission_success_rate": round(
                    launcher_stats.get('missions_completed', 0) /
                    max(1, launcher_stats.get('missions_launched', 1)) * 100,
                    2
                ),
                "avg_cluster_urgency": round(
                    sum(c['urgency_score'] for c in all_clusters) / max(1, len(all_clusters)),
                    2
                )
            },
            "last_triage": triage_stats.get('last_triage', None)
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Learning feedback loop not initialized: {e}")


@router.post("/emit-test-event")
async def emit_test_event(
    event_type: str,
    severity: str = "medium",
    domain: str = "test"
):
    """
    Emit a test event to the learning feedback loop
    
    Args:
        event_type: Type of event to emit
        severity: Event severity (low, medium, high, critical)
        domain: Event domain
        
    Returns:
        Confirmation
    """
    try:
        from backend.learning_systems.event_emitters import emit_learning_event
        
        await emit_learning_event(
            event_type,
            {
                "test": True,
                "domain": domain,
                "timestamp": "test"
            },
            severity=severity
        )
        
        return {
            "status": "emitted",
            "event_type": event_type,
            "severity": severity,
            "domain": domain
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Event emitters not initialized: {e}")


@router.post("/clusters/{cluster_key}/resolve")
async def resolve_cluster(cluster_key: str):
    """
    Manually resolve a cluster
    
    Args:
        cluster_key: Cluster to resolve
        
    Returns:
        Confirmation
    """
    try:
        from backend.learning_systems.learning_triage_agent import learning_triage_agent
        
        if cluster_key not in learning_triage_agent.clusters:
            raise HTTPException(status_code=404, detail=f"Cluster not found: {cluster_key}")
        
        cluster = learning_triage_agent.clusters[cluster_key]
        cluster.resolved = True
        
        logger.info(f"[LEARNING-FEEDBACK-API] Cluster resolved manually: {cluster_key}")
        
        return {
            "status": "resolved",
            "cluster_key": cluster_key
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Triage agent not initialized: {e}")
