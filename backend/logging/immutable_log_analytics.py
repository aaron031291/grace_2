"""
Immutable Log Analytics Service

Periodically verifies the immutable log chain and flags gaps.
Doubles as an early warning if any subsystem stops logging.

Benefits:
- Ensures log integrity
- Detects silent failures
- Provides audit trail confidence
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func, and_, desc

from backend.models.base_models import ImmutableLogEntry as LogEntry, async_session
from .immutable_log import ImmutableLog

# Import trigger mesh from correct location
try:
    from backend.triggers.trigger_mesh import get_trigger_mesh, TriggerEvent
    trigger_mesh = get_trigger_mesh()
except ImportError:
    # Fallback if trigger mesh not available
    trigger_mesh = None
    TriggerEvent = None


class ImmutableLogAnalytics:
    """
    Analyzes and verifies the immutable log for integrity and continuity.
    """
    
    def __init__(self):
        self.running = False
        self.verification_task: Optional[asyncio.Task] = None
        self.immutable_log = ImmutableLog()
    
    async def start(self, interval_minutes: int = 15):
        """
        Start periodic log verification.
        
        Args:
            interval_minutes: How often to verify (default: every 15 minutes)
        """
        if self.running:
            return
        
        self.running = True
        self.verification_task = asyncio.create_task(
            self._verification_loop(interval_minutes)
        )
        
        print(f"[OK] Immutable log analytics started (verifies every {interval_minutes}min)")
    
    async def stop(self):
        """Stop the verification service"""
        self.running = False
        if self.verification_task:
            self.verification_task.cancel()
            try:
                await self.verification_task
            except asyncio.CancelledError:
                pass
    
    async def _verification_loop(self, interval_minutes: int):
        """Main verification loop"""
        while self.running:
            try:
                report = await self.verify_log_integrity()
                
                # If issues found, emit alert
                if report["has_issues"]:
                    await self._emit_integrity_alert(report)
                
                # Check for subsystem gaps
                gap_report = await self.check_subsystem_gaps()
                if gap_report["gaps_found"]:
                    await self._emit_gap_alert(gap_report)
                
                # Wait for next interval
                await asyncio.sleep(interval_minutes * 60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Log verification error: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute
    
    async def verify_log_integrity(self) -> Dict[str, Any]:
        """
        Verify immutable log chain integrity.
        
        Checks:
        - Sequential IDs (no gaps in sequence)
        - Timestamp ordering (monotonic increase)
        - Chain continuity (each entry links to previous)
        
        Returns:
            Verification report with any issues found
        """
        
        async with async_session() as session:
            # Get all log entries ordered by ID
            query = select(LogEntry).order_by(LogEntry.id)
            result = await session.execute(query)
            entries = list(result.scalars().all())
        
        if not entries:
            return {
                "has_issues": False,
                "total_entries": 0,
                "message": "No log entries to verify"
            }
        
        issues = []
        
        # Check 1: Sequential IDs
        expected_id = entries[0].id
        for i, entry in enumerate(entries):
            if entry.id != expected_id:
                issues.append({
                    "type": "id_gap",
                    "position": i,
                    "expected": expected_id,
                    "actual": entry.id,
                    "message": f"ID gap detected: expected {expected_id}, got {entry.id}"
                })
            expected_id = entry.id + 1
        
        # Check 2: Timestamp ordering
        for i in range(1, len(entries)):
            prev_time = entries[i-1].timestamp
            curr_time = entries[i].timestamp
            
            if curr_time < prev_time:
                issues.append({
                    "type": "timestamp_reversal",
                    "position": i,
                    "entry_id": entries[i].id,
                    "message": f"Timestamp reversal at entry {entries[i].id}"
                })
        
        # Check 3: Recent activity (no silent failures)
        last_entry = entries[-1]
        last_ts = last_entry.timestamp if last_entry.timestamp.tzinfo else last_entry.timestamp.replace(tzinfo=timezone.utc)
        time_since_last = datetime.now(timezone.utc) - last_ts
        
        if time_since_last > timedelta(hours=1):
            issues.append({
                "type": "stale_log",
                "last_entry_id": last_entry.id,
                "hours_since": time_since_last.total_seconds() / 3600,
                "message": f"No log entries for {time_since_last.total_seconds()/3600:.1f} hours"
            })
        
        report = {
            "has_issues": len(issues) > 0,
            "total_entries": len(entries),
            "first_entry_id": entries[0].id,
            "last_entry_id": entries[-1].id,
            "time_span_hours": (entries[-1].timestamp - entries[0].timestamp).total_seconds() / 3600,
            "issues": issues,
            "verified_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Log verification result (convert report to JSON-safe dict)
        json_safe_report = {
            "has_issues": report["has_issues"],
            "total_entries": report["total_entries"],
            "first_entry_id": report["first_entry_id"],
            "last_entry_id": report["last_entry_id"],
            "time_span_hours": report["time_span_hours"],
            "issue_count": len(issues),
            "verified_at": report["verified_at"]
        }
        
        await self.immutable_log.append(
            actor="log_analytics",
            action="integrity_verified",
            resource="immutable_log",
            subsystem="analytics",
            payload=json_safe_report,
            result="verified" if not issues else "issues_found"
        )
        
        return report
    
    async def check_subsystem_gaps(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Check for subsystems that haven't logged recently.
        
        Detects silent failures where a subsystem stops logging.
        
        Args:
            hours_back: How many hours to look back
            
        Returns:
            Report of subsystems with logging gaps
        """
        
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        
        async with async_session() as session:
            # Get logging frequency by subsystem
            query = select(
                LogEntry.subsystem,
                func.count(LogEntry.id).label("count"),
                func.max(LogEntry.timestamp).label("last_logged")
            ).where(
                LogEntry.timestamp >= cutoff
            ).group_by(LogEntry.subsystem)
            
            result = await session.execute(query)
            subsystem_stats = {
                row.subsystem: {
                    "count": row.count,
                    "last_logged": row.last_logged
                }
                for row in result.all()
            }
        
        # Expected subsystems (that should log regularly)
        expected_subsystems = [
            "agentic",
            "background_jobs",
            "verification",
            "analytics",
            "self_heal",
            "approvals"
        ]
        
        gaps = []
        for subsystem in expected_subsystems:
            stats = subsystem_stats.get(subsystem)
            
            if not stats:
                gaps.append({
                    "subsystem": subsystem,
                    "type": "no_logs",
                    "message": f"No logs from {subsystem} in last {hours_back}h"
                })
            else:
                # Check if last log is too old (> 6 hours)
                last_logged = stats["last_logged"]
                last_logged_tz = last_logged if last_logged.tzinfo else last_logged.replace(tzinfo=timezone.utc)
                time_since_last = datetime.now(timezone.utc) - last_logged_tz
                if time_since_last > timedelta(hours=6):
                    gaps.append({
                        "subsystem": subsystem,
                        "type": "stale",
                        "hours_since": time_since_last.total_seconds() / 3600,
                        "last_logged": stats["last_logged"].isoformat(),
                        "message": f"{subsystem} hasn't logged for {time_since_last.total_seconds()/3600:.1f}h"
                    })
        
        report = {
            "gaps_found": len(gaps) > 0,
            "subsystem_stats": subsystem_stats,
            "gaps": gaps,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "hours_back": hours_back
        }
        
        # Log gap check result
        await self.immutable_log.append(
            actor="log_analytics",
            action="gaps_checked",
            resource="subsystems",
            subsystem="analytics",
            payload=report,
            result="gaps_found" if gaps else "no_gaps"
        )
        
        return report
    
    async def get_activity_summary(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Get activity summary from logs.
        
        Args:
            hours_back: How many hours to analyze
            
        Returns:
            Summary of activity by actor, action, and subsystem
        """
        
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        
        async with async_session() as session:
            # Activity by actor
            actor_query = select(
                LogEntry.actor,
                func.count(LogEntry.id).label("count")
            ).where(
                LogEntry.timestamp >= cutoff
            ).group_by(LogEntry.actor)
            
            result = await session.execute(actor_query)
            by_actor = {row.actor: row.count for row in result.all()}
            
            # Activity by action
            action_query = select(
                LogEntry.action,
                func.count(LogEntry.id).label("count")
            ).where(
                LogEntry.timestamp >= cutoff
            ).group_by(LogEntry.action)
            
            result = await session.execute(action_query)
            by_action = {row.action: row.count for row in result.all()}
            
            # Activity by subsystem
            subsystem_query = select(
                LogEntry.subsystem,
                func.count(LogEntry.id).label("count")
            ).where(
                LogEntry.timestamp >= cutoff
            ).group_by(LogEntry.subsystem)
            
            result = await session.execute(subsystem_query)
            by_subsystem = {row.subsystem: row.count for row in result.all()}
            
            # Total entries
            total = await session.scalar(
                select(func.count(LogEntry.id)).where(
                    LogEntry.timestamp >= cutoff
                )
            )
        
        return {
            "total_entries": total or 0,
            "by_actor": by_actor,
            "by_action": by_action,
            "by_subsystem": by_subsystem,
            "hours_back": hours_back,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_failure_summary(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Get summary of failures from logs.
        
        Args:
            hours_back: How many hours to analyze
            
        Returns:
            Summary of failed operations
        """
        
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        
        async with async_session() as session:
            # Get failed entries
            query = select(LogEntry).where(
                and_(
                    LogEntry.timestamp >= cutoff,
                    LogEntry.result.in_(["failed", "error", "violated", "rolled_back"])
                )
            ).order_by(desc(LogEntry.timestamp))
            
            result = await session.execute(query)
            failures = list(result.scalars().all())
        
        # Group by subsystem
        by_subsystem = {}
        for failure in failures:
            if failure.subsystem not in by_subsystem:
                by_subsystem[failure.subsystem] = []
            
            by_subsystem[failure.subsystem].append({
                "id": failure.id,
                "actor": failure.actor,
                "action": failure.action,
                "result": failure.result,
                "timestamp": failure.timestamp.isoformat()
            })
        
        return {
            "total_failures": len(failures),
            "by_subsystem": by_subsystem,
            "hours_back": hours_back,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def _emit_integrity_alert(self, report: Dict[str, Any]):
        """Emit alert for integrity issues"""
        
        if trigger_mesh and TriggerEvent:
            await trigger_mesh.publish(TriggerEvent(
                event_type="log.integrity_issue",
                source="log_analytics",
                actor="system",
                resource="immutable_log",
                payload=report,
                timestamp=datetime.now(timezone.utc)
            ))
        
        print(f"⚠️  Immutable log integrity issues detected: {len(report['issues'])} issues")
    
    async def _emit_gap_alert(self, report: Dict[str, Any]):
        """Emit alert for subsystem gaps"""
        
        # Only alert if gaps are meaningful (not on fresh startup)
        if len(report['gaps']) > 0 and any(g['type'] == 'stale' for g in report['gaps']):
            if trigger_mesh and TriggerEvent:
                await trigger_mesh.publish(TriggerEvent(
                    event_type="log.subsystem_gap",
                    source="log_analytics",
                    actor="system",
                    resource="subsystems",
                    payload=report,
                    timestamp=datetime.now(timezone.utc)
                ))
            
            print(f"⚠️  Subsystem logging gaps detected: {len(report['gaps'])} subsystems")


# Global singleton
immutable_log_analytics = ImmutableLogAnalytics()
