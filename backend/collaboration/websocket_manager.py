"""
Collaboration WebSocket Manager
Real-time presence, notifications, and activity tracking
"""
import asyncio
import logging
from typing import Dict, Set, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class CollaborationWebSocketManager:
    """Manages WebSocket connections for collaboration features"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, str] = {}
        self.room_subscriptions: Dict[str, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str, session_id: str):
        """Connect a user to collaboration WebSocket"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.user_connections[user_id] = session_id
        logger.info(f"👥 User {user_id} connected to collaboration WebSocket")
        
        await self.broadcast_presence_update({
            "type": "user_joined",
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def disconnect(self, session_id: str):
        """Disconnect user from collaboration WebSocket"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        
        user_id = None
        for uid, sid in self.user_connections.items():
            if sid == session_id:
                user_id = uid
                break
        
        if user_id:
            del self.user_connections[user_id]
            logger.info(f"👋 User {user_id} disconnected from collaboration")
            
            asyncio.create_task(self.broadcast_presence_update({
                "type": "user_left",
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }))
    
    async def subscribe_to_room(self, session_id: str, room: str):
        """Subscribe user to a room (file, table, etc.)"""
        if room not in self.room_subscriptions:
            self.room_subscriptions[room] = set()
        self.room_subscriptions[room].add(session_id)
    
    async def unsubscribe_from_room(self, session_id: str, room: str):
        """Unsubscribe user from a room"""
        if room in self.room_subscriptions:
            self.room_subscriptions[room].discard(session_id)
    
    async def send_personal_message(self, session_id: str, message: Dict[str, Any]):
        """Send message to specific user"""
        if session_id in self.active_connections:
            try:
                websocket = self.active_connections[session_id]
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {e}")
                self.disconnect(session_id)
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to user by user_id"""
        if user_id in self.user_connections:
            session_id = self.user_connections[user_id]
            await self.send_personal_message(session_id, message)
    
    async def broadcast_to_room(self, room: str, message: Dict[str, Any], exclude_session: str = None):
        """Broadcast message to all users in a room"""
        if room in self.room_subscriptions:
            for session_id in self.room_subscriptions[room]:
                if session_id != exclude_session:
                    await self.send_personal_message(session_id, message)
    
    async def broadcast_presence_update(self, update: Dict[str, Any]):
        """Broadcast presence update to all connected users"""
        disconnected = []
        
        for session_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(update)
            except Exception as e:
                logger.error(f"Failed to broadcast to {session_id}: {e}")
                disconnected.append(session_id)
        
        for session_id in disconnected:
            self.disconnect(session_id)
    
    async def notify_file_edit(self, file_path: str, editor_id: str, editor_name: str):
        """Notify users when file is being edited"""
        message = {
            "type": "file_edit_started",
            "file_path": file_path,
            "editor_id": editor_id,
            "editor_name": editor_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_room(f"file:{file_path}", message, exclude_session=editor_id)
    
    async def notify_file_edit_released(self, file_path: str, editor_id: str):
        """Notify users when file edit is released"""
        message = {
            "type": "file_edit_released",
            "file_path": file_path,
            "editor_id": editor_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_room(f"file:{file_path}", message)
    
    async def notify_workflow_update(self, workflow_id: str, update_type: str, details: Dict[str, Any]):
        """Notify users about workflow updates"""
        message = {
            "type": "workflow_update",
            "workflow_id": workflow_id,
            "update_type": update_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_room(f"workflow:{workflow_id}", message)
    
    async def send_notification(self, user_id: str, notification: Dict[str, Any]):
        """Send notification to specific user"""
        message = {
            "type": "notification",
            "notification": notification,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_to_user(user_id, message)
    
    async def handle_message(self, session_id: str, data: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        message_type = data.get("type")
        
        if message_type == "ping":
            await self.send_personal_message(session_id, {
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif message_type == "subscribe_room":
            room = data.get("room")
            if room:
                await self.subscribe_to_room(session_id, room)
                await self.send_personal_message(session_id, {
                    "type": "subscribed",
                    "room": room
                })
        
        elif message_type == "unsubscribe_room":
            room = data.get("room")
            if room:
                await self.unsubscribe_from_room(session_id, room)
                await self.send_personal_message(session_id, {
                    "type": "unsubscribed",
                    "room": room
                })
        
        elif message_type == "cursor_update":
            room = data.get("room")
            if room:
                await self.broadcast_to_room(room, {
                    "type": "cursor_update",
                    "session_id": session_id,
                    "cursor": data.get("cursor"),
                    "timestamp": datetime.utcnow().isoformat()
                }, exclude_session=session_id)


collaboration_ws_manager = CollaborationWebSocketManager()
