"""
Enhanced Librarian Kernel - Integrated with Real Ingestion Pipeline

Watches:
- grace_training/documents/books/
- storage/uploads/
- External connectors (GitHub, Reddit, YouTube)

Triggers:
- Publishes ingestion.request.created for all sources
- Routes to enhanced ingestion pipeline
- Stores results in book database
- Syncs with Memory kernel
"""

import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from backend.core.kernel_sdk import KernelSDK
from backend.core.message_bus import message_bus, MessagePriority
from backend.core.enhanced_ingestion_pipeline import IngestionOrigin


class BookFileHandler(FileSystemEventHandler):
    """Handles filesystem events for books"""
    
    def __init__(self, librarian_kernel):
        self.librarian = librarian_kernel
    
    def on_created(self, event):
        """File created"""
        if not event.is_directory and self._is_book_file(event.src_path):
            asyncio.create_task(
                self.librarian.handle_file_event("created", event.src_path)
            )
    
    def on_modified(self, event):
        """File modified"""
        if not event.is_directory and self._is_book_file(event.src_path):
            asyncio.create_task(
                self.librarian.handle_file_event("modified", event.src_path)
            )
    
    def _is_book_file(self, path: str) -> bool:
        """Check if file is a book"""
        ext = Path(path).suffix.lower()
        return ext in ['.pdf', '.epub', '.txt', '.md', '.docx']


