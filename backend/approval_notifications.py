"""
Approval Notification System

Server-Sent Events (SSE) and webhooks for real-time approval updates.
Enables frontend subscriptions instead of polling.

Benefits:
- Responsive UI without constant polling
- Lower server load
- Real-time collaboration on approvals
"""

import asyncio
from typing import Dict, Set, Optional, AsyncGenerator
from datetime import datetime, timezone
from fastapi import Request
from fastapi.responses import StreamingResponse
import json

from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log


class ApprovalNotificationManager:
    """
    Manages real-time notifications for approval updates via SSE and webhooks.
    """
    
    def __init__(self):
        self.sse_clients: Dict[str, Set[asyncio.Queue]] = {}  # user_id -> set of queues
        self.webhook_subscriptions: Dict[str, str] = {}  # approval_id -> webhook_url
        self._running = False
    
    async def start(self):
        """Start the notification manager and subscribe to events"""
        if self._running:
            return
        
        # Subscribe to approval-related events
        await trigger_mesh.subscribe("approval.requested", self._handle_approval_requested)
        await trigger_mesh.subscribe("approval.granted", self._handle_approval_granted)
        await trigger_mesh.subscribe("approval.rejected", self._handle_approval_rejected)
        
        self._running = True
        print("[OK] Approval notification manager started")
    
    async def stop(self):
        """Stop the notification manager"""
        self._running = False
        # Clear all SSE clients
        for queues in self.sse_clients.values():
            for queue in queues:
                await queue.put({"event": "shutdown", "data": {}})
        self.sse_clients.clear()
    
    # ========================================================================
    # SSE Management
    # ========================================================================
    
    def register_sse_client(self, user_id: str) -> asyncio.Queue:
        """
        Register a new SSE client for a user.
        
        Returns:
            Queue that will receive approval events
        """
        queue = asyncio.Queue(maxsize=100)
        
        if user_id not in self.sse_clients:
            self.sse_clients[user_id] = set()
        
        self.sse_clients[user_id].add(queue)
        
        return queue
    
    def unregister_sse_client(self, user_id: str, queue: asyncio.Queue):
        """Unregister an SSE client"""
        if user_id in self.sse_clients:
            self.sse_clients[user_id].discard(queue)
            if not self.sse_clients[user_id]:
                del self.sse_clients[user_id]
    
    async def broadcast_to_user(self, user_id: str, event_type: str, data: dict):
        """
        Broadcast an event to all SSE clients for a specific user.
        
        Args:
            user_id: User to notify
            event_type: Type of event (approval_requested, approval_granted, etc.)
            data: Event payload
        """
        if user_id not in self.sse_clients:
            return
        
        message = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Send to all clients for this user
        dead_queues = set()
        for queue in self.sse_clients[user_id]:
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                # Queue is full, client is slow - mark for removal
                dead_queues.add(queue)
            except Exception:
                dead_queues.add(queue)
        
        # Remove dead queues
        for queue in dead_queues:
            self.sse_clients[user_id].discard(queue)
    
    async def sse_stream(self, user_id: str, queue: asyncio.Queue) -> AsyncGenerator[str, None]:
        """
        Generate SSE stream for a client.
        
        Yields:
            Formatted SSE messages
        """
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'event': 'connected', 'user_id': user_id})}\n\n"
            
            # Keep connection alive and send events
            while self._running:
                try:
                    # Wait for event with timeout (for keepalive)
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    
                    if message.get("event") == "shutdown":
                        break
                    
                    # Format as SSE
                    event_type = message.get("event", "message")
                    data = json.dumps(message.get("data", {}))
                    
                    yield f"event: {event_type}\n"
                    yield f"data: {data}\n\n"
                    
                except asyncio.TimeoutError:
                    # Send keepalive comment
                    yield ": keepalive\n\n"
                    
        except asyncio.CancelledError:
            pass
        finally:
            self.unregister_sse_client(user_id, queue)
    
    # ========================================================================
    # Webhook Management
    # ========================================================================
    
    def register_webhook(self, approval_id: str, webhook_url: str):
        """
        Register a webhook for approval updates.
        
        Args:
            approval_id: Approval to watch
            webhook_url: URL to POST updates to
        """
        self.webhook_subscriptions[approval_id] = webhook_url
        
        # Log registration
        asyncio.create_task(
            immutable_log.append(
                actor="approval_notifications",
                action="webhook_registered",
                resource=f"approval_{approval_id}",
                subsystem="notifications",
                payload={"webhook_url": webhook_url},
                result="registered"
            )
        )
    
    def unregister_webhook(self, approval_id: str):
        """Unregister a webhook"""
        self.webhook_subscriptions.pop(approval_id, None)
    
    async def trigger_webhook(self, approval_id: str, event_type: str, data: dict):
        """
        Trigger a webhook for an approval event.
        
        Args:
            approval_id: Approval ID
            event_type: Event type
            data: Event payload
        """
        webhook_url = self.webhook_subscriptions.get(approval_id)
        if not webhook_url:
            return
        
        import aiohttp
        
        payload = {
            "event": event_type,
            "approval_id": approval_id,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status >= 400:
                        raise Exception(f"Webhook returned {response.status}")
            
            # Log success
            await immutable_log.append(
                actor="approval_notifications",
                action="webhook_triggered",
                resource=f"approval_{approval_id}",
                subsystem="notifications",
                payload={"event_type": event_type, "webhook_url": webhook_url},
                result="success"
            )
            
        except Exception as e:
            # Log failure
            await immutable_log.append(
                actor="approval_notifications",
                action="webhook_failed",
                resource=f"approval_{approval_id}",
                subsystem="notifications",
                payload={
                    "event_type": event_type,
                    "webhook_url": webhook_url,
                    "error": str(e)
                },
                result="failed"
            )
    
    # ========================================================================
    # Event Handlers
    # ========================================================================
    
    async def _handle_approval_requested(self, event: TriggerEvent):
        """Handle approval.requested event"""
        payload = event.payload
        approval_id = payload.get("approval_id")
        requested_by = payload.get("requested_by")
        
        # Notify the requester
        if requested_by:
            await self.broadcast_to_user(
                requested_by,
                "approval_requested",
                payload
            )
        
        # Trigger webhook if registered
        if approval_id:
            await self.trigger_webhook(str(approval_id), "approval_requested", payload)
    
    async def _handle_approval_granted(self, event: TriggerEvent):
        """Handle approval.granted event"""
        payload = event.payload
        approval_id = payload.get("approval_id")
        
        # Notify all potential stakeholders (simplified - in production, query DB)
        # For now, broadcast to all connected clients
        for user_id in list(self.sse_clients.keys()):
            await self.broadcast_to_user(
                user_id,
                "approval_granted",
                payload
            )
        
        # Trigger webhook
        if approval_id:
            await self.trigger_webhook(str(approval_id), "approval_granted", payload)
    
    async def _handle_approval_rejected(self, event: TriggerEvent):
        """Handle approval.rejected event"""
        payload = event.payload
        approval_id = payload.get("approval_id")
        
        # Notify all potential stakeholders
        for user_id in list(self.sse_clients.keys()):
            await self.broadcast_to_user(
                user_id,
                "approval_rejected",
                payload
            )
        
        # Trigger webhook
        if approval_id:
            await self.trigger_webhook(str(approval_id), "approval_rejected", payload)


# Global singleton
approval_notifications = ApprovalNotificationManager()
