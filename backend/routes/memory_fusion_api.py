"""
Memory Fusion API
Gated memory fetch through unified logic hub with governance, crypto, and audit
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/api/memory-fusion", tags=["Memory Fusion"])


# Request/Response Models

class FetchRequest(BaseModel):
    """Request to fetch memories through gateway"""
    user: str
    query: Optional[str] = None
    domain: Optional[str] = None
    limit: int = Field(10, ge=1, le=100)
    context: Optional[Dict[str, Any]] = None


class FetchResponse(BaseModel):
    """Response from gated memory fetch"""
    data: List[Dict[str, Any]]
    crypto_id: Optional[str]
    logic_update_id: Optional[str]
    signature: Optional[str]
    audit_ref: Optional[int]
    fetch_session_id: str
    fetched_at: str
    governance_approved: bool
    total_results: int


class VerifyFetchRequest(BaseModel):
    """Request to verify fetch integrity"""
    fetch_session_id: str
    signature: str


class VerifyFetchResponse(BaseModel):
    """Fetch integrity verification result"""
    valid: bool
    reason: Optional[str] = None
    audit_trail_found: Optional[bool] = None
    fetch_timestamp: Optional[str] = None
    immutable_sequence: Optional[int] = None


class StoreRequest(BaseModel):
    """Request to store memory with crypto"""
    user: str
    content: str
    domain: str = "general"
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class StoreResponse(BaseModel):
    """Memory storage result"""
    stored: bool
    memory_id: Optional[int] = None
    crypto_id: Optional[str] = None
    crypto_signature: Optional[str] = None


# Routes

@router.post("/fetch", response_model=FetchResponse)
async def fetch_memories_with_gateway(request: FetchRequest):
    """
    Fetch memories through unified logic gateway
    
    Full governance, crypto verification, and audit trail:
    1. Authenticate request (signed fetch_session_id)
    2. Governance approval check
    3. Crypto signature assignment
    4. Route to Fusion/Lightning/AgenticMemory
    5. Immutable log audit entry
    6. Trigger mesh event emission
    
    Returns memories with crypto_id, logic_update_id, signature for traceability
    """
    
    try:
        from backend.memory_fusion_service import memory_fusion_service
        
        result = await memory_fusion_service.fetch_with_gateway(
            user=request.user,
            query=request.query,
            domain=request.domain,
            limit=request.limit,
            context=request.context
        )
        
        return FetchResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fetch failed: {e}")


@router.get("/fetch/{user}", response_model=FetchResponse)
async def fetch_memories_get(
    user: str,
    query: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Fetch memories through unified logic gateway (GET variant)
    
    Same as POST /fetch but via query parameters for simple fetches
    """
    
    try:
        from backend.memory_fusion_service import memory_fusion_service
        
        result = await memory_fusion_service.fetch_with_gateway(
            user=user,
            query=query,
            domain=domain,
            limit=limit
        )
        
        return FetchResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fetch failed: {e}")


@router.post("/verify-fetch", response_model=VerifyFetchResponse)
async def verify_fetch_integrity(request: VerifyFetchRequest):
    """
    Verify integrity of a previous fetch operation
    
    Validates:
    - Crypto signature matches
    - Audit trail exists in immutable log
    - Fetch session is legitimate
    
    Use this to validate that fetched data came from a legitimate,
    governance-approved, cryptographically-signed fetch session.
    """
    
    try:
        from backend.memory_fusion_service import memory_fusion_service
        
        result = await memory_fusion_service.verify_fetch_integrity(
            fetch_session_id=request.fetch_session_id,
            signature=request.signature
        )
        
        return VerifyFetchResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {e}")


@router.post("/store", response_model=StoreResponse)
async def store_memory_with_crypto(request: StoreRequest):
    """
    Store memory with cryptographic signature
    
    Full governance and crypto flow:
    1. Governance approval check
    2. Crypto signature assignment
    3. Store in PersistentMemory with crypto_id
    4. Publish memory.stored event
    5. Immutable log audit entry
    
    Returns storage result with crypto_id and signature for traceability
    """
    
    try:
        from backend.memory_fusion_service import memory_fusion_service
        
        result = await memory_fusion_service.store_memory_with_crypto(
            user=request.user,
            content=request.content,
            domain=request.domain,
            metadata=request.metadata,
            tags=request.tags
        )
        
        return StoreResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Store failed: {e}")


@router.get("/stats")
async def get_memory_fusion_stats():
    """
    Get memory fusion service statistics
    
    Returns:
    - Cached schemas count
    - Cached configs count
    - Component availability
    - Feature flags (crypto, governance, logic hub)
    """
    
    try:
        from backend.memory_fusion_service import memory_fusion_service
        
        return memory_fusion_service.get_memory_stats()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {e}")


@router.get("/audit-trail/{fetch_session_id}")
async def get_fetch_audit_trail(fetch_session_id: str):
    """
    Get complete audit trail for a fetch session
    
    Returns:
    - Immutable log entries
    - Governance decisions
    - Crypto signatures
    - Trigger mesh events
    
    Full traceability for compliance and debugging
    """
    
    try:
        from backend.immutable_log import immutable_log
        
        # Query immutable log for fetch session
        entries = await immutable_log.get_entries(
            subsystem="memory_fusion",
            limit=100
        )
        
        # Filter for this fetch session
        relevant_entries = [
            e for e in entries
            if fetch_session_id in str(e.get("payload", {}))
        ]
        
        if not relevant_entries:
            raise HTTPException(status_code=404, detail="No audit trail found for this fetch session")
        
        return {
            "fetch_session_id": fetch_session_id,
            "audit_entries": relevant_entries,
            "total_entries": len(relevant_entries)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audit trail: {e}")


@router.post("/schema-update")
async def submit_memory_schema_update(
    domain: str,
    current_schema: Optional[Dict[str, Any]] = None,
    proposed_schema: Dict[str, Any] = ...,
    reasoning: str = ...,
    created_by: str = "api_user"
):
    """
    Submit memory schema update through unified logic hub
    
    Routes through full logic hub pipeline:
    1. Governance approval
    2. Crypto signature
    3. Validation (breaking change detection)
    4. Distribution via trigger mesh
    5. Auto-refresh of memory configs
    
    Returns update_id for tracking
    """
    
    try:
        from backend.memory_fusion_service import memory_fusion_service
        
        update_id = await memory_fusion_service.submit_memory_schema_update(
            domain=domain,
            current_schema=current_schema,
            proposed_schema=proposed_schema,
            reasoning=reasoning,
            created_by=created_by
        )
        
        return {
            "update_id": update_id,
            "status": "submitted",
            "message": f"Memory schema update submitted for domain {domain}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema update failed: {e}")
