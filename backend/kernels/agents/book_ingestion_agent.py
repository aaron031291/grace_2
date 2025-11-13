"""
Book Ingestion Agent - Specialized processor for PDF/EPUB books
Handles: text extraction, chapter detection, summary generation, flashcard creation
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json
import hashlib
import asyncio

from backend.clarity import BaseComponent, ComponentStatus, Event, TrustLevel, get_event_bus
from backend.database import get_db


class BookIngestionAgent(BaseComponent):
    """
    Specialized agent for ingesting books (PDF/EPUB) into Grace's memory.
    
    Workflow:
    1. Extract metadata (title, author, ISBN)
    2. Extract text content (with OCR fallback if needed)
    3. Detect chapters/sections
    4. Chunk content intelligently (by chapter/section)
    5. Generate embeddings for each chunk
    6. Create chapter summaries
    7. Generate flashcards for key concepts
    8. Update memory_documents and related tables
    9. Trigger verification pipeline
    """
    
    def __init__(self):
        super().__init__()
        self.component_type = "book_ingestion_agent"
        self.event_bus = get_event_bus()
        
    async def activate(self) -> bool:
        """Activate the book ingestion agent"""
        self.set_status(ComponentStatus.ACTIVE)
        self.activated_at = datetime.utcnow()
        return True
    
    async def process_book(self, file_path: Path, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main entry point for book ingestion
        
        Args:
            file_path: Path to PDF/EPUB file
            metadata: Optional metadata dict (from .meta.json sidecar)
            
        Returns:
            Dict with ingestion results
        """
        
        result = {
            "status": "started",
            "file_path": str(file_path),
            "document_id": None,
            "chunks_created": 0,
            "insights_created": 0,
            "errors": []
        }
        
        try:
            # Step 1: Extract metadata
            await self.event_bus.publish(Event(
                event_type="book.ingestion.metadata_extraction",
                source=self.component_id,
                payload={"file": str(file_path)}
            ))
            
            extracted_meta = await self._extract_metadata(file_path, metadata)
            
            # Step 2: Create document entry in memory_documents
            document_id = await self._create_document_entry(file_path, extracted_meta)
            result["document_id"] = document_id
            
            # Step 3: Extract text content
            await self.event_bus.publish(Event(
                event_type="book.ingestion.text_extraction",
                source=self.component_id,
                payload={"document_id": document_id}
            ))
            
            content = await self._extract_text(file_path)
            
            # Step 4: Detect chapters/sections
            chapters = await self._detect_chapters(content, extracted_meta)
            
            # Step 5: Chunk and embed
            await self.event_bus.publish(Event(
                event_type="book.ingestion.chunking",
                source=self.component_id,
                payload={"document_id": document_id, "chapters": len(chapters)}
            ))
            
            chunks = await self._create_chunks(chapters, document_id)
            result["chunks_created"] = len(chunks)
            
            # Step 6: Generate summaries and insights
            await self.event_bus.publish(Event(
                event_type="book.ingestion.summary_generation",
                source=self.component_id,
                payload={"document_id": document_id}
            ))
            
            insights = await self._generate_insights(chapters, document_id, extracted_meta)
            result["insights_created"] = len(insights)
            
            # Step 7: Trigger ML/embedding pipeline
            await self._trigger_embedding_pipeline(document_id, chunks)
            
            # Step 8: Queue verification
            await self._queue_verification(document_id)
            
            result["status"] = "completed"
            
            await self.event_bus.publish(Event(
                event_type="book.ingestion.completed",
                source=self.component_id,
                payload=result,
                trust_level=TrustLevel.MEDIUM
            ))
            
        except Exception as e:
            result["status"] = "failed"
            result["errors"].append(str(e))
            
            await self.event_bus.publish(Event(
                event_type="book.ingestion.failed",
                source=self.component_id,
                payload=result,
                trust_level=TrustLevel.LOW
            ))
            
        return result
    
    async def _extract_metadata(self, file_path: Path, provided_meta: Optional[Dict]) -> Dict[str, Any]:
        """Extract or merge metadata"""
        
        meta = {
            "title": file_path.stem,
            "author": "Unknown",
            "isbn": None,
            "domain_tags": [],
            "source_type": "book",
            "file_type": file_path.suffix.lower(),
            "file_size": file_path.stat().st_size,
            "extracted_at": datetime.utcnow().isoformat()
        }
        
        # Check for metadata sidecar
        sidecar_path = file_path.with_suffix('.meta.json')
        if sidecar_path.exists():
            try:
                with open(sidecar_path, 'r', encoding='utf-8') as f:
                    sidecar_meta = json.load(f)
                    meta.update(sidecar_meta)
            except Exception as e:
                meta["metadata_errors"] = [f"Sidecar parsing failed: {e}"]
        
        # Override with provided metadata
        if provided_meta:
            meta.update(provided_meta)
        
        # TODO: Use PyPDF2 or ebooklib to extract metadata from file itself
        # For now, rely on sidecar or filename
        
        return meta
    
    async def _create_document_entry(self, file_path: Path, metadata: Dict) -> str:
        """Create entry in memory_documents table"""
        
        # Generate document ID
        file_hash = hashlib.sha256(str(file_path).encode()).hexdigest()[:16]
        document_id = f"book_{file_hash}"
        
        db = await get_db()
        
        # Check if already exists
        existing = await db.fetch_one(
            "SELECT document_id FROM memory_documents WHERE document_id = ?",
            (document_id,)
        )
        
        if existing:
            # Update metadata instead
            await db.execute(
                """UPDATE memory_documents 
                   SET metadata = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE document_id = ?""",
                (json.dumps(metadata), document_id)
            )
        else:
            # Insert new
            await db.execute(
                """INSERT INTO memory_documents 
                   (document_id, title, author, source_type, file_path, 
                    trust_score, metadata, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (
                    document_id,
                    metadata.get('title', 'Unknown'),
                    metadata.get('author', 'Unknown'),
                    'book',
                    str(file_path),
                    0.5,  # Initial trust score
                    json.dumps(metadata)
                )
            )
        
        await db.commit()
        
        return document_id
    
    async def _extract_text(self, file_path: Path) -> str:
        """Extract text from PDF or EPUB"""
        
        # TODO: Implement actual extraction
        # For PDFs: Use PyPDF2, pdfminer, or pypdf
        # For EPUBs: Use ebooklib
        # For OCR fallback: Use pytesseract
        
        # Placeholder
        return f"[Text content from {file_path.name}]"
    
    async def _detect_chapters(self, content: str, metadata: Dict) -> List[Dict]:
        """Detect chapter/section boundaries"""
        
        # TODO: Implement chapter detection
        # Look for patterns like "Chapter N", "CHAPTER N", numbered sections
        # Use NLP to detect topic shifts
        
        # Placeholder: Create single chapter
        return [{
            "chapter_num": 1,
            "title": "Full Content",
            "content": content,
            "start_pos": 0,
            "end_pos": len(content)
        }]
    
    async def _create_chunks(self, chapters: List[Dict], document_id: str) -> List[Dict]:
        """Create intelligent chunks from chapters"""
        
        chunks = []
        chunk_size = 1024  # tokens
        overlap = 128
        
        for chapter in chapters:
            chapter_text = chapter["content"]
            
            # Simple chunking by character count (TODO: use token-aware chunking)
            for i in range(0, len(chapter_text), chunk_size - overlap):
                chunk_text = chapter_text[i:i + chunk_size]
                
                chunk = {
                    "document_id": document_id,
                    "chapter_num": chapter["chapter_num"],
                    "chunk_index": len(chunks),
                    "content": chunk_text,
                    "metadata": {
                        "chapter_title": chapter["title"],
                        "start_char": i,
                        "end_char": i + len(chunk_text)
                    }
                }
                
                chunks.append(chunk)
        
        # Store chunks in database
        db = await get_db()
        for chunk in chunks:
            await db.execute(
                """INSERT INTO memory_document_chunks
                   (document_id, chunk_index, content, metadata, created_at)
                   VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (
                    chunk["document_id"],
                    chunk["chunk_index"],
                    chunk["content"],
                    json.dumps(chunk["metadata"])
                )
            )
        await db.commit()
        
        return chunks
    
    async def _generate_insights(self, chapters: List[Dict], document_id: str, metadata: Dict) -> List[Dict]:
        """Generate summaries and flashcards"""
        
        insights = []
        
        # TODO: Use LLM to generate:
        # 1. Chapter summaries
        # 2. Key concepts
        # 3. Flashcards
        # 4. Connections to existing knowledge
        
        # Placeholder insight
        summary_insight = {
            "document_id": document_id,
            "insight_type": "summary",
            "content": f"Summary of {metadata.get('title', 'book')} with {len(chapters)} chapters",
            "confidence": 0.7
        }
        
        insights.append(summary_insight)
        
        # Store in memory_insights
        db = await get_db()
        for insight in insights:
            await db.execute(
                """INSERT INTO memory_insights
                   (document_id, insight_type, content, confidence, created_at)
                   VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (
                    insight["document_id"],
                    insight["insight_type"],
                    insight["content"],
                    insight["confidence"]
                )
            )
        await db.commit()
        
        return insights
    
    async def _trigger_embedding_pipeline(self, document_id: str, chunks: List[Dict]):
        """Trigger ML/DL pipeline for embeddings"""
        
        await self.event_bus.publish(Event(
            event_type="ml.embedding.requested",
            source=self.component_id,
            payload={
                "document_id": document_id,
                "chunk_count": len(chunks),
                "priority": "high"
            }
        ))
    
    async def _queue_verification(self, document_id: str):
        """Queue verification job for trust scoring"""
        
        await self.event_bus.publish(Event(
            event_type="verification.book.requested",
            source=self.component_id,
            payload={
                "document_id": document_id,
                "verification_type": "comprehension_qa"
            }
        ))


# Singleton instance
_book_agent = None

def get_book_ingestion_agent() -> BookIngestionAgent:
    global _book_agent
    if _book_agent is None:
        _book_agent = BookIngestionAgent()
    return _book_agent
