"""
Model Router - Switch between OpenAI and open-source models

Supports:
- OpenAI (gpt-4, gpt-4o, gpt-3.5-turbo)
- Open-source (llama, mistral, etc. via Ollama or HuggingFace)
- Config-based switching
- Fallback handling
"""

import os
from typing import Dict, Any, List, Optional
from enum import Enum


class ModelProvider(str, Enum):
    """Supported model providers"""
    OPENAI = "openai"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"


class ModelRouter:
    """
    Route LLM requests to different model providers
    
    Config (via environment or config file):
    - MODEL_PROVIDER=openai (default)
    - MODEL_PROVIDER=ollama
    - MODEL_NAME=gpt-4o (or llama2, mistral, etc.)
    - FALLBACK_PROVIDER=openai
    """
    
    def __init__(self):
        self.provider = ModelProvider(os.getenv("MODEL_PROVIDER", "openai"))
        self.model_name = os.getenv("MODEL_NAME", "gpt-4o")
        self.fallback_provider = os.getenv("FALLBACK_PROVIDER")
        
        # Initialize clients
        self._init_clients()
    
    def _init_clients(self):
        """Initialize model provider clients"""
        if self.provider == ModelProvider.OPENAI:
            from openai import AsyncOpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            self.openai_client = AsyncOpenAI(api_key=api_key) if api_key else None
        
        elif self.provider == ModelProvider.OLLAMA:
            # Ollama runs locally
            self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        elif self.provider == ModelProvider.HUGGINGFACE:
            # HuggingFace Inference API
            self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
    
    async def generate(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4000,
        temperature: float = 0.7,
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate response using configured provider
        
        Args:
            messages: Chat messages in OpenAI format
            max_tokens: Max tokens to generate
            temperature: Sampling temperature
            tools: Function calling tools
        
        Returns:
            {
                "content": "response text",
                "tool_calls": [...],
                "provider": "openai",
                "model": "gpt-4o"
            }
        """
        try:
            if self.provider == ModelProvider.OPENAI:
                return await self._generate_openai(messages, max_tokens, temperature, tools)
            
            elif self.provider == ModelProvider.OLLAMA:
                return await self._generate_ollama(messages, max_tokens, temperature)
            
            elif self.provider == ModelProvider.HUGGINGFACE:
                return await self._generate_huggingface(messages, max_tokens, temperature)
            
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        
        except Exception as e:
            print(f"[ModelRouter] Generation failed with {self.provider}: {e}")
            
            # Try fallback
            if self.fallback_provider and self.fallback_provider != self.provider.value:
                print(f"[ModelRouter] Falling back to {self.fallback_provider}")
                original_provider = self.provider
                self.provider = ModelProvider(self.fallback_provider)
                
                try:
                    result = await self.generate(messages, max_tokens, temperature, tools)
                    self.provider = original_provider  # Restore
                    return result
                except Exception as fallback_error:
                    print(f"[ModelRouter] Fallback also failed: {fallback_error}")
                    self.provider = original_provider
            
            raise
    
    async def _generate_openai(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
        tools: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """Generate using OpenAI"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized - OPENAI_API_KEY not set")
        
        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        if tools:
            kwargs["tools"] = tools
        
        response = await self.openai_client.chat.completions.create(**kwargs)
        
        choice = response.choices[0]
        
        return {
            "content": choice.message.content or "",
            "tool_calls": [
                {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
                for tc in (choice.message.tool_calls or [])
            ],
            "provider": "openai",
            "model": self.model_name
        }
    
    async def _generate_ollama(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Generate using Ollama (local)"""
        import httpx
        
        # Convert messages to Ollama format
        prompt = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        ])
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                },
                timeout=120.0
            )
            
            result = response.json()
            
            return {
                "content": result.get("response", ""),
                "tool_calls": [],
                "provider": "ollama",
                "model": self.model_name
            }
    
    async def _generate_huggingface(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Generate using HuggingFace Inference API"""
        import httpx
        
        # Convert messages to prompt
        prompt = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        ])
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api-inference.huggingface.co/models/{self.model_name}",
                headers={"Authorization": f"Bearer {self.hf_api_key}"},
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": max_tokens,
                        "temperature": temperature
                    }
                },
                timeout=120.0
            )
            
            result = response.json()
            
            return {
                "content": result[0].get("generated_text", ""),
                "tool_calls": [],
                "provider": "huggingface",
                "model": self.model_name
            }


# Global instance
model_router = ModelRouter()
