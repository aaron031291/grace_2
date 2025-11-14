"""
Model Orchestrator - Manages 15+ LLM models with learning
Grace watches, learns, and optimizes model selection
"""

import httpx
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class ModelType(Enum):
    CONVERSATION = "conversation"
    CODING = "coding"
    REASONING = "reasoning"
    VISION = "vision"
    LONG_CONTEXT = "long_context"
    FAST = "fast"

class ModelOrchestrator:
    """
    Orchestrates 15+ models and learns from their performance
    Grace observes which models work best for which tasks
    """
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        
        # All available models
        self.models = {
            # Conversation models
            "qwen2.5:72b": {
                "type": ModelType.CONVERSATION,
                "size": "40GB",
                "quality": 10,
                "speed": 6,
                "specialties": ["reasoning", "multilingual", "general"]
            },
            "qwen2.5:32b": {
                "type": ModelType.CONVERSATION,
                "size": "20GB",
                "quality": 9,
                "speed": 8,
                "specialties": ["chat", "reasoning", "general"]
            },
            
            # Coding models
            "deepseek-coder-v2:16b": {
                "type": ModelType.CODING,
                "size": "9GB",
                "quality": 10,
                "speed": 9,
                "specialties": ["code", "debug", "refactor"]
            },
            "codegemma:7b": {
                "type": ModelType.CODING,
                "size": "5GB",
                "quality": 8,
                "speed": 10,
                "specialties": ["code_completion", "snippets"]
            },
            "granite-code:20b": {
                "type": ModelType.CODING,
                "size": "12GB",
                "quality": 9,
                "speed": 7,
                "specialties": ["enterprise_code", "security"]
            },
            
            # Reasoning models
            "deepseek-r1:70b": {
                "type": ModelType.REASONING,
                "size": "70GB",
                "quality": 10,
                "speed": 5,
                "specialties": ["math", "logic", "complex_reasoning"]
            },
            
            # Long context models
            "kimi:latest": {
                "type": ModelType.LONG_CONTEXT,
                "size": "4GB",
                "quality": 8,
                "speed": 8,
                "specialties": ["long_docs", "conversation_memory"]
            },
            "command-r-plus:latest": {
                "type": ModelType.LONG_CONTEXT,
                "size": "24GB",
                "quality": 9,
                "speed": 7,
                "specialties": ["rag", "document_analysis"]
            },
            
            # Vision model
            "llava:34b": {
                "type": ModelType.VISION,
                "size": "20GB",
                "quality": 9,
                "speed": 6,
                "specialties": ["image_analysis", "visual_qa"]
            },
            
            # Fast models
            "phi3.5:latest": {
                "type": ModelType.FAST,
                "size": "8GB",
                "quality": 8,
                "speed": 10,
                "specialties": ["quick_responses", "simple_tasks"]
            },
            "gemma2:9b": {
                "type": ModelType.FAST,
                "size": "5GB",
                "quality": 8,
                "speed": 10,
                "specialties": ["fast_chat", "efficiency"]
            },
            
            # Specialized models
            "dolphin-mixtral:latest": {
                "type": ModelType.CONVERSATION,
                "size": "26GB",
                "quality": 9,
                "speed": 7,
                "specialties": ["uncensored", "technical"]
            },
            "nous-hermes2-mixtral:latest": {
                "type": ModelType.CONVERSATION,
                "size": "26GB",
                "quality": 9,
                "speed": 7,
                "specialties": ["instructions", "task_following"]
            },
            "wizardlm2:latest": {
                "type": ModelType.REASONING,
                "size": "40GB",
                "quality": 9,
                "speed": 6,
                "specialties": ["academic", "research", "writing"]
            },
            "mistral-nemo:latest": {
                "type": ModelType.FAST,
                "size": "7GB",
                "quality": 8,
                "speed": 9,
                "specialties": ["balanced", "efficient"]
            },
            "llama3.2:latest": {
                "type": ModelType.FAST,
                "size": "2GB",
                "quality": 7,
                "speed": 10,
                "specialties": ["fallback", "quick"]
            }
        }
        
        # Learning data - Grace observes model performance
        self.performance_log = []
        self.model_success_rates = {}
        self.task_to_model_mapping = {}
        
    async def select_best_model(self, message: str, context: Dict = None) -> str:
        """
        Grace's intelligence selects the best model based on:
        - Task type
        - Past performance
        - Context length
        - Learned preferences
        """
        
        message_lower = message.lower()
        
        # Detect task type
        if self._is_code_task(message_lower):
            return await self._select_coding_model(message)
        elif self._is_reasoning_task(message_lower):
            return await self._select_reasoning_model(message)
        elif self._is_vision_task(message_lower):
            return "llava:34b"
        elif self._needs_long_context(message, context):
            return await self._select_long_context_model(message)
        elif self._needs_fast_response(message):
            return await self._select_fast_model(message)
        else:
            return await self._select_conversation_model(message)
    
    def _is_code_task(self, message: str) -> bool:
        keywords = ["code", "function", "class", "debug", "implement", "refactor", "bug", "error", "python", "javascript", "import", "def ", "async ", "const "]
        return any(k in message for k in keywords)
    
    def _is_reasoning_task(self, message: str) -> bool:
        keywords = ["why", "explain", "reason", "logic", "proof", "calculate", "solve", "theorem", "derive"]
        return any(k in message for k in keywords)
    
    def _is_vision_task(self, message: str) -> bool:
        keywords = ["image", "picture", "photo", "screenshot", "diagram", "see this", "look at"]
        return any(k in message for k in keywords)
    
    def _needs_long_context(self, message: str, context: Dict) -> bool:
        if context and len(str(context)) > 5000:
            return True
        return len(message) > 2000
    
    def _needs_fast_response(self, message: str) -> bool:
        keywords = ["quick", "fast", "briefly", "short answer"]
        return any(k in message for k in keywords)
    
    async def _select_coding_model(self, message: str) -> str:
        """Select best coding model based on learned performance"""
        
        # Check Grace's learning data
        if "deepseek-coder-v2:16b" in self.model_success_rates:
            success_rate = self.model_success_rates["deepseek-coder-v2:16b"].get("coding", 0)
            if success_rate > 0.8:
                return "deepseek-coder-v2:16b"
        
        # Try in order: DeepSeek > Granite > CodeGemma
        for model in ["deepseek-coder-v2:16b", "granite-code:20b", "codegemma:7b"]:
            if await self._check_model_available(model):
                return model
        
        return "qwen2.5:32b"  # Fallback - still great at code
    
    async def _select_reasoning_model(self, message: str) -> str:
        """Select best reasoning model"""
        
        # DeepSeek R1 for complex reasoning
        if await self._check_model_available("deepseek-r1:70b"):
            return "deepseek-r1:70b"
        
        # Qwen 72B second choice
        if await self._check_model_available("qwen2.5:72b"):
            return "qwen2.5:72b"
        
        return "qwen2.5:32b"
    
    async def _select_long_context_model(self, message: str) -> str:
        """Select for long context"""
        
        for model in ["kimi:latest", "command-r-plus:latest"]:
            if await self._check_model_available(model):
                return model
        
        return "qwen2.5:32b"
    
    async def _select_fast_model(self, message: str) -> str:
        """Select fastest model"""
        
        for model in ["phi3.5:latest", "gemma2:9b", "mistral-nemo:latest"]:
            if await self._check_model_available(model):
                return model
        
        return "llama3.2:latest"
    
    async def _select_conversation_model(self, message: str) -> str:
        """Select best conversation model based on learning"""
        
        # Check Grace's learned preferences
        best_model = "qwen2.5:32b"
        best_score = 0
        
        for model in ["qwen2.5:72b", "qwen2.5:32b", "nous-hermes2-mixtral:latest"]:
            if model in self.model_success_rates:
                score = self.model_success_rates[model].get("conversation", 0)
                if score > best_score and await self._check_model_available(model):
                    best_score = score
                    best_model = model
        
        return best_model
    
    async def _check_model_available(self, model: str) -> bool:
        """Check if model is pulled and ready"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_url}/api/tags", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    available_models = [m["name"] for m in data.get("models", [])]
                    return any(model in m for m in available_models)
        except:
            pass
        return False
    
    async def chat_with_learning(
        self,
        message: str,
        context: Optional[List[Dict]] = None,
        user_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat with automatic model selection and performance learning
        Grace observes and learns which models work best
        """
        
        start_time = time.time()
        
        # Step 1: Select best model (Grace's intelligence)
        selected_model = user_preference or await self.select_best_model(message, context)
        
        # Step 2: Call the model
        try:
            async with httpx.AsyncClient() as client:
                messages = [
                    {
                        "role": "system",
                        "content": f"You are Grace, an autonomous AI with 20 kernels. Current model: {selected_model}. Be conversational and helpful."
                    }
                ]
                
                if context:
                    messages.extend(context[-10:])  # Up to 10 exchanges for context
                
                messages.append({"role": "user", "content": message})
                
                response = await client.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": selected_model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": 0.8,
                            "num_predict": 500,  # Shorter for faster response
                            "top_k": 40,
                            "top_p": 0.9
                        }
                    },
                    timeout=20.0  # Shorter timeout (20s instead of 90s)
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result["message"]["content"]
                    response_time = time.time() - start_time
                    
                    # Step 3: Grace learns from this interaction
                    await self._record_performance(
                        model=selected_model,
                        task_type=self._classify_task(message),
                        success=True,
                        response_time=response_time,
                        message_length=len(message),
                        response_length=len(response_text)
                    )
                    
                    return {
                        "text": response_text,
                        "model": selected_model,
                        "provider": "ollama",
                        "response_time": response_time,
                        "performance_score": await self._calculate_performance_score(response_time, len(response_text)),
                        "timestamp": datetime.now().isoformat()
                    }
                    
        except Exception as e:
            # Model failed, Grace learns from failure
            await self._record_performance(
                model=selected_model,
                task_type=self._classify_task(message),
                success=False,
                response_time=time.time() - start_time,
                error=str(e)
            )
            
            # Try next best model
            print(f"Model {selected_model} failed: {e}. Trying alternative...")
            return await self._try_alternative_model(message, context, selected_model)
        
        # All models failed
        return {
            "text": "All models unavailable. Please start Ollama: `ollama serve`",
            "model": "none",
            "provider": "fallback",
            "error": "No models available"
        }
    
    async def _try_alternative_model(self, message: str, context: Any, failed_model: str) -> Dict[str, Any]:
        """Try alternative models when one fails"""
        
        alternatives = [
            "qwen2.5:32b", "deepseek-coder-v2:16b", "kimi:latest",
            "phi3.5:latest", "gemma2:9b", "llama3.2:latest"
        ]
        
        for alt_model in alternatives:
            if alt_model == failed_model:
                continue
            
            if await self._check_model_available(alt_model):
                print(f"Trying alternative model: {alt_model}")
                # Retry with this model
                try:
                    return await self.chat_with_learning(message, context, user_preference=alt_model)
                except:
                    continue
        
        return {
            "text": f"I'm currently offline. Please start Ollama and pull a model:\n\n`ollama pull qwen2.5:32b`",
            "model": "none",
            "provider": "error"
        }
    
    async def _check_model_available(self, model: str) -> bool:
        """Check if model is pulled"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_url}/api/tags", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    available = [m["name"] for m in data.get("models", [])]
                    return any(model.split(":")[0] in m for m in available)
        except:
            pass
        return False
    
    def _classify_task(self, message: str) -> str:
        """Classify what type of task this is"""
        message_lower = message.lower()
        
        if any(k in message_lower for k in ["code", "function", "debug", "implement"]):
            return "coding"
        elif any(k in message_lower for k in ["why", "explain", "reason", "calculate", "solve"]):
            return "reasoning"
        elif any(k in message_lower for k in ["image", "picture", "photo", "see"]):
            return "vision"
        elif len(message) > 2000:
            return "long_context"
        else:
            return "conversation"
    
    async def _record_performance(
        self,
        model: str,
        task_type: str,
        success: bool,
        response_time: float,
        message_length: int = 0,
        response_length: int = 0,
        error: str = None
    ):
        """
        Record model performance for Grace to learn from
        This data helps Grace get smarter about model selection
        """
        
        performance_record = {
            "model": model,
            "task_type": task_type,
            "success": success,
            "response_time": response_time,
            "message_length": message_length,
            "response_length": response_length,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to performance log
        self.performance_log.append(performance_record)
        
        # Update success rates
        if model not in self.model_success_rates:
            self.model_success_rates[model] = {}
        
        if task_type not in self.model_success_rates[model]:
            self.model_success_rates[model][task_type] = {
                "successes": 0,
                "failures": 0,
                "avg_response_time": 0,
                "total_calls": 0
            }
        
        stats = self.model_success_rates[model][task_type]
        stats["total_calls"] += 1
        
        if success:
            stats["successes"] += 1
            # Update rolling average response time
            stats["avg_response_time"] = (
                (stats["avg_response_time"] * (stats["total_calls"] - 1) + response_time) 
                / stats["total_calls"]
            )
        else:
            stats["failures"] += 1
        
        # Save to database for long-term learning
        await self._persist_performance_data(performance_record)
    
    async def _persist_performance_data(self, record: Dict):
        """Save performance data to Grace's memory for learning"""
        try:
            from backend.models.base_models import async_session
            from sqlalchemy import text
            
            async with async_session() as session:
                # Store in model_performance table (create if needed)
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS model_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model TEXT,
                        task_type TEXT,
                        success BOOLEAN,
                        response_time REAL,
                        message_length INTEGER,
                        response_length INTEGER,
                        error TEXT,
                        timestamp TEXT
                    )
                """))
                
                await session.execute(text("""
                    INSERT INTO model_performance 
                    (model, task_type, success, response_time, message_length, response_length, error, timestamp)
                    VALUES (:model, :task_type, :success, :response_time, :msg_len, :resp_len, :error, :timestamp)
                """), {
                    "model": record["model"],
                    "task_type": record["task_type"],
                    "success": record["success"],
                    "response_time": record["response_time"],
                    "msg_len": record["message_length"],
                    "resp_len": record["response_length"],
                    "error": record["error"],
                    "timestamp": record["timestamp"]
                })
                
                await session.commit()
                
        except Exception as e:
            print(f"Failed to persist performance data: {e}")
    
    async def _calculate_performance_score(self, response_time: float, response_length: int) -> float:
        """Calculate overall performance score"""
        
        # Faster is better (up to 10s)
        time_score = max(0, 10 - response_time) / 10
        
        # Longer responses often better (up to 500 chars)
        length_score = min(response_length / 500, 1.0)
        
        # Combined score
        return (time_score * 0.3 + length_score * 0.7) * 100
    
    async def get_learning_insights(self) -> Dict[str, Any]:
        """
        Grace's insights about model performance
        Shows what she's learned about each model
        """
        
        insights = {
            "total_interactions": len(self.performance_log),
            "models_tested": len(self.model_success_rates),
            "best_performers": {},
            "recommendations": []
        }
        
        # Find best model for each task type
        task_types = ["coding", "reasoning", "conversation", "vision", "long_context"]
        
        for task_type in task_types:
            best_model = None
            best_rate = 0
            
            for model, stats in self.model_success_rates.items():
                if task_type in stats:
                    task_stats = stats[task_type]
                    if task_stats["total_calls"] > 0:
                        success_rate = task_stats["successes"] / task_stats["total_calls"]
                        if success_rate > best_rate:
                            best_rate = success_rate
                            best_model = model
            
            if best_model:
                insights["best_performers"][task_type] = {
                    "model": best_model,
                    "success_rate": best_rate,
                    "avg_response_time": self.model_success_rates[best_model][task_type]["avg_response_time"]
                }
        
        # Generate recommendations
        if insights["total_interactions"] > 10:
            insights["recommendations"].append("Grace has learned your preferences")
        
        return insights
    
    async def list_available_models(self) -> List[Dict[str, Any]]:
        """List all models with their status"""
        
        available_models = []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_url}/api/tags", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    installed = [m["name"] for m in data.get("models", [])]
                    
                    for model_name, model_info in self.models.items():
                        is_installed = any(model_name.split(":")[0] in m for m in installed)
                        
                        model_data = {
                            "name": model_name,
                            "installed": is_installed,
                            "type": model_info["type"].value,
                            "size": model_info["size"],
                            "quality": model_info["quality"],
                            "speed": model_info["speed"],
                            "specialties": model_info["specialties"]
                        }
                        
                        # Add performance data if available
                        if model_name in self.model_success_rates:
                            model_data["performance"] = self.model_success_rates[model_name]
                        
                        available_models.append(model_data)
                        
        except Exception as e:
            print(f"Failed to list models: {e}")
        
        return available_models

# Global instance
model_orchestrator = ModelOrchestrator()
