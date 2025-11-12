"""
Schema Proposal API Routes
Endpoints for viewing and managing schema proposals
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

router = APIRouter(prefix="/api/memory/tables/proposals", tags=["schema-proposals"])


class RejectRequest(BaseModel):
    reason: Optional[str] = ""


@router.get("/pending")
async def get_pending_proposals(table_name: Optional[str] = None):
    """Get all pending schema proposals"""
    try:
        from backend.memory_tables.schema_proposal_engine import schema_proposal_engine
        
        if not schema_proposal_engine.registry:
            await schema_proposal_engine.initialize()
        
        proposals = await schema_proposal_engine.get_pending_proposals(table_name)
        
        return {
            'success': True,
            'proposals': proposals,
            'count': len(proposals)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{proposal_id}/approve")
async def approve_proposal(proposal_id: str):
    """Approve a schema proposal and execute the change"""
    try:
        from backend.memory_tables.schema_proposal_engine import schema_proposal_engine
        
        if not schema_proposal_engine.registry:
            await schema_proposal_engine.initialize()
        
        result = await schema_proposal_engine.approve_proposal(proposal_id)
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Approval failed'))
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{proposal_id}/reject")
async def reject_proposal(proposal_id: str, request: RejectRequest):
    """Reject a schema proposal"""
    try:
        from backend.memory_tables.schema_proposal_engine import schema_proposal_engine
        
        if not schema_proposal_engine.registry:
            await schema_proposal_engine.initialize()
        
        result = await schema_proposal_engine.reject_proposal(proposal_id, request.reason)
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Rejection failed'))
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schema-tweak")
async def propose_schema_tweak(
    table_name: str,
    field_changes: Dict[str, Any],
    reasoning: str
):
    """Propose schema modifications to an existing table"""
    try:
        from backend.memory_tables.schema_proposal_engine import schema_proposal_engine
        
        if not schema_proposal_engine.registry:
            await schema_proposal_engine.initialize()
        
        result = await schema_proposal_engine.propose_schema_tweak(
            table_name,
            field_changes,
            reasoning
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Proposal failed'))
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
