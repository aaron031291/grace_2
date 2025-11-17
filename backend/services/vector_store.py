"""
Vector Store Abstraction Layer

Supports multiple vector database backends:
- FAISS (local, in-memory)
- Chroma (local, persistent)
- Pinecone (cloud)
- Weaviate (cloud/self-hosted)

Provides unified interface for:
- Indexing vectors
- Similarity search
- Metadata filtering
- Batch operations
"""

import asyncio
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
from datetime import datetime, timezone
import os

try:
    import faiss
except ImportError:
    faiss = None

from backend.models.vector_models import VectorEmbedding, VectorIndex, VectorSearchQuery
from backend.models.base_models import async_session
from backend.logging_utils import log_event
from sqlalchemy import select, update as sql_update


class VectorStoreBackend(ABC):
    """Abstract base class for vector store backends"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]):
        """Initialize the vector store"""
        pass
    
    @abstractmethod
    async def add_vectors(
        self,
        vectors: List[List[float]],
        ids: List[str],
        metadata: List[Dict[str, Any]]
    ) -> bool:
        """Add vectors to the store"""
        pass
    
    @abstractmethod
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        pass
    
    @abstractmethod
    async def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors by ID"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get store statistics"""
        pass


class FAISSBackend(VectorStoreBackend):
    """FAISS in-memory vector store (good for local dev/testing)"""
    
    def __init__(self):
        self.index = None
        self.id_map = {}  # index_id -> embedding_id
        self.metadata_store = {}  # embedding_id -> metadata
        self.dimensions = None
    
    async def initialize(self, config: Dict[str, Any]):
        """Initialize FAISS index"""
        try:
            import faiss
            
            self.dimensions = config.get("dimensions", 1536)
            
            # Use IndexFlatL2 for exact search (cosine similarity)
            self.index = faiss.IndexFlatL2(self.dimensions)
            
            print(f"[FAISS] Initialized with {self.dimensions} dimensions")
            return True
            
        except ImportError:
            print("[FAISS] faiss-cpu package not installed")
            return False
    
    async def add_vectors(
        self,
        vectors: List[List[float]],
        ids: List[str],
        metadata: List[Dict[str, Any]]
    ) -> bool:
        """Add vectors to FAISS index"""
        if not self.index:
            return False
        
        # Convert to numpy array
        vectors_np = np.array(vectors, dtype=np.float32)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(vectors_np)
        
        # Add to index
        start_id = self.index.ntotal
        self.index.add(vectors_np)
        
        # Map IDs
        for i, emb_id in enumerate(ids):
            idx = start_id + i
            self.id_map[idx] = emb_id
            self.metadata_store[emb_id] = metadata[i] if i < len(metadata) else {}
        
        print(f"[FAISS] Added {len(vectors)} vectors (total: {self.index.ntotal})")
        return True
    
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search FAISS index"""
        if not self.index or self.index.ntotal == 0:
            return []
        
        # Convert query to numpy
        query_np = np.array([query_vector], dtype=np.float32)
        faiss.normalize_L2(query_np)
        
        # Search
        distances, indices = self.index.search(query_np, min(top_k, self.index.ntotal))
        
        # Convert results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:  # FAISS returns -1 for missing results
                continue
            
            emb_id = self.id_map.get(int(idx))
            if not emb_id:
                continue
            
            metadata = self.metadata_store.get(emb_id, {})
            
            # Apply filters if provided
            if filters:
                match = True
                for key, value in filters.items():
                    if metadata.get(key) != value:
                        match = False
                        break
                if not match:
                    continue
            
            # Convert L2 distance to similarity score
            # Lower distance = higher similarity
            similarity = 1.0 / (1.0 + float(distances[0][i]))
            
            results.append({
                "embedding_id": emb_id,
                "score": similarity,
                "metadata": metadata
            })
        
        return results
    
    async def delete_vectors(self, ids: List[str]) -> bool:
        """Delete not supported in FAISS (rebuild required)"""
        print("[FAISS] Delete not supported - rebuild index to remove vectors")
        return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get FAISS stats"""
        return {
            "backend": "faiss",
            "total_vectors": self.index.ntotal if self.index else 0,
            "dimensions": self.dimensions,
            "index_type": "IndexFlatL2"
        }


