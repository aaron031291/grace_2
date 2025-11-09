# Grace Speech Pipeline

Complete end-to-end voice interaction system with transcription, security scanning, and text-to-speech responses.

## Architecture Overview

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       │ 1. Record Audio (MediaRecorder API)
       ├──────────────────────────────────────┐
       │                                      │
       │ 2. Upload Audio                      │ WebSocket (Real-time)
       │    POST /api/audio/upload            │ /api/audio/ws
       │                                      │
       v                                      v
┌──────────────────────────────────────────────┐
│           Speech Service (Backend)           │
├──────────────────────────────────────────────┤
│ • Save audio file                            │
│ • Create verification envelope               │
│ • Queue for transcription                    │
│ • Audit logging                              │
└──────┬───────────────────────────────────────┘
       │
       │ 3. Transcribe (Async Task)
       ├─────────────────┐
       │                 │
       v                 v
┌─────────────┐   ┌──────────────┐
│   Whisper   │   │  Hunter      │
│   Model     │   │  Security    │
│ (STT Engine)│   │  Scanning    │
└──────┬──────┘   └──────┬───────┘
       │                 │
       │ Transcript      │ Security Check
       │                 │
       v                 v
┌──────────────────────────────────────────────┐
│         Database (speech_messages)           │
│ • Transcript + confidence                    │
│ • Review status (if flagged)                 │
│ • Audio path + metadata                      │
└──────┬───────────────────────────────────────┘
       │
       │ 4. Response Generation
       ├──────────────────┐
       │                  │
       v                  v
┌─────────────┐    ┌──────────────┐
│    Grace    │    │  TTS Service │
│   (LLM)     │───>│  (Coqui/     │
│  Response   │    │   pyttsx3)   │
└─────────────┘    └──────┬───────┘
                          │
                          │ 5. Audio File
                          v
                   ┌──────────────┐
                   │   Client     │
                   │  Audio       │
                   │  Player      │
                   └──────────────┘
```

## Components

### Backend Services

#### 1. SpeechService (`backend/speech_service.py`)
- **upload_audio()** - Store audio file, create verification envelope, queue transcription
- **_transcribe_audio()** - Background task using Whisper (or mock for testing)
- **_check_transcript_security()** - Run Hunter security scans on transcript
- **get_speech_message()** - Retrieve speech message by ID
- **list_speech_messages()** - List user's speech messages
- **review_transcript()** - Approve/reject transcript
- **delete_speech_message()** - Delete with governance approval

#### 2. TTSService (`backend/tts_service.py`)
- **generate_speech()** - Convert text to speech audio
- **_generate_audio()** - Background task for TTS generation
- **get_tts_message()** - Retrieve TTS message by ID
- Supports: Coqui TTS (preferred), pyttsx3 (fallback), mock (testing)

#### 3. Speech API (`backend/routes/speech_api.py`)
REST endpoints and WebSocket for speech interactions

### Frontend Components

#### 1. AudioRecorder (`SpeechInterface/AudioRecorder.tsx`)
- Microphone access via `getUserMedia()`
- Real-time waveform visualization
- Recording time display
- MediaRecorder with WebM/Opus encoding

#### 2. AudioPlayer (`SpeechInterface/AudioPlayer.tsx`)
- Play/pause controls
- Timeline seeking
- Playback speed control (0.5x - 2x)
- Volume control
- Transcript display with confidence badge

#### 3. SpeechHistory (`SpeechInterface/SpeechHistory.tsx`)
- List all voice messages
- Filter by session
- Status badges (transcribing, needs review, etc.)
- Expandable audio player per message

#### 4. TranscriptView (`SpeechInterface/TranscriptView.tsx`)
- Display transcript with confidence level
- Edit transcript capability
- Review panel (approve/reject)
- Security warnings for quarantined content

## API Documentation

### Upload Audio
```http
POST /api/audio/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <audio file>
session_id: <optional session ID>

Response:
{
  "speech_id": 123,
  "audio_path": "./audio_messages/user_uuid.webm",
  "status": "uploaded",
  "verification_id": "env_123",
  "queued_for_transcription": true
}
```

### Get Speech Message
```http
GET /api/audio/{speech_id}
Authorization: Bearer <token>

