"""
Model Categorization by Specialty
Maps all 21 Grace models to their specialized roles in the trust framework
"""

from typing import Dict, List
from enum import Enum


class ModelSpecialty(Enum):
    """Specialty categories for model routing"""
    RETRIEVAL = "retrieval"
    RESEARCH = "research"
    REASONING = "reasoning"
    CODING = "coding"
    VERIFICATION = "verification"
    VISION = "vision"
    CONVERSATION = "conversation"
    FAST_RESPONSE = "fast_response"
    UNCENSORED = "uncensored"
    GENERAL_PURPOSE = "general_purpose"


class ModelCapability(Enum):
    """Specific capabilities models can have"""
    TOOL_CALLING = "tool_calling"
    FUNCTION_CALLING = "function_calling"
    LONG_CONTEXT = "long_context"
    CODE_GENERATION = "code_generation"
    LOGIC_VALIDATION = "logic_validation"
    FACT_CHECKING = "fact_checking"
    RAG_SPECIALIST = "rag_specialist"
    MULTI_STEP_REASONING = "multi_step_reasoning"
    VISION_TEXT = "vision_text"
    ULTRA_FAST = "ultra_fast"
    MOE_ARCHITECTURE = "moe_architecture"


# Complete model categorization for all 21 models
MODEL_REGISTRY = {
    # Retrieval Specialists
    "command-r-plus:latest": {
        "specialty": ModelSpecialty.RETRIEVAL,
        "capabilities": [
            ModelCapability.RAG_SPECIALIST,
            ModelCapability.LONG_CONTEXT,
            ModelCapability.FACT_CHECKING
        ],
        "context_window": 128_000,
        "size_gb": 59,
        "use_cases": ["RAG", "document retrieval", "fact verification"],
        "trust_level": "high",
        "governance_required": True
    },
    
    "llama3.1:70b": {
        "specialty": ModelSpecialty.RESEARCH,
        "capabilities": [
            ModelCapability.TOOL_CALLING,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.LONG_CONTEXT,
            ModelCapability.MULTI_STEP_REASONING
        ],
        "context_window": 128_000,
        "size_gb": 42,
        "use_cases": ["agentic tasks", "tool use", "research"],
        "trust_level": "very_high",
        "governance_required": True,
        "notes": "Best overall agentic model"
    },
    
    "yi:34b": {
        "specialty": ModelSpecialty.RETRIEVAL,
        "capabilities": [
            ModelCapability.LONG_CONTEXT,
            ModelCapability.MULTI_STEP_REASONING
        ],
        "context_window": 200_000,
        "size_gb": 20,
        "use_cases": ["long document processing", "historical analysis"],
        "trust_level": "high",
        "governance_required": False
    },
    
    # Research Specialists
    "qwen2.5:72b": {
        "specialty": ModelSpecialty.RESEARCH,
        "capabilities": [
            ModelCapability.MULTI_STEP_REASONING,
            ModelCapability.LONG_CONTEXT
        ],
        "context_window": 128_000,
        "size_gb": 42,
        "use_cases": ["deep research", "comprehensive analysis"],
        "trust_level": "high",
        "governance_required": True
    },
    
    # Reasoning Specialists
    "deepseek-r1:70b": {
        "specialty": ModelSpecialty.REASONING,
        "capabilities": [
            ModelCapability.MULTI_STEP_REASONING,
            ModelCapability.LOGIC_VALIDATION
        ],
        "context_window": 64_000,
        "size_gb": 42,
        "use_cases": ["o1-level reasoning", "complex logic", "math"],
        "trust_level": "very_high",
        "governance_required": True,
        "notes": "OpenAI o1 level reasoning"
    },
    
    "deepseek-v2.5:236b": {
        "specialty": ModelSpecialty.REASONING,
        "capabilities": [
            ModelCapability.MOE_ARCHITECTURE,
            ModelCapability.MULTI_STEP_REASONING,
            ModelCapability.CODE_GENERATION
        ],
        "context_window": 128_000,
        "size_gb": 133,
        "use_cases": ["complex reasoning", "logic validation", "coding"],
        "trust_level": "very_high",
        "governance_required": True,
        "notes": "MoE reasoning powerhouse, 236B params"
    },
    
    "mixtral:8x22b": {
        "specialty": ModelSpecialty.REASONING,
        "capabilities": [
            ModelCapability.MOE_ARCHITECTURE,
            ModelCapability.MULTI_STEP_REASONING,
            ModelCapability.LONG_CONTEXT
        ],
        "context_window": 64_000,
        "size_gb": 82,
        "use_cases": ["reasoning", "planning", "analysis"],
        "trust_level": "very_high",
        "governance_required": True,
        "notes": "Best MoE reasoning, 141B params with 39B active"
    },
    
    # Coding Specialists
    "deepseek-coder-v2:16b": {
        "specialty": ModelSpecialty.CODING,
        "capabilities": [
            ModelCapability.CODE_GENERATION,
            ModelCapability.FUNCTION_CALLING
        ],
        "context_window": 128_000,
        "size_gb": 9,
        "use_cases": ["code generation", "debugging", "refactoring"],
        "trust_level": "high",
        "governance_required": True,
        "notes": "Best coding model"
    },
    
    "qwen2.5-coder:32b": {
        "specialty": ModelSpecialty.CODING,
        "capabilities": [
            ModelCapability.CODE_GENERATION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.TOOL_CALLING
        ],
        "context_window": 128_000,
        "size_gb": 19,
        "use_cases": ["coding", "function calling", "automation"],
        "trust_level": "high",
        "governance_required": True,
        "notes": "Excellent for coding agents"
    },
    
    "codegemma:7b": {
        "specialty": ModelSpecialty.CODING,
        "capabilities": [
            ModelCapability.CODE_GENERATION
        ],
        "context_window": 8_000,
        "size_gb": 5,
        "use_cases": ["code completion", "quick fixes"],
        "trust_level": "medium",
        "governance_required": False
    },
    
    "granite-code:20b": {
        "specialty": ModelSpecialty.CODING,
        "capabilities": [
            ModelCapability.CODE_GENERATION
        ],
        "context_window": 8_000,
        "size_gb": 11,
        "use_cases": ["enterprise code", "structured generation"],
        "trust_level": "high",
        "governance_required": False
    },
    
    # Verification Specialists
    "nemotron:70b": {
        "specialty": ModelSpecialty.VERIFICATION,
        "capabilities": [
            ModelCapability.LOGIC_VALIDATION,
            ModelCapability.FACT_CHECKING,
            ModelCapability.MULTI_STEP_REASONING
        ],
        "context_window": 128_000,
        "size_gb": 42,
        "use_cases": ["validation", "verification", "enterprise workflows"],
        "trust_level": "very_high",
        "governance_required": True,
        "notes": "NVIDIA enterprise agent, optimized for validation"
    },
    
    "mixtral:8x7b": {
        "specialty": ModelSpecialty.VERIFICATION,
        "capabilities": [
            ModelCapability.MOE_ARCHITECTURE,
            ModelCapability.LOGIC_VALIDATION
        ],
        "context_window": 32_000,
        "size_gb": 26,
        "use_cases": ["efficient verification", "logic checks"],
        "trust_level": "high",
        "governance_required": False,
        "notes": "Most efficient MoE, 46.7B params with 12.9B active"
    },
    
    # Vision Specialists
    "llava:34b": {
        "specialty": ModelSpecialty.VISION,
        "capabilities": [
            ModelCapability.VISION_TEXT
        ],
        "context_window": 4_096,
        "size_gb": 19,
        "use_cases": ["image analysis", "visual reasoning", "OCR"],
        "trust_level": "high",
        "governance_required": True,
        "notes": "Vision + text multimodal"
    },
    
    # Conversation Specialists
    "qwen2.5:32b": {
        "specialty": ModelSpecialty.CONVERSATION,
        "capabilities": [
            ModelCapability.MULTI_STEP_REASONING
        ],
        "context_window": 128_000,
        "size_gb": 19,
        "use_cases": ["general conversation", "reasoning"],
        "trust_level": "high",
        "governance_required": False
    },
    
    "llama3.2": {
        "specialty": ModelSpecialty.CONVERSATION,
        "capabilities": [],
        "context_window": 128_000,
        "size_gb": 2,
        "use_cases": ["lightweight chat", "quick responses"],
        "trust_level": "medium",
        "governance_required": False,
        "notes": "Lightweight and fast"
    },
    
    # Fast Response Specialists
    "phi3.5:latest": {
        "specialty": ModelSpecialty.FAST_RESPONSE,
        "capabilities": [
            ModelCapability.ULTRA_FAST
        ],
        "context_window": 128_000,
        "size_gb": 2,
        "use_cases": ["ultra-fast responses", "simple queries"],
        "trust_level": "medium",
        "governance_required": False,
        "notes": "3.8B params, extremely fast"
    },
    
    "gemma2:9b": {
        "specialty": ModelSpecialty.FAST_RESPONSE,
        "capabilities": [
            ModelCapability.ULTRA_FAST
        ],
        "context_window": 8_000,
        "size_gb": 5,
        "use_cases": ["fast general queries", "quick answers"],
        "trust_level": "medium",
        "governance_required": False
    },
    
    # Uncensored Specialists
    "dolphin-mixtral:latest": {
        "specialty": ModelSpecialty.UNCENSORED,
        "capabilities": [
            ModelCapability.MOE_ARCHITECTURE
        ],
        "context_window": 32_000,
        "size_gb": 26,
        "use_cases": ["unrestricted generation", "full capabilities"],
        "trust_level": "medium",
        "governance_required": True,
        "notes": "No restrictions, use with care"
    },
    
    "nous-hermes2-mixtral:latest": {
        "specialty": ModelSpecialty.UNCENSORED,
        "capabilities": [
            ModelCapability.MOE_ARCHITECTURE,
            ModelCapability.MULTI_STEP_REASONING
        ],
        "context_window": 32_000,
        "size_gb": 26,
        "use_cases": ["instruction following", "unrestricted tasks"],
        "trust_level": "high",
        "governance_required": False,
        "notes": "Excellent instruction following"
    },
    
    # General Purpose
    "mistral-nemo:latest": {
        "specialty": ModelSpecialty.GENERAL_PURPOSE,
        "capabilities": [],
        "context_window": 128_000,
        "size_gb": 7,
        "use_cases": ["general tasks", "efficient all-around"],
        "trust_level": "high",
        "governance_required": False
    },
    
    # Additional MoE and Agentic Models
    "qwen2.5-coder:32b": {
        "specialty": ModelSpecialty.CODING,
        "capabilities": [
            ModelCapability.CODE_GENERATION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.TOOL_CALLING
        ],
        "context_window": 128_000,
        "size_gb": 19,
        "use_cases": ["coding", "function calling", "automation"],
        "trust_level": "high",
        "governance_required": True,
        "notes": "Excellent for coding agents"
    },
    
    "nemotron:70b": {
        "specialty": ModelSpecialty.VERIFICATION,
        "capabilities": [
            ModelCapability.LOGIC_VALIDATION,
            ModelCapability.FACT_CHECKING,
            ModelCapability.MULTI_STEP_REASONING
        ],
        "context_window": 128_000,
        "size_gb": 42,
        "use_cases": ["validation", "verification", "enterprise workflows"],
        "trust_level": "very_high",
        "governance_required": True,
        "notes": "NVIDIA enterprise agent, optimized for validation"
    },
    
    "mixtral:8x22b": {
        "specialty": ModelSpecialty.REASONING,
        "capabilities": [
            ModelCapability.MOE_ARCHITECTURE,
            ModelCapability.MULTI_STEP_REASONING,
            ModelCapability.LONG_CONTEXT
        ],
        "context_window": 64_000,
        "size_gb": 82,
        "use_cases": ["reasoning", "planning", "analysis"],
        "trust_level": "very_high",
        "governance_required": True,
        "notes": "Best MoE reasoning, 141B params with 39B active"
    },
    
    "mixtral:8x7b": {
        "specialty": ModelSpecialty.VERIFICATION,
        "capabilities": [
            ModelCapability.MOE_ARCHITECTURE,
            ModelCapability.LOGIC_VALIDATION
        ],
        "context_window": 32_000,
        "size_gb": 26,
        "use_cases": ["efficient verification", "logic checks"],
        "trust_level": "high",
        "governance_required": False,
        "notes": "Most efficient MoE, 46.7B params with 12.9B active"
    },
    
    "deepseek-v2.5:236b": {
        "specialty": ModelSpecialty.REASONING,
        "capabilities": [
            ModelCapability.MOE_ARCHITECTURE,
            ModelCapability.MULTI_STEP_REASONING,
            ModelCapability.CODE_GENERATION
        ],
        "context_window": 128_000,
        "size_gb": 133,
        "use_cases": ["complex reasoning", "logic validation", "coding"],
        "trust_level": "very_high",
        "governance_required": True,
        "notes": "MoE reasoning powerhouse, 236B params"
    }
}


