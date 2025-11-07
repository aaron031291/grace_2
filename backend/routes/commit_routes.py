"""
Commit Workflow API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..commit_workflow import grace_commit_workflow
from ..auth import get_current_user

router = APIRouter(prefix="/api/commits", tags=["commits"])


class ProposeCommitRequest(BaseModel):
    changes: List[Dict]  # [{file_path, change_type, content}]
    commit_message: str
    description: str
    branch_name: Optional[str] = None


class ApproveCommitRequest(BaseModel):
    workflow_id: str
    approved: bool
    reason: str = ""


@router.post("/propose")
async def propose_commit(
    request: ProposeCommitRequest,
    user=Depends(get_current_user)
):
    """
    Propose a new commit with code changes.
    Grace will stage, validate, and request approval.
    """
    
    workflow_id = await grace_commit_workflow.propose_commit(
        changes=request.changes,
        commit_message=request.commit_message,
        description=request.description,
        author=user["username"],
        branch_name=request.branch_name
    )
    
    # Run validation
    validation_results = await grace_commit_workflow.stage_and_validate(workflow_id)
    
    # Request approval if validation passed
    approval_id = None
    if validation_results["lint_passed"] and validation_results["tests_passed"]:
        approval_id = await grace_commit_workflow.request_approval(workflow_id)
    
    return {
        "workflow_id": workflow_id,
        "validation": validation_results,
        "approval_id": approval_id,
        "status": "pending_approval" if approval_id else "validation_failed"
    }


@router.get("/workflows")
async def list_workflows(user=Depends(get_current_user)):
    """List all pending commit workflows"""
    return grace_commit_workflow.list_pending_workflows()


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str, user=Depends(get_current_user)):
    """Get details of a specific workflow"""
    
    workflow = grace_commit_workflow.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return {
        "workflow_id": workflow.workflow_id,
        "branch": workflow.branch_name,
        "commit_message": workflow.commit_message,
        "description": workflow.description,
        "author": workflow.author,
        "status": workflow.status,
        "files_changed": len(workflow.changes),
        "lint_passed": workflow.lint_passed,
        "tests_passed": workflow.tests_passed,
        "approval_required": workflow.approval_required,
        "approval_id": workflow.approval_id
    }


@router.post("/execute")
async def execute_commit(
    workflow_id: str,
    create_pr: bool = True,
    user=Depends(get_current_user)
):
    """Execute an approved commit workflow"""
    
    try:
        results = await grace_commit_workflow.execute_commit(workflow_id, create_pr)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rollback")
async def rollback_commit(workflow_id: str, user=Depends(get_current_user)):
    """Rollback a commit workflow"""
    
    try:
        await grace_commit_workflow.rollback(workflow_id)
        return {"status": "rolled_back", "workflow_id": workflow_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
