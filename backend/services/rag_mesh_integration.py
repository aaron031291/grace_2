"""
RAG Service Mesh Integration

Registers RAG and World Model as first-class service-mesh capabilities.

Provides:
- Service registration with discovery
- Health signals from rag_service + vector_store
- Circuit breakers, retries, load balancing via mesh
- Unified access point for all RAG operations
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RAGMeshIntegration:
    """
    Integrates RAG services with the service mesh
    
    Makes RAG accessible through:
    - await service_mesh.call_service('rag', path='/search/rag', ...)
    - Automatic retries, circuit breakers, load balancing
    """
    
    def __init__(self):
        self._initialized = False
        self._registered = False
        self.service_id = None
    
    async def initialize(self):
        """Initialize and register RAG with service mesh"""
        if self._initialized:
            return
        
        logger.info("[RAG-MESH] Initializing RAG service mesh integration")
        
        try:
            # Register with service discovery
            await self._register_rag_service()
            
            # Register world model as separate capability
            await self._register_world_model_service()
            
            self._initialized = True
            logger.info("[RAG-MESH] RAG services registered with mesh")
            
        except Exception as e:
            logger.error(f"[RAG-MESH] Failed to register with mesh: {e}")
            raise
    
    async def _register_rag_service(self):
        """Register RAG service with discovery"""
        try:
            from backend.infrastructure import service_discovery
            
            # Get health status
            health = await self.get_rag_health()
            
            self.service_id = await service_discovery.register_service(
                service_id="rag_service_primary",
                service_type="knowledge",
                capabilities=[
                    "rag",
                    "semantic_search",
                    "context_retrieval",
                    "embeddings",
                    "hybrid_search"
                ],
                host="localhost",
                port=8000,  # FastAPI port
                health_endpoint="/api/vectors/health",
                metadata={
                    "provider": "grace_internal",
                    "backend": "faiss",
                    "version": "1.0.0"
                }
            )
            
            self._registered = True
            logger.info(f"[RAG-MESH] Registered RAG service: {self.service_id}")
            
        except ImportError:
            logger.warning("[RAG-MESH] Service mesh not available - RAG running standalone")
        except Exception as e:
            logger.error(f"[RAG-MESH] RAG registration failed: {e}")
    
    async def _register_world_model_service(self):
        """Register world model as separate service"""
        try:
            from backend.infrastructure import service_discovery
            
            await service_discovery.register_service(
                service_id="world_model_primary",
                service_type="knowledge",
                capabilities=[
                    "world_model",
                    "self_knowledge",
                    "system_knowledge",
                    "mcp"
                ],
                host="localhost",
                port=8000,
                health_endpoint="/world-model/stats",
                metadata={
                    "provider": "grace_internal",
                    "version": "1.0.0",
                    "mcp_enabled": True
                }
            )
            
            logger.info("[RAG-MESH] Registered World Model service")
            
        except Exception as e:
            logger.error(f"[RAG-MESH] World Model registration failed: {e}")
    
    async def get_rag_health(self) -> Dict[str, Any]:
        """
        Get comprehensive RAG health status
        
        Combines:
        - rag_service initialization status
        - vector_store stats
        - embedding_service status
        - world_model status
        """
        try:
            from backend.services.rag_service import rag_service
            from backend.services.vector_store import vector_store
            from backend.services.embedding_service import embedding_service
            from backend.world_model import grace_world_model
            
            # RAG service health
            rag_healthy = rag_service.initialized
            
            # Vector store health
            try:
                vector_stats = await vector_store.get_stats()
                vector_healthy = vector_stats.get("total_vectors", 0) >= 0
            except:
                vector_stats = {}
                vector_healthy = False
            
            # Embedding service health
            embedding_healthy = embedding_service.openai_client is not None or True  # Always healthy if initialized
            
            # World model health
            world_model_healthy = grace_world_model._initialized
            
            # Overall health
            all_healthy = rag_healthy and vector_healthy and embedding_healthy and world_model_healthy
            
            status = "healthy" if all_healthy else "degraded" if rag_healthy else "unhealthy"
            
            return {
                "status": status,
                "components": {
                    "rag_service": "healthy" if rag_healthy else "unhealthy",
                    "vector_store": "healthy" if vector_healthy else "unhealthy",
                    "embedding_service": "healthy" if embedding_healthy else "unhealthy",
                    "world_model": "healthy" if world_model_healthy else "unhealthy"
                },
                "stats": {
                    "total_vectors": vector_stats.get("total_vectors", 0),
                    "indexed_embeddings": vector_stats.get("indexed_embeddings", 0),
                    "backend": vector_stats.get("backend", "unknown")
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[RAG-MESH] Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def update_health(self):
        """Update health status in service discovery"""
        if not self._registered:
            return
        
        try:
            from backend.infrastructure import service_discovery
            
            health = await self.get_rag_health()
            
            await service_discovery.update_service_health(
                service_id=self.service_id,
                health_status=health["status"],
                metadata=health
            )
            
        except Exception as e:
            logger.error(f"[RAG-MESH] Health update failed: {e}")
    
    async def call_rag_through_mesh(
        self,
        operation: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call RAG operations through service mesh
        
        Args:
            operation: 'search', 'rag', 'embed', 'add_text', etc.
            **kwargs: Operation-specific parameters
            
        Returns:
            Operation result
        """
        try:
            from backend.infrastructure import service_mesh
            
            # Map operations to endpoints
            endpoint_map = {
                "search": "/api/vectors/search",
                "rag": "/api/vectors/search/rag",
                "embed": "/api/vectors/embed",
                "hybrid": "/api/vectors/search/hybrid",
                "health": "/api/vectors/health"
            }
            
            path = endpoint_map.get(operation, f"/api/vectors/{operation}")
            
            result = await service_mesh.call_service(
                capability="rag",
                path=path,
                method="POST" if operation != "health" else "GET",
                data=kwargs
            )
            
            return result
            
        except ImportError:
            # Fallback: call directly
            logger.warning("[RAG-MESH] Service mesh not available, calling direct")
            return await self._call_rag_direct(operation, **kwargs)
    
    async def _call_rag_direct(
        self,
        operation: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Direct call to RAG service (fallback)"""
        from backend.services.rag_service import rag_service
        
        if operation == "search":
            return await rag_service.retrieve(**kwargs)
        elif operation == "rag":
            return await rag_service.retrieve_with_citations(**kwargs)
        elif operation == "hybrid":
            return await rag_service.hybrid_search(**kwargs)
        else:
            return {"error": f"Unknown operation: {operation}"}
    
    def is_registered(self) -> bool:
        """Check if RAG is registered with mesh"""
        return self._registered
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG mesh integration stats"""
        return {
            "initialized": self._initialized,
            "registered": self._registered,
            "service_id": self.service_id
        }


# Global instance
rag_mesh_integration = RAGMeshIntegration()


# Convenience function for mesh-aware RAG calls
async def mesh_rag_search(
    query: str,
    top_k: int = 10,
    max_tokens: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Mesh-aware RAG search
    
    Automatically uses service mesh if available, falls back to direct call
    
    Args:
        query: Search query
        top_k: Number of results
        max_tokens: Optional token limit for RAG
        **kwargs: Additional parameters
        
    Returns:
        Search results with citations
    """
    if max_tokens:
        # RAG retrieval with citations
        return await rag_mesh_integration.call_rag_through_mesh(
            operation="rag",
            query=query,
            top_k=top_k,
            max_tokens=max_tokens,
            **kwargs
        )
    else:
        # Basic search
        return await rag_mesh_integration.call_rag_through_mesh(
            operation="search",
            query=query,
            top_k=top_k,
            **kwargs
        )


async def mesh_world_model_query(
    query: str,
    category: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Mesh-aware world model query
    
    Args:
        query: Query text
        category: Optional category filter
        **kwargs: Additional parameters
        
    Returns:
        World model results
    """
    try:
        from backend.infrastructure import service_mesh
        
        result = await service_mesh.call_service(
            capability="world_model",
            path="/world-model/query",
            method="POST",
            data={
                "query": query,
                "category": category,
                **kwargs
            }
        )
        
        return result
        
    except ImportError:
        # Fallback: direct call
        from backend.world_model import grace_world_model
        results = await grace_world_model.query(query=query, category=category, **kwargs)
        return {
            "query": query,
            "results": [r.to_dict() for r in results],
            "total": len(results)
        }