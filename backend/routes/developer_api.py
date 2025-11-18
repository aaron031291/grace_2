"""
Developer API - Senior full-stack software development endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

from backend.developer.developer_agent import developer_agent, DevelopmentJob

router = APIRouter(prefix="/api/developer", tags=["Senior Developer Mode"])


class BuildRequest(BaseModel):
    """Request to build a feature"""
    spec: str
    session_id: Optional[str] = None
    mode: str = "full"  # full, plan-only, dry-run


class BuildResponse(BaseModel):
    """Response from build request"""
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: str
    spec: str
    status: str
    created_at: str
    updated_at: str
    steps: List[Dict[str, Any]]
    artifacts: Dict[str, Any]
    errors: List[str]


@router.post("/build", response_model=BuildResponse)
async def create_build(request: BuildRequest):
    """
    Create a new software development build
    
    This endpoint initiates the full Senior Dev Mode pipeline:
    1. Plan - Analyze spec and create development plan
    2. Design - Generate ADR
    3. Scaffold - Create file structure
    4. Implement - Write code
    5. Test - Generate and run tests
    6. Quality - Run lint/typecheck/coverage/security
    7. PR - Open pull request
    
    Returns job_id to track progress
    """
    try:
        job = developer_agent.create_job(request.spec, request.session_id)
        
        import asyncio
        asyncio.create_task(developer_agent.run_full_pipeline(job))
        
        return BuildResponse(
            job_id=job.job_id,
            status="started",
            message=f"Build job {job.job_id} started. Use /api/developer/jobs/{job.job_id} to track progress."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create build: {str(e)}")


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get status of a development job
    
    Returns complete job information including:
    - Current status
    - All completed steps
    - Artifacts (plan, ADR, code changes, test results, PR link)
    - Any errors
    """
    job = developer_agent.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return JobStatusResponse(**job.to_dict())


@router.get("/jobs", response_model=List[JobStatusResponse])
async def list_jobs(session_id: Optional[str] = None, limit: int = 50):
    """
    List all development jobs
    
    Optionally filter by session_id
    """
    jobs = list(developer_agent.jobs.values())
    
    if session_id:
        jobs = [j for j in jobs if j.session_id == session_id]
    
    # Sort by created_at descending
    jobs.sort(key=lambda j: j.created_at, reverse=True)
    
    jobs = jobs[:limit]
    
    return [JobStatusResponse(**j.to_dict()) for j in jobs]


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """
    Cancel a running development job
    """
    job = developer_agent.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if job.status not in ["running", "created"]:
        raise HTTPException(status_code=400, detail=f"Job {job_id} is not running (status: {job.status})")
    
    job.status = "cancelled"
    job.add_step("cancel", "completed", {"reason": "User requested cancellation"})
    
    return {"message": f"Job {job_id} cancelled"}


@router.get("/capabilities")
async def get_capabilities():
    """
    Get Senior Developer Mode capabilities
    
    Returns information about what Grace can build
    """
    return {
        "capabilities": [
            {
                "name": "Full-Stack Development",
                "description": "Build complete features with backend + frontend",
                "supported_stacks": ["Python/FastAPI", "React/TypeScript", "PostgreSQL"]
            },
            {
                "name": "API Development",
                "description": "Create RESTful APIs with OpenAPI documentation",
                "features": ["CRUD operations", "Authentication", "Validation", "Error handling"]
            },
            {
                "name": "Frontend Components",
                "description": "Build React components with TypeScript",
                "features": ["Functional components", "Hooks", "State management", "Styling"]
            },
            {
                "name": "Testing",
                "description": "Generate comprehensive test suites",
                "types": ["Unit tests", "Integration tests", "E2E tests"]
            },
            {
                "name": "Quality Assurance",
                "description": "Automated code quality checks",
                "checks": ["Linting", "Type checking", "Coverage", "Security scanning"]
            },
            {
                "name": "CI/CD Integration",
                "description": "Open PRs with automated checks",
                "features": ["Branch creation", "PR creation", "CI monitoring", "Deployment"]
            }
        ],
        "pipeline_steps": [
            "Plan - Analyze requirements and create development plan",
            "Design - Generate Architecture Decision Record (ADR)",
            "Scaffold - Create file structure and boilerplate",
            "Implement - Write production-quality code",
            "Test - Generate and run comprehensive tests",
            "Quality - Run lint, typecheck, coverage, security scans",
            "PR - Open pull request with detailed description",
            "Deploy - Deploy to preview/production environments",
            "Monitor - Track metrics and health",
            "Rollback - Revert if issues detected"
        ],
        "best_practices": [
            "Follow existing code conventions",
            "Write self-documenting code",
            "Include comprehensive error handling",
            "Add logging and observability",
            "Maintain backward compatibility",
            "Document breaking changes",
            "Include migration guides"
        ]
    }


@router.post("/jobs/{job_id}/approve/governance")
async def approve_governance(job_id: str, approved_by: str = "system"):
    """
    Approve governance gate for a job
    
    This resumes the pipeline after governance approval:
    - Runs quality scans
    - Calculates trust score
    - Requests user final approval
    """
    job = developer_agent.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if job.status != "waiting_for_governance":
        raise HTTPException(status_code=400, detail=f"Job is not waiting for governance approval (status: {job.status})")
    
    try:
        import asyncio
        asyncio.create_task(developer_agent.resume_after_governance_approval(job, approved_by))
        
        return {
            "message": f"Governance approval granted for job {job_id}",
            "next_stage": "quality_scan"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve governance: {str(e)}")


@router.post("/jobs/{job_id}/approve/user")
async def approve_user(job_id: str, approved_by: str = "user"):
    """
    User final approval for a job
    
    This resumes the pipeline after user approval:
    - Applies changes to branch
    - Opens pull request
    - Completes the job
    """
    job = developer_agent.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if job.status != "waiting_for_user_approval":
        raise HTTPException(status_code=400, detail=f"Job is not waiting for user approval (status: {job.status})")
    
    try:
        import asyncio
        asyncio.create_task(developer_agent.resume_after_user_approval(job, approved_by))
        
        return {
            "message": f"User approval granted for job {job_id}",
            "next_stage": "apply_changes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve user: {str(e)}")


@router.post("/jobs/{job_id}/reject")
async def reject_job(job_id: str, reason: str = ""):
    """
    Reject a job at any approval gate
    """
    job = developer_agent.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job.status = "rejected"
    job.add_error(f"Job rejected: {reason}")
    
    return {
        "message": f"Job {job_id} rejected",
        "reason": reason
    }


@router.get("/health")
async def health_check():
    """Health check for Developer API"""
    return {
        "status": "healthy",
        "active_jobs": len([j for j in developer_agent.jobs.values() if j.status in ["running", "waiting_for_governance", "waiting_for_user_approval"]]),
        "total_jobs": len(developer_agent.jobs),
        "timestamp": datetime.utcnow().isoformat()
    }
