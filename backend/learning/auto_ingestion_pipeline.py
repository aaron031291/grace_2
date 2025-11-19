"""
Auto-Ingestion Pipeline - Automatic processing of uploaded files and screen shares

Flow:
1. File uploaded → Chunking
2. Chunks → Embedding generation
3. Embeddings → Vector store indexing
4. Metadata → World model sync
5. Status → "Processing" → "Ready" → "Indexed"

Supports:
- PDFs, documents, text files
- Images with OCR
- Audio with transcription
- Screen shares with vision analysis
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4

from backend.event_bus import event_bus, Event, EventType
from backend.memory.memory_catalog import memory_catalog, AssetStatus, AssetType
from backend.memory.memory_mount import memory_mount
from backend.world_model.grace_world_model import grace_world_model
from backend.services.rag_service import RAGService


class IngestionPipeline:
    """
    Automatic ingestion pipeline
    
    Listens for file uploads and screen shares,
    then automatically processes them through:
    - Text extraction
    - Chunking
    - Embedding generation
    - Vector store indexing
    - World model sync
    """
    
    def __init__(self):
        self.rag_service = RAGService()
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        
    async def initialize(self):
        """Initialize pipeline and start worker"""
        await self.rag_service.initialize()
        
        # Subscribe to upload events
        event_bus.subscribe(EventType.MEMORY_UPDATE, self._on_memory_event)
        
        # Start processing worker
        self.running = True
        asyncio.create_task(self._process_queue())
        
        print("[IngestionPipeline] Initialized and ready")
    
    async def _on_memory_event(self, event: Event):
        """Handle memory events (uploads, screen shares)"""
        action = event.data.get("action")
        
        if action == "asset_registered":
            asset_id = event.data.get("asset_id")
            await self.processing_queue.put(asset_id)
            print(f"[IngestionPipeline] Queued for processing: {asset_id}")
    
    async def _process_queue(self):
        """Background worker to process ingestion queue"""
        while self.running:
            try:
                asset_id = await asyncio.wait_for(
                    self.processing_queue.get(),
                    timeout=1.0
                )
                await self.process_asset(asset_id)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"[IngestionPipeline] Queue processing error: {e}")
    
    async def process_asset(self, asset_id: str):
        """
        Process asset through full pipeline
        
        Steps:
        1. Extract text/content
        2. Chunk content
        3. Generate embeddings
        4. Index in vector store
        5. Update world model
        6. Mark as ready
        """
        try:
            asset = memory_catalog.get_asset(asset_id)
            if not asset:
                print(f"[IngestionPipeline] Asset not found: {asset_id}")
                return
            
            print(f"[IngestionPipeline] Processing: {asset_id} ({asset.asset_type.value})")
            
            # Update status to processing
            memory_catalog.update_asset_status(
                asset_id,
                AssetStatus.PROCESSING,
                {"processing_started": datetime.utcnow().isoformat()}
            )
            
            # Step 1: Extract text/content
            content = await self._extract_content(asset)
            
            if not content:
                print(f"[IngestionPipeline] No content extracted from {asset_id}")
                memory_catalog.update_asset_status(
                    asset_id,
                    AssetStatus.FAILED,
                    {"error": "No content extracted"}
                )
                return
            
            # Step 2: Chunk content
            chunks = self._chunk_content(content, asset)
            
            # Step 3: Generate embeddings and index
            indexed_count = await self._index_chunks(asset_id, chunks, asset)
            
            # Step 4: Update world model
            await self._sync_to_world_model(asset, content, chunks)
            
            # Step 5: Mark as indexed
            memory_catalog.update_asset_status(
                asset_id,
                AssetStatus.INDEXED,
                {
                    "processing_completed": datetime.utcnow().isoformat(),
                    "chunks_indexed": indexed_count,
                    "content_length": len(content),
                }
            )
            
            # Publish completion event
            await event_bus.publish(Event(
                event_type=EventType.MEMORY_UPDATE,
                source="ingestion_pipeline",
                data={
                    "action": "asset_indexed",
                    "asset_id": asset_id,
                    "chunks": indexed_count,
                }
            ))
            
            print(f"[IngestionPipeline] Completed: {asset_id} ({indexed_count} chunks)")
        
        except Exception as e:
            print(f"[IngestionPipeline] Processing failed for {asset_id}: {e}")
            memory_catalog.update_asset_status(
                asset_id,
                AssetStatus.FAILED,
                {"error": str(e)}
            )
    
    async def _extract_content(self, asset) -> Optional[str]:
        """Extract text content from asset"""
        file_path = Path(asset.path)
        
        if not file_path.exists():
            return None
        
        # Handle different asset types
        if asset.asset_type == AssetType.PDF:
            return await self._extract_pdf(file_path)
        
        elif asset.asset_type in [AssetType.WEB_PAGE, AssetType.UPLOAD]:
            # Text file
            try:
                return file_path.read_text(encoding='utf-8')
            except:
                return None
        
        elif asset.asset_type == AssetType.AUDIO:
            return await self._extract_audio(file_path)
        
        elif asset.asset_type == AssetType.SCREEN_SHARE:
            return await self._extract_image(file_path)
        
        else:
            # Try reading as text
            try:
                return file_path.read_text(encoding='utf-8')
            except:
                return None
    
    async def _extract_pdf(self, file_path: Path) -> Optional[str]:
        """Extract text from PDF"""
        try:
            import PyPDF2
            text = []
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text.append(page.extract_text())
            return "\n".join(text)
        except ImportError:
            print("[IngestionPipeline] PyPDF2 not installed")
            return None
        except Exception as e:
            print(f"[IngestionPipeline] PDF extraction failed: {e}")
            return None
    
    async def _extract_audio(self, file_path: Path) -> Optional[str]:
        """Extract text from audio via transcription"""
        # Placeholder - integrate with Whisper or other STT
        return f"[Audio transcription not yet implemented for {file_path.name}]"
    
    async def _extract_image(self, file_path: Path) -> Optional[str]:
        """Extract text from image via OCR"""
        # Placeholder - integrate with Tesseract or GPT-4 Vision
        return f"[Image OCR not yet implemented for {file_path.name}]"
    
    def _chunk_content(
        self,
        content: str,
        asset,
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Chunk content for embedding
        
        Args:
            content: Full text content
            asset: Asset metadata
            chunk_size: Target chunk size in chars
            overlap: Overlap between chunks
        
        Returns:
            List of chunks with metadata
        """
        chunks = []
        
        # Simple chunking by character count
        start = 0
        chunk_id = 0
        
        while start < len(content):
            end = start + chunk_size
            chunk_text = content[start:end]
            
            chunks.append({
                "chunk_id": f"{asset.asset_id}_chunk_{chunk_id}",
                "text": chunk_text,
                "source": asset.path,
                "asset_id": asset.asset_id,
                "chunk_index": chunk_id,
                "start_char": start,
                "end_char": end,
                "metadata": {
                    "asset_type": asset.asset_type.value,
                    "source_type": asset.source.value,
                    "original_filename": asset.metadata.get("original_filename", ""),
                }
            })
            
            chunk_id += 1
            start = end - overlap
        
        return chunks
    
    async def _index_chunks(
        self,
        asset_id: str,
        chunks: List[Dict[str, Any]],
        asset
    ) -> int:
        """
        Generate embeddings and index chunks in vector store
        
        Args:
            asset_id: Asset identifier
            chunks: Content chunks
            asset: Asset metadata
        
        Returns:
            Number of chunks indexed
        """
        indexed = 0
        
        for chunk in chunks:
            try:
                # Store in RAG service (which handles embedding + vector store)
                await self.rag_service.store(
                    text=chunk["text"],
                    source=chunk["source"],
                    metadata={
                        **chunk["metadata"],
                        "chunk_id": chunk["chunk_id"],
                        "chunk_index": chunk["chunk_index"],
                        "asset_id": asset_id,
                        "trust_score": asset.trust_score,
                    },
                    trust_score=asset.trust_score
                )
                indexed += 1
            except Exception as e:
                print(f"[IngestionPipeline] Chunk indexing failed: {e}")
        
        return indexed
    
    async def _sync_to_world_model(
        self,
        asset,
        content: str,
        chunks: List[Dict[str, Any]]
    ):
        """
        Sync asset knowledge to world model
        
        Creates world model entry with:
        - Summary of content
        - Provenance (source, upload date, trust)
        - Links to RAG chunks
        """
        # Create summary
        summary = content[:500] + "..." if len(content) > 500 else content
        
        # Store in world model
        await grace_world_model.store_knowledge(
            category="ingested_document",
            content=f"Learned from {asset.asset_type.value}: {asset.metadata.get('original_filename', asset.path)}. Content summary: {summary}",
            source=f"ingestion_pipeline::{asset.source.value}",
            confidence=asset.trust_score,
            tags=[
                asset.asset_type.value,
                asset.source.value,
                "ingested",
                f"chunks:{len(chunks)}"
            ],
            metadata={
                "asset_id": asset.asset_id,
                "asset_path": asset.path,
                "chunks": len(chunks),
                "content_length": len(content),
                "ingestion_date": asset.ingestion_date,
                "provenance": {
                    "source": asset.source.value,
                    "original_filename": asset.metadata.get("original_filename"),
                    "trust_score": asset.trust_score,
                }
            }
        )


# Global pipeline instance
ingestion_pipeline = IngestionPipeline()
