"""
Commit Workflow API Routes - Stub for gradual rollout
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..auth import get_current_user
from ..schemas_extended import CommitStatusResponse, CommitWorkflowsResponse

router = APIRouter(prefix="/api/commits", tags=["commits"])


class ProposeCommitRequest(BaseModel):
    changes: List[Dict]
    commit_message: str
    description: str
    branch_name: Optional[str] = None


@router.get("/status", response_model=CommitStatusResponse)
async def get_commit_status(user=Depends(get_current_user)):
    """Get commit workflow system status"""
    return CommitStatusResponse(
        status="active",
        workflows_pending=0,
        message="Commit workflow system ready",
        execution_trace=None,
        data_provenance=[]
    )


@router.get("/workflows", response_model=CommitWorkflowsResponse)
async def list_workflows(user=Depends(get_current_user)):
    """List all pending commit workflows"""
    # TODO: Wire to grace_commit_workflow once fully integrated
    return CommitWorkflowsResponse(
        workflows=[],
        count=0,
        execution_trace=None,
        data_provenance=[]
    )
