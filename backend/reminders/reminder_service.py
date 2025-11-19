"""
Reminder Service - Grace's memory for future tasks

Features:
- Natural language reminder creation
- Scheduled notifications
- Recurring reminders
- Contextual reminders (trigger on events)
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import uuid4
import sqlite3
from pathlib import Path
from enum import Enum

from backend.event_bus import event_bus, Event, EventType


class ReminderStatus(str, Enum):
    """Reminder status"""
    PENDING = "pending"
    TRIGGERED = "triggered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReminderType(str, Enum):
    """Reminder type"""
    TIME_BASED = "time_based"         # Trigger at specific time
    EVENT_BASED = "event_based"       # Trigger on event (job complete, etc.)
    RECURRING = "recurring"           # Repeat daily/weekly/monthly


class ReminderService:
    """
    Grace's reminder system
    
    Parses natural language like:
    - "Remind me tomorrow to review the CRM deploy"
    - "Remind me in 2 hours to check the logs"
    - "Remind me every Monday to review metrics"
    - "Remind me when the data import finishes"
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path("storage/reminders.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self.running = False
    
    def _init_db(self):
        """Initialize reminder database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                reminder_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                reminder_type TEXT NOT NULL,
                trigger_time TEXT,
                trigger_event TEXT,
                recurrence_pattern TEXT,
                status TEXT NOT NULL,
                context TEXT,
                created_at TEXT NOT NULL,
                triggered_at TEXT,
                completed_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON reminders(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trigger_time ON reminders(trigger_time)
        """)
        
        conn.commit()
        conn.close()
    
    async def create_reminder(
        self,
        user_id: str,
        message: str,
        trigger_time: Optional[datetime] = None,
        trigger_event: Optional[str] = None,
        recurrence: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a reminder
        
        Args:
            user_id: User who created reminder
            message: Reminder message
            trigger_time: When to trigger (for time-based)
            trigger_event: Event to trigger on (for event-based)
            recurrence: Recurrence pattern (daily, weekly, monthly)
            context: Additional context
        
        Returns:
            reminder_id
        """
        reminder_id = f"reminder_{uuid4().hex[:12]}"
        
        # Determine reminder type
        if recurrence:
            reminder_type = ReminderType.RECURRING
        elif trigger_event:
            reminder_type = ReminderType.EVENT_BASED
        else:
            reminder_type = ReminderType.TIME_BASED
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO reminders 
            (reminder_id, user_id, message, reminder_type, trigger_time, trigger_event, 
             recurrence_pattern, status, context, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            reminder_id,
            user_id,
            message,
            reminder_type.value,
            trigger_time.isoformat() if trigger_time else None,
            trigger_event,
            recurrence,
            ReminderStatus.PENDING.value,
            str(context) if context else None,
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Publish event
        await event_bus.publish(Event(
            event_type=EventType.AGENT_ACTION,
            source="reminder_service",
            data={
                "action": "reminder_created",
                "reminder_id": reminder_id,
                "user_id": user_id,
                "trigger_time": trigger_time.isoformat() if trigger_time else None,
            }
        ))
        
        print(f"[ReminderService] Created reminder: {reminder_id}")
        return reminder_id
    
    async def parse_natural_language(
        self,
        user_id: str,
        text: str
    ) -> Optional[str]:
        """
        Parse natural language reminder and create it
        
        Examples:
        - "Remind me tomorrow to review the CRM deploy"
        - "Remind me in 2 hours"
        - "Remind me every Monday"
        - "Remind me when the import finishes"
        """
        text_lower = text.lower()
        
        # Extract reminder message (after "to")
        if " to " in text_lower:
            message_part = text.split(" to ", 1)[1]
        else:
            message_part = text
        
        trigger_time = None
        trigger_event = None
        recurrence = None
        
        # Parse time-based triggers
        if "tomorrow" in text_lower:
            trigger_time = datetime.now() + timedelta(days=1)
            trigger_time = trigger_time.replace(hour=9, minute=0, second=0)
        
        elif "in " in text_lower:
            # "in 2 hours", "in 30 minutes"
            import re
            match = re.search(r'in (\d+) (hour|minute|day)', text_lower)
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                
                if unit == "minute":
                    trigger_time = datetime.now() + timedelta(minutes=amount)
                elif unit == "hour":
                    trigger_time = datetime.now() + timedelta(hours=amount)
                elif unit == "day":
                    trigger_time = datetime.now() + timedelta(days=amount)
        
        elif "every" in text_lower:
            # Recurring reminder
            if "monday" in text_lower:
                recurrence = "weekly_monday"
            elif "tuesday" in text_lower:
                recurrence = "weekly_tuesday"
            elif "day" in text_lower:
                recurrence = "daily"
            
            # Set initial trigger to next occurrence
            trigger_time = datetime.now() + timedelta(days=1)
        
        elif "when" in text_lower:
            # Event-based trigger
            if "finish" in text_lower or "complete" in text_lower:
                trigger_event = "task_completed"
            elif "import" in text_lower:
                trigger_event = "import_completed"
            elif "deploy" in text_lower:
                trigger_event = "deployment_completed"
        
        # Create reminder
        if trigger_time or trigger_event or recurrence:
            return await self.create_reminder(
                user_id=user_id,
                message=message_part,
                trigger_time=trigger_time,
                trigger_event=trigger_event,
                recurrence=recurrence
            )
        
        return None
    
    async def check_due_reminders(self):
        """Check for reminders that are due and trigger them"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            SELECT * FROM reminders 
            WHERE status = ? AND trigger_time <= ?
        """, (ReminderStatus.PENDING.value, now))
        
        due_reminders = cursor.fetchall()
        conn.close()
        
        for reminder in due_reminders:
            await self._trigger_reminder(dict(reminder))
    
    async def _trigger_reminder(self, reminder: Dict[str, Any]):
        """Trigger a reminder (send notification)"""
        reminder_id = reminder["reminder_id"]
        
        # Mark as triggered
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE reminders 
            SET status = ?, triggered_at = ?
            WHERE reminder_id = ?
        """, (ReminderStatus.TRIGGERED.value, datetime.utcnow().isoformat(), reminder_id))
        
        conn.commit()
        conn.close()
        
        # Send notification
        from backend.routes.notifications_api import notify_user
        await notify_user(
            user_id=reminder["user_id"],
            notification_type="reminder",
            message=f"⏰ Reminder: {reminder['message']}",
            data={"reminder_id": reminder_id},
            badge="⏰"
        )
        
        # Publish to chat if user is active
        await event_bus.publish(Event(
            event_type=EventType.AGENT_ACTION,
            source="reminder_service",
            data={
                "action": "reminder_triggered",
                "reminder_id": reminder_id,
                "user_id": reminder["user_id"],
                "message": reminder["message"],
            }
        ))
        
        print(f"[ReminderService] Triggered reminder: {reminder_id}")
        
        # Handle recurrence
        if reminder["recurrence_pattern"]:
            await self._schedule_next_occurrence(reminder)
    
    async def _schedule_next_occurrence(self, reminder: Dict[str, Any]):
        """Schedule next occurrence for recurring reminder"""
        pattern = reminder["recurrence_pattern"]
        current_time = datetime.fromisoformat(reminder["trigger_time"])
        
        if pattern == "daily":
            next_time = current_time + timedelta(days=1)
        elif pattern.startswith("weekly_"):
            next_time = current_time + timedelta(weeks=1)
        else:
            return
        
        # Create new reminder for next occurrence
        await self.create_reminder(
            user_id=reminder["user_id"],
            message=reminder["message"],
            trigger_time=next_time,
            recurrence=pattern
        )
    
    async def start(self):
        """Start reminder checker background task"""
        self.running = True
        while self.running:
            try:
                await self.check_due_reminders()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"[ReminderService] Error checking reminders: {e}")
                await asyncio.sleep(60)
    
    def stop(self):
        """Stop reminder checker"""
        self.running = False
    
    def get_pending_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all pending reminders for user"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM reminders 
            WHERE user_id = ? AND status = ?
            ORDER BY trigger_time ASC
        """, (user_id, ReminderStatus.PENDING.value))
        
        reminders = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return reminders


# Global instance
reminder_service = ReminderService()
