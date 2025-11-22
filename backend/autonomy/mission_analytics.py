"""
Mission Analytics - Historical Metrics Persistence

Persists mission outcomes and KPI deltas for trend analysis:
- Missions per domain over time
- MTTR (Mean Time To Repair) trends
- Effectiveness scores by domain
- KPI improvement rates
- Domain health trends

Enables dashboards and reports on Grace's autonomous operations
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class MissionAnalyticRecord:
    """Single analytics record for a mission"""
    record_id: str
    mission_id: str
    domain_id: str
    mission_type: str
    timestamp: str
    success: bool
    duration_seconds: float
    effectiveness_score: float
    metrics_delta: Dict[str, float]  # metric_name -> percent_change
    tasks_count: int
    auto_generated: bool
    metadata: Dict[str, Any]


@dataclass
class DomainTrendData:
    """Trend data for a domain"""
    domain_id: str
    period_start: str
    period_end: str
    total_missions: int
    success_rate: float
    avg_duration_seconds: float
    avg_effectiveness_score: float
    mttr_seconds: float  # Mean Time To Repair
    top_issues: List[str]
    kpi_trends: Dict[str, float]  # metric_name -> avg_improvement


class MissionAnalytics:
    """
    Persists and queries mission analytics for trend analysis
    
    Stores:
    - Individual mission records
    - Aggregated domain trends
    - KPI improvement rates
    - Historical performance data
    """
    
    def __init__(self, storage_path: str = "databases/mission_analytics"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.records_file = self.storage_path / "mission_records.jsonl"
        self.trends_file = self.storage_path / "domain_trends.json"
        
        self._initialized = False
        self.records_count = 0
    
    async def initialize(self):
        """Initialize analytics system"""
        if self._initialized:
            return
        
        logger.info("[ANALYTICS] Initializing mission analytics")
        
        # Count existing records
        if self.records_file.exists():
            with open(self.records_file, 'r') as f:
                self.records_count = sum(1 for _ in f)
        
        self._initialized = True
        logger.info(f"[ANALYTICS] Initialized with {self.records_count} historical records")
    
    async def record_mission(
        self,
        mission_id: str,
        domain_id: str,
        mission_type: str,
        success: bool,
        duration_seconds: float,
        effectiveness_score: float = 0.5,
        metrics_delta: Optional[Dict[str, float]] = None,
        tasks_count: int = 0,
        auto_generated: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record a mission for analytics
        
        Returns record_id
        """
        import uuid
        
        record_id = str(uuid.uuid4())[:12]
        
        record = MissionAnalyticRecord(
            record_id=record_id,
            mission_id=mission_id,
            domain_id=domain_id,
            mission_type=mission_type,
            timestamp=datetime.utcnow().isoformat(),
            success=success,
            duration_seconds=duration_seconds,
            effectiveness_score=effectiveness_score,
            metrics_delta=metrics_delta or {},
            tasks_count=tasks_count,
            auto_generated=auto_generated,
            metadata=metadata or {}
        )
        
        # Append to JSONL file
        with open(self.records_file, 'a') as f:
            f.write(json.dumps(asdict(record)) + '\n')
        
        self.records_count += 1
        
        logger.info(f"[ANALYTICS] Recorded mission {mission_id} for {domain_id}")
        
        return record_id
    
    async def get_domain_trends(
        self,
        domain_id: Optional[str] = None,
        period_days: int = 30
    ) -> List[DomainTrendData]:
        """
        Get trend data for domains
        
        Args:
            domain_id: Specific domain or None for all
            period_days: Days to analyze
        
        Returns:
            List of trend data per domain
        """
        since = datetime.utcnow() - timedelta(days=period_days)
        
        # Load records
        records = self._load_records_since(since)
        
        if domain_id:
            records = [r for r in records if r.domain_id == domain_id]
        
        # Group by domain
        by_domain = {}
        for record in records:
            if record.domain_id not in by_domain:
                by_domain[record.domain_id] = []
            by_domain[record.domain_id].append(record)
        
        # Calculate trends per domain
        trends = []
        for dom_id, dom_records in by_domain.items():
            trend = self._calculate_domain_trend(
                domain_id=dom_id,
                records=dom_records,
                period_start=since,
                period_end=datetime.utcnow()
            )
            trends.append(trend)
        
        return trends
    
    def _calculate_domain_trend(
        self,
        domain_id: str,
        records: List[MissionAnalyticRecord],
        period_start: datetime,
        period_end: datetime
    ) -> DomainTrendData:
        """Calculate trend metrics for a domain"""
        
        total = len(records)
        successful = sum(1 for r in records if r.success)
        success_rate = successful / total if total > 0 else 0
        
        # Average duration
        avg_duration = sum(r.duration_seconds for r in records) / total if total > 0 else 0
        
        # Average effectiveness
        scores = [r.effectiveness_score for r in records if r.effectiveness_score > 0]
        avg_effectiveness = sum(scores) / len(scores) if scores else 0.5
        
        # MTTR: average duration of remediation missions
        remediation = [r for r in records if 'remediation' in r.mission_type or 'fix' in r.mission_type]
        mttr = sum(r.duration_seconds for r in remediation) / len(remediation) if remediation else 0
        
        # Top issues (mission types)
        issue_counts = {}
        for r in records:
            issue_counts[r.mission_type] = issue_counts.get(r.mission_type, 0) + 1
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_issues = [issue for issue, count in top_issues]
        
        # KPI trends (aggregate all metrics_delta)
        kpi_totals = {}
        kpi_counts = {}
        for r in records:
            for metric, delta in r.metrics_delta.items():
                if metric not in kpi_totals:
                    kpi_totals[metric] = 0
                    kpi_counts[metric] = 0
                kpi_totals[metric] += delta
                kpi_counts[metric] += 1
        
        kpi_trends = {
            metric: kpi_totals[metric] / kpi_counts[metric]
            for metric in kpi_totals
        }
        
        return DomainTrendData(
            domain_id=domain_id,
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            total_missions=total,
            success_rate=success_rate,
            avg_duration_seconds=avg_duration,
            avg_effectiveness_score=avg_effectiveness,
            mttr_seconds=mttr,
            top_issues=top_issues,
            kpi_trends=kpi_trends
        )
    
    async def get_missions_per_domain(
        self,
        period_days: int = 30,
        granularity: str = "daily"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get missions per domain over time
        
        Returns:
            {
                "domain_id": [
                    {"date": "2025-11-15", "count": 5},
                    {"date": "2025-11-16", "count": 3}
                ]
            }
        """
        since = datetime.utcnow() - timedelta(days=period_days)
        records = self._load_records_since(since)
        
        # Group by domain and time bucket
        by_domain = {}
        
        for record in records:
            if record.domain_id not in by_domain:
                by_domain[record.domain_id] = {}
            
            # Get time bucket
            timestamp = datetime.fromisoformat(record.timestamp)
            if granularity == "daily":
                bucket = timestamp.strftime("%Y-%m-%d")
            elif granularity == "hourly":
                bucket = timestamp.strftime("%Y-%m-%d %H:00")
            else:
                bucket = timestamp.strftime("%Y-%m-%d")
            
            if bucket not in by_domain[record.domain_id]:
                by_domain[record.domain_id][bucket] = 0
            by_domain[record.domain_id][bucket] += 1
        
        # Convert to list format
        result = {}
        for domain_id, buckets in by_domain.items():
            result[domain_id] = [
                {"date": bucket, "count": count}
                for bucket, count in sorted(buckets.items())
            ]
        
        return result
    
    async def get_mttr_trend(
        self,
        domain_id: Optional[str] = None,
        period_days: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Get Mean Time To Repair trend over time
        
        Returns:
            [
                {"date": "2025-11-15", "mttr_seconds": 120.5},
                {"date": "2025-11-16", "mttr_seconds": 95.3}
            ]
        """
        since = datetime.utcnow() - timedelta(days=period_days)
        records = self._load_records_since(since)
        
        if domain_id:
            records = [r for r in records if r.domain_id == domain_id]
        
        # Filter to remediation missions
        remediation = [
            r for r in records
            if 'remediation' in r.mission_type or 'fix' in r.mission_type or 'heal' in r.mission_type
        ]
        
        # Group by day
        by_day = {}
        for r in remediation:
            timestamp = datetime.fromisoformat(r.timestamp)
            day = timestamp.strftime("%Y-%m-%d")
            
            if day not in by_day:
                by_day[day] = []
            by_day[day].append(r.duration_seconds)
        
        # Calculate average per day
        trend = [
            {
                "date": day,
                "mttr_seconds": sum(durations) / len(durations),
                "count": len(durations)
            }
            for day, durations in sorted(by_day.items())
        ]
        
        return trend
    
    async def get_effectiveness_trend(
        self,
        domain_id: Optional[str] = None,
        period_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get effectiveness score trend over time
        
        Returns:
            [
                {"date": "2025-11-15", "avg_effectiveness": 0.85},
                {"date": "2025-11-16", "avg_effectiveness": 0.92}
            ]
        """
        since = datetime.utcnow() - timedelta(days=period_days)
        records = self._load_records_since(since)
        
        if domain_id:
            records = [r for r in records if r.domain_id == domain_id]
        
        # Filter records with effectiveness scores
        scored = [r for r in records if r.effectiveness_score > 0]
        
        # Group by day
        by_day = {}
        for r in scored:
            timestamp = datetime.fromisoformat(r.timestamp)
            day = timestamp.strftime("%Y-%m-%d")
            
            if day not in by_day:
                by_day[day] = []
            by_day[day].append(r.effectiveness_score)
        
        # Calculate average per day
        trend = [
            {
                "date": day,
                "avg_effectiveness": sum(scores) / len(scores),
                "count": len(scores)
            }
            for day, scores in sorted(by_day.items())
        ]
        
        return trend
    
    def _load_records_since(self, since: datetime) -> List[MissionAnalyticRecord]:
        """Load records since timestamp"""
        records = []
        
        if not self.records_file.exists():
            return records
        
        with open(self.records_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    record = MissionAnalyticRecord(**data)
                    
                    # Filter by timestamp
                    record_time = datetime.fromisoformat(record.timestamp)
                    if record_time >= since:
                        records.append(record)
                        
                except Exception as e:
                    logger.warning(f"[ANALYTICS] Failed to parse record: {e}")
        
        return records
    
    def get_stats(self) -> Dict[str, Any]:
        """Get analytics statistics"""
        return {
            "total_records": self.records_count,
            "storage_path": str(self.storage_path),
            "records_file_exists": self.records_file.exists()
        }


# Global instance
mission_analytics = MissionAnalytics()
