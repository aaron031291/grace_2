"""
Hardened Chat Endpoint - Production-grade error handling

Features:
- Input validation (length, domain enum)
- Comprehensive error handling (never crashes)
- Graceful degradation (always returns response)
- Safe database operations (scalar_one_or_none)
- Timeout protection
- Fallback responses
- Request ID tracking
"""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from datetime import datetime
import logging
import asyncio

from ..auth import get_current_user
from ..memory import PersistentMemory
from ..grace_agent import GraceAutonomous
from ..causal import causal_tracker
from ..hunter import hunter
from ..models import ChatMessage, async_session
from ..agentic_error_handler import agentic_error_handler
from ..memory_learning_pipeline import memory_learning_pipeline
from ..safe_helpers import safe_publish

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    domain: str = Field(default="all", pattern="^(all|core|knowledge|ml|security|transcendence)$")
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class ChatResponse(BaseModel):
    response: str
    domain: str = None
    metadata: dict = {}
    degraded: bool = False
    request_id: str = None


memory = PersistentMemory()
grace = GraceAutonomous(memory=memory)


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    request: Request,
    current_user: str = Depends(get_current_user),
):
    """
    Production-hardened chat endpoint.
    
    Guarantees:
    - Always returns 200 with response (even on errors)
    - Graceful degradation on subsystem failures
    - Comprehensive error logging
    - Request correlation via request_id
    """
    
    start_time = datetime.utcnow()
    request_id = getattr(request.state, "request_id", "unknown")
    degraded = False
    metadata = {"request_id": request_id}
    
    try:
        # Track operation with agentic error handler
        async with agentic_error_handler.track_operation(
            operation="chat_message",
            user=current_user,
            context={"message": req.message[:200], "domain": req.domain}
        ) as operation_id:
            
            metadata["operation_id"] = operation_id
            
            # Security inspection (best-effort, non-blocking)
            try:
                alerts = await asyncio.wait_for(
                    hunter.inspect(current_user, "chat_message", req.message, {"content": req.message}),
                    timeout=2.0
                )
                if alerts:
                    logger.warning(f"Hunter alerts: {len(alerts)} on chat message")
                    await safe_publish(
                        event_type="security.alerts_detected",
                        source="chat",
                        actor=current_user,
                        resource=operation_id,
                        payload={"alert_count": len(alerts)}
                    )
                    metadata["security_alerts"] = len(alerts)
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning(f"Hunter inspection failed: {e}")
                degraded = True
                metadata["hunter_skipped"] = True
            
            # Store user message (with fallback)
            try:
                await asyncio.wait_for(
                    memory.store(current_user, "user", req.message),
                    timeout=5.0
                )
            except Exception as e:
                logger.error(f"Failed to store user message: {e}")
                degraded = True
                metadata["memory_store_failed"] = True
            
            # Get user message ID (safe query)
            trigger_id = None
            try:
                async with async_session() as session:
                    user_msg_result = await session.execute(
                        select(ChatMessage)
                        .where(ChatMessage.user == current_user)
                        .order_by(ChatMessage.created_at.desc())
                        .limit(1)
                    )
                    user_msg = user_msg_result.scalar_one_or_none()
                    if user_msg:
                        trigger_id = user_msg.id
            except Exception as e:
                logger.error(f"Failed to get user message ID: {e}")
                degraded = True
            
            # Generate response (with timeout and fallback)
            response_text = None
            try:
                response_text = await asyncio.wait_for(
                    grace.respond(current_user, req.message),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                logger.error(f"Grace response timeout (30s)")
                response_text = "I apologize, but I'm taking longer than expected to process your request. Please try again."
                degraded = True
                metadata["response_timeout"] = True
            except Exception as e:
                logger.error(f"Grace response failed: {e}", exc_info=True)
                response_text = "I encountered an issue processing your request. Please try again or contact support."
                degraded = True
                metadata["response_error"] = str(e)
            
            # Store Grace response (best-effort)
            try:
                await asyncio.wait_for(
                    memory.store(current_user, "grace", response_text),
                    timeout=5.0
                )
            except Exception as e:
                logger.error(f"Failed to store Grace response: {e}")
                degraded = True
            
            # Get response message ID (safe query)
            response_id = None
            try:
                async with async_session() as session:
                    response_msg_result = await session.execute(
                        select(ChatMessage)
                        .where(ChatMessage.user == current_user)
                        .order_by(ChatMessage.created_at.desc())
                        .limit(1)
                    )
                    response_msg = response_msg_result.scalar_one_or_none()
                    if response_msg:
                        response_id = response_msg.id
            except Exception as e:
                logger.error(f"Failed to get response message ID: {e}")
                degraded = True
            
            # Track causal relationship (best-effort)
            if trigger_id and response_id:
                try:
                    await asyncio.wait_for(
                        causal_tracker.log_interaction(current_user, trigger_id, response_id),
                        timeout=2.0
                    )
                except Exception as e:
                    logger.warning(f"Causal tracking failed: {e}")
                    degraded = True
            
            # Capture in learning pipeline (best-effort)
            try:
                user_mem_id, grace_mem_id = await asyncio.wait_for(
                    memory_learning_pipeline.capture_conversation_turn(
                        user=current_user,
                        user_message=req.message,
                        grace_response=response_text,
                        metadata={"domain": req.domain, "operation_id": operation_id}
                    ),
                    timeout=3.0
                )
                metadata["user_memory_id"] = user_mem_id
                metadata["grace_memory_id"] = grace_mem_id
            except Exception as e:
                logger.warning(f"Learning pipeline capture failed: {e}")
                degraded = True
            
            # Calculate duration
            metadata["duration_ms"] = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return ChatResponse(
                response=response_text,
                domain=req.domain,
                metadata=metadata,
                degraded=degraded,
                request_id=request_id
            )
    
    except Exception as e:
        # Ultimate fallback - should never reach here
        logger.critical(f"Chat endpoint critical failure: {e}", exc_info=True)
        
        return ChatResponse(
            response="I'm experiencing technical difficulties. Please try again in a moment.",
            domain=req.domain,
            metadata={
                "request_id": request_id or "unknown",
                "critical_error": True,
                "error_type": type(e).__name__
            },
            degraded=True,
            request_id=request_id
        )
