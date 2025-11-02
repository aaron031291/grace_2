from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Set
import json
from jose import jwt

router = APIRouter()

class WebSocketClient:
    def __init__(self, websocket: WebSocket, user: str):
        self.websocket = websocket
        self.user = user
        self.subscriptions: Set[str] = set()
    
    async def accept(self):
        await self.websocket.accept()
    
    async def send(self, message: dict):
        await self.websocket.send_json(message)
    
    async def receive(self):
        return await self.websocket.receive_json()
    
    async def close(self):
        await self.websocket.close()

class IDEWebSocketManager:
    def __init__(self):
        self.active_clients: Dict[str, WebSocketClient] = {}
    
    async def connect(self, client: WebSocketClient):
        self.active_clients[client.user] = client
        await client.send({"type": "connected", "user": client.user})
    
    def disconnect(self, user: str):
        if user in self.active_clients:
            del self.active_clients[user]
    
    async def broadcast(self, message: dict, exclude: str = None):
        disconnected = []
        for user, client in self.active_clients.items():
            if user != exclude:
                try:
                    await client.send(message)
                except:
                    disconnected.append(user)
        
        for user in disconnected:
            self.disconnect(user)

ide_ws_manager = IDEWebSocketManager()

@router.websocket("/ide/ws")
async def ide_websocket(websocket: WebSocket, token: str = Query(...)):
    """Main IDE WebSocket endpoint"""
    
    try:
        from backend.auth import SECRET_KEY, ALGORITHM
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        if not username:
            await websocket.close(code=1008)
            return
        
        client = WebSocketClient(websocket, username)
        await client.accept()
        await ide_ws_manager.connect(client)
        
        from .handlers import dispatch_message
        
        try:
            while True:
                message = await client.receive()
                response = await dispatch_message(client, message)
                if response:
                    await client.send(response)
        except WebSocketDisconnect:
            ide_ws_manager.disconnect(username)
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=1011)
