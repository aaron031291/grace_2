"""
Multi-Modal API - Grace's "Mouth"
Text, Voice, Vision responses
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal

from ..multimodal_llm import multimodal_llm

router = APIRouter(prefix="/api/multimodal", tags=["multimodal"])

class ChatRequest(BaseModel):
    message: str
    modality: Literal["text", "vision", "code", "reasoning", "fast"] = "text"
    voice_output: bool = False
    context: Optional[dict] = None

class VoiceRequest(BaseModel):
    text: str
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "nova"

@router.post("/chat")
async def multimodal_chat(request: ChatRequest):
    """
    Chat with Grace using any modality
    
    Natural language examples:
    - "Explain this code" (modality: code)
    - "What's in this image?" (modality: vision)
    - "Quick status check" (modality: fast)
    - "Analyze this complex problem" (modality: reasoning)
    
    Grace automatically selects the best model!
    """
    
    response = await multimodal_llm.generate_response(
        user_message=request.message,
        modality=request.modality,
        context=request.context,
        voice_output=request.voice_output
    )
    
    return {
        "response": response["text"],
        "model_used": response["model_used"],
        "modality": response["modality"],
        "audio_url": response.get("audio_url"),
        "has_audio": response.get("has_audio", False),
        "timestamp": response["timestamp"]
    }

@router.post("/voice/tts")
async def text_to_speech(request: VoiceRequest):
    """
    Generate voice from text
    
    Natural language: "Read this out loud"
    Grace generates natural voice
    """
    
    audio_url = await multimodal_llm._generate_voice(request.text)
    
    if audio_url:
        return {
            "success": True,
            "audio_url": audio_url,
            "text": request.text,
            "voice": request.voice
        }
    else:
        raise HTTPException(status_code=500, detail="TTS not available")

@router.post("/voice/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """
    Transcribe voice to text
    
    Natural language: User speaks, Grace transcribes
    """
    
    audio_bytes = await audio.read()
    transcription = await multimodal_llm.transcribe_voice(audio_bytes)
    
    if transcription:
        return {
            "success": True,
            "transcription": transcription,
            "language": "en"
        }
    else:
        raise HTTPException(status_code=500, detail="STT not available")

@router.post("/vision/analyze")
async def analyze_image(image_url: str, question: str = "What's in this image?"):
    """
    Analyze image with vision model
    
    Natural language: "What's in this screenshot?"
    Grace uses GPT-4 Vision
    """
    
    analysis = await multimodal_llm.analyze_image(image_url, question)
    
    return {
        "success": True,
        "analysis": analysis,
        "image_url": image_url,
        "model_used": "gpt-4-vision"
    }

@router.get("/models")
async def get_available_models():
    """
    Get info about available models
    
    Shows which models Grace can use
    """
    return multimodal_llm.get_model_info()

@router.post("/mode")
async def set_mode(mode: Literal["fast", "balanced", "quality"]):
    """
    Set response mode
    
    - fast: Quick responses (GPT-3.5)
    - balanced: Good quality (GPT-4-turbo)
    - quality: Best responses (GPT-4/Claude Opus)
    """
    multimodal_llm.mode = mode
    return {
        "success": True,
        "mode": mode,
        "message": f"Grace will now use {mode} mode"
    }

@router.post("/voice/toggle")
async def toggle_voice(enabled: bool):
    """
    Toggle voice output
    
    When enabled, Grace speaks responses
    """
    multimodal_llm.use_voice = enabled
    return {
        "success": True,
        "voice_enabled": enabled,
        "message": "Grace will speak responses" if enabled else "Voice output disabled"
    }
