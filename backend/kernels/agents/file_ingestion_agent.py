"""
File Ingestion Agent - Unified processor for all file modalities
Handles: API artifacts, web content, audio, video, code, and XXL uploads

Mirrors the BookIngestionAgent pattern for consistent processing across all file types.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json
import hashlib
import mimetypes

from backend.clarity import BaseComponent, ComponentStatus, Event, TrustLevel, get_event_bus
from backend.database import get_db


class FileIngestionAgent(BaseComponent):
    """
    Unified agent for ingesting all file types into Grace's memory.
    
    Storage Structure:
        storage/memory/raw/
            ├── api/         # API responses (JSON/XML)
            ├── web/         # Web scrapes (HTML/Markdown)
            ├── audio/       # Audio files (MP3/WAV/M4A)
            ├── video/       # Video files (MP4/AVI/MOV)
            ├── code/        # Code files/repos
            ├── xxl/         # Extra-large files (>100MB)
            └── upload/      # General uploads
    
    Workflow:
    1. Detect file type and route to appropriate storage
    2. Extract metadata (size, mime-type, hash)
    3. Trigger modality-specific processing:
       - API/Web: Parse structure, extract entities
       - Audio: Transcribe with Whisper
       - Video: Extract frames + transcribe audio
       - Code: Parse syntax, build knowledge graph
       - XXL: Stream processing with checkpoints
    4. Generate embeddings
    5. Create insights/summaries
    6. Update memory_documents
    7. Trigger verification pipeline
    8. Publish completion event
    """
    
    MODALITY_MAP = {
        'api': ['json', 'xml', 'yaml'],
        'web': ['html', 'htm', 'md', 'markdown'],
        'audio': ['mp3', 'wav', 'm4a', 'flac', 'ogg'],
        'video': ['mp4', 'avi', 'mov', 'mkv', 'webm'],
        'code': ['py', 'js', 'ts', 'java', 'cpp', 'c', 'go', 'rs', 'rb'],
        'upload': []  # Fallback for unknown types
    }
    
    XXL_THRESHOLD = 100 * 1024 * 1024  # 100MB
    
    def __init__(self):
        super().__init__()
        self.component_type = "file_ingestion_agent"
        self.event_bus = get_event_bus()
        self._setup_storage_dirs()
        
    def _setup_storage_dirs(self):
        """Ensure all storage directories exist"""
        base_dir = Path("storage/memory/raw")
        for modality in self.MODALITY_MAP.keys():
            (base_dir / modality).mkdir(parents=True, exist_ok=True)
        (base_dir / "xxl").mkdir(parents=True, exist_ok=True)
        
    async def activate(self) -> bool:
        """Activate the file ingestion agent"""
        self.set_status(ComponentStatus.ACTIVE)
        self.activated_at = datetime.utcnow()
        return True
    
    async def deactivate(self) -> bool:
        """Deactivate the agent"""
        self.set_status(ComponentStatus.INACTIVE)
        return True
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "component_id": self.component_id,
            "status": self.status.value if hasattr(self, 'status') else "unknown",
            "activated_at": self.activated_at.isoformat() if hasattr(self, 'activated_at') and self.activated_at else None,
            "supported_modalities": list(self.MODALITY_MAP.keys())
        }
    
    def _detect_modality(self, file_path: Path) -> str:
        """Detect file modality based on extension"""
        ext = file_path.suffix.lstrip('.').lower()
        
        for modality, extensions in self.MODALITY_MAP.items():
            if ext in extensions:
                return modality
        
        return 'upload'  # Default fallback
    
    def _is_xxl(self, file_path: Path) -> bool:
        """Check if file exceeds XXL threshold"""
        try:
            return file_path.stat().st_size > self.XXL_THRESHOLD
        except:
            return False
    
    async def process_file(
        self, 
        file_path: Path, 
        metadata: Optional[Dict] = None,
        modality: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for file ingestion
        
        Args:
            file_path: Path to file
            metadata: Optional metadata dict
            modality: Optional override for modality detection
            
        Returns:
            Dict with ingestion results
        """
        
        result = {
            "status": "started",
            "file_path": str(file_path),
            "modality": None,
            "document_id": None,
            "chunks_created": 0,
            "insights_created": 0,
            "processed_artifacts": {},
            "errors": []
        }
        
        try:
            # Step 1: Detect modality
            detected_modality = modality or self._detect_modality(file_path)
            is_xxl = self._is_xxl(file_path)
            
            if is_xxl:
                detected_modality = 'xxl'
                
            result["modality"] = detected_modality
            
            await self.event_bus.publish(Event(
                event_type="file.ingestion.started",
                source=self.component_id,
                payload={
                    "file": str(file_path),
                    "modality": detected_modality,
                    "is_xxl": is_xxl
                }
            ))
            
            # Step 2: Move to appropriate storage location
            storage_path = await self._store_file(file_path, detected_modality)
            result["storage_path"] = str(storage_path)
            
            # Step 3: Extract base metadata
            base_metadata = await self._extract_base_metadata(storage_path, metadata)
            
            # Step 4: Create document entry
            document_id = await self._create_document_entry(
                storage_path, 
                base_metadata, 
                detected_modality
            )
            result["document_id"] = document_id
            
            # Step 5: Route to modality-specific processor
            processing_result = await self._process_by_modality(
                storage_path, 
                document_id, 
                detected_modality,
                base_metadata
            )
            result["processed_artifacts"] = processing_result
            
            # Step 6: Trigger embedding pipeline
            await self._trigger_embedding_pipeline(document_id, detected_modality)
            
            # Step 7: Queue verification
            await self._queue_verification(document_id, detected_modality)
            
            # Step 8: Publish completion event
            await self.event_bus.publish(Event(
                event_type="file.ingestion.completed",
                source=self.component_id,
                payload={
                    "document_id": document_id,
                    "modality": detected_modality,
                    "artifacts": processing_result
                }
            ))
            
            result["status"] = "completed"
            
        except Exception as e:
            result["status"] = "failed"
            result["errors"].append(str(e))
            
            await self.event_bus.publish(Event(
                event_type="file.ingestion.failed",
                source=self.component_id,
                payload={
                    "file": str(file_path),
                    "error": str(e)
                }
            ))
        
        return result
    
    async def _store_file(self, file_path: Path, modality: str) -> Path:
        """Move file to appropriate storage directory"""
        storage_base = Path("storage/memory/raw") / modality
        storage_base.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename with hash
        file_hash = hashlib.sha256(str(file_path).encode()).hexdigest()[:16]
        storage_path = storage_base / f"{file_hash}_{file_path.name}"
        
        # Move or copy file
        if file_path != storage_path:
            import shutil
            shutil.copy2(file_path, storage_path)
        
        return storage_path
    
    async def _extract_base_metadata(
        self, 
        file_path: Path, 
        user_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Extract basic file metadata"""
        
        stats = file_path.stat()
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        metadata = {
            "filename": file_path.name,
            "size_bytes": stats.st_size,
            "size_mb": round(stats.st_size / (1024 * 1024), 2),
            "mime_type": mime_type or "application/octet-stream",
            "extension": file_path.suffix,
            "created_at": datetime.fromtimestamp(stats.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "sha256_hash": await self._calculate_hash(file_path)
        }
        
        # Merge with user-provided metadata
        if user_metadata:
            metadata.update(user_metadata)
        
        return metadata
    
    async def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    async def _create_document_entry(
        self, 
        file_path: Path, 
        metadata: Dict[str, Any],
        modality: str
    ) -> str:
        """Create entry in memory_documents table"""
        
        from backend.memory_tables.registry import table_registry
        
        doc_data = {
            "title": metadata.get("title", file_path.name),
            "source_type": modality,
            "file_path": str(file_path),
            "metadata": json.dumps(metadata),
            "trust_score": 0.0,  # Will be updated after verification
            "last_synced_at": datetime.utcnow(),
            "notes": metadata.get("description", "")
        }
        
        row = table_registry.insert_row('memory_documents', doc_data)
        return getattr(row, 'id', None) or str(hash(str(file_path)))
    
    async def _process_by_modality(
        self,
        file_path: Path,
        document_id: str,
        modality: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route to modality-specific processor"""
        
        processors = {
            'api': self._process_api,
            'web': self._process_web,
            'audio': self._process_audio,
            'video': self._process_video,
            'code': self._process_code,
            'xxl': self._process_xxl,
            'upload': self._process_generic
        }
        
        processor = processors.get(modality, self._process_generic)
        return await processor(file_path, document_id, metadata)
    
    async def _process_api(
        self, 
        file_path: Path, 
        document_id: str, 
        metadata: Dict
    ) -> Dict[str, Any]:
        """Process API artifacts (JSON/XML)"""
        
        await self.event_bus.publish(Event(
            event_type="file.processing.api",
            source=self.component_id,
            payload={"document_id": document_id}
        ))
        
        result = {"type": "api", "entities_extracted": 0}
        
        try:
            # Parse JSON/XML structure
            if file_path.suffix == '.json':
                with open(file_path) as f:
                    data = json.load(f)
                result["structure"] = "json"
                result["keys"] = list(data.keys()) if isinstance(data, dict) else []
        except:
            pass
        
        return result
    
    async def _process_web(
        self, 
        file_path: Path, 
        document_id: str, 
        metadata: Dict
    ) -> Dict[str, Any]:
        """Process web content (HTML/Markdown)"""
        
        await self.event_bus.publish(Event(
            event_type="file.processing.web",
            source=self.component_id,
            payload={"document_id": document_id}
        ))
        
        return {"type": "web", "links_extracted": 0, "text_length": 0}
    
    async def _process_audio(
        self, 
        file_path: Path, 
        document_id: str, 
        metadata: Dict
    ) -> Dict[str, Any]:
        """Process audio files - trigger transcription"""
        
        await self.event_bus.publish(Event(
            event_type="file.processing.audio",
            source=self.component_id,
            payload={
                "document_id": document_id,
                "action": "transcription_requested"
            }
        ))
        
        # Store reference to transcription task
        return {
            "type": "audio",
            "transcription_queued": True,
            "transcription_path": f"storage/memory/processed/transcripts/{document_id}.txt"
        }
    
    async def _process_video(
        self, 
        file_path: Path, 
        document_id: str, 
        metadata: Dict
    ) -> Dict[str, Any]:
        """Process video files - extract frames + transcribe"""
        
        await self.event_bus.publish(Event(
            event_type="file.processing.video",
            source=self.component_id,
            payload={
                "document_id": document_id,
                "action": "frame_extraction_and_transcription_requested"
            }
        ))
        
        return {
            "type": "video",
            "frame_extraction_queued": True,
            "transcription_queued": True,
            "frames_path": f"storage/memory/processed/frames/{document_id}/",
            "transcript_path": f"storage/memory/processed/transcripts/{document_id}.txt"
        }
    
    async def _process_code(
        self, 
        file_path: Path, 
        document_id: str, 
        metadata: Dict
    ) -> Dict[str, Any]:
        """Process code files - build knowledge graph"""
        
        await self.event_bus.publish(Event(
            event_type="file.processing.code",
            source=self.component_id,
            payload={
                "document_id": document_id,
                "language": file_path.suffix.lstrip('.'),
                "action": "code_analysis_requested"
            }
        ))
        
        return {
            "type": "code",
            "language": file_path.suffix.lstrip('.'),
            "analysis_queued": True
        }
    
    async def _process_xxl(
        self, 
        file_path: Path, 
        document_id: str, 
        metadata: Dict
    ) -> Dict[str, Any]:
        """Process extra-large files with streaming"""
        
        await self.event_bus.publish(Event(
            event_type="file.processing.xxl",
            source=self.component_id,
            payload={
                "document_id": document_id,
                "size_mb": metadata.get("size_mb", 0),
                "action": "chunked_processing_requested"
            }
        ))
        
        return {
            "type": "xxl",
            "streaming_enabled": True,
            "checkpoint_enabled": True
        }
    
    async def _process_generic(
        self, 
        file_path: Path, 
        document_id: str, 
        metadata: Dict
    ) -> Dict[str, Any]:
        """Generic processor for unknown file types"""
        
        return {
            "type": "generic",
            "mime_type": metadata.get("mime_type", "unknown")
        }
    
    async def _trigger_embedding_pipeline(self, document_id: str, modality: str):
        """Trigger ML embedding generation"""
        
        await self.event_bus.publish(Event(
            event_type="ml.embedding.requested",
            source=self.component_id,
            payload={
                "document_id": document_id,
                "modality": modality,
                "priority": "normal"
            }
        ))
    
    async def _queue_verification(self, document_id: str, modality: str):
        """Queue document for verification"""
        
        await self.event_bus.publish(Event(
            event_type="verification.document.requested",
            source=self.component_id,
            payload={
                "document_id": document_id,
                "verification_type": f"{modality}_comprehensive",
                "triggered_by": "auto_ingestion"
            }
        ))