Response:
{
  "id": 123,
  "user": "test_user",
  "transcript": "Hello Grace, how are you?",
  "confidence": 0.95,
  "language": "en",
  "status": "completed",
  "needs_review": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Stream Audio File
```http
GET /api/audio/{speech_id}/file
Authorization: Bearer <token>

Response: Audio file stream (audio/webm)
```

### List Speech Messages
```http
GET /api/audio/list?session_id=<optional>&limit=50
Authorization: Bearer <token>

Response:
{
  "messages": [
    {
      "id": 123,
      "session_id": "sess_123",
      "transcript": "...",
      "confidence": 0.95,
      "status": "completed",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Review Transcript
```http
POST /api/audio/{speech_id}/review
Authorization: Bearer <token>
Content-Type: application/json

{
  "approved": true,
  "notes": "Transcript verified"
}

Response:
{
  "speech_id": 123,
  "review_status": "approved",
  "reviewed_by": "admin"
}
```

### Delete Speech Message
```http
DELETE /api/audio/{speech_id}
Authorization: Bearer <token>

Response:
{
  "deleted": true,
  "speech_id": 123,
  "approval_id": 456
}
```

### Generate TTS
```http
POST /api/audio/tts/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "Hello, this is Grace speaking",
  "voice_model": "default",
  "speed": 1.0,
  "pitch": 1.0,
  "reply_to_speech_id": 123
}

Response:
{
  "tts_id": 456,
  "audio_path": "./audio_messages/tts/tts_user_uuid.mp3",
  "status": "pending",
  "queued_for_generation": true
}
```

### Get TTS File
```http
GET /api/audio/tts/{tts_id}/file
Authorization: Bearer <token>

Response: Audio file stream (audio/mpeg)
```

### WebSocket Real-time
```javascript
ws://localhost:8000/api/audio/ws?user=<username>

// Client sends audio chunk
{
  "type": "audio_chunk",
  "data": "<base64_audio>",
  "format": "webm"
}

// Server sends transcription update
{
  "type": "transcript_update",
  "speech_id": 123,
  "transcript": "partial transcript...",
  "confidence": 0.85
}
```

## Database Schema

### speech_messages
- id (PK)
- user
- session_id
- audio_path, audio_format, audio_size_bytes, audio_hash
- transcript, language, confidence
- transcription_service, transcription_model
- status (uploaded, transcribing, completed, failed)
- needs_review, review_status, reviewed_by
- verification_envelope_id, audit_log_id
- created_at, transcribed_at, reviewed_at

### tts_messages
- id (PK)
- user, session_id
- text_content
- audio_path, audio_format, audio_size_bytes
- tts_service, voice_model, voice_speed, voice_pitch
- status (pending, generating, completed, failed)
- reply_to_speech_id, reply_to_chat_id
- verification_envelope_id
- created_at, generated_at

### speech_sessions
- id (PK)
- session_id (unique)
- user
- started_at, ended_at
- total_messages, total_duration_ms, avg_confidence
- context_summary, primary_language
- status (active, completed, abandoned)

### audio_quality
- id (PK)
- speech_message_id (FK)
- sample_rate, bit_rate, channels
- noise_level, signal_to_noise_ratio
- clipping_detected, distortion_level
- quality_score (0-100)

## Installation

### Whisper (Speech-to-Text)
```bash
# Install OpenAI Whisper
pip install openai-whisper

# For faster inference (optional)
pip install whisper-jax

# System dependencies (Windows)
# Install ffmpeg from https://ffmpeg.org/download.html
```

### TTS Engines

#### Option 1: Coqui TTS (Recommended)
```bash
pip install TTS

# Test installation
tts --text "Hello Grace" --out_path test.wav
```

#### Option 2: pyttsx3 (Fallback)
```bash
pip install pyttsx3

# Windows: Uses SAPI5
# Linux: Requires espeak
# macOS: Uses NSSpeechSynthesizer
```

### Frontend Dependencies
```bash
cd grace-frontend
npm install

