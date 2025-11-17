from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.sql import func
from ..auth import get_current_user
from ..issue_models import IssueReport
from ..models import async_session
from ..remedy import remedy_inference
router = APIRouter(prefix="/api/issues", tags=["issues"])

@router.get("/")
async def list_issues(
    status: str = None,
    limit: int = 50,
    current_user: str = Depends(get_current_user)
):
    async with async_session() as session:
        query = select(IssueReport).where(IssueReport.user == current_user)
        if status:
            query = query.where(IssueReport.status == status)
        query = query.order_by(IssueReport.created_at.desc()).limit(limit)
        
        result = await session.execute(query)
        return [
            {
                "id": i.id,
                "source": i.source,
                "summary": i.summary,
                "explanation": i.explanation,
                "likely_cause": i.likely_cause,
                "suggested_fix": i.suggested_fix,
                "action_label": i.action_label,
                "status": i.status,
                "created_at": i.created_at,
                "resolved_at": i.resolved_at
            }
            for i in result.scalars().all()
        ]
@router.get("/{issue_id}")
async def get_issue(
    issue_id: int,
    current_user: str = Depends(get_current_user)
):
    async with async_session() as session:
        issue = await session.get(IssueReport, issue_id)
        if not issue or issue.user != current_user:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        return {
            "id": issue.id,
            "source": issue.source,
            "summary": issue.summary,
            "details": issue.details,
            "explanation": issue.explanation,
            "likely_cause": issue.likely_cause,
            "suggested_fix": issue.suggested_fix,
            "action_label": issue.action_label,
            "action_payload": issue.action_payload,
            "status": issue.status,
            "applied_fix": issue.applied_fix,
            "fix_result": issue.fix_result
        }

@router.post("/{issue_id}/resolve")
async def resolve_issue(
    issue_id: int,
    decision: str,
    current_user: str = Depends(get_current_user)
):
    if decision not in {"apply", "dismiss"}:
        raise HTTPException(status_code=400, detail="Invalid decision")
    
    if decision == "apply":
        result = await remedy_inference.apply_fix(issue_id)
        return result
    else:
        async with async_session() as session:
            issue = await session.get(IssueReport, issue_id)
            if issue:
                issue.status = "dismissed"
                issue.resolved_at = func.now()
                await session.commit()
        return {"status": "dismissed"}
