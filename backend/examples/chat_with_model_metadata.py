"""
Example: Returning Model Metadata in Chat Responses
Shows how to include model_used in all AI responses
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    task_type: str = "general"
    model: str = None  # Optional override
    context: dict = {}


class ChatResponse(BaseModel):
    response: str
    model_used: str  # ✅ ADD THIS
    task_type: str
    reasoning_steps: list = []
    citations: list = []
    metadata: dict = {}


# ============================================================================
# BEFORE (No model info)
# ============================================================================

@router.post("/old")
async def chat_old(req: ChatRequest):
    """Old approach - doesn't return model info"""
    
    # Generate response
    response_text = "Here's my response..."
    
    # ❌ User doesn't know which model was used
    return {
        "response": response_text
    }


# ============================================================================
# AFTER (With model metadata)
# ============================================================================

@router.post("/")
async def chat_endpoint(req: ChatRequest):
    """New approach - includes model metadata"""
    
    from backend.model_orchestrator import model_orchestrator
    
    # Let orchestrator select model based on task_type
    if req.model:
        # User specified model
        selected_model = req.model
    else:
        # Auto-select based on task
        selected_model = model_orchestrator.select_model_for_task(
            task_type=req.task_type,
            context=req.context
        )
    
    # Check if model is available
    if not model_orchestrator.is_model_loaded(selected_model):
        # Fallback to next best
        fallback_model = model_orchestrator.get_fallback_model(req.task_type)
        print(f"[CHAT] Model {selected_model} not loaded, using {fallback_model}")
        selected_model = fallback_model
    
    # Generate response using selected model
    response_text = await model_orchestrator.generate(
        model=selected_model,
        prompt=req.message,
        context=req.context
    )
    
    # Extract any reasoning steps or citations
    reasoning_steps = []
    citations = []
    
    # If the model provided reasoning, extract it
    if hasattr(response_text, 'reasoning'):
        reasoning_steps = response_text.reasoning
    
    # ✅ Return model info in response
    return ChatResponse(
        response=response_text,
        model_used=selected_model,  # ✅ INCLUDE THIS
        task_type=req.task_type,
        reasoning_steps=reasoning_steps,
        citations=citations,
        metadata={
            "model_selection": "auto" if not req.model else "manual",
            "fallback_used": selected_model != req.model if req.model else False,
        }
    )


# ============================================================================
# Example: Model Selection Logic
# ============================================================================

def select_model_for_task(task_type: str) -> str:
    """
    Select optimal model based on task type
    This is in model_orchestrator.py
    """
    
    model_map = {
        "coding": "deepseek-coder-v2:16b",
        "debugging": "deepseek-coder-v2:16b",
        "review": "qwen2.5:32b",
        "reasoning": "qwen2.5:32b",
        "research": "qwen2.5:32b",
        "vision": "llava:34b",
        "long_context": "kimi:1.5-latest",
        "general": "qwen2.5:7b",  # Fast for general queries
    }
    
    return model_map.get(task_type, "qwen2.5:7b")


def get_fallback_model(task_type: str) -> str:
    """Fallback if primary model not available"""
    
    fallback_chain = {
        "coding": ["deepseek-coder-v2:16b", "qwen2.5:32b", "qwen2.5:7b"],
        "reasoning": ["qwen2.5:32b", "qwen2.5:7b", "deepseek-coder-v2:16b"],
        "vision": ["llava:34b", "qwen2.5:7b"],
    }
    
    chain = fallback_chain.get(task_type, ["qwen2.5:7b"])
    
    # Return first available model
    for model in chain:
        if is_model_loaded(model):
            return model
    
    # Ultimate fallback
    return "qwen2.5:7b"


# ============================================================================
# Example: Check Model Availability
# ============================================================================

def is_model_loaded(model_name: str) -> bool:
    """
    Check if model is loaded in Ollama
    """
    import requests
    
    try:
        response = requests.get("http://localhost:11434/api/tags")
        loaded_models = response.json().get("models", [])
        
        return any(m["name"] == model_name for m in loaded_models)
    except:
        return False


# ============================================================================
# Example: Full Integration
# ============================================================================

@router.post("/complete")
async def complete_chat_with_model_metadata(req: ChatRequest):
    """
    Complete example with model selection, fallback, and metadata
    """
    
    # 1. Determine model
    selected_model = req.model or select_model_for_task(req.task_type)
    
    # 2. Check availability
    if not is_model_loaded(selected_model):
        fallback = get_fallback_model(req.task_type)
        print(f"[CHAT] {selected_model} not available, using {fallback}")
        selected_model = fallback
    
    # 3. Generate response
    try:
        result = await model_orchestrator.generate(
            model=selected_model,
            prompt=req.message,
            task_type=req.task_type,
            context=req.context
        )
        
        response_text = result.text
        reasoning = result.reasoning if hasattr(result, 'reasoning') else []
        
    except Exception as e:
        # Last resort fallback
        print(f"[CHAT] Error with {selected_model}: {e}")
        selected_model = "qwen2.5:7b"
        result = await model_orchestrator.generate(
            model=selected_model,
            prompt=req.message
        )
        response_text = result.text
        reasoning = []
    
    # 4. Return with full metadata
    return {
        "response": response_text,
        "model_used": selected_model,  # ✅ UI displays this
        "task_type": req.task_type,
        "reasoning_steps": reasoning,
        "citations": extract_citations(response_text),
        "metadata": {
            "model_selection": "manual" if req.model else "auto",
            "primary_model": req.model or select_model_for_task(req.task_type),
            "fallback_used": False,
            "confidence": 0.85,
        }
    }


# ============================================================================
# To integrate into existing backend/routes/chat.py:
# ============================================================================

"""
1. Import model orchestrator:
   from backend.model_orchestrator import model_orchestrator

2. Before generating response:
   selected_model = model_orchestrator.select_model_for_task(task_type)

3. Generate with that model:
   response = await model_orchestrator.generate(model=selected_model, ...)

4. Return model info:
   return ChatResponse(
       response=response,
       model_used=selected_model  # ✅ ADD THIS
   )
"""