# No additional packages needed - uses browser MediaRecorder API
```

## Security Features

### Hunter Integration
- Profanity detection in transcripts
- PII scanning (credit cards, SSNs, etc.)
- Threat detection (violence, harm)
- Auto-quarantine for critical issues
- Governance approval for deletions

### Verification
- Audio file hash verification
- Verification envelopes for all operations
- Immutable audit trail
- Chain-of-custody for audio files

### Privacy
- Audio files stored locally (not cloud)
- Encryption at rest (optional)
- Automatic cleanup of old files
- User-controlled deletion with governance

## Memory Integration

Speech messages are automatically integrated into Grace's memory system:

```python
# Speech transcripts are searchable
memory_service.search(
    query="What did I say about the project?",
    category="speech_transcript"
)

# Link speech to chat messages
memory_service.create_artifact(
    path=f"/conversations/{session_id}/speech_{speech_id}",
    content=transcript,
    category="conversation",
    metadata={
        "speech_id": speech_id,
        "confidence": confidence,
        "audio_hash": audio_hash
    }
)
```

## Testing

### Run Tests
```bash
cd grace_rebuild
python -m pytest tests/test_speech_pipeline.py -v

# Or run directly
python tests/test_speech_pipeline.py
```

### Test Coverage
- ✓ Audio upload
- ✓ Transcription (mock and real)
- ✓ Speech list
- ✓ Transcript review
- ✓ TTS generation
- ✓ Security scanning
- ✓ Message deletion
- ✓ Full conversation flow

## Usage Examples

### Frontend Integration
```typescript
import { AudioRecorder, AudioPlayer, SpeechHistory } from './components/SpeechInterface';

function ChatInterface() {
  const handleRecordingComplete = async (audioBlob: Blob) => {
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.webm');
    
    const response = await fetch('/api/audio/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    const result = await response.json();
    console.log('Uploaded:', result.speech_id);
    
    // Poll for transcription
    pollTranscript(result.speech_id);
  };
  
  return (
    <div>
      <AudioRecorder onRecordingComplete={handleRecordingComplete} />
      <SpeechHistory userId={userId} />
    </div>
  );
}
```

### Backend Integration
```python
from backend.speech_service import speech_service
from backend.tts_service import tts_service

# Upload user audio
result = await speech_service.upload_audio(
    user="alice",
    audio_data=audio_bytes,
    audio_format="webm"
)

# Get transcript
speech_msg = await speech_service.get_speech_message(result["speech_id"])
transcript = speech_msg["transcript"]

# Generate Grace's response
from backend.grace import grace_engine
response = await grace_engine.respond(transcript, user="alice")

# Convert to speech
tts_result = await tts_service.generate_speech(
    user="grace_system",
    text=response,
    reply_to_speech_id=result["speech_id"]
)
```

## Performance Considerations

- **Transcription**: ~2-5 seconds for 10-second audio (Whisper base model)
- **TTS Generation**: ~1-3 seconds for 100 characters (Coqui)
- **Audio Storage**: ~1MB per minute of audio (WebM Opus)
- **Concurrent Processing**: Background tasks don't block API responses

## Troubleshooting

### Whisper Not Transcribing
- Check if `openai-whisper` is installed
- Verify ffmpeg is in PATH
- System falls back to mock transcription for testing

### TTS Silent or Failing
- Check TTS engine installation
- Verify audio output device
- System falls back through: Coqui → pyttsx3 → mock

### Audio Recording Permission Denied
- Browser requires HTTPS for getUserMedia (except localhost)
- Check browser microphone permissions
- Ensure no other app is using microphone

### WebSocket Connection Drops
- Check firewall settings
- Verify WebSocket support in reverse proxy
- Implement reconnection logic in client

## Roadmap

- [ ] Real-time streaming transcription (WebSocket audio chunks)
- [ ] Speaker identification and diarization
- [ ] Multi-language support with auto-detection
- [ ] Voice cloning for personalized Grace voice
- [ ] Audio quality enhancement (noise reduction)
- [ ] Emotion detection in speech
- [ ] Voice authentication
- [ ] Offline mode with local Whisper

## License

Part of the Grace AI Governance System
