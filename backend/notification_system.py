"""
Notification & Alert System
Real-time alerts for Memory Studio events
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import asyncio
from collections import deque

from backend.clarity import BaseComponent, ComponentStatus, get_event_bus, Event


class NotificationLevel(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationType(str, Enum):
    FILE_UPLOADED = "file_uploaded"
    PIPELINE_STARTED = "pipeline_started"
    PIPELINE_COMPLETED = "pipeline_completed"
    PIPELINE_FAILED = "pipeline_failed"
    QUALITY_ISSUE = "quality_issue"
    DUPLICATE_FOUND = "duplicate_found"
    SYNC_COMPLETED = "sync_completed"
    SYNC_FAILED = "sync_failed"
    GRACE_ACTION = "grace_action"
    CONTRADICTION_DETECTED = "contradiction_detected"
    SECURITY_ALERT = "security_alert"
    GOVERNANCE_BLOCK = "governance_block"
    LOW_STORAGE = "low_storage"
    SCHEDULED_JOB = "scheduled_job"


class NotificationSystem(BaseComponent):
    """
    Central notification hub for Memory Studio
    """
    
    def __init__(self):
        super().__init__()
        self.component_type = "notification_system"
        self.event_bus = get_event_bus()
        self.notifications: deque = deque(maxlen=1000)  # Keep last 1000
        self.active_alerts: Dict[str, Dict] = {}
        self.subscribers: List[asyncio.Queue] = []
        
    async def activate(self) -> bool:
        """Activate notification system"""
        self.set_status(ComponentStatus.ACTIVE)
        self.activated_at = datetime.utcnow()
        
        # Subscribe to relevant events
        await self._subscribe_to_events()
        
        await self.event_bus.publish(Event(
            event_type="notifications.system.activated",
            source=self.component_id,
            payload={"component": self.component_type}
        ))
        
        return True
    
    async def _subscribe_to_events(self):
        """Subscribe to event bus for automatic notifications"""
        
        # Subscribe to various event types
        event_mappings = {
            "ingestion.job.completed": self._handle_pipeline_completed,
            "ingestion.job.failed": self._handle_pipeline_failed,
            "grace.memory.file.created": self._handle_grace_action,
            "grace.memory.synced.fusion": self._handle_sync_completed,
            "intelligence.file.analyzed": self._handle_file_analyzed,
        }
        
        for event_type, handler in event_mappings.items():
            # In real implementation, would subscribe to event bus
            # For now, this is a stub
            pass
    
    async def notify(
        self,
        notification_type: NotificationType,
        level: NotificationLevel,
        title: str,
        message: str,
        data: Optional[Dict] = None,
        action_url: Optional[str] = None,
        dismissible: bool = True
    ) -> str:
        """
        Create and broadcast a notification
        Returns notification_id
        """
        
        notification_id = f"notif_{datetime.utcnow().timestamp()}"
        
        notification = {
            "id": notification_id,
            "type": notification_type,
            "level": level,
            "title": title,
            "message": message,
            "data": data or {},
            "action_url": action_url,
            "dismissible": dismissible,
            "created_at": datetime.utcnow().isoformat(),
            "read": False,
            "dismissed": False
        }
        
        self.notifications.append(notification)
        
        # If critical, add to active alerts
        if level == NotificationLevel.CRITICAL:
            self.active_alerts[notification_id] = notification
        
        # Broadcast to all subscribers (WebSocket)
        await self._broadcast(notification)
        
        # Publish as event
        await self.event_bus.publish(Event(
            event_type="notification.created",
            source=self.component_id,
            payload=notification
        ))
        
        return notification_id
    
    async def _broadcast(self, notification: Dict):
        """Broadcast notification to all WebSocket subscribers"""
        for queue in self.subscribers:
            try:
                await queue.put(notification)
            except:
                pass  # Subscriber disconnected
    
    def subscribe(self) -> asyncio.Queue:
        """Subscribe to notification stream (for WebSocket)"""
        queue = asyncio.Queue()
        self.subscribers.append(queue)
        return queue
    
    def unsubscribe(self, queue: asyncio.Queue):
        """Unsubscribe from notifications"""
        if queue in self.subscribers:
            self.subscribers.remove(queue)
    
    async def _handle_pipeline_completed(self, event: Event):
        """Handle pipeline completion"""
        await self.notify(
            notification_type=NotificationType.PIPELINE_COMPLETED,
            level=NotificationLevel.SUCCESS,
            title="Pipeline Completed",
            message=f"Pipeline {event.payload.get('pipeline')} finished successfully",
            data=event.payload
        )
    
    async def _handle_pipeline_failed(self, event: Event):
        """Handle pipeline failure"""
        await self.notify(
            notification_type=NotificationType.PIPELINE_FAILED,
            level=NotificationLevel.ERROR,
            title="Pipeline Failed",
            message=f"Pipeline failed: {event.payload.get('error')}",
            data=event.payload,
            dismissible=False
        )
    
    async def _handle_grace_action(self, event: Event):
        """Handle Grace autonomous action"""
        await self.notify(
            notification_type=NotificationType.GRACE_ACTION,
            level=NotificationLevel.INFO,
            title="Grace Saved Knowledge",
            message=f"Grace created: {event.payload.get('path')}",
            data=event.payload
        )
    
    async def _handle_sync_completed(self, event: Event):
        """Handle Memory Fusion sync"""
        await self.notify(
            notification_type=NotificationType.SYNC_COMPLETED,
            level=NotificationLevel.SUCCESS,
            title="Synced to Memory Fusion",
            message=f"File synced: {event.payload.get('path')}",
            data=event.payload
        )
    
    async def _handle_file_analyzed(self, event: Event):
        """Handle file analysis results"""
        quality = event.payload.get('quality_score', 0)
        duplicates = event.payload.get('duplicates_found', 0)
        
        # Alert on low quality
        if quality < 50:
            await self.notify(
                notification_type=NotificationType.QUALITY_ISSUE,
                level=NotificationLevel.WARNING,
                title="Low Quality File",
                message=f"Quality score {quality}/100 - review recommended",
                data=event.payload
            )
        
        # Alert on duplicates
        if duplicates > 0:
            await self.notify(
                notification_type=NotificationType.DUPLICATE_FOUND,
                level=NotificationLevel.WARNING,
                title="Duplicates Detected",
                message=f"Found {duplicates} duplicate files",
                data=event.payload
            )
    
    def get_notifications(
        self,
        limit: int = 50,
        unread_only: bool = False,
        level: Optional[NotificationLevel] = None
    ) -> List[Dict]:
        """Get notifications"""
        
        notifications = list(self.notifications)
        
        if unread_only:
            notifications = [n for n in notifications if not n.get("read")]
        
        if level:
            notifications = [n for n in notifications if n.get("level") == level]
        
        return notifications[-limit:]
    
    def mark_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        for notif in self.notifications:
            if notif["id"] == notification_id:
                notif["read"] = True
                return True
        return False
    
    def dismiss(self, notification_id: str) -> bool:
        """Dismiss notification"""
        for notif in self.notifications:
            if notif["id"] == notification_id:
                notif["dismissed"] = True
                # Remove from active alerts
                if notification_id in self.active_alerts:
                    del self.active_alerts[notification_id]
                return True
        return False
    
    def get_active_alerts(self) -> List[Dict]:
        """Get active critical alerts"""
        return list(self.active_alerts.values())


# Global instance
_notification_system: Optional[NotificationSystem] = None


async def get_notification_system() -> NotificationSystem:
    """Get or create global notification system"""
    global _notification_system
    if _notification_system is None:
        _notification_system = NotificationSystem()
        await _notification_system.activate()
    return _notification_system
