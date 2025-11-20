"""
Unified Chat API - Single endpoint for all Grace interactions

Handles:
- Text, voice, and vision inputs
- Returns reply + voice_url + actions + telemetry + logs + citations
- Inline log retrieval on request
- Error surfacing with healing options
- World-model telemetry panels
- Governance approvals inline
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.openai_reasoner import openai_reasoner
from backend.services.rag_service import RAGService
from backend.services.log_service import log_service
from backend.world_model.world_model_service import world_model_service
from backend.action_gateway import action_gateway
from backend.reflection_loop import reflection_loop
from backend.event_bus import event_bus, Event, EventType
from backend.core.unified_event_publisher import publish_event_obj

router = APIRouter()

# In-memory conversation storage
conversations: Dict[str, List[Dict[str, Any]]] = {}


class UnifiedChatMessage(BaseModel):
    """Unified chat message - handles all input types"""
    message: str = Field(..., description="User message text or voice transcript")
    session_id: Optional[str] = Field(None, description="Session ID for continuity")
    user_id: str = Field(default="user", description="User identifier")
    
    # Optional context
    attachments: Optional[List[str]] = Field(default_factory=list, description="File attachments")
    vision_context: Optional[Dict[str, Any]] = Field(None, description="Screen/camera context")
    voice_enabled: bool = Field(default=False, description="Persistent voice session active")
    
    # Request-specific flags
    include_logs: bool = Field(default=False, description="Include recent logs")
    include_telemetry: bool = Field(default=True, description="Include system telemetry")


class ActionCard(BaseModel):
    """Action approval card for inline governance"""
    trace_id: str
    action_type: str
    tier: str
    justification: str
    params: Dict[str, Any]
    timestamp: str
    approved: bool = False
    requires_approval: bool = True


class TelemetryPanel(BaseModel):
    """System telemetry for UI panels"""
    health: str  # healthy, degraded, offline
    trust_score: float
    confidence: float
    pending_approvals: int
    active_tasks: int
    active_missions: int
    learning_jobs: int
    incidents: int
    timestamp: str


class LogSnippet(BaseModel):
    """Log entry for inline display"""
    log_type: str  # error, execution, healing, etc.
    timestamp: str
    message: str
    source: str
    severity: Optional[str] = None


class HealingOption(BaseModel):
    """Self-healing option for failed actions"""
    healing_id: str
    title: str
    description: str
    playbook: str
    confidence: float


class UnifiedChatResponse(BaseModel):
    """Comprehensive response from Grace"""
    # Core response
    reply: str
    trace_id: str
    session_id: str
    timestamp: str
    confidence: float
    
    # Voice (if enabled)
    voice_url: Optional[str] = None
    voice_transcript: Optional[str] = None
    
    # Actions & governance
    actions: List[ActionCard] = Field(default_factory=list)
    requires_approval: bool = False
    pending_approvals: List[ActionCard] = Field(default_factory=list)
    
    # Telemetry & monitoring
    telemetry: Optional[TelemetryPanel] = None
    
    # Logs & debugging
    logs: List[LogSnippet] = Field(default_factory=list)
    
    # Citations & sources
    citations: List[str] = Field(default_factory=list)
    
    # Error handling
    error: Optional[str] = None
    healing_options: List[HealingOption] = Field(default_factory=list)


@router.post("/unified/chat", response_model=UnifiedChatResponse)
async def unified_chat(msg: UnifiedChatMessage) -> UnifiedChatResponse:
    """
    Unified chat endpoint - single source of truth for all Grace interactions
    
    Flow:
    1. Detect if message is a log/telemetry request
    2. Assemble full context (RAG + world model + logs if needed)
    3. Call OpenAI reasoner
    4. Process actions through governance
    5. Fetch telemetry panels
    6. Generate voice response if voice_enabled
    7. Include error healing options if applicable
    8. Return comprehensive response
    """
    try:
        trace_id = f"chat_{uuid4().hex[:12]}"
        session_id = msg.session_id or f"session_{uuid4().hex[:8]}"
        
        if session_id not in conversations:
            conversations[session_id] = []
        
        # Publish event
        await publish_event_obj(Event(
            event_type=EventType.AGENT_ACTION,
            source="unified_chat_api",
            data={
                "action": "unified_chat_received",
                "user_id": msg.user_id,
                "voice_enabled": msg.voice_enabled,
                "has_vision": msg.vision_context is not None
            },
            trace_id=trace_id
        ))
        
        # Step 1: Detect log/telemetry requests
        log_intent = await detect_log_request(msg.message)
        logs_data = []
        
        if log_intent:
            # User is asking for logs
            log_results = await log_service.get_logs_by_intent(
                intent=msg.message,
                count=10
            )
            logs_data = [
                LogSnippet(
                    log_type=log_results.get("type", "general"),
                    timestamp=log.get("timestamp", datetime.now().isoformat()),
                    message=log.get("message", log.get("content", "")),
                    source=log.get("source", "unknown"),
                    severity=log.get("level")
                )
                for log in log_results.get("logs", [])
            ]
        elif msg.include_logs:
            # Include recent errors proactively
            recent_errors = await log_service.get_recent_errors(count=5)
            logs_data = [
                LogSnippet(
                    log_type="error",
                    timestamp=err.get("timestamp", ""),
                    message=err.get("message", ""),
                    source=err.get("source", ""),
                    severity=err.get("level")
                )
                for err in recent_errors
            ]
        
        # Step 2: Assemble context
        rag_service = RAGService()
        await rag_service.initialize()
        
        rag_results = await rag_service.retrieve(
            query=msg.message,
            top_k=5,
            similarity_threshold=0.7,
            requested_by=msg.user_id
        )
        
        rag_context = [
            {
                "text": result.get("text", ""),
                "source": result.get("source", "unknown"),
                "trust_score": result.get("trust_score", 0.5),
                "distance": result.get("distance", 1.0)
            }
            for result in rag_results.get("results", [])
        ]
        
        # World model facts
        from backend.world_model.grace_world_model import grace_world_model
        await grace_world_model.initialize()
        
        knowledge_items = await grace_world_model.query(
            query=msg.message,
            top_k=5
        )
        
        world_model_facts = {
            "facts": [
                {
                    "content": k.content,
                    "category": k.category,
                    "source": k.source,
                    "confidence": k.confidence,
                    "tags": k.tags
                }
                for k in knowledge_items
            ],
            "system_status": {
                "total_knowledge": len(grace_world_model.knowledge_base),
                "active_skills": len(reflection_loop.trust_scores)
            }
        }
        
        # Add logs to context if present
        if logs_data:
            world_model_facts["recent_logs"] = [log.dict() for log in logs_data]
        
        # Vision context if present
        if msg.vision_context:
            world_model_facts["vision_context"] = msg.vision_context
        
        # Conversation history
        conversation_history = conversations[session_id][-10:]
        
        # Trust context
        trust_scores = reflection_loop.get_trust_scores()
        trust_context = {
            "trust_score": sum(trust_scores.values()) / len(trust_scores) if trust_scores else 0.8,
            "min_confidence": 0.7,
            "pending_approvals": len([
                a for a in action_gateway.get_action_log()
                if not a.get("approved") and a.get("governance_tier") == "approval_required"
            ])
        }
        
        # Step 3: Call OpenAI reasoner
        response = await openai_reasoner.generate(
            user_message=msg.message,
            conversation_history=conversation_history,
            rag_context=rag_context,
            world_model_facts=world_model_facts,
            trust_context=trust_context
        )
        
        # Step 4: Process actions through governance
        action_cards = []
        for action in response.get("actions", []):
            if action.get("type") == "approval_request":
                gateway_response = await action_gateway.request_action(
                    action_type=action["action"],
                    agent="grace_reasoner",
                    params={
                        "tier": action["tier"],
                        "justification": action["justification"],
                        "trace_id": trace_id
                    },
                    trace_id=trace_id
                )
                
                action_cards.append(ActionCard(
                    trace_id=gateway_response["trace_id"],
                    action_type=action["action"],
                    tier=gateway_response["governance_tier"],
                    justification=action["justification"],
                    params=gateway_response.get("params", {}),
                    timestamp=gateway_response["timestamp"],
                    approved=gateway_response.get("approved", False),
                    requires_approval=not gateway_response.get("approved", False)
                ))
        
        # Get all pending approvals
        pending_approvals_data = [
            a for a in action_gateway.get_action_log()
            if not a.get("approved") and 
            a.get("governance_tier") == "approval_required" and
            not a.get("declined")
        ]
        
        pending_cards = [
            ActionCard(
                trace_id=a["trace_id"],
                action_type=a["action_type"],
                tier=a["governance_tier"],
                justification=a.get("reason", ""),
                params=a.get("params", {}),
                timestamp=a["timestamp"],
                approved=False,
                requires_approval=True
            )
            for a in pending_approvals_data[:5]  # Latest 5
        ]
        
        # Step 5: Fetch telemetry
        telemetry = None
        if msg.include_telemetry:
            telemetry = await fetch_telemetry_panel()
        
        # Step 6: Generate voice response if enabled
        voice_url = None
        if msg.voice_enabled:
            voice_url = await generate_voice_response(
                text=response["reply"],
                session_id=session_id
            )
        
        # Step 7: Check for errors and healing options
        healing_options = []
        error_message = None
        
        if response.get("error"):
            error_message = response["error"]
            healing_options = await get_healing_options(trace_id, error_message)
        
        # Store conversation turn
        conversations[session_id].append({
            "role": "user",
            "content": msg.message,
            "timestamp": datetime.now().isoformat()
        })
        conversations[session_id].append({
            "role": "assistant",
            "content": response["reply"],
            "timestamp": datetime.now().isoformat(),
            "trace_id": trace_id
        })
        
        # Step 8: Return comprehensive response
        return UnifiedChatResponse(
            reply=response["reply"],
            trace_id=trace_id,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            confidence=response["confidence"],
            voice_url=voice_url,
            voice_transcript=response["reply"] if msg.voice_enabled else None,
            actions=action_cards,
            requires_approval=response["requires_approval"],
            pending_approvals=pending_cards,
            telemetry=telemetry,
            logs=logs_data,
            citations=response["citations"],
            error=error_message,
            healing_options=healing_options
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unified chat failed: {str(e)}"
        )


async def detect_log_request(message: str) -> bool:
    """Detect if user is requesting logs"""
    log_keywords = [
        "show logs", "show errors", "latest logs", "recent errors",
        "api errors", "show the logs", "bring up logs", "deployment issues",
        "what went wrong", "show failures", "healing attempts"
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in log_keywords)


async def fetch_telemetry_panel() -> TelemetryPanel:
    """Fetch current system telemetry"""
    trust_scores = reflection_loop.get_trust_scores()
    avg_trust = sum(trust_scores.values()) / len(trust_scores) if trust_scores else 0.8
    
    pending = len([
        a for a in action_gateway.get_action_log()
        if not a.get("approved") and a.get("governance_tier") == "approval_required"
    ])
    
    # Determine health
    if avg_trust >= 0.7:
        health = "healthy"
    elif avg_trust >= 0.5:
        health = "degraded"
    else:
        health = "offline"
    
    return TelemetryPanel(
        health=health,
        trust_score=avg_trust,
        confidence=avg_trust,
        pending_approvals=pending,
        active_tasks=len(action_gateway.action_log),
        active_missions=0,  # Integrate with mission system
        learning_jobs=0,    # Integrate with learning system
        incidents=0,        # Integrate with incident tracker
        timestamp=datetime.now().isoformat()
    )


async def generate_voice_response(text: str, session_id: str) -> str:
    """
    Generate voice audio for response
    
    TODO: Integrate with:
    - OpenAI Realtime API
    - ElevenLabs TTS
    - Azure Speech Services
    
    Args:
        text: Text to convert to speech
        session_id: Session ID for voice stream
    
    Returns:
        URL to audio stream or file
    """
    # Placeholder - integrate with actual TTS service
    # For now, return a mock URL
    return f"/api/voice/stream/{session_id}/response.mp3"


async def get_healing_options(
    trace_id: str,
    error: str
) -> List[HealingOption]:
    """
    Get self-healing options for failed action
    
    Args:
        trace_id: Trace ID of failed action
        error: Error message
    
    Returns:
        List of healing options
    """
    # Placeholder - integrate with actual healing system
    options = []
    
    if "deployment" in error.lower():
        options.append(HealingOption(
            healing_id=f"heal_{trace_id}_rollback",
            title="Rollback Deployment",
            description="Rollback to previous stable version",
            playbook="rollback_deployment",
            confidence=0.9
        ))
    
    if "network" in error.lower() or "timeout" in error.lower():
        options.append(HealingOption(
            healing_id=f"heal_{trace_id}_retry",
            title="Retry with Backoff",
            description="Retry the operation with exponential backoff",
            playbook="retry_with_backoff",
            confidence=0.8
        ))
    
    return options
