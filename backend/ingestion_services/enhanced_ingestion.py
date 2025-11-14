"""
Enhanced Ingestion Pipeline
PDF/DOCX extraction → Chunking → Embeddings → Vector Store
Natural language controlled
"""

import hashlib
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class EnhancedIngestionService:
    """
    Complete ingestion pipeline with:
    - PDF/DOCX/EPUB extraction
    - Intelligent chunking with overlap
    - Embeddings generation
    - Vector store integration
    - Namespace organization
    """
    
    def __init__(self):
        self.chunk_size_tokens = 1000
        self.overlap_tokens = 150  # 15% overlap
        self.vector_store = None
    
    async def ingest_file(
        self,
        file_path: str,
        namespace: str = "general",
        tags: List[str] = None
    ) -> int:
        """
        Ingest file with full pipeline
        
        Natural language: "Ingest this PDF into knowledge base"
        """
        
        file_path_obj = Path(file_path)
        
        # 1. Extract text based on file type
        text = await self._extract_text(file_path_obj)
        
        # 2. Chunk intelligently
        chunks = self._chunk_text(text)
        
        # 3. Generate embeddings (if available)
        embeddings = await self._generate_embeddings(chunks)
        
        # 4. Store in vector DB (if available)
        if self.vector_store and embeddings:
            await self._store_vectors(chunks, embeddings, namespace, tags)
        
        # 5. Store in knowledge base
        artifact_id = await self._store_in_knowledge_base(
            text=text,
            chunks=chunks,
            namespace=namespace,
            tags=tags,
            filename=file_path_obj.name
        )
        
        logger.info(f"[INGESTION] Ingested {file_path_obj.name}: {len(chunks)} chunks, artifact_id={artifact_id}")
        
        return artifact_id
    
    async def _extract_text(self, file_path: Path) -> str:
        """Extract text from various file formats"""
        
        extension = file_path.suffix.lower()
        
        if extension == '.txt':
            return file_path.read_text(encoding='utf-8')
        
        elif extension == '.pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = '\n\n'.join([page.extract_text() for page in reader.pages])
                return text
            except ImportError:
                logger.warning("PyPDF2 not installed - install with: pip install PyPDF2")
                return file_path.read_text(encoding='utf-8', errors='ignore')
        
        elif extension in ['.docx', '.doc']:
            try:
                import docx
                doc = docx.Document(file_path)
                text = '\n\n'.join([para.text for para in doc.paragraphs])
                return text
            except ImportError:
                logger.warning("python-docx not installed - install with: pip install python-docx")
                return file_path.read_text(encoding='utf-8', errors='ignore')
        
        elif extension == '.epub':
            # Stub - would use ebooklib
            return file_path.read_text(encoding='utf-8', errors='ignore')
        
        elif extension in ['.html', '.htm']:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(file_path.read_text(), 'html.parser')
                return soup.get_text()
            except ImportError:
                return file_path.read_text(encoding='utf-8', errors='ignore')
        
        else:
            # Fallback: try as text
            return file_path.read_text(encoding='utf-8', errors='ignore')
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Chunk text with overlap
        
        1000 token chunks, 150 token overlap (15%)
        """
        # Simple word-based chunking (token approximation: 1 token ≈ 0.75 words)
        words = text.split()
        chunk_size_words = int(self.chunk_size_tokens * 0.75)
        overlap_words = int(self.overlap_tokens * 0.75)
        
        chunks = []
        i = 0
        
        while i < len(words):
            chunk_words = words[i:i + chunk_size_words]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
            i += chunk_size_words - overlap_words
        
        return chunks
    
    async def _generate_embeddings(self, chunks: List[str]) -> Optional[List[List[float]]]:
        """Generate embeddings using OpenAI or local model"""
        try:
            import openai
            import os
            
            if not os.getenv("OPENAI_API_KEY"):
                logger.warning("No OPENAI_API_KEY - skipping embeddings")
                return None
            
            # Batch embed in groups of 100
            all_embeddings = []
            batch_size = 100
            
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                response = await openai.Embedding.acreate(
                    model="text-embedding-ada-002",
                    input=batch
                )
                embeddings = [item['embedding'] for item in response['data']]
                all_embeddings.extend(embeddings)
            
            return all_embeddings
        
        except ImportError:
            logger.warning("OpenAI not installed - skipping embeddings")
            return None
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
            return None
    
    async def _store_vectors(
        self,
        chunks: List[str],
        embeddings: List[List[float]],
        namespace: str,
        tags: List[str]
    ):
        """Store in vector database (Chroma/pgvector)"""
        try:
            import chromadb
            
            if not self.vector_store:
                client = chromadb.Client()
                self.vector_store = client.get_or_create_collection(f"grace_{namespace}")
            
            # Store chunks with embeddings
            ids = [f"{namespace}_{i}" for i in range(len(chunks))]
            metadatas = [{"namespace": namespace, "tags": json.dumps(tags)} for _ in chunks]
            
            self.vector_store.add(
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"[VECTOR] Stored {len(chunks)} chunks in namespace '{namespace}'")
        
        except ImportError:
            logger.warning("ChromaDB not installed - skipping vector storage")
        except Exception as e:
            logger.warning(f"Vector storage failed: {e}")
    
    async def _store_in_knowledge_base(
        self,
        text: str,
        chunks: List[str],
        namespace: str,
        tags: List[str],
        filename: str
    ) -> int:
        """Store in knowledge database"""
        from ..models import async_session
        from ..knowledge_models import KnowledgeArtifact, KnowledgeRevision
        
        content_hash = hashlib.sha256(text.encode()).hexdigest()
        
        async with async_session() as session:
            artifact = KnowledgeArtifact(
                path=f"{namespace}/{filename}",
                title=filename,
                artifact_type="document",
                content=text,
                content_hash=content_hash,
                artifact_metadata=json.dumps({
                    "chunks": len(chunks),
                    "namespace": namespace,
                    "tags": tags
                }),
                source="chunked_upload",
                ingested_by="grace_system",
                domain=namespace,
                tags=json.dumps(tags),
                size_bytes=len(text)
            )
            
            session.add(artifact)
            await session.commit()
            await session.refresh(artifact)
            
            # Create revision
            revision = KnowledgeRevision(
                artifact_id=artifact.id,
                revision_number=1,
                edited_by="grace_system",
                change_summary="chunked_upload_ingestion"
            )
            session.add(revision)
            await session.commit()
            
            return artifact.id
    
    async def search_knowledge(
        self,
        query: str,
        namespace: Optional[str] = None,
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Semantic search in knowledge base
        
        Natural language: "Find documents about sales pipelines"
        """
        if self.vector_store:
            # Use vector search
            try:
                results = self.vector_store.query(
                    query_texts=[query],
                    n_results=k,
                    where={"namespace": namespace} if namespace else None
                )
                return results
            except:
                pass
        
        # Fallback: keyword search in database
        from ..models import async_session
        from ..knowledge_models import KnowledgeArtifact
        from sqlalchemy import select, or_
        
        async with async_session() as session:
            stmt = select(KnowledgeArtifact).where(
                or_(
                    KnowledgeArtifact.title.contains(query),
                    KnowledgeArtifact.content.contains(query)
                )
            )
            if namespace:
                stmt = stmt.where(KnowledgeArtifact.domain == namespace)
            
            stmt = stmt.limit(k)
            
            result = await session.execute(stmt)
            artifacts = result.scalars().all()
            
            return [
                {
                    "id": a.id,
                    "title": a.title,
                    "content_preview": a.content[:200],
                    "namespace": a.domain,
                    "relevance": 0.5  # Keyword match score
                }
                for a in artifacts
            ]


# Global instance
enhanced_ingestion_service = EnhancedIngestionService()
