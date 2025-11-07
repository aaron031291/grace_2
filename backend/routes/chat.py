from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from datetime import datetime
from ..auth import get_current_user
from ..memory import PersistentMemory
from ..grace import GraceAutonomous
from ..causal import causal_tracker
from ..hunter import hunter
from ..models import ChatMessage, async_session
from ..agentic_error_handler import agentic_error_handler
from ..memory_learning_pipeline import memory_learning_pipeline, MemoryClassification

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    domain: str = "all"

class ChatResponse(BaseModel):
    response: str
    domain: str = None
    metadata: dict = None

memory = PersistentMemory()
grace = GraceAutonomous(memory=memory)

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    current_user: str = Depends(get_current_user),
):
    """
    Chat endpoint with full agentic error handling.
    
    Errors are instantly captured, sent to Trigger Mesh, and autonomously triaged.
    """
    
    start_time = datetime.utcnow()
    
    # Use agentic error tracking
    async with agentic_error_handler.track_operation(
        operation="chat_message",
        user=current_user,
        context={"message": req.message[:200], "domain": req.domain}
    ) as operation_id:
        
        # Security inspection
        alerts = await hunter.inspect(current_user, "chat_message", req.message, {"content": req.message})
        if alerts:
            print(f"⚠️ Hunter: {len(alerts)} alerts on chat message")
            await agentic_error_handler.capture_warning(
                source="hunter",
                message=f"{len(alerts)} security alerts detected",
                severity="medium",
                context={"alerts": len(alerts)}
            )
        
        # Store user message
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
        
        # Generate response
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
        
        # Track causal relationship
        await causal_tracker.log_interaction(current_user, trigger_id, response_id)
        
        # Capture conversation in learning pipeline
        user_mem_id, grace_mem_id = await memory_learning_pipeline.capture_conversation_turn(
            user=current_user,
            user_message=req.message,
            grace_response=result,
            metadata={"domain": req.domain, "operation_id": operation_id}
        )
        
        return ChatResponse(
            response=result,
            domain=req.domain,
            metadata={
                "operation_id": operation_id,
                "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                "user_memory_id": user_mem_id,
                "grace_memory_id": grace_mem_id
            }
        )
