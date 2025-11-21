"""
Models API - Model fleet monitoring and management
Provides model availability, performance, and selection endpoints
"""

from fastapi import APIRouter
from typing import Dict, List
import logging

from backend.model_categorization import (
    get_summary,
    get_models_by_specialty,
    get_model_info,
    list_all_models,
    ModelSpecialty
)

router = APIRouter(prefix="/api/models", tags=["models"])
logger = logging.getLogger(__name__)


@router.get("/available")
async def list_available_models():
    """
    List all available models grouped by specialty.
    
    Returns:
        Summary of 21 models organized by category
    """
    return get_summary()


@router.get("/all")
async def get_all_models():
    """
    Get detailed info for all 21 models.
    
    Returns:
        List of all models with full metadata
    """
    models = list_all_models()
    detailed = []
    
    for model_name in models:
        info = get_model_info(model_name)
        detailed.append({
            "name": model_name,
            **info
        })
    
    return {"models": detailed, "total": len(detailed)}


@router.get("/specialty/{specialty}")
async def get_models_by_specialty_endpoint(specialty: str):
    """
    Get models for a specific specialty.
    
    Args:
        specialty: One of: retrieval, research, reasoning, coding, 
                  verification, vision, conversation, fast_response, 
                  uncensored, general_purpose
    """
    try:
        specialty_enum = ModelSpecialty(specialty)
        models = get_models_by_specialty(specialty_enum)
        
        detailed = []
        for model_name in models:
            info = get_model_info(model_name)
            detailed.append({
                "name": model_name,
                **info
            })
        
        return {
            "specialty": specialty,
            "models": detailed,
            "count": len(detailed)
        }
    except ValueError:
        return {
            "error": f"Invalid specialty: {specialty}",
            "valid_specialties": [s.value for s in ModelSpecialty]
        }


@router.get("/info/{model_name}")
async def get_model_details(model_name: str):
    """
    Get detailed information about a specific model.
    
    Args:
        model_name: Name of the model (e.g., "deepseek-r1:70b")
    """
    info = get_model_info(model_name)
    
    if not info:
        return {
            "error": f"Model not found: {model_name}",
            "available_models": list_all_models()
        }
    
    return {
        "name": model_name,
        **info
    }


@router.get("/performance")
async def get_model_performance():
    """
    Get model performance metrics.
    
    Note: This would require tracking actual usage.
    For now, returns theoretical performance based on size.
    """
    models = list_all_models()
    performance = []
    
    for model_name in models:
        info = get_model_info(model_name)
        
        # Estimate speed based on size (smaller = faster)
        size_gb = info.get("size_gb", 10)
        estimated_speed = "fast" if size_gb < 10 else "medium" if size_gb < 50 else "slow"
        
        performance.append({
            "name": model_name,
            "specialty": info.get("specialty").value if info.get("specialty") else "unknown",
            "size_gb": size_gb,
            "estimated_speed": estimated_speed,
            "context_window": info.get("context_window", 0)
        })
    
    return {"models": performance}


@router.get("/current-usage")
async def get_current_model_usage():
    """
    Get which models are currently being used by which components.
    
    Returns:
        Mapping of components to their active models
    """
    return {
        "builder_agent": {
            "planning": "mixtral:8x22b",
            "code_generation": "qwen2.5-coder:32b",
            "quick_fixes": "codegemma:7b"
        },
        "self_reflection_loop": {
            "analysis": "deepseek-v2.5:236b"
        },
        "research_pipeline": {
            "research": "qwen2.5:72b",
            "code_generation": "qwen2.5-coder:32b"
        }
    }
