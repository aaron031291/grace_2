"""
MTTR (Mean Time To Recovery) Tracker
Tracks healing actions from detection to resolution
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import asyncio
from collections import defaultdict, deque
import statistics

@dataclass
class HealingAction:
    """Record of a healing action"""
    action_id: str
    issue_type: str
    component: str
    detected_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    playbook_used: Optional[str] = None
    success: bool = False
    error_message: Optional[str] = None
    recovery_time_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict with ISO timestamps"""
        d = asdict(self)
        d['detected_at'] = self.detected_at.isoformat() if self.detected_at else None
        d['started_at'] = self.started_at.isoformat() if self.started_at else None
        d['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        d['failed_at'] = self.failed_at.isoformat() if self.failed_at else None
        return d

class MTTRTracker:
    """Tracks Mean Time To Recovery for healing actions"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.active_actions: Dict[str, HealingAction] = {}
        self.completed_actions: deque = deque(maxlen=window_size)
        self.mttr_by_issue_type: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))
        self.mttr_by_playbook: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))
        
    def start_action(
        self,
        action_id: str,
        issue_type: str,
        component: str,
        playbook: Optional[str] = None
    ) -> HealingAction:
        """Start tracking a healing action"""
        now = datetime.now()
        
        action = HealingAction(
            action_id=action_id,
            issue_type=issue_type,
            component=component,
            detected_at=now,
            started_at=now,
            playbook_used=playbook
        )
        
        self.active_actions[action_id] = action
        return action
    
    def complete_action(
        self,
        action_id: str,
        success: bool,
        error_message: Optional[str] = None
    ) -> Optional[HealingAction]:
        """Mark action as completed"""
        action = self.active_actions.get(action_id)
        
        if not action:
            return None
        
        now = datetime.now()
        action.success = success
        action.error_message = error_message
        
        if success:
            action.completed_at = now
            action.recovery_time_seconds = (now - action.detected_at).total_seconds()
        else:
            action.failed_at = now
            action.recovery_time_seconds = None
        
        # Move to completed and track MTTR
        self.completed_actions.append(action)
        del self.active_actions[action_id]
        
        if success and action.recovery_time_seconds:
            self.mttr_by_issue_type[action.issue_type].append(action.recovery_time_seconds)
            
            if action.playbook_used:
                self.mttr_by_playbook[action.playbook_used].append(action.recovery_time_seconds)
        
        return action
    
    def get_mttr_overall(self) -> Optional[float]:
        """Get overall MTTR in seconds"""
        successful = [
            a.recovery_time_seconds 
            for a in self.completed_actions 
            if a.success and a.recovery_time_seconds
        ]
        
        return statistics.mean(successful) if successful else None
    
    def get_mttr_by_issue_type(self, issue_type: str) -> Optional[float]:
        """Get MTTR for specific issue type"""
        times = self.mttr_by_issue_type.get(issue_type, [])
        return statistics.mean(times) if times else None
    
    def get_mttr_by_playbook(self, playbook: str) -> Optional[float]:
        """Get MTTR for specific playbook"""
        times = self.mttr_by_playbook.get(playbook, [])
        return statistics.mean(times) if times else None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive MTTR statistics"""
        total_actions = len(self.completed_actions)
        successful = sum(1 for a in self.completed_actions if a.success)
        failed = total_actions - successful
        
        success_rate = (successful / total_actions * 100) if total_actions > 0 else 0
        
        mttr_overall = self.get_mttr_overall()
        
        # Calculate percentiles if we have data
        successful_times = [
            a.recovery_time_seconds 
            for a in self.completed_actions 
            if a.success and a.recovery_time_seconds
        ]
        
        percentiles = {}
        if successful_times:
            sorted_times = sorted(successful_times)
            percentiles = {
                "p50": sorted_times[len(sorted_times) // 2],
                "p95": sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 1 else sorted_times[0],
                "p99": sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 1 else sorted_times[0],
            }
        
        # MTTR by issue type
        mttr_by_type = {
            issue_type: {
                "mttr_seconds": statistics.mean(times),
                "sample_count": len(times)
            }
            for issue_type, times in self.mttr_by_issue_type.items()
            if times
        }
        
        # MTTR by playbook
        mttr_by_playbook = {
            playbook: {
                "mttr_seconds": statistics.mean(times),
                "sample_count": len(times)
            }
            for playbook, times in self.mttr_by_playbook.items()
            if times
        }
        
        return {
            "total_actions": total_actions,
            "successful": successful,
            "failed": failed,
            "success_rate_percent": success_rate,
            "mttr_seconds": mttr_overall,
            "mttr_minutes": mttr_overall / 60 if mttr_overall else None,
            "percentiles": percentiles,
            "active_actions_count": len(self.active_actions),
            "mttr_by_issue_type": mttr_by_type,
            "mttr_by_playbook": mttr_by_playbook,
            "recent_actions": [
                a.to_dict() for a in list(self.completed_actions)[-10:]
            ]
        }
    
    def get_recent_failures(self, limit: int = 10) -> List[HealingAction]:
        """Get recent failed actions"""
        failures = [a for a in self.completed_actions if not a.success]
        return list(failures)[-limit:]
    
    def get_slow_actions(self, threshold_seconds: float = 120) -> List[HealingAction]:
        """Get actions that exceeded recovery time threshold"""
        slow = [
            a for a in self.completed_actions 
            if a.success and a.recovery_time_seconds and a.recovery_time_seconds > threshold_seconds
        ]
        return slow

# Global MTTR tracker instance
_mttr_tracker: Optional[MTTRTracker] = None

def get_mttr_tracker() -> MTTRTracker:
    """Get global MTTR tracker instance"""
    global _mttr_tracker
    if _mttr_tracker is None:
        _mttr_tracker = MTTRTracker()
    return _mttr_tracker

# Convenience functions
async def track_healing_action(
    action_id: str,
    issue_type: str,
    component: str,
    playbook: Optional[str] = None
) -> HealingAction:
    """Start tracking a healing action"""
    tracker = get_mttr_tracker()
    return tracker.start_action(action_id, issue_type, component, playbook)

async def complete_healing_action(
    action_id: str,
    success: bool,
    error_message: Optional[str] = None
) -> Optional[HealingAction]:
    """Complete a healing action"""
    tracker = get_mttr_tracker()
    return tracker.complete_action(action_id, success, error_message)

def get_mttr_stats() -> Dict[str, Any]:
    """Get current MTTR statistics"""
    tracker = get_mttr_tracker()
    return tracker.get_stats()
