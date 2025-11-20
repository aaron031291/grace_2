"""
Automation Scheduler
Handles scheduled pipelines, watchers, and automated workflows
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import asyncio

from backend.clarity import BaseComponent, ComponentStatus, get_event_bus, Event
from backend.core.unified_event_publisher import publish_event


class ScheduleType(str, Enum):
    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CRON = "cron"
    WATCHER = "watcher"


class AutomationScheduler(BaseComponent):
    """
    Manages scheduled and automated ingestion workflows
    """
    
    def __init__(self):
        super().__init__()
        self.component_type = "automation_scheduler"
        self.event_bus = get_event_bus()
        self.schedules: Dict[str, Dict] = {}
        self.watchers: Dict[str, Dict] = {}
        self.running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        
    async def activate(self) -> bool:
        """Activate automation scheduler"""
        self.set_status(ComponentStatus.ACTIVE)
        self.activated_at = datetime.utcnow()
        self.running = True
        
        # Start scheduler loop
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        await publish_event(
            "automation.scheduler.activated",
            {"component": self.component_type},
            source=self.component_id
        )
        
        return True
    
    async def deactivate(self) -> bool:
        """Deactivate scheduler"""
        self.running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
        self.set_status(ComponentStatus.STOPPED)
        return True
    
    def create_schedule(
        self,
        schedule_id: str,
        pipeline_id: str,
        file_pattern: str,
        schedule_type: ScheduleType,
        schedule_config: Dict[str, Any],
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new scheduled automation
        
        Args:
            schedule_id: Unique identifier
            pipeline_id: Pipeline to run
            file_pattern: Glob pattern for files (e.g., "*.pdf")
            schedule_type: Type of schedule
            schedule_config: Schedule-specific config (time, interval, etc.)
            enabled: Whether schedule is active
        """
        
        schedule = {
            "schedule_id": schedule_id,
            "pipeline_id": pipeline_id,
            "file_pattern": file_pattern,
            "schedule_type": schedule_type,
            "config": schedule_config,
            "enabled": enabled,
            "created_at": datetime.utcnow().isoformat(),
            "last_run": None,
            "next_run": self._calculate_next_run(schedule_type, schedule_config),
            "run_count": 0,
            "last_status": None
        }
        
        self.schedules[schedule_id] = schedule
        return schedule
    
    def _calculate_next_run(
        self, 
        schedule_type: ScheduleType, 
        config: Dict[str, Any]
    ) -> str:
        """Calculate next run time based on schedule type"""
        
        now = datetime.utcnow()
        
        if schedule_type == ScheduleType.ONCE:
            # Run at specific time
            run_time = datetime.fromisoformat(config.get("run_at", now.isoformat()))
            return run_time.isoformat()
        
        elif schedule_type == ScheduleType.HOURLY:
            # Run every N hours
            hours = config.get("interval_hours", 1)
            next_run = now + timedelta(hours=hours)
            return next_run.isoformat()
        
        elif schedule_type == ScheduleType.DAILY:
            # Run daily at specific time
            hour = config.get("hour", 0)
            minute = config.get("minute", 0)
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run.isoformat()
        
        elif schedule_type == ScheduleType.WEEKLY:
            # Run weekly on specific day
            weekday = config.get("weekday", 0)  # 0 = Monday
            hour = config.get("hour", 0)
            next_run = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            days_ahead = weekday - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run += timedelta(days=days_ahead)
            return next_run.isoformat()
        
        else:
            # Default to 1 hour from now
            return (now + timedelta(hours=1)).isoformat()
    
    def create_watcher(
        self,
        watcher_id: str,
        watch_path: str,
        pipeline_id: str,
        watch_for: str = "new_files",  # new_files, modifications, deletions
        file_filter: Optional[str] = None,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Create a file system watcher
        Automatically triggers pipeline when files change
        """
        
        watcher = {
            "watcher_id": watcher_id,
            "watch_path": watch_path,
            "pipeline_id": pipeline_id,
            "watch_for": watch_for,
            "file_filter": file_filter,
            "enabled": enabled,
            "created_at": datetime.utcnow().isoformat(),
            "files_processed": 0,
            "last_triggered": None
        }
        
        self.watchers[watcher_id] = watcher
        return watcher
    
    async def _scheduler_loop(self):
        """Main scheduler loop - runs every minute"""
        while self.running:
            try:
                await self._check_schedules()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def _check_schedules(self):
        """Check all schedules and trigger due ones"""
        now = datetime.utcnow()
        
        for schedule_id, schedule in self.schedules.items():
            if not schedule["enabled"]:
                continue
            
            next_run = datetime.fromisoformat(schedule["next_run"])
            
            if now >= next_run:
                await self._trigger_schedule(schedule_id)
    
    async def _trigger_schedule(self, schedule_id: str):
        """Trigger a scheduled automation"""
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            return
        
        try:
            # Import here to avoid circular dependency
            from backend.ingestion_pipeline import get_ingestion_pipeline
            
            pipeline = await get_ingestion_pipeline()
            
            # Find files matching pattern (stub - would use glob in real impl)
            files_to_process = [schedule["file_pattern"]]  # Simplified
            
            for file_path in files_to_process:
                await pipeline.start_pipeline(
                    schedule["pipeline_id"],
                    file_path,
                    schedule["config"]
                )
            
            # Update schedule
            schedule["last_run"] = datetime.utcnow().isoformat()
            schedule["run_count"] += 1
            schedule["last_status"] = "success"
            schedule["next_run"] = self._calculate_next_run(
                schedule["schedule_type"],
                schedule["config"]
            )
            
            # Publish event
            await publish_event(
                "automation.schedule.triggered",
                {
                    "schedule_id": schedule_id,
                    "pipeline": schedule["pipeline_id"],
                    "files_processed": len(files_to_process)
                },
                source=self.component_id
            )
            
        except Exception as e:
            schedule["last_status"] = f"failed: {str(e)}"
            print(f"Schedule {schedule_id} failed: {e}")
    
    def list_schedules(self, enabled_only: bool = False) -> List[Dict]:
        """List all schedules"""
        schedules = list(self.schedules.values())
        if enabled_only:
            schedules = [s for s in schedules if s["enabled"]]
        return schedules
    
    def list_watchers(self, enabled_only: bool = False) -> List[Dict]:
        """List all watchers"""
        watchers = list(self.watchers.values())
        if enabled_only:
            watchers = [w for w in watchers if w["enabled"]]
        return watchers
    
    def enable_schedule(self, schedule_id: str) -> bool:
        """Enable a schedule"""
        if schedule_id in self.schedules:
            self.schedules[schedule_id]["enabled"] = True
            return True
        return False
    
    def disable_schedule(self, schedule_id: str) -> bool:
        """Disable a schedule"""
        if schedule_id in self.schedules:
            self.schedules[schedule_id]["enabled"] = False
            return True
        return False
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule"""
        if schedule_id in self.schedules:
            del self.schedules[schedule_id]
            return True
        return False
    
    def get_schedule(self, schedule_id: str) -> Optional[Dict]:
        """Get a specific schedule"""
        return self.schedules.get(schedule_id)


# Global instance
_automation_scheduler: Optional[AutomationScheduler] = None


async def get_automation_scheduler() -> AutomationScheduler:
    """Get or create global automation scheduler"""
    global _automation_scheduler
    if _automation_scheduler is None:
        _automation_scheduler = AutomationScheduler()
        await _automation_scheduler.activate()
    return _automation_scheduler


# Pre-defined automation templates
AUTOMATION_TEMPLATES = {
    "daily_pdf_processing": {
        "name": "Daily PDF Processing",
        "description": "Process all new PDFs every day at 2 AM",
        "schedule_type": "daily",
        "pipeline_id": "pdf_extraction",
        "file_pattern": "**/*.pdf",
        "config": {"hour": 2, "minute": 0}
    },
    "hourly_text_indexing": {
        "name": "Hourly Text Indexing",
        "description": "Index new text files every hour",
        "schedule_type": "hourly",
        "pipeline_id": "text_to_embeddings",
        "file_pattern": "**/*.{txt,md}",
        "config": {"interval_hours": 1}
    },
    "weekly_code_analysis": {
        "name": "Weekly Code Analysis",
        "description": "Analyze code repository every Monday",
        "schedule_type": "weekly",
        "pipeline_id": "code_analysis",
        "file_pattern": "**/*.{py,js,ts}",
        "config": {"weekday": 0, "hour": 9}  # Monday 9 AM
    },
    "audio_watcher": {
        "name": "Audio Transcription Watcher",
        "description": "Auto-transcribe new audio files",
        "type": "watcher",
        "pipeline_id": "audio_transcription",
        "watch_for": "new_files",
        "file_filter": "*.{mp3,wav,m4a}"
    }
}
