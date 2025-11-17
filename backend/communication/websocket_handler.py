"""
WebSocket Handler for Grace Backend

Provides real-time communication for:
- Cockpit interface
- Frontend dashboards
- Live status updates
- Interactive commands
"""

import logging
from typing import Dict, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections and message routing"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.client_states: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.client_states[websocket] = {
            "client_id": client_id or f"client_{id(websocket)}",
            "connected_at": datetime.now().isoformat(),
            "subscriptions": set()
        }
        logger.info(f"WebSocket client connected: {self.client_states[websocket]['client_id']}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
        if websocket in self.client_states:
            client_id = self.client_states[websocket]["client_id"]
            del self.client_states[websocket]
            logger.info(f"WebSocket client disconnected: {client_id}")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message to client: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any], exclude: Optional[WebSocket] = None):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            if connection != exclude:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to broadcast to client: {e}")
                    disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def handle_message(self, websocket: WebSocket, data: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        try:
            message_type = data.get("type", "unknown")

            if message_type == "ping":
                await self.send_personal_message({"type": "pong", "timestamp": datetime.now().isoformat()}, websocket)

            elif message_type == "subscribe":
                # Handle subscription requests
                subscriptions = data.get("subscriptions", [])
                self.client_states[websocket]["subscriptions"].update(subscriptions)
                await self.send_personal_message({
                    "type": "subscribed",
                    "subscriptions": list(self.client_states[websocket]["subscriptions"])
                }, websocket)

            elif message_type == "chat":
                # Handle chat messages
                message = data.get("message", "")
                # Echo back for now - could integrate with LLM
                await self.send_personal_message({
                    "type": "chat_response",
                    "message": f"Echo: {message}",
                    "timestamp": datetime.now().isoformat()
                }, websocket)

            elif message_type == "status_request":
                # Send current status
                status = await self.get_system_status()
                await self.send_personal_message({
                    "type": "status_update",
                    "status": status
                }, websocket)

            else:
                # Unknown message type
                await self.send_personal_message({
                    "type": "error",
                    "error": f"Unknown message type: {message_type}"
                }, websocket)

        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self.send_personal_message({
                "type": "error",
                "error": str(e)
            }, websocket)

    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status for WebSocket clients"""
        try:
            # Import here to avoid circular imports
            from .cognition_metrics import get_metrics_engine

            engine = get_metrics_engine()
            status = engine.get_status()

            return {
                "overall_health": status.get("overall_health", 0),
                "overall_trust": status.get("overall_trust", 0),
                "overall_confidence": status.get("overall_confidence", 0),
                "saas_ready": status.get("saas_ready", False),
                "domains": status.get("domains", {}),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "overall_health": 50.0,
                "overall_trust": 50.0,
                "overall_confidence": 50.0,
                "saas_ready": False,
                "domains": {},
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global WebSocket manager instance
websocket_manager = WebSocketManager()

async def websocket_endpoint(websocket: WebSocket, client_id: Optional[str] = None):
    """WebSocket endpoint handler"""
    await websocket_manager.connect(websocket, client_id)

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()

            # Handle message
            await websocket_manager.handle_message(websocket, data)

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)