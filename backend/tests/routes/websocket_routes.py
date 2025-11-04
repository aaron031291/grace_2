from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from ..websocket_manager import ws_manager
from ..auth import get_current_user

router = APIRouter()

@router.websocket("/ws/{channel}")
async def websocket_endpoint(
    websocket: WebSocket,
    channel: str,
    token: str = Query(...)
):
    """WebSocket endpoint for real-time updates"""
    
    try:
        from jose import jwt
        from ..auth import get_secret_key, ALGORITHM
        
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        if not username:
            await websocket.close(code=1008)
            return
        
        await ws_manager.connect(websocket, username, channel)
        
        try:
            while True:
                data = await websocket.receive_text()
                # Echo or handle client messages if needed
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket, username, channel)
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=1011)

@router.websocket("/ws/meta-updates")
async def meta_updates_websocket(
    websocket: WebSocket,
    token: str = Query(...)
):
    """WebSocket for meta-loop recommendation updates"""
    try:
        from jose import jwt
        from ..auth import get_secret_key, ALGORITHM
        
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        if not username:
            await websocket.close(code=1008)
            return
        
        await websocket.accept()
        await ws_manager.connect(websocket, username, "meta-updates")
        
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket, username, "meta-updates")
    
    except Exception as e:
        print(f"Meta-updates WebSocket error: {e}")
        try:
            await websocket.close(code=1011)
        except:
            pass
