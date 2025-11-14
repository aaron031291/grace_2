"""
Librarian-Ingestion Integration
Connects enhanced ingestion pipeline with Librarian kernel

Flow:
1. Librarian watches filesystem → Publishes ingestion.request.created
2. Enhanced Ingestion Pipeline processes → Creates chunks
3. Chunks stored in Librarian's book database
4. Librarian updates metadata and indexes
5. Memory kernel persists for retrieval

Integration Points:
- Librarian Kernel: File watching, book management
- Enhanced Ingestion: Real extraction, chunking, quality checks
- Memory Kernel: Chunk storage and retrieval
- HTM: Task prioritization with SLAs
- Governance: Trust validation
"""

import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from backend.core.message_bus import message_bus, MessagePriority
from backend.core.enhanced_ingestion_pipeline import (
    enhanced_ingestion_pipeline,
    IngestionOrigin
)


class LibrarianIngestionIntegration:
    """
    Connects Librarian kernel with enhanced ingestion pipeline
    
    Responsibilities:
    - Subscribe to Librarian filesystem events
    - Trigger ingestion pipeline
    - Store chunks in book database
    - Update Librarian indexes
    - Sync with Memory kernel
    """
    
    def __init__(self):
        self.processing_jobs: Dict[str, Dict] = {}
        self.books_indexed: Dict[str, List[str]] = {}  # book_id -> chunk_ids
        
        self._librarian_watch_task: Optional[asyncio.Task] = None
        self._ingestion_complete_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start integration"""
        
        # Subscribe to Librarian filesystem events
        self._librarian_watch_task = asyncio.create_task(
            self._watch_librarian_events()
        )
        
        # Subscribe to ingestion completions
        self._ingestion_complete_task = asyncio.create_task(
            self._watch_ingestion_completions()
        )
        
        print("[LIBRARIAN-INGEST] Integration started")
        print("[LIBRARIAN-INGEST] Watching: filesystem, API uploads, external connectors")
    
    async def _watch_librarian_events(self):
        """Watch Librarian filesystem events and trigger ingestion"""
        
        try:
            queue = await message_bus.subscribe(
                subscriber="librarian_ingestion_integration",
                topic="librarian.file.detected"
            )
            
            while True:
                msg = await queue.get()
                await self._handle_file_detected(msg.payload)
        
        except Exception as e:
            print(f"[LIBRARIAN-INGEST] Watch error: {e}")
    
    async def _handle_file_detected(self, file_data: Dict[str, Any]):
        """Handle file detected by Librarian"""
        
        file_path = Path(file_data.get("file_path"))
        source = file_data.get("source", "filesystem")
        
        print(f"[LIBRARIAN-INGEST] File detected: {file_path.name} (source: {source})")
        
        # Determine priority based on source
        priority = "normal"
        if source == "api_upload":
            priority = "high"
        elif source == "critical_docs":
            priority = "critical"
        
        # Map source to ingestion origin
        origin_map = {
            "filesystem": IngestionOrigin.FILESYSTEM,
            "api_upload": IngestionOrigin.API,
            "github": IngestionOrigin.EXTERNAL,
            "reddit": IngestionOrigin.EXTERNAL,
            "youtube": IngestionOrigin.EXTERNAL
        }
        origin = origin_map.get(source, IngestionOrigin.FILESYSTEM)
        
        # Trigger ingestion pipeline
        try:
            job_id = await enhanced_ingestion_pipeline.start_pipeline(
                file_path=file_path,
                origin=origin,
                priority=priority,
                metadata={
                    "source": source,
                    "librarian_event": file_data
                }
            )
            
            # Track job
            self.processing_jobs[job_id] = {
                "file_path": str(file_path),
                "book_id": file_data.get("book_id"),
                "started_at": datetime.utcnow().isoformat()
            }
            
            print(f"[LIBRARIAN-INGEST] Started pipeline: {job_id}")
        
        except Exception as e:
            print(f"[LIBRARIAN-INGEST] Failed to start pipeline: {e}")
    
    async def _watch_ingestion_completions(self):
        """Watch ingestion completions and store in Librarian"""
        
        try:
            queue = await message_bus.subscribe(
                subscriber="librarian_ingestion_integration",
                topic="ingestion.job.completed"
            )
            
            while True:
                msg = await queue.get()
                await self._handle_ingestion_complete(msg.payload)
        
        except Exception as e:
            print(f"[LIBRARIAN-INGEST] Completion watch error: {e}")
    
    async def _handle_ingestion_complete(self, job_data: Dict[str, Any]):
        """Handle completed ingestion job"""
        
        job_id = job_data.get("job_id")
        chunks_created = job_data.get("chunks_created", 0)
        trust_score = job_data.get("trust_score", 0.0)
        
        print(f"[LIBRARIAN-INGEST] Job completed: {job_id} ({chunks_created} chunks, trust: {trust_score:.2f})")
        
        # Get job details
        job_info = self.processing_jobs.get(job_id)
        if not job_info:
            return
        
        # Get chunks from pipeline
        job_status = enhanced_ingestion_pipeline.get_job_status(job_id)
        if not job_status:
            return
        
        chunks = job_status.get("chunks", [])
        
        # Store chunks in Librarian's book database
        book_id = job_info.get("book_id") or self._extract_book_id(job_info["file_path"])
        
        await self._store_chunks_in_library(book_id, chunks, trust_score)
        
        # Update Librarian metadata
        await self._update_book_metadata(book_id, {
            "chunks_count": len(chunks),
            "trust_score": trust_score,
            "ingested_at": datetime.utcnow().isoformat(),
            "job_id": job_id
        })
        
        # Publish to Memory kernel for retrieval
        await message_bus.publish(
            source="librarian_ingestion_integration",
            topic="memory.chunks.created",
            payload={
                "book_id": book_id,
                "chunks": chunks,
                "trust_score": trust_score
            },
            priority=MessagePriority.NORMAL
        )
        
        # Track indexed chunks
        chunk_ids = [c["chunk_id"] for c in chunks]
        self.books_indexed[book_id] = chunk_ids
        
        # Cleanup
        del self.processing_jobs[job_id]
    
    async def _store_chunks_in_library(
        self,
        book_id: str,
        chunks: List[Dict[str, Any]],
        trust_score: float
    ):
        """Store chunks in Librarian's database"""
        
        # Would integrate with actual Librarian storage
        # For now, publish event
        
        await message_bus.publish(
            source="librarian_ingestion_integration",
            topic="librarian.chunks.store",
            payload={
                "book_id": book_id,
                "chunks": chunks,
                "trust_score": trust_score,
                "timestamp": datetime.utcnow().isoformat()
            },
            priority=MessagePriority.NORMAL
        )
        
        print(f"[LIBRARIAN-INGEST] Stored {len(chunks)} chunks for book: {book_id}")
    
    async def _update_book_metadata(self, book_id: str, metadata: Dict[str, Any]):
        """Update book metadata in Librarian"""
        
        await message_bus.publish(
            source="librarian_ingestion_integration",
            topic="librarian.book.metadata_updated",
            payload={
                "book_id": book_id,
                "metadata": metadata
            },
            priority=MessagePriority.NORMAL
        )
    
    def _extract_book_id(self, file_path: str) -> str:
        """Extract book ID from file path"""
        path = Path(file_path)
        # Use filename without extension as book_id
        return path.stem
    
    async def reprocess_book(
        self,
        book_id: str,
        reason: str = "quality_improvement"
    ):
        """
        Reprocess a book (triggered by Hunter or diagnostics)
        
        Use case: Chunk drift detected, schema change, quality upgrade
        """
        
        print(f"[LIBRARIAN-INGEST] Reprocessing book: {book_id} (reason: {reason})")
        
        # Find original file
        # Would query Librarian for file path
        
        # Publish reprocess event
        await message_bus.publish(
            source="librarian_ingestion_integration",
            topic="ingestion.reprocess",
            payload={
                "book_id": book_id,
                "reason": reason,
                "origin": IngestionOrigin.REPROCESS.value,
                "priority": "high"
            },
            priority=MessagePriority.HIGH
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "active_jobs": len(self.processing_jobs),
            "books_indexed": len(self.books_indexed),
            "total_chunks": sum(len(chunks) for chunks in self.books_indexed.values())
        }


# Global instance
librarian_ingestion_integration = LibrarianIngestionIntegration()