def get_models_by_specialty(specialty: ModelSpecialty) -> List[str]:
    """Get all models for a given specialty"""
    return [
        model for model, config in MODEL_REGISTRY.items()
        if config["specialty"] == specialty
    ]


def get_model_for_task(task_type: str, requires_governance: bool = False) -> str:
    """Route task to best model based on type"""
    
    task_specialty_map = {
        "retrieval": ModelSpecialty.RETRIEVAL,
        "research": ModelSpecialty.RESEARCH,
        "reasoning": ModelSpecialty.REASONING,
        "coding": ModelSpecialty.CODING,
        "verification": ModelSpecialty.VERIFICATION,
        "vision": ModelSpecialty.VISION,
        "conversation": ModelSpecialty.CONVERSATION,
        "fast": ModelSpecialty.FAST_RESPONSE
    }
    
    specialty = task_specialty_map.get(task_type)
    if not specialty:
        return "qwen2.5:32b"  # Default fallback
    
    models = get_models_by_specialty(specialty)
    
    if requires_governance:
        # Filter to governance-enabled models
        models = [m for m in models if MODEL_REGISTRY[m].get("governance_required", False)]
    
    # Return highest trust level model
    if models:
        return sorted(
            models,
            key=lambda m: MODEL_REGISTRY[m].get("trust_level", "low"),
            reverse=True
        )[0]
    
    return "qwen2.5:32b"  # Fallback


def get_model_info(model_name: str) -> Dict:
    """Get detailed info about a model"""
    return MODEL_REGISTRY.get(model_name, {})


def list_all_models() -> List[str]:
    """List all 21 registered models"""
    return list(MODEL_REGISTRY.keys())


def get_summary() -> Dict:
    """Get summary of model distribution"""
    summary = {}
    
    for specialty in ModelSpecialty:
        models = get_models_by_specialty(specialty)
        summary[specialty.value] = {
            "count": len(models),
            "models": models
        }
    
    return summary
