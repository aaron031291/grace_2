"""
Grace Multi-Modal LLM System
Supports: Text, Voice, Vision, Code
Model switching based on task
"""

import os
from typing import Dict, Any, Optional, Literal
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

ModelType = Literal["text", "vision", "code", "reasoning", "fast"]

class MultiModalLLM:
    """
    Grace's multi-modal language model system
    Switches models based on task requirements
    """
    
    def __init__(self):
        self.current_model: Optional[str] = None
        self.models_available = self._detect_available_models()
        self.mode = "balanced"  # balanced, fast, quality
        self.use_voice = False
    
    def _detect_available_models(self) -> Dict[str, bool]:
        """Detect which models are available"""
        available = {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "local": False,  # Would check for local models
            "vision": bool(os.getenv("OPENAI_API_KEY")),  # GPT-4 Vision
            "tts": bool(os.getenv("OPENAI_API_KEY")),  # OpenAI TTS
            "stt": True  # Built-in speech-to-text
        }
        
        logger.info(f"[MULTIMODAL] Available models: {[k for k, v in available.items() if v]}")
        return available
    
    async def generate_response(
        self,
        user_message: str,
        modality: ModelType = "text",
        context: Optional[Dict[str, Any]] = None,
        voice_output: bool = False
    ) -> Dict[str, Any]:
        """
        Generate response with automatic model selection
        
        Args:
            user_message: User input (text or transcribed speech)
            modality: Preferred modality
            context: Additional context
            voice_output: Whether to generate voice response
        
        Returns:
            {
                "text": "response text",
                "audio_url": "url to TTS audio" if voice_output,
                "model_used": "gpt-4",
                "reasoning_trace": [...],
                "execution_trace": {...}
            }
        """
        
        # Select best model for task
        model = await self._select_model(user_message, modality, context)
        
        # Generate text response
        text_response = await self._generate_text(user_message, model, context)
        
        response = {
            "text": text_response,
            "model_used": model,
            "modality": modality,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add voice if requested
        if voice_output and self.models_available["tts"]:
            audio_url = await self._generate_voice(text_response)
            response["audio_url"] = audio_url
            response["has_audio"] = True
        
        return response
    
    async def _select_model(
        self,
        message: str,
        modality: ModelType,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Intelligently select model based on task
        
        - Fast queries → GPT-3.5/Claude Haiku
        - Complex reasoning → GPT-4/Claude Opus
        - Code generation → GPT-4/Claude 3.5 Sonnet
        - Vision tasks → GPT-4 Vision
        - Quick answers → Fast model
        """
        
        message_lower = message.lower()
        
        # Vision tasks
        if modality == "vision" or "image" in message_lower or "picture" in message_lower:
            if self.models_available["vision"]:
                return "gpt-4-vision"
            else:
                return "gpt-4"  # Fallback
        
        # Code tasks
        if modality == "code" or any(kw in message_lower for kw in ["code", "function", "class", "implement"]):
            if self.models_available["anthropic"]:
                return "claude-3-5-sonnet"  # Best for code
            elif self.models_available["openai"]:
                return "gpt-4-turbo"
            else:
                return "grace-llm"  # Built-in fallback
        
        # Reasoning tasks
        if modality == "reasoning" or any(kw in message_lower for kw in ["analyze", "explain", "why", "how does"]):
            if self.models_available["anthropic"]:
                return "claude-3-opus"
            elif self.models_available["openai"]:
                return "gpt-4"
            else:
                return "grace-llm"
        
        # Fast tasks (simple questions, status checks)
        if modality == "fast" or len(message) < 50:
            if self.models_available["openai"]:
                return "gpt-3.5-turbo"
            elif self.models_available["anthropic"]:
                return "claude-3-haiku"
            else:
                return "grace-llm"
        
        # Default: balanced model
        if self.mode == "fast":
            return "gpt-3.5-turbo" if self.models_available["openai"] else "grace-llm"
        elif self.mode == "quality":
            return "gpt-4" if self.models_available["openai"] else "claude-3-opus" if self.models_available["anthropic"] else "grace-llm"
        else:  # balanced
            return "gpt-4-turbo" if self.models_available["openai"] else "grace-llm"
    
    async def _generate_text(
        self,
        message: str,
        model: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate text response using selected model"""
        
        if model.startswith("gpt"):
            return await self._call_openai(message, model, context)
        elif model.startswith("claude"):
            return await self._call_anthropic(message, model, context)
        else:
            return await self._call_grace_llm(message, context)
    
    async def _call_openai(self, message: str, model: str, context: Optional[Dict]) -> str:
        """Call OpenAI API"""
        try:
            import openai
            
            messages = [
                {"role": "system", "content": "You are Grace, an autonomous AI with full system access."},
                {"role": "user", "content": message}
            ]
            
            # Add context if provided
            if context and context.get("knowledge_context"):
                messages.insert(1, {
                    "role": "system",
                    "content": f"Relevant context: {context['knowledge_context']}"
                })
            
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"[MULTIMODAL] OpenAI failed: {e}")
            return await self._call_grace_llm(message, context)
    
    async def _call_anthropic(self, message: str, model: str, context: Optional[Dict]) -> str:
        """Call Anthropic API"""
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            
            system_prompt = "You are Grace, an autonomous AI with full system access."
            if context and context.get("knowledge_context"):
                system_prompt += f"\n\nContext: {context['knowledge_context']}"
            
            response = await client.messages.create(
                model=model,
                system=system_prompt,
                messages=[{"role": "user", "content": message}],
                max_tokens=2000
            )
            
            return response.content[0].text
        
        except Exception as e:
            logger.error(f"[MULTIMODAL] Anthropic failed: {e}")
            return await self._call_grace_llm(message, context)
    
    async def _call_grace_llm(self, message: str, context: Optional[Dict]) -> str:
        """Fallback to built-in Grace LLM"""
        from .grace_llm import get_grace_llm
        from .memory import PersistentMemory
        
        try:
            persistent_memory = PersistentMemory()
            grace_llm = get_grace_llm(persistent_memory)
            result = await grace_llm.generate_response(
                user_message=message,
                context=context or {}
            )
            return result.get("text", "I'm here and operational.")
        except Exception as e:
            logger.error(f"[MULTIMODAL] Grace LLM failed: {e}")
            return f"I'm operational. You asked: '{message}'. How can I help with coding, system analysis, or autonomous tasks?"
    
    async def _generate_voice(self, text: str) -> Optional[str]:
        """Generate voice using TTS"""
        try:
            import openai
            
            response = await openai.Audio.acreate(
                model="tts-1",
                voice="nova",
                input=text
            )
            
            # Save audio file
            from pathlib import Path
            audio_dir = Path("audio_messages")
            audio_dir.mkdir(exist_ok=True)
            
            audio_path = audio_dir / f"grace_{datetime.utcnow().timestamp()}.mp3"
            audio_path.write_bytes(response.content)
            
            return f"/audio/{audio_path.name}"
        
        except Exception as e:
            logger.error(f"[MULTIMODAL] TTS failed: {e}")
            return None
    
    async def transcribe_voice(self, audio_bytes: bytes) -> str:
        """Transcribe voice to text using Whisper"""
        try:
            import openai
            
            # Save temp audio file
            from pathlib import Path
            temp_path = Path("audio_messages/temp_input.webm")
            temp_path.write_bytes(audio_bytes)
            
            with open(temp_path, "rb") as audio_file:
                response = await openai.Audio.atranscribe(
                    model="whisper-1",
                    file=audio_file
                )
            
            temp_path.unlink()  # Clean up
            
            return response.text
        
        except Exception as e:
            logger.error(f"[MULTIMODAL] STT failed: {e}")
            return ""
    
    async def analyze_image(self, image_url: str, question: str) -> str:
        """Analyze image using vision model"""
        try:
            import openai
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"[MULTIMODAL] Vision failed: {e}")
            return "Vision analysis unavailable"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get info about available models"""
        return {
            "available_models": self.models_available,
            "current_model": self.current_model,
            "mode": self.mode,
            "voice_enabled": self.use_voice,
            "capabilities": {
                "text": True,
                "voice": self.models_available["tts"],
                "vision": self.models_available["vision"],
                "code": True,
                "reasoning": True
            }
        }


# Global instance
multimodal_llm = MultiModalLLM()


async def get_grace_llm():
    """Get Grace LLM instance (backwards compatibility)"""
    from .grace_llm import GraceLLM
    from .memory import PersistentMemory
    return GraceLLM(PersistentMemory())
