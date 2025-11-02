from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..auth import get_current_user
from ..memory import PersistentMemory
from ..grace import GraceAutonomous

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

memory = PersistentMemory()
grace = GraceAutonomous(memory=memory)

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    current_user: str = Depends(get_current_user),
):
    await memory.store(current_user, "user", req.message)
    result = await grace.respond(current_user, req.message)
    await memory.store(current_user, "grace", result)
    return ChatResponse(response=result)
