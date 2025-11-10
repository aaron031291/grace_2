
from fastapi import APIRouter, WebSocket
from ..multimodal_llm import multimodal_llm

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        response = await multimodal_llm.generate_response(user_message=data)
        await websocket.send_text(response.get("text", "Sorry, I encountered an error."))
