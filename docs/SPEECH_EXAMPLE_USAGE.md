# Speech Pipeline Usage Examples

Real-world examples showing how to use Grace's speech capabilities.

## Example 1: Simple Voice Message

### Backend
```python
from backend.speech_service import speech_service

# Upload audio
async def handle_voice_message(audio_bytes: bytes, user: str):
    result = await speech_service.upload_audio(
        user=user,
        audio_data=audio_bytes,
        audio_format="webm"
    )
    
    speech_id = result["speech_id"]
    print(f"Uploaded: {speech_id}")
    
    # Wait for transcription (in production, use websocket/polling)
    await asyncio.sleep(3)
    
    # Get transcript
    speech_msg = await speech_service.get_speech_message(speech_id)
    transcript = speech_msg["transcript"]
    
    return transcript
```

### Frontend
```typescript
import { AudioRecorder } from './components/SpeechInterface';

function VoiceMessage() {
  const handleRecording = async (audioBlob: Blob) => {
    const formData = new FormData();
    formData.append('file', audioBlob, 'voice.webm');
    
    const response = await fetch('/api/audio/upload', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    alert(`Uploaded! Speech ID: ${data.speech_id}`);
  };
  
  return <AudioRecorder onRecordingComplete={handleRecording} />;
}
```

---

## Example 2: Voice Chat with Grace

### Complete Flow
```python
async def voice_chat_with_grace(audio_bytes: bytes, user: str):
    # 1. Upload user's voice
    upload_result = await speech_service.upload_audio(
        user=user,
        audio_data=audio_bytes,
        audio_format="webm",
        session_id=f"chat_session_{user}"
    )
    
    speech_id = upload_result["speech_id"]
    
    # 2. Wait for transcription
    for i in range(10):
        await asyncio.sleep(1)
        speech_msg = await speech_service.get_speech_message(speech_id)
        if speech_msg["status"] == "completed":
            break
    
    transcript = speech_msg["transcript"]
    
    # 3. Get Grace's response (example - integrate with your LLM)
    grace_response = f"I heard you say: {transcript}. How can I help?"
    
    # 4. Generate TTS for Grace's response
    tts_result = await tts_service.generate_speech(
        user="grace_system",
        text=grace_response,
        voice_model="default",
        speed=1.0,
        reply_to_speech_id=speech_id,
        session_id=f"chat_session_{user}"
    )
    
    # 5. Wait for TTS
    await asyncio.sleep(3)
    
    tts_msg = await tts_service.get_tts_message(tts_result["tts_id"])
    
    return {
        "user_transcript": transcript,
        "grace_response": grace_response,
        "grace_audio_path": tts_msg["audio_path"]
    }
```

### Frontend Implementation
```typescript
function VoiceChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const handleVoiceMessage = async (audioBlob: Blob) => {
    setIsProcessing(true);
    
    // Upload audio
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.webm');
    
    const uploadRes = await fetch('/api/audio/upload', {
      method: 'POST',
      body: formData
    });
    
    const { speech_id } = await uploadRes.json();
    
    // Poll for transcript
    let transcript = '';
    for (let i = 0; i < 10; i++) {
      await new Promise(r => setTimeout(r, 1000));
      
      const speechRes = await fetch(`/api/audio/${speech_id}`);
      const speechData = await speechRes.json();
      
      if (speechData.status === 'completed') {
        transcript = speechData.transcript;
        break;
      }
    }
    
    // Add user message
    setMessages(prev => [...prev, {
      type: 'user',
      content: transcript,
      audioUrl: `/api/audio/${speech_id}/file`
    }]);
    
    // Get Grace's response (your API)
    const graceRes = await fetch('/api/chat/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: transcript })
    });
    
    const { response } = await graceRes.json();
    
    // Generate TTS
    const ttsRes = await fetch('/api/audio/tts/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: response,
        reply_to_speech_id: speech_id
      })
    });
    
    const { tts_id } = await ttsRes.json();
    
    // Add Grace message
    setMessages(prev => [...prev, {
      type: 'grace',
      content: response,
      audioUrl: `/api/audio/tts/${tts_id}/file`
    }]);
    
    setIsProcessing(false);
  };
  
  return (
    <div>
      {messages.map((msg, i) => (
        <div key={i} className={msg.type}>
          <p>{msg.content}</p>
          <AudioPlayer audioUrl={msg.audioUrl} />
        </div>
      ))}
      
      <AudioRecorder 
        onRecordingComplete={handleVoiceMessage}
        disabled={isProcessing}
      />
      
      {isProcessing && <p>Processing...</p>}
    </div>
  );
}
```

