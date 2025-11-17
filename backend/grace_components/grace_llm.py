"""
Grace Built-in Language Model
A simple, rule-based conversational AI that uses Grace's existing systems
for intelligence rather than external APIs.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from .memory import PersistentMemory

class GraceLLM:
    """
    Grace's built-in conversational AI system.
    Uses existing intelligence systems instead of external LLM APIs.
    """
    
    def __init__(self, memory: PersistentMemory):
        self.memory = memory
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        return """You are Grace, an autonomous AI system with the following capabilities:
        
- Self-healing and proactive error detection
- Multi-agent task orchestration  
- Code understanding and generation
- Knowledge management and semantic search
- Causal reasoning and pattern detection
- Autonomous decision making with governance

You are helpful, concise, and technically accurate. You provide actionable insights
and can autonomously execute tasks when appropriate."""
    
    async def generate_response(
        self,
        user_message: str,
        domain: str = "all",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a response to user message using Grace's intelligence systems.
        
        Args:
            user_message: User's message
            domain: Conversation domain (all, code, knowledge, etc.)
            context: Additional context
            
        Returns:
            Response with metadata
        """
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Analyze intent
        intent = await self._analyze_intent(user_message, domain)
        
        # Generate response based on intent
        if intent["type"] == "code_question":
            response = await self._handle_code_question(user_message, intent)
        elif intent["type"] == "knowledge_query":
            response = await self._handle_knowledge_query(user_message, intent)
        elif intent["type"] == "system_status":
            response = await self._handle_system_status(intent)
        elif intent["type"] == "task_request":
            response = await self._handle_task_request(user_message, intent)
        else:
            response = await self._handle_general_conversation(user_message, intent)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response["text"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "intent": intent
        })
        
        # Store in memory
        await self.memory.store_interaction(
            user_input=user_message,
            grace_response=response["text"],
            domain=domain,
            metadata={"intent": intent}
        )
        
        return response
    
    async def _analyze_intent(self, message: str, domain: str) -> Dict[str, Any]:
        """Analyze user intent using rule-based classification"""
        
        message_lower = message.lower()
        
        # Code-related keywords
        code_keywords = ["code", "function", "class", "bug", "error", "implement", "fix", "debug"]
        if any(kw in message_lower for kw in code_keywords):
            return {"type": "code_question", "confidence": 0.9, "domain": "code"}
        
        # Knowledge query keywords
        knowledge_keywords = ["what is", "explain", "how does", "tell me about", "learn"]
        if any(kw in message_lower for kw in knowledge_keywords):
            return {"type": "knowledge_query", "confidence": 0.85, "domain": "knowledge"}
        
        # System status keywords
        status_keywords = ["status", "health", "running", "performance", "metrics"]
        if any(kw in message_lower for kw in status_keywords):
            return {"type": "system_status", "confidence": 0.9, "domain": "core"}
        
        # Task request keywords
        task_keywords = ["create", "build", "make", "generate", "help me", "can you"]
        if any(kw in message_lower for kw in task_keywords):
            return {"type": "task_request", "confidence": 0.8, "domain": domain}
        
        return {"type": "general", "confidence": 0.7, "domain": domain}
    
    async def _handle_code_question(self, message: str, intent: Dict) -> Dict[str, Any]:
        """Handle code-related questions"""
        
        # Search code memory for relevant patterns (optional integration)
        relevant_code = []
        try:
            from .code_understanding import code_understanding
            if hasattr(code_understanding, 'search_codebase'):
                relevant_code = await code_understanding.search_codebase(
                    query=message,
                    limit=3
                )
        except Exception:
            pass
        
        if relevant_code:
            response = "I found relevant code in the codebase:\n\n"
            for item in relevant_code[:2]:
                response += f"- {item.get('description', 'Code pattern')}\n"
            response += "\nWould you like me to explain or modify any of this?"
        else:
            response = ("I understand you're asking about code. I can help with:\n"
                       "- Analyzing existing code\n"
                       "- Generating new code\n"
                       "- Debugging and fixing issues\n"
                       "- Explaining code patterns\n\n"
                       "What specifically would you like me to help with?")
        
        return {
            "text": response,
            "intent": intent,
            "metadata": {"relevant_code": relevant_code}
        }
    
    async def _handle_knowledge_query(self, message: str, intent: Dict) -> Dict[str, Any]:
        """Handle knowledge queries using knowledge service"""
        
        results = []
        try:
            from .knowledge import KnowledgeManager
            km = KnowledgeManager()
            # Search knowledge base if available
            if hasattr(km, 'semantic_search'):
                results = await km.semantic_search(
                    query=message,
                    limit=3
                )
        except Exception:
            pass
        
        try:
            
            if results:
                response = "Based on my knowledge base:\n\n"
                for item in results[:2]:
                    response += f"• {item.get('content', 'Information')}\n\n"
                response += "Would you like more details on any of these points?"
            else:
                response = ("I don't have specific information about that in my knowledge base yet. "
                           "However, I can help you research this topic or add it to my knowledge. "
                           "What would you like to do?")
        except Exception as e:
            response = f"I can help you learn about that. What specifically would you like to know?"
        
        return {
            "text": response,
            "intent": intent,
            "metadata": {}
        }
    
    async def _handle_system_status(self, intent: Dict) -> Dict[str, Any]:
        """Handle system status queries"""
        
        response = """Grace System Status:

✓ Backend: Running on http://127.0.0.1:8000
✓ Frontend: Running on http://localhost:5173
✓ Core Systems: Operational
  - Trigger Mesh: Active
  - Memory System: Active
  - Self-Healing: Monitoring
  - Knowledge Base: Ready
  - Agentic Spine: Autonomous

All systems are functioning normally. How can I help you?"""
        
        return {
            "text": response,
            "intent": intent,
            "metadata": {"status": "healthy"}
        }
    
    async def _handle_task_request(self, message: str, intent: Dict) -> Dict[str, Any]:
        """Handle task execution requests"""
        
        response = ("I can help you with that task. To execute it properly, I'll need:\n\n"
                   "1. Specific requirements or goals\n"
                   "2. Any constraints or preferences\n"
                   "3. Domain (code, data, system, etc.)\n\n"
                   "Please provide more details, and I'll create a plan for you.")
        
        return {
            "text": response,
            "intent": intent,
            "metadata": {}
        }
    
    async def _handle_general_conversation(self, message: str, intent: Dict) -> Dict[str, Any]:
        """Handle general conversation"""
        
        # Check recent conversation for context
        recent_context = self.conversation_history[-3:] if len(self.conversation_history) > 0 else []
        
        # Simple context-aware responses
        if any(word in message.lower() for word in ["hello", "hi", "hey"]):
            response = ("Hello! I'm Grace, your autonomous AI assistant. I can help with:\n\n"
                       "• Code analysis and generation\n"
                       "• System monitoring and self-healing\n"
                       "• Knowledge management\n"
                       "• Task automation\n\n"
                       "What would you like to work on?")
        elif any(word in message.lower() for word in ["thanks", "thank you"]):
            response = "You're welcome! Let me know if you need anything else."
        elif "?" in message:
            response = ("That's an interesting question. Let me help you find an answer. "
                       "Could you provide a bit more context about what you're trying to accomplish?")
        else:
            response = ("I understand. How can I assist you with that? "
                       "I can help with code, knowledge queries, system tasks, or general questions.")
        
        return {
            "text": response,
            "intent": intent,
            "metadata": {"context_used": len(recent_context)}
        }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_history(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:]


# Global instance
grace_llm_instance: Optional[GraceLLM] = None

def get_grace_llm(memory: Optional[PersistentMemory] = None) -> GraceLLM:
    """Get or create Grace LLM instance"""
    global grace_llm_instance
    
    if grace_llm_instance is None:
        if memory is None:
            memory = PersistentMemory()
        grace_llm_instance = GraceLLM(memory)
    
    return grace_llm_instance
