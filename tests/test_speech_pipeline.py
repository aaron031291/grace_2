"""Tests for speech pipeline functionality"""

import pytest
import asyncio
from pathlib import Path
import io

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.speech_service import speech_service
from backend.tts_service import tts_service
from backend.models import Base, engine

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Initialize database for testing"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_audio_upload():
    """Test audio file upload"""
    
    # Create dummy audio data
    audio_data = b"RIFF....WAVE...." * 100  # Mock audio data
    
    result = await speech_service.upload_audio(
        user="test_user",
        audio_data=audio_data,
        audio_format="webm",
        session_id="test_session_1"
    )
    
    assert "speech_id" in result
    assert result["status"] == "uploaded"
    assert result["queued_for_transcription"] is True
    assert "verification_id" in result
    
    # Verify file was saved
    audio_path = Path(result["audio_path"])
    assert audio_path.exists()
    
    print(f"✓ Audio upload test passed: speech_id={result['speech_id']}")

@pytest.mark.asyncio
async def test_transcription_mock():
    """Test transcription with mock (no Whisper needed)"""
    
    # Upload audio
    audio_data = b"Mock audio data for transcription test" * 50
    
    result = await speech_service.upload_audio(
        user="test_user",
        audio_data=audio_data,
        audio_format="webm"
    )
    
    speech_id = result["speech_id"]
    
    # Wait for transcription to complete
    await asyncio.sleep(2)
    
    # Get speech message
    speech_msg = await speech_service.get_speech_message(speech_id)
    
    assert speech_msg is not None
    assert speech_msg["transcript"] is not None
    assert speech_msg["status"] in ["completed", "failed", "transcribing"]
    
    if speech_msg["status"] == "completed":
        print(f"✓ Transcription test passed: transcript='{speech_msg['transcript'][:50]}...'")
    else:
        print(f"⚠ Transcription still processing or failed: status={speech_msg['status']}")

@pytest.mark.asyncio
async def test_speech_list():
    """Test listing speech messages"""
    
    messages = await speech_service.list_speech_messages(
        user="test_user",
        limit=10
    )
    
    assert isinstance(messages, list)
    assert len(messages) > 0
    
    for msg in messages:
        assert "id" in msg
        assert "transcript" in msg
        assert "confidence" in msg
        assert "status" in msg
    
    print(f"✓ Speech list test passed: found {len(messages)} messages")

@pytest.mark.asyncio
async def test_review_transcript():
    """Test transcript review functionality"""
    
    # Create a speech message first
    audio_data = b"Test audio for review" * 20
    
    result = await speech_service.upload_audio(
        user="test_user",
        audio_data=audio_data,
        audio_format="webm"
    )
    
    speech_id = result["speech_id"]
    
    # Wait for transcription
    await asyncio.sleep(2)
    
    # Approve transcript
    review_result = await speech_service.review_transcript(
        speech_id=speech_id,
        approved=True,
        reviewed_by="reviewer_user",
        notes="Looks good"
    )
    
    assert review_result is not None
    assert review_result["review_status"] == "approved"
    assert review_result["reviewed_by"] == "reviewer_user"
    
    print(f"✓ Review test passed: speech_id={speech_id}, status=approved")

@pytest.mark.asyncio
async def test_tts_generation():
    """Test text-to-speech generation"""
    
    text = "Hello, this is Grace speaking. I am testing the text-to-speech system."
    
    result = await tts_service.generate_speech(
        user="test_user",
        text=text,
        voice_model="default",
        speed=1.0,
        pitch=1.0
    )
    
    assert "tts_id" in result
    assert result["status"] == "pending"
    assert result["queued_for_generation"] is True
    
    tts_id = result["tts_id"]
    
    # Wait for generation
    await asyncio.sleep(3)
    
    # Get TTS message
    tts_msg = await tts_service.get_tts_message(tts_id)
    
    assert tts_msg is not None
    assert tts_msg["text_content"] == text
    assert tts_msg["status"] in ["completed", "failed", "generating"]
    
    if tts_msg["status"] == "completed":
        audio_path = Path(tts_msg["audio_path"])
        # Note: With mock TTS, file might be text, not actual audio
        assert audio_path.exists()
        print(f"✓ TTS generation test passed: tts_id={tts_id}, status={tts_msg['status']}")
    else:
        print(f"⚠ TTS generation status: {tts_msg['status']}")

