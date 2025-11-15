"""
Embedding Generation Service

Generates vector embeddings from text using:
- OpenAI (text-embedding-ada-002, text-embedding-3-small/large)
- HuggingFace models
- Local sentence transformers

Features:
- Batch processing for efficiency
- Token counting and cost tracking
- Caching and deduplication
- Async generation
"""

import asyncio
import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import tiktoken

from backend.models.vector_models import VectorEmbedding, EmbeddingBatch
from backend.models.base_models import async_session
from backend.logging_utils import log_event
from sqlalchemy import select


class EmbeddingModel:
    """Embedding model configuration"""
    
    # OpenAI models
    ADA_002 = "text-embedding-ada-002"
    EMBED_3_SMALL = "text-embedding-3-small"
    EMBED_3_LARGE = "text-embedding-3-large"
    
    # Dimensions
    DIMENSIONS = {
        "text-embedding-ada-002": 1536,
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072
    }
    
    # Pricing (per 1M tokens)
    PRICING = {
        "text-embedding-ada-002": 0.0001,
        "text-embedding-3-small": 0.00002,
        "text-embedding-3-large": 0.00013
    }


class EmbeddingService:
    """
    Service for generating and managing embeddings
    
    Usage:
        service = EmbeddingService()
        await service.initialize()
        
        # Single embedding
        result = await service.embed_text("Hello world")
        
        # Batch embeddings
        results = await service.embed_batch([
            {"text": "Hello", "source_id": "doc1"},
            {"text": "World", "source_id": "doc2"}
        ])
    """
    
    def __init__(
        self,
        default_model: str = EmbeddingModel.EMBED_3_SMALL,
        provider: str = "openai",
        batch_size: int = 100
    ):
        self.default_model = default_model
        self.provider = provider
        self.batch_size = batch_size
        
        self.openai_client = None
        self.tokenizer = None
        
        # Cache for deduplication
        self.embedding_cache: Dict[str, str] = {}  # text_hash -> embedding_id
        
        print(f"[EMBEDDING SERVICE] Initialized (model: {default_model}, provider: {provider})")
    
    async def initialize(self):
        """Initialize embedding providers"""
        if self.provider == "openai":
            try:
                import openai
                import os
                
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    print("[EMBEDDING SERVICE] Warning: OPENAI_API_KEY not set")
                    return
                
                self.openai_client = openai.AsyncOpenAI(api_key=api_key)
                self.tokenizer = tiktoken.encoding_for_model(self.default_model)
                
                print("[EMBEDDING SERVICE] OpenAI client initialized")
                
            except ImportError:
                print("[EMBEDDING SERVICE] Warning: openai package not installed")
            except Exception as e:
                print(f"[EMBEDDING SERVICE] OpenAI initialization error: {e}")
        
        # Load embedding cache from database
        await self._load_cache()
    
    async def _load_cache(self, limit: int = 10000):
        """Load recent embeddings into cache for deduplication"""
        async with async_session() as session:
            result = await session.execute(
                select(VectorEmbedding.text_hash, VectorEmbedding.embedding_id)
                .where(VectorEmbedding.text_hash.isnot(None))
                .order_by(VectorEmbedding.created_at.desc())
                .limit(limit)
            )
            
            for text_hash, embedding_id in result:
                if text_hash:
                    self.embedding_cache[text_hash] = embedding_id
        
        print(f"[EMBEDDING SERVICE] Loaded {len(self.embedding_cache)} embeddings into cache")
    
    def _hash_text(self, text: str) -> str:
        """Generate hash of text for deduplication"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Rough estimate: ~4 chars per token
            return len(text) // 4
    
    def _calculate_cost(self, token_count: int, model: str) -> float:
        """Calculate embedding cost"""
        price_per_million = EmbeddingModel.PRICING.get(model, 0.0001)
        return (token_count / 1_000_000) * price_per_million
    
    async def embed_text(
        self,
        text: str,
        source_type: str = "document",
        source_id: str = None,
        model: Optional[str] = None,
        metadata: Optional[Dict] = None,
        skip_cache: bool = False
    ) -> Dict[str, Any]:
        """
        Generate embedding for single text
        
        Args:
            text: Text to embed
            source_type: Type of source (document, recording, etc.)
            source_id: Source identifier
            model: Embedding model to use
            metadata: Additional metadata
            skip_cache: Force regeneration even if cached
            
        Returns:
            {
                "embedding_id": str,
                "vector": List[float],
                "dimensions": int,
                "token_count": int,
                "cost": float,
                "cached": bool
            }
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        model = model or self.default_model
        embedding_id = f"emb_{source_type}_{datetime.now(timezone.utc).timestamp()}"
        
        # Check cache
        text_hash = self._hash_text(text)
        if not skip_cache and text_hash in self.embedding_cache:
            cached_id = self.embedding_cache[text_hash]
            
            # Load cached embedding
            async with async_session() as session:
                result = await session.execute(
                    select(VectorEmbedding)
                    .where(VectorEmbedding.embedding_id == cached_id)
                )
                cached_emb = result.scalar_one_or_none()
                
                if cached_emb:
                    print(f"[EMBEDDING SERVICE] Cache hit for text hash {text_hash[:8]}")
                    return {
                        "embedding_id": cached_emb.embedding_id,
                        "vector": cached_emb.embedding_vector,
                        "dimensions": cached_emb.vector_dimensions,
                        "token_count": cached_emb.token_count,
                        "cost": 0.0,  # No cost for cached
                        "cached": True
                    }
        
        # Count tokens
        token_count = self._count_tokens(text)
        cost = self._calculate_cost(token_count, model)
        
        # Generate embedding
        vector = await self._generate_embedding(text, model)
        dimensions = len(vector)
        
        # Store in database
        async with async_session() as session:
            embedding = VectorEmbedding(
                embedding_id=embedding_id,
                embedding_vector=vector,
                vector_dimensions=dimensions,
                source_type=source_type,
                source_id=source_id or embedding_id,
                text_content=text[:10000],  # Truncate very long text
                text_hash=text_hash,
                embedding_model=model,
                embedding_provider=self.provider,
                embedding_cost=cost,
                token_count=token_count,
                embedding_metadata=metadata,
                indexed=False
            )
            session.add(embedding)
            await session.commit()
        
        # Update cache
        self.embedding_cache[text_hash] = embedding_id
        
        log_event(
            action="embedding.created",
            actor="embedding_service",
            resource=embedding_id,
            outcome="success",
            payload={
                "source_type": source_type,
                "token_count": token_count,
                "cost": cost,
                "model": model
            }
        )
        
        return {
            "embedding_id": embedding_id,
            "vector": vector,
            "dimensions": dimensions,
            "token_count": token_count,
            "cost": cost,
            "cached": False
        }
    
    async def embed_batch(
        self,
        items: List[Dict[str, Any]],
        model: Optional[str] = None,
        source_type: str = "document"
    ) -> Dict[str, Any]:
        """
        Generate embeddings for batch of texts
        
        Args:
            items: List of {
                "text": str,
                "source_id": str,
                "metadata": dict (optional)
            }
            model: Embedding model
            source_type: Source type for all items
            
        Returns:
            {
                "batch_id": str,
                "embeddings": List[Dict],
                "total_tokens": int,
                "total_cost": float,
                "cached_count": int,
                "generated_count": int
            }
        """
        model = model or self.default_model
        batch_id = f"batch_{datetime.now(timezone.utc).timestamp()}"
        
        # Create batch record
        async with async_session() as session:
            batch_record = EmbeddingBatch(
                batch_id=batch_id,
                batch_size=len(items),
                source_type=source_type,
                status="processing",
                embedding_model=model,
                embedding_provider=self.provider,
                started_at=datetime.now(timezone.utc)
            )
            session.add(batch_record)
            await session.commit()
        
        # Process items
        results = []
        total_tokens = 0
        total_cost = 0.0
        cached_count = 0
        generated_count = 0
        failed_count = 0
        embedding_ids = []
        
        # Split into batches
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            
            # Process batch
            for item in batch:
                try:
                    result = await self.embed_text(
                        text=item["text"],
                        source_type=source_type,
                        source_id=item.get("source_id"),
                        model=model,
                        metadata=item.get("metadata")
                    )
                    
                    results.append(result)
                    total_tokens += result["token_count"]
                    total_cost += result["cost"]
                    embedding_ids.append(result["embedding_id"])
                    
                    if result["cached"]:
                        cached_count += 1
                    else:
                        generated_count += 1
                        
                except Exception as e:
                    print(f"[EMBEDDING SERVICE] Error embedding item: {e}")
                    failed_count += 1
            
            # Small delay between batches to avoid rate limits
            if i + self.batch_size < len(items):
                await asyncio.sleep(0.1)
        
        # Update batch record
        async with async_session() as session:
            from sqlalchemy import update as sql_update
            
            await session.execute(
                sql_update(EmbeddingBatch)
                .where(EmbeddingBatch.batch_id == batch_id)
                .values(
                    status="completed" if failed_count == 0 else "partial",
                    embeddings_created=generated_count + cached_count,
                    embeddings_failed=failed_count,
                    completed_at=datetime.now(timezone.utc),
                    processing_time_ms=(datetime.now(timezone.utc).timestamp() * 1000),
                    total_tokens=total_tokens,
                    total_cost=total_cost,
                    embedding_ids=embedding_ids
                )
            )
            await session.commit()
        
        print(f"[EMBEDDING SERVICE] Batch {batch_id}: {generated_count} generated, {cached_count} cached, {failed_count} failed")
        
        return {
            "batch_id": batch_id,
            "embeddings": results,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "cached_count": cached_count,
            "generated_count": generated_count,
            "failed_count": failed_count
        }
    
    async def _generate_embedding(self, text: str, model: str) -> List[float]:
        """
        Generate embedding vector from text
        
        Args:
            text: Text to embed
            model: Model to use
            
        Returns:
            List of floats (embedding vector)
        """
        if self.provider == "openai":
            if not self.openai_client:
                raise RuntimeError("OpenAI client not initialized")
            
            try:
                response = await self.openai_client.embeddings.create(
                    input=text,
                    model=model
                )
                
                return response.data[0].embedding
                
            except Exception as e:
                print(f"[EMBEDDING SERVICE] OpenAI API error: {e}")
                raise
        
        elif self.provider == "huggingface":
            # Use sentence-transformers for local embeddings
            try:
                from sentence_transformers import SentenceTransformer
                
                # Load model (cached)
                if not hasattr(self, '_hf_model'):
                    self._hf_model = SentenceTransformer(model)
                
                embedding = self._hf_model.encode(text, convert_to_tensor=False)
                return embedding.tolist()
                
            except ImportError:
                raise RuntimeError("sentence-transformers not installed. Run: pip install sentence-transformers")
            except Exception as e:
                print(f"[EMBEDDING SERVICE] HuggingFace error: {e}")
                raise
        
        elif self.provider == "local":
            # Use local sentence-transformers models
            try:
                from sentence_transformers import SentenceTransformer
                
                # Default to all-MiniLM-L6-v2 (fast, 384 dimensions)
                model_name = model or "all-MiniLM-L6-v2"
                
                if not hasattr(self, '_local_model'):
                    self._local_model = SentenceTransformer(model_name)
                
                embedding = self._local_model.encode(text, convert_to_tensor=False)
                return embedding.tolist()
                
            except ImportError:
                raise RuntimeError("sentence-transformers not installed. Run: pip install sentence-transformers")
            except Exception as e:
                print(f"[EMBEDDING SERVICE] Local embedding error: {e}")
                raise
        
        else:
            raise ValueError(f"Unknown provider: {self.provider}. Supported: openai, huggingface, local")
    
    async def embed_chunks(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        source_type: str = "document",
        source_id: str = None,
        parent_id: str = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Split text into chunks and embed each
        
        Args:
            text: Full text to chunk and embed
            chunk_size: Characters per chunk
            chunk_overlap: Overlap between chunks
            source_type: Source type
            source_id: Source identifier
            parent_id: Parent document ID
            metadata: Additional metadata
            
        Returns:
            {
                "chunks": List[Dict],
                "total_chunks": int,
                "total_tokens": int,
                "total_cost": float
            }
        """
        # Split into chunks
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "index": chunk_index,
                    "start": start,
                    "end": min(end, len(text))
                })
                chunk_index += 1
            
            start = end - chunk_overlap
        
        print(f"[EMBEDDING SERVICE] Split text into {len(chunks)} chunks")
        
        # Embed chunks
        items = []
        for chunk in chunks:
            chunk_metadata = {
                **(metadata or {}),
                "chunk_index": chunk["index"],
                "chunk_start": chunk["start"],
                "chunk_end": chunk["end"],
                "parent_id": parent_id
            }
            
            items.append({
                "text": chunk["text"],
                "source_id": f"{source_id}_chunk_{chunk['index']}" if source_id else None,
                "metadata": chunk_metadata
            })
        
        # Batch embed
        result = await self.embed_batch(items, source_type=source_type)
        
        # Add chunk information to results
        for i, embedding in enumerate(result["embeddings"]):
            embedding["chunk_index"] = chunks[i]["index"]
            embedding["chunk_size"] = len(chunks[i]["text"])
        
        return {
            "chunks": result["embeddings"],
            "total_chunks": len(chunks),
            "total_tokens": result["total_tokens"],
            "total_cost": result["total_cost"],
            "batch_id": result["batch_id"]
        }
    
    async def get_embedding(self, embedding_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve embedding by ID"""
        async with async_session() as session:
            result = await session.execute(
                select(VectorEmbedding)
                .where(VectorEmbedding.embedding_id == embedding_id)
            )
            embedding = result.scalar_one_or_none()
            
            if not embedding:
                return None
            
            return {
                "embedding_id": embedding.embedding_id,
                "vector": embedding.embedding_vector,
                "text_content": embedding.text_content,
                "source_type": embedding.source_type,
                "source_id": embedding.source_id,
                "metadata": embedding.embedding_metadata,
                "created_at": embedding.created_at.isoformat() if embedding.created_at else None
            }
    
    async def delete_embedding(self, embedding_id: str) -> bool:
        """Delete embedding"""
        async with async_session() as session:
            from sqlalchemy import delete
            
            result = await session.execute(
                delete(VectorEmbedding)
                .where(VectorEmbedding.embedding_id == embedding_id)
            )
            await session.commit()
            
            # Remove from cache
            for text_hash, cached_id in list(self.embedding_cache.items()):
                if cached_id == embedding_id:
                    del self.embedding_cache[text_hash]
                    break
            
            return result.rowcount > 0


# Global instance
embedding_service = EmbeddingService()
