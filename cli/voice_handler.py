"""
Voice handler for audio recording and playback
"""

import asyncio
from pathlib import Path
from typing import Optional
import wave


class AudioRecorder:
    """Handle audio recording"""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1, format: str = "wav"):
        self.sample_rate = sample_rate
        self.channels = channels
        self.format = format
        self.is_recording = False
    
    async def record(self, duration: int, output_file: Path) -> bool:
        """Record audio for specified duration"""
        try:
            import pyaudio
        except ImportError:
            raise ImportError("PyAudio not installed. Install with: pip install pyaudio")
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        
        audio = pyaudio.PyAudio()
        
        try:
            stream = audio.open(
                format=FORMAT,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            self.is_recording = True
            frames = []
            
            for _ in range(0, int(self.sample_rate / CHUNK * duration)):
                if not self.is_recording:
                    break
                data = stream.read(CHUNK)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            # Save to file
            wf = wave.open(str(output_file), 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            return True
        
        except Exception as e:
            print(f"Recording error: {e}")
            return False
        finally:
            audio.terminate()
            self.is_recording = False
    
    def stop_recording(self):
        """Stop current recording"""
        self.is_recording = False


class AudioPlayer:
    """Handle audio playback"""
    
    def __init__(self):
        self.is_playing = False
    
    async def play(self, audio_file: Path) -> bool:
        """Play audio file"""
        try:
            from pydub import AudioSegment
            from pydub.playback import play
        except ImportError:
            raise ImportError("pydub not installed. Install with: pip install pydub")
        
        try:
            self.is_playing = True
            audio = AudioSegment.from_wav(str(audio_file))
            
            # Play in separate thread to avoid blocking
            await asyncio.to_thread(play, audio)
            
            return True
        
        except Exception as e:
            print(f"Playback error: {e}")
            return False
        finally:
            self.is_playing = False
    
    def stop_playback(self):
        """Stop current playback"""
        self.is_playing = False


class VoiceHandler:
    """Combined voice handler for recording and playback"""
    
    def __init__(self, temp_dir: Optional[Path] = None):
        self.temp_dir = temp_dir or Path.home() / ".grace" / "audio"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.recorder = AudioRecorder()
        self.player = AudioPlayer()
    
    async def record_audio(self, duration: int = 5) -> Optional[Path]:
        """Record audio and return file path"""
        import time
        output_file = self.temp_dir / f"recording_{int(time.time())}.wav"
        
        success = await self.recorder.record(duration, output_file)
        
        if success and output_file.exists():
            return output_file
        return None
    
    async def play_audio(self, audio_file: Path) -> bool:
        """Play audio file"""
        if not audio_file.exists():
            return False
        
        return await self.player.play(audio_file)
    
    def stop_recording(self):
        """Stop current recording"""
        self.recorder.stop_recording()
    
    def stop_playback(self):
        """Stop current playback"""
        self.player.stop_playback()
    
    def cleanup(self):
        """Clean up old temporary files"""
        import time
        current_time = time.time()
        
        # Delete files older than 1 hour
        for file in self.temp_dir.glob("*.wav"):
            if current_time - file.stat().st_mtime > 3600:
                try:
                    file.unlink()
                except Exception:
                    pass
