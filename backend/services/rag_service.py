"""
RAG (Retrieval-Augmented Generation) Service

Provides semantic retrieval for:
- Document Q&A
- Recording playback by query
- Intent-aware context retrieval
- Knowledge base search

Features:
- Query embedding
- Semantic search with filters
- Context window management
- Re-ranking (optional)
- Citation tracking
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from backend.services.embedding_service import embedding_service
from backend.services.vector_store import vector_store
from backend.models.vector_models import VectorEmbedding
from backend.models.base_models import async_session
from backend.logging_utils import log_event
from sqlalchemy import select


class RAGService:
    """
    Retrieval-Augmented Generation Service
    
    Usage:
        rag = RAGService()
        await rag.initialize()
        
        # Retrieve context for question
        context = await rag.retrieve(
            query="What are the main features?",
            top_k=5,
            source_types=["document", "recording"]
        )
        
        # Get context with citations
        result = await rag.retrieve_with_citations(
            query="How to configure Grace?",
            max_tokens=2000
        )
    """
    
    def __init__(self):
        self.initialized = False
        self.max_context_tokens = 4000  # Safe default for most models
    
    async def initialize(self):
        """Initialize RAG service"""
        if self.initialized:
            return
        
        # Initialize dependencies
        await embedding_service.initialize()
        await vector_store.initialize()
        
        self.initialized = True
        print("[RAG SERVICE] Initialized")
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        similarity_threshold: float = 0.7,
        source_types: Optional[List[str]] = None,
        filters: Optional[Dict] = None,
        requested_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context for query
        
        Args:
            query: Search query text
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            source_types: Filter by source types
            filters: Additional metadata filters
            requested_by: Who requested retrieval
            
        Returns:
            {
                "query": str,
                "results": List[Dict],
                "total_results": int,
                "execution_time_ms": float
            }
        """
        start_time = datetime.now(timezone.utc)
        
        # Embed query
        query_embedding = await embedding_service.embed_text(
            text=query,
            source_type="query",
            skip_cache=True  # Don't cache queries
        )
        
        # Apply source type filter
        search_filters = filters or {}
        if source_types:
            search_filters["source_type"] = source_types
        
        # Search vector store
        search_result = await vector_store.search(
            query_vector=query_embedding["vector"],
            top_k=top_k,
            filters=search_filters if search_filters else None,
            similarity_threshold=similarity_threshold,
            requested_by=requested_by
        )
        
        end_time = datetime.now(timezone.utc)
        total_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Send latency telemetry to HTM
        try:
            from backend.trust_framework.htm_anomaly_detector import htm_detector_pool
            # Tokenize latency (10ms buckets, max 5000)
            latency_token = min(int(total_time_ms) // 10, 5000)
            htm_detector_pool.detect_for_model(
                "rag_latency",
                [latency_token],
                [1.0]
            )
        except Exception:
            pass
        
        log_event(
            action="rag.retrieve",
            actor=requested_by,
            resource="vector_search",
            outcome="success",
            payload={
                "query_length": len(query),
                "results_count": len(search_result["results"]),
                "top_k": top_k,
                "execution_time_ms": total_time_ms
            }
        )
        
        return {
            "query": query,
            "query_embedding_id": query_embedding["embedding_id"],
            "results": search_result["results"],
            "total_results": len(search_result["results"]),
            "execution_time_ms": total_time_ms
        }
    
    async def retrieve_with_citations(
        self,
        query: str,
        max_tokens: int = 2000,
        top_k: int = 10,
        source_types: Optional[List[str]] = None,
        requested_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Retrieve context with proper citations for RAG
        
        Args:
            query: Search query
            max_tokens: Maximum tokens in context
            top_k: Number of chunks to retrieve
            source_types: Filter source types
            requested_by: Requester
            
        Returns:
            {
                "context": str,
                "citations": List[Dict],
                "total_tokens": int,
                "sources": List[str]
            }
        """
        # Retrieve results
        retrieval = await self.retrieve(
            query=query,
            top_k=top_k,
            source_types=source_types,
            requested_by=requested_by
        )
        
        # Build context with citations
        context_parts = []
        citations = []
        total_tokens = 0
        seen_sources = set()
        
        for i, result in enumerate(retrieval["results"]):
            # Estimate tokens (rough: 4 chars per token)
            text = result.get("text_content", "")
            chunk_tokens = len(text) // 4
            
            if total_tokens + chunk_tokens > max_tokens:
                break
            
            # Add citation number
            citation_num = i + 1
            
            # Format with citation
            context_parts.append(f"[{citation_num}] {text}")
            
            # Track citation
            citations.append({
                "citation_number": citation_num,
                "embedding_id": result["embedding_id"],
                "source_type": result.get("source_type"),
                "source_id": result.get("source_id"),
                "similarity_score": result.get("score"),
                "metadata": result.get("metadata", {})
            })
            
            # Track source
            source_id = result.get("source_id")
            if source_id:
                seen_sources.add(source_id)
            
            total_tokens += chunk_tokens
        
        # Join context
        context = "\n\n".join(context_parts)
        
        return {
            "context": context,
            "citations": citations,
            "total_tokens": total_tokens,
            "sources": list(seen_sources),
            "query": query
        }
    
    async def retrieve_for_recording(
        self,
        recording_session_id: str,
        query: Optional[str] = None,
        timestamp_seconds: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Retrieve transcript segments from recording
        
        Args:
            recording_session_id: Recording session ID
            query: Optional semantic query
            timestamp_seconds: Optional timestamp to search near
            
        Returns:
            Recording transcript segments
        """
        if query:
            # Semantic search in recording
            return await self.retrieve(
                query=query,
                source_types=["recording", "transcript_segment"],
                filters={"recording_session_id": recording_session_id}
            )
        
        elif timestamp_seconds is not None:
            # Find segments near timestamp
            async with async_session() as session:
                result = await session.execute(
                    select(VectorEmbedding)
                    .where(VectorEmbedding.recording_session_id == recording_session_id)
                    .where(VectorEmbedding.timestamp_seconds.isnot(None))
                    .order_by(VectorEmbedding.timestamp_seconds)
                )
                segments = result.scalars().all()
            
            # Find closest segments
            closest = []
            for seg in segments:
                if seg.timestamp_seconds is None:
                    continue
                
                time_diff = abs(seg.timestamp_seconds - timestamp_seconds)
                if time_diff < 30:  # Within 30 seconds
                    closest.append({
                        "embedding_id": seg.embedding_id,
                        "text_content": seg.text_content,
                        "timestamp_seconds": seg.timestamp_seconds,
                        "time_diff": time_diff,
                        "speaker": seg.speaker
                    })
            
            # Sort by time difference
            closest.sort(key=lambda x: x["time_diff"])
            
            return {
                "recording_session_id": recording_session_id,
                "timestamp_seconds": timestamp_seconds,
                "results": closest[:10]
            }
        
        else:
            # Return all segments
            async with async_session() as session:
                result = await session.execute(
                    select(VectorEmbedding)
                    .where(VectorEmbedding.recording_session_id == recording_session_id)
                    .order_by(VectorEmbedding.timestamp_seconds)
                )
                segments = result.scalars().all()
            
            return {
                "recording_session_id": recording_session_id,
                "results": [
                    {
                        "embedding_id": s.embedding_id,
                        "text_content": s.text_content,
                        "timestamp_seconds": s.timestamp_seconds,
                        "speaker": s.speaker
                    }
                    for s in segments
                ]
            }
    
    async def retrieve_for_intent(
        self,
        intent_id: str,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve context relevant to an intent
        
        Args:
            intent_id: Intent identifier
            query: Optional specific query
            
        Returns:
            Relevant context for intent execution
        """
        if query:
            # Semantic search with intent filter
            return await self.retrieve(
                query=query,
                filters={"intent_id": intent_id},
                requested_by=f"intent_{intent_id}"
            )
        else:
            # Get all embeddings for this intent
            async with async_session() as session:
                result = await session.execute(
                    select(VectorEmbedding)
                    .where(VectorEmbedding.intent_id == intent_id)
                )
                embeddings = result.scalars().all()
            
            return {
                "intent_id": intent_id,
                "results": [
                    {
                        "embedding_id": e.embedding_id,
                        "text_content": e.text_content,
                        "source_type": e.source_type,
                        "source_id": e.source_id
                    }
                    for e in embeddings
                ]
            }
    
    async def get_similar_documents(
        self,
        document_id: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Find documents similar to given document
        
        Args:
            document_id: Source document ID
            top_k: Number of similar docs
            
        Returns:
            Similar documents
        """
        # Get document embedding
        async with async_session() as session:
            result = await session.execute(
                select(VectorEmbedding)
                .where(VectorEmbedding.document_id == document_id)
                .limit(1)
            )
            doc_embedding = result.scalar_one_or_none()
        
        if not doc_embedding:
            return {"error": "Document not found"}
        
        # Search for similar
        search_result = await vector_store.search(
            query_vector=doc_embedding.embedding_vector,
            top_k=top_k + 1,  # +1 to exclude self
            filters={"source_type": "document"}
        )
        
        # Remove self from results
        results = [
            r for r in search_result["results"]
            if r["embedding_id"] != doc_embedding.embedding_id
        ][:top_k]
        
        return {
            "source_document_id": document_id,
            "similar_documents": results
        }
    
    async def hybrid_search(
        self,
        query: str,
        keyword_filter: Optional[str] = None,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Hybrid search combining semantic + keyword filtering
        
        Args:
            query: Semantic query
            keyword_filter: Keyword to filter results
            top_k: Number of results
            
        Returns:
            Hybrid search results
        """
        # Semantic search
        semantic_results = await self.retrieve(query=query, top_k=top_k * 2)
        
        # Apply keyword filter if provided
        if keyword_filter:
            filtered = []
            keyword_lower = keyword_filter.lower()
            
            for result in semantic_results["results"]:
                text = result.get("text_content", "").lower()
                if keyword_lower in text:
                    result["keyword_match"] = True
                    filtered.append(result)
            
            # If not enough keyword matches, add non-matches
            if len(filtered) < top_k:
                for result in semantic_results["results"]:
                    if result not in filtered:
                        result["keyword_match"] = False
                        filtered.append(result)
                    if len(filtered) >= top_k:
                        break
            
            results = filtered[:top_k]
        else:
            results = semantic_results["results"][:top_k]
        
        return {
            "query": query,
            "keyword_filter": keyword_filter,
            "results": results,
            "total_results": len(results)
        }


# Global instance
rag_service = RAGService()
