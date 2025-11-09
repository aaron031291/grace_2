# Speech Pipeline Quick Start Guide

Get Grace's voice interaction working in 5 minutes!

## Step 1: Install Required Dependencies

```bash
cd grace_rebuild
pip install aiofiles
```

**That's it!** The system works with mock transcription/TTS for testing.

## Step 2: Start the Backend

```bash
python -m uvicorn backend.main:app --reload
```

You should see:
```
✓ Database initialized
✓ Grace API server starting...
  Visit: http://localhost:8000/health
  Docs: http://localhost:8000/docs
```

## Step 3: Test the API

Open another terminal:

```bash
cd grace_rebuild
python tests/test_speech_pipeline.py
```

Expected output:
```
Running Speech Pipeline Tests...
============================================================
✓ Audio upload test passed: speech_id=1
✓ Transcription test passed: transcript='[Mock transcription...]'
✓ Speech list test passed: found 1 messages
✓ Review test passed: speech_id=2, status=approved
✓ TTS generation test passed: tts_id=1, status=completed
✓ Security scan test completed
✓ Delete test passed: speech_id=3 deleted successfully
✓ Full conversation flow test passed!
============================================================
All tests completed!
```

## Step 4: Try the API Manually

### Upload Audio (Mock)

```bash
# Create a test audio file
echo "Mock audio data" > test_audio.txt

# Upload it
curl -X POST http://localhost:8000/api/audio/upload \
  -F "file=@test_audio.txt" \
  -H "Content-Type: multipart/form-data"
```

Response:
```json
{
  "speech_id": 1,
  "audio_path": "./audio_messages/test_user_xxxx.webm",
  "status": "uploaded",
  "verification_id": "env_1",
  "queued_for_transcription": true
}
```

### Get Transcript (after 2 seconds)

```bash
curl http://localhost:8000/api/audio/1
```

Response:
```json
{
  "id": 1,
  "user": "anonymous",
  "transcript": "[Mock transcription - install openai-whisper]",
  "confidence": 0.5,
  "language": "en",
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Generate TTS

```bash
curl -X POST http://localhost:8000/api/audio/tts/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is Grace speaking", "speed": 1.0}'
```

Response:
```json
{
  "tts_id": 1,
  "audio_path": "./audio_messages/tts/tts_anonymous_xxxx.mp3",
  "status": "pending",
  "queued_for_generation": true
}
```

## Step 5: Frontend Integration

### Import Components

```typescript
import { ChatWithSpeech } from './components/ChatWithSpeech';

function App() {
  return <ChatWithSpeech />;
}
```

### Or Use Individual Components

```typescript
import { 
  AudioRecorder, 
  AudioPlayer, 
  SpeechHistory 
} from './components/SpeechInterface';

function MyChat() {
  const handleRecording = async (audioBlob: Blob) => {
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.webm');
    
    const response = await fetch('/api/audio/upload', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    console.log('Speech ID:', data.speech_id);
  };
  
  return (
    <div>
      <AudioRecorder onRecordingComplete={handleRecording} />
      <SpeechHistory userId="test_user" />
    </div>
  );
}
```

## Step 6: Install Real Speech Engines (Optional)

For production-quality speech:

### Whisper (Speech-to-Text)

```bash
# Install Whisper
pip install openai-whisper

# Windows: Install ffmpeg
# Download from https://ffmpeg.org/download.html
# Add to PATH

# Linux:
sudo apt install ffmpeg

# Test it
python -c "import whisper; print('Whisper ready!')"
```

### Coqui TTS (Text-to-Speech)

```bash
# Install Coqui TTS
pip install TTS

# Test it
tts --text "Hello Grace" --out_path test.wav

# If successful, you'll hear Grace's voice!
```

### Alternative: pyttsx3 (Simpler TTS)

```bash
# Install pyttsx3
pip install pyttsx3

# Test it
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Hello'); engine.runAndWait()"
```

## Verify Everything Works

1. **Backend is running:**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status": "ok", "message": "Grace API is running"}
   ```

2. **Speech routes are registered:**
   ```bash
   curl http://localhost:8000/docs
   # Visit in browser, look for /api/audio/* endpoints
   ```

3. **Storage directory exists:**
   ```bash
   ls audio_messages/
   # Should show uploaded files
   ```

4. **Tests pass:**
   ```bash
   python tests/test_speech_pipeline.py
   # All tests should pass
   ```

## Common Issues

### "Module 'aiofiles' not found"
```bash
pip install aiofiles
```

### "Audio file not found"
Check that `audio_messages/` directory exists and is writable.

### "Transcription stuck at 'transcribing'"
This is normal with mock transcription. Install Whisper for real transcription:
```bash
pip install openai-whisper
```

### "TTS generation failed"
Install a TTS engine:
```bash
pip install TTS  # or pyttsx3
```

### Frontend microphone not working
- Use HTTPS or localhost (required for `getUserMedia()`)
- Check browser permissions
- Make sure no other app is using the microphone

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/audio/upload` | POST | Upload audio file |
| `/api/audio/{id}` | GET | Get speech message |
| `/api/audio/{id}/file` | GET | Stream audio file |
| `/api/audio/list` | GET | List messages |
| `/api/audio/{id}/review` | POST | Review transcript |
| `/api/audio/{id}` | DELETE | Delete message |
| `/api/audio/tts/generate` | POST | Generate TTS |
| `/api/audio/tts/{id}/file` | GET | Get TTS file |
| `/api/audio/ws` | WebSocket | Real-time updates |

## Next Steps

1. **Read full documentation:** [SPEECH_PIPELINE.md](./SPEECH_PIPELINE.md)
2. **Explore API:** http://localhost:8000/docs
3. **Check implementation:** [SPEECH_IMPLEMENTATION_SUMMARY.md](./SPEECH_IMPLEMENTATION_SUMMARY.md)
4. **Customize:** Adjust voice models, speeds, security rules

## Example Full Conversation

```bash
# 1. User speaks
curl -X POST http://localhost:8000/api/audio/upload \
  -F "file=@user_voice.webm"
# Returns: speech_id: 1

# 2. Wait 2 seconds for transcription

# 3. Get transcript
curl http://localhost:8000/api/audio/1
# Returns: transcript: "How's the weather?"

# 4. Grace responds (mock)
# (In production, this would call your LLM)

# 5. Generate TTS for Grace's response
curl -X POST http://localhost:8000/api/audio/tts/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "The weather is sunny today!", "reply_to_speech_id": 1}'
# Returns: tts_id: 1

# 6. Play Grace's voice
curl http://localhost:8000/api/audio/tts/1/file > grace_response.mp3
# (Play the file)
```

## Success Indicators

✅ Backend starts without errors
✅ Tests pass (at least with mock engines)
✅ Audio files are created in `audio_messages/`
✅ API docs show speech endpoints
✅ Frontend components render
✅ Microphone permission granted
✅ Audio recording works
✅ Transcripts appear (mock or real)

---

**You're ready!** The speech pipeline is fully functional with mock engines for testing. Install Whisper and TTS for production-quality voice interaction.

For questions, see [SPEECH_PIPELINE.md](./SPEECH_PIPELINE.md) troubleshooting section.
