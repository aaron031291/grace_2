"""
World Model Service - Unified facade for World Model Hub
Connects all Grace's systems through a single interface for the frontend
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.world_model.grace_world_model import grace_world_model, WorldKnowledge
from backend.event_bus import event_bus, EventType, Event
from backend.action_gateway import action_gateway
from backend.reflection_loop import reflection_loop
from backend.skills.registry import skill_registry


class WorldModelService:
    """
    Unified service facade for World Model Hub
    Provides single interface to query Grace's internal state
    """
    
    def __init__(self):
        self._initialized = False
    
    async def initialize(self):
        """Initialize world model service"""
        if self._initialized:
            return
        
        if not grace_world_model._initialized:
            await grace_world_model.initialize()
        
        self._initialized = True
        print("[WorldModelService] Initialized")
    
    async def query_context(
        self,
        user_query: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get current context for World Model Hub
        
        Returns:
            - Recent artifacts from memory
            - Active missions
            - Pending approvals
            - Learning jobs
            - Relevant knowledge
        """
        context = {
            "timestamp": datetime.now().isoformat(),
            "query": user_query
        }
        
        if user_query:
            knowledge_items = await grace_world_model.query(
                query=user_query,
                top_k=5
            )
            context["relevant_knowledge"] = [k.to_dict() for k in knowledge_items]
        else:
            context["relevant_knowledge"] = []
        
        recent_artifacts = self._get_recent_artifacts(limit=limit)
        context["recent_artifacts"] = recent_artifacts
        
        context["active_missions"] = self._get_active_missions()
        
        context["pending_approvals"] = self._get_pending_approvals(limit=limit)
        
        context["learning_jobs"] = self._get_learning_jobs()
        
        context["system_health"] = self._get_system_health()
        
        return context
    
    def _get_recent_artifacts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent artifacts from world model"""
        all_knowledge = list(grace_world_model.knowledge_base.values())
        all_knowledge.sort(key=lambda k: k.updated_at, reverse=True)
        
        return [
            {
                "knowledge_id": k.knowledge_id,
                "category": k.category,
                "content": k.content[:200] + "..." if len(k.content) > 200 else k.content,
                "source": k.source,
                "updated_at": k.updated_at,
                "confidence": k.confidence,
                "tags": k.tags
            }
            for k in all_knowledge[:limit]
        ]
    
    def _get_active_missions(self) -> List[Dict[str, Any]]:
        """Get active missions (placeholder)"""
        return []
    
    def _get_pending_approvals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get pending approvals from action gateway"""
        recent_actions = action_gateway.get_action_log(limit=100)
        
        pending = [
            action for action in recent_actions
            if not action.get("approved", False) and 
            action.get("governance_tier") == "approval_required"
        ]
        
        return pending[:limit]
    
    def _get_learning_jobs(self) -> List[Dict[str, Any]]:
        """Get learning jobs (placeholder)"""
        return []
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Get system health summary"""
        return {
            "event_bus": {
                "total_events": len(event_bus.event_log),
                "subscribers": len(event_bus.subscribers)
            },
            "action_gateway": {
                "total_actions": len(action_gateway.action_log),
                "governance_rules": len(action_gateway.governance_rules)
            },
            "reflection_loop": {
                "total_reflections": len(reflection_loop.reflections),
                "trust_scores": len(reflection_loop.trust_scores)
            },
            "skill_registry": {
                "total_skills": len(skill_registry.skills)
            },
            "world_model": {
                "total_knowledge": len(grace_world_model.knowledge_base)
            }
        }
    
    async def link_trace(
        self,
        message_id: str,
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Link a message to an execution trace
        
        Args:
            message_id: ID of the message
            trace_id: Trace ID to link
        
        Returns:
            Trace data with events, actions, reflections
        """
        events = event_bus.get_trace(trace_id)
        
        actions = [
            action for action in action_gateway.get_action_log()
            if action.get("trace_id") == trace_id
        ]
        
        reflections = [
            reflection for reflection in reflection_loop.get_reflections()
            if reflection.get("trace_id") == trace_id
        ]
        
        return {
            "trace_id": trace_id,
            "message_id": message_id,
            "events": events,
            "actions": actions,
            "reflections": reflections,
            "total_events": len(events),
            "total_actions": len(actions),
            "total_reflections": len(reflections)
        }
    
    async def list_recent_artifacts(
        self,
        limit: int = 20,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List recent artifacts from world model
        
        Args:
            limit: Maximum number of artifacts
            category: Filter by category
        
        Returns:
            List of artifacts
        """
        all_knowledge = list(grace_world_model.knowledge_base.values())
        
        if category:
            all_knowledge = [k for k in all_knowledge if k.category == category]
        
        all_knowledge.sort(key=lambda k: k.updated_at, reverse=True)
        
        return [k.to_dict() for k in all_knowledge[:limit]]
    
    async def list_active_missions(self) -> List[Dict[str, Any]]:
        """
        List active missions
        
        Returns:
            List of active missions
        """
        return self._get_active_missions()
    
    async def list_pending_approvals(
        self,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        List pending approvals
        
        Args:
            limit: Maximum number of approvals
        
        Returns:
            List of pending approvals
        """
        return self._get_pending_approvals(limit=limit)
    
    async def approve_action(
        self,
        trace_id: str,
        approved_by: str = "user"
    ) -> Dict[str, Any]:
        """
        Approve a pending action
        
        Args:
            trace_id: Trace ID of the action
            approved_by: Who approved it
        
        Returns:
            Approval result
        """
        actions = action_gateway.get_action_log()
        action = next((a for a in actions if a.get("trace_id") == trace_id), None)
        
        if not action:
            return {
                "success": False,
                "error": f"Action with trace_id {trace_id} not found"
            }
        
        if action.get("approved"):
            return {
                "success": False,
                "error": "Action already approved"
            }
        
        action["approved"] = True
        action["approved_by"] = approved_by
        action["approved_at"] = datetime.now().isoformat()
        action["reason"] = f"Approved by {approved_by}"
        
        await event_bus.publish(Event(
            event_type=EventType.GOVERNANCE_CHECK,
            source="world_model_service",
            data={
                "trace_id": trace_id,
                "action": "approved",
                "approved_by": approved_by
            },
            trace_id=trace_id
        ))
        
        return {
            "success": True,
            "trace_id": trace_id,
            "approved_by": approved_by,
            "action": action
        }
    
    async def decline_action(
        self,
        trace_id: str,
        reason: str,
        declined_by: str = "user"
    ) -> Dict[str, Any]:
        """
        Decline a pending action
        
        Args:
            trace_id: Trace ID of the action
            reason: Reason for declining
            declined_by: Who declined it
        
        Returns:
            Decline result
        """
        actions = action_gateway.get_action_log()
        action = next((a for a in actions if a.get("trace_id") == trace_id), None)
        
        if not action:
            return {
                "success": False,
                "error": f"Action with trace_id {trace_id} not found"
            }
        
        action["declined"] = True
        action["declined_by"] = declined_by
        action["declined_at"] = datetime.now().isoformat()
        action["decline_reason"] = reason
        
        await event_bus.publish(Event(
            event_type=EventType.GOVERNANCE_CHECK,
            source="world_model_service",
            data={
                "trace_id": trace_id,
                "action": "declined",
                "declined_by": declined_by,
                "reason": reason
            },
            trace_id=trace_id
        ))
        
        return {
            "success": True,
            "trace_id": trace_id,
            "declined_by": declined_by,
            "reason": reason,
            "action": action
        }
    
    async def chat_with_grace(
        self,
        message: str,
        user_id: str = "user",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a message to Grace and get a response
        
        Args:
            message: User message
            user_id: User ID
            context: Additional context
        
        Returns:
            Grace's response with trace_id
        """
        trace_id = f"chat_{datetime.now().timestamp()}"
        
        await event_bus.publish(Event(
            event_type=EventType.AGENT_ACTION,
            source="world_model_hub",
            data={
                "action": "chat",
                "message": message,
                "user_id": user_id,
                "context": context or {}
            },
            trace_id=trace_id
        ))
        
        relevant_knowledge = await grace_world_model.query(
            query=message,
            top_k=5
        )
        
        from backend.model_orchestrator import model_orchestrator
        
        knowledge_context = "\n".join([
            f"- {k.content} (source: {k.source}, confidence: {k.confidence})"
            for k in relevant_knowledge
        ])
        
        prompt = f"""You are Grace, an autonomous AI system. A user is talking to you through the World Model Hub.

Your internal knowledge:
{knowledge_context}

System status:
- Event Bus: {len(event_bus.event_log)} events
- Actions: {len(action_gateway.action_log)} actions
- Reflections: {len(reflection_loop.reflections)} reflections
- Skills: {len(skill_registry.skills)} skills
- Knowledge: {len(grace_world_model.knowledge_base)} items

User: {message}

Grace (respond naturally, in first person):"""
        
        try:
            response = await model_orchestrator.generate(
                model="qwen2.5:32b",
                prompt=prompt,
                max_tokens=500
            )
            
            response_text = response.get('text', 'I apologize, but I encountered an error generating a response.')
            
        except Exception as e:
            response_text = f"I apologize, but I encountered an error: {str(e)}"
        
        await grace_world_model.add_knowledge(
            category='temporal',
            content=f"User asked: {message}. I responded: {response_text}",
            source='world_model_hub_chat',
            confidence=1.0,
            tags=['conversation', 'chat'],
            metadata={
                'user_id': user_id,
                'trace_id': trace_id,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        return {
            "response": response_text,
            "trace_id": trace_id,
            "relevant_knowledge": [k.to_dict() for k in relevant_knowledge],
            "timestamp": datetime.now().isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get world model service statistics"""
        return {
            "initialized": self._initialized,
            "world_model": grace_world_model.get_stats(),
            "system_health": self._get_system_health()
        }


# Singleton instance
world_model_service = WorldModelService()
