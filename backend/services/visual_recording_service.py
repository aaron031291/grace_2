"""
Visual Recording Service - Screen & Video Capture

Extends recording service with:
- Screen recording with OCR text extraction
- Video capture with frame extraction
- Visual embeddings (future)
- Timestamped visual search

Governance:
- Same consent flow as voice notes
- Additional consent for visual data
- PII detection in screenshots
"""

from pathlib import Path
from typing import Dict, Any, List

from backend.services.recording_service import recording_service, RecordingType
from backend.services.embedding_service import embedding_service
from backend.logging_utils import log_event


class VisualRecordingService:
    """
    Service for screen and video recordings
    
    Features:
    - Frame extraction at intervals
    - OCR text extraction from frames
    - Embedding of extracted text
    - Visual search capabilities
    """
    
    def __init__(self):
        self.ocr_available = False
        self.video_processing_available = False
        
        # Try to import OCR library
        try:
            import pytesseract
            self.ocr_available = True
            print("[VISUAL RECORDING] OCR available (Tesseract)")
        except ImportError:
            print("[VISUAL RECORDING] OCR not available - install pytesseract")
        
        # Try to import video processing
        try:
            import cv2
            self.video_processing_available = True
            print("[VISUAL RECORDING] Video processing available (OpenCV)")
        except ImportError:
            print("[VISUAL RECORDING] Video processing not available - install opencv-python")
    
    async def start_screen_recording(
        self,
        title: str,
        user_id: str,
        purpose: str = "learning"
    ) -> str:
        """
        Start screen recording session
        
        Args:
            title: Recording title
            user_id: User recording
            purpose: Purpose
            
        Returns:
            session_id
        """
        session_id = await recording_service.start_recording(
            session_type=RecordingType.SCREEN_SHARE,
            title=title,
            purpose=purpose,
            created_by=user_id,
            participants=[{"user_id": user_id, "name": user_id, "role": "host"}],
            consent_given=False
        )
        
        log_event(
            action="screen_recording.started",
            actor=user_id,
            resource=session_id,
            outcome="created",
            payload={"title": title}
        )
        
        return session_id
    
    async def extract_frames(
        self,
        session_id: str,
        video_path: str,
        frame_interval_seconds: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Extract frames from video at intervals
        
        Args:
            session_id: Recording session
            video_path: Path to video file
            frame_interval_seconds: Extract frame every N seconds
            
        Returns:
            List of extracted frames with timestamps
        """
        if not self.video_processing_available:
            return [{"error": "Video processing not available"}]
        
        try:
            import cv2
            
            video = cv2.VideoCapture(video_path)
            fps = video.get(cv2.CAP_PROP_FPS)
            frame_interval = int(fps * frame_interval_seconds)
            
            frames = []
            frame_count = 0
            
            while video.isOpened():
                ret, frame = video.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    # Save frame
                    timestamp_seconds = frame_count / fps
                    frame_path = f"storage/recordings/{session_id}/frame_{int(timestamp_seconds)}.jpg"
                    
                    Path(frame_path).parent.mkdir(parents=True, exist_ok=True)
                    cv2.imwrite(frame_path, frame)
                    
                    # Extract text if OCR available
                    extracted_text = ""
                    if self.ocr_available:
                        extracted_text = await self._ocr_frame(frame_path)
                    
                    frames.append({
                        "frame_number": frame_count,
                        "timestamp_seconds": timestamp_seconds,
                        "frame_path": frame_path,
                        "extracted_text": extracted_text,
                        "text_length": len(extracted_text)
                    })
                
                frame_count += 1
            
            video.release()
            
            print(f"[VISUAL RECORDING] Extracted {len(frames)} frames from {session_id}")
            
            return frames
            
        except Exception as e:
            print(f"[VISUAL RECORDING] Frame extraction error: {e}")
            return [{"error": str(e)}]
    
    async def _ocr_frame(self, frame_path: str) -> str:
        """
        Extract text from image using OCR
        
        Args:
            frame_path: Path to image file
            
        Returns:
            Extracted text
        """
        if not self.ocr_available:
            return ""
        
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(frame_path)
            text = pytesseract.image_to_string(image)
            
            return text.strip()
            
        except Exception as e:
            print(f"[VISUAL RECORDING] OCR error: {e}")
            return ""
    
    async def process_screen_recording(
        self,
        session_id: str,
        video_path: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Complete processing for screen recording
        
        Flow:
        1. Extract frames
        2. OCR each frame
        3. Combine text from all frames
        4. Embed text
        5. Ingest to knowledge base
        
        Args:
            session_id: Recording session
            video_path: Path to video file
            user_id: User
            
        Returns:
            Processing results
        """
        # Extract frames
        frames = await self.extract_frames(session_id, video_path)
        
        if not frames or "error" in frames[0]:
            return {"error": "Frame extraction failed"}
        
        # Combine text from all frames
        all_text = []
        for frame in frames:
            if frame.get("extracted_text"):
                all_text.append(f"[{frame['timestamp_seconds']:.1f}s] {frame['extracted_text']}")
        
        combined_text = "\n".join(all_text)
        
        # Embed text chunks
        if combined_text:
            embed_result = await embedding_service.embed_chunks(
                text=combined_text,
                chunk_size=500,
                chunk_overlap=100,
                source_type="recording",
                source_id=session_id,
                parent_id=session_id,
                metadata={
                    "recording_session_id": session_id,
                    "session_type": "screen_share",
                    "frames_extracted": len(frames),
                    "ocr_enabled": True
                }
            )
            
            # Auto-index (handled by vector_integration)
            
            return {
                "session_id": session_id,
                "frames_extracted": len(frames),
                "text_extracted_length": len(combined_text),
                "embeddings_created": len(embed_result.get("chunks", [])),
                "searchable": True
            }
        
        return {
            "session_id": session_id,
            "frames_extracted": len(frames),
            "text_extracted_length": 0,
            "warning": "No text extracted from frames"
        }
    
    async def search_visual_content(
        self,
        query: str,
        user_id: str,
        session_type: str = "screen_share"
    ) -> Dict[str, Any]:
        """
        Search screen/video recordings
        
        Args:
            query: Search query
            user_id: User
            session_type: Filter by type
            
        Returns:
            Matching frames/segments
        """
        from backend.services.rag_service import rag_service
        
        results = await rag_service.retrieve(
            query=query,
            source_types=["recording"],
            filters={"session_type": session_type},
            requested_by=user_id
        )
        
        return results


# Global instance
visual_recording = VisualRecordingService()
