"""
Knowledge Domain Router
Consolidates all knowledge-related operations: ingest, index, retrieve, ground

Bounded Context: Knowledge I/O operations
- Ingest: knowledge ingestion from various sources
- Index: knowledge indexing and search preparation
- Retrieve: knowledge retrieval and querying
- Ground: grounding operations for verification

Canonical Verbs: query, ingest, search, ground, snapshot, rollback
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ..auth import get_current_user
from ..knowledge import knowledge_engine
from ..ingestion_service import ingestion_service
from ..knowledge_verifier import knowledge_verifier
from ..trusted_sources import trust_manager

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Domain"])


class KnowledgeQuery(BaseModel):
    query: str
    domain: Optional[str] = None
    limit: int = 10
    include_metadata: bool = True


class KnowledgeIngest(BaseModel):
    content: str
    source: str
    domain: str
    metadata: Optional[Dict[str, Any]] = None


class KnowledgeSearch(BaseModel):
    terms: List[str]
    domain: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    limit: int = 20


class KnowledgeGround(BaseModel):
    claim: str
    context: Optional[Dict[str, Any]] = None
    required_confidence: float = 0.8


@router.post("/query")
async def query_knowledge(
    request: KnowledgeQuery,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Query knowledge base with natural language"""
    try:
        results = await knowledge_engine.query(
            query=request.query,
            domain=request.domain,
            limit=request.limit,
            include_metadata=request.include_metadata
        )
        return {
            "results": results,
            "count": len(results),
            "domain": request.domain
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest")
async def ingest_knowledge(
    request: KnowledgeIngest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Ingest new knowledge content"""
    try:
        # Verify source trustworthiness
        if not await trust_manager.is_trusted(request.source):
            raise HTTPException(status_code=403, detail="Source not trusted")

        result = await ingestion_service.ingest_content(
            content=request.content,
            source=request.source,
            domain=request.domain,
            metadata=request.metadata
        )

        return {
            "ingested_id": result.get("id"),
            "status": "ingested",
            "domain": request.domain
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_knowledge(
    request: KnowledgeSearch,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Search knowledge with structured terms"""
    try:
        results = await knowledge_engine.search(
            terms=request.terms,
            domain=request.domain,
            filters=request.filters,
            limit=request.limit
        )
        return {
            "results": results,
            "count": len(results),
            "search_terms": request.terms
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ground")
async def ground_knowledge(
    request: KnowledgeGround,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Ground claims against knowledge base"""
    try:
        grounding = await knowledge_verifier.ground_claim(
            claim=request.claim,
            context=request.context,
            required_confidence=request.required_confidence
        )

        return {
            "claim": request.claim,
            "grounded": grounding.get("grounded", False),
            "confidence": grounding.get("confidence", 0.0),
            "supporting_evidence": grounding.get("evidence", []),
            "contradictions": grounding.get("contradictions", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/snapshot")
async def snapshot_knowledge(
    domain: Optional[str] = None,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create knowledge snapshot for rollback"""
    try:
        snapshot = await knowledge_engine.create_snapshot(domain=domain)
        return {
            "snapshot_id": snapshot.get("id"),
            "domain": domain,
            "timestamp": snapshot.get("timestamp"),
            "item_count": snapshot.get("count")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rollback/{snapshot_id}")
async def rollback_knowledge(
    snapshot_id: str,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Rollback knowledge to snapshot"""
    try:
        result = await knowledge_engine.rollback_to_snapshot(snapshot_id)
        return {
            "snapshot_id": snapshot_id,
            "status": "rolled_back",
            "items_restored": result.get("count", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/domains")
async def list_knowledge_domains(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List available knowledge domains"""
    try:
        domains = await knowledge_engine.list_domains()
        return {
            "domains": domains,
            "count": len(domains)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_knowledge_stats(
    domain: Optional[str] = None,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get knowledge statistics"""
    try:
        stats = await knowledge_engine.get_stats(domain=domain)
        return {
            "domain": domain,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))