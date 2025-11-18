"""
Vector API Routes
Handles embedding, vector storage, and RAG operations
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/vectors",
    tags=["Vector Operations"]
)

@router.get("/health")
async def vector_health():
    """
    Check vector service health
    
    Returns status of all components
    """
    try:
        # Try to import vector services
        try:
            from backend.services.embedding_service import embedding_service
            embedding_status = "healthy"
            embedding_info = {
                "provider": getattr(embedding_service, 'provider', 'unknown'),
                "model": getattr(embedding_service, 'default_model', 'unknown'),
                "cache_size": len(getattr(embedding_service, 'embedding_cache', {}))
            }
        except ImportError:
            embedding_status = "unavailable"
            embedding_info = {}
        
        try:
            from backend.services.vector_store import vector_store
            vector_status = "healthy" if hasattr(vector_store, 'backend') and vector_store.backend else "unhealthy"
            vector_info = {"backend": getattr(vector_store, 'backend_type', 'unknown')}
        except ImportError:
            vector_status = "unavailable"
            vector_info = {}
        
        try:
            from backend.services.rag_service import rag_service
            rag_status = "healthy" if hasattr(rag_service, 'initialized') and rag_service.initialized else "not_initialized"
        except ImportError:
            rag_status = "unavailable"
        
        return {
            "status": "operational",
            "service": "vectors",
            "timestamp": "2024-01-01T00:00:00Z",
            "embedding_service": {
                "status": embedding_status,
                **embedding_info
            },
            "vector_store": {
                "status": vector_status,
                **vector_info
            },
            "rag_service": {
                "status": rag_status
            }
        }
        
    except Exception as e:
        logger.error(f"Vector health check failed: {e}")
        return {
            "status": "error",
            "service": "vectors",
            "error": str(e),
            "embedding_service": {"status": "error"},
            "vector_store": {"status": "error"},
            "rag_service": {"status": "error"}
        }

@router.get("/status")
async def vector_status():
    """Get detailed vector service status"""
    return await vector_health()

@router.post("/embed")
async def create_embedding(text: str):
    """Create embedding for text"""
    try:
        from backend.services.embedding_service import embedding_service
        embedding = await embedding_service.get_embedding(text)
        return {
            "text": text,
            "embedding": embedding,
            "dimensions": len(embedding) if embedding else 0
        }
    except ImportError:
        raise HTTPException(status_code=503, detail="Embedding service not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





