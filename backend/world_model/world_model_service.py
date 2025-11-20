"""
World Model Service - Unified facade for World Model Hub (Orb Interface)
Connects all Grace's systems through a single interface for the frontend
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4

from backend.world_model.grace_world_model import grace_world_model, WorldKnowledge
from backend.event_bus import event_bus, EventType, Event
from backend.core.unified_event_publisher import publish_event
from backend.action_gateway import action_gateway
from backend.reflection_loop import reflection_loop
from backend.skills.registry import skill_registry
try:
    from backend.session_memory.memory import SessionMemory
except ImportError:
    class SessionMemory: pass  # Stub if missing


class WorldModelService:
    """
    Unified service facade for World Model Hub (Orb Interface)
    Provides single interface to query Grace's internal state
    """
    
    def __init__(self):
        self._initialized = False
        self.orb_sessions: Dict[str, SessionMemory] = {}
        self.media_sessions: Dict[str, Dict[str, Any]] = {}
        self.background_tasks: Dict[str, Dict[str, Any]] = {}
        self.voice_enabled_users: set = set()
    
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
        
        await publish_event(
            EventType.GOVERNANCE_CHECK,
            {
                "trace_id": trace_id,
                "action": "approved",
                "approved_by": approved_by
            },
            source="world_model_service"
        )
        
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
        
        await publish_event(
            EventType.GOVERNANCE_CHECK,
            {
                "trace_id": trace_id,
                "action": "declined",
                "declined_by": declined_by,
                "reason": reason
            },
            source="world_model_service"
        )
        
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
        
        await publish_event(
            EventType.AGENT_ACTION,
            {
                "action": "chat",
                "message": message,
                "user_id": user_id,
                "context": context or {}
            },
            source="world_model_hub"
        )
        
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
    
    async def create_orb_session(
        self,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new Orb session
        
        Args:
            user_id: User identifier
            metadata: Optional session metadata
        
        Returns:
            Session ID
        """
        session_id = f"orb_{uuid4().hex[:12]}"
        
        session = SessionMemory(
            session_id=session_id,
            embedding_service=None,
            vector_store=None
        )
        
        self.orb_sessions[session_id] = session
        
        await publish_event(
            EventType.AGENT_ACTION,
            {
                "action": "session_started",
                "session_id": session_id,
                "user_id": user_id,
                "metadata": metadata or {}
            },
            source="orb"
        )
        
        return session_id
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session info or None if not found
        """
        session = self.orb_sessions.get(session_id)
        if not session:
            return None
        
        summary = session.get_summary()
        
        return {
            "session_id": session_id,
            "user_id": "user",
            "start_time": summary["start_time"],
            "duration_seconds": summary["duration_seconds"],
            "duration_formatted": summary["duration_formatted"],
            "message_count": summary["total_messages"],
            "key_topics": summary["key_topics"],
            "status": summary["status"]
        }
    
    async def close_orb_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Close an Orb session
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session summary or None if not found
        """
        session = self.orb_sessions.get(session_id)
        if not session:
            return None
        
        session.close_session()
        
        await session.save_to_vector_store()
        
        summary = session.get_summary()
        
        await publish_event(
            EventType.AGENT_ACTION,
            {
                "action": "session_closed",
                "session_id": session_id,
                "summary": summary
            },
            source="orb"
        )
        
        return summary
    
    async def start_screen_share(
        self,
        user_id: str,
        quality_settings: Dict[str, Any]
    ) -> str:
        """
        Start screen sharing (Phase 1: simulated)
        
        Args:
            user_id: User identifier
            quality_settings: Quality settings
        
        Returns:
            Session ID
        """
        session_id = f"screen_{uuid4().hex[:8]}"
        
        self.media_sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "media_type": "screen_share",
            "status": "active",
            "start_time": datetime.now().isoformat(),
            "metadata": quality_settings
        }
        
        await publish_event(
            EventType.AGENT_ACTION,
            {
                "action": "screen_share_started",
                "session_id": session_id,
                "user_id": user_id
            },
            source="orb"
        )
        
        return session_id
    
    async def stop_screen_share(self, session_id: str) -> bool:
        """
        Stop screen sharing
        
        Args:
            session_id: Session identifier
        
        Returns:
            Success status
        """
        if session_id not in self.media_sessions:
            return False
        
        self.media_sessions[session_id]["status"] = "stopped"
        self.media_sessions[session_id]["end_time"] = datetime.now().isoformat()
        
        await publish_event(
            EventType.AGENT_ACTION,
            {
                "action": "screen_share_stopped",
                "session_id": session_id
            },
            source="orb"
        )
        
        return True
    
    async def start_recording(
        self,
        user_id: str,
        media_type: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Start recording (Phase 1: simulated)
        
        Args:
            user_id: User identifier
            media_type: Type of recording
            metadata: Recording metadata
        
        Returns:
            Session ID
        """
        session_id = f"rec_{uuid4().hex[:8]}"
        
        self.media_sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "media_type": media_type,
            "status": "recording",
            "start_time": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        await publish_event(
            EventType.AGENT_ACTION,
            {
                "action": "recording_started",
                "session_id": session_id,
                "user_id": user_id,
                "media_type": media_type
            },
            source="orb"
        )
        
        return session_id
    
    async def stop_recording(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Stop recording
        
        Args:
            session_id: Session identifier
        
        Returns:
            Recording details or None if not found
        """
        if session_id not in self.media_sessions:
            return None
        
        session = self.media_sessions[session_id]
        session["status"] = "completed"
        end_time = datetime.now()
        session["end_time"] = end_time.isoformat()
        
        start_time = datetime.fromisoformat(session["start_time"])
        duration = (end_time - start_time).total_seconds()
        
        file_path = f"/recordings/{session_id}.{session['media_type'].split('_')[0]}"
        
        await publish_event(
            EventType.AGENT_ACTION,
            {
                "action": "recording_stopped",
                "session_id": session_id,
                "file_path": file_path,
                "duration": duration
            },
            source="orb"
        )
        
        return {
            "file_path": file_path,
            "duration": duration,
            "session_id": session_id
        }
    
    async def toggle_voice(self, user_id: str, enable: bool) -> bool:
        """
        Toggle voice control
        
        Args:
            user_id: User identifier
            enable: Enable or disable
        
        Returns:
            Current voice status
        """
        if enable:
            self.voice_enabled_users.add(user_id)
        else:
            self.voice_enabled_users.discard(user_id)
        
        await publish_event(
            EventType.AGENT_ACTION,
            {
                "action": "voice_toggled",
                "user_id": user_id,
                "enabled": enable
            },
            source="orb"
        )
        
        return enable
    
    async def list_sandbox_experiments(self) -> List[Dict[str, Any]]:
        """
        List sandbox experiments (Phase 1: stub)
        
        Returns:
            List of experiments
        """
        return [
            {
                "experiment_id": "exp_001",
                "status": "validating",
                "title": "Autonomous Learning Enhancement",
                "description": "Testing improved learning loop with feedback",
                "metrics": {"accuracy": 0.92, "speed": 1.5},
                "progress": 0.65
            },
            {
                "experiment_id": "exp_002",
                "status": "ready",
                "title": "Multi-Model Consensus",
                "description": "Cross-model validation for critical decisions",
                "metrics": {"consensus": 0.88, "confidence": 0.91},
                "progress": 1.0
            }
        ]
    
    async def get_consensus_votes(self) -> List[Dict[str, Any]]:
        """
        Get consensus votes (Phase 1: stub)
        
        Returns:
            List of consensus votes
        """
        return [
            {
                "role": "Guardian",
                "avatar": "🛡️",
                "vote": "approve",
                "confidence": 0.95
            },
            {
                "role": "Analyst",
                "avatar": "📊",
                "vote": "caution",
                "confidence": 0.82
            },
            {
                "role": "Architect",
                "avatar": "🏗️",
                "vote": "approve",
                "confidence": 0.88
            }
        ]
    
    async def get_feedback_queue(self) -> List[Dict[str, Any]]:
        """
        Get feedback queue (Phase 1: stub)
        
        Returns:
            List of feedback items
        """
        return [
            {
                "id": "fb_001",
                "title": "Model Selection Strategy",
                "description": "Review model routing decisions for code generation",
                "priority": "high",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "fb_002",
                "title": "Learning Loop Calibration",
                "description": "Validate trust score calculations",
                "priority": "normal",
                "created_at": datetime.now().isoformat()
            }
        ]
    
    async def get_sovereignty_metrics(self) -> Dict[str, Any]:
        """
        Get sovereignty metrics (Phase 1: stub)
        
        Returns:
            Sovereignty metrics
        """
        return {
            "autonomy_level": 0.78,
            "autonomous_decisions_30d": 1247,
            "success_rate": 0.94,
            "learning_velocity": 1.23,
            "trust_calibration": 0.89,
            "active_sandboxes": 2,
            "trust_score": 0.91,
            "pending_reviews": 2
        }
    
    async def create_background_task(
        self,
        task_type: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Create background task
        
        Args:
            task_type: Type of task
            metadata: Task metadata
        
        Returns:
            Task ID
        """
        task_id = f"task_{uuid4().hex[:8]}"
        
        self.background_tasks[task_id] = {
            "task_id": task_id,
            "task_type": task_type,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        await event_bus.publish(Event(
            event_type=EventType.AGENT_ACTION,
            source="orb",
            data={
                "action": "task_created",
                "task_id": task_id,
                "task_type": task_type
            },
            trace_id=task_id
        ))
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task status
        
        Args:
            task_id: Task identifier
        
        Returns:
            Task details or None if not found
        """
        return self.background_tasks.get(task_id)
    
    async def get_orb_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive Orb statistics
        
        Returns:
            Unified stats
        """
        return {
            "sessions": {
                "active": len([s for s in self.orb_sessions.values() if s.status == "active"]),
                "total": len(self.orb_sessions)
            },
            "memory": {
                "total_fragments": len(grace_world_model.knowledge_base),
                "average_trust_score": 0.87,
                "total_size": len(grace_world_model.knowledge_base) * 1024
            },
            "intelligence": {
                "version": "2.0",
                "domain_pods": 5,
                "models_available": len(skill_registry.skills)
            },
            "governance": {
                "total_tasks": len(action_gateway.action_log),
                "pending_tasks": len([a for a in action_gateway.action_log if not a.get("approved")])
            },
            "notifications": {
                "total": len(event_bus.event_log),
                "unread": 0
            },
            "multimodal": {
                "active_sessions": len([s for s in self.media_sessions.values() if s["status"] == "active"]),
                "background_tasks": len(self.background_tasks),
                "voice_enabled_users": len(self.voice_enabled_users)
            }
        }


# Singleton instance
world_model_service = WorldModelService()
