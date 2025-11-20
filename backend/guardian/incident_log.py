"""
Guardian Incident Log - Real MTTR Tracking
Track healing incidents with timestamps for accurate MTTR calculation
Integrated with unified task registry
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

# Import task registry for integration
try:
    from backend.services.task_registry import task_registry
    TASK_REGISTRY_AVAILABLE = True
except ImportError:
    TASK_REGISTRY_AVAILABLE = False
    logger.warning("[INCIDENT-LOG] Task registry not available")


class IncidentStatus(Enum):
    """Incident lifecycle status"""
    DETECTED = "detected"
    REMEDIATING = "remediating"
    RESOLVED = "resolved"
    FAILED = "failed"


@dataclass
class HealingIncident:
    """Single healing incident record"""
    incident_id: str
    detected_at: str
    resolved_at: Optional[str] = None
    status: str = IncidentStatus.DETECTED.value
    playbook_id: Optional[str] = None
    playbook_name: Optional[str] = None
    failure_mode: str = ""
    severity: str = "medium"  # low, medium, high, critical
    mttr_seconds: Optional[float] = None
    actions_taken: List[str] = None
    success: bool = False
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.actions_taken is None:
            self.actions_taken = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def mark_resolved(self, success: bool = True, error: Optional[str] = None):
        """Mark incident as resolved and calculate MTTR"""
        self.resolved_at = datetime.utcnow().isoformat()
        self.status = IncidentStatus.RESOLVED.value if success else IncidentStatus.FAILED.value
        self.success = success
        self.error = error
        
        # Calculate MTTR
        detected = datetime.fromisoformat(self.detected_at.replace('Z', '+00:00'))
        resolved = datetime.fromisoformat(self.resolved_at.replace('Z', '+00:00'))
        self.mttr_seconds = (resolved - detected).total_seconds()


class IncidentLog:
    """
    Persistent log of all healing incidents for MTTR tracking
    """
    
    def __init__(self, log_file: str = "logs/incidents.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache of recent incidents
        self.recent_incidents: List[HealingIncident] = []
        self.max_cache = 100
        
        # Load recent incidents
        self._load_recent_incidents()
    
    def _load_recent_incidents(self):
        """Load recent incidents from log file"""
        if not self.log_file.exists():
            return
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                # Get last 100 lines
                for line in lines[-self.max_cache:]:
                    try:
                        data = json.loads(line)
                        incident = HealingIncident(**data)
                        self.recent_incidents.append(incident)
                    except Exception as e:
                        logger.warning(f"[INCIDENT-LOG] Failed to parse incident: {e}")
        
        except Exception as e:
            logger.error(f"[INCIDENT-LOG] Failed to load incidents: {e}")
    
    async def log_incident(self, incident: HealingIncident):
        """
        Log a new incident and register with task registry
        """
        try:
            # Append to file
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(incident.to_dict()) + '\n')
            
            # Add to cache
            self.recent_incidents.append(incident)
            if len(self.recent_incidents) > self.max_cache:
                self.recent_incidents = self.recent_incidents[-self.max_cache:]
            
            logger.info(f"[INCIDENT-LOG] Logged incident: {incident.incident_id} ({incident.failure_mode})")
            
            # Register with unified task registry
            if TASK_REGISTRY_AVAILABLE:
                await self._register_with_task_registry(incident)
        
        except Exception as e:
            logger.error(f"[INCIDENT-LOG] Failed to log incident: {e}")
    
    async def _register_with_task_registry(self, incident: HealingIncident):
        """Register incident as task in unified registry"""
        try:
            task_data = {
                "task_id": incident.incident_id,
                "task_type": "healing_incident",
                "subsystem": "self_healing",
                "title": f"{incident.severity.upper()}: {incident.failure_mode}",
                "description": f"Playbook: {incident.playbook_name or 'N/A'}",
                "created_by": "guardian",
                "priority": self._severity_to_priority(incident.severity),
                "task_metadata": {
                    "failure_mode": incident.failure_mode,
                    "playbook_id": incident.playbook_id,
                    "playbook_name": incident.playbook_name,
                    **incident.metadata
                }
            }
            
            # Register the task
            await task_registry.register_task(**task_data)
            
            # If already resolved, complete it immediately
            if incident.status == IncidentStatus.RESOLVED.value and incident.resolved_at:
                await task_registry.complete_task(
                    task_id=incident.incident_id,
                    success=incident.success,
                    result={
                        "actions_taken": incident.actions_taken,
                        "mttr_seconds": incident.mttr_seconds,
                        "error": incident.error
                    }
                )
            
            logger.info(f"[INCIDENT-LOG] Registered {incident.incident_id} with task registry")
        except Exception as e:
            logger.warning(f"[INCIDENT-LOG] Failed to register with task registry: {e}")
    
    def _severity_to_priority(self, severity: str) -> int:
        """Convert severity to task priority (1-10)"""
        severity_map = {
            "critical": 10,
            "high": 8,
            "medium": 5,
            "low": 2
        }
        return severity_map.get(severity.lower(), 5)
    
    def create_incident(
        self,
        failure_mode: str,
        severity: str = "medium",
        playbook_id: Optional[str] = None,
        playbook_name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> HealingIncident:
        """
        Create and log a new incident
        
        Returns the incident object for tracking
        """
        incident_id = f"inc_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        incident = HealingIncident(
            incident_id=incident_id,
            detected_at=datetime.utcnow().isoformat(),
            failure_mode=failure_mode,
            severity=severity,
            playbook_id=playbook_id,
            playbook_name=playbook_name,
            metadata=metadata or {}
        )
        
        self.log_incident(incident)
        return incident
    
    async def update_incident(self, incident: HealingIncident):
        """
        Update an existing incident (e.g., mark resolved)
        """
        await self.log_incident(incident)  # Append updated version
    
    def get_recent_incidents(self, limit: int = 10) -> List[HealingIncident]:
        """Get most recent incidents"""
        return self.recent_incidents[-limit:]
    
    def get_incidents_by_playbook(self, playbook_id: str, limit: int = 10) -> List[HealingIncident]:
        """Get incidents for a specific playbook"""
        return [
            inc for inc in self.recent_incidents
            if inc.playbook_id == playbook_id
        ][-limit:]
    
    def calculate_mttr(self, hours: int = 24) -> Dict[str, Any]:
        """
        Calculate MTTR for resolved incidents in the last N hours
        
        Returns:
        - mttr_seconds: Mean time to recovery in seconds
        - mttr_minutes: MTTR in minutes
        - incident_count: Number of incidents included
        - success_rate: Percentage of successful recoveries
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        resolved_incidents = [
            inc for inc in self.recent_incidents
            if inc.resolved_at and datetime.fromisoformat(inc.detected_at.replace('Z', '+00:00')) >= cutoff
        ]
        
        if not resolved_incidents:
            return {
                "mttr_seconds": 0,
                "mttr_minutes": 0,
                "incident_count": 0,
                "success_rate": 0,
                "period_hours": hours
            }
        
        # Calculate average MTTR
        total_mttr = sum(inc.mttr_seconds for inc in resolved_incidents if inc.mttr_seconds)
        avg_mttr = total_mttr / len(resolved_incidents)
        
        # Calculate success rate
        successful = sum(1 for inc in resolved_incidents if inc.success)
        success_rate = (successful / len(resolved_incidents)) * 100
        
        return {
            "mttr_seconds": avg_mttr,
            "mttr_minutes": avg_mttr / 60,
            "incident_count": len(resolved_incidents),
            "success_rate": success_rate,
            "period_hours": hours,
            "successful_recoveries": successful,
            "failed_recoveries": len(resolved_incidents) - successful
        }
    
    def get_stats_by_failure_mode(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics grouped by failure mode
        """
        stats = {}
        
        for incident in self.recent_incidents:
            mode = incident.failure_mode
            if mode not in stats:
                stats[mode] = {
                    "count": 0,
                    "successes": 0,
                    "failures": 0,
                    "total_mttr": 0,
                    "incidents": []
                }
            
            stats[mode]["count"] += 1
            stats[mode]["incidents"].append(incident.incident_id)
            
            if incident.resolved_at:
                if incident.success:
                    stats[mode]["successes"] += 1
                else:
                    stats[mode]["failures"] += 1
                
                if incident.mttr_seconds:
                    stats[mode]["total_mttr"] += incident.mttr_seconds
        
        # Calculate averages
        for mode, data in stats.items():
            resolved = data["successes"] + data["failures"]
            if resolved > 0:
                data["avg_mttr_seconds"] = data["total_mttr"] / resolved
                data["avg_mttr_minutes"] = data["avg_mttr_seconds"] / 60
                data["success_rate"] = (data["successes"] / resolved) * 100
            else:
                data["avg_mttr_seconds"] = 0
                data["avg_mttr_minutes"] = 0
                data["success_rate"] = 0
            
            # Clean up
            del data["total_mttr"]
        
        return stats
    
    def get_top_failure_modes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get top N most common failure modes
        """
        stats = self.get_stats_by_failure_mode()
        
        # Sort by count
        sorted_modes = sorted(
            [{"mode": k, **v} for k, v in stats.items()],
            key=lambda x: x["count"],
            reverse=True
        )
        
        return sorted_modes[:limit]


# Global instance
incident_log = IncidentLog()
