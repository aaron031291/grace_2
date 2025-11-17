"""
Speech Domain Router
Consolidates all speech and audio operations: ASR/TTS/VAD, audio transforms, diarization

Bounded Context: Speech and audio processing
- ASR: Automatic Speech Recognition (speech-to-text)
- TTS: Text-to-Speech synthesis
- VAD: Voice Activity Detection
- Transforms: Audio processing and enhancement
- Diarization: Speaker identification and segmentation

Canonical Verbs: transcribe, synthesize, detect, transform, diarize
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Dict, Any, Optional
from pydantic import BaseModel

from ..auth import get_current_user
from ..speech_service import speech_service
from ..audio_processor import audio_processor

router = APIRouter(prefix="/api/speech", tags=["Speech Domain"])


class TranscribeRequest(BaseModel):
    language: str = "en-US"
    model: str = "default"
    enable_punctuation: bool = True
    enable_timestamps: bool = False


class SynthesizeRequest(BaseModel):
    text: str
    voice: str = "default"
    speed: float = 1.0
    pitch: float = 0.0
    format: str = "mp3"


class VoiceActivityRequest(BaseModel):
    sensitivity: float = 0.5
    min_duration: float = 0.3


class TransformRequest(BaseModel):
    transform_type: str  # "noise_reduction", "volume_normalize", "echo_cancel"
    parameters: Dict[str, Any] = {}


class DiarizeRequest(BaseModel):
    num_speakers: Optional[int] = None
    confidence_threshold: float = 0.7


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    request: TranscribeRequest = None,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Transcribe audio file to text"""
    try:
        if not request:
            request = TranscribeRequest()

        # Read audio file
        audio_data = await file.read()

        result = await speech_service.transcribe(
            audio_data=audio_data,
            language=request.language,
            model=request.model,
            punctuation=request.enable_punctuation,
            timestamps=request.enable_timestamps
        )

        return {
            "text": result.get("text", ""),
            "confidence": result.get("confidence", 0.0),
            "language": request.language,
            "duration": result.get("duration", 0.0),
            "timestamps": result.get("timestamps", []) if request.enable_timestamps else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/synthesize")
async def synthesize_speech(
    request: SynthesizeRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Convert text to speech"""
    try:
        result = await speech_service.synthesize(
            text=request.text,
            voice=request.voice,
            speed=request.speed,
            pitch=request.pitch,
            format=request.format
        )

        return {
            "audio_data": result.get("audio_base64", ""),
            "format": request.format,
            "duration": result.get("duration", 0.0),
            "text": request.text,
            "voice": request.voice
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-activity")
async def detect_voice_activity(
    file: UploadFile = File(...),
    request: VoiceActivityRequest = None,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Detect voice activity in audio"""
    try:
        if not request:
            request = VoiceActivityRequest()

        audio_data = await file.read()

        result = await audio_processor.detect_voice_activity(
            audio_data=audio_data,
            sensitivity=request.sensitivity,
            min_duration=request.min_duration
        )

        return {
            "segments": result.get("segments", []),
            "total_speech_duration": result.get("total_duration", 0.0),
            "segment_count": len(result.get("segments", [])),
            "sensitivity": request.sensitivity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transform")
async def transform_audio(
    file: UploadFile = File(...),
    request: TransformRequest = None,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Apply audio transformation"""
    try:
        if not request:
            request = TransformRequest(transform_type="noise_reduction")

        audio_data = await file.read()

        result = await audio_processor.transform_audio(
            audio_data=audio_data,
            transform_type=request.transform_type,
            parameters=request.parameters
        )

        return {
            "transformed_audio": result.get("audio_base64", ""),
            "transform_type": request.transform_type,
            "parameters": request.parameters,
            "original_duration": result.get("original_duration", 0.0),
            "processed_duration": result.get("processed_duration", 0.0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diarize")
async def diarize_audio(
    file: UploadFile = File(...),
    request: DiarizeRequest = None,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Perform speaker diarization"""
    try:
        if not request:
            request = DiarizeRequest()

        audio_data = await file.read()

        result = await audio_processor.diarize(
            audio_data=audio_data,
            num_speakers=request.num_speakers,
            confidence_threshold=request.confidence_threshold
        )

        return {
            "speakers": result.get("speakers", []),
            "segments": result.get("segments", []),
            "speaker_count": len(result.get("speakers", [])),
            "confidence_threshold": request.confidence_threshold
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def list_voices(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List available TTS voices"""
    try:
        voices = await speech_service.list_voices()
        return {
            "voices": voices,
            "count": len(voices)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages")
async def list_languages(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List supported languages for ASR"""
    try:
        languages = await speech_service.list_languages()
        return {
            "languages": languages,
            "count": len(languages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream/transcribe")
async def start_stream_transcription(
    request: TranscribeRequest = None,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Start streaming transcription session"""
    try:
        if not request:
            request = TranscribeRequest()

        session = await speech_service.start_stream_transcription(
            language=request.language,
            model=request.model,
            punctuation=request.enable_punctuation
        )

        return {
            "session_id": session.get("id"),
            "status": "started",
            "language": request.language,
            "websocket_url": session.get("websocket_url")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream/synthesize")
async def start_stream_synthesis(
    request: SynthesizeRequest = None,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Start streaming synthesis session"""
    try:
        if not request:
            request = request or SynthesizeRequest(text="")

        session = await speech_service.start_stream_synthesis(
            voice=request.voice,
            speed=request.speed,
            pitch=request.pitch,
            format=request.format
        )

        return {
            "session_id": session.get("id"),
            "status": "started",
            "voice": request.voice,
            "websocket_url": session.get("websocket_url")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List available speech models"""
    try:
        models = await speech_service.list_models()
        return {
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/{audio_id}")
async def analyze_audio(
    audio_id: str,
    analysis_type: str = "comprehensive",
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Perform comprehensive audio analysis"""
    try:
        analysis = await audio_processor.analyze_audio(
            audio_id=audio_id,
            analysis_type=analysis_type
        )

        return {
            "audio_id": audio_id,
            "analysis_type": analysis_type,
            "results": analysis,
            "duration": analysis.get("duration", 0.0),
            "quality_score": analysis.get("quality_score", 0.0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))