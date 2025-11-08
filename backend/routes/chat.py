from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from datetime import datetime
import logging
import asyncio
import re
from ..auth import get_current_user
from ..memory import PersistentMemory
from ..grace import GraceAutonomous
from ..causal import causal_tracker
from ..hunter import hunter
from ..models import ChatMessage, async_session
from ..agentic_error_handler import agentic_error_handler
from ..memory_learning_pipeline import memory_learning_pipeline, MemoryClassification

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Hardening: Timeout configuration
CHAT_TIMEOUT_SECONDS = 30
MAX_MESSAGE_LENGTH = 4000
SUSPICIOUS_PATTERNS = [
    r'<script',
    r'javascript:',
    r'onerror=',
    r'onclick=',
    r'\beval\s*\(',
    r'\balert\s*\('
]

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=MAX_MESSAGE_LENGTH, description="User message")
    domain: str = Field(default="all", pattern="^(all|core|knowledge|ml|security|transcendence)$")
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        
        # Hardening: Check for suspicious patterns
        stripped = v.strip()
        for pattern in SUSPICIOUS_PATTERNS:
            if re.search(pattern, stripped, re.IGNORECASE):
                raise ValueError('Message contains potentially unsafe content')
        
        # Hardening: Check for excessive whitespace (potential DoS)
        if len(stripped) < len(v) * 0.1:
            raise ValueError('Message contains excessive whitespace')
        
        return stripped

class ChatResponse(BaseModel):
    response: str
    domain: str = None
    metadata: dict = None
    degraded: bool = False
    request_id: str = None

memory = PersistentMemory()
grace = GraceAutonomous(memory=memory)

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    current_user: str = Depends(get_current_user),
):
    """
    Hardened chat endpoint with comprehensive error handling and graceful degradation.
    
    Hardening includes:
    - Input validation (XSS, injection protection)
    - Timeout controls (30s max)
    - Database transaction safety
    - GraceAutonomous fallback handling
    - Network abort controls
    - Never returns 500 - always provides fallback response
    """
    
    logger = logging.getLogger(__name__)
    start_time = datetime.utcnow()
    request_id = None
    degraded = False
    
    # Hardening: Wrap entire operation with timeout
    try:
        return await asyncio.wait_for(
            _process_chat_message(req, current_user, logger, start_time),
            timeout=CHAT_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        logger.error(f"Chat request timed out after {CHAT_TIMEOUT_SECONDS}s")
        return ChatResponse(
            response="Request processing timed out. Please try a simpler query or try again.",
            domain=req.domain,
            degraded=True,
            metadata={"error": "timeout", "timeout_seconds": CHAT_TIMEOUT_SECONDS}
        )
    except Exception as e:
        logger.error(f"Critical chat endpoint failure: {e}", exc_info=True)
        return ChatResponse(
            response="An unexpected error occurred. The system is still operational.",
            domain=req.domain,
            degraded=True,
            metadata={"error": str(e)[:200]}
        )


async def _process_chat_message(
    req: ChatRequest,
    current_user: str,
    logger,
    start_time: datetime
) -> ChatResponse:
    """Internal processing function with database transaction safety"""
    
    request_id = None
    degraded = False
    
    # Use agentic error tracking
    try:
        async with agentic_error_handler.track_operation(
            operation="chat_message",
            user=current_user,
            context={"message": req.message[:200], "domain": req.domain}
        ) as operation_id:
            request_id = operation_id
            
            # Security inspection (best-effort, non-blocking)
            try:
                alerts = await asyncio.wait_for(
                    hunter.inspect(current_user, "chat_message", req.message, {"content": req.message}),
                    timeout=5.0
                )
                if alerts:
                    print(f"[WARN] Hunter: {len(alerts)} alerts on chat message")
                    await agentic_error_handler.capture_warning(
                        source="hunter",
                        message=f"{len(alerts)} security alerts detected",
                        severity="medium",
                        context={"alerts": len(alerts)}
                    )
            except asyncio.TimeoutError:
                logger.warning("Hunter inspection timed out, continuing without security check")
            except Exception as e:
                logger.warning(f"Hunter inspection failed: {e}, continuing without security check")
            
            # Hardening: Database transaction safety for message storage
            trigger_id = None
            try:
                await memory.store(current_user, "user", req.message)
                
                async with async_session() as session:
                    async with session.begin():
                        result = await session.execute(
                            select(ChatMessage)
                            .where(ChatMessage.user == current_user)
                            .order_by(ChatMessage.created_at.desc())
                            .limit(1)
                        )
                        user_msg = result.scalar_one_or_none()
                        if user_msg:
                            trigger_id = user_msg.id
            except Exception as e:
                logger.error(f"Failed to store user message: {e}", exc_info=True)
            
            # Hardening: GraceAutonomous with timeout and fallback
            try:
                result = await asyncio.wait_for(
                    grace.respond(current_user, req.message),
                    timeout=25.0
                )
            except asyncio.TimeoutError:
                logger.error("Grace response timed out, using fallback")
                result = "I'm taking longer than usual to process this. Please try again or simplify your request."
                degraded = True
            except Exception as e:
                logger.error(f"Grace processing failed: {e}, using fallback", exc_info=True)
                result = "I encountered an issue processing your request. Please try again."
                degraded = True
            
            # Store Grace response
            response_id = None
            try:
                await memory.store(current_user, "grace", result)
                
                async with async_session() as session:
                    async with session.begin():
                        result_query = await session.execute(
                            select(ChatMessage)
                            .where(ChatMessage.user == current_user)
                            .order_by(ChatMessage.created_at.desc())
                            .limit(1)
                        )
                        response_msg = result_query.scalar_one_or_none()
                        if response_msg:
                            response_id = response_msg.id
            except Exception as e:
                logger.error(f"Failed to store Grace response: {e}", exc_info=True)
            
            # Track causal relationship (best-effort)
            if trigger_id and response_id:
                try:
                    await causal_tracker.log_interaction(current_user, trigger_id, response_id)
                except Exception as e:
                    logger.warning(f"Failed to track causal relationship: {e}")
            
            # Capture conversation in learning pipeline (best-effort)
            user_mem_id, grace_mem_id = None, None
            try:
                user_mem_id, grace_mem_id = await memory_learning_pipeline.capture_conversation_turn(
                    user=current_user,
                    user_message=req.message,
                    grace_response=result,
                    metadata={"domain": req.domain, "operation_id": operation_id}
                )
            except Exception as e:
                logger.warning(f"Failed to capture conversation in learning pipeline: {e}")
            
            return ChatResponse(
                response=result,
                domain=req.domain,
                degraded=degraded,
                request_id=operation_id,
                metadata={
                    "operation_id": operation_id,
                    "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                    "user_memory_id": user_mem_id,
                    "grace_memory_id": grace_mem_id
                }
            )
    
    except Exception as outer_error:
        logger.error(f"Unhandled error in chat processing: {outer_error}", exc_info=True)
        return ChatResponse(
            response="An unexpected error occurred while processing your message. The system remains operational.",
            domain=req.domain,
            degraded=True,
            metadata={"error": str(outer_error)[:200]}
        )
