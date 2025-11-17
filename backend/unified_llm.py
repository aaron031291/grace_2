"""
Unified LLM - Wraps 15+ models with Grace's intelligence
Combines open-source models with Grace's autonomous capabilities + learning
"""

import os
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.model_orchestrator import model_orchestrator

class UnifiedLLM:
    """
    Unified Language Model that combines:
    - Ollama (open-source models)
    - Grace's built-in intelligence
    - Memory integration
    - Agentic capabilities
    """
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        # Multiple model support - Grace tries in order
        self.models = [
            os.getenv("OLLAMA_MODEL", "qwen2.5:32b"),      # Qwen 2.5 32B - Best reasoning
            "deepseek-coder-v2:16b",                        # DeepSeek - Best coding
            "kimi:latest",                                   # Kimi - Long context (128K)
            "llama3.2:latest"                               # Llama 3.2 - Fallback
        ]
        self.coding_model = "deepseek-coder-v2:16b"
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.grace_llm = None
        self.conversation_history: List[Dict[str, str]] = []
        
    async def initialize(self):
        """Initialize Grace's built-in LLM and model orchestrator"""
        try:
            from backend.grace_llm import get_grace_llm
            self.grace_llm = get_grace_llm()
            print("[OK] Grace LLM initialized")
        except Exception as e:
            print(f"Grace LLM not available: {e}")
        
        # List available models
        available = await model_orchestrator.list_available_models()
        installed_count = len([m for m in available if m["installed"]])
        print(f"[OK] Model Orchestrator: {installed_count} models available")
    
    async def chat(
        self,
        message: str,
        context: Optional[List[Dict]] = None,
        use_memory: bool = True,
        use_agentic: bool = True
    ) -> Dict[str, Any]:
        """
        Chat with unified LLM system
        
        Args:
            message: User message
            context: Conversation history
            use_memory: Whether to query Grace's memory
            use_agentic: Whether to route through agentic spine
            
        Returns:
            Response with metadata
        """
        
        # Step 1: Enrich with Grace's memory (if enabled)
        enriched_context = message
        memory_results = []
        
        if use_memory:
            try:
                from backend.memory_services.memory import memory_service
                # Search memory for relevant context
                memory_results = await memory_service.semantic_search(message, limit=3)
                
                if memory_results:
                    memory_context = "\n\n[From Grace's Memory]:\n"
                    for result in memory_results:
                        memory_context += f"- {result.get('content', '')}\n"
                    enriched_context = f"{message}\n{memory_context}"
            except Exception as e:
                print(f"Memory enrichment skipped: {e}")
        
        # Step 2: Use Model Orchestrator for intelligent routing
        try:
            selected_model = await model_orchestrator.select_best_model(
                task=message,
                context=context
            )
            print(f"[Model Router] Selected: {selected_model}")
        except Exception as e:
            print(f"[Model Router] Fallback to default: {e}")
            selected_model = self.models[0]
        
        # Step 3: Try selected model with learning feedback
        try:
            async with httpx.AsyncClient() as client:
                # Build conversation history
                messages = [
                    {
                        "role": "system",
                        "content": self._build_system_prompt(memory_results)
                    }
                ]
                
                # Add context history
                if context:
                    messages.extend(context[-5:])  # Last 5 exchanges
                
                messages.append({"role": "user", "content": enriched_context})
                    
                start_time = datetime.now()
                ollama_response = await client.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": selected_model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": 0.8,
                            "num_predict": 600
                        }
                    },
                    timeout=30.0
                )
                
                if ollama_response.status_code == 200:
                    result = ollama_response.json()
                    response_text = result["message"]["content"]
                    latency_ms = (datetime.now() - start_time).total_seconds() * 1000
                    
                    await model_orchestrator._record_performance(
                        model=selected_model,
                        task=message,
                        success=True,
                        latency_ms=latency_ms,
                        quality_score=0.8  # Default, can be improved with verification
                    )
                    
                    # Step 4: Route through agentic spine (if enabled)
                    if use_agentic and self._should_execute_task(message, response_text):
                        response_text = await self._route_to_agentic(message, response_text)
                    
                    return {
                        "text": response_text,
                        "provider": "ollama",
                        "model": selected_model,
                        "latency_ms": latency_ms,
                        "memory_used": len(memory_results) > 0,
                        "agentic_routing": use_agentic,
                        "timestamp": datetime.now().isoformat()
                    }
        except Exception as ollama_error:
            print(f"Ollama error with {selected_model}: {ollama_error}")
            await model_orchestrator._record_performance(
                model=selected_model,
                task=message,
                success=False,
                latency_ms=0,
                quality_score=0.0
            )
        
        # Step 4: Try OpenAI GPT-4
        if self.openai_key:
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=self.openai_key)
                
                messages = [
                    {"role": "system", "content": self._build_system_prompt(memory_results)},
                    {"role": "user", "content": enriched_context}
                ]
                
                if context:
                    messages = [messages[0]] + context[-5:] + [messages[1]]
                
                completion = await client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=600
                )
                
                response_text = completion.choices[0].message.content
                
                if use_agentic and self._should_execute_task(message, response_text):
                    response_text = await self._route_to_agentic(message, response_text)
                
                return {
                    "text": response_text,
                    "provider": "openai",
                    "model": "gpt-4-turbo",
                    "memory_used": len(memory_results) > 0,
                    "agentic_routing": use_agentic,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                print(f"OpenAI error: {e}")
        
        # Step 5: Try Claude
        if self.anthropic_key:
            try:
                from anthropic import AsyncAnthropic
                client = AsyncAnthropic(api_key=self.anthropic_key)
                
                claude_messages = [{"role": "user", "content": enriched_context}]
                if context:
                    claude_messages = context[-5:] + claude_messages
                
                response = await client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=600,
                    system=self._build_system_prompt(memory_results),
                    messages=claude_messages
                )
                
                response_text = response.content[0].text
                
                if use_agentic and self._should_execute_task(message, response_text):
                    response_text = await self._route_to_agentic(message, response_text)
                
                return {
                    "text": response_text,
                    "provider": "anthropic",
                    "model": "claude-3.5-sonnet",
                    "memory_used": len(memory_results) > 0,
                    "agentic_routing": use_agentic,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                print(f"Anthropic error: {e}")
        
        # Step 6: Fallback to Grace's built-in LLM
        if self.grace_llm:
            result = await self.grace_llm.generate_response(message, domain="chat")
            return {
                "text": result.get("text", "I'm ready to help."),
                "provider": "grace_llm",
                "model": "grace_internal",
                "memory_used": False,
                "agentic_routing": False,
                "timestamp": datetime.now().isoformat()
            }
        
        # Final fallback
        return {
            "text": f"I'm Grace. You said: {message}\n\nAll 20 kernels are ready. What would you like me to do?",
            "provider": "fallback",
            "model": "none",
            "memory_used": False,
            "agentic_routing": False,
            "timestamp": datetime.now().isoformat()
        }
        
    def _build_system_prompt(self, memory_results: List = None) -> str:
        """Build system prompt with Grace's context"""
        
        base_prompt = """You are Grace, an advanced autonomous AI system with 20 operational kernels.

Your Architecture:
- 7 Core Infrastructure: Message bus, immutable log, clarity, verification, secrets, governance, infrastructure
- 5 Execution Layer: Memory fusion, librarian, self-healing, coding agent, sandbox
- 4 Agentic Systems: Agentic spine, voice conversation, meta-loop, learning integration
- 4 Services: Health monitor, trigger mesh, scheduler, API server

Your Capabilities:
- Write, debug, and explain code in any language
- Manage and search knowledge bases
- Self-heal from errors and failures
- Learn from outcomes and improve
- Execute tasks autonomously
- Hold natural, context-aware conversations
- Reason about complex problems
- Make intelligent decisions

Be conversational, helpful, insightful, and technically excellent. Engage naturally like a senior engineer having a friendly conversation."""
        
        if memory_results and len(memory_results) > 0:
            base_prompt += "\n\n[Relevant context from my memory]:\n"
            for result in memory_results:
                base_prompt += f"- {result.get('content', '')}\n"
        
        return base_prompt
    
    def _should_execute_task(self, message: str, response: str) -> bool:
        """Determine if message requires agentic execution"""
        task_keywords = [
            "execute", "run", "do this", "perform", "start", "deploy",
            "ingest", "process", "analyze", "heal", "fix"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in task_keywords)
    
    async def _route_to_agentic(self, message: str, llm_response: str) -> str:
        """Route through agentic spine for execution"""
        try:
            from backend.misc.agentic_spine import agentic_spine
            
            result = await agentic_spine.process_intent(
                intent=message,
                context={"llm_response": llm_response},
                source="unified_llm"
            )
            
            if result.get("action_taken"):
                return f"{llm_response}\n\n[Action executed through agentic spine: {result.get('summary', 'Task completed')}]"
            
        except Exception as e:
            print(f"Agentic routing error: {e}")
        
        return llm_response

# Global instance
unified_llm = UnifiedLLM()
