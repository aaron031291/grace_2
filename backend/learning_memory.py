"""
Learning Memory - Automatic Artifact Storage and Ingestion

This module provides helpers for storing artifacts directly into the Learning Memory
folder with automatic ingestion into the memory catalog and ML/DL pipelines.

Usage:
    from backend.learning_memory import store_artifact
    
    # Store mentor response
    await store_artifact(
        content={"mentor": "qwen", "response": "...", "confidence": 0.9},
        category="mentors",
        subcategory="mobile_app_task",
        metadata={"task_id": "mission-123", "model": "qwen:14b"}
    )
    
    # Store auto-fix code
    await store_artifact(
        content=code_diff,
        category="autofixes",
        subcategory="self_healing",
        filename="fix_auth_bug.py",
        metadata={"incident_id": "inc-456"}
    )
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Union
import json
import hashlib

from backend.clarity import get_event_bus, Event
from backend.core.unified_event_publisher import publish_event_obj
from backend.kernels.agents.file_ingestion_agent import FileIngestionAgent


class LearningMemoryHelper:
    """
    Helper for storing artifacts in Learning Memory with auto-ingestion
    """
    
    BASE_PATH = Path("storage/memory/learning")
    
    # Category mappings
    CATEGORIES = {
        "mentors": "Mentor roundtable responses",
        "autofixes": "Self-healing code fixes",
        "code_diffs": "Code change proposals",
        "summaries": "Generated summaries",
        "mission_briefs": "Mission specifications",
        "test_results": "Test execution results",
        "benchmarks": "Benchmark task results",
        "insights": "Generated insights",
        "transcripts": "Conversation transcripts",
        "prototypes": "Sandbox prototypes",
        "decisions": "Architecture decisions"
    }
    
    def __init__(self):
        self.event_bus = get_event_bus()
        self._ingestion_agent: Optional[FileIngestionAgent] = None
    
    def _get_ingestion_agent(self) -> FileIngestionAgent:
        """Lazy-load ingestion agent"""
        if self._ingestion_agent is None:
            self._ingestion_agent = FileIngestionAgent()
        return self._ingestion_agent
    
    async def store_artifact(
        self,
        content: Union[str, Dict, Any],
        category: str = "general",
        subcategory: Optional[str] = None,
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        trust_score: float = 0.8,
        auto_ingest: bool = True
    ) -> Dict[str, Any]:
        """
        Store an artifact in Learning Memory and optionally trigger ingestion
        
        Args:
            content: The content to store (will be JSON-serialized if dict)
            category: Category folder (mentors, autofixes, code_diffs, etc.)
            subcategory: Optional subcategory (task name, mission ID, etc.)
            filename: Optional filename (auto-generated if not provided)
            metadata: Additional metadata to attach
            trust_score: Initial trust score (0-1)
            auto_ingest: Automatically trigger ingestion pipeline
            
        Returns:
            Dict with file_path, document_id, and status
        """
        
        # Build storage path
        category_path = self.BASE_PATH / category
        if subcategory:
            category_path = category_path / subcategory
        category_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            content_hash = hashlib.md5(str(content).encode()).hexdigest()[:8]
            ext = "json" if isinstance(content, dict) else "txt"
            filename = f"{category}_{timestamp}_{content_hash}.{ext}"
        
        file_path = category_path / filename
        
        # Write content
        if isinstance(content, dict) or isinstance(content, list):
            with open(file_path, 'w') as f:
                json.dump(content, f, indent=2, default=str)
        else:
            with open(file_path, 'w') as f:
                f.write(str(content))
        
        # Prepare metadata
        artifact_metadata = {
            "category": category,
            "subcategory": subcategory,
            "stored_at": datetime.utcnow().isoformat(),
            "is_standard_training": True,
            "source_folder": "learning",
            "auto_generated": True,
            "category_description": self.CATEGORIES.get(category, "Unknown")
        }
        
        if metadata:
            artifact_metadata.update(metadata)
        
        # Publish event
        await publish_event_obj(Event(
            event_type="learning.artifact.stored",
            source="learning_memory",
            payload={
                "file_path": str(file_path),
                "category": category,
                "subcategory": subcategory,
                "filename": filename
            }
        ))
        
        result = {
            "status": "stored",
            "file_path": str(file_path),
            "category": category,
            "document_id": None
        }
        
        # Trigger ingestion if requested
        if auto_ingest:
            try:
                agent = self._get_ingestion_agent()
                ingestion_result = await agent.process_file(
                    file_path=file_path,
                    metadata=artifact_metadata,
                    modality=None  # Auto-detect
                )
                
                result.update({
                    "status": "ingested",
                    "document_id": ingestion_result.get("document_id"),
                    "modality": ingestion_result.get("modality"),
                    "ingestion_status": ingestion_result.get("status")
                })
                
            except Exception as e:
                result.update({
                    "status": "stored_but_ingestion_failed",
                    "ingestion_error": str(e)
                })
        
        return result
    
    async def store_mentor_response(
        self,
        task_id: str,
        model_name: str,
        response: str,
        confidence: float,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Convenience method for storing mentor responses
        
        Args:
            task_id: Mission or task identifier
            model_name: Name of the model (e.g., "qwen:14b")
            response: The mentor's response
            confidence: Confidence score (0-1)
            metadata: Additional metadata
        """
        
        content = {
            "task_id": task_id,
            "model": model_name,
            "response": response,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata:
            content["metadata"] = metadata
        
        return await self.store_artifact(
            content=content,
            category="mentors",
            subcategory=task_id,
            metadata={
                "model": model_name,
                "confidence": confidence,
                "artifact_type": "mentor_response"
            },
            trust_score=confidence
        )
    
    async def store_code_fix(
        self,
        incident_id: str,
        code_diff: str,
        description: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Convenience method for storing self-healing code fixes
        """
        
        content = {
            "incident_id": incident_id,
            "description": description,
            "code_diff": code_diff,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata:
            content["metadata"] = metadata
        
        return await self.store_artifact(
            content=content,
            category="autofixes",
            subcategory=incident_id,
            filename=f"fix_{incident_id}.json",
            metadata={
                "incident_id": incident_id,
                "artifact_type": "code_fix"
            }
        )
    
    async def store_mission_brief(
        self,
        mission_id: str,
        objectives: str,
        constraints: Dict,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Convenience method for storing mission specifications
        """
        
        content = {
            "mission_id": mission_id,
            "objectives": objectives,
            "constraints": constraints,
            "created_at": datetime.utcnow().isoformat()
        }
        
        if metadata:
            content["metadata"] = metadata
        
        return await self.store_artifact(
            content=content,
            category="mission_briefs",
            subcategory=mission_id,
            filename=f"brief_{mission_id}.json",
            metadata={
                "mission_id": mission_id,
                "artifact_type": "mission_brief"
            },
            trust_score=1.0  # Mission briefs are authoritative
        )
    
    async def query_category(
        self,
        category: str,
        subcategory: Optional[str] = None,
        limit: int = 20
    ) -> list:
        """
        Query stored artifacts by category
        
        Returns list of file paths
        """
        
        search_path = self.BASE_PATH / category
        if subcategory:
            search_path = search_path / subcategory
        
        if not search_path.exists():
            return []
        
        files = []
        for file_path in search_path.rglob("*"):
            if file_path.is_file():
                files.append(str(file_path))
        
        # Sort by modification time, newest first
        files.sort(key=lambda p: Path(p).stat().st_mtime, reverse=True)
        
        return files[:limit]


# Global instance
_learning_memory = LearningMemoryHelper()


# Convenience functions
async def store_artifact(*args, **kwargs):
    """Store an artifact in Learning Memory"""
    return await _learning_memory.store_artifact(*args, **kwargs)


async def store_mentor_response(*args, **kwargs):
    """Store a mentor response"""
    return await _learning_memory.store_mentor_response(*args, **kwargs)


async def store_code_fix(*args, **kwargs):
    """Store a code fix"""
    return await _learning_memory.store_code_fix(*args, **kwargs)


async def store_mission_brief(*args, **kwargs):
    """Store a mission brief"""
    return await _learning_memory.store_mission_brief(*args, **kwargs)


async def query_category(*args, **kwargs):
    """Query artifacts by category"""
    return await _learning_memory.query_category(*args, **kwargs)
