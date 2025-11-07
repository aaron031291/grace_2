from datetime import datetime
from typing import Dict
from .memory import PersistentMemory
from .knowledge import knowledge_manager
from .cognition_intent import cognition_authority

class GraceAutonomous:
    def __init__(self, memory: PersistentMemory):
        self.memory = memory
        self.use_cognition_pipeline = True  # Feature flag

    async def respond(self, user: str, message: str) -> str:
        """
        Respond to user message.
        
        New Architecture:
        1. Cognition parses intent (not LLM)
        2. Cognition creates plan
        3. Agentic layer executes with safeguards
        4. LLM verbalizes structured result (narrator only)
        """
        
        # Use new cognition pipeline if enabled
        if self.use_cognition_pipeline:
            return await self._respond_via_cognition(user, message)
        
        # Fallback to legacy simple response
        return await self._respond_legacy(user, message)
    
    async def _respond_via_cognition(self, user: str, message: str) -> str:
        """
        New cognition-driven response.
        LLM only narrates, doesn't decide.
        """
        
        # Step 1: Cognition processes the request (parsing, planning, execution)
        cognition_result = await cognition_authority.process_user_request(
            utterance=message,
            user_id=user,
            session_id=f"{user}-{datetime.now().timestamp()}"
        )
        
        # Step 2: Check if waiting for approval
        if cognition_result.get("status") == "pending_approval":
            return (
                f"I've planned an action that requires approval.\n\n"
                f"Intent: {cognition_result['intent_type']}\n"
                f"Plan ID: {cognition_result['plan_id']}\n"
                f"Approval ID: {cognition_result['approval_id']}\n\n"
                f"Please review in the approval panel."
            )
        
        # Step 3: LLM verbalizes the structured result (narrator only)
        return await self._verbalize_result(message, cognition_result)
    
    async def _verbalize_result(self, original_message: str, cognition_result: Dict) -> str:
        """
        LLM verbalizes cognition's structured result.
        
        CRITICAL: LLM is FORBIDDEN from:
        - Making decisions
        - Triggering actions
        - Inventing outputs
        
        LLM is ONLY allowed to:
        - Summarize fields from cognition_result
        - Format in natural language
        - Reference structured data
        """
        
        from datetime import datetime
        
        # Extract structured data
        result = cognition_result.get("result", {})
        intent_type = cognition_result.get("intent_type", "unknown")
        success = cognition_result.get("status") == "completed"
        outputs = result.get("outputs", {})
        verification = result.get("verification", {})
        
        # Simple rule-based verbalization (can replace with LLM later)
        # But LLM prompt would include these same guardrails
        
        if not success:
            return f"I attempted to {intent_type.replace('.', ' ')} but encountered issues. The action has been logged for review."
        
        # Task operations
        if intent_type == "task.list":
            task_data = outputs.get("task.list", {})
            task_count = task_data.get("count", 0)
            return f"You have {task_count} tasks. Check the task panel for details."
        
        # Knowledge operations
        elif intent_type == "knowledge.search":
            search_data = outputs.get("knowledge.search", {})
            result_count = search_data.get("count", 0)
            if result_count > 0:
                return f"I found {result_count} relevant knowledge entries. The top result may help answer your question."
            else:
                return "I don't have information about that yet. Would you like me to research it?"
        
        # Code operations
        elif intent_type == "code.edit":
            code_data = outputs.get("code.edit", {})
            confidence = verification.get("confidence", 0)
            rollback = result.get("rollback_available", False)
            
            return (
                f"Code edit completed with {confidence*100:.0f}% confidence. "
                f"{'Rollback available.' if rollback else ''}"
            )
        
        # Default verbalization
        else:
            action_count = result.get("actions_completed", 0)
            confidence = result.get("confidence", 0)
            
            if confidence > 0:
                return f"Completed {action_count} action(s) with {confidence*100:.0f}% confidence."
            else:
                return "Request processed. Check the activity log for details."
    
    async def _respond_legacy(self, user: str, message: str) -> str:
        """Legacy simple response (fallback)"""
        normalized = message.lower().strip()
        
        knowledge_results = await knowledge_manager.search_knowledge(message, limit=3)
        has_relevant_knowledge = len(knowledge_results) > 0
        
        if "history" in normalized or "remember" in normalized:
            msgs = await self.memory.recent_messages(user, limit=20)
            if len(msgs) < 2:
                return "We just started chatting. Ask me a few more things and then check history again!"
            history = "\n".join(
                f"{m.role.upper()}: {m.content}" for m in msgs[-10:]
            )
            return f"Here are your last {min(len(msgs), 10)} interactions:\n\n{history}"
        
        if "hello" in normalized or "hi" in normalized:
            return "Hello! I'm Grace. How can I help you today?"
        
        if "how are you" in normalized:
            return "I'm functioning optimally. All systems operational. How can I assist you?"
        
        if "thank" in normalized:
            return "You're welcome! Happy to help."
        
        if "bye" in normalized or "goodbye" in normalized:
            return "Goodbye! Feel free to return anytime."
        
        if not has_relevant_knowledge and len(normalized.split()) > 3:
            await self._propose_research(user, message)
            return (
                "I don't have sufficient knowledge about that topic yet. "
                "I've created a research goal to find trusted sources. "
                "You can approve knowledge ingestion in the governance panel, or teach me directly."
            )
        
        if has_relevant_knowledge:
            top_result = knowledge_results[0]
            return f"Based on my knowledge: {top_result['content'][:200]}..."
        
        return "Thanks for your message. I'm still learning. Try asking about your history or saying hello!"
    
    async def _propose_research(self, user: str, query: str):
        """Create research goal when Grace lacks knowledge"""
        from .models import Goal, async_session
        
        async with async_session() as session:
            goal = Goal(
                user=user,
                goal_text=f"Research and ingest knowledge about: {query}",
                status="active"
            )
            session.add(goal)
            await session.commit()
            print(f"✓ Grace proposed research goal: {query[:50]}...")
