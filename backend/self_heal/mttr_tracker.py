"""
MTTR Tracker - Phase 1
Track Mean Time To Recovery and auto-regression detection
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any
import statistics

class MTTRTracker:
    def __init__(self):
        self.incident_history = []
        self.mttr_targets = {
            "critical": 300,  # 5 minutes
            "high": 900,      # 15 minutes
            "medium": 1800,   # 30 minutes
            "low": 3600       # 1 hour
        }
    
    async def track_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Track new incident and calculate MTTR"""
        incident_record = {
            "incident_id": incident["id"],
            "severity": incident["severity"],
            "started_at": datetime.fromisoformat(incident["started_at"]),
            "resolved_at": datetime.fromisoformat(incident["resolved_at"]) if incident.get("resolved_at") else None,
            "resolution_time_seconds": None,
            "auto_resolved": incident.get("auto_resolved", False)
        }
        
        if incident_record["resolved_at"]:
            resolution_time = incident_record["resolved_at"] - incident_record["started_at"]
            incident_record["resolution_time_seconds"] = resolution_time.total_seconds()
        
        self.incident_history.append(incident_record)
        
        # Calculate current MTTR
        mttr_stats = await self._calculate_mttr_stats()
        
        # Check for regression
        regression_detected = await self._detect_regression()
        
        return {
            "incident_tracked": True,
            "current_mttr": mttr_stats,
            "regression_detected": regression_detected,
            "sla_breach": self._check_sla_breach(incident_record)
        }
    
    async def _calculate_mttr_stats(self) -> Dict[str, Any]:
        """Calculate MTTR statistics"""
        resolved_incidents = [i for i in self.incident_history if i["resolution_time_seconds"]]
        
        if not resolved_incidents:
            return {"mttr_seconds": 0, "sample_size": 0}
        
        resolution_times = [i["resolution_time_seconds"] for i in resolved_incidents]
        
        return {
            "mttr_seconds": statistics.mean(resolution_times),
            "median_seconds": statistics.median(resolution_times),
            "sample_size": len(resolved_incidents),
            "last_24h_mttr": self._calculate_recent_mttr(24),
            "trend": self._calculate_trend()
        }
    
    async def _detect_regression(self) -> bool:
        """Detect if MTTR is regressing"""
        if len(self.incident_history) < 10:
            return False
        
        recent_mttr = self._calculate_recent_mttr(24)  # Last 24 hours
        historical_mttr = self._calculate_recent_mttr(168)  # Last week
        
        # Regression if recent MTTR is 20% higher than historical
        return recent_mttr > (historical_mttr * 1.2)
    
    def _calculate_recent_mttr(self, hours: int) -> float:
        """Calculate MTTR for recent time period"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_incidents = [
            i for i in self.incident_history 
            if i["started_at"] > cutoff and i["resolution_time_seconds"]
        ]
        
        if not recent_incidents:
            return 0.0
        
        return statistics.mean([i["resolution_time_seconds"] for i in recent_incidents])
    
    def _calculate_trend(self) -> str:
        """Calculate MTTR trend"""
        if len(self.incident_history) < 5:
            return "insufficient_data"
        
        recent = self._calculate_recent_mttr(24)
        older = self._calculate_recent_mttr(168)
        
        if recent < older * 0.9:
            return "improving"
        elif recent > older * 1.1:
            return "degrading"
        else:
            return "stable"
    
    def _check_sla_breach(self, incident: Dict) -> bool:
        """Check if incident breached SLA"""
        if not incident["resolution_time_seconds"]:
            return False
        
        target = self.mttr_targets.get(incident["severity"], 3600)
        return incident["resolution_time_seconds"] > target

mttr_tracker = MTTRTracker()