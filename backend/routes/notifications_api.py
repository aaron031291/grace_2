"""
Notifications API - SSE stream for real-time updates

Provides Server-Sent Events stream for:
- Approval requests
- Task status updates
- Learning job progress
- System alerts
- Healing actions
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.event_bus import event_bus, EventType

router = APIRouter()


class NotificationStream:
    """Manages SSE streams for clients"""
    
    def __init__(self):
        self.active_streams = set()
    
    async def subscribe(self):
        """Create new notification stream"""
        queue = asyncio.Queue()
        self.active_streams.add(queue)
        
        try:
            while True:
                notification = await queue.get()
                yield f"data: {json.dumps(notification)}\n\n"
        except asyncio.CancelledError:
            self.active_streams.discard(queue)
            raise
    
    async def broadcast(self, notification: Dict[str, Any]):
        """Broadcast notification to all active streams"""
        for queue in self.active_streams:
            try:
                await queue.put(notification)
            except Exception:
                pass


notification_stream = NotificationStream()


async def event_bus_listener():
    """Listen to event bus and broadcast notifications"""
    
    async def on_event(event):
        """Handle event from bus"""
        notification_types = {
            EventType.APPROVAL_REQUESTED: "approval_request",
            EventType.TASK_STARTED: "task_update",
            EventType.TASK_COMPLETED: "task_update",
            EventType.HEALING_TRIGGERED: "healing_action",
            EventType.AGENT_ACTION: "agent_action",
            EventType.MEMORY_UPDATE: "memory_update",
        }
        
        if event.event_type in notification_types:
            notification = {
                "type": notification_types[event.event_type],
                "timestamp": datetime.utcnow().isoformat(),
                "source": event.source,
                "data": event.data,
            }
            await notification_stream.broadcast(notification)
    
    event_bus.subscribe(EventType.APPROVAL_REQUESTED, on_event)
    event_bus.subscribe(EventType.TASK_STARTED, on_event)
    event_bus.subscribe(EventType.TASK_COMPLETED, on_event)
    event_bus.subscribe(EventType.HEALING_TRIGGERED, on_event)
    event_bus.subscribe(EventType.AGENT_ACTION, on_event)
    event_bus.subscribe(EventType.MEMORY_UPDATE, on_event)


@router.get("/notifications/stream")
async def notifications_sse():
    """
    Server-Sent Events stream for real-time notifications
    
    Usage in frontend:
        const eventSource = new EventSource('/api/notifications/stream');
        eventSource.onmessage = (event) => {
            const notification = JSON.parse(event.data);
            // Handle notification
        };
    """
    return StreamingResponse(
        notification_stream.subscribe(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/notifications/test")
async def test_notification(message: str = "Test notification"):
    """Send test notification to all connected clients"""
    await notification_stream.broadcast({
        "type": "test",
        "timestamp": datetime.utcnow().isoformat(),
        "message": message,
    })
    return {"status": "notification sent"}


async def notify_user(
    user_id: str,
    notification_type: str,
    message: str,
    data: Optional[Dict[str, Any]] = None,
    badge: str = "ℹ️"
):
    """
    Send notification to specific user
    
    Args:
        user_id: Target user ID
        notification_type: Type of notification (approval_needed, task_complete, etc.)
        message: Notification message
        data: Additional data payload
        badge: Emoji or icon badge
    """
    await notification_stream.broadcast({
        "type": notification_type,
        "user_id": user_id,
        "message": message,
        "badge": badge,
        "data": data or {},
        "timestamp": datetime.utcnow().isoformat(),
    })