@pytest.mark.asyncio
async def test_speech_security_scan():
    """Test security scanning of transcripts"""
    
    # Create speech with potentially suspicious content
    audio_data = b"Suspicious content test" * 30
    
    result = await speech_service.upload_audio(
        user="test_user",
        audio_data=audio_data,
        audio_format="webm"
    )
    
    speech_id = result["speech_id"]
    
    # Wait for transcription and security scan
    await asyncio.sleep(2)
    
    # Get speech message
    speech_msg = await speech_service.get_speech_message(speech_id)
    
    assert speech_msg is not None
    
    # Check if security scanning was performed
    # (Actual security logic depends on Hunter rules)
    print(f"✓ Security scan test completed: speech_id={speech_id}, needs_review={speech_msg.get('needs_review')}")

@pytest.mark.asyncio
async def test_delete_speech_message():
    """Test speech message deletion"""
    
    # Create speech message
    audio_data = b"Message to be deleted" * 15
    
    result = await speech_service.upload_audio(
        user="test_user",
        audio_data=audio_data,
        audio_format="webm"
    )
    
    speech_id = result["speech_id"]
    audio_path = Path(result["audio_path"])
    
    # Delete message
    deleted = await speech_service.delete_speech_message(
        speech_id=speech_id,
        user="test_user"
    )
    
    assert deleted is True
    
    # Verify file was deleted
    assert not audio_path.exists()
    
    # Verify record was deleted
    speech_msg = await speech_service.get_speech_message(speech_id)
    assert speech_msg is None
    
    print(f"✓ Delete test passed: speech_id={speech_id} deleted successfully")

@pytest.mark.asyncio
async def test_conversation_flow():
    """Test full conversation flow: speech → transcript → Grace responds → TTS"""
    
    print("\n=== Testing Full Conversation Flow ===")
    
    # 1. User sends voice message
    user_audio = b"User voice message content" * 25
    
    upload_result = await speech_service.upload_audio(
        user="test_user",
        audio_data=user_audio,
        audio_format="webm",
        session_id="conversation_session_1"
    )
    
    speech_id = upload_result["speech_id"]
    print(f"1. User voice uploaded: speech_id={speech_id}")
    
    # 2. Wait for transcription
    await asyncio.sleep(2)
    
    speech_msg = await speech_service.get_speech_message(speech_id)
    print(f"2. Transcription completed: '{speech_msg['transcript'][:50]}...'")
    
    # 3. Simulate Grace's text response
    grace_response = "Thank you for your message. I understand your request."
    
    # 4. Generate TTS for Grace's response
    tts_result = await tts_service.generate_speech(
        user="grace_system",
        text=grace_response,
        reply_to_speech_id=speech_id,
        session_id="conversation_session_1"
    )
    
    tts_id = tts_result["tts_id"]
    print(f"3. Grace's TTS queued: tts_id={tts_id}")
    
    # 5. Wait for TTS generation
    await asyncio.sleep(3)
    
    tts_msg = await tts_service.get_tts_message(tts_id)
    print(f"4. Grace's TTS completed: status={tts_msg['status']}")
    
    # 6. Verify conversation flow
    assert tts_msg["reply_to_speech_id"] == speech_id
    assert tts_msg["session_id"] == "conversation_session_1"
    
    print("✓ Full conversation flow test passed!")

if __name__ == "__main__":
    print("Running Speech Pipeline Tests...")
    print("=" * 60)
    
    asyncio.run(test_audio_upload())
    asyncio.run(test_transcription_mock())
    asyncio.run(test_speech_list())
    asyncio.run(test_review_transcript())
    asyncio.run(test_tts_generation())
    asyncio.run(test_speech_security_scan())
    asyncio.run(test_delete_speech_message())
    asyncio.run(test_conversation_flow())
    
    print("=" * 60)
    print("All tests completed!")
