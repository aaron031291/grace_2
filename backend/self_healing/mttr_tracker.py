"""
MTTR (Mean Time To Recovery) Tracker
Tracks remediation times and calculates MTTR metrics
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import logging

from backend.self_healing.failure_detector import FailureMode

logger = logging.getLogger(__name__)

@dataclass
class RemediationEvent:
    """A single remediation event"""
    failure_mode: str
    timestamp: str
    duration_seconds: float
    success: bool
    actions: List[str]
    
class MTTRTracker:
    """Tracks Mean Time To Recovery for all failure modes"""
    
    def __init__(self, history_file: Optional[Path] = None):
        self.history_file = history_file or Path("reports/mttr_history.json")
        self.events: List[RemediationEvent] = []
        self.load_history()
        
    def load_history(self):
        """Load historical remediation events"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.events = [RemediationEvent(**e) for e in data.get('events', [])]
                logger.info(f"Loaded {len(self.events)} historical remediation events")
            except Exception as e:
                logger.warning(f"Failed to load MTTR history: {e}")
    
    def save_history(self):
        """Save remediation history to disk"""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w') as f:
                json.dump({
                    'events': [asdict(e) for e in self.events],
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save MTTR history: {e}")
    
    def record_remediation(
        self,
        failure_mode: FailureMode,
        duration_seconds: float,
        success: bool,
        actions: List[str]
    ):
        """Record a remediation event"""
        event = RemediationEvent(
            failure_mode=failure_mode.value,
            timestamp=datetime.now().isoformat(),
            duration_seconds=duration_seconds,
            success=success,
            actions=actions
        )
        
        self.events.append(event)
        self.save_history()
        
        logger.info(
            f"Recorded remediation: {failure_mode.value} "
            f"({'success' if success else 'failed'}) in {duration_seconds:.2f}s"
        )
    
    def get_mttr(
        self,
        failure_mode: Optional[FailureMode] = None,
        time_window_days: Optional[int] = None
    ) -> float:
        """
        Calculate Mean Time To Recovery
        
        Args:
            failure_mode: Specific failure mode (None for all)
            time_window_days: Only consider events in last N days (None for all time)
        
        Returns:
            MTTR in seconds
        """
        events = self.events
        
        if failure_mode:
            events = [e for e in events if e.failure_mode == failure_mode.value]
        
        if time_window_days:
            cutoff = datetime.now() - timedelta(days=time_window_days)
            events = [
                e for e in events
                if datetime.fromisoformat(e.timestamp) > cutoff
            ]
        
        successful_events = [e for e in events if e.success]
        
        if not successful_events:
            return 0.0
        
        total_time = sum(e.duration_seconds for e in successful_events)
        return total_time / len(successful_events)
    
    def get_success_rate(
        self,
        failure_mode: Optional[FailureMode] = None,
        time_window_days: Optional[int] = None
    ) -> float:
        """
        Calculate remediation success rate
        
        Returns:
            Success rate as a percentage (0-100)
        """
        events = self.events
        
        if failure_mode:
            events = [e for e in events if e.failure_mode == failure_mode.value]
        
        if time_window_days:
            cutoff = datetime.now() - timedelta(days=time_window_days)
            events = [
                e for e in events
                if datetime.fromisoformat(e.timestamp) > cutoff
            ]
        
        if not events:
            return 0.0
        
        successful = sum(1 for e in events if e.success)
        return (successful / len(events)) * 100
    
    def get_stats(self) -> Dict:
        """Get comprehensive MTTR statistics"""
        stats = {
            "overall": {
                "mttr_seconds": self.get_mttr(),
                "success_rate": self.get_success_rate(),
                "total_events": len(self.events),
                "successful_events": sum(1 for e in self.events if e.success)
            },
            "by_failure_mode": {},
            "recent_7_days": {
                "mttr_seconds": self.get_mttr(time_window_days=7),
                "success_rate": self.get_success_rate(time_window_days=7)
            }
        }
        
        for failure_mode in FailureMode:
            mode_events = [e for e in self.events if e.failure_mode == failure_mode.value]
            if mode_events:
                stats["by_failure_mode"][failure_mode.value] = {
                    "mttr_seconds": self.get_mttr(failure_mode),
                    "success_rate": self.get_success_rate(failure_mode),
                    "total_events": len(mode_events),
                    "target_mttr": self._get_target_mttr(failure_mode)
                }
        
        return stats
    
    def _get_target_mttr(self, failure_mode: FailureMode) -> int:
        """Get target MTTR for a failure mode (from documentation)"""
        targets = {
            FailureMode.DATABASE_CORRUPTION: 60,
            FailureMode.PORT_IN_USE: 10,
            FailureMode.SLOW_BOOT: 5,
            FailureMode.OUT_OF_MEMORY: 30,
            FailureMode.DISK_FULL: 45,
            FailureMode.NETWORK_UNREACHABLE: 5,
            FailureMode.API_TIMEOUT: 15,
            FailureMode.MISSING_CONFIG: 10,
            FailureMode.INVALID_CREDENTIALS: 5,
            FailureMode.MODEL_SERVER_DOWN: 20
        }
        return targets.get(failure_mode, 120)
    
    def print_report(self):
        """Print MTTR report"""
        stats = self.get_stats()
        
        print("\n" + "=" * 80)
        print("MTTR (MEAN TIME TO RECOVERY) REPORT")
        print("=" * 80)
        print(f"Total Events: {stats['overall']['total_events']}")
        print(f"Successful: {stats['overall']['successful_events']}")
        print(f"Success Rate: {stats['overall']['success_rate']:.1f}%")
        print(f"\nOverall MTTR: {stats['overall']['mttr_seconds']:.1f}s")
        print(f"Recent 7 Days MTTR: {stats['recent_7_days']['mttr_seconds']:.1f}s")
        
        print(f"\nBy Failure Mode:")
        for mode, mode_stats in stats['by_failure_mode'].items():
            mttr = mode_stats['mttr_seconds']
            target = mode_stats['target_mttr']
            status = "✅" if mttr <= target else "❌"
            print(f"  {status} {mode}: {mttr:.1f}s (target: {target}s)")
        
        print("=" * 80)
