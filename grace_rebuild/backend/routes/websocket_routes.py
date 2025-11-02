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
        from ..auth import SECRET_KEY, ALGORITHM
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
