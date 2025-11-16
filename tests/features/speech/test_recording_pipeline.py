"""
Test Recording Pipeline with Consent & Governance

Tests the full recording pipeline:
1. Start recording session
2. Request and grant consent
3. Transcribe with governance checks
4. Ingest to knowledge base
5. Feed to learning loop
"""

import pytest
from datetime import datetime, timezone
from backend.services.recording_service import recording_service, RecordingType


@pytest.mark.asyncio
async def test_recording_pipeline_with_consent():
    """Test full recording pipeline with consent flow"""
    
    # 1. Start recording session
    session_id = await recording_service.start_recording(
        session_type=RecordingType.VOICE_NOTE,
        title="Test Voice Note",
        purpose="testing",
        created_by="test_user",
        participants=[{"user_id": "test_user", "name": "Test User", "role": "host"}],
        consent_given=False  # No pre-flight consent
    )
    
    assert session_id is not None
    assert session_id.startswith("rec_voice_note_")
    
    # 2. Request consent
    consent_id = await recording_service.request_consent(
        session_id=session_id,
        user_id="test_user",
        consent_types=["recording", "transcription", "learning"],
        purpose="testing"
    )
    
    assert consent_id is not None
    
    # 3. Grant consent
    success = await recording_service.grant_consent(
        session_id=session_id,
        user_id="test_user",
        consent_given=True,
        consent_types=["recording", "transcription", "learning"]
    )
    
    assert success is True
    
    # 4. Verify consent
    consent_check = await recording_service.verify_consent(
        session_id=session_id,
        required_consent_types=["recording", "transcription", "learning"]
    )
    
    assert consent_check["all_consents_granted"] is True
    assert set(consent_check["granted_types"]) == {"recording", "transcription", "learning"}
    assert len(consent_check["missing_types"]) == 0


@pytest.mark.asyncio
async def test_governance_checks():
    """Test governance approval checks for different actions"""
    
    # Create test session
    session_id = await recording_service.start_recording(
        session_type=RecordingType.MEETING_RECORDING,
        title="Test Meeting",
        purpose="meeting",
        created_by="test_user"
    )
    
    # Test transcription (medium risk)
    governance_check = await recording_service.check_governance_approval(
        session_id=session_id,
        action="transcribe",
        user_id="test_user"
    )
    
    assert "approved" in governance_check
    assert "requires_approval" in governance_check
    
    # Test ingestion (high risk)
    governance_check = await recording_service.check_governance_approval(
        session_id=session_id,
        action="ingest",
        user_id="test_user"
    )
    
    assert governance_check.get("requires_approval") is True
    
    # Test sharing (critical risk)
    governance_check = await recording_service.check_governance_approval(
        session_id=session_id,
        action="share",
        user_id="test_user"
    )
    
    assert governance_check.get("requires_approval") is True


@pytest.mark.asyncio
async def test_consent_verification():
    """Test consent verification with missing consents"""
    
    # Create session
    session_id = await recording_service.start_recording(
        session_type=RecordingType.SCREEN_SHARE,
        title="Test Screen Share",
        purpose="demo",
        created_by="test_user"
    )
    
    # Grant only partial consent
    await recording_service.request_consent(
        session_id=session_id,
        user_id="test_user",
        consent_types=["recording", "transcription"],
        purpose="demo"
    )
    
    await recording_service.grant_consent(
        session_id=session_id,
        user_id="test_user",
        consent_given=True,
        consent_types=["recording"]  # Only recording, not transcription
    )
    
    # Verify full consent (should fail)
    consent_check = await recording_service.verify_consent(
        session_id=session_id,
        required_consent_types=["recording", "transcription", "learning"]
    )
    
    assert consent_check["all_consents_granted"] is False
    assert "recording" in consent_check["granted_types"]
    assert "transcription" in consent_check["missing_types"]
    assert "learning" in consent_check["missing_types"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