---

## Example 3: Voice Command System

```python
async def process_voice_command(audio_bytes: bytes, user: str):
    # Upload and transcribe
    result = await speech_service.upload_audio(
        user=user,
        audio_data=audio_bytes,
        audio_format="webm"
    )
    
    # Wait for transcript
    await asyncio.sleep(2)
    speech_msg = await speech_service.get_speech_message(result["speech_id"])
    transcript = speech_msg["transcript"].lower()
    
    # Parse commands
    if "show" in transcript and "dashboard" in transcript:
        return {"action": "navigate", "target": "/dashboard"}
    
    elif "run" in transcript and "tests" in transcript:
        return {"action": "execute", "command": "pytest"}
    
    elif "search" in transcript:
        query = transcript.replace("search", "").strip()
        return {"action": "search", "query": query}
    
    else:
        return {"action": "unknown", "transcript": transcript}
```

---

## Example 4: Multi-Language Support

```python
async def multilingual_conversation(audio_bytes: bytes, user: str):
    # Upload
    result = await speech_service.upload_audio(
        user=user,
        audio_data=audio_bytes,
        audio_format="webm"
    )
    
    # Wait and get transcript with language
    await asyncio.sleep(3)
    speech_msg = await speech_service.get_speech_message(result["speech_id"])
    
    transcript = speech_msg["transcript"]
    language = speech_msg["language"]  # e.g., "es", "fr", "de"
    
    # Respond in same language
    responses = {
        "es": "Hola, entiendo español",
        "fr": "Bonjour, je comprends le français",
        "de": "Hallo, ich verstehe Deutsch",
        "en": "Hello, I understand English"
    }
    
    response_text = responses.get(language, responses["en"])
    
    # Generate TTS (Whisper auto-detects language)
    tts_result = await tts_service.generate_speech(
        user="grace_system",
        text=response_text,
        reply_to_speech_id=result["speech_id"]
    )
    
    return {
        "detected_language": language,
        "transcript": transcript,
        "response": response_text,
        "tts_id": tts_result["tts_id"]
    }
```

---

## Example 5: Voice Notes with Review

```python
async def create_voice_note_with_review(audio_bytes: bytes, user: str):
    # Upload
    result = await speech_service.upload_audio(
        user=user,
        audio_data=audio_bytes,
        audio_format="webm"
    )
    
    speech_id = result["speech_id"]
    
    # Wait for transcription
    await asyncio.sleep(3)
    speech_msg = await speech_service.get_speech_message(speech_id)
    
    # Check if needs review
    if speech_msg.get("needs_review"):
        print(f"⚠ Voice note flagged for review: {speech_msg['review_status']}")
        
        # Admin can review
        review_result = await speech_service.review_transcript(
            speech_id=speech_id,
            approved=True,
            reviewed_by="admin",
            notes="Approved after review"
        )
        
        print(f"✓ Review completed: {review_result['review_status']}")
    
    # Save to memory/knowledge base
    from backend.memory_service import memory_service
    
    artifact_id = await memory_service.create_artifact(
        path=f"/voice_notes/{user}/{speech_id}",
        content=speech_msg["transcript"],
        actor=user,
        category="voice_note",
        metadata={
            "speech_id": speech_id,
            "confidence": speech_msg["confidence"],
            "language": speech_msg["language"]
        }
    )
    
    return {
        "speech_id": speech_id,
        "artifact_id": artifact_id,
        "transcript": speech_msg["transcript"]
    }
```

