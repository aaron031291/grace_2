"""
Cognition API Routes - Central Authority for Intent & Planning

Exposes cognition domain as the decision-making authority:
- Intent parsing
- Plan creation
- Execution orchestration
- Status tracking

LLM calls these endpoints instead of making decisions directly.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..cognition_intent import cognition_authority, CognitionIntent
from ..capability_registry import capability_registry
from ..auth import get_current_user
from ..models import async_session
from ..schemas import (
    CognitionIntentParseResponse, CognitionExecuteResponse, CognitionSessionResponse,
    CognitionRecentIntentsResponse, CognitionCapabilitiesResponse, CognitionLLMToolsResponse,
    CognitionStatusResponse
)

router = APIRouter(prefix="/api/cognition", tags=["cognition"])


# ============= Request/Response Models =============

class IntentRequest(BaseModel):
    utterance: str
    context: Optional[Dict[str, Any]] = None


class IntentResponse(BaseModel):
    intent_id: int
    intent_type: str
    confidence: float
    plan_id: Optional[str] = None
    status: str
    requires_approval: bool = False
    approval_id: Optional[str] = None


class ExecuteRequest(BaseModel):
    intent_type: str
    parameters: Dict[str, Any]


# ============= Intent Endpoints =============

@router.post("/intent/parse", response_model=CognitionIntentParseResponse)
async def parse_intent(
    req: IntentRequest,
    user=Depends(get_current_user)
):
    """
    Parse user utterance into structured intent.
    
    This is the entry point for all user requests.
    Returns intent without execution.
    """
    
    intent = await cognition_authority.parse_intent(
        utterance=req.utterance,
        user_id=user.username,
        context=req.context
    )
    
    return {
        "intent_type": intent.type,
        "parameters": intent.parameters,
        "confidence": intent.confidence,
        "context": intent.context
    }


@router.post("/intent/execute", response_model=CognitionExecuteResponse)
async def execute_intent(
    req: ExecuteRequest,
    user=Depends(get_current_user)
):
    """
    Execute a structured intent directly.
    Bypasses parsing, goes straight to planning & execution.
    """
    
    from dataclasses import asdict
    
    # Create plan
    from ..cognition_intent import Intent
    intent = Intent(
        type=req.intent_type,
        parameters=req.parameters
    )
    
    plan = await cognition_authority.create_plan(intent)
    
    # Execute
    result = await cognition_authority.execute_plan(
        plan=plan,
        session_id=f"{user.username}-{datetime.now().timestamp()}"
    )
    
    return {
        "plan_id": plan.plan_id,
        "success": result.success,
        "actions_completed": result.actions_completed,
        "actions_failed": result.actions_failed,
        "outputs": result.outputs,
        "verification": result.verification,
        "rollback_available": result.rollback_available,
        "confidence": result.confidence
    }


@router.post("/request")
async def process_request(
    req: IntentRequest,
    user=Depends(get_current_user)
):
    """
    Complete flow: Parse -> Plan -> Execute -> Return structured result.
    
    This is the main endpoint for cognition-driven requests.
    """
    
    result = await cognition_authority.process_user_request(
        utterance=req.utterance,
        user_id=user.username,
        session_id=f"{user.username}-{datetime.now().timestamp()}"
    )
    
    return result


# ============= Session & History =============

@router.get("/session/{session_id}", response_model=CognitionSessionResponse)
async def get_session_status(
    session_id: str,
    user=Depends(get_current_user)
):
    """
    Get cognition session status.
    Shows "brain activity" - what cognition is thinking/doing.
    """
    
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(CognitionIntent)
            .where(CognitionIntent.session_id == session_id)
            .order_by(CognitionIntent.created_at.desc())
        )
        intents = result.scalars().all()
        
        return {
            "session_id": session_id,
            "intents": [
                {
                    "id": i.id,
                    "utterance": i.raw_utterance,
                    "intent_type": i.intent_type,
                    "status": i.status,
                    "plan_id": i.plan_id,
                    "requires_approval": i.requires_approval,
                    "created_at": i.created_at.isoformat() if i.created_at else None,
                    "completed_at": i.completed_at.isoformat() if i.completed_at else None
                }
                for i in intents
            ]
        }


@router.get("/intents/recent", response_model=CognitionRecentIntentsResponse)
async def get_recent_intents(
    limit: int = 20,
    user=Depends(get_current_user)
):
    """Get recent cognition intents for user"""
    
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(CognitionIntent)
            .where(CognitionIntent.user_id == user.username)
            .order_by(CognitionIntent.created_at.desc())
            .limit(limit)
        )
        intents = result.scalars().all()
        
        return {
            "intents": [
                {
                    "id": i.id,
                    "utterance": i.raw_utterance,
                    "intent_type": i.intent_type,
                    "status": i.status,
                    "confidence": i.confidence_score,
                    "created_at": i.created_at.isoformat() if i.created_at else None
                }
                for i in intents
            ]
        }


# ============= Capabilities =============

@router.get("/capabilities", response_model=CognitionCapabilitiesResponse)
async def list_capabilities():
    """
    List all available capabilities.
    
    This is the "tool manifest" that LLM sees.
    LLM can ONLY request actions listed here.
    """
    
    return {
        "capabilities": capability_registry.get_all_capabilities(),
        "count": len(capability_registry.capabilities)
    }


@router.get("/capabilities/llm-tools", response_model=CognitionLLMToolsResponse)
async def get_llm_tools():
    """
    Get capabilities in OpenAI function calling format.
    
    Feed this to LLM as available tools.
    LLM requests tools, cognition validates and executes.
    """
    
    return {
        "tools": capability_registry.to_llm_tools()
    }


# ============= Status & Monitoring =============

@router.get("/status", response_model=CognitionStatusResponse)
async def get_cognition_status():
    """Get cognition system status"""
    
    from sqlalchemy import select, func
    
    async with async_session() as session:
        # Count intents by status
        total = await session.execute(
            select(func.count()).select_from(CognitionIntent)
        )
        total_count = total.scalar() or 0
        
        completed = await session.execute(
            select(func.count())
            .select_from(CognitionIntent)
            .where(CognitionIntent.status == "completed")
        )
        completed_count = completed.scalar() or 0
        
        failed = await session.execute(
            select(func.count())
            .select_from(CognitionIntent)
            .where(CognitionIntent.status == "failed")
        )
        failed_count = failed.scalar() or 0
    
    return {
        "total_intents": total_count,
        "completed": completed_count,
        "failed": failed_count,
        "success_rate": (completed_count / total_count * 100) if total_count > 0 else 0,
        "capabilities_registered": len(capability_registry.capabilities),
        "status": "operational"
    }
