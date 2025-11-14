"""
Vector/Embedding API Endpoints

Provides REST API for:
- Embedding generation
- Vector search
- RAG retrieval
- Recording playback
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from backend.services.embedding_service import embedding_service
from backend.services.vector_store import vector_store
from backend.services.rag_service import rag_service


router = APIRouter(prefix="/api/vectors", tags=["vectors"])


# Request/Response Models

class EmbedTextRequest(BaseModel):
    """Request to embed single text"""
    text: str
    source_type: str = "document"
    source_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class EmbedBatchRequest(BaseModel):
    """Request to embed batch of texts"""
    items: List[Dict[str, Any]]
    source_type: str = "document"


class SearchRequest(BaseModel):
    """Semantic search request"""
    query: str
    top_k: int = 10
    similarity_threshold: float = 0.7
    source_types: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None


class RAGRequest(BaseModel):
    """RAG retrieval request"""
    query: str
    max_tokens: int = 2000
    top_k: int = 10
    source_types: Optional[List[str]] = None


class IndexEmbeddingsRequest(BaseModel):
    """Request to index embeddings"""
    embedding_ids: List[str]


# Embedding Endpoints

@router.post("/embed")
async def embed_text(request: EmbedTextRequest):
    """
    Generate embedding for text
    
    Returns embedding ID and vector
    """
    try:
        result = await embedding_service.embed_text(
            text=request.text,
            source_type=request.source_type,
            source_id=request.source_id,
            metadata=request.metadata
        )
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embed/batch")
async def embed_batch(request: EmbedBatchRequest):
    """
    Generate embeddings for batch of texts
    
    Returns batch ID and embedding details
    """
    try:
        result = await embedding_service.embed_batch(
            items=request.items,
            source_type=request.source_type
        )
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embed/chunks")
async def embed_chunks(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    source_type: str = "document",
    source_id: Optional[str] = None
):
    """
    Split text into chunks and embed each
    
    Returns chunked embeddings
    """
    try:
        result = await embedding_service.embed_chunks(
            text=text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            source_type=source_type,
            source_id=source_id
        )
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/embed/{embedding_id}")
async def get_embedding(embedding_id: str):
    """
    Retrieve embedding by ID
    
    Returns embedding details
    """
    result = await embedding_service.get_embedding(embedding_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Embedding not found")
    
    return result


@router.delete("/embed/{embedding_id}")
async def delete_embedding(embedding_id: str):
    """
    Delete embedding
    
    Returns success status
    """
    success = await embedding_service.delete_embedding(embedding_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Embedding not found")
    
    return {"success": True, "embedding_id": embedding_id}


# Vector Store Endpoints

@router.post("/index")
async def index_embeddings(request: IndexEmbeddingsRequest):
    """
    Index embeddings into vector store
    
    Makes embeddings searchable
    """
    try:
        result = await vector_store.index_embeddings(request.embedding_ids)
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/index/stats")
async def get_index_stats():
    """
    Get vector store statistics
    
    Returns index health and metrics
    """
    stats = await vector_store.get_stats()
    return stats


# Search Endpoints

@router.post("/search")
async def semantic_search(request: SearchRequest):
    """
    Semantic search for similar content
    
    Returns ranked results with similarity scores
    """
    try:
        # Initialize services if needed
        if not rag_service.initialized:
            await rag_service.initialize()
        
        result = await rag_service.retrieve(
            query=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            source_types=request.source_types,
            filters=request.filters,
            requested_by="api_user"
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/rag")
async def rag_retrieval(request: RAGRequest):
    """
    RAG retrieval with citations
    
    Returns formatted context ready for LLM
    """
    try:
        if not rag_service.initialized:
            await rag_service.initialize()
        
        result = await rag_service.retrieve_with_citations(
            query=request.query,
            max_tokens=request.max_tokens,
            top_k=request.top_k,
            source_types=request.source_types,
            requested_by="api_user"
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/hybrid")
async def hybrid_search(
    query: str,
    keyword_filter: Optional[str] = None,
    top_k: int = 10
):
    """
    Hybrid semantic + keyword search
    
    Returns results matching both semantic and keyword criteria
    """
    try:
        if not rag_service.initialized:
            await rag_service.initialize()
        
        result = await rag_service.hybrid_search(
            query=query,
            keyword_filter=keyword_filter,
            top_k=top_k
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Recording-Specific Endpoints

@router.get("/recording/{recording_session_id}/search")
async def search_recording(
    recording_session_id: str,
    query: Optional[str] = None,
    timestamp_seconds: Optional[float] = None
):
    """
    Search within recording transcript
    
    Can search by:
    - Semantic query
    - Timestamp proximity
    - Return all segments
    """
    try:
        if not rag_service.initialized:
            await rag_service.initialize()
        
        result = await rag_service.retrieve_for_recording(
            recording_session_id=recording_session_id,
            query=query,
            timestamp_seconds=timestamp_seconds
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Intent-Specific Endpoints

@router.get("/intent/{intent_id}/context")
async def get_intent_context(
    intent_id: str,
    query: Optional[str] = None
):
    """
    Retrieve context for intent execution
    
    Returns relevant knowledge for intent
    """
    try:
        if not rag_service.initialized:
            await rag_service.initialize()
        
        result = await rag_service.retrieve_for_intent(
            intent_id=intent_id,
            query=query
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Document Similarity

@router.get("/document/{document_id}/similar")
async def get_similar_documents(
    document_id: str,
    top_k: int = 5
):
    """
    Find documents similar to given document
    
    Returns semantically similar documents
    """
    try:
        if not rag_service.initialized:
            await rag_service.initialize()
        
        result = await rag_service.get_similar_documents(
            document_id=document_id,
            top_k=top_k
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health Check

@router.get("/health")
async def vector_health():
    """
    Check vector service health
    
    Returns status of all components
    """
    health = {
        "embedding_service": {
            "status": "healthy" if embedding_service.openai_client else "degraded",
            "provider": embedding_service.provider,
            "model": embedding_service.default_model,
            "cache_size": len(embedding_service.embedding_cache)
        },
        "vector_store": {
            "status": "healthy" if vector_store.backend else "unhealthy",
            "backend": vector_store.backend_type
        },
        "rag_service": {
            "status": "healthy" if rag_service.initialized else "not_initialized"
        }
    }
    
    # Get stats
    if vector_store.backend:
        health["vector_store"]["stats"] = await vector_store.get_stats()
    
    return health
