"""
Learning Activity Tracker
Monitors Grace's data absorption, learning progress, and validates knowledge integration
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib


class LearningSource(Enum):
    """Types of learning sources"""
    WEB_SCRAPE = "web_scrape"
    API_FETCH = "api_fetch"
    GITHUB_REPO = "github_repo"
    DOCUMENTATION = "documentation"
    RESEARCH_PAPER = "research_paper"
    CODE_ANALYSIS = "code_analysis"
    CONVERSATION = "conversation"
    FILE_SYSTEM = "file_system"


class LearningStatus(Enum):
    """Status of learning activity"""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    PROCESSING = "processing"
    ABSORBED = "absorbed"
    VALIDATED = "validated"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass
class LearningActivity:
    """Individual learning activity record"""
    activity_id: str
    source_type: str
    source_url: str
    timestamp: str
    status: str
    data_size_bytes: int
    data_hash: str
    content_type: str
    metadata: Dict[str, Any]
    validation_score: float = 0.0
    integration_status: str = "pending"
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


@dataclass
class LearningSession:
    """Learning session tracking multiple activities"""
    session_id: str
    started_at: str
    ended_at: Optional[str]
    target_domain: str
    activities: List[str]  # activity_ids
    total_data_absorbed: int
    validation_score: float
    status: str
    goals: List[str]
    achievements: List[str]


class LearningTracker:
    """
    Tracks all of Grace's learning activities with validation
    """
    
    def __init__(self, storage_dir: str = "logs/learning_activities"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.activities_file = self.storage_dir / "activities.jsonl"
        self.sessions_file = self.storage_dir / "sessions.json"
        self.metrics_file = self.storage_dir / "metrics.json"
        
        self.current_session: Optional[LearningSession] = None
        self.activities_cache: Dict[str, LearningActivity] = {}
        self.sessions_cache: Dict[str, LearningSession] = {}
        
        self._load_state()
    
    def _load_state(self):
        """Load existing state from disk"""
        # Load recent activities
        if self.activities_file.exists():
            with open(self.activities_file, 'r') as f:
                for line in f.readlines()[-1000:]:  # Last 1000 activities
                    if line.strip():
                        try:
                            data = json.loads(line)
                            activity = LearningActivity(**data)
                            self.activities_cache[activity.activity_id] = activity
                        except Exception:
                            pass
        
        # Load sessions
        if self.sessions_file.exists():
            with open(self.sessions_file, 'r') as f:
                sessions_data = json.load(f)
                for session_data in sessions_data:
                    session = LearningSession(**session_data)
                    self.sessions_cache[session.session_id] = session
    
    def start_session(self, target_domain: str, goals: List[str]) -> str:
        """Start a new learning session"""
        session_id = f"learn_{int(time.time())}_{hashlib.md5(target_domain.encode()).hexdigest()[:8]}"
        
        self.current_session = LearningSession(
            session_id=session_id,
            started_at=datetime.utcnow().isoformat(),
            ended_at=None,
            target_domain=target_domain,
            activities=[],
            total_data_absorbed=0,
            validation_score=0.0,
            status="active",
            goals=goals,
            achievements=[]
        )
        
        self.sessions_cache[session_id] = self.current_session
        self._save_sessions()
        
        return session_id
    
    def record_activity(
        self,
        source_type: LearningSource,
        source_url: str,
        data_content: bytes,
        content_type: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Record a learning activity"""
        activity_id = f"act_{int(time.time())}_{hashlib.md5(source_url.encode()).hexdigest()[:8]}"
        
        data_hash = hashlib.sha256(data_content).hexdigest()
        
        activity = LearningActivity(
            activity_id=activity_id,
            source_type=source_type.value,
            source_url=source_url,
            timestamp=datetime.utcnow().isoformat(),
            status=LearningStatus.IN_PROGRESS.value,
            data_size_bytes=len(data_content),
            data_hash=data_hash,
            content_type=content_type,
            metadata=metadata or {},
            validation_score=0.0,
            integration_status="pending"
        )
        
        self.activities_cache[activity_id] = activity
        
        # Add to current session if active
        if self.current_session:
            self.current_session.activities.append(activity_id)
            self.current_session.total_data_absorbed += len(data_content)
        
        self._save_activity(activity)
        return activity_id
    
    def update_activity_status(
        self,
        activity_id: str,
        status: LearningStatus,
        validation_score: float = None,
        integration_status: str = None,
        error: str = None
    ):
        """Update the status of a learning activity"""
        if activity_id not in self.activities_cache:
            raise ValueError(f"Activity {activity_id} not found")
        
        activity = self.activities_cache[activity_id]
        activity.status = status.value
        
        if validation_score is not None:
            activity.validation_score = validation_score
        
        if integration_status is not None:
            activity.integration_status = integration_status
        
        if error:
            activity.errors.append(error)
        
        self._save_activity(activity)
    
    def validate_learning(self, activity_id: str) -> Dict[str, Any]:
        """
        Validate that data was properly absorbed and integrated
        Returns validation report
        """
        if activity_id not in self.activities_cache:
            raise ValueError(f"Activity {activity_id} not found")
        
        activity = self.activities_cache[activity_id]
        
        # Validation checks
        validation_results = {
            "activity_id": activity_id,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        # 1. Data integrity check
        validation_results["checks"]["data_integrity"] = {
            "passed": bool(activity.data_hash),
            "score": 1.0 if activity.data_hash else 0.0,
            "details": f"Data hash: {activity.data_hash[:16]}..."
        }
        
        # 2. Size validation
        size_valid = activity.data_size_bytes > 0
        validation_results["checks"]["size_validation"] = {
            "passed": size_valid,
            "score": 1.0 if size_valid else 0.0,
            "details": f"Data size: {activity.data_size_bytes} bytes"
        }
        
        # 3. Source verification
        source_valid = activity.source_url and activity.source_type
        validation_results["checks"]["source_verification"] = {
            "passed": source_valid,
            "score": 1.0 if source_valid else 0.0,
            "details": f"Source: {activity.source_type} from {activity.source_url[:50]}"
        }
        
        # 4. Status check
        status_valid = activity.status != LearningStatus.FAILED.value
        validation_results["checks"]["status_check"] = {
            "passed": status_valid,
            "score": 1.0 if status_valid else 0.0,
            "details": f"Status: {activity.status}"
        }
        
        # Calculate overall validation score
        total_score = sum(check["score"] for check in validation_results["checks"].values())
        max_score = len(validation_results["checks"])
        validation_score = total_score / max_score if max_score > 0 else 0.0
        
        validation_results["overall_score"] = validation_score
        validation_results["passed"] = validation_score >= 0.8
        
        # Update activity
        self.update_activity_status(
            activity_id,
            LearningStatus.VALIDATED if validation_results["passed"] else LearningStatus.FAILED,
            validation_score=validation_score,
            integration_status="validated" if validation_results["passed"] else "failed"
        )
        
        return validation_results
    
    def end_session(self) -> Dict[str, Any]:
        """End the current learning session and generate report"""
        if not self.current_session:
            raise ValueError("No active session")
        
        session = self.current_session
        session.ended_at = datetime.utcnow().isoformat()
        session.status = "completed"
        
        # Calculate session validation score
        if session.activities:
            total_validation = sum(
                self.activities_cache[aid].validation_score 
                for aid in session.activities 
                if aid in self.activities_cache
            )
            session.validation_score = total_validation / len(session.activities)
        
        # Generate achievements based on goals
        for goal in session.goals:
            if "absorbed" in goal.lower() and session.total_data_absorbed > 0:
                session.achievements.append(f"Absorbed {session.total_data_absorbed} bytes of data")
            if "validated" in goal.lower() and session.validation_score > 0.8:
                session.achievements.append(f"Achieved {session.validation_score:.1%} validation score")
        
        self._save_sessions()
        
        report = {
            "session_id": session.session_id,
            "duration_seconds": (
                datetime.fromisoformat(session.ended_at) - 
                datetime.fromisoformat(session.started_at)
            ).total_seconds(),
            "activities_count": len(session.activities),
            "data_absorbed": session.total_data_absorbed,
            "validation_score": session.validation_score,
            "goals": session.goals,
            "achievements": session.achievements,
            "status": session.status
        }
        
        self.current_session = None
        return report
    
    def get_realtime_status(self) -> Dict[str, Any]:
        """Get real-time learning status for dashboard"""
        recent_activities = sorted(
            self.activities_cache.values(),
            key=lambda a: a.timestamp,
            reverse=True
        )[:20]
        
        # Calculate metrics
        total_activities = len(self.activities_cache)
        validated_activities = sum(
            1 for a in self.activities_cache.values()
            if a.status == LearningStatus.VALIDATED.value
        )
        
        total_data = sum(a.data_size_bytes for a in self.activities_cache.values())
        
        # Source breakdown
        source_counts = {}
        for activity in self.activities_cache.values():
            source_counts[activity.source_type] = source_counts.get(activity.source_type, 0) + 1
        
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "active_session": asdict(self.current_session) if self.current_session else None,
            "total_activities": total_activities,
            "validated_activities": validated_activities,
            "validation_rate": validated_activities / total_activities if total_activities > 0 else 0,
            "total_data_absorbed_bytes": total_data,
            "total_data_absorbed_mb": round(total_data / (1024 * 1024), 2),
            "source_breakdown": source_counts,
            "recent_activities": [
                {
                    "activity_id": a.activity_id,
                    "source_type": a.source_type,
                    "source_url": a.source_url[:60] + "..." if len(a.source_url) > 60 else a.source_url,
                    "timestamp": a.timestamp,
                    "status": a.status,
                    "size_kb": round(a.data_size_bytes / 1024, 2),
                    "validation_score": a.validation_score
                }
                for a in recent_activities
            ],
            "sessions_count": len(self.sessions_cache),
            "current_learning_rate": self._calculate_learning_rate()
        }
        
        return status
    
    def _calculate_learning_rate(self) -> Dict[str, float]:
        """Calculate learning rate over different time windows"""
        now = datetime.utcnow()
        
        def count_in_window(minutes: int) -> int:
            cutoff = now - timedelta(minutes=minutes)
            return sum(
                1 for a in self.activities_cache.values()
                if datetime.fromisoformat(a.timestamp) > cutoff
            )
        
        return {
            "last_5_min": count_in_window(5),
            "last_15_min": count_in_window(15),
            "last_hour": count_in_window(60),
            "last_24h": count_in_window(1440)
        }
    
    def get_learning_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive learning analytics"""
        activities = list(self.activities_cache.values())
        
        if not activities:
            return {"message": "No learning activities recorded yet"}
        
        # Time-based analysis
        earliest = min(datetime.fromisoformat(a.timestamp) for a in activities)
        latest = max(datetime.fromisoformat(a.timestamp) for a in activities)
        total_duration = (latest - earliest).total_seconds()
        
        # Success metrics
        validated = [a for a in activities if a.status == LearningStatus.VALIDATED.value]
        failed = [a for a in activities if a.status == LearningStatus.FAILED.value]
        
        # Data volume analysis
        total_data = sum(a.data_size_bytes for a in activities)
        avg_data_per_activity = total_data / len(activities)
        
        # Source performance
        source_performance = {}
        for source_type in set(a.source_type for a in activities):
            source_activities = [a for a in activities if a.source_type == source_type]
            source_validated = [a for a in source_activities if a.status == LearningStatus.VALIDATED.value]
            
            source_performance[source_type] = {
                "total": len(source_activities),
                "validated": len(source_validated),
                "success_rate": len(source_validated) / len(source_activities) if source_activities else 0,
                "total_data_mb": round(sum(a.data_size_bytes for a in source_activities) / (1024 * 1024), 2)
            }
        
        analytics = {
            "period": {
                "start": earliest.isoformat(),
                "end": latest.isoformat(),
                "duration_hours": round(total_duration / 3600, 2)
            },
            "activities": {
                "total": len(activities),
                "validated": len(validated),
                "failed": len(failed),
                "in_progress": len(activities) - len(validated) - len(failed),
                "success_rate": len(validated) / len(activities)
            },
            "data_volume": {
                "total_bytes": total_data,
                "total_mb": round(total_data / (1024 * 1024), 2),
                "total_gb": round(total_data / (1024 * 1024 * 1024), 3),
                "avg_per_activity_kb": round(avg_data_per_activity / 1024, 2)
            },
            "source_performance": source_performance,
            "average_validation_score": sum(a.validation_score for a in validated) / len(validated) if validated else 0,
            "learning_velocity": {
                "activities_per_hour": len(activities) / (total_duration / 3600) if total_duration > 0 else 0,
                "mb_per_hour": (total_data / (1024 * 1024)) / (total_duration / 3600) if total_duration > 0 else 0
            },
            "sessions": {
                "total": len(self.sessions_cache),
                "avg_activities_per_session": len(activities) / len(self.sessions_cache) if self.sessions_cache else 0
            }
        }
        
        return analytics
    
    def _save_activity(self, activity: LearningActivity):
        """Append activity to JSONL file"""
        with open(self.activities_file, 'a') as f:
            f.write(json.dumps(asdict(activity)) + '\n')
    
    def _save_sessions(self):
        """Save all sessions to JSON file"""
        sessions_data = [asdict(s) for s in self.sessions_cache.values()]
        with open(self.sessions_file, 'w') as f:
            json.dump(sessions_data, f, indent=2)
    
    def get_activity(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific activity by ID"""
        if activity_id in self.activities_cache:
            return asdict(self.activities_cache[activity_id])
        return None
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific session by ID"""
        if session_id in self.sessions_cache:
            return asdict(self.sessions_cache[session_id])
        return None


# Global instance
_tracker = None

def get_learning_tracker() -> LearningTracker:
    """Get or create the global learning tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = LearningTracker()
    return _tracker