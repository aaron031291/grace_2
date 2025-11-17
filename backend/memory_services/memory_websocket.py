"""
Memory WebSocket Handler
Real-time updates for file changes, Grace actions, pipeline progress
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Set, Dict, Any
import json
from datetime import datetime

from backend.clarity import get_event_bus, Event


class MemoryWebSocketManager:
    """Manage WebSocket connections for real-time Memory Studio updates"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.event_bus = get_event_bus()
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to Memory Studio real-time updates"
        })
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.discard(websocket)
        
        # Remove from all subscriptions
        for subscribers in self.subscriptions.values():
            subscribers.discard(websocket)
    
    async def subscribe(self, websocket: WebSocket, event_type: str):
        """Subscribe to specific event types"""
        if event_type not in self.subscriptions:
            self.subscriptions[event_type] = set()
        self.subscriptions[event_type].add(websocket)
        
        await websocket.send_json({
            "type": "subscribed",
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def broadcast_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_to_subscribers(self, event_type: str, message: Dict[str, Any]):
        """Broadcast to clients subscribed to specific event type"""
        if event_type not in self.subscriptions:
            return
        
        disconnected = []
        
        for connection in self.subscriptions[event_type]:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Clean up
        for conn in disconnected:
            self.subscriptions[event_type].discard(conn)
    
    async def send_file_update(self, file_path: str, action: str, metadata: Dict = None):
        """Notify about file changes"""
        message = {
            "type": "file_update",
            "action": action,  # created, updated, deleted
            "file_path": file_path,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        await self.broadcast_all(message)
    
    async def send_pipeline_progress(
        self, 
        job_id: str, 
        pipeline_id: str,
        progress: int,
        stage: str
    ):
        """Notify about pipeline progress"""
        message = {
            "type": "pipeline_progress",
            "job_id": job_id,
            "pipeline_id": pipeline_id,
            "progress": progress,
            "stage": stage,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_subscribers("pipeline_updates", message)
    
    async def send_grace_action(self, action: Dict[str, Any]):
        """Notify about Grace's autonomous actions"""
        message = {
            "type": "grace_action",
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_subscribers("grace_activity", message)
    
    async def send_notification(self, notification: Dict[str, Any]):
        """Send notification to all clients"""
        message = {
            "type": "notification",
            "notification": notification,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_all(message)


# Global manager
ws_manager = MemoryWebSocketManager()


# WebSocket endpoint handler
async def memory_websocket_handler(websocket: WebSocket):
    """
    Main WebSocket handler for Memory Studio
    
    Client can send:
    - {"action": "subscribe", "event_type": "grace_activity"}
    - {"action": "subscribe", "event_type": "pipeline_updates"}
    - {"action": "ping"}
    """
    
    await ws_manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            action = message.get("action")
            
            if action == "subscribe":
                event_type = message.get("event_type")
                if event_type:
                    await ws_manager.subscribe(websocket, event_type)
            
            elif action == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif action == "get_status":
                # Send current status
                await websocket.send_json({
                    "type": "status",
                    "active_connections": len(ws_manager.active_connections),
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


async def start_event_listener():
    """
    Listen to Clarity event bus and broadcast to WebSocket clients
    Should be started on app startup
    """
    event_bus = get_event_bus()
    
    # Define event handlers
    async def on_grace_action(event: Event):
        await ws_manager.send_grace_action(event.payload)
    
    async def on_pipeline_progress(event: Event):
        await ws_manager.send_pipeline_progress(
            event.payload.get("job_id"),
            event.payload.get("pipeline"),
            event.payload.get("progress", 0),
            event.payload.get("stage", "unknown")
        )
    
    async def on_file_update(event: Event):
        await ws_manager.send_file_update(
            event.payload.get("path"),
            event.payload.get("action", "updated"),
            event.payload.get("metadata")
        )
    
    # Subscribe to events
    # In real implementation, would use event bus subscription
    # For now, this is a stub framework
    pass
