"""Text-to-Speech Service"""

import asyncio
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import aiofiles

from sqlalchemy import select, update
from .models import async_session
from .speech_models import TextToSpeechMessage
from .verification import VerificationEngine
from .immutable_log import ImmutableLogger

class TTSService:
    """Manages text-to-speech generation"""
    
    def __init__(self):
        self.tts_storage_path = Path("./audio_messages/tts")
        self.tts_storage_path.mkdir(parents=True, exist_ok=True)
        
        self.verification = VerificationEngine()
        self.audit = ImmutableLogger()
        
        self.tts_engine = None  # Lazy load
        self.engine_type = None  # "coqui", "pyttsx3", or "mock"
    
    def _initialize_tts_engine(self):
        """
        Initialize TTS engine (lazy loading)
        Try Coqui TTS first, fallback to pyttsx3, then mock
        """
        if self.tts_engine is not None:
            return
        
        # Try Coqui TTS
        try:
            from TTS.api import TTS
            self.tts_engine = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
            self.engine_type = "coqui"
            print("✓ Coqui TTS loaded")
            return
        except ImportError:
            print("⚠ Coqui TTS not installed, trying pyttsx3...")
        except Exception as e:
            print(f"⚠ Coqui TTS failed to load: {e}, trying pyttsx3...")
        
        # Try pyttsx3
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.engine_type = "pyttsx3"
            
            # Configure voice
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Prefer female voice for Grace
                female_voices = [v for v in voices if 'female' in v.name.lower()]
                if female_voices:
                    self.tts_engine.setProperty('voice', female_voices[0].id)
                else:
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            print("✓ pyttsx3 TTS loaded")
            return
        except ImportError:
            print("⚠ pyttsx3 not installed, using mock TTS")
        except Exception as e:
            print(f"⚠ pyttsx3 failed to load: {e}, using mock TTS")
        
        # Fallback to mock
        self.engine_type = "mock"
        print("⚠ Using mock TTS (no audio generation)")
    
    async def generate_speech(
        self,
        user: str,
        text: str,
        voice_model: str = "default",
        speed: float = 1.0,
        pitch: float = 1.0,
        reply_to_speech_id: Optional[int] = None,
        reply_to_chat_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate speech from text
        
        Returns:
            {
                "tts_id": int,
                "audio_path": str,
                "status": str,
                "verification_id": str
            }
        """
        
        # Generate unique ID
        tts_id_str = str(uuid.uuid4())
        filename = f"tts_{user}_{tts_id_str}.mp3"
        audio_path = self.tts_storage_path / filename
        
        # Create verification envelope
        verification_id = self.verification.create_envelope(
            action_id=tts_id_str,
            actor=user,
            action_type="tts_generation",
            resource=str(audio_path),
            input_data={"text": text, "voice_model": voice_model}
        )
        
        # Create TTS message record
        async with async_session() as session:
            tts_msg = TextToSpeechMessage(
                user=user,
                session_id=session_id or tts_id_str,
                text_content=text,
                audio_path=str(audio_path),
                audio_format="mp3",
                tts_service=self.engine_type or "pending",
                voice_model=voice_model,
                voice_speed=speed,
                voice_pitch=pitch,
                reply_to_speech_id=reply_to_speech_id,
                reply_to_chat_id=reply_to_chat_id,
                status="pending",
                verification_envelope_id=verification_id
            )
            session.add(tts_msg)
            await session.commit()
            await session.refresh(tts_msg)
            
            tts_id = tts_msg.id
        
        # Log to audit trail
        audit_id = await self.audit.log_event(
            actor=user,
            action="tts_generation",
            resource=f"tts_message_{tts_id}",
            result="queued",
            details={"text_length": len(text), "voice_model": voice_model}
        )
        
        # Queue for generation (async task)
        asyncio.create_task(self._generate_audio(tts_id))
        
        return {
            "tts_id": tts_id,
            "audio_path": str(audio_path),
            "status": "pending",
            "verification_id": verification_id,
            "queued_for_generation": True
        }
    
    async def _generate_audio(self, tts_id: int):
        """
        Background task to generate audio using TTS engine
        """
        try:
            # Initialize engine if needed
            self._initialize_tts_engine()
            
            # Update status to generating
            async with async_session() as session:
                await session.execute(
                    update(TextToSpeechMessage)
                    .where(TextToSpeechMessage.id == tts_id)
                    .values(
                        status="generating",
                        tts_service=self.engine_type
                    )
                )
                await session.commit()
            
            # Get TTS message
            async with async_session() as session:
                result = await session.execute(
                    select(TextToSpeechMessage).where(TextToSpeechMessage.id == tts_id)
                )
                tts_msg = result.scalar_one_or_none()
                
                if not tts_msg:
                    return
                
                text = tts_msg.text_content
                audio_path = tts_msg.audio_path
                speed = tts_msg.voice_speed
                pitch = tts_msg.voice_pitch
            
            # Generate audio based on engine type
            if self.engine_type == "coqui":
                # Coqui TTS
                self.tts_engine.tts_to_file(
                    text=text,
                    file_path=audio_path
                )
            
            elif self.engine_type == "pyttsx3":
                # pyttsx3
                self.tts_engine.setProperty('rate', int(150 * speed))
                # Note: pyttsx3 doesn't support pitch directly
                self.tts_engine.save_to_file(text, audio_path)
                self.tts_engine.runAndWait()
            
            elif self.engine_type == "mock":
                # Mock - create dummy file
                async with aiofiles.open(audio_path, 'w') as f:
                    await f.write("[Mock TTS audio file - install TTS or pyttsx3]")
            
            # Get file size and duration (if available)
            audio_size = 0
            audio_duration = None
            
            if os.path.exists(audio_path):
                audio_size = os.path.getsize(audio_path)
                
                # Try to get duration with mutagen
                try:
                    from mutagen.mp3 import MP3
                    audio_file = MP3(audio_path)
                    audio_duration = int(audio_file.info.length * 1000)  # milliseconds
                except:
                    pass
            
            # Update status to completed
            async with async_session() as session:
                await session.execute(
                    update(TextToSpeechMessage)
                    .where(TextToSpeechMessage.id == tts_id)
                    .values(
                        status="completed",
                        audio_size_bytes=audio_size,
                        audio_duration_ms=audio_duration,
                        generated_at=datetime.utcnow()
                    )
                )
                await session.commit()
            
            print(f"✓ TTS generation completed for message {tts_id}")
        
        except Exception as e:
            # Update status to failed
            async with async_session() as session:
                await session.execute(
                    update(TextToSpeechMessage)
                    .where(TextToSpeechMessage.id == tts_id)
                    .values(
                        status="failed",
                        error_message=str(e)
                    )
                )
                await session.commit()
            
            print(f"✗ TTS generation failed for message {tts_id}: {e}")
    
    async def get_tts_message(self, tts_id: int) -> Optional[Dict[str, Any]]:
        """Get TTS message by ID"""
        
        async with async_session() as session:
            result = await session.execute(
                select(TextToSpeechMessage).where(TextToSpeechMessage.id == tts_id)
            )
            tts_msg = result.scalar_one_or_none()
            
            if not tts_msg:
                return None
            
            return {
                "id": tts_msg.id,
                "user": tts_msg.user,
                "session_id": tts_msg.session_id,
                "text_content": tts_msg.text_content,
                "audio_path": tts_msg.audio_path,
                "audio_format": tts_msg.audio_format,
                "audio_size_bytes": tts_msg.audio_size_bytes,
                "audio_duration_ms": tts_msg.audio_duration_ms,
                "tts_service": tts_msg.tts_service,
                "voice_model": tts_msg.voice_model,
                "status": tts_msg.status,
                "reply_to_speech_id": tts_msg.reply_to_speech_id,
                "reply_to_chat_id": tts_msg.reply_to_chat_id,
                "created_at": tts_msg.created_at.isoformat() if tts_msg.created_at else None,
                "generated_at": tts_msg.generated_at.isoformat() if tts_msg.generated_at else None
            }

tts_service = TTSService()
