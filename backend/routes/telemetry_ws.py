"""
WebSocket endpoint for real-time telemetry streaming
Pushes live updates to dashboards for Layer 1-4 views
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import asyncio
import json
from datetime import datetime
from backend.kernels.kernel_registry import KernelRegistry
from backend.memory_services.htm_queue import HTMQueue
from backend.crypto.crypto_health import CryptoHealthMonitor

router = APIRouter()

# Active WebSocket connections
active_connections: Set[WebSocket] = set()


class TelemetryBroadcaster:
    """Broadcasts telemetry data to all connected clients"""

    def __init__(self):
        self.running = False

    async def start_broadcasting(self):
        """Start the broadcast loop"""
        self.running = True
        while self.running:
            try:
                # Gather all telemetry data
                telemetry = await self.gather_telemetry()

                # Broadcast to all connected clients
                await self.broadcast(telemetry)

                # Wait before next broadcast
                await asyncio.sleep(2)  # Update every 2 seconds
            except Exception as e:
                print(f"Broadcast error: {e}")
                await asyncio.sleep(5)

    async def gather_telemetry(self) -> Dict:
        """Gather all telemetry data from various sources"""
        telemetry = {
            "timestamp": datetime.utcnow().isoformat(),
            "kernels": await self.get_kernel_telemetry(),
            "htm": await self.get_htm_telemetry(),
            "crypto": await self.get_crypto_telemetry(),
        }
        return telemetry

    async def get_kernel_telemetry(self) -> Dict:
        """Get real-time kernel metrics"""
        try:
            registry = KernelRegistry()
            kernels = await registry.get_all_kernels()

            active = sum(1 for k in kernels if k.status == "active")
            idle = sum(1 for k in kernels if k.status == "idle")
            errors = sum(1 for k in kernels if k.status == "error")

            return {
                "total": len(kernels),
                "active": active,
                "idle": idle,
                "errors": errors,
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_htm_telemetry(self) -> Dict:
        """Get real-time HTM queue metrics"""
        try:
            htm_queue = HTMQueue()
            stats = await htm_queue.get_queue_metrics()

            return {
                "queue_depth": stats.get("depth", 0),
                "pending": stats.get("pending", 0),
                "active": stats.get("active", 0),
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_crypto_telemetry(self) -> Dict:
        """Get real-time crypto health"""
        try:
            monitor = CryptoHealthMonitor()
            health = await monitor.get_health_status()

            return {
                "status": health.get("status", "unknown"),
                "signatures_validated": health.get("signatures_validated", 0),
                "signature_failures": health.get("signature_failures", 0),
            }
        except Exception as e:
            return {"error": str(e)}

    async def broadcast(self, message: Dict):
        """Broadcast message to all connected clients"""
        disconnected = set()

        for connection in active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # Remove disconnected clients
        for connection in disconnected:
            active_connections.discard(connection)

    def stop(self):
        """Stop the broadcaster"""
        self.running = False


# Global broadcaster instance
broadcaster = TelemetryBroadcaster()


@router.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    """WebSocket endpoint for real-time telemetry streaming"""
    await websocket.accept()
    active_connections.add(websocket)

    try:
        # Send initial state
        initial_state = await broadcaster.gather_telemetry()
        await websocket.send_json(initial_state)

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for client messages (ping/pong)
                data = await websocket.receive_text()

                # Handle client commands
                if data == "ping":
                    await websocket.send_json({"type": "pong"})

            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                break

    finally:
        active_connections.discard(websocket)


async def start_telemetry_broadcaster():
    """Start the telemetry broadcaster (call from app startup)"""
    asyncio.create_task(broadcaster.start_broadcasting())


async def stop_telemetry_broadcaster():
    """Stop the telemetry broadcaster (call from app shutdown)"""
    broadcaster.stop()