---

## Example 6: Real-time Transcription (WebSocket)

### Backend
```python
from fastapi import WebSocket

@router.websocket("/ws/audio/realtime")
async def realtime_transcription(websocket: WebSocket):
    await websocket.accept()
    
    audio_chunks = []
    
    try:
        while True:
            # Receive audio chunk
            data = await websocket.receive_json()
            
            if data["type"] == "audio_chunk":
                import base64
                chunk = base64.b64decode(data["data"])
                audio_chunks.append(chunk)
                
                # Send acknowledgment
                await websocket.send_json({
                    "type": "ack",
                    "chunk_count": len(audio_chunks)
                })
            
            elif data["type"] == "finalize":
                # Combine chunks
                full_audio = b''.join(audio_chunks)
                
                # Process
                result = await speech_service.upload_audio(
                    user=data.get("user", "anonymous"),
                    audio_data=full_audio,
                    audio_format="webm"
                )
                
                # Send result
                await websocket.send_json({
                    "type": "complete",
                    "speech_id": result["speech_id"]
                })
                
                audio_chunks = []
    
    except WebSocketDisconnect:
        print("Client disconnected")
```

### Frontend
```typescript
function RealtimeTranscription() {
  const [transcript, setTranscript] = useState('');
  const wsRef = useRef<WebSocket | null>(null);
  
  useEffect(() => {
    wsRef.current = new WebSocket('ws://localhost:8000/ws/audio/realtime');
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'complete') {
        // Poll for transcript
        pollTranscript(data.speech_id);
      }
    };
    
    return () => wsRef.current?.close();
  }, []);
  
  const streamAudio = (audioBlob: Blob) => {
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = btoa(String.fromCharCode(...new Uint8Array(reader.result as ArrayBuffer)));
      
      wsRef.current?.send(JSON.stringify({
        type: 'audio_chunk',
        data: base64
      }));
    };
    reader.readAsArrayBuffer(audioBlob);
  };
  
  return (
    <div>
      <AudioRecorder onRecordingComplete={streamAudio} />
      <p>Transcript: {transcript}</p>
    </div>
  );
}
```

---

## Example 7: Voice Authentication

```python
async def voice_authentication(audio_bytes: bytes, claimed_user: str):
    # Upload
    result = await speech_service.upload_audio(
        user=claimed_user,
        audio_data=audio_bytes,
        audio_format="webm"
    )
    
    # Wait for processing
    await asyncio.sleep(3)
    speech_msg = await speech_service.get_speech_message(result["speech_id"])
    
    # Check speaker ID (if configured)
    speaker_id = speech_msg.get("speaker_id")
    speaker_confidence = speech_msg.get("speaker_confidence", 0)
    
    if speaker_id == claimed_user and speaker_confidence > 0.8:
        return {
            "authenticated": True,
            "user": claimed_user,
            "confidence": speaker_confidence
        }
    else:
        return {
            "authenticated": False,
            "reason": "Speaker verification failed"
        }
```

---

## Example 8: Batch Processing

```python
async def process_multiple_recordings(audio_files: list[bytes], user: str):
    results = []
    
    # Upload all files
    for i, audio_data in enumerate(audio_files):
        result = await speech_service.upload_audio(
            user=user,
            audio_data=audio_data,
            audio_format="webm",
            session_id=f"batch_{user}_{int(time.time())}"
        )
        results.append(result)
    
    # Wait for all transcriptions
    await asyncio.sleep(5)
    
    # Collect transcripts
    transcripts = []
    for result in results:
        speech_msg = await speech_service.get_speech_message(result["speech_id"])
        transcripts.append({
            "speech_id": result["speech_id"],
            "transcript": speech_msg["transcript"],
            "confidence": speech_msg["confidence"]
        })
    
    return transcripts
```

