from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from ..auth import get_current_user
from ..memory import PersistentMemory
from ..grace import GraceAutonomous
from ..causal import causal_tracker
from ..hunter import hunter
from ..models import ChatMessage, async_session
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
    alerts = await hunter.inspect(current_user, "chat_message", req.message, {"content": req.message})
    if alerts:
        print(f"[WARN] Hunter: {len(alerts)} alerts on chat message")

    await memory.store(current_user, "user", req.message)

    async with async_session() as session:
        result = await session.execute(
            select(ChatMessage)
            .where(ChatMessage.user == current_user)
            .order_by(ChatMessage.created_at.desc())
            .limit(1)
        )
        user_msg = result.scalar_one()
        trigger_id = user_msg.id

    result = await grace.respond(current_user, req.message)
    await memory.store(current_user, "grace", result)

    async with async_session() as session:
        result_query = await session.execute(
            select(ChatMessage)
            .where(ChatMessage.user == current_user)
            .order_by(ChatMessage.created_at.desc())
            .limit(1)
        )
        response_msg = result_query.scalar_one()
        response_id = response_msg.id

    await causal_tracker.log_interaction(current_user, trigger_id, response_id)

    return ChatResponse(response=result)
