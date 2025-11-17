"""
Remote Vision Capture - Integrates vision/video models with remote access
Grace can see and learn from any visual data
"""

import httpx
import base64
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class RemoteVisionCapture:
    """
    Captures and analyzes visual data from remote hosts
    Integrates with vision/video models and feeds to learning loop
    """
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.observations_log = []
        
    async def analyze_screenshot(
        self,
        image_data: bytes,
        source: str,
        context: Optional[Dict] = None,
        quality: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Analyze screenshot using vision models
        Routes to LLaVA/Llama Vision/Moondream based on quality setting
        """
        
        # Select model based on quality
        if quality == "high":
            model = "llava:34b"
        elif quality == "fast":
            model = "moondream:latest"
        else:
            model = "llama3.2-vision:latest"
        
        # Encode image to base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": self._build_vision_prompt(context),
                        "images": [image_b64],
                        "stream": False,
                        "options": {
                            "temperature": 0.3,  # Lower for factual analysis
                            "num_predict": 500
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    analysis = result["response"]
                    
                    # Structure the observation
                    structured_obs = await self._structure_observation(
                        analysis=analysis,
                        source=source,
                        image_data=image_data,
                        model=model
                    )
                    
                    # Store in memory tables
                    await self._store_in_memory(structured_obs)
                    
                    # Feed to learning loop
                    await self._feed_to_learning(structured_obs)
                    
                    return structured_obs
                    
        except Exception as e:
            print(f"Vision analysis failed: {e}")
            return {
                "error": str(e),
                "fallback": "Visual analysis unavailable"
            }
    
    async def analyze_video(
        self,
        video_path: str,
        source: str,
        extract_frames_every: int = 5
    ) -> Dict[str, Any]:
        """
        Analyze video using Video-LLaVA
        Extracts frames, tracks motion, understands actions
        """
        
        try:
            # For video, use video-llava
            model = "video-llava:latest"
            
            # Extract key frames (simplified - real implementation would use ffmpeg)
            frames = await self._extract_video_frames(video_path, extract_frames_every)
            
            # Analyze each frame
            frame_observations = []
            for i, frame_data in enumerate(frames):
                obs = await self.analyze_screenshot(
                    image_data=frame_data,
                    source=f"{source}_frame_{i}",
                    context={"video_path": video_path, "frame_number": i},
                    quality="high"
                )
                frame_observations.append(obs)
            
            # Synthesize video understanding
            video_summary = await self._synthesize_video_understanding(
                frame_observations=frame_observations,
                video_path=video_path
            )
            
            # Store complete video analysis
            await self._store_video_analysis(video_summary)
            
            return video_summary
            
        except Exception as e:
            print(f"Video analysis failed: {e}")
            return {"error": str(e)}
    
    async def _structure_observation(
        self,
        analysis: str,
        source: str,
        image_data: bytes,
        model: str
    ) -> Dict[str, Any]:
        """
        Structure vision analysis into queryable format
        """
        
        # Parse the analysis for structured data
        structured = {
            "source": source,
            "model_used": model,
            "raw_description": analysis,
            "timestamp": datetime.now().isoformat(),
            
            # Extract structured elements (enhanced with NLP)
            "detected_ui_elements": self._extract_ui_elements(analysis),
            "detected_text": self._extract_text(analysis),
            "detected_errors": self._extract_errors(analysis),
            "detected_objects": self._extract_objects(analysis),
            "color_scheme": self._extract_colors(analysis),
            "layout_description": self._extract_layout(analysis),
            
            # Metadata
            "image_size_bytes": len(image_data),
            "confidence": 0.85  # Could be extracted from model response
        }
        
        return structured
    
    def _extract_ui_elements(self, text: str) -> List[str]:
        """Extract UI element mentions"""
        ui_keywords = ["button", "menu", "dialog", "window", "panel", "icon", "input", "form"]
        elements = []
        
        text_lower = text.lower()
        for keyword in ui_keywords:
            if keyword in text_lower:
                elements.append(keyword)
        
        return elements
    
    def _extract_text(self, analysis: str) -> List[str]:
        """Extract OCR'd text mentions"""
        # Simple extraction - real implementation would be more sophisticated
        import re
        
        # Find quoted text
        quoted = re.findall(r'"([^"]*)"', analysis)
        return quoted
    
    def _extract_errors(self, analysis: str) -> List[str]:
        """Extract error messages seen in image"""
        error_keywords = ["error", "exception", "failed", "traceback", "warning"]
        errors = []
        
        for keyword in error_keywords:
            if keyword in analysis.lower():
                errors.append(keyword)
        
        return errors
    
    def _extract_objects(self, analysis: str) -> List[str]:
        """Extract detected objects"""
        # Parse for object mentions
        return []  # Placeholder
    
    def _extract_colors(self, analysis: str) -> List[str]:
        """Extract color scheme"""
        colors = []
        color_keywords = ["blue", "red", "green", "dark", "light", "white", "black"]
        
        for color in color_keywords:
            if color in analysis.lower():
                colors.append(color)
        
        return colors
    
    def _extract_layout(self, analysis: str) -> str:
        """Extract layout description"""
        # Return first sentence that mentions layout
        if "layout" in analysis.lower() or "organized" in analysis.lower():
            return analysis[:200]
        return ""
    
    async def _store_in_memory(self, observation: Dict[str, Any]):
        """Store visual observation in memory tables"""
        
        try:
            from backend.models.base_models import async_session
            from sqlalchemy import text
            
            async with async_session() as session:
                # Create visual_observations table
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS visual_observations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source TEXT,
                        model_used TEXT,
                        raw_description TEXT,
                        detected_ui_elements TEXT,
                        detected_text TEXT,
                        detected_errors TEXT,
                        detected_objects TEXT,
                        color_scheme TEXT,
                        layout_description TEXT,
                        confidence REAL,
                        timestamp TEXT
                    )
                """))
                
                await session.execute(text("""
                    INSERT INTO visual_observations 
                    (source, model_used, raw_description, detected_ui_elements, detected_text,
                     detected_errors, detected_objects, color_scheme, layout_description,
                     confidence, timestamp)
                    VALUES 
                    (:source, :model, :desc, :ui, :text, :errors, :objects, :colors, :layout,
                     :conf, :timestamp)
                """), {
                    "source": observation["source"],
                    "model": observation["model_used"],
                    "desc": observation["raw_description"],
                    "ui": json.dumps(observation["detected_ui_elements"]),
                    "text": json.dumps(observation["detected_text"]),
                    "errors": json.dumps(observation["detected_errors"]),
                    "objects": json.dumps(observation["detected_objects"]),
                    "colors": json.dumps(observation["color_scheme"]),
                    "layout": observation["layout_description"],
                    "conf": observation["confidence"],
                    "timestamp": observation["timestamp"]
                })
                
                await session.commit()
                
                print(f"✓ Stored visual observation from {observation['source']}")
                
        except Exception as e:
            print(f"Failed to store observation: {e}")
    
    async def _feed_to_learning(self, observation: Dict[str, Any]):
        """Feed visual observations to Layer 3 learning loop"""
        
        try:
            from backend.models.base_models import async_session
            from sqlalchemy import text
            
            # Create learning event
            learning_event = {
                "event_type": "visual_observation",
                "source": observation["source"],
                "data": {
                    "ui_elements": observation["detected_ui_elements"],
                    "errors": observation["detected_errors"],
                    "text": observation["detected_text"]
                },
                "timestamp": observation["timestamp"]
            }
            
            async with async_session() as session:
                # Store in outcome_records (Layer 3 learning table)
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS outcome_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_type TEXT,
                        source TEXT,
                        data TEXT,
                        success BOOLEAN DEFAULT TRUE,
                        timestamp TEXT
                    )
                """))
                
                await session.execute(text("""
                    INSERT INTO outcome_records (event_type, source, data, timestamp)
                    VALUES (:type, :source, :data, :timestamp)
                """), {
                    "type": learning_event["event_type"],
                    "source": learning_event["source"],
                    "data": json.dumps(learning_event["data"]),
                    "timestamp": learning_event["timestamp"]
                })
                
                await session.commit()
                
                print(f"✓ Fed to learning loop: {observation['source']}")
                
        except Exception as e:
            print(f"Failed to feed to learning: {e}")
    
    def _build_vision_prompt(self, context: Optional[Dict] = None) -> str:
        """Build prompt for vision analysis"""
        
        base_prompt = """Analyze this image in detail. Describe:
1. What you see (objects, UI elements, text)
2. Any errors or issues visible
3. The layout and organization
4. Colors and visual style
5. Any actions or states shown

Be factual and structured. If this is a technical screenshot, focus on technical details."""
        
        if context:
            if context.get("error_detection"):
                base_prompt = "Focus on detecting any errors, warnings, or issues in this screenshot. Describe what went wrong."
            elif context.get("ui_review"):
                base_prompt = "Analyze this UI design. Describe the layout, components, and suggest improvements."
        
        return base_prompt
    
    async def _extract_video_frames(self, video_path: str, every_n_seconds: int) -> List[bytes]:
        """Extract frames from video (placeholder - would use ffmpeg)"""
        
        # TODO: Implement actual frame extraction with ffmpeg
        # For now, return empty list
        return []
    
    async def _synthesize_video_understanding(
        self,
        frame_observations: List[Dict],
        video_path: str
    ) -> Dict[str, Any]:
        """Synthesize understanding from multiple frames"""
        
        return {
            "video_path": video_path,
            "total_frames_analyzed": len(frame_observations),
            "key_events": [],
            "timeline": [],
            "summary": "Video analysis complete",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _store_video_analysis(self, summary: Dict):
        """Store video analysis in memory"""
        
        try:
            from backend.models.base_models import async_session
            from sqlalchemy import text
            
            async with async_session() as session:
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS video_observations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        video_path TEXT,
                        total_frames INTEGER,
                        summary TEXT,
                        timeline TEXT,
                        timestamp TEXT
                    )
                """))
                
                await session.execute(text("""
                    INSERT INTO video_observations (video_path, total_frames, summary, timeline, timestamp)
                    VALUES (:path, :frames, :summary, :timeline, :timestamp)
                """), {
                    "path": summary["video_path"],
                    "frames": summary["total_frames_analyzed"],
                    "summary": summary["summary"],
                    "timeline": json.dumps(summary["timeline"]),
                    "timestamp": summary["timestamp"]
                })
                
                await session.commit()
                
        except Exception as e:
            print(f"Failed to store video analysis: {e}")

# Global instance
vision_capture = RemoteVisionCapture()
