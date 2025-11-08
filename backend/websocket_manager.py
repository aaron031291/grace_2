from fastapi import WebSocket
from typing import Dict, Set
import json
import asyncio

class WebSocketManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.user_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user: str, channel: str = "default"):
        """Add new WebSocket connection"""
        await websocket.accept()
        
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        
        if user not in self.user_connections:
            self.user_connections[user] = set()
        self.user_connections[user].add(websocket)
        
        print(f"[OK] WebSocket connected: {user} on {channel}")
    
    def disconnect(self, websocket: WebSocket, user: str, channel: str = "default"):
        """Remove WebSocket connection"""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
        
        if user in self.user_connections:
            self.user_connections[user].discard(websocket)
        
        print(f"[OK] WebSocket disconnected: {user}")
    
    async def broadcast(self, message: dict, channel: str = "default"):
        """Broadcast message to all connections on channel"""
        if channel not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except:
                disconnected.add(connection)
        
        for conn in disconnected:
            self.active_connections[channel].discard(conn)
    
    async def send_to_user(self, user: str, message: dict):
        """Send message to specific user's connections"""
        if user not in self.user_connections:
            return
        
        disconnected = set()
        for connection in self.user_connections[user]:
            try:
                await connection.send_json(message)
            except:
                disconnected.add(connection)
        
        for conn in disconnected:
            self.user_connections[user].discard(conn)

ws_manager = WebSocketManager()

# Hook into Trigger Mesh to broadcast events
async def broadcast_event_handler(event):
    """Broadcast trigger mesh events via WebSocket"""
    await ws_manager.broadcast({
        "type": "event",
        "event_type": event.event_type,
        "source": event.source,
        "resource": event.resource,
        "timestamp": event.timestamp.isoformat()
    }, channel="events")

async def setup_ws_subscriptions():
    """Subscribe WebSocket manager to Trigger Mesh"""
    from .trigger_mesh import trigger_mesh
    trigger_mesh.subscribe("*", broadcast_event_handler)
    print("[OK] WebSocket subscribed to Trigger Mesh")


# Backwards compatibility alias for legacy imports
# Some modules expect a `websocket_manager` symbol; alias it to the existing instance `ws_manager`.
websocket_manager = ws_manager
