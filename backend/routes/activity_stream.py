"""
Activity Stream WebSocket
Real-time stream of Grace's activities
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio

from ..activity_monitor import activity_monitor

router = APIRouter(prefix="/api/activity", tags=["Activity Stream"])


class ActivityStreamer:
    """Manages WebSocket connections for activity streaming"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Connect new client"""
        # Don't accept here - already accepted in route
        self.active_connections.append(websocket)
        
        # Send recent history
        recent_events = activity_monitor.get_recent_events(count=20)
        await websocket.send_json({
            'type': 'history',
            'events': recent_events
        })
        
        # Send current activity
        current = activity_monitor.get_current_activity()
        if current:
            await websocket.send_json({
                'type': 'current',
                'event': current
            })
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect client"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, event: dict):
        """Broadcast event to all connected clients"""
        for connection in self.active_connections[:]:
            try:
                await connection.send_json({
                    'type': 'event',
                    'event': event
                })
            except:
                self.active_connections.remove(connection)


streamer = ActivityStreamer()


@router.websocket("/stream")
async def activity_stream_ws(websocket: WebSocket):
    """
    WebSocket endpoint for real-time activity stream
    
    Connect and receive:
    - Recent activity history
    - Current activity
    - Live updates as Grace works
    """
    
    # Accept connection without auth for now
    await websocket.accept()
    
    await streamer.connect(websocket)
    
    try:
        while True:
            # Keep connection alive and handle messages
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                
                # Handle ping/pong
                if data == "ping":
                    await websocket.send_text("pong")
            
            except asyncio.TimeoutError:
                # Send keepalive
                try:
                    await websocket.send_json({'type': 'keepalive'})
                except:
                    break
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        streamer.disconnect(websocket)


@router.get("/recent")
async def get_recent_activity(count: int = 50):
    """Get recent activity events"""
    
    events = activity_monitor.get_recent_events(count=count)
    
    return {
        'events': events,
        'count': len(events)
    }


@router.get("/current")
async def get_current_activity():
    """Get what Grace is currently doing"""
    
    current = activity_monitor.get_current_activity()
    
    return {
        'current_activity': current,
        'active': current is not None
    }