---

## Example 9: Voice Search

```python
async def voice_search(audio_bytes: bytes, user: str):
    # Transcribe query
    result = await speech_service.upload_audio(
        user=user,
        audio_data=audio_bytes,
        audio_format="webm"
    )
    
    await asyncio.sleep(2)
    speech_msg = await speech_service.get_speech_message(result["speech_id"])
    
    query = speech_msg["transcript"]
    
    # Search in memory
    from backend.memory_service import memory_service
    
    search_results = await memory_service.search_artifacts(
        query=query,
        limit=5
    )
    
    # Format results
    if search_results:
        results_text = f"Found {len(search_results)} results for '{query}': "
        results_text += ", ".join([r["path"] for r in search_results])
    else:
        results_text = f"No results found for '{query}'"
    
    # Respond with TTS
    tts_result = await tts_service.generate_speech(
        user="grace_system",
        text=results_text,
        reply_to_speech_id=result["speech_id"]
    )
    
    return {
        "query": query,
        "results": search_results,
        "tts_id": tts_result["tts_id"]
    }
```

---

## Common Patterns

### Pattern 1: Upload → Wait → Get Transcript
```python
async def get_transcript(audio: bytes, user: str) -> str:
    result = await speech_service.upload_audio(user, audio, "webm")
    await asyncio.sleep(2)
    msg = await speech_service.get_speech_message(result["speech_id"])
    return msg["transcript"]
```

### Pattern 2: Transcript → Process → TTS
```python
async def respond_with_voice(transcript: str, user: str) -> int:
    response = process_text(transcript)
    tts = await tts_service.generate_speech(user, response)
    return tts["tts_id"]
```

### Pattern 3: Check Status Before Processing
```python
async def safe_get_transcript(speech_id: int) -> str:
    msg = await speech_service.get_speech_message(speech_id)
    
    if msg["status"] != "completed":
        raise ValueError(f"Not ready: {msg['status']}")
    
    if msg.get("needs_review"):
        raise ValueError("Needs manual review")
    
    return msg["transcript"]
```

---

## Error Handling

```python
async def robust_voice_processing(audio: bytes, user: str):
    try:
        # Upload
        result = await speech_service.upload_audio(user, audio, "webm")
        speech_id = result["speech_id"]
        
    except Exception as e:
        return {"error": "Upload failed", "details": str(e)}
    
    # Wait with timeout
    for i in range(10):
        await asyncio.sleep(1)
        msg = await speech_service.get_speech_message(speech_id)
        
        if msg["status"] == "completed":
            return {"success": True, "transcript": msg["transcript"]}
        
        if msg["status"] == "failed":
            return {"error": "Transcription failed", "message": msg.get("error_message")}
    
    return {"error": "Timeout", "speech_id": speech_id}
```

---

## Tips & Best Practices

1. **Always wait for status == "completed"** before reading transcript
2. **Use session_id** to group related messages
3. **Check needs_review** before trusting low-confidence transcripts
4. **Link TTS to original speech** with reply_to_speech_id
5. **Handle errors gracefully** - transcription can fail
6. **Set reasonable timeouts** (2-5 seconds for short audio)
7. **Use WebSocket** for real-time feedback
8. **Store important transcripts** in memory/knowledge base
9. **Enable security scanning** for user-generated content
10. **Test with mock engines** before installing Whisper/TTS

---

For more examples, see:
- [SPEECH_PIPELINE.md](./SPEECH_PIPELINE.md) - Full documentation
- [SPEECH_QUICKSTART.md](./SPEECH_QUICKSTART.md) - Getting started
- `tests/test_speech_pipeline.py` - Working test examples
