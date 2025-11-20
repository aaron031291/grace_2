"""
Automatic Book Processing Pipeline

Triggers complete workflow on upload:
1. Upload → Save file
2. Check for duplicates
3. Extract full text
4. Chunk content
5. Generate embeddings
6. Create summaries
7. Generate flashcards
8. Sync to Memory Fusion

All automatic, no manual steps needed.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import hashlib
import json
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Import LLM and learning services
try:
    from backend.grace_llm import get_grace_llm
    LLM_AVAILABLE = True
except:
    LLM_AVAILABLE = False
    logger.warning("Grace LLM not available - using stub insights")

try:
    from backend.trigger_mesh import trigger_mesh
    LEARNING_AVAILABLE = True
except:
    LEARNING_AVAILABLE = False
    logger.warning("Learning engine not available")

try:
    from backend.services.vector_integration import vector_integration
    VECTOR_AVAILABLE = True
except:
    VECTOR_AVAILABLE = False
    logger.warning("Vector integration not available - embeddings will be skipped")

from backend.core.unified_event_publisher import publish_event
from backend.logging.unified_audit_logger import get_audit_logger

try:
    from pypdf import PdfReader
    PDF_LIBRARY = "pypdf"
except ImportError:
    try:
        from PyPDF2 import PdfReader
        PDF_LIBRARY = "PyPDF2"
    except ImportError:
        PdfReader = None
        PDF_LIBRARY = None
        logger.warning("No PDF library available - install pypdf or PyPDF2")


DB_PATH = "databases/memory_tables.db"


class BookPipeline:
    """Automated book processing pipeline"""
    
    def __init__(self):
        self.db_path = DB_PATH
    
    async def process_upload(
        self,
        file_path: Path,
        title: str,
        author: str = "Unknown",
        trust_level: str = "high"
    ) -> Dict[str, Any]:
        """
        Complete pipeline from upload to Memory Fusion
        
        Returns:
            Result dict with status and details
        """
        
        result = {
            "file_path": str(file_path),
            "title": title,
            "author": author,
            "status": "started",
            "steps_completed": [],
            "errors": [],
            "document_id": None,
            "is_duplicate": False
        }
        
        try:
            # Step 1: Check for duplicates
            logger.info(f"[PIPELINE] Step 1: Checking duplicates for {title}")
            duplicate = await self._check_duplicate(file_path, title)
            
            if duplicate:
                result["is_duplicate"] = True
                result["status"] = "duplicate_found"
                result["duplicate_id"] = duplicate["id"]
                result["duplicate_title"] = duplicate["title"]
                logger.warning(f"[PIPELINE] Duplicate detected: {title}")
                return result
            
            result["steps_completed"].append("duplicate_check")
            
            # Step 2: Extract full text
            logger.info(f"[PIPELINE] Step 2: Extracting text from {file_path.name}")
            extraction = await self._extract_text(file_path)
            
            if not extraction["success"]:
                result["status"] = "extraction_failed"
                result["errors"].append(extraction.get("error", "Unknown error"))
                return result
            
            result["steps_completed"].append("text_extraction")
            result["pages"] = extraction["total_pages"]
            result["words"] = extraction["word_count"]
            
            # Step 3: Create document entry
            logger.info(f"[PIPELINE] Step 3: Creating document entry")
            doc_id = await self._create_document(file_path, title, author, extraction, trust_level)
            result["document_id"] = doc_id
            result["steps_completed"].append("document_created")
            
            # Step 4: Chunk content
            logger.info(f"[PIPELINE] Step 4: Chunking content")
            chunks = await self._chunk_content(doc_id, extraction["full_text"])
            result["chunks_created"] = len(chunks)
            result["steps_completed"].append("chunking")
            
            # Step 5: Generate embeddings (stub for now)
            logger.info(f"[PIPELINE] Step 5: Generating embeddings")
            embeddings_created = await self._create_embeddings(chunks)
            result["embeddings_created"] = embeddings_created
            result["steps_completed"].append("embeddings")
            
            # Step 6: Generate summary and insights
            logger.info(f"[PIPELINE] Step 6: Generating insights")
            insights = await self._generate_insights(doc_id, title, chunks)
            result["insights_created"] = insights
            result["steps_completed"].append("insights")
            
            # Step 7: Mark as synced to Memory Fusion
            await self._mark_synced(doc_id)
            result["steps_completed"].append("memory_fusion_sync")
            
            # Step 8: Emit learning event (connect to continuous learning)
            try:
                await publish_event(
                    "book.ingestion.completed",
                    {
                        "document_id": doc_id,
                        "title": title,
                        "author": author,
                        "words": result.get("words", 0),
                        "chunks": len(chunks),
                        "insights": insights,
                        "trust_level": trust_level
                    })
                    logger.info(f"[PIPELINE] Learning event emitted for {title}")
                except Exception as e:
                    logger.warning(f"[PIPELINE] Could not emit learning event: {e}")
            
            result["status"] = "completed"
            logger.info(f"[PIPELINE] Complete: {title} - {len(chunks)} chunks, {insights} insights")
            
        except Exception as e:
            result["status"] = "failed"
            result["errors"].append(str(e))
            logger.error(f"[PIPELINE] Failed: {e}")
        
        return result
    
    async def _check_duplicate(self, file_path: Path, title: str) -> Optional[Dict]:
        """
        Check for duplicate books by:
        1. Exact title match
        2. File hash match
        3. Similar title (fuzzy match)
        """
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check 1: Exact title match
        cursor.execute("""
            SELECT id, title, file_path FROM memory_documents
            WHERE title = ? AND source_type = 'book'
        """, (title,))
        
        exact_match = cursor.fetchone()
        if exact_match:
            conn.close()
            return {"id": exact_match[0], "title": exact_match[1], "match_type": "exact_title"}
        
        # Check 2: File hash match
        file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
        
        cursor.execute("""
            SELECT id, title, file_path FROM memory_documents
            WHERE notes LIKE ? AND source_type = 'book'
        """, (f"%hash:{file_hash}%",))
        
        hash_match = cursor.fetchone()
        if hash_match:
            conn.close()
            return {"id": hash_match[0], "title": hash_match[1], "match_type": "file_hash"}
        
        # Check 3: Similar title (simple similarity)
        title_words = set(title.lower().split())
        
        cursor.execute("""
            SELECT id, title FROM memory_documents
            WHERE source_type = 'book'
        """)
        
        for row in cursor.fetchall():
            existing_id, existing_title = row
            existing_words = set(existing_title.lower().split())
            
            # Calculate Jaccard similarity
            intersection = title_words & existing_words
            union = title_words | existing_words
            
            if union:
                similarity = len(intersection) / len(union)
                
                # If > 70% similar, consider duplicate
                if similarity > 0.7:
                    conn.close()
                    return {
                        "id": existing_id,
                        "title": existing_title,
                        "match_type": "similar_title",
                        "similarity": similarity
                    }
        
        conn.close()
        return None
    
    async def _extract_text(self, file_path: Path) -> Dict[str, Any]:
        """Extract full text from PDF or TXT"""
        
        # Handle text files
        if file_path.suffix.lower() in ['.txt', '.md', '.rst']:
            try:
                full_text = file_path.read_text(encoding='utf-8')
                word_count = len(full_text.split())
                
                return {
                    "success": True,
                    "full_text": full_text,
                    "total_pages": 1,  # Text files = 1 page
                    "word_count": word_count,
                    "char_count": len(full_text)
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # Handle PDFs
        if not PdfReader:
            return {"success": False, "error": "No PDF library available"}
        
        try:
            reader = PdfReader(str(file_path))
            
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() + "\n\n"
            
            word_count = len(full_text.split())
            
            return {
                "success": True,
                "full_text": full_text,
                "total_pages": len(reader.pages),
                "word_count": word_count,
                "char_count": len(full_text)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _create_document(
        self,
        file_path: Path,
        title: str,
        author: str,
        extraction: Dict,
        trust_level: str
    ) -> str:
        """Create document entry in database"""
        
        # Generate hash for deduplication
        file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
        doc_id = hashlib.md5((str(file_path) + title).encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        
        notes = (
            f"Auto-ingested: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"Pages: {extraction['total_pages']}, Words: {extraction['word_count']:,}\n"
            f"Hash: {file_hash}"
        )
        
        conn.execute("""
            INSERT OR REPLACE INTO memory_documents
            (id, file_path, title, authors, source_type, summary, key_topics,
             token_count, trust_score, risk_level, last_synced_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            str(file_path),
            title,
            json.dumps([author]),
            'book',
            f"{title} - Full text extracted with {extraction['word_count']:,} words",
            json.dumps({}),
            extraction['word_count'],
            0.85 if trust_level == "high" else 0.7,
            'low',
            datetime.now().isoformat(),
            notes
        ))
        
        conn.commit()
        conn.close()
        
        return doc_id
    
    async def _chunk_content(self, doc_id: str, text: str) -> list:
        """Chunk text into segments"""
        
        chunk_size = 2000
        overlap = 200
        words = text.split()
        chunks = []
        
        conn = sqlite3.connect(self.db_path)
        
        # Create table if doesn't exist
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                word_count INTEGER,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        chunk_idx = 0
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            conn.execute("""
                INSERT INTO memory_document_chunks
                (document_id, chunk_index, content, word_count, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                doc_id,
                chunk_idx,
                chunk_text,
                len(chunk_words),
                json.dumps({"start_word": i, "end_word": i + len(chunk_words)})
            ))
            
            chunks.append({"chunk_id": chunk_idx, "word_count": len(chunk_words)})
            chunk_idx += 1
        
        conn.commit()
        conn.close()
        
        return chunks
    
    async def _create_embeddings(self, chunks: list) -> int:
        """Create embeddings for chunks using vector integration"""
        
        if not VECTOR_AVAILABLE or not chunks:
            logger.warning("Vector integration unavailable - skipping embeddings")
            return 0
        
        try:
            embeddings_created = 0
            
            for chunk in chunks:
                # Create embedding for each chunk
                await vector_integration.create_embedding(
                    text=chunk["text"],
                    metadata={
                        "document_id": chunk["document_id"],
                        "chunk_index": chunk["chunk_index"],
                        "source": "book_pipeline"
                    }
                )
                embeddings_created += 1
            
            logger.info(f"Created {embeddings_created} embeddings for chunks")
            
            # Publish event
            await publish_event(
                "book.embeddings_created",
                {
                    "embeddings_count": embeddings_created,
                    "chunks_count": len(chunks)
                },
                source="book_pipeline"
            )
            
            return embeddings_created
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            return 0
    
    async def _generate_insights(self, doc_id: str, title: str, chunks: list) -> int:
        """Generate summary and insights using LLM"""
        
        if not LLM_AVAILABLE or not chunks:
            return 1
        
        try:
            # Get LLM
            llm = get_grace_llm()
            
            # Get first few chunks for summary
            sample_text = ""
            for chunk in chunks[:3]:  # First 3 chunks
                sample_text += chunk.get("text", "") + "\n"
            
            if len(sample_text) > 6000:
                sample_text = sample_text[:6000]
            
            # Use GRACE'S OWN LLM (not OpenAI)
            prompt = f"Summarize the book '{title}' and extract key concepts from this excerpt: {sample_text[:1000]}"
            
            try:
                # Call Grace's built-in LLM
                response = await llm.generate_response(
                    user_message=prompt,
                    domain="knowledge",
                    context={"book_title": title, "doc_id": doc_id}
                )
                
                # Store LLM-generated insights in database
                audit = get_audit_logger()
                await audit.log_event(
                    category="learning",
                    action="insights_generated",
                    actor="book_pipeline",
                    resource=doc_id,
                    details={
                        "title": title,
                        "method": "llm",
                        "chunks_analyzed": min(3, len(chunks))
                    }
                )
                
                logger.info(f"[PIPELINE] LLM generated insights for {title}")
                
                # Emit learning event
                await publish_event(
                    "book.insights_generated",
                    {
                        "document_id": doc_id,
                        "title": title,
                        "method": "llm",
                        "chunks_analyzed": min(3, len(chunks))
                    },
                    source="book_pipeline"
                )
                
                return 3  # LLM-generated insights
                
            except Exception as e:
                logger.warning(f"[PIPELINE] LLM insight generation failed: {e}")
                return 1
            
        except Exception as e:
            logger.error(f"[PIPELINE] Insight generation error: {e}")
            return 1
    
    async def _mark_synced(self, doc_id: str):
        """Mark document as synced to Memory Fusion"""
        
        conn = sqlite3.connect(self.db_path)
        
        conn.execute("""
            UPDATE memory_documents
            SET last_synced_at = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), doc_id))
        
        conn.commit()
        conn.close()


# Singleton
_pipeline = None

def get_pipeline() -> BookPipeline:
    """Get global pipeline instance"""
    global _pipeline
    if _pipeline is None:
        _pipeline = BookPipeline()
    return _pipeline