class EnhancedLibrarianKernel(KernelSDK):
    """
    Enhanced Librarian Kernel with real ingestion integration
    
    Features:
    - Real filesystem watching
    - Multi-perspective triggers (filesystem, API, external)
    - Integration with enhanced ingestion pipeline
    - Book database management
    - Memory kernel sync
    """
    
    def __init__(self):
        super().__init__(kernel_name="librarian_enhanced")
        
        # Watch directories
        self.watch_dirs = [
            Path("grace_training/documents/books"),
            Path("storage/uploads"),
            Path("storage/books")
        ]
        
        # Filesystem observer
        self.observer = None
        
        # Book tracking
        self.books: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self.stats = {
            "files_detected": 0,
            "ingestion_triggered": 0,
            "books_indexed": 0,
            "chunks_stored": 0
        }
    
    async def initialize(self):
        """Initialize kernel"""
        
        await self.register_component(
            capabilities=[
                'filesystem_watching',
                'book_management',
                'ingestion_triggering',
                'chunk_storage'
            ],
            contracts={
                'supported_formats': ['pdf', 'epub', 'txt', 'md', 'docx'],
                'watch_latency_ms': {'max': 1000}
            }
        )
        
        # Start filesystem watching
        await self._start_filesystem_watch()
        
        # Subscribe to ingestion completions
        asyncio.create_task(self._watch_ingestion_completions())
        
        # Subscribe to external connector events
        asyncio.create_task(self._watch_external_sources())
        
        print(f"[LIBRARIAN] Enhanced kernel initialized")
        print(f"[LIBRARIAN] Watching {len(self.watch_dirs)} directories")
    
    async def _start_filesystem_watch(self):
        """Start watching filesystem for books"""
        
        # Ensure directories exist
        for watch_dir in self.watch_dirs:
            watch_dir.mkdir(parents=True, exist_ok=True)
        
        # Start watchdog observer
        self.observer = Observer()
        event_handler = BookFileHandler(self)
        
        for watch_dir in self.watch_dirs:
            if watch_dir.exists():
                self.observer.schedule(event_handler, str(watch_dir), recursive=True)
                print(f"[LIBRARIAN] Watching: {watch_dir}")
        
        self.observer.start()
    
    async def handle_file_event(self, event_type: str, file_path: str):
        """Handle filesystem event"""
        
        self.stats["files_detected"] += 1
        
        file_path_obj = Path(file_path)
        
        print(f"[LIBRARIAN] File {event_type}: {file_path_obj.name}")
        
        # Publish librarian.file.detected (for integration layer)
        await message_bus.publish(
            source="librarian_enhanced",
            topic="librarian.file.detected",
            payload={
                "file_path": str(file_path_obj),
                "file_name": file_path_obj.name,
                "event_type": event_type,
                "source": "filesystem",
                "detected_at": datetime.utcnow().isoformat()
            },
            priority=MessagePriority.NORMAL
        )
        
        # Also publish ingestion.request.created (multi-perspective trigger)
        await self._trigger_ingestion(file_path_obj, source="filesystem")
    
    async def _trigger_ingestion(
        self,
        file_path: Path,
        source: str = "filesystem",
        priority: str = "normal"
    ):
        """Trigger ingestion pipeline"""
        
        self.stats["ingestion_triggered"] += 1
        
        # Determine origin
        origin_map = {
            "filesystem": IngestionOrigin.FILESYSTEM,
            "api_upload": IngestionOrigin.API,
            "github": IngestionOrigin.EXTERNAL,
            "reddit": IngestionOrigin.EXTERNAL,
            "youtube": IngestionOrigin.EXTERNAL,
            "hunter_diagnostic": IngestionOrigin.AUTOHEAL
        }
        origin = origin_map.get(source, IngestionOrigin.FILESYSTEM)
        
        # Create book record
        book_id = file_path.stem
        if book_id not in self.books:
            self.books[book_id] = {
                "book_id": book_id,
                "file_path": str(file_path),
                "file_name": file_path.name,
                "source": source,
                "status": "processing",
                "created_at": datetime.utcnow().isoformat()
            }
        
        # Publish multi-perspective trigger event
        await message_bus.publish(
            source="librarian_enhanced",
            topic="ingestion.request.created",
            payload={
                "file_path": str(file_path),
                "book_id": book_id,
                "origin": origin.value,
                "source": source,
                "priority": priority,
                "trust": "filesystem" if origin == IngestionOrigin.FILESYSTEM else "external",
                "sla_seconds": 14400 if priority == "normal" else 1800,  # 4h or 30min
                "metadata": {
                    "detected_by": "librarian_kernel",
                    "file_size": file_path.stat().st_size if file_path.exists() else 0
                }
            },
            priority=MessagePriority.HIGH if priority == "critical" else MessagePriority.NORMAL
        )
        
        print(f"[LIBRARIAN] Triggered ingestion: {book_id} (origin: {origin.value}, priority: {priority})")
    
    async def _watch_ingestion_completions(self):
        """Watch for ingestion completions and update book database"""
        
        try:
            queue = await message_bus.subscribe(
                subscriber="librarian_enhanced",
                topic="ingestion.job.completed"
            )
            
            while True:
                msg = await queue.get()
                await self._handle_ingestion_completed(msg.payload)
        
        except Exception as e:
            print(f"[LIBRARIAN] Completion watch error: {e}")
    
    async def _handle_ingestion_completed(self, job_data: Dict[str, Any]):
        """Handle completed ingestion"""
        
        job_id = job_data.get("job_id")
        chunks_created = job_data.get("chunks_created", 0)
        trust_score = job_data.get("trust_score", 0.0)
        
        # Get job from pipeline
        job_status = enhanced_ingestion_pipeline.get_job_status(job_id)
        if not job_status:
            return
        
        file_path = job_status.get("file_path")
        book_id = Path(file_path).stem if file_path else "unknown"
        
        # Update book record
        if book_id in self.books:
            self.books[book_id].update({
                "status": "completed",
                "chunks_count": chunks_created,
                "trust_score": trust_score,
                "job_id": job_id,
                "completed_at": datetime.utcnow().isoformat()
            })
        
        self.stats["books_indexed"] += 1
        self.stats["chunks_stored"] += chunks_created
        
        # Publish to Librarian's book management
        await message_bus.publish(
            source="librarian_enhanced",
            topic="librarian.book.indexed",
            payload={
                "book_id": book_id,
                "chunks_count": chunks_created,
                "trust_score": trust_score,
                "file_path": file_path
            },
            priority=MessagePriority.NORMAL
        )
        
        print(f"[LIBRARIAN] Book indexed: {book_id} ({chunks_created} chunks)")
    
    async def _watch_external_sources(self):
        """Watch external connectors (GitHub, Reddit, YouTube)"""
        
        try:
            # Subscribe to external connector events
            topics = [
                "external.github.content",
                "external.reddit.content",
                "external.youtube.content"
            ]
            
            for topic in topics:
                asyncio.create_task(self._monitor_external_source(topic))
        
        except Exception as e:
            print(f"[LIBRARIAN] External watch error: {e}")
    
    async def _monitor_external_source(self, topic: str):
        """Monitor specific external source"""
        
        try:
            queue = await message_bus.subscribe(
                subscriber=f"librarian_external_{topic}",
                topic=topic
            )
            
            while True:
                msg = await queue.get()
                
                # External content detected
                source_type = topic.split('.')[-2]  # github, reddit, youtube
                content_data = msg.payload
                
                # Would save to temp file and trigger ingestion
                # For now, publish ingestion request
                
                await message_bus.publish(
                    source="librarian_enhanced",
                    topic="ingestion.request.created",
                    payload={
                        "content_url": content_data.get("url"),
                        "source": source_type,
                        "origin": IngestionOrigin.EXTERNAL.value,
                        "priority": "normal",
                        "metadata": content_data
                    },
                    priority=MessagePriority.NORMAL
                )
                
                print(f"[LIBRARIAN] External content: {source_type}")
        
        except Exception as e:
            print(f"[LIBRARIAN] External source {topic} error: {e}")
    
    async def handle_hunter_reprocess_request(
        self,
        book_id: str,
        reason: str
    ):
        """Handle Hunter/diagnostic reprocess requests"""
        
        print(f"[LIBRARIAN] Reprocess request: {book_id} (reason: {reason})")
        
        # Find book file
        book_info = self.books.get(book_id)
        if not book_info:
            print(f"[LIBRARIAN] Book not found: {book_id}")
            return
        
        file_path = Path(book_info["file_path"])
        
        # Trigger reprocess via ingestion pipeline
        await self._trigger_ingestion(
            file_path=file_path,
            source="hunter_diagnostic",
            priority="high"  # Hunter requests are high priority
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get kernel statistics"""
        return {
            **self.stats,
            "books_tracked": len(self.books),
            "watch_dirs": [str(d) for d in self.watch_dirs]
        }


# Global instance
enhanced_librarian_kernel = EnhancedLibrarianKernel()
