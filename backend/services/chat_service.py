"""
Enhanced Chat Service with Full Context Integration

Gathers:
- Conversation history
- RAG context
- World model facts  
- Trust framework state
- Governance checks
- Notifications
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class ChatHistoryManager:
    """Manages conversation history per session"""
    
    def __init__(self):
        self._sessions: Dict[str, List[Dict[str, Any]]] = {}
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Add message to session history"""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self._sessions[session_id].append(message)
    
    def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        if session_id not in self._sessions:
            return []
        
        return self._sessions[session_id][-limit:]
    
    def get_context_window(self, session_id: str, max_tokens: int = 4000) -> List[Dict[str, Any]]:
        """Get messages that fit within token budget"""
        history = self.get_history(session_id, limit=50)
        
        # Simple estimation: ~4 chars per token
        total_chars = 0
        max_chars = max_tokens * 4
        context = []
        
        for msg in reversed(history):
            msg_chars = len(msg["content"])
            if total_chars + msg_chars > max_chars:
                break
            context.insert(0, msg)
            total_chars += msg_chars
        
        return context


class ActionRegistry:
    """Tracks proposed actions and their governance status"""
    
    def __init__(self):
        self._actions: Dict[str, Dict[str, Any]] = {}
        self._pending_approvals: List[Dict[str, Any]] = []
    
    def register_action(
        self,
        action_type: str,
        agent: str,
        params: Dict[str, Any],
        trace_id: str,
        governance_tier: str = "auto_approve"
    ) -> Dict[str, Any]:
        """Register an action for governance"""
        action_id = str(uuid.uuid4())
        
        action = {
            "action_id": action_id,
            "trace_id": trace_id,
            "action_type": action_type,
            "agent": agent,
            "params": params,
            "governance_tier": governance_tier,
            "approved": governance_tier == "auto_approve",
            "timestamp": datetime.utcnow().isoformat(),
            "reason": "Action proposed by Grace"
        }
        
        self._actions[action_id] = action
        
        # Add to pending approvals if needed
        if governance_tier in ["user_approval", "admin_approval"]:
            self._pending_approvals.append({
                "trace_id": trace_id,
                "action_type": action_type,
                "agent": agent,
                "governance_tier": governance_tier,
                "params": params,
                "reason": action.get("reason", ""),
                "timestamp": action["timestamp"]
            })
        
        return action
    
    def approve_action(self, trace_id: str, approved: bool, reason: str = ""):
        """Approve or reject an action"""
        for action in self._actions.values():
            if action["trace_id"] == trace_id:
                action["approved"] = approved
                action["approval_reason"] = reason
                action["approved_at"] = datetime.utcnow().isoformat()
                
                # Remove from pending
                self._pending_approvals = [
                    p for p in self._pending_approvals 
                    if p["trace_id"] != trace_id
                ]
                return action
        
        return None
    
    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get all pending approvals"""
        return self._pending_approvals.copy()


# Singleton instances
chat_history = ChatHistoryManager()
action_registry = ActionRegistry()


async def gather_full_context(
    user_message: str,
    session_id: str,
    user_id: str = "user"
) -> Dict[str, Any]:
    """
    Gather all context for Grace's response:
    - Conversation history
    - RAG context
    - World model facts
    - Trust framework state
    """
    context = {
        "conversation_history": [],
        "rag_context": [],
        "world_model_facts": {},
        "trust_state": {},
        "user_id": user_id,
        "session_id": session_id
    }
    
    # 1. Conversation History
    try:
        context["conversation_history"] = chat_history.get_context_window(
            session_id, 
            max_tokens=2000
        )
    except Exception as e:
        logger.warning(f"Failed to get conversation history: {e}")
    
    # 2. RAG Context
    try:
        from backend.services.rag_service import rag_service
        await rag_service.initialize()
        
        rag_result = await rag_service.retrieve(
            query=user_message,
            top_k=5,
            similarity_threshold=0.6,
            requested_by=user_id
        )
        context["rag_context"] = rag_result.get("results", [])
    except Exception as e:
        logger.warning(f"RAG retrieval failed: {e}")
    
    # 3. World Model Facts
    try:
        from backend.world_model.grace_world_model import world_model
        await world_model.initialize()
        
        knowledge_items = await world_model.query(user_message, top_k=3)
        if knowledge_items:
            context["world_model_facts"] = {
                "relevant_knowledge": [
                    {
                        "content": k.content,
                        "confidence": k.confidence,
                        "source": k.source,
                        "category": k.category
                    }
                    for k in knowledge_items
                ]
            }
    except Exception as e:
        logger.warning(f"World model query failed: {e}")
    
    # 4. Trust Framework State
    try:
        from backend.trust_framework import calculate_trust_score, model_health_registry
        
        # Get current trust score
        trust_score = calculate_trust_score(
            verification_passed=True,
            model_health_ok=True,
            hallucination_detected=False,
            context_provenance_verified=True
        )
        
        # Get model health
        model_health = model_health_registry.get_current_health()
        
        context["trust_state"] = {
            "trust_score": trust_score.score,
            "trust_level": trust_score.level.value,
            "model_health": model_health.value if model_health else "unknown",
            "guardrail_active": True
        }
    except Exception as e:
        logger.warning(f"Trust framework check failed: {e}")
        context["trust_state"] = {
            "trust_score": 0.8,
            "trust_level": "medium",
            "model_health": "unknown",
            "guardrail_active": False
        }
    
    return context


async def process_actions(
    actions: List[Dict[str, Any]],
    trace_id: str,
    session_id: str
) -> tuple[List[Dict[str, Any]], bool]:
    """
    Process proposed actions through governance
    Returns: (processed_actions, requires_approval)
    """
    processed_actions = []
    requires_approval = False
    
    for action in actions:
        # Determine governance tier based on action type
        governance_tier = determine_governance_tier(action.get("action_type", "unknown"))
        
        # Register action
        registered = action_registry.register_action(
            action_type=action.get("action_type", "unknown"),
            agent=action.get("agent", "grace"),
            params=action.get("params", {}),
            trace_id=trace_id,
            governance_tier=governance_tier
        )
        
        processed_actions.append(registered)
        
        if governance_tier in ["user_approval", "admin_approval"]:
            requires_approval = True
    
    return processed_actions, requires_approval


def determine_governance_tier(action_type: str) -> str:
    """Determine governance tier for an action"""
    # High-risk actions require approval
    high_risk = [
        "file_delete", "system_command", "code_execution",
        "database_modify", "network_request", "secret_access"
    ]
    
    # Medium-risk actions may need approval based on context
    medium_risk = [
        "file_write", "file_read", "api_call", "search"
    ]
    
    if action_type in high_risk:
        return "user_approval"
    elif action_type in medium_risk:
        return "auto_approve"  # Can upgrade to user_approval based on params
    else:
        return "auto_approve"


async def send_approval_notification(
    pending_approvals: List[Dict[str, Any]],
    user_id: str,
    session_id: str
):
    """Send notification for pending approvals"""
    try:
        from backend.routes.session_management_api import send_notification
        
        await send_notification(
            "approval_needed",
            {
                "user_id": user_id,
                "session_id": session_id,
                "approvals": pending_approvals,
                "count": len(pending_approvals),
                "message": f"{len(pending_approvals)} action(s) need approval",
                "badge": "🔐"
            }
        )
    except Exception as e:
        logger.warning(f"Failed to send approval notification: {e}")