class ChromaBackend(VectorStoreBackend):
    """ChromaDB vector store (good for local persistent storage)"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.collection_name = "grace_embeddings"
    
    async def initialize(self, config: Dict[str, Any]):
        """Initialize Chroma"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            persist_directory = config.get("persist_directory", "./chroma_db")
            self.collection_name = config.get("collection_name", "grace_embeddings")
            
            # Create client
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_directory
            ))
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            print(f"[CHROMA] Initialized collection '{self.collection_name}' at {persist_directory}")
            return True
            
        except ImportError:
            print("[CHROMA] chromadb package not installed")
            return False
    
    async def add_vectors(
        self,
        vectors: List[List[float]],
        ids: List[str],
        metadata: List[Dict[str, Any]]
    ) -> bool:
        """Add vectors to Chroma"""
        if not self.collection:
            return False
        
        try:
            self.collection.add(
                embeddings=vectors,
                ids=ids,
                metadatas=metadata if metadata else [{}] * len(ids)
            )
            
            print(f"[CHROMA] Added {len(vectors)} vectors")
            return True
            
        except Exception as e:
            print(f"[CHROMA] Error adding vectors: {e}")
            return False
    
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search Chroma"""
        if not self.collection:
            return []
        
        try:
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                where=filters  # Chroma native filtering
            )
            
            # Convert to standard format
            output = []
            for i in range(len(results['ids'][0])):
                output.append({
                    "embedding_id": results['ids'][0][i],
                    "score": 1.0 - results['distances'][0][i],  # Convert distance to similarity
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {}
                })
            
            return output
            
        except Exception as e:
            print(f"[CHROMA] Search error: {e}")
            return []
    
    async def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors from Chroma"""
        if not self.collection:
            return False
        
        try:
            self.collection.delete(ids=ids)
            print(f"[CHROMA] Deleted {len(ids)} vectors")
            return True
        except Exception as e:
            print(f"[CHROMA] Delete error: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Chroma stats"""
        if not self.collection:
            return {}
        
        count = self.collection.count()
        return {
            "backend": "chroma",
            "total_vectors": count,
            "collection_name": self.collection_name
        }


class VectorStore:
    """
    Unified vector store interface
    
    Usage:
        store = VectorStore(backend="chroma")
        await store.initialize()
        
        # Index vectors
        await store.index_embeddings([embedding_id1, embedding_id2])
        
        # Search
        results = await store.search(query_text="find similar documents")
    """
    
    def __init__(
        self,
        backend: str = "faiss",
        config: Optional[Dict] = None
    ):
        self.backend_type = backend
        self.config = config or {}
        self.backend: Optional[VectorStoreBackend] = None
        
        # Backend selection
        if backend == "faiss":
            self.backend = FAISSBackend()
        elif backend == "chroma":
            self.backend = ChromaBackend()
        else:
            raise ValueError(f"Unsupported backend: {backend}")
        
        self.index_record = None
    
    async def initialize(self):
        """Initialize vector store and create index record"""
        success = await self.backend.initialize(self.config)
        
        if not success:
            raise RuntimeError(f"Failed to initialize {self.backend_type} backend")
        
        # Create or load index record
        index_id = f"idx_{self.backend_type}_{datetime.now(timezone.utc).timestamp()}"
        
        async with async_session() as session:
            self.index_record = VectorIndex(
                index_id=index_id,
                index_name=f"grace_{self.backend_type}_index",
                vector_dimensions=self.config.get("dimensions", 1536),
                backend_type=self.backend_type,
                backend_config=self.config,
                status="active"
            )
            session.add(self.index_record)
            await session.commit()
        
        print(f"[VECTOR STORE] Initialized {self.backend_type} backend")
    
    async def add_text(
        self,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
        source_type: str = "document",
        source_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convenience method: Embed text and immediately index it
        
        This is a thin wrapper that:
        1. Calls embedding_service.embed_text()
        2. Immediately calls index_embeddings() with the embedding_id
        3. Returns metadata/stats
        
        Args:
            content: Text content to embed and index
            source: Source description
            metadata: Additional metadata
            source_type: Type of source (document, recording, etc.)
            source_id: Optional source identifier
            
        Returns:
            {
                "embedding_id": str,
                "indexed": bool,
                "vector_count": int,
                "source": str
            }
        """
        from backend.services.embedding_service import embedding_service
        
        # Step 1: Generate embedding
        embedding_result = await embedding_service.embed_text(
            text=content,
            source_type=source_type,
            source_id=source_id,
            metadata=metadata
        )
        
        embedding_id = embedding_result["embedding_id"]
        
        # Step 2: Immediately index it
        index_result = await self.index_embeddings([embedding_id])
        
        # Step 3: Return metadata/stats
        return {
            "embedding_id": embedding_id,
            "indexed": index_result["indexed_count"] > 0,
            "vector_count": index_result["total_vectors"],
            "source": source,
            "dimensions": embedding_result["dimensions"]
        }
    
    async def count(self) -> int:
        """
        Get count of vectors in the store
        
        Returns:
            Total number of vectors indexed
        """
        stats = await self.backend.get_stats()
        return stats.get("total_vectors", 0)
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """
        List available collections/indexes
        
        Returns:
            List of collection metadata
        """
        # Get all index records from database
        async with async_session() as session:
            result = await session.execute(
                select(VectorIndex)
                .where(VectorIndex.status == "active")
                .order_by(VectorIndex.created_at.desc())
            )
            indexes = result.scalars().all()
        
        collections = []
        for idx in indexes:
            collections.append({
                "index_id": idx.index_id,
                "index_name": idx.index_name,
                "backend_type": idx.backend_type,
                "vector_dimensions": idx.vector_dimensions,
                "total_vectors": idx.total_vectors,
                "created_at": idx.created_at.isoformat() if idx.created_at else None,
                "last_updated_at": idx.last_updated_at.isoformat() if idx.last_updated_at else None
            })
        
        # Add current backend info
        if self.backend:
            backend_stats = await self.backend.get_stats()
            collections.append({
                "index_id": "current",
                "index_name": f"grace_{self.backend_type}_current",
                "backend_type": self.backend_type,
                "vector_dimensions": self.config.get("dimensions", 1536),
                "total_vectors": backend_stats.get("total_vectors", 0),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "active"
            })
        
        return collections
    
    async def index_embeddings(self, embedding_ids: List[str]) -> Dict[str, Any]:
        """
        Index embeddings from database into vector store
        
        Args:
            embedding_ids: List of embedding IDs to index
            
        Returns:
            {
                "indexed_count": int,
                "failed_count": int,
                "total_vectors": int
            }
        """
        # Load embeddings from database
        async with async_session() as session:
            result = await session.execute(
                select(VectorEmbedding)
                .where(VectorEmbedding.embedding_id.in_(embedding_ids))
            )
            embeddings = result.scalars().all()
        
        if not embeddings:
            return {"indexed_count": 0, "failed_count": 0, "total_vectors": 0}
        
        # Prepare vectors
        vectors = []
        ids = []
        metadatas = []
        
        for emb in embeddings:
            vectors.append(emb.embedding_vector)
            ids.append(emb.embedding_id)
            metadatas.append({
                "source_type": emb.source_type,
                "source_id": emb.source_id,
                "created_at": emb.created_at.isoformat() if emb.created_at else None,
                **(emb.embedding_metadata or {})
            })
        
        # Index in backend
        success = await self.backend.add_vectors(vectors, ids, metadatas)
        
        if success:
            # Mark as indexed in database
            async with async_session() as session:
                await session.execute(
                    sql_update(VectorEmbedding)
                    .where(VectorEmbedding.embedding_id.in_(embedding_ids))
                    .values(indexed=True, index_version=self.index_record.index_id if self.index_record else None)
                )
                await session.commit()
            
            indexed_count = len(embeddings)
        else:
            indexed_count = 0
        
        # Update index stats
        stats = await self.backend.get_stats()
        
        async with async_session() as session:
            if self.index_record:
                await session.execute(
                    sql_update(VectorIndex)
                    .where(VectorIndex.index_id == self.index_record.index_id)
                    .values(
                        total_vectors=stats.get("total_vectors", 0),
                        last_updated_at=datetime.now(timezone.utc)
                    )
                )
                await session.commit()
        
        return {
            "indexed_count": indexed_count,
            "failed_count": len(embeddings) - indexed_count,
            "total_vectors": stats.get("total_vectors", 0)
        }
    
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict] = None,
        similarity_threshold: float = 0.0,
        requested_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results
            filters: Metadata filters
            similarity_threshold: Minimum similarity score
            requested_by: Who requested the search
            
        Returns:
            {
                "query_id": str,
                "results": List[Dict],
                "execution_time_ms": float
            }
        """
        start_time = datetime.now(timezone.utc)
        query_id = f"query_{start_time.timestamp()}"
        
        # Search backend
        results = await self.backend.search(query_vector, top_k, filters)
        
        # Filter by similarity threshold
        filtered_results = [r for r in results if r["score"] >= similarity_threshold]
        
        end_time = datetime.now(timezone.utc)
        execution_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Load full embedding data
        if filtered_results:
            embedding_ids = [r["embedding_id"] for r in filtered_results]
            
            async with async_session() as session:
                result = await session.execute(
                    select(VectorEmbedding)
                    .where(VectorEmbedding.embedding_id.in_(embedding_ids))
                )
                embeddings = {e.embedding_id: e for e in result.scalars().all()}
            
            # Enrich results
            for r in filtered_results:
                emb = embeddings.get(r["embedding_id"])
                if emb:
                    r["text_content"] = emb.text_content
                    r["source_type"] = emb.source_type
                    r["source_id"] = emb.source_id
        
        # Log search query
        async with async_session() as session:
            query_record = VectorSearchQuery(
                query_id=query_id,
                query_text="",  # No text for vector search
                top_k=top_k,
                similarity_threshold=similarity_threshold,
                filters=filters,
                result_count=len(filtered_results),
                result_embedding_ids=[r["embedding_id"] for r in filtered_results],
                result_scores=[r["score"] for r in filtered_results],
                execution_time_ms=execution_time_ms,
                requested_by=requested_by
            )
            session.add(query_record)
            await session.commit()
        
        return {
            "query_id": query_id,
            "results": filtered_results,
            "execution_time_ms": execution_time_ms,
            "total_results": len(filtered_results)
        }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        backend_stats = await self.backend.get_stats()
        
        # Get database stats
        async with async_session() as session:
            from sqlalchemy import func
            
            result = await session.execute(
                select(func.count(VectorEmbedding.id))
                .where(VectorEmbedding.indexed)
            )
            indexed_count = result.scalar()
            
            result = await session.execute(
                select(func.count(VectorEmbedding.id))
            )
            total_embeddings = result.scalar()
        
        return {
            **backend_stats,
            "indexed_embeddings": indexed_count,
            "total_embeddings": total_embeddings,
            "index_coverage": (indexed_count / total_embeddings) if total_embeddings > 0 else 0.0
        }


# Global instance
vector_store = VectorStore(backend="faiss")  # Default to FAISS for dev
