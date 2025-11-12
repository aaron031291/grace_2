"""
Notification Service
Manages user notifications with priority, delivery, and tracking
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
from collections import defaultdict

logger = logging.getLogger(__name__)


class NotificationPriority:
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationType:
    WORKFLOW_ASSIGNED = "workflow_assigned"
    WORKFLOW_APPROVED = "workflow_approved"
    WORKFLOW_REJECTED = "workflow_rejected"
    EDIT_REQUEST = "edit_request"
    EDIT_GRANTED = "edit_granted"
    FILE_CHANGED = "file_changed"
    MENTION = "mention"
    SYSTEM_ALERT = "system_alert"
    COPILOT_SUGGESTION = "copilot_suggestion"


class Notification:
    """Represents a user notification"""
    
    def __init__(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        priority: str = NotificationPriority.NORMAL,
        action_url: str = None,
        action_label: str = None,
        metadata: Dict[str, Any] = None
    ):
        self.notification_id = str(uuid.uuid4())
        self.user_id = user_id
        self.notification_type = notification_type
        self.title = title
        self.message = message
        self.priority = priority
        self.action_url = action_url
        self.action_label = action_label
        self.metadata = metadata or {}
        
        self.is_read = False
        self.is_dismissed = False
        self.created_at = datetime.utcnow()
        self.read_at: Optional[datetime] = None
        self.dismissed_at: Optional[datetime] = None
    
    def mark_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
    
    def dismiss(self):
        """Dismiss notification"""
        self.is_dismissed = True
        self.dismissed_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "notification_id": self.notification_id,
            "user_id": self.user_id,
            "notification_type": self.notification_type,
            "title": self.title,
            "message": self.message,
            "priority": self.priority,
            "action_url": self.action_url,
            "action_label": self.action_label,
            "metadata": self.metadata,
            "is_read": self.is_read,
            "is_dismissed": self.is_dismissed,
            "created_at": self.created_at.isoformat(),
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "dismissed_at": self.dismissed_at.isoformat() if self.dismissed_at else None
        }


class NotificationService:
    """
    Manages notifications across Grace.
    Handles creation, delivery, tracking, and cleanup.
    """
    
    def __init__(self):
        self.notifications: Dict[str, Notification] = {}
        self.user_notifications: Dict[str, List[str]] = defaultdict(list)
        self.websocket_manager = None
        self._cleanup_task = None
        self._running = False
    
    def set_websocket_manager(self, ws_manager):
        """Set WebSocket manager for real-time notifications"""
        self.websocket_manager = ws_manager
    
    async def start(self):
        """Start notification service"""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("🔔 Notification service started")
    
    async def stop(self):
        """Stop notification service"""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
        logger.info("🛑 Notification service stopped")
    
    async def create_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        priority: str = NotificationPriority.NORMAL,
        action_url: str = None,
        action_label: str = None,
        metadata: Dict[str, Any] = None
    ) -> Notification:
        """Create and deliver a notification"""
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            action_url=action_url,
            action_label=action_label,
            metadata=metadata
        )
        
        self.notifications[notification.notification_id] = notification
        self.user_notifications[user_id].append(notification.notification_id)
        
        logger.info(f"🔔 Created notification for {user_id}: {title}")
        
        await self._deliver_notification(notification)
        
        return notification
    
    async def _deliver_notification(self, notification: Notification):
        """Deliver notification via WebSocket if user is connected"""
        if self.websocket_manager:
            try:
                await self.websocket_manager.send_notification(
                    notification.user_id,
                    notification.to_dict()
                )
            except Exception as e:
                logger.error(f"Failed to deliver notification via WebSocket: {e}")
    
    async def bulk_notify(
        self,
        user_ids: List[str],
        notification_type: str,
        title: str,
        message: str,
        **kwargs
    ):
        """Send notification to multiple users"""
        for user_id in user_ids:
            await self.create_notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                **kwargs
            )
    
    async def mark_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read"""
        notification = self.notifications.get(notification_id)
        
        if not notification or notification.user_id != user_id:
            return False
        
        notification.mark_read()
        return True
    
    async def mark_all_read(self, user_id: str):
        """Mark all user notifications as read"""
        notification_ids = self.user_notifications.get(user_id, [])
        
        for nid in notification_ids:
            notification = self.notifications.get(nid)
            if notification and not notification.is_read:
                notification.mark_read()
    
    async def dismiss(self, notification_id: str, user_id: str) -> bool:
        """Dismiss notification"""
        notification = self.notifications.get(notification_id)
        
        if not notification or notification.user_id != user_id:
            return False
        
        notification.dismiss()
        return True
    
    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get user notifications"""
        notification_ids = self.user_notifications.get(user_id, [])
        
        notifications = []
        for nid in reversed(notification_ids[-limit:]):
            notification = self.notifications.get(nid)
            if notification:
                if unread_only and notification.is_read:
                    continue
                if notification.is_dismissed:
                    continue
                notifications.append(notification.to_dict())
        
        return notifications
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications"""
        notification_ids = self.user_notifications.get(user_id, [])
        
        count = 0
        for nid in notification_ids:
            notification = self.notifications.get(nid)
            if notification and not notification.is_read and not notification.is_dismissed:
                count += 1
        
        return count
    
    async def _cleanup_loop(self):
        """Clean up old dismissed notifications"""
        while self._running:
            try:
                await self._cleanup_old_notifications()
                await asyncio.sleep(3600)
            except Exception as e:
                logger.error(f"Error in notification cleanup: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_notifications(self):
        """Remove dismissed notifications older than 30 days"""
        cutoff = datetime.utcnow() - timedelta(days=30)
        
        to_remove = []
        for nid, notification in self.notifications.items():
            if notification.is_dismissed and notification.dismissed_at:
                if notification.dismissed_at < cutoff:
                    to_remove.append(nid)
        
        for nid in to_remove:
            notification = self.notifications[nid]
            user_id = notification.user_id
            
            if nid in self.user_notifications.get(user_id, []):
                self.user_notifications[user_id].remove(nid)
            
            del self.notifications[nid]
        
        if to_remove:
            logger.info(f"🧹 Cleaned up {len(to_remove)} old notifications")
    
    async def notify_workflow_assigned(self, user_id: str, workflow_title: str, workflow_id: str):
        """Workflow assigned notification"""
        await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.WORKFLOW_ASSIGNED,
            title="Workflow Assigned",
            message=f"You've been assigned to review: {workflow_title}",
            priority=NotificationPriority.HIGH,
            action_url=f"/workflows/{workflow_id}",
            action_label="Review Workflow"
        )
    
    async def notify_edit_request(self, user_id: str, requester_name: str, file_path: str):
        """Edit request notification"""
        await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.EDIT_REQUEST,
            title="Edit Request",
            message=f"{requester_name} is requesting to edit {file_path}",
            priority=NotificationPriority.NORMAL,
            action_url=f"/files/{file_path}",
            action_label="View File"
        )
    
    async def notify_copilot_suggestion(self, user_id: str, suggestion: str):
        """Co-pilot suggestion notification"""
        await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.COPILOT_SUGGESTION,
            title="Grace Suggestion",
            message=suggestion,
            priority=NotificationPriority.LOW
        )


notification_service = NotificationService()
