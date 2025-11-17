"""
Visual Media Governance Rules

Extended governance for screen/video recordings:
- Higher risk level than voice notes
- PII detection in screenshots
- Face detection consent
- Screen content classification
- Auto-redaction capabilities
"""

from typing import Dict, Any, List

from backend.governance_system.governance import governance_engine


class VisualMediaGovernance:
    """
    Governance rules specific to visual media
    
    Risk Levels:
    - Voice Note: Low
    - Screen Recording: Medium-High (may capture sensitive data)
    - Video Call: High (captures faces, PII)
    - Screen + Video: Critical (full context capture)
    """
    
    def __init__(self):
        # Risk classifications
        self.risk_matrix = {
            "voice_note": "low",
            "screen_share": "medium",
            "video_call": "high",
            "screen_video_combined": "critical"
        }
        
        # Required consent types by media
        self.required_consents = {
            "voice_note": ["recording", "transcription", "learning"],
            "screen_share": ["recording", "transcription", "learning", "visual_data"],
            "video_call": ["recording", "transcription", "learning", "visual_data", "biometric"],
            "meeting_recording": ["recording", "transcription", "learning", "visual_data", "multi_party"]
        }
        
        # PII detection rules
        self.pii_patterns = {
            "screen": ["password", "credit_card", "ssn", "api_key", "private_key"],
            "video": ["face", "license_plate", "badge_number"]
        }
    
    async def check_visual_recording(
        self,
        session_type: str,
        participants: List[Dict],
        has_video: bool,
        has_audio: bool,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Check governance approval for visual recording
        
        Args:
            session_type: Type of recording
            participants: List of participants
            has_video: Contains video
            has_audio: Contains audio
            user_id: User requesting
            
        Returns:
            Governance decision
        """
        # Determine risk level
        risk_level = self.risk_matrix.get(session_type, "medium")
        
        # Upgrade risk if video included
        if has_video and risk_level == "medium":
            risk_level = "high"
        
        # Multi-party increases risk
        if len(participants) > 1 and risk_level != "critical":
            risk_level = "high"
        
        # Check with governance engine
        check_result = await governance_engine.check(
            actor=user_id,
            action=f"recording.{session_type}",
            resource=f"visual_recording_{session_type}",
            payload={
                "session_type": session_type,
                "participant_count": len(participants),
                "has_video": has_video,
                "has_audio": has_audio,
                "risk_level": risk_level
            }
        )
        
        # Add visual-specific requirements
        check_result["required_consents"] = self.required_consents.get(
            session_type,
            ["recording", "transcription", "learning"]
        )
        check_result["risk_level"] = risk_level
        check_result["pii_detection_required"] = (risk_level in ["high", "critical"])
        
        return check_result
    
    async def detect_pii_in_frame(
        self,
        frame_text: str,
        frame_path: str
    ) -> Dict[str, Any]:
        """
        Detect PII in screenshot frame
        
        Args:
            frame_text: OCR extracted text
            frame_path: Path to screenshot
            
        Returns:
            PII detection results
        """
        detected_pii = []
        
        # Check for text-based PII
        text_lower = frame_text.lower()
        for pii_type in self.pii_patterns["screen"]:
            if pii_type in text_lower:
                detected_pii.append({
                    "type": pii_type,
                    "location": "text",
                    "confidence": 0.8
                })
        
        # Check for visual PII (faces, etc.) - would need ML model
        # Placeholder for future face detection
        
        return {
            "has_pii": len(detected_pii) > 0,
            "detected_types": [p["type"] for p in detected_pii],
            "details": detected_pii,
            "redaction_required": len(detected_pii) > 0
        }
    
    async def get_governance_requirements(
        self,
        session_type: str
    ) -> Dict[str, Any]:
        """
        Get governance requirements for session type
        
        Args:
            session_type: Type of recording
            
        Returns:
            Requirements including consent types and risk level
        """
        return {
            "session_type": session_type,
            "risk_level": self.risk_matrix.get(session_type, "medium"),
            "required_consents": self.required_consents.get(session_type, []),
            "pii_detection": True if session_type != "voice_note" else False,
            "governance_approval_required": self.risk_matrix.get(session_type) in ["high", "critical"],
            "retention_max_days": 90 if session_type == "voice_note" else 30
        }


# Global instance
visual_media_governance = VisualMediaGovernance()
